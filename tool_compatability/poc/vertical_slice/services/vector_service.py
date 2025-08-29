"""Simple vector embedding service"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('/home/brian/projects/Digimons/.env')

class VectorService:
    """Simple vector embedding service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"
    
    def embed_text(self, text: str) -> list:
        """Get embedding for text"""
        if not text:
            return [0.0] * 1536  # Return zero vector for empty text
        
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding