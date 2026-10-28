import os
import json
from dotenv import load_dotenv

load_dotenv()

# Thông tin đăng nhập
THUOCSI_USERNAME = os.getenv('THUOCSI_USERNAME')
THUOCSI_PASSWORD = os.getenv('THUOCSI_PASSWORD')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')

# Thời gian chạy bot (giờ, phút)
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 9))
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 0))

# Đường dẫn file Excel
EXCEL_FILE = os.getenv('EXCEL_FILE', './data/prices.xlsx')

# Định nghĩa giá cao/thấp
PRICE_COMPARISON = os.getenv('PRICE_COMPARISON', 'previous_day')

# Load danh sách sản phẩm từ products.json
def load_products():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Không tìm thấy products.json")
        return []
    except json.JSONDecodeError:
        print("⚠️ Lỗi đọc products.json")
        return []

PRODUCTS = load_products()
