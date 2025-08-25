#!/usr/bin/env python3
"""
Working Real Method Comparison - No Dependencies
Uses available data and basic implementations without external packages.
"""

import json
import numpy as np
import time
import re
from typing import Dict, List, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingRealComparison:
    """Working comparison using available data and basic implementations."""
    
    def __init__(self, baseline_file: str):
        self.baseline_file = baseline_file
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Load baseline data
        with open(baseline_file, 'r') as f:
            self.baseline_data = json.load(f)
        
        # Load Twitter data
        self.twitter_data = self.load_twitter_data()
        
        logger.info(f"Loaded {len(self.twitter_data)} users with Twitter data")
    
    def load_twitter_data(self) -> Dict[str, List[str]]:
        """Load actual Twitter data from available sources."""
        twitter_data = {}
        
        # Try loading from available sources
        data_files = [
            "../uncertainty_stress_test/100_users_500tweets_dataset.json",
            "../uncertainty_stress_test/high_volume_500tweet_dataset.json"
        ]
        
        for file_path in data_files:
            if Path(file_path).exists():
                logger.info(f"Loading Twitter data from: {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for user_data in data:
                        user_id = user_data["user_info"]["twitter_id"]
                        tweets = []
                        
                        for tweet in user_data.get("tweets", []):
                            text = tweet.get("text", "").strip()
                            if text and len(text) > 10:
                                tweets.append(text)
                        
                        if len(tweets) >= 5:  # Only include users with sufficient tweets
                            twitter_data[user_id] = tweets
                    
                    logger.info(f"Loaded {len(twitter_data)} users from {file_path}")
                    break
                    
                except Exception as e:
                    logger.warning(f"Failed to load {file_path}: {e}")
        
        return twitter_data
    
    def extract_baseline_results(self, user_id: str) -> Dict[str, Any]:
        """Extract baseline results for a user."""
        for user_result in self.baseline_data["individual_results"]:
            if user_result["user_id"] == user_id:
                predictions = {}
                confidence_scores = {}
                
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
                        
                        # Calculate confidence
                        probs = list(avg_dist.values())
                        entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
                        confidence_scores[trait] = 1 - (entropy / np.log(3))
                
                return {
                    "predictions": predictions,
                    "confidence_scores": confidence_scores,
                    "method": "Likelihood Ratio (Baseline)"
                }
        
        return None
    
    def simple_bert_prediction(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Simple BERT-style prediction using keyword analysis."""
        # Combine all tweets
        combined_text = " ".join(tweets).lower()
        
        predictions = {}
        confidence_scores = {}
        
        # Define trait-specific keywords and scoring
        trait_analysis = {
            'political_orientation': {
                'keywords': ['politics', 'government', 'election', 'democrat', 'republican', 'conservative', 'liberal'],
                'positive': ['democrat', 'liberal', 'progressive', 'left'],
                'negative': ['republican', 'conservative', 'trump', 'right']
            },
            'conspiracy_mentality': {
                'keywords': ['conspiracy', 'truth', 'hidden', 'secret', 'lies', 'fake', 'hoax', 'cover'],
                'positive': ['conspiracy', 'truth', 'hidden', 'secret', 'lies', 'fake', 'hoax'],
                'negative': ['facts', 'evidence', 'science', 'research', 'verified']
            },
            'science_denialism': {
                'keywords': ['science', 'research', 'study', 'evidence', 'vaccine', 'climate', 'expert'],
                'positive': ['fake', 'hoax', 'unproven', 'natural', 'alternative'],
                'negative': ['science', 'research', 'study', 'evidence', 'peer-reviewed']
            },
            'narcissism': {
                'keywords': ['i am', 'my', 'me', 'myself', 'amazing', 'best', 'perfect', 'brilliant'],
                'positive': ['amazing', 'best', 'perfect', 'superior', 'exceptional', 'brilliant'],
                'negative': ['humble', 'modest', 'team', 'together', 'help', 'sorry']
            }
        }
        
        for trait in self.traits:
            analysis = trait_analysis[trait]
            
            # Count keyword occurrences
            keyword_count = sum(1 for keyword in analysis['keywords'] if keyword in combined_text)
            positive_count = sum(1 for keyword in analysis['positive'] if keyword in combined_text)
            negative_count = sum(1 for keyword in analysis['negative'] if keyword in combined_text)
            
            # Count first-person pronouns for narcissism
            if trait == 'narcissism':
                first_person_count = combined_text.count(' i ') + combined_text.count('my ') + combined_text.count(' me ')
                positive_count += first_person_count // 3
            
            # Calculate score
            if keyword_count == 0:
                # No relevant content
                predictions[trait] = {"low_1to4": 0.6, "medium_5to7": 0.3, "high_8to11": 0.1}
                confidence_scores[trait] = 0.3
            else:
                # Score based on positive vs negative indicators
                net_score = positive_count - negative_count
                total_evidence = positive_count + negative_count
                
                if net_score > 1:
                    predictions[trait] = {"low_1to4": 0.1, "medium_5to7": 0.3, "high_8to11": 0.6}
                    confidence_scores[trait] = 0.8
                elif net_score < -1:
                    predictions[trait] = {"low_1to4": 0.7, "medium_5to7": 0.25, "high_8to11": 0.05}
                    confidence_scores[trait] = 0.7
                else:
                    predictions[trait] = {"low_1to4": 0.3, "medium_5to7": 0.6, "high_8to11": 0.1}
                    confidence_scores[trait] = 0.6
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "BERT-style (keyword analysis)"
        }
    
    def beta_bayesian_prediction(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Beta-Bayesian prediction using statistical updating."""
        predictions = {}
        confidence_scores = {}
        
        # Population priors learned from baseline data
        population_priors = {
            'political_orientation': {'alpha': 2.55, 'beta': 1.90},
            'conspiracy_mentality': {'alpha': 3.23, 'beta': 4.16},
            'science_denialism': {'alpha': 3.19, 'beta': 4.61},
            'narcissism': {'alpha': 4.72, 'beta': 5.67}
        }
        
        for trait in self.traits:
            # Start with population prior
            alpha = population_priors[trait]['alpha']
            beta = population_priors[trait]['beta']
            
            # Extract evidence from tweets
            evidence_scores = self.extract_evidence_scores(tweets, trait)
            
            # Update parameters based on evidence
            for score in evidence_scores:
                if score > 0.6:  # Positive evidence
                    alpha += 1
                elif score < 0.4:  # Negative evidence  
                    beta += 1
                # Neutral evidence (0.4-0.6) doesn't update
            
            # Calculate posterior statistics
            mean_value = alpha / (alpha + beta)
            variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
            
            # Convert to probability distribution
            if mean_value < 0.4:
                predictions[trait] = {"low_1to4": 0.8, "medium_5to7": 0.2, "high_8to11": 0.0}
            elif mean_value < 0.7:
                predictions[trait] = {"low_1to4": 0.2, "medium_5to7": 0.8, "high_8to11": 0.0}
            else:
                predictions[trait] = {"low_1to4": 0.0, "medium_5to7": 0.2, "high_8to11": 0.8}
            
            # Confidence based on inverse variance
            confidence_scores[trait] = 1 - variance
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "Beta-Bayesian updating",
            "additional_info": {
                "evidence_count": len(tweets),
                "updates_made": sum(1 for scores in [self.extract_evidence_scores(tweets, t) for t in self.traits] for s in scores if s != 0.5)
            }
        }
    
    def extract_evidence_scores(self, tweets: List[str], trait: str) -> List[float]:
        """Extract evidence scores for a trait from tweets."""
        evidence_scores = []
        
        for tweet in tweets:
            tweet_lower = tweet.lower()
            
            if trait == 'political_orientation':
                political_words = ['politics', 'government', 'election']
                if any(word in tweet_lower for word in political_words):
                    left_words = ['democrat', 'liberal', 'progressive']
                    right_words = ['republican', 'conservative', 'trump']
                    if any(word in tweet_lower for word in left_words):
                        evidence_scores.append(0.7)
                    elif any(word in tweet_lower for word in right_words):
                        evidence_scores.append(0.3)
                    else:
                        evidence_scores.append(0.5)
            
            elif trait == 'conspiracy_mentality':
                conspiracy_words = ['conspiracy', 'truth', 'hidden', 'secret', 'fake', 'hoax']
                rational_words = ['facts', 'evidence', 'verified', 'science']
                if any(word in tweet_lower for word in conspiracy_words):
                    evidence_scores.append(0.8)
                elif any(word in tweet_lower for word in rational_words):
                    evidence_scores.append(0.2)
                else:
                    evidence_scores.append(0.5)
            
            elif trait == 'science_denialism':
                anti_science = ['fake science', 'hoax', 'unproven', 'so-called experts']
                pro_science = ['research shows', 'study finds', 'evidence suggests']
                if any(phrase in tweet_lower for phrase in anti_science):
                    evidence_scores.append(0.8)
                elif any(phrase in tweet_lower for phrase in pro_science):
                    evidence_scores.append(0.2)
                else:
                    evidence_scores.append(0.5)
            
            elif trait == 'narcissism':
                narcissistic_words = ['amazing', 'best', 'perfect', 'brilliant', 'exceptional']
                humble_words = ['humble', 'modest', 'sorry', 'help', 'team']
                self_references = tweet_lower.count(' i ') + tweet_lower.count('my ')
                
                if any(word in tweet_lower for word in narcissistic_words) or self_references > 3:
                    evidence_scores.append(0.7)
                elif any(word in tweet_lower for word in humble_words):
                    evidence_scores.append(0.3)
                else:
                    evidence_scores.append(0.5)
        
        return evidence_scores
    
    def calculate_agreement(self, predictions_list: List[Dict]) -> Dict[str, float]:
        """Calculate agreement between methods."""
        agreement_scores = {}
        
        for trait in self.traits:
            values = []
            for pred_dict in predictions_list:
                if trait in pred_dict["predictions"]:
                    dist = pred_dict["predictions"][trait]
                    value = (dist.get("low_1to4", 0) * 2.5 + 
                           dist.get("medium_5to7", 0) * 6.0 + 
                           dist.get("high_8to11", 0) * 9.5)
                    values.append(value)
            
            if len(values) >= 2:
                agreement_scores[trait] = 1 - (np.std(values) / (np.mean(values) + 1e-10))
            else:
                agreement_scores[trait] = 0.0
        
        return agreement_scores
    
    def run_comparison(self, max_users: int = 10) -> Dict:
        """Run comparison on available users."""
        logger.info(f"Running comparison on up to {max_users} users...")
        
        # Find users with both baseline and Twitter data
        baseline_users = set(result["user_id"] for result in self.baseline_data["individual_results"])
        twitter_users = set(self.twitter_data.keys())
        common_users = list(baseline_users & twitter_users)
        
        if not common_users:
            logger.error("No users found with both baseline and Twitter data")
            return {}
        
        logger.info(f"Found {len(common_users)} users with both datasets")
        
        results = []
        processing_times = {"baseline": [], "bert": [], "beta_bayesian": []}
        
        for i, user_id in enumerate(common_users[:max_users]):
            logger.info(f"Processing user {i+1}/{min(len(common_users), max_users)}: {user_id}")
            
            tweets = self.twitter_data[user_id][:50]  # Use first 50 tweets
            
            # Run baseline method
            start_time = time.time()
            baseline_result = self.extract_baseline_results(user_id)
            processing_times["baseline"].append(time.time() - start_time)
            
            # Run BERT-style method
            start_time = time.time()
            bert_result = self.simple_bert_prediction(user_id, tweets)
            processing_times["bert"].append(time.time() - start_time)
            
            # Run Beta-Bayesian method
            start_time = time.time()
            beta_result = self.beta_bayesian_prediction(user_id, tweets)
            processing_times["beta_bayesian"].append(time.time() - start_time)
            
            # Calculate agreement
            agreement = self.calculate_agreement([baseline_result, bert_result, beta_result])
            
            user_result = {
                "user_id": user_id,
                "tweets_count": len(tweets),
                "baseline": baseline_result,
                "bert": bert_result,
                "beta_bayesian": beta_result,
                "agreement": agreement
            }
            
            results.append(user_result)
        
        # Generate summary report
        report = {
            "summary": {
                "users_compared": len(results),
                "methods": ["Likelihood Ratio (Baseline)", "BERT-style", "Beta-Bayesian"],
                "traits": self.traits
            },
            "processing_times": {
                method: {
                    "mean": np.mean(times),
                    "std": np.std(times)
                } for method, times in processing_times.items()
            },
            "agreement_stats": {},
            "confidence_stats": {}
        }
        
        # Calculate agreement statistics
        for trait in self.traits:
            agreements = [result["agreement"][trait] for result in results]
            report["agreement_stats"][trait] = {
                "mean": np.mean(agreements),
                "std": np.std(agreements)
            }
        
        # Calculate confidence statistics
        for method in ["baseline", "bert", "beta_bayesian"]:
            report["confidence_stats"][method] = {}
            for trait in self.traits:
                confidences = [result[method]["confidence_scores"][trait] for result in results if trait in result[method]["confidence_scores"]]
                if confidences:
                    report["confidence_stats"][method][trait] = {
                        "mean": np.mean(confidences),
                        "std": np.std(confidences)
                    }
        
        return {
            "results": results,
            "report": report
        }

def main():
    """Run the working real comparison."""
    baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
    
    if not Path(baseline_file).exists():
        logger.error(f"Baseline file not found: {baseline_file}")
        return False
    
    try:
        # Run comparison
        logger.info("🚀 Starting working REAL method comparison...")
        comparator = WorkingRealComparison(baseline_file)
        
        results = comparator.run_comparison(max_users=10)
        
        if not results:
            logger.error("No results generated")
            return False
        
        # Display results
        report = results["report"]
        
        print("\\n" + "="*60)
        print("🎯 WORKING REAL METHOD COMPARISON RESULTS")
        print("="*60)
        
        print(f"\\n📈 Users Analyzed: {report['summary']['users_compared']}")
        print(f"🧠 Traits: {', '.join(report['summary']['traits'])}")
        print(f"⚡ Methods: {', '.join(report['summary']['methods'])}")
        
        print("\\n⏱️  PROCESSING TIMES:")
        for method, stats in report["processing_times"].items():
            print(f"   {method:15}: {stats['mean']:.4f}s ± {stats['std']:.4f}s")
        
        print("\\n🤝 PREDICTION AGREEMENT:")
        for trait, stats in report["agreement_stats"].items():
            print(f"   {trait:20}: {stats['mean']:.3f} ± {stats['std']:.3f}")
        
        print("\\n🎯 CONFIDENCE SCORES:")
        for method, trait_stats in report["confidence_stats"].items():
            print(f"   {method.upper()}:")
            for trait, stats in trait_stats.items():
                print(f"     {trait:18}: {stats['mean']:.3f} ± {stats['std']:.3f}")
        
        # Save results
        output_file = "working_real_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\\n💾 Results saved to: {output_file}")
        print("\\n✅ Working real comparison completed!")
        
        # Show some example predictions
        if results["results"]:
            example_user = results["results"][0]
            print(f"\\n📊 Example predictions for {example_user['user_id']}:")
            for trait in comparator.traits:
                baseline = example_user["baseline"]["predictions"][trait]
                bert = example_user["bert"]["predictions"][trait]
                beta = example_user["beta_bayesian"]["predictions"][trait]
                
                print(f"\\n   {trait}:")
                print(f"     Baseline:     Low={baseline['low_1to4']:.2f}, Med={baseline['medium_5to7']:.2f}, High={baseline['high_8to11']:.2f}")
                print(f"     BERT-style:   Low={bert['low_1to4']:.2f}, Med={bert['medium_5to7']:.2f}, High={bert['high_8to11']:.2f}")
                print(f"     Beta-Bayes:   Low={beta['low_1to4']:.2f}, Med={beta['medium_5to7']:.2f}, High={beta['high_8to11']:.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Working comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()