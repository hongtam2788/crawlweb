# GiaThuocSi Bot - Tự động theo dõi giá sản phẩm thuocsi.vn

Bot Python tự động lấy giá sản phẩm từ thuocsi.vn hàng ngày và lưu vào file Excel với định dạng màu sắc.

## 📋 Yêu cầu

- Python 3.9 trở lên
- Windows/Mac/Linux
- Tài khoản thuocsi.vn

## 🚀 Cài đặt nhanh

### 1. Clone repository
```bash
git clone https://github.com/hongtam2788/crawlweb.git
cd crawlweb
```

### 2. Tạo virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Cấu hình
```bash
# Copy template
cp .env.example .env

# Điền thông tin của bạn vào .env
# - THUOCSI_USERNAME: username tài khoản thuocsi.vn
# - THUOCSI_PASSWORD: password tài khoản thuocsi.vn
```

### 5. Thêm danh sách sản phẩm
Mở file `products.json` và điền danh sách 10 sản phẩm:
```json
[
  {
    "STT": 1,
    "name": "Tên sản phẩm",
    "url": "https://thuocsi.vn/product/..."
  },
  ...
]
```

### 6. Test chạy
```bash
python test_scraper.py
```

### 7. Chạy bot
```bash
python main.py
```

## 📅 Chạy tự động hàng ngày

### Windows (Task Scheduler)
1. Mở **Task Scheduler**
2. Tạo **Basic Task**:
   - **Name**: GiaThuocSi
   - **Trigger**: Daily, 9:00 AM
   - **Action**: Run program
     - Program: `C:\Python\python.exe` (đường dẫn Python)
     - Arguments: `C:\path\to\crawlweb\main.py`
     - Start in: `C:\path\to\crawlweb`

### Linux/Mac (Cron)
```bash
# Mở crontab
crontab -e

# Thêm dòng này (chạy lúc 9h sáng)
0 9 * * * cd /path/to/crawlweb && /path/to/python main.py
```

## 📁 Cấu trúc thư mục

```
crawlweb/
├── config.py           # Cấu hình (đọc từ .env)
├── scraper.py          # Lấy giá bằng Playwright
├── excel_handler.py    # Lưu và định dạng Excel
├── scheduler.py        # Lên lịch chạy
├── main.py             # Entry point
├── test_scraper.py     # Test script
├── products.json       # Danh sách sản phẩm (⚠️ hãy điền)
├── .env                # Credentials (⚠️ không commit)
├── .env.example        # Template .env
├── requirements.txt    # Dependencies
├── .gitignore          # Git ignore
└── data/
    └── prices.xlsx     # File Excel lưu giá
```

## 🔐 Bảo mật

⚠️ **QUAN TRỌNG**: 
- **Không bao giờ commit file `.env`** lên GitHub
- File `.env` chứa password của bạn
- File `.gitignore` đã được cấu hình để bảo vệ

## 🎨 Định dạng Excel

Giá sẽ được tô màu tự động:
- 🔴 **Màu đỏ**: Giá cao hơn hôm trước
- 🔵 **Màu xanh**: Giá thấp hơn hôm trước

## 🐛 Xử lý lỗi

### "Lỗi CSS selector"
Nếu bot không lấy được giá:
1. Mở https://thuocsi.vn trong trình duyệt
2. Nhấn F12 để mở DevTools
3. Tìm phần tử giá trên trang
4. Copy CSS selector
5. Cập nhật trong `scraper.py` (tìm `selectors = [...]`)

### "Đăng nhập thất bại"
1. Kiểm tra username/password trong `.env`
2. Thử đăng nhập thủ công trên website
3. Kiểm tra xem có cần CAPTCHA không

### "File Excel bị lock"
- Đóng file Excel trước khi bot chạy
- Bot sẽ tự tạo file nếu chưa tồn tại

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra file `.env` có đúng không
2. Kiểm tra `products.json` có đúng định dạng không
3. Chạy `test_scraper.py` để debug
4. Xem log trong terminal

## 📝 Ghi chú

- Bot chạy ở chế độ headless (không hiển thị trình duyệt)
- Mỗi lần chạy mất ~2-3 phút (tùy tốc độ internet)
- Excel file được tạo tự động nếu chưa tồn tại
- Có thể chỉnh thời gian chạy trong `.env` (SCHEDULE_HOUR, SCHEDULE_MINUTE)

## 📜 License

MIT
