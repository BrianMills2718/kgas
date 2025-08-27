# Clean Vertical Slice - Issue Resolution Phase

## ⚠️ PERMANENT - DO NOT REMOVE ⚠️

### API Configuration
- **API Keys Location**: `/home/brian/projects/Digimons/.env`
- **Default LLM Model**: `gemini/gemini-1.5-flash` via litellm
- **Always load .env first** before claiming API keys are missing
```python
from dotenv import load_dotenv
import os

# ALWAYS load from the project .env file
load_dotenv('/home/brian/projects/Digimons/.env')
api_key = os.getenv('GEMINI_API_KEY')
```

---

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
│   ├── identity_service_v3.py      # Entity deduplication (COMPLETE)
│   ├── crossmodal_service.py       # Graph↔table converter (HAS BUG)
│   └── provenance_enhanced.py      # Uncertainty tracking (COMPLETE)
├── tools/
│   ├── text_loader_v3.py           # Text extraction (COMPLETE)
│   ├── knowledge_graph_extractor.py # LLM extraction (NEEDS FIX)
│   └── graph_persister.py          # Neo4j writer (COMPLETE)
├── config/
│   └── uncertainty_constants.py     # Configurable constants (COMPLETE)
├── framework/
│   └── clean_framework.py          # Tool composition (NEEDS FIX)
└── tests/
    └── test_vertical_slice.py      # End-to-end test (COMPLETE)
```

### Key Architecture Documents
- **`/docs/architecture/VERTICAL_SLICE_20250826.md`** - Complete design & rationale
- **`/docs/architecture/UNCERTAINTY_20250825.md`** - Uncertainty model explanation
- **`/CLAUDE.md`** - This file (implementation instructions)

### Integration Points
- **Gemini API**: via `litellm` with key from `.env`
- **Neo4j**: Graph storage at `bolt://localhost:7687`
- **SQLite**: Metrics storage at `vertical_slice.db`

---

## 3. Current Status

### ✅ Completed (Clean Vertical Slice Phase)
1. **Core Services**: Identity, Provenance, CrossModal (with bug)
2. **Tools**: TextLoader, GraphPersister working
3. **Framework**: Basic chain execution working
4. **Testing**: End-to-end test passing with mock KG extraction

### 🔴 Critical Issues to Fix
1. **KnowledgeGraphExtractor not loading .env** - Using mock instead of real Gemini
2. **DateTime serialization bug** - CrossModalService fails to export to SQLite
3. **Chain discovery hardcoded** - Not truly extensible

---

## 4. PRIORITY FIXES - Critical Issues

### Task 1: Fix .env Loading in KnowledgeGraphExtractor

**File**: `/tool_compatability/poc/vertical_slice/tools/knowledge_graph_extractor.py`

**Current Problem**: 
- Line 19-21: Checking `os.getenv()` without loading .env first
- Causes: Always fails to find API key, falls back to mock

**Fix Implementation**:
```python
# At top of __init__ method (line 13), add:
from dotenv import load_dotenv

def __init__(self, chunk_size=4000, overlap=200, schema_mode="open"):
    # CRITICAL: Load .env FIRST
    load_dotenv('/home/brian/projects/Digimons/.env')
    
    self.tool_id = "KnowledgeGraphExtractor"
    self.chunk_size = chunk_size
    self.overlap = overlap
    self.schema_mode = schema_mode
    
    # Now this will work
    self.api_key = os.getenv('GEMINI_API_KEY')
    if not self.api_key:
        raise ValueError("GEMINI_API_KEY not found in /home/brian/projects/Digimons/.env")
    
    # Always use gemini-1.5-flash
    self.model = "gemini/gemini-1.5-flash"
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_EnvFix.md`
- Show API key loading successfully
- Run actual Gemini extraction
- Compare extraction quality to mock

### Task 2: Fix DateTime Serialization Bug

**File**: `/tool_compatability/poc/vertical_slice/services/crossmodal_service.py`

**Current Problem**:
- Lines 56-67: Neo4j returns DateTime objects, JSON can't serialize them
- Error: "Object of type DateTime is not JSON serializable"

