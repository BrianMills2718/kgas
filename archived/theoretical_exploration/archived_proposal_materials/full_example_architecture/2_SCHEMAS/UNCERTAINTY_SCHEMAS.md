# Uncertainty Schemas for KGAS Tools

## Core Principle: Uncertainty is Localized

Missing data in one stream doesn't contaminate unrelated analyses. For example:
- Missing 30% psychology scores → affects SEM modeling but NOT community detection
- Missing some tweets → affects temporal coverage but NOT user psychology analysis
- Each tool assesses uncertainty based on what IT needs, not global data completeness

## Pure LLM Intelligence Approach: Single Universal Schema

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

# =======================
# UNIVERSAL UNCERTAINTY (ALL Operations)
# =======================

class UniversalUncertainty(BaseModel):
    """Single uncertainty format for ALL operations"""
    uncertainty: float = Field(
        ge=0, le=1, 
        description="0=certain, 1=uncertain"
    )
    reasoning: str = Field(
        description="Expert reasoning for assessment"
    )
    evidence_count: Optional[int] = Field(
        default=None,
        description="Number of evidences (for aggregations)"
    )
    
    # Optional fields for richer context when needed
    primary_factors: Optional[List[str]] = Field(
        default=None,
        description="Main factors affecting uncertainty"
    )
    data_coverage: Optional[float] = Field(
        default=None,
        ge=0, le=1,
        description="Fraction of needed data available"
    )
    propagates_to: Optional[List[str]] = Field(
        default=None,
        description="Which downstream analyses are affected"
    )

class ToolRequest(BaseModel):
    """Input to any tool"""
    input_data: Dict[str, Any]
    theory_schema: Optional[Dict] = None
    options: Optional[Dict] = None
    
    # Upstream uncertainties (for context, not contamination)
    upstream_uncertainties: Optional[Dict[str, UniversalUncertainty]] = None

class ToolResult(BaseModel):
    """Output from any tool"""
    status: str = Field(description="success, error, partial")
    data: Dict[str, Any] = Field(description="Tool output data")
    uncertainty: UniversalUncertainty = Field(description="Tool's uncertainty assessment")
    metadata: Optional[Dict] = None
    provenance: Optional[Dict] = None
```

## Single Assessment Method for All Operations

```python
def assess_uncertainty(context: Dict[str, Any]) -> UniversalUncertainty:
    """LLM handles ALL uncertainty logic - no magic numbers"""
    
    prompt = f"""
    As an expert, assess uncertainty for this {context['type']} operation.
    
    Context: {json.dumps(context, indent=2)}
    
    For individual tools:
    - Consider data quality, completeness, and validity
    - Assess how well the tool's assumptions match reality
    
    For aggregations:
    - Consider how well the evidences agree
    - More agreeing evidence should reduce uncertainty
    - Conflicting evidence should increase uncertainty
    - Consider whether evidences are truly independent
    
    For sequential operations:
    - Consider how upstream uncertainty affects this operation
    - Some operations amplify uncertainty, others are robust
    
    For cross-modal synthesis:
    - Consider convergence across different analysis types
    - Agreement across modalities validates findings
    
    Return your assessment with:
    - uncertainty: 0-1 score
    - reasoning: Complete explanation of your assessment
    - evidence_count: Number of evidences (if aggregating)
    - primary_factors: Main factors affecting uncertainty (optional)
    - data_coverage: Fraction of needed data (optional)
    - propagates_to: Affected downstream analyses (optional)
    """
    
    return llm.structured_output(prompt, UniversalUncertainty)
```

## Dynamic Tool Generation Schemas

```python
class AlgorithmType(str, Enum):
    MATHEMATICAL = "mathematical"  # Formulas like MCR
    LOGICAL = "logical"  # Rule-based like prototype identification
    PROCEDURAL = "procedural"  # Step-by-step like depersonalization

class AlgorithmSpecification(BaseModel):
    """Specification extracted from theory"""
    name: str
    type: AlgorithmType
    formula_or_rules: Union[str, List[str]]
    parameters: Dict[str, str] = Field(description="Parameter descriptions")
    required_inputs: Dict[str, str] = Field(description="Required input fields")
    output_format: Dict[str, str] = Field(description="Expected output structure")

class DynamicToolGenerationRequest(BaseModel):
    """Request to generate a tool from theory"""
    algorithm_spec: AlgorithmSpecification
    theory_name: str
    context: Optional[str] = Field(description="Additional context for generation")

class GeneratedToolCode(BaseModel):
    """Generated tool ready for compilation"""
    tool_id: str
    python_code: str
    algorithm_spec: AlgorithmSpecification
    
    # How this tool assesses uncertainty
    uncertainty_factors: List[str] = Field(
        description="What factors this tool considers for uncertainty"
    )
    
    # Dependencies
    imports_required: List[str]
    input_schema: Dict
    output_schema: Dict

class DynamicToolResult(ToolResult):
    """Result from dynamically generated tool"""
    algorithm_used: str
    calculation_details: Optional[Dict] = Field(
        description="Details about the calculation for transparency"
    )
    
    # Tool-specific uncertainty based on the calculation
    calculation_uncertainty: ToolUncertainty = Field(
        description="Uncertainty specific to this algorithm's assumptions"
    )
```

## Uncertainty Propagation Schemas

```python
class PropagationType(str, Enum):
    """How uncertainties combine"""
    SEQUENTIAL = "sequential"  # Dependent tools in sequence
    PARALLEL = "parallel"  # Independent analyses
    AGGREGATION = "aggregation"  # Multiple instances to population
    VALIDATION = "validation"  # Cross-checking reduces uncertainty

