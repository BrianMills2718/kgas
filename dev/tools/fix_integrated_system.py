#!/usr/bin/env python3
"""
Fixed version of integrated system that produces working code
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from src.theory_to_code.structured_extractor import StructuredParameterExtractor, TextSchema, ResolvedParameters
from src.theory_to_code.simple_executor import SimpleExecutor, ExecutionResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Working theory implementations
WORKING_PROSPECT_THEORY_MODULE = '''
from typing import List
import numpy as np

def value_function(outcome_values: List[float], reference_point: float, alpha: float = 0.88, beta: float = 0.88, lambda_: float = 2.25) -> List[float]:
    """
    Calculate subjective values using Prospect Theory value function.
    
    For gains: v(x) = (x - reference_point)^alpha
    For losses: v(x) = -lambda * |x - reference_point|^beta
    """
    subjective_values = []
    for x in outcome_values:
        x_relative = x - reference_point
        if x_relative >= 0:
            subjective_value = x_relative ** alpha
        else:
            subjective_value = -lambda_ * (-x_relative) ** beta
        subjective_values.append(subjective_value)
    return subjective_values

def probability_weighting_function(objective_probabilities: List[float], gamma: float = 0.61) -> List[float]:
    """
    Calculate decision weights using probability weighting function.
    
    w(p) = p^gamma / (p^gamma + (1-p)^gamma)^(1/gamma)
    """
    decision_weights = []
    for p in objective_probabilities:
        if not (0 <= p <= 1):
            raise ValueError("Each probability should be in the range [0, 1].")
        
        if p == 0:
            weight = 0
        elif p == 1:
            weight = 1
        else:
            try:
                weight = p**gamma / (p**gamma + (1-p)**gamma)**(1/gamma)
            except ZeroDivisionError:
                weight = 0.5
        
        decision_weights.append(weight)
    
    return decision_weights

def prospect_evaluation(outcome_values: List[float], probabilities: List[float], reference_point: float) -> float:
    """
    Calculate overall prospect value using Prospect Theory.
    
    Combines subjective values and decision weights for complete evaluation.
    """
    # Check input validity
    if len(outcome_values) != len(probabilities):
        raise ValueError("Lists must be same length")
    
    # Calculate subjective values
    subjective_values = value_function(outcome_values, reference_point)
    
    # Calculate decision weights  
    decision_weights = probability_weighting_function(probabilities)
    
    # Calculate weighted prospect value
    prospect_value = sum(w * v for w, v in zip(decision_weights, subjective_values))
    
    return prospect_value
'''

@dataclass
class TheoryAnalysis:
    """Complete analysis result"""
    theory_name: str
    timestamp: datetime
    input_text: str
    extracted_parameters: List[Dict[str, Any]]
    computational_results: Dict[str, Any]
    insights: str
    confidence_score: float
    execution_metadata: Dict[str, Any]

class FixedIntegratedTheorySystem:
    """Fixed version of the integrated system"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize components
        self.parameter_extractor = StructuredParameterExtractor()
        self.executor = SimpleExecutor()
        
        # Working theory modules
        self.theory_modules = {
            'prospect_theory': WORKING_PROSPECT_THEORY_MODULE
        }
    
    def analyze_text(self, text: str, theory_name: str = 'prospect_theory') -> TheoryAnalysis:
        """Analyze text using a theory"""
        
        start_time = datetime.now()
        
        if theory_name not in self.theory_modules:
            raise ValueError(f"Theory '{theory_name}' not available")
        
        # Step 1: Extract text-schema from text
        logger.info("Extracting text-schema from text...")
        schema_path = f'config/schemas/{theory_name}_schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Extract structured text-schema
        text_schema = self.parameter_extractor.extract_text_schema(text, schema)
        
        # Step 2: Resolve parameters
        logger.info("Resolving parameters...")
        resolved_params = self.parameter_extractor.resolve_parameters(text_schema)
        
        # Step 3: Execute computational analysis
        logger.info("Executing computational analysis...")
        module_code = self.theory_modules[theory_name]
        
        computational_results = {}
        all_params_data = []
        
        for params in resolved_params:
            logger.info(f"Analyzing {params.prospect_name}...")
            
            # Store parameters for output
            params_dict = {
                'prospect_name': params.prospect_name,
                'outcomes': params.outcomes,
                'probabilities': params.probabilities,
                'reference_point': params.reference_point
            }
            all_params_data.append(params_dict)
            
            # Execute each function
            prospect_results = {}
            
            # Test value function
            value_result = self.executor.execute_module_function(
                module_code, 'value_function', {
                    'outcome_values': params.outcomes,
                    'reference_point': params.reference_point
                }
            )
            prospect_results['value_function'] = {
                'success': value_result.success,
                'value': value_result.result if value_result.success else None,
                'error': value_result.error,
                'execution_time': value_result.execution_time
            }
            
            # Test probability weighting function
            weight_result = self.executor.execute_module_function(
                module_code, 'probability_weighting_function', {
                    'objective_probabilities': params.probabilities
                }
            )
            prospect_results['probability_weighting_function'] = {
                'success': weight_result.success,
                'value': weight_result.result if weight_result.success else None,
                'error': weight_result.error,
                'execution_time': weight_result.execution_time
            }
            
            # Test prospect evaluation
            eval_result = self.executor.execute_module_function(
                module_code, 'prospect_evaluation', {
                    'outcome_values': params.outcomes,
                    'probabilities': params.probabilities,
                    'reference_point': params.reference_point
                }
            )
            prospect_results['prospect_evaluation'] = {
                'success': eval_result.success,
                'value': eval_result.result if eval_result.success else None,
                'error': eval_result.error,
                'execution_time': eval_result.execution_time
            }
            
            computational_results[params.prospect_name] = {
                'parameters': params_dict,
                'results': prospect_results
            }
        
        # Step 4: Generate insights
        insights = self._generate_insights(computational_results)
        
        # Step 5: Create analysis result
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        analysis = TheoryAnalysis(
            theory_name=theory_name,
            timestamp=end_time,
            input_text=text,
            extracted_parameters=all_params_data,
            computational_results=computational_results,
            insights=insights,
            confidence_score=text_schema.confidence,
            execution_metadata={
                'execution_time_seconds': execution_time,
                'num_prospects': len(resolved_params),
                'functions_executed': ['value_function', 'probability_weighting_function', 'prospect_evaluation'],
                'text_schema': text_schema.model_dump(),
                'extraction_notes': text_schema.extraction_notes
            }
        )
        
        return analysis
    
    def _generate_insights(self, results: Dict[str, Any]) -> str:
        """Generate insights from computational results"""
        
        # Find successful evaluations
        successful_evaluations = {}
        for name, data in results.items():
            eval_result = data['results']['prospect_evaluation']
            if eval_result['success']:
                successful_evaluations[name] = eval_result['value']
        
        insights = ["Key behavioral factors from Prospect Theory:"]
        insights.append("- Loss aversion makes losses feel worse than equivalent gains")
        insights.append("- Probability weighting distorts objective probabilities")
        insights.append("- Reference point determines gain/loss framing")
        
        if len(successful_evaluations) >= 2:
            # Rank by prospect value
            ranked = sorted(successful_evaluations.items(), key=lambda x: x[1], reverse=True)
            insights.append(f"\nRanking by prospect value:")
            for i, (name, value) in enumerate(ranked, 1):
                insights.append(f"{i}. {name}: {value:.2f}")
            
            insights.append(f"\nRecommendation: {ranked[0][0]} (highest prospect value)")
        
        return "\n".join(insights)

