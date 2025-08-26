#!/usr/bin/env python3
"""
Simple Text Loader - A real production tool for loading text files
"""

from pathlib import Path
from typing import Dict, Any

class SimpleTextLoader:
    """
    Simple tool for loading text from files.
    Real implementation, no mocks.
    """
    
    def __init__(self):
        self.tool_id = "SimpleTextLoader"
        self.name = "Simple Text Loader"
        self.input_type = "file"  # Will be mapped to DataType.FILE
        self.output_type = "text"  # Will be mapped to DataType.TEXT
        
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Load text from a file
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Dict with text content and metadata
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            content = path.read_text(encoding='utf-8')
            
            return {
                'content': content,
                'file_path': str(path.absolute()),
                'size_bytes': path.stat().st_size,
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to load file: {e}")