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