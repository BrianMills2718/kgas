#!/usr/bin/env python3
"""Graph Tool - Converts table data into graph structures

Creates graph structures from embedded table data for knowledge graph analysis.
Supports both Neo4j and NetworkX backends with uncertainty propagation.
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None


class GraphTool:
    """Converts table data into graph structures for knowledge analysis"""
    
    def __init__(self, neo4j_uri: str = None, neo4j_auth: Tuple[str, str] = None):
        """Initialize GraphTool with optional Neo4j connection
        
        Args:
            neo4j_uri: Neo4j connection URI (optional)
            neo4j_auth: Neo4j authentication tuple (username, password)
        """
        self.logger = logging.getLogger(__name__)
        
        # Neo4j connection (optional)
        self.neo4j_driver = None
        if neo4j_uri and NEO4J_AVAILABLE:
            try:
                auth = neo4j_auth or ("neo4j", "devpassword")
                self.neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=auth)
                self.logger.info("Neo4j connection established")
            except Exception as e:
                self.logger.warning(f"Neo4j connection failed: {e}, using NetworkX only")
        
        # Check NetworkX availability
        if not NETWORKX_AVAILABLE:
            self.logger.warning("NetworkX not available, graph functionality limited")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert vector or table data to graph structure
        
        Args:
            data: Dictionary containing embedding data and metadata from VectorTool or TableTool
            
        Returns:
            Dictionary with success status, graph data, uncertainty, and reasoning
        """
        try:
            # Handle different input types
            if 'embedding' in data:
                # Data from VectorTool (direct) or VectorTool → TableTool chain
                text = data.get('text', '')
                embedding = data.get('embedding', [])
                stored_id = data.get('row_id', data.get('stored_id'))  # TableTool uses 'row_id'
            elif 'row_id' in data:
                # Data from TableTool
                text = data.get('text', '')
                embedding = []
                stored_id = data.get('row_id')
            else:
                # Handle direct text input or unknown format
                text = data.get('text', str(data))
                embedding = []
                stored_id = None
            
            # Create graph from text content
            graph_data = self._create_graph_from_text(text, embedding, stored_id)
            
            # Calculate uncertainty (simple entity extraction confidence)
            uncertainty = self._calculate_graph_uncertainty(graph_data)
            
            # Generate reasoning
            num_nodes = len(graph_data.get('nodes', []))
            num_edges = len(graph_data.get('edges', []))
            reasoning = f"Created graph with {num_nodes} nodes and {num_edges} edges from text analysis"
            
            return {
                'success': True,
                'graph': graph_data,
                'text': text,
                'embedding': embedding,
                'stored_id': stored_id,
                'uncertainty': uncertainty,
                'reasoning': reasoning,
                'graph_stats': {
                    'nodes': num_nodes,
                    'edges': num_edges,
                    'density': self._calculate_graph_density(num_nodes, num_edges)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Graph processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0,
                'reasoning': f'Graph creation failed: {str(e)}'
            }
    
    def _create_graph_from_text(self, text: str, embedding: List[float], stored_id: Optional[str]) -> Dict[str, Any]:
        """Create graph structure from text using LLM-based entity and relationship extraction"""
        
        # Use LLM-based knowledge graph extraction
        from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
        
        try:
            kg_extractor = KnowledgeGraphExtractor()
            kg_result = kg_extractor.process(text)
            
            if not kg_result.get('success', False):
                raise Exception(f"Knowledge graph extraction failed: {kg_result.get('error', 'Unknown error')}")
            
            # Use LLM extracted entities and relationships
            entities = kg_result.get('entities', [])
            relationships = kg_result.get('relationships', [])
            
        except Exception as e:
            self.logger.error(f"LLM knowledge graph extraction failed: {e}")
            # FAIL-FAST: Don't fall back to rule-based extraction
            raise RuntimeError(f"Failed to extract knowledge graph using LLM: {str(e)}") from e
        
        # Convert to graph structure
        nodes = []
        edges = []
        node_ids = {}
        
        # Create nodes for entities (LLM format)
        for i, entity in enumerate(entities):
            node_id = f"node_{i}"
            entity_name = entity.get('name', entity.get('text', f'entity_{i}'))
            node_ids[entity_name] = node_id
            nodes.append({
                'id': node_id,
                'label': entity_name,
                'type': entity.get('type', 'ENTITY'),
                'confidence': 0.8,  # LLM extraction confidence
                'properties': {
                    'name': entity_name,
                    'entity_id': entity.get('id', f'entity_{i}'),
                    'attributes': entity.get('attributes', {}),
                    'source': 'llm_extraction',
                    'stored_id': stored_id
                }
            })
        
        # Create edges for relationships (LLM format)
        for rel in relationships:
            source_name = rel.get('source', '')
            target_name = rel.get('target', '')
            source_id = node_ids.get(source_name)
            target_id = node_ids.get(target_name)
            
            if source_id and target_id and source_id != target_id:
                edges.append({
                    'source': source_id,
                    'target': target_id,
                    'relation': rel.get('type', 'RELATES_TO'),
                    'confidence': 0.75,  # LLM relationship confidence
                    'properties': {
                        'weight': 0.75,
                        'relationship_type': rel.get('type', 'RELATES_TO'),
                        'attributes': rel.get('attributes', {}),
                        'source': 'llm_extraction'
                    }
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'source_text_length': len(text),
                'extraction_method': 'simple_nlp',
                'has_embedding': len(embedding) > 0,
                'stored_id': stored_id
            }
        }
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using simple keyword-based approach"""
        # Simple entity extraction - in production, would use spaCy or similar
        
        # Common entity patterns
        entities = []
        words = text.split()
        
        # Look for capitalized words (potential proper nouns)
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Simple entity classification
                if word.lower() in ['ai', 'artificial', 'intelligence', 'machine', 'learning', 'deep', 'neural', 'network']:
                    entity_type = 'CONCEPT'
                elif word.endswith('ing') or word.endswith('tion') or word.endswith('ment'):
                    entity_type = 'PROCESS'
                else:
                    entity_type = 'ENTITY'
                
                entities.append({
                    'text': word,
                    'type': entity_type,
                    'confidence': 0.7,
                    'position': i
                })
        
        # Look for multi-word phrases (simple bigram/trigram detection)
        for i in range(len(words) - 1):
            if words[i][0].isupper() and words[i+1][0].isupper():
                phrase = f"{words[i]} {words[i+1]}"
                entities.append({
                    'text': phrase,
                    'type': 'PHRASE',
                    'confidence': 0.8,
                    'position': i
                })
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity['text'] not in seen:
                seen.add(entity['text'])
                unique_entities.append(entity)
        
        return sorted(unique_entities, key=lambda x: x['confidence'], reverse=True)[:10]  # Top 10
    
    def _extract_relationships(self, entities: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities based on co-occurrence"""
        relationships = []
        
        # Simple co-occurrence based relationship detection
        entity_texts = [e['text'] for e in entities]
        
        for i, entity1 in enumerate(entity_texts):
            for j, entity2 in enumerate(entity_texts[i+1:], i+1):
                # Check if entities appear near each other in text
                entity1_pos = text.find(entity1)
                entity2_pos = text.find(entity2)
                
                if entity1_pos != -1 and entity2_pos != -1:
                    distance = abs(entity1_pos - entity2_pos)
                    
                    # If entities are within 50 characters, create relationship
                    if distance < 50:
                        # Simple relationship classification
                        if 'and' in text[min(entity1_pos, entity2_pos):max(entity1_pos, entity2_pos) + max(len(entity1), len(entity2))]:
                            relation = 'RELATED_TO'
                        elif any(word in text.lower() for word in ['uses', 'applies', 'implements']):
                            relation = 'USES'
                        elif any(word in text.lower() for word in ['part of', 'component', 'includes']):
                            relation = 'PART_OF'
                        else:
                            relation = 'CO_OCCURS_WITH'
                        
                        confidence = max(0.3, 0.8 - (distance / 100))  # Closer = higher confidence
                        
                        relationships.append({
                            'source': entity1,
                            'target': entity2,
                            'relation': relation,
                            'confidence': confidence,
                            'distance': distance
                        })
        
        return sorted(relationships, key=lambda x: x['confidence'], reverse=True)[:15]  # Top 15
    
    def _calculate_graph_uncertainty(self, graph_data: Dict[str, Any]) -> float:
        """Calculate uncertainty based on graph structure and entity confidence"""
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        if not nodes:
            return 1.0
        
        # Average entity confidence
        entity_confidences = [node.get('confidence', 0.5) for node in nodes]
        avg_entity_conf = sum(entity_confidences) / len(entity_confidences)
        
        # Average relationship confidence
        if edges:
            rel_confidences = [edge.get('confidence', 0.5) for edge in edges]
            avg_rel_conf = sum(rel_confidences) / len(rel_confidences)
        else:
            avg_rel_conf = 0.5
        
        # Graph connectivity factor (more connected = more certain)
        num_nodes = len(nodes)
        num_edges = len(edges)
        expected_edges = num_nodes * (num_nodes - 1) / 2  # Complete graph
        connectivity = num_edges / expected_edges if expected_edges > 0 else 0
        connectivity_factor = min(connectivity * 2, 1.0)  # Boost for connectivity
        
        # Combined uncertainty (lower is more certain)
        uncertainty = 1.0 - ((avg_entity_conf + avg_rel_conf + connectivity_factor) / 3)
        
        return max(0.1, min(0.9, uncertainty))  # Clamp between 0.1 and 0.9
    
    def _calculate_graph_density(self, num_nodes: int, num_edges: int) -> float:
        """Calculate graph density (0-1)"""
        if num_nodes <= 1:
            return 0.0
        
        max_edges = num_nodes * (num_nodes - 1) / 2
        return num_edges / max_edges if max_edges > 0 else 0.0
    
    def create_networkx_graph(self, graph_data: Dict[str, Any]) -> Optional[Any]:
        """Create NetworkX graph from graph data"""
        if not NETWORKX_AVAILABLE:
            self.logger.warning("NetworkX not available")
            return None
        
        G = nx.Graph()
        
        # Add nodes
        for node in graph_data.get('nodes', []):
            G.add_node(node['id'], **node.get('properties', {}))
        
        # Add edges
        for edge in graph_data.get('edges', []):
            G.add_edge(
                edge['source'], 
                edge['target'], 
                relation=edge['relation'],
                **edge.get('properties', {})
            )
        
        return G
    
    def store_in_neo4j(self, graph_data: Dict[str, Any]) -> bool:
        """Store graph in Neo4j database"""
        if not self.neo4j_driver:
            self.logger.warning("Neo4j not available")
            return False
        
        try:
            with self.neo4j_driver.session() as session:
                # Create nodes
                for node in graph_data.get('nodes', []):
                    session.run(
                        "CREATE (n:Entity {id: $id, label: $label, type: $type, confidence: $confidence})",
                        id=node['id'],
                        label=node['label'],
                        type=node['type'],
                        confidence=node['confidence']
                    )
                
                # Create relationships
                for edge in graph_data.get('edges', []):
                    session.run(
                        """
                        MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                        CREATE (a)-[r:RELATES_TO {
                            relation: $relation, 
                            confidence: $confidence
                        }]->(b)
                        """,
                        source=edge['source'],
                        target=edge['target'],
                        relation=edge['relation'],
                        confidence=edge['confidence']
                    )
            
            return True
        
        except Exception as e:
            self.logger.error(f"Neo4j storage failed: {e}")
            return False