# Complete Uncertainty Assessment Walkthrough

Walking through the actual DAG with realistic context available at each step.

## Phase 1: Theory Extraction

### T302_THEORY_EXTRACTION

**Available Context**: 
- Input: Turner & Oakes 1986 PDF
- Output: theory_schema.json

```python
# What the tool actually outputs
tool_output = {
    "tool_id": "T302_THEORY_EXTRACTION",
    "source": "Turner_Oakes_1986.pdf",
    "extraction_result": {
        "theory_name": "Self-Categorization Theory",
        "core_constructs": {
            "meta_contrast_ratio": {
                "formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
                "purpose": "identifies prototypical group members"
            },
            "depersonalization": {
                "definition": "shift from personal to social identity",
                "indicators": ["pronoun shifts", "conformity to prototype"]
            }
        },
        "extraction_notes": "Formula clear, normative fit details sparse"
    }
}

# Uncertainty assessment prompt
prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

# LLM response
UniversalUncertainty(
    uncertainty=0.15,
    reasoning="Theory extraction successful with clear core formula. Some implementation details like normative fit calculation not fully specified in source paper."
)
```

## Phase 2: Multi-Document Ingestion

### T01_PDF_LOAD

**Available Context**:
- Input: COVID tweets PDF
- Output: Extracted text

```python
tool_output = {
    "tool_id": "T01_PDF_LOAD",
    "file": "covid_tweets.pdf",
    "pages_processed": 1547,
    "extraction_quality": "clean",
    "issues": "none"
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.10,
    reasoning="Clean PDF extraction with no issues across 1547 pages."
)
```

### T05_CSV_LOAD

**Available Context**:
- Input: user_psychology.csv
- Output: Loaded data with statistics

```python
tool_output = {
    "tool_id": "T05_CSV_LOAD",
    "file": "user_psychology.csv",
    "total_rows": 2506,
    "valid_rows": 1754,
    "missing_rows": 752,
    "columns": ["uid", "CB_score", "identity_strength", "posted_at"],
    "missing_pattern": "appears random"
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.08,
    reasoning="CSV loaded successfully. 30% rows have missing values but structure is clean and missingness appears random."
)
```

### T300_SCHEMA_DISCOVERER (Aggregation point)

**Available Context**:
- Inputs from T01, T05, T06, T13
- Output: Discovered schemas

```python
tool_output = {
    "tool_id": "T300_SCHEMA_DISCOVERER",
    "sources_analyzed": 4,
    "schemas_discovered": {
        "csv": {"columns": ["uid", "CB_score", "posted_at"]},
        "json": {"structure": {"author": "str", "content": "str"}},
        "graph": {"format": {"nodes": [], "edges": []}}
    },
    "integration_notes": "All schemas successfully mapped"
}

# For aggregation, include evidence details
prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

This tool aggregates inputs from 4 sources with uncertainties:
- T01_PDF: 0.10
- T05_CSV: 0.08  
- T06_JSON: 0.12
- T13_WEB: 0.25

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.12,
    reasoning="Successfully discovered and mapped schemas from all 4 sources. Lower than average uncertainty (0.14) because schemas complement rather than conflict.",
    evidence_count=4
)
```

### T301_SCHEMA_MAPPER

**Available Context**:
- Input: discovered_schemas.json
- Theory schema (from T302)
- Output: mapping_rules.json

```python
# Now we have theory schema available
theory_schema = {
    "required_fields": ["user_identity", "group_membership", "timestamp"],
    "algorithms": {"mcr": "needs position vectors"}
}

tool_output = {
    "tool_id": "T301_SCHEMA_MAPPER",
    "theory_requirements": theory_schema["required_fields"],
    "mappings": {
        "user_identity": {
            "candidates": ["uid", "author", "user_id"],
            "resolution": "fuzzy match all three"
        },
        "timestamp": {
            "candidates": ["posted_at", "created_time"],
            "resolution": "parse both formats"
        }
    },
    "ambiguous_mappings": 3,
    "total_mappings": 47
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Theory schema requires: {json.dumps(theory_schema, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.18,
    reasoning="3 of 47 mappings required fuzzy matching. User identity mapping is critical for theory requirements and has multiple candidates requiring resolution."
)
```

## Phase 3: Theory-Guided Extraction

### T23C_ONTOLOGY_AWARE_EXTRACTOR

