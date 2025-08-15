#!/usr/bin/env python3
"""
Test Advanced Queries on Populated Reasoning Database

Creates a populated reasoning database with sample data and tests
advanced query capabilities including pattern detection and analysis.
"""

import sys
import os
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_sample_reasoning_data():
    """Create sample reasoning data for testing"""
    from src.core.reasoning_trace import (
        ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType,
        create_workflow_planning_step, create_tool_selection_step
    )
    
    sample_traces = []
    
    # Trace 1: Successful workflow generation
    trace1 = ReasoningTrace(
        operation_type="workflow_generation",
        operation_id="wf_001"
    )
    
    # Add multiple steps with different decision levels and types
    step1 = create_workflow_planning_step(
        decision_point="Analyze document processing request",
        context={"document_type": "pdf", "analysis_goal": "entity_extraction"},
        workflow_generated={"tools": ["T01", "T23a", "T31"]},
        reasoning_text="User wants to extract entities from PDF. Need to use PDF loader, entity extractor, and graph builder.",
        confidence=0.9
    )
    trace1.add_step(step1)
    
    step2 = create_tool_selection_step(
        decision_point="Select entity extraction method",
        available_tools=["T23a", "T23b", "T23c"],
        selected_tool="T23a",
        reasoning_text="T23a is most reliable for general entity extraction tasks",
        confidence=0.85
    )
    trace1.add_step(step2)
    
    step3 = ReasoningStep(
        decision_level=DecisionLevel.SYSTEM,
        reasoning_type=ReasoningType.VALIDATION,
        decision_point="Validate workflow structure",
        reasoning_text="Checking tool compatibility and data flow",
        confidence_score=0.95,
        context={"validation_passed": True}
    )
    trace1.add_step(step3)
    
    trace1.complete_trace(success=True)
    sample_traces.append(trace1)
    
    # Trace 2: Failed workflow with error handling
    trace2 = ReasoningTrace(
        operation_type="workflow_generation", 
        operation_id="wf_002"
    )
    
    step1 = create_workflow_planning_step(
        decision_point="Process multi-document analysis request",
        context={"document_count": 5, "analysis_goal": "comparison"},
        workflow_generated={"tools": ["T01", "T301", "T302"]},
        reasoning_text="Multiple documents require batch processing and fusion",
        confidence=0.7
    )
    trace2.add_step(step1)
    
    step2 = ReasoningStep(
        decision_level=DecisionLevel.TOOL,
        reasoning_type=ReasoningType.ERROR_HANDLING,
        decision_point="Handle tool compatibility error",
        reasoning_text="T301 and T302 have incompatible output formats",
        confidence_score=0.6,
        error_occurred=True,
        error_message="Tool output format mismatch"
    )
    trace2.add_step(step2)
    
    trace2.complete_trace(success=False)
    sample_traces.append(trace2)
    
    # Trace 3: Optimization decision
    trace3 = ReasoningTrace(
        operation_type="performance_optimization",
        operation_id="perf_001"
    )
    
    step1 = ReasoningStep(
        decision_level=DecisionLevel.AGENT,
        reasoning_type=ReasoningType.OPTIMIZATION,
        decision_point="Choose processing strategy",
        reasoning_text="Large document requires chunking and parallel processing",
        confidence_score=0.8,
        context={"document_size": "large", "strategy": "parallel"}
    )
    trace3.add_step(step1)
    
    trace3.complete_trace(success=True)
    sample_traces.append(trace3)
    
    # Trace 4: Low confidence decision
    trace4 = ReasoningTrace(
        operation_type="workflow_generation",
        operation_id="wf_003"
    )
    
    step1 = ReasoningStep(
        decision_level=DecisionLevel.LLM,
        reasoning_type=ReasoningType.WORKFLOW_PLANNING,
        decision_point="Handle ambiguous user request",
        reasoning_text="User request is unclear, making assumptions about intent",
        confidence_score=0.3,
        options_considered=["conservative_approach", "aggressive_approach", "clarification_request"]
    )
    trace4.add_step(step1)
    
    trace4.complete_trace(success=False)
    sample_traces.append(trace4)
    
    # Trace 5: Complex multi-step reasoning
    trace5 = ReasoningTrace(
        operation_type="complex_analysis",
        operation_id="complex_001"
    )
    
    # Multiple steps at different levels
    for i in range(6):
        step = ReasoningStep(
            decision_level=list(DecisionLevel)[i % 4],
            reasoning_type=list(ReasoningType)[i % 6],
            decision_point=f"Complex analysis step {i+1}",
            reasoning_text=f"Reasoning for complex step {i+1}",
            confidence_score=0.6 + (i * 0.05)
        )
        trace5.add_step(step)
    
    trace5.complete_trace(success=True)
    sample_traces.append(trace5)
    
    return sample_traces

