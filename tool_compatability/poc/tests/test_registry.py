"""
Tests for Tool Registry
"""

import sys
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.registry import ToolRegistry
from poc.tools import TextLoader
from poc.data_types import DataType, DataSchema
from poc.base_tool import BaseTool


class DummyTextToChunks(BaseTool):
    """Dummy tool for testing: TEXT → CHUNKS"""
    
    @property
    def input_type(self) -> DataType:
        return DataType.TEXT
    
    @property
    def output_type(self) -> DataType:
        return DataType.CHUNKS
    
    @property
    def input_schema(self):
        return DataSchema.TextData
    
    @property
    def output_schema(self):
        return DataSchema.ChunksData
    
    @property
    def config_schema(self):
        from pydantic import BaseModel
        class DummyConfig(BaseModel):
            pass
        return DummyConfig
    
    def default_config(self):
        return self.config_schema()
    
    def _execute(self, input_data, **kwargs):
        # Simple chunking
        chunks = []
        text = input_data.content
        chunk_size = 100
        
        for i in range(0, len(text), chunk_size):
            chunk = DataSchema.Chunk(
                id=f"chunk_{i}",
                text=text[i:i+chunk_size],
                index=i // chunk_size,
                start_char=i,
                end_char=min(i + chunk_size, len(text))
            )
            chunks.append(chunk)
        
        return DataSchema.ChunksData(
            chunks=chunks,
            source_checksum=input_data.checksum,
            chunk_method="fixed_size",
            chunk_params={"size": chunk_size}
        )


class DummyChunksToEntities(BaseTool):
    """Dummy tool for testing: CHUNKS → ENTITIES"""
    
    @property
    def input_type(self) -> DataType:
        return DataType.CHUNKS
    
    @property
    def output_type(self) -> DataType:
        return DataType.ENTITIES
    
    @property
    def input_schema(self):
        return DataSchema.ChunksData
    
    @property
    def output_schema(self):
        return DataSchema.EntitiesData
    
    @property
    def config_schema(self):
        from pydantic import BaseModel
        class DummyConfig(BaseModel):
            pass
        return DummyConfig
    
    def default_config(self):
        return self.config_schema()
    
    def _execute(self, input_data, **kwargs):
        # Dummy entity extraction
        entities = []
        for chunk in input_data.chunks:
            # Pretend we found an entity
            entity = DataSchema.Entity(
                id=f"entity_{chunk.id}",
                text=chunk.text[:20] if len(chunk.text) > 20 else chunk.text,
                type="MISC",
                confidence=0.8
            )
            entities.append(entity)
        
        from datetime import datetime
        return DataSchema.EntitiesData(
            entities=entities,
            relationships=[],
            source_checksum=input_data.source_checksum,
            extraction_model="dummy",
            extraction_timestamp=datetime.now().isoformat()
        )


def test_registry_initialization():
    """Test registry creation"""
    registry = ToolRegistry()
    assert registry is not None
    assert len(registry.tools) == 0
    assert str(registry) == "ToolRegistry(0 tools)"


def test_tool_registration():
    """Test registering tools"""
    registry = ToolRegistry()
    
    # Register a tool
    loader = TextLoader()
    registry.register(loader)
    
    assert len(registry.tools) == 1
    assert "TextLoader" in registry.tools
    assert registry.get_tool("TextLoader") == loader


def test_tool_unregistration():
    """Test removing tools"""
    registry = ToolRegistry()
    
    loader = TextLoader()
    registry.register(loader)
    assert len(registry.tools) == 1
    
    # Unregister
    success = registry.unregister("TextLoader")
    assert success
    assert len(registry.tools) == 0
    
    # Try to unregister non-existent
    success = registry.unregister("NonExistent")
    assert not success


def test_compatibility_checking():
    """Test tool compatibility detection"""
    registry = ToolRegistry()
    
    # Register tools
    loader = TextLoader()
    chunker = DummyTextToChunks()
    extractor = DummyChunksToEntities()
    
    registry.register(loader)
    registry.register(chunker)
    registry.register(extractor)
    
    # Check connections
    assert registry.can_connect("TextLoader", "DummyTextToChunks")  # TEXT → TEXT (compatible)
    assert registry.can_connect("DummyTextToChunks", "DummyChunksToEntities")  # CHUNKS → CHUNKS
    assert not registry.can_connect("TextLoader", "DummyChunksToEntities")  # FILE output != CHUNKS input
    assert not registry.can_connect("DummyChunksToEntities", "TextLoader")  # ENTITIES != FILE


