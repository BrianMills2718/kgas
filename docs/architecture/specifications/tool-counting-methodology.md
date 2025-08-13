# Tool Counting Methodology

**Purpose**: Standardize tool counting across all KGAS documentation  
**Status**: Official methodology for consistent reporting  
**Created**: 2025-08-05 (extracted from roadmap initiatives)

## Counting Standards

### What Counts as a "Tool"

A tool is counted if it meets ALL criteria:
- ✅ Has complete implementation (not stub/placeholder)
- ✅ Can be invoked and produces results  
- ✅ Has been functionally verified with test data
- ✅ Provides distinct functionality (not just a variant)

### What Does NOT Count

The following are NOT counted as separate tools:
- ❌ Base classes or abstract implementations
- ❌ Optimized variants of the same functionality  
- ❌ Test utilities or helper functions
- ❌ Archived or experimental implementations
- ❌ Duplicate implementations with same functionality

### Tool Categories

#### Core Tools
Tools implementing fundamental KGAS functionality:
- Phase 1: Ingestion, processing, graph operations
- Phase 2: Enhanced processing with ontologies
- Phase 3: Multi-document capabilities

#### MCP Server Tools  
Additional tools exposed through Model Context Protocol:
- Pipeline control tools
- Administrative and utility tools
- Query and visualization tools

### Reporting Standards

When reporting tool counts:
1. **Always use functional count** as primary metric
2. **Clarify category** (Core vs Total including MCP)
3. **Reference this methodology** for consistency
4. **Update counts only after functional verification**

### Current Reality Check

Tool counts should reflect actual system capabilities verified through testing, not aspirational goals or file counts.

## Related Documentation

- [ROADMAP_OVERVIEW.md](../../roadmap/ROADMAP_OVERVIEW.md) - Current system status
- [Compatibility Matrix](./compatibility-matrix.md) - Tool integration status