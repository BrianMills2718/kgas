#!/usr/bin/env python3
"""
Quick test of structured output with different models
"""

from universal_model_client import UniversalModelClient
import json

def test_structured_output():
    client = UniversalModelClient()
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 3
            }
        },
        "required": ["name", "age", "skills"],
        "additionalProperties": False
    }
    
    # Test models that should work
    models_to_test = ["gemini_2_5_flash", "o4_mini", "claude_sonnet_4"]
    
    for model in models_to_test:
        try:
            print(f"\n=== Testing {model} ===")
            result = client.complete(
                messages=[{"role": "user", "content": "Create a software developer character"}],
                model=model,
                schema=schema,
                fallback_models=[]  # No fallbacks for individual testing
            )
            
            response_text = result["response"].choices[0].message.content
            print(f"Model used: {result['model_used']}")
            print(f"Native structured output: {result.get('structured_output_native', 'Unknown')}")
            print(f"Response: {response_text}")
            
            # Try to parse JSON
            try:
                parsed = json.loads(response_text)
                print("✅ Valid JSON!")
                print(f"Parsed: {parsed}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
                
        except Exception as e:
            print(f"❌ Error with {model}: {e}")

if __name__ == "__main__":
    test_structured_output()