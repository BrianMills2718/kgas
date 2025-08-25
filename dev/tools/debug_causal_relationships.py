#!/usr/bin/env python3

import asyncio
import sys
import re
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.cross_document_linker import CrossDocumentLinker

async def debug_causal_relationships():
    sample_documents = [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing in 2023. Her work at Stanford University focuses on treating genetic diseases using precision medicine approaches.",
        },
        {
            "path": "doc2.txt", 
            "content": "The CRISPR-Cas9 system has revolutionized biotechnology since Jennifer Doudna's pioneering work led to breakthrough discoveries. Recent advances by researchers like Sarah Chen have shown promising results in clinical trials.",
        },
        {
            "path": "doc3.txt",
            "content": "Stanford University's genetics program has been at the forefront of precision medicine. Dr. Chen's recent publication demonstrates the potential of gene therapy for hereditary conditions.",
        },
        {
            "path": "doc4.txt",
            "content": "Ethical concerns about gene editing have been raised by bioethics committees. While CRISPR offers medical benefits, some argue that genetic modifications could have unintended consequences.",
        },
        {
            "path": "doc5.txt",
            "content": "Jennifer Doudna received the Nobel Prize for CRISPR development. Her collaboration with Emmanuelle Charpentier laid the foundation for modern gene editing technologies. Doudna's research pioneered the CRISPR revolution.",
        }
    ]

    linker = CrossDocumentLinker()
    
    print("=== DEBUGGING CAUSAL RELATIONSHIP DISCOVERY ===")
    
    # Test causal patterns manually - simpler patterns
    causal_patterns = [
        r'([A-Z][a-z]+)\s+(?:pioneered|developed|created)\s+(CRISPR|gene editing|biotechnology)',
        r'(Jennifer Doudna|Doudna).*?(?:led to|pioneered|created)\s+([^\.]+)',
        r'(\w+(?:\s+\w+)*)\s+(?:caused|led to|resulted in|triggered|influenced)\s+(\w+(?:\s+\w+)*)',
        r'(\w+(?:\s+\w+)*)\s+(?:pioneered|developed|created)\s+(\w+(?:\s+\w+)*)'
    ]
    
    print("--- Manual Pattern Testing ---")
    for doc in sample_documents:
        content = doc['content']
        print(f"\nDocument: {doc['path']}")
        print(f"Content: {content}")
        
        found_any = False
        for i, pattern in enumerate(causal_patterns):
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                found_any = True
                print(f"  Pattern {i+1} matches:")
                for match in matches:
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    print(f"    - '{source}' -> '{target}' (full match: '{match.group(0)}')")
                    
                    # Test entity validation
                    source_valid = linker._is_valid_entity(source)
                    target_valid = linker._is_valid_entity(target)
                    print(f"      Source valid: {source_valid}, Target valid: {target_valid}")
        
        if not found_any:
            print("  No causal patterns found")
    
    print("\n--- Full Causal Discovery ---")
    result = await linker.discover_causal_relationships(sample_documents)
    
    print(f"Found {len(result.causal_relationships)} causal relationships:")
    for rel in result.causal_relationships:
        print(f"  - {rel.source_entity} -> {rel.target_entity} (confidence: {rel.confidence_score:.2f})")
        print(f"    Evidence: {rel.evidence_documents}")
        print(f"    Indicators: {rel.causal_indicators}")

if __name__ == "__main__":
    asyncio.run(debug_causal_relationships())