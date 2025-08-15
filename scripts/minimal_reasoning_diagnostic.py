#!/usr/bin/env python3
"""
Minimal Reasoning System Diagnostic

Ultra-minimal validation to identify what's working and what causes timeouts.
Tests one component at a time with immediate feedback.
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test if core modules can be imported"""
    print("1. Testing Basic Imports...")
    
    try:
        from src.core.reasoning_trace import ReasoningTrace, ReasoningStep
        print("   ✅ reasoning_trace module imported")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_data_models():
    """Test basic data model creation"""
    print("2. Testing Data Model Creation...")
    
    try:
        from src.core.reasoning_trace import ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType
        
        # Create simple step
        step = ReasoningStep()
        print(f"   ✅ Basic ReasoningStep created: {step.step_id}")
        
        # Create simple trace
        trace = ReasoningTrace()
        print(f"   ✅ Basic ReasoningTrace created: {trace.trace_id}")
        
        return True
    except Exception as e:
        print(f"   ❌ Data model creation failed: {e}")
        traceback.print_exc()
        return False

def test_database_import():
    """Test if database store can be imported"""
    print("3. Testing Database Store Import...")
    
    try:
        from src.core.reasoning_trace_store import ReasoningTraceStore
        print("   ✅ ReasoningTraceStore imported")
        return True
    except Exception as e:
        print(f"   ❌ Database store import failed: {e}")
        traceback.print_exc()
        return False

def test_minimal_database():
    """Test minimal database creation (no operations)"""
    print("4. Testing Minimal Database Creation...")
    
    try:
        from src.core.reasoning_trace_store import ReasoningTraceStore
        import tempfile
        
        temp_db = tempfile.mktemp(suffix='.db')
        print(f"   Creating temp database: {temp_db}")
        
        # Just create store, don't do operations
        store = ReasoningTraceStore(temp_db)
        print("   ✅ Database store created successfully")
        
        store.close()
        
        # Clean up
        if os.path.exists(temp_db):
            os.remove(temp_db)
        
        return True
    except Exception as e:
        print(f"   ❌ Database creation failed: {e}")
        traceback.print_exc()
        return False

def test_llm_client_import():
    """Test LLM client import"""
    print("5. Testing LLM Client Import...")
    
    try:
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        print("   ✅ EnhancedReasoningLLMClient imported")
        return True
    except Exception as e:
        print(f"   ❌ LLM client import failed: {e}")
        traceback.print_exc()
        return False

def test_query_interface_import():
    """Test query interface import"""
    print("6. Testing Query Interface Import...")
    
    try:
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        print("   ✅ ReasoningQueryInterface imported")
        return True
    except Exception as e:
        print(f"   ❌ Query interface import failed: {e}")
        traceback.print_exc()
        return False

def test_workflow_agent_import():
    """Test workflow agent import"""
    print("7. Testing Workflow Agent Import...")
    
    try:
        from src.agents.reasoning_enhanced_workflow_agent import ReasoningEnhancedWorkflowAgent
        print("   ✅ ReasoningEnhancedWorkflowAgent imported")
        return True
    except Exception as e:
        print(f"   ❌ Workflow agent import failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run minimal diagnostic"""
    print("🔍 Minimal Reasoning System Diagnostic")
    print("Testing core components one at a time...")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_data_models,
        test_database_import,
        test_minimal_database,
        test_llm_client_import,
        test_query_interface_import,
        test_workflow_agent_import
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
            if not result:
                print("   ⚠️  Stopping at first failure for debugging")
                break
        except KeyboardInterrupt:
            print("   ⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)
            break
    
    print("\n📋 Diagnostic Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Tests completed: {total}")
    print(f"Tests passed: {passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%" if total > 0 else "No tests completed")
    
    if passed == total:
        print("🎉 ALL BASIC COMPONENTS WORKING")
    elif passed > 0:
        print("⚠️  PARTIAL SUCCESS - Some components working")
    else:
        print("❌ CORE ISSUES - Basic components not working")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)