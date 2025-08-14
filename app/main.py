# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Literal, Dict, Any
import json
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

# Optional: nice labels for your nodes as they appear
STEP_LABELS: Dict[str, str] = {
    "rewrite_query": "Rewriting Query...",
    "classify_query": "Classify Query...",
    "retrieve_pinecone": "Retrieving info...",
    "rerank_chunks": "Reranking chunks...",
    "generate_code": "Generating code...",
    "execute_code": "Executing code...",
    "match_rfis": "Matching RFIs...",
    "rfi_combine_context": "Combining RFI context...",
    "generate_answer": "Drafting Answer...",
    "respond": "Responding...",
    "check_query": "Checking query...",
}


def ndjson(event_type: str, data: Dict[str, Any]) -> str:
    return json.dumps({"type": event_type, "data": data}) + "\n"

@app.post("/generate-stream")
async def generate_stream(payload: RequestPayload):
    try:
        # 1) Fetch prior summary/preview (same as /generate)
        prior = (
            supabase_client.table("threads")
            .select("summary", "thread_preview")
            .eq("user_id", payload.user_id)
            .eq("id", payload.thread_id)
            .maybe_single()
            .execute()
        )
        prior_summary = (prior.data or {}).get("summary", "") or ""
        prior_preview = (prior.data or {}).get("thread_preview", "") or ""

        # 2) Trim messages to last 5 (same as /generate)
        last_n = 5
        msgs = [m.dict() if hasattr(m, "dict") else m for m in payload.messages]
        trimmed_msgs = msgs[-last_n:]

        # 3) Assemble state and config (same as /generate)
        state = {
            "user_id": payload.user_id,
            "id": payload.thread_id,
            "messages": trimmed_msgs,
            "history": prior_summary or "(none)",
        }
        cfg = {"configurable": {"id": payload.thread_id, "user_id": payload.user_id}}

        # 4) Stream LangGraph updates as NDJSON
        async def gen():
            yield _ndjson("status", {"stage": "started"})

            last_history = prior_summary
            last_preview = prior_preview
            last_answer = None

            # NOTE: .stream(...) should yield per-node updates/diffs
            for update in assistant_graph.stream(state, config=cfg, stream_mode="updates"):
                # update may be {"node_name": {...}} or include a "path"
                if isinstance(update, dict):
                    for node_name, data in update.items():
                        label = STEP_LABELS.get(str(node_name), str(node_name))
                        # announce node progress
                        yield _ndjson("status", {"stage": "node", "node": node_name, "label": label})

                        if isinstance(data, dict):
                            # forward interesting partials if present
                            if "analysis" in data:
                                yield _ndjson("analysis_partial", {"text": data["analysis"]})
                            if "code" in data:
                                yield _ndjson("code_partial", {"code": data["code"]})
                            if "output" in data:
                                yield _ndjson("output_partial", {"text": data["output"]})
                            if "plot_images" in data:
                                yield _ndjson("plots", {"images": data["plot_images"]})
                            if "final_answer" in data:
                                last_answer = data["final_answer"]
                                yield _ndjson("final_partial", {"text": last_answer})
                            if "history" in data:
                                last_history = data["history"] or last_history
                            if "thread_preview" in data:
                                last_preview = data["thread_preview"] or last_preview

            # 5) Persist summary/preview at the end (same as /generate)
            supabase_client.table("threads").upsert({
                "user_id": payload.user_id,
                "id": payload.thread_id,
                "summary": last_history or prior_summary or "",
                "thread_preview": last_preview or prior_preview or "",
            }).execute()

            yield _ndjson("done", {
                "thread_preview": last_preview or "",
                "updated_summary": last_history or "",
                # you can echo last_answer if you want a final payload too
            })

        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # if behind nginx
        }
        return StreamingResponse(gen(), media_type="application/x-ndjson", headers=headers)

    except Exception as e:
        # stream a single error event so the UI can show it
        async def gen_err():
            yield _ndjson("error", {"message": str(e)})
            yield _ndjson("done", {})
        return StreamingResponse(gen_err(), media_type="application/x-ndjson")

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
