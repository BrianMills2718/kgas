# Type-Based Tool Composition - Phase 1 Fix & Validation

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
│   └── Evidence_Phase1_Fix_[Task].md   # Current fixes only
├── completed/
│   └── Evidence_POC_*.md              # Previous attempts (DO NOT MODIFY)
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"

---

## 2. Codebase Structure

### Key Entry Points
- `/tool_compatability/poc/demo.py` - Main demonstration script
- `/tool_compatability/poc/benchmark.py` - Performance testing
- `/tool_compatability/poc/verify_environment.py` - Service verification (TO CREATE)

### Module Organization
```
tool_compatability/poc/
├── base_tool.py          # Base class - metrics, fail-fast
├── data_types.py         # 10 semantic types (FILE, TEXT, ENTITIES, etc.)
├── registry.py           # Tool registry with NetworkX chain discovery
├── tools/
│   ├── text_loader.py    # ✅ TESTED: FILE → TEXT
│   ├── entity_extractor.py # ❌ NOT TESTED: TEXT → ENTITIES (needs Gemini)
│   └── graph_builder.py  # ❌ NOT TESTED: ENTITIES → GRAPH (needs Neo4j)
└── tests/
    ├── test_recovery.py  # ❌ BROKEN: AttributeError on tool_id
    ├── test_schema.py    # ❌ BROKEN: PydanticUserError on Enum
    └── benchmark.py      # ❌ BROKEN: StatisticsError on empty list
```

### Integration Points
- **Gemini API**: via `litellm` in EntityExtractor (requires GEMINI_API_KEY)
- **Neo4j**: via `neo4j-driver` in GraphBuilder (requires Docker container)
- **No ResourceOrchestrator** in this POC (different project component)

---

## 3. Related Documentation & Planning Files

### POC Planning Documents
- `/tool_compatability/poc/README.md` - Original POC design and rationale
- `/tool_compatability/poc/IMPLEMENTATION_CHECKLIST.md` - Detailed implementation tasks
- `/tool_compatability/PROOF_OF_CONCEPT_PLAN.md` - 8-day POC timeline
- `/tool_compatability/DECISION_DOCUMENT.md` - Why type-based approach chosen

### Background & Analysis
- `/tool_compatability/the_real_problem.md` - Root cause analysis of tool incompatibility
- `/tool_compatability/tool_refactoring_overview.md` - Previous refactoring attempts
- `/tool_compatability/ACCURATE_TOOL_INVENTORY.md` - Complete inventory of 38 tools
- `/tool_compatability/tool_disposition_plan.md` - Migration strategy for existing tools

### Previous Evidence (Completed)
- `/evidence/completed/Evidence_POC_Registry.md` - Registry implementation
- `/evidence/completed/Evidence_POC_Tools.md` - Tool implementations
- `/evidence/completed/Evidence_POC_Integration.md` - Integration testing
- `/evidence/completed/Evidence_POC_EdgeCases.md` - Edge case testing
- `/evidence/completed/Evidence_POC_Performance.md` - Performance analysis
- `/evidence/completed/Evidence_POC_Decision.md` - Phase 1 decision (conditional)

### Related Systems
- `/src/tools/phase2/t23c_llm_extractor.py` - Existing LLM extraction tool
- `/src/pipeline/kgas_pipeline.py` - KGAS pipeline implementation
- `/evidence/completed/DOUBLECHECK_KGAS_IMPLEMENTATION.md` - KGAS validation

---

## 4. Current Status: INCOMPLETE

### What Actually Works
- ✅ TextLoader processes files
- ✅ Registry finds chains
- ✅ Basic framework structure

### What's Broken
- ❌ EntityExtractor never tested
- ❌ GraphBuilder never tested
- ❌ Full chain never executed
- ❌ 3 test files have errors
- ❌ Performance criteria failed (101% > 20%)

### Critical Errors to Fix
1. `test_recovery.py`: Multiple `AttributeError: property 'tool_id' of 'X' object has no setter`
2. `test_schema.py:57-73`: `PydanticUserError: A non-annotated attribute was detected: Enum`
3. `benchmark.py:301`: `StatisticsError: mean requires at least one data point`

---

## 5. Task 1: Fix Code Errors (30 minutes)

### Fix 1.1: tool_id Property Errors

**File**: `/tool_compatability/poc/tests/test_recovery.py`

**Find and remove these lines**:
```python
# Line 268: Remove this
failing_extractor.tool_id = "FailingEntityExtractor"

# Line 353: Remove this
exhausted_tool.tool_id = "ResourceExhaustedTool"  

# Line 408: Remove this
tool.tool_id = "StateTracker"

# Line 435: Remove this
tool.tool_id = "StateTracker"
```

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_CodeErrors.md`
```bash
# Show the test now runs
python3 tests/test_recovery.py
# Paste full output including any remaining errors
```

### Fix 1.2: Pydantic Enum Error

**File**: `/tool_compatability/poc/tests/test_schema.py`

**Replace lines 57-73** with:
```python
from enum import Enum

