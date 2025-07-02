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

    print("\n=== Final Answer ===\n")
    print(final_state.get("final_answer", "[No answer generated]"))

    if "code" in final_state:
        print("\n=== Generated Code ===\n")
        print(final_state["code"])

    if "output" in final_state:
        print("\n=== Code Output ===\n")
        print(final_state["output"])

if __name__ == "__main__":
    main()
