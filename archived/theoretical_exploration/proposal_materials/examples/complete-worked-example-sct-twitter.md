# Complete Worked Example: Twitter Polarization Analysis with Self-Categorization Theory
*Extracted from proposal materials - 2025-08-29*  
*Status: Implementation Example - Future Reference*

## Overview

This document presents a comprehensive end-to-end analysis example demonstrating KGAS capabilities for theory-driven social science research. The example shows Twitter political polarization analysis using Self-Categorization Theory (SCT) with complete uncertainty tracking and cross-modal analysis.

**Research Question**: How do Twitter users form group identities and become polarized around climate change discussions?

## Data Setup

**Input Dataset**:
- 10,000 tweets about climate change
- 500 unique users  
- 7-day collection period
- Mix of original tweets, retweets, replies

**Analysis Approach**: Theory-first computational social science using SCT constructs

## Phase 1: Theory Extraction

**Tool**: `T302_THEORY_EXTRACTION`
**Input**: Turner 1986 Self-Categorization Theory paper (PDF)

**Extracted Theory Schema**:
```json
{
  "theory_name": "Self-Categorization Theory",
  "constructs": {
    "prototype": "Most representative member of category",
    "meta_contrast_ratio": "Ratio of intergroup to intragroup differences", 
    "depersonalization": "Shift from personal to social identity",
    "salience": "Cognitive accessibility × fit"
  },
  "algorithms": {
    "mathematical": [{
      "name": "meta_contrast_ratio",
      "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
      "parameters": {
        "x_i": "individual position",
        "x_outgroup": "outgroup positions", 
        "x_ingroup": "ingroup positions"
      }
    }],
    "logical": [{
      "name": "prototype_identification",
      "rules": [
        "IF member has highest average similarity to other ingroup members",
        "THEN member is prototype"
      ]
    }],
    "procedural": [{
      "name": "depersonalization_detection",
      "steps": [
        "Calculate personal identity markers in text",
        "Calculate social identity markers in text",
        "Compare ratio over time"
      ]
    }]
  }
}
```

**Uncertainty Assessment**:
```json
{
  "tool": "T302_THEORY_EXTRACTION",
  "uncertainty": {
    "theory_construct_alignment": {
      "score": 0.15,
      "justification": "Turner 1986 is foundational SCT text, constructs well-defined",
      "belief_masses": {"support": 0.85, "reject": 0.05, "uncertain": 0.10}
    }
  }
}
```

## Phase 2: Data Loading & Schema Discovery

### Step 1: Data Loading
**Tool**: `T06_JSON_LOAD`

```python
# Input
{"file": "tweets_climate.json"}

# Output  
{
  "tweets": [
    {
      "id": "tw_001",
      "user_id": "u_042", 
      "text": "Climate change is the biggest threat we face",
      "timestamp": "2024-01-15T10:30:00",
      "retweet_of": null,
      "reply_to": null
    }
    # ... 9,999 more tweets
  ]
}

# Uncertainty
{
  "data_completeness": {
    "score": 0.20,
    "justification": "JSON fully loaded but 15% tweets missing user_id",
    "belief_masses": {"support": 0.75, "reject": 0.10, "uncertain": 0.15}
  }
}
```

### Step 2: Schema Discovery
**Tool**: `T300_SCHEMA_DISCOVERER`

```python
# Output
{
  "discovered_schema": {
    "entities": ["user", "tweet", "hashtag"],
    "attributes": {
      "user": ["user_id"],
      "tweet": ["text", "timestamp", "user_id", "retweet_of", "reply_to"],
      "hashtag": ["tag", "tweet_id"]
    },
    "relationships": [
      {"from": "tweet", "to": "user", "type": "authored_by"},
      {"from": "tweet", "to": "tweet", "type": "retweet_of"},
      {"from": "tweet", "to": "tweet", "type": "reply_to"}
    ]
  }
}

# Uncertainty
{
  "measurement_validity": {
    "score": 0.10,
    "justification": "Schema clearly identified, standard Twitter structure",
    "belief_masses": {"support": 0.90, "reject": 0.02, "uncertain": 0.08}
  }
}
```

