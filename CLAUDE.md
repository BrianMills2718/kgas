# Clean Vertical Slice Implementation - KGAS Uncertainty System

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files  
- **TEST DRIVEN DESIGN**: Write tests first where possible

### Evidence Requirements
```
evidence/
├── current/
│   └── Evidence_VerticalSlice_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md                      # Archived completed work
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Test with REAL services (Gemini API, Neo4j, SQLite)
- Mark all untested components as "NOT TESTED"

---

## 2. Codebase Structure

### Clean Vertical Slice Location
```
tool_compatability/poc/vertical_slice/
├── services/
│   ├── identity_service_v3.py      # Simplified entity dedup
│   ├── crossmodal_service.py       # Graph↔table converter  
│   └── provenance_enhanced.py      # Extends existing with uncertainty
├── tools/
│   ├── text_loader_v3.py           # With uncertainty assessment
│   ├── knowledge_graph_extractor.py # Single LLM call
│   └── graph_persister.py          # Neo4j writer
├── config/
│   └── uncertainty_constants.py     # Configurable constants
├── framework/
│   └── clean_framework.py          # Physics-style propagation
└── tests/
    └── test_vertical_slice.py      # End-to-end validation
```

### Key Architecture Documents
- **`/docs/architecture/VERTICAL_SLICE_20250826.md`** - Complete design & rationale
- **`/docs/architecture/UNCERTAINTY_20250825.md`** - Uncertainty model explanation
- **`/CLAUDE.md`** - This file (implementation instructions)

### Integration Points
- **Gemini API**: via `litellm` for knowledge graph extraction
- **Neo4j**: Graph storage at `bolt://localhost:7687`
- **SQLite**: Metrics storage at `vertical_slice.db`
- **Config**: `.env` file with `GEMINI_API_KEY`

---

## 3. Current Status

### ✅ Completed (Service Hardening)
1. **Fail-Fast Implementation**: All errors propagate loudly
2. **Real Service Integration**: Gemini API and Neo4j proven working
3. **Configuration Support**: YAML + environment overrides
4. **Chain Discovery**: Framework finds FILE→TEXT→ENTITIES→GRAPH

### 🚧 Ready to Implement (Clean Vertical Slice)
The system needs a clean demonstration of uncertainty propagation through a minimal pipeline.

---

## 4. PHASE 1: Foundation & Services (Day 1)

### Objective
Create clean services isolated from technical debt, verify database connections work.

### Task 1.0: Verify Infrastructure

**File**: Create `/tool_compatability/poc/vertical_slice/test_connections.py`

```python
#!/usr/bin/env python3
"""Test database connections before building services"""

def test_neo4j_connection():
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    driver.verify_connectivity()
    print("✅ Neo4j connected")
    
    # Test VS namespace
    with driver.session() as session:
        session.run("CREATE (n:VSEntity {test: true})")
        result = session.run("MATCH (n:VSEntity) RETURN count(n) as count")
        print(f"✅ VS namespace working: {result.single()['count']} nodes")
        session.run("MATCH (n:VSEntity {test: true}) DELETE n")  # Cleanup
    driver.close()

def test_sqlite_connection():
    import sqlite3
    conn = sqlite3.connect("vertical_slice.db")
    conn.execute("CREATE TABLE IF NOT EXISTS vs_metrics (id TEXT PRIMARY KEY)")
    print("✅ SQLite connected")
    conn.close()

if __name__ == "__main__":
    test_neo4j_connection()
    test_sqlite_connection()
    print("✅ All connections verified")
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_Connections.md`
- Show both database connections working
- Confirm VS namespace doesn't conflict

### Task 1.1: CrossModalService

**File**: Create `/tool_compatability/poc/vertical_slice/services/crossmodal_service.py`

