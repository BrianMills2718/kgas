# KGAS Tool Integration - Complete Implementation Guide

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them  
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **TEST DRIVEN DESIGN**: Write tests first, then implementation
- **LLM-FIRST EXTRACTION**: Use real LLMs (Gemini-2.5-flash via LiteLLM), NO SpaCy fallbacks

### Evidence Requirements
Every implementation MUST generate evidence files with ACTUAL data:
```json
{
  "timestamp": "ISO-8601",
  "test_name": "descriptive_name",
  "status": "success|failure",
  "llm_model": "gemini-2.5-flash",
  "raw_llm_response": "actual LLM output",
  "extracted_entities": ["actual", "entities", "from", "LLM"],
  "assertions": [
    {"test": "description", "passed": true/false, "actual": "value", "expected": "value"}
  ]
}
```

---

## 2. Environment Setup

### Prerequisites
```bash
# Check these are installed:
docker ps | grep neo4j  # Neo4j must be running on port 7687
pip list | grep litellm  # LiteLLM must be installed (current: 1.74.14)
ls -la .env | grep GEMINI_API_KEY  # API key must be present
```

### Required Services
1. **Neo4j Database**
   - Running in Docker on port 7687
   - Credentials: neo4j/devpassword
   - Test connection: `docker exec neo4j cypher-shell -u neo4j -p devpassword "RETURN 1"`

2. **LiteLLM Configuration**
   - Model: `gemini/gemini-2.5-flash` (note the gemini/ prefix)
   - API Key: In `.env` file as `GEMINI_API_KEY`
   - Test: `python3 -c "import litellm; print(litellm.__version__)"`

---

## 3. Current Status (2025-08-24)

### ✅ Interface Issues Fixed
Located in these files:
- `/src/core/tool_contract.py` - ToolRequest has required fields
- `/src/core/service_manager.py` - Identity service fails without Neo4j
- `/src/core/format_adapters.py` - 7 conversion functions implemented

### ❌ Real Functionality NOT Yet Validated
- T23C never called real LLM (only used hardcoded test data)
- Never processed the fictional test document
- Never built knowledge graph from LLM-extracted entities
- Never answered queries using the graph

### ⚠️ Critical Gap
**We fixed the plumbing but haven't run water through the pipes**

---

## 4. Implementation Instructions

### STEP 1: Create LLM Extractor

**File to create**: `/src/tools/phase2/t23c_llm_extractor.py`

```python
#!/usr/bin/env python3
"""T23C LLM Extractor using Gemini-2.5-flash - NO FALLBACKS"""

import os
import sys
import json
import litellm
from dotenv import load_dotenv
from typing import Dict, List, Any
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

class T23CLLMExtractor:
    """Extract entities using REAL LLM - no mocks, no fallbacks"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY required - no fallbacks allowed")
        
        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params
        self.model = "gemini/gemini-2.5-flash"  # Note: gemini/ prefix required
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships using Gemini-2.5-flash"""
        
        # Build extraction prompt
        prompt = """You are an expert at extracting entities and relationships from text.
        
Extract ALL entities and relationships from the following text.

Return a valid JSON object with this exact structure:
{
    "entities": [
        {"name": "entity name", "type": "PERSON|ORG|LOC|PRODUCT", "confidence": 0.95}
    ],
    "relationships": [
        {"source": "entity1", "relation": "LED_BY|HEADQUARTERED_IN|ACQUIRED|etc", "target": "entity2", "confidence": 0.9}
    ]
}

Important:
- Extract ALL entities mentioned (people, companies, locations, products)
- Include confidence scores (0.0-1.0)
- Use consistent entity names across entities and relationships
- Common relations: LED_BY, FOUNDED_BY, HEADQUARTERED_IN, ACQUIRED, WORKS_FOR, BASED_IN, PARTNERED_WITH

Text to analyze:
""" + text

        try:
            # Call LLM via LiteLLM
            response = litellm.completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a precise entity extraction system. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            # Extract content from response
            llm_output = response.choices[0].message.content
            
            # Parse JSON from LLM response
            # Handle potential markdown code blocks
            if "```json" in llm_output:
                json_str = llm_output.split("```json")[1].split("```")[0].strip()
            elif "```" in llm_output:
                json_str = llm_output.split("```")[1].split("```")[0].strip()
            else:
                json_str = llm_output.strip()
            
            extracted_data = json.loads(json_str)
            
            # Add metadata
            result = {
                "extraction_timestamp": datetime.now().isoformat(),
                "model": self.model,
                "text_length": len(text),
                "entities": extracted_data.get("entities", []),
                "relationships": extracted_data.get("relationships", []),
                "raw_llm_response": llm_output
            }
            
            return result
            
        except json.JSONDecodeError as e:
            raise RuntimeError(f"LLM returned invalid JSON: {e}\nResponse: {llm_output}")
        except Exception as e:
            raise RuntimeError(f"LLM extraction failed: {e}")
