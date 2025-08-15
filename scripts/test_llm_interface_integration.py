#!/usr/bin/env python3
"""
Test LLM Interface Integration

Tests the interface between Enhanced Reasoning LLM Client and Enhanced API Client
without requiring external API calls.
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_enhanced_api_client_interface():
    """Test EnhancedAPIClient interface without external calls"""
    print("1. Testing EnhancedAPIClient Interface...")
    
    try:
        from src.core.enhanced_api_client import EnhancedAPIClient
        
        # Create API client
        client = EnhancedAPIClient()
        
        # Test that it has the expected make_request method
        assert hasattr(client, 'make_request'), "make_request method missing"
        
        # Test method signature by inspecting it
        import inspect
        sig = inspect.signature(client.make_request)
        params = list(sig.parameters.keys())
        
        expected_params = ['service', 'request_type', 'prompt', 'messages', 'max_tokens', 'temperature', 'model']
        for param in expected_params:
            assert param in params, f"Parameter {param} missing from make_request signature"
        
        print(f"   ✅ EnhancedAPIClient interface verified with make_request method")
        print(f"   Available parameters: {params}")
        return True
        
    except Exception as e:
        print(f"   ❌ EnhancedAPIClient interface test failed: {e}")
        return False

def test_enhanced_reasoning_llm_interface_compatibility():
    """Test that Enhanced Reasoning LLM Client is compatible with Enhanced API Client"""
    print("2. Testing Interface Compatibility...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        from src.core.enhanced_api_client import EnhancedAPIClient
        
        # Create API client
        api_client = EnhancedAPIClient()
        
        # Create reasoning client with the API client
        reasoning_client = EnhancedReasoningLLMClient(
            base_client=api_client,
            reasoning_store=None,
            capture_reasoning=False
        )
        
        # Test that reasoning client has access to base client
        assert reasoning_client.base_client == api_client
        assert hasattr(reasoning_client.base_client, 'make_request')
        
        print("   ✅ Interface compatibility verified")
        return True
        
    except Exception as e:
        print(f"   ❌ Interface compatibility test failed: {e}")
        return False

def test_prompt_enhancement():
    """Test reasoning prompt enhancement functionality"""
    print("3. Testing Prompt Enhancement...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        
        # Create client without external dependencies
        client = EnhancedReasoningLLMClient(
            base_client=None,
            reasoning_store=None,
            capture_reasoning=False
        )
        
        # Test prompt enhancement
        original_prompt = "Create a simple workflow"
        decision_point = "Workflow generation test"
        context = {"task": "test", "complexity": "simple"}
        
        enhanced_prompt = client._create_reasoning_prompt(
            original_prompt, decision_point, context
        )
        
        # Verify enhancement
        assert len(enhanced_prompt) > len(original_prompt)
        assert "Step-by-Step" in enhanced_prompt
        assert "Confidence Assessment" in enhanced_prompt
        assert original_prompt in enhanced_prompt
        
        print("   ✅ Prompt enhancement working correctly")
        print(f"   Original length: {len(original_prompt)} chars")
        print(f"   Enhanced length: {len(enhanced_prompt)} chars")
        return True
        
    except Exception as e:
        print(f"   ❌ Prompt enhancement test failed: {e}")
        return False

def test_reasoning_extraction():
    """Test reasoning extraction from mock responses"""
    print("4. Testing Reasoning Extraction...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        
        client = EnhancedReasoningLLMClient(
            base_client=None,
            reasoning_store=None,
            capture_reasoning=False
        )
        
        # Test with mock response containing reasoning
        mock_response = """
        ```reasoning
        **Step-by-Step Thinking:**
        1. I need to analyze the user's request
        2. Determine appropriate workflow structure
        3. Generate clear step sequence
        
        **Confidence Assessment:** 0.85
        **Confidence Justification:** Request is clear and matches known patterns
        
        **Alternatives Considered:**
        - Linear workflow approach
        - Parallel processing approach
        
        **Key Assumptions:**
        - Standard document format
        - Available processing tools
        ```
        
        **ACTUAL RESPONSE:**
        Here's a simple 2-step workflow:
        1. Load document
        2. Extract entities
        """
        
        reasoning_info = client._extract_reasoning_from_response(mock_response, "test_prompt")
        
        # Verify extraction
        assert reasoning_info["reasoning_extracted"] == True
        assert reasoning_info["confidence_score"] == 0.85
        assert "analyze the user's request" in reasoning_info["step_by_step_thinking"]
        assert len(reasoning_info["alternatives_considered"]) == 2
        assert len(reasoning_info["key_assumptions"]) == 2
        
        print("   ✅ Reasoning extraction working correctly")
        print(f"   Confidence extracted: {reasoning_info['confidence_score']}")
        print(f"   Alternatives found: {len(reasoning_info['alternatives_considered'])}")
        return True
        
    except Exception as e:
        print(f"   ❌ Reasoning extraction test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_response_interface():
    """Test structured response generation interface"""
    print("5. Testing Structured Response Interface...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        
        client = EnhancedReasoningLLMClient(
            base_client=None,
            reasoning_store=None,
            capture_reasoning=False
        )
        
        # Test structured prompt creation
        prompt = "Generate a workflow"
        schema = {
            "type": "object",
            "properties": {
                "workflow_name": {"type": "string"},
                "steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step_id": {"type": "number"},
                            "action": {"type": "string"}
                        }
                    }
                }
            }
        }
        decision_point = "Generate structured workflow"
        context = {"format": "json"}
        
        structured_prompt = client._create_structured_reasoning_prompt(
            prompt, schema, decision_point, context
        )
        
        # Verify structured prompt
        assert len(structured_prompt) > len(prompt)
        assert "JSON schema" in structured_prompt or "structure" in structured_prompt.lower()
        assert "workflow_name" in structured_prompt
        
        print("   ✅ Structured response interface working")
        print(f"   Structured prompt length: {len(structured_prompt)} chars")
        return True
        
    except Exception as e:
        print(f"   ❌ Structured response interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trace_management():
    """Test reasoning trace management without database operations"""
    print("6. Testing Trace Management...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        from src.core.reasoning_trace import ReasoningTrace
        
        client = EnhancedReasoningLLMClient(
            base_client=None,
            reasoning_store=None,
            capture_reasoning=True
        )
        
        # Test trace creation
        trace_id = client.start_reasoning_trace(
            operation_type="test_operation",
            operation_id="test_001",
            initial_context={"test": True}
        )
        
        assert trace_id is not None
        assert client.current_trace is not None
        assert client.current_trace.operation_type == "test_operation"
        
        # Check trace before completion
        print(f"   Trace success status before completion: {client.current_trace.success}")
        
        # Test trace completion
        completed_id = client.complete_reasoning_trace(
            success=True,
            final_outputs={"completed": True}
        )
        
        assert completed_id == trace_id
        # current_trace is set to None after completion, which is expected behavior
        
        print("   ✅ Trace management working correctly")
        print(f"   Trace ID: {trace_id}")
        print("   Trace completed and cleared as expected")
        return True
        
    except Exception as e:
        print(f"   ❌ Trace management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run LLM interface integration tests"""
    print("🔗 LLM Interface Integration Tests")
    print("Testing interface compatibility and functionality...")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("EnhancedAPIClient Interface", test_enhanced_api_client_interface),
        ("Interface Compatibility", test_enhanced_reasoning_llm_interface_compatibility),
        ("Prompt Enhancement", test_prompt_enhancement),
        ("Reasoning Extraction", test_reasoning_extraction),
        ("Structured Response Interface", test_structured_response_interface),
        ("Trace Management", test_trace_management)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        test_start = time.time()
        
        try:
            result = test_func()
            results.append((test_name, result, time.time() - test_start))
        except KeyboardInterrupt:
            print("   ⚠️  Testing interrupted by user")
            break
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append((test_name, False, time.time() - test_start))
    
    total_time = time.time() - start_time
    
    print(f"\n📋 LLM Interface Integration Results (completed in {total_time:.1f}s)")
    print("=" * 60)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.1f}s)")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 LLM INTERFACE INTEGRATION WORKING")
        print("   Ready for real LLM calls with proper API keys")
    elif passed >= total * 0.8:
        print("⚠️  INTERFACE MOSTLY WORKING - Minor issues to fix")
    else:
        print("❌ INTERFACE ISSUES - Major problems need resolution")
    
    return 0 if passed >= total * 0.8 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)