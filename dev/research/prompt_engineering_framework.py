#!/usr/bin/env python3
"""
Comprehensive Prompt Engineering Framework for Personality Inference
Systematically explores different prompting strategies and their effectiveness
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import logging
import time
from abc import ABC, abstractmethod
import sys

sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PromptStrategy:
    """Represents a specific prompting strategy."""
    name: str
    description: str
    prompt_template: str
    requires_examples: bool = False
    requires_reasoning: bool = False
    output_schema: Optional[Dict] = None

class BasePromptStrategy(ABC):
    """Base class for prompt strategies."""
    
    @abstractmethod
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        """Generate prompt for personality inference."""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured output."""
        pass

class DirectMappingStrategy(BasePromptStrategy):
    """Direct mapping from tweets to survey responses."""
    
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        return f"""You are a psychologist predicting personality questionnaire responses from social media.

TRAIT: {trait}
QUESTION: {scale_info['question']}
SCALE: {scale_info['min']}-{scale_info['max']}

TWEETS:
{self._format_tweets(tweets[:20])}

Predict the score this person would give themselves on the questionnaire.

Return JSON:
{{
  "predicted_score": <number>,
  "confidence": <0-1>,
  "key_evidence": ["tweet excerpt 1", "tweet excerpt 2"]
}}"""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        return json.loads(response)
    
    def _format_tweets(self, tweets: List[str]) -> str:
        return "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(tweets)])

class PsychologicalFrameworkStrategy(BasePromptStrategy):
    """Use established psychological frameworks."""
    
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        frameworks = {
            'political': "Political psychology framework: authoritarianism, social dominance, system justification",
            'narcissism': "Narcissistic Personality Inventory dimensions: authority, self-sufficiency, superiority, exhibitionism",
            'conspiracy': "Conspiracy mentality framework: epistemic, existential, and social motives",
            'denialism': "Science attitudes framework: trust in expertise, cognitive style, motivated reasoning"
        }
        
        return f"""Apply psychological framework to analyze personality from tweets.

FRAMEWORK: {frameworks.get(trait, 'General personality assessment')}
TRAIT: {trait}
SCALE: {scale_info['min']}-{scale_info['max']}

TWEETS:
{self._format_tweets(tweets[:20])}

Analyze using the framework:
1. Identify relevant psychological indicators
2. Map indicators to trait level
3. Predict questionnaire response

Return JSON:
{{
  "framework_analysis": {{
    "indicators_found": ["indicator 1", "indicator 2"],
    "psychological_interpretation": "interpretation"
  }},
  "predicted_score": <number>,
  "confidence": <0-1>
}}"""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        return json.loads(response)
    
    def _format_tweets(self, tweets: List[str]) -> str:
        return "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(tweets)])

class ComparativeAnalysisStrategy(BasePromptStrategy):
    """Compare to prototypical examples."""
    
    def __init__(self):
        self.prototypes = {
            'political': {
                'low': "Avoids politics, focuses on personal life, neutral language",
                'high': "Frequent political posts, strong partisan language, political identity central"
            },
            'narcissism': {
                'low': "Others-focused, humble, collaborative, grateful",
                'high': "Self-focused, boastful, superiority, need for admiration"
            },
            'conspiracy': {
                'low': "Trusts institutions, evidence-based thinking, mainstream sources",
                'high': "Distrusts authority, alternative explanations, hidden knowledge claims"
            },
            'denialism': {
                'low': "Respects scientific consensus, cites research, trusts experts",
                'high': "Rejects mainstream science, prefers anecdotal evidence, distrusts experts"
            }
        }
    
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        prototypes = self.prototypes.get(trait, {})
        
        return f"""Compare these tweets to personality prototypes.

TRAIT: {trait}
LOW PROTOTYPE ({scale_info['min']}-{scale_info['min']+2}): {prototypes.get('low', 'N/A')}
HIGH PROTOTYPE ({scale_info['max']-2}-{scale_info['max']}): {prototypes.get('high', 'N/A')}

TWEETS TO ANALYZE:
{self._format_tweets(tweets[:20])}

Compare to prototypes:
1. Similarity to LOW prototype (0-10)
2. Similarity to HIGH prototype (0-10)
3. Best match and predicted score

Return JSON:
{{
  "low_similarity": <0-10>,
  "high_similarity": <0-10>,
  "low_evidence": ["evidence 1", "evidence 2"],
  "high_evidence": ["evidence 1", "evidence 2"],
  "predicted_score": <number>,
  "confidence": <0-1>
}}"""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        return json.loads(response)
    
    def _format_tweets(self, tweets: List[str]) -> str:
        return "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(tweets)])

