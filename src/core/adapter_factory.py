#!/usr/bin/env python3
"""
Universal Adapter Factory - Wraps any tool for framework compatibility
"""

import inspect
from typing import Any, Dict, Callable, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType


class UniversalAdapter(ExtensibleTool):
    """Adapts any production tool to framework interface"""
    
    def __init__(self, production_tool: Any):
        self.tool = production_tool
        self.tool_id = getattr(production_tool, 'tool_id', 
                               production_tool.__class__.__name__)
        
        # Detect the execution method
        self.execute_method = self._detect_execute_method()
        
    def _detect_execute_method(self) -> Callable:
        """Find the main execution method"""
        # Try common method names
        for method_name in ['execute', 'run', 'process', 'convert', 'transform', 'analyze', '__call__']:
            if hasattr(self.tool, method_name):
                method = getattr(self.tool, method_name)
                if callable(method):
                    return method
        
        # If no standard method found, look for any public method that takes input
        for attr_name in dir(self.tool):
            if not attr_name.startswith('_'):  # Skip private methods
                attr = getattr(self.tool, attr_name)
                if callable(attr) and attr_name not in ['get', 'set', 'validate', 'cleanup', 'initialize']:
                    # Found a potential execution method
                    return attr
        
        raise ValueError(f"No execution method found in {self.tool}")
        
    def get_capabilities(self) -> ToolCapabilities:
        """Generate capabilities from tool inspection"""
        return ToolCapabilities(
            tool_id=self.tool_id,
            name=getattr(self.tool, 'name', self.tool_id),
            description=getattr(self.tool, '__doc__', 'Adapted tool'),
            input_type=self._detect_input_type(),
            output_type=self._detect_output_type(),
        )
        
    def _detect_input_type(self) -> DataType:
        """Detect input type from tool signature or attributes"""
        # Simple detection - enhance as needed
        if hasattr(self.tool, 'input_type'):
            # If it's already a DataType, use it
            if isinstance(self.tool.input_type, DataType):
                return self.tool.input_type
            # Try to map string to DataType
            try:
                return DataType(self.tool.input_type.lower())
            except:
                pass
        return DataType.TEXT  # Safe fallback
        
    def _detect_output_type(self) -> DataType:
        """Detect output type from tool"""
        if hasattr(self.tool, 'output_type'):
            if isinstance(self.tool.output_type, DataType):
                return self.tool.output_type
            try:
                return DataType(self.tool.output_type.lower())
            except:
                pass
        return DataType.TEXT  # Safe fallback
        
    def process(self, input_data: Any, context=None) -> ToolResult:
        """Execute the tool with framework interface"""
        try:
            # Call the detected method
            result = self.execute_method(input_data)
            
            # Wrap result in ToolResult
            if isinstance(result, ToolResult):
                return result
            else:
                return ToolResult(success=True, data=result)
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class UniversalAdapterFactory:
    """Factory for creating adapters"""
    
    def wrap(self, tool: Any) -> ExtensibleTool:
        """
        Wrap any tool with appropriate adapter
        Returns framework-compatible tool
        """
        # If already framework compatible, return as-is
        if isinstance(tool, ExtensibleTool):
            return tool
            
        # Otherwise wrap with universal adapter
        return UniversalAdapter(tool)
        
    def bulk_wrap(self, tools: List[Any]) -> List[ExtensibleTool]:
        """Wrap multiple tools"""
        return [self.wrap(tool) for tool in tools]