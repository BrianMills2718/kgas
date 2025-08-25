# Type-Based Tool Composition: Proof of Concept Plan

## Executive Summary

This proof of concept will validate that type-based tool composition can work in practice by implementing a minimal but complete system with 3 real tools, demonstrating automatic chain discovery, handling edge cases, and measuring actual performance.

## Critical Unknowns We Must Validate

### 1. Memory Boundaries
**Unknown**: At what data size do we hit memory issues with direct passing?
**Test**: Process increasingly large documents until failure
**Success Criteria**: Handle at least 10MB documents in memory

### 2. Schema Evolution  
**Unknown**: What happens when we need to change an Entity schema after tools are deployed?
**Test**: Simulate schema migration mid-pipeline
**Success Criteria**: Strategy for backwards compatibility

### 3. Error Recovery
**Unknown**: How do we handle partial failures without transactions?
**Test**: Force failures at each pipeline stage
**Success Criteria**: Clean recovery or rollback strategy

### 4. Performance Reality
**Unknown**: Actual overhead of type checking, validation, and data passing
**Test**: Benchmark identical pipeline with and without framework
**Success Criteria**: Less than 20% overhead

### 5. Pipeline Branching
**Unknown**: Can one tool output feed multiple downstream tools?
**Test**: TEXT → [EntityExtractor, SentimentAnalyzer] → Merge
**Success Criteria**: Clean branching and merging pattern

## Proof of Concept Scope

### Tools to Implement (Minimum Viable Set)
1. **TextLoader**: FILE → TEXT
2. **EntityExtractor**: TEXT → ENTITIES  
3. **GraphBuilder**: ENTITIES → GRAPH

### Why These Three
- Covers file I/O, LLM integration, and database storage
- Represents the core KGAS pipeline
- Tests all major boundaries (file system, API, database)

## Implementation Plan

### Phase 1: Core Framework (Day 1-2)

#### 1.1 Data Type System
```python
# poc/data_types.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import hashlib

class DataType(Enum):
    """Core data types for proof of concept"""
    FILE = "file"
    TEXT = "text"
    ENTITIES = "entities"
    GRAPH = "graph"

class DataSchema:
    """Exact schemas for each type"""
    
    class FileData(BaseModel):
        path: str
        size_bytes: int
        mime_type: str
        
    class TextData(BaseModel):
        content: str
        metadata: Dict[str, Any] = {}
        char_count: int
        checksum: str  # For integrity validation
        
        @classmethod
        def from_string(cls, content: str, metadata: Dict = None):
            return cls(
                content=content,
                metadata=metadata or {},
                char_count=len(content),
                checksum=hashlib.md5(content.encode()).hexdigest()
            )
    
    class Entity(BaseModel):
        id: str
        text: str
        type: str  # PERSON, ORG, LOCATION
        confidence: float = Field(ge=0.0, le=1.0)
        start_pos: Optional[int] = None
        end_pos: Optional[int] = None
        
    class EntitiesData(BaseModel):
        entities: List[Entity]
        source_checksum: str  # Links back to source text
        extraction_model: str
        extraction_timestamp: str
        
    class GraphData(BaseModel):
        graph_id: str  # Neo4j reference
        node_count: int
        edge_count: int
        source_checksum: str  # Traces back to original
```