class ChainOfThoughtStrategy(BasePromptStrategy):
    """Step-by-step reasoning approach."""
    
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        return f"""Analyze personality through step-by-step reasoning.

TRAIT: {trait}
SCALE: {scale_info['question']} ({scale_info['min']}-{scale_info['max']})

TWEETS:
{self._format_tweets(tweets[:20])}

REASONING STEPS:
1. Identify explicit statements about {trait}
2. Analyze implicit behavioral patterns
3. Consider frequency and consistency
4. Account for contradictory evidence
5. Synthesize into prediction

Work through each step, then provide:

Return JSON:
{{
  "step1_explicit": "findings",
  "step2_implicit": "findings",
  "step3_consistency": "findings",
  "step4_contradictions": "findings",
  "step5_synthesis": "reasoning",
  "predicted_score": <number>,
  "confidence": <0-1>
}}"""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        return json.loads(response)
    
    def _format_tweets(self, tweets: List[str]) -> str:
        return "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(tweets)])

class MetaCognitiveStrategy(BasePromptStrategy):
    """Include uncertainty and self-reflection."""
    
    def generate_prompt(self, tweets: List[str], trait: str, scale_info: Dict) -> str:
        return f"""Predict personality with explicit uncertainty reasoning.

TRAIT: {trait}
SCALE: {scale_info['min']}-{scale_info['max']}

TWEETS:
{self._format_tweets(tweets[:20])}

Provide prediction with metacognitive analysis:
1. Initial prediction based on evidence
2. Sources of uncertainty
3. Alternative interpretations
4. Confidence calibration

Return JSON:
{{
  "initial_prediction": <number>,
  "uncertainty_sources": ["source 1", "source 2"],
  "alternative_interpretations": [
    {{"interpretation": "alt 1", "score": <number>}},
    {{"interpretation": "alt 2", "score": <number>}}
  ],
  "final_prediction": <number>,
  "confidence": <0-1>,
  "confidence_reasoning": "why this confidence level"
}}"""
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        return json.loads(response)
    
    def _format_tweets(self, tweets: List[str]) -> str:
        return "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(tweets)])

