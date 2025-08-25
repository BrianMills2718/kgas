"""
Relationship patterns for semantic extraction
"""
from typing import List, Dict

RELATIONSHIP_PATTERNS = [
    # Leadership patterns - more specific
    {
        "pattern": r"([A-Z][^,]+),\s+led by (?:CEO\s+)?([A-Z][^,\.]+)",
        "relationship": "LED_BY",
        "confidence": 0.9
    },
    {
        "pattern": r"([A-Z][^,]+),\s+(?:headed by|run by) (?:CEO\s+)?([A-Z][^,\.]+)",
        "relationship": "LED_BY", 
        "confidence": 0.85
    },
    {
        "pattern": r"CEO ([A-Z][^,\.]+).*?(?:of|at) ([A-Z][^,\.]+)",
        "relationship": "CEO_OF",
        "confidence": 0.9
    },
    # Foundation patterns
    {
        "pattern": r"([A-Z][^,]+)\s+was founded by ([A-Z][^,]+(?:,\s*[A-Z][^,]+)*)",
        "relationship": "FOUNDED_BY",
        "confidence": 0.9
    },
    {
        "pattern": r"founded by ([A-Z][^,]+(?:,\s*[A-Z][^,]+)*)",
        "relationship": "FOUNDED_BY",
        "confidence": 0.85
    },
    # Location patterns - more specific to avoid conflicts
    {
        "pattern": r"([A-Z][^,]+(?:\s+[A-Z][^,]*)*),\s+is (?:headquartered in|located in|based in) ([A-Z][^,\.]+)",
        "relationship": "HEADQUARTERED_IN",
        "confidence": 0.85
    },
    # Competition patterns
    {
        "pattern": r"([A-Z][^,]+)\s+competes with ([A-Z][^,\.]+)",
        "relationship": "COMPETES_WITH",
        "confidence": 0.8
    },
    # Acquisition patterns
    {
        "pattern": r"([A-Z][^,]+)\s+acquired ([A-Z][^,\.]+)",
        "relationship": "ACQUIRED",
        "confidence": 0.9
    },
    # Subsidiary patterns
    {
        "pattern": r"([A-Z][^,]+),\s+part of ([A-Z][^,\.]+)",
        "relationship": "SUBSIDIARY_OF",
        "confidence": 0.85
    },
    # Default fallback - less greedy
    {
        "pattern": r"([A-Z][A-Za-z\s]+)\s+(?:is|was)\s+([A-Z][A-Za-z\s]+)",
        "relationship": "RELATED_TO",
        "confidence": 0.5
    }
]

def extract_semantic_relationships(text: str, entities: List[Dict]) -> List[Dict]:
    """Extract relationships with semantic types"""
    relationships = []
    
    # Create entity lookup by surface form
    entity_lookup = {e["text"]: e for e in entities}
    
    # Split on sentences but preserve complex sentences
    sentences = text.split('.')
    
    # Also try the whole text as one unit for complex sentences
    all_text_units = [text] + sentences
    
    for sentence in all_text_units:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 10:
            continue
            
        # Try each pattern
        for pattern_info in RELATIONSHIP_PATTERNS:
            import re
            match = re.search(pattern_info["pattern"], sentence, re.IGNORECASE)
            if match:
                subj = match.group(1).strip()
                obj = match.group(2).strip() if match.lastindex >= 2 else ""
                
                # Clean up extracted text - remove non-entity parts
                subj = re.sub(r'.*?([A-Z][A-Za-z\s]+(?:Inc\.|Corporation|Corp\.)?)', r'\1', subj).strip()
                obj = re.sub(r'.*?([A-Z][A-Za-z\s]+)', r'\1', obj).strip()
                
                # Find matching entities
                subj_entity = find_best_entity_match(subj, entity_lookup)
                obj_entity = find_best_entity_match(obj, entity_lookup)
                
                if subj_entity and obj_entity and subj_entity != obj_entity:
                    relationships.append({
                        "source": subj_entity["text"],
                        "target": obj_entity["text"],
                        "relationship_type": pattern_info["relationship"],
                        "confidence": pattern_info["confidence"],
                        "evidence": sentence
                    })
                    break  # Use first matching pattern
    
    return relationships

def find_best_entity_match(text: str, entity_lookup: Dict) -> Dict:
    """Find best matching entity for text fragment"""
    # Exact match
    if text in entity_lookup:
        return entity_lookup[text]
    
    # Partial match
    for entity_text, entity in entity_lookup.items():
        if entity_text.lower() in text.lower() or text.lower() in entity_text.lower():
            return entity
    
    return None