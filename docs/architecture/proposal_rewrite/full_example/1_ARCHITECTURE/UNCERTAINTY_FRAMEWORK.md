# Unified Uncertainty Framework for KGAS

## Core Philosophy

- **No calibration attempts** - We don't try to ensure "80% confident" means right 80% of the time
- **Transparency over precision** - Better to acknowledge uncertainty than hide it  
- **LLM contextual assessment** - No hardcoded rules, LLM assesses based on context
- **Localized uncertainty** - Missing data in one stream doesn't contaminate unrelated analyses
- **Simple 0-1 scores with justification** - Each assessment includes score and explanation

## 7 Core Uncertainty Dimensions

### 1. Theory-Construct Alignment
**What it measures**: Does our operationalization match what the theory specifies?
**Example**: Theory says "identify cohesive identity groups" but we use network clustering (which finds topology, not psychology)
**Assessment**: LLM evaluates whether the computational method captures theoretical intent

### 2. Measurement Validity
**What it measures**: Do our measurements actually capture the intended constructs?
**Example**: Do retweet networks actually represent "influence" or just entertainment value?
**Assessment**: LLM evaluates the gap between what we measure and what we claim to measure

### 3. Data Completeness
**What it measures**: Quality and coverage of input data FOR THIS SPECIFIC TOOL
**Key Insight**: 30% missing psychology scores only affects SEM modeling, NOT community detection
**Includes**:
- Sampling bias (are tweets representative?)
- Temporal relevance (how stale is the data?)
- Extraction completeness (did we get all text from PDFs?)
- Statistical power (enough data for conclusions?)
**Assessment**: LLM evaluates data limitations FOR THE SPECIFIC ANALYSIS

### 4. Entity Resolution
**What it measures**: Accuracy of identifying and linking entities
**Includes**:
- Entity recognition (is "Apple" the company or fruit?)
- Identity resolution (are @jsmith and @johnsmith123 the same person?)
- Mention linking (connecting references across documents)
**Assessment**: LLM evaluates evidence for entity decisions

### 5. Evidence Strength
**What it measures**: How diagnostic is each piece of evidence?
**Example**: "We don't trust vaccines" strongly indicates group identity; "Vaccines are discussed" is weak evidence
**Assessment**: LLM evaluates how well evidence discriminates between hypotheses

### 6. Evidence Integration
**What it measures**: Quality of combining multiple evidence sources
**Method**: Dempster-Shafer for batch evidence processing
**Example**: Combining language patterns + network structure + temporal behavior to assess group identity
**Assessment**: LLM assigns belief masses to {support, reject, uncertain}

### 7. Inference Chain Validity
**What it measures**: Logical soundness of reasoning from evidence to conclusions
**Example**: "High MCR → prototype → influences group → drives vaccine hesitancy" - are all links valid?
**Assessment**: LLM evaluates each inferential step

## Evidence Integration Using Dempster-Shafer

### Why Dempster-Shafer (not Bayesian)
- **Explicit uncertainty**: Can assign belief to "I don't know"
- **Batch processing**: Natural for combining multiple evidence types at once
- **Conflicting evidence**: Handles disagreement between sources well
- **LLM-friendly**: Easier to estimate belief masses than likelihood ratios

### How It Works
The LLM examines evidence and assigns belief masses based on what it observes:
- **Support**: How much evidence supports the hypothesis
- **Reject**: How much evidence contradicts the hypothesis
- **Uncertain**: How much is ambiguous or unknown

These must sum to 1.0 and are based purely on LLM's interpretation of the evidence.

### Dempster-Shafer Combination Formula
```python
def dempster_combine(m1, m2):
    """Combine two belief mass assignments"""
    # Calculate conflict
    K = m1["support"] * m2["reject"] + m1["reject"] * m2["support"]
    
    if K >= 1:  # Complete conflict
        return {"support": 0, "reject": 0, "uncertain": 1}
    
    # Normalization factor
    factor = 1 / (1 - K)
    
    # Combine beliefs
    combined = {
        "support": factor * (m1["support"] * m2["support"] + 
                            m1["support"] * m2["uncertain"] + 
                            m1["uncertain"] * m2["support"]),
        "reject": factor * (m1["reject"] * m2["reject"] + 
                          m1["reject"] * m2["uncertain"] + 
                          m1["uncertain"] * m2["reject"]),
        "uncertain": factor * m1["uncertain"] * m2["uncertain"]
    }
    
    return combined
```