#### 1.2 Tool Base Class
```python
# poc/base_tool.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, ValidationError
import time
import traceback
import psutil
import logging

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)
ConfigT = TypeVar('ConfigT', bound=BaseModel)

class ToolMetrics(BaseModel):
    """Performance metrics for tool execution"""
    start_time: float
    end_time: float
    duration_seconds: float
    memory_before_mb: float
    memory_after_mb: float
    memory_used_mb: float
    success: bool
    error: Optional[str] = None
    
class ToolResult(BaseModel, Generic[OutputT]):
    """Wrapper for tool output with metadata"""
    data: Optional[OutputT]
    metrics: ToolMetrics
    success: bool
    error: Optional[str] = None
    
class BaseTool(ABC, Generic[InputT, OutputT, ConfigT]):
    """Base class for all tools"""
    
    def __init__(self, config: Optional[ConfigT] = None):
        self.config = config or self.default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @property
    @abstractmethod
    def input_type(self) -> DataType:
        pass
        
    @property
    @abstractmethod
    def output_type(self) -> DataType:
        pass
        
    @property
    @abstractmethod
    def input_schema(self) -> type[InputT]:
        pass
        
    @property
    @abstractmethod
    def output_schema(self) -> type[OutputT]:
        pass
        
    @abstractmethod
    def default_config(self) -> ConfigT:
        pass
        
    @abstractmethod
    def _execute(self, input_data: InputT) -> OutputT:
        """Core execution logic - implement this"""
        pass
        
    def validate_input(self, data: Any) -> InputT:
        """Validate and parse input data"""
        try:
            if isinstance(data, dict):
                return self.input_schema(**data)
            elif isinstance(data, self.input_schema):
                return data
            else:
                raise ValueError(f"Invalid input type: {type(data)}")
        except ValidationError as e:
            raise ValueError(f"Input validation failed: {e}")
            
    def process(self, input_data: Any) -> ToolResult[OutputT]:
        """Main entry point with full error handling and metrics"""
        process = psutil.Process()
        start_time = time.time()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        try:
            # Validate input
            validated_input = self.validate_input(input_data)
            
            # Execute tool
            output = self._execute(validated_input)
            
            # Validate output
            if not isinstance(output, self.output_schema):
                raise ValueError(f"Output validation failed: expected {self.output_schema}")
            
            # Collect metrics
            end_time = time.time()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            metrics = ToolMetrics(
                start_time=start_time,
                end_time=end_time,
                duration_seconds=end_time - start_time,
                memory_before_mb=memory_before,
                memory_after_mb=memory_after,
                memory_used_mb=memory_after - memory_before,
                success=True
            )
            
            return ToolResult(
                data=output,
                metrics=metrics,
                success=True
            )
            
        except Exception as e:
            end_time = time.time()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            self.logger.error(f"Tool execution failed: {e}\n{traceback.format_exc()}")
            
            metrics = ToolMetrics(
                start_time=start_time,
                end_time=end_time,
                duration_seconds=end_time - start_time,
                memory_before_mb=memory_before,
                memory_after_mb=memory_after,
                memory_used_mb=memory_after - memory_before,
                success=False,
                error=str(e)
            )
            
            return ToolResult(
                data=None,
                metrics=metrics,
                success=False,
                error=str(e)
            )
```

