# Clean Vertical Slice Architecture - 20250826

**Status**: Planning
**Author**: Brian + Claude
**Purpose**: Define a minimal but complete implementation that demonstrates all core capabilities without technical debt

## Executive Summary

Build a clean vertical slice that demonstrates the extensible tool composition framework with proper uncertainty propagation, using real databases and services. This avoids the existing technical debt while proving the core architectural concepts work end-to-end.

## Core Design Principles

1. **No Legacy Baggage**: Start fresh, don't try to fix 10 different IdentityService implementations
2. **Uncertainty First**: Build uncertainty propagation in from the ground up using construct mapping approach
3. **Real Databases**: Actually use Neo4j for graphs, SQLite for tabular analysis
4. **Truly Modular**: Each tool is independent, framework discovers chains based on semantic types
5. **Fail Fast**: No mocks, no graceful fallbacks - surface errors immediately

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    3 Clean Tools                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ TextLoader   │ │EntityExtractor│ │ GraphBuilder │       │
│  │              │ │              │ │              │       │
│  │ file_path →  │ │ text →       │ │ entities →   │       │
│  │ character_seq│ │ semantic_units│ │ graph_struct │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│         ↓                ↓                ↓                 │
│    uncertainty      uncertainty      uncertainty            │
│      0.15              0.25              0.20               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Extensible Framework                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • Type-based chain discovery                            │ │
│  │ • Semantic type compatibility checking                  │ │
│  │ • Uncertainty propagation (physics model)               │ │
│  │ • Automatic tool registration                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   3 Core Services                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │IdentityService│ │ProvenanceService│ │CrossModalService│ │
│  │              │ │              │ │              │       │
│  │ Entity       │ │ Track ops    │ │ Graph↔Table │       │
│  │ resolution   │ │ + uncertainty│ │ conversions │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    3 Databases                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │Neo4j Graph   │ │Neo4j Vectors │ │SQLite Tables │       │
│  │              │ │              │ │              │       │
│  │Entities,     │ │Embeddings,   │ │Metrics,      │       │
│  │Relationships │ │Similarity    │ │Statistics    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Clean Service Layer (Day 1)

#### 1.1 IdentityService
```python
# /tool_compatability/poc/services/identity_service.py
class IdentityService:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def create_entity(self, text: str, entity_type: str, uncertainty: float) -> str:
        """
        ACTUALLY creates Entity nodes in Neo4j (fixing the current bug!)
        Includes uncertainty score in the node properties
        """
        # Creates both Entity and Mention nodes
        # Links them properly
        # Returns entity_id
    
    def resolve_entity(self, mention_text: str) -> Tuple[str, float]:
        """
        Resolve mention to existing entity or create new one
        Returns (entity_id, resolution_uncertainty)
        """
```

**🔴 UNCERTAINTY**: 
- Should entity resolution uncertainty be separate from extraction uncertainty?
- How do we handle cases where multiple entities could match?
- Should we use embeddings for similarity or just string matching initially?

#### 1.2 ProvenanceService Enhancement
```python
# /tool_compatability/poc/services/provenance_service.py
class ProvenanceService:
    """Enhance existing ProvenanceService with uncertainty tracking"""
    
    def track_operation(self, 
                        tool_id: str,
                        operation: str,
                        inputs: Dict,
                        outputs: Dict,
                        uncertainty: float,
                        reasoning: str,
                        construct_mapping: str) -> str:
        """
        Track operation with uncertainty and construct mapping
        """
        # Store in SQLite with new fields:
        # - uncertainty (0-1)
        # - reasoning (text)
        # - construct_mapping (e.g., "file_path → character_sequence")
```

**✅ CLARITY**: This builds on the existing working ProvenanceService

#### 1.3 CrossModalService
```python
# /tool_compatability/poc/services/crossmodal_service.py
class CrossModalService:
    def __init__(self, neo4j_driver, sqlite_conn):
        self.neo4j = neo4j_driver
        self.sqlite = sqlite_conn
    
    def graph_to_table(self, entity_ids: List[str]) -> pd.DataFrame:
        """
        Export graph metrics to SQLite table for statistical analysis
        Calculate centrality, degree, clustering coefficient
        Store in entity_metrics table
        """
    
    def table_to_graph(self, correlation_matrix: pd.DataFrame) -> None:
        """
        Convert correlation matrix to graph structure
        Create edges for correlations above threshold
        """
    
    def assess_conversion_uncertainty(self, 
                                     source_format: str,
                                     target_format: str,
                                     data_characteristics: Dict) -> float:
        """
        Assess uncertainty of format conversion
        E.g., losing graph structure when converting to table
        """
```

