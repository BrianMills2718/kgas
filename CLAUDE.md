# Type-Based Tool Composition - Phase 2: Service Integration Validation

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them  
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **TEST DRIVEN DESIGN**: Write tests first, then implementation

### Evidence Requirements
Every implementation MUST generate evidence files:
```
evidence/
├── current/
│   └── Evidence_Phase2_[Task].md    # Current Phase 2 work only
├── completed/
│   └── Evidence_POC_*.md           # Phase 1 POC files (DO NOT MODIFY)
```

Evidence files must contain:
- Raw execution logs (not summaries)
- Actual error messages when things fail
- Performance metrics with timestamps
- No success claims without demonstrable proof

---

## 2. Codebase Structure

### Phase 1 Completed (DO NOT MODIFY)
```
tool_compatability/poc/
├── base_tool.py              # ✅ Base class with metrics
├── data_types.py             # ✅ 10 semantic types defined
├── registry.py               # ✅ Tool registry with chain discovery
├── tools/
│   ├── text_loader.py        # ✅ FILE → TEXT (tested)
│   ├── entity_extractor.py   # ⚠️ TEXT → ENTITIES (untested - needs Gemini)
│   └── graph_builder.py      # ⚠️ ENTITIES → GRAPH (untested - needs Neo4j)
├── tests/
│   ├── test_integration.py   # ✅ 12 tests passing (TextLoader only)
│   ├── test_memory.py        # ✅ Memory leak testing
│   ├── test_recovery.py      # ✅ Failure recovery testing
│   └── test_schema.py        # ✅ Schema evolution testing
├── benchmark.py              # ✅ Performance benchmarking
└── demo.py                   # ✅ Main demonstration (partial)

evidence/completed/
├── Evidence_POC_Registry.md     # Phase 1: Registry implementation
├── Evidence_POC_Tools.md        # Phase 1: Tool implementations
├── Evidence_POC_Integration.md  # Phase 1: Integration tests
├── Evidence_POC_EdgeCases.md    # Phase 1: Edge case testing
├── Evidence_POC_Performance.md  # Phase 1: Performance analysis
└── Evidence_POC_Decision.md     # Phase 1: Conditional GO decision
```

### Phase 1 Status
- **Architecture**: ✅ Validated
- **TextLoader**: ✅ Fully tested (FILE → TEXT)
- **EntityExtractor**: ⚠️ Code complete, untested (needs GEMINI_API_KEY)
- **GraphBuilder**: ⚠️ Code complete, untested (needs Neo4j)
- **Performance**: ✅ 0.114ms overhead measured (acceptable)

---

## 3. Phase 2: Service Integration Validation

### CRITICAL REQUIREMENT
Phase 1 proved the concept works but **DID NOT** test with real services. Phase 2 **MUST** complete integration testing before production approval.

### Task 1: Environment Verification (30 minutes)

**File**: Create `/tool_compatability/poc/verify_environment.py`

