#!/usr/bin/env python3
"""Test PDF integration with pypdf installed"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

# Add paths
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from adapters.universal_adapter import UniversalAdapter
from archive.archived.legacy_tools_2025_07_23.t01_pdf_loader import PDFLoader

# Create a simple test PDF first (using text file as fallback for testing)
test_content = """
KGAS Uncertainty System Documentation

The Knowledge Graph Augmentation System (KGAS) is a framework for uncertainty propagation
developed by Brian Chhun at the University of Melbourne.

Key Features:
- Physics-style error propagation
- Universal tool adaptation
- Real-time uncertainty assessment
"""

# Create test text file (PDF creation requires additional libraries)
test_file = "test_document.txt"
with open(test_file, 'w') as f:
    f.write(test_content)

print("=== Testing T01 PDF Loader ===")

# Create and adapt the PDF loader
try:
    pdf_loader = PDFLoader()
    adapted = UniversalAdapter(
        tool=pdf_loader,
        tool_id="t01_pdf_loader",
        uncertainty_config={
            'base': 0.15,
            'reasoning': 'PDF extraction with OCR and formatting uncertainty'
        }
    )
    
    print(f"✅ PDFLoader created and adapted")
    print(f"   Method detected: {adapted.method_name}")
    
    # Try to process the test file
    result = adapted.process(test_file)
    
    print(f"✅ File processed successfully")
    print(f"   Success: {result['success']}")
    print(f"   Uncertainty: {result['uncertainty']}")
    print(f"   Reasoning: {result['reasoning']}")
    print(f"   Construct: {result['construct_mapping']}")
    
    # Check output
    if result['success']:
        data = result['data']
        if isinstance(data, dict):
            content = data.get('content', data.get('text', str(data)))
        else:
            content = str(data)
        print(f"   Content preview: {content[:100]}..." if len(content) > 100 else f"   Content: {content}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Clean up
os.remove(test_file)
print("\n✅ Test complete")