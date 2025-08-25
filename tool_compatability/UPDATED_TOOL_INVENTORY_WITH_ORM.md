# Updated Tool Inventory with ORM Mappings

## Summary
38 existing tools → 19 ORM operators across 4 phases

## Tool to Operator Mapping

| Tool ID | Tool Name | Target Operator | Phase | Semantic Roles | Status |
|---------|-----------|-----------------|-------|----------------|--------|
| **Data Ingestion** |
| T01 | PDF Loader | T01_UniversalLoader | 1 | file→text_content | Not Started |
| T02 | Word Loader | T01_UniversalLoader | 1 | file→text_content | Not Started |
| T03 | Text Loader | T01_UniversalLoader | 1 | file→text_content | Not Started |
| T04 | Markdown Loader | T01_UniversalLoader | 1 | file→text_content | Not Started |
| T05 | CSV Loader | T01_UniversalLoader | 1 | file→structured_data | Not Started |
| T06 | JSON Loader | T01_UniversalLoader | 1 | file→structured_data | Not Started |
| T07 | HTML Loader | T01_UniversalLoader | 1 | url→text_content | Not Started |
| T08 | XML Loader | T01_UniversalLoader | 1 | file→structured_data | Not Started |
| T09 | YAML Loader | T01_UniversalLoader | 1 | file→structured_data | Not Started |
| T10 | Excel Loader | T01_UniversalLoader | 1 | file→structured_data | Not Started |
| T11 | PowerPoint Loader | T01_UniversalLoader | 1 | file→text_content | Not Started |
| T12 | ZIP Extractor | T01_UniversalLoader | 1 | file→multiple_files | Not Started |
| T13 | Web Scraper | T01_UniversalLoader | 1 | url→text_content | Not Started |
| T14 | Email Parser | T01_UniversalLoader | 1 | email→text_content | Not Started |
| **Text Processing** |
| T15A | Text Chunker | T15_Chunker | 1 | text_content→text_segments | Not Started |
| T15B | Vector Embedder | T41_Embedder | 1 | text→vector_embeddings | Not Started |
| T41 | Async Text Embedder | T41_Embedder | 1 | text→vector_embeddings | Not Started |
| **Entity & Relationship Extraction** |
| T23A | spaCy NER | DEPRECATED | - | - | Remove |
| T23C | LLM Entity Extractor | T23_GraphExtractor | 1 | text→graph_structure | Not Started |
| T27 | Relationship Extractor | T23_GraphExtractor | 1 | (internal) | Not Started |
| T31 | Entity Builder | T23_GraphExtractor | 1 | (internal) | Not Started |
| T34 | Edge Builder | T23_GraphExtractor | 1 | (internal) | Not Started |
| **Graph Analysis - Core** |
| T49 | Multi-hop Query | T49_Query | 1 | graph+query→results | Not Started |
| T68 | PageRank | T68_PageRank | 1 | graph→node_scores | Not Started |
| T50 | Community Detection | T50_Community | 1 | graph→communities | Not Started |
| T51 | Centrality Analysis | T51_Centrality | 1 | graph→centralities | Not Started |
| T54 | Graph Visualization | T54_Visualizer | 1 | graph→visualization | Not Started |
| **Graph Analysis - Extended** |
| T56 | Graph Metrics | T56_GraphMetrics | 2 | graph→statistics | Not Started |
| T57 | Path Analysis | T57_PathFinder | 2 | graph+nodes→paths | Not Started |
| T59 | Scale-Free Analysis | T56_GraphMetrics | 2 | (merged) | Not Started |
| T53 | Network Motifs | T57_PathFinder | 2 | (merged) | Not Started |
| T60 | Graph Export | T60_Exporter | 2 | graph→export_format | Not Started |
| **Advanced Operations** |
| T301 | Multi-Doc Fusion | T301_Fusion | 1 | graphs[]→merged_graph | Not Started |
| T85 | Twitter Explorer | T85_SocialExplorer | 2 | query→social_graph | Not Started |
| **Deferred** |
| T52 | Graph Clustering | T52_Clustering | 3 | graph→clusters | Deferred |
| T55 | Temporal Analysis | T55_Temporal | 3 | graph+time→temporal | Deferred |
| T58 | Graph Comparison | T58_Comparison | 3 | graphs[]→similarity | Deferred |
| **New Additions for Parity** |
| NEW | Entity Resolver | Entity_Resolver | 3 | entities→resolved | Not Exist |
| NEW | TF-IDF Ranker | TFIDF_Ranker | 3 | docs→rankings | Not Exist |
| NEW | Chunk Retriever | T15_ChunkRetriever | 2 | chunks+query→relevant | Not Exist |
| NEW | Vector DB | T41_VectorDB | 2 | vectors+query→similar | Not Exist |
| NEW | Table Operator | T05_TableOperator | 3 | table+query→results | Not Exist |
| NEW | Database Interface | T06_DatabaseInterface | 3 | db+sql→results | Not Exist |
| NEW | Iterative Refiner | Iterative_Refiner | 3 | any→refined | Not Exist |

