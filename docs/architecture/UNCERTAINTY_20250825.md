# KGAS Uncertainty System - Simplified Understanding
**Date**: 2025-08-26  
**Status**: Core principles and implementation approach finalized with physics-style error propagation

## Executive Summary

The KGAS uncertainty system enables transparent computational social science by having each tool assess its own operational uncertainty based on local context. These local assessments are then mathematically combined for pipeline-level uncertainty using physics-style error propagation. The system explicitly embraces subjective expert assessment as a feature, not a bug.

## Core Principles (Non-Negotiable)

### 1. Subjective Expert Assessment is Intentional
- **Uncertainty scores ARE meaningful** - they represent the LLM's subjective expert assessment
- **0.30 means what the prompt defines** - typically "moderate confidence" 
- **Subjectivity mirrors human experts** - Social scientists routinely make subjective confidence assessments
- **NOT a calibrated measurement** - Not claiming 0.30 means 70% accurate in objective terms
- **Transparency over precision** - Reasoning explains the score, making subjectivity reviewable

### 2. Dynamic Tool Generation from Theory Schemas
- **Tools generated at runtime** from theory papers, not pre-built
- **Theory schemas � LLM generates Python code** � Runtime compilation
- **Maintains fidelity** to theoretical specifications
- **Implementation choices documented** - When LLM chooses (e.g., cosine vs Euclidean distance), it's recorded with reasoning

### 3. Localized Uncertainty, Not Global
- **Missing data affects only relevant tools** - 30% missing psychology scores � high uncertainty for psychology-dependent tools
- **Independent analyses unaffected** - Community detection works fine without psychology scores
- **Each tool assesses based on ITS needs** - Not global data coverage
- **Prevents cascade** of unnecessary uncertainty propagation

### 4. System Identity: Expert Reasoning Trace System
**What this IS**:
- An expert reasoning trace system
- Makes computational social science transparent
- Documents all analytical decisions
- Embeds expert judgment reproducibly

**What this is NOT**:
- A calibrated measurement instrument
- A predictive model
- A causal inference system
- A claim to objective truth

## The Correct Uncertainty Model

### Every Transformation is a Construct Mapping

The fundamental principle: **Every tool operation is a semantic transformation from one construct to another**, and uncertainty measures how well that mapping preserves/transforms the intended meaning.

#### Construct Mapping Examples

- **PDF → Text**: "visual document" → "character sequence"
- **Text → Entities**: "character sequence" → "semantic units"
- **Entities → Graph**: "semantic units" → "relationship network"
- **Clustering**: "relationship network" → "group boundaries"
- **Tweets → User Belief**: "individual expressions" → "aggregate stance"

### Unified Uncertainty Assessment

Each tool makes **ONE assessment** that captures both:
1. **Operational uncertainty**: "Did I execute the transformation correctly?"
2. **Construct validity**: "Does my output validly represent the target construct?"

#### Example Pipeline with Semantic Awareness

**Tool A** (PDF → Text):
```
Transformation: visual_document → character_sequence
Assessment: "Given OCR challenges on scanned pages, uncertainty 0.2 
            that my text accurately represents the document content"
```

**Tool B** (Text → Entities):
```
Transformation: character_sequence → semantic_units
Assessment: "Given pronoun ambiguity, uncertainty 0.25
            that my entities correctly capture the semantic units"
```

**Tool C** (Entities → Graph):
```
Transformation: semantic_units → relationship_network
Assessment: "Given clear relationships, uncertainty 0.15
            that my graph validly represents the social network"
```

**Tool D** (Clustering on Graph):
```
Transformation: relationship_network → group_boundaries
Assessment: "Given modularity of 0.8, uncertainty 0.25
            that clusters represent true in-groups/out-groups"
Note: Zero operational uncertainty (deterministic), but construct validity uncertainty remains
```

### Why This Unified Model Works

