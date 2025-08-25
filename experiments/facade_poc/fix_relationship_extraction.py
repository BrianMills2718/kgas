#!/usr/bin/env python3
"""
Fix relationship extraction to find all relationships
Test Driven Design: Define expected relationships first
"""

import sys
import json
import re
from datetime import datetime
sys.path.insert(0, '/home/brian/projects/Digimons')

def extract_entities_improved(text: str) -> list:
    """Improved entity extraction that preserves punctuation"""
    entities = []
    
    # Pattern 1: Organization names with suffixes
    org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc\.|Corporation|Corp\.|LLC|Ltd\.))?'
    
    for match in re.finditer(org_pattern, text):
        entity_text = match.group(0)
        
        # Skip common words
        if entity_text.lower() in ['the', 'a', 'an', 'in', 'on', 'at', 'by', 'for', 'ceo']:
            continue
        
        # Determine entity type
        entity_type = "UNKNOWN"
        if any(suffix in entity_text for suffix in ['Inc.', 'Corporation', 'Corp.', 'LLC', 'Ltd.']):
            entity_type = "ORGANIZATION"
        elif len(entity_text.split()) <= 3 and not any(c.isdigit() for c in entity_text):
            entity_type = "PERSON"
        else:
            entity_type = "LOCATION"
        
        entities.append({
            "text": entity_text,
            "entity_type": entity_type,
            "start_pos": match.start(),
            "end_pos": match.end(),
            "confidence": 0.85,
            "entity_id": f"{entity_text.lower().replace(' ', '_').replace('.', '')}_{match.start()}",
            "canonical_name": entity_text
        })
    
    # Pattern 2: Years
    year_pattern = r'\b(19|20)\d{2}\b'
    for match in re.finditer(year_pattern, text):
        entities.append({
            "text": match.group(0),
            "entity_type": "DATE",
            "start_pos": match.start(),
            "end_pos": match.end(),
            "confidence": 0.95,
            "entity_id": f"date_{match.group(0)}",
            "canonical_name": match.group(0)
        })
    
    return entities

def extract_relationships_fixed(text: str, entities: list) -> list:
    """Fixed relationship extraction that handles entity variations"""
    relationships = []
    
    # Build entity lookup with variations
    entity_lookup = {}
    for e in entities:
        # Store with and without punctuation
        entity_lookup[e["text"].lower()] = e
        entity_lookup[e["text"].lower().replace('.', '')] = e
        entity_lookup[e["text"]] = e
    
    # Pattern 1: X, led by [CEO] Y
    pattern = r"([^,]+),\s*led by(?:\s+CEO)?\s+([^,]+)"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        source = match.group(1).strip()
        target = match.group(2).strip()
        
        # Remove "CEO" prefix from target if present
        target = re.sub(r'^CEO\s+', '', target, flags=re.IGNORECASE)
        
        # Check both variations
        source_found = (source in entity_lookup or 
                       source.lower() in entity_lookup or
                       source.replace('.', '') in entity_lookup)
        target_found = (target in entity_lookup or 
                       target.lower() in entity_lookup or
                       target.replace('.', '') in entity_lookup)
        
        if source_found and target_found:
            relationships.append({
                "source": source,
                "target": target,
                "relationship_type": "LED_BY",
                "confidence": 0.9
            })
    
    # Pattern 2: X is/are headquartered in Y (make is/are optional)
    pattern = r"([^,]+?)\s*,.*?(?:is\s+)?headquartered in\s+([^,\.]+)"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        source = match.group(1).strip()
        target = match.group(2).strip()
        
        source_found = (source in entity_lookup or 
                       source.lower() in entity_lookup or
                       source.replace('.', '') in entity_lookup)
        
        if source_found:
            relationships.append({
                "source": source,
                "target": target,
                "relationship_type": "HEADQUARTERED_IN",
                "confidence": 0.9
            })
    
    # Pattern 3: X was founded by Y [and Z]
    pattern = r"([^,]+)\s+was founded by\s+(.+?)(?:\s+in\s+\d{4})"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        org = match.group(1).strip()
        founders_text = match.group(2).strip()
        
        org_found = (org in entity_lookup or 
                    org.lower() in entity_lookup or
                    org.replace('.', '') in entity_lookup)
        
        if org_found:
            # Split on "and" to get multiple founders
            founders = re.split(r'\s+and\s+', founders_text)
            for founder in founders:
                founder = founder.strip()
                if founder and founder != "in":
                    relationships.append({
                        "source": org,
                        "target": founder,
                        "relationship_type": "FOUNDED_BY",
                        "confidence": 0.85
                    })
    
    # Pattern 4: X competes with Y [and Z]
    pattern = r"([^,]+)\s+competes with\s+(.+?)(?:\s+in\s+)"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        company = match.group(1).strip()
        competitors_text = match.group(2).strip()
        
        company_found = (company in entity_lookup or 
                        company.lower() in entity_lookup or
                        company.replace('.', '') in entity_lookup)
        
        if company_found:
            # Split on "and" to get multiple competitors
            competitors = re.split(r'\s+and\s+', competitors_text)
            for competitor in competitors:
                competitor = competitor.strip()
                if competitor:
                    relationships.append({
                        "source": company,
                        "target": competitor,
                        "relationship_type": "COMPETES_WITH",
                        "confidence": 0.8
                    })
    
    return relationships

