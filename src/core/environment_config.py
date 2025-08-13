"""
Environment Configuration System - Phase 7.1

This module manages configuration for different environments with fail-fast validation.
NO FALLBACKS, NO DEFAULTS - Environment must be explicitly configured or system fails immediately.
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Supported environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration with strict validation"""
    uri: str
    username: str
    password: str
    max_connections: int
    connection_timeout: int
    
    def __post_init__(self):
        """Validate configuration immediately - fail fast if invalid"""
        if not self.uri:
            raise ValueError("Database URI is required and cannot be empty")
        if not self.username:
            raise ValueError("Database username is required and cannot be empty")
        if not self.password:
            raise ValueError("Database password is required and cannot be empty")
        if self.max_connections <= 0:
            raise ValueError(f"Max connections must be positive, got: {self.max_connections}")
        if self.connection_timeout <= 0:
            raise ValueError(f"Connection timeout must be positive, got: {self.connection_timeout}")


@dataclass
class LoggingConfig:
    """Logging configuration with strict validation"""
    level: str
    file_output: bool
    file_path: Optional[str]
    console_output: bool
    max_file_size_mb: int
    
    def __post_init__(self):
        """Validate configuration immediately"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of: {valid_levels}")
        
        if self.file_output and not self.file_path:
            raise ValueError("File output enabled but no file path specified")
        
        if self.file_output and self.max_file_size_mb <= 0:
            raise ValueError(f"Max file size must be positive, got: {self.max_file_size_mb}")
        
        if not self.file_output and not self.console_output:
            raise ValueError("At least one output method (file or console) must be enabled")


@dataclass
class LLMConfig:
    """LLM configuration with strict validation"""
    timeout: int
    retry_attempts: int
    max_tokens: int
    temperature: float
    
    def __post_init__(self):
        """Validate configuration immediately"""
        if self.timeout <= 0:
            raise ValueError(f"LLM timeout must be positive, got: {self.timeout}")
        if self.retry_attempts < 0:
            raise ValueError(f"Retry attempts cannot be negative, got: {self.retry_attempts}")
        if self.max_tokens <= 0:
            raise ValueError(f"Max tokens must be positive, got: {self.max_tokens}")
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(f"Temperature must be between 0.0 and 2.0, got: {self.temperature}")


@dataclass
class SecurityConfig:
    """Security configuration with strict validation"""
    api_key_required: bool
    encryption_enabled: bool
    ssl_verify: bool
    allowed_hosts: list
    
    def __post_init__(self):
        """Validate configuration immediately"""
        if not isinstance(self.allowed_hosts, list):
            raise ValueError(f"Allowed hosts must be a list, got: {type(self.allowed_hosts)}")
        if not self.allowed_hosts:
            raise ValueError("At least one allowed host must be specified")


class EnvironmentConfig:
    """
    Environment configuration manager with fail-fast validation.
    
    NO DEFAULTS, NO FALLBACKS - All required configuration must be explicitly provided
    or the system will fail immediately with clear error messages.
    """
    
    def __init__(self, env: Optional[str] = None):
        """Initialize configuration for specified environment"""
        if env is None:
            env = os.getenv("KGAS_ENVIRONMENT")
        
        if not env:
            raise ValueError(
                "Environment not specified. Set KGAS_ENVIRONMENT environment variable "
                "or pass env parameter. Valid values: development, testing, production"
            )
        
        try:
            self.environment = Environment(env.lower())
        except ValueError:
            valid_envs = [e.value for e in Environment]
            raise ValueError(f"Invalid environment: {env}. Must be one of: {valid_envs}")
        
        self.config_dir = Path(__file__).parent.parent.parent / "config"
        self.config_file = self.config_dir / f"{self.environment.value}.json"
        
        # Load and validate configuration immediately
        self._load_and_validate_config()
    
    def _load_and_validate_config(self):
        """Load configuration from file and validate all settings"""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}. "
                f"Create configuration file for {self.environment.value} environment."
            )
        
        try:
            with open(self.config_file, 'r') as f:
                raw_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {self.config_file}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read config file {self.config_file}: {e}")
        
        # Validate all required sections exist
        required_sections = ["neo4j", "logging", "llm", "security"]
        missing_sections = [s for s in required_sections if s not in raw_config]
        if missing_sections:
            raise ValueError(f"Missing required configuration sections: {missing_sections}")
        
        # Parse and validate each configuration section
        try:
            self.neo4j_config = DatabaseConfig(
                uri=self._get_required_env_or_config("NEO4J_URI", raw_config["neo4j"], "uri"),
                username=self._get_required_env_or_config("NEO4J_USERNAME", raw_config["neo4j"], "username"),
                password=self._get_required_env_or_config("NEO4J_PASSWORD", raw_config["neo4j"], "password"),
                max_connections=raw_config["neo4j"]["max_connections"],
                connection_timeout=raw_config["neo4j"]["connection_timeout"]
            )
        except Exception as e:
            raise ValueError(f"Invalid neo4j configuration: {e}")
        
        try:
            self.logging_config = LoggingConfig(
                level=raw_config["logging"]["level"],
                file_output=raw_config["logging"]["file_output"],
                file_path=raw_config["logging"].get("file_path"),
                console_output=raw_config["logging"]["console_output"],
                max_file_size_mb=raw_config["logging"]["max_file_size_mb"]
            )
        except Exception as e:
            raise ValueError(f"Invalid logging configuration: {e}")
        
        try:
            self.llm_config = LLMConfig(
                timeout=raw_config["llm"]["timeout"],
                retry_attempts=raw_config["llm"]["retry_attempts"],
                max_tokens=raw_config["llm"]["max_tokens"],
                temperature=raw_config["llm"]["temperature"]
            )
        except Exception as e:
            raise ValueError(f"Invalid LLM configuration: {e}")
        
        try:
            self.security_config = SecurityConfig(
                api_key_required=raw_config["security"]["api_key_required"],
                encryption_enabled=raw_config["security"]["encryption_enabled"],
                ssl_verify=raw_config["security"]["ssl_verify"],
                allowed_hosts=raw_config["security"]["allowed_hosts"]
            )
        except Exception as e:
            raise ValueError(f"Invalid security configuration: {e}")
    
    def _get_required_env_or_config(self, env_var: str, config_section: Dict[str, Any], config_key: str) -> str:
        """Get value from environment variable or config file, fail if neither exists"""
        env_value = os.getenv(env_var)
        config_value = config_section.get(config_key)
        
        if env_value:
            return env_value
        elif config_value:
            return config_value
        else:
            raise ValueError(
                f"Required configuration missing: {config_key}. "
                f"Set environment variable {env_var} or add '{config_key}' to config file."
            )
    
    def get_neo4j_uri(self) -> str:
        """Get Neo4j connection URI"""
        return self.neo4j_config.uri
    
    def get_neo4j_auth(self) -> tuple:
        """Get Neo4j authentication tuple"""
        return (self.neo4j_config.username, self.neo4j_config.password)
    
    def get_neo4j_config(self) -> DatabaseConfig:
        """Get complete Neo4j configuration"""
        return self.neo4j_config
    
    def get_logging_config(self) -> LoggingConfig:
        """Get complete logging configuration"""
        return self.logging_config
    
    def get_llm_config(self) -> LLMConfig:
        """Get complete LLM configuration"""
        return self.llm_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get complete security configuration"""
        return self.security_config
    
    def validate_runtime_requirements(self):
        """Validate that runtime requirements are met - fail fast if not"""
        # Check Neo4j connectivity
        try:
            import neo4j
            driver = neo4j.GraphDatabase.driver(
                self.neo4j_config.uri,
                auth=(self.neo4j_config.username, self.neo4j_config.password),
                connection_timeout=self.neo4j_config.connection_timeout
            )
            # Test connection immediately
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                if not result.single()["test"] == 1:
                    raise RuntimeError("Neo4j connection test failed")
            driver.close()
        except ImportError:
            raise RuntimeError("neo4j driver not installed. Run: pip install neo4j")
        except Exception as e:
            raise RuntimeError(f"Neo4j connection failed: {e}")
        
        # Check log file directory exists and is writable
        if self.logging_config.file_output:
            log_path = Path(self.logging_config.file_path)
            log_dir = log_path.parent
            if not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    raise RuntimeError(f"Cannot create log directory {log_dir}: {e}")
            
            # Test write permission
            try:
                test_file = log_dir / "test_write_permission.tmp"
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                raise RuntimeError(f"Cannot write to log directory {log_dir}: {e}")
        
        # Validate security requirements in production
        if self.environment == Environment.PRODUCTION:
            if not self.security_config.ssl_verify:
                raise RuntimeError("SSL verification must be enabled in production")
            if not self.security_config.encryption_enabled:
                raise RuntimeError("Encryption must be enabled in production")
            if not self.security_config.api_key_required:
                raise RuntimeError("API key authentication must be required in production")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get current environment information"""
        return {
            "environment": self.environment.value,
            "config_file": str(self.config_file),
            "neo4j_uri": self.neo4j_config.uri,
            "logging_level": self.logging_config.level,
            "file_logging": self.logging_config.file_output,
            "console_logging": self.logging_config.console_output,
            "security_enabled": self.security_config.encryption_enabled,
            "ssl_verify": self.security_config.ssl_verify
        }


def get_environment_config(env: Optional[str] = None) -> EnvironmentConfig:
    """
    Get environment configuration instance.
    
    This function creates and validates the configuration immediately.
    If any validation fails, the system will fail fast with clear error messages.
    """
    return EnvironmentConfig(env)


def validate_environment_setup():
    """
    Validate that the environment is properly set up.
    
    This should be called at application startup to ensure all
    requirements are met before proceeding.
    """
    try:
        config = get_environment_config()
        config.validate_runtime_requirements()
        return config
    except Exception as e:
        print(f"ENVIRONMENT SETUP FAILED: {e}", file=sys.stderr)
        print("Fix the configuration and try again.", file=sys.stderr)
        sys.exit(1)