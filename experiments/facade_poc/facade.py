"""
Knowledge Graph Facade - Clean interface hiding tool complexity.

This facade provides what users actually want:
- Extract knowledge from documents
- Query the knowledge
- No exposure to underlying tool complexity
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGraph:
    """Simple representation of extracted knowledge."""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    def __repr__(self):
        return f"KnowledgeGraph(entities={len(self.entities)}, relationships={len(self.relationships)})"


@dataclass
class QueryResult:
    """Result from querying the knowledge graph."""
    answer: Any
    confidence: float
    sources: List[str]
    
    def __repr__(self):
        return f"QueryResult(answer={self.answer}, confidence={self.confidence:.2f})"


class KnowledgeFacade:
    """
    Clean interface for knowledge extraction and querying.
    
    Users interact with this simple API:
    - extract_knowledge(document) -> KnowledgeGraph
    - query_graph(question) -> QueryResult
    - add_document(document) -> bool
    - get_insights() -> Dict
    
    All complexity is hidden behind this facade.
    """
    
    def __init__(self):
        """Initialize the facade with internal tool wrappers."""
        self._initialize_tools()
        self.graphs = []  # Store extracted graphs
        logger.info("KnowledgeFacade initialized")
    
    def extract_knowledge(self, document_path: str) -> KnowledgeGraph:
        """
        Extract knowledge from a document.
        
        What users see:
            Simple document -> knowledge transformation
            
        What happens internally:
            1. Load document with T03
            2. Extract entities with T23C
            3. Convert entities to mentions (lossy)
            4. Feed to T31 (redundant but required)
            5. Build edges with T34
            6. Return clean KnowledgeGraph
        """
        logger.info(f"Extracting knowledge from: {document_path}")
        
        try:
            # Step 1: Load document
            text = self._load_document(document_path)
            
            # Step 2: Extract entities and relationships with T23C
            t23c_result = self._extract_entities(text)
            
            # Step 3: Convert entities to mentions for T31
            # This is the key translation - T23C outputs entities, T31 needs mentions
            mentions = self._translate_entities_to_mentions(t23c_result['entities'])
            
            # Step 4: Process through T31 (even though redundant)
            # T31 will create entities again from mentions
            t31_result = self._build_entities_from_mentions(mentions)
            
            # Step 5: Build edges with T34
            # T34 needs both entities and relationships
            edges = self._build_edges(t31_result['entities'], t23c_result['relationships'])
            
            # Step 6: Package into clean KnowledgeGraph
            graph = KnowledgeGraph(
                entities=t31_result['entities'],
                relationships=edges,
                metadata={
                    'source': document_path,
                    'entity_count': len(t31_result['entities']),
                    'relationship_count': len(edges)
                }
            )
            
            self.graphs.append(graph)
            logger.info(f"Successfully extracted: {graph}")
            return graph
            
        except Exception as e:
            logger.error(f"Knowledge extraction failed: {e}")
            # Return empty graph rather than exposing internal errors
            return KnowledgeGraph(entities=[], relationships=[], metadata={'error': str(e)})
    
    def query_graph(self, question: str) -> QueryResult:
        """
        Query the knowledge graph with natural language.
        
        What users see:
            Simple question -> answer
            
        What happens internally:
            Complex graph querying with T49
        """
        logger.info(f"Querying graph: {question}")
        
        if not self.graphs:
            return QueryResult(
                answer="No knowledge graphs available. Please extract knowledge from a document first.",
                confidence=0.0,
                sources=[]
            )
        
        try:
            # Use T49 or similar for querying
            # For now, return a simple mock result
            result = self._query_internal(question, self.graphs[-1])
            
            return QueryResult(
                answer=result.get('answer', 'No answer found'),
                confidence=result.get('confidence', 0.5),
                sources=result.get('sources', [])
            )
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return QueryResult(
                answer=f"Query failed: {str(e)}",
                confidence=0.0,
                sources=[]
            )
    
    def add_document(self, document_path: str) -> bool:
        """
        Add a document to the knowledge base.
        
        Simple success/failure response hiding all complexity.
        """
        try:
            graph = self.extract_knowledge(document_path)
            return len(graph.entities) > 0
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get high-level insights from accumulated knowledge.
        
        What users see:
            Simple insights summary
            
        What happens internally:
            Complex analysis across multiple tools
        """
        if not self.graphs:
            return {"message": "No knowledge extracted yet"}
        
        total_entities = sum(len(g.entities) for g in self.graphs)
        total_relationships = sum(len(g.relationships) for g in self.graphs)
        
        # Extract entity types
        entity_types = {}
        for graph in self.graphs:
            for entity in graph.entities:
                etype = entity.get('type', 'UNKNOWN')
                entity_types[etype] = entity_types.get(etype, 0) + 1
        
        return {
            'documents_processed': len(self.graphs),
            'total_entities': total_entities,
            'total_relationships': total_relationships,
            'entity_types': entity_types,
            'most_common_type': max(entity_types.items(), key=lambda x: x[1])[0] if entity_types else None
        }
    
    # Private methods - The complexity lives here
    
    def _initialize_tools(self):
        """Initialize tool wrappers - hidden from users."""
        # These will be imported from wrappers module
        # For now, we'll use mock implementations
        logger.info("Initializing internal tool wrappers")
        self.t03_wrapper = None  # Document loader
        self.t23c_wrapper = None  # Entity extractor
        self.t31_wrapper = None  # Entity builder
        self.t34_wrapper = None  # Edge builder
        self.t49_wrapper = None  # Query engine
    
    def _load_document(self, path: str) -> str:
        """Load document using T03 wrapper."""
        # Mock for now - will use real T03
        logger.debug(f"Loading document: {path}")
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Create mock content for testing
            return "Apple Inc. was founded by Steve Jobs in Cupertino. Microsoft was founded by Bill Gates."
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities using T23C wrapper."""
        # Mock implementation - will use real T23C
        logger.debug("Extracting entities with T23C")
        
        # Simulate T23C output - resolved entities and relationships
        return {
            'entities': [
                {'id': 'e1', 'canonical_name': 'Apple Inc.', 'type': 'ORGANIZATION', 'confidence': 0.95},
                {'id': 'e2', 'canonical_name': 'Steve Jobs', 'type': 'PERSON', 'confidence': 0.98},
                {'id': 'e3', 'canonical_name': 'Cupertino', 'type': 'LOCATION', 'confidence': 0.90},
                {'id': 'e4', 'canonical_name': 'Microsoft', 'type': 'ORGANIZATION', 'confidence': 0.95},
                {'id': 'e5', 'canonical_name': 'Bill Gates', 'type': 'PERSON', 'confidence': 0.98}
            ],
            'relationships': [
                {'source': 'Apple Inc.', 'target': 'Steve Jobs', 'type': 'FOUNDED_BY'},
                {'source': 'Apple Inc.', 'target': 'Cupertino', 'type': 'LOCATED_IN'},
                {'source': 'Microsoft', 'target': 'Bill Gates', 'type': 'FOUNDED_BY'}
            ]
        }
    
    def _translate_entities_to_mentions(self, entities: List[Dict]) -> List[Dict]:
        """
        Critical translation: Convert T23C entities to T31 mentions.
        
        This is lossy - we lose position information and create synthetic mentions.
        But it's necessary because T31 expects mentions, not entities.
        """
        logger.debug("Translating entities to mentions (lossy conversion)")
        
        mentions = []
        for entity in entities:
            # Create synthetic mention from entity
            mention = {
                'text': entity['canonical_name'],
                'entity_type': entity['type'],
                'start_pos': 0,  # Lost this information
                'end_pos': len(entity['canonical_name']),  # Synthetic
                'confidence': entity.get('confidence', 0.8)
            }
            mentions.append(mention)
        
        logger.debug(f"Translated {len(entities)} entities to {len(mentions)} mentions")
        return mentions
    
    def _build_entities_from_mentions(self, mentions: List[Dict]) -> Dict[str, Any]:
        """Build entities using T31 wrapper."""
        # Mock implementation - will use real T31
        logger.debug("Building entities with T31")
        
        # T31 would recreate entities from mentions
        # This is redundant since T23C already did this
        entities = []
        for i, mention in enumerate(mentions):
            entity = {
                'id': f'entity_{i}',
                'canonical_name': mention['text'],
                'type': mention['entity_type'],
                'mentions': [mention]
            }
            entities.append(entity)
        
        return {'entities': entities}
    
    def _build_edges(self, entities: List[Dict], relationships: List[Dict]) -> List[Dict]:
        """Build edges using T34 wrapper."""
        # Mock implementation - will use real T34
        logger.debug("Building edges with T34")
        
        # T34 needs both entities and relationships
        edges = []
        for rel in relationships:
            edge = {
                'source': rel['source'],
                'target': rel['target'],
                'type': rel['type'],
                'weight': 1.0
            }
            edges.append(edge)
        
        return edges
    
    def _query_internal(self, question: str, graph: KnowledgeGraph) -> Dict[str, Any]:
        """Query using T49 or similar."""
        # Mock implementation
        logger.debug(f"Querying: {question}")
        
        # Simple mock logic
        if "companies" in question.lower() or "organization" in question.lower():
            orgs = [e for e in graph.entities if e.get('type') == 'ORGANIZATION']
            org_names = [org['canonical_name'] for org in orgs]
            return {
                'answer': f"Found {len(orgs)} companies: {', '.join(org_names)}",
                'confidence': 0.9,
                'sources': ['document']
            }
        
        return {
            'answer': "Unable to answer that question",
            'confidence': 0.1,
            'sources': []
        }