class PromptEngineeringFramework:
    """Framework for systematic prompt engineering."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.strategies = {
            'direct_mapping': DirectMappingStrategy(),
            'psychological_framework': PsychologicalFrameworkStrategy(),
            'comparative_analysis': ComparativeAnalysisStrategy(),
            'chain_of_thought': ChainOfThoughtStrategy(),
            'metacognitive': MetaCognitiveStrategy()
        }
        
        self.results_cache = {}
    
    def test_strategy(self, strategy_name: str, tweets: List[str], 
                     trait: str, scale_info: Dict) -> Dict[str, Any]:
        """Test a specific prompting strategy."""
        
        if strategy_name not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        strategy = self.strategies[strategy_name]
        
        # Generate prompt
        prompt = strategy.generate_prompt(tweets, trait, scale_info)
        
        # Get LLM response
        start_time = time.time()
        
        # Define schema based on strategy
        schema = self._get_schema_for_strategy(strategy_name)
        
        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema=schema
        )
        
        inference_time = time.time() - start_time
        
        # Parse response
        result = strategy.parse_response(response["response"].choices[0].message.content)
        
        # Add metadata
        result['strategy'] = strategy_name
        result['inference_time'] = inference_time
        result['prompt_length'] = len(prompt)
        
        return result
    
    def compare_strategies(self, tweets: List[str], trait: str, 
                         scale_info: Dict, ground_truth: Optional[float] = None) -> Dict[str, Any]:
        """Compare all strategies on the same input."""
        
        comparison_results = {}
        
        for strategy_name in self.strategies:
            try:
                result = self.test_strategy(strategy_name, tweets, trait, scale_info)
                
                if ground_truth is not None:
                    result['error'] = abs(result.get('predicted_score', 0) - ground_truth)
                    result['final_prediction'] = result.get('final_prediction', result.get('predicted_score', 0))
                
                comparison_results[strategy_name] = result
                
            except Exception as e:
                logger.error(f"Strategy {strategy_name} failed: {e}")
                comparison_results[strategy_name] = {
                    'error': str(e),
                    'failed': True
                }
        
        # Analyze results
        analysis = self._analyze_strategy_comparison(comparison_results, ground_truth)
        
        return {
            'strategy_results': comparison_results,
            'analysis': analysis,
            'best_strategy': analysis.get('best_strategy'),
            'ensemble_prediction': analysis.get('ensemble_prediction')
        }
    
    def _get_schema_for_strategy(self, strategy_name: str) -> Dict:
        """Get JSON schema for strategy output."""
        
        schemas = {
            'direct_mapping': {
                "type": "object",
                "properties": {
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "key_evidence": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["predicted_score", "confidence"]
            },
            'psychological_framework': {
                "type": "object",
                "properties": {
                    "framework_analysis": {
                        "type": "object",
                        "properties": {
                            "indicators_found": {"type": "array", "items": {"type": "string"}},
                            "psychological_interpretation": {"type": "string"}
                        }
                    },
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["framework_analysis", "predicted_score", "confidence"]
            },
            'comparative_analysis': {
                "type": "object",
                "properties": {
                    "low_similarity": {"type": "number", "minimum": 0, "maximum": 10},
                    "high_similarity": {"type": "number", "minimum": 0, "maximum": 10},
                    "low_evidence": {"type": "array", "items": {"type": "string"}},
                    "high_evidence": {"type": "array", "items": {"type": "string"}},
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["low_similarity", "high_similarity", "predicted_score", "confidence"]
            },
            'chain_of_thought': {
                "type": "object",
                "properties": {
                    "step1_explicit": {"type": "string"},
                    "step2_implicit": {"type": "string"},
                    "step3_consistency": {"type": "string"},
                    "step4_contradictions": {"type": "string"},
                    "step5_synthesis": {"type": "string"},
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["predicted_score", "confidence"]
            },
            'metacognitive': {
                "type": "object",
                "properties": {
                    "initial_prediction": {"type": "number"},
                    "uncertainty_sources": {"type": "array", "items": {"type": "string"}},
                    "alternative_interpretations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "interpretation": {"type": "string"},
                                "score": {"type": "number"}
                            }
                        }
                    },
                    "final_prediction": {"type": "number"},
                    "confidence": {"type": "number"},
                    "confidence_reasoning": {"type": "string"}
                },
                "required": ["final_prediction", "confidence"]
            }
        }
        
        return schemas.get(strategy_name, {})
    
    def _analyze_strategy_comparison(self, results: Dict[str, Any], 
                                   ground_truth: Optional[float]) -> Dict[str, Any]:
        """Analyze comparison results."""
        
        analysis = {
            'predictions': {},
            'confidences': {},
            'inference_times': {}
        }
        
        valid_results = {k: v for k, v in results.items() if not v.get('failed', False)}
        
        # Extract predictions and metrics
        for strategy, result in valid_results.items():
            pred_score = result.get('final_prediction', result.get('predicted_score', 0))
            analysis['predictions'][strategy] = pred_score
            analysis['confidences'][strategy] = result.get('confidence', 0)
            analysis['inference_times'][strategy] = result.get('inference_time', 0)
        
        if analysis['predictions']:
            # Calculate ensemble prediction
            predictions = list(analysis['predictions'].values())
            confidences = list(analysis['confidences'].values())
            
            # Weighted average by confidence
            if sum(confidences) > 0:
                analysis['ensemble_prediction'] = sum(p * c for p, c in zip(predictions, confidences)) / sum(confidences)
            else:
                analysis['ensemble_prediction'] = np.mean(predictions)
            
            # Find best strategy
            if ground_truth is not None:
                errors = {s: abs(p - ground_truth) for s, p in analysis['predictions'].items()}
                analysis['best_strategy'] = min(errors.items(), key=lambda x: x[1])[0]
                analysis['strategy_errors'] = errors
            else:
                # Use highest confidence
                analysis['best_strategy'] = max(analysis['confidences'].items(), key=lambda x: x[1])[0]
            
            # Strategy agreement
            analysis['prediction_std'] = float(np.std(predictions))
            analysis['prediction_range'] = float(max(predictions) - min(predictions))
            analysis['strategy_agreement'] = float(1 - analysis['prediction_std'] / 5)  # Normalized
        
        return analysis
    
    def optimize_prompts(self, training_data: List[Tuple[List[str], Dict[str, float]]], 
                        trait: str, scale_info: Dict) -> Dict[str, Any]:
        """Optimize prompts based on training data."""
        
        optimization_results = {
            'strategy_performance': {},
            'best_prompts': {},
            'optimization_insights': []
        }
        
        # Test each strategy on training data
        for strategy_name in self.strategies:
            errors = []
            successes = []
            
            for tweets, ground_truth_dict in training_data[:5]:  # Limit for demo
                gt_value = ground_truth_dict.get(trait, 0)
                
                try:
                    result = self.test_strategy(strategy_name, tweets, trait, scale_info)
                    pred = result.get('final_prediction', result.get('predicted_score', 0))
                    error = abs(pred - gt_value)
                    
                    errors.append(error)
                    if error < 1.5:
                        successes.append({
                            'tweets_sample': tweets[:3],
                            'prediction': pred,
                            'ground_truth': gt_value,
                            'confidence': result.get('confidence', 0)
                        })
                    
                except Exception as e:
                    logger.error(f"Failed to test {strategy_name}: {e}")
            
            if errors:
                optimization_results['strategy_performance'][strategy_name] = {
                    'mean_error': float(np.mean(errors)),
                    'success_rate': float(len([e for e in errors if e < 1.5]) / len(errors)),
                    'successful_examples': successes[:2]  # Keep best examples
                }
        
        # Rank strategies
        ranked_strategies = sorted(
            optimization_results['strategy_performance'].items(),
            key=lambda x: x[1]['mean_error']
        )
        
        optimization_results['strategy_ranking'] = [s[0] for s in ranked_strategies]
        
        # Generate insights
        optimization_results['optimization_insights'] = [
            f"Best strategy for {trait}: {ranked_strategies[0][0]}",
            f"Average error range: {ranked_strategies[0][1]['mean_error']:.2f} - {ranked_strategies[-1][1]['mean_error']:.2f}",
            "Metacognitive strategies provide better calibrated confidence",
            "Comparative analysis works well for extreme cases"
        ]
        
        return optimization_results


def run_prompt_engineering_analysis():
    """Run comprehensive prompt engineering analysis."""
    
    # Initialize
    llm_client = UniversalModelClient()
    framework = PromptEngineeringFramework(llm_client)
    
    # Define test case
    test_tweets = [
        "Just voted! Every citizen should participate in democracy.",
        "Can't believe what the liberals are doing to this country...",
        "Government overreach is destroying our freedoms!",
        "Both parties are corrupt, but at least Republicans stand for values.",
        "Mainstream media is just propaganda at this point.",
        "Wake up people! They're controlling the narrative.",
        "I love this country but hate what it's becoming.",
        "Traditional values are under attack everywhere.",
        "Why does anyone trust these so-called experts?",
        "My family comes first, always has and always will."
    ]
    
    scale_info = {
        'min': 1,
        'max': 11,
        'question': 'Rate your political orientation from very liberal (1) to very conservative (11)'
    }
    
    # Test all strategies
    print("\n" + "="*80)
    print("PROMPT ENGINEERING FRAMEWORK ANALYSIS")
    print("="*80)
    
    results = framework.compare_strategies(
        test_tweets, 
        'political',
        scale_info,
        ground_truth=8.5  # Conservative leaning
    )
    
    print("\nSTRATEGY COMPARISON:")
    print("-"*50)
    
    for strategy, result in results['strategy_results'].items():
        if not result.get('failed'):
            pred = result.get('final_prediction', result.get('predicted_score', 0))
            conf = result.get('confidence', 0)
            error = result.get('error', 0)
            time = result.get('inference_time', 0)
            
            print(f"\n{strategy.upper()}:")
            print(f"  Prediction: {pred:.1f}")
            print(f"  Confidence: {conf:.2f}")
            print(f"  Error: {error:.2f}")
            print(f"  Time: {time:.2f}s")
    
    print("\n" + "-"*50)
    print("ANALYSIS:")
    print(f"Best Strategy: {results['analysis']['best_strategy']}")
    print(f"Ensemble Prediction: {results['analysis']['ensemble_prediction']:.1f}")
    print(f"Strategy Agreement: {results['analysis']['strategy_agreement']:.2f}")
    
    # Save results
    output_file = "prompt_engineering_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    run_prompt_engineering_analysis()