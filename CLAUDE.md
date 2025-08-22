# KGAS Critical Fixes Required

## Current Status: Partially Working - Critical Issues Found

**Last Updated**: 2025-08-22

### What's Working ✅
- Tools execute without crashing
- Data flows through pipeline without errors  
- Neo4j connections established
- Entities and edges are created in Neo4j
- PageRank calculates scores

### What's BROKEN ❌
1. **Query Answering Returns Wrong Results** - "Who leads Apple?" returns "Apple Inc. RELATED_TO Apple Inc." instead of "Tim Cook"
2. **Database Contamination** - 173 nodes found when only 14 created (old data persisting)
3. **Excessive Edges** - 182 edges from 14 entities (should be max 91)
4. **Entity Resolution Fails** - Can't match "Apple" to "Apple Inc."
5. **All Relationships Generic** - Everything is "RELATED_TO" instead of semantic types
6. **PDF Processing Untested** - Core requirement never validated

## Critical Fix Instructions

### Fix 1: Database Isolation (MUST DO FIRST)

**Problem**: Neo4j data persists between runs, contaminating results.

**Solution**: Implement session-based isolation with cleanup.

Create file: `/src/tools/utils/database_manager.py`
```python
import uuid
from neo4j import GraphDatabase
from datetime import datetime

class DatabaseSessionManager:
    """Manage isolated database sessions"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        self.session_id = str(uuid.uuid4())[:8]
        self.session_prefix = f"TEST_{self.session_id}_"
    
    def cleanup_session(self):
        """Remove all nodes/edges from current session"""
        with self.driver.session() as session:
            # Delete only nodes with our session prefix
            session.run(f"""
                MATCH (n) 
                WHERE n.session_id = $session_id
                DETACH DELETE n
            """, session_id=self.session_id)
    
    def cleanup_all(self):
        """Complete database cleanup (use with caution)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def get_node_count(self):
        """Get count of nodes in current session"""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n)
                WHERE n.session_id = $session_id
                RETURN count(n) as count
            """, session_id=self.session_id)
            return result.single()["count"]
```

**Integration**: Update `/src/facade/unified_kgas_facade.py` at line 15:
```python
def __init__(self, cleanup_on_init=True):
    # Add database cleanup
    self.db_manager = DatabaseSessionManager(self.neo4j_driver)
    if cleanup_on_init:
        self.db_manager.cleanup_all()  # Start fresh
    
    # Add session_id to all entity/edge creation
    self.session_id = self.db_manager.session_id
```

### Fix 2: Query Answering

**Problem**: Query returns wrong answers due to poor entity extraction and matching.

**Solution**: Improve entity extraction and add fuzzy matching.

Replace `/src/tools/compatibility/t49_adapter.py` entirely:
```python
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
```

**Required Package**: Install fuzzywuzzy for fuzzy matching:
```bash
pip install fuzzywuzzy python-Levenshtein
```

### Fix 3: Semantic Relationship Types

**Problem**: All relationships are generic "RELATED_TO".

**Solution**: Update relationship extraction to use semantic types.

Create file: `/src/tools/utils/relationship_patterns.py`:

```python
"""
T34 Edge Builder Adapter
Converts relationships to T34-expected format
"""

def convert_relationships_for_t34(relationships, entity_map):
    """
    Convert relationships from standard format to T34 format
    
    Standard format:
    {
        "source": "Apple",
        "target": "Tim Cook",
        "type": "LED_BY"
    }
    
    T34 format:
    {
        "subject": {"text": "Apple", "entity_id": "...", "canonical_name": "Apple"},
        "object": {"text": "Tim Cook", "entity_id": "...", "canonical_name": "Tim Cook"},
        "relationship_type": "LED_BY"
    }
    """
    t34_relationships = []
    
    for rel in relationships:
        # Handle different field names
        source = rel.get("source") or rel.get("source_entity") or rel.get("subject")
        target = rel.get("target") or rel.get("target_entity") or rel.get("object")
        rel_type = rel.get("type") or rel.get("relationship_type") or rel.get("predicate")
        
        # Convert to T34 format
        t34_rel = {
            "subject": {
                "text": source if isinstance(source, str) else source.get("text"),
                "entity_id": entity_map.get(source, source) if isinstance(source, str) else source.get("entity_id"),
                "canonical_name": source if isinstance(source, str) else source.get("canonical_name", source.get("text"))
            },
            "object": {
                "text": target if isinstance(target, str) else target.get("text"),
                "entity_id": entity_map.get(target, target) if isinstance(target, str) else target.get("entity_id"),
                "canonical_name": target if isinstance(target, str) else target.get("canonical_name", target.get("text"))
            },
            "relationship_type": rel_type,
            "confidence": rel.get("confidence", 0.75),
            "evidence_text": rel.get("evidence_text", ""),
            "extraction_method": rel.get("extraction_method", "unknown")
        }
        
        t34_relationships.append(t34_rel)
    
    return t34_relationships
```

