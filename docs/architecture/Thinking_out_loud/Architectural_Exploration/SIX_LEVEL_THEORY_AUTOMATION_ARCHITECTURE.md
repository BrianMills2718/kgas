# Four-Pattern Theory Automation Architecture

**Date**: 2025-08-07 (Updated from Six-Level)  
**Status**: Architecture Refined, Patterns 1-2 Implemented  
**Type**: Target Architecture Design  
**Related**: [Theory-to-Code Workflow](THEORY_TO_CODE_WORKFLOW.md), [ADR-022](adrs/ADR-022-Theory-Selection-Architecture.md)

## Overview

This document defines the **target architecture** for automating social science theories through a four-pattern categorization system. Each pattern has clear boundaries and distinct computational approaches to handle the diversity of theoretical content.

## Architectural Vision

### Core Problem
Social science theories contain diverse operational components that cannot be handled by a single computational approach:
- **Mathematical formulas** require function execution
- **Logical rules** require reasoning engines  
- **Sequential processes** require state machines
- **Classification schemes** require decision trees
- **Decision procedures** require workflow systems
- **Computational algorithms** require iterative processing

### Solution: Four-Pattern Architecture
The system categorizes theoretical components into four distinct patterns, each with specialized implementation approaches and clear boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                    Theory Input (V13 Schema)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Component Detection & Routing                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ EXPRESSIONS │ ALGORITHMS  │  PROCESSES  │    RULES    │  │
│  │   (Direct)  │ (Iterative) │   (State)   │  (Logical)  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Specialized Implementation Engines             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Python    │  Algorithm  │   State     │  OWL2 DL    │  │
│  │ Functions   │   Classes   │  Machines   │ Reasoning   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Unified Results                          │
└─────────────────────────────────────────────────────────────┘
```

## Pattern Definitions

### Pattern 1: EXPRESSIONS
**Purpose**: Direct mathematical relationships without iteration  
**Input**: Mathematical formulas from theory  
**Output**: Python executable functions  
**Implementation**: Direct evaluation with parameter mapping  
**Boundary**: Single expression that evaluates directly  
**Status**: **FULLY IMPLEMENTED**

**Example**:
```python
# From: influence = attention × retention × reproduction × motivation
def social_learning_influence(attention, retention, reproduction, motivation):
    return attention * retention * reproduction * motivation
```

### Pattern 2: ALGORITHMS  
**Purpose**: Iterative computational methods requiring loops  
**Input**: Algorithmic descriptions from theory  
**Output**: Python algorithmic classes with convergence logic  
**Implementation**: Algorithm class generation with iteration control  
**Boundary**: Requires loops/iteration to reach result  
**Status**: **PARTIALLY IMPLEMENTED**

**Example**:
```python
# From: PageRank-style influence propagation
class SocialInfluenceCalculator:
    def __init__(self, damping=0.85, tolerance=1e-6):
        self.damping = damping
        self.tolerance = tolerance
    
    def calculate_influence(self, social_graph):
        # Iterative calculation with convergence
        while not converged and iterations < max_iter:
            new_scores = self.propagate(scores, graph)
            converged = self.check_convergence(scores, new_scores)
            scores = new_scores
        return scores
```

### Pattern 3: PROCESSES
**Purpose**: State-based workflows with transitions  
**Input**: Sequential procedures and decision trees from theory  
**Output**: State machine classes with workflow management  
**Implementation**: State machine generation with transition logic  
**Boundary**: Has explicit states and transitions between them  
**Status**: **PARTIALLY IMPLEMENTED**

**Example**:
```python
# From: Transtheoretical Model stages
class BehaviorChangeProcess:
    def execute(self, context):
        state = "precontemplation"
        while state != "maintenance":
            if state == "precontemplation":
                if self.awareness_raised(context):
                    state = "contemplation"
            elif state == "contemplation":
                if self.pros_outweigh_cons(context):
                    state = "preparation"
            elif state == "preparation":
                if self.action_plan_ready(context):
                    state = "action"
            elif state == "action":
                if self.sustained_behavior(context):
                    state = "maintenance"
        return state
