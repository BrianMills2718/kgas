# Uncertainty Stress Test System - Unified Version

## Overview
This is the unified "best of both worlds" version combining the valuable components from:
- `/experiments/uncertainty_stress_test_system/` (original experiments version)
- `/uncertainty_stress_test/` (reorganized version)

Created: 2025-08-24

## Directory Structure

```
uncertainty_stress_test_unified/
├── core_services/           # Core uncertainty and Bayesian services
├── personality_prediction/  # ML models for personality prediction
├── bayesian/               # Bayesian inference modules
├── analysis/               # Davis methodology and analysis insights
├── optimization/           # Performance optimization tests
├── datasets/              # Consolidated test datasets
├── validation/            # Validation and test scripts
├── testing/               # Core test suite
├── setup/                 # Setup and demo scripts
├── docs/                  # Documentation and guides
└── config/                # Configuration files
```

## Key Components

### Core Services (`/core_services/`)
- **uncertainty_engine.py** - Main uncertainty quantification engine
- **cerqual_assessor.py** - CERQUAL assessment framework
- **bayesian_aggregation_service.py** - Bayesian belief aggregation
- **formal_bayesian_llm_engine.py** - Formal Bayesian LLM integration
- **llm_native_uncertainty_engine.py** - Native LLM uncertainty
- **optimized_llm_native_engine.py** - Performance-optimized version

### Personality Prediction (`/personality_prediction/`)
From experiments version - contains the working ML implementations:
- **real_bert_predictor.py** - BERT-based personality prediction
- **real_beta_bayesian.py** - Bayesian personality modeling
- **traditional_ml_predictor.py** - Random Forest/XGBoost models
- **transformer_personality_predictor.py** - Transformer-based models
- Implementation guides and honest assessments

### Bayesian Modules (`/bayesian/`)
Merged from both versions:
- **llm_bayesian_inference.py** - Core Bayesian inference
- **production_llm_bayesian.py** - Production-ready implementation
- **real_llm_bayesian_inference.py** - Real-world LLM Bayesian

### Analysis (`/analysis/`)
Paul Davis methodology insights and comprehensive synthesis:
- Davis methodology documentation
- Agent extraction notes
- Priority files and rapid analysis tools

### Optimization (`/optimization/`)
From reorganized version - performance testing:
- Parallel processing tests
- Speed comparison benchmarks
- Optimization results

### Datasets (`/datasets/`)
Consolidated test datasets:
- 100_users_500tweets dataset with ground truths
- High volume 500 tweet dataset with ground truths

### Validation & Testing
- Comprehensive uncertainty tests
- Extraordinary claim validation
- Formal Bayesian testing
- SocialMaze integration tests

### Documentation (`/docs/`)
- Implementation reports
- Validation status reports
- External evaluation packages
- Step-by-step implementation guides

## Version Selection Rationale

### From `/experiments/uncertainty_stress_test_system/`:
- **personality_prediction/** - Contains the actual working implementations
- **config/default.yaml** - Original configuration
- Core datasets (JSON files)

### From `/uncertainty_stress_test/`:
- **optimization/** - New performance testing capabilities
- **Step-by-step guides** - Better documentation structure
- **Setup scripts** - Auto setup and one-click tools
- Better organized validation scripts

### Merged/Combined:
- **core_services/** - Identical in both, kept latest
- **bayesian/** - Combined unique modules from both
- **analysis/** - Identical valuable content from both
- **docs/** - Best documentation from both versions

## Archived Content

Previous versions have been archived to:
```
/archived_uncertainty_tests/
├── 2025_07_experiments/     # Original experiments version
├── 2025_07_reorganized/     # Reorganized version with _organization
└── legacy_scripts/          # Deprecated/outdated scripts
```

## Quick Start

### Basic Usage
```python
from core_services.uncertainty_engine import UncertaintyEngine
from personality_prediction.real_bert_predictor import BERTPersonalityPredictor

# Initialize uncertainty engine
engine = UncertaintyEngine()

# Load personality predictor
predictor = BERTPersonalityPredictor()
```

### Running Tests
```bash
# Run uncertainty tests
python testing/run_uncertainty_test.py

# Test SocialMaze integration
python testing/test_socialmaze_uncertainty.py

# Validation suite
python validation/comprehensive_uncertainty_test.py
```

### Setup
```bash
# One-click KGAS setup
python setup/one_click_kgas_setup.py

# Auto Neo4j setup
python setup/auto_neo4j_setup.py
```

## Key Improvements in Unified Version

1. **Consolidated Structure** - No duplicate files or scattered components
2. **Clear Organization** - Logical grouping of related functionality
3. **Best Implementations** - Selected working versions over experimental
4. **Complete Documentation** - Merged documentation from both sources
5. **Performance Tools** - Included optimization testing from reorganized version
6. **Clean Datasets** - Single location for all test data

## Known Limitations

- Some experimental scripts archived (available in archive if needed)
- Kunst-specific validations not included in main (too specialized)
- Some draft documentation excluded (superseded versions archived)

## Future Development

- Continue optimization work from `/optimization/`
- Expand personality prediction models
- Enhance Bayesian inference capabilities
- Improve validation coverage

## Contact & Support

For questions about this unified version or to access archived content, 
refer to the archive directories or the original documentation in `/docs/`.

---
*Unified from multiple sources on 2025-08-24*
*Archive location: /archived_uncertainty_tests/*