**Fix Implementation**:
```python
# Add helper method after __init__ (line 17):
def _serialize_neo4j_value(self, value):
    """Convert Neo4j types to JSON-serializable formats"""
    from datetime import datetime
    
    if value is None:
        return None
    elif hasattr(value, 'iso_format'):  # Neo4j DateTime
        return value.iso_format()
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: self._serialize_neo4j_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [self._serialize_neo4j_value(v) for v in value]
    else:
        return value

# Update graph_to_table method (lines 56-67):
# Process properties before creating DataFrame
for entity in entities:
    if 'properties' in entity:
        entity['properties'] = self._serialize_neo4j_value(entity['properties'])

for rel in relationships:
    if 'properties' in rel:
        rel['properties'] = self._serialize_neo4j_value(rel['properties'])

# Now safe to create DataFrames and serialize
entity_df = pd.DataFrame(entities)
if 'properties' in entity_df.columns:
    import json
    entity_df['properties'] = entity_df['properties'].apply(json.dumps)
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_DateTimeFix.md`
- Show successful SQLite export without warnings
- Query SQLite to verify data stored correctly
- Test with entities that have datetime properties

### Task 3: Implement Dynamic Chain Discovery

**File**: `/tool_compatability/poc/vertical_slice/framework/clean_framework.py`

**Current Problem**:
- Lines 71-81: Hardcoded chain for FILE→NEO4J_GRAPH
- Not extensible to other transformations

**Fix Implementation**:
```python
# Replace find_chain method (lines 71-81):
def find_chain(self, input_type: DataType, output_type: DataType) -> Optional[List[str]]:
    """Use BFS to find shortest tool chain between types"""
    from collections import deque
    
    # Build adjacency list of transformations
    graph = {}
    for tool_id, cap in self.capabilities.items():
        if cap.input_type not in graph:
            graph[cap.input_type] = []
        graph[cap.input_type].append((cap.output_type, tool_id))
    
    # BFS for shortest path
    queue = deque([(input_type, [])])
    visited = {input_type}
    
    while queue:
        current_type, path = queue.popleft()
        
        if current_type == output_type:
            return path
        
        # Explore neighbors
        for next_type, tool_id in graph.get(current_type, []):
            if next_type not in visited:
                visited.add(next_type)
                queue.append((next_type, path + [tool_id]))
    
    return None  # No chain found
```

**Evidence Required**: `evidence/current/Evidence_VerticalSlice_ChainDiscovery.md`
- Test finding FILE→NEO4J_GRAPH chain
- Add new tool and test discovery of new chains
- Show that non-existent chains return None

---

## 5. Testing After Fixes

### Test Command Sequence
```bash
# 1. Test .env loading
cd tool_compatability/poc/vertical_slice
python3 -c "from tools.knowledge_graph_extractor import KnowledgeGraphExtractor; k = KnowledgeGraphExtractor(); print('✅ API key loaded')"

# 2. Test DateTime fix
python3 test_services.py

# 3. Test chain discovery  
python3 framework/clean_framework.py

# 4. Run complete end-to-end test
python3 tests/test_vertical_slice.py
```

### Expected Success Metrics
- No mock KG extraction - real Gemini API calls
- No DateTime serialization warnings
- Dynamic chain discovery working
- Total uncertainty using real values (not mock 0.25)

---

## 6. Secondary Improvements (After Critical Fixes)

### Task 4: Add PDF Support Testing
- Install PyPDF2 or pypdf
- Test with real PDF files
- Document extraction quality

### Task 5: Test Isolation
- Add namespace isolation for tests
- Prevent test data pollution
- Clean up after each test run

### Task 6: Multi-Provider LLM Support
- Support OpenAI/Anthropic as fallbacks
- Keep Gemini as default
- Document which provider was used

---

## 7. Troubleshooting

### If .env not found
```bash
# Check it exists
ls -la /home/brian/projects/Digimons/.env

# Check it has GEMINI_API_KEY
grep GEMINI_API_KEY /home/brian/projects/Digimons/.env
```

### If Gemini API fails
```python
# Enable litellm debug mode
import litellm
litellm.set_verbose = True

# This will show the actual API request/response
```

### If Neo4j connection fails
```bash
# Verify Neo4j is running
docker ps | grep neo4j

# Test connection
python3 test_connections.py
```

---

## 8. Success Criteria

### Minimum for Completion
- [ ] Real Gemini extraction working (no mocks)
- [ ] DateTime serialization fixed (no warnings)  
- [ ] Dynamic chain discovery implemented
- [ ] All tests passing with real components

### Evidence Requirements
Each fix MUST produce evidence showing:
1. The problem before the fix (error messages)
2. The code changes made
3. The successful execution after fix
4. No regressions in other components

---

*Last Updated: 2025-08-27*
*Phase: Clean Vertical Slice - Issue Resolution*
*Priority: Fix critical issues preventing real LLM usage*