```python
#!/usr/bin/env python3
"""
CrossModal Service - Handles graph↔table conversions
Hypergraph approach: edges as rows, properties as columns
"""

import pandas as pd
from neo4j import GraphDatabase
import sqlite3
from typing import List, Dict, Any

class CrossModalService:
    """Convert between graph and tabular representations"""
    
    def __init__(self, neo4j_driver, sqlite_path: str):
        self.neo4j = neo4j_driver
        self.sqlite_path = sqlite_path
    
    def graph_to_table(self, entity_ids: List[str]) -> pd.DataFrame:
        """
        Export graph to relational tables for statistical analysis
        
        Creates:
        1. vs_entity_metrics: node properties and graph metrics  
        2. vs_relationships: edges as rows with properties
        """
        with self.neo4j.session() as session:
            # Get entities with metrics
            entity_query = """
            MATCH (e:VSEntity)
            WHERE e.entity_id IN $entity_ids
            OPTIONAL MATCH (e)-[r]-()
            RETURN e.entity_id as id,
                   e.canonical_name as name,
                   e.entity_type as type,
                   count(DISTINCT r) as degree,
                   properties(e) as properties
            """
            entities = session.run(entity_query, entity_ids=entity_ids).data()
            
            # Get relationships (hypergraph as table)
            relationship_query = """
            MATCH (s:VSEntity)-[r]->(t:VSEntity)
            WHERE s.entity_id IN $entity_ids
            RETURN s.entity_id as source,
                   t.entity_id as target,
                   type(r) as relationship_type,
                   properties(r) as properties
            """
            relationships = session.run(relationship_query, entity_ids=entity_ids).data()
        
        # Write to SQLite
        conn = sqlite3.connect(self.sqlite_path)
        
        # Entity metrics table
        entity_df = pd.DataFrame(entities)
        entity_df.to_sql('vs_entity_metrics', conn, if_exists='replace', index=False)
        
        # Relationships table
        rel_df = pd.DataFrame(relationships)
        rel_df.to_sql('vs_relationships', conn, if_exists='replace', index=False)
        
        conn.close()
        
        print(f"✅ Exported {len(entities)} entities and {len(relationships)} relationships")
        return entity_df
    
    def table_to_graph(self, relationships_df: pd.DataFrame) -> Dict:
        """
        Convert relational table to graph
        Each row becomes an edge with properties
        """
        created_edges = 0
        
        with self.neo4j.session() as session:
            for _, row in relationships_df.iterrows():
                query = """
                MATCH (s:VSEntity {entity_id: $source})
                MATCH (t:VSEntity {entity_id: $target})
                CREATE (s)-[r:VS_RELATION {type: $rel_type}]->(t)
                SET r += $properties
                """
                session.run(
                    query,
                    source=row['source'],
                    target=row['target'],
                    rel_type=row.get('relationship_type', 'RELATED'),
                    properties=row.get('properties', {})
                )
                created_edges += 1
        
        return {"edges_created": created_edges}
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_CrossModal.md`
- Show graph→table export working
- Show table→graph import working
- Verify data in SQLite tables

### Task 1.2: Simplified IdentityService

**File**: Create `/tool_compatability/poc/vertical_slice/services/identity_service_v3.py`

```python
#!/usr/bin/env python3
"""
Simplified IdentityService for MVP
Just handles basic entity deduplication
"""

from typing import List, Dict
from neo4j import GraphDatabase

class IdentityServiceV3:
    """
    Simplified for MVP - just handles entity deduplication
    The bug fix (creating Entity nodes) is handled in GraphPersister
    """
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def find_similar_entities(self, name: str, threshold: float = 0.8) -> List[Dict]:
        """
        Find entities with similar names (for deduplication)
        MVP: Simple string matching, can add embeddings later
        """
        with self.driver.session() as session:
            query = """
            MATCH (e:VSEntity)
            WHERE toLower(e.canonical_name) CONTAINS toLower($name)
            RETURN e.entity_id as id, e.canonical_name as name
            LIMIT 10
            """
            result = session.run(query, name=name)
            return [dict(record) for record in result]
    
    def merge_entities(self, entity_id1: str, entity_id2: str) -> str:
        """
        Merge two entities that refer to the same real-world entity
        Not critical for MVP - can be manual process initially
        """
        with self.driver.session() as session:
            # Move all relationships to entity1
            merge_query = """
            MATCH (e1:VSEntity {entity_id: $id1})
            MATCH (e2:VSEntity {entity_id: $id2})
            OPTIONAL MATCH (e2)-[r]->(target)
            CREATE (e1)-[r2:VS_MERGED]->(target)
            SET r2 = properties(r)
            DELETE r
            DELETE e2
            RETURN e1.entity_id as merged_id
            """
            result = session.run(merge_query, id1=entity_id1, id2=entity_id2)
            return result.single()['merged_id']
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_Identity.md`
- Show entity search working
- Test with similar entity names
- Verify VSEntity namespace

### Task 1.3: Enhanced ProvenanceService

**File**: Create `/tool_compatability/poc/vertical_slice/services/provenance_enhanced.py`