def test_fixed_system():
    """Test the fixed integrated system"""
    
    print("TESTING FIXED INTEGRATED SYSTEM")
    print("=" * 60)
    
    # Test text
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
    
    # Create system and analyze
    system = FixedIntegratedTheorySystem()
    analysis = system.analyze_text(test_text)
    
    # Display results
    print(f"\n✅ Analysis Complete!")
    print(f"Theory: {analysis.theory_name}")
    print(f"Confidence: {analysis.confidence_score:.0%}")
    print(f"Execution time: {analysis.execution_metadata['execution_time_seconds']:.2f}s")
    print(f"Prospects analyzed: {analysis.execution_metadata['num_prospects']}")
    
    print(f"\nExtracted Parameters:")
    for params in analysis.extracted_parameters:
        print(f"  {params['prospect_name']}: {params['outcomes']} @ {params['probabilities']}")
    
    print(f"\nComputational Results:")
    for name, data in analysis.computational_results.items():
        eval_result = data['results']['prospect_evaluation']
        if eval_result['success']:
            print(f"  {name}: Prospect Value = {eval_result['value']:.2f}")
        else:
            print(f"  {name}: FAILED - {eval_result['error']}")
    
    print(f"\nInsights:")
    print(analysis.insights)
    
    # Save results
    output_file = f"analysis_outputs/fixed_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_data = {
        'theory_name': analysis.theory_name,
        'timestamp': analysis.timestamp.isoformat(),
        'input_text': analysis.input_text,
        'extracted_parameters': analysis.extracted_parameters,
        'computational_results': analysis.computational_results,
        'insights': analysis.insights,
        'confidence_score': analysis.confidence_score,
        'execution_metadata': analysis.execution_metadata
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Check if all computations succeeded
    all_success = True
    for name, data in analysis.computational_results.items():
        for func_name, result in data['results'].items():
            if not result['success']:
                all_success = False
                print(f"❌ {name}.{func_name} failed: {result['error']}")
    
    if all_success:
        print(f"\n🎉 ALL COMPUTATIONS SUCCESSFUL!")
    
    return all_success

if __name__ == "__main__":
    test_fixed_system()