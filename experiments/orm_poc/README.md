# ORM Proof of Concept

This directory contains the Phase 0 proof of concept for Object Role Modeling (ORM) based tool compatibility.

## Objective
Validate that semantic role matching provides better tool compatibility detection than field name matching.

## Structure
- `semantic_types.py` - Semantic type definitions and compatibility rules
- `orm_wrapper.py` - Core ORM wrapper implementation
- `role_definitions.py` - Role definitions for tools
- `compatibility_checker.py` - Compatibility checking logic
- `wrapped_tools/` - ORM-wrapped versions of T03, T15A, T23C
- `tests/` - Test suite
- `test_data/` - Test documents
- `results/` - Test results and analysis

## Quick Start
```bash
# Run all tests
python run_poc.py

# Check results
cat results/comparison_report.md
```

## Success Criteria
- Semantic matching correctly identifies valid/invalid connections
- Performance overhead <100ms
- Clear advantages over field matching