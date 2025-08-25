#!/usr/bin/env python3
"""
Improved Bayesian Personality Predictor with Learned Parameters
Uses empirical data to learn likelihood weights and prior distributions
"""

import json
import numpy as np
import time
import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from scipy import stats
from scipy.optimize import minimize
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import cross_val_score
import re
from collections import defaultdict, Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedBayesianPredictor:
    """Enhanced Bayesian predictor with learned parameters from data."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Learned parameters (will be fit from data)
        self.keyword_weights = {}
        self.prior_distributions = {}
        self.likelihood_params = {}
        
        # Feature extractors
        self.tfidf_vectorizers = {}
        self.nb_classifiers = {}
        
        # Enhanced keyword dictionaries with learned weights
        self.trait_keywords = {
            'political_orientation': {
                'high': ['election', 'vote', 'democrat', 'republican', 'liberal', 'conservative', 
                        'congress', 'senate', 'president', 'policy', 'government', 'political',
                        'maga', 'biden', 'trump', 'pelosi', 'mcconnell', 'aoc', 'bernie'],
                'medium': ['news', 'country', 'america', 'nation', 'people', 'society', 'issue'],
                'low': []  # Absence of political keywords
            },
            'conspiracy_mentality': {
                'high': ['wake up', 'sheeple', 'they', 'them', 'hidden', 'truth', 'real', 
                        'agenda', 'control', 'manipulation', 'deep state', 'elite', 'conspiracy',
                        'mainstream media', 'dont trust', 'question everything', 'hoax'],
                'medium': ['suspicious', 'wonder', 'strange', 'investigate', 'research'],
                'low': ['evidence', 'study', 'research shows', 'experts', 'scientists']
            },
            'science_denialism': {
                'high': ['big pharma', 'natural', 'chemicals', 'toxins', 'vaccine', 'hoax',
                        'pseudoscience', 'alternative', 'mainstream science', 'do your research'],
                'medium': ['skeptical', 'question', 'unsure', 'debate', 'controversial'],
                'low': ['peer reviewed', 'scientific', 'evidence based', 'data shows', 'study']
            },
            'narcissism': {
                'high': ['i am', 'my', 'me', 'myself', 'best', 'perfect', 'amazing', 'brilliant',
                        'superior', 'deserve', 'special', 'admire', 'talented', 'exceptional'],
                'medium': ['proud', 'accomplished', 'successful', 'achievement'],
                'low': ['we', 'us', 'team', 'together', 'grateful', 'thankful', 'humble']
            }
        }
        
        # Linguistic features for enhanced extraction
        self.linguistic_patterns = {
            'political_orientation': {
                'partisan_language': re.compile(r'\b(liberal|conservative|left|right)[-\s]?(wing)?\b', re.I),
                'political_entities': re.compile(r'\b(GOP|DNC|MAGA|BLM|antifa)\b', re.I),
                'political_hashtags': re.compile(r'#(resist|maga|blm|alllivesmatter|defundthepolice)', re.I)
            },
            'conspiracy_mentality': {
                'us_vs_them': re.compile(r'\b(they|them|elite|establishment)\s+(want|control|hide)\b', re.I),
                'skepticism_markers': re.compile(r'(wake up|open your eyes|do your own research)', re.I),
                'certainty_language': re.compile(r'(the truth is|obviously|clearly|definitely)\s+\w+', re.I)
            },
            'science_denialism': {
                'anti_expert': re.compile(r'so[- ]called\s+(experts?|scientists?)', re.I),
                'natural_fallacy': re.compile(r'(natural|organic|chemical[- ]free|toxin[- ]free)', re.I),
                'anecdotal_evidence': re.compile(r'(my friend|i know someone|personally seen)', re.I)
            },
            'narcissism': {
                'self_reference': re.compile(r'\b(i|me|my|myself|mine)\b', re.I),
                'grandiosity': re.compile(r'(best|greatest|perfect|amazing|brilliant|superior)', re.I),
                'attention_seeking': re.compile(r'(look at|check out|see my|watch me)', re.I)
            }
        }
    
    def extract_features(self, tweets: List[str]) -> Dict[str, float]:
        """Extract linguistic and behavioral features from tweets."""
        features = {}
        text = ' '.join(tweets).lower()
        
        # Basic statistics
        features['tweet_count'] = len(tweets)
        features['avg_tweet_length'] = np.mean([len(t) for t in tweets])
        features['total_words'] = len(text.split())
        
        # Keyword frequencies
        for trait, keywords in self.trait_keywords.items():
            for level, words in keywords.items():
                count = sum(text.count(word.lower()) for word in words)
                features[f'{trait}_{level}_keywords'] = count / features['total_words'] if features['total_words'] > 0 else 0
        
        # Pattern matches
        for trait, patterns in self.linguistic_patterns.items():
            for pattern_name, pattern in patterns.items():
                matches = len(pattern.findall(text))
                features[f'{trait}_{pattern_name}'] = matches / features['tweet_count']
        
        # Temporal features
        features['tweets_per_day'] = len(tweets) / 30  # Assuming 30-day window
        
        # Engagement patterns (simplified without actual engagement data)
        features['question_ratio'] = sum('?' in tweet for tweet in tweets) / len(tweets)
        features['exclamation_ratio'] = sum('!' in tweet for tweet in tweets) / len(tweets)
        features['caps_ratio'] = sum(word.isupper() for tweet in tweets for word in tweet.split()) / features['total_words']
        
        # Sentiment indicators (simplified)
        positive_words = ['love', 'great', 'awesome', 'amazing', 'wonderful', 'excellent']
        negative_words = ['hate', 'terrible', 'awful', 'horrible', 'disgusting', 'stupid']
        features['positive_ratio'] = sum(word in text for word in positive_words) / features['total_words']
        features['negative_ratio'] = sum(word in text for word in negative_words) / features['total_words']
        
        return features
    
    def learn_parameters(self, training_data: List[Tuple[List[str], Dict[str, float]]]):
        """Learn Bayesian parameters from training data."""
        logger.info(f"Learning parameters from {len(training_data)} training examples")
        
        # Extract features and labels for all training data
        all_features = []
        all_labels = {trait: [] for trait in self.traits}
        
        for tweets, ground_truth in training_data:
            features = self.extract_features(tweets)
            all_features.append(features)
            
            for trait in self.traits:
                # Convert continuous scores to categories
                score = ground_truth.get(trait, 4)
                if trait == 'political_orientation':
                    category = 0 if score <= 4 else (1 if score <= 7 else 2)
                else:
                    category = 0 if score <= 3 else (1 if score <= 5 else 2)
                all_labels[trait].append(category)
        
        # Learn prior distributions from training data
        for trait in self.traits:
            label_counts = Counter(all_labels[trait])
            total = sum(label_counts.values())
            self.prior_distributions[trait] = {
                'low': label_counts[0] / total,
                'medium': label_counts[1] / total,
                'high': label_counts[2] / total
            }
            logger.info(f"{trait} priors: {self.prior_distributions[trait]}")
        
        # Learn keyword weights using feature importance
        feature_matrix = self._features_to_matrix(all_features)
        
        for trait in self.traits:
            # Train a simple classifier to get feature importances
            from sklearn.ensemble import RandomForestClassifier
            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(feature_matrix, all_labels[trait])
            
            # Get feature importances
            feature_names = list(all_features[0].keys())
            importances = clf.feature_importances_
            
            # Store important features for this trait
            self.keyword_weights[trait] = {}
            for name, importance in zip(feature_names, importances):
                if trait in name and importance > 0.01:  # Only keep relevant features
                    self.keyword_weights[trait][name] = importance
            
            # Also train a Naive Bayes classifier for likelihood estimation
            self.nb_classifiers[trait] = MultinomialNB()
            # Need to ensure non-negative features for MultinomialNB
            feature_matrix_positive = np.maximum(feature_matrix, 0)
            self.nb_classifiers[trait].fit(feature_matrix_positive, all_labels[trait])
        
        logger.info("Parameter learning complete")
    
    def _features_to_matrix(self, features_list: List[Dict[str, float]]) -> np.ndarray:
        """Convert feature dictionaries to numpy matrix."""
        if not features_list:
            return np.array([])
        
        feature_names = list(features_list[0].keys())
        matrix = np.zeros((len(features_list), len(feature_names)))
        
        for i, features in enumerate(features_list):
            for j, name in enumerate(feature_names):
                matrix[i, j] = features.get(name, 0)
        
        return matrix
    
    def calculate_likelihood(self, features: Dict[str, float], trait: str, level: str) -> float:
        """Calculate likelihood P(features|trait_level) using learned parameters."""
        # Map level names to indices
        level_map = {'low': 0, 'medium': 1, 'high': 2}
        level_idx = level_map[level]
        
        # If we have a trained classifier, use it
        if trait in self.nb_classifiers and self.nb_classifiers[trait] is not None:
            # Convert features to matrix format
            feature_matrix = self._features_to_matrix([features])
            feature_matrix_positive = np.maximum(feature_matrix, 0)
            
            # Get probability from classifier
            try:
                probs = self.nb_classifiers[trait].predict_proba(feature_matrix_positive)[0]
                return probs[level_idx]
            except:
                pass
        
        # Fallback: calculate based on keyword weights
        likelihood = 1.0
        
        for feature_name, value in features.items():
            if trait in feature_name and level in feature_name:
                # Use learned weights if available
                weight = self.keyword_weights.get(trait, {}).get(feature_name, 0.1)
                
                # Apply likelihood based on feature presence
                if value > 0:
                    likelihood *= (1 + weight * value)
                else:
                    likelihood *= (1 - weight * 0.5)
        
        # Normalize (crude approximation)
        return min(likelihood / 10, 1.0)
    
    def predict(self, tweets: List[str]) -> Dict[str, Any]:
        """Predict personality traits using improved Bayesian inference."""
        # Extract features
        features = self.extract_features(tweets)
        
        predictions = {}
        confidence_scores = {}
        evidence_strength = {}
        
        for trait in self.traits:
            # Get prior distribution
            if trait in self.prior_distributions:
                prior = self.prior_distributions[trait]
            else:
                # Default uniform prior
                prior = {'low': 0.33, 'medium': 0.34, 'high': 0.33}
            
            # Calculate likelihoods for each level
            likelihoods = {}
            for level in ['low', 'medium', 'high']:
                likelihoods[level] = self.calculate_likelihood(features, trait, level)
            
            # Bayesian inference
            posteriors = {}
            evidence = sum(prior[level] * likelihoods[level] for level in ['low', 'medium', 'high'])
            
            if evidence > 0:
                for level in ['low', 'medium', 'high']:
                    posteriors[level] = (prior[level] * likelihoods[level]) / evidence
            else:
                posteriors = prior
            
            # Convert to our format
            predictions[trait] = {
                "low_1to4": posteriors['low'],
                "medium_5to7": posteriors['medium'],
                "high_8to11": posteriors['high']
            }
            
            # Calculate confidence based on posterior entropy
            probs = list(posteriors.values())
            entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
            max_entropy = -np.log(1/3)
            confidence_scores[trait] = 1 - (entropy / max_entropy)
            
            # Store evidence strength
            evidence_strength[trait] = {
                'keyword_evidence': sum(features.get(f'{trait}_{level}_keywords', 0) for level in ['high', 'medium']),
                'pattern_evidence': sum(features.get(f'{trait}_{pattern}', 0) for pattern in self.linguistic_patterns.get(trait, {}).keys()),
                'likelihood_ratios': likelihoods
            }
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "Improved Bayesian (Learned Parameters)",
            "evidence_strength": evidence_strength,
            "features_extracted": len(features)
        }
    
    def batch_predict(self, user_tweets: Dict[str, List[str]]) -> Dict[str, Dict]:
        """Predict for multiple users."""
        results = {}
        
        for user_id, tweets in user_tweets.items():
            results[user_id] = self.predict(tweets)
            
        return results


def load_twitter_data_with_ground_truth(file_path: str) -> List[Tuple[List[str], Dict[str, float]]]:
    """Load Twitter data with ground truth for training."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    training_data = []
    
    for user_data in data:
        user_info = user_data["user_info"]
        tweets = [tweet["text"] for tweet in user_data["tweets"] if tweet.get("text", "").strip()]
        
        if len(tweets) < 10:
            continue
            
        # Extract ground truth
        ground_truth = {
            'political_orientation': float(user_info.get("political", 5)),
            'narcissism': np.mean([float(user_info.get(f"narcissism_{i}", 4)) for i in range(1, 5)]),
            'conspiracy_mentality': np.mean([float(user_info.get(f"conspiracy_{i}", 4)) for i in range(1, 6)]),
            'science_denialism': np.mean([float(user_info.get(f"denialism_{i}", 4)) for i in range(1, 5)])
        }
        
        training_data.append((tweets, ground_truth))
    
    return training_data


