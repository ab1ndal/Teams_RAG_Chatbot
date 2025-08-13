# File: app/utils/helper.py

"""
Render a compact representation of the conversation window.
"""
def render_message_summary(messages, window_size = 5):
    compact_messages = messages[-window_size:]
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in compact_messages])
