# Tool Refactoring Overview

## Executive Summary

We have 38 actual tools (not 121) with fundamental architectural problems: wrong factoring, competing interfaces, and no standardization. This document outlines a pragmatic refactoring approach focused on what actually exists and works.

**Update (2025-08-15)**: Analysis of DIGIMON (16 operators) and StructGPT (interface-based approach) reveals we're over-engineered. We should reduce to ~15-20 operators using Object Role Modeling (ORM) for semantic compatibility.

## Current Reality

### What Actually Exists
- **38 unique tools** implemented (25 in phase1, 12 in phase2, 1 in phase3)
- **2 competing interfaces**: Tool protocol vs KGASTool contract
- **Multiple versions per tool**: standalone, unified, neo4j, fixed (3-5 versions each)
- **9 alias files** for backwards compatibility
- **No standard field names**: text vs content, entities vs extracted_entities, etc.

### Core Problems
1. **Wrong Tool Boundaries**: T31 (Entity Builder) and T34 (Edge Builder) should be internal to T23C
2. **Interface Split**: Orchestrator uses Tool protocol, tools use various interfaces
3. **No Semantic Standards**: Same field names don't guarantee compatible data structures
4. **Over-Engineering**: Building for 121 tools that don't exist instead of 10-15 needed operations

## New Strategic Direction (Based on DIGIMON/StructGPT Analysis)

### Key Insights
1. **DIGIMON uses only 16 operators** for all GraphRAG methods - we have 38+ tools
2. **StructGPT uses ~10 interfaces** for all structured data access - we have dozens
3. **Neither solves dynamic composition** - but our ORM approach could

### Revised Architecture
```python
# Instead of 38-121 tools, organize into DIGIMON-style operator categories
OPERATOR_CATEGORIES = {
    "extraction": ["T23_Unified"],     # Merge T23C+T31+T34
    "transformation": ["T15_Chunker"], # Text processing
    "embedding": ["T41_Embedder"],     # Vector creation
    "graph_ops": ["T49_Query", "T68_PageRank"], # Graph analysis
    "fusion": ["T301_Fusion"],         # Multi-document
}

# Each operator has StructGPT-style interfaces
class KGASOperator:
    def invoke(self, request)  # Interface method
    roles: Dict[str, Role]      # ORM semantic roles
    
# ORM enables dynamic composition
def can_compose(op1: KGASOperator, op2: KGASOperator) -> bool:
    return op1.output_roles.match(op2.input_roles)
```

### Why This Works
- **DIGIMON's lesson**: Fewer, well-designed operators > many poorly-factored tools
- **StructGPT's lesson**: Clean interfaces > complex compatibility layers  
- **ORM innovation**: Semantic role matching > field name matching

## Goals & Constraints

### Primary Goals
1. **Simplify to Core Operations** (~10-15 tools instead of 38)
2. **Standardize One Interface** (eliminate Tool protocol vs KGASTool split)
3. **Define Standard Pipelines** (5-10 common workflows)
4. **Make Tools Actually Compatible** (not just matching field names)

### Hard Constraints
- **Single Developer Environment**: No backwards compatibility needed
- **No Production Data**: Can make breaking changes
- **4-Week Timeline**: Per the contract-first migration plan
- **Must Keep Working**: Can't break existing workflows during migration

### Design Principles
1. **Explicit Over Magic**: Clear contracts, no auto-discovery hopes
2. **Pragmatic Over Perfect**: Working system beats theoretical elegance  
3. **Consolidation Over Proliferation**: Merge tools that always run together
4. **Tested Over Assumed**: Only claim compatibility for tested combinations

## High-Level Strategy (Revised with ORM Approach)

### Phase 1: Define Operator Roles & Semantics (Week 1)
**Create ORM-based operator definitions BEFORE refactoring:**

```python
# Define semantic roles for each operator category
SEMANTIC_ROLES = {
    "text_content": "Raw text document",
    "named_entities": "Extracted entities with types",
    "graph_structure": "Nodes and edges in graph",
    "vector_embeddings": "Semantic vectors",
    "query_results": "Graph query output"
}

# Map existing tools to operators with roles
T23_UNIFIED = OperatorDefinition(
    consumes=["text_content"],
    produces=["named_entities", "graph_structure"],
    merges=[T23C, T31, T34]  # These become internal
)
```

**Specific Operator Definitions:**
- T23_GraphExtractor: text → full graph (merges T23C+T31+T34)
- T15_TextProcessor: text → chunks (keeps chunking separate from embedding)
- T41_Embedder: text/chunks → vectors (pure embedding)
- T01_Loader: files → text (unified loader with format detection)

### Phase 2: Implement ORM Compatibility Layer (Week 2)
**Build the role-matching system FIRST:**

```python
# ORM-based operator interface
class KGASOperator:
    def __init__(self, operator_id: str):
        self.roles = self.define_roles()
    
    def define_roles(self) -> OperatorRoles:
        """Define semantic input/output roles"""
        pass
    
    def invoke(self, request: OperatorRequest) -> OperatorResult:
        """StructGPT-style interface method"""
        pass
    
    def can_connect_to(self, other: 'KGASOperator') -> bool:
        """Check semantic role compatibility"""
        return self.output_roles.matches(other.input_roles)
```

**Implementation steps:**
1. Create OperatorRoles and semantic type system
2. Build compatibility checker using role matching
3. Wrap existing tools with operator interface

### Phase 3: Consolidate Tools into Operators (Week 3)
**Merge tools based on semantic roles:**

