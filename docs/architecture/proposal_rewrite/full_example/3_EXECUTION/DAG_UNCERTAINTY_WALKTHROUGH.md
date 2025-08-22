# Working Through Uncertainty with the Current DAG

## Overview
Using the Self-Categorization Theory COVID discourse DAG to work through how uncertainty assessment and propagation would work at each step.

## Phase 1: Theory Extraction

### Tool: T302_THEORY_EXTRACTION
**Input**: Turner 1986 paper (PDF)
**Output**: theory_schema.json with entities, relations, algorithms

**Uncertainty Assessment by LLM**:
```
Considering:
- Source: Foundational SCT paper, highly cited
- Extraction: Clear mathematical formulas present
- Completeness: All core constructs identified

Uncertainty: 0.15
Justification: "High confidence - foundational text with explicit formulas. Minor uncertainty from interpretation of procedural elements."
Belief masses: {support: 0.85, reject: 0.05, uncertain: 0.10}
```

## Phase 2: Multi-Document Ingestion

### Tool: T01_PDF_LOAD
**Input**: COVID tweets dataset (PDF export)
**Output**: Raw text data

**Uncertainty Assessment**:
```
Considering:
- PDF quality: Clean export, no OCR needed
- Completeness: File fully loaded
- Format issues: Some Unicode errors in 2% of tweets

Uncertainty: 0.10
Justification: "Clean digital PDF, minor Unicode issues"
Belief masses: {support: 0.88, reject: 0.02, uncertain: 0.10}
```

### Tool: T05_CSV_LOAD  
**Input**: User psychology profiles (CSV)
**Output**: Structured user data

**Uncertainty Assessment**:
```
Considering:
- Data completeness: 30% users missing CB_score
- Format: Clean CSV, no parsing errors
- Coverage: Only 751/2506 users have full profiles

Uncertainty: 0.35
Justification: "Significant missing data (30%), but existing data is clean"
Belief masses: {support: 0.60, reject: 0.25, uncertain: 0.15}
```

### Tool: T300_SCHEMA_DISCOVERER
**Input**: All loaded data sources
**Output**: discovered_schemas.json

**Uncertainty Assessment**:
```
Considering:
- Schema clarity: Standard Twitter structure identified
- Field detection: All expected fields found
- Type inference: Confident in 95% of types

Uncertainty: 0.12
Justification: "Clear schema structure, minor ambiguity in nested JSON fields"
Belief masses: {support: 0.86, reject: 0.04, uncertain: 0.10}
```

### Tool: T301_SCHEMA_MAPPER
**Input**: discovered_schemas + theory_schema
**Output**: mapping_rules.json

**Uncertainty Assessment**:
```
Considering:
- Mapping clarity: "user_id" → "individual" is direct
- Conceptual alignment: "tweet.text" → "position" requires interpretation
- Coverage: Can map 80% of theory requirements

Uncertainty: 0.28
Justification: "Direct mappings clear, but position vectors from text require interpretation"
Belief masses: {support: 0.68, reject: 0.17, uncertain: 0.15}
```

### Tool: T302_MULTI_DOC_FUSION
**Input**: All data with mapping rules
**Output**: unified_graph

**Uncertainty Assessment**:
```
Considering:
- Entity resolution: 92% confident matches
- Temporal alignment: Successfully aligned 95% of timestamps
- Missing data handling: Imputed 15% of connections

Uncertainty: 0.22
Justification: "High confidence in matched entities, some uncertainty from imputation"
Belief masses: {support: 0.75, reject: 0.10, uncertain: 0.15}
```

## Phase 3: Theory-Guided Extraction

### Tool: T23C_ONTOLOGY_AWARE_EXTRACTOR
**Input**: unified_graph + theory_schema
**Output**: theory-aligned entities

**Uncertainty Assessment**:
```
Considering:
- Ontology match: "we vaccine hesitant" clearly maps to self-category
- Ambiguous cases: 15% of tweets have unclear group signals
- Context: COVID domain well-covered by ontology

Uncertainty: 0.25
Justification: "Strong ontology coverage, but stance detection from text inherently ambiguous"
Belief masses: {support: 0.70, reject: 0.15, uncertain: 0.15}
```

## Phase 4: Graph Construction

