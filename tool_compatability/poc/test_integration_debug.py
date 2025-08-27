#!/usr/bin/env python3
"""Debug integration issue"""

from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from src.tools.simple_text_loader import SimpleTextLoader
from src.tools.gemini_entity_extractor import GeminiEntityExtractor
from adapters.universal_adapter import UniversalAdapter

# Test simple text loader
print("=== Testing SimpleTextLoader ===")
loader = SimpleTextLoader()
adapted_loader = UniversalAdapter(loader, "simple_text_loader", "process")

# Create test file
with open("test.txt", "w") as f:
    f.write("Brian Chhun works at the University of Melbourne on KGAS.")

result1 = adapted_loader.process("test.txt")
print(f"Success: {result1['success']}")
print(f"Data type: {type(result1['data'])}")
print(f"Data (truncated): {str(result1['data'])[:100]}")
print(f"Uncertainty: {result1['uncertainty']}")

# Test gemini extractor
print("\n=== Testing GeminiEntityExtractor ===")
extractor = GeminiEntityExtractor()
adapted_extractor = UniversalAdapter(extractor, "gemini_entity_extractor", "process")

# Pass the text from loader
text = result1['data'] if isinstance(result1['data'], str) else str(result1['data'])
result2 = adapted_extractor.process(text)
print(f"Success: {result2['success']}")
print(f"Data type: {type(result2['data'])}")
print(f"Data: {result2['data']}")
print(f"Uncertainty: {result2['uncertainty']}")

# Test direct call
print("\n=== Direct call to extractor ===")
direct = extractor.process(text)
print(f"Direct result: {direct}")

import os
os.remove("test.txt")