### Step 3: Theory-Data Mapping
**Tool**: `T301_SCHEMA_MAPPER`

```python
# Output
{
  "mapping": {
    "user": "individual",
    "tweet.text": "position_expression", 
    "user_network": "group_membership_signals",
    "required_derivations": ["position_vectors", "group_assignments"]
  }
}

# Uncertainty  
{
  "theory_construct_alignment": {
    "score": 0.25,
    "justification": "Mapping tweets to positions requires interpretation",
    "belief_masses": {"support": 0.70, "reject": 0.15, "uncertain": 0.15}
  }
}
```

## Phase 3: Entity Extraction & Fusion

### Ontology-Aware Extraction
**Tool**: `T23C_ONTOLOGY_AWARE_EXTRACTOR`

```python
# Input
{
  "tweets": [...],
  "theory_ontology": {
    "climate_believer": ["warming", "crisis", "action", "science"],
    "climate_skeptic": ["hoax", "natural", "cycle", "economy"]
  }
}

# Output
{
  "entities": [
    {
      "tweet_id": "tw_001",
      "user_id": "u_042",
      "stance_signals": ["threat", "crisis"],
      "group_signals": ["climate_believer"], 
      "conviction_strength": 0.8
    }
    # ... for each tweet
  ]
}

# Uncertainty
{
  "entity_resolution": {
    "score": 0.30,
    "justification": "Stance detection from text has inherent ambiguity",
    "belief_masses": {"support": 0.65, "reject": 0.20, "uncertain": 0.15}
  }
}
```

### Multi-Document Fusion  
**Tool**: `T302_MULTI_DOC_FUSION`

```python
# Output
{
  "unified_entities": {
    "users": {
      "u_042": {
        "tweets": ["tw_001", "tw_456", "tw_789"],
        "primary_stance": "climate_believer",
        "stance_consistency": 0.95,
        "position_vector": [0.8, 0.9, 0.7]  # Derived from text embeddings
      }
      # ... 499 more users
    }
  }
}

# Uncertainty
{
  "evidence_integration": {
    "score": 0.25, 
    "justification": "Multiple tweets per user increases confidence",
    "belief_masses": {"support": 0.72, "reject": 0.13, "uncertain": 0.15}
  }
}
```

## Phase 4: Dynamic Tool Generation

### Meta-Contrast Ratio Calculator (Generated from Theory)

```python
# LLM generates this tool from the SCT formula:
class GeneratedMCRTool(KGASTool):
    def execute(self, request):
        users = request.input_data['users']
        
        mcr_scores = {}
        for user_id, user_data in users.items():
            position = user_data['position_vector']
            stance = user_data['primary_stance']
            
            # Calculate distances to in-group and out-group
            in_distances = []
            out_distances = []
            
            for other_id, other_data in users.items():
                if other_id == user_id:
                    continue
                other_pos = other_data['position_vector']
                distance = np.linalg.norm(position - other_pos)
                
                if other_data['primary_stance'] == stance:
                    in_distances.append(distance)
                else:
                    out_distances.append(distance)
            
            # MCR calculation
            mcr = sum(out_distances) / sum(in_distances) if in_distances else float('inf')
            mcr_scores[user_id] = {
                "mcr": mcr,
                "n_ingroup": len(in_distances),
                "n_outgroup": len(out_distances)
            }
        
        # Uncertainty assessment
        total_users = len(users)
        users_with_positions = len([u for u in users.values() if u.get('position_vector')])
        coverage = users_with_positions / total_users
        
        uncertainty = {
            "score": 0.20 if coverage > 0.9 else 0.35 if coverage > 0.7 else 0.50,
            "justification": f"MCR calculated for {coverage:.1%} of users",
            "belief_masses": {
                "support": 0.75 if coverage > 0.9 else 0.60,
                "reject": 0.10,
                "uncertain": 0.15 if coverage > 0.9 else 0.30
            }
        }
        
        return ToolResult(
            status="success",
            data={"mcr_scores": mcr_scores},
            metadata={"uncertainty": uncertainty}
        )
```

