#!/usr/bin/env python3
"""
Test agent reasoning with real LLM (Gemini) for various reasoning types.
This verifies that agent reasoning uses actual LLM, not simplified logic.
"""

import asyncio
import os
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.orchestration.llm_reasoning import LLMReasoningEngine, ReasoningContext, ReasoningType


async def test_strategic_reasoning():
    """Test strategic reasoning with real LLM"""
    print("\n" + "="*60)
    print("🎯 TESTING STRATEGIC REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    context = ReasoningContext(
        task_description="Plan a multi-stage document processing pipeline",
        current_state={"documents": 5, "processed": 0},
        available_actions=["load", "chunk", "extract", "analyze", "store"],
        constraints=["memory_limit: 1GB", "time_limit: 60s"],
        reasoning_type=ReasoningType.STRATEGIC
    )
    
    result = await engine.reason(context)
    
    print(f"\n📊 Strategic Reasoning Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Explanation length: {len(result.explanation)} chars")
    print(f"  Metadata: {result.metadata}")
    
    # Check if real LLM was used
    if result.metadata.get('llm_used'):
        print(f"  ✅ Real LLM Used: {result.metadata['llm_used']}")
    else:
        print(f"  ⚠️ No LLM metadata found")
    
    return result


async def test_tactical_reasoning():
    """Test tactical reasoning with real LLM"""
    print("\n" + "="*60)
    print("⚔️ TESTING TACTICAL REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    context = ReasoningContext(
        task_description="Extract entities from scientific text",
        current_state={"text": "Dr. Jane Smith at MIT developed a new AI algorithm."},
        available_actions=["extract_person", "extract_org", "extract_tech"],
        constraints=["accuracy > 0.8"],
        reasoning_type=ReasoningType.TACTICAL
    )
    
    result = await engine.reason(context)
    
    print(f"\n📊 Tactical Reasoning Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Entities found: {result.decision.get('entities', [])}")
    
    if result.metadata.get('llm_used'):
        print(f"  ✅ Real LLM Used: {result.metadata['llm_used']}")
    
    return result


