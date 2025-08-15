#!/usr/bin/env python3
"""
Final demonstration of the complete theory-to-code system
"""

import os
import sys
import json
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.theory_to_code import IntegratedTheorySystem

print("=" * 70)
print("FINAL DEMONSTRATION: THEORY-TO-CODE SYSTEM")
print("=" * 70)

# Initialize system
print("\n1. Initializing system...")
system = IntegratedTheorySystem()
print("   ✓ System initialized")

# Load theory
print("\n2. Loading Prospect Theory schema...")
schema_path = "config/schemas/prospect_theory_schema.json"
success = system.load_and_compile_theory(schema_path)
print(f"   ✓ Theory loaded and compiled: {success}")

# Test case: Investment decision
test_text = """
The investment committee is evaluating two opportunities:

Investment Alpha: There's a 60% chance of achieving exceptional returns 
(substantial market gains) if the new technology succeeds. However, there's 
a 40% probability of significant financial losses if the technology fails 
to gain market acceptance.

Investment Beta: This established market approach is almost guaranteed 
(90% probability) to deliver moderate but steady returns. There's only a 
10% chance of minor losses due to unexpected market conditions.

The committee must decide based on the firm's current stable financial position.
"""

print("\n3. Input Text:")
print("-" * 70)
print(test_text.strip())
print("-" * 70)

# Analyze
print("\n4. Running analysis...")
start_time = datetime.now()

try:
    analysis = system.analyze_text(test_text, 'prospect_theory')
    
    # Display results
    print("\n5. ANALYSIS RESULTS:")
    print("=" * 70)
    
    # Text-schema extraction
    text_schema = analysis.execution_metadata['text_schema']
    print(f"\nExtraction Confidence: {text_schema['confidence']*100:.0f}%")
    
    print("\nExtracted Prospects:")
    for i, prospect in enumerate(text_schema['extracted_prospects']):
        print(f"\n  {i+1}. {prospect['name']}:")
        print(f"     Outcomes:")
        for outcome in prospect['text_outcomes']:
            print(f"       • {outcome['description']}")
            print(f"         Category: {outcome['linguistic_category']}")
            print(f"         Range: {outcome['mapped_range']}")
        print(f"     Probabilities:")
        for prob in prospect['text_probabilities']:
            print(f"       • {prob['description']}: {prob['value']}")
    
    # Resolved parameters
    print("\n\nResolved Parameters:")
    for params in analysis.extracted_parameters:
        print(f"\n  {params['prospect_name']}:")
        print(f"    Outcomes: {[f'{v:.1f}' for v in params['outcomes']]}")
        print(f"    Probabilities: {params['probabilities']}")
    
    # Computational results
    print("\n\nComputational Analysis:")
    print("-" * 40)
    
    for prospect, data in analysis.computational_results.items():
        print(f"\n  {prospect}:")
        
        # Get the prospect evaluation result
        prospect_eval = data['results'].get('prospect_evaluation', {})
        if prospect_eval.get('success'):
            value = prospect_eval['value']
            print(f"    Overall Value: {value:.2f}")
            
            # Explain components
            value_func = data['results'].get('value_function', {})
            if value_func.get('success'):
                values = value_func['value']
                print(f"    Subjective Values: {[f'{v:.2f}' for v in values]}")
            
            prob_weight = data['results'].get('probability_weighting_function', {})
            if prob_weight.get('success'):
                weights = prob_weight['value']
                print(f"    Decision Weights: {[f'{w:.2f}' for w in weights]}")
    
    # Final recommendation
    print("\n\nDECISION RECOMMENDATION:")
    print("-" * 40)
    print(analysis.insights)
    
    # Behavioral insights
    print("\n\nBEHAVIORAL INSIGHTS:")
    print("-" * 40)
    
    # Compare objective vs subjective probabilities
    for prospect, data in analysis.computational_results.items():
        params = next(p for p in analysis.extracted_parameters if p['prospect_name'] == prospect)
        weights_result = data['results'].get('probability_weighting_function', {})
        
        if weights_result.get('success'):
            print(f"\n{prospect}:")
            obj_probs = params['probabilities']
            subj_weights = weights_result['value']
            
            for i, (obj, subj) in enumerate(zip(obj_probs, subj_weights)):
                diff = (subj - obj) / obj * 100
                print(f"  • Probability {obj:.0%} → Weight {subj:.0%} ({diff:+.0f}% distortion)")
    
    # Execution time
    exec_time = analysis.execution_metadata['execution_time_seconds']
    print(f"\n\nExecution Time: {exec_time:.1f} seconds")
    
    # Save results
    output_path = system.save_analysis(analysis)
    print(f"\nResults saved to: {output_path}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DEMONSTRATION COMPLETE")
print("=" * 70)