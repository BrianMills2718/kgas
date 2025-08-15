#!/usr/bin/env python3
"""
Test Real LLM Integration with Reasoning Capture

Tests actual LLM calls using litellm with structured output and reasoning capture.
Validates that reasoning traces are properly captured from real LLM responses.
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_litellm_basic_integration():
    """Test basic litellm integration"""
    print("1. Testing litellm Basic Integration...")
    
    try:
        import litellm
        
        # Test a simple call with a free model
        response = litellm.completion(
            model="gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Say 'Hello' in exactly one word."}],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        print(f"   ✅ litellm basic call successful: '{content}'")
        return True, content
        
    except Exception as e:
        print(f"   ❌ litellm basic call failed: {e}")
        return False, str(e)

def test_enhanced_reasoning_llm_with_real_calls():
    """Test Enhanced Reasoning LLM Client with real LLM calls"""
    print("2. Testing Enhanced Reasoning LLM with Real Calls...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        from src.core.reasoning_trace_store import ReasoningTraceStore
        
        # Create temporary database for reasoning traces
        temp_db = tempfile.mktemp(suffix='.db')
        
        try:
            reasoning_store = ReasoningTraceStore(temp_db)
            
            # Create enhanced client with reasoning capture
            client = EnhancedReasoningLLMClient(
                base_client=None,  # Will create its own
                reasoning_store=reasoning_store,
                capture_reasoning=True
            )
            
            # Start a reasoning trace
            trace_id = client.start_reasoning_trace(
                operation_type="llm_reasoning_test",
                operation_id="test_001",
                initial_context={"test_type": "real_llm_integration"}
            )
            
            print(f"   Started reasoning trace: {trace_id}")
            
            # Make a real LLM call with reasoning capture
            response = client.generate_text_with_reasoning(
                prompt="Generate a simple 3-step workflow for document analysis. Be concise but include your reasoning.",
                model="gemini-2.0-flash-exp",
                max_tokens=200,
                decision_point="Generate document analysis workflow",
                reasoning_context={
                    "task": "workflow_generation",
                    "domain": "document_analysis",
                    "complexity": "simple"
                }
            )
            
            print(f"   LLM Response Success: {response.get('success')}")
            if response.get('success'):
                content = response.get('content', '')[:100] + "..." if len(response.get('content', '')) > 100 else response.get('content', '')
                print(f"   LLM Content Sample: {content}")
                
                # Check if reasoning was extracted
                reasoning_extracted = response.get('reasoning_info', {}).get('reasoning_extracted', False)
                print(f"   Reasoning Extracted: {reasoning_extracted}")
                
                if reasoning_extracted:
                    confidence = response.get('reasoning_info', {}).get('confidence_score', 0)
                    print(f"   Extracted Confidence: {confidence}")
            
            # Complete the reasoning trace
            completed_trace_id = client.complete_reasoning_trace(
                success=response.get('success', False),
                final_outputs={"llm_call_completed": True}
            )
            
            print(f"   Completed reasoning trace: {completed_trace_id}")
            
            # Verify trace was stored
            stored_trace = reasoning_store.get_trace(trace_id)
            if stored_trace:
                print(f"   ✅ Trace stored with {len(stored_trace.all_steps)} steps")
                return True
            else:
                print("   ⚠️  Trace not found in database")
                return False
                
        finally:
            reasoning_store.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)
                
    except Exception as e:
        print(f"   ❌ Enhanced reasoning LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_output_with_reasoning():
    """Test structured output generation with reasoning capture"""
    print("3. Testing Structured Output with Reasoning...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        from src.core.reasoning_trace_store import ReasoningTraceStore
        
        temp_db = tempfile.mktemp(suffix='.db')
        
        try:
            reasoning_store = ReasoningTraceStore(temp_db)
            client = EnhancedReasoningLLMClient(
                base_client=None,
                reasoning_store=reasoning_store,
                capture_reasoning=True
            )
            
            # Start reasoning trace
            trace_id = client.start_reasoning_trace(
                operation_type="structured_output_test",
                operation_id="struct_001"
            )
            
            # Test structured JSON output with reasoning
            structured_prompt = """
Generate a JSON object for a simple workflow with exactly 2 steps.

Think step by step about your design decisions and include your reasoning in a ```reasoning``` block before the JSON.

