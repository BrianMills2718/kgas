# Unresolved Issues with Simple Contracts

## 🚨 Critical Issues We Haven't Addressed

### 1. **The Field Name Agreement Problem**

We're assuming all tools will magically agree on field names. But who enforces this?

```python
# Tool A produces:
{"extracted_entities": [...]}

# Tool B expects:
{"entities": [...]}

# Our "solution": Just standardize!
# Reality: 35+ tools already exist with different conventions
```

**The Real Problem**: Refactoring 35 existing tools to use standard field names is a massive undertaking. We glossed over this.

### 2. **The Semantic Mismatch Problem**

Even if field names match, do they mean the same thing?

```python
# T23C produces:
{
    "entities": [
        {"id": "e1", "text": "John Smith", "type": "PERSON"}
    ]
}

# But T31 might expect:
{
    "entities": [
        {"entity_id": "e1", "label": "John Smith", "category": "PERSON"}
    ]
}

# Same field name, different internal structure!
```

**We assumed**: Same field name = compatible data
**Reality**: Need to standardize internal structures too

### 3. **The Optional vs Required Problem**

How do we handle optional fields?

```python
# T23C sometimes produces relationships, sometimes doesn't
mode="entity_only" → no relationships field
mode="full" → has relationships field

# T34 REQUIRES relationships
# What happens when T23C runs in entity_only mode?
```

**We said**: "Check if required fields exist"
**But**: How does LLM know which mode to use to ensure downstream compatibility?

### 4. **The Data Transformation Problem**

Some tools need transformed data, not just passed through:

```python
# T23C outputs:
{"text": "John is CEO of TechCorp"}

# T15A (chunker) needs:
{"text": "...", "chunk_size": 500}  # Where does chunk_size come from?

# T91 (formatter) needs:
{"data_to_format": ..., "format_type": "table"}  # Who provides format_type?
```

**Parameters aren't data** - they're configuration. How do they flow?

### 5. **The Type Granularity Problem**

`list` is not specific enough:

```python
# Contract says: {"entities": list}

# But is it:
# - List[Dict[str, Any]]?
# - List[Entity]?
# - List[str]?
# - List[Tuple[str, str, float]]?

# Runtime type checking isn't enough
```

### 6. **The Partial Update Problem**

Tools might update only part of the data:

```python
# Data has: {"entities": [...], "text": "..."}

# T31 produces: {"nodes": [...]}
# Should it preserve "entities" and "text"?
# Or does it replace everything?

# If preserve: How much memory?
# If replace: How do downstream tools get earlier data?
```

### 7. **The Version Evolution Problem**

Tools evolve over time:

```python
# T23C v1: produces {"entities": [...]}
# T23C v2: produces {"entities": [...], "confidence_scores": [...]}

# Old workflows break with v2 (extra field)
# New workflows break with v1 (missing field)
```

How do we handle backward compatibility?

### 8. **The Multi-Input Problem**

Some tools need multiple data sources:

```python
# T99_Merger needs:
# - entities from source A
# - entities from source B

# Simple workflow only has one data dict
# How do we pass multiple sources?
```

### 9. **The State Management Problem**

Some tools need to maintain state:

```python
# T68_PageRank needs:
# - Graph from current iteration
# - Scores from previous iteration (for convergence)

# Where does previous iteration state live?
# How do we pass it?
```

### 10. **The Real LLM Planning Problem**

LLM needs to understand:
- Which tools produce what (contracts) ✓
- Which field names map to what concepts (semantics) ✗
- Which parameters to use for what goal ✗
- How to handle optional fields ✗
- When to use which tool variant ✗

Example:
```
User: "Extract organizations from this document"

LLM needs to know:
- Use T23C (that's in contracts)
- Set mode="entity_only"? "full"? (NOT in contracts)
- Filter entities where type="ORGANIZATION"? (NOT in contracts)
- Or is there a different tool? (NOT clear from contracts)
```

## The Uncomfortable Truth

### What Simple Contracts Actually Solve:
✅ Basic "does this field exist" checking
✅ Simple linear workflows with perfect field matches
✅ Memory efficiency (no accumulation)

### What They DON'T Solve:
❌ Semantic compatibility between tools
❌ Parameter flow and configuration
❌ Optional field handling
❌ Data transformation requirements
❌ Multi-input scenarios
❌ State management
❌ Version compatibility
❌ Complex type validation

## The Real Comparison

### Original Hardcoded System
```python
tool_chains = [
    ["T23C", "T31"],  # We KNOW these work together
]
```
**Advantage**: Guaranteed to work (tested combinations)
**Disadvantage**: Limited to hardcoded chains

### Simple Contracts
```python
T23C: produces {"entities": list}
T31: consumes {"entities": list}
# Therefore compatible?
```
**Advantage**: Dynamic discovery
**Disadvantage**: Field name match ≠ actual compatibility

### What We Actually Need

Maybe a hybrid:

```python
class ToolContract:
    # Basic field info
    consumes = {"entities": List[EntitySchema]}
    produces = {"nodes": List[NodeSchema]}
    
    # Semantic info
    entity_schema = {
        "required": ["id", "text", "type"],
        "optional": ["confidence", "properties"]
    }
    
    # Parameter contracts
    parameters = {
        "mode": {
            "type": "enum",
            "values": ["entity_only", "full"],
            "affects_output": {
                "entity_only": ["entities"],
                "full": ["entities", "relationships"]
            }
        }
    }
    
    # Compatibility rules
    compatible_with = {
        "T31": lambda data: "entities" in data and len(data["entities"]) > 0,
        "T34": lambda data: "relationships" in data
    }
```

But this is getting complex again...

## The Question

**Are we just rebuilding the original system with extra steps?**

The original hardcoded 5 chains because those were TESTED to work.
We're trying to discover chains dynamically, but:
- Field names aren't standardized
- Semantics aren't guaranteed
- Parameters aren't handled
- Types aren't specific enough

**Maybe the hardcoded approach was right, just needed more chains added?**