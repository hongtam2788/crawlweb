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

            # QUAN TRỌNG: Chờ page load hoàn toàn (có thể bị redirect sau login)
            print("⏳ Chờ trang catalog tải hoàn toàn...")
            await asyncio.sleep(5)  # Chờ 5 giây để page tải hoàn toàn

            # Sử dụng exact same logic từ reference code
            print("⏳ Clicking 'Xem thêm' để tải tất cả sản phẩm...")
            all_products = await page.evaluate('''(async () => {
                // 1. Click "Xem thêm" button - exact match like reference code
                for (let i = 0; i < 20; i++) {
                    const btn = [...document.querySelectorAll('button,a,div,span')]
                        .find(e => e.childElementCount === 0 && /^Xem thêm \\d+ sản phẩm$/.test(e.textContent.trim()));
                    if (!btn) {
                        console.log(`Loaded all products after ${i} clicks`);
                        break;
                    }
                    console.log(`Clicking Xem thêm ${i + 1}`);
                    btn.click();
                    await new Promise(r => setTimeout(r, 2500));
                }

                // 2. Define price extraction function - exactly like reference code
                const priceOf = cv => {
                    if (!cv) return '';
                    const key = Object.keys(cv).find(k => k.startsWith('__reactFiber'));
                    let f = cv[key];
                    for (let i = 0; i < 10 && f; i++) {
                        if (f.memoizedProps?.displayPriceFormated != null) {
                            return f.memoizedProps.displayPriceFormated;
                        }
                        f = f.return;
                    }
                    return '';
                };

                // 3. Extract from all product cards
                const rows = [...document.querySelectorAll('[class*="styles_card__"]')]
                    .map(c => {
                        const L = c.innerText.split('\\n').map(s => s.trim()).filter(Boolean);
                        const cv = c.querySelector('canvas[class*="canvasPrice"]');
                        const price = priceOf(cv);

                        // Get product name from text content
                        const name = L[0] || '';

                        return {
                            name: name,
                            price: price,
                        };
                    })
                    .filter(r => r.price !== '');  // Only products with price

                console.log(`Found ${rows.length} products with prices`);
                return rows;
            })()''')

            print(f"✓ Tìm thấy {len(all_products)} sản phẩm có giá\n")

            for idx, product in enumerate(all_products, 1):
                print(f"  {idx}. {product['name']}")
                print(f"     💰 Giá: {product['price']}\n")

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
