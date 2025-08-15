#!/usr/bin/env python3
"""Fix missing category parameter in Phase 2 tools."""

import re
from pathlib import Path

# List of Phase 2 tools that need fixing based on the error messages
tools_to_fix = [
    "t51_centrality_analysis.py",
    "t52_graph_clustering.py", 
    "t53_network_motifs.py",
    "t54_graph_visualization.py",
    "t55_temporal_analysis.py",
    "t56_graph_metrics.py",
    "t57_path_analysis.py"
]

def fix_tool_category(file_path: Path):
    """Add category parameter to get_contract method."""
    content = file_path.read_text()
    
    # Pattern to find ToolContract without category
    pattern = r'(return ToolContract\(\s*tool_id=.*?\s*name=.*?\s*description=.*?)(\s*input_schema=)'
    
    # Check if category is already there
    if 'category=' in content:
        print(f"✅ {file_path.name} already has category parameter")
        return False
    
    # Add category parameter after description
    replacement = r'\1\n            category="graph",\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        file_path.write_text(new_content)
        print(f"✅ Fixed {file_path.name} - added category='graph'")
        return True
    else:
        print(f"❌ Could not fix {file_path.name} - pattern not found")
        return False

def main():
    """Fix all Phase 2 tools."""
    phase2_dir = Path("src/tools/phase2")
    fixed_count = 0
    
    for tool_file in tools_to_fix:
        file_path = phase2_dir / tool_file
        if file_path.exists():
            if fix_tool_category(file_path):
                fixed_count += 1
        else:
            print(f"⚠️  {tool_file} not found")
    
    print(f"\n✅ Fixed {fixed_count} tools")
    
if __name__ == "__main__":
    main()