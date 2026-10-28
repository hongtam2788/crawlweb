import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
from datetime import datetime
from config import EXCEL_FILE, PRICE_COMPARISON
import os

class ExcelHandler:
    def __init__(self):
        self.file = EXCEL_FILE
        self.create_file_if_not_exists()

    def create_file_if_not_exists(self):
        """Tạo file Excel nếu chưa tồn tại"""
        if not os.path.exists(self.file):
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            df = pd.DataFrame(columns=['STT', 'Tên SP', 'URL'])
            df.to_excel(self.file, index=False)
            print(f"✓ Đã tạo file {self.file}")

    def add_prices(self, products_with_prices):
        """Thêm giá mới vào Excel

        products_with_prices: [
            {'STT': 1, 'name': 'SP1', 'url': 'https://...', 'price': 100000},
            ...
        ]
        """
        try:
            today = datetime.now().strftime('%d/%m/%Y')
            df = pd.read_excel(self.file)

            # Nếu file mới, thêm cột URL
            if 'URL' not in df.columns:
                df['URL'] = ''

            # Tạo hoặc cập nhật cột ngày
            if today not in df.columns:
                df[today] = None

            for product in products_with_prices:
                stt = product['STT']

                # Tìm hoặc tạo dòng sản phẩm
                if stt in df['STT'].values:
                    idx = df[df['STT'] == stt].index[0]
                    df.loc[idx, today] = product['price']
                    df.loc[idx, 'URL'] = product['url']
                else:
                    new_row = {
                        'STT': stt,
                        'Tên SP': product['name'],
                        'URL': product['url'],
                        today: product['price']
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            df = df.sort_values('STT').reset_index(drop=True)
            df.to_excel(self.file, index=False)

            # Định dạng màu sắc
            self.format_prices(df, today)
            print(f"✓ Đã lưu {len(products_with_prices)} sản phẩm vào Excel")

        except Exception as e:
            print(f"✗ Lỗi lưu Excel: {e}")

    def format_prices(self, df, date_column):
        """Định dạng màu sắc: Đỏ (cao), Xanh (thấp)"""
        try:
            wb = load_workbook(self.file)
            ws = wb.active

            # Định nghĩa màu
            red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
            red_font = Font(color='FFFFFF', bold=True)

            blue_fill = PatternFill(start_color='0070C0', end_color='0070C0', fill_type='solid')
            blue_font = Font(color='FFFFFF', bold=True)

            # Tìm cột ngày tháng
            col_idx = None
            for idx, cell in enumerate(ws[1], 1):
                if cell.value == date_column:
                    col_idx = idx
                    break

            if col_idx:
                for row in range(2, ws.max_row + 1):
                    cell = ws.cell(row=row, column=col_idx)

                    if cell.value and isinstance(cell.value, (int, float)):
                        # So sánh với giá hôm trước
                        prev_col_idx = col_idx - 1

                        if prev_col_idx > 3:  # Bỏ qua cột STT, Tên SP, URL
                            prev_price = ws.cell(row, prev_col_idx).value

                            if isinstance(prev_price, (int, float)):
                                curr_price = cell.value

                                if curr_price > prev_price:
                                    cell.fill = red_fill
                                    cell.font = red_font
                                elif curr_price < prev_price:
                                    cell.fill = blue_fill
                                    cell.font = blue_font

            wb.save(self.file)
            print("✓ Đã định dạng màu sắc")

        except Exception as e:
            print(f"⚠️ Cảnh báo định dạng Excel: {e}")
