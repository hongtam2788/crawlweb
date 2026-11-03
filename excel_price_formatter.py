import csv
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

class ExcelPriceFormatter:
    """Format CSV price data to Excel with color-coded price changes"""

    def __init__(self, csv_file='data/prices.csv', output_file='data/prices.xlsx'):
        self.csv_file = csv_file
        self.output_file = output_file

    def format_csv_to_excel(self):
        """Read CSV and convert to Excel with price comparison colors"""
        # Read CSV
        rows = []
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                rows.append(row)

        # Create Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Giá Thuốc"

        # Write headers
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.font = Font(color='FFFFFF', bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Define colors
        pink_fill = PatternFill(start_color='FFB3D9', end_color='FFB3D9', fill_type='solid')  # Light pink
        blue_fill = PatternFill(start_color='B3D9FF', end_color='B3D9FF', fill_type='solid')   # Light blue
        gray_fill = PatternFill(start_color='E0E0E0', end_color='E0E0E0', fill_type='solid')   # Gray for unchanged

        # Get date columns (all except first 3: STT, Tên SP, URL)
        date_columns = headers[3:]

        # Write data and apply colors
        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, header in enumerate(headers, 1):
                value = row_data.get(header, '')
                cell = ws.cell(row=row_idx, column=col_idx, value=value)

                # Apply color formatting for price columns
                if header in date_columns and value and value != 'ngừng kinh doanh':
                    try:
                        # Get current and previous prices
                        col_letter = get_column_letter(col_idx)
                        header_idx = headers.index(header)

                        current_price = float(str(value).replace(',', ''))

                        if header_idx > 3:  # Has previous day
                            prev_header = headers[header_idx - 1]
                            prev_value = row_data.get(prev_header, '')

                            if prev_value and prev_value != 'ngừng kinh doanh':
                                prev_price = float(str(prev_value).replace(',', ''))

                                # Apply colors based on comparison
                                if current_price > prev_price:
                                    cell.fill = pink_fill
                                elif current_price < prev_price:
                                    cell.fill = blue_fill
                                else:
                                    cell.fill = gray_fill

                    except (ValueError, IndexError):
                        pass

                # Format text alignment
                if header not in date_columns:
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                else:
                    cell.alignment = Alignment(horizontal='right', vertical='center')

                # Format "ngừng kinh doanh" in gray
                if value == 'ngừng kinh doanh':
                    cell.fill = gray_fill
                    cell.font = Font(color='666666')

        # Adjust column widths
        ws.column_dimensions['A'].width = 5   # STT
        ws.column_dimensions['B'].width = 50  # Tên SP
        ws.column_dimensions['C'].width = 15  # URL
        for col in date_columns:
            col_letter = get_column_letter(headers.index(col) + 1)
            ws.column_dimensions[col_letter].width = 12

        # Save
        wb.save(self.output_file)
        print(f"✅ Formatted Excel: {self.output_file}")
        print(f"   - Màu hồng: Giá cao hơn hôm trước")
        print(f"   - Màu xanh dương nhạt: Giá thấp hơn hôm trước")
        print(f"   - Màu xám: Giá không đổi hoặc ngừng kinh doanh")

if __name__ == '__main__':
    formatter = ExcelPriceFormatter()
    formatter.format_csv_to_excel()
