"""
Type-Based Tool Implementation

Tools that declare their input/output types and work with
the transformation matrix for automatic compatibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time
import json
import logging

from data_types import DataType, validate_data, get_schema
from transformation_matrix import ToolTransformation, TRANSFORMATION_MATRIX


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    output_data: Optional[Dict[str, Any]]
    output_type: Optional[DataType]
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None


class TypeBasedTool(ABC):
    """
    Base class for tools that work with the type transformation system.
    Each tool declares its input and output types.
    """
    
    def __init__(self, tool_id: str, tool_name: str, 
                 input_type: DataType, output_type: DataType):
        self.tool_id = tool_id
        self.tool_name = tool_name
        self.input_type = input_type
        self.output_type = output_type
        self.logger = logging.getLogger(f"Tool.{tool_id}")
        
        # Register with transformation matrix
        self.transformation = ToolTransformation(
            tool_id=tool_id,
            tool_name=tool_name,
            input_type=input_type,
            output_type=output_type
        )
        TRANSFORMATION_MATRIX.register_tool(self.transformation)
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return output data.
        Must be implemented by subclasses.
        """
        pass
    
    def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with validation and error handling.
        """
        start_time = time.time()
        
        # Validate input matches expected type
        if not validate_data(input_data, self.input_type):
            return ToolResult(
                success=False,
                output_data=None,
                output_type=None,
                error=f"Input data does not match schema for {self.input_type.value}",
                execution_time=time.time() - start_time
            )
        
        try:
            # Process the data
            output_data = self.process(input_data)
            
            # Validate output matches expected type
            if not validate_data(output_data, self.output_type):
                return ToolResult(
                    success=False,
                    output_data=output_data,
                    output_type=None,
                    error=f"Output data does not match schema for {self.output_type.value}",
                    execution_time=time.time() - start_time
                )
            
            return ToolResult(
                success=True,
                output_data=output_data,
                output_type=self.output_type,
                execution_time=time.time() - start_time,
                metadata={"tool_id": self.tool_id, "tool_name": self.tool_name}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output_data=None,
                output_type=None,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def get_compatible_tools(self):
        """Get list of tools that can process this tool's output"""
        return TRANSFORMATION_MATRIX.get_compatible_tools(self.tool_id)
    
    def describe(self):
        """Get description of this tool"""
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "transformation": f"{self.input_type.value} → {self.output_type.value}",
            "compatible_tools": self.get_compatible_tools()
        }


# Example implementations of actual tools

