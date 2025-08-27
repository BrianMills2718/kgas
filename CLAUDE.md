# Thesis Evidence Collection Phase - KGAS Uncertainty System

## ⚠️ PERMANENT - DO NOT REMOVE ⚠️

### API Configuration
- **API Keys Location**: `/home/brian/projects/Digimons/.env`
- **Default LLM Model**: `gemini/gemini-1.5-flash` via litellm
- **Always load .env first** before claiming API keys are missing
```python
from dotenv import load_dotenv
import os

# ALWAYS load from the project .env file
load_dotenv('/home/brian/projects/Digimons/.env')
api_key = os.getenv('GEMINI_API_KEY')
```

### Tool Deprecation Notice
- **Spacy is DEPRECATED** - Do NOT use or integrate any tools requiring spacy
- **Deprecated Tools**: t23a_spacy_ner, t27_relationship_extractor

---

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them
  - No graceful error handling that returns success=False
  - No returning 1.0 uncertainty on failure
  - Raise exceptions immediately when tools fail
  - Print clear error messages before raising
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files  
- **TEST DRIVEN DESIGN**: Write tests first where possible

### Evidence Requirements
```
evidence/
├── current/
│   └── Evidence_ThesisMetrics_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md                      # Archived completed work
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Test with REAL data and services
- Archive completed phases to avoid chronological confusion

---

## 2. Codebase Structure

### Core Systems
```
tool_compatability/poc/vertical_slice/
├── framework/
│   └── clean_framework.py          # Main framework with uncertainty propagation
├── tools/
│   ├── text_loader_v3.py          # Text extraction (0.02 uncertainty)
│   ├── knowledge_graph_extractor.py # Entity+relationship extraction (0.25 uncertainty)
│   └── graph_persister.py         # Neo4j persistence (0.0 uncertainty)
├── services/
│   ├── identity_service_v3.py     # Entity deduplication
│   ├── crossmodal_service.py      # Graph↔table conversion
│   └── provenance_enhanced.py     # Operation tracking with uncertainty
├── adapters/
│   └── universal_adapter.py       # Wraps any tool for framework (FAIL-FAST)
└── tests/
    └── test_vertical_slice.py     # End-to-end pipeline test
```

### Key Integration Points
- **Virtual Environment**: `/home/brian/projects/Digimons/.venv` (has pypdf installed)
- **Neo4j**: `bolt://localhost:7687` with auth `("neo4j", "devpassword")`
- **SQLite**: `vertical_slice.db` for metrics storage
- **Integrated Tools**: 7 tools working (see completed evidence)

### Important Files
- `/docs/architecture/architecture_changes_20250827.md` - QualityService removal decision
- `/evidence/completed/Evidence_ToolIntegration_Complete.md` - Tool integration details
- `/tool_compatability/poc/vertical_slice/test_proper_kg_extraction.py` - Correct KG extraction

---

## 3. Current Phase: Thesis Evidence Collection

### Objective
Systematically collect quantitative evidence demonstrating the KGAS uncertainty propagation system's effectiveness for academic thesis.

### Success Criteria
- [ ] Uncertainty propagation metrics across 10+ diverse documents
- [ ] Accuracy measurements against ground truth datasets
- [ ] Performance benchmarks (time, memory, scalability)
- [ ] Statistical analysis of uncertainty vs actual errors
- [ ] Visualizations of uncertainty propagation
- [ ] Comparison with baseline approaches

---

## 4. Phase 1: Create Evidence Collection Framework

### Task 1.1: Ground Truth Dataset Preparation

**File**: Create `/tool_compatability/poc/thesis_evidence/ground_truth_generator.py`

