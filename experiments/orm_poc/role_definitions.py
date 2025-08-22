"""
Role Definitions for ORM Proof of Concept

Defines semantic roles that tools consume and produce.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from semantic_types import SemanticType


class Cardinality(Enum):
    """How many instances of a role are allowed/required."""
    ONE = "1"              # Exactly one (required)
    ZERO_OR_ONE = "0..1"   # Optional (zero or one)
    ONE_OR_MORE = "1..*"   # At least one
    ZERO_OR_MORE = "0..*"  # Any number (including zero)


@dataclass
class Role:
    """
    A semantic role that data plays in tool execution.
    
    Attributes:
        name: Internal name for the role (e.g., "input_text", "entities")
        semantic_type: The semantic type of data in this role
        cardinality: How many instances are allowed/required
        description: Human-readable description
        field_name: Optional field name in actual tool implementation
    """
    name: str
    semantic_type: SemanticType
    cardinality: Cardinality = Cardinality.ONE
    description: str = ""
    field_name: Optional[str] = None
    
    def __repr__(self):
        return f"Role({self.name}: {self.semantic_type.value})"
    
    def is_required(self) -> bool:
        """Check if this role is required (not optional)."""
        return self.cardinality in [Cardinality.ONE, Cardinality.ONE_OR_MORE]
    
    def accepts_multiple(self) -> bool:
        """Check if this role accepts multiple values."""
        return self.cardinality in [Cardinality.ONE_OR_MORE, Cardinality.ZERO_OR_MORE]


# Pre-defined roles for common patterns
class CommonRoles:
    """Common role patterns used across tools."""
    
    # Input roles
    FILE_INPUT = Role(
        name="file_input",
        semantic_type=SemanticType.FILE_REFERENCE,
        cardinality=Cardinality.ONE,
        description="Path to input file",
        field_name="file_path"
    )
    
    TEXT_INPUT = Role(
        name="text_input",
        semantic_type=SemanticType.TEXT_CONTENT,
        cardinality=Cardinality.ONE,
        description="Input text content",
        field_name="text"
    )
    
    CHUNKS_INPUT = Role(
        name="chunks_input",
        semantic_type=SemanticType.TEXT_SEGMENTS,
        cardinality=Cardinality.ONE_OR_MORE,
        description="Text chunks for processing",
        field_name="chunks"
    )
    
    # Output roles
    TEXT_OUTPUT = Role(
        name="text_output",
        semantic_type=SemanticType.TEXT_CONTENT,
        cardinality=Cardinality.ONE,
        description="Output text content",
        field_name="content"
    )
    
    CHUNKS_OUTPUT = Role(
        name="chunks_output",
        semantic_type=SemanticType.TEXT_SEGMENTS,
        cardinality=Cardinality.ONE_OR_MORE,
        description="Chunked text output",
        field_name="chunks"
    )
    
    ENTITIES_OUTPUT = Role(
        name="entities_output",
        semantic_type=SemanticType.NAMED_ENTITIES,
        cardinality=Cardinality.ZERO_OR_MORE,
        description="Extracted named entities",
        field_name="entities"
    )
    
    GRAPH_OUTPUT = Role(
        name="graph_output",
        semantic_type=SemanticType.GRAPH_STRUCTURE,
        cardinality=Cardinality.ONE,
        description="Graph structure with nodes and edges",
        field_name="graph"
    )