"""
Graph to Table Exporter - Fixed Version

Export Neo4j subgraphs to statistical formats with proper ToolResult interface.
"""

from typing import Any, Dict, Optional, List
from datetime import datetime
import pandas as pd
import json
import uuid

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract, ToolErrorCode
from src.core.service_manager import ServiceManager


class GraphTableExporterFixed(BaseTool):
    """
    Export Neo4j subgraphs to statistical formats with proper ToolResult interface.
    
    This is a fixed version that properly implements the BaseTool interface.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize the Graph to Table Exporter."""
        if service_manager is None:
            service_manager = ServiceManager()
        
        super().__init__(service_manager)
        
        self.tool_id = "GRAPH_TABLE_EXPORTER"
        self.name = "Graph to Table Exporter"
        self.category = "cross_modal"
        
        # Get Neo4j manager from service manager
        try:
            self.neo4j_manager = service_manager.get_neo4j_manager()
            self.driver = self.neo4j_manager.get_driver() if self.neo4j_manager else None
            self.services_available = True
        except Exception:
            self.driver = None
            self.services_available = False
    
    def get_contract(self) -> ToolContract:
        """Return tool contract specification."""
        return ToolContract(
            tool_id=self.tool_id,
            name=self.name,
            description="Export Neo4j subgraphs to statistical formats",
            category=self.category,
            input_schema={
                "type": "object",
                "properties": {
                    "graph_data": {
                        "type": "object",
                        "properties": {
                            "nodes": {"type": "array"},
                            "edges": {"type": "array"}
                        },
                        "required": ["nodes", "edges"]
                    },
                    "export_format": {
                        "type": "string",
                        "enum": ["dataframe", "json", "csv", "sqlite"]
                    }
                },
                "required": ["graph_data"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "dataframes": {"type": "object"},
                    "exports": {"type": "object"},
                    "statistics": {"type": "object"}
                }
            },
            dependencies=["neo4j"],
            performance_requirements={
                "max_execution_time": 30.0,
                "max_memory_mb": 1000
            },
            error_conditions=[
                "INVALID_GRAPH_FORMAT",
                "EXPORT_FAILED",
                "NEO4J_NOT_AVAILABLE"
            ]
        )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute graph to table export with proper ToolResult interface."""
        self._start_execution()
        
        try:
            # Validate input
            if not self.validate_input(request.input_data):
                return self._create_error_result(
                    request, 
                    ToolErrorCode.INVALID_INPUT,
                    "Invalid input format"
                )
            
            graph_data = request.input_data.get("graph_data", {})
            export_format = request.input_data.get("export_format", "dataframe")
            
            # Convert graph data to DataFrames
            nodes_df, edges_df = self._graph_to_dataframes(graph_data)
            
            # Generate exports based on format
            exports = {}
            if export_format == "dataframe":
                exports["dataframes"] = {
                    "nodes": nodes_df,
                    "edges": edges_df
                }
            elif export_format == "json":
                exports["json"] = {
                    "nodes": nodes_df.to_dict('records'),
                    "edges": edges_df.to_dict('records')
                }
            elif export_format == "csv":
                # In real implementation, would save to files
                exports["csv"] = {
                    "nodes_csv": nodes_df.to_csv(index=False),
                    "edges_csv": edges_df.to_csv(index=False)
                }
            
            # Generate statistics
            stats = self._generate_statistics(nodes_df, edges_df)
            
            execution_time, memory_used = self._end_execution()
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={
                    "dataframes": exports.get("dataframes", {}),
                    "exports": exports,
                    "statistics": stats,
                    "nodes_count": len(nodes_df),
                    "edges_count": len(edges_df)
                },
                metadata={
                    "export_format": export_format,
                    "timestamp": datetime.now().isoformat()
                },
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            execution_time, memory_used = self._end_execution()
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={},
                error_code=ToolErrorCode.PROCESSING_ERROR,
                error_message=f"Export failed: {str(e)}",
                execution_time=execution_time,
                memory_used=memory_used
            )
    
    def _create_error_result(self, request: ToolRequest, error_code: ToolErrorCode, 
                           error_message: str) -> ToolResult:
        """Create error result with proper format."""
        execution_time, memory_used = self._end_execution()
        return ToolResult(
            tool_id=self.tool_id,
            status="error",
            data={},
            error_code=error_code.value,
            error_message=error_message,
            execution_time=execution_time,
            memory_used=memory_used
        )
    
    def _graph_to_dataframes(self, graph_data: Dict[str, Any]) -> tuple:
        """Convert graph data to pandas DataFrames."""
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        # Create nodes DataFrame
        nodes_data = []
        for node in nodes:
            if isinstance(node, dict):
                nodes_data.append({
                    "id": node.get("id", node.get("entity_id", "")),
                    "name": node.get("canonical_name", node.get("name", "")),
                    "type": node.get("entity_type", node.get("type", "")),
                    "confidence": node.get("confidence", 0.0),
                    **node.get("properties", {})
                })
        
        # Create edges DataFrame
        edges_data = []
        for edge in edges:
            if isinstance(edge, dict):
                edges_data.append({
                    "source": edge.get("source", edge.get("source_id", "")),
                    "target": edge.get("target", edge.get("target_id", "")),
                    "relationship_type": edge.get("relationship_type", ""),
                    "confidence": edge.get("confidence", 0.0),
                    "weight": edge.get("weight", 1.0),
                    **edge.get("properties", {})
                })
        
        nodes_df = pd.DataFrame(nodes_data)
        edges_df = pd.DataFrame(edges_data)
        
        return nodes_df, edges_df
    
    def _generate_statistics(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical summaries."""
        stats = {
            "node_statistics": {
                "total_nodes": len(nodes_df),
                "node_types": nodes_df['type'].value_counts().to_dict() if 'type' in nodes_df.columns else {},
                "avg_confidence": float(nodes_df['confidence'].mean()) if 'confidence' in nodes_df.columns else 0.0
            },
            "edge_statistics": {
                "total_edges": len(edges_df),
                "relationship_types": edges_df['relationship_type'].value_counts().to_dict() if 'relationship_type' in edges_df.columns else {},
                "avg_confidence": float(edges_df['confidence'].mean()) if 'confidence' in edges_df.columns else 0.0,
                "avg_weight": float(edges_df['weight'].mean()) if 'weight' in edges_df.columns else 0.0
            }
        }
        
        return stats