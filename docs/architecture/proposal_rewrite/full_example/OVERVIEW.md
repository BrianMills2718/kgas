# KGAS Uncertainty System: Comprehensive Overview and Design Decisions

## Date: 2025-08-12
## Purpose: Complete record of design decisions, insights, and implementation approach for KGAS uncertainty system

## Executive Summary

This document captures the complete design and rationale for KGAS's uncertainty tracking system, which enables transparent computational social science by embedding expert reasoning throughout the analysis pipeline. The system uses dynamically generated tools from theory schemas, Dempster-Shafer evidence combination, and comprehensive provenance tracking to make social science analyses reproducible and reviewable.

## Core Innovation: Dynamic Tool Generation with Uncertainty

### What We're Building
A system that:
1. **Extracts theories** from academic papers into structured schemas
2. **Generates analysis tools** dynamically from those schemas using LLMs
3. **Tracks uncertainty** at every step with expert reasoning
4. **Aggregates evidence** using Dempster-Shafer theory
5. **Provides complete provenance** for every decision and assessment

### What We're NOT Building
- A calibrated measurement instrument (0.30 doesn't mean 70% accurate in objective terms)
- A predictive system for future behavior
- A causal inference engine
- A system that claims objective truth

## On Subjectivity and Meaningful Uncertainty Scores

**Uncertainty scores ARE meaningful** - they represent the LLM's subjective expert assessment:
- **0.30 means**: What the prompt defines it to mean (typically "moderate confidence")
- **Subjectivity is intentional**: Mirrors how social science experts make judgments
- **Consistency over calibration**: Same prompt + similar evidence = similar assessments
- **Transparency over precision**: Reasoning explains the score, making subjectivity reviewable
- **No different from human experts**: Social scientists routinely make subjective confidence assessments

This is not a limitation to solve - it's an accurate reflection of social science epistemology.

## Fundamental Design Decisions

### 1. Dynamic Tool Generation is Central

**Decision**: Tools are generated from theory schemas at runtime, not pre-built.

**Rationale**: 
- Enables any theory to be computationalized without anticipating all possibilities
- Maintains fidelity to theoretical specifications
- Allows context-specific implementations

**Implementation**:
```python
# Theory schema specifies algorithm
{
    "name": "meta_contrast_ratio",
    "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
    "parameters": {"x_i": "individual position", ...}
}

# LLM generates executable code
generated_tool = llm_generate_code(algorithm_spec)

# Runtime compilation and registration
compiled_tool = compile_and_register(generated_tool)
```

**Key Insight**: When the LLM makes implementation choices (e.g., cosine vs Euclidean distance), these become part of the documented trace with reasoning and uncertainty assessment.

### 2. Uncertainty is Localized, Not Global

**Decision**: Missing data in one stream only affects analyses that need that specific data.

**Rationale**: 
- 30% missing psychology scores shouldn't contaminate network analysis
- Each tool assesses uncertainty based on its specific needs
- Prevents cascade of unnecessary uncertainty

**Example**:
- Missing psychology → SEM modeling: 0.28 uncertainty
- Missing psychology → Community detection: 0.15 uncertainty (unaffected)
- Missing psychology → Text analysis: 0.22 uncertainty (unaffected)

**Implementation Principle**: Each tool assesses `data_coverage` for its specific needs, not global coverage.

### 3. Dempster-Shafer for Evidence Combination

**Decision**: Use D-S theory rather than Bayesian or simple averaging.

**Rationale**:
- Explicit representation of uncertainty ("I don't know")
- Handles conflicting evidence naturally
- LLM-friendly (easier to assign belief masses than likelihood ratios)
- Perfect for combining multiple assessments

**Critical Clarification**: We combine LLM **assessments** about data, not raw data:
```python
# CORRECT: Combining LLM assessments (independent given data)
assessment_1 = llm_assess("Based on linguistic patterns...")  # One perspective
assessment_2 = llm_assess("Based on temporal patterns...")     # Another perspective
combined = dempster_shafer_combine([assessment_1, assessment_2])

# ALSO CORRECT: Combining multiple instances
tweet_assessments = [llm_assess(tweet) for tweet in tweets]  # 50 assessments
user_belief = dempster_shafer_combine(tweet_assessments)     # Aggregated
```

**D-S works for both** because assessments are conditionally independent given the data.

### 4. Expert Reasoning Over Rigid Categories

**Decision**: Use flexible reasoning fields rather than predefined categories.

**Rationale**:
- Leverages LLM intelligence to identify relevant factors
- Avoids constraining analysis to predetermined frameworks
- Adapts to context-specific considerations

**Implementation**:
```python
class ToolUncertainty(BaseModel):
    score: float  # 0-1 uncertainty
    reasoning: str  # Complete reasoning including all relevant factors
    belief_masses: Optional[BeliefMass]  # For D-S when applicable
```

NOT:
```python
# Avoid overly structured schemas
class OverlyStructured:
    bias_factors: List[str]  # Too rigid
    validity_concerns: List[str]  # Prescriptive
    missing_data_impact: float  # Constraining
```

### 5. Comprehensive Provenance and Tracing

**Decision**: Every decision, assessment, and reasoning must be captured.

**Rationale**:
- Makes analysis reviewable by other researchers
- Enables debugging of generated tools
- Provides transparency for stakeholders
- Documents the "why" not just the "what"

**Implementation**:
```python
class ToolDecision(BaseModel):
    decision_type: str  # "algorithm_choice", "parameter_selection"
    implementation: str  # Detailed spec for code generation
    reasoning: str  # Complete reasoning
    uncertainty_impact: float  # How this affects uncertainty
```

## Tool Categories and Namespace Separation

### Persistent Infrastructure Tools (Pre-built)
**Namespace**: `PERSISTENT_*`
- **Data Loaders**: `PERSISTENT_T01_PDF`, `PERSISTENT_T05_CSV`, `PERSISTENT_T06_JSON`
- **Extraction**: `PERSISTENT_T23C_OntologyAwareExtractor`
- **Graph Operations**: `PERSISTENT_T31_EntityBuilder`, `PERSISTENT_T34_EdgeBuilder`

### Aggregation Tools (Pre-built)
**Namespace**: `AGG_*`
- **Tweet→User**: `AGG_TWEET_USER`
- **User→Community**: `AGG_USER_COMMUNITY`
- **Temporal Windows**: `AGG_TEMPORAL`
- **Cross-Modal**: `AGG_CROSS_MODAL`

### Dynamically Generated Tools (Created at runtime)
**Namespace**: `DYNAMIC_{theory}_{algorithm}_{timestamp}`
- **Theory-Specific Calculations**: `DYNAMIC_SCT_MCR_20240812_143022`
- **Theory Rules**: `DYNAMIC_SCT_PROTOTYPE_20240812_143105`
- **Theory Procedures**: `DYNAMIC_SCT_DEPERSONALIZATION_20240812_143201`
- **Any algorithm extracted from theory schemas**

This separation ensures:
- Clear identification of tool origin
- No collision between persistent and dynamic tools
- Complete provenance tracking
- Easy filtering by tool type

## Pure LLM Intelligence Approach for Uncertainty

### Core Principles
1. **Single Universal Schema**: One uncertainty format for all operations
2. **No Magic Numbers**: LLM intelligence determines uncertainty contextually
3. **Runtime Assessment**: Tools assess themselves during execution
4. **Natural Reduction**: Convergent evidence naturally reduces uncertainty
5. **Transparent Reasoning**: Every assessment includes complete justification

### What Uncertainty is NOT About
- **NOT about consistency across runs** - Running 10 times with same result doesn't reduce uncertainty
- **NOT about inter-LLM agreement** - Multiple LLMs agreeing doesn't reduce uncertainty
- **NOT about validation** - These are separate concerns
- **ONLY about the quality/completeness of THIS execution**

### Universal Uncertainty Schema
```python
class UniversalUncertainty(BaseModel):
    """Single uncertainty format for ALL operations"""
    uncertainty: float = Field(ge=0, le=1, description="0=certain, 1=uncertain")
    reasoning: str = Field(description="Expert reasoning for assessment")
    evidence_count: Optional[int] = Field(default=None, description="For aggregations")
    data_coverage: Optional[float] = Field(default=None, description="Fraction of needed data")
```

### Two Assessment Patterns

#### Pattern 1: Post-Execution Assessment (Most Tools)
```python
def assess_uncertainty(tool_output: Dict) -> UniversalUncertainty:
    """Assess based on tool's actual output and execution statistics"""
    
    prompt = f"""
    Assess uncertainty for this tool's output:
    
    {json.dumps(tool_output, indent=2)}
    
    Provide uncertainty (0-1) and reasoning.
    """
    
    return llm.structured_output(prompt, UniversalUncertainty)
```

#### Pattern 2: Self-Assessment in Generated Tools
```python
# Dynamically generated tools can assess their own uncertainty
class GeneratedTool(KGASTool):
    def execute(self, request):
        # Do calculation
        results, stats = self.calculate_with_stats(request.input_data)
        
        # Self-assess based on actual runtime results
        coverage = stats['processed'] / stats['total']
        uncertainty = self.assess_based_on_coverage(coverage)
        
        return ToolResult(
            data=results,
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=f"Processed {coverage:.0%} of required data",
                data_coverage=coverage
            )
        )
```

### Key Behavioral Patterns

#### Convergent Evidence Reduces Uncertainty
- Multiple tweets showing same pattern → lower uncertainty
- Cross-modal agreement → lower uncertainty  
- Multiple simulation runs with consistent results → lower uncertainty

#### Missing Data Localizes Impact
- Missing psychology scores → high uncertainty for MCR calculation
- Missing psychology scores → no impact on community detection
- Each tool assesses based on what IT needs

#### Special Cases
- **Lossless transformations**: Graph→Table format conversion has ~0.02 uncertainty
- **Dynamically generated tools**: Can self-assess based on runtime statistics
- **Aggregation points**: Include upstream uncertainties in context

### The 7 Conceptual Dimensions (Not Prescribed)
The LLM considers relevant factors from these dimensions as appropriate:
1. **Theory-Construct Alignment** - Does operationalization match theory?
2. **Measurement Validity** - Do measurements capture intended constructs?
3. **Data Completeness** - Quality and coverage for specific tool needs
4. **Entity Resolution** - Accuracy of entity identification
5. **Evidence Strength** - How diagnostic is the evidence?
6. **Evidence Integration** - Quality of combining sources (when using D-S)
7. **Inference Chain Validity** - Logical soundness of reasoning

## Optional IC-Inspired Reasoning Structures

While the LLM assesses uncertainty flexibly, we can optionally incorporate Intelligence Community analytical methods to improve reasoning quality:

### Analysis of Competing Hypotheses (ACH)
```python
# Optional structure for complex decisions
prompt_with_ach = """
Hypotheses:
H1: @johnsmith123 and uid_0471 are the same person
H2: They are different people who share a device
H3: They are different people with similar interests

Evidence:
E1: Email hashes match (supports H1, contradicts H2/H3)
E2: Posting times overlap (supports H1/H2, neutral H3)
E3: Writing style similar (supports H1, weak H2/H3)

Assess which hypothesis has LEAST evidence against it.
"""
```

### Key Assumptions Check
```python
# Optional structure for theory application
prompt_with_assumptions = """
Key Assumptions:
1. Network connections = meaningful relationships (validity: 0.7)
2. Community detection = psychological boundaries (validity: 0.6)
3. Online behavior = offline identity (validity: 0.5)

Assess cumulative uncertainty from assumption stack.
"""
```

## Aggregation Architecture

### Principle: Aggregation Reduces Uncertainty

When multiple pieces of evidence agree, uncertainty decreases:
- 23 tweets with ~0.22 uncertainty each
- Aggregated to user level: 0.12 uncertainty (45% reduction)
- Mechanism: Dempster-Shafer combination

### Aggregation Levels

1. **Tweet → User**: Combine multiple tweets to user belief
2. **User → Community**: Aggregate users to community characteristics
3. **Temporal Windows**: Combine time slices into trends
4. **Cross-Modal**: Synthesize graph, table, vector analyses

### When to Use Dempster-Shafer

**USE D-S for**:
- Aggregating multiple tweets into user belief
- Combining users into community characteristics
- Cross-modal synthesis (graph + table + vector)
- Any scenario with 3+ independent evidences

**DON'T USE D-S for**:
- Individual tool uncertainty (use simple score)
- Sequential tool chains (use propagation)
- Single evidence assessment

### Dempster-Shafer Formula (For Aggregation Only)

```python
def dempster_combine(evidences):
    """Only called when aggregating multiple evidences"""
    if len(evidences) < 3:
        # Just average for small sets
        return sum(e.uncertainty for e in evidences) / len(evidences)
    
    # Convert simple uncertainties to belief masses for D-S
    masses = []
    for e in evidences:
        # Simple heuristic: high uncertainty = high uncertain mass
        masses.append({
            "support": (1 - e.uncertainty) * 0.7,
            "reject": (1 - e.uncertainty) * 0.1,
            "uncertain": e.uncertainty + (1 - e.uncertainty) * 0.2
        })
    
    # Now apply D-S combination
    result = masses[0]
    for m in masses[1:]:
        K = result["support"] * m["reject"] + result["reject"] * m["support"]
        if K >= 0.99:
            return {"support": 0, "reject": 0, "uncertain": 1}
        
        factor = 1 / (1 - K)
        result = {
            "support": factor * (result["support"] * m["support"] + 
                                result["support"] * m["uncertain"] + 
                                result["uncertain"] * m["support"]),
            "reject": factor * (result["reject"] * m["reject"] + 
                            result["reject"] * m["uncertain"] + 
                            result["uncertain"] * m["reject"]),
            "uncertain": factor * result["uncertain"] * m["uncertain"]
        }
    
    # Convert back to simple uncertainty score
    return result["uncertain"] + 0.5 * result["reject"]
```

## D-S Computational Efficiency

**Key Insight**: D-S combination is computationally trivial - just multiplication and addition.

**Performance Reality**:
```python
def dempster_combine_sequential(evidences):
    """Sequential combination is O(n) and very fast"""
    result = evidences[0]
    for evidence in evidences[1:]:
        # Just 9 multiplications and additions per combination
        result = dempster_combine(result, evidence)
    return result
    
# 10,000 tweets = 9,999 combinations × 9 operations = ~90K arithmetic operations
# Modern CPU: ~milliseconds for 10,000 combinations
```

**Hierarchical for Parallelization** (not complexity reduction):
```python
def hierarchical_aggregate(evidences, chunk_size=100):
    # Parallel processing of chunks (for multi-core speedup)
    chunk_results = parallel_map(d_s_combine, chunks(evidences, chunk_size))
    
    # Final combination of chunk results
    final = d_s_combine_sequential(chunk_results)
    
    # Same O(n) complexity, but parallelizable
    return final
```

## Generated Code Debugging Strategy

**Philosophy**: Fail-fast during development with complete provenance capture.

**No Sandboxing By Design**: Research environment with trusted users - prioritize debugging over security.

**Implementation**:
```python
class GeneratedToolExecution:
    def execute_with_provenance(self, request, generation_context):
        """Execute with complete provenance capture"""
        execution_record = {
            "timestamp": datetime.now(),
            "tool_generation": {
                "theory_source": generation_context["theory"],
                "algorithm_spec": generation_context["algorithm"],  
                "generated_code": self.generated_code,
                "generation_prompt": generation_context["prompt"],
                "llm_model": generation_context["model"]
            },
            "execution": {
                "input_data": request.input_data,
                "input_shape": describe_shape(request.input_data),
                "parameters": request.parameters
            }
        }
        
        try:
            result = self.compiled_tool.execute(request)
            execution_record["output"] = result
            execution_record["status"] = "success"
        except Exception as e:
            execution_record["error"] = {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            execution_record["status"] = "failed"
            raise  # Fail fast - no recovery during development
        finally:
            # Always record to provenance
            provenance_service.record_execution(execution_record)
        
        return result
```

**Debugging Workflow**:
1. Execution fails → Check provenance record
2. Examine generated code, input data, error trace
3. Adjust generation prompt or input processing
4. Regenerate and retry
5. All attempts recorded for analysis

## Final Schema Design (Simplified and General)

### Core Schemas

```python
class BeliefMass(BaseModel):
    """Dempster-Shafer belief assignment"""
    support: float = Field(ge=0, le=1)
    reject: float = Field(ge=0, le=1)
    uncertain: float = Field(ge=0, le=1)

class ToolUncertainty(BaseModel):
    """Universal uncertainty from any tool"""
    score: float = Field(ge=0, le=1)
    reasoning: str  # Complete reasoning
    belief_masses: Optional[BeliefMass] = None

class ToolDecision(BaseModel):
    """Document any decision made"""
    decision_type: str
    implementation: str  # For code generation
    reasoning: str
    uncertainty_impact: float

class ToolResult(BaseModel):
    """Universal tool output"""
    data: Dict[str, Any]
    uncertainty: ToolUncertainty
    decisions: List[ToolDecision] = []
    provenance: Dict[str, Any]
```

### Aggregation Schemas

```python
class AggregationRequest(BaseModel):
    """Request to aggregate evidence"""
    evidence_items: List[Dict]
    aggregation_context: Dict
    method_hint: Optional[str] = None

class AggregationResult(BaseModel):
    """Result of aggregation"""
    aggregated_data: Dict
    aggregated_uncertainty: ToolUncertainty
    aggregation_reasoning: str
    conflict_analysis: Optional[str] = None
```

## Critical Design Principles

1. **Let LLM Intelligence Shine**: Don't prescribe categories; let LLM determine relevance
2. **Single Reasoning Field**: Comprehensive reasoning in one field, not fragmented
   - The `reasoning` field is THE KEY - it contains the expert judgment
   - More valuable than the numerical scores
   - Should be detailed enough for another expert to understand the logic
3. **Flexible Context**: Pass all context, let LLM extract what matters
4. **Document Decisions**: Implementation details + reasoning for every choice
5. **Minimal Structure**: Just enough for utility, not so much it constrains

## The Reasoning Field is Critical

Every uncertainty assessment MUST include comprehensive reasoning that:
- Explains what factors were considered
- Justifies the uncertainty score
- Documents assumptions made
- Notes what evidence would reduce uncertainty
- Provides enough detail for review and reproducibility

Example:
```python
reasoning = """
MCR calculation uncertainty of 0.18 based on:
- 90% user coverage (50 of 500 users missing position vectors)
- Position vectors derived from tweet embeddings (indirect measure)
- Cosine distance chosen as most aligned with Turner's relative positioning concept
- Clear group boundaries in data (modularity 0.72) increases confidence
- Missing users appear random (no systematic bias detected)
Would reduce uncertainty with: direct attitude measures, complete user coverage
"""
```

## What This System Actually Is

**An expert reasoning trace system** that:
- Makes computational social science transparent
- Documents all analytical decisions
- Captures uncertainty in structured form
- Provides reviewable audit trail
- Embeds expert judgment reproducibly

**NOT**:
- A calibrated measurement instrument
- A predictive model
- A causal inference system
- A claim to objective truth

## Key Insights and Clarifications

### On Theory Application and Temporal Mismatch
The system applies theories computationally but acknowledges theories may not perfectly fit modern contexts (e.g., 1986 face-to-face theory applied to 2021 Twitter). 

**This mismatch is explicitly part of uncertainty assessment**:
- Theory developed for face-to-face → applied to online: increases uncertainty
- Pre-social media theory → applied to Twitter: LLM reasons about applicability
- Different cultural context → uncertainty about generalization
- This is tracked in "Theory-Construct Alignment" dimension
- Makes limitations transparent rather than hidden

### On Bias and Missing Data
The LLM reasons about biases (selection, platform, temporal) as an expert would, incorporating these into uncertainty assessments rather than treating them as separate categories.

### On LLM as Both Generator and Assessor
**This is a deliberate design choice**, not a flaw:
- Human experts also implement their own methods and assess their confidence
- The LLM documents its implementation choices AND reasons about their implications
- Circular dependency concerns are misplaced - this mirrors actual research practice
- Alternative (separate assessor) would add complexity without value
- The key is transparency: both generation decisions and assessments are recorded

### On Validation
Validation is a separate post-processing task. The system focuses on transparent reasoning and uncertainty tracking, not on proving correctness.

### On Scale vs Quality
The system optimizes for quality and transparency over speed and cost. Hierarchical aggregation handles scale when needed.

## Implementation Priorities

1. **Dynamic tool generation** with algorithmic choice documentation
2. **D-S implementation** for both instance and perspective aggregation
3. **Prompts folder structure** for easy modification and review:
   ```
   /prompts/
   ├── tool_generation/
   │   ├── mathematical_tool.prompt
   │   ├── logical_rules.prompt
   │   └── procedural_tool.prompt
   ├── uncertainty_assessment/
   │   ├── data_completeness.prompt
   │   ├── belief_mass_assignment.prompt
   │   └── theory_alignment.prompt
   └── README.md  # Prompt engineering guidelines
   ```
4. **Complete provenance** tracking
5. **Fail-fast debugging** with comprehensive execution records

## Uncertainty Propagation Methods

### Sequential Propagation (Dependent Tools)
When Tool B depends on Tool A's output:
```python
def propagate_sequential(u_a, u_b):
    """Tools in sequence compound uncertainty"""
    # Simple multiplicative model
    combined_score = u_a + u_b * (1 - u_a)
    
    # D-S combination for belief masses
    combined_masses = dempster_combine(u_a.masses, u_b.masses)
    
    return combined_score, combined_masses
```

### Parallel Combination (Independent Analyses)
When multiple tools analyze same data independently:
```python
def combine_parallel(uncertainties):
    """Convergence reduces uncertainty if analyses agree"""
    
    # Calculate average conflict
    conflicts = []
    for i, u1 in enumerate(uncertainties):
        for u2 in uncertainties[i+1:]:
            K = u1.masses["support"] * u2.masses["reject"] + 
                u1.masses["reject"] * u2.masses["support"]
            conflicts.append(K)
    
    avg_conflict = np.mean(conflicts)
    
    if avg_conflict < 0.2:  # Low conflict - convergence
        # Uncertainty reduces by ~30% when modalities agree
        combined_score = min(uncertainties) * 0.7
    else:
        # High conflict increases uncertainty
        combined_score = max(uncertainties) * 1.2
    
    return combined_score
```

## Cross-Modal Convergence Example

When three modalities analyze the same phenomenon:
- **Graph analysis**: 0.15 uncertainty (complete network data)
- **Table analysis**: 0.28 uncertainty (30% missing psychology)
- **Vector analysis**: 0.15 uncertainty (complete text data)

**Without convergence**: Average = 0.19
**With convergence** (all show same pattern): 0.18 (reduced)
**With conflict** (different patterns): 0.35 (increased)

Key insight: Agreement across independent modalities validates findings.

## Example Execution Flow with Real Numbers

1. **Theory Extraction**: PDF → schema (0.15 uncertainty)
   - Clear formulas but some interpretation needed
   
2. **Tool Generation**: Schema → Python code
   - MCR distance choice documented (adds 0.05 uncertainty)
   
3. **Data Loading**: 
   - Tweets: 0.10 uncertainty (clean JSON)
   - Psychology: 0.08 uncertainty (30% missing but clean)
   
4. **Entity Extraction**: Theory-guided (0.22 uncertainty)
   - Stance detection from text inherently ambiguous
   
5. **Graph Analysis**: Community detection (0.15 uncertainty)
   - High modularity, clear communities
   - NOT affected by missing psychology
   
6. **MCR Calculation**: 0.18 uncertainty
   - 90% coverage (10% users no position vectors)
   - NOT 0.30+ despite missing psychology
   
7. **Aggregation**: Tweet→User via D-S
   - Input: 23 tweets at ~0.22 each
   - Output: 0.12 uncertainty (45% reduction)
   - Mechanism: Consistent evidence reduces uncertainty
   
8. **Cross-Modal Synthesis**: 
   - Graph (0.15) + Table (0.28) + Vector (0.15)
   - Convergent findings → 0.18 final uncertainty
   - Despite 30% missing psychology!

## Unresolved Questions and Future Work

### Resolved Through Discussion
- ✅ D-S works for both instance aggregation and perspective combination
- ✅ Uncertainty is localized, not global
- ✅ Reasoning should be unified, not fragmented into categories
- ✅ Generated code needs minimal but sufficient debugging support
- ✅ LLM determines relevant factors rather than using predefined categories

### Still Open
- Optimal chunk size for hierarchical D-S aggregation
- Best practices for LLM code generation prompts
- Handling adversarial or coordinated manipulation (out of scope for now)
- Integration with existing KGAS infrastructure

## Known Limitations and Mitigations

### 1. Algorithm Choice Ambiguity
**Issue**: "Similarity" in formulas could mean different metrics
**Mitigation**: LLM documents choice with reasoning, becomes part of trace

### 2. No Calibration
**Issue**: 0.30 uncertainty doesn't mean 70% accurate
**Mitigation**: This is by design - we provide reasoning not calibrated probabilities

### 3. Scale Challenges
**Issue**: D-S is O(n²) for conflict calculation
**Mitigation**: Hierarchical aggregation, sampling for very large datasets

### 4. Generated Code Debugging
**Issue**: No traditional debugging for LLM-generated code
**Mitigation**: Save all generated code, capture execution context, version with hash

### 5. Theory-Context Mismatch
**Issue**: 1986 face-to-face theory applied to 2021 Twitter
**Mitigation**: Theory applicability becomes part of uncertainty assessment

### 6. Missing Data Patterns
**Issue**: Missing data may not be random (privacy-conscious users)
**Mitigation**: LLM reasons about bias patterns in uncertainty assessment

## What This System Optimizes For

**Quality over Speed**: Careful reasoning over quick results
**Transparency over Precision**: Clear documentation over exact measurements
**Expert Reasoning over Automation**: LLM intelligence over rigid rules
**Reproducibility over Performance**: Complete traces over efficiency

## Why This Approach is Valid

Despite not being calibrated or validated in traditional ways, this system provides value because:

1. **Makes implicit expert judgments explicit**: What researchers do in their heads becomes documented
2. **Enables systematic application**: Theories can be applied consistently across datasets
3. **Provides reviewability**: Other researchers can examine and critique the reasoning
4. **Scales expert reasoning**: One expert's approach can be applied to massive datasets
5. **Maintains theoretical fidelity**: Direct implementation of theoretical constructs
6. **Acknowledges limitations**: Uncertainty and reasoning make limitations transparent

This is not solving the fundamental challenges of social science (formalizing the unformalizable) but rather making computational social science more transparent, systematic, and reviewable.

## Success Metrics

The system succeeds when:
1. Any formalized theory can be applied computationally
2. All analytical decisions are documented and reviewable
3. Uncertainty is transparent and justified
4. Evidence aggregation reduces uncertainty appropriately
5. Complete provenance enables reproducibility

## Final Note for Implementation

This system embeds human expert reasoning in computational analysis. The value is not in perfect measurement but in transparent, reproducible, and reviewable analytical processes. Every uncertainty score comes with reasoning, every decision with justification, and every result with complete provenance.

---

## Questions Requiring User Clarification

While the core design is complete, these questions may need user input:

1. **Chunk size for hierarchical D-S**: What's the optimal balance between performance and accuracy?
2. **LLM model selection**: Which frontier models to use for code generation vs uncertainty assessment?
3. **Sampling strategy**: When datasets are too large, how to sample representatively?
4. **Tool persistence**: Should generated tools be cached or regenerated each time?
5. **Prompting strategies**: Specific templates for code generation from formulas?

## Reference Files

- `full_example_ascii_dag_UPDATED.txt`: Complete DAG showing all analysis phases
- `theory_meta_schema_v13.json`: Universal template for theory extraction

**Document Status**: Complete design specification ready for implementation
**Last Updated**: 2025-08-12
**Next Steps**: Implement core schemas, D-S aggregation, and dynamic tool generation
**Key Innovation**: Embedding expert reasoning in computational social science through transparent uncertainty tracking