1. **Semantic Awareness**: LLM understands the intended construct mapping
2. **Complete Assessment**: One number captures both execution and validity
3. **Handles Deterministic Tools**: They have zero operational uncertainty but still assess construct validity
4. **Local Expertise**: Each tool assesses its specific transformation

## No Hardcoded Numbers

**Critical principle**: There are NO hardcoded numbers in this system.

### What This Means

L **WRONG**: 
- "Reduce uncertainty by 45% when aggregating"
- "Set uncertainty to 0.8 for conflicts"
- "If minimum confidence < 0.3, it dominates"

 **RIGHT**:
- Each LLM assessment is contextual
- The LLM seeing convergent evidence decides how much uncertainty reduces
- The LLM seeing conflict decides how much uncertainty increases
- Every numerical decision comes from intelligent assessment, not rules

### Example: Aggregating Tweets

When combining 50 tweets into user belief:
1. Each tweet gets assessed independently: "uncertainty 0.22 - ambiguous stance"
2. The aggregator looks at all 50 and makes ONE assessment: "uncertainty 0.12 - consistent pattern emerges"
3. The aggregator's assessment IS the combined uncertainty - no formula needed

The LLM doing aggregation can see patterns humans would see and assess accordingly.

## Physics-Style Error Propagation Model

### The Key Insight
This follows the physics error propagation model where each measurement assumes perfect instruments and only accounts for its measurement uncertainty:

**Physics analogy**:
- Measure length: 10.0 ± 0.2 cm (assumes ruler is perfect)
- Measure width: 5.0 ± 0.1 cm (assumes ruler is perfect)
- Combine using error propagation formulas

**Our pipeline model**:
- Tool A: "Given this input, I'm 0.2 uncertain about MY extraction" (assumes input is perfect)
- Tool B: "Given this text, I'm 0.1 uncertain about MY entities" (assumes text is perfect)
- Combine mathematically

### Why This Works
Tool B's assessment naturally captures the actual quality of Tool A's output without knowing A's uncertainty:
- If A produced gibberish (despite only 0.2 uncertainty), B would see the gibberish and assess HIGH uncertainty
- If A produced clean text (despite 0.2 uncertainty), B would assess LOW uncertainty
- B doesn't need to know WHY A was uncertain - B's assessment reflects what it actually receives

## Mathematical Propagation (After Local Assessments)

Mathematical combination happens AFTER all tools make their local assessments:

### 1. Sequential Pipeline Combination (Recommended)
When tools run in sequence (A → B → C), use **probability combination**:
```python
# Each tool is a filter that could introduce errors
confidence = (1 - u_a) * (1 - u_b) * (1 - u_c)
total_uncertainty = 1 - confidence

# Example: [0.2, 0.1, 0.15] → 1 - (0.8 * 0.9 * 0.85) = 0.388
```

This matches intuition: more steps = more chances for error

**When to use alternatives**:
- **Addition**: Only if errors are systematic in same direction (rare)
- **Quadrature**: √(a² + b²) if errors are truly random/independent

### 2. Aggregation Assessment
When combining multiple items (e.g., 50 tweets → user belief):
- The aggregation tool makes ONE assessment of its output
- "Given these 50 tweets, my user belief assessment has 0.12 uncertainty"
- This single assessment IS the aggregated uncertainty
- No mathematical formula needed - the LLM sees the pattern

**Note**: The aggregator assesses "how uncertain am I that these 50 tweets correctly map to this user construct?" - a single unified assessment.

### 3. Merging Parallel Analyses
When multiple analyses merge (e.g., three modalities analyzed same phenomenon):
- The merging tool assesses its synthesis uncertainty
- "Given these three analyses, my synthesis has 0.18 uncertainty"
- The tool naturally accounts for convergence/conflict in its assessment
- No separate convergence detection needed

### 4. Dempster-Shafer (Special Cases Only)
Use D-S ONLY when you have multiple **independent** assessments of the **same thing**:
- Multiple independent judges assessing same entity
- Different tools making independent assessments of identical output
- NOT for normal pipeline operations

