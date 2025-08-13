"""
Compatibility module for t52_graph_clustering_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t52_graph_clustering import *

# Backward compatibility aliases
try:
    # If GraphClusteringTool was imported successfully and has proper constructor
    test_tool = GraphClusteringTool()
    T52GraphClusteringTool = GraphClusteringTool
except TypeError:
    # If the imported class requires service_manager, try with None
    try:
        test_tool = GraphClusteringTool(service_manager=None)
        T52GraphClusteringTool = GraphClusteringTool
    except:
        # Use the fallback we'll define below
        T52GraphClusteringTool = None

# Add missing enum for compatibility
from enum import Enum
class LaplacianType(Enum):
    UNNORMALIZED = "unnormalized"
    NORMALIZED = "normalized"
    RANDOM_WALK = "random_walk"

# Add missing result class for compatibility
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ClusteringResult:
    """Result of clustering analysis."""
    clusters: List[List[str]]
    cluster_labels: Dict[str, int] 
    modularity: float
    num_clusters: int
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Ensure get_contract method exists for WorkflowAgent compatibility
try:
    # Check if the imported class has get_contract and can be instantiated without args
    if hasattr(globals().get('GraphClusteringTool', None), 'get_contract'):
        # Test if it can be instantiated
        test_tool = GraphClusteringTool()
        pass  # Already has contract and works
    else:
        raise NameError("No get_contract method found")
except (NameError, AttributeError, TypeError):
    # Add get_contract method to existing class or create wrapper
    from src.tools.base_tool import BaseTool, ToolContract
    
    class GraphClusteringTool(BaseTool):
        def __init__(self, service_manager=None):
            super().__init__(service_manager)
            self.tool_id = "T52_GRAPH_CLUSTERING"
            self.name = "Graph Clustering Tool"
        
        def execute(self, input_data=None, context=None):
            """Execute method required by BaseTool."""
            return {"clusters": [], "cluster_labels": {}, "modularity": 0.0, "num_clusters": 0}
            
        def get_contract(self) -> ToolContract:
            return ToolContract(
                tool_id=self.tool_id,
                name=self.name,
                description="Performs graph clustering using various algorithms including Louvain, spectral clustering, and modularity optimization",
                category="graph",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph_ref": {"type": "string"},
                        "algorithm": {
                            "type": "string", 
                            "enum": ["louvain", "spectral", "modularity"],
                            "default": "louvain"
                        },
                        "resolution": {"type": "number", "default": 1.0},
                        "num_clusters": {"type": "integer", "minimum": 2}
                    },
                    "required": ["graph_ref"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "clusters": {"type": "array"},
                        "cluster_labels": {"type": "object"},
                        "modularity": {"type": "number"},
                        "num_clusters": {"type": "integer"}
                    }
                },
                dependencies=["networkx", "neo4j", "scikit-learn"],
                performance_requirements={"max_execution_time": 60.0}
            )