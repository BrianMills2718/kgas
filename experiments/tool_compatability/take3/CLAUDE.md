# Pipeline Accumulation Approach for Tool Compatibility

## The Core Problem

We need tools to chain together in DAGs, but each tool has different input/output data structures. Creating a single "UnifiedData" structure with every possible field is impractical and becomes a god object anti-pattern.

## The Solution: Pipeline Accumulation

Instead of forcing all data through one structure, we allow data to **accumulate** as it flows through the pipeline. Each tool:
1. Reads the data it needs from previous stages
2. Processes that data
3. Adds its output as a new stage
4. Passes the accumulated pipeline forward

## Key Principles

1. **No Universal Schema**: Each tool works with its natural data format
2. **Accumulation Not Transformation**: Data builds up, previous stages remain accessible
3. **Explicit Dependencies**: Tools declare which stages they need
4. **Type Safety Through Stages**: Each stage has its own well-defined structure

## How It Works

```python
# Pipeline starts empty
pipeline = PipelineData()

# T01 adds raw text
pipeline.add_stage("raw_text", "John Smith is CEO of TechCorp")

# T23C reads raw_text, adds extraction
extraction = {"entities": [...], "relationships": [...]}
pipeline.add_stage("extraction", extraction)

# T31 reads extraction, adds graph_nodes
nodes = build_nodes(pipeline.get_stage("extraction")["entities"])
pipeline.add_stage("graph_nodes", {"nodes": nodes})

# T68 reads graph_nodes, adds pagerank
scores = calculate_pagerank(pipeline.get_stage("graph_nodes"))
pipeline.add_stage("pagerank", {"scores": scores})

# At the end, pipeline contains ALL stages - any data is accessible
```

## Benefits

1. **No Schema Adapters Needed**: Tools read/write their natural formats
2. **Full Data Lineage**: Can trace how data evolved through pipeline
3. **Flexible Composition**: Tools can read from ANY previous stage
4. **Debugging Friendly**: Can inspect data at each stage
5. **Works with Provenance**: Each stage addition is a provenance event

## Implementation Examples

This directory contains working examples showing how different tool chains work with pipeline accumulation.