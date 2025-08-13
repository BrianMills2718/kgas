#!/usr/bin/env python3
"""
LLM-Enhanced Entity Resolver
Integrates LLM-based entity resolution with the existing identity service
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .entity_resolver import EntityResolver, ExactMatcher, SimilarityMatcher
from .data_models import Entity, Mention
from src.services.llm_entity_resolver import (
    LLMEntityResolutionService,
    EntityResolution,
    MockEntityResolver
)

logger = logging.getLogger(__name__)


class LLMEnhancedEntityResolver(EntityResolver):
    """
    Enhanced entity resolver that uses LLM for improved entity resolution.
    Extends the existing EntityResolver to maintain backward compatibility.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with LLM resolution capability"""
        # Extract LLM-specific kwargs
        use_llm = kwargs.pop('use_llm', True)
        llm_provider = kwargs.pop('llm_provider', None)
        
        # Initialize parent class
        super().__init__(*args, **kwargs)
        
        # Initialize LLM resolution service
        self.use_llm = use_llm
        self.llm_service = None
        
        if self.use_llm:
            try:
                if llm_provider:
                    self.llm_service = LLMEntityResolutionService(provider=llm_provider)
                else:
                    self.llm_service = LLMEntityResolutionService()
                logger.info("LLM entity resolution service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM service, falling back to standard resolution: {e}")
                self.use_llm = False
    
    def resolve_entity(self, normalized_form: str, entity_type: Optional[str],
                      entities: Dict[str, Entity],
                      mention_id: Optional[str] = None) -> Tuple[str, bool]:
        """
        Resolve entity using LLM-enhanced resolution.
        Falls back to parent implementation if LLM not available.
        """
        
        # First try parent's resolution methods
        entity_id, was_created = super().resolve_entity(normalized_form, entity_type, entities, mention_id)
        
        # If no match found and LLM is available, try LLM resolution
        if not entity_id and self.use_llm and self.llm_service:
            llm_entity_id = self._resolve_with_llm(normalized_form, entity_type, entities)
            if llm_entity_id:
                return llm_entity_id, False
        
        return entity_id, was_created
    
    def _resolve_with_llm(self, normalized_form: str, entity_type: Optional[str], entities: Dict[str, Entity]) -> Optional[str]:
        """Use LLM to resolve entity when traditional methods fail"""
        
        try:
            # Prepare context for LLM
            context_text = f"{normalized_form} (type: {entity_type or 'unknown'})"
            
            # Get existing entities for coreference
            existing_entities = [
                {
                    'canonical_name': entity.canonical_name,
                    'entity_type': entity.entity_type,
                    'confidence': entity.confidence
                }
                for entity in entities.values()
            ]
            
            # Use LLM to resolve
            resolutions = self.llm_service.provider.resolve_entities(context_text, existing_entities)
            
            if not resolutions:
                return None
            
            # Find best match from resolutions
            best_resolution = resolutions[0]  # Take highest confidence
            
            # Check if this matches an existing entity
            for entity_id, entity in entities.items():
                # Check canonical name similarity
                if self._names_match(best_resolution.canonical_name, entity.canonical_name):
                    logger.debug(f"LLM matched '{mention.surface_form}' to existing entity '{entity.canonical_name}'")
                    return entity_id
            
            # If no existing entity matches, this might be a new entity
            # Let the parent create it if needed
            return None
            
        except Exception as e:
            logger.warning(f"LLM resolution failed for '{mention.surface_form}': {e}")
            return None
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two names refer to the same entity"""
        
        # Exact match
        if name1.lower() == name2.lower():
            return True
        
        # Last name match for persons
        parts1 = name1.split()
        parts2 = name2.split()
        
        if len(parts1) > 0 and len(parts2) > 0:
            # Check if last names match
            if parts1[-1].lower() == parts2[-1].lower():
                return True
        
        # Check if one is substring of other (e.g., "NASA" in "NASA Administration")
        if name1.lower() in name2.lower() or name2.lower() in name1.lower():
            return True
        
        return False
    
    def find_similar_entities(self, normalized_form: str, entities: Dict[str, Entity],
                            max_results: int = 10,
                            min_similarity: float = 0.75) -> List[Tuple[str, float]]:
        """
        Find similar entities using both embeddings and LLM.
        Returns list of (entity_id, similarity_score) tuples.
        """
        
        # Get results from parent implementation
        results = super().find_similar_entities(normalized_form, entities, max_results, min_similarity)
        
        # Enhance with LLM if available and no good matches found
        if self.use_llm and self.llm_service and (not results or results[0][1] < 0.9):
            llm_results = self._find_similar_with_llm(normalized_form, entities)
            
            # Merge results, preferring higher scores
            merged = {}
            for entity_id, score in results:
                merged[entity_id] = score
            
            for entity_id, score in llm_results:
                if entity_id not in merged or score > merged[entity_id]:
                    merged[entity_id] = score
            
            # Sort and return top results
            results = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:max_results]
        
        return results
    
    def _find_similar_with_llm(self, normalized_form: str, entities: Dict[str, Entity]) -> List[Tuple[str, float]]:
        """Use LLM to find similar entities"""
        
        try:
            # Use LLM to identify potential matches
            resolutions = self.llm_service.provider.resolve_entities(normalized_form)
            
            results = []
            for resolution in resolutions:
                # Find matching entities
                for entity_id, entity in entities.items():
                    if self._names_match(resolution.canonical_name, entity.canonical_name):
                        results.append((entity_id, resolution.confidence))
            
            return results
            
        except Exception as e:
            logger.warning(f"LLM similarity search failed: {e}")
            return []
    
    def get_resolution_confidence(self, mention: Mention, entity: Entity) -> float:
        """
        Calculate confidence score for entity resolution.
        Enhanced with LLM-based confidence assessment.
        """
        
        # Get base confidence from parent
        base_confidence = super().get_resolution_confidence(mention, entity)
        
        # Enhance with LLM confidence if available
        if self.use_llm and self.llm_service and base_confidence < 0.9:
            llm_confidence = self._get_llm_confidence(mention, entity)
            
            # Weighted average (favor LLM for ambiguous cases)
            if base_confidence < 0.7:
                # Low base confidence, trust LLM more
                return 0.3 * base_confidence + 0.7 * llm_confidence
            else:
                # High base confidence, use LLM as verification
                return 0.7 * base_confidence + 0.3 * llm_confidence
        
        return base_confidence
    
    def _get_llm_confidence(self, mention: Mention, entity: Entity) -> float:
        """Get LLM's confidence that mention refers to entity"""
        
        try:
            # Ask LLM to verify the match
            context = f"Does '{mention.surface_form}' refer to '{entity.canonical_name}'? Context: {mention.context[:200] if mention.context else 'No context'}"
            
            resolutions = self.llm_service.provider.resolve_entities(context)
            
            # Check if LLM identified the same entity
            for resolution in resolutions:
                if self._names_match(resolution.canonical_name, entity.canonical_name):
                    return resolution.confidence
            
            # No match found, low confidence
            return 0.3
            
        except Exception as e:
            logger.warning(f"LLM confidence assessment failed: {e}")
            # Return neutral confidence on error
            return 0.5