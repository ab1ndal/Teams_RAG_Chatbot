from fastapi import APIRouter
from app.models.schemas import ChatRequest, ThreadCreate
from app.db.supabase_client import supabase_client
from app.graph.assistant import assistant_graph

router = APIRouter()

@router.post("/chat")
def chat(req: ChatRequest):
    supabase_client.table("messages").insert({
        "thread_id": req.thread_id,
        "user_id": req.user_id,
        "role": "user",
        "content": req.message
    }).execute()

    state = {
        "user_id": req.user_id,
        "thread_id": req.thread_id,
        "messages": [{"role": "user", "content": req.message}]
    }

    result = assistant_graph.invoke(state)
    answer = result.get("final_answer", "")

    supabase_client.table("messages").insert({
        "thread_id": req.thread_id,
        "user_id": req.user_id,
        "role": "assistant",
        "content": answer
    }).execute()

    return {"answer": answer}

@router.post("/threads")
def create_thread(thread: ThreadCreate):
    supabase_client.table("threads").insert(thread.model_dump()).execute()
    return {"status": "created", "thread_id": thread.thread_id}

@router.get("/threads")
def get_threads(user_id: str):
    return supabase_client.table("threads").select("*").eq("user_id", user_id).order("created_at").execute().data

@router.get("/messages")
def get_messages(thread_id: str):
    return supabase_client.table("messages").select("*").eq("thread_id", thread_id).order("created_at").execute().data
