import os, json, hashlib
from app.embedding import embed_text
from app.pinecone_index import upsert_vector
from app.utils import extract_chunks
from pathlib import Path

DOCS_DIR = Path("./docs")
CACHE_FILE = Path("./index_cache.json")
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".xls", ".xlsx", ".xlsm"]

if CACHE_FILE.exists():
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
else:
    cache = {}

for root, _, files in os.walk(DOCS_DIR):
    for filename in files:
        file_path = Path(root) / filename
        ext = file_path.suffix.lower()
        
        if ext not in SUPPORTED_EXTENSIONS:
            continue

        rel_path = str(file_path.relative_to(DOCS_DIR))
        print(f"🔍 Processing: {rel_path}")
        
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    
        if cache.get(rel_path) == file_hash:
            print(f"⏩ Skipped (no changes): {rel_path}")
            continue

        chunks = extract_chunks(str(file_path))
        if not chunks:
            print(f"⚠️ No chunks found for: {rel_path}")
            continue

        print(f"🔍 Extracted {len(chunks)} chunks from {rel_path}")
        for i, chunk in enumerate(chunks):
            vec = embed_text(chunk)
            meta = {
                "file_path": str(file_path), 
                "chunk_id": i, 
                "snippet": chunk
            }
            chunk_id = f"{rel_path}_chunk_{i}".replace(os.sep, "_")
            upsert_vector(chunk_id, vec, meta)

        cache[rel_path] = file_hash
        print(f"✅ Indexed: {rel_path}")

with open(CACHE_FILE, 'w') as f:
    json.dump(cache, f, indent=2)