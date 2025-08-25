#!/usr/bin/env python3
"""
Traditional ML Approaches for Personality Prediction
Uses Random Forest, XGBoost, and ensemble methods with engineered features
"""

import json
import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import re
from collections import Counter
from datetime import datetime

# ML libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.pipeline import Pipeline
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor
import xgboost as xgb
from textstat import flesch_reading_ease, flesch_kincaid_grade

# NLP libraries
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineering:
    """Comprehensive feature extraction for personality prediction."""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        
        # Psychological lexicons
        self.liwc_categories = {
            'i_words': ['i', 'me', 'my', 'myself', 'mine'],
            'we_words': ['we', 'us', 'our', 'ourselves', 'ours'],
            'positive_emotion': ['love', 'nice', 'sweet', 'happy', 'joy', 'wonderful'],
            'negative_emotion': ['hate', 'ugly', 'nasty', 'sad', 'angry', 'terrible'],
            'anxiety': ['worried', 'fearful', 'nervous', 'anxious', 'scared'],
            'anger': ['hate', 'kill', 'annoyed', 'angry', 'frustrated'],
            'certainty': ['always', 'never', 'definitely', 'certainly', 'absolutely'],
            'tentative': ['maybe', 'perhaps', 'possibly', 'might', 'could']
        }
        
        # Domain-specific dictionaries
        self.domain_keywords = {
            'political': {
                'conservative': ['trump', 'maga', 'conservative', 'republican', 'gop', 'right-wing', 
                               'traditional', 'freedom', 'liberty', 'constitution', '2nd amendment'],
                'liberal': ['biden', 'democrat', 'liberal', 'progressive', 'left-wing', 'blm',
                           'equality', 'diversity', 'inclusion', 'climate change', 'social justice'],
                'general': ['vote', 'election', 'campaign', 'politics', 'government', 'congress', 
                           'senate', 'president', 'policy', 'legislation']
            },
            'conspiracy': {
                'markers': ['wake up', 'sheeple', 'hidden agenda', 'they dont want', 'truth',
                           'mainstream media', 'deep state', 'elite', 'illuminati', 'new world order',
                           'false flag', 'psyop', 'controlled', 'manipulation'],
                'skepticism': ['question', 'investigate', 'research', 'dont believe', 'lies']
            },
            'science': {
                'pro_science': ['research', 'study', 'data', 'evidence', 'peer-reviewed', 'scientific',
                               'experts', 'consensus', 'methodology', 'empirical'],
                'anti_science': ['big pharma', 'chemicals', 'toxins', 'natural', 'holistic',
                                'alternative medicine', 'vaccine injury', 'gmo', 'fluoride']
            },
            'narcissism': {
                'grandiose': ['best', 'greatest', 'perfect', 'amazing', 'brilliant', 'genius',
                             'superior', 'exceptional', 'extraordinary', 'unmatched'],
                'entitlement': ['deserve', 'earned', 'owed', 'should get', 'my right'],
                'attention': ['look at me', 'check this out', 'see what i', 'watch me']
            }
        }
    
    def extract_linguistic_features(self, tweets: List[str]) -> Dict[str, float]:
        """Extract linguistic and stylistic features."""
        features = {}
        
        # Combine tweets for analysis
        full_text = ' '.join(tweets)
        words = word_tokenize(full_text.lower())
        sentences = sent_tokenize(full_text)
        
        # Basic statistics
        features['num_tweets'] = len(tweets)
        features['avg_tweet_length'] = np.mean([len(t) for t in tweets])
        features['std_tweet_length'] = np.std([len(t) for t in tweets])
        features['total_words'] = len(words)
        features['unique_words'] = len(set(words))
        features['vocabulary_richness'] = features['unique_words'] / features['total_words'] if features['total_words'] > 0 else 0
        
        # Readability scores
        try:
            features['flesch_reading_ease'] = flesch_reading_ease(full_text)
            features['flesch_kincaid_grade'] = flesch_kincaid_grade(full_text)
        except:
            features['flesch_reading_ease'] = 50.0
            features['flesch_kincaid_grade'] = 8.0
        
        # Punctuation patterns
        features['exclamation_ratio'] = full_text.count('!') / len(tweets)
        features['question_ratio'] = full_text.count('?') / len(tweets)
        features['ellipsis_ratio'] = full_text.count('...') / len(tweets)
        features['caps_word_ratio'] = sum(1 for w in words if w.isupper() and len(w) > 1) / len(words)
        
        # Sentiment features
        sentiments = [self.sia.polarity_scores(tweet) for tweet in tweets]
        features['avg_positive'] = np.mean([s['pos'] for s in sentiments])
        features['avg_negative'] = np.mean([s['neg'] for s in sentiments])
        features['avg_neutral'] = np.mean([s['neu'] for s in sentiments])
        features['avg_compound'] = np.mean([s['compound'] for s in sentiments])
        features['sentiment_volatility'] = np.std([s['compound'] for s in sentiments])
        
        # LIWC-style categories
        for category, word_list in self.liwc_categories.items():
            count = sum(1 for w in words if w in word_list)
            features[f'liwc_{category}_ratio'] = count / len(words) if words else 0
        
        # Pronoun analysis
        pronouns = {
            'first_singular': ['i', 'me', 'my', 'myself', 'mine'],
            'first_plural': ['we', 'us', 'our', 'ourselves', 'ours'],
            'second': ['you', 'your', 'yours', 'yourself'],
            'third': ['he', 'she', 'it', 'they', 'him', 'her', 'them']
        }
        
        for pron_type, pron_list in pronouns.items():
            count = sum(1 for w in words if w in pron_list)
            features[f'pronoun_{pron_type}_ratio'] = count / len(words) if words else 0
        
        # Temporal patterns (simplified without actual timestamps)
        features['tweets_per_burst'] = self._estimate_burst_size(tweets)
        
        # URL and mention patterns
        features['url_ratio'] = sum(1 for t in tweets if 'http' in t or 'www' in t) / len(tweets)
        features['mention_ratio'] = sum(1 for t in tweets if '@' in t) / len(tweets)
        features['hashtag_ratio'] = sum(1 for t in tweets if '#' in t) / len(tweets)
        features['retweet_ratio'] = sum(1 for t in tweets if t.startswith('RT ')) / len(tweets)
        
        return features
    
    def extract_domain_features(self, tweets: List[str]) -> Dict[str, float]:
        """Extract domain-specific features for each personality trait."""
        features = {}
        
        # Combine tweets
        full_text = ' '.join(tweets).lower()
        
        # Political features
        for pol_type, keywords in self.domain_keywords['political'].items():
            count = sum(full_text.count(kw.lower()) for kw in keywords)
            features[f'political_{pol_type}_count'] = count
            features[f'political_{pol_type}_density'] = count / len(full_text.split())
        
        # Conspiracy features
        for cons_type, keywords in self.domain_keywords['conspiracy'].items():
            count = sum(full_text.count(kw.lower()) for kw in keywords)
            features[f'conspiracy_{cons_type}_count'] = count
            features[f'conspiracy_{cons_type}_density'] = count / len(full_text.split())
        
        # Science features
        for sci_type, keywords in self.domain_keywords['science'].items():
            count = sum(full_text.count(kw.lower()) for kw in keywords)
            features[f'science_{sci_type}_count'] = count
            features[f'science_{sci_type}_density'] = count / len(full_text.split())
        
        # Narcissism features
        for narc_type, keywords in self.domain_keywords['narcissism'].items():
            count = sum(full_text.count(kw.lower()) for kw in keywords)
            features[f'narcissism_{narc_type}_count'] = count
            features[f'narcissism_{narc_type}_density'] = count / len(full_text.split())
        
        return features
    
    def extract_topic_features(self, tweets: List[str], n_topics: int = 10) -> Dict[str, float]:
        """Extract topic modeling features using LDA."""
        features = {}
        
        try:
            # Use simple bag of words for LDA
            vectorizer = CountVectorizer(max_features=100, stop_words='english')
            doc_term_matrix = vectorizer.fit_transform(tweets)
            
            # Fit LDA
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, max_iter=10)
            topic_dist = lda.fit_transform(doc_term_matrix)
            
            # Average topic distribution across tweets
            avg_topics = np.mean(topic_dist, axis=0)
            for i, weight in enumerate(avg_topics):
                features[f'topic_{i}_weight'] = weight
                
            # Topic diversity (entropy)
            topic_entropy = -np.sum(avg_topics * np.log(avg_topics + 1e-10))
            features['topic_diversity'] = topic_entropy
            
        except:
            # Fallback to zero features
            for i in range(n_topics):
                features[f'topic_{i}_weight'] = 0.0
            features['topic_diversity'] = 0.0
        
        return features
    
    def _estimate_burst_size(self, tweets: List[str]) -> float:
        """Estimate average burst size (consecutive similar tweets)."""
        if len(tweets) < 2:
            return 1.0
            
        burst_sizes = []
        current_burst = 1
        
        for i in range(1, len(tweets)):
            # Simple similarity: shared words
            words1 = set(tweets[i-1].lower().split())
            words2 = set(tweets[i].lower().split())
            
            similarity = len(words1 & words2) / max(len(words1 | words2), 1)
            
            if similarity > 0.3:  # Threshold for considering tweets similar
                current_burst += 1
            else:
                burst_sizes.append(current_burst)
                current_burst = 1
        
        burst_sizes.append(current_burst)
        return np.mean(burst_sizes)
    
    def extract_all_features(self, tweets: List[str]) -> Dict[str, float]:
        """Extract all features for ML models."""
        features = {}
        
        # Linguistic features
        features.update(self.extract_linguistic_features(tweets))
        
        # Domain-specific features
        features.update(self.extract_domain_features(tweets))
        
        # Topic features
        features.update(self.extract_topic_features(tweets))
        
        return features


