#!/usr/bin/env python3
"""T23C LLM Extractor using Gemini-2.5-flash - NO FALLBACKS"""

import os
import sys
import json
import litellm
from dotenv import load_dotenv
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

class T23CLLMExtractor:
    """Extract entities using REAL LLM - no mocks, no fallbacks"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY required - no fallbacks allowed")
        
        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params
        self.model = "gemini/gemini-2.0-flash-exp"  # Use working model
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships using Gemini-2.5-flash"""
        
        # Build extraction prompt
        prompt = """You are an expert at extracting entities and relationships from text.
        
Extract ALL entities and relationships from the following text.

Return a valid JSON object with this exact structure:
{
    "entities": [
        {"name": "entity name", "type": "PERSON|ORG|LOC|PRODUCT", "confidence": 0.95}
    ],
    "relationships": [
        {"source": "entity1", "relation": "LED_BY|HEADQUARTERED_IN|ACQUIRED|etc", "target": "entity2", "confidence": 0.9}
    ]
}

Important:
- Extract ALL entities mentioned (people, companies, locations, products)
- Include confidence scores (0.0-1.0)
- Use consistent entity names across entities and relationships
- Common relations: LED_BY, FOUNDED_BY, HEADQUARTERED_IN, ACQUIRED, WORKS_FOR, BASED_IN, PARTNERED_WITH

Text to analyze:
""" + text

        try:
            # Call LLM via LiteLLM
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise entity extraction system. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            # Extract content from response
            if not response or not response.choices:
                raise RuntimeError("No response from LLM")
            
            llm_output = response.choices[0].message.content
            
            if not llm_output:
                raise RuntimeError("Empty response from LLM")
            
            # Parse JSON from LLM response
            # Handle potential markdown code blocks
            if "```json" in llm_output:
                json_str = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                json_str = llm_output.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_output.strip()
            
            extracted_data = json.loads(json_str)
            
            # Add metadata
            result = {
                "extraction_timestamp": datetime.now().isoformat(),
                "model": self.model,
                "text_length": len(text),
                "entities": extracted_data.get("entities", []),
                "relationships": extracted_data.get("relationships", []),
                "raw_llm_response": llm_output
            }
            
            return result
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM returned invalid JSON: {e}\nResponse: {llm_output if 'llm_output' in locals() else 'No response'}")
        except Exception as e:
            import traceback
            raise RuntimeError(f"LLM extraction failed: {e}\nTraceback: {traceback.format_exc()}")