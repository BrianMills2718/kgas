#!/usr/bin/env python3
"""
Fix API Endpoint Hardcoding Script

Systematically replaces hardcoded API endpoints with centralized configuration calls.
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

def find_api_hardcoding_files() -> List[str]:
    """Find files with API endpoint hardcoding."""
    try:
        # Use grep to find API endpoint patterns
        result = subprocess.run([
            'grep', '-r', '-l',
            '--include=*.py',
            'https://api\.openai\.com\|https://api\.anthropic\.com\|https://.*\.googleapis\.com',
            '/home/brian/projects/Digimons/src'
        ], capture_output=True, text=True)
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [f for f in files if f and not any(skip in f for skip in ['__pycache__', '.pyc', 'archived'])]
    except subprocess.CalledProcessError:
        return []

def find_file_path_hardcoding_files() -> List[str]:
    """Find files with file path hardcoding."""
    try:
        # Use grep to find file path patterns
        result = subprocess.run([
            'grep', '-r', '-l',
            '--include=*.py',
            'data/\|logs/\|config/\|./data\|./logs\|./config\|\.log\|\.txt\|\.json',
            '/home/brian/projects/Digimons/src'
        ], capture_output=True, text=True)
        
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return [f for f in files if f and not any(skip in f for skip in ['__pycache__', '.pyc', 'archived'])]
    except subprocess.CalledProcessError:
        return []

def fix_api_endpoints_in_file(file_path: str) -> bool:
    """Fix API endpoint hardcoding in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Import statement to add if not present
        import_statement = "from src.core.standard_config import get_api_endpoint"
        
        # API endpoint patterns and replacements
        api_patterns = [
            # OpenAI endpoints
            (r'"https://api\.openai\.com/v1"', 'get_api_endpoint("openai")'),
            (r"'https://api\.openai\.com/v1'", 'get_api_endpoint("openai")'),
            (r'https://api\.openai\.com/v1', 'get_api_endpoint("openai")'),
            
            # Anthropic endpoints
            (r'"https://api\.anthropic\.com/v1"', 'get_api_endpoint("anthropic")'),
            (r"'https://api\.anthropic\.com/v1'", 'get_api_endpoint("anthropic")'),
            (r'https://api\.anthropic\.com/v1', 'get_api_endpoint("anthropic")'),
            
            # Google endpoints
            (r'"https://generativelanguage\.googleapis\.com/v1beta"', 'get_api_endpoint("google")'),
            (r"'https://generativelanguage\.googleapis\.com/v1beta'", 'get_api_endpoint("google")'),
            (r'https://generativelanguage\.googleapis\.com/v1beta', 'get_api_endpoint("google")'),
        ]
        
        # Apply replacements
        for pattern, replacement in api_patterns:
            content = re.sub(pattern, replacement, content)
        
        # Add import if needed and content was changed
        if content != original_content:
            # Check if import already exists
            if import_statement not in content:
                # Find best place to add import
                import_lines = []
                non_import_lines = []
                in_imports = True
                
                for line in content.split('\n'):
                    if in_imports and (line.startswith('import ') or line.startswith('from ') or line.strip() == '' or line.startswith('#')):
                        import_lines.append(line)
                    else:
                        in_imports = False
                        non_import_lines.append(line)
                
                # Add our import at the end of imports
                import_lines.append(import_statement)
                content = '\n'.join(import_lines + non_import_lines)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed API endpoints in {file_path}")
            return True
        else:
            print(f"⏭️  No API endpoint changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def fix_file_paths_in_file(file_path: str) -> bool:
    """Fix file path hardcoding in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Import statement to add if not present
        import_statement = "from src.core.standard_config import get_file_path"
        
        # File path patterns and replacements
        file_patterns = [
            # Data directories
            (r'"./data"', 'get_file_path("data_dir")'),
            (r"'./data'", 'get_file_path("data_dir")'),
            (r'"data/"', 'get_file_path("data_dir")'),
            (r"'data/'", 'get_file_path("data_dir")'),
            
            # Logs directories  
            (r'"./logs"', 'get_file_path("logs_dir")'),
            (r"'./logs'", 'get_file_path("logs_dir")'),
            (r'"logs/"', 'get_file_path("logs_dir")'),
            (r"'logs/'", 'get_file_path("logs_dir")'),
            
            # Config directories
            (r'"./config"', 'get_file_path("config_dir")'),
            (r"'./config'", 'get_file_path("config_dir")'),
            (r'"config/"', 'get_file_path("config_dir")'),
            (r"'config/'", 'get_file_path("config_dir")'),
            
            # Common file extensions with directory
            (r'"data/([^"]+\.json)"', r'get_file_path("data_dir") + "/\1"'),
            (r"'data/([^']+\.json)'", r"get_file_path('data_dir') + '/\1'"),
            (r'"logs/([^"]+\.log)"', r'get_file_path("logs_dir") + "/\1"'),
            (r"'logs/([^']+\.log)'", r"get_file_path('logs_dir') + '/\1'"),
        ]
        
        # Apply replacements
        for pattern, replacement in file_patterns:
            content = re.sub(pattern, replacement, content)
        
        # Add import if needed and content was changed
        if content != original_content:
            # Check if import already exists
            if import_statement not in content:
                # Find best place to add import
                import_lines = []
                non_import_lines = []
                in_imports = True
                
                for line in content.split('\n'):
                    if in_imports and (line.startswith('import ') or line.startswith('from ') or line.strip() == '' or line.startswith('#')):
                        import_lines.append(line)
                    else:
                        in_imports = False
                        non_import_lines.append(line)
                
                # Add our import at the end of imports
                import_lines.append(import_statement)
                content = '\n'.join(import_lines + non_import_lines)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed file paths in {file_path}")
            return True
        else:
            print(f"⏭️  No file path changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def update_standard_config():
    """Update standard_config.py to support API endpoints and file paths."""
    config_file = "/home/brian/projects/Digimons/src/core/standard_config.py"
    
    # API endpoint mappings
    api_endpoints_code = '''
def get_api_endpoint(provider: str) -> str:
    """Get API endpoint for provider with centralized configuration."""
    config = StandardConfig()
    
    endpoints = {
        "openai": "https://api.openai.com/v1",
        "anthropic": "https://api.anthropic.com/v1", 
        "google": "https://generativelanguage.googleapis.com/v1beta"
    }
    
    # Check for environment variable override
    env_key = f"{provider.upper()}_API_ENDPOINT"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Check configuration file
    endpoint = config._config_data.get('api_endpoints', {}).get(provider)
    if endpoint:
        return endpoint
        
    # Return default
    return endpoints.get(provider, f"https://api.{provider}.com/v1")
'''

    # File path mappings
    file_paths_code = '''
def get_file_path(path_type: str) -> str:
    """Get file path with centralized configuration."""
    config = StandardConfig()
    
    defaults = {
        "data_dir": "./data",
        "logs_dir": "./logs", 
        "config_dir": "./config",
        "temp_dir": "./temp",
        "cache_dir": "./cache"
    }
    
    # Check for environment variable override
    env_key = f"KGAS_{path_type.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Check configuration file
    file_path = config._config_data.get('file_paths', {}).get(path_type)
    if file_path:
        return file_path
        
    # Return default
    return defaults.get(path_type, f"./{path_type}")
'''

    try:
        with open(config_file, 'r') as f:
            content = f.read()
            
        # Add the new functions if they don't exist
        if 'def get_api_endpoint(' not in content:
            content += api_endpoints_code
            
        if 'def get_file_path(' not in content:
            content += file_paths_code
            
        with open(config_file, 'w') as f:
            f.write(content)
            
        print("✅ Updated standard_config.py with API endpoints and file paths support")
        return True
        
    except Exception as e:
        print(f"❌ Error updating standard_config.py: {e}")
        return False

def main():
    """Main execution function."""
    print("🔧 KGAS API Endpoints & File Paths Centralization Script")
    print("=" * 60)
    
    # Update standard_config.py first
    print("📝 Updating standard_config.py with new functions...")
    update_standard_config()
    
    # Fix API endpoints
    print("\n🌐 Fixing API endpoint hardcoding...")
    api_files = find_api_hardcoding_files()
    api_files_processed = 0
    api_files_modified = 0
    
    for file_path in api_files:
        api_files_processed += 1
        if fix_api_endpoints_in_file(file_path):
            api_files_modified += 1
    
    # Fix file paths
    print(f"\n📁 Fixing file path hardcoding...")
    file_path_files = find_file_path_hardcoding_files()
    file_path_files_processed = 0
    file_path_files_modified = 0
    
    for file_path in file_path_files:
        file_path_files_processed += 1
        if fix_file_paths_in_file(file_path):
            file_path_files_modified += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CENTRALIZATION SUMMARY")
    print("=" * 60)
    print(f"API Endpoints: {api_files_modified}/{api_files_processed} files modified")
    print(f"File Paths: {file_path_files_modified}/{file_path_files_processed} files modified")
    print(f"Total: {api_files_modified + file_path_files_modified}/{api_files_processed + file_path_files_processed} files modified")
    
    if api_files_modified > 0 or file_path_files_modified > 0:
        print("\n✅ Hardcoding centralization completed successfully!")
        print("🧪 Run tests to verify changes:")
        print("   python -c \"from src.core.standard_config import get_api_endpoint, get_file_path; print('API:', get_api_endpoint('openai')); print('Path:', get_file_path('data_dir'))\"")
    else:
        print("\n✅ No hardcoding found - system already centralized!")

if __name__ == "__main__":
    main()