#!/usr/bin/env python3
"""
KGAS Configuration Setup Wizard

Easy configuration setup for KGAS system with sensible defaults and validation.
Handles passwords, API keys, database connections, and environment settings.
"""

import os
import sys
import random
import string
import getpass
from pathlib import Path
from typing import Dict, Any, Optional
import secrets

class KGASConfigSetup:
    """KGAS Configuration Setup Wizard"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_templates = {
            "development": self._get_dev_template(),
            "testing": self._get_test_template(),
            "production": self._get_prod_template()
        }
    
    def run_setup_wizard(self):
        """Run interactive configuration setup wizard"""
        print("🔧 KGAS Configuration Setup Wizard")
        print("=" * 50)
        print("This wizard will help you set up KGAS configuration with secure defaults.")
        print()
        
        # Choose environment
        env_type = self._choose_environment()
        
        # Get configuration values
        config = self._get_configuration_values(env_type)
        
        # Generate secure passwords if needed
        config = self._generate_secure_defaults(config, env_type)
        
        # Write configuration files
        self._write_configuration_files(config, env_type)
        
        # Show setup summary
        self._show_setup_summary(config, env_type)
        
        print("\n✅ Configuration setup complete!")
        print(f"   Environment: {env_type}")
        print(f"   Config files created in: {self.project_root}")
        print("\n🚀 You can now run KGAS tools with the configured settings.")
    
    def _choose_environment(self) -> str:
        """Choose environment type"""
        print("Choose your environment type:")
        print("1. Development (local development with test data)")
        print("2. Testing (automated testing with ephemeral data)")
        print("3. Production (production deployment with real data)")
        
        while True:
            choice = input("\nEnter choice (1-3): ").strip()
            if choice == "1":
                return "development"
            elif choice == "2":
                return "testing"
            elif choice == "3":
                return "production"
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    
    def _get_configuration_values(self, env_type: str) -> Dict[str, Any]:
        """Get configuration values from user"""
        config = {}
        
        print(f"\n📝 Configuring {env_type} environment...")
        
        # Neo4j Configuration
        print("\n🗄️  Neo4j Database Configuration:")
        config["neo4j_uri"] = input("Neo4j URI [bolt://localhost:7687]: ").strip() or "bolt://localhost:7687"
        config["neo4j_user"] = input("Neo4j Username [neo4j]: ").strip() or "neo4j"
        
        if env_type == "production":
            config["neo4j_password"] = getpass.getpass("Neo4j Password: ")
        else:
            use_generated = input("Use generated secure password for Neo4j? [Y/n]: ").strip().lower()
            if use_generated in ["", "y", "yes"]:
                config["neo4j_password"] = None  # Will be generated
            else:
                config["neo4j_password"] = getpass.getpass("Neo4j Password: ")
        
        # LLM API Keys (optional)
        print("\n🤖 LLM API Configuration (optional - leave blank to skip):")
        config["openai_api_key"] = getpass.getpass("OpenAI API Key (optional): ") or None
        config["anthropic_api_key"] = getpass.getpass("Anthropic API Key (optional): ") or None
        config["google_api_key"] = getpass.getpass("Google API Key (optional): ") or None
        
        # System Configuration
        print("\n⚙️  System Configuration:")
        config["log_level"] = input("Log Level [INFO]: ").strip() or "INFO"
        config["max_workers"] = input("Max Workers [4]: ").strip() or "4"
        
        # Environment-specific settings
        if env_type == "development":
            config["debug_mode"] = input("Enable debug mode? [Y/n]: ").strip().lower() not in ["n", "no"]
            config["metrics_enabled"] = input("Enable metrics collection? [Y/n]: ").strip().lower() not in ["n", "no"]
        elif env_type == "production":
            config["backup_enabled"] = input("Enable automatic backups? [Y/n]: ").strip().lower() not in ["n", "no"]
            config["encryption_enabled"] = input("Enable encryption? [Y/n]: ").strip().lower() not in ["n", "no"]
        
        return config
    
    def _generate_secure_defaults(self, config: Dict[str, Any], env_type: str) -> Dict[str, Any]:
        """Generate secure passwords and defaults"""
        
        # Generate Neo4j password if needed
        if config.get("neo4j_password") is None:
            config["neo4j_password"] = self._generate_secure_password(length=16)
            print(f"   Generated secure Neo4j password: {config['neo4j_password']}")
        
        # Generate PII service credentials for non-production
        if env_type != "production":
            config["pii_password"] = self._generate_secure_password(length=32)
            config["pii_salt"] = self._generate_secure_password(length=16)
        
        # Set environment-specific defaults
        config["environment"] = env_type
        config["kgas_env"] = env_type.upper()
        
        return config
    
    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def _write_configuration_files(self, config: Dict[str, Any], env_type: str):
        """Write configuration files"""
        
        # Write .env file
        env_file = self.project_root / ".env"
        env_content = self._generate_env_content(config, env_type)
        
        if env_file.exists():
            backup_file = self.project_root / f".env.backup.{int(time.time())}"
            env_file.rename(backup_file)
            print(f"   Backed up existing .env to {backup_file.name}")
        
        with open(env_file, "w") as f:
            f.write(env_content)
        print(f"   Created .env file")
        
        # Write config template if doesn't exist
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        template_file = config_dir / f"{env_type}.yaml"
        if not template_file.exists():
            template_content = self.config_templates[env_type]
            with open(template_file, "w") as f:
                f.write(template_content)
            print(f"   Created config/{env_type}.yaml template")
        
        # Write setup documentation
        docs_file = self.project_root / "SETUP_GUIDE.md"
        if not docs_file.exists():
            docs_content = self._generate_setup_docs(config, env_type)
            with open(docs_file, "w") as f:
                f.write(docs_content)
            print("   Created SETUP_GUIDE.md")
    
    def _generate_env_content(self, config: Dict[str, Any], env_type: str) -> str:
        """Generate .env file content"""
        
        content = f"""# KGAS {env_type.title()} Environment Configuration
