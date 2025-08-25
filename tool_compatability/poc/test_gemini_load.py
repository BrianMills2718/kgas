#!/usr/bin/env python3
"""Test if Gemini API key loads from .env"""

import os
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import EntityExtractor which should load .env
from poc.tools.entity_extractor import EntityExtractor

print("="*60)
print("GEMINI API KEY LOADING TEST")
print("="*60)

# Check if loaded
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ GEMINI_API_KEY loaded successfully")
    print(f"   Key starts with: {api_key[:10]}...")
    print(f"   Key length: {len(api_key)} characters")
else:
    print("❌ GEMINI_API_KEY not loaded")
    
# Try to create EntityExtractor
try:
    extractor = EntityExtractor()
    print("\n✅ EntityExtractor created successfully")
    print(f"   Tool ID: {extractor.tool_id}")
    print(f"   Input type: {extractor.input_type}")
    print(f"   Output type: {extractor.output_type}")
except Exception as e:
    print(f"\n❌ Failed to create EntityExtractor: {e}")

print("="*60)