"""
Integration Tests for Tool Composition POC

Tests the complete system with multiple tools working together.
"""

import sys
import pytest
from pathlib import Path
import tempfile
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.registry import ToolRegistry
from poc.tools import TextLoader, EntityExtractor, GraphBuilder
from poc.data_types import DataType, DataSchema


class TestIntegration:
    """Integration test suite"""
    
    @pytest.fixture
    def registry(self):
        """Create registry with all tools"""
        reg = ToolRegistry()
        reg.register(TextLoader())
        reg.register(EntityExtractor())
        reg.register(GraphBuilder())
        return reg
    
    @pytest.fixture
    def sample_file(self):
        """Create a sample test file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            Apple Inc. announced a partnership with Microsoft Corporation today.
            Tim Cook, CEO of Apple, met with Satya Nadella in Cupertino, California.
            The companies will collaborate on cloud computing services.
            """)
            return Path(f.name)
    
    def test_full_chain_execution(self, registry, sample_file):
        """Test FILE → TEXT → ENTITIES → GRAPH chain"""
        # Create input
        file_data = DataSchema.FileData(
            path=str(sample_file),
            size_bytes=sample_file.stat().st_size,
            mime_type="text/plain"
        )
        
        # Find chain
        chain = registry.find_shortest_chain(DataType.FILE, DataType.GRAPH)
        assert chain is not None
        assert len(chain) == 3
        assert chain == ["TextLoader", "EntityExtractor", "GraphBuilder"]
        
        # Execute chain
        result = registry.execute_chain(chain, file_data)
        
        # Verify success
        assert result.success
        assert result.final_output is not None
        assert isinstance(result.final_output, DataSchema.GraphData)
        assert result.final_output.node_count > 0
        
        # Clean up
        sample_file.unlink()
    
    def test_partial_chain_execution(self, registry, sample_file):
        """Test FILE → TEXT → ENTITIES chain"""
        # Create input
        file_data = DataSchema.FileData(
            path=str(sample_file),
            size_bytes=sample_file.stat().st_size,
            mime_type="text/plain"
        )
        
        # Find chain to entities
        chain = registry.find_shortest_chain(DataType.FILE, DataType.ENTITIES)
        assert chain is not None
        assert len(chain) == 2
        assert chain == ["TextLoader", "EntityExtractor"]
        
        # Execute chain
        result = registry.execute_chain(chain, file_data)
        
        # Verify success
        assert result.success
        assert result.final_output is not None
        assert isinstance(result.final_output, DataSchema.EntitiesData)
        assert len(result.final_output.entities) > 0
        
        # Clean up
        sample_file.unlink()
    
    def test_chain_with_large_document(self, registry):
        """Test chain with larger document"""
        # Create larger document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Generate content with many entities
            content = """
            Global Technology Summit 2025 Report
            
            Major announcements from leading technology companies:
            """
            
            companies = ["Apple", "Google", "Microsoft", "Amazon", "Meta", 
                        "Tesla", "NVIDIA", "Intel", "AMD", "Oracle"]
            locations = ["San Francisco", "Seattle", "Austin", "New York", "London"]
            people = ["Tim Cook", "Sundar Pichai", "Satya Nadella", "Andy Jassy", "Mark Zuckerberg"]
            
            for i in range(10):
                content += f"\n{companies[i % len(companies)]} announced new products. "
                content += f"CEO {people[i % len(people)]} presented in {locations[i % len(locations)]}. "
            
            f.write(content)
            doc_path = Path(f.name)
        
        # Create input
        file_data = DataSchema.FileData(
            path=str(doc_path),
            size_bytes=doc_path.stat().st_size,
            mime_type="text/plain"
        )
        
        # Execute full chain
        chain = ["TextLoader", "EntityExtractor", "GraphBuilder"]
        result = registry.execute_chain(chain, file_data)
        
        # Verify
        assert result.success
        assert result.final_output.node_count >= 3  # Should have multiple entities (mock extractor is limited)
        
        # Check memory usage
        total_memory = sum(step["memory"] for step in result.intermediate_results)
        assert total_memory < 100  # Should use less than 100MB
        
        # Clean up
        doc_path.unlink()
    
    def test_multiple_chain_discovery(self, registry):
        """Test finding multiple valid chains"""
        # Add a dummy tool that also produces TEXT from FILE
        class AlternativeLoader(TextLoader):
            @property
            def tool_id(self):
                return "AlternativeLoader"
        
        registry.register(AlternativeLoader())
        
        # Find all chains from FILE to ENTITIES
        chains = registry.find_chains(DataType.FILE, DataType.ENTITIES)
        
        # Should find multiple chains
        assert len(chains) == 2
        assert ["TextLoader", "EntityExtractor"] in chains
        assert ["AlternativeLoader", "EntityExtractor"] in chains
    
    def test_chain_execution_metrics(self, registry, sample_file):
        """Test metrics collection during chain execution"""
        # Create input
        file_data = DataSchema.FileData(
            path=str(sample_file),
            size_bytes=sample_file.stat().st_size,
            mime_type="text/plain"
        )
        
        # Execute chain
        chain = ["TextLoader", "EntityExtractor", "GraphBuilder"]
        result = registry.execute_chain(chain, file_data)
        
        # Verify metrics
        assert result.duration_seconds >= 0
        assert result.memory_used_mb >= 0
        assert len(result.intermediate_results) == 3
        
        for step in result.intermediate_results:
            assert "tool" in step
            assert "duration" in step
            assert "memory" in step
            assert step["success"] is True
        
        # Clean up
        sample_file.unlink()
    
    def test_chain_failure_handling(self, registry):
        """Test chain execution with failure"""
        # Create invalid input (non-existent file)
        file_data = DataSchema.FileData(
            path="/non/existent/file.txt",
            size_bytes=0,
            mime_type="text/plain"
        )
        
        # Execute chain
        chain = ["TextLoader", "EntityExtractor", "GraphBuilder"]
        result = registry.execute_chain(chain, file_data)
        
        # Should fail gracefully
        assert not result.success
        assert result.error is not None
        assert "not found" in result.error.lower()
    
    def test_graph_export_import(self, registry):
        """Test exporting and importing registry graph"""
        # Export graph
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            export_path = Path(f.name)
        
        registry.export_graph(str(export_path))
        
        # Load and verify
        with open(export_path) as f:
            graph_data = json.load(f)
        
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert len(graph_data["nodes"]) == 3
        assert len(graph_data["edges"]) == 2
        
        # Verify structure
        node_ids = {node["id"] for node in graph_data["nodes"]}
        assert "TextLoader" in node_ids
        assert "EntityExtractor" in node_ids
        assert "GraphBuilder" in node_ids
        
        # Clean up
        export_path.unlink()
    
    def test_registry_statistics(self, registry):
        """Test registry statistics collection"""
        stats = registry.get_statistics()
        
        assert stats["tool_count"] == 3
        assert stats["edge_count"] == 2
        assert stats["connectivity"]["weakly_connected"] is True
        assert stats["connectivity"]["components"] == 1
        
        # Verify per-tool stats
        assert "TextLoader" in stats["tools"]
        assert stats["tools"]["TextLoader"]["output_type"] == "text"
        assert stats["tools"]["EntityExtractor"]["input_type"] == "text"
        assert stats["tools"]["EntityExtractor"]["output_type"] == "entities"
    
    def test_compatibility_matrix(self, registry):
        """Test compatibility matrix generation"""
        matrix = registry.visualize_compatibility()
        
        # Should contain all tools
        assert "TextLoader" in matrix
        assert "EntityExtractor" in matrix
        assert "GraphBuilder" in matrix
        
        # Should show compatibility markers
        assert "✓" in matrix  # Has compatible connections
        assert "-" in matrix  # Has self-connections marked


