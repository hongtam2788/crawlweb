import asyncio
from config import PRODUCTS
from scraper import scrape_prices
from excel_handler import ExcelHandler
from datetime import datetime

async def test_scraper():
    """Test scraper với danh sách sản phẩm"""
    print("="*50)
    print("🧪 TEST SCRAPER")
    print("="*50)
    print(f"⏰ Thời gian: {datetime.now()}")
    print(f"📦 Sẽ lấy giá từ {len(PRODUCTS)} sản phẩm\n")

    if not PRODUCTS:
        print("✗ Không tìm thấy sản phẩm nào trong products.json")
        print("💡 Vui lòng điền danh sách sản phẩm vào products.json trước")
        return

    print("📍 Danh sách sản phẩm:")
    for p in PRODUCTS:
        print(f"  {p['STT']}. {p['name']}")
    print()

    # Lấy giá
    results = await scrape_prices(PRODUCTS)

    if results:
        print(f"\n✓ Lấy giá thành công từ {len(results)}/{len(PRODUCTS)} sản phẩm")
        print("\n📊 Kết quả:\n")

        for result in results:
            print(f"  {result['STT']}. {result['name']}")
            print(f"     💰 Giá: {result['price']:,} VNĐ")
            print(f"     🔗 URL: {result['url'][:60]}...")
            print()

        # Lưu vào Excel
        print("💾 Đang lưu vào Excel...")
        excel = ExcelHandler()
        excel.add_prices(results)
        print(f"✓ Đã lưu vào {excel.file}\n")

    else:
        print("\n✗ Không lấy được giá nào")
        print("💡 Kiểm tra:")
        print("   - Thông tin đăng nhập (kiểm tra .env)")
        print("   - Đường dẫn sản phẩm trong products.json")
        print("   - CSS selector trong scraper.py")

    print("="*50)

if __name__ == '__main__':
    asyncio.run(test_scraper())
