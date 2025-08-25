# Tool Disposition Plan for ORM Implementation

## Overview
From 38 existing tools, we'll create ~15 operators covering diverse capabilities to ensure the ORM approach doesn't lock us out of future needs.

## Tool Categories and Disposition

### 1. 📥 **Data Ingestion** (14 tools → 1 operator)

#### Current Tools (T01-T14)
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
- T12: ZIP Extractor
- T13: Web Scraper
- T14: Email Parser

#### **Decision: MERGE into T01_UniversalLoader**
```python
# Single operator with format detection
T01_UniversalLoader:
  inputs: ["file_path" | "url" | "email_source"]
  outputs: ["text_content", "metadata", "structured_data"]
  
# Internally dispatches to appropriate loader
# Preserves all 14 capabilities
```

**Rationale**: All do same thing (file → content), just different formats

---

### 2. 🔪 **Text Processing** (2 tools → 2 operators)

#### Current Tools
- T15A: Text Chunker
- T15B: Vector Embedder

#### **Decision: KEEP SEPARATE**
```python
T15_Chunker:
  inputs: ["text_content"]
  outputs: ["text_segments", "chunk_metadata"]

T41_Embedder:  # Merge T15B + T41
  inputs: ["text_content" | "text_segments"]
  outputs: ["vector_embeddings"]
```

**Rationale**: Chunking and embedding are orthogonal concerns; keeping separate allows flexibility

---

### 3. 🔍 **Entity & Relationship Extraction** (5 tools → 1 operator)

#### Current Tools
- T23A: spaCy NER (deprecated)
- T23C: LLM Entity Extractor
- T27: Relationship Extractor
- T31: Entity Builder (Neo4j nodes)
- T34: Edge Builder (Neo4j edges)

#### **Decision: MERGE into T23_GraphExtractor**
```python
T23_GraphExtractor:
  inputs: ["text_content", "ontology?"]
  outputs: ["named_entities", "relationships", "graph_structure"]
  
# Internally orchestrates:
# 1. Entity extraction (T23C)
# 2. Relationship extraction (T27)
# 3. Node creation (T31)
# 4. Edge creation (T34)
# 5. Graph persistence
```

**Rationale**: These always run together; T31/T34 shouldn't be separate

---

### 4. 📊 **Graph Analysis** (13 tools → 8 operators)

#### Current Tools (Phase 2)
- T49: Multi-hop Query
- T50: Community Detection
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
- T68: PageRank

#### **Decision: KEEP MOST as SEPARATE OPERATORS**
```python
# Core graph operations (KEEP)
T49_Query:
  inputs: ["graph_structure", "query_spec"]
  outputs: ["query_results", "subgraph"]

T68_PageRank:
  inputs: ["graph_structure", "damping_factor?"]
  outputs: ["node_scores", "ranked_nodes"]

T50_Community:
  inputs: ["graph_structure", "algorithm?"]
  outputs: ["communities", "modularity_score"]

T51_Centrality:
  inputs: ["graph_structure", "centrality_type"]
  outputs: ["node_centralities", "central_nodes"]

# Merge similar analyses
T56_GraphMetrics:  # Merge T56 + T59
  inputs: ["graph_structure"]
  outputs: ["graph_statistics", "scale_properties"]

T57_PathAnalysis:  # Merge T57 + T53
  inputs: ["graph_structure", "source?", "target?"]
  outputs: ["paths", "motifs", "patterns"]

# Visualization and export
T54_Visualizer:
  inputs: ["graph_structure", "layout?"]
  outputs: ["visualization", "rendered_graph"]

T60_Exporter:
  inputs: ["graph_structure", "format"]
  outputs: ["exported_data"]
```

**Rationale**: Each provides distinct analytical capability; merging would reduce flexibility

---

### 5. 🔀 **Multi-Document Operations** (1 tool → 1 operator)

#### Current Tool
- T301: Multi-Document Fusion

#### **Decision: KEEP & EXPAND**
```python
T301_Fusion:
  inputs: ["graph_structures[]", "fusion_strategy"]
  outputs: ["merged_graph", "conflict_report", "fusion_metadata"]
```

**Rationale**: Critical for multi-document workflows

---

### 6. 🌍 **External Data** (1 tool → 1 operator)

#### Current Tool
- T85: Twitter Explorer

#### **Decision: GENERALIZE**
```python
T85_SocialExplorer:  # Generalize beyond Twitter
  inputs: ["social_source", "query_params"]
  outputs: ["social_graph", "social_entities", "temporal_data"]
```

**Rationale**: Keep to ensure external data capability

---

### 7. ⏱️ **Temporal Analysis** (1 tool → defer)

#### Current Tool
- T55: Temporal Analysis

#### **Decision: DEFER to Phase 2**
**Rationale**: Important but not core to initial validation

---

### 8. 🔬 **Comparison** (1 tool → defer)

#### Current Tool  
- T58: Graph Comparison

