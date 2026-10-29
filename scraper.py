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
        """Lấy giá từ URL sản phẩm"""
        page = None
        try:
            page = await self.context.new_page()
            await page.goto(product_url, wait_until='networkidle', timeout=30000)

            # Đợi thêm để JavaScript tải xong giá
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)

            # CSS selectors để tìm giá - được cập nhật với nhiều variants hơn
            selectors = [
                # Các selector phổ biến
                'span.price',
                'span.product-price',
                'div.price',
                'span[data-price]',
                'div[data-price]',
                'p.price',
                # Next.js/React-specific selectors
                '[class*="price"]',
                '[class*="Price"]',
                '[class*="salePrice"]',
                '[class*="displayPrice"]',
                '[data-testid*="price"]',
                '[id*="price"]',
                # Các class variants
                '.price__value',
                '.product__price',
                '.product-price-display',
            ]

            price_text = None
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        price_text = await page.text_content(selector)
                        if price_text and price_text.strip():
                            break
                except:
                    continue

            # Nếu vẫn không tìm được, dùng JavaScript để tìm
            if not price_text:
                price_text = await page.evaluate('''() => {
                    // Tìm element chứa giá bằng cách tìm kiếm thường trong các span/div
                    let candidates = [];

                    // Tìm tất cả text nodes chứa số lớn
                    document.querySelectorAll('span, div, p').forEach(el => {
                        const text = el.innerText || el.textContent;
                        if (text) {
                            const cleaned = text.replace(/[.,]/g, '').trim();
                            const numbers = cleaned.match(/[0-9]+/g);
                            if (numbers && numbers.some(n => n.length >= 4)) {
                                candidates.push(text);
                            }
                        }
                    });

                    // Trả về candidate đầu tiên (có khả năng cao là giá)
                    return candidates.length > 0 ? candidates[0] : null;
                }''')

            if price_text:
                # Xóa ký tự không phải số
                price = ''.join(filter(str.isdigit, price_text))
                if price and len(price) >= 4:  # Giá phải có ít nhất 4 chữ số (>= 1000 VND)
                    return int(price)

            return None
        except Exception as e:
            print(f"✗ Lỗi lấy giá từ {product_url}: {e}")
            return None
        finally:
            if page:
                await page.close()

    async def get_catalog_prices(self, products):
        """Lấy giá từ trang product catalog"""
        page = None
        try:
            page = await self.context.new_page()
            print("📖 Đang tải trang product catalog...")
            await page.goto('https://thuocsi.vn/user/product-catalog', wait_until='networkidle', timeout=30000)

            # Đợi JavaScript load xong
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)

            # Tìm tất cả product rows/items trên trang
            product_data = await page.evaluate('''() => {
                const products = [];

                // Tìm tất cả elements có chứa tên sản phẩm
                document.querySelectorAll('[class*="product"], [class*="row"], [class*="item"], tr, div[role="row"]').forEach(el => {
                    const text = el.innerText || el.textContent;
                    if (text) {
                        // Tìm patterns có tên sản phẩm + giá
                        const priceMatch = text.match(/[0-9]{4,}[0-9]{0,}/);
                        if (priceMatch) {
                            products.push({
                                text: text.substring(0, 500),
                                price: priceMatch[0]
                            });
                        }
                    }
                });

                return products;
            }''')

            print(f"Found {len(product_data)} items on catalog page")
            if product_data:
                print(f"Sample: {product_data[0]}")

            return None  # Will implement matching logic next
        except Exception as e:
            print(f"✗ Lỗi lấy giá từ catalog: {e}")
            return None
        finally:
            if page:
                await page.close()

    async def get_multiple_prices(self, products):
        """Lấy giá từ nhiều sản phẩm (song song hoặc từ catalog)"""
        # Thử phương pháp mới: lấy từ catalog page
        catalog_result = await self.get_catalog_prices(products)

        # Nếu catalog không hoạt động, quay lại phương pháp cũ
        if not catalog_result:
            print("\n📍 Fallback: Scraping individual product pages...")
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
        else:
            return catalog_result

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
