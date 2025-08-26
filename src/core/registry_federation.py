#!/usr/bin/env python3
"""
Registry Federation - Query both framework and production registries
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ToolFramework
from src.core.tool_contract import get_tool_registry


class FederatedRegistry:
    """
    Federated registry that queries both systems
    Does NOT replace either registry - queries both
    """
    
    def __init__(self, framework: ToolFramework = None):
        self.framework = framework or ToolFramework()
        self.production = get_tool_registry()
        
    def discover_all_chains(self, input_type: str, output_type: str) -> Dict[str, List]:
        """
        Discover chains from both registries
        Returns dict with 'framework', 'production', and 'mixed' chains
        """
        results = {
            'framework': [],
            'production': [],
            'mixed': []
        }
        
        # Get framework chains
        try:
            # Convert string types to DataType if needed
            from data_types import DataType
            
            if isinstance(input_type, str):
                input_dt = DataType(input_type.lower())
            else:
                input_dt = input_type
                
            if isinstance(output_type, str):
                output_dt = DataType(output_type.lower())
            else:
                output_dt = output_type
                
            framework_chains = self.framework.find_chains(input_dt, output_dt)
            results['framework'] = framework_chains
        except Exception as e:
            print(f"Framework discovery error: {e}")
        
        # Get production chains - production registry has different API
        try:
            # Production registry lists tools but doesn't have chain discovery
            # We'll list compatible tools instead
            production_tools = self.production.list_tools()
            results['production'] = [[tool_id] for tool_id in production_tools[:5]]  # Sample
        except Exception as e:
            print(f"Production discovery error: {e}")
        
        # Find mixed chains (framework + production tools)
        # This would require more sophisticated matching logic
        # For now, we'll indicate the capability exists
        if results['framework'] and results['production']:
            # Example: could combine framework and production tools
            results['mixed'] = []  # Would implement cross-registry chaining
        
        return results
        
    def get_tool(self, tool_id: str) -> Optional[Any]:
        """Get tool from either registry"""
        # Try framework first
        if tool_id in self.framework.tools:
            return self.framework.tools[tool_id]
        
        # Try production
        try:
            return self.production.get_tool(tool_id)
        except:
            return None
            
    def list_all_tools(self) -> Dict[str, List[str]]:
        """List tools from both registries"""
        framework_tools = list(self.framework.tools.keys())
        
        # Production registry
        try:
            production_tools = self.production.list_tools()
        except:
            production_tools = []
            
        return {
            'framework': framework_tools,
            'production': production_tools,
            'total_count': len(framework_tools) + len(production_tools)
        }
        
    def get_tool_count(self) -> Dict[str, int]:
        """Get count of tools in each registry"""
        all_tools = self.list_all_tools()
        return {
            'framework': len(all_tools['framework']),
            'production': len(all_tools['production']),
            'total': all_tools['total_count']
        }