### Tool: T31_ENTITY_BUILDER
**Input**: theory-aligned entities
**Output**: graph nodes

**Uncertainty Assessment**:
```
Considering:
- Node creation: Straightforward from entities
- Attribute assignment: Direct mapping
- No ambiguity in this transformation

Uncertainty: 0.05
Justification: "Direct transformation with no interpretation needed"
Belief masses: {support: 0.93, reject: 0.02, uncertain: 0.05}
```

### Tool: T34_EDGE_BUILDER
**Input**: nodes + relationships
**Output**: graph with edges

**Uncertainty Assessment**:
```
Considering:
- Explicit edges: FOLLOWS, MENTIONS are clear
- Inferred edges: IDENTIFIES_WITH based on language similarity
- Edge weights: Calculated from interaction frequency

Uncertainty: 0.18
Justification: "Explicit relationships clear, inferred group identification has moderate uncertainty"
Belief masses: {support: 0.78, reject: 0.07, uncertain: 0.15}
```

### Tool: T50_COMMUNITY_DETECT
**Input**: graph
**Output**: 3 communities identified

**Uncertainty Assessment**:
```
Considering:
- Algorithm: Louvain method is deterministic for this graph
- Modularity score: 0.72 indicates clear communities
- Stability: Same communities across multiple runs

Uncertainty: 0.15
Justification: "High modularity score, stable communities detected"
Belief masses: {support: 0.82, reject: 0.03, uncertain: 0.15}
```

### Tool: T51_META_CONTRAST_CALCULATOR (Dynamically Generated!)
**Input**: communities + user positions
**Output**: MCR scores per user

**Uncertainty Assessment**:
```
Considering:
- Formula implementation: Direct from theory
- Position vectors: 70% users have complete data
- Distance calculations: Euclidean distance appropriate
- Missing data: MCR undefined for 30% users

Uncertainty: 0.30
Justification: "Correct formula implementation but significant missing position data"
Belief masses: {support: 0.65, reject: 0.20, uncertain: 0.15}
```

## Phase 4.5: Temporal Dynamics

### Tool: T52_TEMPORAL_ANALYZER
**Input**: graph + timestamps
**Output**: temporal_trajectories.json

**Uncertainty Assessment**:
```
Considering:
- Time coverage: 85% of days have data
- Pronoun detection: 90% confidence in I→We shifts
- Trend detection: Clear patterns visible
- Gaps: 15% temporal gaps interpolated

Uncertainty: 0.20
Justification: "Strong temporal patterns detected, some gaps filled with interpolation"
Belief masses: {support: 0.75, reject: 0.10, uncertain: 0.15}
```

## Phase 5: Cross-Modal Transfer (Graph → Table)

### Tool: GRAPH_TABLE_EXPORTER
**Input**: graph communities
**Output**: tabular format

**Uncertainty Assessment**:
```
Considering:
- Format conversion: Lossless transformation
- Schema preservation: All attributes maintained
- No interpretation needed

Uncertainty: 0.02
Justification: "Direct format conversion with no information loss"
Belief masses: {support: 0.96, reject: 0.01, uncertain: 0.03}
```

## Phase 6: Table Analysis

### Tool: STATISTICAL_ANALYSIS_TOOL
**Input**: community table + psychology scores
**Output**: statistics by community

**Uncertainty Assessment**:
```
Considering:
- Sample size: Community A n=512, adequate
- Missing data: 30% missing CB_scores
- Statistical power: Sufficient for mean differences
- Assumptions: Normality approximately met

Uncertainty: 0.25
Justification: "Adequate sample sizes but missing data affects confidence"
Belief masses: {support: 0.70, reject: 0.15, uncertain: 0.15}
```

### Tool: SEM_MODELING_TOOL
**Input**: psychological and behavioral data
**Output**: Model fit CFI=0.94

**Uncertainty Assessment**:
```
Considering:
- Model fit: CFI=0.94 indicates good fit
- Sample size: Adequate for SEM (n=1755 complete cases)
- Missing data: Handled with FIML
- Assumptions: Multivariate normality reasonable

Uncertainty: 0.22
Justification: "Good model fit, appropriate handling of missing data"
Belief masses: {support: 0.73, reject: 0.12, uncertain: 0.15}
```

## Phase 8: Vector Analysis

