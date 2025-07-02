from app.config import PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX
from pinecone import Pinecone

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def upsert_vector(id, vector, metadata, namespace=None):
    index.upsert([(id, vector, metadata)], namespace=namespace)

def query_index(query_vector, top_k=3, namespace=None):
    return index.query(vector=query_vector, top_k=top_k, include_metadata=True, namespace=namespace)

def delete_vector(id, namespace=None):
    index.delete(ids=[id], namespace=namespace)

def fetch_vector(id, namespace=None):
    return index.fetch(ids=[id], namespace=namespace)

def retrieve_docs(query_vector, top_k=3, namespace=None):
    from app.services.embedding import embed_text
    query_vector = embed_text(query_vector)
    return query_index(query_vector, top_k=top_k, namespace=namespace)
