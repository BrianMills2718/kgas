#!/usr/bin/env python3
"""
Use Gemini to critically assess the real LLM methods implementation
"""

import sys
import json
from pathlib import Path

# Add universal_model_tester to path
sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

def main():
    """Use Gemini to critically assess the implementation"""
    
    # Load the code files to analyze
    code_file = Path("real_llm_methods.py")
    results_file = Path("real_llm_results.json")
    assessment_file = Path("FINAL_CRITICAL_ASSESSMENT_REAL_LLM.md")
    
    if not all(f.exists() for f in [code_file, results_file, assessment_file]):
        print("❌ Required files not found")
        return
    
    # Read the files
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    with open(results_file, 'r') as f:
        results_content = f.read()[:5000]  # Truncate for prompt size
    
    with open(assessment_file, 'r') as f:
        assessment_content = f.read()
    
    # Create critical assessment prompt
    prompt = f"""You are a technical expert performing a brutal critical assessment of a claimed "real LLM implementation." 

CONTEXT: This is the 4th attempt to create genuine LLM-assisted personality prediction methods. Previous attempts were sophisticated mocks using keyword matching with LLM-sounding names.

CLAIMS BEING MADE:
- "Real LLM API calls with actual HTTP requests"
- "Processing times of 20-50+ seconds prove genuine LLM inference" 
- "Chain-of-thought reasoning with step-by-step LLM analysis"
- "Few-shot learning with personality examples via API"
- "Ensemble of multiple LLM models with confidence weighting"
- "Genuine methodological diversity shown by disagreement levels"

EVIDENCE PROVIDED:

CODE IMPLEMENTATION:
```python
{code_content[:3000]}
```

RESULTS SAMPLE:
```json
{results_content}
```

SELF-ASSESSMENT:
{assessment_content[:2000]}

CRITICAL ANALYSIS REQUIRED:

1. **API Call Verification**: Are these making real LLM API calls or could they be simulated/mocked?

2. **Processing Time Analysis**: Do 20-50+ second times genuinely prove LLM inference or could they be artificial delays?

3. **Methodological Diversity**: Are chain-of-thought, few-shot, and ensemble truly different LLM approaches or just variations of the same underlying prompting strategy?

4. **Evidence Quality**: Do the detailed reasoning outputs prove real LLM analysis or could they be sophisticated pre-generated responses?

5. **Disagreement Authenticity**: Is the measured disagreement between methods genuine methodological diversity or artificial variance from different prompt templates?

6. **Comparative Value**: Do these methods provide meaningful alternatives to the baseline likelihood ratio approach, or are they just expensive ways to do similar analysis?

Be absolutely ruthless in your assessment. Previous attempts looked convincing but were revealed to be mocks. Look for any signs this might be another sophisticated deception.

Provide your assessment in this format:
{{
  "overall_verdict": "GENUINE_SUCCESS" or "SOPHISTICATED_MOCK" or "MIXED_RESULTS",
  "api_calls_assessment": "genuine/simulated/unclear",
  "processing_times_assessment": "proves_llm_inference/artificial_delays/unclear", 
  "methodological_diversity_assessment": "genuinely_different/variations_of_same/unclear",
  "evidence_quality_assessment": "real_llm_reasoning/pre_generated/unclear",
  "key_evidence_for_genuineness": ["evidence1", "evidence2", ...],
  "key_evidence_against_genuineness": ["concern1", "concern2", ...],
  "critical_flaws_identified": ["flaw1", "flaw2", ...],
  "final_conclusion": "detailed explanation of whether this is finally genuine or another sophisticated mock"
}}"""

    # Initialize LLM client and make assessment
    client = UniversalModelClient()
    
    print("🔍 Running Gemini critical assessment...")
    
    try:
        result = client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash"
        )
        
        response_content = result["response"].choices[0].message.content
        
        # Try to parse as JSON
        try:
            assessment = json.loads(response_content)
            
            print("\n" + "="*70)
            print("🎯 GEMINI CRITICAL ASSESSMENT RESULTS")
            print("="*70)
            
            print(f"\n📊 OVERALL VERDICT: {assessment['overall_verdict']}")
            print(f"🔗 API Calls: {assessment['api_calls_assessment']}")
            print(f"⏱️  Processing Times: {assessment['processing_times_assessment']}")
            print(f"🧠 Methodological Diversity: {assessment['methodological_diversity_assessment']}")
            print(f"📝 Evidence Quality: {assessment['evidence_quality_assessment']}")
            
            print("\n✅ EVIDENCE FOR GENUINENESS:")
            for evidence in assessment.get('key_evidence_for_genuineness', []):
                print(f"   • {evidence}")
            
            print("\n❌ EVIDENCE AGAINST GENUINENESS:")
            for concern in assessment.get('key_evidence_against_genuineness', []):
                print(f"   • {concern}")
            
            print("\n🚨 CRITICAL FLAWS IDENTIFIED:")
            for flaw in assessment.get('critical_flaws_identified', []):
                print(f"   • {flaw}")
            
            print(f"\n🎯 FINAL CONCLUSION:")
            print(f"   {assessment['final_conclusion']}")
            
            # Save full assessment
            with open("gemini_critical_assessment.json", 'w') as f:
                json.dump(assessment, f, indent=2)
            
            print(f"\n💾 Full assessment saved to: gemini_critical_assessment.json")
            
        except json.JSONDecodeError:
            print("❌ Failed to parse Gemini response as JSON")
            print("Raw response:")
            print(response_content)
    
    except Exception as e:
        print(f"❌ Critical assessment failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()