# app/services/smart_indexer.py
import os, json, hashlib
from app.services.embedding import embed_text
from app.services.pinecone_index import upsert_vector
from app.services.utils import extract_chunks
from pathlib import Path

DOCS_DIR = Path("../docs")
CACHE_FILE = Path("../index_cache.json")
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".msg"]

def load_cache(cache_file: Path):
    """
    Loads cache from the cache file if it exists
    """
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache: dict[str, str], cache_file: Path):
    """
    Saves cache to the cache file
    """
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)

def compute_hash(file_path):
    """
    Computes the SHA-256 hash of a file
    """
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def build_metadata(file_path: Path, chunk: str, chunk_id: int, tags: list[str] = [], doc_type: str = None, project_name: str = "Internal Doc", discipline: str = None):
    """
    Builds metadata for a chunk of text
    """
    metadata = {
        "file_path": str(file_path),
        "doc_type": doc_type,
        "folder": Path(file_path).parent.name,
        "file_name": file_path.name,
        "tags": tags,
        "discipline":discipline,
        "project": project_name,
        "chunk_id": chunk_id,
        "snippet": chunk
    }
    return metadata 

def index_file(file_path: Path, cache: dict[str, str], tags: list[str] = [], doc_type: str = None, project_name: str = "Internal Doc", discipline: str = None):
    file_hash = compute_hash(file_path)
    str_file_path = str(file_path)
    if cache.get(str_file_path) == file_hash:
        #print(f"⏩ Skipped (no changes): {file_path}")
        return
    
    chunks = extract_chunks(str_file_path)
    if not chunks:
        #print(f"⚠️ No chunks found for: {str_file_path}")
        return
    #print(f"🔍 Extracted {len(chunks)} chunks from {str_file_path}")
    
    for i, chunk in enumerate(chunks):
        vec = embed_text(chunk)
        chunk_metadata = build_metadata(file_path, chunk, i, tags, doc_type, project_name, discipline)
        chunk_id = f"{str_file_path}_chunk_{i}".replace(os.sep, "_")
        upsert_vector(chunk_id, vec, chunk_metadata)
    cache[str_file_path] = file_hash
    #print(f"✅ Indexed: {str_file_path}")


def run_indexing(cache_file: Path, docs_dir: Path, tags: list[str] = [], doc_type: str = None, project_name: str = "Internal Doc", discipline: str = None):
    print(f"🚀 Starting indexing for {docs_dir}")
    cache = load_cache(cache_file)
    print(f"📁 Cache loaded with {len(cache)} files")

    for root, _, files in os.walk(docs_dir):
        for filename in files:
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()        
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            try:
                index_file(file_path, cache, tags, doc_type, project_name, discipline)
            except Exception as e:
                print(f"❌ Failed to index {file_path}: {e}")
    save_cache(cache, cache_file)