#### **Decision: DEFER to Phase 2**
**Rationale**: Advanced feature, not needed for core pipelines

---

### 9. **Clustering** (1 tool → defer)

#### Current Tool
- T52: Graph Clustering

#### **Decision: DEFER to Phase 2**
**Rationale**: Can be added once core graph ops work

---

## Initial Operator Set (15 operators)

### Phase 1 Core Set (10 operators)
1. **T01_UniversalLoader** - All ingestion capabilities
2. **T15_Chunker** - Text segmentation
3. **T41_Embedder** - Vector creation
4. **T23_GraphExtractor** - Entity/relationship/graph creation
5. **T49_Query** - Graph querying
6. **T68_PageRank** - Importance scoring
7. **T50_Community** - Community detection
8. **T51_Centrality** - Centrality analysis
9. **T54_Visualizer** - Graph visualization
10. **T301_Fusion** - Multi-document merging

### Phase 1.5 Extensions (5 operators)
11. **T56_GraphMetrics** - Statistics and scale analysis
12. **T57_PathAnalysis** - Paths and motifs
13. **T60_Exporter** - Data export
14. **T85_SocialExplorer** - External data
15. **T15_TextProcessor** - Advanced text operations (if needed)

## Capability Coverage Check

### ✅ **Data Types Covered**
- Documents (PDF, Word, etc.) ✓
- Structured data (JSON, CSV, Excel) ✓
- Web data (HTML, scraping) ✓
- Social data (Twitter/external) ✓
- Multi-modal (text + metadata) ✓

### ✅ **Processing Capabilities**
- Text processing (chunking) ✓
- Entity extraction ✓
- Relationship extraction ✓
- Vector embeddings ✓
- Graph construction ✓

### ✅ **Analysis Capabilities**
- Graph queries ✓
- Importance scoring ✓
- Community detection ✓
- Centrality analysis ✓
- Path analysis ✓
- Statistical metrics ✓
- Visualization ✓

### ✅ **Advanced Operations**
- Multi-document fusion ✓
- External data integration ✓
- Data export ✓

### ⏳ **Deferred but Not Lost**
- Temporal analysis (T55)
- Graph comparison (T58)
- Graph clustering (T52)

## Risk Mitigation

### Risk: "What if we need temporal analysis?"
**Mitigation**: T55 can be added as operator in Phase 2 without changing architecture

### Risk: "What if chunking + embedding need to be one operation?"
**Mitigation**: Can create composite operator T15_ChunkAndEmbed that internally uses both

### Risk: "What if we need tool-specific parameters?"
**Mitigation**: ORM roles can include parameter specifications

### Risk: "What if external APIs need different interfaces?"
**Mitigation**: T85_SocialExplorer can be subclassed for specific sources

## Validation Test Cases

To ensure we haven't locked ourselves out:

### Test 1: Simple Document Pipeline
```
T01_UniversalLoader → T23_GraphExtractor → T49_Query
```

### Test 2: Vector Search Pipeline
```
T01_UniversalLoader → T15_Chunker → T41_Embedder → VectorDB
```

### Test 3: Multi-Document Analysis
```
[T01_UniversalLoader]* → [T23_GraphExtractor]* → T301_Fusion → T68_PageRank
```

### Test 4: Social Media Analysis
```
T85_SocialExplorer → T23_GraphExtractor → T50_Community → T54_Visualizer
```

### Test 5: Complex Analytics
```
T01_UniversalLoader → T23_GraphExtractor → T51_Centrality + T56_GraphMetrics → T60_Exporter
```

## Implementation Priority

### Week 1: Core Pipeline (5 operators)
1. T01_UniversalLoader (test with PDF + JSON)
2. T23_GraphExtractor (critical merger)
3. T49_Query
4. T15_Chunker
5. T41_Embedder

### Week 2: Analysis (5 operators)
6. T68_PageRank
7. T50_Community
8. T51_Centrality
9. T301_Fusion
10. T54_Visualizer

### Week 3: Extensions (5 operators)
11. T56_GraphMetrics
12. T57_PathAnalysis
13. T60_Exporter
14. T85_SocialExplorer
15. (Reserve slot for discovered need)

## Success Criteria

1. **All 5 test pipelines work** with ORM-based composition
2. **No capability regression** from current 38 tools
3. **LLM can understand** the 15 operators and their roles
4. **New operators can be added** without breaking existing ones
5. **Performance acceptable** (<20% overhead)

## Conclusion

This plan:
- **Reduces 38 tools to 15 operators** while preserving all capabilities
- **Covers diverse data types** (documents, structured, web, social)
- **Includes various analyses** (graph, statistical, visual)
- **Maintains flexibility** for future additions
- **Tests multiple composition patterns** to ensure ORM doesn't limit us

The key insight: By keeping analysis operators separate but merging ingestion/extraction chains, we maintain flexibility where needed while simplifying where possible.