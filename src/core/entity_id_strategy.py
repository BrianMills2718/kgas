"""
Entity ID Generation Strategy

Defines the system-wide strategy for entity ID generation and management
to ensure consistent IDs throughout the pipeline for provenance tracking.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import hashlib
import uuid
from enum import Enum


class EntityIDStrategy(Enum):
    """Entity ID generation strategies."""
    UUID = "uuid"  # Random UUIDs
    CONTENT_HASH = "content_hash"  # Deterministic based on content
    HIERARCHICAL = "hierarchical"  # Based on source hierarchy
    EXTERNAL = "external"  # Use externally provided IDs


class EntityIDGenerator(ABC):
    """Abstract base class for entity ID generation."""
    
    @abstractmethod
    def generate_entity_id(self, entity_data: Dict[str, Any]) -> str:
        """Generate a unique entity ID."""
        pass
    
    @abstractmethod
    def generate_mention_id(self, mention_data: Dict[str, Any]) -> str:
        """Generate a unique mention ID."""
        pass
    
    @abstractmethod
    def generate_relationship_id(self, relationship_data: Dict[str, Any]) -> str:
        """Generate a unique relationship ID."""
        pass


class ContentBasedIDGenerator(EntityIDGenerator):
    """
    Generate deterministic IDs based on content.
    Same content always generates the same ID.
    """
    
    def generate_entity_id(self, entity_data: Dict[str, Any]) -> str:
        """Generate entity ID based on canonical name and type."""
        canonical_name = entity_data.get("canonical_name", "").lower().strip()
        entity_type = entity_data.get("entity_type", "UNKNOWN")
        
        # Create deterministic hash
        content = f"{entity_type}:{canonical_name}"
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        short_hash = hash_obj.hexdigest()[:12]
        
        return f"entity_{short_hash}"
    
    def generate_mention_id(self, mention_data: Dict[str, Any]) -> str:
        """Generate mention ID based on surface form and position."""
        surface_form = mention_data.get("surface_form", "")
        source_ref = mention_data.get("source_ref", "")
        start_pos = mention_data.get("start_pos", 0)
        
        # Create deterministic hash including position
        content = f"{source_ref}:{start_pos}:{surface_form}"
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        short_hash = hash_obj.hexdigest()[:12]
        
        return f"mention_{short_hash}"
    
    def generate_relationship_id(self, relationship_data: Dict[str, Any]) -> str:
        """Generate relationship ID based on source, target, and type."""
        source_id = relationship_data.get("source_id", "")
        target_id = relationship_data.get("target_id", "")
        rel_type = relationship_data.get("relationship_type", "")
        
        # Create deterministic hash
        content = f"{source_id}:{rel_type}:{target_id}"
        hash_obj = hashlib.sha256(content.encode('utf-8'))
        short_hash = hash_obj.hexdigest()[:12]
        
        return f"rel_{short_hash}"


class UUIDGenerator(EntityIDGenerator):
    """Generate random UUIDs for all IDs."""
    
    def generate_entity_id(self, entity_data: Dict[str, Any]) -> str:
        return f"entity_{uuid.uuid4().hex[:12]}"
    
    def generate_mention_id(self, mention_data: Dict[str, Any]) -> str:
        return f"mention_{uuid.uuid4().hex[:12]}"
    
    def generate_relationship_id(self, relationship_data: Dict[str, Any]) -> str:
        return f"rel_{uuid.uuid4().hex[:12]}"


class HierarchicalIDGenerator(EntityIDGenerator):
    """Generate IDs based on source hierarchy."""
    
    def __init__(self, system_id: str = "kgas"):
        self.system_id = system_id
        self.counters = {
            "entity": 0,
            "mention": 0,
            "relationship": 0
        }
    
    def generate_entity_id(self, entity_data: Dict[str, Any]) -> str:
        entity_type = entity_data.get("entity_type", "UNKNOWN")
        source_ref = entity_data.get("source_ref", "unknown")
        
        self.counters["entity"] += 1
        
        # Hierarchical ID: system/source/type/counter
        return f"{self.system_id}/{source_ref}/{entity_type}/e{self.counters['entity']:06d}"
    
    def generate_mention_id(self, mention_data: Dict[str, Any]) -> str:
        source_ref = mention_data.get("source_ref", "unknown")
        
        self.counters["mention"] += 1
        
        return f"{self.system_id}/{source_ref}/m{self.counters['mention']:06d}"
    
    def generate_relationship_id(self, relationship_data: Dict[str, Any]) -> str:
        source_ref = relationship_data.get("source_ref", "unknown")
        
        self.counters["relationship"] += 1
        
        return f"{self.system_id}/{source_ref}/r{self.counters['relationship']:06d}"


class EntityIDManager:
    """
    Centralized entity ID management for the entire system.
    
    This ensures consistent ID generation and tracking across all tools.
    """
    
    def __init__(self, strategy: EntityIDStrategy = EntityIDStrategy.CONTENT_HASH):
        self.strategy = strategy
        self.generator = self._create_generator(strategy)
        self.id_registry = {}  # Track generated IDs
    
    def _create_generator(self, strategy: EntityIDStrategy) -> EntityIDGenerator:
        """Create the appropriate ID generator based on strategy."""
        if strategy == EntityIDStrategy.UUID:
            return UUIDGenerator()
        elif strategy == EntityIDStrategy.CONTENT_HASH:
            return ContentBasedIDGenerator()
        elif strategy == EntityIDStrategy.HIERARCHICAL:
            return HierarchicalIDGenerator()
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")
    
    def get_or_create_entity_id(self, entity_data: Dict[str, Any]) -> str:
        """
        Get existing entity ID or create new one.
        
        This is the ONLY place entity IDs should be generated.
        """
        # Check if ID already provided (external strategy)
        if "entity_id" in entity_data and self.strategy == EntityIDStrategy.EXTERNAL:
            return entity_data["entity_id"]
        
        # For content-based strategy, check if we've seen this entity before
        if self.strategy == EntityIDStrategy.CONTENT_HASH:
            temp_id = self.generator.generate_entity_id(entity_data)
            
            # Check registry
            registry_key = f"{entity_data.get('entity_type', 'UNKNOWN')}:{entity_data.get('canonical_name', '')}"
            if registry_key in self.id_registry:
                return self.id_registry[registry_key]
            else:
                self.id_registry[registry_key] = temp_id
                return temp_id
        
        # Generate new ID
        return self.generator.generate_entity_id(entity_data)
    
    def get_or_create_mention_id(self, mention_data: Dict[str, Any]) -> str:
        """Get existing mention ID or create new one."""
        if "mention_id" in mention_data and self.strategy == EntityIDStrategy.EXTERNAL:
            return mention_data["mention_id"]
        
        return self.generator.generate_mention_id(mention_data)
    
    def get_or_create_relationship_id(self, relationship_data: Dict[str, Any]) -> str:
        """Get existing relationship ID or create new one."""
        if "relationship_id" in relationship_data and self.strategy == EntityIDStrategy.EXTERNAL:
            return relationship_data["relationship_id"]
        
        return self.generator.generate_relationship_id(relationship_data)
    
    def register_id_mapping(self, internal_id: str, external_id: str):
        """Register a mapping between internal and external IDs."""
        self.id_registry[f"mapping:{internal_id}"] = external_id
        self.id_registry[f"reverse:{external_id}"] = internal_id
    
    def get_id_mapping(self, id_value: str) -> Optional[str]:
        """Get mapped ID if exists."""
        # Check forward mapping
        mapped = self.id_registry.get(f"mapping:{id_value}")
        if mapped:
            return mapped
        
        # Check reverse mapping
        return self.id_registry.get(f"reverse:{id_value}")


# Global instance for system-wide use
_entity_id_manager = None


def get_entity_id_manager() -> EntityIDManager:
    """Get the global entity ID manager instance."""
    global _entity_id_manager
    if _entity_id_manager is None:
        # Default to content-based for deterministic IDs
        _entity_id_manager = EntityIDManager(EntityIDStrategy.CONTENT_HASH)
    return _entity_id_manager


def set_entity_id_strategy(strategy: EntityIDStrategy):
    """Set the global entity ID generation strategy."""
    global _entity_id_manager
    _entity_id_manager = EntityIDManager(strategy)


# Usage in tools:
"""
from src.core.entity_id_strategy import get_entity_id_manager

# In T23c when creating entities:
id_manager = get_entity_id_manager()
entity_id = id_manager.get_or_create_entity_id({
    "canonical_name": "Dr. Sarah Chen",
    "entity_type": "PERSON"
})

# In T31 when processing mentions:
id_manager = get_entity_id_manager()
# Use the SAME id_manager to ensure consistent IDs
entity_id = id_manager.get_or_create_entity_id({
    "canonical_name": mention['text'],
    "entity_type": mention['entity_type']
})
"""