**Available Context**:
- Input: unified_graph + theory_schema
- Output: theory-aligned entities

```python
tool_output = {
    "tool_id": "T23C_ONTOLOGY_AWARE_EXTRACTOR",
    "theory_applied": "Self-Categorization Theory",
    "extraction_results": {
        "self_categories_found": ["vaccine_hesitant", "freedom_fighters", "truth_seekers"],
        "prototype_candidates": 47,
        "depersonalization_instances": 237,
        "extraction_confidence": {
            "categories": "high",
            "prototypes": "requires MCR calculation",
            "depersonalization": "moderate"
        }
    }
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.25,
    reasoning="Theory concepts successfully mapped to data. Categories clearly identified, 237 depersonalization instances found. Prototype identification deferred to MCR calculation. Some subjectivity in mapping abstract concepts to concrete patterns."
)
```

## Phase 4: Graph Analysis

### T50_COMMUNITY_DETECT

**Available Context**:
- Input: Graph from T34
- Output: Communities

```python
tool_output = {
    "tool_id": "T50_COMMUNITY_DETECT",
    "algorithm": "Louvain",
    "graph_stats": {
        "nodes": 2506,
        "edges": 48291,
        "completeness": "full graph available"
    },
    "results": {
        "communities_found": 3,
        "modularity": 0.72,
        "sizes": [512, 887, 1107],
        "stability": "consistent across 10 runs"
    }
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.15,
    reasoning="High modularity (0.72) indicates clear community structure. Results stable across multiple runs. Full graph available with no missing edges."
)
```

### T51_META_CONTRAST_CALCULATOR

**Available Context**:
- Theory schema with MCR formula
- Communities from T50
- Psychology data (70% coverage)

```python
tool_output = {
    "tool_id": "T51_META_CONTRAST_CALCULATOR",
    "formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
    "execution_details": {
        "users_processed": 1754,
        "users_total": 2506,
        "coverage": 0.70,
        "position_vectors": "derived from text embeddings",
        "distance_metric": "cosine"
    },
    "results": {
        "Community_A_prototype": {"user": "ID047", "MCR": 0.94},
        "Community_B_prototype": {"user": "ID892", "MCR": 0.87},
        "Community_C_prototype": {"user": "ID521", "MCR": 0.91}
    }
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

This implements the core theoretical measure from the theory schema.

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.30,
    reasoning="MCR calculated for only 70% of users due to missing psychology data. Using text embeddings as proxy for position vectors rather than direct psychological measures. High MCR scores suggest calculation is working but coverage limitation is significant.",
    data_coverage=0.70
)
```

### T52_TEMPORAL_ANALYZER

**Available Context**:
- Input: Graph with temporal metadata
- Output: Temporal patterns

```python
tool_output = {
    "tool_id": "T52_TEMPORAL_ANALYZER",
    "time_period": "Jan-Dec 2020",
    "patterns_detected": {
        "pronoun_shifts": {
            "I_to_we": 237,
            "we_to_I": 12,
            "ratio": 19.75
        },
        "salience_events": 14,
        "convergence_measured": {
            "within_group_similarity": "increased 0.31→0.23",
            "between_group_distance": "increased 0.45→0.84"
        }
    },
    "temporal_gaps": "15% days missing for some users"
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.22,
    reasoning="Strong directional signal with 237 I→we vs 12 we→I transitions. Clear convergence patterns detected. 15% temporal gaps add some uncertainty but patterns are consistent.",
    evidence_count=237
)
```

## Phase 5-8: Cross-Modal Analysis

### CROSS_MODAL_ANALYZER (Synthesis)

**Available Context**:
- Results from graph, table, vector analyses
- No theory schema needed here

```python
tool_output = {
    "tool_id": "CROSS_MODAL_ANALYZER",
    "modalities_analyzed": {
        "graph": {
            "finding": "3 distinct communities",
            "uncertainty": 0.15
        },
        "table": {
            "finding": "Identity→Rejection correlation r=0.72",
            "uncertainty": 0.28
        },
        "vector": {
            "finding": "Language convergence within groups",
            "uncertainty": 0.18
        }
    },
    "synthesis": "All modalities support group polarization hypothesis",
    "contradictions": "none"
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

This tool synthesizes findings across modalities.

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.18,
    reasoning="Three independent analyses converge on same conclusion with no contradictions. Convergence across modalities increases confidence despite individual uncertainties.",
    evidence_count=3
)
```

