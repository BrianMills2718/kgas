#!/usr/bin/env python3
"""
Test Tool Loader - Register simple tools for testing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType
import json

class SimpleTextLoader(ExtensibleTool):
    """Simple text file loader for testing"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="SimpleTextLoader",
            name="Simple Text Loader",
            description="Load text files",
            input_type=DataType.FILE,
            output_type=DataType.TEXT
        )
    
    def process(self, input_data, context=None):
        """Load text from file"""
        try:
            # If input is a string path
            if isinstance(input_data, str):
                path = Path(input_data)
                if path.exists():
                    text = path.read_text()
                    return ToolResult(success=True, data={"text": text})
                else:
                    return ToolResult(success=False, error=f"File not found: {input_data}")
            else:
                return ToolResult(success=False, error="Invalid input type")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SimpleEntityExtractor(ExtensibleTool):
    """Simple entity extractor for testing"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="SimpleEntityExtractor",
            name="Simple Entity Extractor",
            description="Extract entities from text",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES
        )
    
    def process(self, input_data, context=None):
        """Extract entities from text"""
        try:
            # Get text from input
            if isinstance(input_data, dict) and 'text' in input_data:
                text = input_data['text']
            elif isinstance(input_data, str):
                text = input_data
            else:
                return ToolResult(success=False, error="Invalid input format")
            
            # Simple entity extraction (mock for testing)
            entities = []
            
            # Look for known entities
            known_entities = [
                ("Tim Cook", "PERSON"),
                ("Apple", "ORGANIZATION"),
                ("Satya Nadella", "PERSON"),
                ("Microsoft", "ORGANIZATION"),
                ("Sundar Pichai", "PERSON"),
                ("Google", "ORGANIZATION"),
            ]
            
            for name, entity_type in known_entities:
                if name.lower() in text.lower():
                    entities.append({
                        "text": name,
                        "type": entity_type,
                        "confidence": 0.85
                    })
            
            result = ToolResult(
                success=True, 
                data={"entities": entities},
                uncertainty=0.15,
                reasoning="Simple pattern matching - moderate uncertainty"
            )
            
            return result
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SimpleGraphBuilder(ExtensibleTool):
    """Simple graph builder for testing"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="SimpleGraphBuilder",
            name="Simple Graph Builder",
            description="Build graph from entities",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH
        )
    
    def process(self, input_data, context=None):
        """Build graph from entities"""
        try:
            # Get entities from input
            if isinstance(input_data, dict) and 'entities' in input_data:
                entities = input_data['entities']
            else:
                return ToolResult(success=False, error="Invalid input format")
            
            # Build simple graph (mock)
            nodes = []
            edges = []
            
            for entity in entities:
                nodes.append({
                    "id": entity.get("text", "").replace(" ", "_"),
                    "label": entity.get("text", ""),
                    "type": entity.get("type", "UNKNOWN")
                })
            
            # Create some relationships
            if len(nodes) > 1:
                for i in range(len(nodes) - 1):
                    if nodes[i]["type"] == "PERSON" and nodes[i+1]["type"] == "ORGANIZATION":
                        edges.append({
                            "from": nodes[i]["id"],
                            "to": nodes[i+1]["id"],
                            "type": "WORKS_FOR"
                        })
            
            return ToolResult(
                success=True,
                data={
                    "graph": {
                        "nodes": nodes,
                        "edges": edges,
                        "node_count": len(nodes),
                        "edge_count": len(edges)
                    }
                },
                uncertainty=0.2,
                reasoning="Graph built from extracted entities"
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))

def register_test_tools(composition_service):
    """Register simple test tools with composition service"""
    
    # Create tools
    tools = [
        SimpleTextLoader(),
        SimpleEntityExtractor(),
        SimpleGraphBuilder(),
    ]
    
    # The register_any_tool method should wrap them with UniversalAdapter
    # which includes the service_bridge for entity tracking
    for tool in tools:
        success = composition_service.register_any_tool(tool)
        if not success:
            print(f"Failed to register {tool.__class__.__name__}")
    
    print(f"Registered {len(tools)} test tools with service bridge")
    return len(tools)