```

### Pattern 4: RULES
**Purpose**: Logical inference and conditional reasoning  
**Input**: If-then statements and logical conditions  
**Output**: OWL2 DL ontologies with SWRL rules  
**Implementation**: Logic engine with inference capabilities  
**Boundary**: Declarative logic, not procedural steps  
**Status**: **ARCHITECTURE DEFINED**

**Example**:
```python
# From: Social Identity Theory
# IF same_group(X,Y) AND threat_present THEN in_group_bias(X,Y)
with onto:
    class SocialActor(Thing): pass
    class Group(Thing): pass
    
    # SWRL rule
    imp = Imp()
    imp.set_as_rule([
        "SocialActor(?x), SocialActor(?y), belongsToGroup(?x, ?g), "
        "belongsToGroup(?y, ?g), threatPresent() -> exhibitsBias(?x, ?y, 'positive')"
    ])
```

## Implementation Architecture

### Component Detection System
```python
def detect_operational_components(v13_theory):
    """Route theory components to appropriate implementation engines"""
    components = {
        "expressions": [],   # → Python function generator
        "algorithms": [],    # → Algorithm class generator  
        "processes": [],     # → State machine generator
        "rules": []          # → OWL2 ontology generator
    }
    
    # Extract from V13 algorithms section
    if "algorithms" in v13_theory:
        if "mathematical" in v13_theory["algorithms"]:
            components["expressions"].extend(
                v13_theory["algorithms"]["mathematical"]
            )
        if "logical" in v13_theory["algorithms"]:
            components["rules"].extend(
                v13_theory["algorithms"]["logical"]
            )
        if "procedural" in v13_theory["algorithms"]:
            # Determine if it's iterative (algorithm) or state-based (process)
            for proc in v13_theory["algorithms"]["procedural"]:
                if "convergence" in proc or "iteration" in proc:
                    components["algorithms"].append(proc)
                else:
                    components["processes"].append(proc)
    
    return components
```

### Implementation Strategy Mapping
```python
IMPLEMENTATION_STRATEGIES = {
    "EXPRESSIONS": {
        "generator": DirectFunctionGenerator,
        "validator": MathematicalValidator,
        "executor": PythonFunctionExecutor,
        "format": "python_function",
        "characteristics": "Direct evaluation, no loops"
    },
    "ALGORITHMS": {
        "generator": AlgorithmClassGenerator,
        "validator": ConvergenceValidator,
        "executor": AlgorithmExecutor,
        "format": "python_class",
        "characteristics": "Iterative, convergence criteria"
    },
    "PROCESSES": {
        "generator": StateMachineGenerator,
        "validator": WorkflowValidator,
        "executor": ProcessExecutor,
        "format": "state_machine",
        "characteristics": "State transitions, decision points"
    },
    "RULES": {
        "generator": OWL2OntologyGenerator,
        "validator": DLReasonerValidator,
        "executor": InferenceExecutor,
        "format": "owlready2_ontology",
        "characteristics": "Logical inference, declarative"
    }
}
```

## Integration Architecture

### Unified Execution Interface
```python
class TheoryComponentExecutor:
    """Unified interface for executing all theory component types"""
    
    def __init__(self):
        self.executors = {
            "formulas": PythonFunctionExecutor(),
            "algorithms": AlgorithmExecutor(),
            "procedures": ProcedureExecutor(),
            "rules": OntologyExecutor(),
            "sequences": SequenceExecutor(),
            "frameworks": ClassifierExecutor()
        }
    
    def execute_component(self, component_type, component, inputs):
        executor = self.executors[component_type]
        return executor.execute(component, inputs)
