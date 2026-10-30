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

    async def get_all_prices_from_catalog(self, products):
        """Lấy giá tất cả sản phẩm từ trang catalog duy nhất"""
        page = None
        try:
            page = await self.context.new_page()
            print("📖 Đang tải trang product catalog...")
            await page.goto('https://thuocsi.vn/user/product-catalog', wait_until='domcontentloaded', timeout=15000)

            # Click "Xem thêm" để load tất cả sản phẩm
            print("⏳ Clicking 'Xem thêm' để tải tất cả sản phẩm...")
            for click_count in range(20):
                # Tìm và click button "Xem thêm"
                btn_clicked = await page.evaluate('''() => {
                    const btn = [...document.querySelectorAll('button,a,div,span')]
                        .find(e => e.childElementCount === 0 && /^Xem thêm \\d+ sản phẩm$/.test(e.textContent.trim()));
                    if (btn) {
                        btn.click();
                        return true;
                    }
                    return false;
                }''')

                if not btn_clicked:
                    print("  ✓ Tất cả sản phẩm đã tải")
                    break

                await asyncio.sleep(2.5)  # Wait for content to load

            # Lấy giá tất cả sản phẩm từ trang
            print("📊 Trích xuất giá từ tất cả sản phẩm...")
            extracted_data = await page.evaluate('''() => {
                const getPrice = (canvas) => {
                    if (!canvas) return null;
                    const fiberKey = Object.keys(canvas).find(k => k.startsWith('__reactFiber'));
                    if (!fiberKey) return null;

                    let fiber = canvas[fiberKey];
                    for (let i = 0; i < 15 && fiber; i++) {
                        if (fiber.memoizedProps?.displayPriceFormated) {
                            const priceStr = String(fiber.memoizedProps.displayPriceFormated);
                            const priceNum = parseInt(priceStr.replace(/[^0-9]/g, ''), 10);
                            if (priceNum > 0) return priceNum;
                        }
                        fiber = fiber.return;
                    }
                    return null;
                };

                // Extract từ tất cả product cards
                const products = [...document.querySelectorAll('[class*="styles_card__"]')]
                    .filter(card => card.innerText.length > 0)
                    .map(card => {
                        const nameElems = card.querySelectorAll('[class*="titleWrapper"]');
                        const name = nameElems.length > 0 ? nameElems[0].innerText.trim() : '';
                        const canvas = card.querySelector('canvas[class*="canvasPrice"]');
                        const price = getPrice(canvas);
                        return { name, price };
                    })
                    .filter(p => p.price !== null);

                return products;
            }''')

            # Map với products từ config
            results = []
            extracted_by_name = {p['name']: p['price'] for p in extracted_data}

            for product in products:
                # Tìm giá bằng matching tên (hoặc theo thứ tự)
                price = extracted_by_name.get(product['name'])

                if price:
                    results.append({
                        'STT': product['STT'],
                        'name': product['name'],
                        'url': product['url'],
                        'price': price
                    })
                    print(f"✓ {product['name']}: {price:,} VNĐ")
                else:
                    print(f"⚠️ {product['name']}: Không tìm được giá trên catalog")

            print(f"\n✓ Tổng: {len(results)}/{len(products)} sản phẩm có giá")
            return results

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

async def scrape_prices(products):
    """Wrapper function để scrape giá từ catalog page"""
    scraper = ThuocsiScraper()
    try:
        if not await scraper.setup():
            return []

        if not await scraper.login():
            return []

        results = await scraper.get_all_prices_from_catalog(products)
        return results
    except Exception as e:
        print(f"✗ Lỗi chung: {e}")
        return []
    finally:
        await scraper.close()
