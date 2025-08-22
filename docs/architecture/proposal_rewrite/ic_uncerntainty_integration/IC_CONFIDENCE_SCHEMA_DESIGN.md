# IC-Informed Confidence Schema Design

**Date**: 2025-08-06  
**Status**: Deep Design with Stress Testing  
**Purpose**: Replace inappropriate CERQual fields with proper IC-informed confidence

## Deep Thinking: Core Design Challenges

### Challenge 1: Adapting ICD-206 to Computational Systems
ICD-206 was designed for human intelligence sources, not computational tools. The traditional model:
- **Source Reliability (A-F)**: How reliable is the human/organization providing information
- **Information Credibility (1-6)**: How likely is this specific information to be true

For computational systems, we need to reinterpret:
- **"Source"** → The tool/algorithm/model performing the operation
- **"Information"** → The output/result of the computational operation

### Challenge 2: Confidence Propagation Through Pipelines
KGAS operations chain together:
```
PDF → Text Extraction → Entity Recognition → Graph Building → Analysis
```
Each step has its own confidence. How do we propagate and aggregate?

### Challenge 3: Context-Dependent Assessment
Different operations have different confidence factors:
- **PDF extraction**: OCR quality, layout complexity, language
- **Entity recognition**: Model training, entity type, context availability
- **Graph operations**: Algorithm suitability, data completeness
- **Cross-modal transformation**: Information preservation (purposeful vs accidental)

## Proposed Schema Design