```

### STEP 2: Create Pipeline Integration

**File to create**: `/src/pipeline/kgas_pipeline.py`

```python
#!/usr/bin/env python3
"""KGAS Pipeline - Document → Entities → Graph → Query"""

import os
import sys
from typing import Dict, Any, List

sys.path.insert(0, '/home/brian/projects/Digimons')

from src.tools.phase2.t23c_llm_extractor import T23CLLMExtractor
from src.core.service_manager import ServiceManager
from src.core.format_adapters import FormatAdapter
from neo4j import GraphDatabase

class KGASPipeline:
    """Full pipeline: Document → LLM → Entities → Neo4j → Query"""
    
    def __init__(self):
        # Initialize components
        self.llm_extractor = T23CLLMExtractor()
        self.service_manager = ServiceManager()
        self.format_adapter = FormatAdapter()
        
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
```

### STEP 3: Create End-to-End Test

**File to create**: `/tests/test_real_llm_pipeline.py`

```python
#!/usr/bin/env python3
"""Test KGAS Pipeline with REAL LLM and fictional data"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

from src.pipeline.kgas_pipeline import KGASPipeline

def test_nexora_pipeline():
    """Full pipeline test with fictional Nexora Technologies document"""
    
    print("=" * 60)
    print("KGAS PIPELINE TEST WITH REAL LLM")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = KGASPipeline()
    
    # Load fictional document
    with open("test_data/nexora_technologies.txt", "r") as f:
        document = f.read()
    
    print(f"\n1. Document loaded: {len(document)} characters")
    print(f"   First 100 chars: {document[:100]}...")
    
    # Process document through pipeline
    print("\n2. Processing document through pipeline...")
    results = pipeline.process_document(document)
    
    # Validate LLM extraction
    print("\n3. Validating LLM extraction...")
    entities = results["llm_extraction"]["entities"]
    relationships = results["llm_extraction"]["relationships"]
    
    print(f"   Entities found: {len(entities)}")
    print(f"   Relationships found: {len(relationships)}")
    
    # Check for expected fictional entities
    entity_names = [e["name"] for e in entities]
    expected_entities = ["Nexora Technologies", "Zara Klingston", "Velmont City"]
    
    for expected in expected_entities:
        found = any(expected in name for name in entity_names)
        print(f"   ✓ Found '{expected}': {found}")
        assert found, f"Missing expected entity: {expected}"
    
    # Test queries
    print("\n4. Testing queries...")
    queries = [
        "Who leads Nexora Technologies?",
        "Where is Nexora Technologies headquartered?",
    ]
    
    query_results = []
    for query in queries:
        print(f"\n   Query: {query}")
        answer = pipeline.query(query)
        query_results.append(answer)
        
        if answer["answers"]:
            for ans in answer["answers"]:
                print(f"   Answer: {ans['answer']}")
        else:
            print("   No answer found")
    
    # Validate specific answers
    print("\n5. Validating answers...")
    
    # Query 1: Who leads Nexora?
    q1_answer = query_results[0]
    assert q1_answer["answers"], "No answer for leadership query"
    assert "Zara Klingston" in q1_answer["answers"][0]["answer"], \
        f"Wrong leader: {q1_answer['answers'][0]['answer']}"
    print("   ✓ Correctly identified Zara Klingston as leader")
    
    # Query 2: Where is Nexora headquartered?
    q2_answer = query_results[1]
    assert q2_answer["answers"], "No answer for location query"
    assert "Velmont City" in q2_answer["answers"][0]["answer"], \
        f"Wrong location: {q2_answer['answers'][0]['answer']}"
    print("   ✓ Correctly identified Velmont City as headquarters")
    
    # Generate evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "nexora_pipeline_e2e",
        "status": "success",
        "llm_model": results["llm_extraction"]["model"],
        "document_length": len(document),
        "entities_extracted": len(entities),
        "relationships_extracted": len(relationships),
        "entities_stored": results["pipeline_stages"][1]["entities_stored"],
        "relationships_stored": results["pipeline_stages"][2]["relationships_stored"],
        "sample_entities": entity_names[:10],
        "queries_tested": len(queries),
        "queries_answered": sum(1 for q in query_results if q["answers"]),
        "validation": {
            "found_nexora": "Nexora Technologies" in entity_names,
            "found_zara": "Zara Klingston" in entity_names,
            "correct_leader": "Zara Klingston" in str(query_results[0]),
            "correct_location": "Velmont City" in str(query_results[1])
        }
    }
    
    # Save evidence
    os.makedirs("evidence", exist_ok=True)
    with open("evidence/pipeline_end_to_end.json", "w") as f:
        json.dump(evidence, f, indent=2)
    
    # Save raw LLM response
    with open("evidence/llm_extraction_nexora.json", "w") as f:
        json.dump(results["llm_extraction"], f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE TEST SUCCESSFUL")
    print("Evidence saved to:")
    print("  - evidence/pipeline_end_to_end.json")
    print("  - evidence/llm_extraction_nexora.json")
    print("=" * 60)
    
    # Cleanup
    pipeline.cleanup()
    
    return True

if __name__ == "__main__":
    success = test_nexora_pipeline()
    exit(0 if success else 1)
```

---

## 5. Test Data Location

### Fictional Test Document
**File**: `/test_data/nexora_technologies.txt`

This file contains a completely fictional company (Nexora Technologies) with fictional people and locations. This ensures the LLM is actually extracting entities, not using general knowledge about real companies.

Key fictional entities to extract:
- Nexora Technologies (company)
- Zara Klingston (CEO)
- Velmont City, New Arcadia (headquarters)
- CyberDyne Solutions (competitor)
- Marcus Reeves (competitor's CEO)

---

## 6. Execution Instructions

### Step-by-Step Execution

```bash
# 1. Verify environment
cd /home/brian/projects/Digimons
cat .env | grep GEMINI_API_KEY  # Must show API key

# 2. Check Neo4j is running
docker ps | grep neo4j
docker exec neo4j cypher-shell -u neo4j -p devpassword "MATCH (n) RETURN count(n)"

# 3. Create the implementation files
# Create: src/tools/phase2/t23c_llm_extractor.py (code above)
# Create: src/pipeline/kgas_pipeline.py (code above)
# Create: tests/test_real_llm_pipeline.py (code above)

# 4. Run the test
python3 tests/test_real_llm_pipeline.py

# 5. Verify evidence generated
ls -la evidence/pipeline_end_to_end.json
ls -la evidence/llm_extraction_nexora.json
cat evidence/pipeline_end_to_end.json | jq .validation
```

### Expected Output
```
KGAS PIPELINE TEST WITH REAL LLM
============================================================
1. Document loaded: 1053 characters
2. Processing document through pipeline...
3. Validating LLM extraction...
   Entities found: 15+
   ✓ Found 'Nexora Technologies': True
   ✓ Found 'Zara Klingston': True
4. Testing queries...
   Query: Who leads Nexora Technologies?
   Answer: Nexora Technologies is led by Zara Klingston
5. Validating answers...
   ✓ Correctly identified Zara Klingston as leader
✅ PIPELINE TEST SUCCESSFUL
```

---

## 7. Troubleshooting

### Common Issues and Solutions

1. **GEMINI_API_KEY not found**
   ```bash
   echo 'GEMINI_API_KEY=your_key_here' >> .env
   ```

2. **Neo4j connection refused**
   ```bash
   docker start neo4j
   # Wait 30 seconds for startup
   ```

3. **LiteLLM import error**
   ```bash
   pip install --break-system-packages litellm
   ```

4. **JSON parsing error from LLM**
   - Check the raw response in evidence/llm_extraction_nexora.json
   - The LLM might be returning markdown-wrapped JSON

5. **No entities extracted**
   - Verify API key is valid
   - Check rate limits
   - Try with shorter document first

---

## 8. Success Criteria Checklist

A new LLM implementing this should verify:

- [ ] GEMINI_API_KEY is in .env file
- [ ] Neo4j is running with password "devpassword"
- [ ] LiteLLM is installed (pip list | grep litellm)
- [ ] test_data/nexora_technologies.txt exists
- [ ] T23CLLMExtractor makes real API calls to Gemini
- [ ] Pipeline stores entities in Neo4j
- [ ] Queries return correct answers about fictional companies
- [ ] Evidence files are generated with actual LLM responses
- [ ] NO SpaCy fallbacks used
- [ ] NO mock data used

---

## 9. File Structure Summary

```
/home/brian/projects/Digimons/
├── .env                                    # Contains GEMINI_API_KEY
├── CLAUDE.md                              # This file
├── test_data/
│   └── nexora_technologies.txt           # Fictional test document
├── src/
│   ├── core/
│   │   ├── tool_contract.py              # Has ToolRequest with required fields
│   │   ├── service_manager.py            # Identity service (fails without Neo4j)
│   │   └── format_adapters.py            # Format conversion utilities
│   ├── tools/
│   │   └── phase2/
│   │       └── t23c_llm_extractor.py     # TO CREATE: LLM extraction
│   └── pipeline/
│       └── kgas_pipeline.py              # TO CREATE: Full pipeline
├── tests/
│   └── test_real_llm_pipeline.py         # TO CREATE: End-to-end test
└── evidence/
    ├── pipeline_end_to_end.json          # Will be generated
    └── llm_extraction_nexora.json        # Will be generated
```

---

*Last Updated: 2025-08-24*
*Status: Ready for implementation by any LLM with only this file*
*No additional context required*