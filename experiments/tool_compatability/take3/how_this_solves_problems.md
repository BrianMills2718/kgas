# How Pipeline Accumulation Solves Our Real Problems

## Problem 1: Different Tools Need Different Data Formats

### The Problem
- T23C outputs `{"entities": [...], "relationships": [...]}`
- T31 needs entities to build nodes
- T68 needs a graph structure
- T91 needs something to format into a table

### The Solution
Each tool reads what it needs from the appropriate stage:

```python
# T23C adds extraction results
pipeline.add_stage("extraction", {
    "entities": [...],
    "relationships": [...]
})

# T31 reads extraction, adds nodes
entities = pipeline.get_stage("extraction")["entities"]
pipeline.add_stage("graph_nodes", build_nodes(entities))

# T68 reads graph_structure (created by T34)
graph = pipeline.get_stage("graph_structure")
pipeline.add_stage("pagerank_scores", calculate_pagerank(graph))

# T91 can read EITHER extraction OR pagerank
if pipeline.has_stage("pagerank_scores"):
    format_pagerank(pipeline.get_stage("pagerank_scores"))
else:
    format_extraction(pipeline.get_stage("extraction"))
```

**No adapters needed!** Each tool works with its natural format.

## Problem 2: Tools Don't Know What Previous Tool Produced

### The Problem
In a traditional pipeline, Tool N only sees output from Tool N-1. But what if it needs data from Tool N-3?

### The Solution
All stages remain accessible:

```python
# After 5 tools have run:
pipeline.list_stages()
# ['raw_text', 'extraction', 'graph_nodes', 'graph_structure', 'pagerank_scores']

# Tool 6 can access ANY previous stage:
text = pipeline.get_stage("raw_text")  # From tool 1
entities = pipeline.get_stage("extraction")["entities"]  # From tool 2
scores = pipeline.get_stage("pagerank_scores")  # From tool 5
```

## Problem 3: Same Tool, Different Contexts

### The Problem
T23C should work with both text AND table inputs. How do we handle this without creating T23C_Text and T23C_Table variants?

### The Solution
Tools adapt based on available stages:

```python
class T23C_OntologyAwareExtractor:
    def execute(self, pipeline, params):
        # Check what's available
        if pipeline.has_stage("raw_text"):
            input_data = pipeline.get_stage("raw_text")
            result = extract_from_text(input_data)
        elif pipeline.has_stage("table_data"):
            input_data = pipeline.get_stage("table_data")
            result = extract_from_table(input_data)
        else:
            raise ValueError("Need either text or table")
        
        pipeline.add_stage("extraction", result)
```

One tool, multiple contexts!

## Problem 4: Field Name Mismatches

### The Problem
Without a universal schema, how do we avoid field name conflicts?

### The Solution
Stage names are the contract, not field names:

```python
# Tool A adds data with its field names
pipeline.add_stage("extraction", {
    "entities": [...],  # Tool A calls them "entities"
    "relationships": [...]
})

# Tool B reads from the stage it expects
data = pipeline.get_stage("extraction")
entities = data["entities"]  # Tool B knows extraction stage has "entities"
```

The stage name ("extraction") is the interface, not the internal structure.

## Problem 5: Data Lineage and Debugging

### The Problem
In a complex DAG, how do we know where data came from?

### The Solution
Built-in lineage tracking:

```python
# Automatic dependency tracking
pipeline.add_stage("pagerank_scores", scores, 
                  tool_id="T68_PAGERANK",
                  dependencies=["graph_structure"])

# Query lineage
lineage = pipeline.get_lineage("formatted_table")
# ['raw_text', 'extraction', 'graph_nodes', 'graph_structure', 'pagerank_scores', 'formatted_table']

# Inspect any stage
for stage in pipeline.list_stages():
    meta = pipeline.get_stage_metadata(stage)
    print(f"{stage}: created by {meta.tool_id} at {meta.timestamp}")
```

## Problem 6: The LLM Needs to Plan DAGs

### The Problem
How does the LLM know what tools can connect?

### The Solution
Tools declare their stage requirements:

```python
class ToolCapabilities:
    T23C: {
        "requires": ["raw_text"] OR ["table_data"],
        "produces": "extraction"
    }
    T31: {
        "requires": ["extraction"],
        "produces": "graph_nodes"
    }
    T68: {
        "requires": ["graph_structure"],
        "produces": "pagerank_scores"
    }
```

The LLM can then plan valid DAGs:
1. Start with available data (e.g., "raw_text")
2. Find tools that can consume it (T23C)
3. See what that produces ("extraction")
4. Find tools that can consume that (T31)
5. Continue until goal is reached

## Real Example: Self-Categorization Theory Analysis

```python
# The DAG for SCT analysis
pipeline = PipelineData()

# Load document
pipeline = T01_PDFLoader().execute(pipeline, {"file": "paper.pdf"})

# Extract with theory guidance
pipeline = T23C().execute(pipeline, {
    "mode": "theory_guided",
    "theory": "self_categorization"
})

# Build graph
pipeline = T31().execute(pipeline, {})
pipeline = T34().execute(pipeline, {})

# Theory-specific analysis (T51_MCR)
# Can access extraction for theory annotations
extraction = pipeline.get_stage("extraction")
theory_context = extraction["theory_annotations"]

# And also access graph for structure
graph = pipeline.get_stage("graph_structure")

# Calculate MCR using both
mcr_scores = calculate_mcr(graph, theory_context)
pipeline.add_stage("mcr_analysis", mcr_scores, tool_id="T51_MCR")

# Format results - can access everything
pipeline = T91().execute(pipeline, {})
```

## Why This Works

1. **No Universal Schema Needed**: Each tool uses its natural format
2. **Full Flexibility**: Tools can read from any previous stage
3. **Adaptable Tools**: Same tool works in different contexts
4. **Clear Contracts**: Stage names are the interface
5. **Automatic Lineage**: Dependencies tracked automatically
6. **LLM Friendly**: Clear requirements and productions for planning

## What We Don't Need

❌ Hundreds of schema adapters
❌ A god object with every possible field
❌ Separate tool variants for different inputs
❌ Complex type conversion logic
❌ Manual lineage tracking

## The Key Insight

**Data accumulates, it doesn't transform**

Instead of:
```
A → B → C → D  (each transformation loses previous data)
```

We have:
```
Pipeline: {A} → {A, B} → {A, B, C} → {A, B, C, D}
```

Every tool can see everything that came before, so they can:
- Use what they need
- Ignore what they don't
- Add their contribution
- Leave everything else untouched