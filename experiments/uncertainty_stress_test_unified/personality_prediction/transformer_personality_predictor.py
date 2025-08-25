#!/usr/bin/env python3
"""
Transformer-based Personality Prediction from Twitter
Uses pre-trained language models (BERT/RoBERTa) with fine-tuning
"""

import json
import numpy as np
import time
import logging
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, 
    AutoModel,
    RobertaModel,
    RobertaTokenizer,
    BertModel,
    BertTokenizer,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwitterPersonalityDataset(Dataset):
    """Custom dataset for Twitter personality prediction."""
    
    def __init__(self, tweets_list: List[List[str]], labels: Optional[Dict[str, List[float]]] = None, 
                 tokenizer=None, max_length: int = 512):
        self.tweets_list = tweets_list
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.tweets_list)
    
    def __getitem__(self, idx):
        # Concatenate tweets into a single text
        tweets = self.tweets_list[idx]
        # Take first 10 tweets to fit in context window
        text = " [SEP] ".join(tweets[:10])
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        item = {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten()
        }
        
        # Add labels if available
        if self.labels:
            labels_tensor = torch.tensor([
                self.labels['political'][idx],
                self.labels['narcissism'][idx], 
                self.labels['conspiracy'][idx],
                self.labels['denialism'][idx]
            ], dtype=torch.float)
            item['labels'] = labels_tensor
            
        return item

