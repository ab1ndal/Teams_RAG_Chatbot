import sys
from pathlib import Path

# Ensure app folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.services.document_loader import extract_msg_chunk

example_msg = Path("N:\\2019\\19032.BD - Century City JMB Tower\\CA\\RFI's\\0004\\CCC - RFI 004 - General Seismic Drift Requirements.msg")

print(extract_msg_chunk(example_msg))

