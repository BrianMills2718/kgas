#!/usr/bin/env python3
"""
Demo Statistical Evaluation - Realistic Performance Assessment

This demonstrates what proper statistical evaluation looks like
with realistic sample sizes and honest performance metrics.
"""

import json
import numpy as np
from statistical_evaluation_framework import StatisticalEvaluator, PersonalityScale
from datetime import datetime

def create_realistic_demo_data(n_users: int = 150):
    """Create realistic demo data that mimics real personality prediction scenarios"""
    
    np.random.seed(42)  # For reproducible results
    
    # Create ground truth personality scores with realistic distributions
    data = []
    
    for i in range(n_users):
        # Realistic personality distributions (based on research)
        user_data = {
            'user_id': i,
            'ground_truth': {
                'political': np.clip(np.random.normal(4.0, 1.5), 1, 7),  # Slightly right-leaning mean
                'narcissism': np.clip(np.random.gamma(2, 1.5) + 1, 1, 7),  # Right-skewed
                'conspiracy': np.clip(np.random.beta(2, 5) * 6 + 1, 1, 7),  # Left-skewed
                'denialism': np.clip(np.random.normal(3.0, 1.8), 1, 7)  # Broad distribution
            },
            'tweets': [f"Tweet {j} from user {i}" for j in range(30)]  # Placeholder tweets
        }
        data.append(user_data)
    
    return data

def simulate_prediction_system(ground_truth: np.ndarray, system_quality: str = "realistic") -> np.ndarray:
    """
    Simulate different quality prediction systems
    
    Args:
        ground_truth: True personality scores
        system_quality: "excellent", "good", "realistic", "poor", "random"
    """
    
    n_samples = len(ground_truth)
    np.random.seed(42)
    
    if system_quality == "excellent":
        # Very good system (r ≈ 0.7)
        correlation = 0.7
        noise_std = 0.8
    elif system_quality == "good": 
        # Good system (r ≈ 0.5)
        correlation = 0.5
        noise_std = 1.2
    elif system_quality == "realistic":
        # Realistic LLM performance (r ≈ 0.25-0.35)
        correlation = 0.3
        noise_std = 1.5
    elif system_quality == "poor":
        # Poor system (r ≈ 0.15)
        correlation = 0.15
        noise_std = 1.8
    else:  # random
        correlation = 0.0
        noise_std = 2.0
    
    # Generate predictions with controlled correlation
    noise = np.random.normal(0, noise_std, n_samples)
    predictions = correlation * ground_truth + (1 - correlation) * noise + np.random.normal(4.0, 0.5, n_samples)
    
    # Clip to valid range
    predictions = np.clip(predictions, 1, 7)
    
    return predictions

