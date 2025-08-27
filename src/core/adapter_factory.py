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
    
    def __init__(self, production_tool: Any, service_bridge=None, strict_mode=True):
        """
        Args:
            production_tool: The tool to adapt
            service_bridge: Optional bridge for service integration
            strict_mode: If True, fail entire operation on tracking failure
        """
        self.tool = production_tool
        self.tool_id = getattr(production_tool, 'tool_id', 
                               production_tool.__class__.__name__)
        self.service_bridge = service_bridge  # Add service bridge
        self.strict_mode = strict_mode  # Default to strict!
        
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
        # If tool has its own get_capabilities, use it
        if hasattr(self.tool, 'get_capabilities'):
            return self.tool.get_capabilities()
        
        # Otherwise generate capabilities
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
            try:
                # Get the actual value (works for both attributes and properties)
                input_type_value = getattr(self.tool, 'input_type')
                
                # Properties appear as their values when accessed via getattr
                # If it's still a method, call it
                if callable(input_type_value):
                    input_type_value = input_type_value()
                
                # If it's already a DataType, use it
                if isinstance(input_type_value, DataType):
                    return input_type_value
                    
                # Try to map string to DataType
                # Handle both "FILE" and "DataType.FILE" formats
                type_str = str(input_type_value)
                if 'DataType.' in type_str:
                    type_str = type_str.split('.')[-1]
                return DataType(type_str.lower())
            except Exception as e:
                pass  # Silent fallback
                
        # Check for type hints in the execute method
        try:
            sig = inspect.signature(self.execute_method)
            params = list(sig.parameters.values())
            if params and params[0].annotation != inspect.Parameter.empty:
                # Try to infer from type hints
                annotation = params[0].annotation
                if 'File' in str(annotation):
                    return DataType.FILE
                elif 'Entities' in str(annotation):
                    return DataType.ENTITIES
        except:
            pass
            
        return DataType.TEXT  # Safe fallback
        
    def _detect_output_type(self) -> DataType:
        """Detect output type from tool"""
        if hasattr(self.tool, 'output_type'):
            try:
                # Get the actual value (works for both attributes and properties)
                output_type_value = getattr(self.tool, 'output_type')
                
                # Properties appear as their values when accessed via getattr
                # If it's still a method, call it
                if callable(output_type_value):
                    output_type_value = output_type_value()
                
                # If it's already a DataType, use it
                if isinstance(output_type_value, DataType):
                    return output_type_value
                    
                # Try to map string to DataType
                # Handle both "ENTITIES" and "DataType.ENTITIES" formats
                type_str = str(output_type_value)
                if 'DataType.' in type_str:
                    type_str = type_str.split('.')[-1]
                return DataType(type_str.lower())
            except Exception as e:
                pass  # Silent fallback
        
        return DataType.TEXT  # Safe fallback
        
    def process(self, input_data: Any, context=None) -> ToolResult:
        """Execute tool and ensure uncertainty is added"""
        try:
            # Track execution start with provenance
            if self.service_bridge:
                self.service_bridge.track_execution(
                    self.tool_id, 
                    input_data, 
                    None  # Output not yet known
                )
            
            # Get input uncertainty if it exists
            input_uncertainty = 0.0
            if hasattr(input_data, 'uncertainty'):
                input_uncertainty = input_data.uncertainty
            elif isinstance(input_data, dict) and 'uncertainty' in input_data:
                input_uncertainty = input_data['uncertainty']
            
            # Call the tool
            # For ExtensibleTool, call process with context
            if hasattr(self.tool, 'process') and hasattr(self.tool, 'get_capabilities'):
                result = self.tool.process(input_data, context)
            else:
                result = self.execute_method(input_data)
            
            # Ensure result is a ToolResult
            if not isinstance(result, ToolResult):
                result = ToolResult(success=True, data=result)
            
            # Ensure uncertainty is present
            if not hasattr(result, 'uncertainty') or result.uncertainty == 0.0:
                # Add default uncertainty
                result.uncertainty = 0.1  # Default: slightly uncertain
                result.reasoning = "Default uncertainty - tool provided no assessment"
            
            # Simple propagation: increase uncertainty slightly at each step
            if input_uncertainty > 0:
                result.uncertainty = min(1.0, result.uncertainty + (input_uncertainty * 0.1))
                result.reasoning += f" (propagated from input: {input_uncertainty:.2f})"
            
            # Track execution complete with provenance
            if self.service_bridge:
                trace = self.service_bridge.track_execution(
                    self.tool_id,
                    input_data,
                    result
                )
                result.provenance = trace
                
                # Track entities if found
                if isinstance(result.data, dict) and 'entities' in result.data:
                    tracking_failures = []
                    
                    for i, entity in enumerate(result.data['entities']):
                        if isinstance(entity, dict):
                            try:
                                entity_id = self.service_bridge.track_entity(
                                    surface_form=entity.get('text', entity.get('name', '')),
                                    entity_type=entity.get('type', 'UNKNOWN'),
                                    confidence=entity.get('confidence', 0.5),
                                    source_tool=self.tool_id
                                )
                                entity['entity_id'] = entity_id
                            except Exception as e:
                                # Capture failure details
                                tracking_failures.append({
                                    'index': i,
                                    'entity': entity.get('text', 'unknown'),
                                    'error': str(e)
                                })
                    
                    # Handle failures based on mode
                    if tracking_failures:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Failed to track {len(tracking_failures)} entities: {tracking_failures}")
                        
                        if self.strict_mode:
                            # FAIL LOUDLY
                            return ToolResult(
                                success=False,
                                data=None,
                                error=f"Entity tracking failed for {len(tracking_failures)} entities: {tracking_failures}",
                                uncertainty=1.0,
                                reasoning="Entity tracking failure - maximum uncertainty"
                            )
                        else:
                            # Add warning but continue
                            result.reasoning += f" (WARNING: {len(tracking_failures)} entities not tracked)"
                            result.uncertainty = min(1.0, result.uncertainty + 0.2)
            
            return result
            
        except Exception as e:
            return ToolResult(
                success=False, 
                data=None,
                error=str(e),
                uncertainty=1.0,  # Failures are maximally uncertain
                reasoning="Error occurred - maximum uncertainty"
            )


class UniversalAdapterFactory:
    """Factory for creating adapters"""
    
    def __init__(self, service_bridge=None, strict_mode=True):
        """
        Initialize factory with optional service bridge
        
        Args:
            service_bridge: Optional bridge for service integration
            strict_mode: Default strict mode for adapters
        """
        self.service_bridge = service_bridge
        self.strict_mode = strict_mode
    
    def wrap(self, tool: Any, strict_mode=None) -> ExtensibleTool:
        """
        Wrap any tool with appropriate adapter
        Returns framework-compatible tool with service bridge
        
        Args:
            tool: Tool to wrap
            strict_mode: Override factory's default strict mode
        """
        # Use provided strict_mode or factory default
        mode = strict_mode if strict_mode is not None else self.strict_mode
        
        # Always wrap with universal adapter to add service bridge
        # Even if tool already implements ExtensibleTool
        return UniversalAdapter(tool, self.service_bridge, strict_mode=mode)
        
    def bulk_wrap(self, tools: List[Any]) -> List[ExtensibleTool]:
        """Wrap multiple tools"""
        return [self.wrap(tool) for tool in tools]