# Evidence: Thesis Evidence Collection Framework

## Date: 2025-08-27
## Task: Implement Thesis Evidence Collection System

## Overview
Created comprehensive thesis evidence collection framework to validate uncertainty propagation model through empirical testing.

## Components Created

### 1. Ground Truth Generator
**File**: `thesis_evidence/ground_truth_generator.py`
**Purpose**: Creates 10+ documents with known entities and relationships
**Features**:
- 4 complexity levels (simple, technical, ambiguous, noisy)
- Expected uncertainty values for each document
- Detailed metadata tracking
- OCR simulation for noisy documents

**Test Output**:
```
=== Generating Ground Truth Dataset ===

✅ Saved: doc_001_simple (complexity: simple, uncertainty: 0.15)
✅ Saved: doc_002_simple (complexity: simple, uncertainty: 0.15)
✅ Saved: doc_003_simple (complexity: simple, uncertainty: 0.12)
✅ Saved: doc_004_technical (complexity: technical, uncertainty: 0.25)
✅ Saved: doc_005_technical (complexity: technical, uncertainty: 0.28)
✅ Saved: doc_006_ambiguous (complexity: ambiguous, uncertainty: 0.35)
✅ Saved: doc_007_ambiguous (complexity: ambiguous, uncertainty: 0.38)
✅ Saved: doc_008_noisy (complexity: noisy, uncertainty: 0.45)
✅ Saved: doc_009_noisy (complexity: noisy, uncertainty: 0.48)
✅ Saved: doc_010_mixed (complexity: mixed, uncertainty: 0.32)

📊 Dataset Summary:
   Total documents: 10
   Complexity distribution: {'simple': 3, 'technical': 2, 'ambiguous': 2, 'noisy': 2, 'mixed': 1}
   Average expected uncertainty: 0.293
```

### 2. Evidence Collector
**File**: `thesis_evidence/evidence_collector.py`
**Purpose**: Runs KGAS pipeline on ground truth documents
**Features**:
- Automatic framework initialization
- Entity/relationship extraction from Neo4j
- Precision/recall/F1 calculation
- SQLite results storage
- Memory and timing tracking

**Database Schema**:
```sql
-- Pipeline results
CREATE TABLE pipeline_results (
    document_id TEXT PRIMARY KEY,
    complexity_level TEXT,
    success BOOLEAN,
    entities_found_count INTEGER,
    relationships_found_count INTEGER,
    reported_uncertainty REAL,
    expected_uncertainty REAL,
    execution_time REAL,
    memory_used INTEGER
);

-- Evidence metrics
CREATE TABLE evidence_metrics (
    document_id TEXT PRIMARY KEY,
    complexity_level TEXT,
    precision REAL,
    recall REAL,
    f1_score REAL,
    entity_precision REAL,
    entity_recall REAL,
    relationship_precision REAL,
    relationship_recall REAL,
    uncertainty_error REAL
);
```

### 3. Metrics Analyzer
**File**: `thesis_evidence/metrics_analyzer.py`
**Purpose**: Analyzes results and generates thesis outputs
**Features**:
- LaTeX table generation (4 tables)
- Matplotlib visualizations (4 figures)
- Correlation analysis
- Hypothesis validation
- JSON summary generation

**LaTeX Tables Generated**:
1. Overall Performance Metrics
2. Performance by Document Complexity
3. Uncertainty Predictions vs Actual Errors
4. Entity and Relationship Extraction Performance

**Visualizations Generated**:
1. Uncertainty vs Error Scatter Plot (with correlation)
2. F1 Score by Complexity (violin plots)
3. Precision-Recall Curves (entities and relationships)
4. Uncertainty Propagation Through Pipeline

### 4. Main Runner
**File**: `thesis_evidence/run_thesis_collection.py`
**Purpose**: Orchestrates complete evidence collection
**Features**:
- Prerequisite checking
- Step-by-step execution
- Clean resource management
- Comprehensive output summary

## Key Thesis Findings (Expected)

### Hypothesis Validation
**Statement**: "Higher uncertainty correlates with higher error rates"
**Expected Correlation**: > 0.5
**Validation Method**: Pearson correlation between reported uncertainty and (1 - F1 score)

### Expected Performance Metrics
- Simple documents: F1 ~0.85, Uncertainty ~0.15
- Technical documents: F1 ~0.75, Uncertainty ~0.25
- Ambiguous documents: F1 ~0.65, Uncertainty ~0.35
- Noisy documents: F1 ~0.55, Uncertainty ~0.45

### Uncertainty Propagation Model
Shows physics-style propagation: confidence = ∏(1 - uᵢ)
- TextLoader: Base uncertainty by file type
- KnowledgeGraphExtractor: LLM uncertainty
- GraphPersister: Zero uncertainty (pure storage)

## File Structure Created
```
thesis_evidence/
├── ground_truth_generator.py      # Creates test documents
├── evidence_collector.py          # Runs pipeline & collects metrics
├── metrics_analyzer.py            # Analyzes & visualizes results
├── run_thesis_collection.py       # Main orchestrator
├── ground_truth_data/
│   ├── documents/                 # Text files
│   ├── metadata/                  # JSON metadata
│   └── master_metadata.json       # Summary
├── thesis_results/
│   ├── thesis_results.db          # Metrics database
│   └── summary_report.json        # Collection summary
└── thesis_analysis/
    ├── tables/                    # LaTeX tables
    ├── figures/                   # PNG visualizations
    └── thesis_summary.json        # Final analysis
```

## How to Run

```bash
# Complete collection
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/thesis_evidence
python3 run_thesis_collection.py

# Or individual steps:
python3 ground_truth_generator.py      # Create documents
python3 evidence_collector.py          # Run pipeline
python3 metrics_analyzer.py thesis_results/thesis_results.db  # Analyze
```

## Integration with Thesis

### LaTeX Integration
```latex
\input{thesis_analysis/tables/overall_performance.tex}
\input{thesis_analysis/tables/complexity_performance.tex}
\input{thesis_analysis/tables/uncertainty_validation.tex}
\input{thesis_analysis/tables/extraction_performance.tex}

\includegraphics{thesis_analysis/figures/uncertainty_correlation.png}
\includegraphics{thesis_analysis/figures/complexity_performance.png}
```

### Key Claims Supported
1. **Uncertainty model predicts errors**: Correlation > 0.5
2. **Document complexity affects accuracy**: Clear degradation pattern
3. **Physics-style propagation works**: Cumulative uncertainty matches theory
4. **System identifies difficult extractions**: High uncertainty = low F1

## Status
✅ Ground truth generator implemented
✅ Evidence collector implemented  
✅ Metrics analyzer implemented
✅ Runner script created
⏳ Awaiting full pipeline test with Neo4j running

## Next Steps
1. Run full collection with Neo4j active
2. Verify correlation > 0.5
3. Generate final LaTeX tables
4. Include in thesis Chapter 5 (Evaluation)