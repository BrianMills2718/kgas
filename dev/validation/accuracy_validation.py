#!/usr/bin/env python3
"""
Accuracy Validation: Test if LLM methods actually perform better than baseline
"""

import json
import numpy as np
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr, spearmanr
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccuracyValidator:
    """Validate prediction accuracy against ground truth data."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Load results from all methods
        self.baseline_results = self.load_baseline_results()
        self.llm_results = self.load_llm_results()
        
        # Create synthetic ground truth (since we don't have real ground truth)
        self.ground_truth = self.create_synthetic_ground_truth()
        
    def load_baseline_results(self) -> Dict:
        """Load baseline likelihood ratio results."""
        baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
        
        if not Path(baseline_file).exists():
            logger.error(f"Baseline file not found: {baseline_file}")
            return {}
        
        with open(baseline_file, 'r') as f:
            data = json.load(f)
        
        # Convert to user-centric format
        user_results = {}
        for user_result in data["individual_results"]:
            user_id = user_result["user_id"]
            predictions = {}
            
            for trait in self.traits:
                trait_predictions = []
                for chunk in user_result["chunk_results"]:
                    if chunk["success"] and trait in chunk["result"]:
                        trait_predictions.append(chunk["result"][trait])
                
                if trait_predictions:
                    # Average probability distributions
                    avg_dist = {}
                    for key in ["low_1to4", "medium_5to7", "high_8to11"]:
                        avg_dist[key] = np.mean([pred.get(key, 0) for pred in trait_predictions])
                    predictions[trait] = avg_dist
            
            if predictions:
                user_results[user_id] = predictions
        
        logger.info(f"Loaded baseline results for {len(user_results)} users")
        return user_results
    
    def load_llm_results(self) -> Dict:
        """Load LLM method results."""
        llm_file = "real_llm_results.json"
        
        if not Path(llm_file).exists():
            logger.warning(f"LLM results file not found: {llm_file}")
            return {}
        
        with open(llm_file, 'r') as f:
            data = json.load(f)
        
        # Convert to user-centric format
        user_results = {}
        for result in data["results"]:
            user_id = result["user_id"]
            user_results[user_id] = {
                "baseline": result["baseline"]["predictions"],
                "chain_of_thought": result["real_chain_of_thought"]["predictions"],
                "few_shot": result["real_few_shot"]["predictions"],
                "ensemble": result["real_ensemble"]["predictions"]
            }
        
        logger.info(f"Loaded LLM results for {len(user_results)} users")
        return user_results
    
    def create_synthetic_ground_truth(self) -> Dict[str, Dict[str, float]]:
        """Create synthetic ground truth based on baseline + noise."""
        
        # Find users with both baseline and LLM results
        common_users = set(self.baseline_results.keys()) & set(self.llm_results.keys())
        
        ground_truth = {}
        
        for user_id in common_users:
            user_truth = {}
            
            for trait in self.traits:
                if trait in self.baseline_results[user_id]:
                    baseline_dist = self.baseline_results[user_id][trait]
                    
                    # Convert probability distribution to expected value
                    expected_value = (
                        baseline_dist.get("low_1to4", 0) * 2.5 +
                        baseline_dist.get("medium_5to7", 0) * 6.0 +
                        baseline_dist.get("high_8to11", 0) * 9.5
                    )
                    
                    # Add controlled noise to simulate "true" personality score
                    # Assume baseline is reasonably accurate but not perfect
                    noise = np.random.normal(0, 0.5)  # Small noise
                    true_score = np.clip(expected_value + noise, 1, 11)
                    
                    user_truth[trait] = true_score
            
            if user_truth:
                ground_truth[user_id] = user_truth
        
        logger.info(f"Created ground truth for {len(ground_truth)} users")
        return ground_truth
    
    def distribution_to_expected_value(self, distribution: Dict[str, float]) -> float:
        """Convert probability distribution to expected value."""
        return (
            distribution.get("low_1to4", 0) * 2.5 +
            distribution.get("medium_5to7", 0) * 6.0 +
            distribution.get("high_8to11", 0) * 9.5
        )
    
    def calculate_accuracy_metrics(self, predictions: List[float], ground_truth: List[float]) -> Dict[str, float]:
        """Calculate various accuracy metrics."""
        
        if len(predictions) != len(ground_truth) or len(predictions) == 0:
            return {"error": "Invalid input data"}
        
        # Basic error metrics
        mse = mean_squared_error(ground_truth, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(ground_truth, predictions)
        
        # Correlation metrics
        pearson_r, pearson_p = pearsonr(predictions, ground_truth)
        spearman_r, spearman_p = spearmanr(predictions, ground_truth)
        
        # Custom accuracy metric (percentage within 1 point)
        within_1_point = np.mean(np.abs(np.array(predictions) - np.array(ground_truth)) <= 1.0)
        within_2_points = np.mean(np.abs(np.array(predictions) - np.array(ground_truth)) <= 2.0)
        
        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "pearson_correlation": pearson_r,
            "pearson_p_value": pearson_p,
            "spearman_correlation": spearman_r,
            "spearman_p_value": spearman_p,
            "accuracy_within_1_point": within_1_point,
            "accuracy_within_2_points": within_2_points,
            "sample_size": len(predictions)
        }
    
    def validate_method_accuracy(self, method_name: str, method_results: Dict) -> Dict[str, Any]:
        """Validate accuracy of a specific method against ground truth."""
        
        trait_accuracies = {}
        
        for trait in self.traits:
            predictions = []
            ground_truth_values = []
            
            for user_id in self.ground_truth.keys():
                if (user_id in method_results and 
                    trait in method_results[user_id] and
                    trait in self.ground_truth[user_id]):
                    
                    # Get prediction
                    pred_dist = method_results[user_id][trait]
                    pred_value = self.distribution_to_expected_value(pred_dist)
                    predictions.append(pred_value)
                    
                    # Get ground truth
                    true_value = self.ground_truth[user_id][trait]
                    ground_truth_values.append(true_value)
            
            if predictions:
                accuracy_metrics = self.calculate_accuracy_metrics(predictions, ground_truth_values)
                trait_accuracies[trait] = accuracy_metrics
            else:
                trait_accuracies[trait] = {"error": "No data available"}
        
        return {
            "method": method_name,
            "trait_accuracies": trait_accuracies,
            "overall_metrics": self.calculate_overall_metrics(trait_accuracies)
        }
    
    def calculate_overall_metrics(self, trait_accuracies: Dict) -> Dict[str, float]:
        """Calculate overall metrics across all traits."""
        
        valid_traits = [trait for trait, metrics in trait_accuracies.items() 
                       if "error" not in metrics]
        
        if not valid_traits:
            return {"error": "No valid trait data"}
        
        # Average key metrics across traits
        avg_rmse = np.mean([trait_accuracies[trait]["rmse"] for trait in valid_traits])
        avg_mae = np.mean([trait_accuracies[trait]["mae"] for trait in valid_traits])
        avg_pearson = np.mean([trait_accuracies[trait]["pearson_correlation"] for trait in valid_traits])
        avg_accuracy_1pt = np.mean([trait_accuracies[trait]["accuracy_within_1_point"] for trait in valid_traits])
        avg_accuracy_2pt = np.mean([trait_accuracies[trait]["accuracy_within_2_points"] for trait in valid_traits])
        
        return {
            "average_rmse": avg_rmse,
            "average_mae": avg_mae,
            "average_pearson_correlation": avg_pearson,
            "average_accuracy_within_1_point": avg_accuracy_1pt,
            "average_accuracy_within_2_points": avg_accuracy_2pt,
            "traits_evaluated": len(valid_traits)
        }
    
    def run_accuracy_validation(self) -> Dict[str, Any]:
        """Run comprehensive accuracy validation."""
        
        logger.info("Running accuracy validation against ground truth...")
        
        # Validate baseline method
        baseline_accuracy = self.validate_method_accuracy("Likelihood Ratio (Baseline)", self.baseline_results)
        
        # Validate LLM methods
        method_accuracies = {"baseline": baseline_accuracy}
        
        if self.llm_results:
            # Extract method results from LLM data
            chain_of_thought_results = {}
            few_shot_results = {}
            ensemble_results = {}
            
            for user_id, user_data in self.llm_results.items():
                if "chain_of_thought" in user_data:
                    chain_of_thought_results[user_id] = user_data["chain_of_thought"]
                if "few_shot" in user_data:
                    few_shot_results[user_id] = user_data["few_shot"]
                if "ensemble" in user_data:
                    ensemble_results[user_id] = user_data["ensemble"]
            
            # Validate each LLM method
            if chain_of_thought_results:
                method_accuracies["chain_of_thought"] = self.validate_method_accuracy(
                    "Real Chain-of-Thought LLM", chain_of_thought_results)
            
            if few_shot_results:
                method_accuracies["few_shot"] = self.validate_method_accuracy(
                    "Real Few-Shot LLM", few_shot_results)
            
            if ensemble_results:
                method_accuracies["ensemble"] = self.validate_method_accuracy(
                    "Real Ensemble LLM", ensemble_results)
        
        # Compare methods
        comparison = self.compare_method_accuracies(method_accuracies)
        
        return {
            "method_accuracies": method_accuracies,
            "method_comparison": comparison,
            "ground_truth_info": {
                "users_evaluated": len(self.ground_truth),
                "traits_evaluated": self.traits,
                "creation_method": "baseline_with_controlled_noise"
            }
        }
    
    def compare_method_accuracies(self, method_accuracies: Dict) -> Dict[str, Any]:
        """Compare accuracy metrics between methods."""
        
        comparison = {
            "metric_comparisons": {},
            "best_method_by_metric": {},
            "ranking": {}
        }
        
        # Define key metrics for comparison
        key_metrics = ["average_rmse", "average_mae", "average_pearson_correlation", 
                      "average_accuracy_within_1_point", "average_accuracy_within_2_points"]
        
        for metric in key_metrics:
            metric_values = {}
            
            for method_name, method_data in method_accuracies.items():
                overall_metrics = method_data.get("overall_metrics", {})
                if metric in overall_metrics and "error" not in overall_metrics:
                    metric_values[method_name] = overall_metrics[metric]
            
            if metric_values:
                comparison["metric_comparisons"][metric] = metric_values
                
                # Determine best method (lower is better for error metrics, higher for correlation/accuracy)
                if "rmse" in metric or "mae" in metric:
                    best_method = min(metric_values.items(), key=lambda x: x[1])
                else:
                    best_method = max(metric_values.items(), key=lambda x: x[1])
                
                comparison["best_method_by_metric"][metric] = {
                    "method": best_method[0],
                    "value": best_method[1]
                }
        
        # Overall ranking based on accuracy within 1 point
        if "average_accuracy_within_1_point" in comparison["metric_comparisons"]:
            accuracy_ranking = sorted(
                comparison["metric_comparisons"]["average_accuracy_within_1_point"].items(),
                key=lambda x: x[1], reverse=True
            )
            comparison["ranking"]["by_accuracy_within_1_point"] = accuracy_ranking
        
        return comparison
    
    def calculate_cost_effectiveness(self, method_accuracies: Dict, processing_times: Dict) -> Dict[str, Any]:
        """Calculate cost-effectiveness metrics."""
        
        cost_effectiveness = {}
        
        # Define relative costs (baseline = 1.0)
        relative_costs = {
            "baseline": 1.0,
            "chain_of_thought": 372.5,  # 37.25s vs 0.1s baseline
            "few_shot": 235.6,  # 23.56s vs 0.1s baseline  
            "ensemble": 531.3   # 53.13s vs 0.1s baseline
        }
        
        for method_name, method_data in method_accuracies.items():
            overall_metrics = method_data.get("overall_metrics", {})
            
            if "error" not in overall_metrics and method_name in relative_costs:
                accuracy = overall_metrics.get("average_accuracy_within_1_point", 0)
                cost = relative_costs[method_name]
                
                cost_effectiveness[method_name] = {
                    "accuracy": accuracy,
                    "relative_cost": cost,
                    "accuracy_per_cost": accuracy / cost if cost > 0 else 0,
                    "cost_for_1_percent_accuracy": cost / (accuracy * 100) if accuracy > 0 else float('inf')
                }
        
        return cost_effectiveness


def main():
    """Run accuracy validation and comparison."""
    
    try:
        validator = AccuracyValidator()
        
        # Run comprehensive validation
        results = validator.run_accuracy_validation()
        
        print("\n" + "="*80)
        print("🎯 ACCURACY VALIDATION RESULTS")
        print("="*80)
        
        # Display method comparison
        comparison = results["method_comparison"]
        
        print("\n📊 ACCURACY COMPARISON BY METHOD:")
        if "ranking" in comparison and "by_accuracy_within_1_point" in comparison["ranking"]:
            ranking = comparison["ranking"]["by_accuracy_within_1_point"]
            for i, (method, accuracy) in enumerate(ranking):
                print(f"   {i+1}. {method:25}: {accuracy:.3f} (within 1 point)")
        
        print("\n🏆 BEST METHOD BY METRIC:")
        for metric, best_data in comparison.get("best_method_by_metric", {}).items():
            print(f"   {metric:30}: {best_data['method']} ({best_data['value']:.3f})")
        
        print("\n📈 DETAILED ACCURACY METRICS:")
        for method_name, method_data in results["method_accuracies"].items():
            overall = method_data.get("overall_metrics", {})
            if "error" not in overall:
                print(f"\n   {method_data['method'].upper()}:")
                print(f"     RMSE: {overall.get('average_rmse', 0):.3f}")
                print(f"     MAE:  {overall.get('average_mae', 0):.3f}")
                print(f"     Pearson Correlation: {overall.get('average_pearson_correlation', 0):.3f}")
                print(f"     Accuracy (±1 point): {overall.get('average_accuracy_within_1_point', 0):.3f}")
                print(f"     Accuracy (±2 points): {overall.get('average_accuracy_within_2_points', 0):.3f}")
        
        # Calculate cost-effectiveness
        processing_times = {
            "baseline": 0.0001,
            "chain_of_thought": 37.25,
            "few_shot": 23.56,
            "ensemble": 53.13
        }
        
        cost_effectiveness = validator.calculate_cost_effectiveness(
            results["method_accuracies"], processing_times)
        
        print("\n💰 COST-EFFECTIVENESS ANALYSIS:")
        for method, metrics in cost_effectiveness.items():
            print(f"\n   {method.upper()}:")
            print(f"     Accuracy: {metrics['accuracy']:.3f}")
            print(f"     Relative Cost: {metrics['relative_cost']:.1f}x")
            print(f"     Accuracy per Cost: {metrics['accuracy_per_cost']:.6f}")
            print(f"     Cost for 1% Accuracy: {metrics['cost_for_1_percent_accuracy']:.1f}x")
        
        # Save detailed results
        output_file = "accuracy_validation_results.json"
        with open(output_file, 'w') as f:
            json.dump({
                **results,
                "cost_effectiveness": cost_effectiveness
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        # Generate summary conclusion
        print("\n🎯 ACCURACY VALIDATION CONCLUSION:")
        
        if "ranking" in comparison and "by_accuracy_within_1_point" in comparison["ranking"]:
            best_method, best_accuracy = comparison["ranking"]["by_accuracy_within_1_point"][0]
            baseline_accuracy = next((acc for method, acc in comparison["ranking"]["by_accuracy_within_1_point"] 
                                    if "baseline" in method.lower()), None)
            
            if baseline_accuracy is not None:
                improvement = best_accuracy - baseline_accuracy
                if improvement > 0.05:  # 5% improvement threshold
                    print(f"   ✅ {best_method} shows meaningful improvement: +{improvement:.3f} accuracy")
                elif improvement > 0:
                    print(f"   ⚠️  {best_method} shows marginal improvement: +{improvement:.3f} accuracy")
                else:
                    print(f"   ❌ No LLM method beats baseline (best: {best_method}, {improvement:+.3f})")
                
                # Cost analysis
                if best_method in cost_effectiveness and "baseline" in [m.lower() for m in cost_effectiveness.keys()]:
                    best_cost_effectiveness = cost_effectiveness[best_method]["accuracy_per_cost"]
                    baseline_cost_effectiveness = cost_effectiveness.get("baseline", {}).get("accuracy_per_cost", 0)
                    
                    if baseline_cost_effectiveness > 0:
                        cost_ratio = baseline_cost_effectiveness / best_cost_effectiveness
                        print(f"   💸 Cost-effectiveness: Baseline is {cost_ratio:.0f}x more cost-effective")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Accuracy validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()