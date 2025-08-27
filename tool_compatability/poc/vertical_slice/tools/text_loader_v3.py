#!/usr/bin/env python3
"""TextLoader with uncertainty assessment"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.uncertainty_constants import TEXT_LOADER_UNCERTAINTY, TEXT_LOADER_REASONING

class TextLoaderV3:
    """Text extraction tool with uncertainty assessment"""
    
    def __init__(self):
        self.tool_id = "TextLoaderV3"
        self.uncertainty_constants = TEXT_LOADER_UNCERTAINTY
        self.reasoning_templates = TEXT_LOADER_REASONING
    
    def _assess_text_quality(self, text: str, file_type: str) -> Tuple[float, List[str]]:
        """
        Detect ACTUAL quality problems in text
        Returns: (quality_uncertainty, list_of_issues)
        """
        quality_uncertainty = 0.0
        issues = []
        
        # 1. OCR Error Detection - CRITICAL for thesis
        # Exclude known valid patterns like Neo4j, GPT-4, etc.
        known_valid = ['Neo4j', 'GPT-4', 'GPT-3', 'F1', 'COVID-19', '3D', '2D']
        
        ocr_patterns = [
            (r'\b[A-Za-z]+[0-9][a-z]+\b', "digit in middle of word"),  # Br1an, Un1versity, pr0cessing
            (r'[!@#]+[a-zA-Z]', "symbol before letter"),  # @ne, !th
            (r'[a-zA-Z][!@#]+[a-zA-Z]', "symbol in word"),  # gr@ph, Sm!th
            (r'\b[0-9][A-Za-z]{2,}', "digit at start of word")  # 5ystem, 2O24
        ]
        
        total_words = len(text.split())
        total_ocr_errors = 0
        
        for pattern, description in ocr_patterns:
            matches = re.findall(pattern, text)
            # Filter out known valid patterns
            filtered_matches = [m for m in matches if m not in known_valid and not any(m.startswith(v) or m.endswith(v) for v in known_valid)]
            if filtered_matches:
                total_ocr_errors += len(filtered_matches)
                issues.append(f"{description}: {filtered_matches[:3]}")  # Show first 3 examples
        
        # Calculate OCR error rate
        if total_words > 0:
            ocr_error_rate = total_ocr_errors / total_words
            if ocr_error_rate > 0.01:  # >1% corrupted words
                quality_uncertainty += min(ocr_error_rate * 5, 0.4)  # Cap at 0.4
                issues.append(f"OCR error rate: {ocr_error_rate:.1%}")
        
        # 2. Truncation Detection
        truncation_markers = ['[TRUNCATED]', '[ERROR', 'Page missing', '...']
        for marker in truncation_markers:
            if marker in text:
                quality_uncertainty += 0.2
                issues.append(f"truncation: {marker}")
                break
        
        # 3. Formatting Issues
        # Excessive line breaks
        if text.count('\n\n\n') > 0:
            quality_uncertainty += 0.05
            issues.append("excessive line breaks")
        
        # Broken words across lines (simple check)
        if re.search(r'\w+\n\w+', text):
            quality_uncertainty += 0.05
            issues.append("broken word continuation")
        
        # Multiple spaces
        if '    ' in text or '\t\t' in text:
            quality_uncertainty += 0.03
            issues.append("irregular spacing")
        
        return min(quality_uncertainty, 0.5), issues  # Cap at 0.5 for text quality
        
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
        
        # Get base uncertainty for file type
        base_uncertainty = self.uncertainty_constants.get(file_extension, self.uncertainty_constants["default"])
        base_reasoning = self.reasoning_templates.get(file_extension, self.reasoning_templates["default"])
        
        # NEW: Assess actual text quality
        quality_uncertainty, quality_issues = self._assess_text_quality(text, file_extension)
        
        # Combine uncertainties
        total_uncertainty = min(base_uncertainty + quality_uncertainty, 0.95)
        
        # Build detailed reasoning
        if quality_issues:
            reasoning = f"{base_reasoning} | Quality issues: {'; '.join(quality_issues)}"
        else:
            reasoning = base_reasoning
        
        return {
            'success': True,
            'text': text,
            'char_count': len(text),
            'file_type': file_extension,
            'uncertainty': total_uncertainty,
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