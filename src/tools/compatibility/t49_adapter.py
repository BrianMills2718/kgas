"""
T49 Query Tool Adapter - FIXED VERSION
Properly extracts entities and answers questions
"""

import re
from typing import List, Dict, Any
from neo4j import GraphDatabase
import spacy
from fuzzywuzzy import fuzz

class T49QueryAdapter:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        # Load spaCy for better entity extraction
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Question patterns for different query types
        self.question_patterns = {
            "who_leads": r"who (?:leads?|runs?|manages?|heads?|is ceo of|is the ceo of)\s+(.+?)[\?\.]?$",
            "where_located": r"where (?:is|are)\s+(.+?)\s+(?:located|headquartered|based)[\?\.]?$",
            "who_founded": r"who (?:founded|created|started|established)\s+(.+?)[\?\.]?$",
            "what_does": r"what (?:does|do)\s+(.+?)\s+(?:do|make|produce|sell)[\?\.]?$",
        }
    
    def query(self, question: str) -> List[Dict[str, Any]]:
        """Execute query with improved entity extraction and matching"""
        
        # Detect question type
        question_lower = question.lower()
        question_type = self._detect_question_type(question_lower)
        
        # Extract entities using spaCy
        entities = self._extract_entities_improved(question)
        
        if not entities:
            return [{"answer": "Could not understand the question", "confidence": 0.0}]
        
        # Query based on question type
        with self.driver.session() as session:
            answers = []
            
            for entity in entities:
                # Try fuzzy matching for entities
                fuzzy_matches = self._find_fuzzy_matches(session, entity)
                
                if not fuzzy_matches:
                    continue
                
                # Get relationships based on question type
                for matched_entity in fuzzy_matches:
                    if question_type == "who_leads":
                        result = self._query_leadership(session, matched_entity)
                    elif question_type == "where_located":
                        result = self._query_location(session, matched_entity)
                    elif question_type == "who_founded":
                        result = self._query_founder(session, matched_entity)
                    else:
                        result = self._query_general(session, matched_entity)
                    
                    answers.extend(result)
            
            # Sort by confidence and return top answer
            if answers:
                answers.sort(key=lambda x: x.get("confidence", 0), reverse=True)
                return [answers[0]]  # Return best answer
            
            return [{"answer": f"No information found about {', '.join(entities)}", "confidence": 0.0}]
    
    def _detect_question_type(self, question: str) -> str:
        """Detect the type of question being asked"""
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, question, re.IGNORECASE):
                return q_type
        return "general"
    
    def _extract_entities_improved(self, question: str) -> List[str]:
        """Extract entities using spaCy NER"""
        doc = self.nlp(question)
        entities = []
        
        # Get named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON", "GPE", "PRODUCT"]:
                entities.append(ent.text)
        
        # Also try to extract capitalized sequences (fallback)
        if not entities:
            entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', question)
        
        return entities
    
    def _find_fuzzy_matches(self, session, entity: str, threshold: int = 80) -> List[str]:
        """Find entities in database using fuzzy matching"""
        # Get all entity names from database
        result = session.run("""
            MATCH (n:Entity)
            RETURN DISTINCT n.canonical_name as name
            LIMIT 1000
        """)
        
        matches = []
        for record in result:
            name = record["name"]
            if name:
                # Calculate fuzzy match score
                score = fuzz.ratio(entity.lower(), name.lower())
                if score >= threshold:
                    matches.append(name)
                # Also check partial ratio for substring matches
                elif fuzz.partial_ratio(entity.lower(), name.lower()) >= 90:
                    matches.append(name)
        
        return matches
    
    def _query_leadership(self, session, entity_name: str) -> List[Dict[str, Any]]:
        """Query for leadership relationships"""
        result = session.run("""
            MATCH (org:Entity {canonical_name: $name})-[r]-(person:Entity)
            WHERE type(r) IN ['LED_BY', 'HAS_CEO', 'MANAGED_BY', 'RELATED_TO']
            AND person.entity_type = 'PERSON'
            RETURN person.canonical_name as leader,
                   type(r) as relationship,
                   COALESCE(person.pagerank_score, 0.5) as confidence
            ORDER BY confidence DESC
            LIMIT 1
        """, name=entity_name)
        
        answers = []
        for record in result:
            answers.append({
                "answer": f"{entity_name} is led by {record['leader']}",
                "confidence": float(record['confidence']),
                "relationship": record['relationship']
            })
        return answers
    
    def _query_location(self, session, entity_name: str) -> List[Dict[str, Any]]:
        """Query for location relationships"""
        result = session.run("""
            MATCH (entity:Entity {canonical_name: $name})-[r]-(location:Entity)
            WHERE type(r) IN ['HEADQUARTERED_IN', 'LOCATED_IN', 'BASED_IN', 'RELATED_TO']
            AND location.entity_type IN ['GPE', 'LOC']
            RETURN location.canonical_name as location,
                   type(r) as relationship,
                   COALESCE(location.pagerank_score, 0.5) as confidence
            ORDER BY confidence DESC
            LIMIT 1
        """, name=entity_name)
        
        answers = []
        for record in result:
            answers.append({
                "answer": f"{entity_name} is located in {record['location']}",
                "confidence": float(record['confidence']),
                "relationship": record['relationship']
            })
        return answers
    
    def _query_founder(self, session, entity_name: str) -> List[Dict[str, Any]]:
        """Query for founder relationships"""
        result = session.run("""
            MATCH (entity:Entity {canonical_name: $name})-[r]-(founder:Entity)
            WHERE type(r) IN ['FOUNDED_BY', 'CREATED_BY', 'ESTABLISHED_BY', 'RELATED_TO']
            AND founder.entity_type = 'PERSON'
            RETURN collect(founder.canonical_name) as founders,
                   type(r) as relationship,
                   AVG(COALESCE(founder.pagerank_score, 0.5)) as confidence
            LIMIT 1
        """, name=entity_name)
        
        answers = []
        for record in result:
            if record['founders']:
                founders_str = ", ".join(record['founders'])
                answers.append({
                    "answer": f"{entity_name} was founded by {founders_str}",
                    "confidence": float(record['confidence']),
                    "relationship": record['relationship']
                })
        return answers
    
    def _query_general(self, session, entity_name: str) -> List[Dict[str, Any]]:
        """General relationship query"""
        result = session.run("""
            MATCH (n:Entity {canonical_name: $name})-[r]-(m:Entity)
            RETURN n.canonical_name as source,
                   type(r) as relationship,
                   m.canonical_name as target,
                   COALESCE(m.pagerank_score, 0.5) as confidence
            ORDER BY confidence DESC
            LIMIT 3
        """, name=entity_name)
        
        answers = []
        for record in result:
            answers.append({
                "answer": f"{record['source']} {record['relationship']} {record['target']}",
                "confidence": float(record['confidence']),
                "relationship": record['relationship']
            })
        return answers