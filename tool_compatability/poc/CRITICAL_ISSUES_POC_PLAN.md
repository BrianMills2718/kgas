# Critical Issues POC: Methodical Implementation Plan

## Objective
Build a POC that tests and solves the 5 fundamental issues by attempting to:
1. Load a 50MB PDF
2. Extract entities with custom ontology (multi-input)
3. Build graph with specific schema requirements
4. Document exactly what breaks and how we fix it

## Phase 1: Multi-Input Support (Day 1-2)

### Problem Statement
Current system assumes `tool.process(single_input) → single_output`, but real tools need multiple inputs (text, ontology, config, etc.)

### Implementation Plan

#### 1.1 Create Enhanced Data Types
```python
# poc/data_types_v2.py
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ToolContext(BaseModel):
    """Carries both pipeline data and auxiliary inputs"""
    primary_data: Any  # The main data flowing through chain
    parameters: Dict[str, Dict[str, Any]] = {}  # Per-tool parameters
    shared_context: Dict[str, Any] = {}  # Shared across all tools
    metadata: Dict[str, Any] = {}  # Execution metadata
    
    def get_param(self, tool_id: str, param_name: str, default=None):
        """Get tool-specific parameter"""
        return self.parameters.get(tool_id, {}).get(param_name, default)
    
    def set_param(self, tool_id: str, param_name: str, value: Any):
        """Set tool-specific parameter"""
        if tool_id not in self.parameters:
            self.parameters[tool_id] = {}
        self.parameters[tool_id][param_name] = value
```

#### 1.2 Update Base Tool
```python
# poc/base_tool_v2.py
class BaseToolV2(ABC):
    def process(self, context: ToolContext) -> ToolContext:
        """Process with context carrying multiple inputs"""
        # Extract primary data
        input_data = context.primary_data
        
        # Get tool-specific parameters
        config = context.get_param(self.tool_id, "config", {})
        
        # Process
        output = self._execute(input_data, context)
        
        # Update context with output
        context.primary_data = output
        return context
    
    @abstractmethod
    def _execute(self, input_data: Any, context: ToolContext) -> Any:
        """Execute with access to full context"""
        pass
```

#### 1.3 Test Multi-Input Entity Extractor
```python
# poc/tools/entity_extractor_v2.py
class EntityExtractorV2(BaseToolV2):
    def _execute(self, text_data: TextData, context: ToolContext) -> EntitiesData:
        # Get custom ontology from context
        ontology = context.get_param(self.tool_id, "ontology")
        extraction_rules = context.get_param(self.tool_id, "rules", {})
        
        # Use ontology in extraction
        prompt = f"""
        Extract entities matching this ontology:
        {ontology}
        
        Using these rules:
        {extraction_rules}
        
        From text:
        {text_data.content}
        """
        
        # Call LLM with custom prompt
        entities = self._llm_extract(prompt)
        return entities
```

### Test Script
```python
# tests/test_multi_input.py
def test_entity_extraction_with_ontology():
    """Test multi-input entity extraction"""
    
    # Create context with multiple inputs
    context = ToolContext()
    context.primary_data = TextData(content="John Smith works at Apple Inc.")
    
    # Add custom ontology
    context.set_param("EntityExtractor", "ontology", {
        "PERSON": {"properties": ["name", "role"]},
        "COMPANY": {"properties": ["name", "industry"]}
    })
    
    # Add extraction rules
    context.set_param("EntityExtractor", "rules", {
        "confidence_threshold": 0.8,
        "include_positions": True
    })
    
    # Execute
    extractor = EntityExtractorV2()
    result = extractor.process(context)
    
    assert len(result.primary_data.entities) > 0
    print(f"✅ Multi-input extraction worked")
```

## Phase 2: Schema Versioning (Day 2-3)

### Problem Statement
Changing schemas breaks all downstream tools. Need versioning and migration.

### Implementation Plan

#### 2.1 Versioned Schemas
```python
# poc/schema_versions.py
from typing import Protocol
from abc import ABC, abstractmethod
import semantic_version

class VersionedSchema(BaseModel):
    """Base for versioned schemas"""
    _version: str = "1.0.0"
    
    @classmethod
    def version(cls) -> semantic_version.Version:
        return semantic_version.Version(cls._version)

class EntityV1(VersionedSchema):
    """Version 1: Basic entity"""
    _version = "1.0.0"
    id: str
    text: str
    type: str

class EntityV2(VersionedSchema):
    """Version 2: Added confidence"""
    _version = "2.0.0"
    id: str
    text: str
    type: str
    confidence: float = 0.5
    
class EntityV3(VersionedSchema):
    """Version 3: Added positions"""
    _version = "3.0.0"
    id: str
    text: str
    type: str
    confidence: float = 0.5
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
```

