# Uncertainty Assessment Context Patterns

## Core Principle
If Claude can identify what's important for uncertainty assessment, so can the LLM doing the assessment - just provide the same context.

## Reusable Context Pattern

```python
def assess_uncertainty(operation_type: str, context: Dict[str, Any]) -> UniversalUncertainty:
    """Universal assessment with rich context"""
    
    # Always include theory schema if relevant
    if "theory_schema" in context:
        theory_context = f"""
        Theory Schema:
        {json.dumps(context["theory_schema"], indent=2)}
        """
    else:
        theory_context = ""
    
    # Always include full operational context
    prompt = f"""
    Assess uncertainty for this {operation_type} operation.
    
    {theory_context}
    
    Operational Context:
    {json.dumps(context, indent=2)}
    
    As an expert, consider all relevant factors and provide:
    - uncertainty (0-1)
    - complete reasoning explaining your assessment
    - evidence_count if aggregating multiple items
    """
    
    return llm.structured_output(prompt, UniversalUncertainty)
```

## Examples With Theory Schema

### MCR Calculation (Theory-Critical)

```python
# The theory schema tells the LLM what's important
theory_schema = {
    "name": "Self-Categorization Theory",
    "core_constructs": {
        "meta_contrast_ratio": {
            "importance": "PRIMARY - identifies prototypical members",
            "formula": "MCR = Σ|x_i - x_outgroup| / Σ|x_i - x_ingroup|",
            "requirements": ["position_vectors", "group_membership"]
        },
        "depersonalization": {
            "importance": "SECONDARY - shows identity shift",
            "indicators": ["pronoun_shifts", "language_convergence"]
        }
    }
}

context = {
    "theory_schema": theory_schema,  # This tells LLM that MCR is PRIMARY
    "operation": "mcr_calculation",
    "coverage": 0.70,
    "implementation": {
        "position_vectors": "derived from text embeddings",
        "distance_metric": "cosine"
    }
}

# LLM will understand MCR is critical because theory_schema says so
uncertainty = assess_uncertainty("mcr_calculation", context)
```

### Schema Mapping (With Data Model)

```python
# The data model tells the LLM what's critical
data_model = {
    "critical_fields": {
        "user_identity": "REQUIRED for all joins and entity resolution",
        "timestamp": "REQUIRED for temporal analysis",
        "group_membership": "REQUIRED for MCR calculation"
    },
    "optional_fields": {
        "psychology_scores": "ENHANCES analysis but not required everywhere"
    }
}

context = {
    "data_model": data_model,  # This tells LLM identity is critical
    "mappings": {
        "user_identity": {
            "candidates": ["uid", "author", "user_id"],
            "resolution": "fuzzy matching required"
        },
        "timestamp": {
            "candidates": ["posted_at", "created_time"],
            "resolution": "parse both formats"
        }
    }
}

# LLM will understand identity ambiguity is critical because data_model says so
uncertainty = assess_uncertainty("schema_mapping", context)
```

### Temporal Aggregation (With Pattern Info)

```python
# Include what patterns mean
pattern_context = {
    "pattern_type": "pronoun_shift",
    "pattern_meaning": "depersonalization indicator in SCT",
    "instances_found": 237,
    "reverse_instances": 12,
    "interpretation": "strong directional signal when ratio > 10:1"
}

context = {
    "theory_schema": theory_schema,
    "pattern_context": pattern_context,
    "temporal_windows": ["daily", "weekly", "monthly"],
    "consistency": "pattern visible at all scales"
}

# LLM will understand 237 instances reduces uncertainty
uncertainty = assess_uncertainty("temporal_pattern_aggregation", context)
```

### Cross-Modal Synthesis (With Convergence Definition)

```python
# Define what convergence means
convergence_context = {
    "convergence_definition": "Different analysis methods reaching same conclusion",
    "independence_definition": "Different methods analyzing different aspects",
    "finding": "All three modalities support group polarization"
}

modality_results = {
    "graph": {"finding": "distinct communities", "uncertainty": 0.15},
    "table": {"finding": "identity→rejection path", "uncertainty": 0.28},
    "vector": {"finding": "language convergence", "uncertainty": 0.18}
}

context = {
    "convergence_context": convergence_context,
    "modality_results": modality_results,
    "synthesis": "convergent - all support same hypothesis"
}

# LLM will understand convergence reduces uncertainty
uncertainty = assess_uncertainty("cross_modal_synthesis", context)
```

### Statistical Validation (With Statistical Context)

```python
# Include statistical interpretation
statistical_context = {
    "metric": "Cohen's Kappa",
    "value": 0.73,
    "interpretation_scale": {
        "0.0-0.20": "slight agreement",
        "0.21-0.40": "fair agreement", 
        "0.41-0.60": "moderate agreement",
        "0.61-0.80": "substantial agreement",  # <-- 0.73 falls here
        "0.81-1.00": "almost perfect agreement"
    }
}

context = {
    "statistical_context": statistical_context,
    "llm_results": {
        "GPT-4": {"entities": 2834},
        "Claude": {"entities": 2791},
        "Gemini": {"entities": 2812}
    }
}

# LLM will understand κ=0.73 is substantial
uncertainty = assess_uncertainty("multi_llm_validation", context)
```

## Key Insights

1. **Theory Schema Provides Importance**
   - Don't hardcode "MCR is THE core measure"
   - Let theory_schema specify importance levels
   - LLM reads schema and understands priorities

2. **Data Model Provides Criticality**
   - Don't hardcode "identity is critical for joins"
   - Let data_model specify field requirements
   - LLM reads model and understands dependencies

3. **Statistical Context Provides Interpretation**
   - Don't hardcode "κ=0.73 is good"
   - Provide interpretation scales
   - LLM reads scale and understands quality

4. **Pattern Context Provides Meaning**
   - Don't assume LLM knows what patterns mean
   - Include pattern interpretation in context
   - LLM reads meaning and assesses appropriately

## The Universal Pattern

```python
def assess_uncertainty(operation_type: str, full_context: Dict) -> UniversalUncertainty:
    """
    One function, but with rich, structured context that includes:
    - Theory schema (if applicable)
    - Data model (if applicable)
    - Statistical interpretations (if applicable)
    - Pattern meanings (if applicable)
    - Operational details (always)
    """
    
    prompt = f"""
    Assess uncertainty for {operation_type}.
    
    Full Context:
    {json.dumps(full_context, indent=2)}
    
    Based on all provided context, assess uncertainty (0-1) with complete reasoning.
    """
    
    return llm.structured_output(prompt, UniversalUncertainty)
```

## Why This Works

1. **No Custom Prompts Per Tool** - Just rich context
2. **Reusable Patterns** - Theory schemas, data models, stat scales
3. **LLM Figures It Out** - Given same context I have, LLM reaches same conclusions
4. **Transparent** - Context + reasoning shows the logic

## The Bottom Line

**Stop writing specialized prompts. Provide structured context and let the LLM figure it out - just like you did.**

If you can look at a theory schema and think "MCR is critical," so can the assessment LLM. Just give it the schema.