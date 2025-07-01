# app/clients/openAI_client.py
from app.config import OPENAI_API_KEY
from openai import OpenAI

def get_client(api_key: str = OPENAI_API_KEY):
    return OpenAI(api_key=api_key)