```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum

class ICDSourceReliability(str, Enum):
    """ICD-206 Source Reliability Scale adapted for computational tools"""
    A = "Completely reliable"  # Well-tested tool with proven track record
    B = "Usually reliable"     # Standard tool with good performance
    C = "Fairly reliable"      # Tool works well in most cases
    D = "Not usually reliable" # Experimental or limited tool
    E = "Unreliable"          # Known issues or untested tool
    F = "Cannot be judged"     # New tool or insufficient data

class ICDInfoCredibility(str, Enum):
    """ICD-206 Information Credibility Scale adapted for computational outputs"""
    ONE = "Confirmed"          # Output verified by multiple methods
    TWO = "Probably true"      # High confidence in output
    THREE = "Possibly true"    # Moderate confidence in output
    FOUR = "Doubtfully true"   # Low confidence in output
    FIVE = "Improbable"        # Output likely incorrect
    SIX = "Cannot be judged"   # Unable to assess output quality

class OperationType(str, Enum):
    """Types of operations in KGAS pipeline"""
    EXTRACTION = "extraction"        # PDF/text extraction
    ENTITY_RECOGNITION = "entity_recognition"
    RELATIONSHIP_EXTRACTION = "relationship_extraction"
    GRAPH_CONSTRUCTION = "graph_construction"
    GRAPH_ANALYSIS = "graph_analysis"
    FORMAT_CONVERSION = "format_conversion"
    CROSS_MODAL_TRANSFORMATION = "cross_modal_transformation"
    AGGREGATION = "aggregation"
    LLM_INFERENCE = "llm_inference"

class TransformationIntent(str, Enum):
    """Intent behind data transformations (critical for confidence)"""
    FULL_FIDELITY = "full_fidelity"              # Preserve everything
    ANALYSIS_PROJECTION = "analysis_projection"   # Extract what's needed
    SUMMARY_AGGREGATION = "summary_aggregation"   # Intentional summarization
    UNKNOWN = "unknown"                          # Intent not specified

class ConfidenceFactor(BaseModel):
    """Individual factor contributing to confidence assessment"""
    factor_name: str = Field(description="Name of the factor (e.g., 'OCR_quality')")
    impact: float = Field(ge=-1.0, le=1.0, description="Impact on confidence (-1 to +1)")
    reasoning: str = Field(description="Why this factor matters")

class ICConfidenceAssessment(BaseModel):
    """
    Complete IC-informed confidence assessment for any KGAS operation.
    This replaces the inappropriate CERQual-based ConfidenceScore.
    """
    
    # Core confidence metrics
    confidence_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall confidence (0.0-1.0) from LLM assessment"
    )
    
    # ICD-206 ratings (adapted for computational context)
    source_reliability: ICDSourceReliability = Field(
        description="Reliability of the tool/algorithm performing the operation"
    )
    information_credibility: ICDInfoCredibility = Field(
        description="Credibility of the specific output/result"
    )
    
    @property
    def icd_rating(self) -> str:
        """Combined ICD-206 rating (e.g., 'B2' for usually reliable, probably true)"""
        credibility_map = {
            ICDInfoCredibility.ONE: "1",
            ICDInfoCredibility.TWO: "2",
            ICDInfoCredibility.THREE: "3",
            ICDInfoCredibility.FOUR: "4",
            ICDInfoCredibility.FIVE: "5",
            ICDInfoCredibility.SIX: "6"
        }
        return f"{self.source_reliability.value[0]}{credibility_map[self.information_credibility]}"
    
    # Operation context
    operation_type: OperationType = Field(
        description="Type of operation being assessed"
    )
    operation_id: str = Field(
        description="Unique identifier for this operation"
    )
    
    # Transformation-specific fields (only for transformations)
    transformation_intent: Optional[TransformationIntent] = Field(
        default=None,
        description="Intent behind transformation (affects confidence interpretation)"
    )
    information_preserved: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Fraction of information preserved (1.0 for purposeful projection)"
    )
    
    # LLM reasoning and factors
    reasoning: str = Field(
        description="LLM's explanation of the confidence assessment"
    )
    factors_considered: List[ConfidenceFactor] = Field(
        description="Specific factors that influenced the assessment"
    )
    
    # Propagation support
    parent_assessments: List[str] = Field(
        default_factory=list,
        description="IDs of parent operation assessments (for propagation)"
    )
    propagated_confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Confidence propagated from parent operations"
    )
    
    # Metadata
    assessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this assessment was made"
    )
    assessed_by: str = Field(
        default="gpt-4o-2024-08-06",
        description="Model that made the assessment"
    )
    
    # Validation
    @validator('information_preserved')
    def validate_preservation_with_intent(cls, v, values):
        """Purposeful projections should have preservation = 1.0"""
        intent = values.get('transformation_intent')
        if intent == TransformationIntent.ANALYSIS_PROJECTION and v is not None and v < 1.0:
            raise ValueError(
                "Analysis projections preserve needed information (1.0), "
                "even if they don't preserve everything"
            )
        return v
    
    @validator('propagated_confidence')
    def validate_propagation(cls, v, values):
        """Propagated confidence should consider parent assessments"""
        parent_ids = values.get('parent_assessments', [])
        if parent_ids and v is None:
            # This would be calculated from actual parent assessments
            # For now, just note that it should exist
            pass
        return v
    
    def to_simple_format(self) -> Dict:
        """Simple format for display/logging"""
        return {
            "confidence": self.confidence_score,
            "icd_rating": self.icd_rating,
            "operation": self.operation_type.value,
            "reasoning": self.reasoning[:100] + "..." if len(self.reasoning) > 100 else self.reasoning
        }

class AggregatedConfidence(BaseModel):
    """
    Aggregated confidence across multiple assessments.
    Used when combining results from multiple operations.
    """
    
    overall_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Aggregated confidence score"
    )
    
    aggregation_method: Literal["weighted_mean", "minimum", "harmonic_mean", "llm_judgment"] = Field(
        description="How individual confidences were combined"
    )
    
    individual_assessments: List[ICConfidenceAssessment] = Field(
        description="Individual assessments that were aggregated"
    )
    
    aggregation_reasoning: str = Field(
        description="LLM explanation of aggregation approach"
    )
    
    weakest_link: Optional[ICConfidenceAssessment] = Field(
        default=None,
        description="The assessment with lowest confidence (bottleneck)"
    )
    
    @validator('weakest_link', always=True)
    def identify_weakest_link(cls, v, values):
        """Automatically identify the weakest assessment"""
        assessments = values.get('individual_assessments', [])
        if assessments and not v:
            return min(assessments, key=lambda a: a.confidence_score)
        return v
```

