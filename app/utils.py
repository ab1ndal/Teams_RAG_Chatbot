import os
from pathlib import Path
from pinecone import Pinecone
from app.document_loader import (
    extract_pdf_chunks,
    extract_docx_chunk,
    extract_txt_chunk,
    extract_excel_chunk
)
from app.config import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX


def extract_chunks(file_path: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Dispatches to the appropriate extraction method based on file type."""
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_pdf_chunks(file_path, chunk_size=chunk_size, overlap=overlap)
    elif ext in [".docx", ".doc"]:
        return extract_docx_chunk(file_path, chunk_size=chunk_size, overlap=overlap)
    elif ext in [".txt"]:
        return extract_txt_chunk(file_path, chunk_size=chunk_size, overlap=overlap)
    elif ext in [".xls", ".xlsx", ".xlsm"]:
        return extract_excel_chunk(file_path, chunk_size=chunk_size, overlap=overlap)
    else:
        print(f"❌ Unsupported file type: {ext}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Splits text into overlapping chunks of a fixed size."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return chunks


def clear_index():
    """Deletes all vectors from Pinecone index and removes local cache."""
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    index = pc.Index(PINECONE_INDEX)
    index.delete(delete_all=True)
    print("✅ Cleared all vectors from the index.")

    cache_file = "index_cache.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"✅ Deleted cache file: {cache_file}")
    else:
        print(f"❌ Cache file not found: {cache_file}")