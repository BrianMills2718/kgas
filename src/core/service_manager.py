"""Service Manager - FAIL-FAST Service Coordination

CRITICAL: NO MOCKS. NO SILENT FAILURES. NO GRACEFUL DEGRADATION.

This ServiceManager implements FAIL-FAST philosophy:
- All dependencies are validated at startup
- Services that can't be created cause immediate system failure
- Clear error messages point to exact fixes needed
- No silent fallbacks or mock services

Implements performance optimization F1 from CLAUDE.md.
Provides shared service instances across all tools to prevent duplication.
Target: 10x speedup by eliminating redundant service creation.
"""

from typing import Optional, Dict, Any
import threading
import os
from neo4j import GraphDatabase
import sqlite3
from pathlib import Path

from src.services.identity_service import IdentityService as RealIdentityService
from src.services.provenance_service import ProvenanceService as RealProvenanceService
from src.services.quality_service import QualityService as RealQualityService
from src.core.entity_id_strategy import EntityIDManager, EntityIDStrategy
from .dependency_validator import (
    validate_system_dependencies, 
    detect_system_mode, 
    SystemMode,
    ServiceUnavailableError,
    DependencyError
)
from .config_manager import get_config
from .logging_config import get_logger


class ServiceManager:
    """Singleton service manager for shared services."""
    
    _instance = None
    _lock = threading.Lock()
    _init_lock = threading.Lock()  # Additional lock for thread-safe initialization
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, mode: SystemMode = None, config: Optional[Dict[str, Any]] = None):
        with self._init_lock:  # Protect initialization
            if not hasattr(self, "_initialized"):
                self._initialized = True
                self._identity_service = None
                self._provenance_service = None
                self._quality_service = None
                self._neo4j_driver = None
                self._neo4j_config = None
                self._entity_id_manager = None
                self._config = config or {}
                self.logger = get_logger("core.service_manager")
                
                # Detect system mode
                self.mode = mode or detect_system_mode()
                self.logger.info(f"🚀 ServiceManager initializing in {self.mode.value} mode")
                
                # FAIL FAST: Validate ALL dependencies before creating ANY services
                try:
                    validate_system_dependencies(self.mode)
                except SystemError as e:
                    self.logger.critical("❌ Dependency validation failed - system cannot start")
                    self.logger.critical(str(e))
                    raise
                
                # Initialize entity ID manager FIRST (before other services)
                self._entity_id_manager = self._initialize_entity_id_manager(self._config)
                
                # Only initialize services if ALL dependencies are validated
                self._initialize_real_services()
    
    def _initialize_entity_id_manager(self, config: Dict[str, Any]) -> EntityIDManager:
        """Initialize entity ID manager with configured strategy."""
        strategy_name = config.get("entity_id_strategy", "content_hash")
        
        strategy_map = {
            "uuid": EntityIDStrategy.UUID,
            "content_hash": EntityIDStrategy.CONTENT_HASH,
            "hierarchical": EntityIDStrategy.HIERARCHICAL,
            "external": EntityIDStrategy.EXTERNAL
        }
        
        strategy = strategy_map.get(strategy_name, EntityIDStrategy.CONTENT_HASH)
        self.logger.info(f"Initializing EntityIDManager with {strategy.value} strategy")
        
        return EntityIDManager(strategy)
    
    def _initialize_real_services(self):
        """Initialize real services - NO MOCKS, NO FALLBACKS"""
        try:
            if self.mode == SystemMode.OFFLINE:
                # Offline mode - explicitly no services
                self._identity_service = None
                self._provenance_service = None
                self._quality_service = None
                self.logger.warning("⚠️ OFFLINE MODE: No services initialized - limited functionality")
                return
            
            # Create real services only - dependencies already validated
            self.logger.info("🔧 Initializing real services...")
            
            # Get Neo4j driver
            neo4j_driver = self.get_neo4j_driver()
            if not neo4j_driver:
                raise ServiceUnavailableError(
                    "neo4j_driver",
                    "Neo4j driver creation failed despite validation passing",
                    ["This should not happen - check dependency validator"]
                )
            
            # Initialize identity service
            self._identity_service = RealIdentityService(neo4j_driver)
            self.logger.info("✅ IdentityService initialized")
            
            # Initialize quality service
            self._quality_service = RealQualityService(neo4j_driver)
            self.logger.info("✅ QualityService initialized")
            
            # Initialize provenance service (uses SQLite)
            db_path = Path("data/provenance.db")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            self._provenance_service = RealProvenanceService(connection=conn)
            self.logger.info("✅ ProvenanceService initialized")
            
            self.logger.info("🎉 All real services initialized successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize services: {e}"
            self.logger.critical(f"❌ {error_msg}")
            
            # FAIL FAST - don't create fallbacks, don't continue
            raise ServiceUnavailableError(
                "service_initialization",
                error_msg,
                [
                    "Check dependency validation logs above",
                    "Verify Neo4j is running: docker ps | grep neo4j",
                    "Check SQLite permissions: ls -la data/",
                    "Verify configuration: env | grep KGAS",
                    "Try offline mode: export KGAS_MODE=offline"
                ]
            )
    
    @property
    def identity_service(self):
        """Get identity service - FAILS if not available"""
        if self.mode == SystemMode.OFFLINE:
            raise ServiceUnavailableError(
                "identity_service",
                "Service not available in offline mode",
                [
                    "Set KGAS_MODE=development to enable services",
                    "Or use tools that don't require identity service"
                ]
            )
        
        if not self._identity_service:
            # This should never happen if initialization succeeded
            raise ServiceUnavailableError(
                "identity_service",
                "Service not initialized - this indicates a system error",
                [
                    "Check ServiceManager initialization logs",
                    "Verify dependency validation passed",
                    "Report this as a bug if dependencies are working"
                ]
            )
        
        return self._identity_service
    
    def configure_identity_service(self, **config):
        """Configure identity service before first use.
        
        Args:
            use_embeddings: Enable semantic similarity
            persistence_path: Path to SQLite database
            similarity_threshold: Threshold for entity matching
            etc.
        """
        if self._identity_service:
            raise RuntimeError("Cannot configure identity service after it's been created")
        self._identity_config = config
    
    @property
    def provenance_service(self):
        """Get provenance service - FAILS if not available"""
        if self.mode == SystemMode.OFFLINE:
            raise ServiceUnavailableError(
                "provenance_service",
                "Service not available in offline mode",
                [
                    "Set KGAS_MODE=development to enable services",
                    "Or use tools that don't require provenance tracking"
                ]
            )
        
        if not self._provenance_service:
            # This should never happen if initialization succeeded
            raise ServiceUnavailableError(
                "provenance_service",
                "Service not initialized - this indicates a system error",
                [
                    "Check ServiceManager initialization logs",
                    "Verify SQLite permissions for data/ directory",
                    "Report this as a bug if dependencies are working"
                ]
            )
        
        return self._provenance_service
    
    @property
    def quality_service(self):
        """Get quality service - FAILS if not available"""
        if self.mode == SystemMode.OFFLINE:
            raise ServiceUnavailableError(
                "quality_service",
                "Service not available in offline mode",
                [
                    "Set KGAS_MODE=development to enable services",
                    "Or use tools that don't require quality assessment"
                ]
            )
        
        if not self._quality_service:
            # This should never happen if initialization succeeded
            raise ServiceUnavailableError(
                "quality_service",
                "Service not initialized - this indicates a system error",
                [
                    "Check ServiceManager initialization logs",
                    "Verify Neo4j connection is working",
                    "Report this as a bug if dependencies are working"
                ]
            )
        
        return self._quality_service
    
    @property
    def entity_id_manager(self) -> EntityIDManager:
        """Get entity ID manager - required for all entity operations."""
        if not self._entity_id_manager:
            raise ServiceUnavailableError(
                "entity_id_manager",
                "EntityIDManager not initialized",
                ["Check ServiceManager initialization"]
            )
        return self._entity_id_manager
    
    def get_neo4j_driver(
        self,
        uri: str = None,
        user: str = None,
        password: str = None
    ):
        """Get shared Neo4j driver instance with connection pooling using configuration."""
        # Load configuration if parameters not provided
        config = get_config()
        database_config = config.database  # Changed from neo4j to database
        
        # Use provided parameters or fall back to configuration
        uri = uri or database_config.uri
        user = user or database_config.username  # Changed from user to username
        password = password or database_config.password
        
        config_key = f"{uri}:{user}"
        
        if self._neo4j_driver and self._neo4j_config == config_key:
            return self._neo4j_driver
        
        with self._lock:
            if self._neo4j_driver and self._neo4j_config != config_key:
                self._neo4j_driver.close()
                self._neo4j_driver = None
            
            if not self._neo4j_driver:
                try:
                    self._neo4j_driver = GraphDatabase.driver(
                        uri,
                        auth=(user, password),
                        max_connection_pool_size=database_config.max_connection_pool_size,
                        connection_acquisition_timeout=database_config.connection_acquisition_timeout,
                        keep_alive=database_config.keep_alive
                    )
                    self._neo4j_config = config_key
                    
                    # Test connection with proper single record handling
                    with self._neo4j_driver.session() as session:
                        result = session.run("RETURN 1 as test")
                        result.single()  # Consume single record properly
                    self.logger.info(f"Shared Neo4j connection established to {uri}")
                except Exception as e:
                    self.logger.critical(f"❌ Neo4j connection required but failed: {e}")
                    from .exceptions import ServiceUnavailableError
                    raise ServiceUnavailableError("neo4j", f"Connection failed: {e}", [
                        "Check Neo4j server is running: docker ps | grep neo4j",
                        "Verify connection settings in .env file",
                        "Test connection: docker exec neo4j cypher-shell",
                        "Start Neo4j: docker-compose up neo4j"
                    ])
        
        return self._neo4j_driver
    
    def close_all(self):
        """Close all managed resources."""
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
        self._neo4j_config = None
    
    def get_identity_service(self):
        """Get shared identity service instance - FAILS if not available."""
        return self.identity_service
    
    def get_provenance_service(self):
        """Get shared provenance service instance - FAILS if not available."""
        return self.provenance_service
    
    def get_quality_service(self):
        """Get shared quality service instance - FAILS if not available."""
        return self.quality_service
    
    def get_neo4j_manager(self):
        """Get Neo4j manager instance for compatibility."""
        from .neo4j_manager import Neo4jManager
        from src.core.config_manager import get_config

        return Neo4jManager()
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about shared services."""
        stats = {
            "identity_service_active": self._identity_service is not None,
            "provenance_service_active": self._provenance_service is not None,
            "quality_service_active": self._quality_service is not None,
            "neo4j_driver_active": self._neo4j_driver is not None,
            "neo4j_config": self._neo4j_config,
            "system_mode": self.mode.value
        }
        
        # Add health check info if services exist
        if self._identity_service:
            try:
                stats["identity_health"] = self._identity_service.health_check()
            except:
                stats["identity_health"] = {"status": "unknown"}
        
        if self._provenance_service:
            try:
                stats["provenance_health"] = self._provenance_service.health_check()
            except:
                stats["provenance_health"] = {"status": "unknown"}
        
        if self._quality_service:
            try:
                stats["quality_health"] = self._quality_service.health_check()
            except:
                stats["quality_health"] = {"status": "unknown"}
        
        return stats


# Global instance getter
def get_service_manager() -> ServiceManager:
    """Get the global service manager instance."""
    return ServiceManager()