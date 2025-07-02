import openai
from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)
embedding_model = "text-embedding-3-small"

def embed_text(text: str) -> list[float]:
    """
    Embed the given text using OpenAI's embedding model.
    
    Args:
        text (str): The text to embed.
        
    Returns:
        list: The embedding vector for the text.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty or whitespace.")
    
    response = client.embeddings.create(
        input=[text],
        model=embedding_model
    )
    return response.data[0].embedding