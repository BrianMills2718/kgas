#!/usr/bin/env python3
"""
Clean Tool Framework with Document Tracking
Passes metadata through the entire pipeline for proper isolation
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from neo4j import GraphDatabase

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
from tools.graph_persister_v2 import GraphPersisterV2
from services.identity_service_v3 import IdentityServiceV3
from services.crossmodal_service import CrossModalService
from services.provenance_enhanced import ProvenanceEnhanced

class CleanToolFrameworkV2:
    """
    Tool orchestration framework with document tracking.
    Ensures proper isolation of documents in Neo4j.
    """
    
    def __init__(self, neo4j_uri: str, sqlite_path: str):
        # Initialize database connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri, 
            auth=("neo4j", "devpassword")
        )
        self.sqlite_path = sqlite_path
        
        # Initialize services
        self.identity_service = IdentityServiceV3(self.neo4j_driver)
        self.crossmodal_service = CrossModalService(self.neo4j_driver, sqlite_path)
        self.provenance_service = ProvenanceEnhanced(sqlite_path)
        
        # Initialize tools
        self.tools = {
            'TextLoaderV3': TextLoaderV3(),
            'KnowledgeGraphExtractor': KnowledgeGraphExtractor(),
            'GraphPersisterV2': GraphPersisterV2(
                self.neo4j_driver, 
                self.identity_service, 
                self.crossmodal_service
            )
        }
        
        # Define construct mappings
        self.construct_mappings = {
            'TextLoaderV3': ('file_path', 'character_sequence'),
            'KnowledgeGraphExtractor': ('character_sequence', 'knowledge_graph'),
            'GraphPersisterV2': ('knowledge_graph', 'persisted_graph')
        }
        
        print(f"✅ Framework initialized with {len(self.tools)} tools and document tracking")
    
    def execute_chain_with_metadata(self, 
                                   input_data: Any, 
                                   metadata: Optional[Dict] = None) -> Dict:
        """
        Execute tool chain with metadata passed through
        
        Args:
            input_data: Initial input (e.g., file path)
            metadata: Document metadata including document_id
            
        Returns:
            Dict with results, uncertainties, and document tracking
        """
        # Generate document_id if not provided
        if metadata is None:
            metadata = {}
        
        if 'document_id' not in metadata:
            if isinstance(input_data, str) and Path(input_data).exists():
                metadata['document_id'] = Path(input_data).stem
                metadata['source_file'] = input_data
            else:
                import uuid
                metadata['document_id'] = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Determine chain based on input
        if isinstance(input_data, str) and Path(input_data).exists():
            chain = ['TextLoaderV3', 'KnowledgeGraphExtractor', 'GraphPersisterV2']
        else:
            return {'error': 'Invalid input type'}
        
        # Execute chain with metadata
        current_data = input_data
        uncertainties = []
        steps = []
        
        for tool_name in chain:
            tool = self.tools[tool_name]
            print(f"\nExecuting {tool_name}: {self.construct_mappings[tool_name][0]} → {self.construct_mappings[tool_name][1]}")
            
            try:
                # Special handling for GraphPersisterV2 to pass metadata
                if tool_name == 'GraphPersisterV2':
                    result = tool.process(current_data, metadata)
                else:
                    result = tool.process(current_data)
                
                if result.get('success', True):
                    # Track uncertainty
                    uncertainty = result.get('uncertainty', 0.0)
                    uncertainties.append(uncertainty)
                    
                    # Track provenance
                    operation_id = self.provenance_service.track_operation(
                        tool_id=tool_name,
                        operation='process',
                        inputs={'data_type': type(current_data).__name__},
                        outputs={'success': True, 'uncertainty': uncertainty},
                        uncertainty=uncertainty,
                        reasoning=result.get('reasoning', ''),
                        construct_mapping=result.get('construct_mapping', '')
                    )
                    
                    steps.append({
                        'tool': tool_name,
                        'uncertainty': uncertainty,
                        'operation_id': operation_id
                    })
                    
                    # Prepare data for next tool
                    if tool_name == 'TextLoaderV3':
                        current_data = result.get('text', '')
                    elif tool_name == 'KnowledgeGraphExtractor':
                        current_data = {
                            'entities': result.get('entities', []),
                            'relationships': result.get('relationships', [])
                        }
                    elif tool_name == 'GraphPersisterV2':
                        # Final step - return full result
                        pass
                    
                else:
                    return {
                        'success': False,
                        'error': f"Tool {tool_name} failed",
                        'details': result
                    }
                    
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Tool {tool_name} raised exception",
                    'exception': str(e)
                }
        
        # Calculate combined uncertainty
        confidence = 1.0
        for u in uncertainties:
            confidence *= (1 - u)
        total_uncertainty = 1 - confidence
        
        return {
            'success': True,
            'document_id': metadata['document_id'],
            'steps': steps,
            'uncertainties': uncertainties,
            'total_uncertainty': total_uncertainty,
            'final_output': current_data,
            'provenance_chain': self.provenance_service.get_operation_chain(steps[-1]['operation_id'])
        }
    
    def get_document_results(self, document_id: str) -> Dict:
        """Retrieve all results for a specific document"""
        persister = self.tools['GraphPersisterV2']
        return persister.get_document_graph(document_id)
    
    def cleanup_document(self, document_id: str):
        """Clean up a specific document from Neo4j"""
        persister = self.tools['GraphPersisterV2']
        persister.cleanup_document(document_id)

# Test the framework
if __name__ == "__main__":
    framework = CleanToolFrameworkV2('bolt://localhost:7687', 'vertical_slice.db')
    
    # Create test file
    test_file = Path('test_doc.txt')
    test_file.write_text("""
    Brian Chhun is a PhD student at the University of Melbourne.
    He developed the KGAS system for knowledge graph analysis.
    """)
    
    # Execute with metadata
    metadata = {'document_id': 'test_001', 'source': 'test'}
    result = framework.execute_chain_with_metadata(str(test_file), metadata)
    
    if result['success']:
        print(f"\n✅ Pipeline executed successfully")
        print(f"Document ID: {result['document_id']}")
        print(f"Total uncertainty: {result['total_uncertainty']:.3f}")
        
        # Check what was stored
        graph = framework.get_document_results('test_001')
        print(f"\nStored in Neo4j:")
        print(f"  Entities: {len(graph['entities'])}")
        print(f"  Relationships: {len(graph['relationships'])}")
        
        # Cleanup
        framework.cleanup_document('test_001')
    
    # Cleanup
    test_file.unlink()