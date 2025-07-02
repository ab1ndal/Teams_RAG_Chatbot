# File: app/graph/nodes/generate.py
from typing import Callable
from app.graph.state import AssistantState
from langchain_openai import ChatOpenAI

def generate_answer(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        if state.get("query_type")=="excel_insight":
            state["final_answer"] = state.get("final_answer", "[No final answer generated]")
        else:
            sources = "\n".join([f"[{i+1}] {doc['metadata']['source']}" for i, doc in enumerate(state['ranked_chunks'])])
            context = "\n\n".join([f"[{i+1}] {doc['content']}" for i, doc in enumerate(state['ranked_chunks'])])

            prompt = f"""
            You are a helpful assistant. Use the following context to answer the user's question.
            Context:
            {context}
            Question: {state['query']}
            Answer with inline references like [1], [2], etc., and list sources at the end.
            Sources:
            {sources}
            """
            completion = client.invoke([
                {"role": "system", "content": "You are a helpful assistant. Use the context to answer clearly and professionally."},
                {"role": "user", "content": prompt}
            ])
            answer = completion.content.strip()
            state["final_answer"] = answer
        return state
    return _node