```python
#!/usr/bin/env python3
"""Generate ground truth datasets for accuracy measurement"""

import json
from typing import List, Dict, Any
from pathlib import Path

class GroundTruthGenerator:
    """Create annotated datasets for evaluation"""
    
    def __init__(self, output_dir: str = "thesis_evidence/ground_truth"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_document_set(self) -> List[Dict]:
        """Create diverse test documents with known entities"""
        documents = []
        
        # Document 1: Simple academic paper
        doc1 = {
            "id": "doc1_simple",
            "text": """
            The Knowledge Graph Augmentation System (KGAS) was developed by Brian Chhun
            at the University of Melbourne in 2024. The system uses uncertainty propagation
            to track confidence through transformation pipelines.
            """,
            "expected_entities": [
                {"name": "Knowledge Graph Augmentation System (KGAS)", "type": "system"},
                {"name": "Brian Chhun", "type": "person"},
                {"name": "University of Melbourne", "type": "organization"},
                {"name": "2024", "type": "date"}
            ],
            "expected_relationships": [
                {"source": "Brian Chhun", "target": "KGAS", "type": "developed"},
                {"source": "Brian Chhun", "target": "University of Melbourne", "type": "affiliated_with"},
                {"source": "KGAS", "target": "2024", "type": "created_in"}
            ],
            "complexity": "simple"
        }
        documents.append(doc1)
        
        # Document 2: Complex with ambiguous entities
        doc2 = {
            "id": "doc2_ambiguous",
            "text": """
            Smith et al. (2023) argue that Smith's earlier work contradicts Smith (2021).
            The University system processes data using the University's algorithm,
            which the University claims is superior to other University methods.
            """,
            "expected_entities": [
                {"name": "Smith", "type": "person", "mentions": 3},
                {"name": "University", "type": "organization", "mentions": 4}
            ],
            "expected_relationships": [
                {"source": "Smith", "target": "Smith", "type": "contradicts"}
            ],
            "complexity": "ambiguous"
        }
        documents.append(doc2)
        
        # Add 8 more diverse documents...
        # (Implementation should include various complexity levels)
        
        return documents
    
    def save_ground_truth(self, documents: List[Dict]):
        """Save ground truth to JSON files"""
        for doc in documents:
            output_file = self.output_dir / f"{doc['id']}.json"
            with open(output_file, 'w') as f:
                json.dump(doc, f, indent=2)
            print(f"Saved ground truth: {output_file}")
    
    def create_complexity_matrix(self) -> Dict:
        """Define complexity factors affecting uncertainty"""
        return {
            "simple": {"expected_uncertainty": 0.15, "factors": ["clear_entities", "explicit_relations"]},
            "ambiguous": {"expected_uncertainty": 0.35, "factors": ["entity_ambiguity", "coreference"]},
            "technical": {"expected_uncertainty": 0.25, "factors": ["domain_specific", "abbreviations"]},
            "noisy": {"expected_uncertainty": 0.45, "factors": ["OCR_errors", "formatting_issues"]},
            "long": {"expected_uncertainty": 0.30, "factors": ["length", "topic_drift"]}
        }

if __name__ == "__main__":
    generator = GroundTruthGenerator()
    documents = generator.create_document_set()
    generator.save_ground_truth(documents)
    
    complexity = generator.create_complexity_matrix()
    with open("thesis_evidence/complexity_matrix.json", 'w') as f:
        json.dump(complexity, f, indent=2)
    
    print(f"\n✅ Created {len(documents)} ground truth documents")
    print("✅ Saved complexity matrix")
```

**Evidence Required**: `evidence/current/Evidence_ThesisMetrics_GroundTruth.md`
- Show all 10 documents created
- Display complexity matrix
- Verify JSON files saved correctly

### Task 1.2: Metrics Collection Framework

**File**: Create `/tool_compatability/poc/thesis_evidence/metrics_collector.py`

