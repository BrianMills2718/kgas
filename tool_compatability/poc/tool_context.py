"""
Tool Context - Carries primary data and auxiliary inputs through tool chains
PhD Research: Multi-input support for tool composition
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolContext(BaseModel):
    """
    Carries primary data and auxiliary inputs through chain execution.
    
    This solves the multi-input problem by allowing tools to receive:
    - Primary data (the main data flowing through the chain)
    - Tool-specific parameters (ontologies, configs, rules)
    - Shared context (data accessible to all tools)
    - Metadata (execution tracking, progress, etc.)
    """
    
    # Main data flowing through the chain
    primary_data: Any = None
    
    # Tool-specific parameters: {tool_id: {param_name: value}}
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Shared context accessible to all tools
    shared_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_param(self, tool_id: str, param_name: str, default=None) -> Any:
        """
        Get a tool-specific parameter.
        
        Args:
            tool_id: The tool identifier
            param_name: The parameter name
            default: Default value if parameter not found
            
        Returns:
            The parameter value or default
        """
        tool_params = self.parameters.get(tool_id, {})
        return tool_params.get(param_name, default)
    
    def set_param(self, tool_id: str, param_name: str, value: Any) -> None:
        """
        Set a tool-specific parameter.
        
        Args:
            tool_id: The tool identifier
            param_name: The parameter name
            value: The parameter value
        """
        if tool_id not in self.parameters:
            self.parameters[tool_id] = {}
        self.parameters[tool_id][param_name] = value
    
    def has_param(self, tool_id: str, param_name: str) -> bool:
        """Check if a parameter exists for a tool."""
        return tool_id in self.parameters and param_name in self.parameters[tool_id]
    
    def get_all_params(self, tool_id: str) -> Dict[str, Any]:
        """Get all parameters for a specific tool."""
        return self.parameters.get(tool_id, {})
    
    def set_shared(self, key: str, value: Any) -> None:
        """Set a value in shared context."""
        self.shared_context[key] = value
    
    def get_shared(self, key: str, default=None) -> Any:
        """Get a value from shared context."""
        return self.shared_context.get(key, default)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add execution metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default=None) -> Any:
        """Get execution metadata."""
        return self.metadata.get(key, default)
    
    def clone(self) -> 'ToolContext':
        """Create a deep copy of the context."""
        return ToolContext(
            primary_data=self.primary_data,
            parameters=self.parameters.copy(),
            shared_context=self.shared_context.copy(),
            metadata=self.metadata.copy()
        )
    
    def clear_params(self, tool_id: str = None) -> None:
        """Clear parameters for a specific tool or all tools."""
        if tool_id:
            self.parameters.pop(tool_id, None)
        else:
            self.parameters.clear()
    
    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True  # Allow any type for primary_data