#### 1.3 Tool Registry and Compatibility
```python
# poc/registry.py
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import networkx as nx

class ToolRegistry:
    """Registry for tools with automatic chain discovery"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.compatibility_cache: Dict[Tuple[str, str], bool] = {}
        
    def register(self, tool: BaseTool) -> None:
        """Register a tool"""
        tool_id = tool.__class__.__name__
        self.tools[tool_id] = tool
        self.logger.info(f"Registered {tool_id}: {tool.input_type} → {tool.output_type}")
        
    def can_connect(self, tool1_id: str, tool2_id: str) -> bool:
        """Check if tool1 output can feed tool2 input"""
        cache_key = (tool1_id, tool2_id)
        
        if cache_key in self.compatibility_cache:
            return self.compatibility_cache[cache_key]
            
        tool1 = self.tools.get(tool1_id)
        tool2 = self.tools.get(tool2_id)
        
        if not tool1 or not tool2:
            self.compatibility_cache[cache_key] = False
            return False
            
        # Type compatibility
        type_compatible = tool1.output_type == tool2.input_type
        
        # Schema compatibility (deeper check)
        if type_compatible:
            try:
                # Try to create tool2 input from tool1 output schema
                sample_output = self._create_sample(tool1.output_schema)
                tool2.validate_input(sample_output.dict())
                schema_compatible = True
            except:
                schema_compatible = False
        else:
            schema_compatible = False
            
        result = type_compatible and schema_compatible
        self.compatibility_cache[cache_key] = result
        return result
        
    def find_chains(self, start_type: DataType, end_type: DataType, 
                   max_length: int = 5) -> List[List[str]]:
        """Find all valid tool chains from start to end type"""
        # Build directed graph
        G = nx.DiGraph()
        
        for tool_id, tool in self.tools.items():
            G.add_node(tool_id, input_type=tool.input_type, output_type=tool.output_type)
            
        for t1_id in self.tools:
            for t2_id in self.tools:
                if self.can_connect(t1_id, t2_id):
                    G.add_edge(t1_id, t2_id)
                    
        # Find tools that start with start_type
        start_tools = [tid for tid, tool in self.tools.items() 
                      if tool.input_type == start_type]
        
        # Find tools that end with end_type
        end_tools = [tid for tid, tool in self.tools.items() 
                    if tool.output_type == end_type]
        
        # Find all paths
        all_chains = []
        for start in start_tools:
            for end in end_tools:
                try:
                    paths = list(nx.all_simple_paths(G, start, end, cutoff=max_length))
                    all_chains.extend(paths)
                except nx.NetworkXNoPath:
                    continue
                    
        return all_chains
        
    def visualize_compatibility(self) -> str:
        """Generate compatibility matrix visualization"""
        tools = sorted(self.tools.keys())
        
        # Header
        lines = ["Compatibility Matrix"]
        lines.append("-" * 50)
        
        # Matrix
        header = "FROM \\ TO | " + " | ".join(t[:8] for t in tools)
        lines.append(header)
        lines.append("-" * len(header))
        
        for t1 in tools:
            row = f"{t1[:10]:10} | "
            for t2 in tools:
                if self.can_connect(t1, t2):
                    row += "   ✓    | "
                else:
                    row += "        | "
            lines.append(row)
            
        return "\n".join(lines)
```

### Phase 2: Implement Three Tools (Day 3-4)

#### 2.1 TextLoader Tool
```python
# poc/tools/text_loader.py
from pathlib import Path
from typing import Optional
import magic  # python-magic for mime type detection

class TextLoaderConfig(BaseModel):
    max_size_mb: float = 10.0
    encoding: str = "utf-8"
    
class TextLoader(BaseTool[DataSchema.FileData, DataSchema.TextData, TextLoaderConfig]):
    
    @property
    def input_type(self) -> DataType:
        return DataType.FILE
        
    @property
    def output_type(self) -> DataType:
        return DataType.TEXT
        
    @property
    def input_schema(self):
        return DataSchema.FileData
        
    @property
    def output_schema(self):
        return DataSchema.TextData
        
    def default_config(self) -> TextLoaderConfig:
        return TextLoaderConfig()
        
    def _execute(self, input_data: DataSchema.FileData) -> DataSchema.TextData:
        path = Path(input_data.path)
        
        # Size check
        size_mb = input_data.size_bytes / 1024 / 1024
        if size_mb > self.config.max_size_mb:
            raise ValueError(f"File too large: {size_mb:.1f}MB > {self.config.max_size_mb}MB")
            
        # Read file
        with open(path, 'r', encoding=self.config.encoding) as f:
            content = f.read()
            
        return DataSchema.TextData.from_string(
            content=content,
            metadata={
                "source_file": str(path),
                "mime_type": input_data.mime_type
            }
        )
```

