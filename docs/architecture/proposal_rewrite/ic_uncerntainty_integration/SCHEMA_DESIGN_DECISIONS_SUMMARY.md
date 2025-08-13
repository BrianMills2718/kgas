# IC Confidence Schema: Key Design Decisions

**Date**: 2025-08-06  
**Status**: Design Complete  
**Impact**: Replaces inappropriate CERQual with proper IC-informed confidence

## Problem Solved

The current `ConfidenceScore` model misapplies CERQual framework (designed for human qualitative research) to computational tools. Fields like "methodological_limitations" and "adequacy_of_data" make no sense for a PDF parser or entity extractor.

## Solution: ICConfidenceAssessment

### Core Innovation 1: Adapted ICD-206 for Computational Context

**Traditional ICD-206** (for human intelligence):
- Source = Human informant
- Information = What they report

**Our Adaptation** (for computational systems):
- Source = Tool/Algorithm/Model
- Information = Computational output

```python
# Examples:
"B2" = Usually reliable tool, probably correct output (PyPDF2 extracting clean PDF)
"C4" = Fairly reliable tool, doubtful output (SpaCy on domain-specific text)
"A1" = Completely reliable tool, confirmed output (Purposeful projection)
"D5" = Unreliable tool, improbable output (Buggy exporter losing data)
```

### Core Innovation 2: Transformation Intent

**Critical Insight**: Purposeful projection ≠ Lossy transformation

```python
transformation_intent: TransformationIntent
- FULL_FIDELITY: Keep everything (confidence drops if anything lost)
- ANALYSIS_PROJECTION: Extract what's needed (confidence = 1.0 if got what needed)
- SUMMARY_AGGREGATION: Intentional summary (small confidence penalty)
```

This solves the issue where exporting only edge types for counting would incorrectly be considered "lossy" when it's actually perfect for the task.

### Core Innovation 3: Factor-Based Reasoning

Instead of hardcoded CERQual fields, LLM assesses relevant factors for each operation:

```python
factors_considered: List[ConfidenceFactor]
# Each factor has:
- factor_name: "OCR_quality" or "domain_mismatch"
- impact: -1.0 to +1.0 (negative = reduces confidence)
- reasoning: Why this matters
```

**For PDF extraction**, considers: PDF type, OCR quality, completeness  
**For entity recognition**, considers: Domain match, ambiguity, model confidence  
**For transformations**, considers: Intent, preservation, reversibility

### Core Innovation 4: Propagation Through Pipelines

```python
parent_assessments: List[str]  # Track dependencies
propagated_confidence: float   # Confidence from upstream

# Aggregation handles weakest link problem:
aggregated = AggregatedConfidence(
    aggregation_method="llm_judgment",  # LLM considers full context
    weakest_link=automatically_identified  # Bottleneck highlighted
)
```

## Why This Design Works

### 1. Eliminates Category Error
- ❌ OLD: "methodological_limitations" for a PDF parser (nonsense)
- ✅ NEW: "PDF type impact" and "extraction completeness" (makes sense)

### 2. Handles All KGAS Operations
- Extraction: OCR quality, format complexity
- Recognition: Model suitability, domain match
- Transformation: Intent, preservation, reversibility
- Analysis: Algorithm suitability, data completeness
- LLM inference: Schema validation, hallucination risk

### 3. Respects Purposeful Projection
```python
# Task: Count edge types
# Export: Only edge types
confidence_score = 1.0  # Perfect! Got exactly what needed
transformation_intent = ANALYSIS_PROJECTION
information_preserved = 1.0  # For the NEEDED information
```

### 4. Penalizes Bugs, Not Design Choices
```python
# Buggy exporter only exports 2 fields out of 10
confidence_score = 0.3  # Low! Lost needed information
transformation_intent = FULL_FIDELITY  # Tried to keep everything
information_preserved = 0.2  # Actually lost 80%
```

## Migration Strategy

### Phase 1: Parallel Systems
```python
class ConfidenceAdapter:
    """Run both systems in parallel during migration"""
    
    def assess(self, operation) -> Tuple[ConfidenceScore, ICConfidenceAssessment]:
        old = self.legacy_assessment(operation)  # Current CERQual-based
        new = self.ic_assessment(operation)      # New IC-informed
        
        # Log differences for validation
        if abs(old.value - new.confidence_score) > 0.3:
            logger.warning(f"Large confidence delta: {old.value} vs {new.confidence_score}")
        
        return old, new  # Use old for now, validate new
```

### Phase 2: Switch Default
- Make new schema default, keep adapter for legacy code
- Update all new tools to use ICConfidenceAssessment

### Phase 3: Remove Legacy
- Delete ConfidenceScore model
- Remove CERQual fields completely

## Quick Reference Card

### When to Use Each ICD Rating

**A1 (Completely reliable, Confirmed)**
- Deterministic algorithms with verified inputs
- Purposeful projections getting needed data
- Lossless format conversions

**B2 (Usually reliable, Probably true)**
- Standard tools on appropriate data
- Good extraction from clean sources
- Well-trained models on in-domain data

**C3 (Fairly reliable, Possibly true)**
- Tools operating at edge of capabilities
- Some uncertainty in inputs/processing
- Moderate information loss

**D4 (Not usually reliable, Doubtfully true)**
- Experimental tools
- Poor quality inputs
- Significant information loss

**E5 (Unreliable, Improbable)**
- Known buggy implementations
- Severe data quality issues
- Critical information lost

**F6 (Cannot judge)**
- New/untested tools
- No basis for assessment
- Unknown data quality

## Implementation Checklist

- [ ] Create ICConfidenceAssessment Pydantic model
- [ ] Build ConfidenceAdapter for migration
- [ ] Create LLM confidence estimation service
- [ ] Update tools to use new schema
- [ ] Add transformation intent tracking
- [ ] Implement aggregation for pipelines
- [ ] Validate with real KGAS operations
- [ ] Remove legacy ConfidenceScore model

## Conclusion

This design solves all identified problems:
1. ✅ Removes inappropriate CERQual framework
2. ✅ Uses real ICD-206 standards properly
3. ✅ Distinguishes purposeful projection from accidental loss
4. ✅ Provides transparent reasoning with factors
5. ✅ Supports complex pipeline propagation
6. ✅ Works for all KGAS operation types

The schema is pragmatic, standards-compliant, and ready for implementation.