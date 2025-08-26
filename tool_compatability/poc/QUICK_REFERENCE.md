# Type-Based Tool Composition: Quick Reference

## What It Is
A framework that automatically discovers and chains tools based on their input/output types, eliminating manual configuration.

## The Problem It Solves
KGAS has 60+ tools but only 5 are usable because of hardcoded mappings. We make ALL tools discoverable.

## Core Concepts

### 1. Data Types (10 total)
```python
class DataType(Enum):
    FILE = "file"           # File path
    TEXT = "text"           # Raw text
    CHUNKS = "chunks"       # Text chunks
    ENTITIES = "entities"   # Extracted entities
    GRAPH = "graph"         # Graph structure
    VECTORS = "vectors"     # Embeddings
    QUERY = "query"         # Search query
    RESULTS = "results"     # Query results
    METRICS = "metrics"     # Analysis metrics
    TABLE = "table"         # Tabular data
```

### 2. Tool Registration
```python
# Tools self-register with capabilities
framework.register_tool(StreamingFileLoader())
framework.register_tool(EntityExtractor())
framework.register_tool(GraphBuilder())
```

### 3. Automatic Chain Discovery
```python
# Find all ways to get from FILE to GRAPH
chains = framework.find_chains(DataType.FILE, DataType.GRAPH)
# Returns: [["TextLoader", "EntityExtractor", "GraphBuilder"]]

# Execute the chain
result = framework.execute_chain(chains[0], file_data)
```

### 4. Cross-Modal Support
```python
# Automatic cross-modal conversion
chains = framework.find_chains(DataType.GRAPH, DataType.TABLE)
# Returns: [["GraphToTableConverter"]]

chains = framework.find_chains(DataType.GRAPH, DataType.VECTOR)
# Returns: [["GraphToTableConverter", "TableVectorizer"]]
#      OR: [["GraphVectorizer"]]  # if available
```

## Key Advantages

| Feature | KGAS Current | Our Framework |
|---------|--------------|---------------|
| Tool Discovery | 5 hardcoded | All automatic |
| Chain Building | Manual YAML | Type-based auto |
| New Tools | Update 5+ files | Just register |
| Field Adapters | 8+ manual | Zero needed |
| Cross-Modal | Blocked | Automatic |

## Integration with KGAS

### Quick Win: Wrap Existing Tools
```python
# Make any KGAS tool discoverable
wrapped = KGASToolWrapper(
    kgas_tool=T23C_EntityExtractor(),
    input_type=DataType.TEXT,
    output_type=DataType.ENTITIES
)
framework.register_tool(wrapped)
```

### Long Term: Native Tools
```python
class NativeEntityExtractor(ExtensibleTool):
    def get_capabilities(self):
        return ToolCapabilities(
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES
        )
    
    def process(self, input_data, context=None):
        # Direct implementation, no layers
        entities = extract_entities(input_data.content)
        return ToolResult(success=True, data=entities)
```

## Common Patterns

### 1. Document Processing Pipeline
```python
# FILE → TEXT → ENTITIES → GRAPH
chain = framework.find_chains(DataType.FILE, DataType.GRAPH)
graph = framework.execute_chain(chain[0], file_data)
```

### 2. Cross-Modal Analysis
```python
# GRAPH → TABLE → Statistical Analysis
chain = framework.find_chains(DataType.GRAPH, DataType.TABLE)
table = framework.execute_chain(chain[0], graph_data)
```

### 3. Semantic Search
```python
# TEXT → VECTORS → Similarity Search
chain = framework.find_chains(DataType.TEXT, DataType.VECTORS)
embeddings = framework.execute_chain(chain[0], text_data)
```

## Files to Review

### Core Framework
- `/tool_compatability/poc/framework.py` - Main framework
- `/tool_compatability/poc/data_types.py` - Type definitions
- `/tool_compatability/poc/base_tool.py` - Tool interface

### Documentation
- `TOOL_COMPOSITION_ARCHITECTURE.md` - Full architecture
- `KGAS_INTEGRATION_ANALYSIS.md` - How we fit in KGAS
- `ARCHITECTURE_REVIEW_FINDINGS.md` - Problems we solve

### Example Tools
- `/tools/streaming_file_loader.py` - Native tool example
- `/proof_of_concept_real.py` - Working POC

## Next Steps

1. **Immediate**: Wrap 10-15 critical KGAS tools
2. **Week 1**: Build 5 native tools
3. **Week 2**: Add cross-modal converters
4. **Week 3**: Build composition agent

## The Bottom Line

**KGAS built the engine, we built the transmission.**

Without our framework, KGAS has sophisticated tools that can't work together. With it, everything connects automatically through types.