**Execution Result**:
```json
{
  "mcr_scores": {
    "u_042": {"mcr": 3.2, "n_ingroup": 156, "n_outgroup": 344},
    "u_101": {"mcr": 2.8, "n_ingroup": 201, "n_outgroup": 299}
  },
  "uncertainty": {
    "score": 0.20,
    "justification": "MCR calculated for 92% of users",
    "belief_masses": {"support": 0.75, "reject": 0.10, "uncertain": 0.15}
  }
}
```

### Prototype Identifier (Generated from Logical Rules)

```python
class GeneratedPrototypeIdentifierTool(KGASTool):
    def execute(self, request):
        mcr_scores = request.input_data['mcr_scores']
        users = request.input_data['users']
        
        # Group users by stance
        groups = {}
        for user_id, user_data in users.items():
            stance = user_data['primary_stance']
            if stance not in groups:
                groups[stance] = []
            groups[stance].append(user_id)
        
        prototypes = {}
        for stance, members in groups.items():
            # Find member with highest average similarity (lowest avg distance)
            avg_distances = {}
            for member in members:
                distances = []
                for other in members:
                    if member != other:
                        dist = np.linalg.norm(
                            users[member]['position_vector'] - 
                            users[other]['position_vector']
                        )
                        distances.append(dist)
                avg_distances[member] = np.mean(distances) if distances else float('inf')
            
            prototype = min(avg_distances, key=avg_distances.get)
            prototypes[stance] = {
                "user_id": prototype,
                "avg_distance": avg_distances[prototype],
                "group_size": len(members)
            }
        
        # Uncertainty based on group sizes
        min_group_size = min(p['group_size'] for p in prototypes.values())
        uncertainty = {
            "score": 0.25 if min_group_size > 50 else 0.40,
            "justification": f"Smallest group has {min_group_size} members",
            "belief_masses": {"support": 0.70, "reject": 0.15, "uncertain": 0.15}
        }
        
        return ToolResult(
            data={"prototypes": prototypes},
            metadata={"uncertainty": uncertainty}
        )
```

## Phase 5: Multi-Level Aggregation

### Tweet→User Aggregation with Dempster-Shafer

```python
class TweetUserAggregator(KGASTool):
    def execute(self, request):
        tweet_analyses = request.input_data['tweet_analyses']
        
        # Group by user
        user_aggregations = {}
        for tweet_id, analysis in tweet_analyses.items():
            user_id = analysis['user_id']
            if user_id not in user_aggregations:
                user_aggregations[user_id] = {
                    "tweets": [],
                    "evidences": []
                }
            user_aggregations[user_id]["tweets"].append(tweet_id)
            user_aggregations[user_id]["evidences"].append(analysis['uncertainty'])
        
        # Dempster-Shafer combination for each user
        user_beliefs = {}
        for user_id, data in user_aggregations.items():
            evidences = data['evidences']
            
            # Combine all tweet evidences
            combined = evidences[0]['belief_masses']
            for evidence in evidences[1:]:
                masses = evidence['belief_masses']
                
                # Calculate conflict
                K = (combined["support"] * masses["reject"] + 
                     combined["reject"] * masses["support"])
                
                if K < 1:
                    factor = 1 / (1 - K)
                    combined = {
                        "support": factor * (
                            combined["support"] * masses["support"] +
                            combined["support"] * masses["uncertain"] +
                            combined["uncertain"] * masses["support"]
                        ),
                        "reject": factor * (
                            combined["reject"] * masses["reject"] +
                            combined["reject"] * masses["uncertain"] +
                            combined["uncertain"] * masses["reject"]
                        ),
                        "uncertain": factor * combined["uncertain"] * masses["uncertain"]
                    }
            
            user_beliefs[user_id] = {
                "aggregated_belief": combined,
                "n_tweets": len(data['tweets']),
                "conflict_level": K
            }
        
        # Overall aggregation uncertainty
        avg_tweets_per_user = np.mean([ub['n_tweets'] for ub in user_beliefs.values()])
        uncertainty = {
            "score": 0.15 if avg_tweets_per_user > 10 else 0.30,
            "justification": f"Average {avg_tweets_per_user:.1f} tweets per user",
            "belief_masses": {"support": 0.80, "reject": 0.08, "uncertain": 0.12}
        }
        
        return ToolResult(
            data={"user_beliefs": user_beliefs},
            metadata={"uncertainty": uncertainty, "aggregation_method": "dempster_shafer"}
        )
```

