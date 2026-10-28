# Hướng dẫn Cài đặt trên Windows

## Bước 1: Tải Python

1. Truy cập https://www.python.org/downloads/
2. Tải Python 3.11 hoặc mới hơn
3. **Quan trọng**: Khi cài đặt, ✅ chọn "Add Python to PATH"
4. Nhấn Install

## Bước 2: Tải Git

1. Truy cập https://git-scm.com/download/win
2. Tải và cài đặt Git

## Bước 3: Clone Repository

1. Mở **Command Prompt** (nhấn Win+R, gõ `cmd`, Enter)
2. Chạy lệnh:
```bash
git clone https://github.com/hongtam2788/crawlweb.git
cd crawlweb
```

## Bước 4: Tạo Virtual Environment

Trong Command Prompt, chạy:
```bash
python -m venv venv
venv\Scripts\activate
```

Bạn sẽ thấy `(venv)` ở đầu dòng Command Prompt (nếu thành công)

## Bước 5: Cài đặt Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

## Bước 6: Cấu hình Thông tin

1. Tìm file `.env.example` trong thư mục
2. Nhấp chuột phải → "Rename" → Đổi thành `.env`
3. Nhấp chuột phải vào `.env` → "Edit with Notepad"
4. Điền thông tin:
```
THUOCSI_USERNAME=your_username
THUOCSI_PASSWORD=your_password
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```
5. Lưu file (Ctrl+S)

## Bước 7: Thêm Danh sách Sản phẩm

1. Mở file `products.json`
2. Thay thế các sản phẩm mẫu bằng 10 sản phẩm thực tế:
```json
[
  {
    "STT": 1,
    "name": "MEDX Systane Ultra",
    "url": "https://thuocsi.vn/product/medx-systane-ultra--alcon-c5ml"
  },
  ...
]
```
3. Lưu file

## Bước 8: Test Bot

1. Mở Command Prompt trong thư mục crawlweb
2. Kích hoạt virtual environment: `venv\Scripts\activate`
3. Chạy test: `python test_scraper.py`
4. Chờ hoàn thành (khoảng 2-3 phút)

## Bước 9: Chạy Bot Hàng Ngày

### Cách 1: Dùng File Batch (đơn giản)

1. Tạo file `run_bot.bat` trong thư mục crawlweb:
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
```

2. Để chạy bot: Double-click `run_bot.bat`

### Cách 2: Dùng Task Scheduler (tự động)

1. Nhấn Win+R, gõ `taskschd.msc`, Enter
2. Click "Create Basic Task..."
3. Đặt tên: "GiaThuocSi Bot"
4. Click Next

#### Trigger (Kích hoạt):
- Chọn "Daily"
- Set thời gian: 9:00 AM
- Click Next

#### Action (Hành động):
- Chọn "Start a program"
- Program: `python.exe`
- Arguments: `main.py`
- Start in: `C:\Users\[YourUsername]\crawlweb` (thay [YourUsername])
- Click Next

#### Hoàn thành:
- Click Finish

**Kiểm tra**: Task Scheduler sẽ chạy bot vào 9h sáng hôm sau

## Bước 10: Kiểm tra Kết quả

Tìm file `data/prices.xlsx` - đó là file Excel chứa giá sản phẩm

## ⚠️ Lưu ý Quan Trọng

1. **Bảo vệ file .env**:
   - Đừng chia sẻ file `.env` cho ai
   - Đừng commit `.env` lên GitHub
   - Chỉ chia sẻ file `.env.example` (mẫu)

2. **Python PATH**:
   - Nếu lệnh `python` không hoạt động, hãy dùng `python.exe`

3. **Virtual Environment**:
   - Luôn kích hoạt venv trước khi chạy bot: `venv\Scripts\activate`

4. **Excel File**:
   - Đừng mở file Excel khi bot đang chạy
   - Bot sẽ tự cập nhật file

## 🐛 Xử lý Lỗi Phổ Biến

### "python: command not found"
- Python chưa được thêm vào PATH
- Cài đặt lại Python, lần này chọn "Add Python to PATH"

### "ModuleNotFoundError"
- Quên kích hoạt virtual environment
- Chạy: `venv\Scripts\activate`

### "File '.env' not found"
- Chưa tạo file `.env`
- Rename `.env.example` thành `.env`

### "Lỗi đăng nhập"
- Kiểm tra username/password trong `.env`
- Thử đăng nhập thủ công trên https://thuocsi.vn

## 💡 Mẹo

- Để xem kết quả nhanh: Chạy `python test_scraper.py`
- Để xem bot đang làm gì: Mở Command Prompt và chạy `python main.py`
- Để dừng bot: Nhấn Ctrl+C

## 📞 Cần Giúp?

Nếu gặp vấn đề:
1. Đọc phần "Xử lý Lỗi" ở trên
2. Kiểm tra file `.env` đã cấu hình đúng chưa
3. Kiểm tra danh sách sản phẩm trong `products.json` đúng không
4. Chạy `python test_scraper.py` để debug

Chúc bạn thành công! 🎉