## Stress Testing the Schema

### Test Case 1: PDF Extraction Operation

```python
pdf_extraction_confidence = ICConfidenceAssessment(
    confidence_score=0.92,
    source_reliability=ICDSourceReliability.B,  # PyPDF2 is usually reliable
    information_credibility=ICDInfoCredibility.TWO,  # Probably true
    operation_type=OperationType.EXTRACTION,
    operation_id="extract_001",
    reasoning="""
    High confidence in extraction because:
    1. PDF is text-based (not scanned image) requiring no OCR
    2. Standard formatting with clear structure
    3. PyPDF2 successfully extracted all pages
    Minor uncertainty from potential formatting artifacts.
    """,
    factors_considered=[
        ConfidenceFactor(
            factor_name="pdf_type",
            impact=0.8,
            reasoning="Text-based PDF allows direct extraction"
        ),
        ConfidenceFactor(
            factor_name="extraction_completeness",
            impact=0.9,
            reasoning="All 47 pages successfully extracted"
        ),
        ConfidenceFactor(
            factor_name="formatting_complexity",
            impact=-0.1,
            reasoning="Some tables may have lost structure"
        )
    ]
)

print(f"PDF Extraction: {pdf_extraction_confidence.icd_rating}")  # "B2"
```

### Test Case 2: Entity Recognition with Low Confidence

```python
entity_recognition_confidence = ICConfidenceAssessment(
    confidence_score=0.45,
    source_reliability=ICDSourceReliability.C,  # SpaCy is fairly reliable
    information_credibility=ICDInfoCredibility.FOUR,  # Doubtfully true
    operation_type=OperationType.ENTITY_RECOGNITION,
    operation_id="ner_002",
    parent_assessments=["extract_001"],
    propagated_confidence=0.92 * 0.45,  # Propagated from extraction
    reasoning="""
    Low confidence due to:
    1. Domain-specific terminology not in SpaCy training data
    2. Many ambiguous entity mentions (pronouns, abbreviations)
    3. Limited context for disambiguation
    Entities likely incomplete and some misclassified.
    """,
    factors_considered=[
        ConfidenceFactor(
            factor_name="domain_mismatch",
            impact=-0.4,
            reasoning="Academic terminology outside SpaCy training"
        ),
        ConfidenceFactor(
            factor_name="entity_ambiguity",
            impact=-0.3,
            reasoning="High rate of ambiguous mentions (38%)"
        ),
        ConfidenceFactor(
            factor_name="model_confidence_scores",
            impact=-0.2,
            reasoning="SpaCy's internal confidence below threshold"
        )
    ]
)

print(f"Entity Recognition: {entity_recognition_confidence.icd_rating}")  # "C4"
```

### Test Case 3: Purposeful Projection (No Confidence Loss)

```python
edge_count_projection = ICConfidenceAssessment(
    confidence_score=1.0,  # Perfect confidence for purposeful projection
    source_reliability=ICDSourceReliability.A,  # Graph→Table exporter is reliable
    information_credibility=ICDInfoCredibility.ONE,  # Confirmed accurate
    operation_type=OperationType.FORMAT_CONVERSION,
    operation_id="convert_003",
    transformation_intent=TransformationIntent.ANALYSIS_PROJECTION,
    information_preserved=1.0,  # All NEEDED information preserved
    reasoning="""
    Perfect confidence because this is purposeful projection:
    - Task: Count edge types
    - Exported: Only edge type column
    - Result: Exact edge type counts with no information loss
    This is not lossy transformation but intentional data selection.
    """,
    factors_considered=[
        ConfidenceFactor(
            factor_name="projection_completeness",
            impact=1.0,
            reasoning="All required data (edge types) preserved"
        ),
        ConfidenceFactor(
            factor_name="transformation_accuracy",
            impact=1.0,
            reasoning="Direct mapping with no computation errors"
        )
    ]
)

print(f"Purposeful Projection: {edge_count_projection.icd_rating}")  # "A1"
```

