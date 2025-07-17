# File: tests/test_excel.py
# Author: Abhinav Bindal
# Date: 2025-07-16
# Description: Tests the Excel cache functionality
import sys
from pathlib import Path

# Ensure app folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.services.excel_cache import get_excel_dataframe
from app.config import EXCEL_PATH, REMOVE_COLS, RENAME_COLS, SHEET_NAME, HEADER_ROW, USECOLS


# Load prerequisites
try:
    print("Loading Excel file...")
    print(f"Excel path: {EXCEL_PATH}")
    excel_df = get_excel_dataframe(parquet_path=EXCEL_PATH.with_suffix(".parquet"), excel_path=EXCEL_PATH, 
    sheet_name=SHEET_NAME, header_row=HEADER_ROW, removeCols=REMOVE_COLS, renameCols=RENAME_COLS, usecols=USECOLS,verbose=False)
except Exception as e:
    print(f"Failed to load Excel file: {e}")
    exit(1)

print(excel_df.head())
print(excel_df[excel_df["RFI #"] == 2595])
