import asyncio
from playwright.async_api import async_playwright
import time
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
        """Lấy giá từ URL sản phẩm"""
        page = None
        try:
            page = await self.context.new_page()
            await page.goto(product_url, wait_until='networkidle', timeout=30000)

            # CSS selectors để tìm giá (cần điều chỉnh theo cấu trúc thực tế)
            # Thử các selector phổ biến
            selectors = [
                'span.price',
                'span.product-price',
                'div.price',
                'span[data-price]',
                'div[data-price]',
                'p.price',
            ]

            price_text = None
            for selector in selectors:
                try:
                    price_text = await page.text_content(selector)
                    if price_text and price_text.strip():
                        break
                except:
                    continue

            if price_text:
                # Xóa ký tự không phải số
                price = ''.join(filter(str.isdigit, price_text))
                if price:
                    return int(price)

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
