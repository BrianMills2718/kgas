# Tool-Specific Uncertainty Assessment Examples

Working through the actual DAG to find weak spots in pure LLM approach.

## 1. T302_THEORY_EXTRACTION

**What it does**: Extracts SCT theory from Turner 1986 paper

**Tool-specific prompt**:
```python
context = {
    "type": "theory_extraction",
    "source_paper": "Turner & Oakes 1986",
    "extraction_results": {
        "core_formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
        "key_concepts": ["self-categories", "prototypes", "depersonalization"],
        "missing_details": ["normative fit calculation specifics"],
        "interpretation_choices": ["Used cosine for 'similarity' in formula"]
    }
}

prompt = """
As an expert in theory formalization, assess uncertainty for this theory extraction.

Context: {context}

Consider:
- Are the core formulas clearly specified in the paper?
- What implementation details had to be interpreted?
- Are key concepts well-defined or ambiguous?

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.15,
    reasoning="Core MCR formula is explicit in paper. Main uncertainty from normative fit details being sparse and choosing cosine distance for similarity measure. Key concepts well-defined."
)
```

**WEAK SPOT**: None identified - straightforward assessment

---

## 2. T05_CSV_LOAD (Psychology Data)

**What it does**: Loads user psychology scores, 30% missing

**Tool-specific prompt**:
```python
context = {
    "type": "csv_load",
    "file": "user_psychology.csv",
    "total_rows": 2506,
    "valid_rows": 1754,
    "missing_rows": 752,
    "missing_pattern": "random (no systematic bias detected)",
    "columns_found": ["uid", "CB_score", "identity_strength", "posted_at"],
    "data_quality": "Clean where present, consistent formatting"
}

prompt = """
As a data quality expert, assess uncertainty for this CSV data load.

Context: {context}

Consider:
- Quality of the data that IS present
- Pattern of missingness (random vs systematic)
- Completeness for the specific columns

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.08,
    reasoning="CSV structure is clean, 70% complete data with random missingness. Low uncertainty for loading process itself, though downstream tools using psychology will need to handle gaps.",
    data_coverage=0.70
)
```

**WEAK SPOT**: None - tool just loads data, uncertainty is about the loading process

---

## 3. T301_SCHEMA_MAPPER

**What it does**: Maps discovered schemas to theory requirements

**Tool-specific prompt**:
```python
context = {
    "type": "schema_mapping",
    "mappings_attempted": 47,
    "mappings_successful": 44,
    "ambiguous_mappings": [
        {"theory_needs": "user_identity", "found": ["uid", "author", "user_id"], "choice": "fuzzy match all"},
        {"theory_needs": "group_membership", "found": ["community_id", "cluster"], "choice": "use both"},
        {"theory_needs": "timestamp", "found": ["posted_at", "created_time"], "choice": "parse both formats"}
    ]
}

prompt = """
As a data integration expert, assess uncertainty for this schema mapping.

Context: {context}

Consider:
- How many mappings required interpretation choices?
- Are the ambiguous cases likely to cause issues?
- Quality of the mapping decisions made

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.18,
    reasoning="3 of 47 mappings ambiguous, but reasonable choices made. Identity field mapping could cause join issues. Timestamp parsing adds complexity but both formats are standard."
)
```

**WEAK SPOT #1**: The LLM needs to understand that identity mapping ambiguity is MORE critical than timestamp ambiguity. Will it weight these correctly?

---

## 4. T51_META_CONTRAST_CALCULATOR

**What it does**: Core SCT formula - THE key theoretical measure

