"""Fail-fast validation framework for KGAS."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    NEO4J = "neo4j"
    SQLITE = "sqlite"
    API_CLIENT = "api_client"
    IDENTITY_SERVICE = "identity_service"
    PROVENANCE_SERVICE = "provenance_service"
    QUALITY_SERVICE = "quality_service"
    ENTITY_ID_MANAGER = "entity_id_manager"

@dataclass
class ServiceRequirement:
    """Definition of a required service."""
    service_type: ServiceType
    description: str
    validation_method: str
    error_message: str

class SystemInitializationError(Exception):
    """Raised when system cannot initialize due to missing dependencies."""
    pass

class ServiceUnavailableError(Exception):
    """Raised when a required service is not available."""
    def __init__(self, service_name: str, reason: str, fix_instructions: List[str]):
        self.service_name = service_name
        self.reason = reason
        self.fix_instructions = fix_instructions
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format error message with fix instructions."""
        msg = f"\n{'='*60}\n"
        msg += f"SERVICE UNAVAILABLE: {self.service_name}\n"
        msg += f"REASON: {self.reason}\n"
        msg += f"\nTO FIX THIS ERROR:\n"
        for i, instruction in enumerate(self.fix_instructions, 1):
            msg += f"  {i}. {instruction}\n"
        msg += f"{'='*60}\n"
        return msg

