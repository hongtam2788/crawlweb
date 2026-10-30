import asyncio
import os
from scraper import scrape_all_prices
from excel_handler import ExcelHandler
from datetime import datetime

async def test_scraper():
    """Scrape tất cả sản phẩm từ catalog và lưu vào Excel"""
    print("="*50)
    print("🧪 SCRAPER - LẤY TẤT CẢ GIÁ TỪ CATALOG")
    print("="*50)
    print(f"⏰ Thời gian: {datetime.now()}")
    print(f"📍 Nguồn: https://thuocsi.vn/user/product-catalog\n")

    # Tạo folder data nếu chưa tồn tại
    os.makedirs("data", exist_ok=True)
    print("✓ Folder data/ đã sẵn sàng\n")

    # Lấy giá tất cả sản phẩm từ catalog
    print("📡 Đang tải catalog và lấy giá sản phẩm...")
    results = await scrape_all_prices()

    if results:
        print(f"\n✓ Lấy giá thành công từ {len(results)} sản phẩm")
        print("\n📊 Danh sách sản phẩm:\n")

        for idx, result in enumerate(results, 1):
            print(f"  {idx}. {result['name']}")
            print(f"     💰 Giá: {result['price']:,} VNĐ\n")

        # Lưu vào Excel
        print("💾 Đang lưu vào Excel...")
        excel = ExcelHandler()

        # Convert results để phù hợp với ExcelHandler (thêm STT và URL)
        formatted_results = [
            {
                'STT': idx,
                'name': result['name'],
                'url': '',  # Không có URL vì lấy từ catalog chung
                'price': result['price']
            }
            for idx, result in enumerate(results, 1)
        ]

        excel.add_prices(formatted_results)
        print(f"✓ Đã lưu {len(results)} sản phẩm vào {excel.file}\n")

    else:
        print("\n✗ Không lấy được giá nào")
        print("💡 Kiểm tra:")
        print("   - Thông tin đăng nhập trong .env (THUOCSI_USERNAME, THUOCSI_PASSWORD)")
        print("   - Kết nối mạng có bình thường không?")
        print("   - Trang https://thuocsi.vn/user/product-catalog có truy cập được không?")

    print("="*50)

if __name__ == '__main__':
    asyncio.run(test_scraper())