## Where Uncertainty Decreases (Aggregation)

### The Primary Mechanism: Evidence Aggregation
Uncertainty decreases when a tool sees multiple pieces of evidence that agree:
- **Multiple measurements of same construct**: 50 tweets → user belief (0.22 → 0.12)
- **Multiple sources confirming information**: Name from text + metadata + header → canonical name
- **Pattern recognition in noisy data**: Noisy text → clear entities
- **Convergent analyses**: Multiple analysis methods reaching same conclusion

### Key Principle
**Uncertainty decreases when a tool recognizes evidence of correctness** - this happens primarily at aggregation points where multiple inputs are combined to assess a single construct.

### Aggregation Tool Guidance
Aggregation tools should assess uncertainty considering:
```python
"""
Assess uncertainty considering:
- Consistency: Do inputs agree? (high agreement → lower uncertainty)
- Independence: Are inputs independent? (more independent → more reduction)
- Coverage: How many inputs? (more inputs → more confidence, with diminishing returns)
- Pattern strength: How clear is the pattern? (clearer → lower uncertainty)
"""
```

### Important Clarification
**Cross-modal is NOT special**: Whether evidence comes from different analysis modes (graph, text, vector) or the same mode is irrelevant. What matters is:
- Are the evidences independent?
- Do they agree?
- Are there enough of them?

The mode doesn't determine independence - the data generation process does.

## Universal Uncertainty Schema

```python
class UniversalUncertainty(BaseModel):
    """Single uncertainty format for ALL operations"""
    uncertainty: float  # 0=certain, 1=uncertain
    reasoning: str  # Expert reasoning for assessment (CRITICAL)
    evidence_count: Optional[int]  # For aggregations
    data_coverage: Optional[float]  # Fraction of needed data
```

### The Reasoning Field is Critical

Every uncertainty assessment MUST include comprehensive reasoning that:
- Explains what factors were considered
- Justifies the uncertainty score
- Documents assumptions made
- Notes what evidence would reduce uncertainty
- Provides enough detail for review and reproducibility

Example reasoning:
```
"MCR calculation uncertainty of 0.18 based on:
- Successfully processed 450 of 500 users (90% coverage)
- Position vectors computed from clear textual indicators
- Used cosine distance as most appropriate for relative positioning
- Clear group boundaries evident in data (modularity 0.72)
- Missing users appear randomly distributed
Would reduce uncertainty with: complete user coverage, direct attitude measures"
```

## When to Use What

### Use Local LLM Assessment For:
- Individual tool uncertainty
- Assessing data quality within a tool's domain
- Determining aggregation uncertainty
- Detecting convergence/conflict
- Any context-specific judgment

### Use Mathematical Combination For:
- Final pipeline uncertainty
- Combining sequential tool uncertainties
- Dempster-Shafer for multiple independent assessments
- Computing confidence from uncertainty

### Never Use:
- Hardcoded uncertainty values
- Fixed reduction/amplification rates
- Rule-based uncertainty propagation
- Global uncertainty that affects all tools equally

## Practical Implementation

### Tool Implementation Pattern

```python
class SomeTool(ExtensibleTool):
    def get_capabilities(self):
        return ToolCapabilities(
            input_construct="source_construct",  # What the input represents
            output_construct="target_construct",  # What the output should represent
            transformation_type="method_name"     # How we transform
        )
    
    def process(self, input_data, context):
        # Do the actual work (could be LLM or deterministic)
        result = self._execute(input_data)
        
        # Assess uncertainty of construct mapping
        uncertainty_assessment = self._assess_transformation_uncertainty(
            input_data, 
            result,
            self.get_capabilities()
        )
        
        return ToolResult(
            data=result,
            uncertainty=uncertainty_assessment.uncertainty,
            reasoning=uncertainty_assessment.reasoning
        )
    
    def _assess_transformation_uncertainty(self, input_data, output_data, capabilities):
        prompt = f"""
        Transformation: {capabilities.input_construct} → {capabilities.output_construct}
        Method: {capabilities.transformation_type}
        
        Input characteristics: {self._describe(input_data)}
        Output characteristics: {self._describe(output_data)}
        
        Assess uncertainty (0-1) that the output validly represents 
        the intended {capabilities.output_construct} given the input {capabilities.input_construct}.
        
        Consider both:
        - Operational success (did the transformation work correctly?)
        - Construct validity (does the output mean what we intend?)
        
        For deterministic algorithms, operational uncertainty is 0, 
        but construct validity uncertainty remains.
        """
        return llm.assess(prompt)
```