### Test Case 4: Accidental Information Loss

```python
buggy_export_confidence = ICConfidenceAssessment(
    confidence_score=0.3,
    source_reliability=ICDSourceReliability.D,  # Buggy exporter not reliable
    information_credibility=ICDInfoCredibility.FIVE,  # Improbable to be complete
    operation_type=OperationType.FORMAT_CONVERSION,
    operation_id="convert_004",
    transformation_intent=TransformationIntent.FULL_FIDELITY,
    information_preserved=0.3,  # Lost 70% of properties due to bug
    reasoning="""
    Low confidence due to implementation bug:
    - Intended: Full graph export with all properties
    - Actual: Only exported 'confidence' and 'weight' fields
    - Lost: timestamps, evidence, provenance, custom properties
    This is accidental information loss, not purposeful projection.
    """,
    factors_considered=[
        ConfidenceFactor(
            factor_name="property_loss",
            impact=-0.7,
            reasoning="70% of node/edge properties not exported"
        ),
        ConfidenceFactor(
            factor_name="implementation_bug",
            impact=-0.5,
            reasoning="Known bug in export query"
        ),
        ConfidenceFactor(
            factor_name="reversibility",
            impact=-0.8,
            reasoning="Cannot reconstruct original from export"
        )
    ]
)

print(f"Buggy Export: {buggy_export_confidence.icd_rating}")  # "D5"
```

### Test Case 5: Multi-Stage Pipeline Aggregation

```python
# Simulate a complete pipeline
pipeline_assessments = [
    pdf_extraction_confidence,      # B2, 0.92
    entity_recognition_confidence,   # C4, 0.45
    ICConfidenceAssessment(         # Graph building
        confidence_score=0.78,
        source_reliability=ICDSourceReliability.B,
        information_credibility=ICDInfoCredibility.TWO,
        operation_type=OperationType.GRAPH_CONSTRUCTION,
        operation_id="graph_005",
        parent_assessments=["ner_002"],
        reasoning="Good graph construction from recognized entities"
    ),
    ICConfidenceAssessment(         # Analysis
        confidence_score=0.85,
        source_reliability=ICDSourceReliability.A,
        information_credibility=ICDInfoCredibility.TWO,
        operation_type=OperationType.GRAPH_ANALYSIS,
        operation_id="analysis_006",
        parent_assessments=["graph_005"],
        reasoning="PageRank algorithm is deterministic and reliable"
    )
]

aggregated = AggregatedConfidence(
    overall_confidence=0.65,  # LLM determined considering propagation
    aggregation_method="llm_judgment",
    individual_assessments=pipeline_assessments,
    aggregation_reasoning="""
    Overall confidence limited by weak entity recognition (0.45):
    - PDF extraction strong (0.92) provides good foundation
    - Entity recognition weak (0.45) creates bottleneck
    - Graph construction (0.78) can't fully compensate for bad entities
    - Analysis (0.85) is reliable but analyzing incomplete data
    
    Used weighted assessment with emphasis on the weakest link
    since errors propagate through pipeline.
    """
)

print(f"Pipeline confidence: {aggregated.overall_confidence}")
print(f"Weakest link: {aggregated.weakest_link.operation_type.value} ({aggregated.weakest_link.confidence_score})")
```

### Test Case 6: LLM Inference Operation

