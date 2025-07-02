# File: app/graph/nodes/generate.py
from typing import Callable
from app.graph.state import AssistantState

def generate_answer() -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["final_answer"] = state.get("output", "[No final answer generated]")
        return state
    return _node