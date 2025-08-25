# Type-Based Tool Composition - Implementation Guide

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them  
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **TEST DRIVEN DESIGN**: Write tests first, then implementation
- **DIRECT DATA PASSING**: Pass actual data, not references (except graphs in Neo4j)

### Evidence Requirements
Every implementation MUST generate evidence files:
```
evidence/
├── current/
│   └── Evidence_POC_[Component].md  # Current POC work only
├── completed/
│   └── Evidence_KGAS_Pipeline.md    # Completed KGAS implementation
```

Evidence files must contain:
- Raw execution logs (not summaries)
- Actual error messages when things fail
- Performance metrics with timestamps
- No success claims without demonstrable proof

---

## 2. Codebase Structure

### Completed: KGAS Pipeline
```
src/
├── tools/phase2/
│   └── t23c_llm_extractor.py      # Real Gemini LLM extraction (no mocks)
├── pipeline/
│   └── kgas_pipeline.py           # Document → LLM → Neo4j → Query
└── tests/
    └── test_real_llm_pipeline.py  # End-to-end validation

evidence/completed/
├── pipeline_end_to_end.json       # Test results with metrics
├── llm_extraction_nexora.json     # Raw LLM responses
└── DOUBLECHECK_KGAS_IMPLEMENTATION.md
```

**Status**: ✅ Working with Gemini-2.0-flash-exp, Neo4j storage, query system functional

### In Progress: Tool Compatibility POC
```
tool_compatability/
├── PROOF_OF_CONCEPT_PLAN.md       # Comprehensive 8-day plan
├── DECISION_DOCUMENT.md           # Why type-based > ORM
├── poc/
│   ├── data_types.py             # ✅ 10 semantic types defined
│   ├── base_tool.py              # ✅ Base class with metrics
│   ├── registry.py               # TODO: Tool registry & chain discovery
│   ├── tools/                    # TODO: Three test tools
│   │   ├── text_loader.py       # TODO: FILE → TEXT
│   │   ├── entity_extractor.py  # TODO: TEXT → ENTITIES  
│   │   └── graph_builder.py     # TODO: ENTITIES → GRAPH
│   ├── tests/                    # TODO: Edge case testing
│   └── demo.py                   # TODO: Main demonstration
```

---

## 3. Current Mission: Type-Based Tool Composition POC

### The Problem
- 38 poorly-factored tools with incompatible interfaces
- Field name matching doesn't work (entities vs extracted_entities)
- 5 previous approaches failed (God object, type matching, accumulation, contracts, ORM)
- Tools factored at wrong boundaries (T31/T34 should be internal to T23C)

### The Solution
**Type-based composition with exact schemas**:
1. ~10 semantic types (TEXT, ENTITIES, GRAPH, etc.)
2. Each type has ONE exact Pydantic schema
3. Tools declare input/output types
4. Type matching enables automatic compatibility

---

## 4. Implementation Instructions (Day 1)

### Task 1: Create Tool Registry (Morning)

**File**: `/tool_compatability/poc/registry.py`

```python
from typing import Dict, List, Set, Tuple
import networkx as nx
from .base_tool import BaseTool
from .data_types import DataType, are_types_compatible

class ToolRegistry:
    """Registry with automatic chain discovery"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.compatibility_cache: Dict[Tuple[str, str], bool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool"""
        self.tools[tool.tool_id] = tool
        self.compatibility_cache.clear()
    
    def can_connect(self, tool1_id: str, tool2_id: str) -> bool:
        """Check if tool1 output feeds tool2 input"""
        cache_key = (tool1_id, tool2_id)
        if cache_key in self.compatibility_cache:
            return self.compatibility_cache[cache_key]
        
        tool1 = self.tools.get(tool1_id)
        tool2 = self.tools.get(tool2_id)
        
        if not tool1 or not tool2:
            return False
        
        # Simple type matching
        compatible = are_types_compatible(tool1.output_type, tool2.input_type)
        self.compatibility_cache[cache_key] = compatible
        return compatible
    
    def find_chains(self, start_type: DataType, end_type: DataType) -> List[List[str]]:
        """Find all valid tool chains"""
        # Build graph
        G = nx.DiGraph()
        for tool_id in self.tools:
            G.add_node(tool_id)
        
        for t1 in self.tools:
            for t2 in self.tools:
                if self.can_connect(t1, t2):
                    G.add_edge(t1, t2)
        
        # Find paths
        chains = []
        start_tools = [t for t, tool in self.tools.items() 
                      if tool.input_type == start_type]
        end_tools = [t for t, tool in self.tools.items() 
                    if tool.output_type == end_type]
        
        for start in start_tools:
            for end in end_tools:
                try:
                    paths = nx.all_simple_paths(G, start, end, cutoff=5)
                    chains.extend(list(paths))
                except nx.NetworkXNoPath:
                    pass
        
        return chains
```

**Test**: Create `test_registry.py` to verify registration and chain discovery work.

### Task 2: Implement TextLoader (Afternoon)

**File**: `/tool_compatability/poc/tools/text_loader.py`

