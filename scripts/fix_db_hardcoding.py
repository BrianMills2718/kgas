#!/usr/bin/env python3
"""
Systematic Database Connection Hardcoding Fix Script

This script fixes hardcoded database connection strings by replacing them
with calls to the standard config system.
"""

import os
import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def fix_database_hardcoding_in_file(file_path: str) -> bool:
    """Fix database hardcoding in a single file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        # Replace with: neo4j_uri = get_database_uri()
        pattern1 = r'neo4j_uri\s*=\s*os\.getenv\([\'"]NEO4J_URI[\'"],\s*[\'"]bolt://[^\'\"]*[\'\"]\)'
        content = re.sub(pattern1, 'neo4j_uri = get_database_uri()', content)
        
        # Pattern 2: "bolt://localhost:7687" direct usage
        pattern2 = r'[\'"]bolt://localhost:7687[\'"]'
        content = re.sub(pattern2, 'get_database_uri()', content)
        
        # Pattern 3: "neo4j://graph/main" graph references
        pattern3 = r'[\'"]neo4j://graph/main[\'"]'
        content = re.sub(pattern3, '"neo4j://graph/main"', content)  # Keep as is for now
        
        # Add import if we made changes and don't have it
        if content != original_content:
            if 'get_database_uri' in content and 'from src.core.standard_config import' not in content:
                # Add import after existing imports
                lines = content.split('\n')
                insert_pos = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_pos = i + 1
                    elif line.strip() and not line.startswith('#'):
                        break
                
                import_line = "from src.core.standard_config import get_database_uri"
                lines.insert(insert_pos, import_line)
                content = '\n'.join(lines)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        
    return False

def main():
    """Main execution"""
    print("🗄️ Starting systematic database hardcoding fix")
    
    # Read database hardcoding files
    with open('/tmp/db_hardcoding.txt', 'r') as f:
        files_to_fix = []
        for line in f:
            if line.strip():
                file_path = line.split(':')[0]
                if file_path not in files_to_fix:
                    files_to_fix.append(file_path)
    
    print(f"Found {len(files_to_fix)} files with database hardcoding")
    
    # Process files
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            print(f"🔧 Processing {file_path}")
            if fix_database_hardcoding_in_file(file_path):
                fixed_count += 1
                print(f"  ✅ Fixed")
            else:
                print(f"  ⏭️ No changes needed")
    
    print(f"\n🎉 Database hardcoding fix complete!")
    print(f"   Files processed: {len(files_to_fix)}")
    print(f"   Files modified: {fixed_count}")

if __name__ == "__main__":
    main()