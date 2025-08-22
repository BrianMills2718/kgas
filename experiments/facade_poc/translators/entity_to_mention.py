"""
Entity to Mention Translator

Critical translation layer that converts T23C's resolved entities 
back into mentions that T31 expects.

This is a lossy conversion - we lose:
- Original text positions
- Surface form variations
- Context information

But it's necessary to bridge the conceptual gap between tools.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EntityToMentionTranslator:
    """
    Translates resolved entities (from T23C) to raw mentions (for T31).
    
    The fundamental incompatibility:
    - T23C outputs: Resolved, deduplicated Entity objects
    - T31 expects: Raw Mention objects with text positions
    
    This translator bridges that gap, even if imperfectly.
    """
    
    def translate(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert entities to mentions.
        
        Args:
            entities: List of entity dicts from T23C with structure:
                {
                    'id': 'entity_123',
                    'canonical_name': 'John Smith',
                    'entity_type': 'PERSON',
                    'confidence': 0.95,
                    'attributes': {...}
                }
        
        Returns:
            List of mention dicts for T31 with structure:
                {
                    'text': 'John Smith',
                    'entity_type': 'PERSON',
                    'start_pos': 0,  # Synthetic
                    'end_pos': 10,   # Synthetic
                    'confidence': 0.95
                }
        """
        mentions = []
        
        for entity in entities:
            # Extract what we can from the entity
            canonical_name = entity.get('canonical_name', '')
            entity_type = entity.get('entity_type', 'UNKNOWN')
            confidence = entity.get('confidence', 0.8)
            
            # Check if entity has stored mention information
            # Some T23C implementations might preserve this
            if 'mentions' in entity:
                # Use preserved mention data if available
                for mention_data in entity['mentions']:
                    mention = self._create_mention_from_data(mention_data, entity_type, confidence)
                    mentions.append(mention)
            else:
                # Create synthetic mention from entity
                mention = self._create_synthetic_mention(canonical_name, entity_type, confidence)
                mentions.append(mention)
        
        logger.info(f"Translated {len(entities)} entities to {len(mentions)} mentions")
        return mentions
    
    def _create_mention_from_data(self, mention_data: Dict, entity_type: str, confidence: float) -> Dict:
        """Create mention from preserved mention data."""
        return {
            'text': mention_data.get('surface_text', mention_data.get('text', '')),
            'entity_type': entity_type,
            'start_pos': mention_data.get('start_pos', 0),
            'end_pos': mention_data.get('end_pos', 0),
            'confidence': mention_data.get('confidence', confidence),
            'source_ref': mention_data.get('source_ref', 'unknown')
        }
    
    def _create_synthetic_mention(self, canonical_name: str, entity_type: str, confidence: float) -> Dict:
        """Create synthetic mention when position data is lost."""
        return {
            'text': canonical_name,
            'entity_type': entity_type,
            'start_pos': 0,  # Lost this information
            'end_pos': len(canonical_name),  # Synthetic
            'confidence': confidence,
            'source_ref': 'synthetic'  # Mark as synthetic
        }
    
    def translate_with_context(self, entities: List[Dict], original_text: str = None) -> List[Dict]:
        """
        Enhanced translation that attempts to recover position information.
        
        If we have the original text, we can try to find where entities appear.
        """
        mentions = []
        
        for entity in entities:
            canonical_name = entity.get('canonical_name', '')
            entity_type = entity.get('entity_type', 'UNKNOWN')
            confidence = entity.get('confidence', 0.8)
            
            if original_text and canonical_name:
                # Try to find entity in original text
                position = original_text.find(canonical_name)
                if position != -1:
                    mention = {
                        'text': canonical_name,
                        'entity_type': entity_type,
                        'start_pos': position,
                        'end_pos': position + len(canonical_name),
                        'confidence': confidence,
                        'source_ref': 'recovered'
                    }
                else:
                    # Not found in text, create synthetic
                    mention = self._create_synthetic_mention(canonical_name, entity_type, confidence)
            else:
                # No context, create synthetic
                mention = self._create_synthetic_mention(canonical_name, entity_type, confidence)
            
            mentions.append(mention)
        
        return mentions


class MentionToEntityTranslator:
    """
    Reverse translator: Converts mentions (from T31) back to entities.
    
    This is used when we need to normalize T31 output for other tools.
    """
    
    def translate(self, mentions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert mentions to entities by grouping and deduplicating.
        
        Args:
            mentions: List of mention dicts from T31
        
        Returns:
            List of entity dicts
        """
        # Group mentions by text and type
        entity_groups = {}
        
        for mention in mentions:
            key = (mention.get('text', ''), mention.get('entity_type', 'UNKNOWN'))
            
            if key not in entity_groups:
                entity_groups[key] = {
                    'canonical_name': mention['text'],
                    'entity_type': mention['entity_type'],
                    'mentions': [],
                    'confidence': 0.0
                }
            
            entity_groups[key]['mentions'].append(mention)
            # Average confidence across mentions
            entity_groups[key]['confidence'] = max(
                entity_groups[key]['confidence'],
                mention.get('confidence', 0.5)
            )
        
        # Convert to entity list
        entities = []
        for i, ((text, etype), group) in enumerate(entity_groups.items()):
            entity = {
                'id': f'entity_{i}',
                'canonical_name': text,
                'entity_type': etype,
                'confidence': group['confidence'],
                'mention_count': len(group['mentions'])
            }
            entities.append(entity)
        
        logger.info(f"Translated {len(mentions)} mentions to {len(entities)} entities")
        return entities