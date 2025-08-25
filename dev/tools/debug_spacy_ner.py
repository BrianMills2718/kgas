#!/usr/bin/env python3
"""
Debug spaCy NER extraction
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

import spacy

def debug_spacy_ner():
    """Debug spaCy NER directly"""
    
    print("=== Testing spaCy NER Directly ===")
    
    # Test text
    test_text = """John Smith is the CEO of TechCorp Corporation, a leading technology company based in San Francisco, California. 

The company was founded in 2010 and has grown rapidly under John's leadership. TechCorp specializes in artificial intelligence and machine learning solutions for enterprise clients.

Mary Johnson, the CTO of TechCorp, leads the engineering team responsible for developing innovative AI products."""
    
    print(f"Test text length: {len(test_text)} characters")
    
    # Load spaCy model directly
    try:
        print("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
        print("spaCy model loaded successfully")
        
        # Process text
        print("Processing text...")
        doc = nlp(test_text)
        
        # Extract entities
        print(f"\nFound {len(doc.ents)} entities:")
        for ent in doc.ents:
            print(f"  - {ent.text} ({ent.label_}) [{ent.start_char}:{ent.end_char}]")
        
        # Check entity types
        entity_types = set(ent.label_ for ent in doc.ents)
        print(f"\nEntity types found: {entity_types}")
        
        # Test filtering
        target_types = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT", 
                       "WORK_OF_ART", "LAW", "LANGUAGE", "DATE", 
                       "TIME", "MONEY", "FACILITY", "LOC", "NORP",
                       "PERCENT", "QUANTITY", "ORDINAL", "CARDINAL"}
        
        filtered_entities = [ent for ent in doc.ents if ent.label_ in target_types]
        print(f"\nFiltered entities ({len(filtered_entities)}):")
        for ent in filtered_entities:
            if len(ent.text.strip()) >= 2:  # Apply length filter
                print(f"  - {ent.text} ({ent.label_})")
        
    except OSError as e:
        if "Can't find model" in str(e):
            print("spaCy model not found. Installing...")
            import subprocess
            result = subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                                  capture_output=True, text=True)
            print(f"Installation result: {result.returncode}")
            if result.returncode == 0:
                print("Model installed, trying again...")
                debug_spacy_ner()
            else:
                print(f"Installation failed: {result.stderr}")
        else:
            print(f"Error loading spaCy: {e}")

if __name__ == "__main__":
    debug_spacy_ner()