# app/graph/assistant_graph.py

from pathlib import Path
from langgraph.graph import StateGraph, END, START
from app.graph.state import AssistantState
from app.graph.nodes.classify import classify_query
from app.graph.nodes.excel_insight import generate_code, execute_code
from app.graph.nodes.rfi_lookup import match_rf_is, load_folder_content, combine_context
from app.graph.nodes.generate import generate_answer
from app.graph.nodes.respond import respond
from app.services.excel_cache import get_excel_dataframe
from app.config import EXCEL_PATH
from app.graph.nodes.rag import retrieve_pinecone
from app.clients.openAI_client import get_client

# Load prerequisites
excel_df = get_excel_dataframe(EXCEL_PATH)
llm_client = get_client()

# Bind Excel nodes with df
generate_code_node = generate_code(excel_df)
execute_code_node = execute_code(excel_df)

# Bind LLM client
classify_node = classify_query(llm_client)

# Define LangGraph
builder = StateGraph(AssistantState)

# Add all nodes
builder.add_node("classify_query", classify_node)
builder.add_node("generate_code", generate_code_node)
builder.add_node("execute_code", execute_code_node)
builder.add_node("match_rf_is", match_rf_is)
builder.add_node("load_folder_content", load_folder_content)
builder.add_node("combine_context", combine_context)
builder.add_node("generate_answer", generate_answer)
builder.add_node("respond", respond)
builder.add_node("retrieve_pinecone", retrieve_pinecone)

# Define graph structure
builder.set_entry_point("classify_query")
builder.add_conditional_edges("classify_query", lambda state: state["query_class"], {
    "excel_insight": "generate_code",
    "rfi_lookup": "match_rf_is",
    "general": "retrieve_pinecone"
})

# Excel path
builder.add_edge("generate_code", "execute_code")
builder.add_edge("execute_code", "respond")

# RFI path
builder.add_edge("match_rf_is", "load_folder_content")
builder.add_edge("load_folder_content", "combine_context")
builder.add_edge("combine_context", "generate_answer")
builder.add_edge("generate_answer", "respond")

# Pinecone path
builder.add_edge("retrieve_pinecone", "generate_answer")

# Final node
builder.set_finish_point("respond")

# Compile
assistant_graph = builder.compile()
