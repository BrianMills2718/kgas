"""
Phase 1 tools load theory YAML and map MCL IDs before extraction.
"""

"""Phase 1 Tools - Vertical Slice Implementation

Implements the critical path for Document → Knowledge Graph → Answer workflow.

IMPORTANT: Default Extraction Approach
======================================
Use T23c (Ontology-Aware Extractor) from phase2 for entity + relationship extraction.
It extracts entities, relationships, and properties in ONE LLM call.

Pattern-based tools (T23a, T27) have been ARCHIVED to reduce confusion.
See src/tools/phase1/archived_extraction/ if you need pattern-based extraction.

Current Phase 1 Tools:
- T01: PDF Loader - Load documents
- T15a: Text Chunker - Split text into chunks
- T15b: Vector Embedder - Generate embeddings
- T31: Entity Builder - Build graph nodes
- T34: Edge Builder - Build graph edges
- T68: PageRank - Calculate node importance
- T49: Multi-hop Query - Query the graph

DEPRECATED (archived):
- T23a: spaCy NER - Use T23c instead
- T27: Relationship Extractor - Use T23c instead
"""