async def test_adaptive_reasoning():
    """Test adaptive reasoning with learning from history"""
    print("\n" + "="*60)
    print("🔄 TESTING ADAPTIVE REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    # Include execution history for adaptive learning
    context = ReasoningContext(
        task_description="Choose optimal processing strategy based on past performance",
        current_state={"document_type": "technical_paper", "size": "large"},
        available_actions=["fast_process", "thorough_process", "hybrid_process"],
        constraints=["optimize for accuracy"],
        reasoning_type=ReasoningType.ADAPTIVE,
        memory_context={
            "past_executions": [
                {"doc_type": "technical_paper", "strategy": "fast_process", "accuracy": 0.65},
                {"doc_type": "technical_paper", "strategy": "thorough_process", "accuracy": 0.92},
                {"doc_type": "news_article", "strategy": "fast_process", "accuracy": 0.88}
            ]
        }
    )
    
    result = await engine.reason(context)
    
    print(f"\n📊 Adaptive Reasoning Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Learning applied: {result.metadata.get('used_history', False)}")
    
    if result.metadata.get('llm_used'):
        print(f"  ✅ Real LLM Used: {result.metadata['llm_used']}")
    
    return result


async def test_diagnostic_reasoning():
    """Test diagnostic reasoning for error analysis"""
    print("\n" + "="*60)
    print("🔍 TESTING DIAGNOSTIC REASONING")
    print("="*60)
    
    engine = LLMReasoningEngine()
    
    context = ReasoningContext(
        task_description="Diagnose pipeline failure and suggest fixes",
        current_state={
            "error": "NoneType has no attribute 'text'",
            "failed_node": "chunk_text",
            "input_received": None
        },
        available_actions=["retry", "skip", "use_default", "check_upstream"],
        constraints=["maintain data integrity"],
        reasoning_type=ReasoningType.DIAGNOSTIC
    )
    
    result = await engine.reason(context)
    
    print(f"\n📊 Diagnostic Reasoning Result:")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Root cause: {result.decision.get('diagnosis', 'unknown')}")
    
    if result.metadata.get('llm_used'):
        print(f"  ✅ Real LLM Used: {result.metadata['llm_used']}")
    
    return result


async def main():
    """Run all reasoning tests"""
    print("\n" + "="*80)
    print("🧠 TESTING AGENT REASONING WITH REAL LLM (GEMINI)")
    print("="*80)
    
    # Check if Gemini is configured
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️ WARNING: GEMINI_API_KEY not set - tests may fail or use simulation")
    
    results = []
    
    # Test all reasoning types
    try:
        strategic = await test_strategic_reasoning()
        results.append(("Strategic", strategic))
    except Exception as e:
        print(f"  ❌ Strategic reasoning failed: {e}")
        results.append(("Strategic", None))
    
    try:
        tactical = await test_tactical_reasoning()
        results.append(("Tactical", tactical))
    except Exception as e:
        print(f"  ❌ Tactical reasoning failed: {e}")
        results.append(("Tactical", None))
    
    try:
        adaptive = await test_adaptive_reasoning()
        results.append(("Adaptive", adaptive))
    except Exception as e:
        print(f"  ❌ Adaptive reasoning failed: {e}")
        results.append(("Adaptive", None))
    
    try:
        diagnostic = await test_diagnostic_reasoning()
        results.append(("Diagnostic", diagnostic))
    except Exception as e:
        print(f"  ❌ Diagnostic reasoning failed: {e}")
        results.append(("Diagnostic", None))
    
    # Summary
    print("\n" + "="*80)
    print("📈 REASONING TEST SUMMARY")
    print("="*80)
    
    llm_count = 0
    for reasoning_type, result in results:
        if result and result.metadata.get('llm_used'):
            print(f"  ✅ {reasoning_type}: Real LLM ({result.metadata['llm_used']})")
            llm_count += 1
        elif result:
            print(f"  ⚠️ {reasoning_type}: No LLM metadata")
        else:
            print(f"  ❌ {reasoning_type}: Failed")
    
    print(f"\n✨ Results: {llm_count}/{len(results)} using real LLM")
    
    # Create evidence file
    evidence = f"""# Evidence: Agent Reasoning with Real LLM

## Date: {datetime.now().isoformat()}

## Test Results

### Reasoning Types Tested
1. **Strategic** - High-level planning and strategy
2. **Tactical** - Specific task execution (e.g., entity extraction)
3. **Adaptive** - Learning from past executions
4. **Diagnostic** - Error analysis and recovery

### LLM Usage
- Configured Model: Gemini 2.0 Flash
- API Key Set: {"Yes" if os.getenv('GEMINI_API_KEY') else "No"}
- Tests Using Real LLM: {llm_count}/{len(results)}

### Detailed Results
"""
    
    for reasoning_type, result in results:
        if result:
            evidence += f"""
#### {reasoning_type} Reasoning
- **Decision Made**: Yes
- **Confidence**: {result.confidence:.2f}
- **LLM Used**: {result.metadata.get('llm_used', 'Unknown')}
- **Explanation Length**: {len(result.explanation)} characters
"""
    
    evidence += f"""
## Validation

The agent reasoning system is {"✅ USING REAL LLM" if llm_count > 0 else "⚠️ NOT USING REAL LLM"}.

### Key Evidence
- LLM metadata present in results: {llm_count > 0}
- Gemini API configured: {bool(os.getenv('GEMINI_API_KEY'))}
- All reasoning types functional: {all(r for _, r in results)}

## Conclusion

{"✅ Agent reasoning confirmed to use real Gemini LLM for decision making." if llm_count == len(results) else "⚠️ Some reasoning types not using real LLM."}

## Reproduction Commands

```bash
# Set Gemini API key
export GEMINI_API_KEY=your_key_here

# Run reasoning tests
python test_agent_reasoning_real.py

# Check LLM logs
grep "Used real Gemini API" logs/*.log
```
"""
    
    with open("Evidence_Agent_Reasoning_Real.md", "w") as f:
        f.write(evidence)
    
    print(f"\n📄 Evidence file created: Evidence_Agent_Reasoning_Real.md")
    
    return llm_count == len(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'✅' if success else '⚠️'} Agent Reasoning Test: {'PASSED' if success else 'NEEDS ATTENTION'}")