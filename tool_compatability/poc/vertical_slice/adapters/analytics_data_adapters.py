#!/usr/bin/env python3
"""
Analytics Data Adapters - Convert vertical slice data formats to analytics-compatible formats

Converts between vertical slice tool outputs and the data formats expected by analytics components:
- TABLE format: pandas.DataFrame
- GRAPH format: {'nodes': [...], 'edges': [...]}
- VECTOR format: numpy arrays (handled by embedding services)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class VerticalSliceDataAdapter:
    """Convert vertical slice tool outputs to analytics-compatible formats"""
    
    def __init__(self):
        self.supported_conversions = [
            'vertical_slice_to_table',
            'vertical_slice_to_graph', 
            'table_to_vertical_slice',
            'graph_to_vertical_slice'
        ]
        logger.info(f"VerticalSliceDataAdapter initialized with conversions: {self.supported_conversions}")
    
    def vertical_slice_to_table(self, vertical_slice_data: Dict[str, Any], 
                               include_metadata: bool = True) -> pd.DataFrame:
        """Convert vertical slice tool output to pandas DataFrame for analytics TABLE format
        
        Args:
            vertical_slice_data: Output from vertical slice tools (VectorTool, TableTool, GraphTool)
            include_metadata: Whether to include tool metadata in the DataFrame
            
        Returns:
            pandas.DataFrame suitable for analytics CrossModalConverter TABLE format
        """
        try:
            rows = []
            
            # Handle different types of vertical slice data
            if 'text' in vertical_slice_data:
                # Text-based data (from VectorTool output)
                row = {
                    'text': vertical_slice_data['text'],
                    'data_type': 'text',
                    'source_tool': vertical_slice_data.get('source_tool', 'unknown')
                }
                
                # Add embedding if available
                if 'embedding' in vertical_slice_data:
                    embedding = vertical_slice_data['embedding']
                    row['embedding_dim'] = len(embedding) if embedding else 0
                    row['has_embedding'] = bool(embedding)
                    # Store first 5 embedding values for analysis
                    if embedding:
                        for i in range(min(5, len(embedding))):
                            row[f'embed_{i}'] = embedding[i]
                
                rows.append(row)
                
            elif 'entities' in vertical_slice_data and 'relationships' in vertical_slice_data:
                # Graph-based data (from GraphTool output)  
                entities = vertical_slice_data['entities']
                relationships = vertical_slice_data['relationships']
                
                # Create rows for entities
                for entity in entities:
                    row = {
                        'text': entity.get('name', entity.get('label', str(entity))),
                        'data_type': 'entity',
                        'entity_type': entity.get('type', 'unknown'),
                        'entity_id': entity.get('id', ''),
                        'source_tool': 'GraphTool'
                    }
                    rows.append(row)
                
                # Create rows for relationships  
                for rel in relationships:
                    row = {
                        'text': f"{rel.get('source', '')} {rel.get('type', 'relates_to')} {rel.get('target', '')}",
                        'data_type': 'relationship',
                        'relation_type': rel.get('type', 'unknown'),
                        'source_entity': rel.get('source', ''),
                        'target_entity': rel.get('target', ''),
                        'source_tool': 'GraphTool'
                    }
                    rows.append(row)
            
            elif 'row_id' in vertical_slice_data:
                # Database storage data (from TableTool output)
                row = {
                    'text': f"Stored data with ID {vertical_slice_data['row_id']}",
                    'data_type': 'stored_data',
                    'storage_id': vertical_slice_data['row_id'],
                    'source_tool': 'TableTool'
                }
                rows.append(row)
            
            else:
                # Generic data - convert to text representation
                row = {
                    'text': str(vertical_slice_data),
                    'data_type': 'generic',
                    'source_tool': 'unknown'
                }
                rows.append(row)
            
            # Add metadata columns if requested
            if include_metadata:
                for row in rows:
                    row['uncertainty'] = vertical_slice_data.get('uncertainty', 0.0)
                    row['reasoning'] = vertical_slice_data.get('reasoning', '')
                    row['success'] = vertical_slice_data.get('success', True)
                    row['processing_time'] = vertical_slice_data.get('processing_time', 0.0)
            
            # Create DataFrame
            df = pd.DataFrame(rows)
            
            logger.info(f"Converted vertical slice data to DataFrame: {df.shape} rows x {df.shape[1] if len(df.columns) else 0} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to convert vertical slice data to table format: {e}")
            # Return minimal DataFrame on error
            return pd.DataFrame([{
                'text': str(vertical_slice_data),
                'data_type': 'error',
                'error_message': str(e),
                'source_tool': 'adapter_error'
            }])
    
    def vertical_slice_to_graph(self, vertical_slice_data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Convert vertical slice tool output to graph format for analytics GRAPH format
        
        Args:
            vertical_slice_data: Output from vertical slice tools
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists for analytics CrossModalConverter
        """
        try:
            nodes = []
            edges = []
            
            if 'entities' in vertical_slice_data and 'relationships' in vertical_slice_data:
                # Already in graph format (from GraphTool)
                entities = vertical_slice_data['entities']
                relationships = vertical_slice_data['relationships']
                
                # Convert entities to nodes
                for entity in entities:
                    node = {
                        'id': entity.get('id', entity.get('name', f"node_{len(nodes)}")),
                        'label': entity.get('name', entity.get('label', 'Unknown')),
                        'type': entity.get('type', 'entity'),
                        'properties': {
                            'source_tool': 'GraphTool',
                            'uncertainty': vertical_slice_data.get('uncertainty', 0.0),
                            **entity.get('attributes', {})
                        }
                    }
                    nodes.append(node)
                
                # Convert relationships to edges  
                for rel in relationships:
                    edge = {
                        'source': rel.get('source', ''),
                        'target': rel.get('target', ''),
                        'relation': rel.get('type', 'relates_to'),
                        'type': rel.get('type', 'relates_to'),
                        'properties': {
                            'source_tool': 'GraphTool',
                            'uncertainty': vertical_slice_data.get('uncertainty', 0.0),
                            **rel.get('attributes', {})
                        }
                    }
                    edges.append(edge)
            
            elif 'text' in vertical_slice_data:
                # Text-based data - create simple text node
                node = {
                    'id': 'text_node_0',
                    'label': vertical_slice_data['text'][:100] + '...' if len(vertical_slice_data['text']) > 100 else vertical_slice_data['text'],
                    'type': 'text',
                    'properties': {
                        'full_text': vertical_slice_data['text'],
                        'source_tool': vertical_slice_data.get('source_tool', 'VectorTool'),
                        'uncertainty': vertical_slice_data.get('uncertainty', 0.0),
                        'has_embedding': 'embedding' in vertical_slice_data
                    }
                }
                nodes.append(node)
            
            elif 'row_id' in vertical_slice_data:
                # Storage data - create storage node  
                node = {
                    'id': f"storage_{vertical_slice_data['row_id']}",
                    'label': f"Stored Data {vertical_slice_data['row_id']}",
                    'type': 'storage',
                    'properties': {
                        'storage_id': vertical_slice_data['row_id'],
                        'source_tool': 'TableTool',
                        'uncertainty': vertical_slice_data.get('uncertainty', 0.0)
                    }
                }
                nodes.append(node)
            
            else:
                # Generic data - create generic node
                node = {
                    'id': 'generic_node_0',
                    'label': 'Generic Data',
                    'type': 'generic',
                    'properties': {
                        'data': str(vertical_slice_data),
                        'source_tool': 'unknown',
                        'uncertainty': vertical_slice_data.get('uncertainty', 0.0)
                    }
                }
                nodes.append(node)
            
            result = {
                'nodes': nodes,
                'edges': edges
            }
            
            logger.info(f"Converted vertical slice data to graph format: {len(nodes)} nodes, {len(edges)} edges")
            return result
            
        except Exception as e:
            logger.error(f"Failed to convert vertical slice data to graph format: {e}")
            # Return minimal graph on error
            return {
                'nodes': [{
                    'id': 'error_node',
                    'label': 'Conversion Error',
                    'type': 'error',
                    'properties': {
                        'error_message': str(e),
                        'original_data': str(vertical_slice_data)
                    }
                }],
                'edges': []
            }
    
    def table_to_vertical_slice(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert pandas DataFrame back to vertical slice format
        
        Args:
            df: pandas DataFrame from analytics
            
        Returns:
            List of vertical slice compatible dictionaries
        """
        try:
            results = []
            
            for _, row in df.iterrows():
                vs_data = {
                    'text': row.get('text', ''),
                    'data_type': row.get('data_type', 'unknown'),
                    'source_tool': row.get('source_tool', 'analytics'),
                    'uncertainty': row.get('uncertainty', 0.0),
                    'reasoning': row.get('reasoning', 'Converted from analytics DataFrame'),
                    'success': row.get('success', True)
                }
                
                # Add type-specific fields
                if row.get('data_type') == 'entity':
                    vs_data['entity_type'] = row.get('entity_type', 'unknown')
                    vs_data['entity_id'] = row.get('entity_id', '')
                elif row.get('data_type') == 'relationship':
                    vs_data['relation_type'] = row.get('relation_type', 'unknown')
                    vs_data['source_entity'] = row.get('source_entity', '')
                    vs_data['target_entity'] = row.get('target_entity', '')
                
                results.append(vs_data)
            
            logger.info(f"Converted DataFrame to vertical slice format: {len(results)} items")
            return results
            
        except Exception as e:
            logger.error(f"Failed to convert DataFrame to vertical slice format: {e}")
            return [{
                'text': 'Conversion error',
                'data_type': 'error',
                'error_message': str(e),
                'uncertainty': 1.0,
                'success': False
            }]
    
    def graph_to_vertical_slice(self, graph_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Convert graph format back to vertical slice GraphTool format
        
        Args:
            graph_data: Graph with 'nodes' and 'edges' from analytics
            
        Returns:
            Vertical slice GraphTool compatible format
        """
        try:
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            
            # Convert nodes to entities
            entities = []
            for node in nodes:
                entity = {
                    'id': node.get('id', ''),
                    'name': node.get('label', node.get('id', 'Unknown')),
                    'type': node.get('type', 'entity'),
                    'attributes': node.get('properties', {})
                }
                entities.append(entity)
            
            # Convert edges to relationships
            relationships = []
            for edge in edges:
                relationship = {
                    'source': edge.get('source', ''),
                    'target': edge.get('target', ''),
                    'type': edge.get('relation', edge.get('type', 'relates_to')),
                    'attributes': edge.get('properties', {})
                }
                relationships.append(relationship)
            
            result = {
                'success': True,
                'entities': entities,
                'relationships': relationships,
                'uncertainty': 0.0,  # Will be recalculated by analytics
                'reasoning': 'Converted from analytics graph format',
                'construct_mapping': 'graph → entities_and_relationships'
            }
            
            logger.info(f"Converted graph to vertical slice format: {len(entities)} entities, {len(relationships)} relationships")
            return result
            
        except Exception as e:
            logger.error(f"Failed to convert graph to vertical slice format: {e}")
            return {
                'success': False,
                'entities': [],
                'relationships': [],
                'uncertainty': 1.0,
                'reasoning': f'Conversion error: {str(e)}',
                'error': str(e)
            }


# Factory function for easy usage
def create_data_adapter() -> VerticalSliceDataAdapter:
    """Create a vertical slice data adapter instance"""
    return VerticalSliceDataAdapter()


# Test the adapter
if __name__ == "__main__":
    adapter = VerticalSliceDataAdapter()
    
    print("=== Testing Analytics Data Adapters ===\n")
    
    # Test 1: VectorTool output to table
    print("📊 Test 1: VectorTool output → Table")
    vector_output = {
        'success': True,
        'text': 'Machine learning and artificial intelligence research',
        'embedding': [0.1, 0.2, 0.3, -0.1, 0.5],  # Simplified embedding
        'uncertainty': 0.05,
        'reasoning': 'Generated embedding with 5% uncertainty',
        'source_tool': 'VectorTool'
    }
    
    table_df = adapter.vertical_slice_to_table(vector_output)
    print(f"   DataFrame shape: {table_df.shape}")
    print(f"   Columns: {list(table_df.columns)}")
    print(f"   Sample data: {table_df.iloc[0]['text'][:50]}...")
    
    # Test 2: GraphTool output to graph
    print("\n🔗 Test 2: GraphTool output → Graph") 
    graph_output = {
        'success': True,
        'entities': [
            {'id': '1', 'name': 'Machine Learning', 'type': 'CONCEPT'},
            {'id': '2', 'name': 'Neural Networks', 'type': 'CONCEPT'}
        ],
        'relationships': [
            {'source': 'Machine Learning', 'target': 'Neural Networks', 'type': 'INCLUDES'}
        ],
        'uncertainty': 0.25,
        'reasoning': 'Extracted entities and relationships'
    }
    
    graph_format = adapter.vertical_slice_to_graph(graph_output)
    print(f"   Nodes: {len(graph_format['nodes'])}")
    print(f"   Edges: {len(graph_format['edges'])}")
    print(f"   Sample node: {graph_format['nodes'][0]['label']}")
    
    print("\n✅ Data adapter tests completed successfully!")