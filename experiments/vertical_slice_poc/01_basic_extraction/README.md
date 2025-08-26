# Experiment 01: Basic Knowledge Graph Extraction

## Goal
Prove we can extract a knowledge graph WITH uncertainty assessment from an LLM in a single call.

## What We're Testing

1. **Can the LLM extract entities AND relationships?**
2. **Does it return uncertainty and reasoning?**
3. **Is the output consistent across multiple runs?**
4. **What prompt format works best?**

## Files

- `extract_kg.py` - Main extraction script
- `test_document.txt` - Sample document about a company acquisition
- `test_consistency.py` - Test extraction consistency across multiple runs
- `outputs/` - Extraction results saved here

## Quick Start

### 1. Single Extraction Test
```bash
python extract_kg.py
```

This will:
- Read the test document
- Call the LLM to extract knowledge graph
- Display entity/relationship counts
- Show uncertainty assessment
- Save results to `outputs/extraction_result.json`

### 2. Consistency Test
```bash
python test_consistency.py
```

This will:
- Run extraction 3 times on the same document
- Compare entities and relationships found
- Analyze uncertainty variation
- Save all runs to `outputs/consistency_run_*.json`

## Expected Output

A successful extraction should return:
```json
{
  "entities": [
    {
      "id": "techcorp",
      "name": "TechCorp Corporation",
      "type": "organization",
      "properties": {
        "ticker": "TECH",
        "headquarters": "San Francisco"
      }
    }
  ],
  "relationships": [
    {
      "source": "techcorp",
      "target": "dataflow_systems",
      "type": "ACQUIRES",
      "properties": {
        "amount": "$2.3 billion",
        "date": "Q2 2025"
      }
    }
  ],
  "uncertainty": 0.15,
  "reasoning": "Clear factual business news with specific details..."
}
```

## Success Criteria

✅ Extraction succeeds when:
- At least 10 entities extracted (document has ~20+ named entities)
- At least 15 relationships identified
- Uncertainty value between 0.0 and 1.0
- Reasoning explains the uncertainty
- JSON is valid and parseable

⚠️ Warning signs:
- Different runs extract wildly different entities
- Uncertainty not included in response
- JSON parsing failures
- Empty entity/relationship lists

## Common Issues

### Issue: "No API key found"
**Solution**: Add your API key to `/home/brian/projects/Digimons/.env`:
```
GEMINI_API_KEY=your_key_here
```

### Issue: "JSON parsing failed"
**Problem**: LLM returned malformed JSON
**Solution**: The script tries to clean markdown formatting, but may need prompt adjustment

### Issue: "High variation between runs"
**Problem**: LLM giving inconsistent results
**Solution**: May need to adjust temperature or try different model

## What We Learn

From this experiment, we learn:
1. Whether LLMs can reliably extract KGs with uncertainty
2. What prompt format works best
3. How consistent extractions are
4. What uncertainty values we typically get
5. Whether the approach is viable for production

## Next Steps

If this experiment succeeds:
- Move to Experiment 02: Neo4j persistence
- Test with longer documents requiring chunking
- Try different LLM providers for comparison

If it fails:
- Adjust prompt engineering
- Try different LLM models
- Consider splitting extraction and uncertainty assessment