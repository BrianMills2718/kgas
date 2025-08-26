# Experiment 01 Results: Basic Knowledge Graph Extraction

**Date**: 2025-01-26
**Status**: ✅ SUCCESS

## Summary

Successfully extracted knowledge graphs with uncertainty assessment from a business document using Gemini 1.5 Flash in a single API call.

## Key Results

### Extraction Quality
- **Entities Found**: 23-27 entities (document has ~30 named entities)
- **Relationships Found**: 17-22 relationships
- **Entity Types**: person, organization, location, event, concept
- **Relationship Types**: EMPLOYS, ACQUIRED, LOCATED_IN, ADVISED, etc.

### Uncertainty Assessment
- **Uncertainty Score**: 0.25 (consistent across all runs)
- **Reasoning Provided**: Yes - explains forward-looking statements and projections
- **Consistency**: Perfect - all three runs returned same uncertainty

### Consistency Analysis
- **Entity Consistency**: 61.3% (19 common entities out of 31 total unique)
- **Relationship Consistency**: 21.2% (lower due to relationship type variations)
- **Uncertainty Consistency**: 100% (all runs returned 0.25)

## What Worked

1. **Single LLM Call**: Successfully got entities, relationships, uncertainty, and reasoning in one call
2. **JSON Structure**: LLM reliably returned valid JSON with requested structure
3. **Uncertainty Assessment**: LLM provided reasonable uncertainty (0.25) with clear reasoning
4. **Entity Extraction**: Found most major entities from the document
5. **Properties**: Extracted relevant properties (titles, locations, dates, amounts)

## Issues Encountered

1. **Model Name**: Initial model `gemini-pro` didn't exist, had to use `gemini-1.5-flash`
2. **Relationship Variations**: Same relationships expressed differently across runs (e.g., EMPLOYS vs WORKS_FOR)
3. **Entity ID Variations**: Some entities had different IDs across runs (affects relationship consistency)

## What We Learned

### 1. LLM Can Extract KG with Uncertainty
✅ **Confirmed**: The LLM successfully extracts structured knowledge graphs AND provides uncertainty assessment in a single call.

### 2. Prompt Engineering Matters
The explicit prompt with clear JSON structure and examples worked well. The LLM understood:
- Entity structure (id, name, type, properties)
- Relationship structure (source, target, type, properties)
- Uncertainty as a float 0-1
- Need for reasoning explanation

### 3. Consistency Is Moderate
- **Entities**: Core entities consistently found, but some variation in peripheral ones
- **Relationships**: More variation due to different ways of expressing same relationship
- **Uncertainty**: Perfectly consistent - always 0.25 for this document

### 4. Uncertainty Assessment Is Reasonable
The LLM correctly identified sources of uncertainty:
- Forward-looking statements (merger closing dates, integration plans)
- Projections (cost synergies, earnings impact)
- Future events (board composition changes)

## Actual Output Example

```json
{
  "entities": [
    {
      "id": "techcorp",
      "name": "TechCorp Corporation",
      "type": "organization",
      "properties": {
        "headquarters": "San Francisco, California",
        "stock_symbol": "NASDAQ: TECH"
      }
    }
  ],
  "relationships": [
    {
      "source": "techcorp",
      "target": "dataflow_systems",
      "type": "ACQUIRED",
      "properties": {
        "amount": "$2.3 billion",
        "expected_close": "Q2 2025"
      }
    }
  ],
  "uncertainty": 0.25,
  "reasoning": "Forward-looking statements and projections introduce uncertainty"
}
```

## Implications for Production

### Viable for MVP ✅
The approach works well enough for an MVP:
- Extraction quality is good (finds most entities)
- Uncertainty assessment is consistent and reasonable
- Single API call is efficient
- JSON structure is reliable

### Areas for Improvement
1. **Entity Resolution**: Need to normalize entity IDs across extractions
2. **Relationship Normalization**: Standardize relationship types (EMPLOYS vs WORKS_FOR)
3. **Chunking**: Test with longer documents that exceed context window
4. **Cost**: Each extraction costs ~$0.001 with Gemini 1.5 Flash

## Next Steps

1. ✅ Basic extraction works
2. **Next**: Test Neo4j persistence - can we write this KG to Neo4j?
3. **Then**: Test uncertainty propagation through pipeline
4. **Finally**: Wrap in extensible framework if all succeeds

## Conclusion

**The experiment succeeded.** We can extract knowledge graphs with uncertainty assessment from text using a single LLM call. The quality is sufficient for MVP, and uncertainty assessment works as designed.