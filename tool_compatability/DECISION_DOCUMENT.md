# Tool Compatibility Decision Document

## Executive Summary

After analyzing 5 failed compatibility approaches and the current state of 38 poorly-factored tools, we recommend **type-based composition with direct data passing** as the solution. This approach is simpler than ORM, more reliable than field matching, and achievable within 4 weeks.

## The Problem

- **38 tools** with incompatible interfaces (not the claimed 121)
- **75 implementation files** with duplicates and versions
- Tools factored at wrong boundaries (T31/T34 shouldn't exist)
- Multiple failed attempts at automatic compatibility

## Failed Approaches Analysis

### 1. Unified Data Contract (Take 1)
**Approach**: God object with all possible fields
**Why it failed**: Complexity explosion, unmaintainable

### 2. Type-Based Matching (Take 2)
**Approach**: Python type matching
**Why it failed**: Types too generic, no semantic meaning

### 3. Pipeline Accumulation (Take 3)
**Approach**: Accumulate all data through pipeline
**Why it failed**: Memory explosion, debugging nightmare

### 4. Simple Contracts (Take 4)
**Approach**: Field name matching
**Why it failed**: Same name ≠ same structure/semantics

### 5. ORM/Semantic Matching (Proposed)
**Approach**: Semantic role matching
**Why we're not doing it**: Too complex for the benefit

## Recommended Solution: Type-Based Composition

### Core Principles

1. **~10 Semantic Types** (TEXT, ENTITIES, GRAPH, etc.)
2. **Exact Schemas** per type (Pydantic models)
3. **Direct Data Passing** (except graphs in Neo4j)
4. **Type Matching** for compatibility

### Why This Works

```python
# Simple and Clear
if tool1.output_type == tool2.input_type:
    # They're compatible!
    
# No ambiguity
DataSchema.Entity = exactly one structure
All tools use the SAME Entity class
```

### Implementation Plan

#### Phase 1: Proof of Concept (1 week)
- Build core framework
- Implement 3 test tools
- Validate <20% performance overhead
- Test edge cases

#### Phase 2: Tool Consolidation (1 week)
- Merge 38 tools → ~15 properly-bounded tools
- T23C+T31+T34 → GraphBuilder
- 14 loaders → DocumentLoader

#### Phase 3: Migration (2 weeks)
- Wrap existing tools for compatibility
- Update pipelines gradually
- Maintain backward compatibility

## Critical Issues Addressed

### Issue: Multi-Input Tools
**Solution**: Primary input for chaining, parameters dict for additional inputs

### Issue: Memory Limits
**Solution**: Direct passing up to 10MB, references for larger data

### Issue: Schema Evolution
**Solution**: Pydantic models with versioning and migration functions

### Issue: Service Dependencies
**Solution**: Validate at startup, not per-tool

### Issue: Performance
**Solution**: Direct passing avoids database round-trips (5-10x faster)

## Risk Analysis

### Risks of Type-Based Approach
1. **Memory limits** for large data (>10MB)
2. **No transaction support** across tools
3. **Synchronous only** initially

### Risks of NOT Doing This
1. **Continued incompatibility** between tools
2. **More failed workarounds** 
3. **Unable to compose pipelines**
4. **Technical debt accumulation**

## Success Metrics

- ✅ 38 tools → 15 tools (60% reduction)
- ✅ <20% performance overhead
- ✅ Automatic chain discovery working
- ✅ New tools automatically compatible
- ✅ Can explain system in 5 minutes

## Decision Points

### Go with Type-Based if POC shows:
- [ ] Performance overhead <20%
- [ ] Memory handling up to 10MB
- [ ] Clean failure recovery
- [ ] Developer experience improved

### Fallback to Hardcoded Chains if:
- [ ] Performance overhead >50%
- [ ] Memory issues at <5MB
- [ ] Too complex for team
- [ ] POC fails core scenarios

## Timeline

**Week 1**: POC Development and Testing
**Week 2**: Go/No-Go Decision
**Week 3-4**: Full Implementation (if go)
**Week 5-6**: Migration and Testing

## Recommendation

**Proceed with Type-Based Composition POC immediately.**

This approach:
- Solves real problems (incompatibility)
- Is simple enough to understand
- Can be implemented incrementally
- Doesn't require rewriting everything

The alternative (continuing with current chaos or implementing ORM) will cost more time and add more complexity without clear benefits.

## Next Steps

1. Run POC (5-8 days)
2. Evaluate results against success criteria
3. Make go/no-go decision
4. Implement or pivot to hardcoded chains

---

*Decision Date: 2025-01-25*
*Decision Makers: [To be filled]*
*Decision: [Pending POC Results]*