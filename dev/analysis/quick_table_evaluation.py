#!/usr/bin/env python3
"""
Quick table evaluation - just get the r values for each scale
"""

import json
import numpy as np
from pathlib import Path
import sys
from scipy.stats import pearsonr

sys.path.append(str(Path(__file__).parent / "uncertainty_stress_test" / "personality-prediction"))

from quick_test_personality_system import QuickPersonalitySystem

def quick_table_evaluation(n_users: int = 15):
    """Get r values for each personality scale quickly"""
    
    print("=== QUICK TABLE EVALUATION ===")
    
    # Load data
    dataset_path = Path(__file__).parent / "uncertainty_stress_test" / "100_users_500tweets_dataset.json"
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # Initialize system
    system = QuickPersonalitySystem()
    
    # Process users
    valid_users = []
    
    for user in data[:n_users]:
        user_info = user.get('user_info', {})
        tweets = user.get('tweets', [])
        
        # Extract scores
        user_scores = {}
        
        # Political
        if 'political' in user_info and user_info['political']:
            try:
                user_scores['political'] = float(user_info['political'])
            except:
                pass
        
        # Narcissism (average of items)
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
        
        # Conspiracy (average of items)
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
            
        # Denialism (average of items)
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
        
        # Extract tweets
        tweet_texts = [t['text'] for t in tweets if t.get('text', '').strip()][:10]
        
        if len(tweet_texts) >= 3 and len(user_scores) >= 2:
            valid_users.append((tweet_texts, user_scores))
    
    print(f"Processing {len(valid_users)} valid users")
    
    # Make predictions
    all_predictions = []
    
    for i, (tweets, true_scores) in enumerate(valid_users):
        print(f"User {i+1}/{len(valid_users)}: ", end="", flush=True)
        
        try:
            result = system.predict_user_personality(tweets)
            
            if 'trait_predictions' in result:
                pred_scores = {}
                for scale in ['political', 'narcissism', 'conspiracy', 'denialism']:
                    if scale in result['trait_predictions']:
                        pred_scores[scale] = result['trait_predictions'][scale]['predicted_score']
                
                all_predictions.append((true_scores, pred_scores))
                print(f"✓ ({len(pred_scores)} scales)")
            else:
                print("✗")
                
        except Exception as e:
            print(f"✗")
    
    print(f"\nGot predictions for {len(all_predictions)} users")
    
    # Calculate correlations for each scale
    results = {}
    
    print(f"\n{'Scale':<15} {'Method':<25} {'N':<4} {'r':<6} {'p-value':<8}")
    print("-" * 65)
    
    for scale in ['political', 'narcissism', 'conspiracy', 'denialism']:
        # Extract data for this scale
        y_true = []
        y_pred = []
        
        for true_scores, pred_scores in all_predictions:
            if scale in true_scores and scale in pred_scores:
                y_true.append(true_scores[scale])
                y_pred.append(pred_scores[scale])
        
        if len(y_true) >= 5:
            y_true = np.array(y_true)
            y_pred = np.array(y_pred)
            
            # Calculate correlation
            r, p_value = pearsonr(y_true, y_pred)
            
            results[scale] = {
                'n': len(y_true),
                'r': r,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
            
            # Print row
            method = "LLM Direct Survey Mapping"
            sig_marker = "*" if p_value < 0.05 else " "
            print(f"{scale:<15} {method:<25} {len(y_true):<4} {r:<6.3f}{sig_marker} {p_value:<8.4f}")
        
        else:
            print(f"{scale:<15} {'LLM Direct Survey Mapping':<25} {'<5':<4} {'N/A':<6} {'N/A':<8}")
    
    print("\n* = statistically significant (p < 0.05)")
    
    # Summary
    valid_results = [r for r in results.values() if not np.isnan(r['r'])]
    if valid_results:
        mean_r = np.mean([r['r'] for r in valid_results])
        significant_count = sum(1 for r in valid_results if r['significant'])
        
        print(f"\nSUMMARY:")
        print(f"Mean correlation: {mean_r:.3f}")
        print(f"Significant correlations: {significant_count}/{len(valid_results)}")
    
    return results

if __name__ == "__main__":
    results = quick_table_evaluation()