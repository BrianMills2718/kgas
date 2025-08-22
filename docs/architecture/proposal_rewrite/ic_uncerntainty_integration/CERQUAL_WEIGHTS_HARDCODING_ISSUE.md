# CERQual Weights Hardcoding Issue & Resolution Plan

**Date**: 2025-08-06  
**Status**: Issue Identified, Resolution Planned  
**Priority**: HIGH - Blocks flexible uncertainty quantification

## The Problem

### Hardcoded Weights Found
In `/src/core/confidence_scoring/cerqual_assessment.py` lines 43-48:

```python
def calculate_combined_score(self) -> float:
    """Calculate combined CERQual confidence score"""
    # Weighted combination: all dimensions are important but methodological limitations 
    # and adequacy of data are slightly more critical
    weights = {
        "methodological_limitations": 0.3,
        "relevance": 0.2,
        "coherence": 0.2,
        "adequacy_of_data": 0.3
    }
```

And line 139:
```python
# Combine with base confidence using weighted average
combined_score = (score.value * 0.6) + (cerqual_score * 0.4)
```

### Why This Is Wrong

1. **Context-Dependent Weights**: Different analysis types need different weight emphasis
   - Entity extraction: methodological_limitations might be most critical
   - Theory synthesis: coherence might be most important
   - Cross-document analysis: relevance might dominate

2. **Domain-Specific Requirements**: Academic domains have different priorities
   - Medical research: adequacy_of_data critical
   - Literary analysis: coherence paramount
   - Technical documentation: methodological_limitations key

3. **Task-Specific Emphasis**: Different tasks within same domain vary
   - Initial extraction: methodology matters most
   - Final synthesis: coherence and relevance matter most

4. **CERQual Misapplication**: CERQual is for human qualitative research synthesis, not computational tools
   - These dimensions don't even apply to tool outputs
   - We're forcing a human research framework onto computational processes

## The Solution: LLM-Based Flexible Aggregation

### Immediate Fix: Remove Hardcoded Weights

```python
class CERQualAssessment:
    """DEPRECATED: Moving to LLM-based assessment"""
    
    def calculate_combined_score_llm(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to flexibly aggregate CERQual dimensions based on context
        
        Returns:
            - score: float (0.0-1.0)
            - weights_used: Dict[str, float] (for transparency)
            - reasoning: str (explanation of weight selection)
        """
        prompt = f"""
        Given these quality dimensions for {context.get('task_type', 'analysis')}:
        - Methodological limitations: {self.methodological_limitations}
        - Relevance: {self.relevance}
        - Coherence: {self.coherence}
        - Adequacy of data: {self.adequacy_of_data}
        
        Context:
        - Domain: {context.get('domain', 'general')}
        - Analysis phase: {context.get('phase', 'unknown')}
        - Data type: {context.get('data_type', 'mixed')}
        
        Determine appropriate weights for combining these dimensions into a single 
        confidence score. Consider which dimensions are most critical for this 
        specific context and explain your reasoning.
        
        Return:
        1. Combined score (0.0-1.0)
        2. Weights used for each dimension
        3. Brief reasoning for weight selection
        """
        
        # LLM determines contextually appropriate weights
        response = llm.structured_completion(
            prompt=prompt,
            schema=CERQualAggregationResponse
        )
        
        return {
            "score": response.combined_score,
            "weights_used": response.weights,
            "reasoning": response.reasoning
        }
```

### Better Solution: Replace CERQual with IC Standards

