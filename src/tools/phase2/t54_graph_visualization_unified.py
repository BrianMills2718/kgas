"""
Compatibility module for t54_graph_visualization_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t54_graph_visualization import *

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract
    if hasattr(globals().get('GraphVisualizationTool', None), 'get_contract'):
        pass  # Already has contract
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class GraphVisualizationTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T54_GRAPH_VISUALIZATION"
            self.name = "Graph Visualization"
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Create interactive graph visualizations with advanced layouts",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_ref": {"type": "string"},
                        "layout_type": {"type": "string", "enum": ["spring", "circular", "kamada_kawai", "hierarchical"]}
                    },
                    "required": ["graph_ref"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "visualization": {"type": "object"},
                        "layout_info": {"type": "object"}
                    }
                },
                dependencies=["plotly", "networkx", "neo4j"],
                performance_requirements={"max_execution_time": 30.0}
            )