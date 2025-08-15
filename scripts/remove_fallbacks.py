#!/usr/bin/env python3
"""
Script to identify and report all fallback/mock patterns in production code.
This helps enforce the fail-fast philosophy from CLAUDE.md
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_fallback_patterns(file_path: Path) -> List[Tuple[int, str]]:
    """Find lines with fallback/mock patterns in a file"""
    
    # Skip test files and mock factories (those are allowed)
    if 'test' in str(file_path).lower() or 'mock' in file_path.name.lower():
        return []
    
    patterns = [
        r'fallback',
        r'simulate',
        r'degrade', 
        r'stub(?!born)',  # stub but not stubborn
        r'mock(?!ing)',   # mock but not mocking
        r'_simulate_',
        r'_fallback_',
        r'FallbackAnalyzer',
        r'FallbackCoordinator',
        r'FallbackClusterer',
        r'# Simulate',
        r'# Fallback',
        r'create_fallback',
        r'using simulated',
        r'using fallback'
    ]
    
    matches = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append((i, line.strip()))
                    break
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return matches

def main():
    """Find all fallback patterns in production code"""
    
    src_dir = Path('/home/brian/projects/Digimons/src')
    
    # Find all Python files
    python_files = list(src_dir.rglob('*.py'))
    
    print("Scanning for fallback/mock patterns in production code...")
    print("=" * 80)
    
    violations = {}
    
    for file_path in python_files:
        # Skip test directories
        if '/test' in str(file_path) or '/testing/' in str(file_path):
            continue
            
        matches = find_fallback_patterns(file_path)
        if matches:
            violations[file_path] = matches
    
    if not violations:
        print("✅ No fallback/mock patterns found in production code!")
        return
    
    print(f"❌ Found fallback/mock patterns in {len(violations)} files:\n")
    
    for file_path, matches in violations.items():
        rel_path = file_path.relative_to(src_dir)
        print(f"\n📄 {rel_path}")
        print("-" * 40)
        for line_num, line_content in matches[:5]:  # Show first 5 matches
            print(f"  Line {line_num}: {line_content[:100]}")
        if len(matches) > 5:
            print(f"  ... and {len(matches) - 5} more")
    
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Files with violations: {len(violations)}")
    print(f"  Total violations: {sum(len(m) for m in violations.values())}")
    print("\nThese patterns violate the fail-fast philosophy from CLAUDE.md:")
    print("  - NO lazy mocking/stubs/fallbacks/pseudo code")
    print("  - Fail-fast approach - Code must fail immediately")
    print("  - REAL API CALLS ONLY - All code must use real services")

if __name__ == "__main__":
    main()