# File: scripts/test_excel_pipeline.py
import sys
import os
from pathlib import Path

# Ensure app folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.graph.assistant import assistant_graph

def main():
    # Example Excel insight query
    test_message = {
        "role": "user",
        "content": "List all unanswered RFIs and how long they have been pending."
    }

    state = {
        "user_id": "test_user",
        "messages": [test_message],
        "thread_id": "test_excel_001"
    }

    # Invoke assistant graph
    final_state = assistant_graph.invoke(state)

    print(final_state.get("final_answer", "[No answer generated]"))

if __name__ == "__main__":
    main()
