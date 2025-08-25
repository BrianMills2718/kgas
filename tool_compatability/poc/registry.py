"""
Tool Registry with Automatic Chain Discovery

This module provides the central registry for tools and implements
automatic discovery of valid tool chains based on type compatibility.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
import networkx as nx
from pydantic import BaseModel
import json
import logging
from datetime import datetime

from .base_tool import BaseTool, ToolInfo
from .data_types import DataType, are_types_compatible


class ChainExecutionResult(BaseModel):
    """Result of executing a tool chain"""
    chain: List[str]
    success: bool
    duration_seconds: float
    memory_used_mb: float
    intermediate_results: List[Dict[str, Any]]
    final_output: Optional[Any] = None
    error: Optional[str] = None


class ToolRegistry:
    """
    Central registry for tools with automatic chain discovery.
    
    This registry:
    - Manages tool registration and lookup
    - Discovers valid tool chains automatically
    - Executes chains with metrics collection
    - Provides visualization capabilities
    """
    
    def __init__(self):
        """Initialize the registry"""
        self.tools: Dict[str, BaseTool] = {}
        self.compatibility_cache: Dict[Tuple[str, str], bool] = {}
        self.logger = logging.getLogger(__name__)
        
    # ========== Registration ==========
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
        """
        tool_id = tool.tool_id
        
        if tool_id in self.tools:
            self.logger.warning(f"Overwriting existing tool: {tool_id}")
        
        self.tools[tool_id] = tool
        self.compatibility_cache.clear()  # Invalidate cache
        
        self.logger.info(f"Registered tool: {tool_id} "
                        f"({tool.input_type.value} → {tool.output_type.value})")
    
    def unregister(self, tool_id: str) -> bool:
        """
        Remove a tool from the registry.
        
        Args:
            tool_id: ID of tool to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        if tool_id in self.tools:
            del self.tools[tool_id]
            self.compatibility_cache.clear()
            self.logger.info(f"Unregistered tool: {tool_id}")
            return True
        return False
    
    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    # ========== Compatibility Checking ==========
    
    def can_connect(self, tool1_id: str, tool2_id: str) -> bool:
        """
        Check if tool1's output can feed into tool2's input.
        
        Args:
            tool1_id: ID of source tool
            tool2_id: ID of target tool
            
        Returns:
            True if tools are compatible
        """
        # Check cache first
        cache_key = (tool1_id, tool2_id)
        if cache_key in self.compatibility_cache:
            return self.compatibility_cache[cache_key]
        
        # Get tools
        tool1 = self.tools.get(tool1_id)
        tool2 = self.tools.get(tool2_id)
        
        if not tool1 or not tool2:
            self.compatibility_cache[cache_key] = False
            return False
        
        # Check type compatibility
        compatible = are_types_compatible(tool1.output_type, tool2.input_type)
        
        # Cache result
        self.compatibility_cache[cache_key] = compatible
        
        return compatible
    
    # ========== Chain Discovery ==========
    
    def build_graph(self) -> nx.DiGraph:
        """
        Build a directed graph of tool connections.
        
        Returns:
            NetworkX directed graph where edges indicate compatibility
        """
        G = nx.DiGraph()
        
        # Add all tools as nodes
        for tool_id, tool in self.tools.items():
            G.add_node(tool_id, 
                      input_type=tool.input_type.value,
                      output_type=tool.output_type.value)
        
        # Add edges for compatible connections
        for t1_id in self.tools:
            for t2_id in self.tools:
                if t1_id != t2_id and self.can_connect(t1_id, t2_id):
                    G.add_edge(t1_id, t2_id)
        
        return G
    
    def find_chains(self, 
                   start_type: DataType, 
                   end_type: DataType,
                   max_length: int = 5) -> List[List[str]]:
        """
        Find all valid tool chains from start_type to end_type.
        
        Args:
            start_type: Required input type
            end_type: Desired output type
            max_length: Maximum chain length
            
        Returns:
            List of tool chains (each chain is a list of tool IDs)
        """
        G = self.build_graph()
        chains = []
        
        # Find tools that accept start_type
        start_tools = [
            tool_id for tool_id, tool in self.tools.items()
            if tool.input_type == start_type
        ]
        
        # Find tools that produce end_type
        end_tools = [
            tool_id for tool_id, tool in self.tools.items()
            if tool.output_type == end_type
        ]
        
        # Find all simple paths
        for start_tool in start_tools:
            for end_tool in end_tools:
                if start_tool == end_tool:
                    # Single tool chain
                    chains.append([start_tool])
                else:
                    # Multi-tool chain
                    try:
                        paths = nx.all_simple_paths(
                            G, start_tool, end_tool, 
                            cutoff=max_length
                        )
                        chains.extend(list(paths))
                    except nx.NetworkXNoPath:
                        continue
        
        # Sort by chain length (prefer shorter chains)
        chains.sort(key=len)
        
        return chains
    
    def find_shortest_chain(self,
                          start_type: DataType,
                          end_type: DataType) -> Optional[List[str]]:
        """
        Find the shortest valid chain from start_type to end_type.
        
        Args:
            start_type: Required input type
            end_type: Desired output type
            
        Returns:
            Shortest tool chain or None if no chain exists
        """
        chains = self.find_chains(start_type, end_type)
        return chains[0] if chains else None
    
    # ========== Chain Execution ==========
    
    def execute_chain(self, 
                     chain: List[str], 
                     input_data: Any) -> ChainExecutionResult:
        """
        Execute a tool chain.
        
        Args:
            chain: List of tool IDs in execution order
            input_data: Initial input data
            
        Returns:
            ChainExecutionResult with metrics and output
        """
        start_time = datetime.now()
        intermediate_results = []
        current_data = input_data
        total_memory = 0.0
        
        try:
            for i, tool_id in enumerate(chain):
                tool = self.get_tool(tool_id)
                if not tool:
                    raise ValueError(f"Tool not found: {tool_id}")
                
                self.logger.info(f"Executing step {i+1}/{len(chain)}: {tool_id}")
                
                # Execute tool
                result = tool.process(current_data)
                
                if not result.success:
                    raise RuntimeError(f"Tool {tool_id} failed: {result.error}")
                
                # Collect metrics
                intermediate_results.append({
                    "tool": tool_id,
                    "success": result.success,
                    "duration": result.metrics.duration_seconds,
                    "memory": result.metrics.memory_used_mb
                })
                
                total_memory += result.metrics.memory_used_mb
                
                # Update data for next tool
                current_data = result.data
            
            # Calculate total duration
            duration = (datetime.now() - start_time).total_seconds()
            
            return ChainExecutionResult(
                chain=chain,
                success=True,
                duration_seconds=duration,
                memory_used_mb=total_memory,
                intermediate_results=intermediate_results,
                final_output=current_data
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            return ChainExecutionResult(
                chain=chain,
                success=False,
                duration_seconds=duration,
                memory_used_mb=total_memory,
                intermediate_results=intermediate_results,
                error=str(e)
            )
    
    # ========== Visualization ==========
    
    def visualize_compatibility(self) -> str:
        """
        Generate a text-based compatibility matrix.
        
        Returns:
            String representation of compatibility matrix
        """
        if not self.tools:
            return "No tools registered"
        
        tool_ids = sorted(self.tools.keys())
        max_len = max(len(tid) for tid in tool_ids)
        
        # Build header
        lines = []
        header = " " * (max_len + 2) + "| "
        for tid in tool_ids:
            header += tid[:8].center(9) + "| "
        lines.append(header)
        lines.append("-" * len(header))
        
        # Build rows
        for t1_id in tool_ids:
            row = t1_id.ljust(max_len) + " | "
            for t2_id in tool_ids:
                if t1_id == t2_id:
                    row += "   -    | "
                elif self.can_connect(t1_id, t2_id):
                    row += "   ✓    | "
                else:
                    row += "        | "
            lines.append(row)
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry stats
        """
        G = self.build_graph()
        
        stats = {
            "tool_count": len(self.tools),
            "edge_count": G.number_of_edges(),
            "tools": {},
            "connectivity": {
                "average_degree": sum(dict(G.degree()).values()) / len(G) if len(G) > 0 else 0,
                "strongly_connected": nx.is_strongly_connected(G),
                "weakly_connected": nx.is_weakly_connected(G),
                "components": nx.number_weakly_connected_components(G)
            }
        }
        
        # Per-tool statistics
        for tool_id, tool in self.tools.items():
            stats["tools"][tool_id] = {
                "input_type": tool.input_type.value,
                "output_type": tool.output_type.value,
                "in_degree": G.in_degree(tool_id),
                "out_degree": G.out_degree(tool_id)
            }
        
        return stats
    
    def export_graph(self, filepath: str) -> None:
        """
        Export the tool graph to a JSON file.
        
        Args:
            filepath: Path to save the graph
        """
        G = self.build_graph()
        
        data = {
            "nodes": [
                {
                    "id": node,
                    "input_type": G.nodes[node]["input_type"],
                    "output_type": G.nodes[node]["output_type"]
                }
                for node in G.nodes()
            ],
            "edges": [
                {"source": u, "target": v}
                for u, v in G.edges()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Exported graph to {filepath}")
    
    # ========== String Representation ==========
    
    def __str__(self) -> str:
        return f"ToolRegistry({len(self.tools)} tools)"
    
    def __repr__(self) -> str:
        tool_list = ", ".join(self.tools.keys())
        return f"ToolRegistry(tools=[{tool_list}])"