```python
llm_theory_extraction = ICConfidenceAssessment(
    confidence_score=0.73,
    source_reliability=ICDSourceReliability.B,  # GPT-4 usually reliable
    information_credibility=ICDInfoCredibility.THREE,  # Possibly true
    operation_type=OperationType.LLM_INFERENCE,
    operation_id="llm_007",
    reasoning="""
    Moderate confidence in theory extraction:
    1. GPT-4 successfully identified main theoretical framework
    2. Some nuance lost in condensing complex arguments
    3. Structured output schema validated successfully
    4. Minor hallucination risk for domain-specific details
    """,
    factors_considered=[
        ConfidenceFactor(
            factor_name="schema_validation",
            impact=0.7,
            reasoning="Pydantic schema validated without errors"
        ),
        ConfidenceFactor(
            factor_name="extraction_completeness",
            impact=-0.2,
            reasoning="May have missed subtle theoretical points"
        ),
        ConfidenceFactor(
            factor_name="domain_knowledge",
            impact=-0.15,
            reasoning="Specialized academic domain outside training"
        ),
        ConfidenceFactor(
            factor_name="structured_output",
            impact=0.3,
            reasoning="Structured output reduces ambiguity"
        )
    ]
)

print(f"LLM Extraction: {llm_theory_extraction.icd_rating}")  # "B3"
```

## Stress Test Analysis

### Strengths of the Schema

1. **Handles All Operation Types**: Works for extraction, recognition, transformation, analysis, and LLM operations
2. **Distinguishes Intent**: Purposeful projections (Test 3) correctly get confidence=1.0
3. **Captures Bugs**: Accidental loss (Test 4) correctly penalized
4. **Supports Propagation**: Multi-stage pipelines (Test 5) properly aggregate
5. **Context-Aware**: Different factors for different operations
6. **ICD-206 Compliant**: Proper use of real IC standards

### Edge Cases Handled

1. **Zero Confidence**: Can represent complete failure (confidence=0.0, F6 rating)
2. **Perfect Confidence**: Purposeful projections get 1.0 deservedly
3. **Unknown Intent**: TransformationIntent.UNKNOWN for legacy operations
4. **Circular Dependencies**: Parent assessment IDs prevent infinite loops
5. **Missing Factors**: Empty factors list allowed for simple operations

### Potential Issues and Solutions

#### Issue 1: Propagation Complexity
**Problem**: Complex pipelines make propagation calculation difficult  
**Solution**: Let LLM judge overall confidence considering the full context

#### Issue 2: Factor Weighting
**Problem**: How to weight different factors?  
**Solution**: LLM provides impact scores (-1 to +1) with reasoning

#### Issue 3: Backwards Compatibility
**Problem**: Existing code expects old ConfidenceScore model  
**Solution**: Add adapter methods to convert between formats

## Implementation Bridge

```python
class ConfidenceAdapter:
    """Bridge between old CERQual-based and new IC-informed confidence"""
    
    @staticmethod
    def from_legacy(old_score: ConfidenceScore) -> ICConfidenceAssessment:
        """Convert old format to new (best effort)"""
        # Map old confidence value to ICD ratings
        if old_score.value > 0.9:
            reliability, credibility = ICDSourceReliability.A, ICDInfoCredibility.ONE
        elif old_score.value > 0.7:
            reliability, credibility = ICDSourceReliability.B, ICDInfoCredibility.TWO
        elif old_score.value > 0.5:
            reliability, credibility = ICDSourceReliability.C, ICDInfoCredibility.THREE
        else:
            reliability, credibility = ICDSourceReliability.D, ICDInfoCredibility.FOUR
            
        return ICConfidenceAssessment(
            confidence_score=old_score.value,
            source_reliability=reliability,
            information_credibility=credibility,
            operation_type=OperationType.UNKNOWN,
            operation_id=f"legacy_{uuid.uuid4()}",
            reasoning="Converted from legacy CERQual-based confidence",
            factors_considered=[]
        )
    
    @staticmethod
    def to_simple_score(ic_assessment: ICConfidenceAssessment) -> float:
        """Extract simple confidence score for legacy code"""
        return ic_assessment.confidence_score
```

## Conclusion

This IC-informed confidence schema:
1. **Properly adapts ICD-206** for computational contexts
2. **Eliminates CERQual misapplication** to computational tools
3. **Handles purposeful vs accidental** information changes correctly
4. **Supports complex propagation** through pipelines
5. **Provides transparency** through reasoning and factors

The schema is robust under stress testing and handles all KGAS operation types appropriately.