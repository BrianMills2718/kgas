"""
Mock implementations of T03, T15A, and T23C for POC testing.

These are simplified versions that demonstrate the field name mismatch problem.
"""

import json
from typing import Dict, Any, List


class MockT03TextLoader:
    """Mock T03 Text Loader - loads text from files."""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load text from file.
        
        Expects: {"file_path": str}
        Returns: {"content": str, "metadata": dict}  # Note: outputs "content"
        """
        file_path = params.get("file_path")
        
        if not file_path:
            raise ValueError("file_path is required")
        
        # Mock file loading
        if file_path.endswith(".txt"):
            mock_content = f"This is mock content from {file_path}. It contains information about artificial intelligence and machine learning."
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
        
        return {
            "content": mock_content,  # T03 outputs "content"
            "metadata": {
                "file_path": file_path,
                "size": len(mock_content)
            }
        }


class MockT15ATextChunker:
    """Mock T15A Text Chunker - splits text into chunks."""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chunk text into segments.
        
        Expects: {"text": str}  # Note: expects "text" not "content"
        Returns: {"chunks": List[Dict], "num_chunks": int}
        """
        text = params.get("text")  # T15A expects "text"
        
        if not text:
            raise ValueError("text is required")
        
        # Mock chunking - split by sentences
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        
        chunks = []
        for i, sentence in enumerate(sentences):
            chunks.append({
                "id": f"chunk_{i}",
                "text": sentence + ".",
                "position": i
            })
        
        return {
            "chunks": chunks,
            "num_chunks": len(chunks)
        }


class MockT23CEntityExtractor:
    """Mock T23C Entity Extractor - extracts named entities."""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract named entities from text.
        
        Expects: {"text": str} or {"chunks": List[Dict]}  # Can accept either
        Returns: {"entities": List[Dict], "relationships": List[Dict]}
        """
        # T23C can work with either text or chunks
        text = params.get("text", "")
        chunks = params.get("chunks", [])
        
        if not text and not chunks:
            raise ValueError("Either text or chunks is required")
        
        # If chunks provided, concatenate them
        if chunks and not text:
            text = " ".join([c.get("text", "") for c in chunks])
        
        # Mock entity extraction
        mock_entities = []
        
        if "artificial intelligence" in text.lower():
            mock_entities.append({
                "text": "artificial intelligence",
                "type": "CONCEPT",
                "confidence": 0.95
            })
        
        if "machine learning" in text.lower():
            mock_entities.append({
                "text": "machine learning",
                "type": "CONCEPT",
                "confidence": 0.92
            })
        
        # Mock relationships
        mock_relationships = []
        if len(mock_entities) >= 2:
            mock_relationships.append({
                "source": mock_entities[0]["text"],
                "target": mock_entities[1]["text"],
                "type": "RELATED_TO"
            })
        
        return {
            "entities": mock_entities,
            "relationships": mock_relationships,
            "num_entities": len(mock_entities)
        }


class MockT68PageRank:
    """Mock T68 PageRank - requires graph structure."""
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate PageRank scores.
        
        Expects: {"graph": Dict} with nodes and edges
        Returns: {"scores": Dict[str, float]}
        """
        graph = params.get("graph")
        
        if not graph:
            raise ValueError("graph is required")
        
        # This tool expects a graph structure, not text or entities
        if "nodes" not in graph or "edges" not in graph:
            raise ValueError("graph must contain nodes and edges")
        
        # Mock PageRank calculation
        scores = {}
        for node in graph.get("nodes", []):
            scores[node.get("id", "")] = 0.5  # Mock score
        
        return {
            "scores": scores,
            "num_nodes": len(scores)
        }