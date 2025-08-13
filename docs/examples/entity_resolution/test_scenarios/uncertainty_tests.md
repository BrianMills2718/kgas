# Entity Resolution Uncertainty Tests

**Consolidated from**: uncertainty_stress_tests.md, extreme_uncertainty_cases.md  
**Purpose**: Test uncertainty quantification and propagation in entity resolution  
**Last Updated**: 2025-08-06

---

## Overview

This document consolidates tests focused on uncertainty in entity resolution, including:
- How uncertainty is quantified and tracked through the pipeline
- Extreme uncertainty scenarios (complete ambiguity, null references)
- Uncertainty propagation through analytical stages
- Impact of uncertainty on research conclusions

---

## Part 1: Uncertainty Propagation Tests

### Test 1: Political Coalition Formation with Uncertainty Tracking

#### Input Text
```
Congressional Hearing Transcript - Day 1:
Sen_A (R): "We Republicans demand fiscal responsibility."
Sen_B (D): "We Democrats will protect social programs."
Sen_C (R): "Some of us are willing to negotiate."
Sen_D (D): "We moderates from both parties should find common ground."
Sen_E (R): "They don't speak for all of us."
Sen_F (D): "When they say 'moderates,' who exactly do they mean?"

Day 3:
Sen_C (R): "We've formed a bipartisan working group."
Sen_D (D): "Our coalition includes members from both parties."
Sen_A (R): "They've betrayed conservative principles."
Sen_B (D): "Those turncoats have abandoned progressive values."
```

#### Stage 1: Theory Schema Extraction
```json
{
  "theory": "Social Movement Coalition Theory",
  "schema": {
    "entities": ["Political_Actor", "Coalition", "Party"],
    "relations": ["belongs_to", "opposes", "forms_coalition"],
    "properties": ["ideology", "negotiation_stance", "coalition_membership"]
  },
  "extraction_uncertainty": {
    "confidence": 0.85,
    "factors": {
      "schema_completeness": 0.9,
      "construct_clarity": 0.8
    },
    "uncertainty_type": "epistemic",
    "explanation": "Theory provides clear coalition concepts but may miss emergent dynamics"
  }
}
```

#### Stage 2: Entity Extraction with Uncertainty
```json
{
  "entity_instances": [
    {
      "text": "We Republicans",
      "speaker": "Sen_A",
      "resolved_entity": {
        "value": "Republican_Party",
        "confidence": 0.95,
        "uncertainty_type": "low_aleatory"
      }
    },
    {
      "text": "Some of us",
      "speaker": "Sen_C",
      "resolved_entity": {
        "distribution": {
          "Republican_Moderates": 0.6,
          "Republican_Party_Subset": 0.3,
          "Unclear": 0.1
        },
        "confidence": 0.6,
        "uncertainty_type": "high_epistemic",
        "explanation": "Ambiguous subset reference"
      }
    },
    {
      "text": "They",
      "speaker": "Sen_E",
      "resolved_entity": {
        "distribution": {
          "Moderates": 0.4,
          "Democrats": 0.3,
          "Sen_C_and_allies": 0.2,
          "Unknown": 0.1
        },
        "confidence": 0.4,
        "uncertainty_type": "high_aleatory",
        "explanation": "Multiple valid interpretations"
      }
    }
  ]
}
```

#### Stage 3: Relationship Extraction with Uncertainty
```json
{
  "relationships": [
    {
      "subject": "Sen_C",
      "predicate": "forms_coalition",
      "object": "Bipartisan_Working_Group",
      "confidence": 0.9,
      "uncertainty_factors": {
        "entity_uncertainty": 0.05,
        "relation_uncertainty": 0.05
      },
      "combined_confidence": 0.855
    },
    {
      "subject": "Unknown_They",
      "predicate": "betrayed",
      "object": "conservative_principles",
      "confidence": 0.4,
      "uncertainty_factors": {
        "entity_uncertainty": 0.5,
        "relation_uncertainty": 0.1
      },
      "combined_confidence": 0.2,
      "note": "High uncertainty due to unresolved entity"
    }
  ]
}
```

#### Stage 4: Graph Construction with Uncertainty
```json
{
  "graph_metrics": {
    "total_nodes": 15,
    "certain_nodes": 8,
    "uncertain_nodes": 7,
    "avg_node_confidence": 0.72,
    "total_edges": 23,
    "certain_edges": 12,
    "uncertain_edges": 11,
    "avg_edge_confidence": 0.68
  },
  "uncertainty_distribution": {
    "high_confidence": 8,
    "medium_confidence": 9,
    "low_confidence": 6
  }
}
```

#### Stage 5: Analysis with Uncertainty Propagation
```json
{
  "coalition_analysis": {
    "identified_coalitions": 3,
    "confidence_per_coalition": {
      "Traditional_Republicans": 0.9,
      "Traditional_Democrats": 0.88,
      "Bipartisan_Moderates": 0.65
    },
    "uncertainty_impact": "Medium - core coalitions clear but moderate coalition membership uncertain"
  },
  "key_findings": [
    {
      "finding": "Bipartisan coalition emerged by Day 3",
      "confidence": 0.75,
      "caveat": "Coalition composition uncertain due to ambiguous references"
    },
    {
      "finding": "Both parties show internal division",
      "confidence": 0.85,
      "caveat": "Extent of division unclear due to unresolved 'they' references"
    }
  ]
}
```

---

## Part 2: Extreme Uncertainty Scenarios

### Test 2: Complete Ambiguity (Diplomatic Cables)

#### Input