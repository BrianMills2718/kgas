#!/usr/bin/env python3
"""
Analyze accuracy of predictions against Kunst ground truth data
"""

import json
import numpy as np
from pathlib import Path
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr

def load_kunst_comparison_data():
    """Load the Kunst comparison data with ground truth."""
    file_path = Path("/home/brian/projects/Digimons/uncertainty_stress_test/kunst_sample_5users_bayesian_comparison.json")
    
    with open(file_path, 'r') as f:
        return json.load(f)

def analyze_accuracy(data):
    """Analyze prediction accuracy against ground truth."""
    
    results = {
        'single_update': {},
        'sequential_updates': {},
        'overall': {}
    }
    
    # Collect all predictions and ground truth values
    all_predictions_single = []
    all_predictions_seq = []
    all_ground_truth = []
    
    # Trait-specific analysis
    traits = ['political', 'narcissism', 'conspiracy', 'denialism']
    
    for trait in traits:
        predictions_single = []
        predictions_seq = []
        ground_truth = []
        scales = []
        
        for user_data in data:
            # Get ground truth
            gt_value = user_data['ground_truth'][trait]
            
            # Get predictions
            single_pred = user_data['single_update'][trait]['predicted_score']
            seq_pred = user_data['sequential_updates'][trait]['predicted_score']
            
            # Get scale info
            scale = user_data['single_update'][trait]['scale']
            
            predictions_single.append(single_pred)
            predictions_seq.append(seq_pred)
            ground_truth.append(gt_value)
            scales.append(scale)
            
            # Add to overall lists
            all_predictions_single.append(single_pred)
            all_predictions_seq.append(seq_pred)
            all_ground_truth.append(gt_value)
        
        # Calculate metrics for this trait
        results['single_update'][trait] = calculate_metrics(predictions_single, ground_truth, scales[0])
        results['sequential_updates'][trait] = calculate_metrics(predictions_seq, ground_truth, scales[0])
    
    # Overall metrics
    results['overall']['single_update'] = calculate_metrics(all_predictions_single, all_ground_truth, None)
    results['overall']['sequential_updates'] = calculate_metrics(all_predictions_seq, all_ground_truth, None)
    
    return results

def calculate_metrics(predictions, ground_truth, scale):
    """Calculate various accuracy metrics."""
    
    predictions = np.array(predictions)
    ground_truth = np.array(ground_truth)
    
    # Basic metrics
    mae = mean_absolute_error(ground_truth, predictions)
    mse = mean_squared_error(ground_truth, predictions)
    rmse = np.sqrt(mse)
    
    # Correlation
    if len(predictions) > 1:
        correlation, p_value = pearsonr(predictions, ground_truth)
    else:
        correlation, p_value = 0.0, 1.0
    
    # Scale-adjusted metrics
    if scale:
        scale_range = scale[1] - scale[0]
        mae_percent = (mae / scale_range) * 100
        rmse_percent = (rmse / scale_range) * 100
    else:
        mae_percent = None
        rmse_percent = None
    
    # Classification accuracy (low/medium/high)
    if scale and scale[1] == 7:  # 1-7 scale
        pred_class = ['low' if p <= 3 else 'medium' if p <= 5 else 'high' for p in predictions]
        true_class = ['low' if t <= 3 else 'medium' if t <= 5 else 'high' for t in ground_truth]
    elif scale and scale[1] == 11:  # 1-11 scale
        pred_class = ['low' if p <= 4 else 'medium' if p <= 7 else 'high' for p in predictions]
        true_class = ['low' if t <= 4 else 'medium' if t <= 7 else 'high' for t in ground_truth]
    else:
        pred_class = []
        true_class = []
    
    if pred_class:
        classification_accuracy = np.mean(np.array(pred_class) == np.array(true_class))
    else:
        classification_accuracy = None
    
    # Direction accuracy (prediction in right direction from midpoint)
    if scale:
        midpoint = (scale[0] + scale[1]) / 2
        pred_direction = predictions > midpoint
        true_direction = ground_truth > midpoint
        direction_accuracy = np.mean(pred_direction == true_direction)
    else:
        direction_accuracy = None
    
    return {
        'mae': mae,
        'mse': mse,
        'rmse': rmse,
        'mae_percent': mae_percent,
        'rmse_percent': rmse_percent,
        'correlation': correlation,
        'p_value': p_value,
        'classification_accuracy': classification_accuracy,
        'direction_accuracy': direction_accuracy,
        'n_samples': len(predictions)
    }

