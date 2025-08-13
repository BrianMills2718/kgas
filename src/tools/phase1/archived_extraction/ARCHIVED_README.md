# Archived Pattern-Based Extraction Tools

**Status**: ARCHIVED - These tools are preserved for potential future use but are NOT the recommended extraction approach.

## Why Archived?

These tools were causing confusion during development by suggesting a multi-step extraction pipeline when the correct approach is to use T23c for complete extraction in a single LLM call.

## Archived Tools:

### T23a SpaCy NER (4 variants)
- `t23a_spacy_ner.py` - Base implementation
- `t23a_spacy_ner_unified.py` - Service-integrated version
- `t23a_spacy_ner_standalone.py` - Self-contained version
- `t23a_llm_enhanced.py` - Hybrid SpaCy/LLM approach

**Purpose**: Fast entity extraction using SpaCy pre-trained models
**Limitation**: Extracts ONLY entities, no relationships
**Use Case**: High-volume processing where LLM costs are prohibitive

### T27 Relationship Extractor (4 variants)
- `t27_relationship_extractor.py` - Base implementation
- `t27_relationship_extractor_unified.py` - Service-integrated version
- `t27_relationship_extractor_standalone.py` - Self-contained version
- `t27_relationship_extractor_fixed.py` - Bug-fixed version

**Purpose**: Pattern-based relationship extraction using regex
**Limitation**: Only finds explicit patterns like "X works for Y"
**Use Case**: Structured text with predictable relationship patterns

## The Problem with This Approach

Using T23a + T27 suggests a pipeline:
1. Extract entities with SpaCy (T23a)
2. Extract relationships between those entities (T27)

This is suboptimal because:
- Two separate processing steps
- Pattern-based relationship extraction misses implicit relationships
- No property extraction
- No unified understanding of the text

## The Correct Approach

**Use T23c (Ontology-Aware Extractor)** which extracts entities + relationships + properties in one LLM call.

Benefits:
- Single API call
- Full contextual understanding
- Extracts implicit relationships
- Extracts entity properties
- Ontology-guided extraction

## When These Tools Might Still Be Useful

1. **Cost-Sensitive Batch Processing**: When processing millions of documents where LLM costs would be prohibitive
2. **Structured Text**: When text follows predictable patterns (e.g., regulatory filings)
3. **Entity-Only Needs**: When you genuinely only need entities without relationships
4. **Hybrid Approaches**: Using SpaCy for initial filtering before LLM processing

## Restoration Instructions

To restore these tools:

```bash
# Move files back to parent directory
cd src/tools/phase1
mv archived_extraction/t23a_*.py .
mv archived_extraction/t27_*.py .

# Update imports in your code
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
```

## Migration Guide

If you have code using these tools, migrate to T23c:

### Before (Two-Step Process):
```python
# Step 1: Extract entities
entities = spacy_ner.extract_entities(text)

# Step 2: Extract relationships
relationships = relationship_extractor.extract_relationships(text, entities)
```

### After (Single LLM Call):
```python
# Extract everything in one call
result = ontology_extractor.extract_entities(
    text=text,
    ontology=domain_ontology,
    # Returns entities AND relationships AND properties
)
entities = result.entities
relationships = result.relationships
```

## Archive Date: 2025-08-04

Archived to reduce confusion and establish T23c as the default extraction approach for the KGAS system.