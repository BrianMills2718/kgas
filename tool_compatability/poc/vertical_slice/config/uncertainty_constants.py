#!/usr/bin/env python3
"""
Configurable uncertainty constants for deterministic operations
These are clearly labeled and easily adjustable
"""

# TextLoader uncertainties by file type
TEXT_LOADER_UNCERTAINTY = {
    "pdf": 0.15,      # OCR challenges, formatting loss
    "txt": 0.02,      # Nearly perfect extraction
    "docx": 0.08,     # Some formatting complexity
    "html": 0.12,     # Tag stripping, structure loss
    "md": 0.03,       # Clean markdown extraction
    "rtf": 0.10,      # Format conversion challenges
    "default": 0.10   # Unknown file types
}

# Reasoning templates
TEXT_LOADER_REASONING = {
    "pdf": "PDF extraction may have OCR errors or formatting loss",
    "txt": "Plain text extraction with minimal uncertainty",
    "docx": "Word document with potential formatting complexity",
    "html": "HTML parsing may lose semantic structure",
    "md": "Markdown extraction preserves structure well",
    "default": "Standard uncertainty for file format extraction"
}