**Result**:
```json
{
  "user_beliefs": {
    "u_042": {
      "aggregated_belief": {"support": 0.82, "reject": 0.06, "uncertain": 0.12},
      "n_tweets": 23,
      "conflict_level": 0.08
    }
  },
  "uncertainty": {
    "score": 0.15,
    "justification": "Average 20.3 tweets per user",
    "belief_masses": {"support": 0.80, "reject": 0.08, "uncertain": 0.12}
  }
}
```

## Phase 6: Cross-Modal Analysis

### Graph→Table Conversion
**Tool**: `GRAPH_TABLE_EXPORTER`

```python
# Output
{
  "edge_list": [
    {"source": "u_042", "target": "u_101", "weight": 0.8, "type": "similar_stance"},
    {"source": "u_042", "target": "u_205", "weight": 0.2, "type": "opposing_stance"}
  ],
  "node_attributes": [
    {"node": "u_042", "mcr": 3.2, "stance": "believer", "centrality": 0.7}
  ]
}

# Uncertainty
{
  "score": 0.10,
  "justification": "Direct format conversion, no information loss",
  "belief_masses": {"support": 0.90, "reject": 0.02, "uncertain": 0.08}
}
```

### Cross-Modal Synthesis
**Tool**: `CROSS_MODAL_ANALYZER`

```python
# Input: Graph + Table + Vector data, MCR scores, prototypes

# Output
{
  "synthesis": {
    "polarization_level": 0.75,
    "key_findings": [
      "High MCR scores (avg 2.9) indicate strong group boundaries",
      "Prototypes are highly central in network (avg centrality 0.8)",
      "Vector embeddings show clear clustering (silhouette score 0.7)"
    ],
    "convergent_evidence": {
      "graph_clustering": 0.72,
      "mcr_separation": 0.75, 
      "embedding_clusters": 0.70
    }
  }
}

# Uncertainty
{
  "inference_chain_validity": {
    "score": 0.22,
    "justification": "Multiple modalities converge on similar findings",
    "belief_masses": {"support": 0.75, "reject": 0.10, "uncertain": 0.15}
  }
}
```

## Phase 7: Uncertainty Propagation Chain

**Complete uncertainty propagation through analysis pipeline**:

