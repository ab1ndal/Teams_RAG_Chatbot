
from app.document_loader import (
    extract_pdf_chunks,
    extract_docx_chunk,
    extract_txt_chunk
)
import pytest
from pathlib import Path

# Use raw string to handle special characters
file_path = Path(__file__).resolve().parents[1] / "docs" / "2511" / "jmb_-_century_city_center-rfi#2511-str_-_rtl_-_motor_court_east_canopy_framing_revised_design_confirmation-202411111729.pdf"

# Convert Path object to string
file_path_str = str(file_path)

print(f"File path: {file_path_str}")

# Check if the file exists
if file_path.exists():
    print("File exists")
    print(extract_pdf_chunks(file_path_str, chunk_size=1000, overlap=200))
else:
    print("File does not exist")
