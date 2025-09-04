# Meta-Schema v14 Design Notes

## Purpose
Enhance v13 to better capture operationalization clarity and support multiple uncertainty dimensions that can be tracked separately or combined based on analytical needs.

## Key Enhancements from v13

### 1. Operationalization Clarity Metrics
**Rationale**: The schema should capture HOW CLEAR the theory's specifications are, not just what they specify.

**Implementation**:
```json
"operationalization_clarity": {
  "type": "object",
  "properties": {
    "construct_definitions": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "clarity_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "How unambiguously this construct is defined"
          },
          "definition_source": {
            "type": "string",
            "description": "Page/section where defined"
          },
          "measurement_guidance": {
            "type": "string",
            "enum": ["explicit", "implied", "absent"],
            "description": "Does theory specify how to measure?"
          },
          "ambiguity_notes": {
            "type": "string",
            "description": "What aspects remain unclear"
          }
        }
      }
    }
  }
}
```

**Example for Social Identity Theory**:
```json
"operationalization_clarity": {
  "construct_definitions": {
    "in_group": {
      "clarity_score": 0.95,
      "definition_source": "Tajfel & Turner 1979, p.40",
      "measurement_guidance": "implied",
      "ambiguity_notes": "Clear concept, but measurement method varies by context"
    },
    "identity_strength": {
      "clarity_score": 0.65,
      "definition_source": "Multiple papers with variations",
      "measurement_guidance": "absent",
      "ambiguity_notes": "Multiple scales exist (Mael & Ashforth 1992, Luhtanen & Crocker 1992)"
    }
  }
}
```

### 2. Alternative Interpretations (Lightweight Version)
**Rationale**: Track when constructs have multiple valid operationalizations without overcomplicating.

**Implementation**:
```json
"operationalization_variants": {
  "type": "object",
  "description": "When constructs have multiple valid interpretations",
  "additionalProperties": {
    "type": "object",
    "properties": {
      "has_variants": {"type": "boolean"},
      "variant_count": {"type": "integer"},
      "preferred_variant": {"type": "string"},
      "variant_notes": {"type": "string"}
    }
  }
}
```

**Example**:
```json
"operationalization_variants": {
  "group_identification": {
    "has_variants": true,
    "variant_count": 3,
    "preferred_variant": "network_communities",
    "variant_notes": "Can be: network communities, self-reported groups, or interaction clusters"
  }
}
```

### 3. Parameter Uncertainty Specification
**Rationale**: Formulas often have parameters where theory doesn't specify exact values.

**Current v13 Gap**: 
```json
// v13 just has:
"parameters": {
  "type": "object"  // No guidance on uncertainty
}
```

**v14 Enhancement**:
```json
"algorithms": {
  "mathematical": {
    "items": {
      "properties": {
        "parameters": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "default_value": {"type": "number"},
              "theoretical_range": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Theory-specified bounds if any"
              },
              "empirical_range": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Range from literature"
              },
              "sensitivity": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "How much results change with parameter"
              },
              "selection_guidance": {
                "type": "string",
                "description": "How to choose value"
              }
            }
          }
        }
      }
    }
  }
}
```

**Example for Community Detection**:
```json
"parameters": {
  "resolution": {
    "default_value": 1.0,
    "theoretical_range": null,  // Theory doesn't specify
    "empirical_range": [0.5, 2.0],  // From literature
    "sensitivity": "high",
    "selection_guidance": "Higher values create more, smaller communities. Test stability across range."
  },
  "threshold": {
    "default_value": 3,
    "theoretical_range": [3, 6],  // "Several interactions" per theory
    "empirical_range": [2, 10],
    "sensitivity": "medium",
    "selection_guidance": "Minimum interactions to establish group membership"
  }
}
```

### 4. Method Selection Guidance
**Clarification**: v13 allows specifying computational format (graph/table/vector) and some structure, but doesn't guide algorithm selection within that format.

**Current v13 Limitation**:
```json
// v13 says we need a graph with communities
"computational_representation": {
  "primary_format": "graph",
  "data_structure": {
    "graph_spec": {
      "directed": false,
      "weighted": true
      // But no guidance on HOW to find communities
    }
  }
}
```

