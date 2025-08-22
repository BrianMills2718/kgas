"""
ORM-wrapped versions of tools for POC testing.
"""

from orm_wrapper import ORMWrapper
from role_definitions import Role, Cardinality
from semantic_types import SemanticType
from mock_tools import (
    MockT03TextLoader,
    MockT15ATextChunker,
    MockT23CEntityExtractor,
    MockT68PageRank
)


def create_t03_orm():
    """Create ORM-wrapped T03 Text Loader."""
    return ORMWrapper(
        tool=MockT03TextLoader(),
        tool_id="T03_TextLoader",
        input_roles=[
            Role(
                name="file_input",
                semantic_type=SemanticType.FILE_REFERENCE,
                cardinality=Cardinality.ONE,
                description="Path to text file",
                field_name="file_path"
            )
        ],
        output_roles=[
            Role(
                name="text_output",
                semantic_type=SemanticType.TEXT_CONTENT,
                cardinality=Cardinality.ONE,
                description="Loaded text content",
                field_name="content"  # T03 outputs "content"
            )
        ]
    )


def create_t15a_orm():
    """Create ORM-wrapped T15A Text Chunker."""
    return ORMWrapper(
        tool=MockT15ATextChunker(),
        tool_id="T15A_TextChunker",
        input_roles=[
            Role(
                name="text_input",
                semantic_type=SemanticType.TEXT_CONTENT,
                cardinality=Cardinality.ONE,
                description="Text to chunk",
                field_name="text"  # T15A expects "text" not "content"
            )
        ],
        output_roles=[
            Role(
                name="chunks_output",
                semantic_type=SemanticType.TEXT_SEGMENTS,
                cardinality=Cardinality.ONE_OR_MORE,
                description="Text chunks",
                field_name="chunks"
            )
        ]
    )


def create_t23c_orm():
    """Create ORM-wrapped T23C Entity Extractor."""
    return ORMWrapper(
        tool=MockT23CEntityExtractor(),
        tool_id="T23C_EntityExtractor",
        input_roles=[
            Role(
                name="text_input",
                semantic_type=SemanticType.TEXT_CONTENT,
                cardinality=Cardinality.ZERO_OR_ONE,
                description="Text to analyze",
                field_name="text"
            ),
            Role(
                name="chunks_input",
                semantic_type=SemanticType.TEXT_SEGMENTS,
                cardinality=Cardinality.ZERO_OR_ONE,
                description="Text chunks to analyze",
                field_name="chunks"
            )
        ],
        output_roles=[
            Role(
                name="entities_output",
                semantic_type=SemanticType.NAMED_ENTITIES,
                cardinality=Cardinality.ZERO_OR_MORE,
                description="Extracted entities",
                field_name="entities"
            ),
            Role(
                name="relationships_output",
                semantic_type=SemanticType.ENTITY_RELATIONSHIPS,
                cardinality=Cardinality.ZERO_OR_MORE,
                description="Entity relationships",
                field_name="relationships"
            )
        ]
    )


def create_t68_orm():
    """Create ORM-wrapped T68 PageRank (for invalid connection testing)."""
    return ORMWrapper(
        tool=MockT68PageRank(),
        tool_id="T68_PageRank",
        input_roles=[
            Role(
                name="graph_input",
                semantic_type=SemanticType.GRAPH_STRUCTURE,
                cardinality=Cardinality.ONE,
                description="Graph to analyze",
                field_name="graph"
            )
        ],
        output_roles=[
            Role(
                name="scores_output",
                semantic_type=SemanticType.NODE_SCORES,
                cardinality=Cardinality.ONE,
                description="PageRank scores",
                field_name="scores"
            )
        ]
    )


def get_all_wrapped_tools():
    """Get all wrapped tools for testing."""
    return {
        "T03": create_t03_orm(),
        "T15A": create_t15a_orm(),
        "T23C": create_t23c_orm(),
        "T68": create_t68_orm()
    }