class T23C_LLMExtractor(TypeBasedTool):
    """Extract entities and relationships using LLM"""
    
    def __init__(self):
        super().__init__(
            tool_id="T23C",
            tool_name="LLM Ontology-Aware Extractor",
            input_type=DataType.RAW_TEXT,
            output_type=DataType.EXTRACTED_DATA
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        In real implementation, this would call an LLM.
        For demo, we'll simulate extraction.
        """
        text = input_data.get("text", "")
        
        # Simulated LLM extraction
        # In reality: response = llm.extract(text, ontology)
        
        return {
            "entities": [
                {
                    "id": "e1",
                    "type": "PERSON",
                    "text": "Jane Smith",
                    "confidence": 0.95
                },
                {
                    "id": "e2",
                    "type": "ORGANIZATION",
                    "text": "TechCorp",
                    "confidence": 0.90
                }
            ],
            "relationships": [
                {
                    "source_id": "e1",
                    "target_id": "e2",
                    "type": "WORKS_AT",
                    "confidence": 0.85
                }
            ],
            "properties": {
                "extracted_at": time.time(),
                "model": "gpt-4"
            },
            "confidence": 0.90,
            "model_used": "gpt-4"
        }


class T31_GraphBuilder(TypeBasedTool):
    """Build graph structure from extracted data"""
    
    def __init__(self):
        super().__init__(
            tool_id="T31",
            tool_name="Entity Builder",
            input_type=DataType.EXTRACTED_DATA,
            output_type=DataType.GRAPH_STRUCTURE
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert extracted data to graph structure"""
        
        entities = input_data.get("entities", [])
        relationships = input_data.get("relationships", [])
        
        # Build nodes
        nodes = []
        for entity in entities:
            nodes.append({
                "id": entity["id"],
                "label": entity["text"],
                "type": entity["type"],
                "properties": {
                    "confidence": entity.get("confidence", 1.0)
                }
            })
        
        # Build edges
        edges = []
        for rel in relationships:
            edges.append({
                "source": rel["source_id"],
                "target": rel["target_id"],
                "type": rel["type"],
                "properties": {
                    "confidence": rel.get("confidence", 1.0)
                }
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        }


class T68_PageRank(TypeBasedTool):
    """Calculate PageRank scores for graph nodes"""
    
    def __init__(self):
        super().__init__(
            tool_id="T68",
            tool_name="PageRank Calculator",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.ENRICHED_GRAPH
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate PageRank and enrich graph"""
        
        nodes = input_data.get("nodes", [])
        edges = input_data.get("edges", [])
        
        # Simplified PageRank calculation
        # In reality: use networkx or custom implementation
        
        # Add scores to nodes
        enriched_nodes = []
        for node in nodes:
            enriched_node = node.copy()
            enriched_node["scores"] = {
                "pagerank": 0.15 + 0.85 * (1.0 / len(nodes))  # Simplified
            }
            enriched_nodes.append(enriched_node)
        
        # Add weights to edges
        enriched_edges = []
        for edge in edges:
            enriched_edge = edge.copy()
            enriched_edge["weight"] = edge.get("properties", {}).get("confidence", 1.0)
            enriched_edges.append(enriched_edge)
        
        return {
            "nodes": enriched_nodes,
            "edges": enriched_edges,
            "metrics": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "density": len(edges) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0
            }
        }


class T91_GraphToTable(TypeBasedTool):
    """Convert enriched graph to table format"""
    
    def __init__(self):
        super().__init__(
            tool_id="T91",
            tool_name="Graph to Table Converter",
            input_type=DataType.ENRICHED_GRAPH,
            output_type=DataType.TABLE_FORMAT
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert graph to tabular format"""
        
        nodes = input_data.get("nodes", [])
        edges = input_data.get("edges", [])
        
        # Create node table
        node_columns = [
            {"name": "id", "type": "string"},
            {"name": "label", "type": "string"},
            {"name": "type", "type": "string"},
            {"name": "pagerank", "type": "float"}
        ]
        
        node_rows = []
        for node in nodes:
            node_rows.append([
                node["id"],
                node["label"],
                node["type"],
                node.get("scores", {}).get("pagerank", 0.0)
            ])
        
        # Create edge table
        edge_columns = [
            {"name": "source", "type": "string"},
            {"name": "target", "type": "string"},
            {"name": "type", "type": "string"},
            {"name": "weight", "type": "float"}
        ]
        
        edge_rows = []
        for edge in edges:
            edge_rows.append([
                edge["source"],
                edge["target"],
                edge["type"],
                edge.get("weight", 1.0)
            ])
        
        return {
            "columns": node_columns,
            "rows": node_rows,
            "metadata": {
                "source": "graph",
                "tables": {
                    "nodes": {"columns": node_columns, "rows": node_rows},
                    "edges": {"columns": edge_columns, "rows": edge_rows}
                }
            },
            "summary": {
                "total_nodes": len(node_rows),
                "total_edges": len(edge_rows)
            }
        }


class T15B_VectorEmbedder(TypeBasedTool):
    """Generate vector embeddings from text"""
    
    def __init__(self):
        super().__init__(
            tool_id="T15B",
            tool_name="Vector Embedder",
            input_type=DataType.RAW_TEXT,
            output_type=DataType.VECTOR_EMBEDDINGS
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate embeddings from text"""
        
        text = input_data.get("text", "")
        
        # Simulated embedding generation
        # In reality: embeddings = embedding_model.encode(text)
        
        # Split text into chunks for embedding
        chunks = text.split(". ")[:3]  # Simple sentence splitting
        
        embeddings = []
        for i, chunk in enumerate(chunks):
            # Simulate 384-dimensional embedding
            vector = [0.1 * (i + 1)] * 384  # Simplified
            
            embeddings.append({
                "id": f"emb_{i}",
                "vector": vector,
                "metadata": {
                    "text": chunk[:100],  # Store first 100 chars
                    "position": i
                }
            })
        
        return {
            "embeddings": embeddings,
            "model": "text-embedding-3-small",
            "dimension": 384
        }


def create_tool_registry():
    """Create and register all tools"""
    tools = {
        "T23C": T23C_LLMExtractor(),
        "T31": T31_GraphBuilder(),
        "T68": T68_PageRank(),
        "T91": T91_GraphToTable(),
        "T15B": T15B_VectorEmbedder()
    }
    return tools