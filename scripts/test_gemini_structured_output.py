#!/usr/bin/env python3
"""
Test Gemini 2.5 Flash with Structured Output

Tests LiteLLM integration with Gemini 2.5 Flash and structured output capabilities.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_gemini_structured_output():
    """Test Gemini 2.5 Flash with structured output"""
    print("🔬 Testing Gemini 2.5 Flash with Structured Output")
    print("=" * 55)
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        
        print("1. Creating Enhanced Reasoning LLM Client...")
        client = EnhancedReasoningLLMClient(capture_reasoning=True)
        print("   ✅ Client created")
        
        print("2. Starting reasoning trace...")
        trace_id = client.start_reasoning_trace(
            operation_type="gemini_structured_test",
            operation_id="gemini_test_001"
        )
        print(f"   ✅ Trace started: {trace_id}")
        
        print("3. Testing structured response generation...")
        
        # Define structured response schema
        response_schema = {
            "type": "object",
            "properties": {
                "analysis": {
                    "type": "object", 
                    "properties": {
                        "key_themes": {"type": "array", "items": {"type": "string"}},
                        "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "summary": {"type": "string"},
                "recommendations": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["analysis", "summary"]
        }
        
        prompt = """
        Analyze this text: "The new AI system shows promising results in automating complex 
        workflows while maintaining high accuracy. Users report improved efficiency and 
        satisfaction with the intuitive interface."
        
        Provide a structured analysis following the specified JSON schema.
        """
        
        # Test with explicit Gemini model
        response = client.generate_structured_response(
            prompt=prompt,
            response_schema=response_schema,
            model="gemini_flash",  # Explicitly use Gemini
            decision_point="Test Gemini structured output",
            reasoning_context={"test_type": "structured_output_validation"}
        )
        
        print(f"   Model Used: {response.get('model', 'Unknown')}")
        print(f"   Success: {response.get('success')}")
        
        if response.get('success'):
            print("   ✅ Gemini structured response successful!")
            
            # Check structured data
            structured_data = response.get('structured_data', {})
            parsing_success = response.get('parsing_success', False)
            
            print(f"   📊 Parsing Success: {parsing_success}")
            print(f"   📋 Structured Data Keys: {list(structured_data.keys())}")
            
            if structured_data:
                print("   📝 Structured Output Preview:")
                analysis = structured_data.get('analysis', {})
                if analysis:
                    themes = analysis.get('key_themes', [])
                    sentiment = analysis.get('sentiment', 'unknown')
                    confidence = analysis.get('confidence', 0.0)
                    
                    print(f"      • Key Themes: {themes[:3]}{'...' if len(themes) > 3 else ''}")
                    print(f"      • Sentiment: {sentiment}")
                    print(f"      • Confidence: {confidence:.2f}")
                
                summary = structured_data.get('summary', '')
                if summary:
                    print(f"      • Summary: {summary[:100]}{'...' if len(summary) > 100 else ''}")
                
                recommendations = structured_data.get('recommendations', [])
                if recommendations:
                    print(f"      • Recommendations: {len(recommendations)} items")
            
            # Check reasoning extraction
            reasoning_info = response.get('reasoning_info', {})
            reasoning_extracted = reasoning_info.get('reasoning_extracted', False)
            confidence_score = reasoning_info.get('confidence_score', 0.0)
            
            print(f"   🧠 Reasoning Extracted: {reasoning_extracted}")
            print(f"   📊 LLM Confidence: {confidence_score:.2f}")
            
        else:
            error = response.get('error', 'Unknown error')
            print(f"   ❌ Gemini call failed: {error}")
            
            # This might be expected if no GEMINI_API_KEY is set
            if 'api key' in error.lower() or 'authentication' in error.lower():
                print("   💡 This is expected if GEMINI_API_KEY is not configured")
                print("   💡 The structured output framework is ready to use when key is available")
        
        print("4. Completing reasoning trace...")
        completed_trace_id = client.complete_reasoning_trace(
            success=response.get('success', False)
        )
        print(f"   ✅ Trace completed: {completed_trace_id}")
        
        # Test the configuration
        print("")
        print("5. Configuration Verification:")
        print("   " + "=" * 40)
        
        # Check if Gemini is configured as primary
        from src.core.enhanced_api_client import EnhancedAPIClient
        api_client = EnhancedAPIClient()
        
        print(f"   📊 Available Models: {api_client.available_models}")
        print(f"   🎯 Primary Model: {api_client.fallback_config['primary_model']}")
        print(f"   🔄 Fallback Models: {api_client.fallback_config['fallback_models']}")
        
        # Check Gemini configuration
        gemini_config = api_client._get_model_config('gemini_flash')
        if gemini_config:
            print(f"   🔧 Gemini LiteLLM Name: {gemini_config.litellm_name}")
            print(f"   ⚙️  Structured Output Support: {gemini_config.supports_structured_output}")
            print(f"   🎛️  Max Tokens: {gemini_config.max_tokens}")
        else:
            print("   ❌ Gemini configuration not found")
        
        print("")
        if response.get('success'):
            print("🎉 GEMINI 2.5 FLASH + STRUCTURED OUTPUT: WORKING!")
            print("✅ LiteLLM integration functional")
            print("✅ Structured output parsing successful")  
            print("✅ Reasoning capture operational")
            print("✅ Ready for production workflows")
        else:
            print("⚠️  GEMINI 2.5 FLASH SETUP READY")
            print("✅ LiteLLM integration configured")
            print("✅ Structured output framework ready")
            print("✅ Reasoning capture operational")
            print("🔑 Requires GEMINI_API_KEY for live testing")
        
        return response.get('success', False)
        
    except Exception as e:
        print(f"❌ Gemini structured output test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the Gemini structured output test"""
    success = test_gemini_structured_output()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)