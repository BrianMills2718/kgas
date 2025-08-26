# Uncertainty System Reality Check - What Actually Exists

## Executive Summary

After deep investigation of `/experiments/uncertainty_stress_test_unified/`, the reality is:
- **Multiple competing approaches** were implemented but never unified
- **LLM-heavy implementation** that makes API calls for every uncertainty assessment
- **Significant biases** detected (sample size bias +18.6%, language complexity bias +8.0%)
- **75% ready** for external evaluation with critical issues remaining
- **Mock mode fallbacks** despite claims of "no mocks"

## What They Actually Built

### 1. **Core Services** (4 main components)

#### BayesianAggregationService (`bayesian_aggregation_service.py`)
```python
# What it does:
- Makes LLM calls to assess evidence quality (GPT-4)
- Calculates likelihood of evidence given hypothesis via LLM
- Performs Bayesian belief updates
- Generates analysis reports

# Reality:
- Every evidence assessment = 1-2 LLM API calls
- Falls back to default scores when API fails
- Cost: ~$0.10-0.50 per analysis
```

#### UncertaintyEngine (`uncertainty_engine.py`)
```python
# What it does:
- Extract claims from text using LLM
- Assess confidence with CERQual dimensions
- Update confidence with new evidence
- Cross-modal uncertainty translation

# Reality:
- 655 lines of code
- Makes 50-100 API calls per comprehensive test
- Has caching but only 15-20% hit rate
```

#### CERQualAssessor (`cerqual_assessor.py`)
```python
# What it does:
- Academic framework: Confidence in Evidence from Reviews
- 4 dimensions: Methodological, Relevance, Coherence, Adequacy
- LLM-powered assessment

# Reality:
- Takes 10-15 seconds for 3 studies
- Another LLM call for each assessment
```

#### LLMNativeUncertaintyEngine (`llm_native_uncertainty_engine.py`)
```python
# What it does:
- "Contextual intelligence" approach
- Single consolidated LLM analysis
- IC methodologies integration

# Reality:
- Alternative approach, not integrated with main system
- Competes with UncertaintyEngine rather than complementing
```

### 2. **Test Results Reality**

#### Ground Truth Validation
- **83.3% accuracy** (5/6 test cases)
- Failed on moderate evidence (underconfident by 10.7%)
- Works well on extremes (very strong or very weak evidence)

#### Critical Biases Found
```
Sample Size Bias: +18.6% for large N regardless of effect size
Language Complexity: +8.0% for technical jargon
Source Prestige: 0% (correctly ignored - one success!)
```

#### Performance Reality
```
Initial Confidence: <10ms (because it's just an LLM call)
Bayesian Update: ~100ms per evidence
CERQual Assessment: 10-15s for 3 studies
Total API Calls: 50-100 per comprehensive test
Processing Speed: 3-5 texts per minute
```

### 3. **What "Mock Mode" Really Means**

Despite claims of "no mocks", the SocialMaze test shows:
```
Mode: Mock Mode (no API)
Duration: 0.0 seconds
```

They have fallback defaults everywhere:
```python
def _default_quality_scores(self):
    return {
        "factual_accuracy": 0.6,
        "source_credibility": 0.6,
        # ... hardcoded defaults
    }
```

## The Real Architecture

```
Text Input
    ↓
LLM Call #1: Extract Claims
    ↓
LLM Call #2: Assess Claim Confidence
    ↓
For Each Evidence:
    LLM Call #3: Assess Evidence Quality
    LLM Call #4: Calculate Likelihood
    ↓
Math: Bayesian Update (finally, no LLM!)
    ↓
LLM Call #5: Cross-modal Translation
    ↓
Output: Confidence Score with 50+ API calls worth of "intelligence"
```

## What's Missing vs Claims

### ADR-029 Claims vs Reality

| ADR-029 Promise | Reality |
|-----------------|---------|
| "Single integrated LLM analysis" | Multiple fragmented calls per operation |
| "Mathematical propagation" | Yes, but wrapped in LLM calls |
| "IC methodologies" | Implemented but not integrated |
| "Sustainable tracking" | 50-100 API calls per analysis |
| "Root-sum-squares propagation" | Exists but rarely used |

### Integration Reality

They built:
- Standalone test suite
- Never integrated with main KGAS
- No connection to `/src/core/confidence_scoring/`
- Separate from production systems

## The Actual Approach That Works

From their own validation report:
1. **LLM extracts and assesses** everything
2. **Bayesian math** for actual propagation (the only non-LLM part)
3. **CERQual framework** for structure
4. **Significant biases** remain unfixed

## Practical Recommendations

### 1. **Stop the LLM Madness**
```python
# Instead of:
confidence = await llm_assess_confidence(text, claim)  # API call

# Use:
confidence = calculate_confidence_from_features(
    text_features, 
    claim_features,
    mathematical_model  # No LLM!
)
```

### 2. **Fix the Biases**
```python
# Current problem:
sample_adequacy = min(1.0, total_n / 1000)  # Linear with N

# Fix:
sample_adequacy = calculate_statistical_power(n, effect_size)
```

### 3. **Use What Actually Works**
- Bayesian update math (keep this)
- CERQual structure (keep this)
- Drop the 50+ LLM calls per assessment
- Use `/src/core/confidence_scoring/` instead

## The Bottom Line

They built an **LLM-powered uncertainty system** that:
- Makes expensive API calls for everything
- Has significant unfixed biases
- Never integrated with production
- Competes with itself (multiple engines)
- Falls back to hardcoded defaults

**What we should actually use:**
1. The mathematical propagation formulas (root-sum-squares)
2. The CERQual framework structure
3. The Bayesian update logic
4. **NOT the LLM-everything approach**

## For Our Type-Based Framework

```python
class PracticalUncertaintyContext:
    """What we should actually implement"""
    
    def __init__(self):
        # Use existing mathematical infrastructure
        from src.core.confidence_scoring.combination_methods import BayesianCombiner
        self.combiner = BayesianCombiner()
        
    def propagate(self, confidences):
        # Pure math, no LLM
        return self.combiner.combine(confidences)
    
    def assess_initial(self, features):
        # Feature-based, not LLM-based
        return self.calculate_from_features(features)
```

The lesson: **They overcomplicated it**. The math works. The framework structure works. The "make LLM do everything" approach doesn't.