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
        """Get embedding with FAIL-FAST error handling (no fallbacks)"""
        if not text or len(text.strip()) == 0:
            raise ValueError("Cannot embed empty text - text is required for meaningful embedding")
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except AuthenticationError as e:
            print("❌ Invalid API key")
            raise RuntimeError("OpenAI API authentication failed - check OPENAI_API_KEY") from e
        except RateLimitError as e:
            print("❌ Rate limited by OpenAI")
            raise RuntimeError("OpenAI API rate limit exceeded - cannot continue") from e
        except Exception as e:
            print(f"❌ Embedding failed: {e}")
            raise RuntimeError(f"OpenAI embedding API failed: {str(e)}") from e