#### 2.2 Migration System
```python
# poc/migrations.py
class SchemaMigrator:
    """Handles schema migrations"""
    
    migrations = {}
    
    @classmethod
    def register_migration(cls, from_version: str, to_version: str):
        """Decorator to register migrations"""
        def decorator(func):
            cls.migrations[(from_version, to_version)] = func
            return func
        return decorator
    
    @classmethod
    def migrate(cls, data: Any, target_version: str) -> Any:
        """Migrate data to target version"""
        current_version = data._version if hasattr(data, '_version') else "1.0.0"
        
        if current_version == target_version:
            return data
        
        # Find migration path
        path = cls.find_migration_path(current_version, target_version)
        
        # Apply migrations
        for from_v, to_v in path:
            migration_func = cls.migrations[(from_v, to_v)]
            data = migration_func(data)
        
        return data

# Register migrations
@SchemaMigrator.register_migration("1.0.0", "2.0.0")
def migrate_entity_v1_to_v2(entity: EntityV1) -> EntityV2:
    return EntityV2(
        id=entity.id,
        text=entity.text,
        type=entity.type,
        confidence=0.5  # Default value
    )

@SchemaMigrator.register_migration("2.0.0", "3.0.0")
def migrate_entity_v2_to_v3(entity: EntityV2) -> EntityV3:
    return EntityV3(
        id=entity.id,
        text=entity.text,
        type=entity.type,
        confidence=entity.confidence,
        start_pos=None,
        end_pos=None
    )
```

### Test Script
```python
# tests/test_schema_versioning.py
def test_schema_migration_chain():
    """Test migrating through multiple versions"""
    
    # Start with V1 entity
    entity_v1 = EntityV1(id="1", text="Apple", type="ORG")
    
    # Migrate to V3
    entity_v3 = SchemaMigrator.migrate(entity_v1, "3.0.0")
    
    assert entity_v3._version == "3.0.0"
    assert entity_v3.confidence == 0.5  # Default from V2
    assert entity_v3.start_pos is None  # Default from V3
    print(f"✅ Schema migration chain worked")
```

## Phase 3: Memory Management (Day 3-4)

### Problem Statement
System crashes with large files (50MB+ PDFs). Need streaming and references.

### Implementation Plan

#### 3.1 Data References
```python
# poc/data_references.py
import os
import hashlib
from typing import Optional, Union

class DataReference(BaseModel):
    """Reference to data stored elsewhere"""
    storage_type: str  # "filesystem", "memory", "s3", "database"
    location: str  # Path or URI
    size_bytes: int
    checksum: str
    mime_type: Optional[str] = None
    
    def load(self, max_size: int = 10_000_000) -> bytes:
        """Load data with size limit"""
        if self.size_bytes > max_size:
            raise ValueError(f"Data too large: {self.size_bytes} > {max_size}")
        
        if self.storage_type == "filesystem":
            with open(self.location, 'rb') as f:
                return f.read()
        elif self.storage_type == "memory":
            return MEMORY_STORE[self.location]
        else:
            raise NotImplementedError(f"Storage type {self.storage_type}")
    
    def stream(self, chunk_size: int = 1024*1024):
        """Stream data in chunks"""
        if self.storage_type == "filesystem":
            with open(self.location, 'rb') as f:
                while chunk := f.read(chunk_size):
                    yield chunk

class SmartData(BaseModel):
    """Data that can be either embedded or referenced"""
    content: Optional[Union[str, bytes]] = None  # Small data
    reference: Optional[DataReference] = None  # Large data
    
    @property
    def is_embedded(self) -> bool:
        return self.content is not None
    
    @property
    def is_referenced(self) -> bool:
        return self.reference is not None
    
    def get_content(self) -> Union[str, bytes]:
        """Get content, loading from reference if needed"""
        if self.is_embedded:
            return self.content
        elif self.is_referenced:
            return self.reference.load()
        else:
            raise ValueError("No content or reference")
    
    @classmethod
    def from_data(cls, data: Union[str, bytes], threshold: int = 1_000_000):
        """Create SmartData, using reference if too large"""
        size = len(data)
        
        if size <= threshold:
            # Embed small data
            return cls(content=data)
        else:
            # Store large data and reference it
            location = f"/tmp/data_{hashlib.md5(data).hexdigest()}"
            with open(location, 'wb') as f:
                f.write(data.encode() if isinstance(data, str) else data)
            
            return cls(reference=DataReference(
                storage_type="filesystem",
                location=location,
                size_bytes=size,
                checksum=hashlib.md5(data).hexdigest()
            ))
```

