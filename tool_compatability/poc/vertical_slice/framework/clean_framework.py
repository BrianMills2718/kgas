#!/usr/bin/env python3
"""
Clean Tool Framework with Uncertainty Propagation
Physics-style error propagation for sequential tools
"""

import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from neo4j import GraphDatabase

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.identity_service_v3 import IdentityServiceV3
from services.provenance_enhanced import ProvenanceEnhanced
from services.crossmodal_service import CrossModalService

class DataType(Enum):
    """Data types that tools can process"""
    FILE = "file"
    TEXT = "text"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    NEO4J_GRAPH = "neo4j_graph"
    TABLE = "table"
    VECTOR = "vector"

@dataclass
class ToolCapabilities:
    """Tool capabilities declaration"""
    tool_id: str
    input_type: DataType
    output_type: DataType
    input_construct: str
    output_construct: str
    transformation_type: str

@dataclass
class ChainResult:
    """Result of executing a tool chain"""
    success: bool
    data: Any
    total_uncertainty: float
    step_uncertainties: List[float]
    step_reasonings: List[str]
    error: Optional[str] = None

class CleanToolFramework:
    """Framework for tool composition with uncertainty propagation"""
    
    def __init__(self, neo4j_uri: str, sqlite_path: str):
        """Initialize framework with real database connections"""
        # Real database connections
        self.neo4j = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "devpassword"))
        self.sqlite_path = sqlite_path
        
        # Initialize services
        self.identity = IdentityServiceV3(self.neo4j)
        self.provenance = ProvenanceEnhanced(sqlite_path)
        self.crossmodal = CrossModalService(self.neo4j, sqlite_path)
        
        # Tool registry
        self.tools = {}
        self.capabilities = {}
    
    def register_tool(self, tool, capabilities: ToolCapabilities):
        """Register a tool with its capabilities"""
        self.tools[capabilities.tool_id] = tool
        self.capabilities[capabilities.tool_id] = capabilities
        print(f"✅ Registered tool: {capabilities.tool_id} ({capabilities.input_type.value} → {capabilities.output_type.value})")
    
    def find_chain(self, input_type: DataType, output_type: DataType) -> Optional[List[str]]:
        """
        Find a chain of tools that transforms input_type to output_type
        Simple implementation for MVP - can be enhanced with graph search later
        """
        # For MVP, we'll hardcode the known chain
        if input_type == DataType.FILE and output_type == DataType.NEO4J_GRAPH:
            # Check if we have the required tools
            required = ["TextLoaderV3", "KnowledgeGraphExtractor", "GraphPersister"]
            if all(tool_id in self.tools for tool_id in required):
                return required
        
        # Direct transformation
        for tool_id, cap in self.capabilities.items():
            if cap.input_type == input_type and cap.output_type == output_type:
                return [tool_id]
        
        # TODO: Implement proper chain discovery with BFS/DFS
        return None
    
    def execute_chain(self, chain: List[str], input_data: Any) -> ChainResult:
        """
        Execute tool chain with uncertainty propagation
        """
        uncertainties = []
        reasonings = []
        construct_mappings = []
        current_data = input_data
        
        for tool_id in chain:
            if tool_id not in self.tools:
                return ChainResult(
                    success=False,
                    data=None,
                    total_uncertainty=1.0,
                    step_uncertainties=[],
                    step_reasonings=[],
                    error=f"Tool {tool_id} not registered"
                )
            
            tool = self.tools[tool_id]
            cap = self.capabilities[tool_id]
            
            print(f"\nExecuting {tool_id}: {cap.input_construct} → {cap.output_construct}")
            
            # Execute tool
            try:
                result = tool.process(current_data)
                
                if not result.get('success', False):
                    return ChainResult(
                        success=False,
                        data=None,
                        total_uncertainty=1.0,
                        step_uncertainties=uncertainties,
                        step_reasonings=reasonings,
                        error=f"{tool_id} failed: {result.get('error', 'Unknown error')}"
                    )
                
                # Track uncertainty and reasoning
                uncertainties.append(result.get('uncertainty', 0.5))
                reasonings.append(result.get('reasoning', 'No reasoning provided'))
                construct_mappings.append(result.get('construct_mapping', f"{cap.input_construct} → {cap.output_construct}"))
                
                # Track in provenance
                self.provenance.track_operation(
                    tool_id=tool_id,
                    operation=cap.transformation_type,
                    inputs={'data_type': cap.input_type.value},
                    outputs={'data_type': cap.output_type.value},
                    uncertainty=result.get('uncertainty', 0.5),
                    reasoning=result.get('reasoning', ''),
                    construct_mapping=result.get('construct_mapping', '')
                )
                
                # Propagate data based on tool output
                if tool_id == "TextLoaderV3":
                    current_data = result.get('text')
                elif tool_id == "KnowledgeGraphExtractor":
                    current_data = {
                        'entities': result.get('entities', []),
                        'relationships': result.get('relationships', [])
                    }
                elif tool_id == "GraphPersister":
                    current_data = result
                else:
                    current_data = result.get('data', result)
                    
            except Exception as e:
                return ChainResult(
                    success=False,
                    data=None,
                    total_uncertainty=1.0,
                    step_uncertainties=uncertainties,
                    step_reasonings=reasonings,
                    error=f"{tool_id} raised exception: {str(e)}"
                )
        
        # Combine uncertainties using physics model
        total_uncertainty = self._combine_sequential_uncertainties(uncertainties)
        
        print(f"\n=== Chain Execution Complete ===")
        print(f"Steps: {' → '.join(chain)}")
        print(f"Construct mappings: {' → '.join(construct_mappings)}")
        print(f"Uncertainties: {uncertainties}")
        print(f"Total uncertainty: {total_uncertainty:.3f}")
        
        return ChainResult(
            success=True,
            data=current_data,
            total_uncertainty=total_uncertainty,
            step_uncertainties=uncertainties,
            step_reasonings=reasonings
        )
    
    def _combine_sequential_uncertainties(self, uncertainties: List[float]) -> float:
        """
        Physics-style error propagation for sequential tools
        confidence = ∏(1 - uᵢ)
        total_uncertainty = 1 - confidence
        """
        confidence = 1.0
        for u in uncertainties:
            confidence *= (1 - u)
        return 1 - confidence
    
    def cleanup(self):
        """Clean up database connections"""
        self.neo4j.close()

