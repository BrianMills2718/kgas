#!/usr/bin/env python3
"""
Complete Theory Application Pipeline

This demonstrates the full workflow:
1. Theory Schema → LLM → Executable Code
2. Text → LLM → Structured Parameters
3. Execute Analysis → Generate Insights
4. Output Results in Multiple Formats
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
from pathlib import Path

@dataclass
class TheoryAnalysisResult:
    """Complete result of applying a theory to text"""
    theory_name: str
    timestamp: datetime
    input_text: str
    extracted_parameters: Dict[str, Any]
    computational_results: Dict[str, Any]
    insights: str
    confidence_score: float
    metadata: Dict[str, Any]

class TheoryOutputHandler:
    """Handles different output formats for theory analysis results"""
    
    def __init__(self, output_dir: str = "./theory_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_as_json(self, result: TheoryAnalysisResult, filename: Optional[str] = None) -> str:
        """Save results as JSON for further processing"""
        if not filename:
            filename = f"{result.theory_name.lower().replace(' ', '_')}_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        # Convert to dict with proper serialization
        result_dict = asdict(result)
        result_dict['timestamp'] = result.timestamp.isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(result_dict, f, indent=2)
        
        return str(filepath)
    
    def save_as_report(self, result: TheoryAnalysisResult, filename: Optional[str] = None) -> str:
        """Generate a human-readable report"""
        if not filename:
            filename = f"{result.theory_name.lower().replace(' ', '_')}_report_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = self.output_dir / filename
        
        report = f"""# {result.theory_name} Analysis Report

Generated: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Input Text
{result.input_text}

## Extracted Parameters
"""
        # Format extracted parameters
        for key, value in result.extracted_parameters.items():
            report += f"\n### {key}\n"
            if isinstance(value, list):
                for item in value:
                    report += f"- {item}\n"
            else:
                report += f"{value}\n"
        
        report += f"""
## Computational Results
"""
        # Format computational results
        for analysis, results in result.computational_results.items():
            report += f"\n### {analysis.replace('_', ' ').title()}\n"
            report += f"```json\n{json.dumps(results, indent=2)}\n```\n"
        
        report += f"""
## Insights
{result.insights}

## Confidence Score
{result.confidence_score:.2%}

