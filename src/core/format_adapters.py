"""Format adapters for tool compatibility - REAL IMPLEMENTATION"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FormatAdapter:
    """Production format adaptation - NOT mocked"""
    
    @staticmethod
    def t23c_to_t31(t23c_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert T23C output to T31 input format.
        REAL conversion, not stubbed.
        
        T23C output format:
        {
            "entity_id": "e1",
            "canonical_name": "Apple Inc.",
            "entity_type": "ORG",
            "confidence": 0.9
        }
        
        T31 input format:
        {
            "text": "Apple Inc.",
            "entity_type": "ORG",
            "confidence": 0.9,
            "start": 0,
            "end": 10
        }
        """
        mentions = []
        for entity in t23c_entities:
            # Required T31 fields
            mention = {
                "text": entity.get("canonical_name", ""),
                "entity_type": entity.get("entity_type", "UNKNOWN"),
                "confidence": entity.get("confidence", 0.5),
                "start": entity.get("start_pos", 0),
                "end": entity.get("end_pos", len(entity.get("canonical_name", "")))
            }
            
            # Preserve additional fields
            for key, value in entity.items():
                if key not in ["canonical_name", "entity_type", "confidence", "start_pos", "end_pos"]:
                    mention[f"t23c_{key}"] = value  # Prefix to avoid conflicts
            
            mentions.append(mention)
        
        return mentions
    
    @staticmethod
    def t31_to_t34(t31_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure T31 output has 'text' field for T34.
        REAL implementation.
        
        T31 output may not have 'text' field, only 'canonical_name'
        T34 requires 'text' field for entity display
        """
        adapted = []
        for entity in t31_entities:
            # Make a copy to avoid modifying original
            adapted_entity = entity.copy()
            
            # Ensure 'text' field exists
            if "text" not in adapted_entity:
                adapted_entity["text"] = adapted_entity.get("canonical_name", "")
            
            adapted.append(adapted_entity)
        
        return adapted
    
    @staticmethod
    def normalize_relationship(rel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize relationship format.
        Handles all variations found in codebase.
        
        Variations:
        - {source, target, type}
        - {subject, object, relationship_type}
        - {source_entity, target_entity, relationship}
        - {subject, object, predicate}
        
        Normalized to:
        - {subject, object, relationship_type, confidence}
        """
        normalized = {}
        
        # Map all variations for subject
        normalized["subject"] = (
            rel.get("subject") or 
            rel.get("source") or 
            rel.get("source_entity")
        )
        
        # Map all variations for object
        normalized["object"] = (
            rel.get("object") or 
            rel.get("target") or 
            rel.get("target_entity")
        )
        
        # Map all variations for relationship type
        normalized["relationship_type"] = (
            rel.get("relationship_type") or 
            rel.get("relationship") or 
            rel.get("predicate") or
            rel.get("type") or
            "RELATED_TO"
        )
        
        # Ensure confidence exists
        normalized["confidence"] = rel.get("confidence", 0.5)
        
        # Preserve other fields
        for key, value in rel.items():
            if key not in ["subject", "source", "source_entity",
                          "object", "target", "target_entity",
                          "relationship_type", "relationship", "predicate", "type",
                          "confidence"]:
                normalized[key] = value
        
        return normalized
    
    @staticmethod
    def wrap_for_tool_request(data: Any, operation: str = "execute") -> Dict[str, Any]:
        """
        Wrap data in ToolRequest-compatible format.
        """
        return {
            "input_data": data,
            "operation": operation,
            "parameters": {},
            "validation_mode": False
        }
    
    @staticmethod
    def unwrap_tool_response(response: Dict[str, Any]) -> Any:
        """
        Unwrap ToolResponse format to get actual data.
        
        Handles both:
        - {"success": True, "data": {...}}
        - Direct data dict
        """
        if isinstance(response, dict):
            if "success" in response:
                # Wrapped format with success indicator
                if response["success"]:
                    return response.get("data", {})
                else:
                    # Operation failed
                    error_msg = response.get('error') or response.get('error_message', 'Unknown error')
                    raise RuntimeError(f"Tool operation failed: {error_msg}")
            else:
                # Direct data format (no success field)
                return response
        else:
            # Non-dict response
            return response
    
    @staticmethod
    def convert_entity_mentions_to_t31(mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert entity mentions from various formats to T31 format.
        """
        t31_mentions = []
        for mention in mentions:
            t31_mention = {
                "text": mention.get("text") or mention.get("surface_form") or mention.get("canonical_name", ""),
                "entity_type": mention.get("entity_type") or mention.get("type", "UNKNOWN"),
                "confidence": mention.get("confidence", 0.5),
                "start": mention.get("start") or mention.get("start_pos", 0),
                "end": mention.get("end") or mention.get("end_pos", 0)
            }
            
            # Preserve entity_id if present
            if "entity_id" in mention:
                t31_mention["entity_id"] = mention["entity_id"]
            
            # Preserve any additional metadata
            for key, value in mention.items():
                if key not in ["text", "surface_form", "canonical_name", 
                              "entity_type", "type", "confidence",
                              "start", "start_pos", "end", "end_pos", "entity_id"]:
                    t31_mention[f"meta_{key}"] = value
            
            t31_mentions.append(t31_mention)
        
        return t31_mentions
    
    @staticmethod
    def convert_relationships_for_t34(relationships: List[Dict[str, Any]], 
                                     entity_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Convert relationships to T34 edge builder format.
        
        T34 expects:
        {
            "subject": {"text": "Apple", "entity_id": "...", "canonical_name": "Apple Inc."},
            "object": {"text": "Tim Cook", "entity_id": "...", "canonical_name": "Tim Cook"},
            "relationship_type": "LED_BY",
            "confidence": 0.85
        }
        """
        t34_relationships = []
        
        for rel in relationships:
            # Normalize the relationship first
            normalized = FormatAdapter.normalize_relationship(rel)
            
            # Build T34 format
            t34_rel = {
                "subject": FormatAdapter._format_entity_for_t34(
                    normalized["subject"], entity_map
                ),
                "object": FormatAdapter._format_entity_for_t34(
                    normalized["object"], entity_map
                ),
                "relationship_type": normalized["relationship_type"],
                "confidence": normalized["confidence"]
            }
            
            # Preserve additional fields
            for key, value in normalized.items():
                if key not in ["subject", "object", "relationship_type", "confidence"]:
                    t34_rel[key] = value
            
            t34_relationships.append(t34_rel)
        
        return t34_relationships
    
    @staticmethod
    def _format_entity_for_t34(entity: Any, entity_map: Dict[str, str]) -> Dict[str, Any]:
        """
        Format an entity reference for T34.
        Handles both string names and dict entities.
        """
        if isinstance(entity, str):
            # Simple string name
            entity_id = entity_map.get(entity, f"unknown_{entity}")
            return {
                "text": entity,
                "entity_id": entity_id,
                "canonical_name": entity
            }
        elif isinstance(entity, dict):
            # Already formatted entity
            return {
                "text": entity.get("text") or entity.get("canonical_name", ""),
                "entity_id": entity.get("entity_id", "unknown"),
                "canonical_name": entity.get("canonical_name") or entity.get("text", "")
            }
        else:
            # Unknown format
            return {
                "text": str(entity),
                "entity_id": "unknown",
                "canonical_name": str(entity)
            }

# Global instance for convenience
format_adapter = FormatAdapter()