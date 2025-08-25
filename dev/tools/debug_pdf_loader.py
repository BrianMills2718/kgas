#!/usr/bin/env python3
"""
Debug PDF loader issue where it returns empty content
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import get_service_manager
from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.base_tool import ToolRequest

def debug_pdf_loader():
    """Debug the PDF loader issue"""
    
    print("=== Debugging PDF Loader ===")
    
    # Create test text file
    test_file = "/tmp/test_document.txt"
    test_content = """This is a test document for debugging the PDF loader.
    
It contains multiple paragraphs and should be properly extracted.

The loader should return this content when processing the file.
"""
    
    print(f"Creating test file: {test_file}")
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print(f"Test file created with {len(test_content)} characters")
    
    # Initialize service manager and PDF loader
    print("\nInitializing service manager...")
    service_manager = get_service_manager()
    
    print("Creating PDF loader...")
    pdf_loader = T01PDFLoaderUnified(service_manager)
    
    # Test file path validation
    print("\nTesting file path validation...")
    validation_result = pdf_loader._validate_file_path(test_file)
    print(f"Validation result: {validation_result}")
    
    if not validation_result.get("valid", False):
        print("ISSUE: File validation failed!")
        return
    
    # Test text extraction directly
    print("\nTesting direct text extraction...")
    try:
        extraction_result = pdf_loader._extract_text_from_txt(Path(test_file))
        print(f"Extraction result status: {extraction_result.get('status')}")
        print(f"Extracted text length: {len(extraction_result.get('text', ''))}")
        print(f"Page count: {extraction_result.get('page_count')}")
        print(f"First 100 chars: {extraction_result.get('text', '')[:100]}")
    except Exception as e:
        print(f"Direct extraction failed: {e}")
        return
    
    # Test full execute method
    print("\nTesting full execute method...")
    request = ToolRequest(
        tool_id="T01",
        operation="load_document",
        input_data={
            "file_path": test_file,
            "workflow_id": "debug_test"
        },
        parameters={}
    )
    
    try:
        result = pdf_loader.execute(request)
        print(f"Execute result status: {result.status}")
        print(f"Result data keys: {list(result.data.keys()) if result.data else 'None'}")
        
        if result.data and 'document' in result.data:
            doc = result.data['document']
            print(f"Document text length: {doc.get('text_length', 0)}")
            print(f"Document confidence: {doc.get('confidence', 0)}")
            print(f"Document page count: {doc.get('page_count', 0)}")
            print(f"First 100 chars of text: {doc.get('text', '')[:100]}")
        else:
            print("No document data found in result!")
            print(f"Full result: {result}")
    except Exception as e:
        print(f"Execute method failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print(f"\nCleaning up test file: {test_file}")
    os.remove(test_file)
    
    print("=== Debug complete ===")

if __name__ == "__main__":
    debug_pdf_loader()