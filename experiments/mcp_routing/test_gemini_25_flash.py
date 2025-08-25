#!/usr/bin/env python3
"""
Test the new Gemini-2.5-flash model to ensure it's available and working
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

async def test_gemini_25_flash():
    """Test the new Gemini-2.5-flash model"""
    
    print("🔍 Testing Gemini-2.5-flash (latest model)...")
    print(f"Google API Key: {os.getenv('GOOGLE_API_KEY')[:20]}...")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Try the new model with full path
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        print("\n📝 Testing tool selection with Gemini-2.5-flash...")
        
        prompt = """You are a tool selection expert for knowledge graph workflows. Select the best tools for this task.

WORKFLOW: Analyze an academic research paper to extract key methodological contributions and relationships

CONTEXT: {
  "document_type": "academic_paper",
  "domain": "machine_learning", 
  "complexity": "high",
  "expected_entities": ["methods", "algorithms", "datasets", "metrics"]
}

AVAILABLE TOOLS:
1. load_document_comprehensive: Load document with full metadata extraction
2. load_document_basic: Basic document loading without metadata
3. extract_knowledge_graph: Extract entities and relationships from text
4. analyze_graph_insights: Analyze knowledge graph for patterns and insights
5. export_results_comprehensive: Export comprehensive results

Select the most appropriate tools with their parameters. Return JSON:
[
  {
    "tool": "exact_tool_name",
    "parameters": {"param1": "value1"},
    "reasoning": "why this tool is optimal"
  }
]

Respond with only the JSON array."""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 1000,
            }
        )
        
        print(f"✅ Response received from Gemini-2.5-flash!")
        print(f"📄 Raw response length: {len(response.text)} characters")
        print(f"📄 Raw response preview: {response.text[:200]}...")
        
        # Try to parse the JSON
        response_text = response.text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        try:
            parsed_tools = json.loads(response_text)
            print(f"✅ JSON parsed successfully!")
            print(f"🛠️  Selected {len(parsed_tools)} tools:")
            
            for i, tool in enumerate(parsed_tools, 1):
                print(f"   {i}. {tool.get('tool', 'unknown')}")
                if tool.get('parameters'):
                    print(f"      Parameters: {tool['parameters']}")
                if tool.get('reasoning'):
                    print(f"      Reasoning: {tool['reasoning'][:100]}...")
                    
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw text to parse: {response_text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini-2.5-flash: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_25_flash())
    if success:
        print("\n✅ Gemini-2.5-flash is working correctly!")
        print("🚀 Ready to run full validation with the latest model.")
    else:
        print("\n❌ Gemini-2.5-flash test failed.")
        print("🔍 May need to check model availability or API access.")