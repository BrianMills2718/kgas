# Theory Meta-Schema Specification
*Extracted from proposal materials - 2025-08-29*
*Status: Future Implementation - Phase 2 (Theory-Specific Tools)*

## Overview

The Theory Meta-Schema v13 defines the structured format for extracting and representing academic theories in machine-readable form. This specification supports the **feasibility demonstration** of automated theory operationalization - proving that LLM systems can systematically convert academic theories into executable computational analysis.

**Architectural Purpose**: Enable dynamic tool generation from theory schemas, supporting Phase 2 of KGAS development (theory-specific tools) after Phase 1 demonstrates generalist tool functionality.

## Schema Architecture

### **Core Components**
The v13 schema structures theories through four primary layers:

1. **Metadata Layer** - Bibliographic information, provenance, and validity evidence
2. **Theoretical Structure** - Entities, relations, and logical constraints  
3. **Computational Representation** - Data structures and format specifications
4. **Algorithms Layer** - Mathematical formulas, logical rules, and procedures

### **Feasibility Focus**
This schema prioritizes **architectural feasibility** over optimization:
- **Goal**: Demonstrate that theories CAN be extracted and operationalized
- **Success Criteria**: End-to-end functionality from paper → schema → executable analysis
- **Performance**: Assumes future LLM improvements will enhance accuracy within this architecture

## Theory Meta-Schema v13.0 Specification

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Theory Meta-Schema v13.0",
  "description": "Value-driven meta-schema focusing on two-layer architecture with added theory validity evidence tracking",
  "version": "13.0",
  "type": "object",
  "required": [
    "theory_id",
    "theory_name", 
    "version",
    "metadata",
    "theoretical_structure",
    "computational_representation", 
    "algorithms",
    "telos",
    "theory_validity_evidence"
  ]
}
```

### **Key Schema Sections**

#### **1. Theory Identity**
```json
"theory_id": {
  "type": "string", 
  "pattern": "^[a-z_][a-z0-9_]*$",
  "description": "Unique identifier for the theory"
},
"theory_name": {
  "type": "string",
  "description": "Human-readable name of the theory"
}
```

#### **2. Metadata Layer**
Comprehensive bibliographic and provenance information including:
- **Authors and Citations**: Full bibliographic references
- **Theoretical Provenance**: How theory relates to other theories (extends, replaces, synthesizes, contradicts)
- **Scope Definition**: Phenomena explained, boundary conditions, level of analysis

#### **3. Theory Validity Evidence**
Structured evidence supporting theory credibility:
- **Empirical Support**: Supporting/contradicting studies, meta-analyses
- **Citation Metrics**: Total citations, field-normalized scores, h-index data
- **Replication Status**: Direct/conceptual replications with success rates
- **Practical Applications**: Real-world interventions and policy influence
- **Validity Assessment**: Internal, external, construct, and predictive validity ratings

#### **4. Theoretical Structure**
Core theoretical components extracted from papers:

**Entities** - Theoretical concepts with:
- Indigenous names (exact author terminology)
- Standardized names for cross-theory comparison
- Properties and measurement specifications
- Constraints and examples from source text

**Relations** - Connections between entities with:
- Directional relationships and properties
- Logical constraints (symmetric, transitive, etc.)
- Indigenous terminology preservation

**Modifiers** - Qualifiers that condition entities/relations:
- Temporal, modal, certainty, normative, contextual categories

#### **5. Computational Representation**
Data structure specifications for theory implementation:

```json
"primary_format": {
  "enum": ["graph", "table", "matrix", "vector", "tree", "sequence", "hypergraph"]
},
"data_structure": {
  "graph_spec": {
    "directed": boolean,
    "weighted": boolean,
    "node_types": array,
    "edge_types": array
  },
  "table_spec": {
    "entity_tables": array,
    "relation_tables": array
  }
}
```

**Projections**: Alternative representations for specific computations, enabling cross-modal analysis.

#### **6. Algorithms Layer**  
Executable components extracted from theories:

**Mathematical Algorithms**:
- Formulas with LaTeX representation
- Parameter specifications and computational complexity
- Implementation guidance

**Logical Rules**:
- If-then rules with logic notation
- Implementation types (forward/backward chaining, constraint satisfaction)

**Procedural Steps**:
- Sequential processes from theory
- Data requirements and outputs

#### **7. Telos (Purpose)**
What the theory is for and what questions it answers:
- **Analytical Questions**: Descriptive, explanatory, predictive, prescriptive, evaluative
- **Success Criteria**: How to validate successful theory application
- **Value Propositions**: What the theory provides for different research questions

#### **8. Extraction and Validation**
Automated processes for theory extraction:
- **Entity/Relation Extraction**: LLM-guided, pattern matching, hybrid methods
- **Structural Tests**: Constraint validation and logical consistency checks
- **Empirical Tests**: Validation against paper claims with expected/actual results

## Implementation Phases

### **Phase 1: Generalist Tools (Current)**
- Schema serves as specification document
- Manual theory application using pre-built tools
- Focus on architectural feasibility demonstration

### **Phase 2: Theory-Specific Tools (Future)**  
- Automated schema extraction from academic papers
- Dynamic tool generation from schema algorithms
- LLM-driven theory operationalization
- End-to-end theory automation pipeline

## Usage in KGAS Architecture

### **Current Role (Phase 1)**
- **Documentation**: Specification for future capability
- **Planning**: Architectural foundation for Phase 2 development
- **Validation**: Framework for testing theory extraction feasibility

### **Future Role (Phase 2)**
- **Input Format**: LLMs extract theories into v13 format
- **Tool Generation**: Schema algorithms become executable Python tools  
- **Validation Framework**: Automated theory application assessment
- **Cross-Modal Integration**: Theory-guided data format selection

## Success Criteria

### **Feasibility Demonstration** 
- **Technical**: Can academic theories be extracted into structured format?
- **Computational**: Can schemas generate executable analysis tools?
- **Architectural**: Does the v13 structure support diverse theory types?

### **Not Required for Success**
- **Perfect Extraction**: 100% accuracy not needed for feasibility proof
- **Production Performance**: Optimization assumed for future LLM improvements  
- **Complete Automation**: Manual validation acceptable for architectural demonstration

## Schema File Location

**Complete Schema**: Available as JSON Schema at:
`/docs/architecture/specifications/theory_meta_schema_v13.json`

**Size**: 1,108 lines of comprehensive JSON Schema specification
**Coverage**: Supports mathematical, logical, and procedural theory components
**Validation**: Built-in structural and empirical testing frameworks

---

## Future Enhancements (v14+)

Planning documents identify potential v14 enhancements:
- **Operationalization Clarity Metrics**: How unambiguous theory specifications are
- **Parameter Uncertainty Ranges**: Theoretical vs empirical parameter bounds  
- **Method Selection Guidance**: Algorithm recommendations for theory requirements
- **Multi-Dimensional Uncertainty**: Separate uncertainty tracking for different aspects

**Focus**: Current v13 schema sufficient for feasibility demonstration; enhancements for production optimization.

---

**Status**: Ready for Phase 2 implementation when Phase 1 demonstrates architectural feasibility
**Next Steps**: Use v13 as specification during generalist tool development, implement extraction pipeline when moving to theory-specific tools