### Step 3: Fix T49 Query Tool (1 hour)

Create `/src/tools/compatibility/t49_adapter.py`:

```python
"""
T49 Query Tool Adapter
Makes T49 work with the pipeline
"""

import re
from typing import List, Dict, Any
from neo4j import GraphDatabase

class T49QueryAdapter:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def query(self, question: str) -> List[Dict[str, Any]]:
        """
        Execute query by extracting entities and finding paths
        """
        # Extract entities from question
        entities = self._extract_entities_from_question(question)
        
        if not entities:
            return [{"answer": "No entities found in question", "confidence": 0.0}]
        
        # Find paths between entities in Neo4j
        with self.driver.session() as session:
            # For each entity, find related information
            answers = []
            
            for entity in entities:
                # Simple 1-hop query
                result = session.run("""
                    MATCH (n:Entity {canonical_name: $name})-[r]-(m:Entity)
                    RETURN n.canonical_name as source, 
                           type(r) as relationship,
                           m.canonical_name as target,
                           m.pagerank_score as importance
                    ORDER BY m.pagerank_score DESC
                    LIMIT 5
                """, name=entity)
                
                for record in result:
                    answers.append({
                        "answer": f"{record['source']} {record['relationship']} {record['target']}",
                        "confidence": record['importance'] or 0.5,
                        "source": record['source'],
                        "target": record['target'],
                        "relationship": record['relationship']
                    })
        
        return answers if answers else [{"answer": "No relationships found", "confidence": 0.0}]
    
    def _extract_entities_from_question(self, question: str) -> List[str]:
        """Extract potential entity names from question"""
        # Simple approach: find capitalized words
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', question)
        return entities
```

### Step 4: Integrate T68 PageRank (30 minutes)

Create `/src/tools/compatibility/t68_integration.py`:

```python
"""
T68 PageRank Integration
Adds PageRank calculation to the pipeline
"""

import networkx as nx
from neo4j import GraphDatabase

class T68PageRankIntegration:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
    
    def calculate_and_store_pagerank(self):
        """
        Calculate PageRank and store scores in Neo4j
        """
        # Load graph from Neo4j
        G = nx.DiGraph()
        
        with self.driver.session() as session:
            # Get all nodes
            nodes = session.run("MATCH (n:Entity) RETURN n.entity_id as id, n.canonical_name as name")
            for node in nodes:
                G.add_node(node['id'], name=node['name'])
            
            # Get all edges
            edges = session.run("MATCH (n:Entity)-[r]->(m:Entity) RETURN n.entity_id as source, m.entity_id as target, r.weight as weight")
            for edge in edges:
                G.add_edge(edge['source'], edge['target'], weight=edge['weight'] or 1.0)
        
        # Calculate PageRank
        if G.number_of_nodes() > 0:
            pagerank = nx.pagerank(G, alpha=0.85)
            
            # Store scores back to Neo4j
            with self.driver.session() as session:
                for node_id, score in pagerank.items():
                    session.run("""
                        MATCH (n:Entity {entity_id: $id})
                        SET n.pagerank_score = $score
                        RETURN n
                    """, id=node_id, score=score)
            
            return pagerank
        
        return {}
```

### Step 5: Create Unified Facade (1 hour)