### Pipeline Orchestration Pattern

```python
def run_pipeline(input_data):
    # Each tool assesses its own uncertainty
    result_a = tool_a.process(input_data)  # uncertainty: 0.2
    result_b = tool_b.process(result_a.data)  # uncertainty: 0.25
    result_c = tool_c.process(result_b.data)  # uncertainty: 0.15
    
    # Mathematical combination for pipeline uncertainty
    pipeline_uncertainty = combine_sequential([
        result_a.uncertainty,
        result_b.uncertainty,
        result_c.uncertainty
    ])
    
    return PipelineResult(
        final_data=result_c.data,
        total_uncertainty=pipeline_uncertainty,
        step_uncertainties=[0.2, 0.25, 0.15],
        reasoning=combine_reasoning([
            result_a.reasoning,
            result_b.reasoning,
            result_c.reasoning
        ])
    )
```

## Key Insights

### 1. Construct Mapping is Universal
Every tool operation is a semantic transformation between constructs, and uncertainty measures the fidelity of that mapping.

### 2. One Number is Sufficient
A single uncertainty value captures both operational success and construct validity because the LLM understands the semantic intent.

### 3. Deterministic Tools Have Uncertainty Too
Algorithms with zero operational uncertainty still have construct validity uncertainty (e.g., do these clusters represent in-groups?).

### 4. Context Stays Local
Tool B doesn't need Tool A's uncertainty - B assesses the quality of its own construct mapping based on what it receives.

### 5. Mathematical Combination is Simple
Once each tool provides its local assessment, combining them is straightforward mathematics using physics-style error propagation.

### 6. Aggregation Enables Reduction
When tools combine multiple measurements of the same construct, uncertainty can decrease through evidence aggregation.

## Common Misconceptions to Avoid

L **"Tool B should know Tool A's uncertainty"**
- No, Tool B assesses its own operation only

L **"We need rules for how much uncertainty reduces with convergence"**
- No, the LLM assessing convergence decides contextually

L **"Missing data should increase uncertainty globally"**
- No, only tools that need that specific data are affected

L **"We need complex propagation formulas"**
- No, simple mathematical combination after local assessment

L **"Uncertainty compounds through the pipeline"**
- Not automatically - each tool makes fresh assessment of its own operation

## Remaining Clarifications Needed

### 1. **DAG Composition with Reconvergence**
**Question**: How do we handle complex DAGs where paths split and reconverge?
```
     A (0.2)
    /        \
   B (0.1)   C (0.15)
    \        /
     D (0.1)
```

**Current thinking**: 
- Option 1: Track dependencies and avoid double-counting (complex)
- Option 2: Let D's assessment naturally account for correlation (simpler)
- Option 3: Always use probability combination and accept conservative estimates

**Open issue**: In flexible type-based composition, we may not know the DAG structure ahead of time

### 2. **Handling Extreme Uncertainties**
**Question**: What happens when a tool reports very high uncertainty (e.g., 0.95)?
- Should the pipeline continue or halt?
- Should there be automatic fallback to alternative methods?
- How do we prevent propagating garbage through expensive operations?

**Current thinking**: Continue but flag for review, let downstream tools naturally assess high uncertainty