## Uncertainty Propagation Principles

### 1. Localized Effects
Missing data only affects tools that need that specific data:
- Missing psychology scores → affects SEM modeling (0.28 uncertainty)
- Missing psychology scores → does NOT affect community detection (0.15 uncertainty)
- Missing psychology scores → does NOT affect text analysis (0.22 uncertainty)

### 2. Sequential Propagation (Dependent Tools)
When Tool B depends on Tool A's output:
```python
def propagate_sequential(u_a, u_b):
    """Tools in sequence compound uncertainty"""
    combined_score = u_a + u_b * (1 - u_a)
    # Also combine belief masses using Dempster-Shafer
    return combined_score
```

### 3. Parallel Combination (Independent Analyses)
When multiple tools analyze same data independently:
- If they agree → uncertainty reduces (convergence validation)
- If they conflict → uncertainty increases (divergent evidence)

### 4. Aggregation Reduces Uncertainty
Multiple instances providing consistent evidence:
- 23 tweets with ~0.22 uncertainty each
- Aggregated to user level: 0.12 uncertainty (45% reduction)
- Mechanism: Dempster-Shafer combination of consistent evidence

## Optional IC-Inspired Reasoning Structures

While the LLM assesses uncertainty flexibly, we can optionally incorporate Intelligence Community methods:

### Analysis of Competing Hypotheses (ACH)
```python
prompt_with_ach = """
Hypotheses:
H1: @johnsmith123 and uid_0471 are the same person
H2: They are different people who share a device
H3: They are different people with similar interests

Evidence:
E1: Email hashes match perfectly (supports H1, contradicts H2/H3)
E2: Posting times overlap 60% (supports H1/H2, neutral H3)
E3: Writing style similarity 0.72 (supports H1, weak support H2/H3)

Assess which hypothesis has LEAST evidence against it.
"""
```

### Key Assumptions Check
```python
prompt_with_assumptions = """
Key Assumptions:
1. Network connections indicate meaningful relationships
   - Validity: 0.7 (could be entertainment following)
2. Community detection captures psychological boundaries
   - Validity: 0.6 (algorithm vs psychology gap)
3. Online behavior reflects offline identity
   - Validity: 0.5 (performative vs authentic)

Assess cumulative uncertainty from assumption stack.
"""
```

## Types of Truth We Assess

1. **Construct Assessment**: "Does this text indicate in-group identity?"
   - Truth about social perceptions, not objective reality

2. **Identity Resolution**: "Are @johnsmith and @jsmith123 the same person?"
   - Factual truth, but often unknowable with certainty

3. **Measurement Fidelity**: "Did we extract what theory specifies?"
   - Truth about operationalization matching intent

4. **Perceptual Truth**: "Does this user perceive vaccines as dangerous?"
   - Truth about expressed beliefs, not factual claims

## Key Implementation Principles

1. **Each tool outputs uncertainty**: Every ToolResult includes ToolUncertainty
2. **Context-aware assessment**: LLM considers specific tool needs, not global state
3. **Selective propagation**: Uncertainty only flows to dependent downstream tools
4. **Aggregation opportunity**: Multiple consistent evidences reduce uncertainty
5. **Convergence validation**: Agreement across modalities reduces uncertainty
6. **Transparency required**: Always include justification with scores

## Critical Insights from Practice

1. **Missing data has localized impact**: 30% missing psychology doesn't affect graph analysis
2. **Aggregation is powerful**: 23 tweets → 45% uncertainty reduction at user level
3. **Convergence validates**: Three modalities agreeing → confidence increases
4. **Early uncertainty matters most**: Schema mapping uncertainty affects everything downstream
5. **Dynamic tools assess contextually**: Generated MCR tool knows its coverage and adjusts

## Final System Properties

With this framework, the system achieves:
- **Overall uncertainty ~0.18** despite 30% missing data
- **Localized impacts** preventing contamination
- **Transparent reasoning** with justifications
- **Adaptive assessment** based on context
- **Convergent validation** across modalities