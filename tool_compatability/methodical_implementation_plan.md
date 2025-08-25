# Methodical Implementation Plan for ORM-Based Tool Refactoring

## Core Hypothesis to Validate

**Hypothesis**: Object Role Modeling (ORM) with semantic role matching will enable dynamic tool composition where:
1. Tools can discover compatibility through role semantics
2. LLMs can understand and create valid chains
3. The system scales better than field-name matching

## Phase 0: Proof of Concept (Days 1-3)

### Goal
Validate ORM concept with minimal implementation before full refactor.

### Implementation
```python
# Pick 3 tools that SHOULD compose: T03 → T15A → T23C
# Create minimal ORM wrappers

class MinimalORMWrapper:
    def __init__(self, tool, input_roles, output_roles):
        self.tool = tool
        self.input_roles = input_roles
        self.output_roles = output_roles
    
    def can_connect(self, other):
        # Test semantic matching
        return any(
            out_role.semantic_type == in_role.semantic_type
            for out_role in self.output_roles
            for in_role in other.input_roles
        )

# Test with real tools
t03_orm = MinimalORMWrapper(
    T03TextLoader(),
    input_roles=[Role("file_path", "file_reference")],
    output_roles=[Role("content", "text_content")]
)

t15a_orm = MinimalORMWrapper(
    T15AChunker(),
    input_roles=[Role("text", "text_content")],  # Matches T03 output!
    output_roles=[Role("chunks", "text_segments")]
)

# Validate: Can we detect compatibility?
assert t03_orm.can_connect(t15a_orm) == True
```

### Validation Criteria
- [ ] Can detect valid connections (T03 → T15A)
- [ ] Can detect invalid connections (T03 → T68)
- [ ] Can execute simple 3-tool pipeline
- [ ] Performance acceptable (<100ms overhead)

### Decision Gate
**STOP if ORM doesn't provide clear benefits over field matching**

## Phase 1: Build Core Infrastructure (Days 4-7)

### Goal
Create the ORM compatibility system without modifying existing tools.

### Components to Build

#### 1.1 Semantic Type Registry
```python
# semantic_types.py
class SemanticTypeRegistry:
    TYPES = {
        # Data representations
        "text_content": "Raw text document",
        "text_segments": "Chunked text pieces",
        "named_entities": "Extracted entities with types",
        "entity_relationships": "Relations between entities",
        
        # Graph representations  
        "graph_nodes": "Nodes for graph database",
        "graph_edges": "Edges connecting nodes",
        "graph_structure": "Complete graph with nodes and edges",
        
        # Vector representations
        "vector_embeddings": "Semantic vector representations",
        
        # Query representations
        "query_request": "Graph query specification",
        "query_results": "Results from graph query"
    }
    
    def compatible(self, type1: str, type2: str) -> bool:
        # Define compatibility rules
        COMPATIBILITY = {
            ("text_content", "text_content"): True,
            ("named_entities", "named_entities"): True,
            ("text_segments", "text_content"): True,  # Chunks can be treated as text
            # Add more rules
        }
        return COMPATIBILITY.get((type1, type2), False)
```

#### 1.2 Role Definition System
```python
# operator_roles.py
@dataclass
class Role:
    name: str                   # Internal name
    semantic_type: str          # From registry
    cardinality: Cardinality    # ONE, ZERO_OR_ONE, etc.
    description: str            # Human-readable
    
@dataclass
class OperatorRoles:
    operator_id: str
    inputs: Dict[str, Role]
    outputs: Dict[str, Role]
    
    def matches(self, other: 'OperatorRoles') -> Dict[str, str]:
        """Returns mapping of compatible roles"""
        mappings = {}
        for out_name, out_role in self.outputs.items():
            for in_name, in_role in other.inputs.items():
                if SemanticTypeRegistry.compatible(
                    out_role.semantic_type, 
                    in_role.semantic_type
                ):
                    mappings[out_name] = in_name
        return mappings
```

#### 1.3 Operator Base Class
```python
# kgas_operator.py
class KGASOperator(ABC):
    def __init__(self, operator_id: str):
        self.operator_id = operator_id
        self.roles = self.define_roles()
        
    @abstractmethod
    def define_roles(self) -> OperatorRoles:
        """Define semantic input/output roles"""
        pass
    
    @abstractmethod
    def invoke(self, request: OperatorRequest) -> OperatorResult:
        """Execute operator logic"""
        pass
    
    def can_chain_with(self, other: 'KGASOperator') -> bool:
        """Check if this operator's output can feed other's input"""
        return bool(self.roles.matches(other.roles))
```

