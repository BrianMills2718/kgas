#!/usr/bin/env python3
"""
Check what Gemini models are actually available with our API key
"""

import os
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

def check_available_models():
    """Check what Gemini models are available"""
    
    print("🔍 Checking available Gemini models...")
    print(f"Google API Key: {os.getenv('GOOGLE_API_KEY')[:20]}...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        print("\n📋 Listing available models...")
        
        models = genai.list_models()
        gemini_models = []
        
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models.append(model.name)
                print(f"   ✅ {model.name}")
                if hasattr(model, 'display_name'):
                    print(f"      Display name: {model.display_name}")
                if hasattr(model, 'description'):
                    print(f"      Description: {model.description[:100]}...")
        
        if not gemini_models:
            print("   ❌ No Gemini models found")
        
        print(f"\n🔍 Found {len(gemini_models)} Gemini model(s)")
        
        # Test each model with a simple prompt
        print("\n🧪 Testing each model...")
        for model_name in gemini_models[:3]:  # Test first 3 models
            try:
                print(f"\nTesting {model_name}...")
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content(
                    "Hello! Please respond with just: OK",
                    generation_config={
                        "temperature": 0.1,
                        "max_output_tokens": 10,
                    }
                )
                
                if response.text and response.text.strip():
                    print(f"   ✅ {model_name}: Working (response: '{response.text.strip()}')")
                else:
                    print(f"   ❌ {model_name}: Empty response")
                    
            except Exception as e:
                print(f"   ❌ {model_name}: Error - {e}")
        
        return gemini_models
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    available_models = check_available_models()
    
    if available_models:
        print(f"\n✅ Found {len(available_models)} Gemini models")
        print("🎯 Recommended model for validation:")
        
        # Check for the latest models first
        priority_models = ['gemini-2.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-flash', 'gemini-pro']
        
        for priority in priority_models:
            matching = [m for m in available_models if priority in m.lower()]
            if matching:
                print(f"   🚀 {matching[0]} (latest priority model found)")
                break
        else:
            print(f"   🚀 {available_models[0]} (first available model)")
    else:
        print("\n❌ No Gemini models available")
        print("🔍 Check API key permissions or Google AI Studio access")