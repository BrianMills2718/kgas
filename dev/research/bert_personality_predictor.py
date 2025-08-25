#!/usr/bin/env python3
"""
BERT-based Personality Prediction for Twitter Data
Adapted from rcantini/BERT_personality_detection for comparison with likelihood ratio approach.

Key differences from original:
- Uses your 4 traits: political_orientation, conspiracy_mentality, science_denialism, narcissism  
- Processes Twitter data format from your system
- Outputs probability distributions compatible with your evaluation framework
"""

import json
import numpy as np
import pandas as pd
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
try:
    import tensorflow as tf
    from transformers import TFBertModel, BertTokenizer
    import tensorflow.keras as keras
    import tensorflow.keras.layers as layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BertPersonalityPredictor:
    """BERT-based personality predictor for your 4 psychological traits."""
    
    def __init__(self, max_seq_len: int = 256, bert_model: str = 'bert-base-uncased'):
        self.max_seq_len = max_seq_len
        self.bert_model = bert_model
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        self.model = None
        self.tokenizer = None
        
        # Initialize tokenizer if TensorFlow is available
        if HAS_TENSORFLOW:
            try:
                self.tokenizer = BertTokenizer.from_pretrained(self.bert_model)
            except Exception as e:
                logger.warning(f"Could not load BERT tokenizer: {e}")
                self.tokenizer = None
        else:
            logger.warning("TensorFlow not available, BERT functionality disabled")
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess Twitter text for BERT input."""
        # Similar to original but adapted for tweets
        text = text.lower()
        text = re.sub(r'\\[.*?\\]', '', text)  # Remove text in square brackets
        text = re.sub(r'https?://\\S+|www\\.\\S+', '', text)  # Remove URLs
        text = re.sub(r'<.*?>+', '', text)  # Remove HTML tags
        text = re.sub(r'\\n', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\\w*\\d\\w*', '', text)  # Remove words with numbers
        text = re.sub(r'@\\w+', '', text)  # Remove @mentions
        text = re.sub(r'#\\w+', '', text)  # Remove hashtags
        text = re.sub(r'\\s+', ' ', text)  # Collapse multiple spaces
        text = text.strip()
        
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
            
        return text
    
    def prepare_bert_input(self, texts: List[str]) -> List[np.ndarray]:
        """Prepare texts for BERT input."""
        if isinstance(texts, str):
            texts = [texts]
            
        # Clean texts
        cleaned_texts = [self.preprocess_text(text) for text in texts]
        
        # Tokenize
        encodings = self.tokenizer(
            cleaned_texts,
            truncation=True,
            padding='max_length',
            max_length=self.max_seq_len,
            return_tensors='tf'
        )
        
        return [
            np.array(encodings["input_ids"]),
            np.array(encodings["attention_mask"]),
            np.array(encodings["token_type_ids"])
        ]
    
    def build_model(self):
        """Build BERT-based model for personality prediction."""
        if not HAS_TENSORFLOW:
            raise RuntimeError("TensorFlow not available for BERT model")
        
        # Input layers
        input_ids = layers.Input(shape=(self.max_seq_len,), dtype=tf.int32, name='input_ids')
        input_mask = layers.Input(shape=(self.max_seq_len,), dtype=tf.int32, name='attention_mask')
        input_type = layers.Input(shape=(self.max_seq_len,), dtype=tf.int32, name='token_type_ids')
        inputs = [input_ids, input_mask, input_type]
        
        # BERT layer
        bert = TFBertModel.from_pretrained(self.bert_model)
        bert_outputs = bert(inputs)
        last_hidden_states = bert_outputs.last_hidden_state
        
        # Global average pooling
        avg = layers.GlobalAveragePooling1D()(last_hidden_states)
        
        # Dropout for regularization
        dropout = layers.Dropout(0.3)(avg)
        
        # Output layer - 4 traits, each with sigmoid activation
        output = layers.Dense(len(self.traits), activation="sigmoid")(dropout)
        
        model = keras.Model(inputs=inputs, outputs=output)
        return model
    
    def convert_your_data_to_training_format(self, results_file: str) -> Tuple[List[str], np.ndarray]:
        """Convert your Twitter results data to training format for BERT."""
        with open(results_file, 'r') as f:
            data = json.load(f)
        
        texts = []
        labels = []
        
        for user_result in data["individual_results"]:
            user_id = user_result["user_id"]
            
            # Aggregate user's tweets into one text
            user_tweets = []
            user_predictions = {trait: [] for trait in self.traits}
            
            for chunk_result in user_result["chunk_results"]:
                if chunk_result["success"]:
                    result = chunk_result["result"]
                    
                    # Convert probability distributions to single values (weighted average)
                    for trait in self.traits:
                        if trait in result:
                            prob_dist = result[trait]
                            # Convert to single value: low=0.2, medium=0.6, high=1.0
                            value = (prob_dist.get("low_1to4", 0) * 0.2 + 
                                   prob_dist.get("medium_5to7", 0) * 0.6 + 
                                   prob_dist.get("high_8to11", 0) * 1.0)
                            user_predictions[trait].append(value)
            
            # Get user tweets (we'll need to load the original tweet data)
            # For now, create placeholder - in real implementation, load actual tweets
            user_text = f"User {user_id} aggregated content"  # This needs actual tweet text
            
            # Average predictions across chunks for ground truth
            if all(len(user_predictions[trait]) > 0 for trait in self.traits):
                label_vector = [np.mean(user_predictions[trait]) for trait in self.traits]
                texts.append(user_text)
                labels.append(label_vector)
        
        return texts, np.array(labels)
    
    def load_twitter_data_for_user(self, user_id: str, data_dir: str = "uncertainty_stress_test") -> str:
        """Load actual Twitter text for a user. This would need to be implemented based on your data structure."""
        # Placeholder - you'd implement this to load actual tweet text
        # from your Twitter dataset based on user_id
        return f"Sample Twitter content for {user_id}"
    
    def train_model(self, texts: List[str], labels: np.ndarray, 
                   validation_split: float = 0.2, epochs: int = 5, batch_size: int = 16):
        """Train the BERT model."""
        logger.info(f"Training BERT model on {len(texts)} samples")
        
        # Prepare BERT inputs
        X = self.prepare_bert_input(texts)
        
        # Split data
        indices = np.arange(len(texts))
        train_idx, val_idx = train_test_split(indices, test_size=validation_split, random_state=42)
        
        X_train = [x[train_idx] for x in X]
        X_val = [x[val_idx] for x in X]
        y_train = labels[train_idx]
        y_val = labels[val_idx]
        
        # Build model
        self.model = self.build_model()
        
        # Compile model
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=2e-5),
            loss='mse',  # Using MSE since we're predicting continuous values
            metrics=['mae']
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        
        return history
    
    def predict_personality(self, texts: List[str]) -> np.ndarray:
        """Predict personality traits for given texts."""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model first.")
        
        X = self.prepare_bert_input(texts)
        predictions = self.model.predict(X)
        return predictions
    
    def convert_predictions_to_your_format(self, predictions: np.ndarray) -> List[Dict]:
        """Convert BERT predictions to your probability distribution format."""
        results = []
        
        for pred in predictions:
            result = {}
            for i, trait in enumerate(self.traits):
                value = pred[i]
                
                # Convert single value back to probability distribution
                # This is a simplification - you might want a more sophisticated mapping
                if value < 0.4:
                    result[trait] = {"low_1to4": 0.8, "medium_5to7": 0.2, "high_8to11": 0.0}
                elif value < 0.7:
                    result[trait] = {"low_1to4": 0.2, "medium_5to7": 0.8, "high_8to11": 0.0}
                else:
                    result[trait] = {"low_1to4": 0.0, "medium_5to7": 0.3, "high_8to11": 0.7}
                    
            results.append(result)
        
        return results
    
    def evaluate_against_baseline(self, baseline_file: str, test_texts: List[str]) -> Dict:
        """Evaluate BERT predictions against your baseline results."""
        # Load baseline results
        with open(baseline_file, 'r') as f:
            baseline_data = json.load(f)
        
        # Get BERT predictions
        bert_predictions = self.predict_personality(test_texts)
        bert_formatted = self.convert_predictions_to_your_format(bert_predictions)
        
        # Compare accuracies
        comparison = {
            "method": "BERT vs Likelihood Ratio",
            "bert_mae": {},
            "baseline_mae": baseline_data["accuracy_metrics"]["scale_specific_accuracy"],
            "differences": {}
        }
        
        # Calculate MAE for BERT (simplified - would need actual ground truth)
        for trait in self.traits:
            # This would need ground truth data for proper evaluation
            comparison["bert_mae"][trait] = {"placeholder": "needs_ground_truth"}
        
        return comparison

def main():
    """Example usage of BERT personality predictor."""
    predictor = BertPersonalityPredictor()
    
    # Example training (would need actual data)
    sample_texts = [
        "I believe in conspiracy theories and distrust the government",
        "I love science and evidence-based reasoning",
        "I'm amazing and everyone should recognize my talents",
        "I have moderate political views and trust scientific institutions"
    ]
    
    sample_labels = np.array([
        [0.7, 0.9, 0.1, 0.8],  # high political, high conspiracy, low science denial, high narcissism
        [0.3, 0.1, 0.1, 0.2],  # low on most traits
        [0.5, 0.3, 0.2, 0.9],  # high narcissism
        [0.4, 0.2, 0.1, 0.3]   # moderate across traits
    ])
    
    # Train model (in practice, you'd use much more data)
    logger.info("Training BERT model...")
    history = predictor.train_model(sample_texts, sample_labels, epochs=2)
    
    # Make predictions
    test_texts = ["I think vaccines are dangerous and the media lies to us"]
    predictions = predictor.predict_personality(test_texts)
    formatted_results = predictor.convert_predictions_to_your_format(predictions)
    
    logger.info(f"BERT predictions: {formatted_results}")
    
    return predictor

if __name__ == "__main__":
    main()