```python
#!/usr/bin/env python3
"""
Enhanced ProvenanceService with uncertainty tracking
Builds on existing ProvenanceService
"""

import sqlite3
import json
import time
from typing import Dict, Any
from datetime import datetime

class ProvenanceEnhanced:
    """Track operations with uncertainty and construct mapping"""
    
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
        self._setup_database()
    
    def _setup_database(self):
        """Create provenance tables with uncertainty fields"""
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vs_provenance (
                operation_id TEXT PRIMARY KEY,
                tool_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                inputs TEXT,
                outputs TEXT,
                uncertainty REAL,
                reasoning TEXT,
                construct_mapping TEXT,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def track_operation(self, 
                       tool_id: str,
                       operation: str,
                       inputs: Dict,
                       outputs: Dict,
                       uncertainty: float,
                       reasoning: str,
                       construct_mapping: str) -> str:
        """
        Track operation with uncertainty and construct mapping
        """
        import uuid
        operation_id = f"op_{uuid.uuid4().hex[:12]}"
        
        conn = sqlite3.connect(self.sqlite_path)
        conn.execute("""
            INSERT INTO vs_provenance 
            (operation_id, tool_id, operation, inputs, outputs, 
             uncertainty, reasoning, construct_mapping, execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            operation_id,
            tool_id,
            operation,
            json.dumps(inputs),
            json.dumps(outputs),
            uncertainty,
            reasoning,
            construct_mapping,
            time.time()
        ))
        conn.commit()
        conn.close()
        
        return operation_id
    
    def get_operation_chain(self, final_operation_id: str) -> List[Dict]:
        """Get all operations leading to a result"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.execute("""
            SELECT * FROM vs_provenance 
            WHERE created_at <= (
                SELECT created_at FROM vs_provenance 
                WHERE operation_id = ?
            )
            ORDER BY created_at
        """, (final_operation_id,))
        
        operations = []
        for row in cursor:
            operations.append({
                'operation_id': row[0],
                'tool_id': row[1],
                'operation': row[2],
                'uncertainty': row[5],
                'reasoning': row[6],
                'construct_mapping': row[7]
            })
        
        conn.close()
        return operations
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_Provenance.md`
- Show operation tracking with uncertainty
- Retrieve operation chain
- Verify all fields stored correctly

---

## 5. PHASE 2: Tools with Uncertainty (Day 2)

### Task 2.0: Uncertainty Constants

**File**: Create `/tool_compatability/poc/vertical_slice/config/uncertainty_constants.py`

```python
#!/usr/bin/env python3
"""
Configurable uncertainty constants for deterministic operations
These are clearly labeled and easily adjustable
"""

# TextLoader uncertainties by file type
TEXT_LOADER_UNCERTAINTY = {
    "pdf": 0.15,      # OCR challenges, formatting loss
    "txt": 0.02,      # Nearly perfect extraction
    "docx": 0.08,     # Some formatting complexity
    "html": 0.12,     # Tag stripping, structure loss
    "md": 0.03,       # Clean markdown extraction
    "rtf": 0.10,      # Format conversion challenges
    "default": 0.10   # Unknown file types
}

# Reasoning templates
TEXT_LOADER_REASONING = {
    "pdf": "PDF extraction may have OCR errors or formatting loss",
    "txt": "Plain text extraction with minimal uncertainty",
    "docx": "Word document with potential formatting complexity",
    "html": "HTML parsing may lose semantic structure",
    "md": "Markdown extraction preserves structure well",
    "default": "Standard uncertainty for file format extraction"
}
```

### Task 2.1: TextLoaderV3

**File**: Create `/tool_compatability/poc/vertical_slice/tools/text_loader_v3.py`

**Implementation**: See VERTICAL_SLICE_20250826.md lines 244-299 for complete implementation

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_TextLoader.md`
- Test with PDF, TXT, and DOCX files
- Show uncertainty assessments for each
- Verify construct mapping recorded

### Task 2.2: KnowledgeGraphExtractor

**File**: Create `/tool_compatability/poc/vertical_slice/tools/knowledge_graph_extractor.py`

**Implementation**: See VERTICAL_SLICE_20250826.md lines 308-401 for complete implementation

**Key Points**:
- Single LLM call for entities AND relationships
- Handles chunking for long documents (4000 chars with overlap)
- Returns unified uncertainty for entire extraction

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_KGExtractor.md`
- Show actual Gemini API call and response
- Test with real document text
- Verify entities AND relationships extracted together

### Task 2.3: GraphPersister

**File**: Create `/tool_compatability/poc/vertical_slice/tools/graph_persister.py`

**Implementation**: See VERTICAL_SLICE_20250826.md lines 410-508 for complete implementation

