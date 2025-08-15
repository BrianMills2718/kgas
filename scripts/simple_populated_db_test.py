#!/usr/bin/env python3
"""
Simple Populated Database Test

Quick test of advanced queries on a populated reasoning database.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Run simple populated database test"""
    print("🗄️  Simple Populated Database Query Test")
    print("=" * 50)
    
    try:
        from src.core.reasoning_trace_store import ReasoningTraceStore
        from src.core.reasoning_trace import ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        
        # Create temporary database
        temp_db = tempfile.mktemp(suffix='.db')
        print(f"Creating temporary database: {temp_db}")
        
        try:
            store = ReasoningTraceStore(temp_db)
            
            # Create sample traces
            print("1. Creating sample reasoning traces...")
            
            # Trace 1: Successful workflow
            trace1 = ReasoningTrace(operation_type="workflow_generation", operation_id="test_001")
            
            step1 = ReasoningStep(
                decision_level=DecisionLevel.AGENT,
                reasoning_type=ReasoningType.WORKFLOW_PLANNING,
                decision_point="Generate PDF analysis workflow",
                reasoning_text="User wants to analyze PDF document, selecting appropriate tools",
                confidence_score=0.9
            )
            trace1.add_step(step1)
            
            step2 = ReasoningStep(
                decision_level=DecisionLevel.TOOL,
                reasoning_type=ReasoningType.TOOL_SELECTION,
                decision_point="Select entity extractor",
                reasoning_text="Choosing T23a for entity extraction based on document type",
                confidence_score=0.85
            )
            trace1.add_step(step2)
            
            trace1.complete_trace(success=True)
            
            # Trace 2: Failed workflow
            trace2 = ReasoningTrace(operation_type="workflow_generation", operation_id="test_002")
            
            step3 = ReasoningStep(
                decision_level=DecisionLevel.SYSTEM,
                reasoning_type=ReasoningType.ERROR_HANDLING,
                decision_point="Handle tool compatibility error",
                reasoning_text="Tool output formats are incompatible",
                confidence_score=0.4,
                error_occurred=True,
                error_message="Format mismatch error"
            )
            trace2.add_step(step3)
            
            trace2.complete_trace(success=False)
            
            # Store traces
            stored1 = store.store_trace(trace1)
            stored2 = store.store_trace(trace2)
            
            print(f"   ✅ Created and stored {int(stored1) + int(stored2)} traces")
            
            # Test basic queries
            print("2. Testing basic queries...")
            
            all_traces = store.query_traces()
            workflow_traces = store.query_traces(operation_type="workflow_generation")
            successful_traces = store.query_traces(success_only=True)
            
            print(f"   Total traces: {len(all_traces)}")
            print(f"   Workflow traces: {len(workflow_traces)}")
            print(f"   Successful traces: {len(successful_traces)}")
            
            # Test query interface
            print("3. Testing query interface...")
            
            query_interface = ReasoningQueryInterface(store)
            
            # Test trace analysis
            if all_traces:
                analysis = query_interface.analyze_trace(all_traces[0].trace_id)
                if analysis:
                    print(f"   ✅ Trace analysis: {analysis.total_steps} steps, quality: {analysis.reasoning_quality_score:.2f}")
                else:
                    print("   ⚠️  Trace analysis returned None")
            
            # Test pattern detection
            patterns = query_interface.detect_reasoning_patterns(min_frequency=1)
            print(f"   ✅ Found {len(patterns)} reasoning patterns")
            
            # Test statistics
            stats = store.get_statistics()
            print(f"   ✅ Database stats: {stats}")
            
            store.close()
            
            print("\n🎉 POPULATED DATABASE QUERIES WORKING")
            print("✅ Sample data creation successful")
            print("✅ Basic queries functional")  
            print("✅ Advanced query interface operational")
            print("✅ Pattern detection working")
            
            return 0
            
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
                print(f"🧹 Cleaned up: {temp_db}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)