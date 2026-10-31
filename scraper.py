import asyncio
import random
from playwright.async_api import async_playwright
from config import THUOCSI_USERNAME, THUOCSI_PASSWORD

class ThuocsiScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def setup(self):
        """Khởi tạo Playwright với anti-bot detection"""
        try:
            self.playwright = await async_playwright().start()

            # 1. Tắt headless mode + thêm anti-detection flags
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Non-headless mode - giống browser thực
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-popup-blocking'
                ]
            )

            # 2. Cấu hình context với user-agent giả lập và locale VN
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080},
                locale='vi-VN',
                timezone_id='Asia/Ho_Chi_Minh',
                permissions=['geolocation'],
                geolocation={'latitude': 10.7769, 'longitude': 106.6826},  # Hà Nội
            )

            print("✓ Playwright đã khởi tạo với anti-bot detection")
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

            # Che giấu dấu hiệu Playwright
            await page.evaluate('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                Object.defineProperty(navigator, 'chromeFlags', {
                    get: () => undefined,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['vi-VN', 'vi', 'en-US', 'en'],
                });
                window.chrome = { runtime: {} };
            ''')

            await page.goto('https://thuocsi.vn/login', wait_until='networkidle', timeout=30000)

            # Delay ngẫu nhiên để giống người thực
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # Điền username (sử dụng input[name="username"] cho login tab)
            await page.fill('input[name="username"]', THUOCSI_USERNAME)
            await asyncio.sleep(random.uniform(0.5, 1.0))

            # Điền password
            await page.fill('input[name="password"]', THUOCSI_PASSWORD)
            await asyncio.sleep(random.uniform(0.5, 1.0))

            # Click nút đăng nhập (submit button với text "Đăng Nhập")
            submit_button = await page.query_selector('button[type="submit"]')
            await submit_button.click()

            # Chờ navigate xong
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(random.uniform(2.0, 3.0))

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

            # Che giấu dấu hiệu automation
            await page.evaluate('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                Object.defineProperty(navigator, 'chromeFlags', {
                    get: () => undefined,
                });
                window.chrome = { runtime: {} };
            ''')

            print("📖 Đang tải trang product catalog...")
            await page.goto('https://thuocsi.vn/user/product-catalog', wait_until='domcontentloaded', timeout=30000)

            # Chờ trang load hoàn toàn + delay ngẫu nhiên
            print("⏳ Chờ trang catalog tải hoàn toàn...")
            await asyncio.sleep(random.uniform(5.0, 7.0))

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
                        const cv = c.querySelector('canvas[class*="canvasPrice"]');
                        const price = priceOf(cv);

                        // Get product name from image alt attribute (most reliable)
                        const img = c.querySelector('img');
                        const name = img ? img.getAttribute('alt') : '';

                        return {
                            name: name,
                            price: price,
                        };
                    })
                    .filter(r => r.price !== '' && r.name !== '');  // Only products with price AND name

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
