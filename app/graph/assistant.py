# app/graph/assistant.py

from pathlib import Path
from langgraph.graph import StateGraph, END
from app.graph.state import AssistantState
from app.graph.nodes.classify import classify_query
from app.graph.nodes.excel_insight import generate_code, execute_code
from app.graph.nodes.rfi_lookup import match_rfis, load_folder_content, combine_context
from app.graph.nodes.generate import generate_answer
from app.graph.nodes.respond import respond
from app.services.excel_cache import get_excel_dataframe
from app.config import EXCEL_PATH, REMOVE_COLS, RENAME_COLS, SHEET_NAME, HEADER_ROW
from app.graph.nodes.rag import retrieve_pinecone
from app.clients.openAI_client import get_client
from app.graph.nodes.guardrails import check_query

# Load prerequisites
try:
    excel_df = get_excel_dataframe(parquet_path=EXCEL_PATH.with_suffix(".parquet"), excel_path=EXCEL_PATH, sheet_name=SHEET_NAME, header_row=HEADER_ROW, removeCols=REMOVE_COLS, renameCols=RENAME_COLS)
except Exception as e:
    print(f"Failed to load Excel file: {e}")
    exit(1)

classify_llm_client = get_client(temperature=0)
base_llm_client = get_client(temperature=0.7)
codegen_llm_client = get_client(temperature=0.3)

# Bind Excel nodes with LLM and df
generate_code_node = generate_code(codegen_llm_client, excel_df)
execute_code_node = execute_code(classify_llm_client, excel_df)

# Bind LLM client
classify_node = classify_query(classify_llm_client)

# Define LangGraph
builder = StateGraph(AssistantState)

# Add all nodes
builder.add_node("check_query", check_query)
builder.add_node("classify_query", classify_node)
builder.add_node("generate_code", generate_code_node)
builder.add_node("execute_code", execute_code_node)
builder.add_node("match_rfis", match_rfis)
builder.add_node("load_folder_content", load_folder_content)
builder.add_node("combine_context", combine_context)
builder.add_node("generate_answer", generate_answer)
builder.add_node("respond", respond)
builder.add_node("retrieve_pinecone", retrieve_pinecone)

# Define graph structure
builder.set_entry_point("check_query")
builder.add_conditional_edges("check_query", lambda state: "error" in state,{
        True: "respond",
        False: "classify_query"
    }
)
builder.add_conditional_edges("classify_query", lambda state: state["query_class"], {
    "excel_insight": "generate_code",
    "rfi_lookup": "match_rfis",
    "general": "retrieve_pinecone"
})



# Excel path
builder.add_edge("generate_code", "execute_code")
builder.add_edge("execute_code", "respond")

# RFI path
builder.add_edge("match_rfis", "load_folder_content")
builder.add_edge("load_folder_content", "combine_context")
builder.add_edge("combine_context", "generate_answer")
builder.add_edge("generate_answer", "respond")

# Pinecone path
builder.add_edge("retrieve_pinecone", "generate_answer")

# Final node
builder.set_finish_point("respond")

# Compile
assistant_graph = builder.compile()
