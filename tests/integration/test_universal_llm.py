#!/usr/bin/env python3
"""
Test Universal LLM Kit directly
"""

import sys
import os
sys.path.append('/home/brian/projects/Digimons/universal_llm_kit')
sys.path.append('/home/brian/projects/Digimons/src/orchestration')

from dotenv import load_dotenv
load_dotenv()

def test_universal_llm():
    """Test Universal LLM Kit structured output"""
    print("Testing Universal LLM Kit...")
    
    try:
        from universal_llm import structured
        from reasoning_schema import ReasoningResponse
        
        print("✅ Imports successful")
        
        # Simple test
        prompt = "Analyze this task: Create a simple plan for organizing files"
        
        print("Making structured API call...")
        response = structured(prompt, ReasoningResponse)
        
        print(f"✅ Response received: {type(response)}")
        print(f"Response length: {len(response)} characters")
        print(f"Response preview: {response[:200]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_universal_llm()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")