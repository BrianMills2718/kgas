# KGAS Uncertainty System - Implementation Guide

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
│   └── Evidence_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md         # Archived completed work
```

---

## 2. PERMANENT INFORMATION -- DO NOT REMOVE

### Planning Documents
- **`/docs/architecture/VERTICAL_SLICE_20250826.md`** - Complete vertical slice design & implementation plan
- **`/docs/architecture/UNCERTAINTY_20250825.md`** - Uncertainty propagation model specification
- **`/docs/PHASE_C_FUTURE_WORK.md`** - Long-term roadmap beyond MVP

### Codebase Structure
```
tool_compatability/poc/vertical_slice/
├── tools/                          # Core pipeline tools
│   ├── text_loader_v3.py          # OCR detection, file loading
│   ├── knowledge_graph_extractor.py # Gemini LLM extraction
│   ├── graph_persister_v2.py      # Neo4j with document isolation
├── framework/
│   ├── clean_framework_v2.py      # Pipeline orchestration with metadata
├── services/
│   ├── identity_service_v3.py     # Entity deduplication (partial)
│   ├── crossmodal_service.py      # Graph↔Table conversion (partial)
│   ├── provenance_enhanced.py     # Operation tracking (partial)
├── thesis_evidence/
│   └── evidence_collector.py      # Evaluation framework
```

### Infrastructure
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db`
- **Gemini API**: Via `.env` file at `/home/brian/projects/Digimons/.env`
- **Model**: `gemini/gemini-1.5-flash` via litellm

---

## 3. Current Sprint (Week of 2025-08-26)

### Objective
Fix document isolation and achieve accurate F1 scores for thesis evidence.

### Recently Completed ✅
- Document isolation in Neo4j (GraphPersisterV2 with document_id tagging)
- Improved Gemini retry mechanism (10 attempts, exponential backoff)
- Fixed entity/relationship matching (case-insensitive)
- OCR error detection in TextLoaderV3

### Active Issues
1. **F1 Score Accuracy**: Was 0.033 due to Neo4j accumulation, should be ~0.9 with isolation
2. **Service Integration**: Only 3/6 services connected to pipeline
3. **Uncertainty Correlation**: Negative correlation needs investigation with clean data

### Next Steps
1. Re-run thesis collection with GraphPersisterV2 document isolation
2. Verify F1 scores improve to expected ~0.9
3. Integrate ProvenanceEnhanced for operation tracking
4. Connect IdentityService for cross-document entity resolution

---

## 4. Quick Commands

```bash
# Test document isolation
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
python3 test_document_isolation.py

# Run thesis evidence collection
cd thesis_evidence
python3 run_thesis_collection.py

# Test specific tool
python3 -c "from tools.text_loader_v3 import TextLoaderV3; t = TextLoaderV3(); print(t.process('test.txt'))"

# Check Neo4j for document entities
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
with driver.session() as s:
    result = s.run('MATCH (e:VSEntity) RETURN e.document_id, count(e)')
    for r in result: print(r)
"
```

---

## 5. Integration Status

### Working ✅
- TextLoaderV3 → KnowledgeGraphExtractor → GraphPersisterV2 pipeline
- Document isolation in Neo4j
- Basic uncertainty propagation (physics-style)
- Thesis evidence collection framework

### Partially Integrated ⚠️
- CrossModalService (graph→table export works, reverse not tested)
- IdentityService (finds similar entities, merge not integrated)
- ProvenanceEnhanced (tracks operations, not connected to pipeline)

### Not Integrated ❌
- ServiceBridge, CompositionService, PiiService from src/core/
- YAML configuration loading
- Full KGAS architecture vision

---

## 6. Known Issues & Workarounds

### Issue: Gemini API Overload
**Workaround**: Implemented 10-retry exponential backoff in knowledge_graph_extractor.py

### Issue: Low F1 Scores
**Root Cause**: Neo4j accumulated entities across documents
**Fix**: GraphPersisterV2 implements document_id isolation

### Issue: Entity Type Mismatches
**Fix**: Prompt updated to use specific types (PERSON, ORGANIZATION, SYSTEM, etc.)

---

*Last Updated: 2025-08-27*
*For implementation details, see referenced planning documents*