#### 3.2 Streaming PDF Loader
```python
# poc/tools/pdf_loader_v2.py
import PyPDF2
from typing import Generator

class PDFLoaderV2(BaseToolV2):
    """PDF loader with streaming support"""
    
    def _execute(self, file_data: FileData, context: ToolContext) -> TextData:
        file_size = os.path.getsize(file_data.path)
        
        # Check size
        if file_size > 10_000_000:  # 10MB threshold
            # Use streaming approach
            return self._stream_process(file_data, context)
        else:
            # Load normally
            return self._batch_process(file_data, context)
    
    def _stream_process(self, file_data: FileData, context: ToolContext) -> TextData:
        """Process large PDF in chunks"""
        
        # Create reference to output
        output_file = f"/tmp/extracted_{os.path.basename(file_data.path)}.txt"
        
        with open(file_data.path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            with open(output_file, 'w') as out:
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    out.write(text)
                    
                    # Update progress in context
                    context.metadata['progress'] = f"{page_num}/{len(reader.pages)}"
        
        # Return reference, not content
        return TextData(
            content=None,
            reference=DataReference(
                storage_type="filesystem",
                location=output_file,
                size_bytes=os.path.getsize(output_file),
                checksum=self._calculate_checksum(output_file)
            )
        )
```

### Test Script
```python
# tests/test_large_pdf.py
def test_50mb_pdf_processing():
    """Test processing a 50MB PDF"""
    
    # Create a large test PDF (or use existing)
    test_pdf = "/tmp/large_test.pdf"
    create_large_pdf(test_pdf, size_mb=50)
    
    # Load with streaming
    loader = PDFLoaderV2()
    context = ToolContext()
    context.primary_data = FileData(
        path=test_pdf,
        size_bytes=os.path.getsize(test_pdf),
        mime_type="application/pdf"
    )
    
    result = loader.process(context)
    
    # Check that it used reference, not embedded
    assert result.primary_data.reference is not None
    assert result.primary_data.content is None
    print(f"✅ 50MB PDF processed via streaming")
```

## Phase 4: Semantic Compatibility (Day 4-5)

### Problem Statement
Type matching isn't enough - need semantic compatibility.

### Implementation Plan

#### 4.1 Semantic Types
```python
# poc/semantic_types.py
from typing import Dict, List, Optional

class SemanticType(BaseModel):
    """Rich type with semantic information"""
    base_type: DataType  # FILE, TEXT, ENTITIES, GRAPH
    domain: str  # "social", "knowledge", "chemical", "financial"
    schema_version: str  # Version of the schema
    required_fields: List[str] = []
    optional_fields: List[str] = []
    constraints: Dict[str, Any] = {}
    
    def is_compatible_with(self, other: 'SemanticType') -> bool:
        """Check semantic compatibility"""
        # Base type must match
        if self.base_type != other.base_type:
            return False
        
        # Domain must be compatible
        if not self._domains_compatible(self.domain, other.domain):
            return False
        
        # Required fields must be present
        for field in other.required_fields:
            if field not in self.required_fields + self.optional_fields:
                return False
        
        return True
    
    def _domains_compatible(self, domain1: str, domain2: str) -> bool:
        """Check if domains are compatible"""
        # Define compatibility rules
        compatible_domains = {
            "general": ["social", "knowledge", "financial"],  # General works with anything
            "social": ["general", "social"],
            "knowledge": ["general", "knowledge"],
            "financial": ["general", "financial"],
        }
        
        return domain2 in compatible_domains.get(domain1, [domain1])

class SemanticTool(BaseToolV2):
    """Tool with semantic type information"""
    
    @property
    @abstractmethod
    def input_semantic_type(self) -> SemanticType:
        pass
    
    @property
    @abstractmethod
    def output_semantic_type(self) -> SemanticType:
        pass
    
    def can_accept(self, data_type: SemanticType) -> bool:
        """Check if tool can accept this semantic type"""
        return data_type.is_compatible_with(self.input_semantic_type)
```

