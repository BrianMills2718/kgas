"""
Data Type System for Tool Composition POC

This module defines the core data types and schemas used throughout the tool system.
Each type has an exact schema to ensure compatibility.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime


class DataType(Enum):
    """
    Core data types for the proof of concept.
    
    These are semantic types, not Python types. Each represents a meaningful
    category of data that tools can produce or consume.
    """
    FILE = "file"          # File reference with metadata
    TEXT = "text"          # Raw text content
    CHUNKS = "chunks"      # Text split into segments
    ENTITIES = "entities"  # Named entities extracted from text
    GRAPH = "graph"        # Graph structure (reference to Neo4j)
    VECTORS = "vectors"    # Embeddings/vector representations
    QUERY = "query"        # Query specification
    RESULTS = "results"    # Query or analysis results
    METRICS = "metrics"    # Performance or analysis metrics
    TABLE = "table"        # Tabular data


class DataSchema:
    """
    Exact schemas for each data type.
    
    These Pydantic models define the precise structure of data for each type.
    Tools must use these exact schemas to ensure compatibility.
    """
    
    class FileData(BaseModel):
        """Schema for FILE type"""
        path: str
        size_bytes: int
        mime_type: str
        encoding: Optional[str] = "utf-8"
        
        class Config:
            schema_extra = {
                "example": {
                    "path": "/data/document.txt",
                    "size_bytes": 1024,
                    "mime_type": "text/plain",
                    "encoding": "utf-8"
                }
            }
    
    class TextData(BaseModel):
        """Schema for TEXT type"""
        content: str
        metadata: Dict[str, Any] = Field(default_factory=dict)
        char_count: int
        checksum: str  # MD5 hash for integrity validation
        
        @classmethod
        def from_string(cls, content: str, metadata: Optional[Dict] = None):
            """Convenience constructor"""
            return cls(
                content=content,
                metadata=metadata or {},
                char_count=len(content),
                checksum=hashlib.md5(content.encode()).hexdigest()
            )
        
        def truncated_preview(self, max_chars: int = 100) -> str:
            """Get truncated preview of content"""
            if len(self.content) <= max_chars:
                return self.content
            return self.content[:max_chars] + "..."
    
    class Chunk(BaseModel):
        """Individual chunk within CHUNKS type"""
        id: str
        text: str
        index: int  # Position in sequence
        start_char: int  # Start position in original text
        end_char: int    # End position in original text
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class ChunksData(BaseModel):
        """Schema for CHUNKS type"""
        chunks: List[Chunk]
        source_checksum: str  # Links back to source text
        chunk_method: str  # "sliding_window", "sentence", etc.
        chunk_params: Dict[str, Any]  # chunk_size, overlap, etc.
        
        def total_chars(self) -> int:
            """Total characters across all chunks"""
            return sum(len(chunk.text) for chunk in self.chunks)
    
    class Entity(BaseModel):
        """Individual entity within ENTITIES type"""
        id: str
        text: str
        type: str  # PERSON, ORG, LOCATION, PRODUCT, etc.
        confidence: float = Field(ge=0.0, le=1.0)
        start_pos: Optional[int] = None
        end_pos: Optional[int] = None
        metadata: Dict[str, Any] = Field(default_factory=dict)
        
        def __hash__(self):
            """Make entity hashable for deduplication"""
            return hash((self.text, self.type))
    
    class Relationship(BaseModel):
        """Relationship between entities"""
        source_id: str
        target_id: str
        relation_type: str  # WORKS_FOR, LOCATED_IN, etc.
        confidence: float = Field(ge=0.0, le=1.0)
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class EntitiesData(BaseModel):
        """Schema for ENTITIES type"""
        entities: List[Entity]
        relationships: List[Relationship] = Field(default_factory=list)
        source_checksum: str  # Links back to source text
        extraction_model: str  # Model used for extraction
        extraction_timestamp: str
        
        def entity_count_by_type(self) -> Dict[str, int]:
            """Count entities by type"""
            counts = {}
            for entity in self.entities:
                counts[entity.type] = counts.get(entity.type, 0) + 1
            return counts
    
    class GraphData(BaseModel):
        """Schema for GRAPH type"""
        graph_id: str  # Reference to graph in Neo4j
        node_count: int
        edge_count: int
        source_checksum: str  # Traces back to original text
        created_timestamp: str
        metadata: Dict[str, Any] = Field(default_factory=dict)
        
        def is_empty(self) -> bool:
            """Check if graph is empty"""
            return self.node_count == 0 and self.edge_count == 0
    
    class VectorData(BaseModel):
        """Schema for VECTORS type"""
        vectors: List[List[float]]  # List of vector embeddings
        dimensions: int
        source_ids: List[str]  # IDs of source chunks/entities
        model: str  # Model used for embedding
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class QueryData(BaseModel):
        """Schema for QUERY type"""
        query_text: str
        query_type: str  # "similarity", "graph_traversal", "aggregation"
        parameters: Dict[str, Any] = Field(default_factory=dict)
        limit: Optional[int] = 10
        
    class ResultsData(BaseModel):
        """Schema for RESULTS type"""
        query: QueryData
        results: List[Dict[str, Any]]
        count: int
        execution_time_ms: float
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class MetricsData(BaseModel):
        """Schema for METRICS type"""
        metric_type: str  # "performance", "quality", "analysis"
        values: Dict[str, Any]
        timestamp: str
        source: str  # Tool that generated metrics
        metadata: Dict[str, Any] = Field(default_factory=dict)


# Type compatibility rules
TYPE_COMPATIBILITY = {
    # Direct compatibility (same type always compatible)
    (DataType.TEXT, DataType.TEXT): True,
    (DataType.FILE, DataType.FILE): True,
    (DataType.CHUNKS, DataType.CHUNKS): True,
    (DataType.ENTITIES, DataType.ENTITIES): True,
    (DataType.GRAPH, DataType.GRAPH): True,
    (DataType.VECTORS, DataType.VECTORS): True,
    (DataType.QUERY, DataType.QUERY): True,
    (DataType.RESULTS, DataType.RESULTS): True,
    (DataType.METRICS, DataType.METRICS): True,
    
    # Special compatibility rules
    (DataType.CHUNKS, DataType.TEXT): True,  # Chunks can be treated as text
    (DataType.RESULTS, DataType.TEXT): True,  # Results can be formatted as text
}


def are_types_compatible(output_type: DataType, input_type: DataType) -> bool:
    """
    Check if two data types are compatible.
    
    Args:
        output_type: The type being produced
        input_type: The type being consumed
        
    Returns:
        True if the types are compatible
    """
    return TYPE_COMPATIBILITY.get((output_type, input_type), False)