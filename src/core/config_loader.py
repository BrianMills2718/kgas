#!/usr/bin/env python3
"""
Configuration loader for services
Provides centralized configuration management
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Loads and manages service configuration"""
    
    def __init__(self, config_path: str = None, env_prefix: str = "KGAS_"):
        """
        Initialize config loader
        
        Args:
            config_path: Path to YAML config file
            env_prefix: Prefix for environment variable overrides
        """
        self.config_path = config_path or "config/services.yaml"
        self.env_prefix = env_prefix
        self._config = None
        
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file and environment
        
        Priority order:
        1. Environment variables (override)
        2. Config file
        3. Defaults
        """
        if self._config is not None:
            return self._config
            
        # Start with defaults
        config = self._get_defaults()
        
        # Load from file
        file_config = self._load_from_file()
        if file_config:
            config = self._merge_configs(config, file_config)
        
        # Override with environment variables
        env_config = self._load_from_env()
        if env_config:
            config = self._merge_configs(config, env_config)
        
        self._config = config
        logger.info(f"Configuration loaded from {self.config_path}")
        
        return config
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'services': {
                'identity': {
                    'persistence': False,
                    'db_path': 'data/identity.db',
                    'embeddings': False
                },
                'provenance': {
                    'backend': 'memory',
                    'track_inputs': True,
                    'track_outputs': True
                },
                'quality': {
                    'thresholds': {
                        'high_confidence': 0.8,
                        'medium_confidence': 0.5,
                        'low_confidence': 0.2
                    },
                    'propagation_factor': 0.1
                },
                'workflow': {
                    'checkpoint_dir': 'data/checkpoints',
                    'auto_save': False,
                    'save_interval': 300
                }
            },
            'framework': {
                'strict_mode': True,
                'enable_metrics': True,
                'log_level': 'INFO'
            }
        }
    
    def _load_from_file(self) -> Optional[Dict[str, Any]]:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return None
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded config from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            return None
    
    def _load_from_env(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables
        
        Examples:
            KGAS_SERVICES_IDENTITY_PERSISTENCE=true
            KGAS_FRAMEWORK_STRICT_MODE=false
        """
        env_config = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to config path
                config_path = key[len(self.env_prefix):].lower().split('_')
                
                # Parse value
                parsed_value = self._parse_env_value(value)
                
                # Set in nested dict
                self._set_nested_dict(env_config, config_path, parsed_value)
        
        if env_config:
            logger.info(f"Loaded {len(env_config)} settings from environment")
        
        return env_config
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        # Handle boolean values explicitly
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try to parse as JSON (handles int, float, list, dict)
        try:
            return json.loads(value)
        except:
            pass
        
        # Return as string
        return value
    
    def _set_nested_dict(self, d: dict, path: list, value: Any):
        """Set value in nested dictionary using path"""
        for key in path[:-1]:
            if key not in d:
                d[key] = {}
            d = d[key]
        d[path[-1]] = value
    
    def _merge_configs(self, base: dict, override: dict) -> dict:
        """
        Recursively merge two configuration dictionaries
        Override values take precedence
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for specific service"""
        config = self.load_config()
        return config.get('services', {}).get(service_name, {})
    
    def get_framework_config(self) -> Dict[str, Any]:
        """Get framework configuration"""
        config = self.load_config()
        return config.get('framework', {})


# Module-level convenience functions
_default_loader = None

def load_service_config(config_path: str = None) -> Dict[str, Any]:
    """Load service configuration"""
    global _default_loader
    if _default_loader is None or config_path:
        _default_loader = ConfigLoader(config_path)
    return _default_loader.load_config().get('services', {})

def get_service_config(service_name: str, config_path: str = None) -> Dict[str, Any]:
    """Get configuration for specific service"""
    global _default_loader
    if _default_loader is None or config_path:
        _default_loader = ConfigLoader(config_path)
    return _default_loader.get_service_config(service_name)

def get_framework_config(config_path: str = None) -> Dict[str, Any]:
    """Get framework configuration"""
    global _default_loader
    if _default_loader is None or config_path:
        _default_loader = ConfigLoader(config_path)
    return _default_loader.get_framework_config()