```python
from pathlib import Path
from poc.base_tool import BaseTool
from poc.data_types import DataType, DataSchema

class TextLoaderConfig(BaseModel):
    max_size_mb: float = 10.0
    encoding: str = "utf-8"

class TextLoader(BaseTool):
    @property
    def input_type(self) -> DataType:
        return DataType.FILE
    
    @property
    def output_type(self) -> DataType:
        return DataType.TEXT
    
    def _execute(self, input_data: DataSchema.FileData) -> DataSchema.TextData:
        path = Path(input_data.path)
        
        # Size check
        size_mb = input_data.size_bytes / (1024 * 1024)
        if size_mb > self.config.max_size_mb:
            raise ValueError(f"File too large: {size_mb:.1f}MB")
        
        # Read file
        with open(path, 'r', encoding=self.config.encoding) as f:
            content = f.read()
        
        return DataSchema.TextData.from_string(content)
```

### Task 3: Create Demo Script

**File**: `/tool_compatability/poc/demo.py`

```python
#!/usr/bin/env python3
"""POC Demo - Shows type-based tool composition"""

from poc.registry import ToolRegistry
from poc.tools.text_loader import TextLoader
# Import other tools as implemented

def main():
    # Initialize registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(TextLoader())
    # Register other tools
    
    # Show compatibility matrix
    print(registry.visualize_compatibility())
    
    # Find chains
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    print(f"Found {len(chains)} chains from FILE to GRAPH")
    
    # Execute a chain
    # ... implementation

if __name__ == "__main__":
    main()
```

---

## 5. Testing Protocol

### Day 1: Basic Functionality
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc
python -m pytest tests/test_registry.py -v
python demo.py  # Should show compatibility matrix
```

### Day 5-6: Edge Cases
```bash
python tests/test_memory.py     # Find memory limits
python tests/test_recovery.py   # Test failure recovery
python tests/test_schema.py     # Schema evolution
```

### Day 7: Performance
```bash
python benchmark.py
# Success: <20% overhead vs direct calls
```

---

## 6. Evidence Requirements

### For Each Component
Create: `evidence/current/Evidence_POC_[Component].md`

Template:
```markdown
# Evidence: [Component] Implementation

## Execution Log
```
$ python test_[component].py
[PASTE RAW OUTPUT]
```

## Metrics
- Execution time: X.XX seconds
- Memory used: X.X MB
- Tests passed: X/Y

## Compatibility
- Input: [TYPE]
- Output: [TYPE]
- Connects to: [List]
```

### Final POC Summary
Create: `evidence/current/Evidence_POC_Decision.md`

Must include:
1. Performance overhead percentage
2. Memory limit discovered
3. Chain discovery success/failure
4. Go/no-go recommendation with evidence

---

## 7. Daily Checklist

### Day 1
- [ ] Create registry.py with chain discovery
- [ ] Implement TextLoader tool
- [ ] Test tool registration
- [ ] Generate Evidence_POC_Registry.md

### Day 2
- [ ] Implement EntityExtractor (use Gemini)
- [ ] Implement GraphBuilder (use Neo4j)
- [ ] Test full chain execution
- [ ] Generate Evidence_POC_Tools.md

### Days 3-4
- [ ] Integration testing
- [ ] Multi-tool pipeline execution
- [ ] Generate Evidence_POC_Integration.md

### Days 5-6
- [ ] Memory limit testing
- [ ] Failure recovery patterns
- [ ] Schema evolution testing
- [ ] Generate Evidence_POC_EdgeCases.md

### Day 7
- [ ] Performance benchmarking
- [ ] Framework vs direct comparison
- [ ] Generate Evidence_POC_Performance.md

### Day 8
- [ ] Run complete demo
- [ ] Collect all metrics
- [ ] Make go/no-go decision
- [ ] Generate Evidence_POC_Decision.md

---

## 8. Success Criteria

**POC succeeds if**:
- ✓ Registry discovers chains automatically
- ✓ Performance overhead <20%
- ✓ Handles 10MB documents
- ✓ Three tools work together

**POC fails if**:
- ✗ Performance overhead >50%
- ✗ Memory fails at <5MB
- ✗ Chain discovery doesn't work
- ✗ Tools can't compose

---

## 9. Environment Setup

### Prerequisites
```bash
# Verify environment
docker ps | grep neo4j       # Must be running
echo $GEMINI_API_KEY         # Must be set
pip list | grep pydantic     # Required
pip list | grep networkx     # For chain discovery
pip list | grep litellm      # For EntityExtractor
```

### Python Path
```bash
export PYTHONPATH=/home/brian/projects/Digimons/tool_compatability:$PYTHONPATH
```

---

## 10. Next Steps After POC

**If POC succeeds**:
1. Week 1: Migrate high-value tools
2. Week 2: Build production registry
3. Week 3: Create migration guide
4. Week 4: Deprecate old system

**If POC fails**:
1. Document specific failures
2. Implement hardcoded chains
3. Accept 20-30 specific workflows

---

*Last Updated: 2025-01-25*
*POC Timeline: 8 days from start*
*Decision Point: Day 8*