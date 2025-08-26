#!/usr/bin/env python3
"""Integrate existing tools with the framework"""

import sys
import os
from pathlib import Path

# Setup paths
poc_dir = Path(__file__).parent
sys.path.insert(0, str(poc_dir))
sys.path.insert(0, str(poc_dir.parent.parent))

# Import framework components
from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType, DataSchema
from semantic_types import MEDICAL_RECORDS, MEDICAL_ENTITIES, MEDICAL_KNOWLEDGE_GRAPH
from data_references import ProcessingStrategy

# Import tools using absolute path to avoid package issues
os.chdir(poc_dir)
from tools import text_loader, entity_extractor, graph_builder
TextLoader = text_loader.TextLoader
EntityExtractor = entity_extractor.EntityExtractor
GraphBuilder = graph_builder.GraphBuilder

class TextLoaderAdapter(ExtensibleTool):
    """Adapter to make TextLoader work with framework"""
    
    def __init__(self):
        self.tool = TextLoader()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="TextLoader",
            name="Text File Loader",
            description="Load text files into memory",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            semantic_output=MEDICAL_RECORDS,  # For medical pipeline
            max_input_size=10 * 1024 * 1024,  # 10MB
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        try:
            # Use existing TextLoader
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=str(result.error) if hasattr(result, 'error') else "Unknown error")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class EntityExtractorAdapter(ExtensibleTool):
    """Adapter for EntityExtractor with Gemini"""
    
    def __init__(self):
        self.tool = EntityExtractor()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="EntityExtractor",
            name="Medical Entity Extractor",
            description="Extract medical entities using Gemini",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            semantic_input=MEDICAL_RECORDS,
            semantic_output=MEDICAL_ENTITIES,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        # MUST USE REAL GEMINI API - NO MOCKS
        # EntityExtractor should already load API key from .env
        try:
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=str(result.error) if hasattr(result, 'error') else "Unknown error")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class GraphBuilderAdapter(ExtensibleTool):
    """Adapter for GraphBuilder with Neo4j"""
    
    def __init__(self):
        self.tool = GraphBuilder()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphBuilder",
            name="Medical Knowledge Graph Builder",
            description="Build knowledge graph in Neo4j",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH,
            semantic_input=MEDICAL_ENTITIES,
            semantic_output=MEDICAL_KNOWLEDGE_GRAPH,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        # MUST WRITE TO REAL NEO4J - NO MOCKS (or mock if real not available)
        try:
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=str(result.error) if hasattr(result, 'error') else "Unknown error")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

def register_real_tools(framework):
    """Register all real tools with framework"""
    
    print("\n📦 Registering Real Tools:")
    print("-" * 40)
    
    framework.register_tool(TextLoaderAdapter())
    framework.register_tool(EntityExtractorAdapter())
    framework.register_tool(GraphBuilderAdapter())
    
    return framework

if __name__ == "__main__":
    # Test the adapters
    from framework import ToolFramework
    
    print("Testing Framework Integration")
    print("="*60)
    
    framework = ToolFramework()
    register_real_tools(framework)
    
    print("\nRegistered tools:")
    for tool_id, caps in framework.capabilities.items():
        print(f"  - {tool_id}: {caps.input_type} → {caps.output_type}")
    
    print("\n✅ Integration successful")