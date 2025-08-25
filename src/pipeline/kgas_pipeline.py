#!/usr/bin/env python3
"""KGAS Pipeline - Document → Entities → Graph → Query"""

import os
import sys
from typing import Dict, Any, List

sys.path.insert(0, '/home/brian/projects/Digimons')

# Direct import to avoid problematic __init__.py files
import importlib.util
spec = importlib.util.spec_from_file_location("t23c_llm_extractor", "/home/brian/projects/Digimons/src/tools/phase2/t23c_llm_extractor.py")
t23c_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t23c_module)
T23CLLMExtractor = t23c_module.T23CLLMExtractor

from neo4j import GraphDatabase

class KGASPipeline:
    """Full pipeline: Document → LLM → Entities → Neo4j → Query"""
    
    def __init__(self):
        # Initialize components
        self.llm_extractor = T23CLLMExtractor()
        
        # Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
    
    def process_document(self, text: str) -> Dict[str, Any]:
        """Process document through full pipeline"""
        
        results = {
            "pipeline_stages": []
        }
        
        # Stage 1: LLM Extraction
        print("Stage 1: Extracting entities with LLM...")
        extraction = self.llm_extractor.extract_entities(text)
        results["llm_extraction"] = extraction
        results["pipeline_stages"].append({
            "stage": "llm_extraction",
            "entities_found": len(extraction["entities"]),
            "relationships_found": len(extraction["relationships"])
        })
        
        # Stage 2: Store Entities in Neo4j
        print("Stage 2: Storing entities in Neo4j...")
        stored_entities = self._store_entities_in_neo4j(extraction["entities"])
        results["stored_entities"] = stored_entities
        results["pipeline_stages"].append({
            "stage": "entity_storage",
            "entities_stored": len(stored_entities)
        })
        
        # Stage 3: Store Relationships in Neo4j
        print("Stage 3: Storing relationships in Neo4j...")
        stored_relationships = self._store_relationships_in_neo4j(
            extraction["relationships"], 
            stored_entities
        )
        results["stored_relationships"] = stored_relationships
        results["pipeline_stages"].append({
            "stage": "relationship_storage",
            "relationships_stored": len(stored_relationships)
        })
        
        return results
    
    def _store_entities_in_neo4j(self, entities: List[Dict]) -> List[Dict]:
        """Store entities as nodes in Neo4j"""
        stored = []
        
        with self.neo4j_driver.session() as session:
            for entity in entities:
                # Create node
                result = session.run("""
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type,
                        e.confidence = $confidence,
                        e.created_at = timestamp()
                    RETURN e.name as name, id(e) as node_id
                """, 
                name=entity["name"],
                type=entity["type"],
                confidence=entity.get("confidence", 0.9)
                )
                
                record = result.single()
                if record:
                    stored.append({
                        "name": record["name"],
                        "node_id": record["node_id"],
                        "type": entity["type"]
                    })
        
        return stored
    
    def _store_relationships_in_neo4j(self, relationships: List[Dict], 
                                     entities: List[Dict]) -> List[Dict]:
        """Store relationships as edges in Neo4j"""
        stored = []
        
        with self.neo4j_driver.session() as session:
            for rel in relationships:
                # Create relationship
                rel_type = rel["relation"].upper().replace(" ", "_")
                
                result = session.run(f"""
                    MATCH (a:Entity {{name: $source}})
                    MATCH (b:Entity {{name: $target}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r.confidence = $confidence,
                        r.created_at = timestamp()
                    RETURN a.name as source, b.name as target, type(r) as relation
                """,
                source=rel["source"],
                target=rel["target"],
                confidence=rel.get("confidence", 0.8)
                )
                
                record = result.single()
                if record:
                    stored.append({
                        "source": record["source"],
                        "target": record["target"],
                        "relation": record["relation"]
                    })
        
        return stored
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge graph"""
        
        # Extract key entity from question
        # Simple approach - look for capitalized words
        import re
        entities_in_question = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', question)
        
        results = {
            "question": question,
            "entities_identified": entities_in_question,
            "answers": []
        }
        
        with self.neo4j_driver.session() as session:
            # Query patterns based on question type
            if "who leads" in question.lower() or "who is the ceo" in question.lower():
                for entity in entities_in_question:
                    result = session.run("""
                        MATCH (org:Entity {name: $name})-[:LED_BY|CEO|FOUNDED_BY]->(person:Entity)
                        RETURN person.name as leader, person.type as type
                        LIMIT 1
                    """, name=entity)
                    
                    record = result.single()
                    if record:
                        results["answers"].append({
                            "entity": entity,
                            "answer": f"{entity} is led by {record['leader']}",
                            "leader": record["leader"]
                        })
            
            elif "where" in question.lower() and "headquartered" in question.lower():
                for entity in entities_in_question:
                    result = session.run("""
                        MATCH (org:Entity {name: $name})-[:HEADQUARTERED_IN|BASED_IN|LOCATED_IN]->(loc:Entity)
                        RETURN loc.name as location, loc.type as type
                        LIMIT 1
                    """, name=entity)
                    
                    record = result.single()
                    if record:
                        results["answers"].append({
                            "entity": entity,
                            "answer": f"{entity} is headquartered in {record['location']}",
                            "location": record["location"]
                        })
        
        return results
    
    def cleanup(self):
        """Clean up connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()