```python
#!/usr/bin/env python3
"""Collect comprehensive metrics for thesis evidence"""

import time
import json
import psutil
import sqlite3
from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PipelineMetrics:
    """Metrics for a single pipeline execution"""
    document_id: str
    pipeline_steps: List[str]
    
    # Uncertainty metrics
    step_uncertainties: List[float]
    combined_uncertainty: float
    expected_uncertainty: float
    uncertainty_error: float
    
    # Accuracy metrics
    entities_extracted: int
    entities_expected: int
    entity_precision: float
    entity_recall: float
    entity_f1: float
    
    relationships_extracted: int
    relationships_expected: int
    relationship_precision: float
    relationship_recall: float
    relationship_f1: float
    
    # Performance metrics
    execution_time: float
    memory_peak_mb: float
    memory_delta_mb: float
    
    # Metadata
    timestamp: str
    document_complexity: str
    document_length: int

class MetricsCollector:
    """Collect and analyze thesis evidence metrics"""
    
    def __init__(self, db_path: str = "thesis_metrics.db"):
        self.db_path = db_path
        self._setup_database()
        self.start_memory = None
        self.start_time = None
    
    def _setup_database(self):
        """Create metrics storage tables"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_metrics (
                run_id TEXT PRIMARY KEY,
                document_id TEXT,
                pipeline_steps TEXT,
                step_uncertainties TEXT,
                combined_uncertainty REAL,
                expected_uncertainty REAL,
                uncertainty_error REAL,
                entities_extracted INTEGER,
                entities_expected INTEGER,
                entity_precision REAL,
                entity_recall REAL,
                entity_f1 REAL,
                relationships_extracted INTEGER,
                relationships_expected INTEGER,
                relationship_precision REAL,
                relationship_recall REAL,
                relationship_f1 REAL,
                execution_time REAL,
                memory_peak_mb REAL,
                memory_delta_mb REAL,
                timestamp TEXT,
                document_complexity TEXT,
                document_length INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    def start_collection(self):
        """Start collecting metrics"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    def end_collection(self, 
                      pipeline_result: Any,
                      ground_truth: Dict,
                      extracted_data: Dict) -> PipelineMetrics:
        """Calculate final metrics"""
        execution_time = time.time() - self.start_time
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_delta = peak_memory - self.start_memory
        
        # Calculate accuracy metrics
        entity_metrics = self._calculate_entity_accuracy(
            extracted_data.get('entities', []),
            ground_truth.get('expected_entities', [])
        )
        
        relationship_metrics = self._calculate_relationship_accuracy(
            extracted_data.get('relationships', []),
            ground_truth.get('expected_relationships', [])
        )
        
        # Calculate uncertainty error
        uncertainty_error = abs(
            pipeline_result.total_uncertainty - 
            ground_truth.get('expected_uncertainty', 0.25)
        )
        
        return PipelineMetrics(
            document_id=ground_truth['id'],
            pipeline_steps=pipeline_result.chain,
            step_uncertainties=pipeline_result.step_uncertainties,
            combined_uncertainty=pipeline_result.total_uncertainty,
            expected_uncertainty=ground_truth.get('expected_uncertainty', 0.25),
            uncertainty_error=uncertainty_error,
            entities_extracted=len(extracted_data.get('entities', [])),
            entities_expected=len(ground_truth.get('expected_entities', [])),
            entity_precision=entity_metrics['precision'],
            entity_recall=entity_metrics['recall'],
            entity_f1=entity_metrics['f1'],
            relationships_extracted=len(extracted_data.get('relationships', [])),
            relationships_expected=len(ground_truth.get('expected_relationships', [])),
            relationship_precision=relationship_metrics['precision'],
            relationship_recall=relationship_metrics['recall'],
            relationship_f1=relationship_metrics['f1'],
            execution_time=execution_time,
            memory_peak_mb=peak_memory,
            memory_delta_mb=memory_delta,
            timestamp=datetime.now().isoformat(),
            document_complexity=ground_truth.get('complexity', 'unknown'),
            document_length=len(ground_truth.get('text', ''))
        )
    
    def _calculate_entity_accuracy(self, extracted: List, expected: List) -> Dict:
        """Calculate precision, recall, F1 for entities"""
        extracted_names = {e.get('name', e.get('text', '')).lower() for e in extracted}
        expected_names = {e['name'].lower() for e in expected}
        
        true_positives = len(extracted_names & expected_names)
        false_positives = len(extracted_names - expected_names)
        false_negatives = len(expected_names - extracted_names)
        
        precision = true_positives / (true_positives + false_positives) if extracted_names else 0
        recall = true_positives / (true_positives + false_negatives) if expected_names else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {'precision': precision, 'recall': recall, 'f1': f1}
    
    def _calculate_relationship_accuracy(self, extracted: List, expected: List) -> Dict:
        """Calculate precision, recall, F1 for relationships"""
        # Similar to entity accuracy but for relationships
        # (Implementation details...)
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}  # Placeholder
    
    def save_metrics(self, metrics: PipelineMetrics):
        """Save metrics to database"""
        conn = sqlite3.connect(self.db_path)
        # Convert dataclass to dict and save
        # (Implementation...)
        conn.close()
        
    def generate_summary_statistics(self) -> Dict:
        """Generate summary statistics for thesis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Average uncertainty by complexity
        cursor.execute("""
            SELECT document_complexity, 
                   AVG(combined_uncertainty) as avg_uncertainty,
                   AVG(uncertainty_error) as avg_error,
                   AVG(entity_f1) as avg_entity_f1,
                   AVG(execution_time) as avg_time
            FROM pipeline_metrics
            GROUP BY document_complexity
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return {
            'by_complexity': results,
            'total_documents': len(results)
        }
```

