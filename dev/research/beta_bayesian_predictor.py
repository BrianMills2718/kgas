#!/usr/bin/env python3
"""
Beta Distribution Bayesian Updating for Personality Prediction
Adapted from ajosanchez/applied-bayesian-updating for comparison with likelihood ratio approach.

Key differences from your current method:
- Uses Beta distributions for modeling trait probabilities
- Sequential updating with conjugate priors
- Different uncertainty quantification approach
- Compares success/failure rates rather than likelihood ratios
"""

import json
import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BetaParameters:
    """Parameters for Beta distribution."""
    alpha: float
    beta: float
    
    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def variance(self) -> float:
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab * ab * (ab + 1))
    
    @property
    def confidence_interval_95(self) -> Tuple[float, float]:
        dist = stats.beta(self.alpha, self.beta)
        return dist.interval(0.95)

class BetaBayesianPredictor:
    """Beta distribution-based Bayesian personality predictor."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Initialize weak priors for each trait (Beta(1,1) = uniform)
        self.priors = {trait: BetaParameters(alpha=1.0, beta=1.0) for trait in self.traits}
        
        # Population-level priors (will be learned from data)
        self.population_priors = {}
        
        # Individual user posteriors
        self.user_posteriors = {}
    
    def establish_population_priors(self, baseline_results: str) -> Dict[str, BetaParameters]:
        """Learn population-level priors from baseline data using method of moments."""
        with open(baseline_results, 'r') as f:
            data = json.load(f)
        
        trait_values = {trait: [] for trait in self.traits}
        
        # Extract trait values from baseline results
        for user_result in data["individual_results"]:
            user_traits = self.extract_user_trait_values(user_result)
            for trait, value in user_traits.items():
                if value is not None:
                    trait_values[trait].append(value)
        
        # Estimate Beta parameters using method of moments
        for trait in self.traits:
            if len(trait_values[trait]) > 1:
                values = np.array(trait_values[trait])
                
                # Clip values to (0,1) for Beta distribution
                values = np.clip(values, 0.001, 0.999)
                
                sample_mean = np.mean(values)
                sample_var = np.var(values)
                
                # Method of moments for Beta distribution
                if sample_var > 0 and sample_var < sample_mean * (1 - sample_mean):
                    common_factor = sample_mean * (1 - sample_mean) / sample_var - 1
                    alpha = sample_mean * common_factor
                    beta = (1 - sample_mean) * common_factor
                else:
                    # Fallback to weak informative priors
                    alpha = sample_mean * 10
                    beta = (1 - sample_mean) * 10
                
                self.population_priors[trait] = BetaParameters(alpha=alpha, beta=beta)
                logger.info(f"Population prior for {trait}: α={alpha:.2f}, β={beta:.2f}, mean={alpha/(alpha+beta):.3f}")
            else:
                # Use weak prior if insufficient data
                self.population_priors[trait] = BetaParameters(alpha=1.0, beta=1.0)
        
        return self.population_priors
    
    def extract_user_trait_values(self, user_result: Dict) -> Dict[str, float]:
        """Extract single trait values from user result data."""
        user_traits = {}
        
        for trait in self.traits:
            trait_values = []
            
            for chunk_result in user_result["chunk_results"]:
                if chunk_result["success"] and trait in chunk_result["result"]:
                    prob_dist = chunk_result["result"][trait]
                    
                    # Convert probability distribution to single value (expected value)
                    value = (prob_dist.get("low_1to4", 0) * 0.25 + 
                           prob_dist.get("medium_5to7", 0) * 0.6 + 
                           prob_dist.get("high_8to11", 0) * 0.9)
                    trait_values.append(value)
            
            if trait_values:
                user_traits[trait] = np.mean(trait_values)
            else:
                user_traits[trait] = None
        
        return user_traits
    
    def binary_evidence_from_tweets(self, tweets: List[str], trait: str) -> List[int]:
        """Convert tweet content to binary evidence (success/failure) for a trait.
        
        This is a simplified implementation - in practice you'd use NLP to classify tweets.
        """
        evidence = []
        
        # Define keywords for each trait (simplified approach)
        trait_keywords = {
            'political_orientation': ['politics', 'democrat', 'republican', 'liberal', 'conservative', 'election', 'vote'],
            'conspiracy_mentality': ['conspiracy', 'secret', 'cover-up', 'truth', 'lie', 'hidden', 'control'],
            'science_denialism': ['fake', 'hoax', 'deny', 'science', 'research', 'study', 'evidence'],
            'narcissism': ['amazing', 'best', 'perfect', 'superior', 'talent', 'special', 'better']
        }
        
        keywords = trait_keywords.get(trait, [])
        
        for tweet in tweets:
            tweet_lower = tweet.lower()
            # Simple keyword-based classification (1 = evidence for trait, 0 = against)
            keyword_count = sum(1 for keyword in keywords if keyword in tweet_lower)
            evidence.append(1 if keyword_count > 0 else 0)
        
        return evidence
    
    def sequential_bayesian_update(self, user_id: str, trait: str, evidence: List[int]) -> BetaParameters:
        """Perform sequential Bayesian updating with Beta-Binomial conjugacy."""
        
        # Start with population prior for this trait
        if trait in self.population_priors:
            current_alpha = self.population_priors[trait].alpha
            current_beta = self.population_priors[trait].beta
        else:
            current_alpha = 1.0
            current_beta = 1.0
        
        # Sequential update with each piece of evidence
        for evidence_point in evidence:
            if evidence_point == 1:  # Success (evidence for trait)
                current_alpha += 1
            else:  # Failure (evidence against trait)
                current_beta += 1
        
        final_params = BetaParameters(alpha=current_alpha, beta=current_beta)
        
        # Store user's posterior
        if user_id not in self.user_posteriors:
            self.user_posteriors[user_id] = {}
        self.user_posteriors[user_id][trait] = final_params
        
        return final_params
    
    def predict_user_personality(self, user_id: str, tweets: List[str]) -> Dict[str, Dict]:
        """Predict personality for a user using Beta-Bayesian updating."""
        results = {}
        
        for trait in self.traits:
            # Convert tweets to binary evidence
            evidence = self.binary_evidence_from_tweets(tweets, trait)
            
            # Perform Bayesian updating
            posterior = self.sequential_bayesian_update(user_id, trait, evidence)
            
            # Convert to your probability distribution format
            mean_value = posterior.mean
            ci_lower, ci_upper = posterior.confidence_interval_95
            
            # Map continuous value to categorical probabilities
            if mean_value < 0.4:
                prob_dist = {"low_1to4": 0.8, "medium_5to7": 0.2, "high_8to11": 0.0}
            elif mean_value < 0.7:
                prob_dist = {"low_1to4": 0.2, "medium_5to7": 0.8, "high_8to11": 0.0}
            else:
                prob_dist = {"low_1to4": 0.0, "medium_5to7": 0.3, "high_8to11": 0.7}
            
            results[trait] = {
                **prob_dist,
                "beta_mean": mean_value,
                "beta_alpha": posterior.alpha,
                "beta_beta": posterior.beta,
                "confidence_interval": {"lower": ci_lower, "upper": ci_upper},
                "evidence_count": len(evidence),
                "positive_evidence": sum(evidence)
            }
        
        return results
    
    def predict_batch_users(self, users_data: List[Dict]) -> List[Dict]:
        """Predict personality for multiple users."""
        results = []
        
        for user_data in users_data:
            user_id = user_data["user_id"]
            tweets = user_data.get("tweets", [])
            
            if isinstance(tweets[0], dict):
                # Extract text if tweets are objects
                tweet_texts = [tweet.get("text", "") for tweet in tweets]
            else:
                tweet_texts = tweets
            
            prediction = self.predict_user_personality(user_id, tweet_texts)
            
            results.append({
                "user_id": user_id,
                "prediction": prediction,
                "method": "beta_bayesian",
                "tweets_analyzed": len(tweet_texts)
            })
        
        return results
    
    def compare_approaches(self, user_id: str, trait: str) -> Dict:
        """Compare Beta updating vs your likelihood ratio approach."""
        if user_id not in self.user_posteriors or trait not in self.user_posteriors[user_id]:
            return {"error": "No posterior found for user/trait"}
        
        posterior = self.user_posteriors[user_id][trait]
        
        return {
            "method": "beta_bayesian",
            "user_id": user_id,
            "trait": trait,
            "posterior_mean": posterior.mean,
            "posterior_variance": posterior.variance,
            "credible_interval_95": posterior.confidence_interval_95,
            "alpha": posterior.alpha,
            "beta": posterior.beta,
            "interpretation": {
                "high_confidence": posterior.variance < 0.05,
                "evidence_strength": posterior.alpha + posterior.beta - 2,  # Total evidence beyond prior
                "trait_likelihood": "high" if posterior.mean > 0.7 else "medium" if posterior.mean > 0.4 else "low"
            }
        }
    
    def evaluate_against_baseline(self, baseline_file: str, test_data: List[Dict]) -> Dict:
        """Evaluate Beta predictions against baseline likelihood ratio results."""
        # Make Beta predictions
        beta_results = self.predict_batch_users(test_data)
        
        # Load baseline
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        # Calculate comparison metrics
        comparison = {
            "method_comparison": "Beta Bayesian vs Likelihood Ratio",
            "beta_bayesian_results": len(beta_results),
            "baseline_results": len(baseline_data["individual_results"]),
            "methodology_differences": {
                "beta_approach": "Sequential updating with Beta-Binomial conjugacy",
                "baseline_approach": "Likelihood ratio updates with full probability distributions",
                "uncertainty_representation": "Beta distribution vs custom probability distributions",
                "evidence_processing": "Binary evidence vs continuous LLM outputs"
            },
            "computational_differences": {
                "beta_complexity": "O(n) for n pieces of evidence",
                "baseline_complexity": "More complex LLM processing per chunk"
            }
        }
        
        return comparison

def load_sample_twitter_data() -> List[Dict]:
    """Load sample Twitter data for testing."""
    return [
        {
            "user_id": "test_user_1",
            "tweets": [
                "I don't trust the government at all, they're hiding things from us",
                "These scientists don't know what they're talking about",
                "I'm the smartest person in my field, everyone knows it",
                "Politics is all about control and power"
            ]
        },
        {
            "user_id": "test_user_2", 
            "tweets": [
                "I believe in evidence-based policy making",
                "Science has helped us understand the world better",
                "We should listen to experts in their fields",
                "Collaboration is key to solving problems"
            ]
        }
    ]

def main():
    """Example usage of Beta Bayesian predictor."""
    predictor = BetaBayesianPredictor()
    
    # Load sample data
    test_users = load_sample_twitter_data()
    
    # Establish population priors (would use your baseline results file)
    # predictor.establish_population_priors("uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json")
    
    # Make predictions
    logger.info("Making Beta Bayesian predictions...")
    results = predictor.predict_batch_users(test_users)
    
    # Display results
    for result in results:
        logger.info(f"\\nUser: {result['user_id']}")
        for trait, prediction in result["prediction"].items():
            logger.info(f"  {trait}: mean={prediction['beta_mean']:.3f}, "
                       f"α={prediction['beta_alpha']:.1f}, β={prediction['beta_beta']:.1f}")
    
    # Compare approaches
    comparison = predictor.compare_approaches("test_user_1", "conspiracy_mentality")
    logger.info(f"\\nComparison for conspiracy_mentality: {comparison}")
    
    return predictor, results

if __name__ == "__main__":
    main()