```python
#!/usr/bin/env python3
"""Verify all required services are available"""

import os
import sys
from neo4j import GraphDatabase
import litellm

def check_neo4j():
    """Verify Neo4j is running and accessible"""
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        driver.verify_connectivity()
        driver.close()
        return True, "Neo4j connected successfully"
    except Exception as e:
        return False, f"Neo4j error: {e}"

def check_gemini():
    """Verify Gemini API is accessible"""
    if not os.getenv("GEMINI_API_KEY"):
        return False, "GEMINI_API_KEY not set"
    
    try:
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": "Say 'ok'"}],
            max_tokens=10
        )
        return True, "Gemini API working"
    except Exception as e:
        return False, f"Gemini error: {e}"

def main():
    print("Environment Verification")
    print("=" * 50)
    
    # Check Neo4j
    neo4j_ok, neo4j_msg = check_neo4j()
    print(f"Neo4j: {'✅' if neo4j_ok else '❌'} {neo4j_msg}")
    
    # Check Gemini
    gemini_ok, gemini_msg = check_gemini()
    print(f"Gemini: {'✅' if gemini_ok else '❌'} {gemini_msg}")
    
    # Overall status
    if neo4j_ok and gemini_ok:
        print("\n✅ All services available - proceed to Task 2")
        return 0
    else:
        print("\n❌ Services missing - see setup instructions below")
        if not neo4j_ok:
            print("\nTo start Neo4j:")
            print("  docker run -d --name neo4j -p 7687:7687 -p 7474:7474 \\")
            print("    -e NEO4J_AUTH=neo4j/devpassword neo4j:latest")
        if not gemini_ok:
            print("\nTo get Gemini API key:")
            print("  1. Visit https://makersuite.google.com/app/apikey")
            print("  2. Create new API key")
            print("  3. export GEMINI_API_KEY='your-key-here'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Evidence Required**: Create `evidence/current/Evidence_Phase2_Environment.md`
- Include full output of verify_environment.py
- Document which services are available
- If services missing, document setup steps taken

### Task 2: Full Chain Execution (1 hour)

**PREREQUISITE**: Task 1 must show all services available

**File**: Create `/tool_compatability/poc/test_full_chain.py`

```python
#!/usr/bin/env python3
"""Test complete chain with real services"""

import os
import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
from poc.tools.entity_extractor import EntityExtractor
from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataType, DataSchema

def test_full_chain():
    """Execute FILE → TEXT → ENTITIES → GRAPH with real services"""
    
    # Create test document
    test_content = """
    Nexora Corporation Announces Strategic Partnership
    
    SAN FRANCISCO - Nexora Corporation, led by CEO Sarah Mitchell, 
    announced a partnership with TechVentures International today.
    The deal, worth $50 million, will accelerate quantum computing
    development. CTO Emily Chen will lead the joint research team
    in Palo Alto, California.
    """
    
    # Save test file
    test_file = "/tmp/phase2_test.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print("Full Chain Execution Test")
    print("=" * 50)
    
    # Initialize registry and tools
    registry = ToolRegistry()
    
    # Register all tools (MUST use real services)
    text_loader = TextLoader()
    entity_extractor = EntityExtractor()  # Requires GEMINI_API_KEY
    graph_builder = GraphBuilder()        # Requires Neo4j
    
    registry.register(text_loader)
    registry.register(entity_extractor)
    registry.register(graph_builder)
    
    # Find chain
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    if not chains:
        print("❌ No chain found")
        return False
    
    chain = chains[0]
    print(f"Chain: {' → '.join(chain)}")
    
    # Execute chain
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type="text/plain"
    )
    
    current_data = file_data
    timings = []
    
    for tool_id in chain:
        tool = registry.tools[tool_id]
        print(f"\nExecuting {tool_id}...")
        
        start = time.perf_counter()
        result = tool.process(current_data)
        duration = time.perf_counter() - start
        timings.append((tool_id, duration))
        
        if not result.success:
            print(f"  ❌ Failed: {result.error}")
            return False
        
        print(f"  ✅ Success in {duration:.3f}s")
        
        # Show intermediate results
        if hasattr(result.data, 'entities'):
            print(f"  Entities found: {len(result.data.entities)}")
            for e in result.data.entities[:3]:
                print(f"    - {e.text} ({e.type})")
        elif hasattr(result.data, 'node_count'):
            print(f"  Graph created: {result.data.node_count} nodes, {result.data.edge_count} edges")
        
        current_data = result.data
    
    # Summary
    print("\n" + "=" * 50)
    print("Chain Execution Complete!")
    print(f"Total time: {sum(d for _, d in timings):.3f}s")
    for tool, duration in timings:
        print(f"  {tool}: {duration:.3f}s")
    
    return True

if __name__ == "__main__":
    success = test_full_chain()
    sys.exit(0 if success else 1)
