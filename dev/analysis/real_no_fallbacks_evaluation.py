#!/usr/bin/env python3
"""
Real evaluation with no fallbacks - properly extract results
"""

import json
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent / "uncertainty_stress_test" / "personality-prediction"))

from quick_test_personality_system import QuickPersonalitySystem
from statistical_evaluation_framework import StatisticalEvaluator, PersonalityScale

def real_evaluation(n_users: int = 20):
    """Run real evaluation with proper extraction"""
    
    print("=== REAL NO-FALLBACKS EVALUATION ===")
    print(f"Testing {n_users} users with real LLM predictions")
    
    # Load data
    dataset_path = Path(__file__).parent / "uncertainty_stress_test" / "100_users_500tweets_dataset.json"
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # Initialize system
    system = QuickPersonalitySystem()
    evaluator = StatisticalEvaluator()
    
    # Focus on political orientation
    scale = 'political'
    scale_info = PersonalityScale("Political Orientation", "political", 1, 11, 2.0, 6.0, 2.5)
    
    # Process users
    valid_users = []
    y_true = []
    
    for user in data[:n_users]:
        user_info = user.get('user_info', {})
        tweets = user.get('tweets', [])
        
        # Check if user has political score
        if 'political' in user_info and user_info['political']:
            try:
                political_score = float(user_info['political'])
                tweet_texts = [t['text'] for t in tweets if t.get('text', '').strip()][:10]  # 10 tweets
                
                if len(tweet_texts) >= 3:  # Minimum tweets
                    valid_users.append(tweet_texts)
                    y_true.append(political_score)
            except:
                pass
    
    print(f"Found {len(valid_users)} valid users")
    
    if len(valid_users) < 5:
        print("❌ Not enough valid users")
        return
    
    y_true = np.array(y_true)
    print(f"Ground truth: mean={np.mean(y_true):.2f}, std={np.std(y_true):.2f}, range={np.min(y_true):.1f}-{np.max(y_true):.1f}")
    
    # Make predictions
    print("\nMaking real LLM predictions...")
    y_pred = []
    confidences = []
    
    for i, tweets in enumerate(valid_users):
        print(f"  User {i+1}/{len(valid_users)}: ", end="", flush=True)
        
        try:
            result = system.predict_user_personality(tweets)
            
            # Extract prediction using correct structure
            if 'trait_predictions' in result and 'political' in result['trait_predictions']:
                political_result = result['trait_predictions']['political']
                pred_score = political_result['predicted_score']
                confidence = political_result['confidence']
                
                y_pred.append(pred_score)
                confidences.append(confidence)
                
                print(f"pred={pred_score:.1f} (conf={confidence:.2f}, true={y_true[i]:.1f})")
            else:
                raise RuntimeError("Missing political prediction in result")
                
        except Exception as e:
            print(f"FAILED: {e}")
            # Don't use fallbacks - skip this user
            continue
    
    if len(y_pred) != len(y_true):
        print(f"❌ Prediction failures: got {len(y_pred)} predictions for {len(y_true)} users")
        return
    
    y_pred = np.array(y_pred)
    confidences = np.array(confidences)
    
    print(f"\nPredictions: mean={np.mean(y_pred):.2f}, std={np.std(y_pred):.2f}, range={np.min(y_pred):.1f}-{np.max(y_pred):.1f}")
    print(f"Confidences: mean={np.mean(confidences):.2f}, std={np.std(confidences):.2f}")
    
    # Statistical evaluation
    result = evaluator.evaluate_prediction_system(y_true, y_pred, scale_info)
    
    print(f"\n=== REAL RESULTS ===")
    print(f"Sample size: {len(y_true)}")
    print(f"Correlation: {result.correlation:.3f} (p = {result.correlation_pvalue:.4f})")
    print(f"MAE: {result.mae:.3f}")
    print(f"RMSE: {result.rmse:.3f}")
    print(f"R²: {result.r_squared:.3f}")
    print(f"Effect size: {result.effect_size_cohens_d:.3f}")
    print(f"Statistical power: {result.statistical_power:.3f}")
    print(f"Significant: {result.is_significant}")
    
    # Individual predictions
    print(f"\n=== INDIVIDUAL RESULTS ===")
    errors = np.abs(y_pred - y_true)
    for i in range(len(y_true)):
        print(f"User {i+1}: pred={y_pred[i]:.1f}, true={y_true[i]:.1f}, error={errors[i]:.1f}, conf={confidences[i]:.2f}")
    
    # Honest interpretation
    if result.correlation < 0.1:
        interpretation = "NEGLIGIBLE - essentially random"
    elif result.correlation < 0.3:
        interpretation = "WEAK - limited utility"
    elif result.correlation < 0.5:
        interpretation = "MODERATE - some utility"
    else:
        interpretation = "STRONG - substantial utility"
    
    print(f"\n🔍 HONEST ASSESSMENT:")
    print(f"   Correlation: r = {result.correlation:.3f}")
    print(f"   Interpretation: {interpretation}")
    print(f"   Variance explained: {result.r_squared:.1%}")
    print(f"   These are REAL LLM predictions on REAL data with NO FALLBACKS")
    
    # Save results
    results = {
        'n_users': len(y_true),
        'ground_truth': y_true.tolist(),
        'predictions': y_pred.tolist(),
        'confidences': confidences.tolist(),
        'correlation': float(result.correlation),
        'correlation_pvalue': float(result.correlation_pvalue),
        'mae': float(result.mae),
        'rmse': float(result.rmse),
        'r_squared': float(result.r_squared),
        'is_significant': bool(result.is_significant),
        'interpretation': interpretation,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('real_no_fallbacks_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results saved to real_no_fallbacks_results.json")
    
    return results

if __name__ == "__main__":
    results = real_evaluation(n_users=15)  # Start with 15 users