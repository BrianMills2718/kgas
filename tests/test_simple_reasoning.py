#!/usr/bin/env python3
"""
Simple test of LLM reasoning to isolate the issue
"""

import sys
import os
import asyncio
sys.path.append('/home/brian/projects/Digimons')

from dotenv import load_dotenv
load_dotenv()

from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningContext, ReasoningType
from src.orchestration.base import Task, TaskPriority

async def test_simple_reasoning():
    """Test a single reasoning call"""
    print("Testing simple LLM reasoning...")
    
    try:
        # Create reasoning engine
        engine = LLMReasoningEngine()
        print(f"✅ Engine created with config: {engine.llm_config}")
        
        # Create simple task
        task = Task(
            task_type="test",
            parameters={"text": "This is a test"},
            context={},
            priority=TaskPriority.MEDIUM
        )
        
        # Create reasoning context
        context = ReasoningContext(
            agent_id="test_agent",
            task=task,
            memory_context={},
            reasoning_type=ReasoningType.TACTICAL
        )
        
        print("Making reasoning call...")
        
        # Execute reasoning
        result = await engine.reason(context)
        
        print(f"✅ Reasoning completed")
        print(f"  Success: {result.success}")
        print(f"  Confidence: {result.confidence}")
        print(f"  Execution time: {result.execution_time:.3f}s")
        print(f"  Error: {result.error}")
        
        if result.success:
            print(f"  Decision keys: {list(result.decision.keys())}")
            print(f"  Reasoning chain length: {len(result.reasoning_chain)}")
        
        # Check if real API was used
        if result.metadata and result.metadata.get("model_used") == "simulated":
            print("❌ Used simulation instead of real API")
            return False
        else:
            print("✅ Used real API")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_simple_reasoning())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")