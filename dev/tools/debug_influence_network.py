#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.cross_document_linker import CrossDocumentLinker

async def debug_influence_network():
    sample_documents = [
        {
            "path": "doc1.txt",
            "content": "Dr. Sarah Chen published groundbreaking research on CRISPR gene editing in 2023. Her work at Stanford University focuses on treating genetic diseases using precision medicine approaches.",
            "metadata": {
                "authors": ["Dr. Sarah Chen"],
                "date": "2023-03-15",
                "keywords": ["CRISPR", "gene editing", "genetics", "medicine"],
                "references": ["Smith2022.pdf", "genetic_therapy_review.txt"]
            }
        },
        {
            "path": "doc2.txt", 
            "content": "The CRISPR-Cas9 system has revolutionized biotechnology since Jennifer Doudna's pioneering work led to breakthrough discoveries. Recent advances by researchers like Sarah Chen have shown promising results in clinical trials.",
            "metadata": {
                "authors": ["Dr. Michael Rodriguez"],
                "date": "2023-05-20",
                "keywords": ["CRISPR", "biotechnology", "clinical trials"],
                "references": ["Chen2023.pdf", "doudna_nature.pdf"]
            }
        },
        {
            "path": "doc3.txt",
            "content": "Stanford University's genetics program has been at the forefront of precision medicine. Dr. Chen's recent publication demonstrates the potential of gene therapy for hereditary conditions.",
            "metadata": {
                "authors": ["Prof. Lisa Wang"],
                "date": "2023-07-10", 
                "keywords": ["Stanford", "genetics", "precision medicine", "gene therapy"],
                "references": ["stanford_report.pdf", "Chen2023.pdf"]
            }
        },
        {
            "path": "doc4.txt",
            "content": "Ethical concerns about gene editing have been raised by bioethics committees. While CRISPR offers medical benefits, some argue that genetic modifications could have unintended consequences.",
            "metadata": {
                "authors": ["Dr. Robert Kim"],
                "date": "2023-06-01",
                "keywords": ["ethics", "gene editing", "bioethics", "CRISPR"],
                "references": ["ethics_review.pdf", "bioethics_guidelines.txt"]
            }
        },
        {
            "path": "doc5.txt",
            "content": "Jennifer Doudna received the Nobel Prize for CRISPR development. Her collaboration with Emmanuelle Charpentier laid the foundation for modern gene editing technologies. Doudna's research pioneered the CRISPR revolution.",
            "metadata": {
                "authors": ["Science Reporter"],
                "date": "2023-04-12",
                "keywords": ["Nobel Prize", "Jennifer Doudna", "CRISPR", "collaboration"],
                "references": ["nobel_announcement.pdf", "Doudna_Charpentier2012.pdf"]
            }
        }
    ]

    linker = CrossDocumentLinker()
    
    print("=== DEBUGGING INFLUENCE NETWORK CONSTRUCTION ===")
    
    # Test entity extraction first
    print("\n--- Entity Extraction ---")
    for doc in sample_documents:
        print(f"\nDocument: {doc['path']}")
        entities = linker._extract_entities(doc['content'])
        print(f"Entities: {entities}")
    
    print("\n--- Influence Patterns Testing ---")
    influence_patterns = [
        r'\b(\w+(?:\s+\w+)*)\s+(?:influenced|inspired|mentored|collaborated with)\s+(\w+(?:\s+\w+)*)\b',
        r'\b(\w+(?:\s+\w+)*)\s+(?:based on|building on|following)\s+(\w+(?:\s+\w+)*)\b',
        r'\b(\w+(?:\s+\w+)*)\s+(?:pioneered|developed)\s+.*?(?:used by|adopted by)\s+(\w+(?:\s+\w+)*)\b'
    ]
    
    import re
    for doc in sample_documents:
        content = doc['content']
        print(f"\nDocument: {doc['path']}")
        print(f"Content: {content}")
        
        for i, pattern in enumerate(influence_patterns):
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                print(f"  Pattern {i+1} matches:")
                for match in matches:
                    influencer = match.group(1).strip()
                    influenced = match.group(2).strip()
                    print(f"    - '{influencer}' -> '{influenced}'")
                    print(f"      Valid: {linker._is_valid_entity(influencer)} -> {linker._is_valid_entity(influenced)}")
            else:
                print(f"  Pattern {i+1}: No matches")
    
    # Test reference extraction
    print("\n--- Reference Analysis ---")
    for doc in sample_documents:
        metadata = doc.get('metadata', {})
        authors = metadata.get('authors', [])
        references = metadata.get('references', [])
        
        print(f"\nDocument: {doc['path']}")
        print(f"Authors: {authors}")
        print(f"References: {references}")
        
        for ref in references:
            person = linker._extract_person_from_reference(ref)
            print(f"  Reference '{ref}' -> Person: {person}")
    
    print("\n--- Full Influence Network ---")
    result = await linker.build_influence_network(sample_documents)
    
    print(f"Influence graph: {dict(result.influence_graph)}")
    print(f"Influence scores: {dict(result.influence_scores)}")
    print(f"Influence paths: {result.influence_paths}")

if __name__ == "__main__":
    asyncio.run(debug_influence_network())