## Phase Summary

### Phase 1: Core Pipeline (10 operators)
- T01_UniversalLoader (merges 14 tools)
- T15_Chunker
- T41_Embedder (merges T15B + T41)
- T23_GraphExtractor (merges T23C + T27 + T31 + T34)
- T49_Query
- T68_PageRank
- T50_Community
- T51_Centrality
- T54_Visualizer
- T301_Fusion

### Phase 2: DIGIMON Parity (6 operators)
- T56_GraphMetrics (merges T56 + T59)
- T57_PathFinder (merges T57 + T53)
- T60_Exporter
- T85_SocialExplorer
- T41_VectorDB (new)
- T15_ChunkRetriever (new)

### Phase 3: Full Parity (9 operators)
- T52_Clustering
- T55_Temporal
- T58_Comparison
- Entity_Resolver (new)
- TFIDF_Ranker (new)
- T05_TableOperator (new)
- T06_DatabaseInterface (new)
- Iterative_Refiner (new)

### Phase 4: Validation & Migration
- Full system testing
- Performance optimization
- Documentation
- Deprecation of old tools

## Semantic Role Categories

```python
SEMANTIC_TYPES = {
    # Input types
    "file_reference": "Path to file",
    "url": "Web URL",
    "email_source": "Email data",
    
    # Text types
    "text_content": "Raw text",
    "text_segments": "Chunked text",
    
    # Structured types
    "structured_data": "JSON/CSV/Excel data",
    "table_data": "Tabular data",
    
    # Entity types
    "named_entities": "Extracted entities",
    "resolved_entities": "Disambiguated entities",
    "entity_relationships": "Relations between entities",
    
    # Graph types
    "graph_structure": "Complete graph",
    "graph_nodes": "Node collection",
    "graph_edges": "Edge collection",
    "communities": "Community structure",
    "paths": "Graph paths",
    
    # Vector types
    "vector_embeddings": "Semantic vectors",
    
    # Query types
    "query_spec": "Query specification",
    "query_results": "Query output",
    
    # Analysis types
    "node_scores": "Scoring/ranking",
    "centralities": "Centrality measures",
    "statistics": "Graph metrics",
    "visualization": "Visual representation"
}
```

## Implementation Priority

### Week 1: Proof of Concept
1. Build ORM infrastructure
2. Wrap T03 → T15A → T23C
3. Test semantic matching

### Week 2: Core Pipeline
4. Implement Phase 1 operators
5. Test document → graph → query

### Week 3: Extended Capabilities
6. Implement Phase 2 operators
7. Test DIGIMON parity

### Week 4: Complete System
8. Add remaining operators
9. Full validation
10. Migration from old tools

## Notes

- **DEPRECATED**: T23A (spaCy NER) - replaced by T23C
- **MERGED**: Many tools become internal operations within operators
- **NEW**: 7 operators needed for full DIGIMON/StructGPT parity
- **DEFERRED**: 3 operators moved to Phase 3 (not critical for initial validation)