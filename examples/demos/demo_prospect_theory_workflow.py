#!/usr/bin/env python3
"""
Demonstrate the complete workflow for applying Prospect Theory to text
using LLM-generated code.

Workflow:
1. Load theory schema (Prospect Theory)
2. Generate executable code from formula descriptions
3. Extract parameters from example text
4. Execute analysis
5. Interpret results
"""

import json
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
import numpy as np

# Example text for analysis
EXAMPLE_TEXT = """
The government is considering a new climate policy. There's a 70% chance 
it will reduce emissions significantly, leading to major environmental gains. 
However, there's a 30% chance it could fail, resulting in moderate economic 
losses compared to the current situation. The opposition proposes maintaining 
the status quo, which is certain but provides no improvement.
"""

class ProspectTheoryFormulas:
    """LLM would generate this from the schema formulas"""
    
    @staticmethod
    def value_function(x: float, reference_point: float = 0) -> float:
        """
        Calculate subjective value using Prospect Theory value function
        v(x) = x^α if x ≥ 0 (gains), v(x) = -λ(-x)^β if x < 0 (losses)
        """
        α = 0.88  # Concavity parameter for gains
        β = 0.88  # Convexity parameter for losses
        λ = 2.25  # Loss aversion coefficient
        
        relative_outcome = x - reference_point
        
        if relative_outcome >= 0:  # Gain
            return relative_outcome ** α
        else:  # Loss
            return -λ * ((-relative_outcome) ** β)
    
    @staticmethod
    def probability_weighting(p: float, domain: str = 'gain') -> float:
        """
        Weight probabilities according to Tversky-Kahneman function
        w(p) = p^γ / (p^γ + (1-p)^γ)^(1/γ)
        """
        γ = 0.61 if domain == 'gain' else 0.69
        
        if p == 0:
            return 0
        elif p == 1:
            return 1
        else:
            return (p ** γ) / ((p ** γ + (1 - p) ** γ) ** (1 / γ))
    
    @staticmethod
    def prospect_value(outcomes: List[float], probabilities: List[float], 
                      reference_point: float = 0) -> float:
        """
        Calculate overall prospect value
        V = Σ w(p_i) * v(x_i)
        """
        total_value = 0
        
        for outcome, prob in zip(outcomes, probabilities):
            # Determine if gain or loss for probability weighting
            domain = 'gain' if outcome >= reference_point else 'loss'
            
            # Weight the probability
            weighted_prob = ProspectTheoryFormulas.probability_weighting(prob, domain)
            
            # Calculate subjective value
            subj_value = ProspectTheoryFormulas.value_function(outcome, reference_point)
            
            # Add to total
            total_value += weighted_prob * subj_value
        
        return total_value


class ExtractedParameters(BaseModel):
    """LLM would generate this based on theory requirements"""
    
    prospect_name: str
    outcomes: List[float] = Field(description="Outcome values on normalized scale")
    probabilities: List[float] = Field(description="Probabilities for each outcome")
    reference_point: float = Field(default=0, description="Reference point (status quo)")
    description: str = Field(description="Text description of the prospect")


def simulate_llm_extraction(text: str) -> List[ExtractedParameters]:
    """
    Simulate what an LLM would extract from the text.
    In reality, this would be a call to GPT-4 or similar.
    """
    # For demo purposes, manually extract the parameters
    # In real implementation, this would be:
    # prompt = f"Extract prospect theory parameters from: {text}"
    # response = llm.generate(prompt)
    
    prospects = [
        ExtractedParameters(
            prospect_name="Climate Policy",
            outcomes=[60, -20],  # Major gain (60), Moderate loss (-20)
            probabilities=[0.7, 0.3],
            reference_point=0,  # Current situation
            description="New climate policy with uncertain outcomes"
        ),
        ExtractedParameters(
            prospect_name="Status Quo",
            outcomes=[0],  # No change
            probabilities=[1.0],  # Certain
            reference_point=0,
            description="Maintain current policy"
        )
    ]
    
    return prospects


