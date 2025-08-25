#!/usr/bin/env python3
"""
Statistical Evaluation Framework for Personality Prediction

Expert statistician approach to properly evaluate LLM-based personality inference.
Implements rigorous statistical methodology with proper sample sizes, 
cross-validation, significance testing, and effect size calculations.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from scipy import stats
from scipy.stats import pearsonr, spearmanr, ttest_ind, bootstrap
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@dataclass
class StatisticalTestResult:
    """Statistical test result with all relevant metrics"""
    n_samples: int
    correlation: float
    correlation_pvalue: float
    mae: float
    rmse: float
    r_squared: float
    effect_size_cohens_d: float
    confidence_interval_95: Tuple[float, float]
    statistical_power: float
    is_significant: bool
    baseline_comparison: Dict[str, float]

@dataclass 
class PersonalityScale:
    """Personality scale definition with statistical properties"""
    name: str
    trait_key: str
    min_value: int
    max_value: int
    expected_variance: float
    population_mean: Optional[float] = None
    population_std: Optional[float] = None

class StatisticalEvaluator:
    """Expert statistical evaluation of personality prediction systems"""
    
    def __init__(self, alpha: float = 0.05, power_threshold: float = 0.8):
        self.alpha = alpha
        self.power_threshold = power_threshold
        
        # Define personality scales with realistic statistical properties
        self.scales = [
            PersonalityScale("Political Orientation", "political", 1, 7, 2.0, 4.0, 1.5),
            PersonalityScale("Narcissism", "narcissism", 1, 7, 1.5, 3.5, 1.2),
            PersonalityScale("Conspiracy Mentality", "conspiracy", 1, 7, 2.5, 3.0, 1.6),
            PersonalityScale("Climate Denialism", "denialism", 1, 7, 3.0, 2.5, 1.8)
        ]
        
    def calculate_required_sample_size(self, effect_size: float = 0.3, 
                                     power: float = 0.8, alpha: float = 0.05) -> int:
        """
        Calculate minimum sample size for detecting meaningful effects.
        
        For correlation studies, using Cohen's convention:
        - Small effect: r = 0.1 (Cohen's d ≈ 0.2)
        - Medium effect: r = 0.3 (Cohen's d ≈ 0.6) 
        - Large effect: r = 0.5 (Cohen's d ≈ 1.0)
        """
        # Convert correlation to z-score using Fisher transformation
        z_alpha = stats.norm.ppf(1 - alpha/2)
        z_beta = stats.norm.ppf(power)
        
        # For correlation, sample size formula
        r = effect_size
        z_r = 0.5 * np.log((1 + r) / (1 - r))  # Fisher z-transformation
        
        # Sample size calculation for correlation
        n = ((z_alpha + z_beta) / z_r) ** 2 + 3
        
        return max(int(np.ceil(n)), 30)  # Minimum 30 for CLT
    
    def create_baseline_models(self, y_true: np.ndarray) -> Dict[str, Any]:
        """Create baseline models for comparison"""
        n_samples = len(y_true)
        
        # Random baseline (uniform distribution within scale range)
        scale_min, scale_max = int(np.min(y_true)), int(np.max(y_true))
        random_predictions = np.random.uniform(scale_min, scale_max, n_samples)
        
        # Mean baseline (always predict the mean)
        mean_predictions = np.full(n_samples, np.mean(y_true))
        
        # Simple heuristic baseline (predict based on simple rule)
        # E.g., predict slightly above/below mean based on some simple pattern
        heuristic_predictions = np.where(
            np.arange(n_samples) % 2 == 0, 
            np.mean(y_true) + 0.5,
            np.mean(y_true) - 0.5
        )
        heuristic_predictions = np.clip(heuristic_predictions, scale_min, scale_max)
        
        return {
            "random": random_predictions,
            "mean": mean_predictions, 
            "simple_heuristic": heuristic_predictions
        }
    
    def calculate_effect_size(self, y_true: np.ndarray, y_pred: np.ndarray,
                            baseline_pred: np.ndarray) -> float:
        """Calculate Cohen's d effect size comparing prediction to baseline"""
        
        # Calculate residuals
        system_errors = y_true - y_pred
        baseline_errors = y_true - baseline_pred
        
        # Cohen's d = (mean1 - mean2) / pooled_std
        mean_diff = np.mean(np.abs(baseline_errors)) - np.mean(np.abs(system_errors))
        pooled_std = np.sqrt((np.var(baseline_errors) + np.var(system_errors)) / 2)
        
        if pooled_std == 0:
            return 0.0
            
        return mean_diff / pooled_std
    
    def bootstrap_confidence_interval(self, y_true: np.ndarray, y_pred: np.ndarray,
                                    metric_func: callable, n_bootstrap: int = 1000,
                                    confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for any metric"""
        
        def bootstrap_metric(indices):
            return metric_func(y_true[indices], y_pred[indices])
        
        # Bootstrap sampling
        n_samples = len(y_true)
        bootstrap_scores = []
        
        np.random.seed(42)  # For reproducibility
        for _ in range(n_bootstrap):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            score = bootstrap_metric(indices)
            bootstrap_scores.append(score)
        
        # Calculate percentiles
        alpha = (1 - confidence_level) / 2
        lower_percentile = alpha * 100
        upper_percentile = (1 - alpha) * 100
        
        ci_lower = np.percentile(bootstrap_scores, lower_percentile)
        ci_upper = np.percentile(bootstrap_scores, upper_percentile)
        
        return (ci_lower, ci_upper)
    
    def calculate_statistical_power(self, effect_size: float, n_samples: int,
                                  alpha: float = 0.05) -> float:
        """Calculate achieved statistical power given effect size and sample size"""
        
        # For correlation studies
        z_alpha = stats.norm.ppf(1 - alpha/2)
        
        # Convert effect size to z-score
        r = effect_size
        z_r = 0.5 * np.log((1 + r) / (1 - r))  # Fisher z-transformation
        
        # Calculate power
        z_beta = z_r * np.sqrt(n_samples - 3) - z_alpha
        power = stats.norm.cdf(z_beta)
        
        return max(0.0, min(1.0, power))
    
    def cross_validate_predictions(self, prediction_func: callable, 
                                 X: List[Dict], y: np.ndarray,
                                 cv_folds: int = 5) -> Dict[str, float]:
        """Perform cross-validation evaluation"""
        
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        cv_scores = {
            'mae': [],
            'rmse': [],
            'correlation': [],
            'r_squared': []
        }
        
        for train_idx, test_idx in kf.split(X):
            # Split data
            X_train = [X[i] for i in train_idx]
            X_test = [X[i] for i in test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Make predictions on test set
            y_pred = []
            for user_data in X_test:
                pred = prediction_func(user_data)
                y_pred.append(pred)
            
            y_pred = np.array(y_pred)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            correlation, _ = pearsonr(y_test, y_pred)
            r_squared = r2_score(y_test, y_pred)
            
            cv_scores['mae'].append(mae)
            cv_scores['rmse'].append(rmse) 
            cv_scores['correlation'].append(correlation)
            cv_scores['r_squared'].append(r_squared)
        
        # Return mean and std of CV scores
        return {
            'mae_mean': np.mean(cv_scores['mae']),
            'mae_std': np.std(cv_scores['mae']),
            'rmse_mean': np.mean(cv_scores['rmse']),
            'rmse_std': np.std(cv_scores['rmse']),
            'correlation_mean': np.mean(cv_scores['correlation']),
            'correlation_std': np.std(cv_scores['correlation']),
            'r_squared_mean': np.mean(cv_scores['r_squared']),
            'r_squared_std': np.std(cv_scores['r_squared'])
        }
    
    def evaluate_prediction_system(self, y_true: np.ndarray, y_pred: np.ndarray,
                                 scale: PersonalityScale) -> StatisticalTestResult:
        """Comprehensive statistical evaluation of prediction system"""
        
        n_samples = len(y_true)
        
        # Basic metrics
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r_squared = r2_score(y_true, y_pred)
        
        # Correlation analysis
        correlation, correlation_pvalue = pearsonr(y_true, y_pred)
        
        # Create baseline models
        baselines = self.create_baseline_models(y_true)
        
        # Compare to baselines
        baseline_comparison = {}
        for baseline_name, baseline_pred in baselines.items():
            baseline_mae = mean_absolute_error(y_true, baseline_pred)
            baseline_comparison[f"{baseline_name}_mae"] = baseline_mae
            baseline_comparison[f"improvement_over_{baseline_name}"] = (baseline_mae - mae) / baseline_mae
        
        # Effect size calculation (vs random baseline)
        effect_size = self.calculate_effect_size(y_true, y_pred, baselines["random"])
        
        # Confidence interval for correlation
        correlation_ci = self.bootstrap_confidence_interval(
            y_true, y_pred, lambda x, y: pearsonr(x, y)[0]
        )
        
        # Statistical power
        statistical_power = self.calculate_statistical_power(abs(correlation), n_samples)
        
        # Significance test
        is_significant = correlation_pvalue < self.alpha
        
        return StatisticalTestResult(
            n_samples=n_samples,
            correlation=correlation,
            correlation_pvalue=correlation_pvalue,
            mae=mae,
            rmse=rmse,
            r_squared=r_squared,
            effect_size_cohens_d=effect_size,
            confidence_interval_95=correlation_ci,
            statistical_power=statistical_power,
            is_significant=is_significant,
            baseline_comparison=baseline_comparison
        )
    
    def power_analysis_report(self) -> Dict[str, Any]:
        """Generate power analysis for different effect sizes and sample sizes"""
        
        effect_sizes = [0.1, 0.2, 0.3, 0.5]  # Small, small-medium, medium, large
        sample_sizes = [30, 50, 100, 200, 500]
        
        power_matrix = {}
        required_n = {}
        
        for effect_size in effect_sizes:
            power_matrix[f"effect_{effect_size}"] = {}
            for n in sample_sizes:
                power = self.calculate_statistical_power(effect_size, n)
                power_matrix[f"effect_{effect_size}"][f"n_{n}"] = power
            
            # Calculate required sample size for 80% power
            required_n[f"effect_{effect_size}"] = self.calculate_required_sample_size(effect_size)
        
        return {
            "power_matrix": power_matrix,
            "required_sample_sizes": required_n,
            "interpretation": {
                "effect_0.1": "Small effect (barely detectable)",
                "effect_0.2": "Small-medium effect (psychologically meaningful)",
                "effect_0.3": "Medium effect (practically significant)",
                "effect_0.5": "Large effect (substantial practical importance)"
            }
        }
    
    def generate_statistical_report(self, results: Dict[str, StatisticalTestResult]) -> str:
        """Generate comprehensive statistical report"""
        
        report = "# STATISTICAL EVALUATION REPORT: Personality Prediction\n\n"
        report += "## Executive Summary\n\n"
        
        # Calculate overall metrics
        n_scales = len(results)
        significant_scales = sum(1 for r in results.values() if r.is_significant)
        mean_correlation = np.mean([r.correlation for r in results.values()])
        mean_mae = np.mean([r.mae for r in results.values()])
        
        report += f"- **Scales tested**: {n_scales}\n"
        report += f"- **Statistically significant**: {significant_scales}/{n_scales} ({significant_scales/n_scales*100:.1f}%)\n"
        report += f"- **Mean correlation**: {mean_correlation:.3f}\n"
        report += f"- **Mean MAE**: {mean_mae:.3f}\n\n"
        
        # Detailed results by scale
        report += "## Detailed Results by Scale\n\n"
        
        for scale_name, result in results.items():
            report += f"### {scale_name}\n\n"
            report += f"- **Sample size**: {result.n_samples}\n"
            report += f"- **Correlation**: {result.correlation:.3f} (p = {result.correlation_pvalue:.4f})\n"
            report += f"- **95% CI**: [{result.confidence_interval_95[0]:.3f}, {result.confidence_interval_95[1]:.3f}]\n"
            report += f"- **MAE**: {result.mae:.3f}\n"
            report += f"- **RMSE**: {result.rmse:.3f}\n"
            report += f"- **R²**: {result.r_squared:.3f}\n"
            report += f"- **Effect size (Cohen's d)**: {result.effect_size_cohens_d:.3f}\n"
            report += f"- **Statistical power**: {result.statistical_power:.3f}\n"
            report += f"- **Statistically significant**: {'Yes' if result.is_significant else 'No'}\n\n"
            
            # Baseline comparison
            report += "#### Baseline Comparisons:\n"
            for baseline, value in result.baseline_comparison.items():
                if "improvement" in baseline:
                    report += f"- {baseline}: {value:.1%}\n"
            report += "\n"
        
        # Interpretation
        report += "## Statistical Interpretation\n\n"
        
        if mean_correlation < 0.1:
            interpretation = "**Negligible correlation** - predictions are essentially random"
        elif mean_correlation < 0.3:
            interpretation = "**Weak correlation** - some predictive ability but limited practical utility"
        elif mean_correlation < 0.5:
            interpretation = "**Moderate correlation** - meaningful predictive ability"
        else:
            interpretation = "**Strong correlation** - substantial predictive ability"
            
        report += f"{interpretation}\n\n"
        
        # Power analysis summary
        power_analysis = self.power_analysis_report()
        report += "## Power Analysis\n\n"
        report += "Required sample sizes for 80% power:\n"
        for effect, n in power_analysis["required_sample_sizes"].items():
            effect_size = effect.split("_")[1]
            report += f"- Effect size {effect_size}: n = {n}\n"
        
        return report

def main():
    """Run statistical evaluation framework demo"""
    
    print("=== STATISTICAL EVALUATION FRAMEWORK ===")
    print("Expert statistician approach to personality prediction evaluation")
    
    evaluator = StatisticalEvaluator()
    
    # Generate power analysis
    print("\n--- Power Analysis ---")
    power_analysis = evaluator.power_analysis_report()
    
    print("Required sample sizes for 80% statistical power:")
    for effect, n in power_analysis["required_sample_sizes"].items():
        effect_size = effect.split("_")[1] 
        print(f"  Effect size {effect_size}: n = {n}")
    
    print(f"\nMinimum recommended sample size: {max(power_analysis['required_sample_sizes'].values())}")
    
    # Demo with simulated data
    print("\n--- Demo with Simulated Data ---")
    np.random.seed(42)
    
    n_samples = 100
    true_correlation = 0.3  # Medium effect size
    
    # Simulate realistic personality data
    y_true = np.random.normal(4.0, 1.5, n_samples)  # Political orientation
    y_true = np.clip(y_true, 1, 7)  # Clip to scale range
    
    # Simulate predictions with some correlation to truth
    noise = np.random.normal(0, 1, n_samples)
    y_pred = true_correlation * y_true + (1 - true_correlation) * noise + np.random.normal(4.0, 0.5, n_samples)
    y_pred = np.clip(y_pred, 1, 7)
    
    # Evaluate
    scale = PersonalityScale("Political Orientation", "political", 1, 7, 2.0, 4.0, 1.5)
    result = evaluator.evaluate_prediction_system(y_true, y_pred, scale)
    
    # Generate report
    results = {"Political Orientation": result}
    report = evaluator.generate_statistical_report(results)
    
    print(f"\nSample evaluation result:")
    print(f"  Correlation: {result.correlation:.3f} (p = {result.correlation_pvalue:.4f})")
    print(f"  MAE: {result.mae:.3f}")
    print(f"  Effect size: {result.effect_size_cohens_d:.3f}")
    print(f"  Statistical power: {result.statistical_power:.3f}")
    print(f"  Significant: {result.is_significant}")
    
    # Save framework for use
    with open("statistical_framework_demo.md", "w") as f:
        f.write(report)
    
    print(f"\n✅ Statistical evaluation framework ready")
    print(f"   Next step: Apply to real personality prediction system with n≥100")

if __name__ == "__main__":
    main()