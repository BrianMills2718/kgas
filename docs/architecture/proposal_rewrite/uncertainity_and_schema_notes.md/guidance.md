# Uncertainty Framework Guidance for KGAS

## Core Principles

### 1. Social Science Research Focus
- We are NOT trying to determine objective truth or ground truth
- We study perceptions, beliefs, and social constructs
- "Source credibility" is itself a construct to be measured (with uncertainty about our measurement), not a source of uncertainty about truth

### 2. No Hardcoded Rules or Thresholds
- NO rules like "if uncertainty > 0.7 then do X"
- All decisions should be contextual and reasoned by the LLM
- Single DAG generation (not multiple for high uncertainty)

### 3. Simple Uncertainty Scoring
- Single 0-1 uncertainty score per operation
- English justification required for each score
- LLM uses theory schema context to assess uncertainty
- Not breaking down into subcategories (entity recognition, construct validity, etc.)

### 4. Full Graph Extraction
- Extract entities + relations + properties in ONE LLM call
- Based on theory schema specification
- Not separate extraction steps for entities, then relations, etc.

### 5. Out of Scope
- **Calibration**: Not attempting to calibrate confidence scores
- **Consistency**: Not requiring consistent uncertainty assessments across runs
- **Adaptive execution**: Not changing approach based on uncertainty (yet)
- **Ground truth validation**: We're studying social phenomena, not facts

## Revised Uncertainty Dimensions for Social Science

### What ARE Valid Sources of Uncertainty

1. **Measurement Uncertainty**
   - How well did we measure the construct?
   - Example: "How confident are we that this language indicates in-group identity?"
   - This is about our measurement quality, not about "truth"

2. **Theoretical Ambiguity**
   - How clearly does the theory specify what to look for?
   - Example: "SCT mentions 'depersonalization' but doesn't specify linguistic markers"
   - Theory gaps that require interpretation

3. **Temporal Stability**
   - Has the measured construct likely changed since measurement?
   - Example: "These tweets are from 2020; group identity may have shifted by 2025"
   - Not about "truth decay" but construct stability

4. **Extraction Completeness**
   - Did we capture all relevant information from the source?
   - Example: "PDF parsing might have missed images containing important context"
   - Technical limitations in data extraction

5. **Construct Operationalization**
   - How well does our operational definition match the theoretical construct?
   - Example: "We measure 'influence' via retweets, but influence is multifaceted"
   - Gap between what we measure and what theory describes

6. **Statistical Uncertainty**
   - Standard statistical measures (confidence intervals, p-values, power)
   - Example: "Sample size of 100 gives wide confidence intervals"
   - Can use real statistical packages where appropriate

7. **Linguistic Ambiguity**
   - Ambiguity in the natural language request or data
   - Example: "Analyze extremism" - which definition of extremism?
   - Multiple valid interpretations

### What are NOT Sources of Uncertainty (for our purposes)

1. **Source Credibility** (as truth indicator)
   - We don't care if a bot said something false
   - We care that a bot said it (and how others perceived it)

2. **Cross-Source Agreement**
   - Multiple sources agreeing/disagreeing is just evidence to analyze
   - Not uncertainty about truth

3. **Factual Accuracy**
   - Someone saying "vaccines cause autism" isn't uncertainty
   - It's data about their expressed belief

## How Uncertainty Should Be Assessed

### During Theory-Guided Extraction
```python
# Simple, flexible approach
prompt = f"""
Given this theory schema: {theory_schema}
And this text: {text}

Extract a graph of entities, relations, and properties as specified by the theory.

Then assess your uncertainty (0-1) about this extraction and explain why.
Consider:
- How clearly the theory maps to the text
- Ambiguities in interpretation
- Missing context that would help
"""

# Returns:
# - Extracted graph
# - Uncertainty score (single number)
# - Justification (English explanation)
```

### During Statistical Analysis
```python
# LLM acts as statistician
prompt = f"""
We have {n} samples from a population.
We're measuring {construct} with variance {var}.
We want to test {hypothesis}.

What is the statistical uncertainty here?
Consider sample size, effect size, statistical power.
You may suggest using specific statistical tests.
"""

# Can invoke actual statistical packages based on LLM recommendation
```

### During Cross-Modal Synthesis
```python
# Simple integration assessment
prompt = f"""
Graph analysis shows: {graph_findings}
Statistical analysis shows: {table_findings}
Text analysis shows: {vector_findings}

Assess uncertainty (0-1) in synthesizing these findings.
Explain what makes integration more/less certain.
"""
```

## What We're NOT Doing

1. **Multiple DAGs**: One DAG per request, even if uncertain
2. **Threshold-based decisions**: No "if uncertainty > X then Y"
3. **Calibration**: Not trying to make 0.8 confidence = 80% correct
4. **Consistency enforcement**: Each assessment is independent
5. **Truth-seeking**: We study social phenomena, not objective facts
6. **Adaptive execution**: Not changing approach based on uncertainty (yet)

## Role of IC Methods

The IC methods (ACH, Key Assumptions Check) are:
- Analytical frameworks the LLM can use to structure reasoning
- NOT hardcoded procedures
- Optional tools for complex analyses
- Ways to make reasoning more systematic

Example:
```python
# LLM might choose to use ACH structure
prompt = f"""
If helpful, you may use Analysis of Competing Hypotheses:
- List possible explanations
- Evaluate evidence against each
- Identify which has least contradicting evidence

But only if this structure helps clarify the analysis.
"""
```

## Key Insight: Uncertainty as Transparency

Uncertainty scores are primarily for:
1. **Transparency**: Showing where interpretation was difficult
2. **Documentation**: Recording what required judgment calls
3. **Provenance**: Understanding how confident we are in each step

NOT for:
1. **Decision-making**: Not using thresholds to change behavior
2. **Validation**: Not trying to achieve "correct" uncertainty
3. **Optimization**: Not trying to minimize uncertainty

## Summary

The uncertainty framework should:
- Support social science research (studying perceptions, not truth)
- Use simple, contextual LLM assessment (not complex subcategories)
- Provide transparency about interpretation challenges
- Avoid hardcoded rules and thresholds
- Focus on measurement quality, not factual accuracy