import asyncio
from playwright.async_api import async_playwright
import time
import re
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

    async def get_product_price(self, product_url):
        """Lấy giá từ URL sản phẩm - để browser decrypt"""
        page = None
        try:
            page = await self.context.new_page()
            # Use domcontentloaded instead of networkidle to load faster (faster DOM ready)
            await page.goto(product_url, wait_until='domcontentloaded', timeout=15000)

            # Đợi JavaScript trang decrypt giá (tối đa 10 giây)
            await page.wait_for_load_state('domcontentloaded')

            print(f"⏳ Đợi JavaScript decrypt giá (max 8s)...")
            for wait_sec in range(8):
                await asyncio.sleep(1)

                # Tìm giá trong DOM sau mỗi giây
                price_text = await page.evaluate('''() => {
                    // Tìm tất cả text nodes chứa số tiền
                    let numbers = [];

                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null
                    );

                    let node;
                    while (node = walker.nextNode()) {
                        const text = node.textContent.trim();

                        // Match: số 4+ chữ số (có thể có dấu phân cách)
                        // VD: 150000, 150.000, 150,000
                        const matches = text.match(/[0-9]{1,3}(?:[.,][0-9]{3})*[0-9]{0,3}/g);
                        if (matches) {
                            numbers.push(...matches);
                        }
                    }

                    // Lọc ra những số lớn (giá hợp lệ: >= 1000)
                    const priceNumbers = numbers
                        .map(n => parseInt(n.replace(/[.,]/g, ''), 10))
                        .filter(n => n >= 1000 && n <= 999999999)
                        .sort((a, b) => b - a);

                    return priceNumbers.length > 0 ? priceNumbers[0] : null;
                }''')

                if price_text:
                    print(f"  ✓ Tìm được giá: {price_text:,} VNĐ")
                    return price_text

            print(f"  ✗ Không tìm được giá trong {wait_sec}s")
            return None

        except Exception as e:
            print(f"✗ Lỗi lấy giá từ {product_url}: {e}")
            return None
        finally:
            if page:
                await page.close()

    async def get_multiple_prices(self, products):
        """Lấy giá từ nhiều sản phẩm (song song)"""
        tasks = [self.get_product_price(p['url']) for p in products]
        prices = await asyncio.gather(*tasks)

        results = []
        for product, price in zip(products, prices):
            if price:
                results.append({
                    'STT': product['STT'],
                    'name': product['name'],
                    'url': product['url'],
                    'price': price
                })
                print(f"✓ {product['name']}: {price:,} VNĐ")
            else:
                print(f"✗ {product['name']}: Không lấy được giá")

        return results

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

async def scrape_prices(products):
    """Wrapper function để scrape giá"""
    scraper = ThuocsiScraper()
    try:
        if not await scraper.setup():
            return []

        if not await scraper.login():
            return []

        results = await scraper.get_multiple_prices(products)
        return results
    except Exception as e:
        print(f"✗ Lỗi chung: {e}")
        return []
    finally:
        await scraper.close()