# Generated by KGAS Configuration Setup Wizard
# 
# This file contains environment variables for KGAS system configuration.
# Keep this file secure and do not commit it to version control.

# Environment Settings
KGAS_ENV={config['kgas_env']}
KGAS_ENVIRONMENT={config['environment']}
KGAS_LOG_LEVEL={config['log_level']}

# Neo4j Database Configuration
NEO4J_URI={config['neo4j_uri']}
NEO4J_USER={config['neo4j_user']}
NEO4J_PASSWORD={config['neo4j_password']}

# System Configuration
KGAS_MAX_WORKERS={config['max_workers']}
"""
        
        # Add LLM API keys if provided
        if config.get("openai_api_key"):
            content += f"\n# LLM API Configuration\nOPENAI_API_KEY={config['openai_api_key']}\n"
        
        if config.get("anthropic_api_key"):
            content += f"ANTHROPIC_API_KEY={config['anthropic_api_key']}\n"
            
        if config.get("google_api_key"):
            content += f"GOOGLE_API_KEY={config['google_api_key']}\n"
        
        # Add environment-specific settings
        if env_type == "development":
            content += f"""
# Development Settings
KGAS_DEBUG={'true' if config.get('debug_mode', True) else 'false'}
KGAS_METRICS_ENABLED={'true' if config.get('metrics_enabled', True) else 'false'}
"""
        
        elif env_type == "testing":
            content += f"""
# Testing Settings
KGAS_PII_PASSWORD={config.get('pii_password', 'test_pii_password_32_chars_long!!')}
KGAS_PII_SALT={config.get('pii_salt', 'test_salt_16_chars')}
KGAS_TESTING=true
"""
        
        elif env_type == "production":
            content += f"""
# Production Settings
KGAS_BACKUP_ENABLED={'true' if config.get('backup_enabled', True) else 'false'}
KGAS_ENCRYPTION_ENABLED={'true' if config.get('encryption_enabled', True) else 'false'}
KGAS_PRODUCTION=true
"""
        
        content += """
# Optional: Override default configuration file location
# KGAS_CONFIG_FILE=./config/custom.yaml

# Optional: Custom data directories
# KGAS_DATA_DIR=./data
# KGAS_LOGS_DIR=./logs
# KGAS_BACKUP_DIR=./backups
"""
        
        return content
    
    def _get_dev_template(self) -> str:
        """Get development configuration template"""
        return """# KGAS Development Configuration
