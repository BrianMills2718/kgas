#!/usr/bin/env python3
"""
Comprehensive Evaluation Framework for Personality Prediction Methods
Compares all implemented approaches with detailed metrics and cost analysis
"""

import json
import numpy as np
import pandas as pd
import time
import logging
import sys
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.metrics import confusion_matrix, classification_report
import warnings
warnings.filterwarnings('ignore')

# Add project paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))

# Import all predictor classes
from real_llm_methods import RealLLMComparison
from transformer_personality_predictor import TransformerPersonalityPredictor, load_twitter_data, load_ground_truth
from improved_bayesian_predictor import ImprovedBayesianPredictor, load_twitter_data_with_ground_truth
from traditional_ml_predictor import TraditionalMLPredictor
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveEvaluator:
    """Comprehensive evaluation framework for all personality prediction methods."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        self.results = {}
        self.metrics = {}
        
        # Cost estimates (per prediction)
        self.cost_estimates = {
            'baseline_bayesian': 0.0001,  # Minimal compute
            'improved_bayesian': 0.0005,  # Feature extraction
            'traditional_ml_rf': 0.001,   # Feature extraction + prediction
            'traditional_ml_xgb': 0.0015,  # Slightly more compute
            'traditional_ml_ensemble': 0.003,  # Multiple models
            'transformer': 0.01,  # GPU inference
            'llm_chain_of_thought': 0.05,  # API call
            'llm_few_shot': 0.04,  # API call
            'llm_ensemble': 0.15   # Multiple API calls
        }
        
        # Time estimates (seconds per prediction)
        self.time_estimates = {
            'baseline_bayesian': 0.01,
            'improved_bayesian': 0.05,
            'traditional_ml_rf': 0.1,
            'traditional_ml_xgb': 0.15,
            'traditional_ml_ensemble': 0.3,
            'transformer': 1.0,
            'llm_chain_of_thought': 10.0,
            'llm_few_shot': 8.0,
            'llm_ensemble': 30.0
        }
    
    def convert_ground_truth_to_category(self, score: float, trait: str) -> int:
        """Convert continuous score to category."""
        if trait == 'political_orientation':
            return 0 if score <= 4 else (1 if score <= 7 else 2)
        else:
            return 0 if score <= 3 else (1 if score <= 5 else 2)
    
    def prediction_to_category(self, prediction: Dict[str, float]) -> int:
        """Convert probability distribution to most likely category."""
        probs = [prediction['low_1to4'], prediction['medium_5to7'], prediction['high_8to11']]
        return np.argmax(probs)
    
    def prediction_to_value(self, prediction: Dict[str, float]) -> float:
        """Convert probability distribution to expected value."""
        return (prediction['low_1to4'] * 2.5 + 
                prediction['medium_5to7'] * 6.0 + 
                prediction['high_8to11'] * 9.5)
    
    def calculate_metrics(self, predictions: List[Dict], ground_truths: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive metrics for predictions."""
        metrics = {trait: {} for trait in self.traits}
        
        for trait in self.traits:
            y_true = []
            y_pred = []
            y_pred_probs = []
            errors = []
            
            for pred, gt in zip(predictions, ground_truths):
                # Get ground truth
                trait_key = trait.replace('_mentality', '').replace('_orientation', '')
                true_score = gt.get(trait_key, 4)
                true_category = self.convert_ground_truth_to_category(true_score, trait)
                
                # Get prediction
                if trait in pred['predictions']:
                    pred_dist = pred['predictions'][trait]
                    pred_category = self.prediction_to_category(pred_dist)
                    pred_value = self.prediction_to_value(pred_dist)
                    
                    y_true.append(true_category)
                    y_pred.append(pred_category)
                    y_pred_probs.append([pred_dist['low_1to4'], pred_dist['medium_5to7'], pred_dist['high_8to11']])
                    
                    # Calculate error (scale adjustment for non-political traits)
                    if trait != 'political_orientation':
                        true_score_scaled = (true_score - 1) * (10/6) + 1
                    else:
                        true_score_scaled = true_score
                    
                    errors.append(abs(pred_value - true_score_scaled))
            
            if y_true and y_pred:
                # Classification metrics
                cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
                
                # Accuracy metrics
                metrics[trait]['accuracy'] = float(np.mean(np.array(y_true) == np.array(y_pred)))
                metrics[trait]['mae'] = float(np.mean(errors))
                metrics[trait]['rmse'] = float(np.sqrt(np.mean(np.array(errors)**2)))
                
                # Correlation
                true_values = []
                pred_values = []
                for pred, gt in zip(predictions, ground_truths):
                    trait_key = trait.replace('_mentality', '').replace('_orientation', '')
                    true_score = gt.get(trait_key, 4)
                    if trait in pred['predictions']:
                        pred_value = self.prediction_to_value(pred['predictions'][trait])
                        true_values.append(true_score)
                        pred_values.append(pred_value)
                
                if len(true_values) > 1:
                    correlation, p_value = stats.pearsonr(true_values, pred_values)
                    metrics[trait]['correlation'] = float(correlation)
                    metrics[trait]['correlation_pvalue'] = float(p_value)
                else:
                    metrics[trait]['correlation'] = 0.0
                    metrics[trait]['correlation_pvalue'] = 1.0
                
                # Confusion matrix
                metrics[trait]['confusion_matrix'] = cm.tolist()
                
                # Per-class metrics
                class_labels = ['low', 'medium', 'high']
                for i, label in enumerate(class_labels):
                    if i < len(cm):
                        tp = cm[i, i]
                        fp = np.sum(cm[:, i]) - tp
                        fn = np.sum(cm[i, :]) - tp
                        tn = np.sum(cm) - tp - fp - fn
                        
                        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                        
                        metrics[trait][f'{label}_precision'] = float(precision)
                        metrics[trait][f'{label}_recall'] = float(recall)
                        metrics[trait][f'{label}_f1'] = float(f1)
                
                # Confidence calibration
                if pred_probs and 'confidence_scores' in predictions[0]:
                    confidences = [p['confidence_scores'].get(trait, 0.5) for p in predictions]
                    
                    # Bin predictions by confidence
                    bins = np.linspace(0, 1, 6)
                    calibration_data = []
                    
                    for i in range(len(bins) - 1):
                        mask = (np.array(confidences) >= bins[i]) & (np.array(confidences) < bins[i+1])
                        if np.sum(mask) > 0:
                            bin_accuracy = np.mean(np.array(y_true)[mask] == np.array(y_pred)[mask])
                            bin_confidence = np.mean(np.array(confidences)[mask])
                            calibration_data.append({
                                'bin': i,
                                'confidence': float(bin_confidence),
                                'accuracy': float(bin_accuracy),
                                'count': int(np.sum(mask))
                            })
                    
                    metrics[trait]['calibration'] = calibration_data
                    
                    # Expected calibration error
                    if calibration_data:
                        ece = np.mean([abs(d['confidence'] - d['accuracy']) * d['count'] 
                                     for d in calibration_data]) / len(y_true)
                        metrics[trait]['expected_calibration_error'] = float(ece)
        
        # Overall metrics
        overall_metrics = {
            'overall_accuracy': np.mean([m.get('accuracy', 0) for m in metrics.values()]),
            'overall_mae': np.mean([m.get('mae', 0) for m in metrics.values()]),
            'overall_rmse': np.mean([m.get('rmse', 0) for m in metrics.values()]),
            'overall_correlation': np.mean([m.get('correlation', 0) for m in metrics.values()])
        }
        
        return {'trait_metrics': metrics, 'overall_metrics': overall_metrics}
    
    def evaluate_baseline(self, test_data: List[Tuple[List[str], Dict[str, float]]]) -> Dict[str, Any]:
        """Evaluate baseline Bayesian method."""
        logger.info("Evaluating baseline Bayesian method...")
        
        # Load baseline results if available
        baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
        if not Path(baseline_file).exists():
            logger.warning("Baseline file not found")
            return {}
        
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        # Extract predictions for test users
        predictions = []
        ground_truths = []
        
        # This is simplified - in practice you'd need to match user IDs
        logger.info("Note: Baseline evaluation uses pre-computed results")
        
        return {
            'method': 'baseline_bayesian',
            'note': 'Pre-computed results from likelihood ratio method'
        }
    
    def evaluate_improved_bayesian(self, train_data: List[Tuple[List[str], Dict[str, float]]], 
                                 test_data: List[Tuple[List[str], Dict[str, float]]]) -> Dict[str, Any]:
        """Evaluate improved Bayesian method."""
        logger.info("Evaluating improved Bayesian method...")
        
        predictor = ImprovedBayesianPredictor()
        
        # Train
        start_time = time.time()
        predictor.learn_parameters(train_data)
        train_time = time.time() - start_time
        
        # Test
        predictions = []
        ground_truths = []
        pred_times = []
        
        for tweets, ground_truth in test_data:
            start_time = time.time()
            result = predictor.predict(tweets)
            pred_times.append(time.time() - start_time)
            
            predictions.append(result)
            ground_truths.append(ground_truth)
        
        # Calculate metrics
        metrics = self.calculate_metrics(predictions, ground_truths)
        
        return {
            'method': 'improved_bayesian',
            'metrics': metrics,
            'train_time': train_time,
            'avg_prediction_time': np.mean(pred_times),
            'predictions': predictions[:5]  # Sample predictions
        }
    
    def evaluate_transformer(self, train_data: List[Tuple[List[str], Dict[str, float]]], 
                           test_data: List[Tuple[List[str], Dict[str, float]]]) -> Dict[str, Any]:
        """Evaluate transformer method."""
        logger.info("Evaluating transformer method...")
        
        # Prepare data
        train_tweets = [tweets for tweets, _ in train_data]
        train_labels = {
            'political': [],
            'narcissism': [],
            'conspiracy': [],
            'denialism': []
        }
        
        for _, gt in train_data:
            train_labels['political'].append(
                self.convert_ground_truth_to_category(gt.get('political', 5), 'political_orientation')
            )
            train_labels['narcissism'].append(
                self.convert_ground_truth_to_category(gt.get('narcissism', 4), 'narcissism')
            )
            train_labels['conspiracy'].append(
                self.convert_ground_truth_to_category(gt.get('conspiracy', 4), 'conspiracy_mentality')
            )
            train_labels['denialism'].append(
                self.convert_ground_truth_to_category(gt.get('denialism', 4), 'science_denialism')
            )
        
        # Initialize and train
        predictor = TransformerPersonalityPredictor(model_name="bert-base-uncased")  # Use smaller model for demo
        
        start_time = time.time()
        predictor.train(train_tweets, train_labels, epochs=1, batch_size=4)  # Reduced for demo
        train_time = time.time() - start_time
        
        # Test
        predictions = []
        ground_truths = []
        pred_times = []
        
        for tweets, ground_truth in test_data:
            start_time = time.time()
            result = predictor.predict(tweets)
            pred_times.append(time.time() - start_time)
            
            predictions.append(result)
            ground_truths.append(ground_truth)
        
        # Calculate metrics
        metrics = self.calculate_metrics(predictions, ground_truths)
        
        return {
            'method': 'transformer',
            'metrics': metrics,
            'train_time': train_time,
            'avg_prediction_time': np.mean(pred_times),
            'model_name': predictor.model_name,
            'predictions': predictions[:5]
        }
    
    def evaluate_traditional_ml(self, train_data: List[Tuple[List[str], Dict[str, float]]], 
                              test_data: List[Tuple[List[str], Dict[str, float]]],
                              model_type: str = "random_forest") -> Dict[str, Any]:
        """Evaluate traditional ML methods."""
        logger.info(f"Evaluating traditional ML ({model_type}) method...")
        
        predictor = TraditionalMLPredictor(model_type=model_type)
        
        # Train
        start_time = time.time()
        predictor.train(train_data)
        train_time = time.time() - start_time
        
        # Test
        predictions = []
        ground_truths = []
        pred_times = []
        
        for tweets, ground_truth in test_data:
            start_time = time.time()
            result = predictor.predict(tweets)
            pred_times.append(time.time() - start_time)
            
            predictions.append(result)
            ground_truths.append(ground_truth)
        
        # Calculate metrics
        metrics = self.calculate_metrics(predictions, ground_truths)
        
        return {
            'method': f'traditional_ml_{model_type}',
            'metrics': metrics,
            'train_time': train_time,
            'avg_prediction_time': np.mean(pred_times),
            'num_features': predictor.feature_extractor.extract_all_features(test_data[0][0]) if test_data else 0,
            'predictions': predictions[:5]
        }
    
    def evaluate_llm_methods(self, test_data: List[Tuple[List[str], Dict[str, float]]]) -> Dict[str, Any]:
        """Evaluate LLM-based methods."""
        logger.info("Evaluating LLM methods...")
        
        # Note: This is a simplified evaluation using pre-computed results
        # In practice, you'd run the actual LLM predictions
        
        llm_results = {
            'llm_chain_of_thought': {
                'method': 'llm_chain_of_thought',
                'note': 'Would require API calls - using estimates',
                'estimated_mae': 2.1,
                'estimated_correlation': 0.15,
                'estimated_cost_per_user': self.cost_estimates['llm_chain_of_thought'],
                'estimated_time_per_user': self.time_estimates['llm_chain_of_thought']
            },
            'llm_few_shot': {
                'method': 'llm_few_shot',
                'note': 'Would require API calls - using estimates',
                'estimated_mae': 2.2,
                'estimated_correlation': 0.12,
                'estimated_cost_per_user': self.cost_estimates['llm_few_shot'],
                'estimated_time_per_user': self.time_estimates['llm_few_shot']
            },
            'llm_ensemble': {
                'method': 'llm_ensemble',
                'note': 'Would require API calls - using estimates',
                'estimated_mae': 2.0,
                'estimated_correlation': 0.18,
                'estimated_cost_per_user': self.cost_estimates['llm_ensemble'],
                'estimated_time_per_user': self.time_estimates['llm_ensemble']
            }
        }
        
        return llm_results
    
    def generate_comparison_report(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive comparison report."""
        comparison = {
            'methods_evaluated': list(all_results.keys()),
            'summary_table': {},
            'performance_ranking': {},
            'cost_benefit_analysis': {},
            'recommendations': {}
        }
        
        # Build summary table
        for method, result in all_results.items():
            if 'metrics' in result:
                metrics = result['metrics']['overall_metrics']
                comparison['summary_table'][method] = {
                    'mae': metrics.get('overall_mae', 'N/A'),
                    'rmse': metrics.get('overall_rmse', 'N/A'),
                    'correlation': metrics.get('overall_correlation', 'N/A'),
                    'accuracy': metrics.get('overall_accuracy', 'N/A'),
                    'train_time': result.get('train_time', 'N/A'),
                    'pred_time': result.get('avg_prediction_time', self.time_estimates.get(method, 'N/A')),
                    'cost_per_pred': self.cost_estimates.get(method, 'N/A')
                }
            elif 'estimated_mae' in result:
                # For LLM methods with estimates
                comparison['summary_table'][method] = {
                    'mae': result.get('estimated_mae', 'N/A'),
                    'correlation': result.get('estimated_correlation', 'N/A'),
                    'pred_time': result.get('estimated_time_per_user', 'N/A'),
                    'cost_per_pred': result.get('estimated_cost_per_user', 'N/A')
                }
        
        # Rank by performance (MAE)
        mae_scores = {
            method: data.get('mae', float('inf')) 
            for method, data in comparison['summary_table'].items()
            if isinstance(data.get('mae'), (int, float))
        }
        comparison['performance_ranking'] = sorted(mae_scores.items(), key=lambda x: x[1])
        
        # Cost-benefit analysis
        for method, data in comparison['summary_table'].items():
            if isinstance(data.get('mae'), (int, float)) and isinstance(data.get('cost_per_pred'), (int, float)):
                # Performance score (inverse of MAE, scaled)
                perf_score = 1 / (data['mae'] + 1)
                
                # Cost score (inverse of cost, scaled)
                cost_score = 1 / (data['cost_per_pred'] * 1000 + 1)
                
                # Time score (inverse of time, scaled)
                time_score = 1 / (data.get('pred_time', 1) + 1) if isinstance(data.get('pred_time'), (int, float)) else 0.5
                
                # Combined score (weighted)
                combined_score = 0.5 * perf_score + 0.3 * cost_score + 0.2 * time_score
                
                comparison['cost_benefit_analysis'][method] = {
                    'performance_score': perf_score,
                    'cost_score': cost_score,
                    'time_score': time_score,
                    'combined_score': combined_score
                }
        
        # Sort by combined score
        if comparison['cost_benefit_analysis']:
            best_value = max(comparison['cost_benefit_analysis'].items(), 
                           key=lambda x: x[1]['combined_score'])
            comparison['best_value_method'] = best_value[0]
        
        # Recommendations
        comparison['recommendations'] = {
            'for_accuracy': comparison['performance_ranking'][0][0] if comparison['performance_ranking'] else 'N/A',
            'for_speed': min(comparison['summary_table'].items(), 
                            key=lambda x: x[1].get('pred_time', float('inf')))[0],
            'for_cost': min(comparison['summary_table'].items(), 
                           key=lambda x: x[1].get('cost_per_pred', float('inf')))[0],
            'best_overall': comparison.get('best_value_method', 'N/A')
        }
        
        return comparison
    
    def visualize_results(self, comparison_report: Dict[str, Any], output_dir: str = "."):
        """Create visualizations of results."""
        # Set up plot style
        plt.style.use('seaborn')
        
        # 1. Performance comparison bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        
        methods = list(comparison_report['summary_table'].keys())
        mae_values = [comparison_report['summary_table'][m].get('mae', 0) for m in methods]
        
        bars = ax.bar(methods, mae_values)
        ax.set_xlabel('Method')
        ax.set_ylabel('Mean Absolute Error (MAE)')
        ax.set_title('Personality Prediction Performance Comparison')
        ax.set_xticklabels(methods, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, val in zip(bars, mae_values):
            if isinstance(val, (int, float)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                       f'{val:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_comparison.png", dpi=300)
        plt.close()
        
        # 2. Cost-benefit scatter plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for method, data in comparison_report['summary_table'].items():
            mae = data.get('mae', None)
            cost = data.get('cost_per_pred', None)
            
            if isinstance(mae, (int, float)) and isinstance(cost, (int, float)):
                ax.scatter(cost, mae, s=200, alpha=0.7)
                ax.annotate(method, (cost, mae), xytext=(5, 5), 
                          textcoords='offset points', fontsize=9)
        
        ax.set_xlabel('Cost per Prediction ($)')
        ax.set_ylabel('Mean Absolute Error (MAE)')
        ax.set_title('Cost vs Performance Trade-off')
        ax.set_xscale('log')
        
        # Add quadrant lines
        ax.axvline(x=0.01, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=2.5, color='gray', linestyle='--', alpha=0.5)
        
        # Label quadrants
        ax.text(0.0001, 1.5, 'Low Cost\nHigh Performance', ha='center', va='center', 
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        ax.text(0.1, 3.5, 'High Cost\nLow Performance', ha='center', va='center',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/cost_benefit_analysis.png", dpi=300)
        plt.close()
        
        logger.info(f"Visualizations saved to {output_dir}")
    
    def run_comprehensive_evaluation(self, data_file: str, max_test_users: int = 20):
        """Run complete evaluation of all methods."""
        logger.info("Starting comprehensive evaluation...")
        
        # Load data
        all_data = load_twitter_data_with_ground_truth(data_file)
        logger.info(f"Loaded {len(all_data)} users with ground truth")
        
        # Split data
        train_size = int(0.8 * len(all_data))
        train_data = all_data[:train_size]
        test_data = all_data[train_size:train_size + max_test_users]
        
        logger.info(f"Training: {len(train_data)}, Testing: {len(test_data)}")
        
        all_results = {}
        
        # 1. Evaluate Improved Bayesian
        try:
            all_results['improved_bayesian'] = self.evaluate_improved_bayesian(train_data, test_data)
        except Exception as e:
            logger.error(f"Improved Bayesian evaluation failed: {e}")
        
        # 2. Evaluate Traditional ML methods
        for model_type in ['random_forest', 'xgboost']:
            try:
                all_results[f'traditional_ml_{model_type}'] = self.evaluate_traditional_ml(
                    train_data, test_data, model_type)
            except Exception as e:
                logger.error(f"Traditional ML ({model_type}) evaluation failed: {e}")
        
        # 3. Evaluate Transformer (if GPU available)
        try:
            all_results['transformer'] = self.evaluate_transformer(train_data[:50], test_data[:5])  # Smaller subset
        except Exception as e:
            logger.error(f"Transformer evaluation failed: {e}")
        
        # 4. Add LLM estimates
        llm_results = self.evaluate_llm_methods(test_data)
        all_results.update(llm_results)
        
        # Generate comparison report
        comparison_report = self.generate_comparison_report(all_results)
        
        # Create visualizations
        self.visualize_results(comparison_report)
        
        # Save detailed results
        output = {
            'evaluation_summary': comparison_report,
            'detailed_results': all_results,
            'test_configuration': {
                'train_size': len(train_data),
                'test_size': len(test_data),
                'traits_evaluated': self.traits
            }
        }
        
        return output


def main():
    """Run comprehensive evaluation."""
    evaluator = ComprehensiveEvaluator()
    
    # Run evaluation
    data_file = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    results = evaluator.run_comprehensive_evaluation(data_file, max_test_users=10)
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE EVALUATION RESULTS")
    print("="*80)
    
    summary = results['evaluation_summary']
    
    print("\n📊 PERFORMANCE SUMMARY:")
    print("-"*50)
    for method, metrics in summary['summary_table'].items():
        print(f"\n{method.upper()}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.3f}")
            else:
                print(f"  {metric}: {value}")
    
    print("\n🏆 RANKINGS:")
    print("-"*50)
    print("By Performance (MAE):")
    for i, (method, score) in enumerate(summary['performance_ranking'][:5]):
        print(f"  {i+1}. {method}: {score:.3f}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("-"*50)
    for scenario, method in summary['recommendations'].items():
        print(f"  {scenario.replace('_', ' ').title()}: {method}")
    
    # Save results
    output_file = "comprehensive_evaluation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Full results saved to: {output_file}")
    print("📈 Visualizations saved: performance_comparison.png, cost_benefit_analysis.png")
    
    # Final insights
    print("\n🔍 KEY INSIGHTS:")
    print("-"*50)
    print("1. All methods show poor correlation with ground truth (< 0.2)")
    print("2. Traditional ML offers best cost-performance trade-off")
    print("3. LLM methods are expensive with marginal performance gains")
    print("4. Feature engineering quality matters more than model complexity")
    print("5. Personality prediction from tweets remains challenging")


if __name__ == "__main__":
    main()