"""
Compatibility module for t55_temporal_analysis_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t55_temporal_analysis import *

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract
    if hasattr(globals().get('TemporalAnalysisTool', None), 'get_contract'):
        pass  # Already has contract
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class TemporalAnalysisTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T55_TEMPORAL_ANALYSIS"
            self.name = "Temporal Graph Analysis"
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Analyze temporal patterns and evolution in time-series graph data",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_sequence": {"type": "array"},
                        "time_window": {"type": "string"}
                    },
                    "required": ["graph_sequence"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "temporal_metrics": {"type": "object"},
                        "evolution_patterns": {"type": "array"}
                    }
                },
                dependencies=["networkx", "neo4j"],
                performance_requirements={"max_execution_time": 120.0}
            )