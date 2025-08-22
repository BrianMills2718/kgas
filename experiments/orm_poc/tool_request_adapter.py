"""
Adapter to handle interface mismatches between ORM wrapper and real tools.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


@dataclass
class EnhancedToolRequest:
    """Extended ToolRequest with additional attributes some tools expect."""
    input_data: Any
    validation_mode: bool = False  # T23C expects this
    operation: str = "extract"  # T23C expects this (line 334)
    theory_schema: Optional[Any] = None
    concept_library: Optional[Any] = None
    options: Dict[str, Any] = field(default_factory=dict)
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


class ToolInterfaceAdapter:
    """Adapts between ORM wrapper dict interface and tool-specific interfaces."""
    
    def __init__(self, tool, tool_type: str = "standard"):
        """
        Initialize adapter for a specific tool.
        
        Args:
            tool: The actual tool instance
            tool_type: Type of tool interface ("standard", "t23c", "t03")
        """
        self.tool = tool
        self.tool_type = tool_type
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool with proper interface adaptation.
        
        Args:
            data: Simple dict input from ORM wrapper
            
        Returns:
            Dict with tool output
        """
        if self.tool_type == "t23c":
            return self._execute_t23c(data)
        elif self.tool_type == "t03":
            return self._execute_t03(data)
        else:
            return self._execute_standard(data)
    
    def _execute_t23c(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute T23C with its specific interface requirements."""
        # T23C expects validation_mode and operation attributes
        request = EnhancedToolRequest(
            input_data=data,
            validation_mode=False,  # Default to False
            operation="extract"  # Default operation
        )
        
        try:
            result = self.tool.execute(request)
            
            # Extract data from ToolResult
            if hasattr(result, 'data'):
                return result.data
            elif hasattr(result, 'success') and result.success:
                # Some tools return different result structures
                return {
                    "entities": getattr(result, 'entities', []),
                    "relationships": getattr(result, 'relationships', []),
                    "metadata": getattr(result, 'metadata', {})
                }
            else:
                return {"error": str(result)}
                
        except Exception as e:
            return {"error": f"T23C execution failed: {e}"}
    
    def _execute_t03(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute T03 with standard ToolRequest."""
        from src.core.tool_contract import ToolRequest
        
        request = ToolRequest(input_data=data)
        
        try:
            result = self.tool.execute(request)
            
            if hasattr(result, 'data'):
                return result.data
            elif hasattr(result, 'content'):
                return {"content": result.content}
            else:
                return {"content": str(result)}
                
        except Exception as e:
            return {"error": f"T03 execution failed: {e}"}
    
    def _execute_standard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with standard ToolRequest interface."""
        from src.core.tool_contract import ToolRequest
        
        request = ToolRequest(input_data=data)
        
        try:
            result = self.tool.execute(request)
            
            if hasattr(result, 'data'):
                return result.data
            else:
                return {"result": result}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}


def create_adapted_tool(tool_class, service_manager, tool_type: str):
    """
    Create a tool instance with proper adapter.
    
    Args:
        tool_class: The tool class to instantiate
        service_manager: ServiceManager instance
        tool_type: Type of tool interface
        
    Returns:
        ToolInterfaceAdapter wrapping the tool
    """
    tool_instance = tool_class(service_manager)
    return ToolInterfaceAdapter(tool_instance, tool_type)