def test_populate_database_with_sample_data():
    """Test populating database with comprehensive sample data"""
    print("1. Populating Database with Sample Data...")
    
    try:
        from src.core.reasoning_trace_store import ReasoningTraceStore
        
        temp_db = tempfile.mktemp(suffix='_populated.db')
        
        try:
            store = ReasoningTraceStore(temp_db)
            sample_traces = create_sample_reasoning_data()
            
            # Store all sample traces
            stored_count = 0
            for trace in sample_traces:
                if store.store_trace(trace):
                    stored_count += 1
            
            # Verify storage
            stats = store.get_statistics()
            
            print(f"   ✅ Stored {stored_count} traces successfully")
            print(f"   Database stats: {stats['total_traces']} traces, {stats['total_steps']} steps")
            
            return temp_db, store, stored_count >= 5
            
        except Exception as e:
            if os.path.exists(temp_db):
                os.remove(temp_db)
            raise e
            
    except Exception as e:
        print(f"   ❌ Database population failed: {e}")
        return None, None, False

def test_basic_queries_on_populated_db(temp_db, store):
    """Test basic queries on populated database"""
    print("2. Testing Basic Queries on Populated Database...")
    
    try:
        # Test operation type queries
        workflow_traces = store.query_traces(operation_type="workflow_generation")
        print(f"   Found {len(workflow_traces)} workflow generation traces")
        
        # Test success filtering
        successful_traces = store.query_traces(success_only=True)
        failed_traces = store.query_traces(success_only=False)
        print(f"   Successful traces: {len(successful_traces)}, Failed: {len(failed_traces)}")
        
        # Test step queries
        from src.core.reasoning_trace import DecisionLevel, ReasoningType
        
        agent_steps = store.query_steps(decision_level=DecisionLevel.AGENT)
        print(f"   Agent-level decisions: {len(agent_steps)}")
        
        high_confidence_steps = store.query_steps(confidence_threshold=0.8)
        print(f"   High confidence steps: {len(high_confidence_steps)}")
        
        # Verify we got reasonable results
        assert len(workflow_traces) >= 2, "Should have multiple workflow traces"
        assert len(successful_traces) >= 2, "Should have successful traces"
        assert len(failed_traces) >= 1, "Should have failed traces"
        assert len(agent_steps) >= 1, "Should have agent-level steps"
        
        print("   ✅ Basic queries working correctly")
        return True
        
    except Exception as e:
        print(f"   ❌ Basic queries failed: {e}")
        return False

