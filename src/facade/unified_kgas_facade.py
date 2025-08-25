"""
Unified KGAS Facade
Single interface that makes all tools work together
"""

import os
import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from typing import Dict, Any, List
import spacy
import re
from neo4j import GraphDatabase

# Import compatibility layers
from src.tools.compatibility.tool_patches import PatchedToolRequest
from src.tools.compatibility.t34_adapter import convert_relationships_for_t34
from src.tools.compatibility.t49_adapter import T49QueryAdapter
from src.tools.compatibility.t68_integration import T68PageRankIntegration
from src.tools.utils.database_manager import DatabaseSessionManager
from src.tools.utils.relationship_patterns import extract_semantic_relationships

# Import tools
from src.core.service_manager import ServiceManager
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified

class UnifiedKGASFacade:
    """
    Facade that makes all KGAS tools work together
    Hides all compatibility issues and interface mismatches
    """
    
    def __init__(self, cleanup_on_init=True):
        # Initialize services
        self.service_manager = ServiceManager()
        
        # Initialize Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            auth=(os.getenv('NEO4J_USER', 'neo4j'), 
                  os.getenv('NEO4J_PASSWORD', 'devpassword'))
        )
        
        # Add database cleanup
        self.db_manager = DatabaseSessionManager(self.neo4j_driver)
        if cleanup_on_init:
            self.db_manager.cleanup_all()  # Start fresh
        
        # Add session_id to all entity/edge creation
        self.session_id = self.db_manager.session_id
        
        # Initialize tools
        self.t31_entity_builder = T31EntityBuilderUnified(self.service_manager)
        self.t34_edge_builder = T34EdgeBuilderUnified(self.service_manager)
        
        # Initialize adapters
        self.t49_query = T49QueryAdapter(self.neo4j_driver)
        self.t68_pagerank = T68PageRankIntegration(self.neo4j_driver)
        
        # Initialize NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
    
    def process_document(self, text: str) -> Dict[str, Any]:
        """
        Complete pipeline: Text → Entities → Graph → PageRank
        """
        results = {
            "entities": [],
            "edges": [],
            "pagerank": {},
            "success": False
        }
        
        try:
            # Step 1: Extract entities
            entities = self._extract_entities(text)
            
            # Step 2: Build entities in Neo4j
            graph_entities = self._build_entities(entities)
            results["entities"] = graph_entities
            
            # Step 3: Extract relationships
            relationships = self._extract_relationships(text, entities)
            
            # Step 4: Build edges in Neo4j
            if relationships and graph_entities:
                entity_map = self._build_entity_map(graph_entities)
                graph_edges = self._build_edges(relationships, entity_map)
                results["edges"] = graph_edges
            
            # Step 5: Calculate PageRank
            if graph_entities:
                pagerank = self.t68_pagerank.calculate_and_store_pagerank()
                results["pagerank"] = pagerank
            
            results["success"] = True
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def query(self, question: str) -> List[Dict[str, Any]]:
        """
        Answer questions using the knowledge graph
        """
        return self.t49_query.query(question)
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        entities = []
        
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "entity_type": ent.label_,
                    "start_pos": ent.start_char,
                    "end_pos": ent.end_char,
                    "confidence": 0.85
                })
        
        return entities
    
    def _build_entities(self, entities: List[Dict]) -> List[Dict]:
        """Build entities in Neo4j using T31"""
        if not entities:
            return []
        
        request = PatchedToolRequest(input_data={"mentions": entities})
        result = self.t31_entity_builder.execute(request)
        
        if result.status == "success":
            return result.data.get("entities", [])
        return []
    
    def _extract_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships between entities using semantic patterns"""
        # Use semantic relationship extraction
        relationships = extract_semantic_relationships(text, entities)
        
        # Convert format for compatibility
        converted_relationships = []
        for rel in relationships:
            converted_relationships.append({
                "source": rel["source"],
                "target": rel["target"],
                "type": rel["relationship_type"],
                "confidence": rel["confidence"]
            })
        
        return converted_relationships
    
    def _build_entity_map(self, entities: List[Dict]) -> Dict[str, str]:
        """Build mapping from entity names to IDs"""
        entity_map = {}
        for entity in entities:
            name = entity.get("canonical_name", "")
            entity_id = entity.get("entity_id", "")
            entity_map[name] = entity_id
            
            # Also map surface forms
            for surface in entity.get("surface_forms", []):
                entity_map[surface] = entity_id
        
        return entity_map
    
    def _build_edges(self, relationships: List[Dict], entity_map: Dict) -> List[Dict]:
        """Build edges in Neo4j using T34"""
        # Convert to T34 format
        t34_relationships = convert_relationships_for_t34(relationships, entity_map)
        
        # Create request with compatibility patch
        request = PatchedToolRequest(
            input_data={"relationships": t34_relationships},
            options={"verify_entities": False}
        )
        
        result = self.t34_edge_builder.execute(request)
        
        if result.status == "success":
            return result.data.get("edges", [])
        return []