### Tool: T15B_VECTOR_EMBEDDER
**Input**: tweet texts
**Output**: embedding vectors

**Uncertainty Assessment**:
```
Considering:
- Embedding model: Sentence-BERT well-validated
- Text quality: 98% tweets have sufficient length
- Domain relevance: Model trained on similar social media

Uncertainty: 0.12
Justification: "Well-validated embedding model appropriate for domain"
Belief masses: {support: 0.85, reject: 0.03, uncertain: 0.12}
```

### Tool: SEMANTIC_DISTANCE_CALC
**Input**: embeddings
**Output**: distance metrics between groups

**Uncertainty Assessment**:
```
Considering:
- Distance metric: Cosine similarity standard for embeddings
- Sample sizes: Sufficient for both groups
- Temporal stability: Patterns consistent over time

Uncertainty: 0.15
Justification: "Standard approach with adequate data"
Belief masses: {support: 0.80, reject: 0.05, uncertain: 0.15}
```

## Phase 9: Cross-Modal Synthesis

### Tool: CROSS_MODAL_ANALYZER
**Input**: graph + table + vector results
**Output**: integrated findings

**Uncertainty Assessment**:
```
Considering:
- Convergence: All three modalities show similar patterns
- Graph: Communities clearly separated (modularity=0.72)
- Table: Psychology differences significant (p<0.001)
- Vector: Language divergence clear (d=0.84)
- Integration: Consistent story across modalities

Uncertainty: 0.18
Justification: "Strong convergent evidence across modalities reduces uncertainty"
Belief masses: {support: 0.78, reject: 0.07, uncertain: 0.15}
```

## Aggregation Example: Tweet → User Level

### TWEET_USER_AGGREGATOR (Missing from DAG but needed!)

**Input**: 23 tweets from user_042 with uncertainties
**Process**: Dempster-Shafer combination

```python
# Tweet-level uncertainties for user_042
tweet_evidences = [
    {"support": 0.70, "reject": 0.15, "uncertain": 0.15},  # tweet 1
    {"support": 0.65, "reject": 0.20, "uncertain": 0.15},  # tweet 2
    {"support": 0.75, "reject": 0.10, "uncertain": 0.15},  # tweet 3
    # ... 20 more tweets
]

# Dempster-Shafer combination
combined = tweet_evidences[0]
for evidence in tweet_evidences[1:]:
    K = combined["support"] * evidence["reject"] + combined["reject"] * evidence["support"]
    if K < 1:
        factor = 1 / (1 - K)
        combined = {
            "support": factor * (combined["support"] * evidence["support"] + 
                                combined["support"] * evidence["uncertain"] +
                                combined["uncertain"] * evidence["support"]),
            "reject": factor * (combined["reject"] * evidence["reject"] +
                              combined["reject"] * evidence["uncertain"] +
                              combined["uncertain"] * evidence["reject"]),
            "uncertain": factor * combined["uncertain"] * evidence["uncertain"]
        }

# After combining 23 tweets
final_user_belief = {
    "support": 0.82,  # Increased from individual tweets
    "reject": 0.08,   # Decreased due to consistency
    "uncertain": 0.10  # Reduced through aggregation
}

Uncertainty: 0.15  # Reduced from 0.25 average of tweets
Justification: "23 consistent tweets provide strong aggregate evidence"
```

## Uncertainty Propagation Through Dependencies

### Sequential Propagation (Dependent Tools)

When Tool B depends on Tool A's output:
```python
def propagate_sequential(uncertainty_a, uncertainty_b):
    """Tools in sequence compound uncertainty"""
    # Simple multiplicative model for demonstration
    combined_score = uncertainty_a + uncertainty_b * (1 - uncertainty_a)
    
    # Dempster-Shafer for belief masses
    K = (uncertainty_a["support"] * uncertainty_b["reject"] + 
         uncertainty_a["reject"] * uncertainty_b["support"])
    
    if K >= 1:
        # Complete conflict - use maximum uncertainty
        return {"score": 1.0, "masses": {"support": 0, "reject": 0, "uncertain": 1}}
    
    factor = 1 / (1 - K)
    combined_masses = {
        "support": factor * (uncertainty_a["support"] * uncertainty_b["support"] + 
                            uncertainty_a["support"] * uncertainty_b["uncertain"] +
                            uncertainty_b["support"] * uncertainty_a["uncertain"]),
        "reject": factor * (uncertainty_a["reject"] * uncertainty_b["reject"] +
                          uncertainty_a["reject"] * uncertainty_b["uncertain"] +
                          uncertainty_b["reject"] * uncertainty_a["uncertain"]),
        "uncertain": factor * uncertainty_a["uncertain"] * uncertainty_b["uncertain"]
    }
    
    return {"score": combined_score, "masses": combined_masses}
```

