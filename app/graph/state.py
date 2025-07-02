# app/graph/state.py

from typing import TypedDict, Optional, List, Any
from openai.types.chat import ChatCompletionMessage

class AssistantState(TypedDict, total=False):
    user_id: str                    # Authenticated user
    messages: List[ChatCompletionMessage]   # Original user messages
    thread_id: str                  # Thread/session ID
    query_class: str               # 'excel_insight' | 'general' | 'rfi_lookup'

    # Excel analysis
    code: str                       # Generated pandas code
    output: str                     # Output from code execution

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
