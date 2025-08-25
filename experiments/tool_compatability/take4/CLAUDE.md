# Simple Explicit Tool Contracts

## The Problem We're Solving

We need to chain ~35 tools together in workflows where:
- Each tool has specific input requirements
- Each tool produces specific outputs
- The LLM needs to plan valid tool sequences
- We need to avoid the complexity of DAGs and pipeline accumulation

## The Solution: Explicit Contracts

Each tool declares exactly what it consumes and produces. No magic, no accumulation, just simple data passing.

## Core Principles

1. **Explicit Over Implicit**: Every tool clearly states its inputs/outputs
2. **Simple Data Dictionary**: Just pass a dict between tools, updating it as we go
3. **Type Safety**: Validate that required fields exist and have correct types
4. **No Accumulation**: Only keep current working data, not entire history
5. **Linear Execution**: Tools run in sequence, no complex DAG logic

## How It Works

```python
# Tool declares its contract
class T23C:
    def get_contract(self):
        return {
            "consumes": {"text": str},  # What I need
            "produces": {"entities": list, "relationships": list}  # What I create
        }
    
    def execute(self, data: dict) -> dict:
        text = data["text"]  # Get what I need
        # Process...
        return {
            "entities": extracted_entities,
            "relationships": extracted_relationships
        }

# Workflow execution
workflow = SimpleWorkflow()
workflow.data = {"text": "John is CEO of TechCorp"}

# T23C adds entities and relationships to data
workflow.execute(T23C())  
# data now has: {"text": "...", "entities": [...], "relationships": [...]}

# T31 uses entities to create nodes
workflow.execute(T31())
# data now has: {"text": "...", "entities": [...], "relationships": [...], "nodes": [...]}
```

## Benefits

1. **Simple**: No complex pipeline logic
2. **Explicit**: Clear what each tool needs/produces
3. **Memory Efficient**: Only keep current data
4. **Type Safe**: Can validate at each step
5. **LLM Friendly**: Clear contracts for planning
6. **Fast**: No accumulation overhead
7. **Debuggable**: See exactly what data flows between tools

## What We're Testing

1. Can this handle all real tool combinations?
2. What about tools that need multiple inputs?
3. How do we handle optional fields?
4. What about tools that can consume different input types?
5. How does error handling work?
6. Can we run the same tool multiple times?
7. How do we merge data from multiple sources?
8. Is the LLM planning actually simpler?

## Expected Outcome

A simple, robust system that:
- Works in 1 week instead of 6
- Handles 90% of use cases
- Is actually maintainable
- Doesn't have the 10 critical issues of pipeline accumulation