### Test Script
```python
# tests/test_semantic_compatibility.py
def test_semantic_incompatibility():
    """Test that semantic types prevent invalid connections"""
    
    # Social graph extractor
    social_extractor = SocialGraphExtractor()
    assert social_extractor.output_semantic_type.domain == "social"
    
    # Chemical analyzer expecting chemical graph
    chemical_analyzer = ChemicalAnalyzer()
    assert chemical_analyzer.input_semantic_type.domain == "chemical"
    
    # These should NOT be compatible despite both being GRAPH type
    assert not chemical_analyzer.can_accept(social_extractor.output_semantic_type)
    print(f"✅ Semantic incompatibility detected correctly")
```

## Phase 5: State Management (Day 5-6)

### Problem Statement
No transaction support - partial failures leave inconsistent state.

### Implementation Plan

#### 5.1 Transactional Execution
```python
# poc/transactions.py
from typing import List, Tuple, Any
import json

class CompensatingAction:
    """Action that can be undone"""
    
    def __init__(self, tool_id: str, action_type: str, data: Any):
        self.tool_id = tool_id
        self.action_type = action_type
        self.data = data
        self.timestamp = time.time()
    
    def compensate(self):
        """Undo this action"""
        if self.action_type == "neo4j_write":
            # Delete nodes/edges created
            self._rollback_neo4j()
        elif self.action_type == "file_write":
            # Delete file created
            os.remove(self.data['path'])
        elif self.action_type == "api_call":
            # Log that compensation needed (can't undo API calls)
            print(f"Warning: Cannot compensate API call to {self.data['endpoint']}")

class TransactionalExecutor:
    """Execute chains with transaction support"""
    
    def __init__(self):
        self.completed_actions: List[CompensatingAction] = []
        self.checkpoints: List[Any] = []
    
    def execute_with_rollback(self, chain: List[str], context: ToolContext) -> Any:
        """Execute chain with automatic rollback on failure"""
        
        try:
            for i, tool_id in enumerate(chain):
                # Checkpoint before each tool
                self.checkpoints.append(self._create_checkpoint(context))
                
                # Execute tool
                tool = registry.get_tool(tool_id)
                result = tool.process(context)
                
                # Record compensating action
                if hasattr(tool, 'get_compensating_action'):
                    action = tool.get_compensating_action(result)
                    self.completed_actions.append(action)
                
                context = result
            
            return context
            
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            print(f"🔄 Rolling back {len(self.completed_actions)} actions...")
            
            # Rollback in reverse order
            for action in reversed(self.completed_actions):
                try:
                    action.compensate()
                    print(f"  ✅ Rolled back {action.tool_id}")
                except Exception as rollback_error:
                    print(f"  ❌ Rollback failed for {action.tool_id}: {rollback_error}")
            
            # Restore last checkpoint
            if self.checkpoints:
                context = self.checkpoints[0]
            
            raise e
```

### Test Script
```python
# tests/test_transactions.py
def test_rollback_on_failure():
    """Test that partial failures trigger rollback"""
    
    # Create chain that fails partway
    chain = ["TextLoader", "EntityExtractor", "FailingGraphBuilder"]
    
    executor = TransactionalExecutor()
    context = ToolContext()
    context.primary_data = FileData(path="/tmp/test.txt")
    
    try:
        result = executor.execute_with_rollback(chain, context)
        assert False, "Should have failed"
    except:
        # Check that rollback occurred
        assert len(executor.completed_actions) == 2
        # Verify Neo4j was cleaned up
        assert count_neo4j_nodes() == 0
        print(f"✅ Rollback executed successfully")
```

## Integration Test: The Full Scenario

