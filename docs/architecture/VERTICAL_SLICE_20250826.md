# Clean Vertical Slice Architecture - 20250826

**Status**: Planning
**Author**: Brian + Claude
**Purpose**: Define a minimal but complete implementation that demonstrates all core capabilities without technical debt

## Executive Summary

Build a clean vertical slice using **standard knowledge graph extraction** that demonstrates the extensible tool composition framework with proper uncertainty propagation, using real databases. This avoids the existing technical debt while proving the core architectural concepts work end-to-end.

**Key Simplification**: Use standard KG extraction that gets entities AND relationships in one LLM call, rather than separate entity extraction and relationship inference steps.

## Core Design Principles

1. **No Legacy Baggage**: Start fresh, don't try to fix 10 different IdentityService implementations
2. **Uncertainty First**: Build uncertainty propagation in from the ground up using construct mapping approach
3. **Real Databases**: Actually use Neo4j for graphs, SQLite for tabular analysis
4. **Truly Modular**: Each tool is independent, framework discovers chains based on semantic types
5. **Fail Fast**: No mocks, no graceful fallbacks - surface errors immediately

### Uncertainty Principle Clarification
**Not all deterministic operations are equal**:
- **Lossy operations** (TextLoader): Have uncertainty even when successful because information can be lost
- **Lossless operations** (GraphPersister): Have zero uncertainty when successful because they preserve data exactly
- The key question: "Can this operation degrade the data even when it succeeds?"

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    3 Clean Tools                             │
│  ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐   │
│  │ TextLoader   │ │KnowledgeGraph    │ │GraphPersister│   │
│  │              │ │Extractor         │ │              │   │
│  │ file_path →  │ │ text →           │ │ kg_data →    │   │
│  │ document_text│ │ knowledge_graph  │ │ neo4j_graph  │   │
│  └──────────────┘ └──────────────────┘ └──────────────┘   │
│         ↓                ↓                    ↓             │
│    uncertainty      uncertainty          uncertainty        │
│      0.15              0.25                 0.10            │
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
│  │ deduplication│ │ + uncertainty│ │ conversions │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    2 Databases                               │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │     Neo4j              │    │     SQLite             │  │
│  │                        │    │                        │  │
│  │ • Nodes & Properties   │    │ • Entity Metrics       │  │
│  │ • Edges & Properties   │    │ • Statistical Tables   │  │
│  │ • Vector Embeddings    │    │ • Correlation Matrices │  │
│  └────────────────────────┘    └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Clean Service Layer (Day 1)

#### 1.1 IdentityService (Simplified)
```python
# /tool_compatability/poc/services/identity_service.py
class IdentityService:
    """
    Simplified for MVP - just handles entity deduplication across extractions
    The bug fix (creating Entity nodes) is handled in GraphPersister
    """
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def find_similar_entities(self, name: str, threshold: float = 0.8) -> List[Dict]:
        """
        Find entities with similar names (for deduplication)
        MVP: Simple string matching, can add embeddings later
        """
        query = """
        MATCH (e:Entity)
        WHERE toLower(e.canonical_name) CONTAINS toLower($name)
        RETURN e.entity_id as id, e.canonical_name as name
        LIMIT 10
        """
        # Returns list of similar entities
    
    def merge_entities(self, entity_id1: str, entity_id2: str) -> str:
        """
        Merge two entities that refer to the same real-world entity
        Not critical for MVP - can be manual process initially
        """
        # Merges relationships, keeps one canonical entity
```