## Phase 10: Agent-Based Simulation

### AGENT_PARAMETERIZATION_TOOL

**Available Context**:
- All previous results
- Need to create 2506 agents

```python
tool_output = {
    "tool_id": "AGENT_PARAMETERIZATION_TOOL",
    "agents_created": 2506,
    "parameter_sources": {
        "psychology": {
            "available": 1754,
            "imputed": 752,
            "method": "network homophily"
        },
        "network": {
            "available": 2506,
            "imputed": 0
        },
        "language": {
            "available": 2506,
            "imputed": 0
        }
    }
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.35,
    reasoning="30% of agents use imputed psychology parameters. Network and language parameters complete. Imputation based on network homophily is reasonable but adds significant uncertainty for simulation."
)
```

### SIMULATION_EXECUTION_TOOL

**Available Context**:
- Parameterized agents
- Running interventions

```python
tool_output = {
    "tool_id": "SIMULATION_EXECUTION_TOOL",
    "scenarios": {
        "trusted_messenger": {
            "runs": 100,
            "mean_effect": -0.24,
            "std_dev": 0.08,
            "all_runs_direction": "reduction"
        },
        "identity_affirmation": {
            "runs": 100,
            "mean_effect": -0.31,
            "std_dev": 0.12,
            "all_runs_direction": "reduction"
        },
        "confrontation": {
            "runs": 100,
            "mean_effect": +0.12,
            "std_dev": 0.05,
            "all_runs_direction": "increase"
        }
    }
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

Input parameter uncertainty was 0.35 from imputation.

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.28,
    reasoning="Despite parameter uncertainty, all 300 simulation runs show consistent direction of effects. Multiple runs reduce uncertainty from 0.35 to 0.28. Standard deviations small relative to effect sizes.",
    evidence_count=300
)
```

## Phase 11: Theory Validation

### THEORY_VALIDATION_TOOL

**Available Context**:
- All results
- Original theory schema

```python
tool_output = {
    "tool_id": "THEORY_VALIDATION_TOOL",
    "theory": "Self-Categorization Theory",
    "predictions_tested": {
        "MCR_predicts_influence": {"result": "confirmed", "r": 0.72},
        "threat_triggers_salience": {"result": "confirmed", "r": 0.81},
        "depersonalization_occurs": {"result": "confirmed", "instances": 237},
        "prototype_guides_convergence": {"result": "confirmed", "measured": true}
    },
    "predictions_confirmed": "4 of 4"
}

prompt = """
Assess uncertainty for this tool's output:

{json.dumps(tool_output, indent=2)}

This validates the theory predictions against findings.

Provide uncertainty (0-1) and reasoning.
"""

UniversalUncertainty(
    uncertainty=0.20,
    reasoning="All 4 theory predictions confirmed with strong correlations. Multiple validation methods (correlation, instance counting, simulation) converge. Some uncertainty remains from 30% missing psychology data affecting MCR calculation.",
    evidence_count=4
)
```

## Key Observations

1. **Context We Actually Have**:
   - Tool outputs with their actual results
   - Theory schema when relevant (from T302)
   - Upstream uncertainties for aggregation points
   - Basic metadata about what the tool does

2. **Context We DON'T Have**:
   - Elaborate data models (not created anywhere)
   - Statistical interpretation guides (LLM knows these)
   - Pattern definitions (LLM figures out from data)

3. **Natural Uncertainty Flow**:
   - Low for clean data loads (0.08-0.10)
   - Increases with ambiguity (0.18 for mapping)
   - High for missing critical data (0.30 for MCR)
   - Reduces with convergence (0.18 for cross-modal)
   - Reduces with multiple runs (0.35→0.28 for simulation)

4. **Simple, Scalable Pattern**:
   ```python
   def assess_uncertainty(tool_output: Dict, additional_context: Optional[Dict] = None) -> UniversalUncertainty:
       context = tool_output
       if additional_context:
           context.update(additional_context)
       
       prompt = f"""
       Assess uncertainty for this tool's output:
       
       {json.dumps(context, indent=2)}
       
       Provide uncertainty (0-1) and reasoning.
       """
       
       return llm.structured_output(prompt, UniversalUncertainty)
   ```

The LLM sees the actual data (70% coverage, 237 instances, κ=0.73) and assesses appropriately without needing elaborate context structures.