def test_chain_discovery():
    """Test finding tool chains"""
    registry = ToolRegistry()
    
    # Register tools to form a chain
    loader = TextLoader()
    chunker = DummyTextToChunks()
    extractor = DummyChunksToEntities()
    
    registry.register(loader)
    registry.register(chunker)
    registry.register(extractor)
    
    # Find chains FILE → TEXT
    chains = registry.find_chains(DataType.FILE, DataType.TEXT)
    assert len(chains) == 1
    assert chains[0] == ["TextLoader"]
    
    # Find chains FILE → CHUNKS
    chains = registry.find_chains(DataType.FILE, DataType.CHUNKS)
    assert len(chains) == 1
    assert chains[0] == ["TextLoader", "DummyTextToChunks"]
    
    # Find chains FILE → ENTITIES
    chains = registry.find_chains(DataType.FILE, DataType.ENTITIES)
    assert len(chains) == 1
    assert chains[0] == ["TextLoader", "DummyTextToChunks", "DummyChunksToEntities"]
    
    # No chain from ENTITIES → FILE
    chains = registry.find_chains(DataType.ENTITIES, DataType.FILE)
    assert len(chains) == 0


def test_shortest_chain():
    """Test finding shortest chain"""
    registry = ToolRegistry()
    
    loader = TextLoader()
    chunker = DummyTextToChunks()
    
    registry.register(loader)
    registry.register(chunker)
    
    # Shortest chain FILE → TEXT
    chain = registry.find_shortest_chain(DataType.FILE, DataType.TEXT)
    assert chain == ["TextLoader"]
    
    # Shortest chain FILE → CHUNKS
    chain = registry.find_shortest_chain(DataType.FILE, DataType.CHUNKS)
    assert chain == ["TextLoader", "DummyTextToChunks"]
    
    # No chain CHUNKS → FILE
    chain = registry.find_shortest_chain(DataType.CHUNKS, DataType.FILE)
    assert chain is None


def test_graph_building():
    """Test graph construction"""
    registry = ToolRegistry()
    
    loader = TextLoader()
    chunker = DummyTextToChunks()
    
    registry.register(loader)
    registry.register(chunker)
    
    G = registry.build_graph()
    
    assert G.number_of_nodes() == 2
    assert G.number_of_edges() == 1  # TextLoader → DummyTextToChunks
    assert G.has_edge("TextLoader", "DummyTextToChunks")


def test_statistics():
    """Test registry statistics"""
    registry = ToolRegistry()
    
    loader = TextLoader()
    chunker = DummyTextToChunks()
    
    registry.register(loader)
    registry.register(chunker)
    
    stats = registry.get_statistics()
    
    assert stats["tool_count"] == 2
    assert stats["edge_count"] == 1
    assert "TextLoader" in stats["tools"]
    assert "DummyTextToChunks" in stats["tools"]
    assert stats["tools"]["TextLoader"]["output_type"] == "text"
    assert stats["tools"]["DummyTextToChunks"]["input_type"] == "text"


def test_chain_execution():
    """Test executing a tool chain"""
    registry = ToolRegistry()
    
    # Register tool
    loader = TextLoader()
    registry.register(loader)
    
    # Create test file
    test_file = Path("/tmp/test_chain.txt")
    test_file.write_text("Test content for chain execution")
    
    try:
        # Create input
        file_data = DataSchema.FileData(
            path=str(test_file),
            size_bytes=test_file.stat().st_size,
            mime_type="text/plain"
        )
        
        # Execute single-tool chain
        result = registry.execute_chain(["TextLoader"], file_data)
        
        assert result.success
        assert result.chain == ["TextLoader"]
        assert len(result.intermediate_results) == 1
        assert result.final_output is not None
        assert isinstance(result.final_output, DataSchema.TextData)
        assert result.final_output.content == "Test content for chain execution"
        
    finally:
        if test_file.exists():
            test_file.unlink()


def test_multi_tool_chain_execution():
    """Test executing a multi-tool chain"""
    registry = ToolRegistry()
    
    # Register tools
    loader = TextLoader()
    chunker = DummyTextToChunks()
    
    registry.register(loader)
    registry.register(chunker)
    
    # Create test file
    test_file = Path("/tmp/test_multi_chain.txt")
    test_content = "A" * 250  # Long enough for multiple chunks
    test_file.write_text(test_content)
    
    try:
        # Create input
        file_data = DataSchema.FileData(
            path=str(test_file),
            size_bytes=test_file.stat().st_size,
            mime_type="text/plain"
        )
        
        # Execute chain
        result = registry.execute_chain(["TextLoader", "DummyTextToChunks"], file_data)
        
        assert result.success
        assert len(result.intermediate_results) == 2
        assert result.final_output is not None
        assert isinstance(result.final_output, DataSchema.ChunksData)
        assert len(result.final_output.chunks) == 3  # 250 chars / 100 chunk size
        
    finally:
        if test_file.exists():
            test_file.unlink()


def test_visualization():
    """Test compatibility matrix visualization"""
    registry = ToolRegistry()
    
    loader = TextLoader()
    chunker = DummyTextToChunks()
    
    registry.register(loader)
    registry.register(chunker)
    
    matrix = registry.visualize_compatibility()
    
    assert "TextLoader" in matrix
    assert "DummyTextToChunks" in matrix
    assert "✓" in matrix  # Should show compatibility


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])