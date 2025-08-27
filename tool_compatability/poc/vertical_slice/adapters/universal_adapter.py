#!/usr/bin/env python3
"""
Universal Adapter: Wraps any tool to work with KGAS framework
Handles uncertainty assessment and service integration
"""

import time
import json
import inspect
from typing import Any, Dict, Optional, Callable
from pathlib import Path

class UniversalAdapter:
    """
    Universal wrapper that adapts any tool to the KGAS framework interface
    Provides:
    - Standard process() interface
    - Uncertainty assessment
    - Service integration (Identity, Provenance, Quality)
    - Construct mapping
    """
    
    def __init__(self, 
                 tool: Any, 
                 tool_id: str,
                 method_name: Optional[str] = None,
                 uncertainty_config: Optional[Dict] = None):
        """
        Initialize universal adapter
        
        Args:
            tool: The tool instance to wrap
            tool_id: Unique identifier for the tool
            method_name: Name of method to call (auto-detected if None)
            uncertainty_config: Configuration for uncertainty assessment
        """
        self.tool = tool
        self.tool_id = tool_id
        self.method_name = method_name or self._detect_method()
        self.uncertainty_config = uncertainty_config or self._default_uncertainty()
        
        # Get the actual method
        if not hasattr(self.tool, self.method_name):
            raise ValueError(f"Tool {tool_id} does not have method {self.method_name}")
        
        self.method = getattr(self.tool, self.method_name)
        
    def _detect_method(self) -> str:
        """Auto-detect the main processing method"""
        # Priority order for method names
        priority_methods = ['process', 'run', 'execute', 'transform', 'extract', 'load']
        
        for method_name in priority_methods:
            if hasattr(self.tool, method_name) and callable(getattr(self.tool, method_name)):
                return method_name
        
        # If no standard method found, look for any public method
        methods = [m for m in dir(self.tool) 
                  if not m.startswith('_') and callable(getattr(self.tool, m))]
        
        if methods:
            # Exclude common methods
            excluded = ['__init__', '__str__', '__repr__', '__dict__', '__class__']
            public_methods = [m for m in methods if m not in excluded]
            if public_methods:
                return public_methods[0]  # Take first public method
        
        raise ValueError(f"Could not detect processing method for {self.tool_id}")
    
    def _default_uncertainty(self) -> Dict:
        """Default uncertainty configuration based on tool type"""
        tool_name = self.tool_id.lower()
        
        # Base uncertainties by operation type
        if 'load' in tool_name or 'read' in tool_name:
            return {
                'base': 0.05,
                'reasoning': 'Data loading operation with minimal uncertainty'
            }
        elif 'extract' in tool_name:
            if 'entity' in tool_name or 'relationship' in tool_name:
                return {
                    'base': 0.25,
                    'reasoning': 'Entity/relationship extraction with LLM uncertainty'
                }
            else:
                return {
                    'base': 0.15,
                    'reasoning': 'Information extraction with moderate uncertainty'
                }
        elif 'chunk' in tool_name or 'split' in tool_name:
            return {
                'base': 0.03,
                'reasoning': 'Deterministic text chunking operation'
            }
        elif 'build' in tool_name or 'persist' in tool_name or 'save' in tool_name:
            return {
                'base': 0.0,
                'success_uncertainty': 0.0,
                'reasoning': 'Storage operation - zero uncertainty on success'
            }
        elif 'query' in tool_name or 'search' in tool_name:
            return {
                'base': 0.10,
                'reasoning': 'Query operation with retrieval uncertainty'
            }
        else:
            return {
                'base': 0.10,
                'reasoning': 'Standard processing operation'
            }
    
    def _assess_uncertainty(self, input_data: Any, output_data: Any, success: bool) -> float:
        """
        Assess uncertainty based on operation characteristics
        """
        if not success:
            # FAIL-FAST: Don't assess uncertainty for failures, just fail
            raise RuntimeError(f"Tool {self.tool_id} operation failed - cannot assess uncertainty")
        
        if 'success_uncertainty' in self.uncertainty_config:
            return self.uncertainty_config['success_uncertainty']
        
        base_uncertainty = self.uncertainty_config.get('base', 0.10)
        
        # Adjust based on data characteristics
        adjustments = 0.0
        
        # Input size adjustment
        if hasattr(input_data, '__len__'):
            input_size = len(input_data)
            if input_size > 10000:  # Large input
                adjustments += 0.02
            elif input_size < 100:  # Small input
                adjustments -= 0.01
        
        # Output completeness adjustment
        if isinstance(output_data, dict):
            if 'error' in output_data:
                adjustments += 0.05
            if 'confidence' in output_data:
                # Use tool's own confidence if available
                tool_confidence = output_data.get('confidence', 1.0)
                return 1.0 - tool_confidence
        
        # Cap total uncertainty
        total_uncertainty = base_uncertainty + adjustments
        return min(max(total_uncertainty, 0.0), 1.0)
    
    def _infer_construct_mapping(self, input_data: Any, output_data: Any) -> str:
        """Infer construct mapping from data types"""
        input_construct = self._infer_construct(input_data, 'input')
        output_construct = self._infer_construct(output_data, 'output')
        return f"{input_construct} → {output_construct}"
    
    def _infer_construct(self, data: Any, direction: str) -> str:
        """Infer semantic construct from data"""
        if isinstance(data, str):
            if len(data) < 100:
                return "file_path" if '/' in data or '\\' in data else "short_text"
            else:
                return "character_sequence"
        elif isinstance(data, dict):
            if 'entities' in data and 'relationships' in data:
                return "knowledge_graph"
            elif 'text' in data:
                return "document"
            elif 'embeddings' in data or 'vector' in data:
                return "vector_representation"
            else:
                return "structured_data"
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                if 'entity' in str(data[0]).lower():
                    return "entity_list"
                elif 'chunk' in str(data[0]).lower():
                    return "text_chunks"
                else:
                    return "object_collection"
            else:
                return "item_list"
        elif hasattr(data, '__class__'):
            return data.__class__.__name__.lower()
        else:
            return "data"
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Standard process interface for KGAS framework
        
        Returns:
            Dictionary with:
            - success: bool
            - data: processed output
            - uncertainty: float
            - reasoning: str
            - construct_mapping: str
            - metadata: additional info
        """
        start_time = time.time()
        
        try:
            # Prepare arguments for the method
            sig = inspect.signature(self.method)
            params = sig.parameters
            
            # Handle different parameter styles
            if len(params) == 0:
                # No parameters (shouldn't happen for processing methods)
                result = self.method()
            elif len(params) == 1 and 'self' not in params:
                # Single parameter - pass input directly
                result = self.method(input_data)
            else:
                # Multiple parameters - try to match
                if 'data' in params:
                    result = self.method(data=input_data, **kwargs)
                elif 'input' in params:
                    result = self.method(input=input_data, **kwargs)
                elif 'text' in params and isinstance(input_data, str):
                    result = self.method(text=input_data, **kwargs)
                elif 'file' in params or 'path' in params or 'file_path' in params:
                    # File-based methods
                    param_name = 'file' if 'file' in params else ('path' if 'path' in params else 'file_path')
                    result = self.method(**{param_name: input_data}, **kwargs)
                else:
                    # Try positional
                    result = self.method(input_data, **kwargs)
            
            # Normalize result
            if isinstance(result, dict):
                output_data = result
                success = result.get('success', True)
            else:
                output_data = result
                success = result is not None
            
            # Assess uncertainty
            uncertainty = self._assess_uncertainty(input_data, output_data, success)
            
            # Infer construct mapping
            construct_mapping = self._infer_construct_mapping(input_data, output_data)
            
            # Build response
            response = {
                'success': success,
                'data': output_data,
                'uncertainty': uncertainty,
                'reasoning': self.uncertainty_config.get('reasoning', f'{self.tool_id} processing'),
                'construct_mapping': construct_mapping,
                'metadata': {
                    'tool_id': self.tool_id,
                    'method': self.method_name,
                    'execution_time': time.time() - start_time
                }
            }
            
            # If the tool returned a dict, merge useful fields
            if isinstance(output_data, dict):
                # Preserve tool's uncertainty if it has one
                if 'uncertainty' in output_data:
                    response['uncertainty'] = output_data['uncertainty']
                # Preserve tool's reasoning if it has one
                if 'reasoning' in output_data:
                    response['reasoning'] = output_data['reasoning']
                # Extract actual data if nested
                if 'data' in output_data:
                    response['data'] = output_data['data']
                elif 'result' in output_data:
                    response['data'] = output_data['result']
                elif 'output' in output_data:
                    response['data'] = output_data['output']
            
            return response
            
        except Exception as e:
            # FAIL-FAST: Surface errors immediately
            print(f"❌ ERROR in {self.tool_id}.{self.method_name}: {str(e)}")
            print(f"   Input type: {type(input_data)}")
            print(f"   Input data (first 200 chars): {str(input_data)[:200]}")
            raise RuntimeError(
                f"Tool {self.tool_id} failed with {e.__class__.__name__}: {str(e)}\n"
                f"Method: {self.method_name}\n"
                f"Input type: {type(input_data)}"
            ) from e
    
    def __repr__(self):
        return f"UniversalAdapter({self.tool_id}, method={self.method_name})"


# Factory function for easy creation
def adapt_tool(tool: Any, 
               tool_id: str, 
               method: Optional[str] = None,
               uncertainty: Optional[float] = None,
               reasoning: Optional[str] = None) -> UniversalAdapter:
    """
    Convenience factory for creating adapted tools
    
    Example:
        adapted = adapt_tool(PDFLoader(), "t01_pdf_loader", uncertainty=0.15)
    """
    uncertainty_config = {}
    if uncertainty is not None:
        uncertainty_config['base'] = uncertainty
    if reasoning is not None:
        uncertainty_config['reasoning'] = reasoning
    
    return UniversalAdapter(
        tool=tool,
        tool_id=tool_id,
        method_name=method,
        uncertainty_config=uncertainty_config if uncertainty_config else None
    )


if __name__ == "__main__":
    # Test the universal adapter
    print("=== Testing Universal Adapter ===\n")
    
    # Test with a mock tool
    class MockTool:
        def process(self, text):
            return {
                'entities': [
                    {'id': '1', 'name': 'Test Entity', 'type': 'person'}
                ],
                'relationships': []
            }
    
    # Create adapter
    mock_tool = MockTool()
    adapter = UniversalAdapter(mock_tool, "mock_extractor")
    
    # Test processing
    result = adapter.process("This is test text with entities.")
    
    print(f"Tool ID: {adapter.tool_id}")
    print(f"Method: {adapter.method_name}")
    print(f"Success: {result['success']}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Construct: {result['construct_mapping']}")
    print(f"Data: {result['data']}")
    
    print("\n✅ Universal Adapter test complete")