#### 2.2 EntityExtractor Tool
```python
# poc/tools/entity_extractor.py
import os
import litellm
from datetime import datetime

class EntityExtractorConfig(BaseModel):
    model: str = "gemini/gemini-2.0-flash-exp"
    confidence_threshold: float = 0.7
    
class EntityExtractor(BaseTool[DataSchema.TextData, DataSchema.EntitiesData, EntityExtractorConfig]):
    
    @property
    def input_type(self) -> DataType:
        return DataType.TEXT
        
    @property
    def output_type(self) -> DataType:
        return DataType.ENTITIES
        
    def _execute(self, input_data: DataSchema.TextData) -> DataSchema.EntitiesData:
        # Call LLM
        prompt = f"""Extract all named entities from this text.
        Return JSON: {{"entities": [{{"text": "...", "type": "PERSON|ORG|LOCATION", "confidence": 0.9}}]}}
        
        Text: {input_data.content[:2000]}"""  # Limit for POC
        
        response = litellm.completion(
            model=self.config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        # Parse response (simplified for POC)
        import json
        result = json.loads(response.choices[0].message.content)
        
        entities = []
        for i, ent in enumerate(result["entities"]):
            if ent.get("confidence", 1.0) >= self.config.confidence_threshold:
                entities.append(DataSchema.Entity(
                    id=f"e_{i}",
                    text=ent["text"],
                    type=ent["type"],
                    confidence=ent.get("confidence", 0.9)
                ))
                
        return DataSchema.EntitiesData(
            entities=entities,
            source_checksum=input_data.checksum,
            extraction_model=self.config.model,
            extraction_timestamp=datetime.now().isoformat()
        )
```

#### 2.3 GraphBuilder Tool
```python
# poc/tools/graph_builder.py
from neo4j import GraphDatabase
import uuid

class GraphBuilderConfig(BaseModel):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "devpassword"
    
class GraphBuilder(BaseTool[DataSchema.EntitiesData, DataSchema.GraphData, GraphBuilderConfig]):
    
    def __init__(self, config: Optional[GraphBuilderConfig] = None):
        super().__init__(config)
        self.driver = GraphDatabase.driver(
            self.config.neo4j_uri,
            auth=(self.config.neo4j_user, self.config.neo4j_password)
        )
        
    @property
    def input_type(self) -> DataType:
        return DataType.ENTITIES
        
    @property
    def output_type(self) -> DataType:
        return DataType.GRAPH
        
    def _execute(self, input_data: DataSchema.EntitiesData) -> DataSchema.GraphData:
        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        
        with self.driver.session() as session:
            # Create nodes
            for entity in input_data.entities:
                session.run("""
                    CREATE (e:Entity {
                        id: $id,
                        text: $text,
                        type: $type,
                        confidence: $confidence,
                        graph_id: $graph_id
                    })
                """, id=entity.id, text=entity.text, type=entity.type,
                     confidence=entity.confidence, graph_id=graph_id)
                     
        return DataSchema.GraphData(
            graph_id=graph_id,
            node_count=len(input_data.entities),
            edge_count=0,  # No edges in POC
            source_checksum=input_data.source_checksum
        )
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.close()
```

### Phase 3: Edge Cases and Testing (Day 5-6)

#### 3.1 Memory Stress Test
```python
# poc/tests/test_memory.py
def test_memory_limits():
    """Find the breaking point for direct data passing"""
    sizes_mb = [1, 5, 10, 20, 50, 100]
    
    for size_mb in sizes_mb:
        # Generate text of specific size
        text = "x" * (size_mb * 1024 * 1024)
        
        try:
            # Create pipeline
            loader = TextLoader()
            extractor = EntityExtractor()
            
            # Process
            text_data = DataSchema.TextData.from_string(text)
            result = extractor.process(text_data)
            
            print(f"✓ {size_mb}MB processed successfully")
            print(f"  Memory used: {result.metrics.memory_used_mb:.1f}MB")
            
        except MemoryError:
            print(f"✗ Failed at {size_mb}MB - memory limit reached")
            break
        except Exception as e:
            print(f"✗ Failed at {size_mb}MB - {e}")
```