### Testing Strategy
1. **Unit tests** for each component
2. **Integration test** with wrapped tools
3. **No changes to existing tools yet**

## Phase 2: Wrap Existing Tools (Days 8-10)

### Goal
Create operator wrappers for existing tools WITHOUT modifying them.

### Priority Order (based on most-used pipeline)
1. **T01** → T01_Loader (PDF/text loading)
2. **T15A** → T15_Chunker (text chunking)
3. **T23C+T31+T34** → T23_GraphExtractor (entity extraction + graph building)
4. **T49** → T49_Query (graph querying)
5. **T68** → T68_PageRank (graph analysis)

### Wrapper Template
```python
class T01_LoaderOperator(KGASOperator):
    def __init__(self):
        super().__init__("T01_Loader")
        self.legacy_tool = T01PDFLoader()  # Existing tool
        
    def define_roles(self) -> OperatorRoles:
        return OperatorRoles(
            operator_id=self.operator_id,
            inputs={
                "file": Role(
                    name="file",
                    semantic_type="file_reference",
                    cardinality=Cardinality.ONE,
                    description="Path to document file"
                )
            },
            outputs={
                "content": Role(
                    name="content",
                    semantic_type="text_content",
                    cardinality=Cardinality.ONE,
                    description="Extracted text content"
                )
            }
        )
    
    def invoke(self, request: OperatorRequest) -> OperatorResult:
        # Adapt between new interface and legacy tool
        legacy_result = self.legacy_tool.execute({
            "file_path": request.data["file"]
        })
        
        return OperatorResult(
            status="success",
            data={"content": legacy_result["text"]},
            semantic_types={"content": "text_content"}
        )
```

### Validation Tests
For each wrapped operator:
1. **Standalone test**: Operator works with test data
2. **Compatibility test**: Detects valid/invalid connections
3. **Pipeline test**: Works in expected chains

## Phase 3: Test Core Pipelines (Days 11-14)

### Goal
Validate that ORM-based composition works for real workflows.

### Test Pipelines (in order)

#### Pipeline 1: Document to Graph
```python
# Most critical pipeline
pipeline = [T01_Loader, T15_Chunker, T23_GraphExtractor]

test_cases = [
    "simple_text.txt",
    "complex_pdf.pdf", 
    "large_document.pdf"
]

for doc in test_cases:
    result = execute_pipeline(pipeline, {"file": doc})
    assert "graph_structure" in result
    assert validate_graph(result["graph_structure"])
```

#### Pipeline 2: Graph Analysis
```python
pipeline = [T49_Query, T68_PageRank]

test_queries = [
    "Find all persons",
    "Get relationships for John Smith",
    "Calculate importance scores"
]
```

#### Pipeline 3: Multi-Document Fusion
```python
pipeline = [T01_Loader, T23_GraphExtractor, T301_Fusion]

test_docs = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
```

### Success Metrics
- [ ] All test pipelines execute successfully
- [ ] Performance within 20% of current system
- [ ] Results quality matches or exceeds current
- [ ] Memory usage acceptable

## Phase 4: LLM Integration Testing (Days 15-17)

### Goal
Validate that LLMs can understand and use the ORM system.

### Test Scenarios

#### 4.1 Operator Discovery
```python
prompt = """
Given these operators and their roles:
{operator_descriptions}

Question: What operators would you use to extract entities from a PDF?

Think step by step about semantic roles.
"""

# LLM should identify: T01_Loader → T23_GraphExtractor
```

#### 4.2 Chain Composition
```python
prompt = """
You have operators with these roles:
- T01_Loader: file_reference → text_content
- T15_Chunker: text_content → text_segments  
- T23_GraphExtractor: text_content → graph_structure
- T49_Query: graph_structure + query → query_results

Create a pipeline to answer questions about a PDF.
"""

# LLM should compose: T01 → T23 → T49
```

#### 4.3 Invalid Chain Detection
```python
prompt = """
Can you connect:
T01_Loader (produces: text_content) → 
T68_PageRank (requires: graph_structure)?

Explain why or why not based on semantic roles.
"""

# LLM should recognize incompatibility
```

### Success Criteria
- [ ] LLM correctly identifies compatible operators 80%+ of time
- [ ] LLM creates valid pipelines for common tasks
- [ ] LLM explains compatibility decisions correctly

## Phase 5: Consolidate Tools (Days 18-21)

### Goal
Actually merge tools that belong together, guided by ORM roles.

### Consolidation Plan

