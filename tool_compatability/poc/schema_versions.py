"""
Schema Versioning System - Handle schema evolution without breaking tools
PhD Research: Maintaining compatibility as schemas evolve
"""

from typing import Dict, Any, Optional, List, Tuple, Callable
from pydantic import BaseModel, Field
from abc import ABC


def compare_versions(v1: str, v2: str) -> int:
    """
    Compare two version strings.
    Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    
    for i in range(max(len(parts1), len(parts2))):
        p1 = parts1[i] if i < len(parts1) else 0
        p2 = parts2[i] if i < len(parts2) else 0
        
        if p1 < p2:
            return -1
        elif p1 > p2:
            return 1
    
    return 0


class VersionedSchema(BaseModel, ABC):
    """Base class for versioned schemas"""
    _version: str = "1.0.0"
    
    @classmethod
    def version(cls) -> str:
        """Get version string of this schema"""
        return cls._version
    
    class Config:
        """Allow version field"""
        underscore_attrs_are_private = False


# Entity Schema Versions

class EntityV1(VersionedSchema):
    """Version 1.0.0 - Basic entity with minimal fields"""
    _version: str = "1.0.0"
    
    id: str
    text: str
    type: str
    
    class Config:
        underscore_attrs_are_private = False


class EntityV2(VersionedSchema):
    """Version 2.0.0 - Added confidence score"""
    _version: str = "2.0.0"
    
    id: str
    text: str
    type: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    class Config:
        underscore_attrs_are_private = False


class EntityV3(VersionedSchema):
    """Version 3.0.0 - Added position information"""
    _version: str = "3.0.0"
    
    id: str
    text: str
    type: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        underscore_attrs_are_private = False


class SchemaMigrator:
    """
    Handles migration between schema versions.
    
    Key features:
    - Register migration functions between versions
    - Find migration paths automatically
    - Apply migrations in sequence
    - Validate migration results
    """
    
    # Registry of migration functions
    _migrations: Dict[Tuple[str, str], Callable] = {}
    
    @classmethod
    def register_migration(cls, from_version: str, to_version: str):
        """
        Decorator to register a migration function.
        
        Usage:
            @SchemaMigrator.register_migration("1.0.0", "2.0.0")
            def migrate_v1_to_v2(entity: EntityV1) -> EntityV2:
                return EntityV2(...)
        """
        def decorator(func: Callable):
            cls._migrations[(from_version, to_version)] = func
            return func
        return decorator
    
    @classmethod
    def migrate(cls, data: VersionedSchema, target_version: str) -> VersionedSchema:
        """
        Migrate data to target version.
        
        Args:
            data: The data to migrate
            target_version: The target version string
            
        Returns:
            Migrated data at target version
        """
        current_version = data._version if hasattr(data, '_version') else "1.0.0"
        
        # No migration needed
        if current_version == target_version:
            return data
        
        # Check if backward migration (not supported)
        if compare_versions(target_version, current_version) < 0:
            raise ValueError(f"Backward migration not supported: {current_version} → {target_version}")
        
        # Find migration path
        path = cls.find_migration_path(current_version, target_version)
        
        if not path:
            raise ValueError(f"No migration path found from {current_version} to {target_version}")
        
        # Apply migrations in sequence
        result = data
        for from_v, to_v in path:
            migration_func = cls._migrations.get((from_v, to_v))
            if not migration_func:
                raise ValueError(f"No migration function for {from_v} → {to_v}")
            
            result = migration_func(result)
            
            # Verify version was updated
            if not hasattr(result, '_version') or result._version != to_v:
                raise ValueError(f"Migration function didn't set version to {to_v}")
        
        return result
    
    @classmethod
    def find_migration_path(cls, from_version: str, to_version: str) -> List[Tuple[str, str]]:
        """
        Find the shortest migration path between versions.
        
        Uses breadth-first search to find the path.
        """
        if from_version == to_version:
            return []
        
        # Build graph of available migrations
        graph = {}
        for (from_v, to_v) in cls._migrations.keys():
            if from_v not in graph:
                graph[from_v] = []
            graph[from_v].append(to_v)
        
        # BFS to find path
        from collections import deque
        queue = deque([(from_version, [])])
        visited = {from_version}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_version:
                return path
            
            if current in graph:
                for next_version in graph[current]:
                    if next_version not in visited:
                        visited.add(next_version)
                        new_path = path + [(current, next_version)]
                        queue.append((next_version, new_path))
        
        return []  # No path found
    
    @classmethod
    def can_migrate(cls, from_version: str, to_version: str) -> bool:
        """Check if migration is possible between versions."""
        return bool(cls.find_migration_path(from_version, to_version))
    
    @classmethod
    def get_available_migrations(cls) -> List[Tuple[str, str]]:
        """Get list of all registered migrations."""
        return list(cls._migrations.keys())


# Register Entity migrations

@SchemaMigrator.register_migration("1.0.0", "2.0.0")
def migrate_entity_v1_to_v2(entity: EntityV1) -> EntityV2:
    """Migrate Entity from V1 to V2 - adds confidence field"""
    return EntityV2(
        _version="2.0.0",
        id=entity.id,
        text=entity.text,
        type=entity.type,
        confidence=0.5  # Default confidence
    )


@SchemaMigrator.register_migration("2.0.0", "3.0.0")
def migrate_entity_v2_to_v3(entity: EntityV2) -> EntityV3:
    """Migrate Entity from V2 to V3 - adds position fields"""
    return EntityV3(
        _version="3.0.0",
        id=entity.id,
        text=entity.text,
        type=entity.type,
        confidence=entity.confidence,
        start_pos=None,  # Default to None
        end_pos=None,    # Default to None
        metadata={}      # Empty metadata
    )


# Additional schema versions for other data types can be added here
# (TextData versions removed to avoid migration conflicts)