# Deprecated Concepts Directory

*Over-engineered ideas that violate KISS principles - 2025-08-31*

## Purpose

This directory contains concepts and frameworks from proposal materials that are **too complex for practical implementation** but may have historical or reference value.

## Why These Concepts Are Deprecated

### Complexity vs Value
- **Over-engineered**: Solutions far more complex than the problems they solve
- **KISS Violation**: Conflict with "Keep It Simple" implementation philosophy  
- **Academic Focus**: Designed for research papers, not working systems
- **High Risk**: Complex implementations with uncertain benefits

### Current System Reality
The working KGAS system uses:
- ✅ Simple tool chaining (TEXT→VECTOR→TABLE)
- ✅ Basic adapter patterns for service integration
- ✅ Straightforward error handling and validation
- ✅ Neo4j + SQLite bi-store architecture

These deprecated concepts propose:
- ❌ Complex uncertainty frameworks (14 dimensions)
- ❌ Dynamic tool generation by LLMs
- ❌ Advanced theory selection algorithms
- ❌ Sophisticated mathematical propagation

## Deprecated Concept Categories

### `/dynamic-tool-generation/`
**Concept**: LLM-generated executable tools from theory schemas
**Why Deprecated**: Massive complexity for uncertain benefit, security risks, current static tools work fine

### `/uncertainty-frameworks/`  
**Concept**: 14-dimension uncertainty propagation with Dempster-Shafer theory
**Why Deprecated**: Academic over-engineering, simple success/failure handling sufficient for MVP

### `/theory-selection/`
**Concept**: Automated theory selection using DEPI taxonomy and complex matching
**Why Deprecated**: Requires mature NLP and theory database, user-specified theories work fine

## Usage Guidelines

### For Reference Only
- These concepts may contain interesting ideas
- Do NOT implement these in the working system
- Use for inspiration or future research directions only

### If Considering Implementation
1. **Check KISS compliance** - Does this add necessary simplicity?
2. **Validate user need** - Is there actual demand for this complexity?
3. **Assess current system** - Do simpler approaches work adequately?
4. **Calculate risk/benefit** - Is the implementation effort justified?

### Decision Criteria
Ask yourself:
- Does the current simple approach work?
- Is this solving a real problem users have?
- Can this be implemented with <50 lines of code?
- Does this make the system more reliable or more complex?

## Extraction History

These concepts were identified during the proposal_rewrite directory audit (August 2025) and moved here because they:

1. **Violated KISS principles** in CLAUDE.md
2. **Over-engineered solutions** for simple problems  
3. **Added complexity** without clear benefit
4. **Conflicted with working system** architecture

## Future Consideration

These concepts are **permanently deprecated** unless:
- User demand clearly demonstrates need for complexity
- Simple approaches prove fundamentally inadequate
- Implementation effort becomes trivial (highly unlikely)

The KGAS philosophy prioritizes **working, simple solutions** over **sophisticated, complex frameworks**.

---

*"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry*