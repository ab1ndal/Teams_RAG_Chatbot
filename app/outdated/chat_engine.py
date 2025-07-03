from app.embedding import embed_text
from app.pinecone_index import query_index
from app.document_loader import extract_pdf_page_chunk, extract_docx_chunk, extract_txt_chunk, extract_excel_chunk
from app.utils import load_full_chunk


def chat_with_rag(user_query):
    q_vec = embed_text(user_query)
    results = query_index(q_vec, top_k=3)
    context = "\n\n".join([
        load_full_chunk(m["metadata"]["file_path"], m["metadata"]["chunk_id"])
        for m in results["matches"]
    ])
    return context

