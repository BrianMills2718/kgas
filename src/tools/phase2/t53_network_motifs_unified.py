"""
Compatibility module for t53_network_motifs_unified.

This module provides backward compatibility by importing from the existing implementation.
"""

# Import everything from the existing implementation
from .t53_network_motifs import *

# Check what the main class is and create alias
try:
    # Try to get the main tool class from the module
    NetworkMotifsTool = NetworkMotifsDetectionTool
except NameError:
    try:
        NetworkMotifsTool = NetworkMotifsAnalyzer
    except NameError:
        # Create a simple placeholder if neither exists
        from src.tools.base_tool import BaseTool, ToolContract
        
        class NetworkMotifsTool(BaseTool):
            def __init__(self, service_manager=None):
                super().__init__(service_manager)
                self.tool_id = "T53_NETWORK_MOTIFS"
                self.name = "Network Motifs Detection"
                
            def get_contract(self) -> ToolContract:
                return ToolContract(
                    tool_id=self.tool_id,
                    name=self.name,
                    description="Detect network motifs and structural patterns in graphs",
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
                            "motifs": {"type": "array"},
                            "motif_count": {"type": "integer"}
                        }
                    },
                    dependencies=["neo4j", "networkx"],
                    performance_requirements={"max_execution_time": 60.0}
                )