**✅ SIMPLIFIED**: 
- No complex resolution needed for MVP
- Bug fix moved to GraphPersister where entities are created
- Can enhance with embeddings and better matching later

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
    """
    Handles graph↔table conversions using hypergraph approach
    Treats edges as n-ary relations with properties as columns
    """
    def __init__(self, neo4j_driver, sqlite_conn):
        self.neo4j = neo4j_driver
        self.sqlite = sqlite_conn
    
    def graph_to_table(self, entity_ids: List[str]) -> pd.DataFrame:
        """
        Export graph to relational tables for statistical analysis
        
        Creates two tables:
        1. entity_metrics: node properties and graph metrics
        2. relationships: edges as rows with properties as columns
        """
        # Get entities and calculate metrics
        entity_query = """
        MATCH (e:Entity)
        WHERE e.entity_id IN $entity_ids
        OPTIONAL MATCH (e)-[r]-()
        RETURN e.entity_id as id,
               e.canonical_name as name,
               e.entity_type as type,
               count(DISTINCT r) as degree,
               properties(e) as properties
        """
        
        # Get relationships (hypergraph as table)
        relationship_query = """
        MATCH (s:Entity)-[r]->(t:Entity)
        WHERE s.entity_id IN $entity_ids
        RETURN s.entity_id as source,
               t.entity_id as target,
               type(r) as relationship_type,
               properties(r) as properties
        """
        
        # Write to SQLite tables
        # This is the straightforward mapping you described
    
    def table_to_graph(self, relationships_df: pd.DataFrame) -> Dict:
        """
        Convert relational table to graph
        Each row becomes an edge with properties
        """
        created_edges = 0
        for _, row in relationships_df.iterrows():
            # Create edge in Neo4j
            query = """
            MATCH (s:Entity {entity_id: $source})
            MATCH (t:Entity {entity_id: $target})
            CREATE (s)-[r:$rel_type]->(t)
            SET r += $properties
            """
            # Execute query
            created_edges += 1
        
        return {"edges_created": created_edges}
```

**✅ SIMPLIFIED**:
- Hypergraph approach: edges as rows, properties as columns
- Straightforward bidirectional mapping
- No complex threshold decisions needed

### Phase 2: Tool Implementation with Uncertainty (Day 2)

#### 2.0 Uncertainty Constants Configuration
```python
# /tool_compatability/poc/config/uncertainty_constants.py
"""
Configurable uncertainty constants for deterministic operations
These are clearly labeled and easily adjustable, not buried in code
"""

# TextLoader uncertainties by file type
TEXT_LOADER_UNCERTAINTY = {
    "pdf": 0.15,      # OCR challenges, formatting loss
    "txt": 0.02,      # Nearly perfect extraction
    "docx": 0.08,     # Some formatting complexity
    "html": 0.12,     # Tag stripping, structure loss
    "md": 0.03,       # Clean markdown extraction
    "rtf": 0.10,      # Format conversion challenges
    "default": 0.10   # Unknown file types
}

# Reasoning templates
TEXT_LOADER_REASONING = {
    "pdf": "PDF extraction may have OCR errors or formatting loss",
    "txt": "Plain text extraction with minimal uncertainty",
    "docx": "Word document with potential formatting complexity",
    "html": "HTML parsing may lose semantic structure",
    "md": "Markdown extraction preserves structure well",
    "default": "Standard uncertainty for file format extraction"
}
```

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
        Use configurable constants for file type uncertainty
        """
        from config.uncertainty_constants import TEXT_LOADER_UNCERTAINTY, TEXT_LOADER_REASONING
        
        file_extension = input_file.path.split('.')[-1].lower()
        uncertainty = TEXT_LOADER_UNCERTAINTY.get(file_extension, TEXT_LOADER_UNCERTAINTY["default"])
        reasoning = TEXT_LOADER_REASONING.get(file_extension, TEXT_LOADER_REASONING["default"])
        
        return UncertaintyAssessment(
            score=uncertainty,
            reasoning=reasoning
        )
```

**✅ CLARIFIED**:
- Using configurable constants from uncertainty_constants.py
- Clear reasoning templates for each file type
- No LLM needed for deterministic file operations