**Tool-specific prompt**:
```python
context = {
    "type": "mcr_calculation",
    "formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
    "coverage": {
        "users_with_position_vectors": 1754,
        "users_total": 2506,
        "percentage": 0.70
    },
    "implementation_choices": {
        "distance_metric": "cosine (paper said 'similarity')",
        "position_derivation": "text embeddings (no direct attitude measure)",
        "group_definition": "from community detection algorithm"
    },
    "results": {
        "prototype_users_identified": 3,
        "mcr_scores_range": [0.45, 0.94],
        "score_distribution": "bimodal"
    }
}

prompt = """
As an expert in Self-Categorization Theory, assess uncertainty for this MCR calculation.

Context: {context}

Consider:
- MCR is THE core measure for identifying prototypes in SCT
- Coverage of users with necessary data
- Validity of using text embeddings as position vectors
- Appropriateness of distance metric choice

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.30,
    reasoning="MCR is critical for SCT but only calculable for 70% of users. Text embeddings are indirect proxy for psychological position. Cosine distance reasonable for high-dimensional vectors but not specified by theory. Bimodal distribution suggests calculation is capturing real structure.",
    data_coverage=0.70
)
```

**WEAK SPOT #2**: Will the LLM recognize that this is THE critical measure and weight uncertainty appropriately? The prompt says "THE core measure" but will that be enough?

---

## 5. T52_TEMPORAL_ANALYZER (Aggregation Example)

**What it does**: Tracks changes over time, finds 237 I→We transitions

**Tool-specific prompt**:
```python
context = {
    "type": "temporal_pattern_analysis",
    "patterns_found": {
        "pronoun_shifts": {"I_to_we": 237, "we_to_I": 12},
        "salience_events": 14,
        "language_convergence": "detected in 67% of high-identity users"
    },
    "time_windows_analyzed": ["daily", "weekly", "monthly"],
    "consistency_across_windows": "High - patterns visible at all scales",
    "data_gaps": "15% of days missing for some users, interpolated"
}

prompt = """
As a temporal analysis expert, assess uncertainty for these temporal patterns.

Context: {context}

Consider:
- Number of instances of each pattern
- Consistency across different time scales  
- Impact of interpolated gaps
- Strength of the signal (237 vs 12 shows clear direction)

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.22,
    reasoning="237 I→we transitions vs only 12 reverse shows strong directional pattern. Consistency across all time scales increases confidence. 15% gaps are concerning but interpolation reasonable for < 7 day gaps.",
    evidence_count=237
)
```

**WEAK SPOT #3**: This is aggregation of temporal evidence. Will LLM recognize that 237 instances of the SAME pattern should reduce uncertainty? Not guaranteed.

---

## 6. CROSS_MODAL_ANALYZER (Convergence Example)

**What it does**: Synthesizes graph, table, vector findings

**Tool-specific prompt**:
```python
context = {
    "type": "cross_modal_synthesis",
    "modality_findings": {
        "graph": {
            "finding": "3 distinct communities with high modularity (0.72)",
            "confidence": "high",
            "based_on": "complete network data"
        },
        "table": {
            "finding": "Identity→Rejection pathway confirmed (r=0.72)",
            "confidence": "moderate", 
            "based_on": "70% psychology coverage"
        },
        "vector": {
            "finding": "Language convergence within groups, divergence between",
            "confidence": "high",
            "based_on": "complete text data"
        }
    },
    "convergence_assessment": "All three modalities support group polarization hypothesis",
    "contradictions": "None - findings align despite different data sources"
}

prompt = """
As a cross-modal analysis expert, assess uncertainty for this synthesis.

Context: {context}

Consider:
- Agreement vs contradiction between modalities
- Whether findings truly converge or are independent
- Strength of each modality's evidence
- What convergence means for overall confidence

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.18,
    reasoning="Strong convergence across all three modalities increases confidence. Graph and vector have complete data with high confidence. Table has moderate confidence but finding aligns perfectly. No contradictions found.",
    evidence_count=3
)
```

**WEAK SPOT #4**: Critical that LLM recognizes convergence should reduce uncertainty below the average. Will it?

---

## 7. T60_LLM_CONSISTENCY_CHECKER (Multi-LLM Agreement)

**What it does**: Runs extraction with multiple LLMs, checks agreement

