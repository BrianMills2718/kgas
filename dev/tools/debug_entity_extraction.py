#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.entity_resolver import EntityResolver

async def debug_entity_extraction():
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
            "content": "The CRISPR-Cas9 system has revolutionized biotechnology since Jennifer Doudna's pioneering work. Recent advances by researchers like Sarah Chen have shown promising results in clinical trials.",
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
            "content": "Jennifer Doudna received the Nobel Prize for CRISPR development. Her collaboration with Emmanuelle Charpentier laid the foundation for modern gene editing technologies.",
            "metadata": {
                "authors": ["Science Reporter"],
                "date": "2023-04-12",
                "keywords": ["Nobel Prize", "Jennifer Doudna", "CRISPR", "collaboration"],
                "references": ["nobel_announcement.pdf", "Doudna_Charpentier2012.pdf"]
            }
        }
    ]

    entity_resolver = EntityResolver()
    
    print("=== DEBUGGING ENTITY EXTRACTION ===")
    
    # Extract entities from each document individually
    for doc in sample_documents:
        print(f"\n--- Document: {doc['path']} ---")
        print(f"Content: {doc['content']}")
        
        entity_refs = entity_resolver._extract_entity_references(doc)
        
        print(f"Found {len(entity_refs)} entity references:")
        for ref in entity_refs:
            print(f"  - {ref.entity_name} (type: {ref.entity_type}, confidence: {ref.confidence_score:.2f})")
            print(f"    Context: {ref.mention_context[:100]}...")
            
        # Also check for CRISPR mentions specifically
        import re
        crispr_pattern = r'\b([A-Z]{2,}(?:-[A-Za-z0-9]+)*)\b'
        matches = re.finditer(crispr_pattern, doc['content'], re.IGNORECASE)
        print(f"  Manual CRISPR pattern matches:")
        for match in matches:
            entity_name = match.group(1)
            print(f"    - Found: '{entity_name}'")
            if "crispr" in entity_name.lower():
                # Test validation
                is_valid = entity_resolver._is_valid_entity_name(entity_name)
                context = doc['content'][max(0, match.start() - 50):match.end() + 50]
                confidence = entity_resolver._calculate_entity_confidence(entity_name, context, "technology")
                print(f"      Valid: {is_valid}, Confidence: {confidence:.2f}")
                print(f"      Context: {context}")
        
        print()
    
    # Now test full coreference resolution
    print("\n=== FULL COREFERENCE RESOLUTION ===")
    result = await entity_resolver.resolve_entity_coreferences(sample_documents)
    
    print(f"Total clusters: {len(result.entity_clusters)}")
    for cluster in result.entity_clusters:
        print(f"\nCluster: {cluster.canonical_name} (type: {cluster.entity_type})")
        print(f"  Confidence: {cluster.cluster_confidence:.2f}")
        print(f"  References ({len(cluster.entity_references)}):")
        for ref in cluster.entity_references:
            print(f"    - {ref.entity_name} from {ref.document_path} (conf: {ref.confidence_score:.2f})")

if __name__ == "__main__":
    asyncio.run(debug_entity_extraction())