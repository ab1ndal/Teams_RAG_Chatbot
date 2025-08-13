# File: app/graph/nodes/respond.py
from app.graph.state import AssistantState
from typing import Callable

# This node is responsible for formatting the final output for the user

def respond(state: AssistantState) -> AssistantState:
    print("Responding...")
    if "error" in state:
        state["final_answer"] = state["error"]
    elif "final_answer" not in state:
        state["final_answer"] = "⚠️ Something went wrong. Please try again later."
    return state
