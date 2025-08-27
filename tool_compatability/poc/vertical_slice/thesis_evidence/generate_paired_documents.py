#!/usr/bin/env python3
"""Generate paired documents for valid uncertainty comparison"""

import json
import os
import random
from pathlib import Path

class PairedDocumentGenerator:
    def __init__(self):
        self.base_dir = Path("ground_truth_paired")
        self.base_dir.mkdir(exist_ok=True)
        (self.base_dir / "documents").mkdir(exist_ok=True)
        (self.base_dir / "metadata").mkdir(exist_ok=True)
        
        # Base documents - each will have clean and noisy versions
        self.base_documents = [
            {
                "id": "doc_A",
                "content": """Brian Chhun is a PhD student at the University of Melbourne. 
He developed the KGAS system for knowledge graph analysis.
The system uses Neo4j for graph storage and Python for processing.
His supervisor is Professor Jane Smith from the Computer Science department.""",
                "entities": [
                    {"name": "Brian Chhun", "type": "PERSON"},
                    {"name": "University of Melbourne", "type": "ORGANIZATION"},
                    {"name": "KGAS", "type": "SYSTEM"},
                    {"name": "Neo4j", "type": "TECHNOLOGY"},
                    {"name": "Python", "type": "TECHNOLOGY"},
                    {"name": "Jane Smith", "type": "PERSON"},
                    {"name": "Computer Science department", "type": "ORGANIZATION"}
                ],
                "relationships": [
                    {"source": "Brian Chhun", "target": "University of Melbourne", "type": "STUDIES_AT"},
                    {"source": "Brian Chhun", "target": "KGAS", "type": "DEVELOPED"},
                    {"source": "KGAS", "target": "Neo4j", "type": "USES"},
                    {"source": "KGAS", "target": "Python", "type": "USES"},
                    {"source": "Jane Smith", "target": "Brian Chhun", "type": "SUPERVISES"},
                    {"source": "Jane Smith", "target": "Computer Science department", "type": "MEMBER_OF"}
                ]
            },
            {
                "id": "doc_B",
                "content": """The research team includes Dr. Michael Chen and Dr. Sarah Johnson.
They collaborate on uncertainty quantification methods for knowledge graphs.
The project received funding from the Australian Research Council in 2024.
Initial results were published in the Journal of Knowledge Graphs.""",
                "entities": [
                    {"name": "Michael Chen", "type": "PERSON"},
                    {"name": "Sarah Johnson", "type": "PERSON"},
                    {"name": "Australian Research Council", "type": "ORGANIZATION"},
                    {"name": "Journal of Knowledge Graphs", "type": "ORGANIZATION"}
                ],
                "relationships": [
                    {"source": "Michael Chen", "target": "Sarah Johnson", "type": "COLLABORATES_WITH"},
                    {"source": "Australian Research Council", "target": "Michael Chen", "type": "FUNDS"},
                    {"source": "Australian Research Council", "target": "Sarah Johnson", "type": "FUNDS"}
                ]
            },
            {
                "id": "doc_C",
                "content": """DataCorp acquired TechStartup for $50 million in a strategic merger.
The CEO John Williams announced the integration of their AI platform.
The new system will process customer data using machine learning algorithms.
Emily Davis leads the technical integration team from headquarters in Sydney.""",
                "entities": [
                    {"name": "DataCorp", "type": "ORGANIZATION"},
                    {"name": "TechStartup", "type": "ORGANIZATION"},
                    {"name": "John Williams", "type": "PERSON"},
                    {"name": "AI platform", "type": "SYSTEM"},
                    {"name": "Emily Davis", "type": "PERSON"},
                    {"name": "Sydney", "type": "LOCATION"}
                ],
                "relationships": [
                    {"source": "DataCorp", "target": "TechStartup", "type": "ACQUIRED"},
                    {"source": "John Williams", "target": "DataCorp", "type": "CEO_OF"},
                    {"source": "Emily Davis", "target": "DataCorp", "type": "WORKS_AT"},
                    {"source": "DataCorp", "target": "Sydney", "type": "LOCATED_IN"}
                ]
            },
            {
                "id": "doc_D", 
                "content": """The quantum computing research involves complex mathematical frameworks.
Professor Zhang developed novel error correction algorithms at MIT.
The approach uses topological quantum codes for fault tolerance.
Google and IBM are competing to achieve quantum supremacy.""",
                "entities": [
                    {"name": "Professor Zhang", "type": "PERSON"},
                    {"name": "MIT", "type": "ORGANIZATION"},
                    {"name": "Google", "type": "ORGANIZATION"},
                    {"name": "IBM", "type": "ORGANIZATION"},
                    {"name": "quantum computing", "type": "TECHNOLOGY"},
                    {"name": "error correction algorithms", "type": "CONCEPT"},
                    {"name": "topological quantum codes", "type": "CONCEPT"}
                ],
                "relationships": [
                    {"source": "Professor Zhang", "target": "MIT", "type": "WORKS_AT"},
                    {"source": "Professor Zhang", "target": "error correction algorithms", "type": "DEVELOPED"},
                    {"source": "Google", "target": "quantum computing", "type": "RESEARCHES"},
                    {"source": "IBM", "target": "quantum computing", "type": "RESEARCHES"}
                ]
            },
            {
                "id": "doc_E",
                "content": """Climate change affects global food security and water resources.
The United Nations released a report on sustainable development goals.
Dr. Martinez coordinates international efforts from Geneva offices.
Rising temperatures threaten agricultural yields in developing nations.""",
                "entities": [
                    {"name": "United Nations", "type": "ORGANIZATION"},
                    {"name": "Dr. Martinez", "type": "PERSON"},
                    {"name": "Geneva", "type": "LOCATION"},
                    {"name": "climate change", "type": "CONCEPT"},
                    {"name": "food security", "type": "CONCEPT"},
                    {"name": "sustainable development goals", "type": "CONCEPT"}
                ],
                "relationships": [
                    {"source": "Dr. Martinez", "target": "United Nations", "type": "WORKS_AT"},
                    {"source": "United Nations", "target": "Geneva", "type": "LOCATED_IN"},
                    {"source": "United Nations", "target": "sustainable development goals", "type": "PUBLISHED"}
                ]
            }
        ]
    
    def add_ocr_noise(self, text: str, noise_level: float = 0.15) -> str:
        """Add OCR-style noise to text"""
        replacements = {
            'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '5',
            'A': '@', 'E': '3', 'I': '1', 'O': '0', 'S': '5'
        }
        
        noisy = []
        for char in text:
            if char.isalpha() and random.random() < noise_level:
                # OCR error
                if char in replacements and random.random() < 0.7:
                    noisy.append(replacements[char])
                else:
                    noisy.append(char)
            else:
                noisy.append(char)
        
        return ''.join(noisy)
    
    def add_truncation_noise(self, text: str) -> str:
        """Add truncation and missing text"""
        lines = text.split('\n')
        noisy_lines = []
        
        for i, line in enumerate(lines):
            if i == 0:
                # Truncate beginning
                noisy_lines.append(line[:len(line)//2] + "... [TRUNCATED]")
            elif i == len(lines) - 1:
                # Missing end
                noisy_lines.append(line[:len(line)//3] + "...")
            else:
                # Random spacing issues
                if random.random() < 0.3:
                    words = line.split()
                    spaced = '    '.join(words)
                    noisy_lines.append(spaced)
                else:
                    noisy_lines.append(line)
        
        return '\n'.join(noisy_lines)
    
    def generate_paired_documents(self):
        """Generate clean and noisy versions of each document"""
        documents = []
        metadata = {}
        
        doc_id = 1
        for base_doc in self.base_documents:
            # Clean version
            clean_id = f"doc_{doc_id:03d}_clean"
            clean_path = self.base_dir / "documents" / f"{clean_id}.txt"
            
            with open(clean_path, 'w') as f:
                f.write(base_doc["content"])
            
            metadata[clean_id] = {
                "document_id": clean_id,
                "base_id": base_doc["id"],
                "complexity_level": "clean",
                "text_content": base_doc["content"],
                "expected_entities": base_doc["entities"],
                "expected_relationships": base_doc["relationships"],
                "expected_uncertainty": 0.15,
                "noise_type": "none"
            }
            documents.append(clean_id)
            doc_id += 1
            
            # OCR noise version
            ocr_id = f"doc_{doc_id:03d}_ocr"
            ocr_content = self.add_ocr_noise(base_doc["content"], noise_level=0.15)
            ocr_path = self.base_dir / "documents" / f"{ocr_id}.txt"
            
            with open(ocr_path, 'w') as f:
                f.write(ocr_content)
            
            metadata[ocr_id] = {
                "document_id": ocr_id,
                "base_id": base_doc["id"],
                "complexity_level": "ocr_noise",
                "text_content": ocr_content,
                "expected_entities": base_doc["entities"],
                "expected_relationships": base_doc["relationships"],
                "expected_uncertainty": 0.45,
                "noise_type": "ocr"
            }
            documents.append(ocr_id)
            doc_id += 1
            
            # Heavy noise version
            heavy_id = f"doc_{doc_id:03d}_heavy"
            heavy_content = self.add_ocr_noise(base_doc["content"], noise_level=0.35)
            heavy_content = self.add_truncation_noise(heavy_content)
            heavy_path = self.base_dir / "documents" / f"{heavy_id}.txt"
            
            with open(heavy_path, 'w') as f:
                f.write(heavy_content)
            
            metadata[heavy_id] = {
                "document_id": heavy_id,
                "base_id": base_doc["id"],
                "complexity_level": "heavy_noise",
                "text_content": heavy_content,
                "expected_entities": base_doc["entities"],
                "expected_relationships": base_doc["relationships"],
                "expected_uncertainty": 0.75,
                "noise_type": "ocr+truncation"
            }
            documents.append(heavy_id)
            doc_id += 1
        
        # Save individual metadata files
        for doc_id, meta in metadata.items():
            meta_path = self.base_dir / "metadata" / f"{doc_id}.json"
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
        
        # Save master metadata
        master = {
            "total_documents": len(documents),
            "base_documents": len(self.base_documents),
            "noise_levels": ["clean", "ocr_noise", "heavy_noise"],
            "documents": documents,
            "metadata": metadata
        }
        
        with open(self.base_dir / "master_metadata.json", 'w') as f:
            json.dump(master, f, indent=2)
        
        print(f"✅ Generated {len(documents)} paired documents:")
        print(f"   - {len(self.base_documents)} base documents")
        print(f"   - 3 versions each (clean, OCR noise, heavy noise)")
        print(f"   - Saved to {self.base_dir}/")
        
        return documents

if __name__ == "__main__":
    generator = PairedDocumentGenerator()
    generator.generate_paired_documents()