#!/usr/bin/env python3
"""
Ground Truth Dataset Generator for Thesis Evidence Collection
Creates 10+ documents with varying complexity and known entities/relationships
"""

import os
import json
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class GroundTruthDocument:
    """Ground truth specification for a document"""
    document_id: str
    complexity_level: str  # simple, technical, ambiguous, noisy
    text_content: str
    expected_entities: List[Dict[str, str]]
    expected_relationships: List[Dict[str, str]]
    expected_uncertainty: float
    complexity_factors: Dict[str, Any]

class GroundTruthGenerator:
    """Generate ground truth documents for thesis evaluation"""
    
    def __init__(self, output_dir: str = "ground_truth_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/documents", exist_ok=True)
        os.makedirs(f"{output_dir}/metadata", exist_ok=True)
    
    def generate_all_documents(self) -> List[GroundTruthDocument]:
        """Generate complete ground truth dataset"""
        documents = []
        
        # Simple documents (low uncertainty ~0.15)
        documents.extend(self._generate_simple_documents())
        
        # Technical documents (medium uncertainty ~0.25)
        documents.extend(self._generate_technical_documents())
        
        # Ambiguous documents (higher uncertainty ~0.35)
        documents.extend(self._generate_ambiguous_documents())
        
        # Noisy documents (highest uncertainty ~0.45)
        documents.extend(self._generate_noisy_documents())
        
        # Save all documents
        for doc in documents:
            self._save_document(doc)
        
        # Save master metadata
        self._save_master_metadata(documents)
        
        return documents
    
    def _generate_simple_documents(self) -> List[GroundTruthDocument]:
        """Generate simple, clear documents with obvious entities"""
        documents = []
        
        # Document 1: Basic academic context
        doc1 = GroundTruthDocument(
            document_id="doc_001_simple",
            complexity_level="simple",
            text_content="""
Brian Chhun is a PhD student at the University of Melbourne. 
He developed the KGAS system for knowledge graph analysis.
The system uses Neo4j for graph storage and Python for processing.
His supervisor is Professor Jane Smith from the Computer Science department.
            """.strip(),
            expected_entities=[
                {"name": "Brian Chhun", "type": "PERSON", "confidence": 0.95},
                {"name": "University of Melbourne", "type": "ORGANIZATION", "confidence": 0.95},
                {"name": "KGAS", "type": "SYSTEM", "confidence": 0.90},
                {"name": "Neo4j", "type": "TECHNOLOGY", "confidence": 0.90},
                {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.90},
                {"name": "Jane Smith", "type": "PERSON", "confidence": 0.95},
                {"name": "Computer Science department", "type": "ORGANIZATION", "confidence": 0.85}
            ],
            expected_relationships=[
                {"source": "Brian Chhun", "target": "University of Melbourne", "type": "STUDIES_AT"},
                {"source": "Brian Chhun", "target": "KGAS", "type": "DEVELOPED"},
                {"source": "KGAS", "target": "Neo4j", "type": "USES"},
                {"source": "KGAS", "target": "Python", "type": "USES"},
                {"source": "Jane Smith", "target": "Brian Chhun", "type": "SUPERVISES"},
                {"source": "Jane Smith", "target": "Computer Science department", "type": "MEMBER_OF"}
            ],
            expected_uncertainty=0.15,
            complexity_factors={
                "clarity": "high",
                "entity_density": 7/4,  # 7 entities in 4 sentences
                "ambiguity": "none",
                "technical_terms": ["KGAS", "Neo4j"],
                "noise_level": 0.0
            }
        )
        documents.append(doc1)
        
        # Document 2: Research collaboration
        doc2 = GroundTruthDocument(
            document_id="doc_002_simple",
            complexity_level="simple",
            text_content="""
The research team includes Dr. Michael Chen and Dr. Sarah Johnson.
They collaborate with Brian Chhun on uncertainty quantification methods.
The project received funding from the Australian Research Council in 2024.
Initial results were published in the Journal of Knowledge Graphs.
            """.strip(),
            expected_entities=[
                {"name": "Michael Chen", "type": "PERSON", "confidence": 0.95},
                {"name": "Sarah Johnson", "type": "PERSON", "confidence": 0.95},
                {"name": "Brian Chhun", "type": "PERSON", "confidence": 0.95},
                {"name": "Australian Research Council", "type": "ORGANIZATION", "confidence": 0.95},
                {"name": "Journal of Knowledge Graphs", "type": "PUBLICATION", "confidence": 0.90}
            ],
            expected_relationships=[
                {"source": "Michael Chen", "target": "Brian Chhun", "type": "COLLABORATES_WITH"},
                {"source": "Sarah Johnson", "target": "Brian Chhun", "type": "COLLABORATES_WITH"},
                {"source": "Michael Chen", "target": "Sarah Johnson", "type": "COLLABORATES_WITH"},
                {"source": "Australian Research Council", "target": "project", "type": "FUNDS"},
                {"source": "results", "target": "Journal of Knowledge Graphs", "type": "PUBLISHED_IN"}
            ],
            expected_uncertainty=0.15,
            complexity_factors={
                "clarity": "high",
                "entity_density": 5/4,
                "ambiguity": "none",
                "technical_terms": ["uncertainty quantification"],
                "noise_level": 0.0
            }
        )
        documents.append(doc2)
        
        # Document 3: System components
        doc3 = GroundTruthDocument(
            document_id="doc_003_simple",
            complexity_level="simple",
            text_content="""
KGAS consists of three main components: the IdentityService, the ProvenanceService, and the QualityService.
The IdentityService handles entity resolution and deduplication.
The ProvenanceService tracks all operations and transformations.
The QualityService assesses confidence scores for extracted entities.
            """.strip(),
            expected_entities=[
                {"name": "KGAS", "type": "SYSTEM", "confidence": 0.95},
                {"name": "IdentityService", "type": "COMPONENT", "confidence": 0.95},
                {"name": "ProvenanceService", "type": "COMPONENT", "confidence": 0.95},
                {"name": "QualityService", "type": "COMPONENT", "confidence": 0.95}
            ],
            expected_relationships=[
                {"source": "KGAS", "target": "IdentityService", "type": "HAS_COMPONENT"},
                {"source": "KGAS", "target": "ProvenanceService", "type": "HAS_COMPONENT"},
                {"source": "KGAS", "target": "QualityService", "type": "HAS_COMPONENT"},
                {"source": "IdentityService", "target": "entity resolution", "type": "PERFORMS"},
                {"source": "ProvenanceService", "target": "operations", "type": "TRACKS"},
                {"source": "QualityService", "target": "confidence scores", "type": "ASSESSES"}
            ],
            expected_uncertainty=0.12,
            complexity_factors={
                "clarity": "high",
                "entity_density": 4/4,
                "ambiguity": "none",
                "technical_terms": ["entity resolution", "deduplication", "confidence scores"],
                "noise_level": 0.0
            }
        )
        documents.append(doc3)
        
        return documents
    
    def _generate_technical_documents(self) -> List[GroundTruthDocument]:
        """Generate technical documents with domain-specific terminology"""
        documents = []
        
        # Document 4: Technical implementation
        doc4 = GroundTruthDocument(
            document_id="doc_004_technical",
            complexity_level="technical",
            text_content="""
The system implements physics-style uncertainty propagation using the formula: confidence = ∏(1 - uᵢ).
Graph embeddings are generated using TransE with 384-dimensional vectors.
The Louvain algorithm detects communities with modularity optimization.
Structural Equation Modeling requires conversion to tabular format via the CrossModalService.
            """.strip(),
            expected_entities=[
                {"name": "uncertainty propagation", "type": "METHOD", "confidence": 0.85},
                {"name": "TransE", "type": "ALGORITHM", "confidence": 0.85},
                {"name": "Louvain algorithm", "type": "ALGORITHM", "confidence": 0.85},
                {"name": "Structural Equation Modeling", "type": "METHOD", "confidence": 0.80},
                {"name": "CrossModalService", "type": "COMPONENT", "confidence": 0.90}
            ],
            expected_relationships=[
                {"source": "system", "target": "uncertainty propagation", "type": "IMPLEMENTS"},
                {"source": "Graph embeddings", "target": "TransE", "type": "GENERATED_BY"},
                {"source": "Louvain algorithm", "target": "communities", "type": "DETECTS"},
                {"source": "Structural Equation Modeling", "target": "tabular format", "type": "REQUIRES"},
                {"source": "CrossModalService", "target": "conversion", "type": "PERFORMS"}
            ],
            expected_uncertainty=0.25,
            complexity_factors={
                "clarity": "medium",
                "entity_density": 5/4,
                "ambiguity": "low",
                "technical_terms": ["TransE", "Louvain", "modularity", "SEM", "embeddings"],
                "noise_level": 0.0
            }
        )
        documents.append(doc4)
        
        # Document 5: Architecture details
        doc5 = GroundTruthDocument(
            document_id="doc_005_technical",
            complexity_level="technical",
            text_content="""
The bi-store architecture uses Neo4j 5.13+ with native vector indices for similarity search.
SQLite handles tabular analytics with entity_metrics and correlation_matrix tables.
The ServiceManager implements dependency injection using Python's __init__ pattern.
Pydantic schemas enforce structured output from LLM operations with litellm integration.
            """.strip(),
            expected_entities=[
                {"name": "bi-store architecture", "type": "ARCHITECTURE", "confidence": 0.80},
                {"name": "Neo4j 5.13+", "type": "TECHNOLOGY", "confidence": 0.90},
                {"name": "SQLite", "type": "TECHNOLOGY", "confidence": 0.90},
                {"name": "ServiceManager", "type": "COMPONENT", "confidence": 0.85},
                {"name": "Pydantic", "type": "TECHNOLOGY", "confidence": 0.85},
                {"name": "litellm", "type": "TECHNOLOGY", "confidence": 0.85}
            ],
            expected_relationships=[
                {"source": "bi-store architecture", "target": "Neo4j 5.13+", "type": "USES"},
                {"source": "bi-store architecture", "target": "SQLite", "type": "USES"},
                {"source": "SQLite", "target": "entity_metrics", "type": "HAS_TABLE"},
                {"source": "SQLite", "target": "correlation_matrix", "type": "HAS_TABLE"},
                {"source": "ServiceManager", "target": "dependency injection", "type": "IMPLEMENTS"},
                {"source": "Pydantic schemas", "target": "LLM operations", "type": "ENFORCES"}
            ],
            expected_uncertainty=0.28,
            complexity_factors={
                "clarity": "medium",
                "entity_density": 6/4,
                "ambiguity": "low",
                "technical_terms": ["vector indices", "dependency injection", "schemas", "LLM"],
                "noise_level": 0.0
            }
        )
        documents.append(doc5)
        
        return documents
    
    def _generate_ambiguous_documents(self) -> List[GroundTruthDocument]:
        """Generate documents with ambiguous references"""
        documents = []
        
        # Document 6: Ambiguous pronouns and references
        doc6 = GroundTruthDocument(
            document_id="doc_006_ambiguous",
            complexity_level="ambiguous",
            text_content="""
The system was developed by the team at Melbourne. It uses their framework for analysis.
They integrated it with the existing infrastructure. The service handles this efficiently.
It processes the data and sends it to them for review. They approve it after validation.
            """.strip(),
            expected_entities=[
                {"name": "system", "type": "SYSTEM", "confidence": 0.70},
                {"name": "team", "type": "GROUP", "confidence": 0.65},
                {"name": "Melbourne", "type": "LOCATION", "confidence": 0.75},
                {"name": "framework", "type": "SYSTEM", "confidence": 0.60},
                {"name": "service", "type": "COMPONENT", "confidence": 0.60},
                {"name": "infrastructure", "type": "SYSTEM", "confidence": 0.65}
            ],
            expected_relationships=[
                {"source": "team", "target": "system", "type": "DEVELOPED"},
                {"source": "system", "target": "framework", "type": "USES"},
                {"source": "service", "target": "data", "type": "PROCESSES"},
                {"source": "team", "target": "Melbourne", "type": "LOCATED_AT"}
            ],
            expected_uncertainty=0.35,
            complexity_factors={
                "clarity": "low",
                "entity_density": 6/4,
                "ambiguity": "high",
                "technical_terms": [],
                "noise_level": 0.0,
                "pronoun_references": ["it", "their", "they", "them", "this"]
            }
        )
        documents.append(doc6)
        
        # Document 7: Multiple entities with same name
        doc7 = GroundTruthDocument(
            document_id="doc_007_ambiguous",
            complexity_level="ambiguous",
            text_content="""
Smith published the paper on graph analysis. The Smith algorithm improves performance.
Professor Smith supervises the project, while Dr. Smith from Sydney collaborates remotely.
The analysis shows Smith's method outperforms traditional approaches by Smith et al.
            """.strip(),
            expected_entities=[
                {"name": "Smith", "type": "PERSON", "confidence": 0.60},
                {"name": "Smith algorithm", "type": "ALGORITHM", "confidence": 0.70},
                {"name": "Professor Smith", "type": "PERSON", "confidence": 0.75},
                {"name": "Dr. Smith", "type": "PERSON", "confidence": 0.75},
                {"name": "Sydney", "type": "LOCATION", "confidence": 0.85},
                {"name": "Smith's method", "type": "METHOD", "confidence": 0.65}
            ],
            expected_relationships=[
                {"source": "Smith", "target": "paper", "type": "PUBLISHED"},
                {"source": "Professor Smith", "target": "project", "type": "SUPERVISES"},
                {"source": "Dr. Smith", "target": "Sydney", "type": "LOCATED_AT"},
                {"source": "Smith's method", "target": "traditional approaches", "type": "OUTPERFORMS"}
            ],
            expected_uncertainty=0.38,
            complexity_factors={
                "clarity": "low",
                "entity_density": 6/3,
                "ambiguity": "very high",
                "technical_terms": ["graph analysis"],
                "noise_level": 0.0,
                "name_confusion": "multiple entities named Smith"
            }
        )
        documents.append(doc7)
        
        return documents
    
    def _generate_noisy_documents(self) -> List[GroundTruthDocument]:
        """Generate documents with OCR errors and formatting issues"""
        documents = []
        
        # Document 8: OCR-style errors
        doc8 = GroundTruthDocument(
            document_id="doc_008_noisy",
            complexity_level="noisy",
            text_content="""
Br1an Chhun developcd the KGA5 svstem at the Un1versity of Me1bourne.
The 5ystem uses Ne04j for gr@ph storage and Pyth0n for pr0cessing.
Prof3ssor J@ne Sm!th supervises the pr0ject in the C0mputer Sc1ence dep@rtment.
The Austral!an Research C0uncil pr0vided fund1ng in 2O24.
            """.strip(),
            expected_entities=[
                {"name": "Brian Chhun", "type": "PERSON", "confidence": 0.55},
                {"name": "KGAS", "type": "SYSTEM", "confidence": 0.50},
                {"name": "University of Melbourne", "type": "ORGANIZATION", "confidence": 0.60},
                {"name": "Neo4j", "type": "TECHNOLOGY", "confidence": 0.55},
                {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.60},
                {"name": "Jane Smith", "type": "PERSON", "confidence": 0.50},
                {"name": "Computer Science", "type": "ORGANIZATION", "confidence": 0.55},
                {"name": "Australian Research Council", "type": "ORGANIZATION", "confidence": 0.55}
            ],
            expected_relationships=[
                {"source": "Brian Chhun", "target": "KGAS", "type": "DEVELOPED"},
                {"source": "Brian Chhun", "target": "University of Melbourne", "type": "WORKS_AT"},
                {"source": "KGAS", "target": "Neo4j", "type": "USES"},
                {"source": "Jane Smith", "target": "Brian Chhun", "type": "SUPERVISES"},
                {"source": "Australian Research Council", "target": "project", "type": "FUNDS"}
            ],
            expected_uncertainty=0.45,
            complexity_factors={
                "clarity": "very low",
                "entity_density": 8/4,
                "ambiguity": "medium",
                "technical_terms": [],
                "noise_level": 0.4,
                "ocr_errors": ["Br1an", "KGA5", "svstem", "Un1versity", "Me1bourne", "Ne04j", "gr@ph", "Pyth0n", "pr0cessing"]
            }
        )
        documents.append(doc8)
        
        # Document 9: Mixed formatting and truncation
        doc9 = GroundTruthDocument(
            document_id="doc_009_noisy",
            complexity_level="noisy",
            text_content="""
The KGAS sys... [TRUNCATED] ...developed by Brian Ch
hun at the
University    of     Melbourne.     It   uses
Neo4j for graph
stor
age and Python for data proc...
[ERROR: Page 2 missing]
The system implements uncertain... propaga... using physics-sty... 
formula: conf = ∏(1 - u
            """.strip(),
            expected_entities=[
                {"name": "KGAS", "type": "SYSTEM", "confidence": 0.60},
                {"name": "Brian Chhun", "type": "PERSON", "confidence": 0.45},
                {"name": "University of Melbourne", "type": "ORGANIZATION", "confidence": 0.65},
                {"name": "Neo4j", "type": "TECHNOLOGY", "confidence": 0.70},
                {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.65}
            ],
            expected_relationships=[
                {"source": "Brian Chhun", "target": "KGAS", "type": "DEVELOPED"},
                {"source": "Brian Chhun", "target": "University of Melbourne", "type": "WORKS_AT"},
                {"source": "KGAS", "target": "Neo4j", "type": "USES"},
                {"source": "KGAS", "target": "Python", "type": "USES"}
            ],
            expected_uncertainty=0.48,
            complexity_factors={
                "clarity": "very low",
                "entity_density": 5/8,
                "ambiguity": "high",
                "technical_terms": ["uncertainty propagation"],
                "noise_level": 0.5,
                "formatting_issues": ["truncation", "line breaks", "missing pages", "spacing errors"]
            }
        )
        documents.append(doc9)
        
        # Document 10: Mixed complexity
        doc10 = GroundTruthDocument(
            document_id="doc_010_mixed",
            complexity_level="mixed",
            text_content="""
Brian Chhun's KGAS system at Melbourne University uses advanced techniques.
The syst3m impl3ments physics-style uncerta!nty pr0pagation with confidence = ∏(1 - uᵢ).
It integrates with Neo4j, Python, and the team's custom framework.
Smith and Chen collaborate on this, but Smith from Sydney works on different aspects than Smith the professor.
Results show it outperforms baseline methods by 42% in F1 score.
            """.strip(),
            expected_entities=[
                {"name": "Brian Chhun", "type": "PERSON", "confidence": 0.85},
                {"name": "KGAS", "type": "SYSTEM", "confidence": 0.80},
                {"name": "Melbourne University", "type": "ORGANIZATION", "confidence": 0.85},
                {"name": "Neo4j", "type": "TECHNOLOGY", "confidence": 0.85},
                {"name": "Python", "type": "TECHNOLOGY", "confidence": 0.85},
                {"name": "Smith", "type": "PERSON", "confidence": 0.50},
                {"name": "Chen", "type": "PERSON", "confidence": 0.75},
                {"name": "Sydney", "type": "LOCATION", "confidence": 0.80}
            ],
            expected_relationships=[
                {"source": "Brian Chhun", "target": "KGAS", "type": "OWNS"},
                {"source": "KGAS", "target": "Melbourne University", "type": "LOCATED_AT"},
                {"source": "KGAS", "target": "Neo4j", "type": "INTEGRATES_WITH"},
                {"source": "Smith", "target": "Chen", "type": "COLLABORATES_WITH"},
                {"source": "Smith", "target": "Sydney", "type": "FROM"},
                {"source": "KGAS", "target": "baseline methods", "type": "OUTPERFORMS"}
            ],
            expected_uncertainty=0.32,
            complexity_factors={
                "clarity": "medium",
                "entity_density": 8/5,
                "ambiguity": "medium",
                "technical_terms": ["uncertainty propagation", "F1 score"],
                "noise_level": 0.15,
                "mixed_issues": ["OCR errors", "ambiguous references", "technical content"]
            }
        )
        documents.append(doc10)
        
        return documents
    
    def _save_document(self, doc: GroundTruthDocument):
        """Save document text and metadata"""
        # Save text content
        text_path = f"{self.output_dir}/documents/{doc.document_id}.txt"
        with open(text_path, 'w') as f:
            f.write(doc.text_content)
        
        # Save metadata
        metadata_path = f"{self.output_dir}/metadata/{doc.document_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(asdict(doc), f, indent=2)
        
        print(f"✅ Saved: {doc.document_id} (complexity: {doc.complexity_level}, uncertainty: {doc.expected_uncertainty:.2f})")
    
    def _save_master_metadata(self, documents: List[GroundTruthDocument]):
        """Save master metadata file with all document info"""
        master_data = {
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(documents),
            "complexity_distribution": {},
            "documents": []
        }
        
        # Count complexity levels
        for doc in documents:
            level = doc.complexity_level
            master_data["complexity_distribution"][level] = master_data["complexity_distribution"].get(level, 0) + 1
            
            # Add summary
            master_data["documents"].append({
                "id": doc.document_id,
                "complexity": doc.complexity_level,
                "expected_uncertainty": doc.expected_uncertainty,
                "entity_count": len(doc.expected_entities),
                "relationship_count": len(doc.expected_relationships)
            })
        
        # Save master file
        with open(f"{self.output_dir}/master_metadata.json", 'w') as f:
            json.dump(master_data, f, indent=2)
        
        print(f"\n📊 Dataset Summary:")
        print(f"   Total documents: {len(documents)}")
        print(f"   Complexity distribution: {master_data['complexity_distribution']}")
        print(f"   Average expected uncertainty: {sum(d.expected_uncertainty for d in documents)/len(documents):.3f}")


if __name__ == "__main__":
    print("=== Generating Ground Truth Dataset ===\n")
    
    generator = GroundTruthGenerator(
        output_dir="/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence/ground_truth_data"
    )
    
    documents = generator.generate_all_documents()
    
    print(f"\n✅ Generated {len(documents)} ground truth documents")
    print(f"📁 Location: {generator.output_dir}")