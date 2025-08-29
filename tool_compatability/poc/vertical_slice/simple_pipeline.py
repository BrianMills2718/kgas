#!/usr/bin/env python3
"""Simple pipeline using services directly"""

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from services.vector_service import VectorService
from services.table_service import TableService
from tools.text_loader_v3 import TextLoaderV3

def process_document(filepath: str):
    """Simple document processing pipeline"""
    
    # Initialize services
    vector_svc = VectorService()
    table_svc = TableService()
    text_loader = TextLoaderV3()
    
    # Load document
    print(f"Loading {filepath}...")
    result = text_loader.process(filepath)
    text = result.get('text', '')
    
    if not text:
        print("❌ No text extracted")
        return False
    
    print(f"✅ Extracted {len(text)} characters")
    
    # Generate embedding
    print("Generating embedding...")
    embedding = vector_svc.embed_text(text[:1000])  # First 1000 chars
    print(f"✅ Generated {len(embedding)}-dimensional embedding")
    
    # Store in table
    print("Storing in database...")
    row_id = table_svc.save_embedding(filepath, embedding)
    print(f"✅ Stored with ID {row_id}")
    
    # Store metadata
    metadata = {
        'filepath': filepath,
        'text_length': len(text),
        'embedding_dims': len(embedding)
    }
    table_svc.save_data(f"metadata_{filepath}", metadata)
    print("✅ Metadata stored")
    
    return True

if __name__ == "__main__":
    # Test with a simple file
    with open('test_doc.txt', 'w') as f:
        f.write("This is a test document for the simple pipeline.")
    
    if process_document('test_doc.txt'):
        print("\n✅ Pipeline successful!")
    else:
        print("\n❌ Pipeline failed!")