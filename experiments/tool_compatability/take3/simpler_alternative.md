# A Simpler Alternative: Explicit Tool Contracts

## The Realization

After stress-testing pipeline accumulation, we found ~10 major issues that need complex solutions. But what if we're over-engineering this?

## The Actual Requirements

Looking at your real needs:
1. ~35 tools that need to chain together
2. Single user (no concurrency issues)
3. Mostly linear workflows
4. Research documents (not millions of records)
5. LLM can plan the workflow

## The Simpler Solution: Explicit Input/Output Contracts

### Core Idea

Each tool explicitly declares what it consumes and produces:

```python
class ToolContract:
    """Simple, explicit contract for each tool"""
    
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.consumes = {}  # field_name -> type
        self.produces = {}  # field_name -> type

class T23C_Contract(ToolContract):
    def __init__(self):
        super().__init__("T23C")
        self.consumes = {
            "text": str,  # OR
            "table_data": dict
        }
        self.produces = {
            "entities": list,
            "relationships": list
        }

class T31_Contract(ToolContract):
    def __init__(self):
        super().__init__("T31")
        self.consumes = {
            "entities": list
        }
        self.produces = {
            "nodes": list
        }
```

### Simple Data Passing

Instead of complex pipeline accumulation:

```python
class SimpleWorkflow:
    """Just pass data between tools"""
    
    def __init__(self):
        self.data = {}  # Current working data
        self.history = []  # For debugging
    
    def execute_tool(self, tool, params=None):
        """Execute tool with current data"""
        
        # Check if tool can run
        contract = tool.get_contract()
        for field, type_ in contract.consumes.items():
            if field not in self.data:
                raise ValueError(f"{tool.tool_id} needs '{field}' but it's not available")
        
        # Run tool
        result = tool.execute(self.data, params)
        
        # Update data with results
        for field, value in result.items():
            self.data[field] = value
        
        # Save history for debugging
        self.history.append({
            "tool": tool.tool_id,
            "input": dict(self.data),
            "output": result
        })
        
        return self.data
```

### The Compatibility Matrix

With explicit contracts, building the matrix is trivial:

```python
class CompatibilityMatrix:
    """Which tools can follow which tools"""
    
    def __init__(self, tools):
        self.tools = tools
        self.contracts = {t.tool_id: t.get_contract() for t in tools}
    
    def can_follow(self, tool_a: str, tool_b: str) -> bool:
        """Can tool_b run after tool_a?"""
        
        produces = self.contracts[tool_a].produces
        consumes = self.contracts[tool_b].consumes
        
        # Check if tool_a produces what tool_b needs
        for field in consumes:
            if field not in produces:
                return False
        return True
    
    def build_matrix(self) -> dict:
        """Build full compatibility matrix"""
        matrix = {}
        
        for t1 in self.tools:
            matrix[t1] = []
            for t2 in self.tools:
                if self.can_follow(t1, t2):
                    matrix[t1].append(t2)
        
        return matrix
```

### LLM Planning Becomes Trivial

```python
def generate_llm_prompt(start_data: dict, goal: str) -> str:
    """Generate prompt for LLM to plan workflow"""
    
    return f"""
    Starting data: {list(start_data.keys())}
    Goal: {goal}
    
    Available tools and their contracts:
    
    T01_PDF_LOADER:
      Needs: file_path
      Produces: text
    
    T23C_EXTRACTOR:
      Needs: text OR table_data
      Produces: entities, relationships
    
    T31_NODE_BUILDER:
      Needs: entities
      Produces: nodes
    
    T34_EDGE_BUILDER:
      Needs: nodes, relationships
      Produces: graph
    
    T68_PAGERANK:
      Needs: graph
      Produces: pagerank_scores
    
    Plan a sequence of tools to achieve the goal.
    """
```

### Handling the Edge Cases

**Multiple runs of same tool?**
```python
# Just namespace the output
result1 = t23c.execute(data, params={"mode": "quick"})
data["extraction_quick"] = result1

result2 = t23c.execute(data, params={"mode": "detailed"})  
data["extraction_detailed"] = result2
```

**Batch processing?**
```python
# Simple loop
for doc in documents:
    workflow = SimpleWorkflow()
    workflow.data = {"file_path": doc}
    workflow.execute_tool(T01_PDFLoader())
    workflow.execute_tool(T23C_Extractor())
    results.append(workflow.data)
```

**Error recovery?**
```python
# Simple try/catch with state
try:
    workflow.execute_tool(risky_tool)
except Exception as e:
    # Workflow.data still has everything up to failure
    # Can retry or skip
    logger.error(f"Tool failed, data state: {workflow.data}")
```

## The Comparison

### Pipeline Accumulation
- **Pros**: Elegant, preserves everything, flexible
- **Cons**: Memory issues, complex error handling, no type safety, performance degradation
- **Effort**: 4-6 weeks to make production-ready

### Simple Contracts
- **Pros**: Explicit, simple, easy to debug, type-checkable, memory-efficient
- **Cons**: Less flexible, need to specify contracts
- **Effort**: 1 week to implement

## The Recommendation

**Go with Simple Contracts** because:

1. **It works today** - No complex issues to solve
2. **LLM friendly** - Clear contracts for planning
3. **Debuggable** - Explicit data flow
4. **Type safe** - Can validate at each step
5. **Memory efficient** - Only keep current data
6. **Fast** - No accumulation overhead

## Implementation Plan (5 days)

### Day 1: Define Contracts
```python
# For each of 35 tools
contracts = {
    "T01": {"consumes": {"file_path": str}, "produces": {"text": str}},
    "T23C": {"consumes": {"text": str}, "produces": {"entities": list}},
    # ... etc
}
```

### Day 2: Build Compatibility Matrix
- Generate matrix from contracts
- Validate no orphaned tools
- Identify common patterns

### Day 3: Simple Workflow Executor
- Basic data passing
- Contract validation
- Error handling

### Day 4: LLM Planning Integration
- Generate planning prompts
- Parse LLM responses
- Execute planned workflows

### Day 5: Testing & Refinement
- Test all tool combinations
- Add logging/debugging
- Performance testing

## The Bottom Line

Simple contracts give you:
- ✅ 90% of the flexibility
- ✅ 10% of the complexity
- ✅ 1 week vs 6 weeks
- ✅ Actually maintainable

Pipeline accumulation is elegant but over-engineered for your needs.

**Simple explicit contracts are the pragmatic choice.**