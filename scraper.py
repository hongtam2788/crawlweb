import asyncio
from playwright.async_api import async_playwright
import time
import re
import json
from config import THUOCSI_USERNAME, THUOCSI_PASSWORD

class ThuocsiScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.cookies = None

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

            # Lưu cookies để dùng cho API calls
            self.cookies = await self.context.cookies()

            print("✓ Đăng nhập thành công")
            return True
        except Exception as e:
            print(f"✗ Lỗi đăng nhập: {e}")
            return False
        finally:
            if page:
                await page.close()

    def extract_sku_from_url(self, product_url):
        """Lấy SKU từ URL sản phẩm"""
        # URL format: https://thuocsi.vn/product/medx-refresh-tears-allergan-c15ml?isAvailable=false
        # SKU là phần sau /product/
        match = re.search(r'/product/([^?]+)', product_url)
        if match:
            return match.group(1)
        return None

    async def get_prices_from_api(self, products):
        """Lấy giá từ API endpoint"""
        page = None
        try:
            page = await self.context.new_page()
            print("📡 Đang gọi API để lấy giá...")

            # Trích SKU codes từ URLs
            sku_codes = []
            for product in products:
                sku = self.extract_sku_from_url(product['url'])
                if sku:
                    sku_codes.append(sku)

            if not sku_codes:
                print("✗ Không thể trích SKU từ URLs")
                return None

            print(f"📦 Gửi request cho {len(sku_codes)} SKU...")

            # Gọi API để lấy giá
            response = await page.evaluate('''async (skuCodes) => {
                try {
                    const res = await fetch('https://api.thuocsi.vn/sku/price-volatility/list', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            skuCodes: skuCodes
                        }),
                        credentials: 'include'
                    });

                    if (!res.ok) {
                        return { error: `HTTP ${res.status}` };
                    }

                    const data = await res.json();
                    return data;
                } catch (e) {
                    return { error: e.message };
                }
            }''', sku_codes)

            if response and 'error' not in response:
                print(f"✓ API response nhận được: {len(response) if isinstance(response, list) else 1} items")
                return response
            else:
                print(f"✗ API error: {response.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            print(f"✗ Lỗi gọi API: {e}")
            return None
        finally:
            if page:
                await page.close()

    async def match_prices_to_products(self, products, api_response):
        """Match giá từ API response với products"""
        results = []

        if not api_response:
            return results

        # Nếu response là dict (keyed by SKU)
        if isinstance(api_response, dict):
            for product in products:
                sku = self.extract_sku_from_url(product['url'])
                if sku and sku in api_response:
                    price_data = api_response[sku]
                    # Tìm giá trong response
                    price = None
                    if isinstance(price_data, dict):
                        price = price_data.get('price') or price_data.get('salePrice') or price_data.get('currentPrice')
                    elif isinstance(price_data, (int, float)):
                        price = price_data

                    if price:
                        results.append({
                            'STT': product['STT'],
                            'name': product['name'],
                            'url': product['url'],
                            'price': int(price)
                        })
                        print(f"✓ {product['name']}: {int(price):,} VNĐ")
                    else:
                        print(f"✗ {product['name']}: Giá không tìm thấy")
        # Nếu response là list
        elif isinstance(api_response, list):
            for product in products:
                sku = self.extract_sku_from_url(product['url'])
                for item in api_response:
                    if item.get('sku') == sku or item.get('skuCode') == sku:
                        price = item.get('price') or item.get('salePrice') or item.get('currentPrice')
                        if price:
                            results.append({
                                'STT': product['STT'],
                                'name': product['name'],
                                'url': product['url'],
                                'price': int(price)
                            })
                            print(f"✓ {product['name']}: {int(price):,} VNĐ")

        return results

    async def get_multiple_prices(self, products):
        """Lấy giá từ API (phương pháp chính)"""
        api_response = await self.get_prices_from_api(products)

        if api_response:
            return await self.match_prices_to_products(products, api_response)
        else:
            print("✗ Không lấy được giá từ API")
            return []

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