def evaluate_predictions(predictions: Dict[str, Any], ground_truth: Dict[str, float]) -> Dict[str, float]:
    """Evaluate prediction accuracy."""
    errors = {}
    
    for trait, pred_dist in predictions['predictions'].items():
        # Convert distribution to point estimate
        pred_value = (pred_dist['low_1to4'] * 2.5 + 
                     pred_dist['medium_5to7'] * 6.0 + 
                     pred_dist['high_8to11'] * 9.5)
        
        # Adjust scale for comparison
        if trait == 'political_orientation':
            true_value = ground_truth.get(trait.replace('_orientation', ''), 5)
        else:
            true_value = ground_truth.get(trait.replace('_mentality', ''), 4)
            # Scale to match prediction scale
            true_value = (true_value - 1) * (10/6) + 1
        
        errors[trait] = abs(pred_value - true_value)
    
    return errors


def main():
    """Demo improved Bayesian personality prediction."""
    # Load data
    twitter_file = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    all_data = load_twitter_data_with_ground_truth(twitter_file)
    
    logger.info(f"Loaded {len(all_data)} users with ground truth")
    
    # Split into train/test
    train_size = int(0.8 * len(all_data))
    train_data = all_data[:train_size]
    test_data = all_data[train_size:]
    
    logger.info(f"Training on {len(train_data)} users, testing on {len(test_data)} users")
    
    # Initialize and train predictor
    predictor = ImprovedBayesianPredictor()
    predictor.learn_parameters(train_data)
    
    # Test on sample users
    logger.info("\nTesting improved Bayesian predictor...")
    test_results = []
    all_errors = {trait: [] for trait in predictor.traits}
    
    for i, (tweets, ground_truth) in enumerate(test_data[:10]):
        result = predictor.predict(tweets)
        errors = evaluate_predictions(result, ground_truth)
        
        # Store results
        test_results.append({
            "user_index": i,
            "ground_truth": ground_truth,
            "predictions": result,
            "errors": errors
        })
        
        # Accumulate errors
        for trait, error in errors.items():
            all_errors[trait].append(error)
        
        # Print sample results
        if i < 3:
            print(f"\nTest User {i+1}:")
            print(f"Ground Truth: {ground_truth}")
            print(f"Predictions:")
            for trait, pred in result['predictions'].items():
                print(f"  {trait}: {pred}")
            print(f"Confidence: {result['confidence_scores']}")
            print(f"Errors: {errors}")
    
    # Calculate average errors
    avg_errors = {trait: np.mean(errors) for trait, errors in all_errors.items()}
    
    print(f"\n=== IMPROVED BAYESIAN PERFORMANCE ===")
    print(f"Average Errors (MAE):")
    for trait, error in avg_errors.items():
        print(f"  {trait}: {error:.2f}")
    print(f"Overall MAE: {np.mean(list(avg_errors.values())):.2f}")
    
    # Save results
    output = {
        "method": "Improved Bayesian with Learned Parameters",
        "training_size": len(train_data),
        "test_size": len(test_data),
        "average_errors": avg_errors,
        "overall_mae": float(np.mean(list(avg_errors.values()))),
        "test_results": test_results[:5],  # Save subset
        "learned_priors": predictor.prior_distributions,
        "feature_importance_summary": {
            trait: list(predictor.keyword_weights.get(trait, {}).keys())[:10]
            for trait in predictor.traits
        }
    }
    
    output_file = "improved_bayesian_results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()