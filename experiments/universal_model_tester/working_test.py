#!/usr/bin/env python3
"""
Working universal client with direct model mapping
"""

from litellm import completion
from dotenv import load_dotenv
import json
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Simple model mapping
MODELS = {
    "gemini_2_5_flash": {
        "litellm_name": "gemini/gemini-2.5-flash",
        "supports_structured": True
    },
    "o4_mini": {
        "litellm_name": "o4-mini", 
        "supports_structured": False
    },
    "claude_sonnet_4": {
        "litellm_name": "claude-sonnet-4-20250514",
        "supports_structured": True
    }
}

def complete_with_fallback(messages, schema=None):
    """Simple completion with fallback"""
    
    # Try models in order
    for model_name, config in MODELS.items():
        try:
            print(f"Trying {model_name}...")
            
            params = {
                "model": config["litellm_name"],
                "messages": messages
            }
            
            # Handle structured output
            if schema:
                if config["supports_structured"]:
                    params["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "output",
                            "schema": schema,
                            "strict": True
                        }
                    }
                else:
                    # Add schema to prompt for o4-mini
                    modified_messages = messages.copy()
                    modified_messages[-1]["content"] += f"\n\nFormat as JSON: {json.dumps(schema)}"
                    params["messages"] = modified_messages
                    params["response_format"] = {"type": "json_object"}
            
            response = completion(**params)
            
            return {
                "response": response,
                "model_used": config["litellm_name"],
                "success": True
            }
            
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    raise Exception("All models failed")

def main():
    """Test the working client"""
    
    # Simple test
    print("=== Simple Test ===")
    result = complete_with_fallback([{"role": "user", "content": "Say hello!"}])
    print(f"Success! Used: {result['model_used']}")
    print(f"Response: {result['response'].choices[0].message.content}")
    
    # Structured output test
    print("\n=== Structured Output Test ===")
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name", "age"],
        "additionalProperties": False
    }
    
    result = complete_with_fallback(
        [{"role": "user", "content": "Create a fictional character"}],
        schema=schema
    )
    print(f"Success! Used: {result['model_used']}")
    print(f"Response: {result['response'].choices[0].message.content}")

if __name__ == "__main__":
    main()