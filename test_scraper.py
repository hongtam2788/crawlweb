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

        formatted_results = []
        for idx, result in enumerate(results, 1):
            # Parse price - có thể là chuỗi hoặc số
            price_str = result['price']
            if isinstance(price_str, str):
                # Nếu là chuỗi định dạng giá (ví dụ "123.456đ" hoặc "123.456"), lấy số
                price_value = int(price_str.replace('.', '').replace('đ', '').strip())
            else:
                price_value = int(price_str)

            print(f"  {idx}. {result['name']}")
            print(f"     💰 Giá: {price_value:,} VNĐ\n")

            formatted_results.append({
                'STT': idx,
                'name': result['name'],
                'url': '',
                'price': price_value
            })

        # Lưu vào Excel
        print("💾 Đang lưu vào Excel...")
        excel = ExcelHandler()
        excel.add_prices(formatted_results)
        print(f"✓ Đã lưu {len(formatted_results)} sản phẩm vào {excel.file}\n")

    else:
        print("\n✗ Không lấy được giá nào")
        print("💡 Kiểm tra:")
        print("   - Thông tin đăng nhập trong .env (THUOCSI_USERNAME, THUOCSI_PASSWORD)")
        print("   - Kết nối mạng có bình thường không?")
        print("   - Trang https://thuocsi.vn/user/product-catalog có truy cập được không?")

    print("="*50)

if __name__ == '__main__':
    asyncio.run(test_scraper())
