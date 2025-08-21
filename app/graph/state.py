# app/graph/state.py

from typing import TypedDict, Optional, List, Annotated
from openai.types.chat import ChatCompletionMessage
from langgraph.graph.message import add_messages

class AssistantState(TypedDict, total=False):
    user_id: str                    # Authenticated user
    messages: Annotated[List[ChatCompletionMessage], add_messages]   # Original user messages
    thread_id: str                  # Thread/session ID
    query_class: str                # 'excel_insight' | 'general' | 'rfi_lookup' | 'building_code_query'
    query_subclass: Optional[str]   # 'needs_llm' | 'no_llm'
    history: str                    # compact running conversation history
    thread_preview: str             # compact running conversation history (5 words)
    rewritten_query: Optional[str]  # Rewritten vague query
    previous_rewrites: Optional[str] # Previous rewritten queries (if any)

    # Excel analysis
    code: str                       # Generated pandas code
    output: str                     # Output from code execution
    plot_images: List[str]          # Base64 encoded plot images
    executed: bool                  # Whether the code has been executed

    # RFI-specific path
    rfi_matches: List[dict]         # Matching rows from Excel
    rfi_folder_paths: List[str]     # File paths to RFI folders
    folder_contents: List[str]      # Read text from files
    context: str                    # Aggregated metadata + folder text

    # General search context (Pinecone-based)
    retrieved_chunks: List[str]     # Contextual chunks from semantic search
    source_paths: List[str]         # Source file paths from Pinecone
    ranked_chunks: List[str]        # Ranked chunks from semantic search

    # Final result
    final_answer: str               # Response to user
    error: Optional[str]            # Error message if any