**🔴 UNCERTAINTIES**:
- What's the minimum correlation threshold for creating edges?
- Should conversion uncertainty be tracked separately from analytical uncertainty?
- Do we need vector↔graph conversions in the MVP?

### Phase 2: Tool Implementation with Uncertainty (Day 2)

#### 2.1 TextLoaderV3
```python
# /tool_compatability/poc/tools/text_loader_v3.py
class TextLoaderV3(ExtensibleTool):
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="TextLoaderV3",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="character_sequence",
            transformation_type="text_extraction",
            semantic_input=None,  # No semantic requirement for input
            semantic_output=SemanticType.DOCUMENT_TEXT
        )
    
    def process(self, input_data: FileData, context: ToolContext) -> ToolResult:
        # Extract text from file
        text = self._extract_text(input_data.path)
        
        # Assess uncertainty of construct mapping
        uncertainty_assessment = self._assess_uncertainty(
            input_file=input_data,
            output_text=text
        )
        
        # Track in provenance
        self.provenance.track_operation(
            tool_id="TextLoaderV3",
            operation="text_extraction",
            uncertainty=uncertainty_assessment.score,
            reasoning=uncertainty_assessment.reasoning,
            construct_mapping="file_path → character_sequence"
        )
        
        return ToolResult(
            success=True,
            data=text,
            uncertainty=uncertainty_assessment.score,
            reasoning=uncertainty_assessment.reasoning
        )
    
    def _assess_uncertainty(self, input_file: FileData, output_text: str) -> UncertaintyAssessment:
        """
        Assess how well we extracted character sequence from file
        """
        # Factors to consider:
        # - File type (PDF vs TXT)
        # - OCR needed?
        # - Encoding issues?
        # - Formatting preserved?
```

**🔴 UNCERTAINTIES**:
- Should we use LLM for uncertainty assessment or rule-based initially?
- How detailed should the reasoning field be?
- Should we batch uncertainty assessments for performance?

#### 2.2 EntityExtractorV3
```python
# /tool_compatability/poc/tools/entity_extractor_v3.py
class EntityExtractorV3(ExtensibleTool):
    def __init__(self, llm_client, identity_service):
        self.llm = llm_client
        self.identity = identity_service
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="EntityExtractorV3",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            input_construct="character_sequence",
            output_construct="semantic_units",
            transformation_type="entity_extraction",
            semantic_input=SemanticType.DOCUMENT_TEXT,
            semantic_output=SemanticType.NAMED_ENTITIES
        )
    
    def process(self, input_data: str, context: ToolContext) -> ToolResult:
        # Extract entities using LLM
        extraction_result = self.llm.extract_entities(input_data)
        
        # Resolve entities using IdentityService
        resolved_entities = []
        for entity in extraction_result.entities:
            entity_id, resolution_uncertainty = self.identity.resolve_entity(
                entity.text, 
                entity.type
            )
            resolved_entities.append({
                'id': entity_id,
                'text': entity.text,
                'type': entity.type,
                'resolution_uncertainty': resolution_uncertainty
            })
        
        # Single unified uncertainty assessment
        uncertainty = self._assess_transformation_uncertainty(
            input_text=input_data,
            extracted_entities=resolved_entities
        )
        
        return ToolResult(
            success=True,
            data=resolved_entities,
            uncertainty=uncertainty.score,
            reasoning=uncertainty.reasoning
        )
```

**🔴 UNCERTAINTIES**:
- Should entity resolution be part of extraction or separate tool?
- How do we handle entity coreference (pronouns, aliases)?
- What LLM model/temperature for extraction?
- Should we chunk large texts?

#### 2.3 GraphBuilderV3
```python
# /tool_compatability/poc/tools/graph_builder_v3.py
class GraphBuilderV3(ExtensibleTool):
    def __init__(self, neo4j_driver, crossmodal_service):
        self.neo4j = neo4j_driver
        self.crossmodal = crossmodal_service
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphBuilderV3",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH,
            input_construct="semantic_units",
            output_construct="relationship_network",
            transformation_type="graph_construction",
            semantic_input=SemanticType.NAMED_ENTITIES,
            semantic_output=SemanticType.KNOWLEDGE_GRAPH
        )
    
    def process(self, input_data: List[Dict], context: ToolContext) -> ToolResult:
        # Build relationships between entities
        relationships = self._infer_relationships(input_data)
        
        # Write to Neo4j
        for rel in relationships:
            self._create_relationship(rel)
        
        # Export initial metrics to SQLite for analysis
        entity_ids = [e['id'] for e in input_data]
        metrics_df = self.crossmodal.graph_to_table(entity_ids)
        
        # Assess construction uncertainty
        uncertainty = self._assess_graph_construction_uncertainty(
            entities=input_data,
            relationships=relationships
        )
        
        return ToolResult(
            success=True,
            data={'entities': len(input_data), 'relationships': len(relationships)},
            uncertainty=uncertainty.score,
            reasoning=uncertainty.reasoning
        )
```

