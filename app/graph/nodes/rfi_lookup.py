# File: app/graph/nodes/rfi_lookup.py
from typing import Callable
import pandas as pd
from app.graph.state import AssistantState

# Temporary stubs for RFI lookup nodes

def match_rfis(df: pd.DataFrame) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        # Placeholder: no-op implementation
        state["rfi_matches"] = []
        return state
    return _node

def load_folder_content() -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["rfi_folder_paths"] = []
        state["folder_contents"] = []
        return state
    return _node

def combine_context() -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["context"] = ""
        return state
    return _node
