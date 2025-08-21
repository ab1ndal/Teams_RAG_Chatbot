# app/graph/assistant.py

from pathlib import Path
from langgraph.graph import StateGraph
from app.graph.state import AssistantState
from app.graph.nodes.classify import classify_and_rewrite_query
from app.graph.nodes.excel_insight import generate_code, execute_code
from app.graph.nodes.rfi_lookup import match_rfis, rfi_combine_context
from app.graph.nodes.generate import generate_answer
from app.graph.nodes.respond import respond
from app.services.excel_cache import get_excel_dataframe
from app.config import EXCEL_PATH, REMOVE_COLS, RENAME_COLS, SHEET_NAME, HEADER_ROW, USECOLS
from app.graph.nodes.rag import retrieve_pinecone, rerank_chunks
from app.clients.openAI_client import get_client
from app.graph.nodes.guardrails import check_query, check_query_llm

def _route_after_check(s):
    print("Routing after check...")
    return "error" if "error" in s else s.get("query_class", "general")

# Load prerequisites
try:
    #print("Loading Excel file...")
    #print(f"Excel path: {EXCEL_PATH}")
    excel_df = get_excel_dataframe(parquet_path=EXCEL_PATH.with_suffix(".parquet"), excel_path=EXCEL_PATH, 
    sheet_name=SHEET_NAME, header_row=HEADER_ROW, removeCols=REMOVE_COLS, renameCols=RENAME_COLS, usecols=USECOLS,verbose=False)
except Exception as e:
    print(f"Failed to load Excel file: {e}")
    exit(1)

classify_llm_client = get_client(model="gpt-4o-mini",temperature=0.2)
base_llm_client = get_client(model="gpt-4o",temperature=0.7)
codegen_llm_client = get_client(model="gpt-4o",temperature=0.3)
fast_classifier = get_client(model="gpt-4o-mini", temperature=0)

# Bind Excel nodes with LLM and df
generate_code_node = generate_code(codegen_llm_client, excel_df)
execute_code_node = execute_code(fast_classifier, excel_df)
match_rfis_node = match_rfis(codegen_llm_client)
rfi_combine_context_node = rfi_combine_context(codegen_llm_client)

# Bind LLM client
classify_and_refine_node = classify_and_rewrite_query(classify_llm_client)
rerank_chunks_node = rerank_chunks(codegen_llm_client)
#rewrite_query_node = rewrite_query(classify_llm_client)
generate_answer_node = generate_answer(codegen_llm_client)
retrieve_pinecone_node = retrieve_pinecone(codegen_llm_client)

# Define LangGraph
builder = StateGraph(AssistantState)

# Add all nodes
builder.add_node("check_query", check_query)
builder.add_node("check_query_llm", check_query_llm)
builder.add_node("classify_and_refine_query", classify_and_refine_node)
builder.add_node("generate_code", generate_code_node)
builder.add_node("execute_code", execute_code_node)
builder.add_node("match_rfis", match_rfis_node)
builder.add_node("rfi_combine_context", rfi_combine_context_node)
builder.add_node("generate_answer", generate_answer_node)
builder.add_node("respond", respond)
builder.add_node("retrieve_pinecone", retrieve_pinecone_node)
#builder.add_node("rewrite_query", rewrite_query_node)
builder.add_node("rerank_chunks", rerank_chunks_node)

# Define graph structure
builder.set_entry_point("check_query")
builder.add_conditional_edges(
    "check_query", 
    lambda state: "error" in state,{
        True: "respond",
        False: "classify_and_refine_query"
    }
)

builder.add_edge("classify_and_refine_query", "check_query_llm")

builder.add_conditional_edges(
    "check_query_llm", 
    _route_after_check,
    {
        "error": "respond",
        "excel_insight": "generate_code",
        "rfi_lookup": "generate_code",
        "building_code_query": "retrieve_pinecone",
        "general": "retrieve_pinecone"
    }
)

builder.add_conditional_edges("retrieve_pinecone", lambda state: "error" in state,{
        True: "respond",
        False: "rerank_chunks"
    }
)

# Excel path
builder.add_edge("generate_code", "execute_code")

builder.add_conditional_edges("execute_code", lambda state: state["query_class"], {
        "excel_insight": "generate_answer",
        "rfi_lookup": "match_rfis",
    })

# RFI path
builder.add_edge("match_rfis", "rfi_combine_context")
builder.add_edge("rfi_combine_context", "generate_answer")

# General Path
builder.add_edge("rerank_chunks", "generate_answer")

builder.add_edge("generate_answer", "respond")

# Final node
builder.set_finish_point("respond")

# Compile
assistant_graph = builder.compile()