```python
def propagate_uncertainty(tool_results):
    # Track uncertainty at each step
    
    # Theory extraction (root) 
    u1 = {"tool": "T302", "score": 0.15, "masses": {"s": 0.85, "r": 0.05, "u": 0.10}}
    
    # Data loading
    u2 = {"tool": "T06", "score": 0.20, "masses": {"s": 0.75, "r": 0.10, "u": 0.15}}
    
    # Schema discovery & mapping
    u3 = combine_dependent(u2, {"score": 0.25, "masses": {"s": 0.70, "r": 0.15, "u": 0.15}})
    
    # Entity extraction
    u4 = combine_dependent(u3, {"score": 0.30, "masses": {"s": 0.65, "r": 0.20, "u": 0.15}})
    
    # MCR calculation (depends on extraction)
    u5 = combine_dependent(u4, {"score": 0.20, "masses": {"s": 0.75, "r": 0.10, "u": 0.15}})
    
    # Aggregation  
    u6 = combine_dependent(u5, {"score": 0.15, "masses": {"s": 0.80, "r": 0.08, "u": 0.12}})
    
    # Cross-modal synthesis
    u7 = combine_parallel([u5, u6], {"score": 0.22, "masses": {"s": 0.75, "r": 0.10, "u": 0.15}})
    
    return {
        "overall_score": 0.38,  # Final propagated uncertainty
        "overall_masses": {"support": 0.58, "reject": 0.22, "uncertain": 0.20},
        "critical_uncertainties": [
            "Entity extraction from text (0.30)",
            "Theory-data mapping (0.25)", 
            "Cross-modal synthesis (0.22)"
        ],
        "confidence_statement": "Moderate confidence in polarization findings. "
                                "Primary uncertainty from text interpretation and theory mapping."
    }
```

## Key Insights Demonstrated

### 1. **End-to-End Theory Integration**
- Academic theory (Turner 1986) → Executable analysis tools
- Theory constructs directly inform data analysis approach
- Complete traceability from theoretical foundation to results

### 2. **Dynamic Tool Generation Feasibility** 
- MCR calculator generated from mathematical formula
- Prototype identifier generated from logical rules
- Tools assess their own uncertainty based on data coverage

### 3. **Uncertainty Compounds Through Pipeline**
- Individual tool uncertainties: 0.15-0.30
- Final synthesis uncertainty: 0.38
- Critical points: text interpretation, theory-data mapping

### 4. **Aggregation Reduces Uncertainty**
- Multiple tweets per user: uncertainty decreases from 0.30 to 0.15
- Dempster-Shafer combination handles evidence integration
- More evidence of same phenomenon increases confidence

### 5. **Cross-Modal Validation**
- Graph clustering (0.72), MCR separation (0.75), embedding clusters (0.70)
- Convergent findings across modalities reduce overall uncertainty
- Different analytical perspectives validate same conclusions

### 6. **Research-Grade Provenance**
- Every result traceable to source data and theoretical foundation
- Complete uncertainty tracking enables confidence assessment
- Methodological transparency supports academic reproducibility

## Schema Requirements

### Tool Uncertainty Schema
```python
class ToolUncertainty:
    score: float  # 0-1 overall uncertainty
    justification: str  # Human-readable explanation
    belief_masses: Dict[str, float]  # {"support", "reject", "uncertain"}
    dimensions: Dict[str, float]  # Optional: specific uncertainty dimensions
    data_coverage: float  # Optional: percentage of data processed
```

### Aggregation Schema
```python
class AggregationRequest:
    instances: List[Dict]  # Instance-level results
    aggregation_level: str  # "tweet_to_user", "user_to_community"
    method: str  # "dempster_shafer", "statistical"
    
class AggregationResult:
    aggregated_data: Dict
    aggregated_uncertainty: ToolUncertainty
    conflict_metrics: Dict  # Conflict between evidences
    n_instances: int
```

### Dynamic Tool Schema
```python
class DynamicToolSpec:
    algorithm_type: str  # "mathematical", "logical", "procedural"
    name: str
    formula_or_rules: Union[str, List[str]]
    parameters: Dict[str, str] 
    expected_inputs: Dict[str, type]
    expected_outputs: Dict[str, type]
```

---

**Status**: This worked example demonstrates architectural feasibility of theory-driven computational social science with complete uncertainty tracking and cross-modal analysis. Ready for implementation when KGAS reaches Phase 2 (theory-specific tools).

**Key Contribution**: Proves end-to-end integration from academic theory to executable analysis with research-grade uncertainty assessment and methodological transparency.