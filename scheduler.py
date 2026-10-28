from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio
from config import SCHEDULE_HOUR, SCHEDULE_MINUTE, PRODUCTS
from scraper import scrape_prices
from excel_handler import ExcelHandler

def run_price_update():
    """Hàm chạy việc cập nhật giá (wrapper sync)"""
    print(f"\n{'='*50}")
    print(f"[{datetime.now()}] Bắt đầu cập nhật giá...")
    print(f"{'='*50}")

    try:
        if not PRODUCTS:
            print("✗ Không tìm thấy sản phẩm nào trong products.json")
            return

        print(f"📦 Sẽ lấy giá từ {len(PRODUCTS)} sản phẩm")

        # Chạy code async từ code sync
        results = asyncio.run(scrape_prices(PRODUCTS))

        if results:
            excel = ExcelHandler()
            excel.add_prices(results)
            print(f"\n✓ Hoàn thành! Đã lưu {len(results)} sản phẩm vào Excel")
        else:
            print("\n✗ Không lấy được giá nào")

    except Exception as e:
        print(f"✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()

    print(f"{'='*50}\n")

def start_scheduler():
    """Khởi động scheduler"""
    try:
        scheduler = BackgroundScheduler()

        # Lên lịch chạy vào khung giờ cố định
        scheduler.add_job(
            run_price_update,
            CronTrigger(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE),
            id='thuocsi_price_update',
            name='Cập nhật giá ThuocSi',
            replace_existing=True,
            misfire_grace_time=60
        )

        scheduler.start()
        print(f"✓ Scheduler đã khởi động")
        print(f"✓ Bot sẽ chạy lúc {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} mỗi ngày")
        print(f"✓ Danh sách sản phẩm: {len(PRODUCTS)} sản phẩm được tải từ products.json")

        return scheduler

    except Exception as e:
        print(f"✗ Lỗi khởi động scheduler: {e}")
        return None

def stop_scheduler(scheduler):
    """Dừng scheduler"""
    if scheduler:
        scheduler.shutdown()
        print("✓ Scheduler đã dừng")
