# [DEPRECATED] Hybrid Uncertainty System: Simplified Example

## DEPRECATED: This document describes the hybrid approach which has been superseded by the Pure LLM Intelligence approach
## See: 20250812_uncertainty_approach_change.md for the current approach

## Overview
[DEPRECATED] This example shows the hybrid approach: simple uncertainty for tools, D-S only for aggregation.

## Phase 1: Individual Tools (Simple Uncertainty)

### Tool: Text Chunker
```python
result = ToolResult(
    data={"chunks": [...]},
    uncertainty=SimpleToolUncertainty(
        uncertainty=0.15,
        reasoning="Clear sentence boundaries, minimal ambiguity in splitting",
        primary_factors=["Text clarity", "Standard formatting"]
    )
)
```

### Tool: Entity Extractor
```python
result = ToolResult(
    data={"entities": [...]},
    uncertainty=SimpleToolUncertainty(
        uncertainty=0.25,
        reasoning="Some ambiguous entity mentions, context helps but not definitive",
        primary_factors=["Pronoun resolution", "Acronym disambiguation"]
    )
)
```

### Tool: MCR Calculator (Dynamic)
```python
result = ToolResult(
    data={"mcr_scores": {...}},
    uncertainty=SimpleToolUncertainty(
        uncertainty=0.20,
        reasoning="90% user coverage, clear group boundaries, theory from 1986 applied to 2021 data adds some uncertainty",
        primary_factors=["10% missing users", "Temporal theory mismatch", "Clear patterns"]
    )
)
```

## Phase 2: Aggregation (D-S Applied)

### Tweet → User Aggregation
```python
# Input: 23 tweets from user with simple uncertainties
tweet_uncertainties = [
    SimpleToolUncertainty(uncertainty=0.22, reasoning="..."),
    SimpleToolUncertainty(uncertainty=0.18, reasoning="..."),
    SimpleToolUncertainty(uncertainty=0.25, reasoning="..."),
    # ... 20 more
]

# Aggregation with D-S
aggregator = TweetUserAggregator()
result = aggregator.aggregate(
    DSAggregationInput(
        evidences=tweet_uncertainties,
        aggregation_context="Combining 23 tweets to assess user stance"
    )
)

# Output
DSAggregationResult(
    aggregated_uncertainty=0.12,  # Reduced from ~0.22 average
    belief_masses=BeliefMass(
        support=0.75,
        reject=0.10,
        uncertain=0.15
    ),
    reasoning="Consistent pro-vaccine stance across tweets, low conflict",
    n_evidences=23,
    conflict_level=0.08
)
```

### Cross-Modal Synthesis
```python
# Three modalities with simple uncertainties
graph_result = SimpleToolUncertainty(uncertainty=0.15, reasoning="Clear communities")
table_result = SimpleToolUncertainty(uncertainty=0.28, reasoning="30% missing psychology")
vector_result = SimpleToolUncertainty(uncertainty=0.18, reasoning="Good embeddings")

# D-S synthesis
synthesis = CrossModalSynthesizer()
result = synthesis.synthesize(
    DSAggregationInput(
        evidences=[graph_result, table_result, vector_result],
        aggregation_context="Convergence across graph, table, vector modalities"
    )
)

# Output
DSAggregationResult(
    aggregated_uncertainty=0.18,  # Convergence reduces uncertainty
    belief_masses=BeliefMass(
        support=0.70,
        reject=0.12,
        uncertain=0.18
    ),
    reasoning="Graph and vector strongly agree, table limited by missing data but consistent where available",
    n_evidences=3,
    conflict_level=0.15
)
```

## Implementation Patterns

### Pattern 1: Simple Tool Uncertainty
```python
class GeneratedTool(KGASTool):
    def execute(self, request):
        # Do computation
        result_data = self.compute(request.input_data)
        
        # Assess uncertainty (simple)
        uncertainty = self.assess_simple_uncertainty(result_data, request.context)
        
        return ToolResult(
            data=result_data,
            uncertainty=uncertainty  # SimpleToolUncertainty
        )
    
    def assess_simple_uncertainty(self, data, context):
        prompt = f"""
        Assess uncertainty for this {self.tool_name} result.
        Consider all relevant factors.
        Return SimpleToolUncertainty with score (0-1) and reasoning.
        """
        return llm.structured_output(prompt, SimpleToolUncertainty)
```

### Pattern 2: D-S Aggregation Tool
```python
class AggregationTool(KGASTool):
    def execute(self, request):
        evidences = request.input_data['evidences']
        
        if len(evidences) < 3:
            # Too few for D-S, just average
            avg_uncertainty = sum(e.uncertainty for e in evidences) / len(evidences)
            return ToolResult(
                data={"aggregated": avg_uncertainty},
                uncertainty=SimpleToolUncertainty(
                    uncertainty=avg_uncertainty,
                    reasoning=f"Simple average of {len(evidences)} evidences"
                )
            )
        
        # Use D-S for 3+ evidences
        result = self.dempster_shafer_aggregate(evidences)
        
        return ToolResult(
            data={"aggregated": result.aggregated_uncertainty},
            uncertainty=result  # DSAggregationResult
        )
```

## Key Benefits of Hybrid Approach

1. **Simplicity**: Most tools just output a number + reasoning
2. **Power Where Needed**: D-S for aggregation where it adds value
3. **Less Debugging**: Fewer belief masses to validate
4. **Clear Mental Model**: Tools are simple, aggregation is sophisticated
5. **Flexibility**: Can use D-S when helpful, skip when not

## Prompt Examples

### Simple Tool Prompt
```yaml
tool_uncertainty_prompt: |
  As an expert, assess the uncertainty of this {tool_name} output.
  
  Context: {context}
  Result: {result}
  
  Consider all relevant factors that affect confidence.
  
  Return SimpleToolUncertainty with:
  - uncertainty: 0-1 score (0=certain, 1=very uncertain)
  - reasoning: Your expert assessment
  - primary_factors: Main factors affecting uncertainty
```

### D-S Aggregation Prompt
```yaml
ds_aggregation_prompt: |
  Using Dempster-Shafer theory, combine these {n} evidences.
  
  Evidences: {evidences}
  Context: {aggregation_context}
  
  Assign belief masses (support, reject, uncertain) that sum to 1.0.
  Consider the level of agreement/conflict between evidences.
  
  Return DSAggregationResult with aggregated assessment.
```

## Summary

The hybrid approach gives us:
- **80% of the simplicity** (most tools are simple)
- **100% of the power** (D-S where it matters)
- **Better juice/squeeze ratio** than full D-S everywhere