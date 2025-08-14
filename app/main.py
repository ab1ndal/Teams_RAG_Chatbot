# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
from app.graph.assistant import assistant_graph  # your LangGraph pipeline
from app.db.supabase_client import supabase_client

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

@app.get("/")
def root():
    return {"status": "Backend is running"}

@app.get("/health")
def health_check():
    return {"ok": True}

@app.post("/generate")
async def generate_response(payload: RequestPayload):
    try:
        # Get prior summary
        prior = (
            supabase_client.table("threads")
            .select("summary", "thread_preview")
            .eq("user_id", payload.user_id)
            .eq("id", payload.thread_id)
            .maybe_single()
            .execute()
        )
        prior_summary = (prior.data or {}).get("summary", "")
        prior_preview = (prior.data or {}).get("thread_preview", "")

        # Trim messages to 5
        last_n = 5
        msgs = [m.dict() if hasattr(m, "dict") else m for m in payload.messages]
        trimmed_msgs = msgs[-last_n:]
        
        # Assemble state for LangGraph
        state = {
            "user_id": payload.user_id,
            "id": payload.thread_id,
            "messages": trimmed_msgs,
            "history": prior_summary or "(none)",
        }

        cfg = {"configurable": {"id": payload.thread_id, "user_id": payload.user_id}}
        result = assistant_graph.invoke(state, config=cfg)
        updated_summary = result.get("history", prior_summary or "")
        preview = result.get("thread_preview", prior_preview or "")
        
        supabase_client.table("threads").upsert({
            "user_id": payload.user_id,
            "id": payload.thread_id,
            "summary": updated_summary,
            "thread_preview": preview
        }).execute()

        
        return {
            "final_answer": result.get("final_answer", "[No answer generated]"),
            "analysis": result.get("analysis", "[No analysis generated]"),
            "code": result.get("code", "[No code generated]"),
            "plot_images": result.get("plot_images", []),
            "thread_preview": preview,
            "updated_summary": updated_summary
        }

    except Exception as e:
        return {
            "final_answer": "[Error in assistant graph]",
            "error": str(e)
        }