**v14 Enhancement**:
```json
"method_selection": {
  "type": "object",
  "description": "Guidance for choosing computational methods",
  "properties": {
    "community_detection": {
      "type": "object",
      "properties": {
        "theory_requirements": {
          "type": "string",
          "description": "What the theory needs from communities"
        },
        "recommended_algorithms": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "algorithm": {"type": "string"},
              "suitability_score": {"type": "number"},
              "rationale": {"type": "string"},
              "limitations": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

**Example**:
```json
"method_selection": {
  "community_detection": {
    "theory_requirements": "Identify cohesive subgroups with strong internal ties and identity",
    "recommended_algorithms": [
      {
        "algorithm": "louvain",
        "suitability_score": 0.75,
        "rationale": "Good for finding communities at multiple scales",
        "limitations": "May miss overlapping group memberships"
      },
      {
        "algorithm": "label_propagation",
        "suitability_score": 0.60,
        "rationale": "Fast, captures natural boundaries",
        "limitations": "Non-deterministic, less stable"
      },
      {
        "algorithm": "sbm",
        "suitability_score": 0.85,
        "rationale": "Statistically principled, handles group structure well",
        "limitations": "Computationally expensive, requires parameter tuning"
      }
    ]
  }
}
```

## Multiple Uncertainty Dimensions

### Design Philosophy
Rather than combining uncertainties into a single measure, track multiple dimensions that can be reported separately or combined based on needs:

```python
class MultiDimensionalUncertainty:
    """Track uncertainties separately for different purposes"""
    
    def __init__(self):
        # Each dimension tracked independently
        self.dimensions = {
            # Type A: Theory-Question Fit (affects answer validity)
            "theory_question_fit": {
                "value": 0.85,
                "propagate": True,  # User choice
                "interpretation": "How well does selected theory address the question"
            },
            
            # Type B: Theory Application Fidelity (per paper)
            "theory_fidelity": {
                "value": 0.90,
                "propagate": True,
                "interpretation": "How well we applied theory as authors intended"
            },
            
            # Type C: Operationalization Quality (theory→computation)
            "operationalization": {
                "value": 0.72,
                "propagate": True,
                "interpretation": "How well computation captures theoretical constructs"
            },
            
            # Type D: Statistical/Data Uncertainty
            "statistical": {
                "value": 0.88,
                "propagate": True,
                "interpretation": "Data quality, sampling, measurement error"
            }
        }
    
    def get_combined(self, method="root_sum_squares"):
        """Combine selected dimensions when needed"""
        to_propagate = [d["value"] for d in self.dimensions.values() 
                       if d["propagate"]]
        if method == "root_sum_squares":
            uncertainties = [1 - v for v in to_propagate]
            variances = [u**2 for u in uncertainties]
            total_var = sum(variances)
            return 1 - math.sqrt(total_var)
    
    def get_interpretation_matrix(self):
        """Different combinations answer different questions"""
        return {
            "theory_fidelity_only": "How well did we implement what paper said?",
            "operationalization_only": "How well does computation match concepts?",
            "statistical_only": "Traditional confidence intervals",
            "theory_question + statistical": "Answer confidence for policy maker",
            "all_dimensions": "Complete uncertainty picture"
        }
```

## IC Methods During Tool Execution

### Integration Pattern
IC methods like ACH can be applied at tool execution time, not just theory selection:

```python
class ToolWithICAnalysis:
    def execute(self, request):
        # 1. Generate competing hypotheses for this specific analysis
        hypotheses = self.generate_local_hypotheses(request.data)
        # Example: "These are separate communities" vs "This is one community with factions"
        
        # 2. Build evidence matrix for this tool's decision
        evidence_matrix = self.build_ach_matrix(
            hypotheses=hypotheses,
            evidence=request.data
        )
        
        # 3. Assess assumptions for this specific operation
        assumptions = self.identify_assumptions()
        # Example: "Network structure reflects social structure"
        
        # 4. Execute primary analysis
        result = self.run_analysis(request)
        
        # 5. Store IC analysis in result metadata
        result.ic_metadata = {
            "competing_hypotheses": evidence_matrix,
            "critical_assumptions": assumptions,
            "sensitivity": self.test_sensitivity(result)
        }
        
        return result
