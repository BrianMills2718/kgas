#!/usr/bin/env python3
"""TextLoader with uncertainty assessment"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.uncertainty_constants import TEXT_LOADER_UNCERTAINTY, TEXT_LOADER_REASONING

class TextLoaderV3:
    """Text extraction tool with uncertainty assessment"""
    
    def __init__(self):
        self.tool_id = "TextLoaderV3"
        
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from file with uncertainty assessment
        
        Returns:
            Dict with text content, uncertainty, and reasoning
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f"File not found: {file_path}",
                'uncertainty': 1.0,
                'reasoning': "File does not exist"
            }
        
        # Extract text based on file type
        file_extension = file_path.split('.')[-1].lower()
        
        # For MVP, we'll handle simple text files
        try:
            if file_extension in ['txt', 'md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_extension == 'pdf':
                # Simplified PDF extraction for MVP
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() + '\n'
            else:
                # Generic text extraction attempt
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0,
                'reasoning': f"Failed to extract text: {e}"
            }
        
        # Assess uncertainty based on file type
        uncertainty = TEXT_LOADER_UNCERTAINTY.get(file_extension, TEXT_LOADER_UNCERTAINTY["default"])
        reasoning = TEXT_LOADER_REASONING.get(file_extension, TEXT_LOADER_REASONING["default"])
        
        # Add metadata about extraction quality
        if file_extension == 'pdf' and 'encoding' in text.lower():
            uncertainty *= 1.2  # Increase uncertainty for encoded PDFs
            reasoning += " (detected encoding issues)"
        
        return {
            'success': True,
            'text': text,
            'char_count': len(text),
            'file_type': file_extension,
            'uncertainty': min(uncertainty, 1.0),  # Cap at 1.0
            'reasoning': reasoning,
            'construct_mapping': 'file_path → character_sequence'
        }

# Test the tool
if __name__ == "__main__":
    loader = TextLoaderV3()
    
    # Create test file
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document.\nIt has multiple lines.\nAnd contains sample text.")
    
    # Test extraction
    result = loader.process(test_file)
    print(f"Success: {result['success']}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"Reasoning: {result['reasoning']}")
    print(f"Text length: {result.get('char_count', 0)} chars")
    
    # Cleanup
    os.remove(test_file)