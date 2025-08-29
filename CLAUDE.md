# KGAS Implementation Guide

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only
- **FAIL-FAST**: Surface errors immediately, no error suppression
- **KISS**: Keep It Simple - avoid over-engineering
- **TEST PROPERLY**: Unit tests, integration tests, error cases

---

## 2. CURRENT SPRINT (2025-08-29)

### 🎯 Sprint Focus: Add Vector & Table Services
**Objective**: Add vector embeddings and table storage capabilities
**Time**: 1 hour  
**Guide**: `/home/brian/projects/Digimons/docs/architecture/SERVICE_IMPLEMENTATION_SIMPLE.md`

### Implementation Checklist
- [ ] Run verify_setup.py - single check for everything
- [ ] Create VectorService (20 lines, just calls OpenAI)
- [ ] Create TableService (40 lines, just SQLite operations)
- [ ] Run test_services.py - proper unit & integration tests
- [ ] Test simple_pipeline.py - direct service usage

### Why Simple Plan?
- **No unnecessary wrappers** - Services used directly
- **No BFS chain discovery** - We know what to call
- **Proper testing** - Unit, integration, and error tests
- **Clear success criteria** - Tests pass or fail

---

## 3. CODEBASE STRUCTURE

### Active Implementation
**Location**: `/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/`
- **PURPOSE**: POC for testing service integration patterns
- **NOT A REPLACEMENT**: Testing patterns to apply back to main `/src` codebase
- **FOCUS**: Proving simple, working patterns

### What We're Building
```
services/
├── vector_service.py    # NEW: OpenAI embeddings (20 lines)
└── table_service.py     # NEW: SQLite storage (40 lines)

tests/
├── test_services.py     # Unit & integration tests
└── simple_pipeline.py   # Direct service usage example
```

### What Already Exists
```
tools/
├── text_loader_v3.py    # File loading with OCR detection
├── knowledge_graph_extractor.py  # Gemini extraction
└── graph_persister_v2.py # Neo4j with document isolation

services/
├── crossmodal_service.py  # Graph↔Table (partial)
├── identity_service_v3.py # Entity deduplication (partial)
└── provenance_enhanced.py # Operation tracking (partial)
```

---

## 4. INFRASTRUCTURE

- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (use vs2_ prefix for new tables)
- **OpenAI**: text-embedding-3-small model
- **Gemini**: gemini-1.5-flash via litellm
- **Config**: API keys in `/home/brian/projects/Digimons/.env`

---

## 5. TESTING APPROACH

### Systematic Testing Plan
```python
# 1. Unit Tests (test each service)
test_vector_service()  # Test embedding generation
test_table_service()   # Test data storage

# 2. Integration Tests (services together)
test_integration()     # Vector + Table working together

# 3. Error Cases
test_empty_inputs()    # Handle edge cases
test_api_failures()    # Handle external failures
```

### Success Criteria
- All unit tests pass
- Integration tests pass
- Error cases handled gracefully
- No "count ✅ symbols" nonsense

---

## 6. PERMANENT REFERENCES

### Implementation Guides
| Guide | Purpose | Complexity |
|-------|---------|------------|
| `SERVICE_IMPLEMENTATION_SIMPLE.md` | Current sprint - KISS approach | Simple |
| `SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md` | Over-engineered version | Complex |
| `VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md` | Future phases | Medium |

### Architecture Docs
- `VERTICAL_SLICE_20250826.md` - System design
- `UNCERTAINTY_20250825.md` - Propagation model
- `/architecture_review_20250808/` - Why we're in vertical_slice not /src

---

## 7. RECENT WORK & STATUS

### Completed ✅
- Document isolation in Neo4j
- Gemini retry mechanism (10 attempts, exponential backoff)
- Entity extraction evaluation (F1: 0.413, separate concern)

### Current Sprint
- Adding VectorService (NEW capability)
- Adding TableService (NEW capability)
- No complex wrappers, just simple services

### Known Issues
- Only 3/6 services integrated
- CrossModalService only works graph→table
- Main `/src` has architectural debt (see Aug 8 review)

---

## 8. QUICK COMMANDS

```bash
# Verify setup (one command)
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
python3 verify_setup.py

# Run all tests
python3 test_services.py

# Test pipeline
python3 simple_pipeline.py

# Check what's in database
sqlite3 vertical_slice.db "SELECT COUNT(*) FROM vs2_embeddings;"
```

---

*Last Updated: 2025-08-29*
*Philosophy: Keep It Simple, Test It Properly*