#### 2.2 KnowledgeGraphExtractor
```python
# /tool_compatability/poc/tools/knowledge_graph_extractor.py
class KnowledgeGraphExtractor(ExtensibleTool):
    def __init__(self, llm_client, chunk_size=4000, overlap=200, schema_mode="open"):
        self.llm = llm_client
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.schema_mode = schema_mode  # open/closed/hybrid
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="KnowledgeGraphExtractor",
            input_type=DataType.TEXT,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="document_text",
            output_construct="knowledge_graph",
            transformation_type="knowledge_graph_extraction",
            semantic_input=SemanticType.DOCUMENT_TEXT,
            semantic_output=SemanticType.KNOWLEDGE_GRAPH
        )
    
    def process(self, input_data: str, context: ToolContext) -> ToolResult:
        # Handle chunking if text is too long
        if len(input_data) > self.chunk_size:
            chunks = self._create_chunks(input_data)
            kg_chunks = []
            
            for chunk in chunks:
                kg_data = self._extract_knowledge_graph(chunk)
                kg_chunks.append(kg_data)
            
            # Merge all chunks into single graph
            final_kg = self._merge_knowledge_graphs(kg_chunks)
        else:
            # Single extraction for short text
            final_kg = self._extract_knowledge_graph(input_data)
        
        # Single unified uncertainty assessment for entire extraction
        uncertainty = self._assess_extraction_uncertainty(
            text_length=len(input_data),
            entity_count=len(final_kg['entities']),
            relationship_count=len(final_kg['relationships']),
            chunk_count=len(chunks) if len(input_data) > self.chunk_size else 1
        )
        
        return ToolResult(
            success=True,
            data=final_kg,
            uncertainty=uncertainty.score,
            reasoning=uncertainty.reasoning
        )
    
    def _extract_knowledge_graph(self, text: str) -> Dict:
        """
        Standard knowledge graph extraction - entities AND relationships in one call
        """
        prompt = """
        Extract a knowledge graph from the following text.
        
        Return JSON with:
        {
          "entities": [
            {
              "id": "unique_identifier",
              "name": "entity name",
              "type": "person|organization|location|event|concept",
              "attributes": {"key": "value"}
            }
          ],
          "relationships": [
            {
              "source": "source_entity_id",
              "target": "target_entity_id",
              "type": "relationship_type",
              "attributes": {"key": "value"}
            }
          ]
        }
        
        Text: {text}
        """
        
        # Get structured output based on schema mode
        if self.schema_mode == "open":
            # Accept any properties
            kg_data = self.llm.extract_structured(prompt, response_format="json")
        elif self.schema_mode == "closed":
            # Enforce specific schema
            kg_data = self.llm.extract_structured(prompt, response_format=KGSchema)
        else:  # hybrid
            # Required fields + additional allowed
            kg_data = self.llm.extract_structured(prompt, response_format=HybridKGSchema)
        
        return kg_data
```

**✅ CLARIFICATIONS**:
- Chunking handled same as everything else (4000 chars with overlap)
- Schema mode supports open/closed/hybrid as requested
- Standard extraction gets entities AND relationships together
- Entity deduplication not a concern for MVP (per your feedback)

#### 2.3 GraphPersister
```python
# /tool_compatability/poc/tools/graph_persister.py
class GraphPersister(ExtensibleTool):
    def __init__(self, neo4j_driver, identity_service, crossmodal_service):
        self.neo4j = neo4j_driver
        self.identity = identity_service
        self.crossmodal = crossmodal_service
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphPersister",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH,
            input_construct="knowledge_graph",
            output_construct="persisted_graph",
            transformation_type="graph_persistence",
            semantic_input=SemanticType.KNOWLEDGE_GRAPH,
            semantic_output=SemanticType.NEO4J_GRAPH
        )
    
    def process(self, input_data: Dict, context: ToolContext) -> ToolResult:
        """
        Persist knowledge graph to Neo4j
        Input format: {"entities": [...], "relationships": [...]}
        """
        entities = input_data['entities']
        relationships = input_data['relationships']
        
        # Create entities in Neo4j (fixing the IdentityService bug here!)
        entity_map = {}  # Map from extraction IDs to Neo4j IDs
        for entity in entities:
            neo4j_id = self._create_or_merge_entity(entity)
            entity_map[entity['id']] = neo4j_id
        
        # Create relationships in Neo4j
        relationship_count = 0
        for rel in relationships:
            source_id = entity_map.get(rel['source'])
            target_id = entity_map.get(rel['target'])
            
            if source_id and target_id:
                self._create_relationship(source_id, target_id, rel)
                relationship_count += 1
        
        # Export graph metrics to SQLite for cross-modal analysis
        if self.crossmodal:
            self.crossmodal.graph_to_table(list(entity_map.values()))
        
        # Assess persistence uncertainty
        # IMPORTANT: GraphPersister has zero uncertainty on success because it's a pure
        # storage operation - no transformation or interpretation occurs.
        # This is different from TextLoader which can lose information even when "successful"
        if len(entity_map) == len(entities) and relationship_count == len(relationships):
            # All operations succeeded - data is in Neo4j EXACTLY as provided
            uncertainty = 0.0
            reasoning = "All entities and relationships successfully persisted to Neo4j with perfect fidelity"
        else:
            # Some operations failed
            failed_entities = len(entities) - len(entity_map)
            failed_rels = len(relationships) - relationship_count
            uncertainty = (failed_entities + failed_rels) / (len(entities) + len(relationships))
            reasoning = f"Failed to persist {failed_entities} entities and {failed_rels} relationships"
        
        return ToolResult(
            success=True,
            data={
                'entities_created': len(entity_map),
                'relationships_created': relationship_count,
                'neo4j_ids': entity_map
            },
            uncertainty=uncertainty.score,
            reasoning=uncertainty.reasoning
        )
    
    def _create_or_merge_entity(self, entity: Dict) -> str:
        """
        Create or merge entity in Neo4j (FIXES THE BUG!)
        Actually creates Entity nodes, not just Mentions
        """
        query = """
        MERGE (e:Entity {canonical_name: $name})
        ON CREATE SET
            e.entity_id = $entity_id,
            e.entity_type = $entity_type,
            e.created_at = datetime()
        SET e += $attributes
        RETURN e.entity_id as entity_id
        """
        
        with self.neo4j.session() as session:
            result = session.run(
                query,
                name=entity['name'],
                entity_id=f"entity_{uuid.uuid4().hex[:12]}",
                entity_type=entity['type'],
                attributes=entity.get('attributes', {})
            )
            return result.single()['entity_id']
```