class PersonalityPredictionHead(nn.Module):
    """Multi-task prediction head for personality traits."""
    
    def __init__(self, hidden_size: int, num_traits: int = 4):
        super().__init__()
        self.num_traits = num_traits
        
        # Shared layers
        self.shared = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Trait-specific heads (output 3 probabilities for low/medium/high)
        self.trait_heads = nn.ModuleList([
            nn.Linear(hidden_size // 4, 3) for _ in range(num_traits)
        ])
        
    def forward(self, x):
        # x shape: (batch_size, hidden_size)
        shared_features = self.shared(x)
        
        # Get predictions for each trait
        outputs = []
        for head in self.trait_heads:
            trait_logits = head(shared_features)
            trait_probs = torch.softmax(trait_logits, dim=-1)
            outputs.append(trait_probs)
            
        # Stack outputs: (batch_size, num_traits, 3)
        return torch.stack(outputs, dim=1)

class TransformerPersonalityPredictor:
    """Transformer-based personality predictor using pre-trained models."""
    
    def __init__(self, model_name: str = "roberta-base", device: str = None):
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Load tokenizer and base model
        if 'roberta' in model_name.lower():
            self.tokenizer = RobertaTokenizer.from_pretrained(model_name)
            self.base_model = RobertaModel.from_pretrained(model_name)
        else:  # Default to BERT
            self.tokenizer = BertTokenizer.from_pretrained(model_name)
            self.base_model = BertModel.from_pretrained(model_name)
            
        # Add prediction head
        self.prediction_head = PersonalityPredictionHead(self.base_model.config.hidden_size)
        
        # Move to device
        self.base_model.to(self.device)
        self.prediction_head.to(self.device)
        
        # Training components
        self.optimizer = None
        self.scheduler = None
        self.loss_fn = nn.CrossEntropyLoss()
        
    def prepare_training_data(self, twitter_data: Dict[str, List[str]], 
                            ground_truth: Optional[Dict] = None) -> Tuple[List[List[str]], Dict[str, List[float]]]:
        """Prepare data for training."""
        tweets_list = []
        labels = {'political': [], 'narcissism': [], 'conspiracy': [], 'denialism': []}
        
        for user_id, tweets in twitter_data.items():
            tweets_list.append(tweets)
            
            if ground_truth and user_id in ground_truth:
                gt = ground_truth[user_id]
                # Convert scores to categories (low/medium/high)
                labels['political'].append(self._score_to_category(gt.get('political', 5), scale='political'))
                labels['narcissism'].append(self._score_to_category(gt.get('narcissism', 4), scale='trait'))
                labels['conspiracy'].append(self._score_to_category(gt.get('conspiracy', 4), scale='trait'))
                labels['denialism'].append(self._score_to_category(gt.get('denialism', 4), scale='trait'))
            else:
                # Use default categories if no ground truth
                for trait in labels:
                    labels[trait].append(1)  # Default to medium
                    
        return tweets_list, labels
    
    def _score_to_category(self, score: float, scale: str = 'trait') -> int:
        """Convert continuous score to category index (0=low, 1=medium, 2=high)."""
        if scale == 'political':
            # Political scale is 1-11
            if score <= 4:
                return 0  # Low
            elif score <= 7:
                return 1  # Medium
            else:
                return 2  # High
        else:
            # Other traits are 1-7
            if score <= 3:
                return 0  # Low
            elif score <= 5:
                return 1  # Medium
            else:
                return 2  # High
    
    def _category_to_distribution(self, category: int) -> Dict[str, float]:
        """Convert category index to probability distribution."""
        if category == 0:
            return {"low_1to4": 0.8, "medium_5to7": 0.15, "high_8to11": 0.05}
        elif category == 1:
            return {"low_1to4": 0.15, "medium_5to7": 0.7, "high_8to11": 0.15}
        else:
            return {"low_1to4": 0.05, "medium_5to7": 0.15, "high_8to11": 0.8}
    
    def train(self, tweets_list: List[List[str]], labels: Dict[str, List[float]], 
              epochs: int = 3, batch_size: int = 8, learning_rate: float = 2e-5):
        """Train the model on labeled data."""
        logger.info(f"Training on {len(tweets_list)} users for {epochs} epochs")
        
        # Create dataset
        dataset = TwitterPersonalityDataset(tweets_list, labels, self.tokenizer)
        
        # Split into train/val
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Setup optimizer
        params = list(self.base_model.parameters()) + list(self.prediction_head.parameters())
        self.optimizer = torch.optim.AdamW(params, lr=learning_rate)
        
        # Setup scheduler
        total_steps = len(train_loader) * epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=int(0.1 * total_steps),
            num_training_steps=total_steps
        )
        
        # Training loop
        self.base_model.train()
        self.prediction_head.train()
        
        for epoch in range(epochs):
            train_loss = 0
            
            for batch in train_loader:
                # Move batch to device
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # Forward pass
                outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
                pooled_output = outputs.pooler_output
                predictions = self.prediction_head(pooled_output)
                
                # Calculate loss for each trait
                loss = 0
                for trait_idx in range(4):
                    trait_preds = predictions[:, trait_idx, :]
                    trait_labels = labels[:, trait_idx].long()
                    loss += self.loss_fn(trait_preds, trait_labels)
                
                loss = loss / 4  # Average across traits
                train_loss += loss.item()
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                self.optimizer.step()
                self.scheduler.step()
                
            # Validation
            val_loss = self.validate(val_loader)
            
            logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss/len(train_loader):.4f}, "
                       f"Val Loss: {val_loss:.4f}")
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate the model."""
        self.base_model.eval()
        self.prediction_head.eval()
        
        total_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
                pooled_output = outputs.pooler_output
                predictions = self.prediction_head(pooled_output)
                
                loss = 0
                for trait_idx in range(4):
                    trait_preds = predictions[:, trait_idx, :]
                    trait_labels = labels[:, trait_idx].long()
                    loss += self.loss_fn(trait_preds, trait_labels)
                
                total_loss += loss.item() / 4
                
        self.base_model.train()
        self.prediction_head.train()
        
        return total_loss / len(val_loader)
    
    def predict(self, tweets: List[str]) -> Dict[str, Any]:
        """Predict personality traits for a single user."""
        self.base_model.eval()
        self.prediction_head.eval()
        
        # Prepare input
        text = " [SEP] ".join(tweets[:10])
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=512,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
            pooled_output = outputs.pooler_output
            predictions = self.prediction_head(pooled_output)
        
        # Convert to distributions
        predictions_dict = {}
        confidence_scores = {}
        
        trait_names = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        for i, trait in enumerate(trait_names):
            probs = predictions[0, i, :].cpu().numpy()
            
            # Convert to our format
            predictions_dict[trait] = {
                "low_1to4": float(probs[0]),
                "medium_5to7": float(probs[1]),
                "high_8to11": float(probs[2])
            }
            
            # Calculate confidence based on entropy
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            max_entropy = -np.log(1/3)
            confidence_scores[trait] = float(1 - (entropy / max_entropy))
        
        return {
            "predictions": predictions_dict,
            "confidence_scores": confidence_scores,
            "method": f"Transformer ({self.model_name})",
            "model_type": "neural"
        }
    
    def predict_batch(self, user_tweets: Dict[str, List[str]], batch_size: int = 16) -> Dict[str, Dict]:
        """Predict for multiple users efficiently."""
        results = {}
        
        # Prepare all tweets
        user_ids = list(user_tweets.keys())
        tweets_list = [user_tweets[uid] for uid in user_ids]
        
        # Create dataset without labels
        dataset = TwitterPersonalityDataset(tweets_list, None, self.tokenizer)
        dataloader = DataLoader(dataset, batch_size=batch_size)
        
        self.base_model.eval()
        self.prediction_head.eval()
        
        all_predictions = []
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask)
                pooled_output = outputs.pooler_output
                predictions = self.prediction_head(pooled_output)
                
                all_predictions.append(predictions.cpu())
        
        # Concatenate all predictions
        all_predictions = torch.cat(all_predictions, dim=0)
        
        # Convert to results format
        trait_names = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        for idx, user_id in enumerate(user_ids):
            user_preds = all_predictions[idx]
            
            predictions_dict = {}
            confidence_scores = {}
            
            for i, trait in enumerate(trait_names):
                probs = user_preds[i].numpy()
                
                predictions_dict[trait] = {
                    "low_1to4": float(probs[0]),
                    "medium_5to7": float(probs[1]),
                    "high_8to11": float(probs[2])
                }
                
                entropy = -np.sum(probs * np.log(probs + 1e-10))
                max_entropy = -np.log(1/3)
                confidence_scores[trait] = float(1 - (entropy / max_entropy))
            
            results[user_id] = {
                "predictions": predictions_dict,
                "confidence_scores": confidence_scores,
                "method": f"Transformer ({self.model_name})"
            }
            
        return results

    def save_model(self, path: str):
        """Save the trained model."""
        torch.save({
            'base_model_state': self.base_model.state_dict(),
            'prediction_head_state': self.prediction_head.state_dict(),
            'model_name': self.model_name
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a trained model."""
        checkpoint = torch.load(path, map_location=self.device)
        self.base_model.load_state_dict(checkpoint['base_model_state'])
        self.prediction_head.load_state_dict(checkpoint['prediction_head_state'])
        logger.info(f"Model loaded from {path}")


