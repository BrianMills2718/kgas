#!/usr/bin/env python3
"""
Gemini Entity Extractor - Real entity extraction using Gemini API
NO MOCKS - This uses the actual Gemini API
"""

import os
import json
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
import litellm

# Load environment variables
load_dotenv('/home/brian/projects/Digimons/.env')

class GeminiEntityExtractor:
    """
    Extract entities from text using Gemini API.
    Real implementation, no mocks.
    """
    
    def __init__(self):
        self.tool_id = "GeminiEntityExtractor"
        self.name = "Gemini Entity Extractor"
        self.input_type = "text"  # Will be mapped to DataType.TEXT
        self.output_type = "entities"  # Will be mapped to DataType.ENTITIES
        
        # Get API key from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Set up litellm
        litellm.api_key = self.api_key
        
    def process(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using Gemini
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dict with extracted entities and metadata
        """
        try:
            # Construct prompt for entity extraction
            prompt = f"""Extract all named entities from the following text. 
For each entity, provide:
1. The entity text
2. The entity type (PERSON, ORGANIZATION, LOCATION, DATE, etc.)
3. A confidence score (0.0 to 1.0)

Return the results as a JSON array of objects with keys: "text", "type", "confidence"

Text to analyze:
{text[:2000]}  # Limit to 2000 chars for API limits

Response (JSON only, no other text):"""

            # Call Gemini API via litellm
            response = litellm.completion(
                model="gemini/gemini-2.0-flash-exp",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=1000
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                # Clean up response if needed
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                entities = json.loads(content)
                
                # Ensure it's a list
                if not isinstance(entities, list):
                    entities = []
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract entities manually
                entities = []
                print(f"Warning: Could not parse JSON from Gemini response: {content[:200]}")
            
            return {
                'entities': entities,
                'source_text': text[:500],  # First 500 chars
                'entity_count': len(entities),
                'api_response': content[:500],  # For evidence
                'model': 'gemini/gemini-2.0-flash-exp'
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract entities: {e}")