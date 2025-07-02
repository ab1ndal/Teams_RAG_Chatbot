# File: app/graph/nodes/rag.py
from typing import Callable
from app.graph.state import AssistantState

def retrieve_pinecone() -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["retrieved_chunks"] = []
        state["source_paths"] = []
        return state
    return _node