Since CERQual is misapplied (it's for human research, not computational tools), replace with actual IC standards:

```python
class ICConfidenceAssessment:
    """
    IC-compliant confidence assessment using ICD-206 standards
    """
    
    def assess_with_llm(self, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to assess confidence with ICD-206 standards
        
        Returns:
            - confidence_score: float (0.0-1.0)
            - source_reliability: str (A-F per ICD-206)
            - information_credibility: int (1-6 per ICD-206)
            - reasoning: str (explanation of assessment)
        """
        prompt = f"""
        Assess the confidence level for this {context.get('data_type', 'data')}:
        
        Data: {data}
        
        Context:
        - Processing method: {context.get('method', 'unknown')}
        - Data completeness: {context.get('completeness', 'unknown')}
        - Processing phase: {context.get('phase', 'unknown')}
        
        Using ICD-206 standards, provide:
        1. Overall confidence score (0.0-1.0)
        2. Source reliability rating (A=Completely reliable to F=Cannot be judged)
        3. Information credibility (1=Confirmed to 6=Cannot be judged)
        4. Brief reasoning considering completeness and accuracy
        
        Focus on actual data quality, not theoretical frameworks.
        """
        
        response = llm.structured_completion(
            prompt=prompt,
            schema=ICAssessmentResponse
        )
        
        return {
            "confidence_score": response.confidence,
            "icd_206_rating": f"{response.source_reliability}{response.info_credibility}",
            "reasoning": response.reasoning
        }
```

### Migration Path

#### Phase 1: Add LLM Alternative (Week 1)
1. Add `calculate_combined_score_llm()` method alongside existing
2. Add feature flag to switch between hardcoded and LLM weights
3. Log both results for comparison and validation

#### Phase 2: Deprecate CERQual (Week 2)
1. Mark CERQual methods as deprecated
2. Create ICConfidenceAssessment class with proper IC standards
3. Update all callers to use new assessment

#### Phase 3: Remove Hardcoded Values (Week 3)
1. Remove hardcoded weights entirely
2. Remove CERQual dimensions from ConfidenceScore model
3. Simplify to single confidence score with IC ratings

## Specific Changes Required

### 1. Update ConfidenceScore Model
```python
class ConfidenceScore(BaseModel):
    """Simplified confidence model with IC standards"""
    
    # Core confidence
    value: float = Field(ge=0.0, le=1.0)
    confidence_range: Optional[Tuple[float, float]] = None
    
    # IC Standards (not CERQual)
    icd_206_source_reliability: Optional[str] = Field(
        default=None,
        pattern="^[A-F]$",
        description="ICD-206 source reliability (A-F)"
    )
    icd_206_info_credibility: Optional[int] = Field(
        default=None,
        ge=1, le=6,
        description="ICD-206 information credibility (1-6)"
    )
    
    # Remove these CERQual fields:
    # - methodological_limitations
    # - relevance  
    # - coherence
    # - adequacy_of_data
    
    # Keep essential fields
    evidence_weight: PositiveInt
    source: Optional[str]
    assessment_reasoning: Optional[str]  # NEW: LLM's reasoning
```

### 2. Create Flexible Aggregation Service
```python
class FlexibleConfidenceAggregator:
    """Context-aware confidence aggregation using LLM"""
    
    def __init__(self, llm_service):
        self.llm = llm_service
    
    def aggregate_scores(
        self, 
        scores: List[ConfidenceScore],
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """
        Aggregate multiple confidence scores based on context
        
        The LLM considers:
        - Task type and phase
        - Domain requirements
        - Data characteristics
        - Score sources and reliability
        """
        
        prompt = self._build_aggregation_prompt(scores, context)
        response = self.llm.structured_completion(
            prompt=prompt,
            schema=AggregatedConfidenceResponse
        )
        
        return ConfidenceScore(
            value=response.aggregated_score,
            icd_206_source_reliability=response.source_reliability,
            icd_206_info_credibility=response.info_credibility,
            evidence_weight=len(scores),
            assessment_reasoning=response.reasoning,
            metadata={
                "aggregation_context": context,
                "component_scores": [s.value for s in scores]
            }
        )
```

### 3. Update All Callers
Search and update all code that uses CERQual methods:
- Replace `calculate_combined_score()` with LLM-based version
- Remove references to CERQual dimensions
- Update to use IC standards

## Benefits of This Approach

### 1. **Contextual Flexibility**
- Weights adapt to specific task and domain
- No more one-size-fits-all scoring
- Dynamic adjustment based on data characteristics

### 2. **Transparency**
- LLM provides reasoning for weight selection
- Auditable decision process
- Clear explanation of confidence assessment

### 3. **Standards Compliance**
- Uses real IC standards (ICD-206)
- Removes misapplied CERQual framework
- Proper source reliability and credibility ratings

### 4. **Simplicity**
- Single confidence score with reasoning
- No complex multi-dimensional frameworks
- Clear, interpretable outputs

## Testing Strategy

### Validation Approach
1. **Parallel Running**: Run both hardcoded and LLM methods, compare results
2. **Context Variation**: Test with different contexts to verify adaptation
3. **Reasoning Review**: Manually review LLM reasoning for sensibility
4. **Performance Monitoring**: Track LLM call overhead and optimize

### Test Cases
```python
def test_flexible_aggregation():
    """Test that LLM aggregation adapts to context"""
    
    # Same scores, different contexts
    scores = [ConfidenceScore(value=0.7), ConfidenceScore(value=0.8)]
    
    # Medical context - should weight data adequacy higher
    medical_result = aggregator.aggregate_scores(scores, {
        "domain": "medical",
        "task": "diagnosis_extraction"
    })
    
    # Literary context - should weight coherence higher
    literary_result = aggregator.aggregate_scores(scores, {
        "domain": "literary",
        "task": "theme_analysis"
    })
    
    # Results should differ based on context
    assert medical_result.value != literary_result.value
    assert medical_result.assessment_reasoning != literary_result.assessment_reasoning
```

## Implementation Priority

### Immediate (This Week)
1. Create parallel LLM-based scoring method
2. Add feature flag for gradual rollout
3. Start logging comparison data

### Short-term (Next 2 Weeks)
1. Create ICConfidenceAssessment class
2. Deprecate CERQual methods
3. Update documentation

### Medium-term (Within Month)
1. Migrate all callers to new system
2. Remove hardcoded weights
3. Simplify ConfidenceScore model

## Conclusion

The hardcoded CERQual weights represent a fundamental misunderstanding:
1. **CERQual is for human research**, not computational tools
2. **Weights must be contextual**, not fixed
3. **IC standards (ICD-206) are more appropriate** than CERQual

The solution is to let LLMs handle the complexity of contextual weight selection while we focus on providing clear IC-compliant outputs and maintaining transparency through reasoning.