```

## Uncertainty Propagation Through Complex DAGs

### The Challenge
How does uncertainty flow through a DAG like:
```
     A
    / \
   B   C
    \ / \
     D   E
      \ /
       F
```

### Propagation Patterns

```python
class DAGUncertaintyPropagation:
    """Handle uncertainty through complex tool chains"""
    
    def propagate_through_dag(self, dag, uncertainties):
        """Propagate uncertainties through DAG topology"""
        
        # Track uncertainty at each node
        node_uncertainties = {}
        
        for node in dag.topological_sort():
            if node.is_source():
                # Initial uncertainty
                node_uncertainties[node] = uncertainties[node]
            else:
                # Combine parent uncertainties
                parent_uncertainties = [
                    node_uncertainties[p] for p in node.parents
                ]
                
                # Different combination rules based on relationship
                if node.operation_type == "merge":
                    # When combining different views of same thing
                    combined = self.combine_correlated(parent_uncertainties)
                elif node.operation_type == "sequential":
                    # When one feeds into another
                    combined = self.propagate_sequential(parent_uncertainties)
                elif node.operation_type == "parallel":
                    # When independent analyses combine
                    combined = self.combine_independent(parent_uncertainties)
                
                # Add node's own uncertainty
                node_uncertainties[node] = self.add_local_uncertainty(
                    combined, node.local_uncertainty
                )
        
        return node_uncertainties
    
    def combine_correlated(self, uncertainties, correlation=0.5):
        """When uncertainties are correlated (shared data/methods)"""
        # Account for correlation in combination
        n = len(uncertainties)
        variances = [(1-u)**2 for u in uncertainties]
        
        # Correlation increases total uncertainty
        total_var = sum(variances)
        for i in range(n):
            for j in range(i+1, n):
                total_var += 2 * correlation * math.sqrt(variances[i] * variances[j])
        
        return 1 - math.sqrt(total_var/n)
    
    def propagate_sequential(self, uncertainties):
        """When one tool's output feeds next tool"""
        # Multiplicative degradation
        result = uncertainties[0]
        for u in uncertainties[1:]:
            result = result * u
        return result
    
    def combine_independent(self, uncertainties):
        """When tools analyze independently"""
        # Root-sum-squares for independent
        variances = [(1-u)**2 for u in uncertainties]
        return 1 - math.sqrt(sum(variances))
```

### Example DAG Propagation
```python
# Community Detection → Psychology Analysis → Language Analysis
#                    ↘                      ↗
#                      Network Analysis

dag_uncertainties = {
    "community_detection": {
        "theory_fidelity": 0.85,
        "operationalization": 0.70,
        "statistical": 0.90
    },
    # After community detection
    "psychology_analysis": {
        "inherits_from": "community_detection",
        "local_statistical": 0.95,  # Good ground truth
        "combined": propagate_sequential([0.85, 0.70, 0.90, 0.95])
    },
    # Parallel network analysis  
    "network_analysis": {
        "inherits_from": "community_detection",
        "local_operationalization": 0.80,
        "combined": propagate_sequential([0.85, 0.70, 0.90, 0.80])
    },
    # Merge psychology and network
    "language_analysis": {
        "inherits_from": ["psychology_analysis", "network_analysis"],
        "local_uncertainty": 0.75,
        "combined": combine_correlated([psych_combined, network_combined], correlation=0.6)
    }
}
```

## Recommendations for v14

1. **Add operationalization_clarity** - Essential for understanding theory ambiguity
2. **Lightweight variant tracking** - Just note existence, not full specifications
3. **Parameter uncertainty ranges** - Critical for reproducibility
4. **Method selection guidance** - Bridge theory requirements to algorithms
5. **Multi-dimensional uncertainty** - Track separately, combine as needed
6. **IC analysis at execution** - Not just theory selection
7. **DAG-aware propagation** - Handle complex tool chains properly

## Implementation Priority

1. **High Priority**: Operationalization clarity, parameter uncertainty
2. **Medium Priority**: Method selection guidance, multi-dimensional tracking
3. **Lower Priority**: Alternative interpretations, complex DAG patterns

The key insight is that different uncertainty combinations answer different questions, and all should be available rather than forcing a single combined measure.