#!/usr/bin/env python3
"""
OpenAI-based embedding service for analytics integration
Implements the same interface as RealEmbeddingService but uses OpenAI API
"""

import asyncio
import logging
import os
from typing import List, Dict, Any
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """OpenAI-based embedding service compatible with analytics components"""
    
    def __init__(self):
        """Initialize OpenAI embedding service"""
        # Load environment
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"
        self.embedding_dim = 1536  # text-embedding-3-small dimensions
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        logger.info(f"Initialized OpenAI embedding service with model: {self.model}")
    
    async def generate_text_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text inputs using OpenAI API
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)
        
        try:
            # Filter out empty texts
            valid_texts = [text.strip() for text in texts if text and text.strip()]
            if not valid_texts:
                raise ValueError("No valid text inputs provided")
            
            # Get embeddings from OpenAI
            response = self.client.embeddings.create(
                input=valid_texts,
                model=self.model
            )
            
            # Convert to numpy array
            embeddings = np.array([embedding.embedding for embedding in response.data])
            
            logger.debug(f"Generated embeddings for {len(valid_texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate text embeddings: {e}")
            raise RuntimeError(f"OpenAI embedding generation failed: {str(e)}") from e
    
    async def generate_image_embeddings(self, image_paths: List[str]) -> np.ndarray:
        """Generate embeddings for images - NOT SUPPORTED with OpenAI text embeddings
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Empty array - images not supported
        """
        logger.warning("Image embeddings not supported with OpenAI text embedding service")
        # Return empty array with correct shape
        return np.array([]).reshape(0, self.embedding_dim)
    
    async def generate_structured_embeddings(self, structured_data: List[Dict[str, Any]]) -> np.ndarray:
        """Generate embeddings for structured data by converting to text
        
        Args:
            structured_data: List of structured data dictionaries
            
        Returns:
            numpy array of embeddings
        """
        if not structured_data:
            return np.array([]).reshape(0, self.embedding_dim)
        
        try:
            # Convert structured data to text representations
            texts = []
            for data in structured_data:
                if isinstance(data, dict):
                    # Convert dict to readable text
                    text_parts = []
                    for key, value in data.items():
                        text_parts.append(f"{key}: {str(value)}")
                    texts.append(", ".join(text_parts))
                else:
                    texts.append(str(data))
            
            # Generate embeddings for text representations
            return await self.generate_text_embeddings(texts)
            
        except Exception as e:
            logger.error(f"Failed to generate structured embeddings: {e}")
            raise RuntimeError(f"Structured embedding generation failed: {str(e)}") from e
    
    def get_embedding_dimensions(self) -> Dict[str, int]:
        """Get embedding dimensions for different modalities
        
        Returns:
            Dictionary with dimension info
        """
        return {
            "text": self.embedding_dim,
            "image": 0,  # Not supported
            "structured": self.embedding_dim
        }
    
    async def close(self):
        """Close connections (no-op for OpenAI client)"""
        logger.info("OpenAI embedding service closed")
        pass


# Test the service
if __name__ == "__main__":
    async def test_service():
        service = OpenAIEmbeddingService()
        
        # Test text embeddings
        test_texts = ["Hello world", "This is a test", "OpenAI embeddings work great"]
        embeddings = await service.generate_text_embeddings(test_texts)
        
        print(f"✅ Generated embeddings: {embeddings.shape}")
        print(f"Dimensions: {service.get_embedding_dimensions()}")
        
        await service.close()
    
    asyncio.run(test_service())