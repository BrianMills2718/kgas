#!/usr/bin/env python3
"""
Tool Converter - Convert existing KGAS tools to type-based system
PhD Research: Rapid tool library expansion
"""

import sys
from pathlib import Path
from typing import Any, Optional, Type
import inspect

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.base_tool import BaseTool
from poc.data_types import DataType, DataSchema

class ToolConverter:
    """Convert existing tools to type-based system"""
    
    def __init__(self):
        self.converted_tools = []
    
    def analyze_tool(self, tool_class: Type) -> Dict[str, Any]:
        """Analyze an existing tool to determine its types"""
        
        analysis = {
            "class_name": tool_class.__name__,
            "methods": [],
            "likely_input": None,
            "likely_output": None,
            "conversion_difficulty": "unknown"
        }
        
        # Check for execute/process methods
        for method_name in ["execute", "process", "run", "__call__"]:
            if hasattr(tool_class, method_name):
                method = getattr(tool_class, method_name)
                sig = inspect.signature(method)
                
                analysis["methods"].append({
                    "name": method_name,
                    "params": list(sig.parameters.keys()),
                    "return_annotation": sig.return_annotation
                })
        
        # Guess types based on class name
        name_lower = tool_class.__name__.lower()
        
        if "loader" in name_lower or "reader" in name_lower:
            analysis["likely_input"] = DataType.FILE
            analysis["likely_output"] = DataType.TEXT
        elif "extract" in name_lower:
            analysis["likely_input"] = DataType.TEXT
            analysis["likely_output"] = DataType.ENTITIES
        elif "graph" in name_lower or "neo4j" in name_lower:
            analysis["likely_input"] = DataType.ENTITIES
            analysis["likely_output"] = DataType.GRAPH
        elif "embed" in name_lower or "vector" in name_lower:
            analysis["likely_input"] = DataType.TEXT
            analysis["likely_output"] = DataType.VECTORS
        
        # Estimate conversion difficulty
        if analysis["methods"]:
            if len(analysis["methods"][0]["params"]) <= 2:
                analysis["conversion_difficulty"] = "easy"
            else:
                analysis["conversion_difficulty"] = "moderate"
        else:
            analysis["conversion_difficulty"] = "hard"
        
        return analysis
    
    def create_wrapper(
        self,
        original_tool: Type,
        input_type: DataType,
        output_type: DataType,
        input_schema: Type[BaseModel],
        output_schema: Type[BaseModel]
    ) -> Type[BaseTool]:
        """Create a wrapper for an existing tool"""
        
        class WrappedTool(BaseTool[input_schema, output_schema, BaseModel]):
            """Auto-generated wrapper for existing tool"""
            
            def __init__(self):
                super().__init__()
                self.original = original_tool()
                self.tool_id = f"Wrapped_{original_tool.__name__}"
            
            @property
            def input_type(self) -> DataType:
                return input_type
            
            @property
            def output_type(self) -> DataType:
                return output_type
            
            @property
            def input_schema(self) -> Type[BaseModel]:
                return input_schema
            
            @property
            def output_schema(self) -> Type[BaseModel]:
                return output_schema
            
            def _execute(self, input_data: input_schema) -> output_schema:
                """Execute the wrapped tool"""
                
                # Convert input to format expected by original tool
                if hasattr(self.original, 'execute'):
                    # Adapt input format
                    original_input = self._adapt_input(input_data)
                    result = self.original.execute(original_input)
                elif hasattr(self.original, 'process'):
                    original_input = self._adapt_input(input_data)
                    result = self.original.process(original_input)
                else:
                    raise NotImplementedError("Original tool has no execute/process method")
                
                # Convert output to our schema
                return self._adapt_output(result)
            
            def _adapt_input(self, input_data: input_schema) -> Any:
                """Adapt our schema to original tool's expected input"""
                
                # This is where we handle the impedance mismatch
                if hasattr(input_data, 'content'):
                    return {"text": input_data.content}
                elif hasattr(input_data, 'path'):
                    return {"file_path": input_data.path}
                else:
                    return input_data.__dict__
            
            def _adapt_output(self, original_output: Any) -> output_schema:
                """Adapt original tool's output to our schema"""
                
                # Map fields from original to our schema
                if output_type == DataType.ENTITIES:
                    # Convert whatever format to our EntitiesData
                    entities = []
                    
                    if isinstance(original_output, dict):
                        if "entities" in original_output:
                            for e in original_output["entities"]:
                                entities.append(DataSchema.Entity(
                                    id=e.get("id", f"e_{len(entities)}"),
                                    text=e.get("text", e.get("name", "")),
                                    type=e.get("type", "UNKNOWN"),
                                    confidence=e.get("confidence", 0.5)
                                ))
                    
                    return DataSchema.EntitiesData(
                        entities=entities,
                        relationships=[],
                        source_checksum="",
                        extraction_model=original_tool.__name__,
                        extraction_timestamp=""
                    )
                
                elif output_type == DataType.TEXT:
                    content = ""
                    if isinstance(original_output, str):
                        content = original_output
                    elif isinstance(original_output, dict):
                        content = original_output.get("text", 
                                   original_output.get("content", str(original_output)))
                    
                    return DataSchema.TextData.from_string(content)
                
                else:
                    raise NotImplementedError(f"Output adaptation for {output_type} not implemented")
        
        # Set proper name for debugging
        WrappedTool.__name__ = f"Wrapped_{original_tool.__name__}"
        
        return WrappedTool
    
    def convert_batch(self, tool_classes: List[Type]) -> List[Type[BaseTool]]:
        """Convert multiple tools at once"""
        
        converted = []
        
        for tool_class in tool_classes:
            print(f"\nAnalyzing {tool_class.__name__}...")
            analysis = self.analyze_tool(tool_class)
            
            print(f"  Likely: {analysis['likely_input']} → {analysis['likely_output']}")
            print(f"  Difficulty: {analysis['conversion_difficulty']}")
            
            if analysis['likely_input'] and analysis['likely_output']:
                # Determine schemas based on types
                input_schema = self._get_schema_for_type(analysis['likely_input'])
                output_schema = self._get_schema_for_type(analysis['likely_output'])
                
                wrapped = self.create_wrapper(
                    tool_class,
                    analysis['likely_input'],
                    analysis['likely_output'],
                    input_schema,
                    output_schema
                )
                
                converted.append(wrapped)
                print(f"  ✅ Converted successfully")
            else:
                print(f"  ❌ Could not determine types")
        
        return converted
    
    def _get_schema_for_type(self, data_type: DataType) -> Type[BaseModel]:
        """Get the schema class for a data type"""
        
        mapping = {
            DataType.FILE: DataSchema.FileData,
            DataType.TEXT: DataSchema.TextData,
            DataType.ENTITIES: DataSchema.EntitiesData,
            DataType.GRAPH: DataSchema.GraphData,
            # Add more as needed
        }
        
        return mapping.get(data_type, BaseModel)