```python
# Example: T23_GraphExtractor internally uses T23C, T31, T34
class T23_GraphExtractor(KGASOperator):
    def define_roles(self):
        return OperatorRoles(
            inputs={"document": "text_content"},
            outputs={
                "entities": "named_entities",
                "graph": "graph_structure"
            }
        )
    
    def invoke(self, request):
        # Internally orchestrates T23C → T31 → T34
        entities = self._extract_entities(request.document)
        nodes = self._build_nodes(entities)
        edges = self._build_edges(entities)
        return GraphStructure(nodes, edges)
```

### Phase 4: Validate with Standard Pipelines (Week 4)
**Test ORM-based composition with real workflows:**

```python
# Define pipelines using role-based composition
pipeline_builder = ORMPipelineBuilder()

# System discovers valid chains via role matching
doc_to_graph = pipeline_builder.find_chain(
    start_role="file_path",
    end_role="graph_structure"
)
# Returns: [T01_Loader, T23_GraphExtractor]

# Test with real data
result = pipeline_builder.execute(
    chain=doc_to_graph,
    input_data={"file": "test.pdf"}
)
```

## Implementation Guidance

### What to Keep
- Core operations that are actually used
- The KGASTool interface (it's well-designed)
- Working pipelines (just formalize them)

### What to Delete  
- Tool protocol and all adapters
- Alias files (after migration)
- Duplicate versions (keep only unified)
- Tools that aren't used

### What to Refactor
- Merge T31/T34 into T23C
- Combine all loaders into one smart loader
- Standardize all field names
- Simplify tool IDs (T01 instead of T01_PDF_LOADER_UNIFIED)

### Migration Order
1. **Start with most-used pipeline**: PDF → Graph → Query
2. **Fix one pipeline completely** before moving to next
3. **Test each migration** with actual data
4. **Document working combinations**

## Critical Questions to Resolve

### Technical Questions
1. **Which interface wins?** KGASTool or Tool protocol? (Recommend: KGASTool)
2. **How to handle parameters?** Part of ToolRequest or separate?
3. **State management?** Some tools need previous iteration data
4. **Multi-input tools?** How to pass multiple data sources?

### Semantic Questions  
1. **Field name standards?** Who decides text vs content?
2. **Internal structures?** What's the canonical entity format?
3. **Optional fields?** How to handle when downstream requires them?
4. **Type specificity?** List[Dict] or List[EntitySchema]?

### Strategic Questions
1. **How many tools do we really need?** 10? 15? 20?
2. **Should we hardcode pipelines?** Or try for dynamic composition?
3. **Version compatibility?** Handle evolution or force updates?
4. **LLM planning?** How much can LLM actually figure out?

## Uncertainties & Risks

### Major Uncertainties
- **Actual tool usage**: Which of the 38 tools are actually used?
- **Hidden dependencies**: What breaks when we merge tools?
- **Performance impact**: Will consolidated tools be slower?
- **LLM capabilities**: Can LLM really plan tool sequences?

### Key Risks
1. **Breaking existing workflows** during migration
2. **Semantic mismatches** even with standard names
3. **Parameter/configuration complexity** not addressed
4. **State management** for iterative tools unresolved

## Success Metrics

### Week 1 Success
- [ ] T23C + T31 + T34 merged and working
- [ ] One complete pipeline migrated
- [ ] No decrease in functionality

### Week 2 Success  
- [ ] All tools use KGASTool interface
- [ ] Orchestrator updated
- [ ] Tool protocol deleted

### Week 3 Success
- [ ] Standard field names defined
- [ ] All tools use standard contracts
- [ ] Field mapping eliminated

### Week 4 Success
- [ ] 5-10 standard pipelines defined
- [ ] All pipelines tested with real data
- [ ] Documentation complete

## The Uncomfortable Truth

From reviewing unresolved_issues.md, simple contracts DON'T solve:
- Semantic compatibility between tools
- Parameter flow and configuration  
- Optional field handling
- Data transformation requirements
- Multi-input scenarios
- State management
- Version compatibility
- Complex type validation

**We might be better off with:**
- 10-15 well-designed tools (not 38)
- 5-10 hardcoded pipelines (not dynamic discovery)
- Explicit compatibility rules (not field name matching)
- Tested combinations (not theoretical compatibility)

## Recommendation (Updated with ORM Strategy)

**Build semantic compatibility using Object Role Modeling:**

1. **Reduce to ~15 operators** (like DIGIMON's 16) with clear semantic roles
2. **Use ORM for compatibility** - roles match, not field names
3. **Implement StructGPT-style interfaces** for clean data access
4. **Test with 3-5 core pipelines** before claiming general composability
5. **Start small** - get 5 operators working with ORM first

This ORM approach:
- **Solves the core problem** - semantic compatibility beyond syntax
- **Enables LLM discovery** - roles are understandable to LLMs
- **Scales better** - new operators just need role definitions
- **Matches your vision** - true dynamic composition

### Why ORM Over Previous Approaches
- **Field matching fails** - same name ≠ same meaning
- **Hardcoded pipelines limit** - no flexibility for LLM creativity
- **Type checking insufficient** - List[Dict] too generic
- **Role matching works** - semantic compatibility explicit

## Next Steps

1. **Inventory actual tool usage** - Which tools are really needed?
2. **Design consolidated tools** - What should T23_GraphExtractor look like?
3. **Create migration plan** - Order of operations for safe migration
4. **Build test suite** - Ensure nothing breaks during refactoring
5. **Start with one pipeline** - PDF → Graph → Query as proof of concept