#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('/home/brian/projects/Digimons')

from src.relationships.cross_document_linker import CrossDocumentLinker

async def debug_evidence_linking():
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
    
    print("=== DEBUGGING EVIDENCE LINKING ===")
    
    # Test claim extraction first
    print("\n--- Claim Extraction ---")
    for doc in sample_documents:
        print(f"\nDocument: {doc['path']}")
        claims = linker._extract_claims(doc['content'])
        print(f"Claims found: {len(claims)}")
        for i, claim in enumerate(claims):
            print(f"  {i+1}. {claim}")
    
    # Test reference matching
    print("\n--- Reference Matching ---")
    for doc in sample_documents:
        doc_path = doc['path']
        metadata = doc.get('metadata', {})
        references = metadata.get('references', [])
        
        print(f"\nDocument: {doc_path}")
        print(f"References: {references}")
        
        for ref in references:
            print(f"  Testing reference: {ref}")
            for other_doc in sample_documents:
                if doc_path != other_doc.get('path', ''):
                    matches = linker._matches_reference(ref, other_doc)
                    if matches:
                        print(f"    -> Matches {other_doc.get('path', '')}: {matches}")
    
    print("\n--- Full Evidence Linking ---")
    result = await linker.link_supporting_evidence(sample_documents)
    
    print(f"Evidence chains found: {len(result.evidence_chains)}")
    for i, chain in enumerate(result.evidence_chains):
        print(f"  Chain {i+1}:")
        print(f"    Primary claim: {chain.primary_claim}")
        print(f"    Supporting docs: {chain.supporting_documents}")
        print(f"    Evidence strength: {chain.evidence_strength}")
        print(f"    Cross references: {chain.cross_references}")
    
    print(f"Cross-reference network edges: {len(result.cross_reference_network.edges())}")
    print(f"Evidence quality scores: {result.evidence_quality_scores}")

if __name__ == "__main__":
    asyncio.run(debug_evidence_linking())