"""
Compatibility module for t56_graph_metrics_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t56_graph_metrics import *

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract
    if hasattr(globals().get('GraphMetricsTool', None), 'get_contract'):
        pass  # Already has contract
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class GraphMetricsTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T56_GRAPH_METRICS"
            self.name = "Graph Metrics Calculator"
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Calculate comprehensive graph metrics including global and local measures",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_ref": {"type": "string"}
                    },
                    "required": ["graph_ref"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "global_metrics": {"type": "object"},
                        "local_metrics": {"type": "object"}
                    }
                },
                dependencies=["networkx", "neo4j"],
                performance_requirements={"max_execution_time": 45.0}
            )