```

**Evidence Required**: Create `evidence/current/Evidence_Phase2_FullChain.md`
- Include complete execution log
- Show all intermediate outputs
- Document actual timings for each tool
- Include any error messages if failures occur

### Task 3: Performance Validation (1 hour)

**PREREQUISITE**: Task 2 must complete successfully

**File**: Create `/tool_compatability/poc/validate_performance.py`

```python
#!/usr/bin/env python3
"""Validate performance with real services"""

import os
import sys
import time
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
from poc.tools.entity_extractor import EntityExtractor
from poc.tools.graph_builder import GraphBuilder
from poc.data_types import DataType, DataSchema

def measure_direct_api_calls(test_content: str, iterations: int = 10):
    """Measure performance of direct API calls without framework"""
    import litellm
    from neo4j import GraphDatabase
    
    times = []
    for i in range(iterations):
        start = time.perf_counter()
        
        # Direct Gemini call
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{
                "role": "user", 
                "content": f"Extract entities from: {test_content}"
            }],
            max_tokens=1000
        )
        
        # Direct Neo4j write
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        with driver.session() as session:
            session.run("CREATE (n:TestEntity {text: $text})", text="test")
        driver.close()
        
        duration = time.perf_counter() - start
        times.append(duration)
        print(f"  Direct iteration {i+1}: {duration:.3f}s")
    
    return times

def measure_framework_calls(test_file: str, iterations: int = 10):
    """Measure performance through framework"""
    registry = ToolRegistry()
    registry.register(TextLoader())
    registry.register(EntityExtractor())
    registry.register(GraphBuilder())
    
    times = []
    for i in range(iterations):
        file_data = DataSchema.FileData(
            path=test_file,
            size_bytes=os.path.getsize(test_file),
            mime_type="text/plain"
        )
        
        chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
        chain = chains[0]
        
        start = time.perf_counter()
        current_data = file_data
        for tool_id in chain:
            tool = registry.tools[tool_id]
            result = tool.process(current_data)
            if not result.success:
                raise RuntimeError(f"Tool {tool_id} failed")
            current_data = result.data
        
        duration = time.perf_counter() - start
        times.append(duration)
        print(f"  Framework iteration {i+1}: {duration:.3f}s")
    
    return times

def main():
    # Test content
    test_content = "John Smith is the CEO of TechCorp in San Francisco."
    test_file = "/tmp/perf_test.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print("Performance Validation")
    print("=" * 50)
    
    print("\nDirect API Calls (10 iterations):")
    direct_times = measure_direct_api_calls(test_content)
    
    print("\nFramework Calls (10 iterations):")
    framework_times = measure_framework_calls(test_file)
    
    # Analysis
    direct_mean = statistics.mean(direct_times)
    framework_mean = statistics.mean(framework_times)
    overhead = ((framework_mean - direct_mean) / direct_mean) * 100
    
    print("\n" + "=" * 50)
    print("Results:")
    print(f"Direct mean: {direct_mean:.3f}s")
    print(f"Framework mean: {framework_mean:.3f}s")
    print(f"Overhead: {overhead:.1f}%")
    
    if overhead < 20:
        print(f"✅ PASS: Overhead {overhead:.1f}% is below 20% threshold")
    else:
        print(f"❌ FAIL: Overhead {overhead:.1f}% exceeds 20% threshold")

if __name__ == "__main__":
    main()
```

**Evidence Required**: Create `evidence/current/Evidence_Phase2_Performance.md`
- Show 10 iterations of timing data
- Calculate mean, median, std deviation
- Compare framework vs direct API calls
- Determine if <20% overhead requirement is met

### Task 4: Large Document Test (30 minutes)

**PREREQUISITE**: Task 2 must complete successfully

Create and test with progressively larger documents to find limits.

**File**: Create `/tool_compatability/poc/test_large_documents.py`

Test with:
- 1KB document
- 100KB document  
- 1MB document
- 10MB document

**Evidence Required**: Create `evidence/current/Evidence_Phase2_LargeFiles.md`
- Document maximum size successfully processed
- Show memory usage for each size
- Include any failure messages

### Task 5: Final Decision (30 minutes)

**File**: Create `evidence/current/Evidence_Phase2_Decision.md`

Template:
```markdown
# Phase 2 Final Decision

