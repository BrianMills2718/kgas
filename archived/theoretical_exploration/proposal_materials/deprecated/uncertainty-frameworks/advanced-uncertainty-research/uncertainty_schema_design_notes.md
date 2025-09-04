# Uncertainty and Schema Design Notes

## Critical Distinctions to Maintain

### 1. Workflow Template vs DAG Specification

**Workflow Template Schema**
- Abstract, reusable pattern
- Example: "Extract entities → Build graph → Find communities → Analyze"
- Not tied to specific tools or data
- Like a recipe template: "Mix dry ingredients, add wet ingredients, bake"

**DAG Specification Schema**
- Concrete instance ready for execution
- Example: "T23A_SPACY_NER on doc_001.txt → T31_ENTITY_BUILDER with threshold=0.8 → Louvain with resolution=1.0 → Statistical analysis"
- Specific tools, parameters, data references
- Like a recipe with amounts: "2 cups flour, 1 egg, bake at 350°F for 30 min"

```json
// Workflow Template
{
  "template_id": "theory_guided_discourse_analysis",
  "abstract_steps": [
    {"step": "extract_theoretical_constructs", "modality": "any"},
    {"step": "identify_groups", "modality": "graph"},
    {"step": "measure_properties", "modality": "table"}
  ]
}

// DAG Specification (instance of template)
{
  "dag_id": "sit_covid_analysis_2025_001",
  "concrete_steps": [
    {"tool": "T23A_SPACY_NER", "input": "covid_tweets.json", "params": {"model": "en_core_web_lg"}},
    {"tool": "T31_ENTITY_BUILDER", "input": "$step1.output", "params": {"threshold": 0.8}},
    {"tool": "Louvain", "input": "$step2.output", "params": {"resolution": 1.0}}
  ]
}
```

### 2. Database-Aligned Data Schemas

**Principle**: Align schemas with our two databases rather than creating abstract types

**Neo4j (Graph + Vector)**
```python
# Everything in Neo4j is a node or edge
class Neo4jNode:
    """Base for all graph entities"""
    id: str
    labels: List[str]  # Could be ["Entity", "Person", "Community"]
    properties: Dict
    embedding: Optional[Vector]  # Native vector support

class Neo4jEdge:
    """Base for all relationships"""
    source_id: str
    target_id: str
    type: str
    properties: Dict
    
# A "Community" is just a node with label "Community" and member edges
# Not a separate schema!
```

**SQLite (Relational + Metadata)**
```python
class SQLiteRecord:
    """Base for all relational data"""
    table_name: str
    data: Dict  # JSON column for flexibility
    metadata: Dict
    created_at: datetime
    
# Statistical results are records in 'statistical_results' table
# Provenance are records in 'provenance' table
# Not separate schema types!
```

**Key Insight**: Communities, statistical results, etc. aren't separate schemas - they're instances of our base database schemas with different labels/tables.

### 3. Statistical Results as Metadata

Statistical results are fundamentally different from entities/relationships:
- Entities/relationships = data
- Statistical results = metadata about data

```python
# Data (goes in Neo4j)
entity = {"id": "user_123", "type": "Person", "properties": {...}}

# Metadata about data (goes in SQLite)
statistical_result = {
    "analysis_type": "correlation",
    "data_refs": ["user_123", "user_456"],  # References to Neo4j
    "value": 0.67,
    "p_value": 0.001,
    "confidence_interval": [0.55, 0.79]
}
```

### 4. Cross-Modal Schema Examples

Cross-modal schemas define transformations between representations:

```json
// Graph → Table Transformation Schema
{
  "transformation_id": "graph_to_table_001",
  "source_format": "graph",
  "target_format": "table",
  "method": "adjacency_matrix",
  "preserves": ["nodes", "edge_weights"],
  "loses": ["edge_attributes", "node_positions"],
  "parameters": {
    "include_self_loops": false,
    "weight_attribute": "strength"
  }
}

// Table → Vector Transformation Schema  
{
  "transformation_id": "table_to_vector_001",
  "source_format": "table",
  "target_format": "vector",
  "method": "tfidf_embedding",
  "preserves": ["term_frequency"],
  "loses": ["column_relationships", "row_order"],
  "parameters": {
    "max_features": 1000,
    "norm": "l2"
  }
}
```

### 5. Provenance Schema Status

**TODO**: Check if PROVENANCE.md defines a schema or just requirements

Based on PROVENANCE.md, we need:
```python
class ProvenanceSchema:
    # Core tracking
    activity_id: str
    tool_id: str
    timestamp: datetime
    
    # Inputs/Outputs
    input_refs: List[str]  # References to data
    output_refs: List[str]
    
    # Uncertainty tracking
    uncertainty_propagation: Dict  # How uncertainty changed
    
    # IC Analysis
    assumptions_tested: List[Dict]
    alternatives_considered: List[str]
    
    # Transformation lineage
    format_conversions: List[Dict]
```

