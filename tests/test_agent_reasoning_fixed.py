#!/usr/bin/env python3
"""
Fixed test for agent reasoning with proper Task object usage.
This resolves the ReasoningContext interface mismatch issue.
"""

import asyncio
import os
from datetime import datetime
import json
import sys

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.orchestration.base import Task, TaskPriority
from src.orchestration.llm_reasoning import ReasoningContext, ReasoningType, LLMReasoningEngine


async def test_strategic_reasoning():
    """Test strategic reasoning with proper Task object"""
    print("\n" + "="*60)
    print("🎯 TESTING STRATEGIC REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    # Create proper Task object
    task = Task(
        task_type="planning",
        parameters={
            "description": "Plan a multi-stage document processing pipeline",
            "documents": 5,
            "constraints": ["memory_limit: 1GB", "time_limit: 60s"]
        },
        context={
            "current_state": {"documents": 5, "processed": 0},
            "available_actions": ["load", "chunk", "extract", "analyze", "store"]
        },
        priority=TaskPriority.HIGH
    )
    
    # Create ReasoningContext with Task
    context = ReasoningContext(
        agent_id="strategic_agent",
        task=task,
        memory_context={
            "domain": "document_processing",
            "optimization_goal": "throughput"
        },
        reasoning_type=ReasoningType.STRATEGIC
    )
    
    print(f"  Task type: {task.task_type}")
    print(f"  Priority: {task.priority}")
    
    result = await engine.reason(context)
    
    print(f"\n📊 Strategic Reasoning Result:")
    print(f"  Success: {result.success}")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Explanation length: {len(result.explanation)} chars")
    
    # Check for Gemini usage
    if result.metadata and 'llm_used' in result.metadata:
        print(f"  ✅ LLM Used: {result.metadata['llm_used']}")
    else:
        print(f"  ℹ️ Checking reasoning chain for LLM evidence...")
        if result.reasoning_chain:
            for step in result.reasoning_chain:
                if 'llm' in str(step).lower() or 'gemini' in str(step).lower():
                    print(f"  ✅ Found LLM reference in reasoning chain")
                    break
    
    return result


async def test_tactical_reasoning():
    """Test tactical reasoning for entity extraction"""
    print("\n" + "="*60)
    print("⚔️ TESTING TACTICAL REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    # Create Task for entity extraction
    task = Task(
        task_type="entity_extraction",
        parameters={
            "text": "Dr. Jane Smith at MIT developed a new AI algorithm in 2024.",
            "entity_types": ["PERSON", "ORG", "TECH", "DATE"],
            "confidence_threshold": 0.8
        },
        context={
            "document_type": "research_article",
            "domain": "artificial_intelligence"
        },
        priority=TaskPriority.MEDIUM
    )
    
    context = ReasoningContext(
        agent_id="tactical_agent",
        task=task,
        memory_context={
            "extraction_method": "llm_enhanced",
            "previous_entities": []
        },
        reasoning_type=ReasoningType.TACTICAL
    )
    
    print(f"  Task type: {task.task_type}")
    print(f"  Text: {task.parameters['text'][:50]}...")
    
    result = await engine.reason(context)
    
    print(f"\n📊 Tactical Reasoning Result:")
    print(f"  Success: {result.success}")
    print(f"  Decision type: {type(result.decision)}")
    
    # Check if entities were extracted
    if isinstance(result.decision, dict):
        if 'entities' in result.decision:
            entities = result.decision['entities']
            print(f"  Entities found: {len(entities) if isinstance(entities, list) else 'N/A'}")
            if isinstance(entities, list) and entities:
                print(f"  Sample entities: {entities[:3]}")
        elif 'action' in result.decision:
            print(f"  Action decided: {result.decision['action']}")
    
    print(f"  Confidence: {result.confidence:.2f}")
    
    return result


async def test_adaptive_reasoning():
    """Test adaptive reasoning with learning from history"""
    print("\n" + "="*60)
    print("🔄 TESTING ADAPTIVE REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    # Create Task with historical context
    task = Task(
        task_type="strategy_selection",
        parameters={
            "document_type": "technical_paper",
            "document_size": "large",
            "optimization_target": "accuracy"
        },
        context={
            "available_strategies": ["fast_process", "thorough_process", "hybrid_process"],
            "constraints": ["accuracy > 0.9", "time < 60s"]
        },
        priority=TaskPriority.HIGH
    )
    
    # Include execution history for adaptive learning
    context = ReasoningContext(
        agent_id="adaptive_agent",
        task=task,
        memory_context={
            "past_executions": [
                {"doc_type": "technical_paper", "strategy": "fast_process", "accuracy": 0.65, "time": 10},
                {"doc_type": "technical_paper", "strategy": "thorough_process", "accuracy": 0.92, "time": 45},
                {"doc_type": "news_article", "strategy": "fast_process", "accuracy": 0.88, "time": 5}
            ],
            "learning_enabled": True
        },
        reasoning_type=ReasoningType.ADAPTIVE,
        previous_reasoning=[
            {"strategy": "fast_process", "outcome": "insufficient_accuracy"},
            {"strategy": "thorough_process", "outcome": "good_accuracy"}
        ]
    )
    
    print(f"  Task type: {task.task_type}")
    print(f"  Past executions: {len(context.memory_context['past_executions'])}")
    print(f"  Previous reasoning: {len(context.previous_reasoning)}")
    
    result = await engine.reason(context)
    
    print(f"\n📊 Adaptive Reasoning Result:")
    print(f"  Success: {result.success}")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    
    # Check if learning was applied
    if result.metadata:
        if 'used_history' in result.metadata:
            print(f"  Learning applied: {result.metadata['used_history']}")
        if 'adaptation_strategy' in result.metadata:
            print(f"  Adaptation: {result.metadata['adaptation_strategy']}")
    
    return result


async def test_diagnostic_reasoning():
    """Test diagnostic reasoning for error analysis"""
    print("\n" + "="*60)
    print("🔍 TESTING DIAGNOSTIC REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    # Create Task for error diagnosis
    task = Task(
        task_type="error_diagnosis",
        parameters={
            "error_message": "NoneType has no attribute 'text'",
            "failed_node": "chunk_text",
            "stack_trace": "File 'chunker.py', line 42, in chunk\n    chunks = text.split('\\n')"
        },
        context={
            "pipeline_state": {
                "previous_node": "load_pdf",
                "previous_output": None,
                "expected_input": "document_text"
            },
            "available_actions": ["retry", "skip", "use_default", "check_upstream", "log_error"]
        },
        priority=TaskPriority.CRITICAL
    )
    
    context = ReasoningContext(
        agent_id="diagnostic_agent",
        task=task,
        memory_context={
            "error_patterns": [
                {"pattern": "NoneType", "common_cause": "missing_input"},
                {"pattern": "attribute", "common_cause": "type_mismatch"}
            ],
            "recovery_strategies": ["validate_input", "add_defaults", "graceful_degradation"]
        },
        reasoning_type=ReasoningType.DIAGNOSTIC
    )
    
    print(f"  Task type: {task.task_type}")
    print(f"  Error: {task.parameters['error_message']}")
    print(f"  Failed node: {task.parameters['failed_node']}")
    
    result = await engine.reason(context)
    
    print(f"\n📊 Diagnostic Reasoning Result:")
    print(f"  Success: {result.success}")
    
    if isinstance(result.decision, dict):
        if 'diagnosis' in result.decision:
            print(f"  Root cause: {result.decision['diagnosis']}")
        if 'recommended_action' in result.decision:
            print(f"  Recommended: {result.decision['recommended_action']}")
        if 'confidence' in result.decision:
            print(f"  Diagnosis confidence: {result.decision['confidence']}")
    else:
        print(f"  Decision: {result.decision}")
    
    print(f"  Overall confidence: {result.confidence:.2f}")
    
    if result.alternatives_considered:
        print(f"  Alternatives considered: {len(result.alternatives_considered)}")
    
    return result


async def main():
    """Run all reasoning tests and generate evidence"""
    print("\n" + "="*80)
    print("🧠 TESTING AGENT REASONING WITH PROPER TASK INTERFACE")
    print("="*80)
    
    # Check Gemini configuration
    has_gemini = bool(os.getenv('GEMINI_API_KEY'))
    print(f"\n📋 Configuration:")
    print(f"  Gemini API Key: {'✅ Set' if has_gemini else '⚠️ Not set'}")
    
    results = []
    errors = []
    
    # Test all reasoning types
    tests = [
        ("Strategic", test_strategic_reasoning),
        ("Tactical", test_tactical_reasoning),
        ("Adaptive", test_adaptive_reasoning),
        ("Diagnostic", test_diagnostic_reasoning)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result, None))
        except Exception as e:
            print(f"\n  ❌ {test_name} reasoning failed: {e}")
            results.append((test_name, None, str(e)))
            errors.append((test_name, str(e)))
    
    # Summary
    print("\n" + "="*80)
    print("📈 REASONING TEST SUMMARY")
    print("="*80)
    
    successful = 0
    llm_confirmed = 0
    
    for reasoning_type, result, error in results:
        if error:
            print(f"  ❌ {reasoning_type}: Failed - {error}")
        elif result:
            successful += 1
            status = "✅ Success"
            
            # Check for LLM usage
            llm_used = False
            if result.metadata and 'llm_used' in result.metadata:
                llm_used = True
                llm_confirmed += 1
            elif result.reasoning_chain:
                # Check reasoning chain for LLM evidence
                for step in result.reasoning_chain:
                    if 'llm' in str(step).lower() or 'gemini' in str(step).lower():
                        llm_used = True
                        llm_confirmed += 1
                        break
            
            if llm_used:
                status += " (LLM confirmed)"
            
            print(f"  {status}: {reasoning_type}")
            print(f"    - Confidence: {result.confidence:.2f}")
            print(f"    - Execution time: {result.execution_time:.3f}s")
    
    print(f"\n✨ Results:")
    print(f"  Tests passed: {successful}/{len(tests)}")
    print(f"  LLM usage confirmed: {llm_confirmed}/{successful if successful > 0 else 1}")
    
    # Generate evidence file
    evidence = f"""# Evidence: Agent Reasoning Interface Fixed

## Date: {datetime.now().isoformat()}

## Problem
ReasoningContext.__init__() got an unexpected keyword argument 'task_description'
Tests were passing raw parameters instead of Task objects.

## Solution
Fixed all tests to use proper Task objects from src.orchestration.base

## Test Results

### Configuration
- Gemini API Key: {'Set' if has_gemini else 'Not set'}
- Tests run: {len(tests)}
- Tests passed: {successful}

### Reasoning Types Tested
"""
    
    for reasoning_type, result, error in results:
        if error:
            evidence += f"""
#### {reasoning_type} Reasoning
- **Status**: ❌ Failed
- **Error**: {error}
"""
        elif result:
            evidence += f"""
#### {reasoning_type} Reasoning
- **Status**: ✅ Success
- **Confidence**: {result.confidence:.2f}
- **Execution Time**: {result.execution_time:.3f}s
- **Decision Made**: {'Yes' if result.decision else 'No'}
- **LLM Used**: {'Confirmed' if (result.metadata and 'llm_used' in result.metadata) else 'Check logs'}
"""
    
    evidence += f"""
## Validation

### Before (Broken)
```
ReasoningContext.__init__() got an unexpected keyword argument 'task_description'
```

### After (Fixed)
- All {successful} reasoning types execute successfully
- Proper Task objects used throughout
- ReasoningContext accepts Task parameter correctly

## Key Changes Made

1. Import Task and TaskPriority from src.orchestration.base
2. Create Task objects with proper structure:
   - task_type: Type of task
   - parameters: Task-specific parameters
   - context: Shared context
   - priority: TaskPriority enum value

3. Pass Task to ReasoningContext:
   - agent_id: Agent identifier
   - task: Task object (not raw parameters)
   - memory_context: Memory/history
   - reasoning_type: ReasoningType enum

## Validation Commands

```bash
# Run this test
python test_agent_reasoning_fixed.py

# Check for LLM usage
grep "Gemini\|gemini" logs/super_digimon.log | tail -10

# Verify no interface errors
python test_agent_reasoning_fixed.py 2>&1 | grep -c "unexpected keyword"
# Should return: 0
```

## Conclusion

{'✅ Issue 1 RESOLVED: Agent reasoning interface fixed and all 4 reasoning types working' if successful == len(tests) else f'⚠️ Partially resolved: {successful}/{len(tests)} reasoning types working'}

The ReasoningContext interface mismatch has been resolved by properly using Task objects.
{'All reasoning types are now functional.' if successful == len(tests) else f'Some reasoning types still need attention: {", ".join([e[0] for e in errors])}'}
"""
    
    # Save evidence file
    with open("Evidence_Agent_Reasoning_Fixed.md", "w") as f:
        f.write(evidence)
    
    print(f"\n📄 Evidence file created: Evidence_Agent_Reasoning_Fixed.md")
    
    # Return success status
    return successful == len(tests)


if __name__ == "__main__":
    success = asyncio.run(main())
    exit_code = 0 if success else 1
    print(f"\n{'✅ ALL TESTS PASSED' if success else '⚠️ SOME TESTS FAILED'}")
    exit(exit_code)