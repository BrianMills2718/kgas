# Type-Based Tool Composition - Proof of Concept

## Overview

This POC validates that type-based tool composition can solve our tool compatibility problems without the complexity of semantic matching (ORM) or the brittleness of field-name matching.

## Key Concepts

### 1. Data Types (Not Python Types)
We define ~10 semantic data types (TEXT, ENTITIES, GRAPH, etc.) that represent meaningful categories of data. Tools declare which type they consume and produce.

### 2. Exact Schemas
Each data type has a precise Pydantic schema. All tools using that type MUST use the exact same schema. This eliminates field name mismatches.

### 3. Direct Data Passing
Tools pass actual data, not references (except for graphs which live in Neo4j). This keeps things simple and fast.

### 4. Automatic Chain Discovery
The registry can automatically find valid tool chains by matching output types to input types.

## Project Structure

```
poc/
├── README.md                # This file
├── data_types.py           # Core data types and schemas
├── base_tool.py            # Base class all tools inherit from
├── registry.py             # Tool registry and chain discovery
├── tools/                  # Tool implementations
│   ├── __init__.py
│   ├── text_loader.py     # FILE → TEXT
│   ├── entity_extractor.py # TEXT → ENTITIES
│   └── graph_builder.py    # ENTITIES → GRAPH
├── tests/                  # Test suite
│   ├── test_memory.py      # Memory limit testing
│   ├── test_recovery.py    # Failure recovery testing
│   ├── test_schema.py      # Schema evolution testing
│   └── test_performance.py # Performance benchmarking
├── demo.py                 # Main demonstration script
└── benchmark.py            # Performance comparison

```

## Running the POC

### Prerequisites

```bash
# 1. Ensure Neo4j is running
docker ps | grep neo4j

# 2. Install dependencies
pip install pydantic psutil networkx python-magic litellm neo4j

# 3. Set environment variables
export GEMINI_API_KEY="your-key-here"
```

### Run the Demo

```bash
cd /home/brian/projects/Digimons/tool_compatability/poc
python demo.py
```

Expected output:
```
============================================================
COMPATIBILITY MATRIX
============================================================
FROM \ TO  | TextLoa | EntityE | GraphBu
TextLoader |         |    ✓    |        
EntityExt  |         |         |    ✓   
GraphBuil  |         |         |        

============================================================
DISCOVERED CHAINS: FILE → GRAPH
============================================================
1. TextLoader → EntityExtractor → GraphBuilder

============================================================
EXECUTING CHAIN
============================================================
✓ Success! Created graph: graph_abc123
  Nodes: 2
```

### Run Tests

```bash
# Test memory limits
python -m pytest tests/test_memory.py -v

# Test failure recovery
python -m pytest tests/test_recovery.py -v

# Test schema evolution
python -m pytest tests/test_schema.py -v

# Benchmark performance
python benchmark.py
```

## Adding a New Tool

### 1. Define the Tool Class

```python
from poc.base_tool import BaseTool
from poc.data_types import DataType, DataSchema

class YourTool(BaseTool):
    @property
    def input_type(self) -> DataType:
        return DataType.TEXT  # What type you consume
    
    @property
    def output_type(self) -> DataType:
        return DataType.METRICS  # What type you produce
    
    def _execute(self, input_data: DataSchema.TextData) -> DataSchema.MetricsData:
        # Your logic here
        return DataSchema.MetricsData(...)
```

### 2. Register the Tool

```python
registry = ToolRegistry()
registry.register(YourTool())
```

### 3. It Automatically Works!

Any tool outputting TEXT can now feed into YourTool.
YourTool can feed into any tool accepting METRICS.

## Critical Edge Cases Tested

### 1. Memory Limits
- Test processes documents from 1MB to 100MB
- Identifies memory threshold for direct passing
- Provides guidance on when to use references

### 2. Schema Evolution  
- Shows how to handle schema changes
- Migration strategies for backward compatibility
- Version management approach

### 3. Pipeline Failures
- Checkpointing for recovery
- Partial pipeline rollback
- Error propagation

### 4. Performance Overhead
- Measures framework overhead vs direct calls
- Target: <20% overhead
- Identifies bottlenecks

## Success Criteria

✅ **Must Have**
- [ ] Three tools working with type-based composition
- [ ] Automatic chain discovery functioning
- [ ] Less than 20% performance overhead
- [ ] Clean error handling with recovery

✅ **Should Have**
- [ ] Handle 10MB documents without memory issues
- [ ] Schema migration strategy demonstrated
- [ ] Pipeline branching pattern shown
- [ ] Debugging/observability tools

✅ **Nice to Have**
- [ ] Async tool support pattern
- [ ] Resource pooling for Neo4j connections
- [ ] Metrics aggregation system
- [ ] LLM-friendly tool descriptions

## Key Decisions Made

### Why Direct Data Passing?
- **Simplicity**: No reference management complexity
- **Performance**: 5-10x faster than database round-trips
- **Debugging**: Can inspect data at each step
- **Testing**: Easy to unit test tools in isolation

### Why Not ORM?
- **Complexity**: Semantic role matching is complex
- **Unclear Benefits**: Type matching achieves same goal
- **Maintenance**: Simpler system easier to maintain

### Why These Specific Types?
- **Coverage**: Cover 90% of use cases
- **Clarity**: Each type has clear meaning
- **Composability**: Natural connection points

## Known Limitations

1. **Large Data**: Direct passing has memory limits (~10MB)
2. **Multi-Input**: Handled via parameters dict, not perfect
3. **Async**: Current design is synchronous
4. **Transactions**: No multi-tool transaction support

## Migration Path

If POC succeeds:

### Week 1: Core Tools
- Merge badly-factored tools (38 → 15)
- Implement standardized interfaces
- Maintain backward compatibility

### Week 2: Registry System  
- Production-ready registry
- Chain discovery optimization
- Performance monitoring

### Week 3: Documentation
- Tool development guide
- Migration guide for existing code
- Best practices document

### Week 4: Deprecation
- Mark old system deprecated
- Provide migration tools
- Update all documentation

## Questions to Answer

1. **Memory Threshold**: At what size must we use references?
2. **Performance Overhead**: Is <20% achievable?
3. **Schema Evolution**: Is our strategy sufficient?
4. **Developer Experience**: Is this simpler than current system?

## Conclusion

This POC will provide concrete evidence about whether type-based composition is the right approach. We'll have real performance numbers, actual failure scenarios tested, and a working system to evaluate.

The goal is not perfection, but validation that this approach is:
- Simpler than current system
- Performant enough for production
- Extensible for future needs
- Maintainable by the team