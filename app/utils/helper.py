# File: app/utils/helper.py
from langchain.schema import HumanMessage, AIMessage, SystemMessage

"""
Render a compact representation of the conversation window.
"""
def render_message_summary(messages, window_size = 5):
    compact_messages = messages[-window_size:]
    return "\n".join([f"{_role(msg)}: {_content(msg)}" for msg in compact_messages])

def _content(m) -> str:
    return m.get("content", "") if isinstance(m, dict) else getattr(m, "content", "")

def _role(m) -> str:
    if isinstance(m, dict):
        return m.get("role") or m.get("type") or "user"
    if isinstance(m, HumanMessage): return "user"
    if isinstance(m, AIMessage):    return "assistant"
    if isinstance(m, SystemMessage):return "system"
    return getattr(m, "type", "user")

def _last_user_text(msgs) -> str:
    # prefer the most-recent *user* message; fallback to the last message
    for m in reversed(msgs or []):
        if _role(m) == "user":
            return _content(m)
    return _content(msgs[-1]) if msgs else ""