**Evidence Required**: `evidence/current/Evidence_ThesisMetrics_Framework.md`
- Show database creation
- Demonstrate metrics calculation
- Test with sample data

---

## 5. Phase 2: Execute Evidence Collection

### Task 2.1: Run Pipeline Tests

**File**: Create `/tool_compatability/poc/thesis_evidence/run_experiments.py`

```python
#!/usr/bin/env python3
"""Execute experiments for thesis evidence collection"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

# Add paths
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
from tools.graph_persister import GraphPersister
from thesis_evidence.metrics_collector import MetricsCollector, PipelineMetrics
from thesis_evidence.ground_truth_generator import GroundTruthGenerator

def run_experiment(document: Dict, framework: CleanToolFramework, collector: MetricsCollector) -> PipelineMetrics:
    """Run single experiment with metrics collection"""
    
    # Save document to file
    doc_file = f"temp_{document['id']}.txt"
    with open(doc_file, 'w') as f:
        f.write(document['text'])
    
    # Start metrics collection
    collector.start_collection()
    
    # Execute pipeline
    chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    result = framework.execute_chain(chain, doc_file)
    
    # Extract entities and relationships from result
    # (Parse from result.data - implementation needed)
    extracted_data = {
        'entities': [],  # Parse from result
        'relationships': []  # Parse from result
    }
    
    # End collection and calculate metrics
    metrics = collector.end_collection(result, document, extracted_data)
    
    # Clean up
    import os
    os.remove(doc_file)
    
    return metrics

def main():
    """Run all experiments"""
    print("="*60)
    print("THESIS EVIDENCE COLLECTION")
    print("="*60)
    
    # Initialize
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="vertical_slice.db"
    )
    
    # Register tools
    framework.register_tool(TextLoaderV3(), ToolCapabilities(
        tool_id="TextLoaderV3",
        input_type=DataType.FILE,
        output_type=DataType.TEXT,
        input_construct="file_path",
        output_construct="character_sequence",
        transformation_type="text_extraction"
    ))
    
    framework.register_tool(KnowledgeGraphExtractor(), ToolCapabilities(
        tool_id="KnowledgeGraphExtractor",
        input_type=DataType.TEXT,
        output_type=DataType.KNOWLEDGE_GRAPH,
        input_construct="character_sequence",
        output_construct="knowledge_graph",
        transformation_type="knowledge_graph_extraction"
    ))
    
    framework.register_tool(
        GraphPersister(framework.neo4j, framework.identity, framework.crossmodal),
        ToolCapabilities(
            tool_id="GraphPersister",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH,
            input_construct="knowledge_graph",
            output_construct="persisted_graph",
            transformation_type="graph_persistence"
        )
    )
    
    # Load ground truth
    ground_truth_dir = Path("thesis_evidence/ground_truth")
    documents = []
    for json_file in ground_truth_dir.glob("*.json"):
        with open(json_file) as f:
            documents.append(json.load(f))
    
    # Run experiments
    collector = MetricsCollector()
    all_metrics = []
    
    for i, doc in enumerate(documents, 1):
        print(f"\n[{i}/{len(documents)}] Processing {doc['id']}...")
        
        # Clean Neo4j before each run
        with framework.neo4j.session() as session:
            session.run("MATCH (n:VSEntity) DETACH DELETE n")
        
        metrics = run_experiment(doc, framework, collector)
        all_metrics.append(metrics)
        collector.save_metrics(metrics)
        
        print(f"  Uncertainty: {metrics.combined_uncertainty:.3f} (expected: {metrics.expected_uncertainty:.3f})")
        print(f"  Entity F1: {metrics.entity_f1:.3f}")
        print(f"  Time: {metrics.execution_time:.2f}s, Memory: {metrics.memory_delta_mb:.1f}MB")
    
    # Generate summary
    summary = collector.generate_summary_statistics()
    
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    for complexity_stats in summary['by_complexity']:
        print(f"\n{complexity_stats[0]} complexity:")
        print(f"  Avg uncertainty: {complexity_stats[1]:.3f}")
        print(f"  Avg error: {complexity_stats[2]:.3f}")
        print(f"  Avg entity F1: {complexity_stats[3]:.3f}")
        print(f"  Avg time: {complexity_stats[4]:.2f}s")
    
    # Save results
    with open("thesis_evidence/results.json", 'w') as f:
        json.dump({
            'metrics': [asdict(m) for m in all_metrics],
            'summary': summary
        }, f, indent=2)
    
    print(f"\n✅ Completed {len(documents)} experiments")
    print("✅ Results saved to thesis_evidence/results.json")
    
    framework.cleanup()

if __name__ == "__main__":
    main()
```

