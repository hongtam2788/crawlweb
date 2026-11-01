import csv
import os
from datetime import datetime
from config import EXCEL_FILE

class CSVHandler:
    def __init__(self):
        self.file = EXCEL_FILE.replace('.xlsx', '.csv')
        self.create_file_if_not_exists()

    def create_file_if_not_exists(self):
        """Tạo file CSV nếu chưa tồn tại"""
        if not os.path.exists(self.file):
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            with open(self.file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['STT', 'Tên SP', 'URL'])
            print(f"✓ Đã tạo file {self.file}")

    def add_prices(self, products_with_prices):
        """Thêm giá mới vào CSV"""
        try:
            today = datetime.now().strftime('%d/%m/%Y')

            # Đọc file hiện tại
            existing_rows = {}
            if os.path.exists(self.file):
                with open(self.file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        for row in reader:
                            existing_rows[int(row['STT'])] = row
                    fieldnames = reader.fieldnames or ['STT', 'Tên SP', 'URL']
                    if today not in fieldnames:
                        fieldnames.append(today)
                    else:
                        fieldnames = fieldnames
            else:
                fieldnames = ['STT', 'Tên SP', 'URL', today]

            # Thêm giá mới
            for product in products_with_prices:
                stt = product['STT']
                if stt not in existing_rows:
                    existing_rows[stt] = {
                        'STT': stt,
                        'Tên SP': product['name'],
                        'URL': product['url'],
                    }
                existing_rows[stt][today] = product['price']

            # Ghi file CSV
            with open(self.file, 'w', encoding='utf-8', newline='') as f:
                # Ensure all fieldnames are in order
                all_fieldnames = ['STT', 'Tên SP', 'URL']
                date_columns = sorted([k for k in fieldnames if k not in all_fieldnames])
                all_fieldnames.extend(date_columns)

                writer = csv.DictWriter(f, fieldnames=all_fieldnames)
                writer.writeheader()

                # Sort by STT
                for stt in sorted(existing_rows.keys()):
                    row = existing_rows[stt]
                    # Fill missing values
                    for fn in all_fieldnames:
                        if fn not in row:
                            row[fn] = ''
                    writer.writerow(row)

            print(f"✓ Đã lưu {len(products_with_prices)} sản phẩm vào CSV")
            print(f"✓ File: {self.file}")

        except Exception as e:
            print(f"✗ Lỗi lưu CSV: {e}")