#### 3.2 Pipeline Failure Recovery
```python
# poc/tests/test_recovery.py
class PipelineExecutor:
    """Executor with checkpointing and recovery"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.checkpoints: Dict[str, Any] = {}
        
    def execute_with_recovery(self, chain: List[str], input_data: Any) -> Any:
        """Execute chain with checkpointing"""
        
        for i, tool_id in enumerate(chain):
            checkpoint_key = f"{chain}_{i}"
            
            # Check if we have a checkpoint
            if checkpoint_key in self.checkpoints:
                print(f"Resuming from checkpoint: {checkpoint_key}")
                current_data = self.checkpoints[checkpoint_key]
            else:
                # Execute tool
                tool = self.registry.tools[tool_id]
                result = tool.process(current_data if i > 0 else input_data)
                
                if not result.success:
                    print(f"Failed at {tool_id}: {result.error}")
                    # Save checkpoint of last successful step
                    if i > 0:
                        self.checkpoints[f"{chain}_{i-1}"] = current_data
                    raise Exception(f"Pipeline failed at {tool_id}")
                    
                current_data = result.data
                # Save checkpoint
                self.checkpoints[checkpoint_key] = current_data
                
        return current_data
```

#### 3.3 Schema Evolution Test
```python
# poc/tests/test_schema_evolution.py
def test_schema_migration():
    """Test handling schema changes"""
    
    # V1 Schema
    class EntityV1(BaseModel):
        text: str
        type: str
        
    # V2 Schema (adds confidence)
    class EntityV2(BaseModel):
        text: str
        type: str
        confidence: float = 0.9  # Default for migration
        
    # Migration function
    def migrate_entity(v1: EntityV1) -> EntityV2:
        return EntityV2(
            text=v1.text,
            type=v1.type,
            confidence=0.9  # Default value
        )
        
    # Test migration
    old_entity = EntityV1(text="Microsoft", type="ORG")
    new_entity = migrate_entity(old_entity)
    assert new_entity.confidence == 0.9
```

### Phase 4: Performance Benchmarking (Day 7)

#### 4.1 Benchmark Suite
```python
# poc/benchmark.py
import time
from typing import List, Dict

class Benchmark:
    """Compare performance with and without framework"""
    
    def run_with_framework(self, text: str) -> Dict:
        """Run using our framework"""
        start = time.time()
        
        # Using framework
        registry = ToolRegistry()
        loader = TextLoader()
        extractor = EntityExtractor()
        builder = GraphBuilder()
        
        registry.register(loader)
        registry.register(extractor)
        registry.register(builder)
        
        # Execute chain
        text_data = DataSchema.TextData.from_string(text)
        entities_result = extractor.process(text_data)
        graph_result = builder.process(entities_result.data)
        
        return {
            "duration": time.time() - start,
            "success": graph_result.success,
            "memory_used": sum([
                entities_result.metrics.memory_used_mb,
                graph_result.metrics.memory_used_mb
            ])
        }
        
    def run_direct(self, text: str) -> Dict:
        """Run without framework (direct calls)"""
        start = time.time()
        
        # Direct implementation
        # ... (simplified direct calls)
        
        return {"duration": time.time() - start}
        
    def compare(self, test_texts: List[str]):
        """Compare framework vs direct"""
        framework_times = []
        direct_times = []
        
        for text in test_texts:
            fw_result = self.run_with_framework(text)
            direct_result = self.run_direct(text)
            
            framework_times.append(fw_result["duration"])
            direct_times.append(direct_result["duration"])
            
        avg_framework = sum(framework_times) / len(framework_times)
        avg_direct = sum(direct_times) / len(direct_times)
        overhead = (avg_framework - avg_direct) / avg_direct * 100
        
        print(f"Average framework time: {avg_framework:.2f}s")
        print(f"Average direct time: {avg_direct:.2f}s")
        print(f"Overhead: {overhead:.1f}%")
```

