# File: app/graph/nodes/rfi_lookup.py
from typing import Callable
import pandas as pd
from app.graph.state import AssistantState
from langchain_openai import ChatOpenAI

# Temporary stubs for RFI lookup nodes

def match_rfis(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        folder_paths = []
        for rfi in state["rfi_matches"]:
            folder_paths.append(rfi['Link'])
        state["rfi_folder_paths"] = folder_paths
        print(state["rfi_matches"])
        print(state["rfi_folder_paths"])
        state["folder_contents"] = []
        return state
    return _node

def rfi_combine_context(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        state["context"] = ""
        return state
    return _node

def query_rfi_chunks(query:str, top_k:int = 10):
    pass