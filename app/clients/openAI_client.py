# app/clients/openAI_client.py
from app.config import OPENAI_API_KEY
from langchain_openai import ChatOpenAI

def get_client(api_key: str = OPENAI_API_KEY, model: str = "gpt-4o", temperature: float = 0.3):
    return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)