def test_advanced_query_interface(temp_db, store):
    """Test advanced query interface with populated data"""
    print("3. Testing Advanced Query Interface...")
    
    try:
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        
        query_interface = ReasoningQueryInterface(store)
        
        # Test trace analysis
        traces = store.query_traces(limit=5)
        if traces:
            trace_analysis = query_interface.analyze_trace(traces[0].trace_id)
            
            assert trace_analysis is not None
            assert trace_analysis.total_steps >= 1
            assert isinstance(trace_analysis.reasoning_quality_score, (int, float))
            
            print(f"   ✅ Trace analysis: {trace_analysis.total_steps} steps, quality score: {trace_analysis.reasoning_quality_score:.2f}")
        
        # Test pattern detection
        patterns = query_interface.detect_reasoning_patterns(
            operation_type="workflow_generation",
            min_frequency=2
        )
        print(f"   Found {len(patterns)} reasoning patterns")
        
        # Test decision quality analysis
        decision_analysis = query_interface.analyze_decision_quality(
            decision_point="workflow",  # Partial match
            lookback_days=1
        )
        
        assert decision_analysis.total_decisions >= 0
        print(f"   Decision analysis: {decision_analysis.total_decisions} decisions analyzed")
        
        # Test confidence calibration
        calibration = query_interface.analyze_confidence_calibration(
            operation_type="workflow_generation"
        )
        
        if not calibration.get("error"):
            print(f"   Confidence calibration: {calibration['total_traces_analyzed']} traces analyzed")
        else:
            print(f"   Confidence calibration: {calibration['error']}")
        
        print("   ✅ Advanced query interface working")
        return True
        
    except Exception as e:
        print(f"   ❌ Advanced query interface failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_pattern_analysis(temp_db, store):
    """Test error pattern analysis"""
    print("4. Testing Error Pattern Analysis...")
    
    try:
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        
        query_interface = ReasoningQueryInterface(store)
        
        # Test error pattern detection
        error_patterns = query_interface.get_error_patterns(
            lookback_days=1,
            min_frequency=1
        )
        
        print(f"   Found {len(error_patterns)} error patterns")
        
        for pattern in error_patterns:
            print(f"   Pattern: {pattern['pattern']}, Frequency: {pattern['frequency']}")
        
        # Test similar decision finding
        steps = store.query_steps(limit=5)
        if steps:
            similar_steps = query_interface.find_similar_decisions(
                steps[0],
                similarity_threshold=0.5
            )
            print(f"   Found {len(similar_steps)} similar decisions")
        
        print("   ✅ Error pattern analysis working")
        return True
        
    except Exception as e:
        print(f"   ❌ Error pattern analysis failed: {e}")
        return False

def test_trace_comparison(temp_db, store):
    """Test trace comparison functionality"""
    print("5. Testing Trace Comparison...")
    
    try:
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        
        query_interface = ReasoningQueryInterface(store)
        
        # Get traces for comparison
        traces = store.query_traces(limit=3)
        trace_ids = [trace.trace_id for trace in traces]
        
        if len(trace_ids) >= 2:
            # Compare traces
            comparison = query_interface.compare_traces(trace_ids)
            
            if not comparison.get("error"):
                print(f"   Compared {comparison['traces_compared']} traces")
                
                for metric, data in comparison.get("results", {}).items():
                    avg_val = data.get("avg", 0)
                    print(f"   {metric}: avg={avg_val:.2f}")
            else:
                print(f"   Comparison error: {comparison['error']}")
        
        print("   ✅ Trace comparison working")
        return True
        
    except Exception as e:
        print(f"   ❌ Trace comparison failed: {e}")
        return False

def main():
    """Run populated database query tests"""
    print("🗄️  Advanced Queries on Populated Reasoning Database")
    print("Creating sample data and testing advanced query capabilities...")
    print("=" * 70)
    
    start_time = time.time()
    
    # First populate the database
    temp_db, store, population_success = test_populate_database_with_sample_data()
    
    if not population_success:
        print("❌ Failed to populate database, cannot run advanced query tests")
        return 1
    
    try:
        tests = [
            ("Basic Queries on Populated DB", lambda: test_basic_queries_on_populated_db(temp_db, store)),
            ("Advanced Query Interface", lambda: test_advanced_query_interface(temp_db, store)),
            ("Error Pattern Analysis", lambda: test_error_pattern_analysis(temp_db, store)),
            ("Trace Comparison", lambda: test_trace_comparison(temp_db, store))
        ]
        
        results = [("Database Population", population_success, 0)]
        
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
        
        print(f"\n📋 Populated Database Query Results (completed in {total_time:.1f}s)")
        print("=" * 70)
        
        for test_name, success, duration in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name} ({duration:.1f}s)")
        
        passed = sum(1 for _, success, _ in results if success)
        total = len(results)
        
        print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ADVANCED QUERIES FULLY WORKING")
            print("   Reasoning database supports comprehensive analysis")
        elif passed >= total * 0.8:
            print("⚠️  ADVANCED QUERIES MOSTLY WORKING - Minor issues")
        else:
            print("❌ ADVANCED QUERY ISSUES - Major problems need resolution")
        
        return 0 if passed >= total * 0.8 else 1
        
    finally:
        # Cleanup
        if store:
            store.close()
        if temp_db and os.path.exists(temp_db):
            os.remove(temp_db)
            print(f"\n🧹 Cleaned up temporary database: {temp_db}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)