"""
Semantic Type Registry for ORM Proof of Concept

Defines semantic types and compatibility rules for tool composition.
"""

from enum import Enum
from typing import Dict, Tuple, Set


class SemanticType(Enum):
    """Semantic types for data flowing between tools."""
    
    # Input types
    FILE_REFERENCE = "file_reference"      # Path to file
    URL = "url"                           # Web URL
    
    # Text types
    TEXT_CONTENT = "text_content"          # Raw text document
    TEXT_SEGMENTS = "text_segments"        # Chunked text pieces
    
    # Entity types
    NAMED_ENTITIES = "named_entities"      # Extracted entities with types
    ENTITY_RELATIONSHIPS = "entity_relationships"  # Relations between entities
    
    # Graph types
    GRAPH_STRUCTURE = "graph_structure"    # Complete graph with nodes and edges
    GRAPH_NODES = "graph_nodes"           # Collection of nodes
    GRAPH_EDGES = "graph_edges"           # Collection of edges
    
    # Vector types
    VECTOR_EMBEDDINGS = "vector_embeddings"  # Semantic vectors
    
    # Query types
    QUERY_SPEC = "query_spec"             # Query specification
    QUERY_RESULTS = "query_results"       # Query output
    
    # Analysis types
    NODE_SCORES = "node_scores"           # PageRank or similar scores
    CENTRALITIES = "centralities"         # Centrality measures


class SemanticTypeRegistry:
    """Registry for semantic type compatibility rules."""
    
    # Define which types are compatible (can be connected)
    COMPATIBILITY_RULES: Dict[Tuple[SemanticType, SemanticType], bool] = {
        # Exact matches are always compatible
        (SemanticType.TEXT_CONTENT, SemanticType.TEXT_CONTENT): True,
        (SemanticType.TEXT_SEGMENTS, SemanticType.TEXT_SEGMENTS): True,
        (SemanticType.NAMED_ENTITIES, SemanticType.NAMED_ENTITIES): True,
        
        # Text segments can be treated as text content
        (SemanticType.TEXT_SEGMENTS, SemanticType.TEXT_CONTENT): True,
        
        # File reference can't directly connect to anything except loaders
        (SemanticType.FILE_REFERENCE, SemanticType.TEXT_CONTENT): False,
        (SemanticType.FILE_REFERENCE, SemanticType.NAMED_ENTITIES): False,
        
        # Graph structure incompatible with text
        (SemanticType.TEXT_CONTENT, SemanticType.GRAPH_STRUCTURE): False,
        (SemanticType.GRAPH_STRUCTURE, SemanticType.TEXT_CONTENT): False,
        
        # Entities can feed into graph construction (implicitly)
        (SemanticType.NAMED_ENTITIES, SemanticType.GRAPH_NODES): True,
        (SemanticType.ENTITY_RELATIONSHIPS, SemanticType.GRAPH_EDGES): True,
    }
    
    @classmethod
    def are_compatible(cls, output_type: SemanticType, input_type: SemanticType) -> bool:
        """
        Check if an output type can connect to an input type.
        
        Args:
            output_type: The semantic type being produced
            input_type: The semantic type being consumed
            
        Returns:
            True if types are compatible, False otherwise
        """
        # Check exact match first
        if output_type == input_type:
            return True
        
        # Check compatibility rules
        key = (output_type, input_type)
        if key in cls.COMPATIBILITY_RULES:
            return cls.COMPATIBILITY_RULES[key]
        
        # Default to incompatible if not explicitly defined
        return False
    
    @classmethod
    def get_compatible_inputs(cls, output_type: SemanticType) -> Set[SemanticType]:
        """Get all input types compatible with given output type."""
        compatible = set()
        for input_type in SemanticType:
            if cls.are_compatible(output_type, input_type):
                compatible.add(input_type)
        return compatible
    
    @classmethod
    def get_compatible_outputs(cls, input_type: SemanticType) -> Set[SemanticType]:
        """Get all output types compatible with given input type."""
        compatible = set()
        for output_type in SemanticType:
            if cls.are_compatible(output_type, input_type):
                compatible.add(output_type)
        return compatible


# Convenience function
def compatible(output_type: SemanticType, input_type: SemanticType) -> bool:
    """Check if two semantic types are compatible."""
    return SemanticTypeRegistry.are_compatible(output_type, input_type)