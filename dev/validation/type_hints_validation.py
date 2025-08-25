#!/usr/bin/env python3
"""
Direct validation of type hints implementation in testing framework.
"""

import os
import sys
import subprocess
from pathlib import Path

def collect_testing_files():
    """Collect all Python files in the testing framework."""
    testing_dir = Path("src/testing")
    python_files = list(testing_dir.glob("*.py"))
    
    print(f"🔍 Found {len(python_files)} Python files in testing framework:")
    for file in python_files:
        print(f"  - {file}")
    
    return python_files

def create_repomix_bundle():
    """Create a repomix bundle of the testing framework."""
    print("\n📦 Creating repomix bundle of testing framework...")
    
    try:
        # Create repomix bundle
        result = subprocess.run([
            "repomix", 
            "src/testing/",
            "--output", "type_hints_bundle.xml",
            "--ignore", "__pycache__,*.pyc,*.log"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Repomix bundle created successfully")
        return "type_hints_bundle.xml"
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating repomix bundle: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ repomix command not found. Please install repomix.")
        return None

def run_gemini_analysis(bundle_file):
    """Run Gemini analysis on the type hints implementation."""
    print("\n🤖 Running Gemini analysis...")
    
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ Google GenerativeAI library not found. Install with: pip install google-generativeai")
        return None
    
    # Configure Gemini
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Read the bundle
    with open(bundle_file, 'r') as f:
        codebase = f.read()
    
    # Create validation prompt
    prompt = f"""
Critically assess the implementation of comprehensive type hints throughout this Python testing framework codebase.

{codebase}

## Assessment Criteria:

### 1. Type Hint Completeness
- Are all functions, methods, and class attributes properly type-hinted?
- Are there any missing type annotations that should be present?
- Rate completeness: 0-100%

### 2. Type Accuracy & Appropriateness  
- Are the type annotations accurate for their actual usage?
- Do the types match the runtime behavior of the code?
- Are complex types (Dict, List, Callable, Optional) used correctly?

### 3. Optional/Union Type Handling
- Are nullable parameters properly annotated with Optional[Type]?
- Are default None values correctly handled?
- Are Union types used appropriately where needed?

### 4. Interface Consistency
- Do type hints match the service interfaces being implemented?
- Are abstract base class types properly inherited and typed?
- Is typing consistent across related modules?

### 5. Python Typing Best Practices
- Are imports from typing module appropriate and minimal?
- Are type aliases used where beneficial?
- Are generic types properly parameterized?
- Do type hints follow PEP 484/526/544 conventions?

### 6. Type Safety Improvements
- Do the type hints actually catch potential runtime errors?
- Would these annotations help with IDE support and autocomplete?
- Are there any type hints that are too broad (overuse of Any)?

### 7. Maintainability Impact
- Do the type hints make the code more self-documenting?
- Are the annotations readable and clear?
- Do they add value without excessive verbosity?

## Claims to Validate:
1. ✅/❌ "All testing framework files have comprehensive type hints"
2. ✅/❌ "All Optional parameters properly annotated" 
3. ✅/❌ "Return types specified for all methods"
4. ✅/❌ "Complex data structures properly typed"
5. ✅/❌ "Type hints improve code maintainability"
6. ✅/❌ "Type annotations follow Python best practices"

## Critical Issues to Flag:
- Missing type hints in critical areas
- Incorrect Optional usage
- Overly broad 'Any' usage where specific types possible
- Type hints that contradict actual usage
- Inconsistent patterns across modules
- Type annotations that add no value

## Response Format:
For each file, provide:
- **Completeness Score**: X/100%
- **Critical Issues**: List specific problems with line references
- **Strengths**: What was done well
- **Recommendations**: Specific improvements needed

Then provide an **Overall Assessment** with:
- **PASS/FAIL** for each claim
- **Overall Grade**: A-F 
- **Summary**: 2-3 sentences on type hints quality
- **Priority Fixes**: Top 3 issues to address

Be thorough and critical - this is a code review, not a celebration.
"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"❌ Error running Gemini analysis: {e}")
        return None

def save_results(analysis_result):
    """Save the analysis results to a file."""
    if analysis_result:
        output_file = "TYPE_HINTS_GEMINI_ASSESSMENT.md"
        with open(output_file, 'w') as f:
            f.write("# Type Hints Implementation Assessment\n\n")
            f.write("**Generated by Gemini 2.0 Flash**\n\n")
            f.write("---\n\n")
            f.write(analysis_result)
        
        print(f"\n📄 Analysis saved to: {output_file}")
        return output_file
    
    return None

def main():
    """Main validation workflow."""
    print("🔬 TYPE HINTS IMPLEMENTATION VALIDATION")
    print("=" * 50)
    
    # Step 1: Collect files
    files = collect_testing_files()
    if not files:
        print("❌ No testing files found")
        return 1
    
    # Step 2: Create bundle
    bundle_file = create_repomix_bundle()
    if not bundle_file:
        print("❌ Failed to create code bundle")
        return 1
    
    # Step 3: Run analysis
    analysis = run_gemini_analysis(bundle_file)
    if not analysis:
        print("❌ Failed to run Gemini analysis")
        return 1
    
    # Step 4: Save results
    output_file = save_results(analysis)
    if output_file:
        print(f"\n✅ Validation complete! Results in: {output_file}")
        return 0
    else:
        print("❌ Failed to save results")
        return 1

if __name__ == "__main__":
    sys.exit(main())