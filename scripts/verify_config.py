#!/usr/bin/env python3
"""
KGAS Configuration Verification Script

Verifies that KGAS configuration is properly set up and all required
components are accessible.
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def load_environment():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv()
            return True, "Environment variables loaded from .env"
        else:
            return False, ".env file not found"
    except ImportError:
        return False, "python-dotenv not installed. Run: pip install python-dotenv"
    except Exception as e:
        return False, f"Error loading .env: {e}"

def check_required_env_vars() -> Tuple[bool, List[str]]:
    """Check required environment variables"""
    required_vars = [
        "NEO4J_URI",
        "NEO4J_USER", 
        "NEO4J_PASSWORD"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    return len(missing) == 0, missing

def check_neo4j_connection() -> Tuple[bool, str]:
    """Check Neo4j database connection"""
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            
            # Get database info
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            components = list(result)
            
            driver.close()
            
            if components:
                version = components[0]["versions"][0]
                edition = components[0]["edition"]
                return True, f"Neo4j {version} ({edition}) - Connection successful"
            else:
                return True, "Neo4j connection successful"
                
    except ImportError:
        return False, "neo4j driver not installed. Run: pip install neo4j"
    except Exception as e:
        return False, f"Neo4j connection failed: {e}"

def check_llm_apis() -> Dict[str, Tuple[bool, str]]:
    """Check LLM API configurations"""
    apis = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY", 
        "Google": "GOOGLE_API_KEY"
    }
    
    results = {}
    for name, env_var in apis.items():
        api_key = os.getenv(env_var)
        if api_key and api_key not in ["", "test-key"]:
            results[name] = (True, "API key configured")
        elif api_key == "test-key":
            results[name] = (True, "Test API key (non-functional)")
        else:
            results[name] = (False, "API key not configured")
    
    return results

def check_config_files() -> Dict[str, Tuple[bool, str]]:
    """Check configuration files"""
    files_to_check = {
        ".env": "Environment variables file",
        "config/default.yaml": "Default configuration", 
        "config/config.yaml": "Main configuration (optional)",
        "SETUP_GUIDE.md": "Setup documentation (optional)"
    }
    
    results = {}
    for file_path, description in files_to_check.items():
        path = Path(file_path)
        if path.exists():
            try:
                if file_path.endswith('.yaml'):
                    import yaml
                    with open(path) as f:
                        yaml.safe_load(f)
                    results[file_path] = (True, f"{description} - Valid YAML")
                else:
                    results[file_path] = (True, f"{description} - Exists")
            except Exception as e:
                results[file_path] = (False, f"{description} - Invalid: {e}")
        else:
            if "optional" in description:
                results[file_path] = (True, f"{description} - Not required")
            else:
                results[file_path] = (False, f"{description} - Missing")
    
    return results

def check_python_dependencies() -> Dict[str, Tuple[bool, str]]:
    """Check Python dependencies"""
    dependencies = {
        "neo4j": "Neo4j database driver",
        "python-dotenv": "Environment variable loading",
        "yaml": "YAML configuration parsing",
        "pydantic": "Configuration validation",
        "fastapi": "Web API framework",
        "uvicorn": "ASGI server"
    }
    
    results = {}
    for package, description in dependencies.items():
        try:
            if package == "yaml":
                import yaml
            else:
                __import__(package)
            results[package] = (True, f"{description} - Available")
        except ImportError:
            results[package] = (False, f"{description} - Not installed")
    
    return results

def check_system_settings() -> Dict[str, Tuple[bool, str]]:
    """Check system configuration settings"""
    settings = {}
    
    # Check log level
    log_level = os.getenv("KGAS_LOG_LEVEL", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level in valid_levels:
        settings["Log Level"] = (True, f"Set to {log_level}")
    else:
        settings["Log Level"] = (False, f"Invalid log level: {log_level}")
    
    # Check max workers
    max_workers = os.getenv("KGAS_MAX_WORKERS", "4")
    try:
        workers = int(max_workers)
        if 1 <= workers <= 32:
            settings["Max Workers"] = (True, f"Set to {workers}")
        else:
            settings["Max Workers"] = (False, f"Invalid worker count: {workers}")
    except ValueError:
        settings["Max Workers"] = (False, f"Invalid worker count: {max_workers}")
    
    # Check environment
    env = os.getenv("KGAS_ENV", "development")
    valid_envs = ["development", "testing", "production"]
    if env.lower() in valid_envs:
        settings["Environment"] = (True, f"Set to {env}")
    else:
        settings["Environment"] = (False, f"Invalid environment: {env}")
    
    return settings

def print_section(title: str, results: Dict[str, Tuple[bool, str]]):
    """Print a results section"""
    print(f"\n{title}:")
    print("-" * len(title))
    
    for item, (success, message) in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {item}: {message}")

def print_check_result(title: str, success: bool, message: str):
    """Print a single check result"""
    status = "✅" if success else "❌"
    print(f"  {status} {title}: {message}")

def main():
    """Main verification function"""
    print("🔍 KGAS Configuration Verification")
    print("=" * 50)
    
    overall_success = True
    
    # Load environment
    env_success, env_message = load_environment()
    print_check_result("Environment Loading", env_success, env_message)
    if not env_success:
        overall_success = False
    
    # Check required environment variables
    env_vars_success, missing_vars = check_required_env_vars()
    if env_vars_success:
        print_check_result("Required Environment Variables", True, "All required variables present")
    else:
        print_check_result("Required Environment Variables", False, f"Missing: {', '.join(missing_vars)}")
        overall_success = False
    
    # Check Neo4j connection
    neo4j_success, neo4j_message = check_neo4j_connection()
    print_check_result("Neo4j Connection", neo4j_success, neo4j_message)
    if not neo4j_success:
        overall_success = False
    
    # Check configuration files
    config_results = check_config_files()
    print_section("Configuration Files", config_results)
    if not all(success for success, _ in config_results.values()):
        overall_success = False
    
    # Check Python dependencies
    dep_results = check_python_dependencies()
    print_section("Python Dependencies", dep_results)
    if not all(success for success, _ in dep_results.values()):
        overall_success = False
    
    # Check LLM APIs (informational only)
    api_results = check_llm_apis()
    print_section("LLM API Configuration (Optional)", api_results)
    
    # Check system settings
    system_results = check_system_settings()
    print_section("System Settings", system_results)
    if not all(success for success, _ in system_results.values()):
        overall_success = False
    
    # Summary
    print(f"\n{'=' * 50}")
    if overall_success:
        print("🎉 CONFIGURATION VERIFICATION SUCCESSFUL!")
        print("   All required components are properly configured.")
        print("   KGAS system is ready to use.")
        return 0
    else:
        print("❌ CONFIGURATION VERIFICATION FAILED!")
        print("   Some required components are not properly configured.")
        print("   Please fix the issues above before using KGAS.")
        print("\n💡 Quick fixes:")
        print("   • Run: python scripts/setup_config.py")
        print("   • Check: SETUP_GUIDE.md")
        print("   • Install missing dependencies with pip")
        return 1

if __name__ == "__main__":
    sys.exit(main())