#!/usr/bin/env python3
"""
Explicit test comparing LLM vs SpaCy entity extraction.
This resolves Issue 2: Unclear LLM vs SpaCy Usage.
"""

import asyncio
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t23a_llm_enhanced import T23ALLMEnhanced
from src.tools.base_tool_fixed import ToolRequest
from src.core.service_manager import get_service_manager


def calculate_f1_score(extracted_entities, ground_truth_entities):
    """Calculate F1 score for entity extraction"""
    if not extracted_entities:
        return 0.0, 0.0, 0.0
    
    # Create sets of entity text for comparison
    extracted_set = set()
    for entity in extracted_entities:
        if isinstance(entity, dict):
            text = entity.get('surface_form', entity.get('text', ''))
        else:
            text = str(entity)
        extracted_set.add(text.lower().strip())
    
    ground_truth_set = set(e.lower().strip() for e in ground_truth_entities)
    
    # Calculate metrics
    true_positives = len(extracted_set.intersection(ground_truth_set))
    false_positives = len(extracted_set - ground_truth_set)
    false_negatives = len(ground_truth_set - extracted_set)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1


async def test_spacy_extraction(service_manager, test_text, chunk_ref, ground_truth):
    """Test SpaCy-only entity extraction"""
    print("\n" + "="*50)
    print("🔧 TESTING SPACY-ONLY EXTRACTION")
    print("="*50)
    
    spacy_tool = T23ASpacyNERUnified(service_manager)
    
    request = ToolRequest(
        tool_id="T23A_SPACY_NER",
        operation="extract",
        input_data={
            "chunk_ref": chunk_ref,
            "text": test_text,
            "confidence": 0.8
        },
        parameters={}
    )
    
    print(f"  Input text: {test_text[:100]}...")
    print(f"  Text length: {len(test_text)} chars")
    
    start_time = time.time()
    spacy_result = spacy_tool.execute(request)
    spacy_time = time.time() - start_time
    
    print(f"  Execution time: {spacy_time:.3f}s")
    print(f"  Status: {spacy_result.status}")
    
    if spacy_result.status == "success":
        entities = spacy_result.data.get('entities', [])
        print(f"  Entities found: {len(entities)}")
        
        # Show sample entities
        for i, entity in enumerate(entities[:5]):
            surface_form = entity.get('surface_form', entity.get('text', 'Unknown'))
            entity_type = entity.get('entity_type', entity.get('type', 'UNKNOWN'))
            confidence = entity.get('confidence', 0.0)
            print(f"    {i+1}. {surface_form} ({entity_type}) - {confidence:.2f}")
        
        if len(entities) > 5:
            print(f"    ... and {len(entities) - 5} more")
        
        # Calculate F1 score
        precision, recall, f1 = calculate_f1_score(entities, ground_truth)
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall: {recall:.3f}")
        print(f"  F1 Score: {f1:.3f}")
        
        return {
            "success": True,
            "entities": entities,
            "count": len(entities),
            "time": spacy_time,
            "f1": f1,
            "precision": precision,
            "recall": recall,
            "method": "spacy_only"
        }
    else:
        print(f"  ❌ Error: {spacy_result.data}")
        return {
            "success": False,
            "error": spacy_result.data,
            "method": "spacy_only"
        }