def test_relationship_extraction():
    """Test that we find all expected relationships"""
    
    test_cases = [
        {
            "text": "Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino.",
            "expected_entities": ["Apple Inc.", "Tim Cook", "Cupertino"],
            "expected_relationships": [
                ("Apple Inc.", "LED_BY", "Tim Cook"),
                ("Apple Inc.", "HEADQUARTERED_IN", "Cupertino")
            ]
        },
        {
            "text": "Microsoft Corporation was founded by Bill Gates and Paul Allen in 1975.",
            "expected_entities": ["Microsoft Corporation", "Bill Gates", "Paul Allen", "1975"],
            "expected_relationships": [
                ("Microsoft Corporation", "FOUNDED_BY", "Bill Gates"),
                ("Microsoft Corporation", "FOUNDED_BY", "Paul Allen")
            ]
        },
        {
            "text": "Google competes with Microsoft and Apple in cloud services.",
            "expected_entities": ["Google", "Microsoft", "Apple"],
            "expected_relationships": [
                ("Google", "COMPETES_WITH", "Microsoft"),
                ("Google", "COMPETES_WITH", "Apple")
            ]
        }
    ]
    
    all_passed = True
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        expected_entities = test_case["expected_entities"]
        expected_relationships = test_case["expected_relationships"]
        
        print(f"\nTest Case {i}:")
        print(f"Text: {text}")
        
        # Extract entities
        entities = extract_entities_improved(text)
        entity_texts = [e["text"] for e in entities]
        
        print(f"Extracted entities: {entity_texts}")
        
        # Check entities
        entities_correct = 0
        for exp_entity in expected_entities:
            # Check exact match or close match
            found = any(
                exp_entity == e or 
                exp_entity.replace('.', '') == e.replace('.', '') 
                for e in entity_texts
            )
            if found:
                print(f"  ✅ Entity found: {exp_entity}")
                entities_correct += 1
            else:
                print(f"  ❌ Entity missing: {exp_entity}")
                all_passed = False
        
        # Extract relationships
        relationships = extract_relationships_fixed(text, entities)
        rel_tuples = [(r["source"], r["relationship_type"], r["target"]) for r in relationships]
        
        print(f"Extracted relationships: {rel_tuples}")
        
        # Check relationships
        relationships_correct = 0
        for exp_rel in expected_relationships:
            # Check with flexible matching
            found = any(
                (r[0] == exp_rel[0] or r[0].replace('.', '') == exp_rel[0].replace('.', '')) and
                r[1] == exp_rel[1] and
                (r[2] == exp_rel[2] or r[2].replace('.', '') == exp_rel[2].replace('.', ''))
                for r in rel_tuples
            )
            if found:
                print(f"  ✅ Relationship found: {exp_rel}")
                relationships_correct += 1
            else:
                print(f"  ❌ Relationship missing: {exp_rel}")
                all_passed = False
        
        # Calculate percentages
        entity_percent = (entities_correct / len(expected_entities) * 100) if expected_entities else 0
        rel_percent = (relationships_correct / len(expected_relationships) * 100) if expected_relationships else 0
        
        print(f"  Entity extraction: {entities_correct}/{len(expected_entities)} ({entity_percent:.0f}%)")
        print(f"  Relationship extraction: {relationships_correct}/{len(expected_relationships)} ({rel_percent:.0f}%)")
        
        results.append({
            "test_case": i,
            "entities_correct": entities_correct,
            "entities_total": len(expected_entities),
            "relationships_correct": relationships_correct,
            "relationships_total": len(expected_relationships),
            "entity_percentage": entity_percent,
            "relationship_percentage": rel_percent
        })
    
    return all_passed, results

def generate_evidence():
    """Generate evidence file for relationship extraction fix"""
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "operation": "relationship_extraction_fix",
        "tests": {},
        "success_criteria": {}
    }
    
    print("=" * 60)
    print("RELATIONSHIP EXTRACTION FIX")
    print("=" * 60)
    
    all_passed, results = test_relationship_extraction()
    
    evidence["tests"]["extraction_results"] = results
    
    # Calculate overall metrics
    total_entities_correct = sum(r["entities_correct"] for r in results)
    total_entities = sum(r["entities_total"] for r in results)
    total_relationships_correct = sum(r["relationships_correct"] for r in results)
    total_relationships = sum(r["relationships_total"] for r in results)
    
    entity_rate = total_entities_correct / total_entities if total_entities > 0 else 0
    relationship_rate = total_relationships_correct / total_relationships if total_relationships > 0 else 0
    
    evidence["metrics"] = {
        "entity_extraction_rate": entity_rate,
        "relationship_extraction_rate": relationship_rate,
        "entities_found": f"{total_entities_correct}/{total_entities}",
        "relationships_found": f"{total_relationships_correct}/{total_relationships}"
    }
    
    # Success criteria: 75%+ relationship extraction
    evidence["success_criteria"]["entities_extracted"] = entity_rate >= 0.9
    evidence["success_criteria"]["relationships_75_percent"] = relationship_rate >= 0.75
    evidence["success_criteria"]["all_tests_passed"] = all_passed
    
    # Save evidence
    import os
    os.makedirs("experiments/facade_poc/evidence", exist_ok=True)
    evidence_file = f"experiments/facade_poc/evidence/relationship_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(evidence_file, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"\n✅ Evidence saved to: {evidence_file}")
    
    return evidence

if __name__ == "__main__":
    evidence = generate_evidence()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    metrics = evidence.get("metrics", {})
    print(f"Entity extraction rate: {metrics.get('entity_extraction_rate', 0):.1%}")
    print(f"Relationship extraction rate: {metrics.get('relationship_extraction_rate', 0):.1%}")
    
    criteria = evidence.get("success_criteria", {})
    if criteria.get("relationships_75_percent"):
        print("✅ Relationship extraction meets 75% threshold")
    else:
        print("❌ Relationship extraction below 75% threshold")
    
    if criteria.get("all_tests_passed"):
        print("✅ All tests passed")
    else:
        print("⚠️ Some tests need improvement")