### Phase 5: Integration and Demo (Day 8)

#### 5.1 Main Demo Script
```python
# poc/demo.py
#!/usr/bin/env python3
"""
Proof of Concept Demo
Demonstrates type-based tool composition with automatic chain discovery
"""

import logging
from pathlib import Path

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize registry
    registry = ToolRegistry()
    
    # Register tools
    registry.register(TextLoader())
    registry.register(EntityExtractor())
    registry.register(GraphBuilder())
    
    # Show compatibility matrix
    print("\n" + "="*60)
    print("COMPATIBILITY MATRIX")
    print("="*60)
    print(registry.visualize_compatibility())
    
    # Find possible chains
    print("\n" + "="*60)
    print("DISCOVERED CHAINS: FILE → GRAPH")
    print("="*60)
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    for i, chain in enumerate(chains, 1):
        print(f"{i}. {' → '.join(chain)}")
        
    # Execute a chain
    print("\n" + "="*60)
    print("EXECUTING CHAIN")
    print("="*60)
    
    # Prepare input
    test_file = Path("test_data/sample.txt")
    test_file.write_text("Microsoft Corporation is led by CEO Satya Nadella.")
    
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=test_file.stat().st_size,
        mime_type="text/plain"
    )
    
    # Execute
    executor = PipelineExecutor(registry)
    chain = ["TextLoader", "EntityExtractor", "GraphBuilder"]
    
    try:
        result = executor.execute_with_recovery(chain, file_data)
        print(f"✓ Success! Created graph: {result.graph_id}")
        print(f"  Nodes: {result.node_count}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        
    # Show performance metrics
    print("\n" + "="*60)
    print("PERFORMANCE METRICS")
    print("="*60)
    # ... display collected metrics

if __name__ == "__main__":
    main()
```

## Success Criteria

### Must Have (Core Validation)
- [ ] Three tools working with type-based composition
- [ ] Automatic chain discovery functioning
- [ ] Less than 20% performance overhead
- [ ] Clean error handling with recovery

### Should Have (Practical Concerns)
- [ ] Handle 10MB documents without memory issues
- [ ] Schema migration strategy demonstrated
- [ ] Pipeline branching pattern shown
- [ ] Debugging/observability tools

### Nice to Have (Future Proofing)
- [ ] Async tool support pattern
- [ ] Resource pooling for Neo4j connections
- [ ] Metrics aggregation system
- [ ] LLM-friendly tool descriptions

## Risk Mitigation

### Risk 1: Memory Explosion
**Mitigation**: Implement streaming for large data:
```python
class StreamingTextData(BaseModel):
    chunk_iterator: Iterator[str]  # Instead of full content
    metadata: Dict[str, Any]
```

### Risk 2: Neo4j Connection Pool Exhaustion
**Mitigation**: Singleton connection manager:
```python
class ConnectionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.driver = GraphDatabase.driver(...)
        return cls._instance
```

### Risk 3: Type Proliferation
**Mitigation**: Strict type approval process:
- New types require justification
- Try to use existing types first
- Document why new type is needed

## Timeline

**Day 1-2**: Core framework (base classes, registry)
**Day 3-4**: Three tools implementation
**Day 5-6**: Edge cases and testing
**Day 7**: Performance benchmarking
**Day 8**: Integration and demo

## Deliverables

1. **Working Code**: `/tool_compatability/poc/` directory
2. **Test Results**: Memory limits, performance metrics
3. **Documentation**: How to add new tools
4. **Decision Doc**: Go/no-go for full implementation

## Next Steps After POC

If successful:
1. Migrate remaining high-value tools (week 1)
2. Build production registry system (week 2)
3. Create tool development guide (week 3)
4. Deprecate old tool system (week 4)

If unsuccessful:
1. Document specific failures
2. Consider hybrid approach
3. Revisit hardcoded chains option

---

This POC will give us concrete answers about feasibility, not theoretical possibilities.