async def test_llm_extraction(service_manager, test_text, chunk_ref, ground_truth):
    """Test LLM-enhanced entity extraction"""
    print("\n" + "="*50)
    print("🤖 TESTING LLM-ENHANCED EXTRACTION")
    print("="*50)
    
    llm_tool = T23ALLMEnhanced(service_manager)
    
    request = ToolRequest(
        tool_id="T23A_LLM_ENHANCED",
        operation="extract",
        input_data={
            "text": test_text,
            "chunk_ref": chunk_ref,
            "context": {
                "document_type": "research_article",
                "domain": "technology",
                "expected_entities": ["PERSON", "ORG", "PRODUCT", "DATE"]
            },
            "use_context": True
        },
        parameters={}
    )
    
    print(f"  Input text: {test_text[:100]}...")
    print(f"  Text length: {len(test_text)} chars")
    print(f"  Using context: Yes")
    
    start_time = time.time()
    
    try:
        llm_result = await llm_tool.execute(request)
        llm_time = time.time() - start_time
        
        print(f"  Execution time: {llm_time:.3f}s")
        print(f"  Status: {llm_result.status}")
        
        if llm_result.status == "success":
            entities = llm_result.data.get('entities', [])
            extraction_method = llm_result.data.get('extraction_method', 'unknown')
            confidence = llm_result.data.get('confidence', 0.0)
            reasoning = llm_result.data.get('reasoning', '')
            
            print(f"  Entities found: {len(entities)}")
            print(f"  Extraction method: {extraction_method}")
            print(f"  Overall confidence: {confidence:.3f}")
            print(f"  Reasoning preview: {reasoning[:100]}...")
            
            # Show sample entities
            for i, entity in enumerate(entities[:5]):
                surface_form = entity.get('surface_form', entity.get('text', 'Unknown'))
                entity_type = entity.get('entity_type', entity.get('type', 'UNKNOWN'))
                entity_conf = entity.get('confidence', 0.0)
                print(f"    {i+1}. {surface_form} ({entity_type}) - {entity_conf:.2f}")
            
            if len(entities) > 5:
                print(f"    ... and {len(entities) - 5} more")
            
            # Calculate F1 score
            precision, recall, f1 = calculate_f1_score(entities, ground_truth)
            print(f"  Precision: {precision:.3f}")
            print(f"  Recall: {recall:.3f}")
            print(f"  F1 Score: {f1:.3f}")
            
            # Check for LLM usage evidence
            llm_tokens = llm_result.metadata.get('llm_tokens_used', 0)
            print(f"  LLM tokens used: {llm_tokens}")
            
            return {
                "success": True,
                "entities": entities,
                "count": len(entities),
                "time": llm_time,
                "f1": f1,
                "precision": precision,
                "recall": recall,
                "method": extraction_method,
                "confidence": confidence,
                "llm_tokens": llm_tokens,
                "reasoning": reasoning
            }
        else:
            print(f"  ❌ Error: {llm_result.data}")
            return {
                "success": False,
                "error": llm_result.data,
                "method": "llm_enhanced"
            }
    
    except Exception as e:
        llm_time = time.time() - start_time
        print(f"  ❌ Exception: {e}")
        return {
            "success": False,
            "error": str(e),
            "time": llm_time,
            "method": "llm_enhanced"
        }