### 6. Configuration vs Algorithm Parameters

These ARE distinct:

**System Configuration** (global, stable)
```json
{
  "neo4j_url": "bolt://localhost:7687",
  "max_memory": "8GB",
  "parallel_workers": 4,
  "api_keys": {...}
}
```

**Algorithm Parameters** (per-execution, varies)
```json
{
  "louvain_resolution": 1.0,  // Might change per analysis
  "entity_threshold": 0.8,     // Might vary by data quality
  "chunk_size": 500            // Might vary by document type
}
```

## Critical Uncertainty Distinctions

### The Fidelity Hierarchy

We need to track MULTIPLE types of fidelity:

1. **Paper Fidelity**: Did we implement what the paper says?
   - "Paper says use Louvain" → We use Louvain → 100% paper fidelity
   
2. **Theory Fidelity**: Does what the paper says match what theory intends?
   - Theory: "identify cohesive groups"
   - Paper: "use Louvain"
   - Fidelity depends on whether Louvain finds theoretical groups

3. **Construct Validity**: Does the method capture the construct?
   - Construct: "group identity"
   - Method: "network communities"
   - Validity: Do network communities = identity groups?

4. **Implementation Fidelity**: Did we execute the method correctly?
   - Method: "Louvain with resolution=1.0"
   - Execution: Ran successfully with those parameters
   - Fidelity: 100% if no bugs

```python
class MultilevelFidelity:
    paper_fidelity: float      # Did we do what paper said?
    theory_fidelity: float     # Does paper match theory intent?
    construct_validity: float  # Does method capture construct?
    implementation_fidelity: float  # Did we execute correctly?
    
    def get_appropriate_fidelity(self, audience):
        if audience == "replication_researcher":
            return self.paper_fidelity  # They care about reproducing paper
        elif audience == "theorist":
            return self.theory_fidelity  # They care about theory intent
        elif audience == "methodologist":
            return self.construct_validity  # They care about measurement
        elif audience == "engineer":
            return self.implementation_fidelity  # They care about bugs
```

### The Belief/Statement Problem

You're absolutely right - someone's statement doesn't equal their belief:

```python
class StatementAnalysis:
    statement: str  # "Vaccines are dangerous"
    
    # Multiple interpretations
    literal_meaning: str  # Face value of words
    
    # Possible actual meanings
    sincere_belief: float  # Probability they believe it
    sarcasm_probability: float  # Probability of sarcasm
    strategic_messaging: float  # Probability of strategic speech
    social_signaling: float  # Probability of group signaling
    
    # How to determine?
    context_clues: List[str]  # Emoji, punctuation, history
    discourse_markers: List[str]  # "Obviously", "Everyone knows"
    consistency_check: float  # Matches other statements?
    
    def get_best_interpretation(self):
        # This is where IC methods help!
        # ACH: Sincere vs Sarcastic vs Strategic
        # Evidence: Context, consistency, markers
        pass
```

## Recommended Path Forward

### Phase 1: Core Schema Consolidation
1. Define base Neo4j node/edge schemas
2. Define base SQLite record schema
3. Map all data types to these bases

### Phase 2: Uncertainty Framework
1. Define multilevel fidelity tracking
2. Create provenance schema with uncertainty
3. Design IC analysis integration points

### Phase 3: Transformation Schemas
1. Define cross-modal transformation schemas
2. Specify information preservation/loss
3. Create uncertainty propagation rules

### Critical Decisions Needed

1. **How many fidelity levels to track?**
   - All 4 (paper, theory, construct, implementation)?
   - Or simplified (intended vs actual)?

2. **How to handle belief ambiguity?**
   - Always flag uncertainty?
   - Use IC methods at extraction?
   - Carry multiple interpretations?

3. **Where to store what?**
   - Entities/relationships → Neo4j
   - Statistics/provenance → SQLite
   - Uncertainty → Both? (operational in SQLite, semantic in Neo4j?)

## Open Questions

1. Should transformation schemas be stored or computed?
2. How much IC analysis should be mandatory vs optional?
3. Can we automate fidelity assessment or needs human review?
4. Should schemas version themselves for evolution?

## Schema Inventory Status

### Priority 1 (Figure out now)
- [ ] Provenance Schema - Check existing, define if needed
- [ ] Uncertainty Schema - Multiple dimensions design
- [ ] Base database schemas - Neo4j node/edge, SQLite record

### Priority 2 (Needed for implementation)
- [ ] Tool execution schema with uncertainty
- [ ] Transformation schemas for cross-modal
- [ ] DAG execution with uncertainty propagation

### Priority 3 (Can defer)
- [ ] Validation schemas (noted but deferred)
- [ ] Visualization schemas
- [ ] Export schemas

## Next Steps

1. Review existing provenance specification
2. Design multilevel fidelity schema
3. Create base database schemas
4. Build uncertainty propagation framework
5. Test with vaccine hesitancy example