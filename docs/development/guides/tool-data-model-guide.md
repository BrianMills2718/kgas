# KGAS Data Model Flow Documentation

## Overview
This document defines the data model transformations between KGAS tools to ensure compatibility.

## Core Data Models

### 1. Raw Text
- **Source**: Document loaders (T01-T14)
- **Format**: Plain text string
- **Example**: `"Dr. Sarah Chen from Stanford University researches AI ethics."`

### 2. Chunks
- **Source**: Text Chunker (T15a)
- **Format**: 
  ```python
  {
    "chunk_id": "chunk_001",
    "text": "...",
    "start_pos": 0,
    "end_pos": 512,
    "source_ref": "doc_001"
  }
  ```

### 3. Mentions (Surface Forms)
- **Source**: NER tools (T23a SpaCy, T27 patterns)
- **Purpose**: Raw text occurrences before entity resolution
- **Format**:
  ```python
  {
    "text": "Dr. Sarah Chen",        # Surface form as it appears
    "entity_type": "PERSON",
    "start": 0,                       # Position in chunk
    "end": 14,
    "confidence": 0.9,
    "entity_id": null                 # Not yet resolved
  }
  ```

### 4. Entities (Resolved Identities)
- **Source**: T23c Ontology Extractor, Identity Service
- **Purpose**: Canonical entities after resolution
- **Format**:
  ```python
  {
    "entity_id": "entity_001",
    "canonical_name": "Dr. Sarah Chen",  # Primary name
    "entity_type": "PERSON",
    "confidence": 0.95,
    "attributes": {},
    "created_at": "2025-01-27T..."
  }
  ```

### 5. Graph Nodes
- **Source**: T31 Entity Builder
- **Purpose**: Neo4j graph representation
- **Format**: Neo4j node with properties

### 6. Relationships
- **Source**: T23c, T27, T34
- **Format**:
  ```python
  {
    "head_entity": "Dr. Sarah Chen",  # Entity reference
    "tail_entity": "Stanford",
    "relationship_type": "AFFILIATED_WITH",
    "confidence": 0.8
  }
  ```

## Tool Data Expectations

### Extraction Tools

#### T23a (SpaCy NER)
- **Input**: Text string
- **Output**: Mentions (not entities!)

#### T23c (Ontology Extractor)
- **Input**: Text string
- **Output**: 
  - `entities`: List of resolved Entity objects
  - `relationships`: List of Relationship objects
  - `mentions`: List of Mention objects (currently not exposed)

### Graph Building Tools

#### T31 (Entity Builder)
- **Expected Input**: 
  ```python
  {
    "mentions": [
      {
        "text": "...",          # REQUIRED
        "entity_type": "...",   # REQUIRED
        "confidence": 0.8,
        "entity_id": "..."      # Optional
      }
    ],
    "source_refs": ["..."]
  }
  ```
- **NOT**: Direct Entity objects from T23c

#### T34 (Edge Builder)
- **Expected Input**:
  ```python
  {
    "relationships": [
      {
        "head_entity": "...",
        "tail_entity": "...",
        "relationship_type": "...",
        "confidence": 0.8
      }
    ]
  }
  ```

### Cross-Modal Tools

#### GraphTableExporter
- **Input**: Graph data (nodes + edges)
- **Output**: Should be ToolResult, currently returns dict

#### VectorEmbedder (T15b)
- **Expected Input**:
  ```python
  {
    "chunks": [
      {
        "chunk_id": "...",
        "text": "...",
        "metadata": {}
      }
    ]
  }
  ```
- **Should also accept**: `{"texts": ["...", "..."]}`

## Data Flow Paths

### Path 1: Traditional NER Flow
```
Text → T23a (SpaCy) → Mentions → T31 → Graph Nodes
                    ↘
Text → T27 (Patterns) → Relationships → T34 → Graph Edges
```

### Path 2: Modern LLM Flow (CURRENT DEFAULT)
```
Text → T23c (LLM) → Entities + Relationships + (hidden Mentions)
                  ↓
                  Need adapter or fix
                  ↓
                T31 (expects Mentions) → Graph Nodes
                T34 (expects Relationships) → Graph Edges
```

## Integration Issues

### Issue 1: T23c → T31 Mismatch
- **Problem**: T23c outputs Entities, T31 expects Mentions
- **Solution**: Either:
  1. Expose mentions in T23c output
  2. Add Entity→Mention adapter
  3. Update T31 to accept both formats

### Issue 2: Tool Interface Compliance
- **Problem**: Some tools return dict instead of ToolResult
- **Solution**: Wrap all returns in ToolResult objects

### Issue 3: Input Format Flexibility
- **Problem**: Tools too strict about input formats
- **Solution**: Add input adapters or relaxed validation

## Validation Requirements

The contract validator should check:
1. **Schema Compliance**: Field names and types
2. **Semantic Mapping**: Field meanings (e.g., text vs canonical_name)
3. **Data Model Compatibility**: Can output of Tool A feed into Tool B?
4. **Format Flexibility**: Does tool handle common variations?