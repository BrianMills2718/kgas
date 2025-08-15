# Scripts Directory

This directory contains all utility scripts organized by purpose.

## Directory Structure

### Validation Scripts (`/validation/`)
Scripts for running validations and tests:
- `run_*.py` - Validation execution scripts
- `direct_*.py` - Direct validation scripts
- Various validation utilities

### Analysis Scripts (`/analysis/`)
Scripts for system analysis and documentation processing:
- `check_*.py` - System checking utilities
- `debug_*.py` - Debugging utilities
- `architecture_review.py` - Architecture analysis
- `extract_all_adrs.py` - ADR extraction
- `concatenate_architecture_docs.py` - Documentation processing
- `create_static_visualization.py` - Visualization generation
- `view_visualizations.py` - Visualization viewing
- `run_kgas_analysis.sh` - Analysis execution

### Demo Scripts (`/demo/`)
Scripts for demonstrations and examples:
- Various demo and example scripts

### Testing Scripts (`/testing/`)
Scripts for testing system functionality:
- `test_*.py` - Test execution scripts
- `demonstrate_*.py` - Testing demonstrations

## Usage

Run scripts from the repository root:
```bash
# Validation
python scripts/validation/run_final_validation.py

# Analysis  
python scripts/analysis/architecture_review.py

# Demo
python scripts/demo/demo_both_databases.py
```

---

*This directory consolidates scripts that were previously scattered at repository root.*