# Test the framework
if __name__ == "__main__":
    print("=== Testing Clean Framework ===")
    
    # Initialize framework
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="vertical_slice.db"
    )
    
    # Import tools
    from tools.text_loader_v3 import TextLoaderV3
    from tools.graph_persister import GraphPersister
    
    # Create tool instances
    text_loader = TextLoaderV3()
    
    # Create a mock KG extractor for testing without API key
    class MockKGExtractor:
        def __init__(self):
            self.tool_id = "KnowledgeGraphExtractor"
        
        def process(self, text):
            return {
                'success': True,
                'entities': [
                    {'id': '1', 'name': 'Test Entity', 'type': 'person'},
                    {'id': '2', 'name': 'Test Org', 'type': 'organization'}
                ],
                'relationships': [
                    {'source': '1', 'target': '2', 'type': 'WORKS_AT'}
                ],
                'uncertainty': 0.25,
                'reasoning': 'Mock extraction for framework testing',
                'construct_mapping': 'character_sequence → knowledge_graph'
            }
    
    kg_extractor = MockKGExtractor()
    graph_persister = GraphPersister(framework.neo4j, framework.identity, framework.crossmodal)
    
    # Register tools
    framework.register_tool(text_loader, ToolCapabilities(
        tool_id="TextLoaderV3",
        input_type=DataType.FILE,
        output_type=DataType.TEXT,
        input_construct="file_path",
        output_construct="character_sequence",
        transformation_type="text_extraction"
    ))
    
    framework.register_tool(kg_extractor, ToolCapabilities(
        tool_id="KnowledgeGraphExtractor",
        input_type=DataType.TEXT,
        output_type=DataType.KNOWLEDGE_GRAPH,
        input_construct="character_sequence",
        output_construct="knowledge_graph",
        transformation_type="knowledge_graph_extraction"
    ))
    
    framework.register_tool(graph_persister, ToolCapabilities(
        tool_id="GraphPersister",
        input_type=DataType.KNOWLEDGE_GRAPH,
        output_type=DataType.NEO4J_GRAPH,
        input_construct="knowledge_graph",
        output_construct="persisted_graph",
        transformation_type="graph_persistence"
    ))
    
    # Find chain
    chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    if chain:
        print(f"\n✅ Found chain: {' → '.join(chain)}")
    else:
        print("\n❌ No chain found")
    
    framework.cleanup()