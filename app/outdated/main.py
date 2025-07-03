from fastapi import FastAPI
from pydantic import BaseModel
from app.embedding import embed_text
from app.pinecone_index import query_index
from app.guardrails import is_query_allowed
from pathlib import Path
from app.clients.openAI_client import get_client

client = get_client()

app = FastAPI(title="Teams RAG Bot")

class QueryRequest(BaseModel):
    user_id: str
    query: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/rag/query", response_model=QueryResponse)
async def rag_query(request: QueryRequest):
    query_text = request.query.strip()

    # 1. Guardrails
    if not is_query_allowed(query_text):
        return QueryResponse(answer="🚫 This query is restricted or outside permitted scope.")

    # 2. Embed query
    query_vector = embed_text(query_text)

    # 3. Retrieve chunks from Pinecone
    results = query_index(query_vector, top_k=10)
    matches = results.get("matches", [])
    if not matches:
        return QueryResponse(answer="❌ No relevant documents found.")

    # 4. Gather context and sources
    context_chunks = [match["metadata"].get("snippet", "") for match in matches]
    sources = [match["metadata"].get("file_path", "unknown") for match in matches]
    unique_file_paths = set(sources)
    full_documents = []
    for path in unique_file_paths:
        try:
            with open(Path(path), 'r', encoding='utf-8', errors="ignore") as f:
                full_documents.append(f.read())
        except Exception as e:
            full_documents.append(f"❌ Error reading {path}: {str(e)}")

    context = "\n\n".join(context_chunks)
    #print(context)
    #context = "\n-------\n".join(full_documents)

    # 5. Call o4-mini to generate the final response
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful engineering assistant. Use the context to answer clearly and professionally."},
                {"role": "user", "content": f"Context:\n{context}"},
                {"role": "user", "content": f"Question: {query_text}"}
            ],
            temperature=0.3,
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        return QueryResponse(answer=f"❌ LLM error: {str(e)}")

    # 6. Format sources
    sources_list = "\n".join(f"• `{src}`" for src in set(sources))
    final_response = f"{answer}\n\n---\n📚 **Sources:**\n{sources_list}"

    return QueryResponse(answer=final_response)