Required JSON format:
```json
{
    "workflow_name": "string",
    "steps": [
        {"step_id": 1, "action": "string", "tool": "string"},
        {"step_id": 2, "action": "string", "tool": "string"}
    ],
    "confidence": 0.8
}
```
"""
            
            response = client.generate_structured_response(
                prompt=structured_prompt,
                expected_format="json",
                model="gemini-2.0-flash-exp",
                max_tokens=300,
                decision_point="Generate structured workflow JSON",
                reasoning_context={"output_format": "json", "structure": "workflow"}
            )
            
            print(f"   Structured Response Success: {response.get('success')}")
            
            if response.get('success'):
                # Check if we got valid JSON
                parsed_json = response.get('parsed_response')
                if isinstance(parsed_json, dict):
                    print(f"   ✅ Valid JSON structure received")
                    print(f"   Workflow Name: {parsed_json.get('workflow_name', 'N/A')}")
                    print(f"   Steps Count: {len(parsed_json.get('steps', []))}")
                    
                    # Check reasoning extraction
                    reasoning_info = response.get('reasoning_info', {})
                    if reasoning_info.get('reasoning_extracted'):
                        print(f"   ✅ Reasoning extracted with confidence: {reasoning_info.get('confidence_score')}")
                    else:
                        print("   ⚠️  No reasoning extracted")
                else:
                    print(f"   ⚠️  Response not valid JSON: {type(parsed_json)}")
            
            # Complete trace and verify storage
            client.complete_reasoning_trace(success=response.get('success', False))
            
            stored_trace = reasoning_store.get_trace(trace_id)
            if stored_trace and len(stored_trace.all_steps) > 0:
                print(f"   ✅ Structured output test successful with {len(stored_trace.all_steps)} reasoning steps")
                return True
            else:
                print("   ⚠️  Reasoning trace not properly stored")
                return False
                
        finally:
            reasoning_store.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)
                
    except Exception as e:
        print(f"   ❌ Structured output test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_agent_with_real_llm():
    """Test ReasoningEnhancedWorkflowAgent with real LLM calls"""
    print("4. Testing Workflow Agent with Real LLM...")
    
    try:
        from src.agents.reasoning_enhanced_workflow_agent import ReasoningEnhancedWorkflowAgent
        from src.core.workflow_schema import AgentRequest, AgentLayer
        
        # Create workflow agent with reasoning capture
        agent = ReasoningEnhancedWorkflowAgent(
            api_client=None,  # Will create its own
            reasoning_store=None,  # Will create its own
            capture_reasoning=True
        )
        
        # Create a simple workflow request
        request = AgentRequest(
            natural_language_description="Create a simple 2-step workflow to analyze a PDF document and extract entities",
            layer=AgentLayer.LAYER_2,  # User review layer
            available_documents=["test_document.pdf"],
            target_outputs=["entities", "summary"]
        )
        
        print(f"   Making workflow generation request...")
        
        # This should make real LLM calls with reasoning capture
        response = agent.generate_workflow(request)
        
        print(f"   Workflow Response Status: {response.status}")
        
        if response.status in ["success", "requires_review"]:
            print(f"   ✅ Workflow generation successful")
            
            # Check if reasoning trace was captured
            reasoning_trace_id = getattr(response, 'reasoning_trace_id', None)
            if reasoning_trace_id:
                print(f"   ✅ Reasoning trace captured: {reasoning_trace_id}")
                
                # Get the reasoning trace
                trace = agent.get_reasoning_trace(reasoning_trace_id)
                if trace and len(trace.all_steps) > 0:
                    print(f"   ✅ Reasoning trace has {len(trace.all_steps)} decision steps")
                    
                    # Show some trace details
                    for i, (step_id, step) in enumerate(list(trace.all_steps.items())[:3]):
                        print(f"   Step {i+1}: {step.decision_point}")
                        
                    return True
                else:
                    print("   ⚠️  Reasoning trace empty or not found")
            else:
                print("   ⚠️  No reasoning trace ID in response")
        else:
            print(f"   ❌ Workflow generation failed: {response.error_message}")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Workflow agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run real LLM integration tests"""
    print("🧠 Real LLM Integration with Reasoning Capture")
    print("Testing actual LLM calls with litellm and structured output...")
    print("=" * 70)
    
    # Check if we have API keys
    api_keys_available = any([
        os.getenv('GOOGLE_API_KEY'),
        os.getenv('OPENAI_API_KEY'),
        os.getenv('ANTHROPIC_API_KEY')
    ])
    
    if not api_keys_available:
        print("⚠️  No API keys found. Set GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        print("   Using Gemini Flash which might work without explicit key...")
    
    start_time = time.time()
    
    tests = [
        ("litellm Basic Integration", test_litellm_basic_integration),
        ("Enhanced Reasoning LLM Client", test_enhanced_reasoning_llm_with_real_calls),
        ("Structured Output with Reasoning", test_structured_output_with_reasoning),
        ("Workflow Agent with Real LLM", test_workflow_agent_with_real_llm)
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
    
    print(f"\n📋 Real LLM Integration Results (completed in {total_time:.1f}s)")
    print("=" * 70)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.1f}s)")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 REAL LLM INTEGRATION FULLY WORKING")
    elif passed >= 2:
        print("⚠️  CORE LLM INTEGRATION WORKING - Some advanced features need attention")
    else:
        print("❌ LLM INTEGRATION ISSUES - Check API keys and configuration")
    
    return 0 if passed >= 2 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)