### 3. **Uncertainty Thresholds for Decision Making**
**Question**: When do we act on uncertainty values?
- At what point is uncertainty "too high" to trust results?
- Should different domains have different acceptable thresholds?
- How do users interpret and use uncertainty scores?

**Current thinking**: Present uncertainty transparently, let researchers judge based on their domain

### 4. **Handling Tool Failures vs High Uncertainty**
**Question**: How do we distinguish between:
- Tool failure (error, exception) → No output
- Tool success with high uncertainty → Output with uncertainty 0.9+

**Current thinking**: Failures stop pipeline, high uncertainty continues but is tracked

### 5. **Ensemble Assessment for Critical Operations**
**Question**: For critical assessments, should we:
- Run assessment multiple times and average?
- Use multiple LLM models and combine?
- Accept single assessment variability?

**Current thinking**: Single assessment for speed, ensemble for critical paths (user choice)

### 6. **Granularity of Reasoning**
**Question**: How detailed should reasoning be?
- Full reasoning for every operation (verbose but complete)
- Summary reasoning with details on demand (efficient but may lose context)
- Hierarchical reasoning (overview + drill-down capability)

**Current thinking**: Full reasoning stored, summary presented, details queryable

### 7. **Temporal Consistency**
**Question**: Running the same pipeline twice might give different uncertainties due to LLM variability
- Is this acceptable?
- Should we cache assessments for identical inputs?
- How do we handle reproducibility requirements?

**Current thinking**: Accept variability as inherent, document timestamp with assessments

### 8. **Cross-Pipeline Uncertainty Comparison**
**Question**: Can we compare uncertainties across different pipelines?
- Is 0.3 uncertainty in pipeline A comparable to 0.3 in pipeline B?
- Should uncertainty be normalized per pipeline type?

**Current thinking**: Uncertainties are pipeline-specific, not globally comparable

### 9. **Recognizing Aggregation Points in Flexible Pipelines**
**Question**: In type-based tool composition, how do we identify aggregation points?
- The pipeline is composed dynamically based on types
- We don't know ahead of time where aggregations will occur
- How does a tool know it's doing aggregation vs transformation?

**Current thinking**: Tools that combine multiple inputs of the same type are likely aggregators. They can self-identify based on their operation (e.g., "I'm combining 50 items into 1")

## Implementation Status

### What's Clear
✅ Every tool operation is a construct-to-construct mapping  
✅ One uncertainty number captures both operational and construct validity  
✅ Physics-style error propagation for sequential pipelines  
✅ Probability combination (1 - ∏(1-u)) for sequential tools  
✅ Single unified assessment for aggregations  
✅ No hardcoded numbers or rules  
✅ Comprehensive reasoning required  
✅ Aggregation is primary mechanism for uncertainty reduction  
✅ Cross-modal is not special - just evidence aggregation  
✅ Uncertainty embedded in tool output, not separate LLM call  
✅ Deterministic tools assess construct validity, not operational uncertainty  

### What Needs Testing
🔄 Performance impact of LLM assessments at scale  
🔄 Consistency of assessments across multiple runs  
🔄 User interpretation and utility of uncertainty scores  
🔄 Edge cases with very high/low uncertainties  

### What's Deferred
📋 Calibration mechanisms (intentionally not part of MVP)  
📋 Uncertainty visualization and reporting tools  
📋 Domain-specific uncertainty guidelines  
📋 Automated uncertainty-based decision making  

## Conclusion

The KGAS uncertainty system is elegantly simple:
1. Each tool assesses its own operational uncertainty based on local expertise
2. These assessments are subjective expert judgments (by design)
3. Mathematical combination uses physics-style error propagation
4. No hardcoded numbers or rules
5. Comprehensive reasoning makes everything reviewable

This approach leverages LLM intelligence for contextual assessment while keeping the system modular, scalable, and transparent. The remaining questions are primarily about operational policies rather than fundamental design, allowing the system to evolve based on real usage patterns.