**🔴 UNCERTAINTIES**:
- How do we infer relationships between entities?
- Should relationship inference use LLM or proximity-based rules?
- What relationship types should we support initially?
- Should we calculate graph metrics immediately or on-demand?

### Phase 3: Framework Integration (Day 3)

#### 3.1 Enhanced Framework with Uncertainty
```python
# /tool_compatability/poc/framework_v2.py
class CleanToolFramework:
    def __init__(self, neo4j_uri: str, sqlite_path: str):
        # Real database connections
        self.neo4j = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "password"))
        self.sqlite = sqlite3.connect(sqlite_path)
        
        # Initialize services
        self.identity = IdentityService(self.neo4j)
        self.provenance = ProvenanceService(self.sqlite)
        self.crossmodal = CrossModalService(self.neo4j, self.sqlite)
        
        # Tool registry
        self.tools = {}
        self.capabilities = {}
    
    def execute_chain(self, chain: List[str], input_data: Any) -> ChainResult:
        """
        Execute tool chain with uncertainty propagation
        """
        uncertainties = []
        reasonings = []
        current_data = input_data
        
        for tool_id in chain:
            tool = self.tools[tool_id]
            
            # Execute tool
            result = tool.process(current_data, context=None)
            
            if not result.success:
                raise ToolExecutionError(f"{tool_id} failed: {result.error}")
            
            # Track uncertainty
            uncertainties.append(result.uncertainty)
            reasonings.append(result.reasoning)
            
            # Propagate data
            current_data = result.data
        
        # Combine uncertainties using physics model
        total_uncertainty = self._combine_sequential_uncertainties(uncertainties)
        
        return ChainResult(
            data=current_data,
            total_uncertainty=total_uncertainty,
            step_uncertainties=uncertainties,
            step_reasonings=reasonings
        )
    
    def _combine_sequential_uncertainties(self, uncertainties: List[float]) -> float:
        """
        Physics-style error propagation for sequential tools
        """
        confidence = 1.0
        for u in uncertainties:
            confidence *= (1 - u)
        return 1 - confidence
```

**✅ CLARITY**: This follows the physics error propagation model from our uncertainty document

### Phase 4: Testing & Validation (Day 4)

#### 4.1 End-to-End Test
```python
# /tool_compatability/poc/test_vertical_slice.py
def test_complete_pipeline():
    """Test file → entities → graph with uncertainty propagation"""
    
    # Setup
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="test_analysis.db"
    )
    
    # Register tools
    framework.register_tool(TextLoaderV3())
    framework.register_tool(EntityExtractorV3(llm_client, framework.identity))
    framework.register_tool(GraphBuilderV3(framework.neo4j, framework.crossmodal))
    
    # Create test file
    test_file = create_test_document()
    
    # Find chain
    chain = framework.find_chain(
        input_type=DataType.FILE,
        output_type=DataType.GRAPH,
        domain=Domain.GENERAL
    )
    
    # Execute
    result = framework.execute_chain(chain, test_file)
    
    # Verify
    assert result.total_uncertainty < 0.5  # Combined uncertainty reasonable
    assert len(result.step_uncertainties) == 3
    verify_neo4j_entities()
    verify_sqlite_metrics()
    verify_provenance_tracking()
```

**🔴 UNCERTAINTIES**:
- What's a reasonable uncertainty threshold for acceptance?
- Should we test with real LLM or mock for speed?
- How do we verify uncertainty assessments are reasonable?

## Critical Questions Needing Clarification

### 1. Uncertainty Assessment Implementation
**Question**: Should uncertainty assessment use LLM calls or rule-based heuristics initially?

**Options**:
- **Option A**: Every tool makes LLM call for uncertainty assessment (accurate but expensive)
- **Option B**: Rule-based for deterministic operations, LLM for complex assessments
- **Option C**: Hybrid - batch multiple assessments into single LLM call

**Trade-offs**: Cost vs accuracy vs latency

### 2. Entity Resolution Strategy
**Question**: How sophisticated should entity resolution be in the MVP?

