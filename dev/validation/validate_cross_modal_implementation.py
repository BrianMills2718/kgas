#!/usr/bin/env python3
"""
Direct Gemini validation of Cross-Modal Analysis Orchestration implementation
"""

import subprocess
import sys
import os

# Create a validation prompt
validation_prompt = """
CRITICAL ASSESSMENT: Cross-Modal Analysis Orchestration Implementation

Analyze the implementation against the original plan and assess these specific claims:

CLAIMS TO VALIDATE:
1. "Mode Selection Service fully implemented with LLM reasoning"
2. "Cross-Modal Converter fully implemented with bidirectional conversion"
3. "Cross-Modal Orchestrator fully implemented with workflow optimization"
4. "Cross-Modal Validator fully implemented with comprehensive validation"
5. "All core functionality from plan is fully implemented"

CRITICAL ASSESSMENT CRITERIA:
1. Are all 4 critical components from the plan ACTUALLY implemented?
2. Does the implementation match the architectural design in the plan?
3. What production readiness and integration gaps exist?
4. Are there any misleading claims about "full implementation"?
5. What core functionality from the plan is missing?

BE EXTREMELY SKEPTICAL AND LOOK FOR:
- Stub implementations or placeholders
- Missing critical features from the plan
- Integration issues that would prevent actual usage
- Architectural mismatches with the original design
- Incomplete converter implementations (the plan mentions bidirectional conversion)
- Missing workflow optimization algorithms
- Lack of actual LLM integration
- No real validation framework

SPECIFIC QUESTIONS TO ANSWER:
1. Is the LLM client in ModeSelectionService actually initialized and working?
2. Are all conversion directions implemented (Graph↔Table↔Vector)?
3. Is the workflow optimization actually functional or just placeholder code?
4. Can these services actually be used in production?
5. What percentage of the planned functionality is ACTUALLY implemented vs stubbed?

Provide a brutally honest assessment with specific examples from the code.
"""

# Files to analyze
files_to_analyze = [
    "src/analytics/mode_selection_service.py",
    "src/analytics/cross_modal_converter.py",
    "src/analytics/cross_modal_orchestrator.py",
    "src/analytics/cross_modal_validator.py",
    "src/analytics/__init__.py",
    "Cross-Modal Analysis Orchestration  plan.md"
]

# Create a simple validation using available tools
print("Creating comprehensive code bundle for Gemini validation...")

# First, let's concatenate the relevant files
bundle_content = f"# Cross-Modal Analysis Orchestration - Critical Assessment Bundle\n\n"
bundle_content += f"## Validation Prompt\n\n{validation_prompt}\n\n"
bundle_content += "---\n\n"

for file_path in files_to_analyze:
    if os.path.exists(file_path):
        print(f"Adding {file_path}...")
        bundle_content += f"## File: {file_path}\n\n"
        try:
            with open(file_path, 'r') as f:
                bundle_content += f"```python\n{f.read()}\n```\n\n"
        except:
            bundle_content += f"Error reading file: {file_path}\n\n"
    else:
        print(f"Warning: {file_path} not found")

# Save the bundle
bundle_path = "cross_modal_validation_bundle.md"
with open(bundle_path, 'w') as f:
    f.write(bundle_content)

print(f"\nValidation bundle created: {bundle_path}")
print(f"Bundle size: {len(bundle_content):,} characters")
print("\nThe bundle contains all code and the validation prompt for Gemini analysis.")
print("\nKey validation points:")
print("1. Check if LLM client is actually initialized in ModeSelectionService")
print("2. Verify all bidirectional conversions are implemented")
print("3. Assess if workflow optimization is real or placeholder")
print("4. Evaluate production readiness and integration status")
print("5. Calculate percentage of planned vs actual functionality")