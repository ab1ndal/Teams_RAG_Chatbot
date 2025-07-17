# File: tests/test_multi_input.py
import sys
from pathlib import Path

# Ensure app folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.graph.assistant import assistant_graph

def interactive_mode():
    print("Enter your Excel insight queries (type 'exit' to quit):")
    count = 1

    while True:
        query = input(f"\n[{count}] > ").strip()
        if query.lower() == "exit":
            print("\nExiting interactive test.")
            break

        if not query:
            print("Please enter a valid instruction.")
            continue

        state = {
            "user_id": f"test_user_{count}",
            "messages": [{"role": "user", "content": query}],
            "thread_id": f"interactive_test_{count:03}"
        }

        final_state = assistant_graph.invoke(state)
        final_answer = final_state.get("final_answer", "[No answer generated]")

        print(final_answer)
        print("----------------")
        count += 1

if __name__ == "__main__":
    interactive_mode()