class TraditionalMLPredictor:
    """Traditional ML approaches for personality prediction."""
    
    def __init__(self, model_type: str = "ensemble"):
        """
        Initialize predictor with specified model type.
        Options: 'random_forest', 'xgboost', 'gradient_boost', 'ensemble'
        """
        self.model_type = model_type
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Feature engineering
        self.feature_extractor = FeatureEngineering()
        self.scaler = StandardScaler()
        
        # Models for each trait
        self.models = {}
        self.is_trained = False
        
        # Feature names (will be set during training)
        self.feature_names = None
        
    def _create_model(self, trait: str):
        """Create model based on type."""
        if self.model_type == "random_forest":
            return RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "xgboost":
            return xgb.XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                objective='multi:softprob',
                num_class=3,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boost":
            return GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:  # ensemble
            # Return a voting classifier with multiple models
            from sklearn.ensemble import VotingClassifier
            return VotingClassifier([
                ('rf', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)),
                ('gb', GradientBoostingClassifier(n_estimators=50, max_depth=5, random_state=42)),
                ('xgb', xgb.XGBClassifier(n_estimators=100, max_depth=6, random_state=42))
            ], voting='soft')
    
    def prepare_training_data(self, twitter_data: List[Tuple[List[str], Dict[str, float]]]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepare features and labels for training."""
        logger.info(f"Extracting features for {len(twitter_data)} users...")
        
        # Extract features for all users
        feature_list = []
        labels = {trait: [] for trait in self.traits}
        
        for i, (tweets, ground_truth) in enumerate(twitter_data):
            if i % 10 == 0:
                logger.info(f"Processing user {i+1}/{len(twitter_data)}")
                
            # Extract features
            features = self.feature_extractor.extract_all_features(tweets)
            feature_list.append(features)
            
            # Convert ground truth to categories
            for trait in self.traits:
                score = ground_truth.get(trait.replace('_mentality', '').replace('_orientation', ''), 4)
                
                if trait == 'political_orientation':
                    category = 0 if score <= 4 else (1 if score <= 7 else 2)
                else:
                    category = 0 if score <= 3 else (1 if score <= 5 else 2)
                    
                labels[trait].append(category)
        
        # Convert to numpy arrays
        self.feature_names = list(feature_list[0].keys())
        X = np.array([[features.get(name, 0) for name in self.feature_names] for features in feature_list])
        y = {trait: np.array(labels[trait]) for trait in self.traits}
        
        return X, y
    
    def train(self, twitter_data: List[Tuple[List[str], Dict[str, float]]], 
              optimize_hyperparameters: bool = False):
        """Train models on the data."""
        logger.info(f"Training {self.model_type} models...")
        
        # Prepare data
        X, y = self.prepare_training_data(twitter_data)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model for each trait
        for trait in self.traits:
            logger.info(f"Training model for {trait}...")
            
            # Create model
            model = self._create_model(trait)
            
            # Optionally optimize hyperparameters
            if optimize_hyperparameters and self.model_type == "random_forest":
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [5, 10, 15],
                    'min_samples_split': [2, 5, 10]
                }
                
                grid_search = GridSearchCV(
                    model, param_grid, cv=3, scoring='f1_weighted', n_jobs=-1
                )
                grid_search.fit(X_scaled, y[trait])
                model = grid_search.best_estimator_
                logger.info(f"Best params for {trait}: {grid_search.best_params_}")
            else:
                # Train with default parameters
                model.fit(X_scaled, y[trait])
            
            # Store trained model
            self.models[trait] = model
            
            # Evaluate with cross-validation
            scores = cross_val_score(model, X_scaled, y[trait], cv=3, scoring='f1_weighted')
            logger.info(f"{trait} - CV F1 Score: {np.mean(scores):.3f} (+/- {np.std(scores):.3f})")
        
        self.is_trained = True
        logger.info("Training complete!")
    
    def predict(self, tweets: List[str]) -> Dict[str, Any]:
        """Predict personality traits for a single user."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Extract features
        features = self.feature_extractor.extract_all_features(tweets)
        
        # Convert to array
        X = np.array([[features.get(name, 0) for name in self.feature_names]])
        X_scaled = self.scaler.transform(X)
        
        predictions = {}
        confidence_scores = {}
        feature_importance = {}
        
        for trait in self.traits:
            model = self.models[trait]
            
            # Get probability predictions
            probs = model.predict_proba(X_scaled)[0]
            
            # Convert to our format
            predictions[trait] = {
                "low_1to4": float(probs[0]),
                "medium_5to7": float(probs[1]),
                "high_8to11": float(probs[2])
            }
            
            # Calculate confidence (based on max probability)
            confidence_scores[trait] = float(np.max(probs))
            
            # Get feature importance (if available)
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                top_features_idx = np.argsort(importances)[-10:]
                feature_importance[trait] = {
                    self.feature_names[i]: float(importances[i]) 
                    for i in top_features_idx
                }
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": f"Traditional ML ({self.model_type})",
            "feature_importance": feature_importance,
            "num_features": len(self.feature_names)
        }
    
    def predict_batch(self, user_tweets: Dict[str, List[str]]) -> Dict[str, Dict]:
        """Predict for multiple users efficiently."""
        results = {}
        
        # Extract features for all users
        feature_list = []
        user_ids = list(user_tweets.keys())
        
        logger.info(f"Extracting features for {len(user_ids)} users...")
        for user_id in user_ids:
            features = self.feature_extractor.extract_all_features(user_tweets[user_id])
            feature_list.append(features)
        
        # Convert to array and scale
        X = np.array([[features.get(name, 0) for name in self.feature_names] for features in feature_list])
        X_scaled = self.scaler.transform(X)
        
        # Predict for each trait
        for trait in self.traits:
            model = self.models[trait]
            all_probs = model.predict_proba(X_scaled)
            
            for i, user_id in enumerate(user_ids):
                if user_id not in results:
                    results[user_id] = {
                        "predictions": {},
                        "confidence_scores": {},
                        "method": f"Traditional ML ({self.model_type})"
                    }
                
                probs = all_probs[i]
                results[user_id]["predictions"][trait] = {
                    "low_1to4": float(probs[0]),
                    "medium_5to7": float(probs[1]),
                    "high_8to11": float(probs[2])
                }
                results[user_id]["confidence_scores"][trait] = float(np.max(probs))
        
        return results


