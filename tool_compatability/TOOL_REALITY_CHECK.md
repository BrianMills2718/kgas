# KGAS Tool Reality Check

## The Actual Tool Situation

### What Really Exists (38 tools implemented)

#### Phase 1: Core Tools
**Loaders (T01-T14)** - All implemented as `unified` versions
- T01: PDF Loader
- T02: Word Loader  
- T03: Text Loader
- T04: Markdown Loader
- T05: CSV Loader
- T06: JSON Loader
- T07: HTML Loader
- T08: XML Loader
- T09: YAML Loader
- T10: Excel Loader
- T11: PowerPoint Loader
- T12: ZIP Loader
- T13: Web Scraper
- T14: Email Parser

**Processing Tools**
- T15A: Text Chunker (splits text into chunks)
- T15B: Vector Embedder (creates embeddings, stores in vector DB)
- T23A: spaCy NER (deprecated but exists)
- T23C: LLM Entity Extractor (just an alias to T23C ontology-aware)
- T27: Relationship Extractor
- T41: Async Text Embedder (async version of embedding)

**Graph Construction**
- T31: Entity Builder (creates Neo4j nodes from entities)
- T34: Edge Builder (creates Neo4j edges from relationships)

**Graph Operations**  
- T49: Multi-hop Query
- T68: PageRank
- T85: Twitter Explorer (?)

#### Phase 2: Advanced Tools (T50-T60, T23C)
- T23C: Ontology-Aware Extractor (the real implementation)
- T50: Community Detection/Graph Builder
- T51: Centrality Analysis
- T52: Graph Clustering
- T53: Network Motifs
- T54: Graph Visualization
- T55: Temporal Analysis
- T56: Graph Metrics
- T57: Path Analysis
- T58: Graph Comparison
- T59: Scale-Free Analysis
- T60: Graph Export

#### Phase 3: Advanced Tools
- T301: Multi-Document Fusion

### The Real Problems

## 1. Tool Factoring is Wrong

**Current (Bad):**
```
Text → T23C (extract entities + relationships) → entities
                                              ↓
                                         relationships
                                              ↓
entities → T31 (build nodes) → nodes
relationships → T34 (build edges) → edges
nodes + edges → somehow merge? → graph
```

**Should Be (Good):**
```
Text → T23_GRAPH_EXTRACTOR → Complete Graph in Neo4j
```

T31 and T34 should be internal to T23C, not separate tools!

## 2. Duplicate Functionality

- **T15B vs T41**: Both do embeddings, one is async
- **T23A vs T23C**: Both extract entities, deprecated vs current
- **Multiple loader versions**: standalone, unified, neo4j variants

## 3. Alias Hell

Many files are just compatibility shims:
- `t23c_llm_entity_extractor.py` → imports from `t23c_ontology_aware_extractor`
- `t31_entity_builder.py` → imports from `t31_entity_builder_unified`
- `t15a_text_chunker.py` → imports from `t15a_text_chunker_unified`

## 4. Tool Registry Problems

The architecture doc lists 121 tools but only ~38 exist. The hardcoded mappings in various files only know about 5-10 tools.

## 5. No Clear Pipeline Definition

With 38 tools, there should be maybe 5-10 standard pipelines:
1. **Document → Graph**: T01 → T15A → T23C (with T31/T34 inside) → Neo4j
2. **Document → Vectors**: T01 → T15A → T15B → Vector Store
3. **Graph → Analysis**: Neo4j → T68 (PageRank) → Results
4. **Graph → Query**: Neo4j → T49 (Multi-hop) → Answers
5. **Graph → Visualization**: Neo4j → T54 → Interactive Plot

## The Solution

### 1. Merge Tools That Always Run Together
- Merge T31 + T34 into T23C as internal operations
- Merge T15B + T41 into one embedding tool (with async option)

### 2. Simplify to Core Tools
```python
CORE_TOOLS = {
    # Loaders (pick format)
    "load_document": T01-T14 (based on file type),
    
    # Processing
    "chunk_text": T15A,
    "extract_graph": T23C (includes T31/T34 internally),
    "create_embeddings": T15B/T41 (unified),
    
    # Analysis  
    "analyze_graph": T50-T60 (various algorithms),
    "query_graph": T49,
    "visualize_graph": T54
}
```

### 3. Define Standard Pipelines
```python
PIPELINES = {
    "document_to_graph": ["load_document", "chunk_text", "extract_graph"],
    "document_to_vectors": ["load_document", "chunk_text", "create_embeddings"],
    "graph_analysis": ["analyze_graph", "visualize_graph"],
    "question_answering": ["load_document", "extract_graph", "query_graph"]
}
```

### 4. Fix Tool Discovery
Instead of hardcoded mappings, use actual tool discovery:
```python
def discover_tools():
    """Find all tools that implement the Tool protocol"""
    tool_modules = glob.glob("src/tools/**/*_unified.py")
    tools = {}
    for module_path in tool_modules:
        # Import and check if it implements Tool protocol
        # Register in tools dict
    return tools
```

## Next Steps

1. **Refactor T23C** to include T31/T34 functionality internally
2. **Unify embedders** (T15B and T41) into one tool
3. **Remove aliases** and point everything to the real implementations
4. **Create pipeline definitions** instead of letting users figure out tool chains
5. **Implement tool discovery** instead of hardcoded mappings

## The Bottom Line

You have ~38 tools when you need maybe 10-15 core operations. The issue isn't finding compatible tools - it's that the tools are factored at the wrong level of abstraction. Instead of "extract entities" and "build nodes" as separate tools, you should have "build graph from text" as one operation.