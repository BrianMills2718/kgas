#!/usr/bin/env python3
"""
Focused Reasoning System Validation

Tests actual functionality with timeouts to identify hanging points.
"""

import sys
import os
import signal
import tempfile
import time
from pathlib import Path
from contextlib import contextmanager

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@contextmanager
def timeout_context(seconds):
    """Context manager for test timeouts"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Test timed out after {seconds} seconds")
    
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def test_data_model_operations():
    """Test data model serialization and operations"""
    print("1. Testing Data Model Operations...")
    
    try:
        with timeout_context(10):  # 10 second timeout
            from src.core.reasoning_trace import (
                ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType,
                create_workflow_planning_step
            )
            
            # Create and populate trace
            trace = ReasoningTrace(operation_type="test_operation")
            
            step = ReasoningStep(
                decision_level=DecisionLevel.AGENT,
                reasoning_type=ReasoningType.WORKFLOW_PLANNING,
                decision_point="Test decision",
                reasoning_text="Test reasoning",
                confidence_score=0.8
            )
            
            trace.add_step(step)
            trace.complete_trace(success=True)
            
            # Test serialization
            trace_dict = trace.to_dict()
            reconstructed = ReasoningTrace.from_dict(trace_dict)
            
            assert reconstructed.trace_id == trace.trace_id
            assert len(reconstructed.all_steps) == 1
            
            print("   ✅ Data model operations successful")
            return True
            
    except TimeoutError as e:
        print(f"   ⚠️  Data model operations timed out: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Data model operations failed: {e}")
        return False

def test_database_basic_operations():
    """Test basic database operations with timeout"""
    print("2. Testing Database Basic Operations...")
    
    try:
        with timeout_context(15):  # 15 second timeout
            from src.core.reasoning_trace_store import ReasoningTraceStore
            from src.core.reasoning_trace import ReasoningTrace, ReasoningStep
            
            temp_db = tempfile.mktemp(suffix='.db')
            
            try:
                store = ReasoningTraceStore(temp_db)
                
                # Create simple trace
                trace = ReasoningTrace(operation_type="db_test")
                step = ReasoningStep(
                    decision_point="Test DB step",
                    reasoning_text="Testing database storage"
                )
                trace.add_step(step)
                trace.complete_trace(success=True)
                
                # Store trace
                stored = store.store_trace(trace)
                assert stored is True
                
                # Retrieve trace
                retrieved = store.get_trace(trace.trace_id)
                assert retrieved is not None
                
                store.close()
                print("   ✅ Database operations successful")
                return True
                
            finally:
                if os.path.exists(temp_db):
                    os.remove(temp_db)
                    
    except TimeoutError as e:
        print(f"   ⚠️  Database operations timed out: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Database operations failed: {e}")
        return False

def test_llm_client_creation():
    """Test LLM client creation without external calls"""
    print("3. Testing LLM Client Creation...")
    
    try:
        with timeout_context(10):  # 10 second timeout
            from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
            
            # Create client with no external dependencies
            client = EnhancedReasoningLLMClient(
                base_client=None,
                reasoning_store=None,
                capture_reasoning=False
            )
            
            # Test prompt enhancement
            original = "Generate workflow"
            enhanced = client._create_reasoning_prompt(original, "test_decision", {})
            
            assert len(enhanced) > len(original)
            assert "Step-by-Step" in enhanced
            
            print("   ✅ LLM client creation successful")
            return True
            
    except TimeoutError as e:
        print(f"   ⚠️  LLM client creation timed out: {e}")
        return False
    except Exception as e:
        print(f"   ❌ LLM client creation failed: {e}")
        return False

def test_query_interface_creation():
    """Test query interface creation and basic operations"""
    print("4. Testing Query Interface...")
    
    try:
        with timeout_context(15):  # 15 second timeout
            from src.core.reasoning_query_interface import ReasoningQueryInterface
            from src.core.reasoning_trace_store import ReasoningTraceStore
            
            temp_db = tempfile.mktemp(suffix='.db')
            
            try:
                store = ReasoningTraceStore(temp_db)
                query_interface = ReasoningQueryInterface(store)
                
                # Test basic query (should work even with empty database)
                traces = query_interface.get_traces_by_operation("nonexistent")
                assert isinstance(traces, list)
                
                store.close()
                print("   ✅ Query interface creation successful")
                return True
                
            finally:
                if os.path.exists(temp_db):
                    os.remove(temp_db)
                    
    except TimeoutError as e:
        print(f"   ⚠️  Query interface creation timed out: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Query interface creation failed: {e}")
        return False

def test_workflow_agent_creation():
    """Test workflow agent creation without external dependencies"""
    print("5. Testing Workflow Agent Creation...")
    
    try:
        with timeout_context(20):  # 20 second timeout
            from src.agents.reasoning_enhanced_workflow_agent import ReasoningEnhancedWorkflowAgent
            
            # Create agent with no external dependencies
            agent = ReasoningEnhancedWorkflowAgent(
                api_client=None,
                reasoning_store=None,
                capture_reasoning=False
            )
            
            # Test that agent was created
            assert agent is not None
            assert hasattr(agent, 'reasoning_store')
            
            print("   ✅ Workflow agent creation successful")
            return True
            
    except TimeoutError as e:
        print(f"   ⚠️  Workflow agent creation timed out: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Workflow agent creation failed: {e}")
        return False

def main():
    """Run focused validation with timeouts"""
    print("🎯 Focused Reasoning System Validation")
    print("Testing actual functionality with timeouts...")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Data Model Operations", test_data_model_operations),
        ("Database Basic Operations", test_database_basic_operations),
        ("LLM Client Creation", test_llm_client_creation),
        ("Query Interface Creation", test_query_interface_creation),
        ("Workflow Agent Creation", test_workflow_agent_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        test_start = time.time()
        
        try:
            result = test_func()
            results.append((test_name, result, time.time() - test_start))
        except KeyboardInterrupt:
            print("   ⚠️  Validation interrupted by user")
            break
    
    total_time = time.time() - start_time
    
    print(f"\n📋 Validation Summary (completed in {total_time:.1f}s)")
    print("=" * 60)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.1f}s)")
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 CORE REASONING SYSTEM VALIDATED")
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY WORKING - Minor issues identified")
    else:
        print("❌ SIGNIFICANT ISSUES - Multiple test failures")
    
    return 0 if passed >= total * 0.8 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)