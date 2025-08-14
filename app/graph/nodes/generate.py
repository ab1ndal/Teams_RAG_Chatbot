# File: app/graph/nodes/generate.py
from typing import Callable, Dict, List
from app.graph.state import AssistantState
from app.utils import helper
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, ValidationError
import json
import re

class ResponsePayload(BaseModel):
    answer: str = Field(..., description="Final answer text with inline refs like [1], [2], etc., and a Sources list at the end.")
    updated_summary: str = Field(..., description="Compact running summary (<=300 words)")
    thread_preview: str = Field(..., description="Compact running conversation history (5 words)")

def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json)?\n?|\n?```$", "", t, flags=re.IGNORECASE)
    return t.strip()

def generate_answer(client: ChatOpenAI) -> Callable[[AssistantState], AssistantState]:
    structured = client.with_structured_output(ResponsePayload)
    def _node(state: AssistantState) -> AssistantState:
        print("Generating answer...")
        if state.get("query_type")=="excel_insight":
            state["final_answer"] = state.get("final_answer", "[No final answer generated]")
            return state
        else:
            #Inputs
            ranked_chunks = state.get("ranked_chunks", [])
            # Deduplicate sources
            path_to_index: Dict[str, int] = {}
            unique_sources: List[str] = []
            context_blocks: List[str] = []
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

            recent_history = helper.render_message_summary(state.get('messages', []), window_size=5)

            system_msg = (
            "You answer STRICTLY using the provided context only. "
            "If the answer is not fully supported by the context, say exactly: "
            "'Not found in provided sources.' "
            "Every substantive sentence MUST include an inline reference like [1], [2], etc. "
            "End with a 'Sources:' list that matches the inline indices. "
            "Return ONLY the schema fields (answer, updated_summary, thread_preview)."
            )

            user_msg = f"""
            Answer the user, update the thread preview (summary of the latest message and the recent turns in 5 words or less), AND update a compact running summary (<=300 words), focus on decisions, assumptions, sources, constraints, and any unresolved issues.

            Guidelines for the "answer" field:
            - The "answer" must be supported by the context only. If the answer is not fully supported by the context, say exactly: 'Not found in provided sources.'
            - Every substantive sentence MUST include an inline reference like [1], [2], etc.
            - End with a 'Sources:' list that matches the inline indices.
            ----
            Current Summary (may be "(none)"):
            {state.get('history', '(none)')}

            Recent turns:
            {recent_history}

            Retreived Context:
            {context}

            Sources:
            {sources}

            User Question: 
            {state.get('rewritten_query', "")}
            """

            try:
                response: ResponsePayload = structured.invoke([
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
                ])
                state["history"] = response.updated_summary
                state["final_answer"] = response.answer
                state["thread_preview"] = response.thread_preview
                return state
            except ValidationError as e:
                # Extremely rare: try one cheap repair pass on raw content
                raw = client.invoke([
                    {"role": "system", "content": "You are a strict JSON emitter. Output a JSON object with keys: answer, updated_summary. No prose, no fences."},
                    {"role": "user", "content": user_msg}
                ]).content
                raw = _strip_code_fences(raw)
                try:
                    data = json.loads(raw)
                    state["history"] = data["updated_summary"]
                    state["final_answer"] = data["answer"]
                    state["thread_preview"] = data["thread_preview"]
                except Exception as e:
                    state["error"] = f"❌ Failed to parse JSON: {e}"
            return state
    return _node