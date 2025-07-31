from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    thread_id: str
    message: str

class ThreadCreate(BaseModel):
    thread_id: str
    user_id: str
    title: str

class ProfileCreate(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    department: str
    title: str