**✅ CLARIFICATIONS**:
- No relationship inference needed - they come from KnowledgeGraphExtractor
- GraphPersister just writes what it receives to Neo4j
- Fixes IdentityService bug by actually creating Entity nodes
- Exports metrics to SQLite for cross-modal analysis

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

### 1. Uncertainty Assessment Implementation ✅ RESOLVED

**Decision**: Mixed approach based on tool type

**Implementation**:
- **KnowledgeGraphExtractor**: Option A - Single LLM call returns graph + uncertainty + reasoning
- **GraphPersister**: 0.0 uncertainty if successful (see distinction below)
- **TextLoader**: Configurable constants in `uncertainty_constants.py` (not buried in code)

**Critical Distinction - Not All Deterministic Operations Are Equal**:
- **TextLoader** is deterministic BUT can do its job badly (e.g., PDF→text loses formatting, OCR errors)
  - Even when "successful", uncertainty exists about extraction quality
  - Hence configurable uncertainty values (PDF=0.15, TXT=0.02)
- **GraphPersister** is different - if it succeeds, the job is done perfectly
  - Success means nodes/edges are in Neo4j exactly as specified
  - No quality degradation possible - either written or not
  - Hence uncertainty = 0.0 on success

**Key Principle**: Uncertainty measures "how well did we preserve/transform meaning?"
- TextLoader: Can lose meaning even when "successful" (formatting, special chars, etc.)
- GraphPersister: Preserves exactly what it receives - no transformation uncertainty

### 2. Service Initialization
**Question**: How do we handle service dependencies cleanly?

**Current mess**: ServiceManager has complex initialization with multiple patterns
**Proposed**: Simple dependency injection in tool constructors

**Concerns**:
- Database connection management
- Service lifecycle
- Testing without real databases

### 3. Performance vs Accuracy Trade-offs
**Question**: What's our position on performance for the MVP?

**Options**:
- **Accuracy first**: Full LLM assessments, complete analysis (slow but correct)
- **Performance first**: Cached assessments, batching (fast but approximate)
- **Configurable**: Let user choose accuracy/performance level

### 4. Testing Strategy
**Question**: How do we test the vertical slice end-to-end?

**Specific needs**:
- Test data (what document to use?)
- Expected outputs (how many entities/relationships expected?)
- Database verification (how to check Neo4j and SQLite correctly populated?)

**Resolved Questions** (based on your feedback):
- ✅ Entity Resolution: Simple string matching is fine for MVP
- ✅ Relationship Inference: Not needed - KnowledgeGraphExtractor handles it
- ✅ Cross-Modal Triggers: Explicit tools, not automatic
- ✅ Aggregation Identification: Not relevant for this 3-tool chain
- ✅ Schema Enforcement: Start with open schema
- ✅ Chunking: Same as everything else (4000 chars with overlap)

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