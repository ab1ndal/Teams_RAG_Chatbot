from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can restrict to prod frontend later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
handler = Mangum(app)