```

### Component Validation Framework
```python
class ComponentValidator:
    """Ensures generated components meet quality standards"""
    
    def validate_formula(self, function_code, test_cases):
        """Validate mathematical function accuracy"""
        pass
    
    def validate_algorithm(self, algorithm_class, convergence_tests):
        """Validate algorithm convergence and correctness"""
        pass
    
    def validate_procedure(self, state_machine, workflow_tests):
        """Validate workflow execution and state transitions"""
        pass
    
    def validate_rules(self, ontology, reasoning_tests):
        """Validate logical reasoning and inference"""
        pass
    
    def validate_sequence(self, transition_system, sequence_tests):
        """Validate temporal progression logic"""
        pass
    
    def validate_framework(self, classifier, classification_tests):
        """Validate classification accuracy and consistency"""
        pass
```

## Technical Requirements

### Core Dependencies
- **Python 3.8+**: Foundation for all implementations
- **litellm**: LLM integration for code generation
- **owlready2**: OWL2 DL reasoning (for Level 4)
- **scikit-learn**: Classification frameworks (for Level 6)
- **networkx**: Algorithm implementations (for Level 2)

### Level-Specific Requirements
```python
LEVEL_REQUIREMENTS = {
    "FORMULAS": ["ast", "exec", "numpy"],
    "ALGORITHMS": ["networkx", "scipy", "convergence_metrics"],
    "PROCEDURES": ["statemachine", "workflow_engine"],
    "RULES": ["owlready2", "pellet_reasoner", "rdflib"],
    "SEQUENCES": ["transitions", "temporal_logic"],
    "FRAMEWORKS": ["scikit-learn", "decision_trees", "feature_extraction"]
}
```

## Implementation Phases

### Phase 1: Foundation (COMPLETE)
- Level 1 (FORMULAS) fully implemented
- Component detection architecture
- V12 meta-schema integration
- LLM code generation pipeline

### Phase 2: Core Expansion (NEXT)
**Priority Order**:
1. **Level 2 (ALGORITHMS)** - Most similar to existing implementation
2. **Level 3 (PROCEDURES)** - Builds on state management concepts
3. **Level 6 (FRAMEWORKS)** - Leverages existing ML infrastructure

### Phase 3: Advanced Systems
4. **Level 5 (SEQUENCES)** - Requires temporal logic framework
5. **Level 4 (RULES)** - Requires owlready2 installation and ontology expertise

## Quality Assurance

### Testing Strategy
Each level requires specialized testing approaches:

```python
TESTING_STRATEGIES = {
    "FORMULAS": "mathematical_accuracy_tests",
    "ALGORITHMS": "convergence_and_performance_tests", 
    "PROCEDURES": "workflow_execution_tests",
    "RULES": "logical_reasoning_tests",
    "SEQUENCES": "temporal_progression_tests",
    "FRAMEWORKS": "classification_accuracy_tests"
}
```

### Validation Criteria
- **Correctness**: All implementations must produce theoretically valid results
- **Performance**: Execution within reasonable time bounds for academic use
- **Robustness**: Graceful handling of edge cases and invalid inputs
- **Consistency**: Results must be reproducible across multiple runs

## Future Extensions

### Multi-Theory Integration
- **Theory Composition**: Combine multiple theories in single analysis
- **Cross-Theory Validation**: Identify theoretical conflicts and contradictions
- **Theory Libraries**: Pre-compiled theory components for rapid deployment

### Advanced Automation
- **Auto-Categorization**: Automatic detection of component types from natural language
- **Optimization**: Performance optimization for computationally intensive theories
- **Visualization**: Visual representation of theory execution flows

## Success Metrics

### Implementation Metrics
- **Coverage**: Percentage of social science theories automatable (target: 80%+)
- **Accuracy**: Correctness of theoretical implementations (target: 95%+)
- **Performance**: Execution time for typical analyses (target: <10 minutes)

### Research Impact Metrics  
- **Adoption**: Number of researchers using automated theories
- **Publications**: Academic papers enabled by automation
- **Reproducibility**: Percentage of results independently verified

---

**Status Summary**: The six-level architecture provides a comprehensive framework for automating diverse social science theories. Level 1 is fully operational, demonstrating the viability of the approach. Levels 2-6 have complete architectural designs ready for implementation.

**Next Steps**: Implement Level 2 (ALGORITHMS) as the next priority, leveraging existing infrastructure and building toward comprehensive theory automation capability.