api:
  anthropic_api_key: '${ANTHROPIC_API_KEY:-}'
  google_api_key: '${GOOGLE_API_KEY:-}'
  max_retries: 3
  openai_api_key: '${OPENAI_API_KEY:-}'
  timeout: 30

llm:
  primary_model: "gpt_4o_mini"
  fallback_models:
    - "gemini_flash" 
    - "claude_sonnet_4"
  timeout_seconds: 30
  max_retries: 3
  fallback_on_rate_limit: true
  fallback_on_timeout: true
  fallback_on_error: true

database:
  database: neo4j
  host: '${NEO4J_HOST:-localhost}'
  password: '${NEO4J_PASSWORD}'
  port: '${NEO4J_PORT:-7687}'
  username: '${NEO4J_USER:-neo4j}'

system:
  backup_enabled: false
  encryption_enabled: false
  log_level: '${KGAS_LOG_LEVEL:-DEBUG}'
  max_workers: '${KGAS_MAX_WORKERS:-4}'
  metrics_enabled: true
  debug_mode: true
"""
    
    def _get_test_template(self) -> str:
        """Get testing configuration template"""
        return """# KGAS Testing Configuration
api:
  anthropic_api_key: 'test-key'
  google_api_key: 'test-key'
  max_retries: 1
  openai_api_key: 'test-key'
  timeout: 10

llm:
  primary_model: "gpt_4o_mini"
  fallback_models: []
  timeout_seconds: 10
  max_retries: 1
  fallback_on_rate_limit: false
  fallback_on_timeout: false
  fallback_on_error: false

database:
  database: neo4j
  host: '${NEO4J_HOST:-localhost}'
  password: '${NEO4J_PASSWORD}'
  port: '${NEO4J_PORT:-7687}'
  username: '${NEO4J_USER:-neo4j}'

system:
  backup_enabled: false
  encryption_enabled: false
  log_level: '${KGAS_LOG_LEVEL:-INFO}'
  max_workers: '${KGAS_MAX_WORKERS:-2}'
  metrics_enabled: false
  testing_mode: true
"""
    
    def _get_prod_template(self) -> str:
        """Get production configuration template"""
        return """# KGAS Production Configuration
api:
  anthropic_api_key: '${ANTHROPIC_API_KEY}'
  google_api_key: '${GOOGLE_API_KEY}'
  max_retries: 5
  openai_api_key: '${OPENAI_API_KEY}'
  timeout: 60

llm:
  primary_model: "gpt_4o_mini"
  fallback_models:
    - "gemini_flash" 
    - "claude_sonnet_4"
  timeout_seconds: 60
  max_retries: 5
  fallback_on_rate_limit: true
  fallback_on_timeout: true
  fallback_on_error: true

database:
  database: neo4j
  host: '${NEO4J_HOST:-localhost}'
  password: '${NEO4J_PASSWORD}'
  port: '${NEO4J_PORT:-7687}'
  username: '${NEO4J_USER:-neo4j}'

system:
  backup_enabled: '${KGAS_BACKUP_ENABLED:-true}'
  encryption_enabled: '${KGAS_ENCRYPTION_ENABLED:-true}'
  log_level: '${KGAS_LOG_LEVEL:-INFO}'
  max_workers: '${KGAS_MAX_WORKERS:-8}'
  metrics_enabled: true
  production_mode: true
"""
    
    def _generate_setup_docs(self, config: Dict[str, Any], env_type: str) -> str:
        """Generate setup documentation"""
        return f"""# KGAS Setup Guide

This guide was generated by the KGAS Configuration Setup Wizard for your **{env_type}** environment.

## Configuration Files Created

### Environment Variables (`.env`)
Contains your environment-specific configuration including:
- Database connection settings
- API keys (if provided)
- System configuration
- Environment flags

**Important**: Keep `.env` file secure and never commit it to version control.

### YAML Configuration (`config/{env_type}.yaml`)
Contains structured configuration that references environment variables.

## Quick Start

