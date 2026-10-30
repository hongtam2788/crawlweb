import os
from dotenv import load_dotenv

load_dotenv()

# Thông tin đăng nhập thuocsi.vn
THUOCSI_USERNAME = os.getenv('THUOCSI_USERNAME')
THUOCSI_PASSWORD = os.getenv('THUOCSI_PASSWORD')

# Đường dẫn file Excel output
EXCEL_FILE = os.getenv('EXCEL_FILE', './data/prices.xlsx')

# Định nghĩa giá cao/thấp
PRICE_COMPARISON = os.getenv('PRICE_COMPARISON', 'previous_day')
