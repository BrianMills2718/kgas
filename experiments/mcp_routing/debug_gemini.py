#!/usr/bin/env python3
"""
Debug Gemini API responses to understand what's happening
"""

import os
import asyncio
import json
from pathlib import Path

# Load environment variables
def load_env():
    env_path = Path("/home/brian/projects/Digimons/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

async def test_gemini_direct():
    """Test Gemini API directly to see what's happening"""
    
    print("🔍 Testing Gemini API directly...")
    print(f"Google API Key: {os.getenv('GOOGLE_API_KEY')[:20]}...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("\n📝 Testing simple prompt...")
        
        response = model.generate_content(
            "Hello! Please respond with a simple JSON: {\"message\": \"hello from gemini\"}",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 100,
            }
        )
        
        print(f"✅ Response received!")
        print(f"📄 Raw response text: '{response.text}'")
        print(f"📊 Response length: {len(response.text)} characters")
        
        if response.text.strip():
            print("✅ Non-empty response received")
            try:
                # Try to parse as JSON
                if '{' in response.text:
                    json_part = response.text[response.text.find('{'):response.text.rfind('}')+1]
                    parsed = json.loads(json_part)
                    print(f"✅ JSON parsed successfully: {parsed}")
                else:
                    print("⚠️ No JSON found in response")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
        else:
            print("❌ Empty response received")
            
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())