# Define Enum outside of class
class EntityTypeV4(str, Enum):
    PERSON = "PERSON"
    ORG = "ORG"
    LOCATION = "LOCATION"
    OTHER = "OTHER"

class EntityV4(BaseModel):
    """V4: Made type an enum, added timestamp"""
    id: str
    text: str
    type: EntityTypeV4  # Use the external Enum
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_doc: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)
```

**Also fix lines 104-112** - Replace `EntityV4.EntityType` with `EntityTypeV4`

### Fix 1.3: Empty Statistics List

**File**: `/tool_compatability/poc/benchmark.py`

**Replace lines 299-310** with:
```python
# Benchmark compatibility checking
times_compat = []

# Try to test compatibility between different types
if tool_ids:  # Only if we have tools
    for _ in range(1000):  # Reduce iterations
        start = time.perf_counter()
        # Just test first tool with itself
        _ = registry.can_connect(tool_ids[0], tool_ids[0])
        times_compat.append(time.perf_counter() - start)

# Only calculate if we have data
if times_compat:
    compat_time = statistics.mean(times_compat) * 1_000_000
else:
    compat_time = 0.0  # No data available

results = {
    "tool_lookup_us": statistics.mean(times_lookup) * 1_000_000 if times_lookup else 0,
    "chain_discovery_us": statistics.mean(times_chain) * 1_000_000 if times_chain else 0,
    "compatibility_check_us": compat_time
}
```

---

## 6. Task 2: Environment Verification (10 minutes)

### Create Verification Script

**File**: Create `/tool_compatability/poc/verify_environment.py`

```python
#!/usr/bin/env python3
"""Verify which services are available for testing"""

import os
import sys