### Complete Test Script
```python
# tests/test_critical_issues_integrated.py

def test_complete_scenario():
    """
    Test the complete scenario with all fixes:
    1. Load 50MB PDF
    2. Extract entities with custom ontology
    3. Build graph with specific schema
    """
    
    print("="*60)
    print("CRITICAL ISSUES INTEGRATION TEST")
    print("="*60)
    
    # 1. Create large PDF
    test_pdf = "/tmp/large_test.pdf"
    create_test_pdf(test_pdf, size_mb=50)
    print(f"✅ Created 50MB test PDF")
    
    # 2. Setup context with multi-input
    context = ToolContext()
    context.primary_data = FileData(
        path=test_pdf,
        size_bytes=os.path.getsize(test_pdf),
        mime_type="application/pdf"
    )
    
    # Add custom ontology
    context.set_param("EntityExtractorV2", "ontology", {
        "PERSON": {
            "properties": ["name", "title", "organization"],
            "relationships": ["WORKS_FOR", "REPORTS_TO"]
        },
        "ORGANIZATION": {
            "properties": ["name", "industry", "size"],
            "relationships": ["SUBSIDIARY_OF", "PARTNER_WITH"]
        },
        "TECHNOLOGY": {
            "properties": ["name", "version", "type"],
            "relationships": ["DEPENDS_ON", "INTEGRATES_WITH"]
        }
    })
    
    # Add graph schema requirements
    context.set_param("GraphBuilderV2", "schema", {
        "node_id_pattern": "org_{type}_{id}",
        "required_properties": ["source", "confidence", "timestamp"],
        "index_on": ["type", "name"]
    })
    
    # 3. Execute with transaction support
    executor = TransactionalExecutor()
    chain = ["PDFLoaderV2", "EntityExtractorV2", "GraphBuilderV2"]
    
    try:
        # Execute chain
        print(f"\nExecuting chain: {' → '.join(chain)}")
        result = executor.execute_with_rollback(chain, context)
        
        # Verify results
        assert result.primary_data.reference is not None, "Should use reference for large data"
        assert result.metadata['nodes_created'] > 0, "Should create nodes"
        
        print(f"\n✅ SUCCESS: All critical issues handled")
        print(f"  - Multi-input: Custom ontology used")
        print(f"  - Memory: 50MB PDF processed via streaming")
        print(f"  - Schema: Specific requirements met")
        print(f"  - State: Transaction support active")
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILURE: {e}")
        print(f"  Completed actions rolled back: {len(executor.completed_actions)}")
        
        # Analyze what broke
        print(f"\n📊 FAILURE ANALYSIS:")
        if "memory" in str(e).lower():
            print("  - Memory management needs improvement")
        if "schema" in str(e).lower():
            print("  - Schema compatibility issue")
        if "ontology" in str(e).lower():
            print("  - Multi-input handling issue")
        
        return False

if __name__ == "__main__":
    success = test_complete_scenario()
    sys.exit(0 if success else 1)
```

## Implementation Schedule

### Day 1: Multi-Input Support
- [ ] Implement ToolContext
- [ ] Update BaseToolV2
- [ ] Create EntityExtractorV2 with ontology support
- [ ] Test multi-input extraction

### Day 2: Schema Versioning
- [ ] Implement VersionedSchema
- [ ] Create SchemaMigrator
- [ ] Write migration functions
- [ ] Test version chain migrations

### Day 3: Memory Management
- [ ] Implement DataReference
- [ ] Create SmartData
- [ ] Build PDFLoaderV2 with streaming
- [ ] Test 50MB PDF processing

### Day 4: Semantic Compatibility
- [ ] Implement SemanticType
- [ ] Create domain compatibility rules
- [ ] Update tools with semantic types
- [ ] Test incompatibility detection

### Day 5: State Management
- [ ] Implement CompensatingAction
- [ ] Build TransactionalExecutor
- [ ] Add rollback to tools
- [ ] Test failure recovery

### Day 6: Integration Testing
- [ ] Run complete scenario test
- [ ] Document what breaks
- [ ] Fix issues found
- [ ] Verify all solutions work together

## Success Criteria

✅ **Multi-Input**: EntityExtractor uses custom ontology
✅ **Schema Versioning**: Can migrate Entity from V1 to V3
✅ **Memory**: Process 50MB PDF without loading into memory
✅ **Semantic**: Detect incompatible graph types
✅ **State**: Rollback partial Neo4j writes on failure

## Evidence Collection

Each test creates evidence file:
```
evidence/current/
├── Evidence_MultiInput_Success.md
├── Evidence_SchemaVersioning_Success.md
├── Evidence_MemoryManagement_50MB.md
├── Evidence_SemanticCompatibility.md
├── Evidence_StateManagement_Rollback.md
└── Evidence_Integration_Complete.md
```

## Expected Outcomes

### What Will Break Initially
1. **Memory**: OOM error with 50MB PDF
2. **Multi-Input**: No way to pass ontology
3. **Schema**: Tools expect different Entity versions
4. **Semantic**: Wrong graph types connect
5. **State**: Partial data in Neo4j after failure

### What Will Work After Fixes
1. **Memory**: Streaming and references handle large files
2. **Multi-Input**: ToolContext carries all inputs
3. **Schema**: Automatic migration between versions
4. **Semantic**: Type system prevents invalid connections
5. **State**: Transactions ensure consistency

This methodical plan addresses all critical issues with concrete, testable solutions.