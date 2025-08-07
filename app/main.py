# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
from app.graph.assistant import assistant_graph  # your LangGraph pipeline

app = FastAPI()

# Enable CORS for your frontend (adjust allowed origins in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use ["http://localhost:5173"] or Vercel domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model from frontend
class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class RequestPayload(BaseModel):
    user_id: str
    thread_id: str
    messages: List[Message]

@app.post("/generate")
async def generate_response(payload: RequestPayload):
    # Assemble state for LangGraph
    state = {
        "user_id": payload.user_id,
        "thread_id": payload.thread_id,
        "messages": [m.dict() for m in payload.messages],
    }

    try:
        result = assistant_graph.invoke(state)
        final_answer = result.get("final_answer", "[No answer generated]")
        return {"final_answer": final_answer}

    except Exception as e:
        return {"final_answer": "[Error in assistant graph]", "error": str(e)}
