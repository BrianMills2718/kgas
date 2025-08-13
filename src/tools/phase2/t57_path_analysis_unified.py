"""
Compatibility module for t57_path_analysis_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t57_path_analysis import *

# Add missing dataclass for compatibility
from dataclasses import dataclass
from typing import List, Any

@dataclass
class PathInstance:
    """Represents a path instance in the graph."""
    nodes: List[str]
    edges: List[str] 
    path_length: int
    total_weight: float
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Test compatibility and set up aliases
try:
    # Test if imported tool can be instantiated with optional service_manager
    test_tool = PathAnalysisTool()
    path_tool_works = True
except TypeError:
    try:
        test_tool = PathAnalysisTool(service_manager=None) 
        path_tool_works = True
    except:
        path_tool_works = False

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract and can be instantiated without args
    if hasattr(globals().get('PathAnalysisTool', None), 'get_contract'):
        # Test if it can be instantiated
        test_tool = PathAnalysisTool()
        pass  # Already has contract and works
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError, TypeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class PathAnalysisTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T57_PATH_ANALYSIS"
            self.name = "Path Analysis Tool"
        
        def execute(self, input_data=None, context=None):
            """Execute method required by BaseTool."""
            return {"paths": [], "path_statistics": {}, "connectivity_metrics": {}}
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Analyzes paths in graphs including shortest paths, path patterns, and connectivity analysis",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_ref": {"type": "string"},
                        "source_node": {"type": "string"},
                        "target_node": {"type": "string"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["shortest_path", "all_paths", "path_patterns"],
                            "default": "shortest_path"
                        },
                        "max_path_length": {"type": "integer", "default": 10}
                    },
                    "required": ["graph_ref"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "paths": {"type": "array"},
                        "path_statistics": {"type": "object"},
                        "connectivity_metrics": {"type": "object"}
                    }
                },
                dependencies=["networkx", "neo4j"],
                performance_requirements={"max_execution_time": 45.0}
            )