def load_twitter_data_with_ground_truth(file_path: str) -> List[Tuple[List[str], Dict[str, float]]]:
    """Load Twitter data with ground truth."""
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
            'political': float(user_info.get("political", 5)),
            'narcissism': np.mean([float(user_info.get(f"narcissism_{i}", 4)) for i in range(1, 5)]),
            'conspiracy': np.mean([float(user_info.get(f"conspiracy_{i}", 4)) for i in range(1, 6)]),
            'denialism': np.mean([float(user_info.get(f"denialism_{i}", 4)) for i in range(1, 5)])
        }
        
        training_data.append((tweets, ground_truth))
    
    return training_data


def evaluate_model(predictor: TraditionalMLPredictor, test_data: List[Tuple[List[str], Dict[str, float]]]) -> Dict[str, Any]:
    """Evaluate model performance."""
    all_errors = {trait: [] for trait in predictor.traits}
    all_predictions = []
    
    for tweets, ground_truth in test_data:
        result = predictor.predict(tweets)
        
        for trait in predictor.traits:
            # Convert prediction to point estimate
            pred_dist = result['predictions'][trait]
            pred_value = (pred_dist['low_1to4'] * 2.5 + 
                         pred_dist['medium_5to7'] * 6.0 + 
                         pred_dist['high_8to11'] * 9.5)
            
            # Get ground truth value
            trait_key = trait.replace('_mentality', '').replace('_orientation', '')
            true_value = ground_truth.get(trait_key, 4)
            
            # Scale for comparison
            if trait != 'political_orientation':
                true_value = (true_value - 1) * (10/6) + 1
            
            error = abs(pred_value - true_value)
            all_errors[trait].append(error)
        
        all_predictions.append(result)
    
    # Calculate metrics
    metrics = {
        'mae_by_trait': {trait: np.mean(errors) for trait, errors in all_errors.items()},
        'overall_mae': np.mean([e for errors in all_errors.values() for e in errors]),
        'rmse_by_trait': {trait: np.sqrt(np.mean(np.array(errors)**2)) for trait, errors in all_errors.items()},
        'confidence_stats': {
            trait: {
                'mean': np.mean([p['confidence_scores'][trait] for p in all_predictions]),
                'std': np.std([p['confidence_scores'][trait] for p in all_predictions])
            }
            for trait in predictor.traits
        }
    }
    
    return metrics


