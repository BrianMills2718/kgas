#!/usr/bin/env python3
"""
Comprehensive evaluation of all 4 personality scales
Generate table with r values for each scale
"""

import json
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent / "uncertainty_stress_test" / "personality-prediction"))

from quick_test_personality_system import QuickPersonalitySystem
from statistical_evaluation_framework import StatisticalEvaluator, PersonalityScale

def evaluate_all_scales(n_users: int = 25):
    """Evaluate all 4 personality scales"""
    
    print("=== COMPREHENSIVE PERSONALITY EVALUATION ===")
    print(f"Testing {n_users} users across all 4 personality scales")
    
    # Load data
    dataset_path = Path(__file__).parent / "uncertainty_stress_test" / "100_users_500tweets_dataset.json"
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # Initialize system
    system = QuickPersonalitySystem()
    evaluator = StatisticalEvaluator()
    
    # Define scales
    scales = {
        'political': PersonalityScale("Political Orientation", "political", 1, 11, 2.0, 6.0, 2.5),
        'narcissism': PersonalityScale("Narcissism", "narcissism", 1, 7, 1.5, 3.5, 1.2),
        'conspiracy': PersonalityScale("Conspiracy Mentality", "conspiracy", 1, 7, 2.5, 3.0, 1.6),
        'denialism': PersonalityScale("Science Denialism", "denialism", 1, 7, 3.0, 2.5, 1.8)
    }
    
    # Process users and extract all personality scores
    valid_users = []
    personality_scores = {scale: [] for scale in scales.keys()}
    
    for user in data[:n_users]:
        user_info = user.get('user_info', {})
        tweets = user.get('tweets', [])
        
        # Extract tweet texts
        tweet_texts = [t['text'] for t in tweets if t.get('text', '').strip()][:10]
        
        if len(tweet_texts) < 3:
            continue
            
        # Extract personality scores
        user_scores = {}
        
        # Political (single item)
        if 'political' in user_info and user_info['political']:
            try:
                user_scores['political'] = float(user_info['political'])
            except:
                pass
        
        # Narcissism (average of 4 items)
        narcissism_items = []
        for i in range(1, 5):
            key = f'narcissism_{i}'
            if key in user_info and user_info[key]:
                try:
                    narcissism_items.append(float(user_info[key]))
                except:
                    pass
        if narcissism_items:
            user_scores['narcissism'] = np.mean(narcissism_items)
        
        # Conspiracy (average of 5 items)
        conspiracy_items = []
        for i in range(1, 6):
            key = f'conspiracy_{i}'
            if key in user_info and user_info[key]:
                try:
                    conspiracy_items.append(float(user_info[key]))
                except:
                    pass
        if conspiracy_items:
            user_scores['conspiracy'] = np.mean(conspiracy_items)
            
        # Denialism (average of 4 items)
        denialism_items = []
        for i in range(1, 5):
            key = f'denialism_{i}'
            if key in user_info and user_info[key]:
                try:
                    denialism_items.append(float(user_info[key]))
                except:
                    pass
        if denialism_items:
            user_scores['denialism'] = np.mean(denialism_items)
        
        # Only include users with at least 2 valid personality scores
        if len(user_scores) >= 2:
            valid_users.append((tweet_texts, user_scores))
    
    print(f"Found {len(valid_users)} valid users")
    
    if len(valid_users) < 10:
        print("❌ Not enough valid users")
        return
    
    # Make predictions for all users
    print("\nMaking LLM predictions for all users...")
    all_predictions = []
    
    for i, (tweets, true_scores) in enumerate(valid_users):
        print(f"  User {i+1}/{len(valid_users)}: ", end="", flush=True)
        
        try:
            result = system.predict_user_personality(tweets)
            
            if 'trait_predictions' in result:
                user_predictions = {}
                for scale in scales.keys():
                    if scale in result['trait_predictions']:
                        scale_result = result['trait_predictions'][scale]
                        user_predictions[scale] = {
                            'predicted_score': scale_result['predicted_score'],
                            'confidence': scale_result['confidence']
                        }
                
                all_predictions.append((true_scores, user_predictions))
                print(f"✓ ({len(user_predictions)} scales)")
            else:
                print("✗ No predictions")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\nSuccessfully predicted for {len(all_predictions)} users")
    
    # Evaluate each scale
    results_table = {}
    
    print(f"\n=== EVALUATION RESULTS ===")
    print(f"{'Scale':<20} {'N':<4} {'r':<6} {'p-value':<8} {'MAE':<6} {'R²':<6}")
    print("-" * 60)
    
    for scale_name, scale_info in scales.items():
        # Extract predictions and ground truth for this scale
        y_true = []
        y_pred = []
        confidences = []
        
        for true_scores, pred_scores in all_predictions:
            if scale_name in true_scores and scale_name in pred_scores:
                y_true.append(true_scores[scale_name])
                y_pred.append(pred_scores[scale_name]['predicted_score'])
                confidences.append(pred_scores[scale_name]['confidence'])
        
        if len(y_true) < 5:
            print(f"{scale_name:<20} {'<5':<4} {'N/A':<6} {'N/A':<8} {'N/A':<6} {'N/A':<6}")
            continue
            
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Statistical evaluation
        result = evaluator.evaluate_prediction_system(y_true, y_pred, scale_info)
        
        # Store results
        results_table[scale_name] = {
            'n': len(y_true),
            'correlation': result.correlation,
            'p_value': result.correlation_pvalue,
            'mae': result.mae,
            'r_squared': result.r_squared,
            'is_significant': result.is_significant,
            'ground_truth_mean': float(np.mean(y_true)),
            'ground_truth_std': float(np.std(y_true)),
            'prediction_mean': float(np.mean(y_pred)),
            'prediction_std': float(np.std(y_pred)),
            'confidence_mean': float(np.mean(confidences))
        }
        
        # Print row
        significance_marker = "*" if result.is_significant else " "
        print(f"{scale_name:<20} {len(y_true):<4} {result.correlation:<6.3f}{significance_marker} {result.correlation_pvalue:<8.4f} {result.mae:<6.3f} {result.r_squared:<6.3f}")
    
    print("\n* = statistically significant (p < 0.05)")
    
    # Summary statistics
    print(f"\n=== SUMMARY ===")
    significant_scales = [s for s, r in results_table.items() if r['is_significant']]
    mean_r = np.mean([r['correlation'] for r in results_table.values() if not np.isnan(r['correlation'])])
    
    print(f"Scales with significant correlations: {len(significant_scales)}/{len(results_table)}")
    print(f"Mean correlation across all scales: {mean_r:.3f}")
    print(f"Significant scales: {', '.join(significant_scales)}")
    
    # Save results
    output = {
        'evaluation_timestamp': datetime.now().isoformat(),
        'n_users_total': len(valid_users),
        'n_users_predicted': len(all_predictions),
        'results_by_scale': results_table,
        'summary': {
            'significant_scales': significant_scales,
            'mean_correlation': float(mean_r),
            'scales_evaluated': list(results_table.keys())
        }
    }
    
    with open('comprehensive_personality_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nDetailed results saved to comprehensive_personality_results.json")
    
    return results_table

if __name__ == "__main__":
    results = evaluate_all_scales(n_users=30)