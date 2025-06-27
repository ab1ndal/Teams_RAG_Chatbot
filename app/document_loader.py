from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd

def find_likely_header(df: pd.DataFrame, max_rows_to_check=10):
    for i in range(max_rows_to_check):
        if df.iloc[i].count() > len(df.columns) // 2:
            return i
    return 0

def extract_pdf_chunks(file_path: str, batch_size: int = 30, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    try:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = []
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            batch_chunks = splitter.split_documents(batch_docs)
            chunks.extend([chunk.page_content for chunk in batch_chunks])
        return chunks
    except Exception as e:
        print(f"❌ PDF error in {file_path}: {e}")
        return []


def extract_docx_chunk(file_path: str, batch_size: int = 30, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    try:
        print(f"Loading {file_path}...")
        loader = Docx2txtLoader(file_path)
        print("Loading...")
        docs = loader.load()
        print("Loading Successful")

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = []
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            batch_chunks = splitter.split_documents(batch_docs)
            chunks.extend([chunk.page_content for chunk in batch_chunks])
        print(f"🔍 Extracted {len(chunks)} chunks from {file_path}")
        return chunks
    except Exception as e:
        print(f"❌ DOCX error in {file_path}: {e}")
        return []


def extract_txt_chunk(file_path: str, batch_size: int = 30, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    try:
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        chunks = []
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]
            batch_chunks = splitter.split_documents(batch_docs)
            chunks.extend([chunk.page_content for chunk in batch_chunks])
        return chunks
    except Exception as e:
        print(f"❌ TXT error in {file_path}: {e}")
        return []


def extract_excel_chunk(file_path: str, row_block_size: int = 30, row_overlap: int = 5, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    try:
        xls = pd.ExcelFile(file_path)
        raw_blocks = []
        for sheet in xls.sheet_names:
            temp_df = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=str)
            header_row = find_likely_header(temp_df)
            df = pd.read_excel(xls, sheet_name=sheet, header=header_row, dtype=str).fillna("")
            headers = "\t".join(df.columns.astype(str))
            start = 0
            while start < len(df):
                block = df.iloc[start:start + row_block_size]
                if block.empty:
                    break
                block_text = "\n".join("\t".join(row.astype(str)) for _, row in block.iterrows())
                raw_blocks.append(f"[{sheet}]\n{headers}\n{block_text}")
                start += row_block_size - row_overlap

        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        docs = [Document(page_content=blk) for blk in raw_blocks]
        return [c.page_content for c in splitter.split_documents(docs)]
    except Exception as e:
        print(f"❌ Excel error in {file_path}: {e}")
        return []
    