"""Simple vector embedding service"""
import os
import time
from openai import OpenAI, AuthenticationError, RateLimitError
from dotenv import load_dotenv

load_dotenv('/home/brian/projects/Digimons/.env')

class VectorService:
    """Simple vector embedding service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"
    
    def embed_text(self, text: str) -> list:
        """Get embedding with error handling"""
        if not text:
            return [0.0] * 1536
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except AuthenticationError:
            print("❌ Invalid API key")
            raise
        except RateLimitError:
            print("⚠️ Rate limited, waiting 1s...")
            time.sleep(1)
            return self.embed_text(text)  # Retry once
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            return [0.0] * 1536  # Fallback to zero vector