# Theory Extraction Integration Architecture

**Status**: Integration Planning  
**Related**: [Two-Layer Theory Architecture](./two-layer-theory-architecture.md)  
**Experimental System**: `/experiments/lit_review`  
**Target Integration**: Main KGAS Architecture  

## Executive Summary

This document defines the integration architecture for connecting the sophisticated theory extraction system (`/experiments/lit_review`) with the main KGAS service architecture. The experimental system is fully functional with proven capabilities - integration focuses on architectural connection rather than rebuilding functionality.

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Target Integration Architecture](#target-integration-architecture)
3. [Integration Approach](#integration-approach)
4. [Service Layer Integration](#service-layer-integration)
5. [Data Store Integration](#data-store-integration)
6. [Tool Pipeline Integration](#tool-pipeline-integration)
7. [MCP Protocol Integration](#mcp-protocol-integration)
8. [Implementation Phases](#implementation-phases)

## Current State Analysis

### Experimental System Capabilities

**Location**: `/experiments/lit_review`

**Proven Functionality**:
- **Layer 1 (Structure Extraction)**: 3-phase LLM-guided extraction with V13 meta-schema
- **Layer 2 (Theory Application)**: Universal theory applicator with multi-stage processing
- **Quality Assurance**: Multi-agent validation achieving 100/100 standards
- **Advanced Methods**: Context-aware refinement achieving 10/10 quality scores
- **Multi-Model Support**: O3, Gemini, GPT-4, Claude with intelligent fallbacks

**Key Components**:
```
/experiments/lit_review/
├── src/
│   ├── schema_creation/
│   │   └── multiphase_processor_improved.py     # 3-phase extraction
│   ├── schema_application/
│   │   └── universal_theory_applicator.py       # Theory application
│   ├── testing/                                 # Validation framework
│   ├── ui/                                      # Analysis interface
│   └── visualization/                           # Results visualization
├── multi_agent_system/                          # 100/100 quality methodology
├── schemas/                                     # Generated theory schemas
│   ├── young1996/                               # Cognitive mapping theory
│   ├── semantic_hypergraph/                     # Complex n-ary relations
│   └── elaboration_likelihood_model/            # Social psychology
└── results/                                     # Validation results
```

**Performance Metrics**:
- 100% success rate across 10 diverse theories
- 7 academic domains validated
- 8.95/10 average quality (10/10 with advanced methods)
- 20-105 seconds processing time per theory
- Multi-theory parallel processing capability

### Main KGAS Architecture

**Service-Oriented Architecture**:
```python
class ServiceManager:
    def __init__(self):
        self.identity_service = IdentityService()
        self.provenance_service = ProvenanceService()
        self.neo4j_manager = Neo4jManager()
        self.sqlite_manager = SQLiteManager()
        self.structured_llm_service = StructuredLLMService()
```

**Tool Pipeline Pattern**:
```python
class KGASTool:
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
    
    def execute(self, request: ToolRequest) -> ToolResult:
        # Standard tool interface with contracts
        pass
```

**Data Storage**:
- **Neo4j**: Graph data, entities, relationships, vectors
- **SQLite**: Metadata, provenance, workflow states

## Target Integration Architecture

### High-Level Integration Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    KGAS Main Architecture                    │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐ │
│  │ ServiceManager │ │  Tool Pipeline │ │  MCP Protocol    │ │
│  └───────┬────────┘ └───────┬────────┘ └─────────┬────────┘ │
└──────────┼──────────────────┼────────────────────┼──────────┘
           │                  │                    │
      ┌────▼──────────────────▼────────────────────▼────┐
      │           Integration Layer                      │
      │  ┌──────────────────────────────────────────┐   │
      │  │      TheoryExtractionService             │   │
      │  │  ┌─────────────┐ ┌─────────────────────┐ │   │
      │  │  │ Wrapper API │ │ Data Conversion     │ │   │
      │  │  └─────────────┘ └─────────────────────┘ │   │
      │  └──────────────────────────────────────────┘   │
      └─────────────────┼────────────────────────────────┘
                        │
      ┌─────────────────▼────────────────────────────────┐
      │        Experimental System (Preserved)           │
      │                /experiments/lit_review           │
      │  ┌──────────────────────────────────────────┐   │
      │  │  Multiphase Processor (Layer 1)          │   │
      │  │  Universal Applicator (Layer 2)           │   │
      │  │  Multi-Agent Validation                   │   │
      │  │  Advanced Quality Methods                 │   │
      │  └──────────────────────────────────────────┘   │
      └──────────────────────────────────────────────────┘
```

### Integration Design Principles

1. **Preserve Experimental System**: Do not modify working experimental code
2. **Wrapper Pattern**: Create integration layer that calls experimental system
3. **Service Architecture Compliance**: Integrate with ServiceManager pattern
4. **Data Format Bridge**: Convert between experimental and main system formats
5. **Tool Contract Compliance**: Wrap as standard KGAS tools
6. **MCP Exposure**: Make available via MCP protocol
7. **Performance Preservation**: Maintain experimental system's high performance

## Service Layer Integration

### TheoryExtractionService Implementation

```python
class TheoryExtractionService:
    """Service wrapper around experimental theory extraction system"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.identity_service = service_manager.identity_service
        self.provenance_service = service_manager.provenance_service
        self.neo4j_manager = service_manager.neo4j_manager
        self.sqlite_manager = service_manager.sqlite_manager
        
        # Initialize experimental system interface
        self.experimental_system = ExperimentalTheorySystem()
    
    def extract_theory(self, paper_path: str, theory_name: str) -> TheorySchema:
        """Extract theory using experimental system, integrate with KGAS services"""
        
        # Generate unique theory ID
        theory_id = self.identity_service.generate_theory_id(theory_name)
        
        # Track operation start
        operation_id = self.provenance_service.start_operation(
            tool_name="theory_extraction",
            inputs={"paper_path": paper_path, "theory_name": theory_name}
        )
        
        try:
            # Call experimental system (unchanged)
            experimental_result = self.experimental_system.extract_theory(
                paper_path=paper_path,
                output_path=None  # Keep in memory
            )
            
            # Convert to KGAS format
            kgas_schema = self._convert_experimental_to_kgas(
                experimental_result, theory_id
            )
            
            # Store in KGAS data stores
            self._store_theory_in_neo4j(kgas_schema)
            self._store_theory_metadata(kgas_schema)
            
            # Track successful completion
            self.provenance_service.complete_operation(
                operation_id, 
                outputs={"theory_id": theory_id, "quality_score": kgas_schema.quality_score}
            )
            
            return kgas_schema
            
        except Exception as e:
            self.provenance_service.fail_operation(operation_id, str(e))
            raise
    
    def apply_theory(self, theory_id: str, text: str, domain: str = "general") -> TheoryApplication:
        """Apply extracted theory to text using experimental system"""
        
        # Retrieve theory schema
        theory_schema = self._load_theory_from_neo4j(theory_id)
        
        # Convert to experimental format
        experimental_schema = self._convert_kgas_to_experimental(theory_schema)
        
        # Apply using experimental system
        application_result = self.experimental_system.apply_theory(
            schema=experimental_schema,
            text=text,
            domain=domain
        )
        
        # Convert back to KGAS format and store
        kgas_application = self._convert_application_to_kgas(application_result)
        self._store_application_results(kgas_application)
        
        return kgas_application
    
    def _convert_experimental_to_kgas(self, experimental_result: dict, theory_id: str) -> TheorySchema:
        """Convert experimental system output to KGAS schema format"""
        # Implementation handles format conversion
        pass
    
    def _store_theory_in_neo4j(self, schema: TheorySchema):
        """Store theory schema as nodes and relationships in Neo4j"""
        # Implementation creates graph representation
        pass
    
    def _store_theory_metadata(self, schema: TheorySchema):
        """Store theory metadata in SQLite"""
        # Implementation stores searchable metadata
        pass
```

### ExperimentalTheorySystem Interface

```python
class ExperimentalTheorySystem:
    """Interface to the experimental theory extraction system"""
    
    def __init__(self):
        # Set up paths to experimental system
        self.experimental_root = Path("/experiments/lit_review")
        self.processor_path = self.experimental_root / "src/schema_creation/multiphase_processor_improved.py"
        self.applicator_path = self.experimental_root / "src/schema_application/universal_theory_applicator.py"
        
        # Initialize experimental system components
        sys.path.insert(0, str(self.experimental_root))
        
    def extract_theory(self, paper_path: str, output_path: Optional[str] = None) -> dict:
        """Call experimental multiphase processor"""
        
        # Import experimental modules
        from src.schema_creation.multiphase_processor_improved import process_paper
        
        # Use experimental system directly
        result = process_paper(paper_path, output_path)
        
        return result
    
    def apply_theory(self, schema: dict, text: str, domain: str) -> dict:
        """Call experimental universal applicator"""
        
        # Import experimental modules
        from src.schema_application.universal_theory_applicator import UniversalTheoryApplicator
        
        # Create temporary schema file
        temp_schema_path = self._write_temp_schema(schema)
        
        try:
            # Use experimental system
            applicator = UniversalTheoryApplicator(temp_schema_path)
            result = applicator.apply(text, domain)
            
            return result.model_dump()
            
        finally:
            # Clean up temporary file
            temp_schema_path.unlink()
    
    def _write_temp_schema(self, schema: dict) -> Path:
        """Write schema to temporary file for experimental system"""
        # Implementation creates temp file
        pass
```

## Data Store Integration

### Neo4j Integration Pattern

```python
class TheoryGraphManager:
    """Manages theory storage in Neo4j"""
    
    def store_theory_schema(self, schema: TheorySchema):
        """Store theory as graph structure"""
        
        with self.neo4j_manager.get_session() as session:
            # Create theory node
            session.run("""
                CREATE (t:Theory {
                    theory_id: $theory_id,
                    name: $name,
                    citation: $citation,
                    model_type: $model_type,
                    quality_score: $quality_score,
                    created_at: datetime()
                })
            """, 
                theory_id=schema.theory_id,
                name=schema.name,
                citation=schema.citation,
                model_type=schema.model_type,
                quality_score=schema.quality_score
            )
            
            # Create entity nodes
            for entity_def in schema.entity_definitions:
                session.run("""
                    MATCH (t:Theory {theory_id: $theory_id})
                    CREATE (e:TheoryEntity {
                        entity_id: $entity_id,
                        name: $name,
                        category: $category,
                        description: $description
                    })
                    CREATE (t)-[:DEFINES_ENTITY]->(e)
                """,
                    theory_id=schema.theory_id,
                    entity_id=entity_def.entity_id,
                    name=entity_def.name,
                    category=entity_def.category,
                    description=entity_def.description
                )
            
            # Create relationship definitions
            for rel_def in schema.relationship_definitions:
                session.run("""
                    MATCH (t:Theory {theory_id: $theory_id})
                    CREATE (r:TheoryRelationship {
                        relationship_id: $relationship_id,
                        name: $name,
                        domain: $domain,
                        range: $range,
                        description: $description
                    })
                    CREATE (t)-[:DEFINES_RELATIONSHIP]->(r)
                """,
                    theory_id=schema.theory_id,
                    relationship_id=rel_def.relationship_id,
                    name=rel_def.name,
                    domain=rel_def.domain,
                    range=rel_def.range,
                    description=rel_def.description
                )
```

### SQLite Integration Pattern

```python
class TheoryMetadataManager:
    """Manages theory metadata in SQLite"""
    
    def __init__(self, sqlite_manager: SQLiteManager):
        self.sqlite_manager = sqlite_manager
        self._create_theory_tables()
    
    def _create_theory_tables(self):
        """Create theory-specific tables"""
        
        self.sqlite_manager.execute("""
            CREATE TABLE IF NOT EXISTS theories (
                theory_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                citation TEXT NOT NULL,
                model_type TEXT NOT NULL,
                quality_score REAL,
                extraction_method TEXT,
                paper_source TEXT,
                domain_coverage TEXT,
                entity_count INTEGER,
                relationship_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_applied TIMESTAMP
            )
        """)
        
        self.sqlite_manager.execute("""
            CREATE TABLE IF NOT EXISTS theory_applications (
                application_id TEXT PRIMARY KEY,
                theory_id TEXT,
                input_text_hash TEXT,
                domain TEXT,
                results_summary TEXT,
                confidence_score REAL,
                processing_time REAL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (theory_id) REFERENCES theories (theory_id)
            )
        """)
        
        self.sqlite_manager.execute("""
            CREATE TABLE IF NOT EXISTS theory_provenance (
                provenance_id TEXT PRIMARY KEY,
                theory_id TEXT,
                operation_type TEXT,
                input_data TEXT,
                output_data TEXT,
                processing_time REAL,
                quality_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (theory_id) REFERENCES theories (theory_id)
            )
        """)
    
    def store_theory_metadata(self, schema: TheorySchema):
        """Store searchable theory metadata"""
        
        self.sqlite_manager.execute("""
            INSERT INTO theories (
                theory_id, name, citation, model_type, quality_score,
                extraction_method, paper_source, domain_coverage,
                entity_count, relationship_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            schema.theory_id,
            schema.name,
            schema.citation,
            schema.model_type,
            schema.quality_score,
            schema.extraction_method,
            schema.paper_source,
            schema.domain_coverage,
            len(schema.entity_definitions),
            len(schema.relationship_definitions)
        ))
```

## Tool Pipeline Integration

### T-THEORY Tool Series

```python
class T01TheoryExtractionTool(KGASTool):
    """T01: Theory Extraction from Academic Papers"""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.theory_service = service_manager.theory_extraction_service
        self.tool_id = "T01_THEORY_EXTRACTION"
        self.version = "1.0.0"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute theory extraction"""
        
        # Validate inputs
        if not self._validate_inputs(request.input_data):
            return ToolResult.error("Invalid inputs for theory extraction")
        
        paper_path = request.input_data["paper_path"]
        theory_name = request.input_data.get("theory_name", "extracted_theory")
        
        try:
            # Extract theory using service
            theory_schema = self.theory_service.extract_theory(paper_path, theory_name)
            
            return ToolResult.success(data={
                "theory_id": theory_schema.theory_id,
                "theory_name": theory_schema.name,
                "model_type": theory_schema.model_type,
                "quality_score": theory_schema.quality_score,
                "entity_count": len(theory_schema.entity_definitions),
                "relationship_count": len(theory_schema.relationship_definitions),
                "extraction_time": theory_schema.processing_time
            })
            
        except Exception as e:
            return ToolResult.error(f"Theory extraction failed: {str(e)}")
    
    def _validate_inputs(self, input_data: dict) -> bool:
        """Validate tool inputs"""
        return (
            "paper_path" in input_data and
            Path(input_data["paper_path"]).exists()
        )

class T02TheoryApplicationTool(KGASTool):
    """T02: Apply Extracted Theory to Text"""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.theory_service = service_manager.theory_extraction_service
        self.tool_id = "T02_THEORY_APPLICATION"
        self.version = "1.0.0"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute theory application"""
        
        # Validate inputs
        if not self._validate_inputs(request.input_data):
            return ToolResult.error("Invalid inputs for theory application")
        
        theory_id = request.input_data["theory_id"]
        text = request.input_data["text"]
        domain = request.input_data.get("domain", "general")
        
        try:
            # Apply theory using service
            application_result = self.theory_service.apply_theory(theory_id, text, domain)
            
            return ToolResult.success(data={
                "theory_id": theory_id,
                "domain": domain,
                "extracted_entities": len(application_result.entities),
                "extracted_relationships": len(application_result.relationships),
                "confidence_score": application_result.confidence_score,
                "processing_time": application_result.processing_time
            })
            
        except Exception as e:
            return ToolResult.error(f"Theory application failed: {str(e)}")

class T03TheoryValidationTool(KGASTool):
    """T03: Validate Theory Extraction Quality"""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(service_manager)
        self.theory_service = service_manager.theory_extraction_service
        self.tool_id = "T03_THEORY_VALIDATION"
        self.version = "1.0.0"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute theory validation using multi-agent system"""
        
        theory_id = request.input_data["theory_id"]
        validation_criteria = request.input_data.get("criteria", "standard")
        
        try:
            # Use experimental multi-agent validation system
            validation_result = self.theory_service.validate_theory(theory_id, validation_criteria)
            
            return ToolResult.success(data={
                "theory_id": theory_id,
                "validation_score": validation_result.score,
                "passed": validation_result.score >= 90,
                "criteria_results": validation_result.criteria_results,
                "recommendations": validation_result.recommendations
            })
            
        except Exception as e:
            return ToolResult.error(f"Theory validation failed: {str(e)}")
```

## MCP Protocol Integration

### MCP Server Integration

```python
class TheoryExtractionMCPServer:
    """MCP Server for theory extraction tools"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.theory_tools = {
            "theory_extract": T01TheoryExtractionTool(service_manager),
            "theory_apply": T02TheoryApplicationTool(service_manager),
            "theory_validate": T03TheoryValidationTool(service_manager)
        }
    
    def list_tools(self) -> List[MCPTool]:
        """List available theory tools for MCP clients"""
        return [
            MCPTool(
                name="theory_extract",
                description="Extract theoretical framework from academic paper",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "paper_path": {"type": "string", "description": "Path to academic paper"},
                        "theory_name": {"type": "string", "description": "Name for extracted theory"}
                    },
                    "required": ["paper_path"]
                }
            ),
            MCPTool(
                name="theory_apply",
                description="Apply extracted theory to analyze text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "theory_id": {"type": "string", "description": "ID of extracted theory"},
                        "text": {"type": "string", "description": "Text to analyze"},
                        "domain": {"type": "string", "description": "Domain context"}
                    },
                    "required": ["theory_id", "text"]
                }
            ),
            MCPTool(
                name="theory_validate",
                description="Validate quality of extracted theory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "theory_id": {"type": "string", "description": "ID of theory to validate"},
                        "criteria": {"type": "string", "description": "Validation criteria level"}
                    },
                    "required": ["theory_id"]
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: dict) -> MCPResult:
        """Execute theory tool via MCP"""
        
        if name not in self.theory_tools:
            return MCPResult.error(f"Unknown tool: {name}")
        
        tool = self.theory_tools[name]
        request = ToolRequest(input_data=arguments)
        result = tool.execute(request)
        
        if result.status == "success":
            return MCPResult.success(result.data)
        else:
            return MCPResult.error(result.error_details)
```

## Implementation Phases

### Phase 1: Service Layer Integration (1-2 months)

**Objective**: Create basic integration between experimental system and main KGAS services

**Deliverables**:
- `TheoryExtractionService` implementation
- `ExperimentalTheorySystem` interface wrapper
- Basic data format conversion utilities
- Integration with ServiceManager
- Error handling and logging

**Success Criteria**:
- Can extract theory from paper using integrated service
- Theory metadata stored in SQLite
- Basic provenance tracking working
- No modification to experimental system required

### Phase 2: Data Store Integration (2-3 months)

**Objective**: Full integration with Neo4j and SQLite data persistence

**Deliverables**:
- `TheoryGraphManager` for Neo4j storage
- `TheoryMetadataManager` for SQLite storage
- Complete data format conversion
- Query interfaces for stored theories
- Identity service integration

**Success Criteria**:
- Theories stored as graph structures in Neo4j
- Searchable metadata in SQLite
- Can retrieve and apply stored theories
- Full provenance tracking implemented

### Phase 3: Tool Pipeline Integration (3-4 months)

**Objective**: Wrap experimental system as standard KGAS tools

**Deliverables**:
- T01, T02, T03 theory tools implementation
- Tool contract compliance
- Integration with existing tool pipeline
- Tool validation and testing

**Success Criteria**:
- Theory tools available in tool registry
- Can execute theory extraction/application via tool interface
- Tools integrate with workflow orchestration
- Multi-agent validation system accessible

### Phase 4: MCP and Cross-Modal Integration (4-5 months)

**Objective**: Complete MVP integration with external access and cross-modal analysis

**Deliverables**:
- MCP server for theory tools
- Cross-modal analysis integration
- End-to-end workflow testing
- Performance optimization
- Documentation and examples

**Success Criteria**:
- Theory tools available via MCP protocol
- External systems can access theory extraction
- Theories connect to cross-modal analysis pipeline
- Full end-to-end workflow functional

## Performance and Quality Considerations

### Performance Preservation

- **No Performance Degradation**: Integration layer must not slow down experimental system
- **Asynchronous Processing**: Long-running extractions handled asynchronously
- **Caching Strategy**: Cache frequently used theories and results
- **Resource Management**: Proper cleanup of temporary files and processes

### Quality Assurance

- **Multi-Agent Validation**: Preserve 100/100 quality standards from experimental system
- **Error Propagation**: Proper error handling and reporting from experimental system
- **Result Validation**: Validate integration layer doesn't corrupt experimental results
- **Regression Testing**: Ensure integration doesn't break experimental capabilities

### Monitoring and Observability

- **Performance Metrics**: Track extraction times, quality scores, success rates
- **Integration Health**: Monitor integration layer performance and errors
- **Usage Analytics**: Track theory extraction and application patterns
- **Quality Trends**: Monitor theory extraction quality over time

## Risk Mitigation

### Integration Risks

1. **Experimental System Breakage**: Minimize risk by not modifying experimental code
2. **Performance Degradation**: Use wrapper pattern to minimize overhead
3. **Data Format Issues**: Comprehensive testing of format conversion
4. **Dependency Conflicts**: Careful management of Python path and imports

### Mitigation Strategies

1. **Thorough Testing**: Comprehensive integration testing at each phase
2. **Rollback Plan**: Ability to disable integration and use experimental system directly
3. **Monitoring**: Real-time monitoring of integration health
4. **Documentation**: Clear documentation of integration architecture and troubleshooting

## Success Metrics

### Integration Success

- **Functional Equivalence**: Integrated system produces same results as experimental system
- **Performance Parity**: No significant performance degradation
- **Service Integration**: Proper integration with all KGAS services
- **Tool Availability**: Theory tools accessible via standard interfaces

### MVP Completion

- **End-to-End Workflow**: Complete theory extraction to application workflow
- **External Access**: Theory tools available via MCP protocol
- **Data Persistence**: Theories properly stored and retrievable
- **Quality Maintenance**: Preservation of experimental system's quality standards

This integration architecture provides a comprehensive plan for connecting the sophisticated experimental theory extraction system with the main KGAS architecture while preserving all existing capabilities and maintaining high quality standards.