**Evidence Required**: `evidence/current/Evidence_ThesisMetrics_Experiments.md`
- Full execution log for all 10 documents
- Summary statistics
- Verify results.json created

---

## 6. Phase 3: Analysis and Visualization

### Task 3.1: Statistical Analysis

**File**: Create `/tool_compatability/poc/thesis_evidence/analyze_results.py`

```python
#!/usr/bin/env python3
"""Analyze experimental results for thesis"""

import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class ThesisAnalyzer:
    """Analyze and visualize thesis evidence"""
    
    def __init__(self, results_path: str = "thesis_evidence/results.json"):
        with open(results_path) as f:
            self.data = json.load(f)
        self.df = pd.DataFrame(self.data['metrics'])
    
    def uncertainty_analysis(self):
        """Analyze uncertainty propagation"""
        # 1. Correlation between expected and actual uncertainty
        correlation = stats.pearsonr(
            self.df['expected_uncertainty'],
            self.df['combined_uncertainty']
        )
        
        # 2. Uncertainty by document complexity
        complexity_groups = self.df.groupby('document_complexity')
        uncertainty_by_complexity = complexity_groups['combined_uncertainty'].agg(['mean', 'std'])
        
        # 3. Uncertainty propagation through pipeline
        avg_step_uncertainties = np.mean(self.df['step_uncertainties'].tolist(), axis=0)
        
        return {
            'correlation': correlation,
            'by_complexity': uncertainty_by_complexity,
            'step_propagation': avg_step_uncertainties
        }
    
    def accuracy_analysis(self):
        """Analyze extraction accuracy"""
        # F1 scores by complexity
        f1_by_complexity = self.df.groupby('document_complexity')[
            ['entity_f1', 'relationship_f1']
        ].mean()
        
        # Relationship between uncertainty and accuracy
        uncertainty_vs_f1 = stats.pearsonr(
            self.df['combined_uncertainty'],
            self.df['entity_f1']
        )
        
        return {
            'f1_by_complexity': f1_by_complexity,
            'uncertainty_accuracy_correlation': uncertainty_vs_f1
        }
    
    def performance_analysis(self):
        """Analyze performance metrics"""
        # Scalability: time vs document length
        length_time_correlation = stats.pearsonr(
            self.df['document_length'],
            self.df['execution_time']
        )
        
        # Memory usage statistics
        memory_stats = self.df['memory_delta_mb'].describe()
        
        return {
            'scalability': length_time_correlation,
            'memory_stats': memory_stats
        }
    
    def create_visualizations(self):
        """Create thesis visualizations"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 1. Uncertainty propagation
        ax1 = axes[0, 0]
        steps = ['TextLoader', 'KG Extractor', 'Persister']
        avg_uncertainties = self.uncertainty_analysis()['step_propagation']
        ax1.bar(steps, avg_uncertainties)
        ax1.set_title('Uncertainty Propagation Through Pipeline')
        ax1.set_ylabel('Uncertainty')
        
        # 2. Expected vs Actual Uncertainty
        ax2 = axes[0, 1]
        ax2.scatter(self.df['expected_uncertainty'], self.df['combined_uncertainty'])
        ax2.plot([0, 0.5], [0, 0.5], 'r--', alpha=0.5)
        ax2.set_xlabel('Expected Uncertainty')
        ax2.set_ylabel('Actual Uncertainty')
        ax2.set_title('Uncertainty Calibration')
        
        # 3. F1 by Complexity
        ax3 = axes[0, 2]
        f1_data = self.accuracy_analysis()['f1_by_complexity']
        f1_data.plot(kind='bar', ax=ax3)
        ax3.set_title('Accuracy by Document Complexity')
        ax3.set_ylabel('F1 Score')
        
        # 4. Uncertainty vs Accuracy
        ax4 = axes[1, 0]
        ax4.scatter(self.df['combined_uncertainty'], self.df['entity_f1'])
        ax4.set_xlabel('Uncertainty')
        ax4.set_ylabel('Entity F1 Score')
        ax4.set_title('Uncertainty vs Accuracy')
        
        # 5. Execution Time Distribution
        ax5 = axes[1, 1]
        ax5.hist(self.df['execution_time'], bins=20)
        ax5.set_xlabel('Execution Time (seconds)')
        ax5.set_ylabel('Frequency')
        ax5.set_title('Processing Time Distribution')
        
        # 6. Memory Usage by Complexity
        ax6 = axes[1, 2]
        self.df.boxplot(column='memory_delta_mb', by='document_complexity', ax=ax6)
        ax6.set_xlabel('Document Complexity')
        ax6.set_ylabel('Memory Usage (MB)')
        ax6.set_title('Memory Usage by Complexity')
        
        plt.tight_layout()
        plt.savefig('thesis_evidence/thesis_visualizations.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("✅ Saved visualizations to thesis_evidence/thesis_visualizations.png")
    
    def generate_thesis_tables(self):
        """Generate LaTeX tables for thesis"""
        # Table 1: Summary statistics
        summary_table = self.df.groupby('document_complexity').agg({
            'combined_uncertainty': ['mean', 'std'],
            'entity_f1': ['mean', 'std'],
            'execution_time': ['mean', 'std']
        }).round(3)
        
        latex_table = summary_table.to_latex()
        with open('thesis_evidence/summary_table.tex', 'w') as f:
            f.write(latex_table)
        
        print("✅ Generated LaTeX table: thesis_evidence/summary_table.tex")
        
        return summary_table

if __name__ == "__main__":
    analyzer = ThesisAnalyzer()
    
    print("=== Uncertainty Analysis ===")
    uncertainty = analyzer.uncertainty_analysis()
    print(f"Correlation with expected: {uncertainty['correlation'][0]:.3f} (p={uncertainty['correlation'][1]:.3f})")
    
    print("\n=== Accuracy Analysis ===")
    accuracy = analyzer.accuracy_analysis()
    print(accuracy['f1_by_complexity'])
    
    print("\n=== Performance Analysis ===")
    performance = analyzer.performance_analysis()
    print(f"Scalability correlation: {performance['scalability'][0]:.3f}")
    
    # Create visualizations
    analyzer.create_visualizations()
    
    # Generate thesis tables
    analyzer.generate_thesis_tables()
```