def main():
    """Demo traditional ML approaches."""
    # Load data
    twitter_file = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    all_data = load_twitter_data_with_ground_truth(twitter_file)
    
    logger.info(f"Loaded {len(all_data)} users with ground truth")
    
    # Split data
    train_size = int(0.8 * len(all_data))
    train_data = all_data[:train_size]
    test_data = all_data[train_size:]
    
    logger.info(f"Training: {len(train_data)}, Testing: {len(test_data)}")
    
    # Test different model types
    model_types = ['random_forest', 'xgboost', 'ensemble']
    results = {}
    
    for model_type in model_types:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {model_type.upper()} model")
        logger.info(f"{'='*60}")
        
        # Initialize and train
        predictor = TraditionalMLPredictor(model_type=model_type)
        predictor.train(train_data, optimize_hyperparameters=False)
        
        # Evaluate
        metrics = evaluate_model(predictor, test_data[:10])  # Use subset for quick demo
        results[model_type] = metrics
        
        # Print results
        print(f"\n{model_type.upper()} Results:")
        print(f"Overall MAE: {metrics['overall_mae']:.2f}")
        print("MAE by trait:")
        for trait, mae in metrics['mae_by_trait'].items():
            print(f"  {trait}: {mae:.2f}")
    
    # Compare models
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    
    comparison_df = pd.DataFrame({
        model: {
            'Overall MAE': results[model]['overall_mae'],
            **{f'{trait} MAE': mae for trait, mae in results[model]['mae_by_trait'].items()}
        }
        for model in model_types
    }).T
    
    print(comparison_df.round(2))
    
    # Save detailed results
    output = {
        'model_comparison': results,
        'best_model': min(results.keys(), key=lambda m: results[m]['overall_mae']),
        'feature_count': len(predictor.feature_names),
        'sample_features': predictor.feature_names[:20]  # First 20 features
    }
    
    output_file = "traditional_ml_results.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()