**Options**:
- **Option A**: Simple string matching (fast but limited)
- **Option B**: Embedding-based similarity (more accurate but requires vectors)
- **Option C**: LLM-based resolution (most accurate but expensive)

**Current IdentityService bug**: Creates Mentions but not Entities - we need to fix this

### 3. Relationship Inference
**Question**: How do we infer relationships between entities for graph construction?

**Options**:
- **Option A**: Co-occurrence in same sentence/paragraph (simple but noisy)
- **Option B**: LLM-based relationship extraction (accurate but slow)
- **Option C**: Dependency parsing + rules (middle ground)

**Uncertainty impact**: Relationship quality directly affects graph analysis uncertainty

### 4. Cross-Modal Conversion Triggers
**Question**: When should we automatically trigger format conversions?

**Examples**:
- After building graph, auto-export metrics to SQLite?
- After computing correlations, auto-create correlation graph?
- Should conversions be explicit tools or automatic?

### 5. Service Initialization
**Question**: How do we handle service dependencies cleanly?

**Current mess**: ServiceManager has complex initialization with multiple patterns
**Proposed**: Simple dependency injection in tool constructors

**Concerns**:
- Database connection management
- Service lifecycle
- Testing without real databases

### 6. Performance vs Accuracy Trade-offs
**Question**: What's our position on performance for the MVP?

**Options**:
- **Accuracy first**: Full LLM assessments, complete analysis (slow but correct)
- **Performance first**: Cached assessments, batching (fast but approximate)
- **Configurable**: Let user choose accuracy/performance level

### 7. Aggregation Tool Identification
**Question**: How do tools self-identify as aggregators for uncertainty reduction?

**Proposed approach**:
```python
def process(self, input_data: List[Any], context):
    if len(input_data) > 1 and len(output) == 1:
        # This is aggregation - uncertainty likely reduces
        uncertainty = self._assess_aggregation_uncertainty()
```

**Concerns**: Not all many-to-one operations are aggregations

### 8. Testing Strategy
**Question**: How do we test uncertainty propagation correctness?

**Challenges**:
- Uncertainty is subjective by design
- No ground truth for validation
- LLM assessments vary between runs

**Options**:
- Test that uncertainties are within reasonable ranges
- Test that aggregation reduces uncertainty
- Test that known-bad inputs produce high uncertainty

## Success Criteria

### Minimum Viable Success
- [ ] One complete chain executes (File → Entities → Graph)
- [ ] Uncertainty propagates through chain
- [ ] Real Neo4j has entities and relationships
- [ ] Real SQLite has metrics table
- [ ] ProvenanceService tracks all operations with uncertainty

### Target Success
- [ ] All above plus...
- [ ] Cross-modal conversion works (graph → table)
- [ ] Semantic types prevent invalid chains
- [ ] Memory usage reasonable (<100MB for small file)
- [ ] Uncertainty assessments include detailed reasoning
- [ ] At least 10 entities extracted and linked

### Stretch Goals
- [ ] All above plus...
- [ ] Vector embeddings for entities
- [ ] Similarity-based entity resolution
- [ ] Correlation matrix → graph conversion
- [ ] Aggregation tool with uncertainty reduction
- [ ] Performance metrics tracking

## Risk Assessment

### High Risk Items
1. **LLM Cost**: Uncertainty assessment for every operation could be expensive
2. **Database Setup**: Requiring both Neo4j and SQLite increases complexity
3. **Service Fragmentation**: Current codebase has conflicting implementations

### Mitigation Strategies
1. **Cache assessments** for identical inputs
2. **Docker compose** for database setup
3. **Ignore existing code** - build clean from scratch

## Next Steps

1. **Resolve critical questions** above before implementation
2. **Set up clean directory** structure in `/tool_compatability/poc/vertical_slice/`
3. **Create database schemas** for all three databases
4. **Implement services** with minimal functionality
5. **Build tools** with uncertainty assessment
6. **Test end-to-end** with real data

## Open Questions for Brian

1. **Uncertainty Assessment**: LLM-based or rule-based for MVP?
2. **Entity Resolution**: How sophisticated should it be initially?
3. **Performance Target**: What's acceptable latency for 100-page document?
4. **Database Setup**: Should we use Docker or assume databases exist?
5. **Testing Strategy**: Mock LLM for tests or use real API?
6. **Semantic Types**: Should we use existing KGAS semantic types or create new ones?
7. **Error Handling**: Fail fast everywhere or some recovery attempts?

---

*Document created: 2025-08-26*
*Status: Awaiting clarification on open questions*
*Next update: After Brian's feedback on critical questions*