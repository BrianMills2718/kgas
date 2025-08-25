# PhD Tool Composition System - Implementation Phase

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
│   └── Evidence_Week1_[Task].md   # Current week only
├── completed/
│   └── Evidence_POC_*.md          # Previous POC phase (DO NOT MODIFY)
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"
- Test the 50MB PDF scenario to expose issues

---

## 2. Codebase Structure

### Key Entry Points
- `/tool_compatability/poc/` - Main POC directory
- `/tool_compatability/poc/demo.py` - Basic demonstration
- `/tool_compatability/poc/test_full_chain.py` - Full chain test with Gemini

### Core Modules
```
tool_compatability/poc/
├── base_tool.py          # Base class - needs multi-input support
├── data_types.py         # 10 types - needs schema versioning
├── registry.py           # Tool registry - works but needs semantic types
├── tools/
│   ├── text_loader.py    # ✅ Working
│   ├── entity_extractor.py # ✅ Working with Gemini API
│   └── graph_builder.py  # ✅ Working with Neo4j
└── tests/
    └── test_critical_issues.py # TO CREATE - Test 50MB PDF scenario
```

### Planning Documents
- `/tool_compatability/poc/CRITICAL_ISSUES_POC_PLAN.md` - Detailed fixes for 5 issues
- `/tool_compatability/poc/PHD_IMPLEMENTATION_PLAN.md` - 12-week research plan
- `/tool_compatability/METHODICAL_IMPLEMENTATION_PLAN.md` - Week-by-week breakdown

### Integration Points
- **Gemini API**: Key in `.env` file, auto-loaded via python-dotenv
- **Neo4j**: Docker container at bolt://localhost:7687
- **No ResourceOrchestrator** in POC (different project component)

---

## 3. Current Status

### What Works
- ✅ Basic chain: FILE → TEXT → ENTITIES → GRAPH
- ✅ Type-based composition proven
- ✅ Automatic chain discovery functional
- ✅ All 3 tools execute successfully

### Critical Issues Identified (Must Fix)
1. **No Multi-Input Support** - Can't pass ontology to EntityExtractor
2. **No Schema Versioning** - Changing Entity breaks everything
3. **No Memory Management** - 50MB PDF will cause OOM
4. **No Semantic Types** - Can't distinguish social vs chemical graphs
5. **No State Management** - Partial failures leave Neo4j inconsistent

---

## 4. Week 1 Tasks: Fix Critical Issues

### Day 1: Multi-Input Support (PRIORITY 1)

#### Context
Tools need multiple inputs (text + ontology + config), but current system only supports single input/output.

#### Implementation Tasks

**Task 1.1: Create ToolContext** (2 hours)
```python
# File: /tool_compatability/poc/tool_context.py
from typing import Dict, Any
from pydantic import BaseModel

class ToolContext(BaseModel):
    """Carries primary data and auxiliary inputs through chain"""
    primary_data: Any  # Main data flowing through
    parameters: Dict[str, Dict[str, Any]] = {}  # Tool-specific params
    shared_context: Dict[str, Any] = {}  # Shared across all tools
    
    def get_param(self, tool_id: str, param_name: str, default=None):
        return self.parameters.get(tool_id, {}).get(param_name, default)
    
    def set_param(self, tool_id: str, param_name: str, value: Any):
        if tool_id not in self.parameters:
            self.parameters[tool_id] = {}
        self.parameters[tool_id][param_name] = value
```

**Task 1.2: Update BaseTool** (2 hours)
- Modify `base_tool.py` to accept ToolContext
- Keep backward compatibility
- Update process() signature

**Task 1.3: Test Multi-Input** (1 hour)
```python
# File: /tool_compatability/poc/tests/test_multi_input.py
def test_entity_extraction_with_ontology():
    """Prove we can pass custom ontology"""
    context = ToolContext()
    context.primary_data = TextData(content="John works at Apple")
    context.set_param("EntityExtractor", "ontology", {
        "PERSON": ["name", "role"],
        "COMPANY": ["name", "industry"]
    })
    
    extractor = EntityExtractorV2()
    result = extractor.process(context)
    
    # Evidence: Show ontology was used
    assert "ontology" in extractor.last_prompt  # Capture prompt for evidence
    print(f"Entities found: {result.primary_data.entities}")
```

**Evidence Required**: `evidence/current/Evidence_Week1_MultiInput.md`
```bash
# Run test and capture output
python3 tests/test_multi_input.py
# Show that custom ontology affected extraction
# Include the actual prompt sent to Gemini
```

### Day 2: Schema Versioning

#### Context
When Entity schema changes, all tools break. Need migration system.

#### Implementation Tasks

**Task 2.1: Create Versioned Schemas** (2 hours)
```python
# File: /tool_compatability/poc/schema_versions.py
class EntityV1(BaseModel):
    """Version 1.0.0"""
    _version = "1.0.0"
    id: str
    text: str
    type: str

class EntityV2(BaseModel):
    """Version 2.0.0 - Added confidence"""
    _version = "2.0.0"
    id: str
    text: str
    type: str
    confidence: float = 0.5
```

**Task 2.2: Migration System** (2 hours)
```python
# File: /tool_compatability/poc/migrations.py
class SchemaMigrator:
    @classmethod
    def migrate_v1_to_v2(cls, entity: EntityV1) -> EntityV2:
        return EntityV2(..., confidence=0.5)  # Default value
```

**Task 2.3: Test Migration Chain** (1 hour)
- Create V1 entity
- Migrate to V2, then V3
- Verify data preserved

**Evidence Required**: `evidence/current/Evidence_Week1_SchemaVersioning.md`

### Day 3: Memory Management

