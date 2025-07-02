# File: app/graph/nodes/rag.py
from typing import Callable
from app.graph.state import AssistantState
from langchain_openai import ChatOpenAI

def rewrite_query(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        user_query = state["messages"][-1]["content"]
        prompt = f"Rewrite this query to make it more precise and suitable for document retrieval: {user_query}"
        rewritten = client.invoke([
            {"role": "system", "content": "You are a helpful assistant that rewrites vague or imprecise queries into concise, focused ones for knowledge retrieval."},
            {"role": "user", "content": prompt}
        ])
        state["query"] = rewritten.content.strip()
        return state
    return _node


def rerank_chunks(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        query = state["query"]
        docs = state.get("retrieved_chunks", [])

        rerank_prompt = f"""You are given the query: "{query}". Rank the following chunks in order of relevance. Return only the top 5.
        Chunks:
        {json.dumps(docs, indent=2)}
        Return a JSON list of the top 5 chunks ordered by relevance.
        """
        result = client.invoke([
            {"role": "system", "content": "You are a ranking assistant that prioritizes text chunks by their relevance to a user query."},
            {"role": "user", "content": rerank_prompt}
        ])
        ranked = json.loads(result.content)
        state["ranked_chunks"] = ranked
        return state
    return _node


def retrieve_pinecone(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["retrieved_chunks"] = []
        state["source_paths"] = []
        return state
    return _node