**Evidence Required**: `evidence/current/Evidence_ThesisMetrics_Analysis.md`
- Statistical analysis results
- Correlation coefficients
- Generated visualizations
- LaTeX tables

---

## 7. Testing Commands

```bash
# Phase 1: Create ground truth
python3 tool_compatability/poc/thesis_evidence/ground_truth_generator.py

# Phase 2: Run experiments
python3 tool_compatability/poc/thesis_evidence/run_experiments.py

# Phase 3: Analyze results
python3 tool_compatability/poc/thesis_evidence/analyze_results.py

# Verify evidence
ls -la thesis_evidence/
cat thesis_evidence/results.json | jq '.summary'
```

---

## 8. Success Metrics

### Quantitative Targets
- **Uncertainty Calibration**: Correlation > 0.7 between expected and actual
- **Entity Extraction F1**: Average > 0.75 across all complexities
- **Performance**: < 5 seconds for documents under 5000 characters
- **Memory**: < 100MB delta for standard documents
- **Scalability**: Linear time complexity (correlation > 0.8)

### Required Deliverables
1. **10+ annotated test documents** with ground truth
2. **Complete metrics database** with all experiments
3. **Statistical analysis** showing system effectiveness
4. **Visualizations** for thesis presentation
5. **LaTeX tables** ready for thesis inclusion

---

## 9. Important Notes

1. **Real Data Only**: Use actual Gemini API calls, no mocking
2. **Clean State**: Clear Neo4j before each experiment
3. **Reproducibility**: Save all intermediate results
4. **Error Handling**: Use fail-fast, log all errors
5. **Evidence**: Document everything with raw logs

---

*Last Updated: 2025-08-27*
*Phase: Thesis Evidence Collection*
*Priority: Generate quantitative evidence for academic thesis*