#### Context
50MB PDFs cause OOM. Need streaming/references.

#### Implementation Tasks

**Task 3.1: Create DataReference** (2 hours)
```python
# File: /tool_compatability/poc/data_references.py
class DataReference(BaseModel):
    storage_type: str  # "filesystem", "s3"
    location: str
    size_bytes: int
    
    def stream(self, chunk_size=1024*1024):
        """Stream data in chunks"""
        with open(self.location, 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk
```

**Task 3.2: Test 50MB PDF** (3 hours)
```python
# File: /tool_compatability/poc/tests/test_50mb_pdf.py
def test_large_pdf_processing():
    """THIS TEST MUST FAIL FIRST, THEN PASS AFTER FIX"""
    
    # Create 50MB test PDF
    create_large_pdf("/tmp/test_50mb.pdf", size_mb=50)
    
    # Try current approach (WILL FAIL WITH OOM)
    try:
        loader = TextLoader()
        result = loader.process(FileData(path="/tmp/test_50mb.pdf"))
        print("ERROR: Should have failed with OOM!")
    except MemoryError as e:
        print(f"✅ Expected failure: {e}")
    
    # Try streaming approach (SHOULD WORK)
    loader_v2 = StreamingTextLoader()
    result = loader_v2.process(FileData(path="/tmp/test_50mb.pdf"))
    assert result.reference is not None  # Using reference, not embedded
    print("✅ 50MB PDF processed via streaming")
```

**Evidence Required**: `evidence/current/Evidence_Week1_MemoryManagement.md`
- Show OOM error with current approach
- Show successful processing with streaming
- Include memory usage stats

### Day 4: Semantic Compatibility

#### Context
Type matching isn't enough - social graphs ≠ chemical graphs.

#### Implementation Tasks

**Task 4.1: Create SemanticType** (2 hours)
```python
# File: /tool_compatability/poc/semantic_types.py
class SemanticType(BaseModel):
    base_type: DataType  # GRAPH
    domain: str  # "social", "chemical"
    
    def is_compatible_with(self, other):
        return self.base_type == other.base_type and \
               self.domain == other.domain
```

**Task 4.2: Test Incompatibility** (1 hour)
- Create SocialGraphExtractor (outputs social graph)
- Create ChemicalAnalyzer (expects chemical graph)
- Verify they're rejected as incompatible

**Evidence Required**: `evidence/current/Evidence_Week1_SemanticTypes.md`

### Day 5: State Management

#### Context
Failures leave partial data in Neo4j. Need transactions.

#### Implementation Tasks

**Task 5.1: Transactional Executor** (3 hours)
```python
# File: /tool_compatability/poc/transactions.py
class TransactionalExecutor:
    def execute_with_rollback(self, chain, context):
        completed = []
        try:
            for tool in chain:
                result = tool.process(context)
                completed.append((tool, result))
            return result
        except Exception as e:
            # Rollback in reverse order
            for tool, result in reversed(completed):
                tool.rollback(result)
            raise e
```

**Task 5.2: Test Rollback** (2 hours)
- Execute chain that fails at GraphBuilder
- Verify Neo4j was cleaned up
- Check no partial data remains

**Evidence Required**: `evidence/current/Evidence_Week1_StateManagement.md`

---

## 5. Integration Test (End of Week 1)

### The Complete Scenario Test

```python
# File: /tool_compatability/poc/tests/test_complete_scenario.py
def test_all_critical_issues_resolved():
    """
    The ultimate test combining all fixes:
    1. Load 50MB PDF (memory management)
    2. Extract with custom ontology (multi-input)
    3. Handle schema migration (versioning)
    4. Check semantic compatibility (semantic types)
    5. Rollback on failure (transactions)
    """
    
    # This test MUST work after all fixes
    # Document each step with evidence
```

**Evidence Required**: `evidence/current/Evidence_Week1_Integration.md`

---

## 6. Success Criteria

### Each Day Must Produce:
1. Working code (no mocks/stubs)
2. Test that proves it works
3. Evidence file with execution logs
4. Clear documentation of issues found

### Week 1 Complete When:
- [ ] 50MB PDF processes without OOM
- [ ] Custom ontology affects extraction
- [ ] Schema migrations work V1→V2→V3
- [ ] Incompatible semantic types rejected
- [ ] Failed operations roll back cleanly

---

## 7. Common Issues & Solutions

### If Gemini API fails:
```bash
# Check API key loaded
python3 -c "import os; print(os.getenv('GEMINI_API_KEY')[:10])"
# Should show: AIzaSyDXaL...
```

### If Neo4j connection fails:
```bash
# Check Docker running
docker ps | grep neo4j
# Restart if needed
docker restart neo4j
```

### If OOM occurs:
```bash
# Monitor memory during test
watch -n 1 free -h
# In another terminal, run test
```

---

## 8. Daily Workflow

### Morning:
1. Read today's tasks in CLAUDE.md
2. Write test FIRST (TDD)
3. Run test, see it fail
4. Implement solution
5. Run test, see it pass

### Afternoon:
6. Create evidence file
7. Include raw terminal output
8. Document any issues found
9. Commit with descriptive message

### End of Day:
10. Update CLAUDE.md if needed
11. Archive completed evidence
12. Plan tomorrow's work

---

## 9. Next Phase (Week 2)

After Week 1 fixes complete:
1. Expand to 20+ tools
2. Add branching/parallel execution
3. Build composition agent
4. Performance optimization
5. Begin benchmarking

See `/tool_compatability/poc/PHD_IMPLEMENTATION_PLAN.md` for full timeline.

---

*Last Updated: 2025-01-25*
*Phase: Week 1 - Critical Issues*
*Status: Ready to implement multi-input support*