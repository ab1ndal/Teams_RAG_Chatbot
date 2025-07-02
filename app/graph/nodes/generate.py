# File: app/graph/nodes/generate.py
from typing import Callable
from app.graph.state import AssistantState
from langchain_openai import ChatOpenAI

def generate_answer(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    def _node(state: AssistantState) -> AssistantState:
        if state.get("query_type")=="excel_insight":
            state["final_answer"] = state.get("final_answer", "[No final answer generated]")
            return state
        else:
            #Inputs
            ranked_chunks = state.get("ranked_chunks", [])
            # Deduplicate sources
            path_to_index = {}
            unique_sources = []
            context_blocks = []
            for doc in ranked_chunks:
                snippet = doc['snippet']
                path = doc['metadata']['file_path']
                if path not in path_to_index:
                    path_to_index[path] = len(unique_sources)+1
                    unique_sources.append(path)
                index = path_to_index[path]
                context_blocks.append(f"[{index}] {snippet}")

            sources = "\n".join(f"[{i+1}] {path}" for i, path in enumerate(unique_sources))
            context = "\n\n".join(context_blocks)

            prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.
            Context:
            {context}
            Question: {state['messages'][-1]['content']}
            Answer with inline references like [1], [2], etc., and list sources at the end.
            Sources:
            {sources}
            """
            completion = client.invoke([
                {"role": "system", "content": "You are a helpful assistant. Use the context to answer clearly and professionally."},
                {"role": "user", "content": prompt.strip()}
            ])
            answer = completion.content.strip()
            state["final_answer"] = answer
        return state
    return _node