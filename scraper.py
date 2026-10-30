import asyncio
from playwright.async_api import async_playwright
from config import THUOCSI_USERNAME, THUOCSI_PASSWORD

class ThuocsiScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def setup(self):
        """Khởi tạo Playwright"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            print("✓ Playwright đã khởi tạo thành công")
            return True
        except Exception as e:
            print(f"✗ Lỗi khởi tạo Playwright: {e}")
            return False

    async def login(self):
        """Đăng nhập vào thuocsi.vn"""
        page = None
        try:
            if not self.context:
                print("✗ Context chưa được khởi tạo")
                return False

            page = await self.context.new_page()
            print("⏳ Đang đăng nhập vào thuocsi.vn...")

            await page.goto('https://thuocsi.vn/login', wait_until='networkidle')

            # Điền username
            await page.fill('input[name="email"]', THUOCSI_USERNAME)
            await page.fill('input[name="password"]', THUOCSI_PASSWORD)

            # Click nút đăng nhập
            await page.click('button[type="submit"]')

            # Chờ navigate xong
            await page.wait_for_load_state('networkidle')

            print("✓ Đăng nhập thành công")
            return True
        except Exception as e:
            print(f"✗ Lỗi đăng nhập: {e}")
            return False
        finally:
            if page:
                await page.close()

    async def get_all_products_from_catalog(self):
        """Lấy TẤT CẢ giá sản phẩm từ trang catalog"""
        page = None
        try:
            page = await self.context.new_page()
            print("📖 Đang tải trang product catalog...")
            await page.goto('https://thuocsi.vn/user/product-catalog', wait_until='domcontentloaded', timeout=15000)

            # Click "Xem thêm" để load tất cả sản phẩm
            print("⏳ Clicking 'Xem thêm' để tải tất cả sản phẩm...")
            for click_count in range(20):
                btn_clicked = await page.evaluate('''() => {
                    // More flexible selector for "Xem thêm" button
                    const buttons = [...document.querySelectorAll('button, a, div, span')];
                    const btn = buttons.find(e => {
                        const text = e.textContent.trim();
                        return e.childElementCount === 0 && /Xem thêm/.test(text) && /\\d+ sản phẩm/.test(text);
                    });
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                }''')

                if not btn_clicked:
                    print(f"  ✓ Tất cả sản phẩm đã tải")
                    break

                await asyncio.sleep(2.5)

            # Lấy tất cả giá sản phẩm từ trang - thử nhiều cách
            print("📊 Trích xuất giá từ tất cả sản phẩm...")
            all_products = await page.evaluate('''() => {
                const results = [];

                // Tìm tất cả product cards - flexible selector
                const cards = [
                    ...document.querySelectorAll('[class*="card"]'),
                    ...document.querySelectorAll('[class*="product"]'),
                    ...document.querySelectorAll('[role="button"]')
                ];

                // Remove duplicates
                const uniqueCards = Array.from(new Set(cards));

                uniqueCards.forEach((card, idx) => {
                    if (idx >= 1000) return; // Limit để safety

                    const cardText = card.innerText || card.textContent || '';
                    if (cardText.length < 5) return; // Skip empty cards

                    // Try to find price using multiple methods
                    let price = null;

                    // Method 1: Try React fiber on any canvas element
                    if (!price) {
                        const canvas = card.querySelector('canvas');
                        if (canvas) {
                            const fiberKey = Object.keys(canvas).find(k => k.startsWith('__react'));
                            if (fiberKey) {
                                let fiber = canvas[fiberKey];
                                for (let i = 0; i < 20 && fiber; i++) {
                                    if (fiber.memoizedProps) {
                                        // Try different property names
                                        const priceProps = ['displayPriceFormated', 'displayPrice', 'price', 'formatedPrice'];
                                        for (const prop of priceProps) {
                                            if (fiber.memoizedProps[prop]) {
                                                const priceStr = String(fiber.memoizedProps[prop]);
                                                const priceNum = parseInt(priceStr.replace(/[^0-9]/g, ''), 10);
                                                if (priceNum > 0) {
                                                    price = priceNum;
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    if (price) break;
                                    fiber = fiber.return;
                                }
                            }
                        }
                    }

                    // Method 2: Extract numbers from text that look like prices
                    if (!price) {
                        const numbers = cardText.match(/\\d{1,3}(?:[.,]\\d{3})*[0-9]*/g) || [];
                        const priceNumbers = numbers
                            .map(n => parseInt(n.replace(/[.,]/g, ''), 10))
                            .filter(n => n >= 1000 && n <= 999999999)
                            .sort((a, b) => b - a);
                        if (priceNumbers.length > 0) {
                            price = priceNumbers[0];
                        }
                    }

                    // Get product name - try multiple selectors
                    let name = '';
                    const nameSelectors = [
                        '[class*="titleWrapper"]',
                        '[class*="title"]',
                        '[class*="name"]',
                        'h2, h3, h4'
                    ];
                    for (const selector of nameSelectors) {
                        const nameEl = card.querySelector(selector);
                        if (nameEl) {
                            name = nameEl.innerText?.trim() || nameEl.textContent?.trim() || '';
                            if (name) break;
                        }
                    }

                    // If still no name, try first meaningful text
                    if (!name) {
                        const lines = cardText.split('\\n').filter(l => l.trim().length > 0);
                        name = lines[0] || '';
                    }

                    if (price && name) {
                        results.push({ name: name.substring(0, 100), price });
                    }
                });

                return results;
            }''')

            print(f"\n✓ Tổng: {len(all_products)} sản phẩm được tìm thấy")
            for product in all_products:
                print(f"  ✓ {product['name']}: {product['price']:,} VNĐ")

            return all_products

        except Exception as e:
            print(f"✗ Lỗi lấy giá từ catalog: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if page:
                await page.close()

    async def close(self):
        """Đóng browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✓ Đã đóng Playwright")
        except Exception as e:
            print(f"✗ Lỗi đóng Playwright: {e}")

async def scrape_all_prices():
    """Scrape tất cả giá từ catalog page"""
    scraper = ThuocsiScraper()
    try:
        if not await scraper.setup():
            return []

        if not await scraper.login():
            return []

        results = await scraper.get_all_products_from_catalog()
        return results
    except Exception as e:
        print(f"✗ Lỗi chung: {e}")
        return []
    finally:
        await scraper.close()
