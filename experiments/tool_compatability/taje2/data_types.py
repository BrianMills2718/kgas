"""
Data Type Definitions for Tool Compatibility

This defines the different states/types that data can exist in
as it flows through the KGAS pipeline. Tools transform data from
one type to another, creating a directed graph of transformations.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json


class DataType(Enum):
    """
    The different states that data can exist in.
    Each represents a specific schema/structure.
    """
    
    # Input types
    RAW_TEXT = "raw_text"                    # Unprocessed text document
    RAW_PDF = "raw_pdf"                      # PDF file
    RAW_HTML = "raw_html"                    # HTML content
    
    # Extraction outputs
    EXTRACTED_DATA = "extracted_data"        # Entities, relationships, properties from LLM
    TOKENIZED_TEXT = "tokenized_text"        # Text broken into tokens
    PARSED_DOCUMENT = "parsed_document"      # Structured document (sections, metadata)
    
    # Graph representations
    GRAPH_STRUCTURE = "graph_structure"      # Nodes and edges (Neo4j ready)
    ENRICHED_GRAPH = "enriched_graph"       # Graph with computed metrics
    COMMUNITY_GRAPH = "community_graph"      # Graph with community detection
    
    # Vector representations
    VECTOR_EMBEDDINGS = "vector_embeddings"  # Dense vector representations
    VECTOR_INDEX = "vector_index"            # Indexed vectors for similarity search
    
    # Table representations
    TABLE_FORMAT = "table_format"            # Rows and columns
    STATISTICAL_SUMMARY = "statistical_summary"  # Aggregated statistics
    
    # Analysis outputs
    ANALYZED_RESULTS = "analyzed_results"    # Generic analysis output
    THEORY_VALIDATION = "theory_validation"  # Theory-specific analysis
    METRICS_REPORT = "metrics_report"        # Computed metrics and scores
    
    # Storage formats
    NEO4J_TRANSACTION = "neo4j_transaction"  # Ready for Neo4j insert
    SQLITE_RECORDS = "sqlite_records"        # Ready for SQLite insert


@dataclass
class DataSchema:
    """
    Schema definition for a data type.
    Defines the structure that data must conform to.
    """
    data_type: DataType
    required_fields: List[str]
    optional_fields: List[str]
    field_types: Dict[str, str]  # field_name -> type description
    database: Optional[str] = None  # Which database this targets
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Check if data conforms to this schema"""
        # Check all required fields are present
        for field in self.required_fields:
            if field not in data:
                return False
        
        # Check no unexpected fields (optional)
        all_fields = set(self.required_fields + self.optional_fields)
        for field in data.keys():
            if field not in all_fields:
                print(f"Warning: unexpected field '{field}' in {self.data_type.value}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary for serialization"""
        return {
            "data_type": self.data_type.value,
            "required": self.required_fields,
            "optional": self.optional_fields,
            "types": self.field_types,
            "database": self.database
        }


# Define schemas for each data type
SCHEMAS = {
    DataType.RAW_TEXT: DataSchema(
        data_type=DataType.RAW_TEXT,
        required_fields=["text"],
        optional_fields=["source", "metadata"],
        field_types={
            "text": "string",
            "source": "string", 
            "metadata": "object"
        }
    ),
    
    DataType.EXTRACTED_DATA: DataSchema(
        data_type=DataType.EXTRACTED_DATA,
        required_fields=["entities", "relationships"],
        optional_fields=["properties", "confidence", "model_used"],
        field_types={
            "entities": "array<{id, type, text, confidence}>",
            "relationships": "array<{source_id, target_id, type, confidence}>",
            "properties": "object",
            "confidence": "float",
            "model_used": "string"
        }
    ),
    
    DataType.GRAPH_STRUCTURE: DataSchema(
        data_type=DataType.GRAPH_STRUCTURE,
        required_fields=["nodes", "edges"],
        optional_fields=["metadata", "graph_type"],
        field_types={
            "nodes": "array<{id, label, type, properties}>",
            "edges": "array<{source, target, type, properties}>",
            "metadata": "object",
            "graph_type": "string"
        },
        database="neo4j"
    ),
    
    DataType.ENRICHED_GRAPH: DataSchema(
        data_type=DataType.ENRICHED_GRAPH,
        required_fields=["nodes", "edges", "metrics"],
        optional_fields=["centrality", "communities"],
        field_types={
            "nodes": "array<{id, label, type, properties, scores}>",
            "edges": "array<{source, target, type, properties, weight}>",
            "metrics": "object<{node_count, edge_count, density, ...}>",
            "centrality": "object<{node_id: score}>",
            "communities": "array<array<node_id>>"
        },
        database="neo4j"
    ),
    
    DataType.TABLE_FORMAT: DataSchema(
        data_type=DataType.TABLE_FORMAT,
        required_fields=["columns", "rows"],
        optional_fields=["metadata", "summary"],
        field_types={
            "columns": "array<{name, type}>",
            "rows": "array<array>",
            "metadata": "object",
            "summary": "object"
        },
        database="sqlite"
    ),
    
    DataType.VECTOR_EMBEDDINGS: DataSchema(
        data_type=DataType.VECTOR_EMBEDDINGS,
        required_fields=["embeddings"],
        optional_fields=["model", "dimension"],
        field_types={
            "embeddings": "array<{id, vector, metadata}>",
            "model": "string",
            "dimension": "integer"
        },
        database="neo4j"  # Neo4j supports vector storage
    ),
    
    DataType.ANALYZED_RESULTS: DataSchema(
        data_type=DataType.ANALYZED_RESULTS,
        required_fields=["analysis_type", "results"],
        optional_fields=["confidence", "metadata"],
        field_types={
            "analysis_type": "string",
            "results": "object",
            "confidence": "float",
            "metadata": "object"
        }
    ),
    
    DataType.NEO4J_TRANSACTION: DataSchema(
        data_type=DataType.NEO4J_TRANSACTION,
        required_fields=["cypher_statements", "parameters"],
        optional_fields=["transaction_id"],
        field_types={
            "cypher_statements": "array<string>",
            "parameters": "object",
            "transaction_id": "string"
        },
        database="neo4j"
    ),
    
    DataType.SQLITE_RECORDS: DataSchema(
        data_type=DataType.SQLITE_RECORDS,
        required_fields=["table_name", "records"],
        optional_fields=["operation"],
        field_types={
            "table_name": "string",
            "records": "array<object>",
            "operation": "string"  # insert, update, etc.
        },
        database="sqlite"
    )
}


def get_schema(data_type: DataType) -> DataSchema:
    """Get the schema for a data type"""
    return SCHEMAS.get(data_type)


def validate_data(data: Dict[str, Any], data_type: DataType) -> bool:
    """Validate that data conforms to a specific type's schema"""
    schema = get_schema(data_type)
    if not schema:
        raise ValueError(f"No schema defined for {data_type}")
    return schema.validate(data)


def describe_transformation(from_type: DataType, to_type: DataType) -> str:
    """Describe what a transformation does"""
    descriptions = {
        (DataType.RAW_TEXT, DataType.EXTRACTED_DATA): "Extract entities and relationships using LLM",
        (DataType.EXTRACTED_DATA, DataType.GRAPH_STRUCTURE): "Build graph from entities and relationships",
        (DataType.GRAPH_STRUCTURE, DataType.ENRICHED_GRAPH): "Compute graph metrics and enrich nodes",
        (DataType.ENRICHED_GRAPH, DataType.TABLE_FORMAT): "Convert graph to tabular format",
        (DataType.RAW_TEXT, DataType.VECTOR_EMBEDDINGS): "Generate embeddings from text",
        (DataType.GRAPH_STRUCTURE, DataType.NEO4J_TRANSACTION): "Prepare graph for Neo4j insertion",
        (DataType.TABLE_FORMAT, DataType.SQLITE_RECORDS): "Prepare table for SQLite storage",
        # Add more descriptions as needed
    }
    
    return descriptions.get((from_type, to_type), f"Transform {from_type.value} to {to_type.value}")