def print_results(results):
    """Print formatted results."""
    
    print("="*80)
    print("🎯 KUNST GROUND TRUTH ACCURACY ANALYSIS")
    print("="*80)
    print()
    
    print("📊 BASELINE METHOD PERFORMANCE")
    print("-"*50)
    
    # Overall results
    print("\n🔍 OVERALL ACCURACY:")
    single = results['overall']['single_update']
    seq = results['overall']['sequential_updates']
    
    print(f"   Single Update:     MAE={single['mae']:.2f}, RMSE={single['rmse']:.2f}, r={single['correlation']:.3f}")
    print(f"   Sequential Update: MAE={seq['mae']:.2f}, RMSE={seq['rmse']:.2f}, r={seq['correlation']:.3f}")
    
    # Trait-specific results
    print("\n📈 BY TRAIT:")
    traits = ['political', 'narcissism', 'conspiracy', 'denialism']
    
    for trait in traits:
        print(f"\n   {trait.upper()}:")
        
        single = results['single_update'][trait]
        seq = results['sequential_updates'][trait]
        
        print(f"   Single Update:")
        print(f"     MAE: {single['mae']:.2f} ({single['mae_percent']:.1f}% of scale)")
        print(f"     RMSE: {single['rmse']:.2f} ({single['rmse_percent']:.1f}% of scale)")
        print(f"     Correlation: {single['correlation']:.3f} (p={single['p_value']:.3f})")
        if single['classification_accuracy'] is not None:
            print(f"     Classification Accuracy: {single['classification_accuracy']:.2f}")
        if single['direction_accuracy'] is not None:
            print(f"     Direction Accuracy: {single['direction_accuracy']:.2f}")
        
        print(f"   Sequential Update:")
        print(f"     MAE: {seq['mae']:.2f} ({seq['mae_percent']:.1f}% of scale)")
        print(f"     RMSE: {seq['rmse']:.2f} ({seq['rmse_percent']:.1f}% of scale)")
        print(f"     Correlation: {seq['correlation']:.3f} (p={seq['p_value']:.3f})")
        if seq['classification_accuracy'] is not None:
            print(f"     Classification Accuracy: {seq['classification_accuracy']:.2f}")
        if seq['direction_accuracy'] is not None:
            print(f"     Direction Accuracy: {seq['direction_accuracy']:.2f}")
    
    print("\n" + "="*80)
    print("💡 KEY INSIGHTS:")
    print("="*80)
    
    # Calculate average MAE across traits
    avg_mae_single = np.mean([results['single_update'][t]['mae'] for t in traits])
    avg_mae_seq = np.mean([results['sequential_updates'][t]['mae'] for t in traits])
    
    print(f"\n1. Average MAE across traits:")
    print(f"   - Single Update: {avg_mae_single:.2f}")
    print(f"   - Sequential Update: {avg_mae_seq:.2f}")
    
    # Find best and worst performing traits
    mae_by_trait = {t: results['sequential_updates'][t]['mae'] for t in traits}
    best_trait = min(mae_by_trait, key=mae_by_trait.get)
    worst_trait = max(mae_by_trait, key=mae_by_trait.get)
    
    print(f"\n2. Best performing trait: {best_trait} (MAE={mae_by_trait[best_trait]:.2f})")
    print(f"   Worst performing trait: {worst_trait} (MAE={mae_by_trait[worst_trait]:.2f})")
    
    # Check if sequential updates improve over single
    improvements = []
    for trait in traits:
        single_mae = results['single_update'][trait]['mae']
        seq_mae = results['sequential_updates'][trait]['mae']
        improvement = (single_mae - seq_mae) / single_mae * 100
        improvements.append(improvement)
    
    avg_improvement = np.mean(improvements)
    print(f"\n3. Sequential updates vs single update:")
    print(f"   Average improvement: {avg_improvement:.1f}%")
    
    # Sample details
    print(f"\n4. Sample size: {results['overall']['single_update']['n_samples'] // len(traits)} users")

def main():
    """Run the analysis."""
    
    # Load data
    data = load_kunst_comparison_data()
    
    # Analyze accuracy
    results = analyze_accuracy(data)
    
    # Print results
    print_results(results)
    
    # Save detailed results
    output_file = "kunst_accuracy_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Show individual user examples
    print("\n📋 INDIVIDUAL USER EXAMPLES:")
    print("-"*50)
    
    for i, user_data in enumerate(data[:3]):  # Show first 3 users
        print(f"\nUser: {user_data['user']}")
        print(f"Tweet count: {user_data['tweet_count']}")
        print("\n   Trait      | Ground Truth | Predicted | Error")
        print("   -----------|--------------|-----------|-------")
        
        for trait in ['political', 'narcissism', 'conspiracy', 'denialism']:
            gt = user_data['ground_truth'][trait]
            pred = user_data['sequential_updates'][trait]['predicted_score']
            error = abs(gt - pred)
            updates = user_data['sequential_updates'][trait]['updates']
            
            print(f"   {trait:10} | {gt:12.2f} | {pred:9.2f} | {error:5.2f} (updates: {updates})")

if __name__ == "__main__":
    main()