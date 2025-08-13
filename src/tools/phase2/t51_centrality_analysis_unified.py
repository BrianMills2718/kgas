"""
Compatibility module for t51_centrality_analysis_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t51_centrality_analysis import *

# The existing file should contain the unified implementation

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract
    if hasattr(globals().get('CentralityAnalysisTool', None), 'get_contract'):
        pass  # Already has contract
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class CentralityAnalysisTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T51_CENTRALITY_ANALYSIS"
            self.name = "Centrality Analysis Tool"
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Analyzes graph centrality metrics including degree, betweenness, closeness, and eigenvector centrality",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_ref": {"type": "string"},
                        "centrality_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["degree", "betweenness", "closeness", "eigenvector"]
                        },
                        "normalize": {"type": "boolean", "default": True}
                    },
                    "required": ["graph_ref"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "centrality_scores": {"type": "object"},
                        "statistics": {"type": "object"},
                        "top_nodes": {"type": "array"}
                    }
                },
                dependencies=["networkx", "neo4j"],
                performance_requirements={"max_execution_time": 45.0}
            )