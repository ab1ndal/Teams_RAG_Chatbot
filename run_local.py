from app.main import rag_query, QueryRequest
import asyncio

def test_local():
    while True:
        query = input("Ask a question: ")
        if query.lower() in ["quit", "exit"]: break

        request = QueryRequest(user_id="local-user", query=query)
        response = asyncio.run(rag_query(request))
        print("\n🧠 Answer:\n" + response.answer + "\n" + "-"*50)

test_local()