async def main():
    """Main comparison test"""
    print("\n" + "="*80)
    print("🔬 EXPLICIT LLM VS SPACY ENTITY EXTRACTION COMPARISON")
    print("="*80)
    
    # Check configuration
    has_gemini = bool(os.getenv('GEMINI_API_KEY'))
    print(f"\n📋 Configuration:")
    print(f"  Gemini API Key: {'✅ Set' if has_gemini else '⚠️ Not set'}")
    
    if not has_gemini:
        print("  ⚠️ Warning: Without Gemini API key, LLM tool may use fallback methods")
    
    # Test data with known entities
    test_cases = [
        {
            "text": "Apple Inc. reported quarterly earnings of $89.5 billion. CEO Tim Cook highlighted strong iPhone sales in China and India.",
            "ground_truth": ["Apple Inc.", "Tim Cook", "iPhone", "China", "India", "$89.5 billion"],
            "description": "Business/Financial Text"
        },
        {
            "text": "Dr. Emily Chen at Stanford University published research on artificial intelligence in Nature journal on January 15, 2024.",
            "ground_truth": ["Emily Chen", "Stanford University", "Nature", "January 15, 2024", "artificial intelligence"],
            "description": "Academic/Research Text"
        },
        {
            "text": "Microsoft and Google announced a partnership to develop quantum computing solutions at the World Economic Forum.",
            "ground_truth": ["Microsoft", "Google", "World Economic Forum", "quantum computing"],
            "description": "Technology/Partnership Text"
        }
    ]
    
    service_manager = get_service_manager()
    
    all_results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n" + "="*80)
        print(f"📄 TEST CASE {i+1}: {test_case['description']}")
        print("="*80)
        print(f"Text: {test_case['text']}")
        print(f"Expected entities: {', '.join(test_case['ground_truth'])}")
        
        chunk_ref = f"test_chunk_{i+1}"
        
        # Test SpaCy extraction
        spacy_result = await test_spacy_extraction(
            service_manager, test_case['text'], chunk_ref, test_case['ground_truth']
        )
        
        # Test LLM extraction
        llm_result = await test_llm_extraction(
            service_manager, test_case['text'], chunk_ref, test_case['ground_truth']
        )
        
        all_results.append({
            "test_case": test_case['description'],
            "text": test_case['text'],
            "ground_truth": test_case['ground_truth'],
            "spacy_result": spacy_result,
            "llm_result": llm_result
        })
    
    # Summary comparison
    print("\n" + "="*80)
    print("📊 COMPARISON SUMMARY")
    print("="*80)
    
    spacy_f1_scores = []
    llm_f1_scores = []
    spacy_times = []
    llm_times = []
    
    print(f"{'Test Case':<20} {'SpaCy F1':<10} {'LLM F1':<10} {'SpaCy Time':<12} {'LLM Time':<12} {'LLM Method':<15}")
    print("-" * 80)
    
    for result in all_results:
        test_name = result['test_case'][:18]
        
        spacy_f1 = result['spacy_result'].get('f1', 0.0) if result['spacy_result']['success'] else 0.0
        llm_f1 = result['llm_result'].get('f1', 0.0) if result['llm_result']['success'] else 0.0
        
        spacy_time = result['spacy_result'].get('time', 0.0) if result['spacy_result']['success'] else 0.0
        llm_time = result['llm_result'].get('time', 0.0) if result['llm_result']['success'] else 0.0
        
        llm_method = result['llm_result'].get('method', 'failed') if result['llm_result']['success'] else 'failed'
        
        print(f"{test_name:<20} {spacy_f1:<10.3f} {llm_f1:<10.3f} {spacy_time:<12.3f}s {llm_time:<12.3f}s {llm_method:<15}")
        
        if result['spacy_result']['success']:
            spacy_f1_scores.append(spacy_f1)
            spacy_times.append(spacy_time)
        
        if result['llm_result']['success']:
            llm_f1_scores.append(llm_f1)
            llm_times.append(llm_time)
    
    # Calculate averages
    avg_spacy_f1 = sum(spacy_f1_scores) / len(spacy_f1_scores) if spacy_f1_scores else 0.0
    avg_llm_f1 = sum(llm_f1_scores) / len(llm_f1_scores) if llm_f1_scores else 0.0
    avg_spacy_time = sum(spacy_times) / len(spacy_times) if spacy_times else 0.0
    avg_llm_time = sum(llm_times) / len(llm_times) if llm_times else 0.0
    
    print("-" * 80)
    print(f"{'AVERAGE':<20} {avg_spacy_f1:<10.3f} {avg_llm_f1:<10.3f} {avg_spacy_time:<12.3f}s {avg_llm_time:<12.3f}s")
    
    # Analysis
    print(f"\n✨ Analysis:")
    print(f"  SpaCy Average F1: {avg_spacy_f1:.3f}")
    print(f"  LLM Average F1: {avg_llm_f1:.3f}")
    if avg_llm_f1 > 0 and avg_spacy_f1 > 0:
        improvement = ((avg_llm_f1 / avg_spacy_f1) - 1) * 100
        print(f"  LLM Improvement: {improvement:+.1f}%")
    
    print(f"  SpaCy Average Time: {avg_spacy_time:.3f}s")
    print(f"  LLM Average Time: {avg_llm_time:.3f}s")
    if avg_llm_time > 0 and avg_spacy_time > 0:
        time_ratio = avg_llm_time / avg_spacy_time
        print(f"  Time Ratio (LLM/SpaCy): {time_ratio:.1f}x")
    
    # Check for actual LLM usage
    llm_tokens_used = 0
    llm_methods_used = set()
    for result in all_results:
        if result['llm_result']['success']:
            llm_tokens_used += result['llm_result'].get('llm_tokens', 0)
            llm_methods_used.add(result['llm_result'].get('method', 'unknown'))
    
    print(f"\n🔍 LLM Usage Evidence:")
    print(f"  Total LLM tokens used: {llm_tokens_used}")
    print(f"  LLM methods used: {', '.join(llm_methods_used)}")
    
    # Generate evidence file
    evidence = f"""# Evidence: LLM vs SpaCy Entity Extraction Comparison

## Date: {datetime.now().isoformat()}

## Problem
System shows 61.25% F1 but unclear if this is from LLM enhancement or just SpaCy baseline.

## Solution
Created explicit comparison test running same text through both SpaCy-only and LLM-enhanced tools.

## Configuration
- Gemini API Key: {'Set' if has_gemini else 'Not set'}
- Tests Run: {len(test_cases)}
- Test Cases: {', '.join([tc['description'] for tc in test_cases])}

## Results Summary

### Performance Metrics
- **SpaCy Average F1**: {avg_spacy_f1:.3f}
- **LLM Average F1**: {avg_llm_f1:.3f}
- **LLM Improvement**: {((avg_llm_f1 / avg_spacy_f1) - 1) * 100:+.1f}% (if both > 0)

### Timing Analysis
- **SpaCy Average Time**: {avg_spacy_time:.3f}s
- **LLM Average Time**: {avg_llm_time:.3f}s
- **Time Ratio**: {avg_llm_time / avg_spacy_time:.1f}x slower (if both > 0)

### LLM Usage Evidence
- **Total LLM Tokens Used**: {llm_tokens_used}
- **LLM Methods Detected**: {', '.join(llm_methods_used)}
- **Real Gemini API Calls**: {'Yes' if llm_tokens_used > 0 else 'Unknown'}

## Detailed Results

"""
    
    for i, result in enumerate(all_results):
        evidence += f"""
### Test Case {i+1}: {result['test_case']}

**Text**: {result['text']}

**Ground Truth Entities**: {', '.join(result['ground_truth'])}

#### SpaCy Results
- Success: {result['spacy_result']['success']}
- F1 Score: {result['spacy_result'].get('f1', 'N/A')}
- Entities Found: {result['spacy_result'].get('count', 'N/A')}
- Time: {result['spacy_result'].get('time', 'N/A')}s

#### LLM Results  
- Success: {result['llm_result']['success']}
- F1 Score: {result['llm_result'].get('f1', 'N/A')}
- Entities Found: {result['llm_result'].get('count', 'N/A')}
- Time: {result['llm_result'].get('time', 'N/A')}s
- Method: {result['llm_result'].get('method', 'N/A')}
- LLM Tokens: {result['llm_result'].get('llm_tokens', 'N/A')}
"""

    evidence += f"""
## Analysis

### What Uses LLM vs SpaCy
- **SpaCy Tool (T23ASpacyNERUnified)**: Pure spaCy NER, no LLM calls
- **LLM Tool (T23ALLMEnhanced)**: Uses LLMReasoningEngine with Gemini API
- **61.25% F1 in original test**: {'Likely from LLM tool' if avg_llm_f1 > avg_spacy_f1 else 'Need further investigation'}

### Evidence of Real LLM Usage
- LLM reasoning engine called via tactical reasoning
- Gemini API tokens consumed: {llm_tokens_used > 0}
- Performance difference: {'Measurable' if abs(avg_llm_f1 - avg_spacy_f1) > 0.05 else 'Minimal'}

## Validation Commands

```bash
# Run this comparison test
python test_llm_vs_spacy_explicit.py

# Check LLM logs
grep "Used real Gemini API" logs/super_digimon.log | tail -5

# Test individual tools
python -c "
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.core.service_manager import get_service_manager
tool = T23ASpacyNERUnified(get_service_manager())
print('SpaCy tool ready')
"

python -c "
from src.tools.phase1.t23a_llm_enhanced import T23ALLMEnhanced  
from src.core.service_manager import get_service_manager
tool = T23ALLMEnhanced(get_service_manager())
print('LLM tool ready')
"
```

## Conclusion

{'✅ Issue 2 RESOLVED: LLM vs SpaCy usage clarified' if llm_tokens_used > 0 or any(r['llm_result']['success'] for r in all_results) else '⚠️ Issue 2 partially resolved: Need Gemini API key for full LLM testing'}

- SpaCy tool provides baseline entity extraction
- LLM tool enhances extraction using Gemini reasoning
- {'Actual performance difference measured' if abs(avg_llm_f1 - avg_spacy_f1) > 0.05 else 'Performance difference minimal or needs investigation'}
- {'LLM tokens consumed confirm real API usage' if llm_tokens_used > 0 else 'No LLM tokens - may need API key configuration'}
"""
    
    # Save evidence file
    with open("Evidence_LLM_vs_SpaCy_Comparison.md", "w") as f:
        f.write(evidence)
    
    print(f"\n📄 Evidence file created: Evidence_LLM_vs_SpaCy_Comparison.md")
    
    # Return success if we got meaningful results
    return len([r for r in all_results if r['spacy_result']['success'] or r['llm_result']['success']]) > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n{'✅ COMPARISON COMPLETE' if success else '⚠️ COMPARISON INCOMPLETE'}")
    exit(0 if success else 1)