class UncertaintyFlow(BaseModel):
    """Track uncertainty through DAG"""
    tool_id: str
    tool_type: str
    
    # Input uncertainties
    inherited_uncertainties: Dict[str, ToolUncertainty] = Field(
        description="Uncertainties from upstream tools"
    )
    
    # This tool's contribution
    local_uncertainty: ToolUncertainty = Field(
        description="Uncertainty from this tool's operation"
    )
    
    # Combined output
    output_uncertainty: ToolUncertainty = Field(
        description="Combined uncertainty after this tool"
    )
    
    # How it was combined
    propagation_type: PropagationType
    combination_method: str = Field(description="How uncertainties were combined")

class DAGUncertaintyTrace(BaseModel):
    """Complete uncertainty trace through DAG execution"""
    dag_id: str
    execution_timestamp: str
    
    # Uncertainty at each step
    tool_traces: List[UncertaintyFlow]
    
    # Critical path analysis
    critical_uncertainties: List[Dict] = Field(
        description="Tools contributing most to final uncertainty"
    )
    
    # Final assessment
    final_uncertainty: ToolUncertainty
    
    # Recommendations
    improvement_suggestions: List[str] = Field(
        description="Where to focus to reduce uncertainty"
    )
```

## Cross-Modal Synthesis Schema

```python
class ModalityEvidence(BaseModel):
    """Evidence from one modality"""
    modality: str = Field(description="graph, table, or vector")
    key_findings: List[str]
    belief_masses: BeliefMass
    supporting_metrics: Dict[str, float]

class CrossModalSynthesisRequest(ToolRequest):
    """Request for cross-modal synthesis"""
    modality_results: Dict[str, ModalityEvidence]
    synthesis_goal: str = Field(description="What we're trying to determine")

class ConvergenceAssessment(BaseModel):
    """How well modalities agree"""
    agreement_score: float = Field(ge=0, le=1)
    convergent_findings: List[str]
    divergent_findings: List[str]
    explanation: str

class CrossModalSynthesisResult(ToolResult):
    """Synthesized cross-modal findings"""
    synthesis: Dict[str, Any]
    convergence: ConvergenceAssessment
    
    # Reduced uncertainty from convergence
    integrated_uncertainty: ToolUncertainty = Field(
        description="Lower uncertainty when modalities agree"
    )
    
    # Which modality was most informative
    primary_evidence_source: str
    evidence_weights: Dict[str, float] = Field(
        description="How much each modality contributed"
    )
```

## Practical Examples

### Example 1: MCR Calculator Uncertainty (Localized)

```python
mcr_context = {
    "type": "mcr_calculation",
    "coverage": 0.70,
    "missing_users": 150,
    "total_users": 500,
    "calculation_details": {
        "method": "cosine_distance",
        "groups_identified": 2
    }
}

mcr_uncertainty = assess_uncertainty(mcr_context)
# Returns:
# UniversalUncertainty(
#     uncertainty=0.30,
#     reasoning="MCR calculated for 70% of users. Missing 30% doesn't affect the 70% we calculated. Cosine distance appropriate for text-derived position vectors.",
#     primary_factors=["30% users missing position vectors", "Position vectors derived from text embeddings"],
#     data_coverage=0.70,
#     propagates_to=["prototype_identification", "polarization_measurement"]
# )
```

### Example 2: Community Detection Uncertainty (Independent)

```python
community_context = {
    "type": "community_detection",
    "modularity": 0.72,
    "stability_across_runs": 0.95,
    "graph_completeness": 1.0,
    "note": "Missing psychology scores irrelevant for topology"
}

community_uncertainty = assess_uncertainty(community_context)
# Returns:
# UniversalUncertainty(
#     uncertainty=0.15,
#     reasoning="Graph structure clear with modularity=0.72. Communities stable across multiple runs. Missing psychology scores don't affect graph topology.",
#     primary_factors=["High modularity score", "Stable communities"],
#     data_coverage=1.0,
#     propagates_to=["community_level_analysis"]
# )
```

### Example 3: Tweet→User Aggregation

```python
aggregation_context = {
    "type": "tweet_to_user_aggregation",
    "user_id": "user_042",
    "evidences": [
        {"tweet_id": "001", "uncertainty": 0.22, "reasoning": "Clear stance..."},
        {"tweet_id": "002", "uncertainty": 0.20, "reasoning": "Consistent..."},
        # ... 21 more tweets with uncertainties between 0.18-0.25
    ],
    "agreement_analysis": "23 tweets show consistent pro-vaccine stance"
}

aggregation_uncertainty = assess_uncertainty(aggregation_context)
# Returns:
# UniversalUncertainty(
#     uncertainty=0.15,  # LLM reduces from ~0.22 average due to consistency
#     reasoning="23 consistent tweets provide strong evidence of user stance. Low conflict between tweets increases confidence.",
#     evidence_count=23,
#     data_coverage=1.0
# )
```

## Key Design Principles

1. **Uncertainty is Local**: Each tool assesses based on ITS needs, not global completeness
2. **Missing Data is Selective**: Only affects tools that need that specific data
3. **Aggregation Reduces Uncertainty**: Multiple consistent evidences increase confidence
4. **Convergence Validates**: Agreement across modalities reduces uncertainty
5. **Propagation is Selective**: Uncertainty only propagates to dependent downstream tools
6. **Context Matters**: LLM considers domain knowledge, not just statistics

## Implementation Notes

- Every tool outputs `ToolUncertainty` as part of `ToolResult`
- Aggregation tools are special - they reduce uncertainty through evidence combination
- Dynamic tools assess uncertainty based on their specific calculation needs
- Cross-modal synthesis leverages convergence to reduce uncertainty
- The DAG executor tracks uncertainty flow but doesn't blindly propagate everything