def check_neo4j():
    """Check if Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        driver.verify_connectivity()
        driver.close()
        return True, "Connected to Neo4j"
    except Exception as e:
        return False, str(e)

def check_gemini():
    """Check if Gemini API is accessible"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "GEMINI_API_KEY not set"
    
    try:
        import litellm
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return True, "Gemini API working"
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("ENVIRONMENT VERIFICATION")
    print("="*60)
    
    neo4j_ok, neo4j_msg = check_neo4j()
    print(f"Neo4j:  {'✅' if neo4j_ok else '❌'} {neo4j_msg}")
    
    gemini_ok, gemini_msg = check_gemini()
    print(f"Gemini: {'✅' if gemini_ok else '❌'} {gemini_msg}")
    
    print("="*60)
    
    if neo4j_ok and gemini_ok:
        print("Status: READY for full testing")
        print("Next: Run test_full_chain.py")
    elif neo4j_ok or gemini_ok:
        print("Status: PARTIAL testing possible")
        print("Next: Test available components only")
    else:
        print("Status: BLOCKED - No services available")
        print("\nTo setup Neo4j:")
        print("  docker run -d --name neo4j -p 7687:7687 \\")
        print("    -e NEO4J_AUTH=neo4j/devpassword neo4j:latest")
        print("\nTo setup Gemini:")
        print("  1. Visit https://makersuite.google.com/app/apikey")
        print("  2. export GEMINI_API_KEY='your-key'")
    
    return 0 if (neo4j_ok and gemini_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
```

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_Environment.md`
```bash
python3 verify_environment.py
# Paste COMPLETE output showing which services are available
```

---

## 7. Task 3: Test What's Available (1-2 hours)

### Path A: If BOTH Services Available

**File**: Create `/tool_compatability/poc/test_full_chain.py`

```python
#!/usr/bin/env python3
"""Test the complete chain with real services"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
from poc.tools.entity_extractor import EntityExtractor
from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataType, DataSchema

def test_chain():
    print("="*60)
    print("FULL CHAIN TEST")
    print("="*60)
    
    # Test document
    test_content = """
    John Smith is the CEO of TechCorp in San Francisco.
    The company raised $10M from Venture Partners.
    """
    
    test_file = "/tmp/test_chain.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Setup
    registry = ToolRegistry()
    registry.register(TextLoader())
    registry.register(EntityExtractor())  # Will fail without GEMINI_API_KEY
    registry.register(GraphBuilder())     # Will fail without Neo4j
    
    # Find chain
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    if not chains:
        print("❌ No chain found")
        return False
    
    print(f"Chain: {' → '.join(chains[0])}")
    
    # Execute
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type="text/plain"
    )
    
    current_data = file_data
    for tool_id in chains[0]:
        tool = registry.tools[tool_id]
        print(f"\nExecuting {tool_id}...")
        
        start = time.perf_counter()
        result = tool.process(current_data)
        duration = time.perf_counter() - start
        
        if not result.success:
            print(f"  ❌ Failed: {result.error}")
            return False
        
        print(f"  ✅ Success in {duration:.3f}s")
        
        # Show results
        if hasattr(result.data, 'content'):
            print(f"  Content: {result.data.content[:50]}...")
        elif hasattr(result.data, 'entities'):
            print(f"  Entities: {len(result.data.entities)}")
            for e in result.data.entities[:3]:
                print(f"    - {e.text} ({e.type})")
        elif hasattr(result.data, 'node_count'):
            print(f"  Graph: {result.data.node_count} nodes, {result.data.edge_count} edges")
        
        current_data = result.data
    
    print("\n" + "="*60)
    print("✅ FULL CHAIN SUCCESSFUL")
    return True

if __name__ == "__main__":
    success = test_chain()
    sys.exit(0 if success else 1)
```

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_FullChain.md`
```bash
python3 test_full_chain.py
# Paste COMPLETE output including all tool executions and timings
```

### Path B: If Only TextLoader Works

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_TextLoaderOnly.md`
```bash
python3 demo.py
# Paste output showing TextLoader works

python3 benchmark.py
# Paste performance results
```

### Path C: If Nothing Works

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_Blocked.md`
```
Document exact errors when trying to:
1. Start Neo4j
2. Set GEMINI_API_KEY
3. Run any tests
```

---

## 8. Task 4: Performance Validation (30 minutes)

**Only if Task 3 Path A succeeded**

**File**: Create `/tool_compatability/poc/validate_performance.py`

```python
#!/usr/bin/env python3
"""Measure real performance with actual services"""

import time
import statistics
# ... implement as shown in previous CLAUDE.md

def measure_direct():
    """Direct API calls without framework"""
    # Time raw Gemini + Neo4j calls
    pass

def measure_framework():
    """Same operations through framework"""
    # Time full chain execution
    pass

# Compare and calculate overhead percentage
```

**Evidence Required**: `evidence/current/Evidence_Phase1_Fix_Performance.md`
- Show at least 5 iterations
- Calculate mean times
- Show overhead percentage
- Mark PASS (<20%) or FAIL (>20%)

---

## 9. Task 5: Final Honest Assessment (30 minutes)

**File**: Create `evidence/current/Evidence_Phase1_Fix_FINAL.md`

```markdown
# Phase 1 Final Assessment

## What Was Actually Tested
| Component | Attempted | Result | Evidence |
|-----------|-----------|--------|----------|
| TextLoader | Yes | [✅/❌] | [file:line] |
| EntityExtractor | [Yes/No] | [✅/❌/NOT TESTED] | [file:line or "No service"] |
| GraphBuilder | [Yes/No] | [✅/❌/NOT TESTED] | [file:line or "No service"] |
| Full Chain | [Yes/No] | [✅/❌/NOT TESTED] | [file:line or "No service"] |

## Performance Results
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Overhead | <20% | [X% or "NOT TESTED"] | [✅/❌/N/A] |

## Known Issues
1. [List all unresolved problems]

## Recommendation
[One of these]:
- GO: All tests passed, ready for production
- CONDITIONAL GO: Core works, needs [specific requirements]
- BLOCKED: Cannot proceed without [specific services/fixes]
- NO GO: Fundamental issues found [list them]
```

---

## 10. Success Criteria

### Minimum Success (Fix & Document)
- ✅ All code errors fixed
- ✅ Tests run without crashes
- ✅ Honest documentation of what works/doesn't

### Target Success (Validate Core)
- ✅ At least one full chain execution
- ✅ Real performance measured
- ✅ Clear go/no-go decision

### Full Success (Production Ready)
- ✅ 10+ successful chain executions
- ✅ Performance <20% overhead
- ✅ 1MB document processed

---

## 11. Common Issues & Solutions

### Docker/Neo4j Issues
```bash
# If "connection refused"
docker ps  # Check if running
docker logs neo4j  # Check for errors

# If "authentication failed"  
docker exec -it neo4j cypher-shell
# Default: neo4j/neo4j, then change to devpassword
```

### Gemini API Issues
```bash
# If "API key not valid"
echo $GEMINI_API_KEY  # Check format
curl -H "x-goog-api-key: $GEMINI_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models"
# Should list available models
```

### Python Import Issues
```bash
pip install litellm neo4j pydantic networkx psutil
export PYTHONPATH=/home/brian/projects/Digimons/tool_compatability:$PYTHONPATH
```

---

*Last Updated: 2025-01-25*
*Phase: 1 - Fix and Validation*
*Status: Awaiting fixes and service verification*
*Timeline: 2-3 hours to complete*