### Parallel Combination (Independent Analyses)

When multiple tools analyze same data independently:
```python
def combine_parallel(uncertainties):
    """Independent analyses can reduce uncertainty if they agree"""
    
    # If all agree (low conflict), uncertainty reduces
    # If they disagree (high conflict), uncertainty increases
    
    conflicts = []
    for i, u1 in enumerate(uncertainties):
        for u2 in uncertainties[i+1:]:
            K = u1["support"] * u2["reject"] + u1["reject"] * u2["support"]
            conflicts.append(K)
    
    avg_conflict = np.mean(conflicts)
    
    if avg_conflict < 0.2:  # Low conflict - analyses agree
        # Uncertainty reduces
        combined = dempster_shafer_combine_all(uncertainties)
        combined["score"] *= (1 - 0.3)  # 30% reduction for agreement
    else:  # High conflict
        combined["score"] = min(1.0, avg_conflict + 0.2)
    
    return combined
```

## Final Uncertainty Calculation

### Tracing Through Entire DAG

```python
# Starting uncertainties
u_theory = 0.15
u_data_load = 0.10  # PDF
u_psych_load = 0.35  # CSV with missing data
u_schema_discovery = 0.12
u_schema_mapping = 0.28
u_fusion = 0.22
u_extraction = 0.25
u_graph_build = 0.11  # Combined T31 + T34
u_community = 0.15
u_mcr = 0.30
u_temporal = 0.20
u_stats = 0.25
u_sem = 0.22
u_vectors = 0.12
u_distance = 0.15

# Sequential dependencies
u_after_loading = propagate_sequential(u_data_load, u_psych_load)  # ~0.42
u_after_schema = propagate_sequential(u_after_loading, u_schema_mapping)  # ~0.58
u_after_fusion = propagate_sequential(u_after_schema, u_fusion)  # ~0.67
u_after_extraction = propagate_sequential(u_after_fusion, u_extraction)  # ~0.75

# Parallel analyses (graph, table, vector) - can reduce if they agree
u_graph_path = propagate_sequential(u_after_extraction, u_mcr)  # ~0.83
u_table_path = propagate_sequential(u_after_extraction, u_stats)  # ~0.81
u_vector_path = propagate_sequential(u_after_extraction, u_vectors)  # ~0.78

# Cross-modal synthesis - reduces due to convergence
u_synthesis = combine_parallel([u_graph_path, u_table_path, u_vector_path])
# If modalities agree: ~0.65 (reduced from ~0.80 average)
# If modalities conflict: ~0.90

# Final with theory validation
u_final = propagate_sequential(u_synthesis, u_theory_validation)
```

**Final Result**: 
- **With convergent evidence**: ~0.68 uncertainty
- **With conflicting evidence**: ~0.92 uncertainty
- **Critical contributors**: Missing psychology data (0.35), schema mapping (0.28), MCR calculation (0.30)

## Key Insights from Walkthrough

1. **Aggregation Reduces Uncertainty**: Multiple tweets from same user → stronger confidence
2. **Convergence Reduces Uncertainty**: When graph/table/vector agree → higher confidence  
3. **Missing Data Dominates**: 30% missing psychology scores affects everything downstream
4. **Early Uncertainty Compounds**: Schema mapping uncertainty (0.28) affects all analyses
5. **Cross-Modal Validation Works**: Independent modalities agreeing increases confidence

## What This Shows We Need

1. **Aggregation Tools**: Critical for reducing uncertainty through evidence combination
2. **Conflict Detection**: Need to identify when evidence disagrees
3. **Sensitivity Analysis**: Which uncertainties matter most?
4. **Improvement Recommendations**: Where to focus data collection
5. **Contextual Assessment**: LLM considers domain knowledge, not just statistics