## Metadata
- Theory Version: {result.metadata.get('theory_version', 'N/A')}
- Schema Version: {result.metadata.get('schema_version', 'N/A')}
- Processing Time: {result.metadata.get('processing_time_ms', 'N/A')}ms
"""
        
        with open(filepath, 'w') as f:
            f.write(report)
        
        return str(filepath)
    
    def save_for_visualization(self, result: TheoryAnalysisResult) -> str:
        """Save data in format suitable for visualization tools"""
        filename = f"{result.theory_name.lower().replace(' ', '_')}_viz_{result.timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = self.output_dir / filename
        
        # Extract data for visualization
        viz_data = []
        
        # Example: For Prospect Theory, create rows for each prospect
        if 'prospects' in result.extracted_parameters:
            for prospect in result.extracted_parameters['prospects']:
                for i, (outcome, prob) in enumerate(zip(prospect.get('outcomes', []), 
                                                       prospect.get('probabilities', []))):
                    viz_data.append({
                        'prospect_name': prospect['name'],
                        'outcome': outcome,
                        'probability': prob,
                        'outcome_index': i,
                        'reference_point': prospect.get('reference_point', 0),
                        'timestamp': result.timestamp
                    })
        
        # Save as CSV
        if viz_data:
            df = pd.DataFrame(viz_data)
            df.to_csv(filepath, index=False)
            return str(filepath)
        
        return ""
    
    def generate_decision_recommendation(self, result: TheoryAnalysisResult) -> Dict[str, Any]:
        """Generate actionable decision recommendations based on analysis"""
        
        recommendations = {
            'primary_recommendation': '',
            'supporting_evidence': [],
            'risk_factors': [],
            'confidence': result.confidence_score,
            'alternative_considerations': []
        }
        
        # Extract key decision from computational results
        if 'prospect_evaluation' in result.computational_results:
            prospects = result.computational_results['prospect_evaluation']
            
            # Find best option
            best_option = max(prospects.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0)
            recommendations['primary_recommendation'] = f"Choose {best_option[0]} (Value: {best_option[1]:.2f})"
            
            # Add supporting evidence
            recommendations['supporting_evidence'].append(
                f"Quantitative analysis shows {best_option[0]} has highest expected value"
            )
            
            # Add risk factors
            if 'risk_assessment' in result.metadata:
                recommendations['risk_factors'].extend(result.metadata['risk_assessment'])
        
        return recommendations


class IntegratedTheoryApplication:
    """Complete pipeline for applying theories to text"""
    
    def __init__(self, theory_schema_path: str):
        self.theory_schema = self.load_theory_schema(theory_schema_path)
        self.output_handler = TheoryOutputHandler()
    
    def load_theory_schema(self, path: str) -> Dict[str, Any]:
        """Load theory schema from file"""
        with open(path, 'r') as f:
            return json.load(f)
    
    def process_text(self, text: str) -> TheoryAnalysisResult:
        """Complete pipeline to process text with theory"""
        
        start_time = datetime.now()
        
        # Step 1: Generate code from theory (simulated)
        print("1. Generating code from theory schema...")
        code = self.generate_theory_code()
        
        # Step 2: Extract parameters from text (simulated)
        print("2. Extracting parameters from text...")
        parameters = self.extract_parameters_from_text(text)
        
        # Step 3: Execute analysis (simulated)
        print("3. Running computational analysis...")
        results = self.execute_analysis(parameters)
        
        # Step 4: Generate insights (simulated)
        print("4. Generating insights...")
        insights = self.generate_insights(results, parameters)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create result object
        result = TheoryAnalysisResult(
            theory_name=self.theory_schema['theory_name'],
            timestamp=datetime.now(),
            input_text=text,
            extracted_parameters=parameters,
            computational_results=results,
            insights=insights,
            confidence_score=0.85,  # Simulated confidence
            metadata={
                'theory_version': self.theory_schema.get('theory_version', '1.0'),
                'schema_version': self.theory_schema.get('meta_schema_version', '11.1'),
                'processing_time_ms': round(processing_time),
                'risk_assessment': ['Probability estimates may be subjective', 
                                   'Outcomes scaled from qualitative descriptions']
            }
        )
        
        return result
    
    def generate_theory_code(self) -> str:
        """Simulate LLM code generation"""
        # In production, this would call LLM
        return "# Generated code for theory"
    
    def extract_parameters_from_text(self, text: str) -> Dict[str, Any]:
        """Simulate parameter extraction"""
        # In production, this would use LLM
        return {
            'prospects': [
                {
                    'name': 'Climate Policy',
                    'outcomes': [60, -20],
                    'probabilities': [0.7, 0.3],
                    'reference_point': 0
                },
                {
                    'name': 'Status Quo',
                    'outcomes': [0],
                    'probabilities': [1.0],
                    'reference_point': 0
                }
            ]
        }
    
    def execute_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate analysis execution"""
        # In production, this would run generated code
        return {
            'prospect_evaluation': {
                'Climate Policy': 9.31,
                'Status Quo': 0.0
            },
            'value_components': {
                'Climate Policy': {
                    'gain_component': 19.45,
                    'loss_component': -10.14
                }
            },
            'probability_weights': {
                'Climate Policy': {
                    'gain_weight': 0.53,
                    'loss_weight': 0.33
                }
            }
        }
    
    def generate_insights(self, results: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Generate insights from results"""
        # In production, this could use LLM or rule-based system
        return """
Based on Prospect Theory analysis:

1. **Recommended Choice**: Climate Policy (Prospect Value: 9.31)
   - The risky option is preferred over the certain status quo
   - This aligns with prospect theory predictions about risk-seeking in mixed domains

2. **Key Behavioral Factors**:
   - Probability weighting: The 70% chance is underweighted to 53%
   - Loss aversion: The potential loss is amplified by factor of 2.25
   - Despite these biases, the large potential gain dominates

3. **Decision Psychology**:
   - Decision makers will likely choose the risky climate policy
   - The certainty of status quo (typically overvalued) is overcome by gain magnitude
   - Framing as "environmental gains" vs "economic losses" affects perception

4. **Practical Implications**:
   - Present the policy emphasizing the 70% success probability
   - Acknowledge but don't overemphasize the potential losses
   - Use concrete examples of the gains to make them more salient
"""


def demonstrate_complete_pipeline():
    """Demonstrate the complete theory application pipeline"""
    
    print("=" * 60)
    print("COMPLETE THEORY APPLICATION PIPELINE")
    print("=" * 60)
    
    # Initialize pipeline
    schema_path = "/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json"
    pipeline = IntegratedTheoryApplication(schema_path)
    
    # Example text
    text = """
    The city council is debating a new transportation initiative. 
    Analysis shows there's a 65% probability it will significantly reduce 
    traffic congestion and improve air quality, representing a major gain 
    for residents. However, there's a 35% chance it could fail and result 
    in moderate financial losses due to wasted infrastructure investment. 
    The alternative is to maintain current transportation policies, which 
    guarantees no change but avoids any risk.
    """
    
    print(f"\nAnalyzing text:")
    print(text.strip())
    print("\n" + "-" * 40 + "\n")
    
    # Process text
    result = pipeline.process_text(text)
    
    # Save outputs
    print("\n5. Saving outputs...")
    
    # Save as JSON
    json_path = pipeline.output_handler.save_as_json(result)
    print(f"   ✓ JSON saved: {json_path}")
    
    # Save as report
    report_path = pipeline.output_handler.save_as_report(result)
    print(f"   ✓ Report saved: {report_path}")
    
    # Save for visualization
    viz_path = pipeline.output_handler.save_for_visualization(result)
    if viz_path:
        print(f"   ✓ Visualization data saved: {viz_path}")
    
    # Generate recommendations
    recommendations = pipeline.output_handler.generate_decision_recommendation(result)
    print(f"\n6. Decision Recommendation:")
    print(f"   {recommendations['primary_recommendation']}")
    print(f"   Confidence: {recommendations['confidence']:.0%}")
    
    print("\n7. What to do with outputs:")
    print("   - JSON: Feed to downstream analysis or ML models")
    print("   - Report: Share with stakeholders for decision-making")
    print("   - Visualization: Create charts showing prospect comparisons")
    print("   - Recommendations: Integrate into decision support systems")
    
    print("\n✅ Pipeline complete!")
    
    return result


if __name__ == "__main__":
    result = demonstrate_complete_pipeline()