**Critical**: 
- Creates VSEntity nodes (fixes IdentityService bug)
- Has 0.0 uncertainty on success (pure storage operation)
- Exports metrics to SQLite via CrossModalService

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_GraphPersister.md`
- Show entities created in Neo4j
- Verify relationships created
- Confirm 0.0 uncertainty on success

---

## 6. PHASE 3: Framework Integration (Day 3)

### Task 3.1: Clean Framework

**File**: Create `/tool_compatability/poc/vertical_slice/framework/clean_framework.py`

**Implementation**: See VERTICAL_SLICE_20250826.md lines 519-578 for complete implementation

**Physics-Style Propagation**:
```python
def _combine_sequential_uncertainties(self, uncertainties: List[float]) -> float:
    """
    Physics-style error propagation for sequential tools
    confidence = ∏(1 - uᵢ)
    total_uncertainty = 1 - confidence
    """
    confidence = 1.0
    for u in uncertainties:
        confidence *= (1 - u)
    return 1 - confidence
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_Framework.md`
- Show chain discovery working
- Demonstrate uncertainty propagation
- Verify math is correct

---

## 7. PHASE 4: Testing & Validation (Day 4)

### Task 4.1: End-to-End Test

**File**: Create `/tool_compatability/poc/vertical_slice/tests/test_vertical_slice.py`

**Implementation**: See VERTICAL_SLICE_20250826.md lines 586-620 for test structure

**Test Document**: Create a real PDF with known content for testing

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_EndToEnd.md`
- Complete pipeline execution log
- Neo4j query showing VSEntity nodes
- SQLite query showing metrics
- Provenance with uncertainty values
- Total uncertainty calculation

---

## 8. Success Criteria

### Minimum Viable Success ✅
- [ ] One complete chain executes (File → KnowledgeGraph → Neo4j)
- [ ] Uncertainty propagates through chain
- [ ] Real Neo4j has VSEntity nodes and relationships
- [ ] Real SQLite has vs_entity_metrics table
- [ ] ProvenanceEnhanced tracks all operations with uncertainty

### Target Success 🎯
- [ ] All above plus...
- [ ] CrossModal conversion works (graph → table)
- [ ] At least 10 entities extracted and linked
- [ ] Uncertainty assessments include detailed reasoning
- [ ] Combined uncertainty ~0.35 (0.15 × 0.25 × 0.0)

### Evidence Collection
Each task MUST produce evidence showing:
1. Raw terminal output of execution
2. Database queries verifying data stored
3. Uncertainty values and reasoning
4. No mocks - actual API calls and database writes

---

## 9. Testing Commands

```bash
# Phase 1: Test infrastructure
python3 tool_compatability/poc/vertical_slice/test_connections.py

# Phase 2: Test individual tools
python3 -c "from tool_compatability.poc.vertical_slice.tools.text_loader_v3 import TextLoaderV3; t = TextLoaderV3(); print(t.process('test.pdf'))"

# Phase 3: Test framework
python3 -c "from tool_compatability.poc.vertical_slice.framework.clean_framework import CleanToolFramework; f = CleanToolFramework('bolt://localhost:7687', 'vertical_slice.db'); print('Framework initialized')"

# Phase 4: Run end-to-end test
python3 tool_compatability/poc/vertical_slice/tests/test_vertical_slice.py
```

---

## 10. Troubleshooting

### If Neo4j connection fails
```bash
# Start Neo4j
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest

# Verify
python3 -c "from neo4j import GraphDatabase; d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword')); d.verify_connectivity(); print('Connected')"
```

### If Gemini API fails
```bash
# Check API key
cat .env | grep GEMINI

# Test directly
python3 -c "import os; print(f'Key exists: {bool(os.getenv(\"GEMINI_API_KEY\"))}')"
```

### If imports fail
```bash
# Ensure in correct directory
cd tool_compatability/poc/vertical_slice

# Add to path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 11. Important Notes

1. **VS Prefix**: All Neo4j labels/types use VS prefix to avoid conflicts
2. **No ServiceManager**: Direct instantiation to avoid complexity
3. **Real Databases**: No mocks, Neo4j and SQLite must be running
4. **Uncertainty is Subjective**: It's expert assessment, not calibration
5. **GraphPersister Zero Uncertainty**: Storage operations have 0.0 on success

---

*Last Updated: 2025-08-26*
*Phase: Clean Vertical Slice*
*Priority: Demonstrate uncertainty propagation with minimal pipeline*