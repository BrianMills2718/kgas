#!/usr/bin/env python3
"""
Kunst Ground Truth Validation
Uses actual personality self-assessment data from Kunst dataset as ground truth
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr, spearmanr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KunstGroundTruthValidator:
    """Validate predictions against actual Kunst personality assessments."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Map our trait names to Kunst scale names
        self.trait_mapping = {
            'political_orientation': 'political_orientation',  # Political (1-11)
            'conspiracy_mentality': 'conspiracy_score',        # CMQ_1-5 mean
            'science_denialism': 'denialism_score',           # Denialism_1-4 mean  
            'narcissism': 'narcissism_score'                  # Narcissism_1-4 mean
        }
        
        # Load all data
        self.kunst_data = self.load_kunst_validation_data()
        self.baseline_results = self.load_baseline_results()
        self.llm_results = self.load_llm_results()
        
    def load_kunst_validation_data(self) -> Dict:
        """Load Kunst validation dataset with ground truth."""
        kunst_file = Path("/home/brian/projects/Digimons/data/datasets/kunst_dataset/kunst_full_dataset_with_tweets/First degree data/validation_dataset/kunst_validation_dataset.json")
        
        if not kunst_file.exists():
            # Try alternative location
            kunst_file = Path("/home/brian/projects/Digimons/uncertainty_stress_test/kunst_validation_dataset.json")
        
        if not kunst_file.exists():
            logger.error(f"Kunst validation dataset not found at expected locations")
            return {}
        
        with open(kunst_file, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded Kunst data for {len(data.get('users', {}))} users")
        return data
    
    def load_baseline_results(self) -> Dict:
        """Load baseline prediction results."""
        # First check if we have Kunst-specific baseline results
        kunst_baseline = Path("/home/brian/projects/Digimons/uncertainty_stress_test/kunst_bayesian_comparison_results.json")
        
        if kunst_baseline.exists():
            with open(kunst_baseline, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded Kunst-specific baseline results")
            return data
        
        # Otherwise use general baseline
        baseline_file = Path("../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json")
        
        if not baseline_file.exists():
            logger.error(f"Baseline file not found")
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
        llm_file = Path("real_llm_results.json")
        
        if not llm_file.exists():
            logger.warning(f"LLM results file not found")
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
    
    def get_kunst_ground_truth(self, user_id: str) -> Dict[str, float]:
        """Get ground truth scores from Kunst data for a user."""
        
        if not self.kunst_data or 'users' not in self.kunst_data:
            return {}
        
        user_data = self.kunst_data['users'].get(user_id, {})
        if not user_data:
            return {}
        
        profile = user_data.get('psychological_profile', {})
        
        ground_truth = {}
        
        # Map Kunst scales to our trait names
        for our_trait, kunst_scale in self.trait_mapping.items():
            value = profile.get(kunst_scale)
            
            if value is not None:
                # Convert to 1-11 scale if needed
                if our_trait == 'political_orientation':
                    # Already 1-11
                    ground_truth[our_trait] = float(value)
                else:
                    # Other scales might be on different ranges (e.g., 1-7)
                    # For now assume they're comparable
                    ground_truth[our_trait] = float(value)
        
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
        
        # Custom accuracy metrics
        within_1_point = np.mean(np.abs(np.array(predictions) - np.array(ground_truth)) <= 1.0)
        within_2_points = np.mean(np.abs(np.array(predictions) - np.array(ground_truth)) <= 2.0)
        
        # Direction accuracy (high/medium/low classification)
        pred_class = np.array(['low' if p <= 4 else 'medium' if p <= 7 else 'high' for p in predictions])
        true_class = np.array(['low' if t <= 4 else 'medium' if t <= 7 else 'high' for t in ground_truth])
        classification_accuracy = np.mean(pred_class == true_class)
        
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
            "classification_accuracy": classification_accuracy,
            "sample_size": len(predictions)
        }
    
    def validate_method_against_kunst(self, method_name: str, method_results: Dict) -> Dict[str, Any]:
        """Validate a specific method against Kunst ground truth."""
        
        trait_accuracies = {}
        all_predictions = []
        all_ground_truth = []
        
        for trait in self.traits:
            predictions = []
            ground_truth_values = []
            user_ids_matched = []
            
            # Find users with both predictions and ground truth
            for user_id in self.kunst_data.get('users', {}).keys():
                ground_truth = self.get_kunst_ground_truth(user_id)
                
                if (user_id in method_results and 
                    trait in method_results[user_id] and
                    trait in ground_truth):
                    
                    # Get prediction
                    pred_dist = method_results[user_id][trait]
                    pred_value = self.distribution_to_expected_value(pred_dist)
                    predictions.append(pred_value)
                    
                    # Get ground truth
                    true_value = ground_truth[trait]
                    ground_truth_values.append(true_value)
                    user_ids_matched.append(user_id)
                    
                    # Add to overall lists
                    all_predictions.append(pred_value)
                    all_ground_truth.append(true_value)
            
            if predictions:
                accuracy_metrics = self.calculate_accuracy_metrics(predictions, ground_truth_values)
                accuracy_metrics['users_matched'] = user_ids_matched
                trait_accuracies[trait] = accuracy_metrics
            else:
                trait_accuracies[trait] = {"error": "No matching users found"}
        
        # Calculate overall metrics across all traits
        overall_metrics = {}
        if all_predictions:
            overall_metrics = self.calculate_accuracy_metrics(all_predictions, all_ground_truth)
        
        return {
            "method": method_name,
            "trait_accuracies": trait_accuracies,
            "overall_metrics": overall_metrics,
            "total_comparisons": len(all_predictions)
        }
    
    def run_kunst_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation against Kunst ground truth."""
        
        logger.info("Running validation against Kunst ground truth data...")
        
        # Check if we have Kunst data
        if not self.kunst_data or 'users' not in self.kunst_data:
            logger.error("No Kunst validation data available")
            return {"error": "Kunst data not loaded"}
        
        results = {}
        
        # Validate baseline if available
        if self.baseline_results:
            logger.info("Validating baseline method...")
            baseline_validation = self.validate_method_against_kunst(
                "Likelihood Ratio (Baseline)", self.baseline_results)
            results["baseline"] = baseline_validation
        
        # Validate LLM methods if available
        if self.llm_results:
            # Extract method results
            all_methods = {}
            
            # Aggregate results by method across users
            for user_id, user_data in self.llm_results.items():
                for method_name in ["chain_of_thought", "few_shot", "ensemble"]:
                    if method_name in user_data:
                        if method_name not in all_methods:
                            all_methods[method_name] = {}
                        all_methods[method_name][user_id] = user_data[method_name]
            
            # Validate each method
            for method_name, method_data in all_methods.items():
                logger.info(f"Validating {method_name} method...")
                method_validation = self.validate_method_against_kunst(
                    f"Real {method_name.replace('_', ' ').title()} LLM", method_data)
                results[method_name] = method_validation
        
        return results
    
    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate comprehensive validation report."""
        
        report = []
        report.append("="*80)
        report.append("🎯 KUNST GROUND TRUTH VALIDATION RESULTS")
        report.append("="*80)
        report.append("")
        
        # Summary of data
        report.append("📊 VALIDATION DATASET:")
        report.append(f"   Kunst users with ground truth: {len(self.kunst_data.get('users', {}))}")
        report.append("")
        
        # Results by method
        for method_key, method_results in validation_results.items():
            if 'error' in method_results:
                continue
                
            report.append(f"\n{method_results['method'].upper()}:")
            report.append("-" * 50)
            
            overall = method_results.get('overall_metrics', {})
            if overall and 'rmse' in overall:
                report.append(f"   Overall RMSE: {overall['rmse']:.3f}")
                report.append(f"   Overall MAE: {overall['mae']:.3f}")
                report.append(f"   Pearson Correlation: {overall['pearson_correlation']:.3f}")
                report.append(f"   Classification Accuracy: {overall['classification_accuracy']:.3f}")
                report.append(f"   Within 1 point: {overall['accuracy_within_1_point']:.3f}")
                report.append(f"   Within 2 points: {overall['accuracy_within_2_points']:.3f}")
                report.append(f"   Total comparisons: {overall['sample_size']}")
            
            # Trait-specific results
            report.append("\n   By Trait:")
            for trait, metrics in method_results['trait_accuracies'].items():
                if 'error' not in metrics:
                    report.append(f"   - {trait}:")
                    report.append(f"     RMSE: {metrics['rmse']:.3f}, MAE: {metrics['mae']:.3f}")
                    report.append(f"     Correlation: {metrics['pearson_correlation']:.3f}")
                    report.append(f"     Within 1pt: {metrics['accuracy_within_1_point']:.3f}")
                    report.append(f"     Users matched: {metrics['sample_size']}")
        
        return "\n".join(report)


def main():
    """Run Kunst ground truth validation."""
    
    try:
        validator = KunstGroundTruthValidator()
        
        # Run validation
        results = validator.run_kunst_validation()
        
        # Generate report
        report = validator.generate_validation_report(results)
        print(report)
        
        # Save results
        output_file = "kunst_validation_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Kunst validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()