1. **Start Neo4j Database**
   ```bash
   # Using Docker (recommended)
   docker run -d \\
     --name neo4j-kgas \\
     -p 7474:7474 -p 7687:7687 \\
     -e NEO4J_AUTH={config['neo4j_user']}/{config['neo4j_password']} \\
     neo4j:latest
   ```

2. **Verify Configuration**
   ```bash
   python scripts/verify_config.py
   ```

3. **Run KGAS Tools**
   ```bash
   # Test basic functionality
   python -c "from src.core.config_manager import get_settings; print(get_settings())"
   
   # Run MCP server
   python src/mcp_server.py
   ```

## Configuration Options

### Required Settings
- `NEO4J_URI`: Neo4j database connection URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password

### Optional Settings
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models
- `GOOGLE_API_KEY`: Google API key for Gemini models
- `KGAS_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `KGAS_MAX_WORKERS`: Maximum number of worker threads

### Environment-Specific Settings

#### Development
- `KGAS_DEBUG`: Enable debug mode
- `KGAS_METRICS_ENABLED`: Enable metrics collection

#### Testing
- `KGAS_TESTING`: Enable testing mode
- `KGAS_PII_PASSWORD`: PII service test password
- `KGAS_PII_SALT`: PII service test salt

#### Production
- `KGAS_BACKUP_ENABLED`: Enable automatic backups
- `KGAS_ENCRYPTION_ENABLED`: Enable encryption
- `KGAS_PRODUCTION`: Enable production mode

## Updating Configuration

### Adding New Settings
1. Add environment variable to `.env` file
2. Reference in `config/{env_type}.yaml` using `${{VAR_NAME}}` syntax
3. Update code to use the new setting

### Changing Passwords
1. Update `.env` file with new password
2. Update database with new credentials
3. Restart KGAS services

### Environment Migration
To migrate between environments:
1. Run setup wizard again: `python scripts/setup_config.py`
2. Choose new environment type
3. Update deployment configurations accordingly

## Security Best Practices

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong passwords** - Generated passwords are recommended
3. **Rotate credentials regularly** - Especially for production
4. **Restrict file permissions** - `chmod 600 .env`
5. **Use encrypted storage** - For production secrets

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Verify Neo4j is running: `docker ps`
   - Check credentials in `.env` file
   - Test connection: `python scripts/test_neo4j.py`

2. **Environment Variables Not Loading**
   - Verify `.env` file exists and is readable
   - Check file permissions: `ls -la .env`
   - Restart application after changes

3. **Configuration Not Found**
   - Set `KGAS_CONFIG_FILE` to specify custom location
   - Verify YAML syntax: `python -c "import yaml; yaml.safe_load(open('config/{env_type}.yaml'))"`

### Getting Help

- Check logs in `logs/` directory
- Run diagnostic script: `python scripts/diagnose_config.py`
- Review documentation in `docs/` directory

## Next Steps

1. **Verify installation**: Run `python scripts/verify_installation.py`
2. **Load test data**: Run `python scripts/load_test_data.py`
3. **Start services**: Run `python scripts/start_services.py`
4. **Run tests**: Run `pytest tests/` to verify everything works

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
Environment: {env_type}
"""
    
    def _show_setup_summary(self, config: Dict[str, Any], env_type: str):
        """Show setup summary"""
        print(f"\n📋 Setup Summary for {env_type.title()} Environment:")
        print("-" * 40)
        print(f"Neo4j URI: {config['neo4j_uri']}")
        print(f"Neo4j User: {config['neo4j_user']}")
        print(f"Log Level: {config['log_level']}")
        print(f"Max Workers: {config['max_workers']}")
        
        if config.get("openai_api_key"):
            print("OpenAI API: ✅ Configured")
        if config.get("anthropic_api_key"):
            print("Anthropic API: ✅ Configured")
        if config.get("google_api_key"):
            print("Google API: ✅ Configured")
        
        print(f"\nFiles created:")
        print(f"  • .env (environment variables)")
        print(f"  • config/{env_type}.yaml (configuration template)")
        print(f"  • SETUP_GUIDE.md (setup documentation)")


def main():
    """Main entry point for configuration setup"""
    import time
    
    setup = KGASConfigSetup()
    
    try:
        setup.run_setup_wizard()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()