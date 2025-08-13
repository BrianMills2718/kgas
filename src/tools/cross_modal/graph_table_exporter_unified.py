"""
Graph Table Exporter Unified Tool - Converts graph data to tabular format
"""

import logging
from typing import Dict, Any
from .graph_table_exporter import GraphTableExporter as GraphTableExporterImpl
from src.tools.base_tool import BaseTool
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class GraphTableExporterUnified(BaseTool):
    """
    Unified interface for Graph Table Exporter.
    Converts graph data from Neo4j to structured table formats.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize Graph Table Exporter with unified interface"""
        if service_manager is None:
            service_manager = ServiceManager()
        super().__init__(service_manager)
        
        # Set standardized tool ID
        self.tool_id = "GRAPH_TABLE_EXPORTER"
        self.tool_name = "Graph Table Exporter"
        
        # Initialize the implementation
        self.exporter = GraphTableExporterImpl()
        
        logger.info("Graph Table Exporter initialized with unified interface")
    
    def execute(self, request) -> Dict[str, Any]:
        """Execute graph to table export"""
        try:
            # Handle both dict and ToolRequest input
            if hasattr(request, 'input_data'):
                # ToolRequest object
                input_data = request.input_data
                graph_data = input_data.get("graph_data", {})
                table_type = input_data.get("format", input_data.get("table_type", "edge_list"))
            else:
                # Dict input (legacy)
                graph_data = request.get("graph_data", {})
                table_type = request.get("table_type", "edge_list")
            
            # Use the actual exporter execute method
            export_input = {
                "graph_data": graph_data,
                "format": table_type,
                "filter_params": {"format": table_type}
            }
            result = self.exporter.execute(export_input)
            
            return {
                "status": "success",
                "data": result,
                "metadata": {
                    "tool_id": self.tool_id,
                    "table_type": table_type
                }
            }
        except Exception as e:
            logger.error(f"Graph table export failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {"tool_id": self.tool_id}
            }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if not isinstance(input_data, dict):
            return False
        if "graph_data" not in input_data:
            return False
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Check tool health"""
        return {
            "status": "success",
            "healthy": True,
            "tool_id": self.tool_id,
            "metadata": {"exporter_available": self.exporter is not None}
        }
    
    def get_status(self) -> str:
        """Get tool status"""
        return "ready"
    
    def get_contract(self) -> Dict[str, Any]:
        """Get tool contract"""
        return {
            "tool_id": self.tool_id,
            "name": self.tool_name,
            "description": "Convert graph data to tabular formats",
            "category": "cross_modal",  # Required parameter for ToolContract
            "input_schema": {
                "type": "object",
                "properties": {
                    "graph_data": {"type": "object"},
                    "table_type": {"type": "string", "enum": ["edge_list", "node_attributes", "adjacency", "full"]}
                },
                "required": ["graph_data"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "table_data": {"type": "object"},
                    "metadata": {"type": "object"}
                }
            },
            "dependencies": [],
            "performance_requirements": {
                "max_execution_time": 30.0,
                "max_memory_mb": 500
            }
        }