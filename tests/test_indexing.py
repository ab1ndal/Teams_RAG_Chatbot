import sys
from pathlib import Path

# Ensure app folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.services.smart_indexer import run_indexing

folder_path = Path("N:\\2019\\19032.BD - Century City JMB Tower\\CA\\RFI's\\")
CACHE_FILE = Path("./index_cache.json")

# go to every subfolder and index all files
for subfolder in folder_path.iterdir():
    if subfolder.is_dir():
        rfi_number = subfolder.name.strip()
        run_indexing(
            CACHE_FILE, 
            Path(subfolder), 
            doc_type="RFI", 
            project_name="Century City JMB Tower", 
            discipline="STR", 
            tags=["RFI", "STR", "Century City JMB Tower", "CCC", rfi_number]
        )
        print(f"✅ Indexed {rfi_number}")


