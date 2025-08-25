#!/usr/bin/env python3
"""
Quick Test of LLM Personality System
Runs faster test with fewer API calls
"""

import json
import numpy as np
import time
import logging
from pathlib import Path
import sys
from typing import Dict, List, Any

sys.path.append(str(Path(__file__).parent.parent.parent / "universal_model_tester"))

# NO FALLBACKS - fail loudly if import fails
from universal_model_client import UniversalModelClient

from working_llm_personality_system import (
    WorkingLLMPersonalitySystem, 
    PersonalitySystemValidator,
    PERSONALITY_SCALES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuickPersonalitySystem(WorkingLLMPersonalitySystem):
    """Faster version using single strategy."""
    
    def __init__(self):
        super().__init__(use_real_llm=True)
        # Use only one strategy for speed
        self.inference_strategies = [self.direct_survey_mapping]
    
    def quick_predict(self, tweets: List[str], trait_name: str) -> Dict[str, Any]:
        """Quick prediction using single strategy."""
        scale = PERSONALITY_SCALES[trait_name]
        return self.direct_survey_mapping(tweets, scale)

def run_quick_test():
    """Run quick test of the system."""
    
    print("\n" + "="*60)
    print("QUICK LLM PERSONALITY SYSTEM TEST")
    print("="*60)
    
    # Load test data
    dataset_path = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    
    if not Path(dataset_path).exists():
        print("Dataset not found - using simulated results")
        show_simulated_results()
        return
    
    # Initialize quick system
    system = QuickPersonalitySystem()
    
    # Load one user for testing
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    test_user = data[0]
    user_info = test_user['user_info']
    tweets = [t['text'] for t in test_user['tweets'] if t.get('text', '').strip()][:20]  # First 20 tweets
    
    print(f"\nTesting on user: {user_info['twitter_id']}")
    print(f"Using {len(tweets)} tweets")
    
    # Ground truth
    def safe_float(value, default):
        try:
            return float(value) if value and str(value).strip() else default
        except (ValueError, TypeError):
            return default
    
    ground_truth = {
        'political': safe_float(user_info.get('political'), 5),
        'narcissism': np.mean([safe_float(user_info.get(f'narcissism_{i}'), 4) for i in range(1, 5)]),
        'conspiracy': np.mean([safe_float(user_info.get(f'conspiracy_{i}'), 4) for i in range(1, 6)]),
        'denialism': np.mean([safe_float(user_info.get(f'denialism_{i}'), 4) for i in range(1, 5)])
    }
    
    print(f"\nGround Truth: {ground_truth}")
    
    # Test each trait
    results = {}
    for trait_name in ['political']:  # Test just one trait for speed
        print(f"\nPredicting {trait_name}...")
        
        try:
            start_time = time.time()
            result = system.quick_predict(tweets, trait_name)
            inference_time = time.time() - start_time
            
            pred_score = result.get('predicted_score', 0)
            confidence = result.get('confidence', 0)
            error = abs(pred_score - ground_truth[trait_name])
            
            results[trait_name] = {
                'prediction': pred_score,
                'confidence': confidence,
                'ground_truth': ground_truth[trait_name],
                'error': error,
                'time': inference_time
            }
            
            print(f"Prediction: {pred_score:.1f}")
            print(f"Ground Truth: {ground_truth[trait_name]:.1f}")
            print(f"Error: {error:.1f}")
            print(f"Confidence: {confidence:.2f}")
            print(f"Time: {inference_time:.1f}s")
            
            # Show reasoning if available
            if 'reasoning' in result:
                print(f"Reasoning: {result['reasoning'][:200]}...")
            
        except Exception as e:
            print(f"Failed to predict {trait_name}: {e}")
            results[trait_name] = {'error': str(e)}
    
    # Save results
    output_file = "quick_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

def show_simulated_results():
    """Show what results would look like."""
    
    print("\nSIMULATED RESULTS (for demonstration):")
    print("-" * 50)
    
    simulated_results = {
        'political': {
            'prediction': 6.2,
            'ground_truth': 6.0,
            'error': 0.2,
            'confidence': 0.85,
            'reasoning': 'User shows moderate conservative views based on posts about traditional values and skepticism of government overreach.'
        },
        'narcissism': {
            'prediction': 3.8,
            'ground_truth': 4.0,
            'error': 0.2,
            'confidence': 0.72,
            'reasoning': 'Posts show balanced self-regard with some self-promotion but also consideration for others.'
        },
        'conspiracy': {
            'prediction': 7.1,
            'ground_truth': 7.6,
            'error': 0.5,
            'confidence': 0.68,
            'reasoning': 'Strong skepticism of mainstream narratives and references to hidden agendas in multiple posts.'
        },
        'denialism': {
            'prediction': 4.3,
            'ground_truth': 4.25,
            'error': 0.05,
            'confidence': 0.79,
            'reasoning': 'Moderate distrust of scientific authority with preference for natural solutions.'
        }
    }
    
    print("TRAIT PREDICTIONS:")
    for trait, result in simulated_results.items():
        print(f"\n{trait.upper()}:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Ground Truth: {result['ground_truth']}")
        print(f"  Error: {result['error']:.1f}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
    
    avg_error = np.mean([r['error'] for r in simulated_results.values()])
    avg_confidence = np.mean([r['confidence'] for r in simulated_results.values()])
    
    print(f"\nOVERALL PERFORMANCE:")
    print(f"  Average Error: {avg_error:.2f}")
    print(f"  Average Confidence: {avg_confidence:.2f}")
    print(f"  Assessment: {'Good' if avg_error < 1.0 else 'Fair' if avg_error < 2.0 else 'Poor'}")

if __name__ == "__main__":
    run_quick_test()