def demo_conversion():
    """Demonstrate tool conversion"""
    
    # Mock some existing tools
    class T01_PDFLoader:
        def execute(self, file_path: str) -> dict:
            return {"text": f"Content from {file_path}"}
    
    class T23C_EntityExtractor:
        def process(self, data: dict) -> dict:
            return {
                "entities": [
                    {"text": "John", "type": "PERSON", "confidence": 0.9},
                    {"text": "Apple", "type": "ORG", "confidence": 0.8}
                ]
            }
    
    class T31_GraphBuilder:
        def execute(self, entities: dict) -> dict:
            return {"graph_id": "graph_123", "nodes": 2}
    
    # Convert them
    converter = ToolConverter()
    
    print("="*60)
    print("TOOL CONVERSION DEMO")
    print("="*60)
    
    tools_to_convert = [T01_PDFLoader, T23C_EntityExtractor, T31_GraphBuilder]
    wrapped_tools = converter.convert_batch(tools_to_convert)
    
    print(f"\n✅ Converted {len(wrapped_tools)} tools")
    
    # Test the wrapped tools
    if wrapped_tools:
        print("\nTesting wrapped tools...")
        
        from poc.registry import ToolRegistry
        registry = ToolRegistry()
        
        for wrapped_class in wrapped_tools:
            tool = wrapped_class()
            registry.register(tool)
            print(f"  Registered: {tool.tool_id}")
        
        # Check what chains we can build
        print("\nDiscovered chains:")
        chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
        for chain in chains:
            print(f"  {' → '.join(chain)}")


if __name__ == "__main__":
    demo_conversion()