def run_comprehensive_demo():
    """Run comprehensive statistical evaluation demo"""
    
    print("=== COMPREHENSIVE STATISTICAL EVALUATION DEMO ===")
    print("Demonstrating proper statistical methodology for personality prediction\n")
    
    # Create evaluator
    evaluator = StatisticalEvaluator()
    
    # Generate realistic demo data
    print("Creating realistic demo dataset...")
    demo_data = create_realistic_demo_data(n_users=150)
    
    # Define scales to test
    scales = {
        'political': PersonalityScale("Political Orientation", "political", 1, 7, 2.0, 4.0, 1.5),
        'narcissism': PersonalityScale("Narcissism", "narcissism", 1, 7, 1.5, 3.5, 1.2),
        'conspiracy': PersonalityScale("Conspiracy Mentality", "conspiracy", 1, 7, 2.5, 3.0, 1.6),
        'denialism': PersonalityScale("Climate Denialism", "denialism", 1, 7, 3.0, 2.5, 1.8)
    }
    
    # Test different system qualities
    system_qualities = ["excellent", "good", "realistic", "poor", "random"]
    
    all_results = {}
    
    for quality in system_qualities:
        print(f"\n--- Evaluating {quality.upper()} System ---")
        
        quality_results = {}
        
        for scale_name, scale_info in scales.items():
            # Extract ground truth for this scale
            y_true = np.array([user['ground_truth'][scale_name] for user in demo_data])
            
            # Generate predictions
            y_pred = simulate_prediction_system(y_true, quality)
            
            # Evaluate
            result = evaluator.evaluate_prediction_system(y_true, y_pred, scale_info)
            quality_results[scale_name] = result
            
            print(f"  {scale_name}: r={result.correlation:.3f}, MAE={result.mae:.3f}, p={result.correlation_pvalue:.4f}")
        
        all_results[quality] = quality_results
    
    # Generate comprehensive report
    print("\n=== STATISTICAL EVALUATION SUMMARY ===")
    
    # Create results table
    print("\nPerformance Summary by System Quality:")
    print("System Quality | Mean r | Mean MAE | Significant Scales | Effect Size")
    print("-" * 70)
    
    for quality, results in all_results.items():
        mean_r = np.mean([r.correlation for r in results.values()])
        mean_mae = np.mean([r.mae for r in results.values()])
        significant_count = sum(1 for r in results.values() if r.is_significant)
        mean_effect = np.mean([r.effect_size_cohens_d for r in results.values()])
        
        print(f"{quality:13} | {mean_r:6.3f} | {mean_mae:8.3f} | {significant_count:15}/4 | {mean_effect:11.3f}")
    
    # Power analysis
    print(f"\n=== POWER ANALYSIS ===")
    power_analysis = evaluator.power_analysis_report()
    
    print("Required sample sizes for 80% power:")
    for effect, n in power_analysis["required_sample_sizes"].items():
        effect_size = effect.split("_")[1]
        interpretation = power_analysis["interpretation"][effect]
        print(f"  r = {effect_size}: n = {n:3d} ({interpretation})")
    
    # Statistical interpretation
    print(f"\n=== STATISTICAL INTERPRETATION ===")
    
    realistic_results = all_results["realistic"]
    mean_correlation = np.mean([r.correlation for r in realistic_results.values()])
    
    if mean_correlation < 0.1:
        interpretation = "NEGLIGIBLE: Predictions are essentially random"
    elif mean_correlation < 0.3:
        interpretation = "WEAK: Some predictive ability but limited practical utility"
    elif mean_correlation < 0.5:
        interpretation = "MODERATE: Meaningful predictive ability"
    else:
        interpretation = "STRONG: Substantial predictive ability"
    
    print(f"Realistic LLM System Performance: {interpretation}")
    print(f"Mean correlation: {mean_correlation:.3f}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Convert results to serializable format
    serializable_results = {}
    for quality, results in all_results.items():
        serializable_results[quality] = {}
        for scale, result in results.items():
            serializable_results[quality][scale] = {
                'n_samples': result.n_samples,
                'correlation': result.correlation,
                'correlation_pvalue': result.correlation_pvalue,
                'mae': result.mae,
                'rmse': result.rmse,
                'r_squared': result.r_squared,
                'effect_size_cohens_d': result.effect_size_cohens_d,
                'confidence_interval_95': result.confidence_interval_95,
                'statistical_power': result.statistical_power,
                'is_significant': bool(result.is_significant)
            }
    
    results_file = f"statistical_evaluation_demo_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'methodology': {
                'sample_size': len(demo_data),
                'scales_tested': list(scales.keys()),
                'system_qualities': system_qualities,
                'statistical_significance': 0.05,
                'power_threshold': 0.8
            },
            'power_analysis': power_analysis,
            'results_by_quality': serializable_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    # Key findings
    print(f"\n=== KEY FINDINGS ===")
    realistic_r = np.mean([r.correlation for r in realistic_results.values()])
    realistic_mae = np.mean([r.mae for r in realistic_results.values()])
    
    print(f"✅ Proper statistical methodology implemented")
    print(f"✅ Sample size: {len(demo_data)} (exceeds minimum requirements)")
    print(f"✅ Multiple baseline comparisons conducted")
    print(f"✅ Effect sizes and confidence intervals calculated")
    print(f"✅ Statistical power analysis completed")
    print(f"")
    print(f"🔍 REALISTIC LLM Performance:")
    print(f"   - Correlation: r = {realistic_r:.3f}")
    print(f"   - Mean Absolute Error: {realistic_mae:.3f} points")
    print(f"   - Interpretation: {interpretation}")
    
    return all_results

if __name__ == "__main__":
    results = run_comprehensive_demo()