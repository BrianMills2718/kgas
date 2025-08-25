#!/usr/bin/env python3
"""
Debug Gemini API response format to understand JSON parsing issue
"""

import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from dotenv import load_dotenv
load_dotenv()

def test_gemini_response():
    """Test what Gemini actually returns"""
    print("Testing raw Gemini API response...")
    
    try:
        import google.generativeai as genai
        
        # Check API key
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not gemini_key:
            print("❌ No Gemini API key found")
            return False
        
        print(f"✅ Gemini API key found: {gemini_key[:10]}...")
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        
        # Create the model - use Gemini 2.5 Flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Simple test prompt that should return JSON
        test_prompt = """
Please respond with a JSON object containing:
- reasoning_chain: Array of reasoning steps  
- decision: Object with decisions
- confidence: Number between 0.0 and 1.0
- explanation: String explanation

IMPORTANT: Response must be valid JSON only. Use this exact format:
{"reasoning_chain": ["step1", "step2"], "decision": {"approach": "value"}, "confidence": 0.8, "explanation": "brief explanation"}
"""
        
        print("Sending test prompt to Gemini...")
        
        # Generate response with higher token limit
        response = model.generate_content(
            test_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4000,  # Increased to match fix
            )
        )
        
        print(f"✅ Gemini response received")
        print(f"Response type: {type(response.text)}")
        print(f"Response length: {len(response.text)} characters")
        print("\n" + "="*60)
        print("RAW GEMINI RESPONSE:")
        print("="*60)
        print(repr(response.text))
        print("="*60)
        print("FORMATTED GEMINI RESPONSE:")
        print("="*60)
        print(response.text)
        print("="*60)
        
        # Test JSON parsing
        import json
        print("\nTesting JSON parsing...")
        
        try:
            # Try direct parsing
            parsed = json.loads(response.text)
            print("✅ Direct JSON parsing successful")
            print(f"Parsed keys: {list(parsed.keys())}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Direct JSON parsing failed: {e}")
            
            # Try extracting from markdown
            print("Attempting markdown extraction...")
            cleaned = response.text.strip()
            
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:].strip()
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3].strip()
                    
                print(f"Extracted from markdown: {repr(cleaned)}")
                
                try:
                    parsed = json.loads(cleaned)
                    print("✅ Markdown extraction successful")
                    print(f"Parsed keys: {list(parsed.keys())}")
                    return True
                except json.JSONDecodeError as e2:
                    print(f"❌ Markdown extraction failed: {e2}")
            
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini_response()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")