## Environment Status
- Neo4j: [✅/❌] [details from Task 1]
- Gemini API: [✅/❌] [details from Task 1]

## Test Results
| Test | Target | Actual | Pass |
|------|--------|--------|------|
| Full chain execution | Works | [result] | [✅/❌] |
| Performance overhead | <20% | [value]% | [✅/❌] |
| 10MB document | Processes | [result] | [✅/❌] |
| No memory leaks | 0MB growth | [value]MB | [✅/❌] |

## Evidence References
- Environment: Evidence_Phase2_Environment.md
- Full chain: Evidence_Phase2_FullChain.md
- Performance: Evidence_Phase2_Performance.md
- Large files: Evidence_Phase2_LargeFiles.md

## Decision: [GO/NO-GO/BLOCKED]

### Rationale
[Evidence-based rationale for decision]

### If BLOCKED
[Specific steps needed to unblock]

### If GO
[Next steps for production migration]
```

---

## 4. Setup Instructions

### Neo4j Setup
```bash
# Check if running
docker ps | grep neo4j

# If not running, start it
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest

# Wait for startup (30 seconds)
sleep 30

# Verify connection
docker logs neo4j | grep "Started"
```

### Gemini API Setup
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Export it:
```bash
export GEMINI_API_KEY='your-key-here'
# Verify
echo $GEMINI_API_KEY
```

### Python Dependencies
```bash
pip install litellm neo4j pydantic networkx psutil
```

---

## 5. Success Criteria

**Phase 2 completes successfully if**:
- ✓ All three tools work with real services
- ✓ Full chain executes FILE → TEXT → ENTITIES → GRAPH
- ✓ Performance overhead <20% with real operations
- ✓ Can process 10MB documents
- ✓ No memory leaks over 10 iterations

**Phase 2 fails if**:
- ✗ Cannot connect to required services
- ✗ Performance overhead >50% with real operations
- ✗ Cannot process 5MB documents
- ✗ Memory leaks detected

---

## 6. Timeline

**Total Time Required**: ~4 hours

| Task | Time | Dependencies |
|------|------|--------------|
| Environment setup | 30 min | Docker, API key |
| Full chain test | 1 hour | Services ready |
| Performance validation | 1 hour | Chain working |
| Large document test | 30 min | Chain working |
| Final decision | 30 min | All tests complete |

---

## 7. Common Issues & Solutions

### Neo4j Connection Refused
```bash
# Check if container exists
docker ps -a | grep neo4j

# Remove old container if exists
docker rm -f neo4j

# Start fresh
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest
```

### Gemini API Error
```bash
# Verify key is set
echo $GEMINI_API_KEY

# Test with curl
curl -H "Content-Type: application/json" \
     -H "x-goog-api-key: $GEMINI_API_KEY" \
     -X POST \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
     "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
```

---

## 8. Next Steps After Phase 2

**If Phase 2 succeeds (GO)**:
- Phase 3: Migrate high-value tools (T23C, T31, T34)
- Phase 4: Migrate remaining 35 tools
- Phase 5: Deprecate old system

**If Phase 2 blocked**:
- Document specific blockers
- Estimate time to resolve
- Consider alternative services (OpenAI, PostgreSQL)

**If Phase 2 fails**:
- Analyze root cause
- Consider architectural changes
- Document lessons learned

---

*Last Updated: 2025-01-25*
*Current Phase: 2 - Service Integration Validation*
*Phase 1 Status: Complete (Architecture Validated)*
*Phase 2 Status: Not Started - Awaiting Service Setup*