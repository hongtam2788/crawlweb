import time
from scheduler import start_scheduler, stop_scheduler

def main():
    print("="*50)
    print("🤖 GiaThuocSi Bot v1.0")
    print("="*50)
    print("📍 Bot tự động theo dõi giá sản phẩm thuocsi.vn")
    print("📅 Chạy hàng ngày vào lúc 9:00 sáng")
    print("="*50 + "\n")

    scheduler = start_scheduler()

    if not scheduler:
        print("✗ Không thể khởi động bot")
        return

    print("\n✓ Bot đang chạy. Nhấn Ctrl+C để dừng...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n✓ Bot đang dừng...")
        stop_scheduler(scheduler)
        print("✓ Tạm biệt!")

if __name__ == '__main__':
    main()