def load_twitter_data(file_path: str) -> Dict[str, List[str]]:
    """Load Twitter dataset."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    twitter_data = {}
    for user_data in data:
        user_id = user_data["user_info"]["twitter_id"]
        tweets = [tweet["text"] for tweet in user_data["tweets"] if tweet.get("text", "").strip()]
        if len(tweets) >= 10:
            twitter_data[user_id] = tweets
    
    return twitter_data


def load_ground_truth(twitter_data_path: str) -> Dict[str, Dict[str, float]]:
    """Load ground truth from Twitter dataset annotations."""
    with open(twitter_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ground_truth = {}
    
    for user_data in data:
        user_id = user_data["user_info"]["twitter_id"]
        user_info = user_data["user_info"]
        
        # Extract ground truth values
        political = float(user_info.get("political", 5))
        
        # Average narcissism scores
        narcissism_scores = [float(user_info.get(f"narcissism_{i}", 4)) for i in range(1, 5)]
        narcissism = np.mean(narcissism_scores)
        
        # Average conspiracy scores
        conspiracy_scores = [float(user_info.get(f"conspiracy_{i}", 4)) for i in range(1, 6)]
        conspiracy = np.mean(conspiracy_scores)
        
        # Average denialism scores
        denialism_scores = [float(user_info.get(f"denialism_{i}", 4)) for i in range(1, 5)]
        denialism = np.mean(denialism_scores)
        
        ground_truth[user_id] = {
            'political': political,
            'narcissism': narcissism,
            'conspiracy': conspiracy,
            'denialism': denialism
        }
    
    return ground_truth


def main():
    """Demo transformer-based personality prediction."""
    # Load data
    twitter_file = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    twitter_data = load_twitter_data(twitter_file)
    ground_truth = load_ground_truth(twitter_file)
    
    logger.info(f"Loaded {len(twitter_data)} users with tweets")
    logger.info(f"Loaded {len(ground_truth)} users with ground truth")
    
    # Initialize model
    predictor = TransformerPersonalityPredictor(model_name="roberta-base")
    
    # Prepare training data (using subset for demo)
    train_users = list(twitter_data.keys())[:80]
    test_users = list(twitter_data.keys())[80:100]
    
    train_tweets = [twitter_data[uid] for uid in train_users]
    train_labels = {
        'political': [predictor._score_to_category(ground_truth[uid]['political'], 'political') for uid in train_users],
        'narcissism': [predictor._score_to_category(ground_truth[uid]['narcissism']) for uid in train_users],
        'conspiracy': [predictor._score_to_category(ground_truth[uid]['conspiracy']) for uid in train_users],
        'denialism': [predictor._score_to_category(ground_truth[uid]['denialism']) for uid in train_users]
    }
    
    # Train model
    logger.info("Training transformer model...")
    predictor.train(train_tweets, train_labels, epochs=2, batch_size=4)
    
    # Test on a few users
    logger.info("\nTesting on sample users...")
    test_results = []
    
    for user_id in test_users[:5]:
        tweets = twitter_data[user_id]
        result = predictor.predict(tweets)
        
        # Compare with ground truth
        gt = ground_truth[user_id]
        
        print(f"\nUser: {user_id}")
        print(f"Ground Truth - Political: {gt['political']:.1f}, Narcissism: {gt['narcissism']:.1f}")
        print(f"Predictions:")
        for trait, pred in result['predictions'].items():
            print(f"  {trait}: Low={pred['low_1to4']:.2f}, Med={pred['medium_5to7']:.2f}, High={pred['high_8to11']:.2f}")
        
        test_results.append({
            "user_id": user_id,
            "ground_truth": gt,
            "predictions": result
        })
    
    # Save results
    output_file = "transformer_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    logger.info(f"\nResults saved to {output_file}")
    
    # Save model
    predictor.save_model("transformer_personality_model.pt")


if __name__ == "__main__":
    main()