def analyze_prospects(prospects: List[ExtractedParameters]) -> Dict[str, Any]:
    """Apply Prospect Theory analysis to extracted prospects"""
    
    results = {}
    
    for prospect in prospects:
        # Calculate prospect value
        value = ProspectTheoryFormulas.prospect_value(
            outcomes=prospect.outcomes,
            probabilities=prospect.probabilities,
            reference_point=prospect.reference_point
        )
        
        # Calculate component values for insight
        components = []
        for outcome, prob in zip(prospect.outcomes, prospect.probabilities):
            domain = 'gain' if outcome >= prospect.reference_point else 'loss'
            weighted_prob = ProspectTheoryFormulas.probability_weighting(prob, domain)
            subj_value = ProspectTheoryFormulas.value_function(outcome, prospect.reference_point)
            components.append({
                'outcome': outcome,
                'probability': prob,
                'weighted_probability': weighted_prob,
                'subjective_value': subj_value,
                'contribution': weighted_prob * subj_value
            })
        
        results[prospect.prospect_name] = {
            'total_value': value,
            'components': components,
            'description': prospect.description
        }
    
    return results


def generate_insights(results: Dict[str, Any]) -> str:
    """Generate human-readable insights from the analysis"""
    
    # Find preferred choice
    max_value = -float('inf')
    preferred_choice = None
    
    for name, data in results.items():
        if data['total_value'] > max_value:
            max_value = data['total_value']
            preferred_choice = name
    
    insights = []
    insights.append(f"Preferred Choice: {preferred_choice} (Value: {max_value:.2f})")
    insights.append("\nDetailed Analysis:")
    
    for name, data in results.items():
        insights.append(f"\n{name}:")
        insights.append(f"  Total Prospect Value: {data['total_value']:.2f}")
        
        for comp in data['components']:
            gain_loss = "gain" if comp['outcome'] >= 0 else "loss"
            insights.append(f"  - Outcome {comp['outcome']} ({gain_loss}):")
            insights.append(f"    Original probability: {comp['probability']:.2f}")
            insights.append(f"    Weighted probability: {comp['weighted_probability']:.2f}")
            insights.append(f"    Subjective value: {comp['subjective_value']:.2f}")
    
    # Add behavioral insights
    insights.append("\nBehavioral Insights:")
    
    # Check for loss aversion
    for name, data in results.items():
        has_losses = any(comp['outcome'] < 0 for comp in data['components'])
        if has_losses:
            insights.append(f"- {name} involves potential losses, triggering loss aversion")
    
    # Check for certainty effect
    for name, data in results.items():
        has_certainty = any(comp['probability'] == 1.0 for comp in data['components'])
        if has_certainty:
            insights.append(f"- {name} offers certainty, which is typically overvalued")
    
    return "\n".join(insights)


def main():
    """Run the complete workflow"""
    
    print("=" * 60)
    print("PROSPECT THEORY APPLICATION WORKFLOW")
    print("=" * 60)
    
    # Step 1: Show the example text
    print("\n1. ANALYZING TEXT:")
    print(EXAMPLE_TEXT)
    
    # Step 2: Extract parameters (simulating LLM extraction)
    print("\n2. EXTRACTING PARAMETERS (via LLM):")
    prospects = simulate_llm_extraction(EXAMPLE_TEXT)
    for p in prospects:
        print(f"\n{p.prospect_name}:")
        print(f"  Outcomes: {p.outcomes}")
        print(f"  Probabilities: {p.probabilities}")
        print(f"  Reference Point: {p.reference_point}")
    
    # Step 3: Apply Prospect Theory analysis
    print("\n3. APPLYING PROSPECT THEORY:")
    results = analyze_prospects(prospects)
    
    # Step 4: Generate insights
    print("\n4. INSIGHTS:")
    insights = generate_insights(results)
    print(insights)
    
    # Step 5: Show what this means
    print("\n5. INTERPRETATION:")
    print("According to Prospect Theory, decision-makers will likely choose the")
    print("Climate Policy despite the risk, because:")
    print("- The probability weighting function overweights the 70% chance")
    print("- The potential gain is evaluated more favorably than the loss is painful")
    print("- The certainty of the status quo is less attractive than the risky option")
    
    return results


if __name__ == "__main__":
    results = main()