#### Step 1: T23_GraphExtractor
Merge T23C + T31 + T34 into single operator:
```python
class T23_GraphExtractor(KGASOperator):
    def invoke(self, request):
        # Single operation from text to graph
        text = request.data["content"]
        
        # Internal pipeline (hidden from users)
        entities = self._extract_entities(text)
        nodes = self._build_nodes(entities)
        edges = self._build_edges(entities)
        
        # Store complete graph
        graph = self.neo4j_service.create_graph(nodes, edges)
        
        return OperatorResult(
            data={"graph": graph},
            semantic_types={"graph": "graph_structure"}
        )
```

#### Step 2: T01_UniversalLoader
Merge all loaders (T01-T14) with format detection:
```python
class T01_UniversalLoader(KGASOperator):
    def invoke(self, request):
        file_path = request.data["file"]
        format = detect_format(file_path)
        
        loader = {
            "pdf": self._load_pdf,
            "txt": self._load_text,
            "json": self._load_json,
            # etc.
        }[format]
        
        return loader(file_path)
```

### Testing After Each Consolidation
1. Run all pipelines from Phase 3
2. Compare results with pre-consolidation
3. Check performance metrics

## Phase 6: Full System Validation (Days 22-24)

### Goal
Validate complete system before removing old code.

### Comprehensive Tests

#### 6.1 All Historical Pipelines
```python
# Test every pipeline that ever worked
HISTORICAL_PIPELINES = load_from_evidence_files()

for pipeline in HISTORICAL_PIPELINES:
    old_result = execute_legacy(pipeline, test_data)
    new_result = execute_orm(pipeline, test_data)
    
    assert results_equivalent(old_result, new_result)
```

#### 6.2 Stress Testing
- Large documents (>1000 pages)
- Many documents (>100 files)
- Complex graphs (>10000 nodes)
- Concurrent pipelines

#### 6.3 Edge Cases
- Empty documents
- Malformed data
- Missing service connections
- Invalid semantic types

### Performance Benchmarks
```python
Metric              Target      Acceptable
-----------------------------------------
Latency overhead    <50ms       <100ms
Memory overhead     <10%        <20%
Throughput          Same        -10%
```

## Phase 7: Migration & Cleanup (Days 25-28)

### Goal
Remove old code and fully migrate to ORM system.

### Steps
1. **Update all references** to use new operators
2. **Remove Tool protocol** and adapters
3. **Delete duplicate tool versions**
4. **Update documentation**
5. **Create migration guide**

### Rollback Plan
- Git branch with old system preserved
- Feature flag to switch between systems
- Monitoring to detect issues

## Risk Mitigation

### Risk 1: ORM Doesn't Improve Composability
**Mitigation**: Test in Phase 0 before committing
**Fallback**: Use hardcoded pipelines with better documentation

### Risk 2: Performance Degradation
**Mitigation**: Benchmark at each phase
**Fallback**: Optimize hot paths or cache role matching

### Risk 3: LLMs Can't Understand Roles
**Mitigation**: Test early in Phase 4
**Fallback**: Provide examples and better prompts

### Risk 4: Semantic Types Too Rigid
**Mitigation**: Allow type aliases and inheritance
**Fallback**: Expand compatibility rules

## Success Metrics

### Technical Metrics
- [ ] 15 operators replace 38 tools
- [ ] All historical pipelines work
- [ ] Performance within 10% of current
- [ ] Memory usage reduced

### Usability Metrics  
- [ ] LLM can compose valid pipelines
- [ ] New operators easier to add
- [ ] Clear compatibility rules
- [ ] Better error messages

### Code Quality Metrics
- [ ] Lines of code reduced by 30%+
- [ ] Test coverage >80%
- [ ] No duplicate implementations
- [ ] Single interface pattern

## Decision Gates

### After Phase 0 (Day 3)
**Continue if**: ORM shows clear benefits
**Stop if**: No improvement over field matching

### After Phase 3 (Day 14)
**Continue if**: Core pipelines work
**Pivot if**: Major issues, consider hybrid approach

### After Phase 4 (Day 17)
**Continue if**: LLMs understand system
**Pivot if**: LLMs confused, simplify roles

### After Phase 6 (Day 24)
**Deploy if**: All tests pass
**Delay if**: Performance or quality issues

## Timeline Summary

```
Week 1: Validate concept, build infrastructure
Week 2: Wrap tools, test pipelines
Week 3: LLM testing, consolidation
Week 4: Full validation, migration
```

## Next Immediate Steps

1. **Today**: Create Phase 0 proof of concept
2. **Tomorrow**: Test with T03 → T15A → T23C chain
3. **Day 3**: Make go/no-go decision
4. **Day 4**: Start infrastructure if POC succeeds

This methodical approach ensures we validate each assumption before committing to the full refactor, with clear decision points and fallback options throughout.