**Tool-specific prompt**:
```python
context = {
    "type": "multi_llm_validation",
    "llm_results": {
        "GPT-4": {"entities": 2834, "relationships": 4521},
        "Claude": {"entities": 2791, "relationships": 4492},
        "Gemini": {"entities": 2812, "relationships": 4507}
    },
    "agreement_metrics": {
        "cohen_kappa": 0.73,
        "overlap_percentage": 0.89,
        "divergent_cases": 127
    },
    "resolution": "majority vote for divergent cases"
}

prompt = """
As an LLM validation expert, assess uncertainty for this multi-model consensus.

Context: {context}

Consider:
- Level of agreement between models (κ=0.73 is substantial)
- Number and nature of divergent cases
- Whether models might share biases
- Value of multiple independent assessments

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.15,
    reasoning="High agreement (κ=0.73) across three frontier models increases confidence. 89% overlap is strong. 127 divergent cases out of ~2800 is acceptable. Models have different training but might share some biases.",
    evidence_count=3
)
```

**WEAK SPOT #5**: Will LLM recognize that inter-rater reliability of 0.73 is actually quite good?

---

## 8. SIMULATION_EXECUTION_TOOL (Complex Propagation)

**What it does**: Runs intervention scenarios 100 times each

**Tool-specific prompt**:
```python
context = {
    "type": "simulation_results",
    "parameter_quality": "30% agents use imputed psychology",
    "scenarios_tested": 3,
    "runs_per_scenario": 100,
    "results": {
        "trusted_messenger": {
            "mean_effect": -0.24,
            "std_dev": 0.08,
            "direction_consistency": "100% of runs showed reduction"
        },
        "identity_affirmation": {
            "mean_effect": -0.31,
            "std_dev": 0.12,
            "direction_consistency": "100% of runs showed reduction"
        },
        "direct_confrontation": {
            "mean_effect": +0.12,
            "std_dev": 0.05,
            "direction_consistency": "100% of runs showed increase"
        }
    }
}

prompt = """
As a simulation analysis expert, assess uncertainty for these intervention results.

Context: {context}

Consider:
- Impact of imputed parameters on reliability
- Consistency of direction across all runs
- Magnitude of standard deviations relative to effects
- What 100 runs tells us despite parameter uncertainty

Provide uncertainty (0-1) and reasoning.
"""
```

**Expected output**:
```python
UniversalUncertainty(
    uncertainty=0.28,
    reasoning="Despite 30% imputed parameters, all 300 runs show consistent direction of effects. Standard deviations are relatively small compared to effect sizes. Parameter uncertainty affects magnitude precision but not direction.",
    evidence_count=300
)
```

**WEAK SPOT #6**: This requires sophisticated reasoning - imputation increases uncertainty but consistent patterns reduce it. Will LLM balance these correctly?

---

## Key Weak Spots Identified

1. **Identity Mapping Criticality** (T301): Will LLM weight identity ambiguity as more critical than timestamp ambiguity?

2. **Theory-Critical Measures** (T51_MCR): Will LLM recognize MCR is THE core measure and assign appropriate weight?

3. **Temporal Pattern Aggregation** (T52): Will LLM understand 237 instances of same pattern reduces uncertainty?

4. **Convergence Recognition** (Cross-Modal): Will LLM reduce uncertainty below average when modalities converge?

5. **Statistical Interpretation** (T60): Will LLM know κ=0.73 is "substantial" agreement?

6. **Complex Balancing** (Simulation): Will LLM balance parameter uncertainty against pattern consistency?

## Common Thread

The weak spots all require **domain knowledge or statistical understanding**:
- What makes identity mapping critical
- What κ=0.73 means
- How convergence differs from independence
- Theory-specific importance (MCR for SCT)

## Solution: Richer Context in Prompts

Instead of hoping LLM figures it out, be explicit:
```python
# Bad:
"Consider the mappings"

# Good:
"Consider: Identity mapping is critical for joining data - ambiguity here cascades"

# Bad:
"Agreement between models"

# Good:
"Agreement (κ=0.73 is considered 'substantial' agreement in statistics)"
```

This keeps the pure LLM approach but provides the context needed for appropriate assessment.