class ConfigurationError(Exception):
    """Raised when configuration is invalid or conflicting."""
    def __init__(self, issue: str, conflicts: Optional[Dict[str, Any]] = None):
        self.issue = issue
        self.conflicts = conflicts
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format configuration error message."""
        msg = f"\n{'='*60}\n"
        msg += f"CONFIGURATION ERROR: {self.issue}\n"
        if self.conflicts:
            msg += "\nCONFLICTS DETECTED:\n"
            for key, values in self.conflicts.items():
                msg += f"  - {key}: {values}\n"
        msg += f"{'='*60}\n"
        return msg

class FailFastValidator:
    """Validates system state and fails fast on issues."""
    
    def __init__(self):
        self.required_services = self._define_required_services()
        self.validated_services = set()
    
    def _define_required_services(self) -> List[ServiceRequirement]:
        """Define all required services and their validation."""
        return [
            ServiceRequirement(
                ServiceType.NEO4J,
                "Neo4j graph database for entity and relationship storage",
                "check_neo4j_connection",
                "Neo4j database connection required"
            ),
            ServiceRequirement(
                ServiceType.SQLITE,
                "SQLite database for metadata and configuration",
                "check_sqlite_connection",
                "SQLite database required"
            ),
            ServiceRequirement(
                ServiceType.API_CLIENT,
                "Enhanced API client for LLM interactions",
                "check_api_client",
                "API client with valid credentials required"
            ),
            ServiceRequirement(
                ServiceType.IDENTITY_SERVICE,
                "Identity service for entity resolution",
                "check_identity_service",
                "Identity service required for entity management"
            ),
            ServiceRequirement(
                ServiceType.PROVENANCE_SERVICE,
                "Provenance service for tracking data lineage",
                "check_provenance_service",
                "Provenance service required for data lineage"
            ),
            ServiceRequirement(
                ServiceType.QUALITY_SERVICE,
                "Quality service for data validation",
                "check_quality_service",
                "Quality service required for data quality"
            ),
            ServiceRequirement(
                ServiceType.ENTITY_ID_MANAGER,
                "Entity ID manager for consistent ID generation",
                "check_entity_id_manager",
                "Entity ID manager required for ID consistency"
            )
        ]
    
    def validate_all_services(self, service_manager: Any) -> None:
        """Validate all required services are available.
        
        Args:
            service_manager: ServiceManager instance to validate
            
        Raises:
            SystemInitializationError: If any required service is unavailable
        """
        logger.info("Starting fail-fast service validation...")
        failures = []
        
        for requirement in self.required_services:
            try:
                self._validate_service(service_manager, requirement)
                self.validated_services.add(requirement.service_type)
                logger.info(f"✅ {requirement.service_type.value}: VALIDATED")
            except Exception as e:
                failures.append((requirement, str(e)))
                logger.error(f"❌ {requirement.service_type.value}: FAILED - {e}")
        
        if failures:
            self._handle_validation_failures(failures)
    
    def _validate_service(self, service_manager: Any, requirement: ServiceRequirement) -> None:
        """Validate a single service requirement."""
        # Check service availability
        if requirement.service_type == ServiceType.NEO4J:
            if not hasattr(service_manager, 'neo4j_manager') or not service_manager.neo4j_manager:
                raise ServiceUnavailableError(
                    "Neo4j Manager",
                    "Neo4j connection not established",
                    [
                        "Ensure Neo4j is running (docker-compose up neo4j)",
                        "Set NEO4J_PASSWORD environment variable",
                        "Verify Neo4j URI is correct (default: bolt://localhost:7687)"
                    ]
                )
            # Test connection
            service_manager.neo4j_manager.test_connection()
            
        elif requirement.service_type == ServiceType.SQLITE:
            if not hasattr(service_manager, 'sqlite_manager') or not service_manager.sqlite_manager:
                raise ServiceUnavailableError(
                    "SQLite Manager",
                    "SQLite database not initialized",
                    [
                        "Ensure data directory exists",
                        "Check SQLITE_DB_PATH configuration",
                        "Verify write permissions on database file"
                    ]
                )
            
        elif requirement.service_type == ServiceType.API_CLIENT:
            if not hasattr(service_manager, 'api_client') or not service_manager.api_client:
                raise ServiceUnavailableError(
                    "Enhanced API Client",
                    "No API client configured",
                    [
                        "Set at least one API key: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY",
                        "Verify API key validity",
                        "Check network connectivity to API endpoints"
                    ]
                )
            # Test API availability
            if not service_manager.api_client.has_any_api():
                raise ServiceUnavailableError(
                    "API Services",
                    "No LLM APIs available",
                    [
                        "Configure at least one valid API key",
                        "OPENAI_API_KEY for OpenAI GPT models",
                        "ANTHROPIC_API_KEY for Claude models",
                        "GOOGLE_API_KEY for Gemini models"
                    ]
                )
                
        elif requirement.service_type == ServiceType.ENTITY_ID_MANAGER:
            if not hasattr(service_manager, 'entity_id_manager') or not service_manager.entity_id_manager:
                raise ServiceUnavailableError(
                    "Entity ID Manager",
                    "Entity ID manager not initialized",
                    [
                        "Check ServiceManager initialization",
                        "Verify entity_id_strategy configuration",
                        "Ensure EntityIDManager is imported correctly"
                    ]
                )
    
    def _handle_validation_failures(self, failures: List[tuple]) -> None:
        """Handle validation failures with clear error reporting."""
        error_msg = "\n" + "="*80 + "\n"
        error_msg += "SYSTEM INITIALIZATION FAILED - FAIL-FAST VALIDATION\n"
        error_msg += "="*80 + "\n\n"
        error_msg += f"Failed services: {len(failures)}\n\n"
        
        for requirement, error in failures:
            error_msg += f"❌ {requirement.service_type.value}:\n"
            error_msg += f"   {requirement.description}\n"
            error_msg += f"   Error: {error}\n\n"
        
        error_msg += "CANNOT PROCEED WITHOUT ALL REQUIRED SERVICES\n"
        error_msg += "="*80 + "\n"
        
        raise SystemInitializationError(error_msg)
    
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate configuration for conflicts and missing values.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Check for environment vs config conflicts
        self._check_config_conflicts(config)
        
        # Check required configuration values
        self._check_required_config(config)
    
    def _check_config_conflicts(self, config: Dict[str, Any]) -> None:
        """Check for configuration conflicts."""
        import os
        
        conflicts = {}
        
        # Check Neo4j password
        env_password = os.getenv('NEO4J_PASSWORD')
        config_password = config.get('neo4j', {}).get('password')
        
        if env_password and config_password and env_password != config_password:
            conflicts['NEO4J_PASSWORD'] = {
                'environment': env_password,
                'config': config_password
            }
        
        # Check SQLite path
        env_db_path = os.getenv('SQLITE_DB_PATH')
        config_db_path = config.get('sqlite', {}).get('db_path')
        
        if env_db_path and config_db_path and env_db_path != config_db_path:
            conflicts['SQLITE_DB_PATH'] = {
                'environment': env_db_path,
                'config': config_db_path
            }
        
        if conflicts:
            raise ConfigurationError(
                "Configuration values conflict between environment and config file",
                conflicts
            )
    
    def _check_required_config(self, config: Dict[str, Any]) -> None:
        """Check that all required configuration values are present."""
        import os
        
        # Neo4j password is required
        neo4j_password = (config.get('neo4j', {}).get('password') or 
                         os.getenv('NEO4J_PASSWORD'))
        if not neo4j_password:
            raise ConfigurationError(
                "NEO4J_PASSWORD is required but not set",
                {"suggestion": "Set NEO4J_PASSWORD environment variable or neo4j.password in config"}
            )
        
        # At least one API key is required
        has_api_key = (
            os.getenv('OPENAI_API_KEY') or
            os.getenv('ANTHROPIC_API_KEY') or
            os.getenv('GOOGLE_API_KEY') or
            config.get('api_keys', {}).get('openai') or
            config.get('api_keys', {}).get('anthropic') or
            config.get('api_keys', {}).get('google')
        )
        
        if not has_api_key:
            raise ConfigurationError(
                "At least one LLM API key is required",
                {"suggestion": "Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"}
            )