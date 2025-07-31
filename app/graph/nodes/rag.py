# File: app/graph/nodes/rag.py
from typing import Callable
from app.graph.state import AssistantState
from langchain_openai import ChatOpenAI
from app.services.pinecone_index import retrieve_docs
import json
import re

def rewrite_query(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        user_query = state["messages"][-1]["content"] if state.get("messages") else ""
        prompt = f"Rewrite this query to make it more precise and suitable for document retrieval: {user_query}. DO NOT replace any acronyms."
        rewritten = client.invoke([
            {"role": "system", "content": "You are a helpful assistant that rewrites vague or imprecise queries into concise, focused ones for knowledge retrieval."},
            {"role": "user", "content": prompt}
        ])
        state["messages"][-1]["content"] = rewritten.content.strip()
        return state
    return _node


def rerank_chunks(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        query = state["messages"][-1]["content"] if state.get("messages") else ""
        docs = state.get("retrieved_chunks", [])

        # Prepare input as numbered snippet list for ranking
        doc_texts = [doc.get("snippet", "") for doc in docs]
        indexed_chunks = [f"{i+1}. {text}" for i, text in enumerate(doc_texts)]

        rerank_prompt = f"""You are given a user query and a list of document chunks. Your job is to return the top 5 most relevant chunks.\nQuery:"{query}"\nChunks:{json.dumps(indexed_chunks, indent=2)}\nInstructions:\n
            - Only return a JSON list of 15 integers, each representing the index (1-based) of the top 15 relevant chunks.
            - Do not return any explanations or commentary. Just a JSON list like: [3, 1, 7, 2, 5, ...]
        """

        result = client.invoke([
            {"role": "system", "content": "You are a ranking assistant. Return only the JSON list of indices."},
            {"role": "user", "content": rerank_prompt.strip()}
        ])

        try:
            raw_output = result.content.strip()
            # Remove markdown code block if present
            if raw_output.startswith("```") and raw_output.endswith("```"):
                raw_output = re.sub(r"^```(?:json)?\n|\n```$", "", raw_output.strip(), flags=re.IGNORECASE)

            top_indices = json.loads(raw_output)
            # Adjust for 0-based indexing and preserve original metadata
            ranked_docs = [docs[i - 1] for i in top_indices if 0 < i <= len(docs)]
            state["ranked_chunks"] = ranked_docs
        except Exception as e:
            state["ranked_chunks"] = []
            state["error"] = f"❌ Failed to parse reranked output: {str(e)}"

        return state
    return _node



def retrieve_pinecone(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        query = state["messages"][-1]["content"] if state.get("messages") else ""
        results = retrieve_docs(query, top_k=50).get("matches", [])
        if not results:
            state["retrieved_chunks"] = []
            state["source_paths"] = []
            state["error"] = "❌ No relevant documents found."
            return state
        state["retrieved_chunks"] = [
            {
                "snippet": result["metadata"].get("snippet", ""),
                "metadata": result["metadata"] 
            }
            for result in results]
        return state
    return _node