class TestErrorScenarios:
    """Test error handling scenarios"""
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        registry = ToolRegistry()
        registry.register(TextLoader())
        registry.register(EntityExtractor())
        
        # Create empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            empty_file = Path(f.name)
        
        file_data = DataSchema.FileData(
            path=str(empty_file),
            size_bytes=0,
            mime_type="text/plain"
        )
        
        # Should handle empty file gracefully
        result = registry.execute_chain(["TextLoader", "EntityExtractor"], file_data)
        assert result.success
        
        # Clean up
        empty_file.unlink()
    
    def test_large_file_rejection(self):
        """Test rejection of files over size limit"""
        loader = TextLoader(config={"max_size_mb": 0.001})  # 1KB limit
        
        # Create file larger than limit
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("x" * 2000)  # 2KB of data
            large_file = Path(f.name)
        
        file_data = DataSchema.FileData(
            path=str(large_file),
            size_bytes=2000,
            mime_type="text/plain"
        )
        
        result = loader.process(file_data)
        assert not result.success
        assert "too large" in result.error.lower()
        
        # Clean up
        large_file.unlink()
    
    def test_encoding_detection(self):
        """Test automatic encoding detection"""
        loader = TextLoader()
        
        # Create file with UTF-8 content
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write("Hello 世界 🌍")
            utf8_file = Path(f.name)
        
        file_data = DataSchema.FileData(
            path=str(utf8_file),
            size_bytes=utf8_file.stat().st_size,
            mime_type="text/plain",
            encoding=None  # Don't specify encoding
        )
        
        result = loader.process(file_data)
        assert result.success
        assert "世界" in result.data.content
        assert "🌍" in result.data.content
        
        # Clean up
        utf8_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])