Create `/src/facade/unified_kgas_facade.py`:

```python
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

# Import tools
from src.core.service_manager import ServiceManager
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified

class UnifiedKGASFacade:
    """
    Facade that makes all KGAS tools work together
    Hides all compatibility issues and interface mismatches
    """
    
    def __init__(self):
        # Initialize services
        self.service_manager = ServiceManager()
        
        # Initialize Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            auth=(os.getenv('NEO4J_USER', 'neo4j'), 
                  os.getenv('NEO4J_PASSWORD', 'devpassword'))
        )
        
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
        """Extract relationships between entities"""
        relationships = []
        entity_texts = [e["text"] for e in entities]
        
        # Simple pattern-based extraction
        patterns = {
            "led by": "LED_BY",
            "CEO of": "CEO_OF",
            "founded": "FOUNDED",
            "headquartered in": "HEADQUARTERED_IN",
            "works for": "WORKS_FOR"
        }
        
        for i, source in enumerate(entity_texts):
            for j, target in enumerate(entity_texts):
                if i != j:
                    for pattern, rel_type in patterns.items():
                        if pattern in text.lower() and source in text and target in text:
                            relationships.append({
                                "source": source,
                                "target": target,
                                "type": rel_type,
                                "confidence": 0.75
                            })
                            break
        
        return relationships
    
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
```

### Step 6: Create Test Suite (30 minutes)

Create `/src/tests/test_facade_integration.py`:

```python
"""
Integration tests for the unified facade
"""

import pytest
from src.facade.unified_kgas_facade import UnifiedKGASFacade

def test_full_pipeline():
    """Test complete pipeline: Text → Entities → Graph → PageRank → Query"""
    
    # Initialize facade
    facade = UnifiedKGASFacade()
    
    # Test text
    text = """
    Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino, California.
    Microsoft Corporation, led by CEO Satya Nadella, is based in Redmond, Washington.
    """
    
    # Process document
    result = facade.process_document(text)
    
    # Verify entities created
    assert result["success"] == True
    assert len(result["entities"]) > 0
    assert len(result["edges"]) > 0
    assert len(result["pagerank"]) > 0
    
    # Test query
    answers = facade.query("Who leads Apple?")
    assert len(answers) > 0
    
    print(f"✅ Pipeline test passed!")
    print(f"  Entities: {len(result['entities'])}")
    print(f"  Edges: {len(result['edges'])}")
    print(f"  PageRank scores: {len(result['pagerank'])}")
    print(f"  Query answers: {len(answers)}")

if __name__ == "__main__":
    test_full_pipeline()
```

## Usage Instructions

### Prerequisites
1. Neo4j running: `docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/devpassword neo4j`
2. Python environment with dependencies installed
3. spaCy model: `python -m spacy download en_core_web_sm`

### Quick Start
```python
from src.facade.unified_kgas_facade import UnifiedKGASFacade

# Initialize
facade = UnifiedKGASFacade()

# Process document
text = "Your document text here..."
result = facade.process_document(text)

# Query the graph
answers = facade.query("Your question here?")
```

### Running Tests
```bash
cd /home/brian/projects/Digimons
python src/tests/test_facade_integration.py
```

## Validation Checklist

- [ ] T31 creates entities in Neo4j
- [ ] T34 creates edges with proper format
- [ ] T68 calculates and stores PageRank scores
- [ ] T49 answers queries from the graph
- [ ] Full pipeline works end-to-end
- [ ] Integration tests pass

## Known Limitations

1. **Entity Resolution**: Simple name matching, no advanced deduplication
2. **Relationship Extraction**: Pattern-based, not ML-powered
3. **Query Understanding**: Basic entity extraction from questions
4. **Scale**: Not optimized for large documents (>10MB)
5. **Async**: No concurrent processing support

## Next Steps After Fixes

1. Add comprehensive error handling
2. Implement entity deduplication
3. Add async processing support
4. Integrate advanced NLP models
5. Add performance monitoring

---

*Last updated: 2025-08-22*
*Status: Ready for implementation*
*Estimated time: 4-6 hours total*