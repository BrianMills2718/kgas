#!/usr/bin/env python3
"""
Real Beta-Bayesian Personality Prediction - No Mocks
Uses actual NLP processing and statistical inference on real Twitter data.
"""

import json
import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
import re
from collections import Counter

# Use actual NLP libraries
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    HAS_NLP = True
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('vader_lexicon')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords') 
        nltk.download('vader_lexicon')
        
except ImportError:
    HAS_NLP = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BetaParameters:
    """Beta distribution parameters with statistical properties."""
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
    
    @property
    def mode(self) -> float:
        if self.alpha > 1 and self.beta > 1:
            return (self.alpha - 1) / (self.alpha + self.beta - 2)
        return self.mean

class RealBetaBayesianPredictor:
    """Real Beta-Bayesian predictor using actual NLP and statistics."""
    
    def __init__(self):
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Initialize NLP tools
        if HAS_NLP:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            self.stop_words = set(stopwords.words('english'))
        else:
            logger.warning("NLTK not available. Install with: pip install nltk textstat")
            self.sentiment_analyzer = None
            self.stop_words = set()
        
        # Population priors learned from data
        self.population_priors = {}
        
        # Evidence extraction models
        self.trait_keywords = self._build_trait_keywords()
        self.evidence_extractors = self._build_evidence_extractors()
    
    def _build_trait_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """Build comprehensive keyword dictionaries for each trait."""
        return {
            'political_orientation': {
                'positive': ['democrat', 'liberal', 'progressive', 'left', 'biden', 'obama', 'socialism', 'equality', 'rights', 'diversity'],
                'negative': ['republican', 'conservative', 'trump', 'right', 'traditional', 'capitalism', 'freedom', 'liberty', 'patriot'],
                'neutral': ['politics', 'government', 'election', 'vote', 'policy', 'congress', 'senate', 'politician']
            },
            'conspiracy_mentality': {
                'positive': ['conspiracy', 'coverup', 'hidden', 'secret', 'truth', 'lies', 'manipulation', 'control', 'agenda', 'propaganda', 'fake', 'hoax'],
                'negative': ['facts', 'evidence', 'science', 'research', 'verified', 'official', 'credible', 'legitimate', 'authentic'],
                'neutral': ['question', 'doubt', 'skeptical', 'unclear', 'uncertain', 'investigate']
            },
            'science_denialism': {
                'positive': ['pseudoscience', 'unproven', 'theory', 'belief', 'opinion', 'natural', 'alternative', 'holistic', 'intuition'],
                'negative': ['science', 'research', 'study', 'evidence', 'data', 'peer-reviewed', 'scientific', 'empirical', 'validated'],
                'neutral': ['health', 'medicine', 'treatment', 'study', 'experiment', 'test']
            },
            'narcissism': {
                'positive': ['amazing', 'best', 'perfect', 'superior', 'exceptional', 'talented', 'special', 'unique', 'brilliant', 'genius', 'incredible'],
                'negative': ['humble', 'modest', 'ordinary', 'average', 'learning', 'mistake', 'sorry', 'team', 'together', 'help'],
                'neutral': ['good', 'great', 'nice', 'fine', 'okay', 'decent', 'solid']
            }
        }
    
    def _build_evidence_extractors(self) -> Dict[str, callable]:
        """Build evidence extraction functions for each trait."""
        return {
            'political_orientation': self._extract_political_evidence,
            'conspiracy_mentality': self._extract_conspiracy_evidence,
            'science_denialism': self._extract_science_evidence,
            'narcissism': self._extract_narcissism_evidence
        }
    
    def _extract_political_evidence(self, tweet: str) -> float:
        """Extract political orientation evidence from tweet."""
        if not HAS_NLP:
            return 0.5  # Neutral if no NLP
        
        tweet_lower = tweet.lower()
        keywords = self.trait_keywords['political_orientation']
        
        # Count keyword matches
        positive_score = sum(1 for word in keywords['positive'] if word in tweet_lower)
        negative_score = sum(1 for word in keywords['negative'] if word in tweet_lower)
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.polarity_scores(tweet)
        
        # Political content detection
        political_words = sum(1 for word in keywords['neutral'] if word in tweet_lower)
        
        if political_words == 0:
            return 0.5  # No political content
        
        # Combine evidence
        if positive_score > negative_score:
            return 0.7 + 0.2 * min(sentiment['pos'], 1.0)
        elif negative_score > positive_score:
            return 0.3 - 0.2 * min(sentiment['neg'], 1.0)
        else:
            return 0.5 + 0.1 * sentiment['compound']
    
    def _extract_conspiracy_evidence(self, tweet: str) -> float:
        """Extract conspiracy mentality evidence from tweet."""
        if not HAS_NLP:
            return 0.5
        
        tweet_lower = tweet.lower()
        keywords = self.trait_keywords['conspiracy_mentality']
        
        # Count conspiracy indicators
        conspiracy_score = sum(1 for word in keywords['positive'] if word in tweet_lower)
        rational_score = sum(1 for word in keywords['negative'] if word in tweet_lower)
        
        # Check for conspiracy phrases
        conspiracy_phrases = ['wake up', 'open your eyes', 'they dont want', 'follow the money', 'question everything']
        phrase_score = sum(1 for phrase in conspiracy_phrases if phrase in tweet_lower)
        
        # Sentiment analysis (negative sentiment often correlates with conspiracy thinking)
        sentiment = self.sentiment_analyzer.polarity_scores(tweet)
        
        total_evidence = conspiracy_score + phrase_score
        if total_evidence > rational_score:
            return 0.7 + 0.2 * min(total_evidence / 5, 1.0)
        elif rational_score > total_evidence:
            return 0.3 - 0.1 * min(rational_score / 3, 1.0)
        else:
            return 0.5 + 0.1 * abs(sentiment['compound'])
    
    def _extract_science_evidence(self, tweet: str) -> float:
        """Extract science denialism evidence from tweet."""
        if not HAS_NLP:
            return 0.5
        
        tweet_lower = tweet.lower()
        keywords = self.trait_keywords['science_denialism']
        
        # Count anti-science vs pro-science indicators
        antiscience_score = sum(1 for word in keywords['positive'] if word in tweet_lower)
        proscience_score = sum(1 for word in keywords['negative'] if word in tweet_lower)
        
        # Check for science denial phrases
        denial_phrases = ['so called experts', 'mainstream science', 'big pharma', 'natural immunity']
        denial_score = sum(1 for phrase in denial_phrases if phrase in tweet_lower)
        
        total_denial = antiscience_score + denial_score
        if total_denial > proscience_score:
            return 0.7 + 0.2 * min(total_denial / 3, 1.0)
        elif proscience_score > total_denial:
            return 0.3 - 0.1 * min(proscience_score / 3, 1.0)
        else:
            return 0.5
    
    def _extract_narcissism_evidence(self, tweet: str) -> float:
        """Extract narcissism evidence from tweet."""
        if not HAS_NLP:
            return 0.5
        
        tweet_lower = tweet.lower()
        keywords = self.trait_keywords['narcissism']
        
        # Count self-aggrandizing vs humble language
        narcissistic_score = sum(1 for word in keywords['positive'] if word in tweet_lower)
        humble_score = sum(1 for word in keywords['negative'] if word in tweet_lower)
        
        # Count first-person pronouns (narcissistic indicator)
        first_person = tweet_lower.count(' i ') + tweet_lower.count('my ') + tweet_lower.count('me ')
        
        # Check for self-promotional phrases
        self_promo = ['proud of myself', 'i am the', 'my achievement', 'my success']
        promo_score = sum(1 for phrase in self_promo if phrase in tweet_lower)
        
        # Reading complexity (narcissists often use complex language)
        try:
            complexity = flesch_kincaid_grade(tweet)
            complexity_score = 1 if complexity > 12 else 0
        except:
            complexity_score = 0
        
        total_narcissism = narcissistic_score + (first_person / 10) + promo_score + complexity_score
        
        if total_narcissism > humble_score + 1:
            return 0.7 + 0.2 * min(total_narcissism / 5, 1.0)
        elif humble_score > total_narcissism:
            return 0.3 - 0.1 * min(humble_score / 3, 1.0)
        else:
            return 0.5 + 0.1 * (first_person / 20)
    
    def extract_evidence_from_tweets(self, tweets: List[str], trait: str) -> List[float]:
        """Extract evidence scores for a trait from a list of tweets."""
        if trait not in self.evidence_extractors:
            raise ValueError(f"Unknown trait: {trait}")
        
        extractor = self.evidence_extractors[trait]
        evidence_scores = []
        
        for tweet in tweets:
            if len(tweet.strip()) > 10:  # Skip very short tweets
                score = extractor(tweet.strip())
                evidence_scores.append(score)
        
        return evidence_scores
    
    def learn_population_priors(self, baseline_file: str):
        """Learn population-level priors from baseline data using method of moments."""
        logger.info("Learning population priors from baseline data...")
        
        with open(baseline_file, 'r') as f:
            data = json.load(f)
        
        trait_values = {trait: [] for trait in self.traits}
        
        # Extract trait values from baseline results
        for user_result in data["individual_results"]:
            for trait in self.traits:
                trait_scores = []
                
                for chunk_result in user_result["chunk_results"]:
                    if chunk_result["success"] and trait in chunk_result["result"]:
                        prob_dist = chunk_result["result"][trait]
                        
                        # Convert to expected value (normalized to 0-1)
                        expected_value = (
                            prob_dist.get("low_1to4", 0) * 0.25 +
                            prob_dist.get("medium_5to7", 0) * 0.6 +
                            prob_dist.get("high_8to11", 0) * 0.9
                        )
                        trait_scores.append(expected_value)
                
                if trait_scores:
                    trait_values[trait].append(np.mean(trait_scores))
        
        # Estimate Beta parameters using method of moments
        for trait in self.traits:
            values = np.array(trait_values[trait])
            values = np.clip(values, 0.001, 0.999)  # Avoid boundary issues
            
            if len(values) > 1:
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
                logger.info(f"Prior for {trait}: α={alpha:.2f}, β={beta:.2f}, mean={alpha/(alpha+beta):.3f}")
            else:
                # Use weak prior
                self.population_priors[trait] = BetaParameters(alpha=1.0, beta=1.0)
    
    def bayesian_update(self, user_id: str, trait: str, tweets: List[str]) -> BetaParameters:
        """Perform Bayesian updating for a trait using evidence from tweets."""
        
        # Start with population prior
        if trait in self.population_priors:
            current_alpha = self.population_priors[trait].alpha
            current_beta = self.population_priors[trait].beta
        else:
            current_alpha = 1.0
            current_beta = 1.0
        
        # Extract evidence from tweets
        evidence_scores = self.extract_evidence_from_tweets(tweets, trait)
        
        if not evidence_scores:
            return BetaParameters(alpha=current_alpha, beta=current_beta)
        
        # Convert continuous evidence to binary using threshold
        threshold = 0.6  # Evidence above 0.6 counts as positive
        
        for score in evidence_scores:
            if score > threshold:
                current_alpha += 1  # Positive evidence
            elif score < (1 - threshold):
                current_beta += 1   # Negative evidence
            # Neutral evidence (0.4-0.6) doesn't update
        
        return BetaParameters(alpha=current_alpha, beta=current_beta)
    
    def predict_personality(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Predict personality using real Bayesian updating."""
        results = {}
        
        for trait in self.traits:
            # Perform Bayesian updating
            posterior = self.bayesian_update(user_id, trait, tweets)
            
            # Convert to your probability distribution format
            mean_value = posterior.mean
            ci_lower, ci_upper = posterior.confidence_interval_95
            
            # Map to categorical probabilities
            if mean_value < 0.4:
                prob_dist = {"low_1to4": 0.8, "medium_5to7": 0.2, "high_8to11": 0.0}
            elif mean_value < 0.7:
                prob_dist = {"low_1to4": 0.2, "medium_5to7": 0.8, "high_8to11": 0.0}
            else:
                prob_dist = {"low_1to4": 0.0, "medium_5to7": 0.2, "high_8to11": 0.8}
            
            results[trait] = {
                **prob_dist,
                "beta_mean": mean_value,
                "beta_alpha": posterior.alpha,
                "beta_beta": posterior.beta,
                "confidence_interval": {"lower": ci_lower, "upper": ci_upper},
                "evidence_count": len(tweets),
                "processed_tweets": len([t for t in tweets if len(t.strip()) > 10])
            }
        
        return results
    
    def load_twitter_data(self, data_file: str) -> Dict[str, List[str]]:
        """Load real Twitter data."""
        logger.info(f"Loading Twitter data from {data_file}")
        
        # Try multiple data file locations
        data_paths = [
            data_file,
            "../data/datasets/kunst_dataset/kunst_full_dataset_with_tweets/First degree data/web-immunization-364608.Participants_2019_2021.tweets.jsonl",
            "../uncertainty_stress_test/100_users_500tweets_dataset.json"
        ]
        
        for path in data_paths:
            if Path(path).exists():
                logger.info(f"Found data at: {path}")
                
                try:
                    if path.endswith('.jsonl'):
                        return self._load_jsonl_data(path)
                    elif path.endswith('.json'):
                        return self._load_json_data(path)
                except Exception as e:
                    logger.warning(f"Failed to load {path}: {e}")
                    continue
        
        logger.warning("No Twitter data found, using minimal sample")
        return {"sample_user": ["This is a sample tweet for testing"]}
    
    def _load_jsonl_data(self, path: str) -> Dict[str, List[str]]:
        """Load JSONL format Twitter data."""
        user_tweets = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                user_id = str(data.get('user_id', data.get('user', 'unknown')))
                tweet_text = data.get('text', data.get('tweet_text', ''))
                
                if user_id not in user_tweets:
                    user_tweets[user_id] = []
                if tweet_text.strip():
                    user_tweets[user_id].append(tweet_text.strip())
        
        return user_tweets
    
    def _load_json_data(self, path: str) -> Dict[str, List[str]]:
        """Load JSON format Twitter data."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        user_tweets = {}
        
        if isinstance(data, list):
            for user_data in data:
                user_id = str(user_data.get('user_id', 'unknown'))
                tweets = user_data.get('tweets', [])
                
                user_tweets[user_id] = []
                for tweet in tweets:
                    if isinstance(tweet, dict):
                        text = tweet.get('text', tweet.get('tweet_text', ''))
                    else:
                        text = str(tweet)
                    
                    if text.strip():
                        user_tweets[user_id].append(text.strip())
        
        return user_tweets

def main():
    """Test the real Beta-Bayesian predictor."""
    if not HAS_NLP:
        print("Please install required packages:")
        print("pip install nltk textstat")
        return
    
    predictor = RealBetaBayesianPredictor()
    
    # Load real data
    baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
    
    if Path(baseline_file).exists():
        # Learn population priors from your baseline data
        predictor.learn_population_priors(baseline_file)
        
        # Load Twitter data
        twitter_data = predictor.load_twitter_data("twitter_data.json")
        
        # Test prediction on first user
        test_user = list(twitter_data.keys())[0]
        test_tweets = twitter_data[test_user][:20]  # Use first 20 tweets
        
        logger.info(f"Testing prediction for user {test_user} with {len(test_tweets)} tweets")
        
        # Make prediction
        prediction = predictor.predict_personality(test_user, test_tweets)
        
        logger.info("Prediction results:")
        for trait, result in prediction.items():
            logger.info(f"  {trait}: mean={result['beta_mean']:.3f}, "
                       f"α={result['beta_alpha']:.1f}, β={result['beta_beta']:.1f}")
    else:
        logger.error(f"Baseline file not found: {baseline_file}")
    
    return predictor

if __name__ == "__main__":
    main()