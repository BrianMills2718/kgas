#!/usr/bin/env python3
"""
REAL LLM-Assisted Alternative Methods
Uses actual LLM API calls with different prompting strategies.
"""

import json
import numpy as np
import time
import sys
import os
from typing import Dict, List, Any, Tuple
from pathlib import Path
import logging

# Add universal_model_tester to path
sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealChainOfThoughtPredictor:
    """Method 1: Real chain-of-thought reasoning with actual LLM calls."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
    
    def generate_cot_prompt(self, tweets: List[str], trait: str) -> str:
        """Generate chain-of-thought prompt for trait analysis."""
        
        # Sample tweets for analysis
        sample_tweets = tweets[:8] if len(tweets) > 8 else tweets
        tweets_text = "\n".join([f"Tweet {i+1}: {tweet}" for i, tweet in enumerate(sample_tweets)])
        
        trait_descriptions = {
            'political_orientation': {
                'name': 'Political Orientation',
                'low_desc': 'apolitical, avoids political topics, moderate views, non-partisan',
                'high_desc': 'strong political engagement, partisan language, ideological consistency, politically active'
            },
            'conspiracy_mentality': {
                'name': 'Conspiracy Mentality', 
                'low_desc': 'trusts official sources, accepts mainstream explanations, evidence-based thinking',
                'high_desc': 'questions official narratives, sees hidden agendas, alternative explanations, skeptical of authority'
            },
            'science_denialism': {
                'name': 'Science Denialism',
                'low_desc': 'trusts scientific consensus, evidence-based thinking, respects expertise',
                'high_desc': 'questions scientific authority, prefers alternative explanations, skeptical of experts'
            },
            'narcissism': {
                'name': 'Narcissism',
                'low_desc': 'modest, collaborative, acknowledges others, humble communication style',
                'high_desc': 'self-focused, grandiose language, seeks attention/admiration, superior attitude'
            }
        }
        
        trait_info = trait_descriptions[trait]
        
        prompt = f"""You are a psychology expert analyzing Twitter data for personality traits. Use step-by-step reasoning to assess {trait_info['name']}.

TWEETS TO ANALYZE:
{tweets_text}

STEP-BY-STEP ANALYSIS:

Step 1: Identify relevant indicators
- Look for language patterns, topics, and attitudes related to {trait_info['name']}
- Low {trait_info['name']}: {trait_info['low_desc']}
- High {trait_info['name']}: {trait_info['high_desc']}

Step 2: Evaluate evidence strength
- Count clear indicators for high vs low {trait_info['name']}
- Consider context, intensity, and consistency of language
- Note any contradictory evidence

Step 3: Make assessment
Based on your analysis, provide probability distributions for this person's {trait_info['name']} level.

IMPORTANT: Your response must be valid JSON with this exact structure:
{{
  "step1_indicators": "brief description of relevant patterns found",
  "step2_evidence": "analysis of evidence strength and consistency", 
  "step3_assessment": "final reasoning for probability distribution",
  "low_1to4": 0.X,
  "medium_5to7": 0.Y,
  "high_8to11": 0.Z,
  "confidence": 0.W
}}

Ensure probabilities sum to 1.0. Confidence should reflect certainty of assessment (0.0-1.0)."""

        return prompt
    
    def predict_with_real_cot(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Predict using real chain-of-thought LLM reasoning."""
        
        predictions = {}
        confidence_scores = {}
        reasoning = {}
        
        # JSON schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "step1_indicators": {"type": "string"},
                "step2_evidence": {"type": "string"},
                "step3_assessment": {"type": "string"},
                "low_1to4": {"type": "number", "minimum": 0, "maximum": 1},
                "medium_5to7": {"type": "number", "minimum": 0, "maximum": 1},
                "high_8to11": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["step1_indicators", "step2_evidence", "step3_assessment", "low_1to4", "medium_5to7", "high_8to11", "confidence"],
            "additionalProperties": False
        }
        
        for trait in self.traits:
            try:
                prompt = self.generate_cot_prompt(tweets, trait)
                
                # Make real LLM call
                result = self.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    model="gemini_2_5_flash",
                    schema=schema
                )
                
                # Parse response
                response_content = result["response"].choices[0].message.content
                cot_result = json.loads(response_content)
                
                # Normalize probabilities to ensure they sum to 1
                total = cot_result["low_1to4"] + cot_result["medium_5to7"] + cot_result["high_8to11"]
                if total > 0:
                    predictions[trait] = {
                        "low_1to4": cot_result["low_1to4"] / total,
                        "medium_5to7": cot_result["medium_5to7"] / total,
                        "high_8to11": cot_result["high_8to11"] / total
                    }
                else:
                    predictions[trait] = {"low_1to4": 0.6, "medium_5to7": 0.3, "high_8to11": 0.1}
                
                confidence_scores[trait] = cot_result.get("confidence", 0.5)
                reasoning[trait] = {
                    "step1": cot_result.get("step1_indicators", ""),
                    "step2": cot_result.get("step2_evidence", ""),
                    "step3": cot_result.get("step3_assessment", "")
                }
                
            except Exception as e:
                logger.error(f"Chain-of-thought failed for {trait}: {e}")
                # Fallback values
                predictions[trait] = {"low_1to4": 0.5, "medium_5to7": 0.4, "high_8to11": 0.1}
                confidence_scores[trait] = 0.3
                reasoning[trait] = {"error": str(e)}
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "Real Chain-of-Thought LLM",
            "reasoning": reasoning,
            "model_used": result.get("model_used", "unknown")
        }


class RealFewShotPredictor:
    """Method 2: Real few-shot learning with actual LLM calls."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
    
    def generate_few_shot_prompt(self, tweets: List[str], trait: str) -> str:
        """Generate few-shot prompt with personality examples."""
        
        trait_examples = {
            'political_orientation': [
                {
                    'tweets': 'Voted early today! | Every citizen should participate in democracy | Policy discussions are important for our future',
                    'label': 'medium',
                    'reasoning': 'Shows civic engagement but balanced, non-partisan approach'
                },
                {
                    'tweets': 'TRUMP 2024! MAGA! | These liberals are destroying our country | The deep state is real, wake up America!',
                    'label': 'high', 
                    'reasoning': 'Highly partisan language, strong political identity, conspiracy elements'
                },
                {
                    'tweets': 'Beautiful sunset today | Coffee shop wifi is great | Just finished reading a good book',
                    'label': 'low',
                    'reasoning': 'No political content, focused on personal life and daily activities'
                }
            ],
            'conspiracy_mentality': [
                {
                    'tweets': 'Wake up sheeple! The truth is hidden! | Question everything they tell you | They dont want us to know the real agenda',
                    'label': 'high',
                    'reasoning': 'Classic conspiracy language, distrust of authority, alternative explanations'
                },
                {
                    'tweets': 'According to the latest research | Experts recommend this approach | The data clearly shows the trend',
                    'label': 'low', 
                    'reasoning': 'Trusts expert sources, evidence-based thinking, accepts mainstream information'
                },
                {
                    'tweets': 'Something seems off about this story | Not sure what to believe anymore | Need to investigate this further',
                    'label': 'medium',
                    'reasoning': 'Some skepticism but seeking information rather than rejecting authority'
                }
            ],
            'science_denialism': [
                {
                    'tweets': 'Natural immunity is superior | Big pharma just wants profits | Do your own research, dont trust so-called experts',
                    'label': 'high',
                    'reasoning': 'Rejects scientific consensus, prefers alternative explanations, distrust of institutions'
                },
                {
                    'tweets': 'New study published in Nature shows | Peer review process ensures quality | Evidence-based medicine saves lives',
                    'label': 'low',
                    'reasoning': 'Trusts scientific process, respects peer review, evidence-based approach'
                },
                {
                    'tweets': 'Science is always evolving | More research needed on this topic | Good to question but need evidence',
                    'label': 'medium',
                    'reasoning': 'Accepts scientific method but acknowledges limitations and uncertainty'
                }
            ],
            'narcissism': [
                {
                    'tweets': 'I am absolutely brilliant at this | Everyone should admire my work | I deserve special recognition for my achievements',
                    'label': 'high',
                    'reasoning': 'Grandiose self-image, seeks admiration, sense of entitlement'
                },
                {
                    'tweets': 'Thanks to my team for the help | We accomplished this together | Always learning from others experiences',
                    'label': 'low',
                    'reasoning': 'Collaborative approach, acknowledges others, modest and grateful'
                },
                {
                    'tweets': 'Pretty proud of my work today | I think I handled that well | My project turned out nice',
                    'label': 'medium',
                    'reasoning': 'Healthy self-regard without grandiosity, balanced self-assessment'
                }
            ]
        }
        
        examples = trait_examples[trait]
        
        prompt = f"""You are a psychology expert using few-shot learning to classify personality traits. Learn from these examples then classify new data.

TRAIT: {trait.replace('_', ' ').title()}

TRAINING EXAMPLES:

Example 1:
Tweets: {examples[0]['tweets']}
Classification: {examples[0]['label']}
Reasoning: {examples[0]['reasoning']}

Example 2:
Tweets: {examples[1]['tweets']}
Classification: {examples[1]['label']}
Reasoning: {examples[1]['reasoning']}

Example 3:
Tweets: {examples[2]['tweets']}
Classification: {examples[2]['label']}
Reasoning: {examples[2]['reasoning']}

Now classify these new tweets using the same approach:

TWEETS TO CLASSIFY:
{' | '.join(tweets[:12])}

Provide your analysis in this exact JSON format:
{{
  "classification": "low/medium/high",
  "reasoning": "explanation based on examples above",
  "confidence_explanation": "why you are confident/uncertain",
  "low_1to4": 0.X,
  "medium_5to7": 0.Y,
  "high_8to11": 0.Z,
  "confidence": 0.W
}}

Ensure probabilities sum to 1.0."""

        return prompt
    
    def predict_with_real_few_shot(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Predict using real few-shot LLM learning."""
        
        predictions = {}
        confidence_scores = {}
        classifications = {}
        
        # JSON schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "classification": {"type": "string", "enum": ["low", "medium", "high"]},
                "reasoning": {"type": "string"},
                "confidence_explanation": {"type": "string"},
                "low_1to4": {"type": "number", "minimum": 0, "maximum": 1},
                "medium_5to7": {"type": "number", "minimum": 0, "maximum": 1},
                "high_8to11": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["classification", "reasoning", "confidence_explanation", "low_1to4", "medium_5to7", "high_8to11", "confidence"],
            "additionalProperties": False
        }
        
        for trait in self.traits:
            try:
                prompt = self.generate_few_shot_prompt(tweets, trait)
                
                # Make real LLM call
                result = self.llm_client.complete(
                    messages=[{"role": "user", "content": prompt}],
                    model="gemini_2_5_flash",
                    schema=schema
                )
                
                # Parse response
                response_content = result["response"].choices[0].message.content
                fs_result = json.loads(response_content)
                
                # Normalize probabilities
                total = fs_result["low_1to4"] + fs_result["medium_5to7"] + fs_result["high_8to11"]
                if total > 0:
                    predictions[trait] = {
                        "low_1to4": fs_result["low_1to4"] / total,
                        "medium_5to7": fs_result["medium_5to7"] / total,
                        "high_8to11": fs_result["high_8to11"] / total
                    }
                else:
                    predictions[trait] = {"low_1to4": 0.6, "medium_5to7": 0.3, "high_8to11": 0.1}
                
                confidence_scores[trait] = fs_result.get("confidence", 0.5)
                classifications[trait] = {
                    "label": fs_result.get("classification", "medium"),
                    "reasoning": fs_result.get("reasoning", ""),
                    "confidence_explanation": fs_result.get("confidence_explanation", "")
                }
                
            except Exception as e:
                logger.error(f"Few-shot failed for {trait}: {e}")
                # Fallback values
                predictions[trait] = {"low_1to4": 0.5, "medium_5to7": 0.4, "high_8to11": 0.1}
                confidence_scores[trait] = 0.3
                classifications[trait] = {"error": str(e)}
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "Real Few-Shot LLM",
            "classifications": classifications,
            "model_used": result.get("model_used", "unknown")
        }


class RealEnsembleLLMPredictor:
    """Method 3: Real ensemble of different LLM models/strategies."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        self.models = ["gemini_2_5_flash", "o4_mini", "claude_haiku_3_5"]
    
    def generate_direct_prompt(self, tweets: List[str], trait: str) -> str:
        """Generate direct classification prompt."""
        
        trait_descriptions = {
            'political_orientation': 'Political engagement and partisan language',
            'conspiracy_mentality': 'Tendency to believe in conspiracy theories and distrust authority',
            'science_denialism': 'Rejection of scientific consensus and expertise',
            'narcissism': 'Self-focused behavior and grandiose self-image'
        }
        
        prompt = f"""Analyze these tweets for {trait_descriptions[trait]}:

TWEETS:
{chr(10).join(tweets[:10])}

Rate the person's {trait.replace('_', ' ')} level as low (1-4), medium (5-7), or high (8-11).

Respond in JSON format:
{{
  "analysis": "brief explanation of key indicators",
  "low_1to4": 0.X,
  "medium_5to7": 0.Y,
  "high_8to11": 0.Z,
  "confidence": 0.W
}}

Probabilities must sum to 1.0."""

        return prompt
    
    def predict_with_real_ensemble(self, user_id: str, tweets: List[str]) -> Dict[str, Any]:
        """Predict using real ensemble of LLM models."""
        
        # JSON schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "analysis": {"type": "string"},
                "low_1to4": {"type": "number", "minimum": 0, "maximum": 1},
                "medium_5to7": {"type": "number", "minimum": 0, "maximum": 1},
                "high_8to11": {"type": "number", "minimum": 0, "maximum": 1},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["analysis", "low_1to4", "medium_5to7", "high_8to11", "confidence"],
            "additionalProperties": False
        }
        
        model_results = {}
        
        # Get predictions from multiple models
        for model in self.models:
            model_predictions = {}
            
            for trait in self.traits:
                try:
                    prompt = self.generate_direct_prompt(tweets, trait)
                    
                    # Make real LLM call with specific model
                    result = self.llm_client.complete(
                        messages=[{"role": "user", "content": prompt}],
                        model=model,
                        schema=schema
                    )
                    
                    # Parse response
                    response_content = result["response"].choices[0].message.content
                    model_result = json.loads(response_content)
                    
                    # Normalize probabilities
                    total = model_result["low_1to4"] + model_result["medium_5to7"] + model_result["high_8to11"]
                    if total > 0:
                        model_predictions[trait] = {
                            "low_1to4": model_result["low_1to4"] / total,
                            "medium_5to7": model_result["medium_5to7"] / total,
                            "high_8to11": model_result["high_8to11"] / total,
                            "confidence": model_result.get("confidence", 0.5),
                            "analysis": model_result.get("analysis", "")
                        }
                    else:
                        model_predictions[trait] = {
                            "low_1to4": 0.6, "medium_5to7": 0.3, "high_8to11": 0.1,
                            "confidence": 0.3, "analysis": "fallback"
                        }
                    
                except Exception as e:
                    logger.error(f"Ensemble model {model} failed for {trait}: {e}")
                    model_predictions[trait] = {
                        "low_1to4": 0.5, "medium_5to7": 0.4, "high_8to11": 0.1,
                        "confidence": 0.2, "analysis": f"error: {e}"
                    }
            
            model_results[model] = model_predictions
        
        # Ensemble the results with confidence weighting
        predictions = {}
        confidence_scores = {}
        
        for trait in self.traits:
            # Get valid predictions
            valid_predictions = []
            weights = []
            
            for model, model_preds in model_results.items():
                if trait in model_preds and "error" not in model_preds[trait].get("analysis", ""):
                    valid_predictions.append(model_preds[trait])
                    weights.append(model_preds[trait]["confidence"])
            
            if valid_predictions:
                # Weighted average
                total_weight = sum(weights)
                if total_weight > 0:
                    weights = [w / total_weight for w in weights]
                else:
                    weights = [1/len(valid_predictions)] * len(valid_predictions)
                
                avg_low = sum(p["low_1to4"] * w for p, w in zip(valid_predictions, weights))
                avg_medium = sum(p["medium_5to7"] * w for p, w in zip(valid_predictions, weights))
                avg_high = sum(p["high_8to11"] * w for p, w in zip(valid_predictions, weights))
                
                # Normalize final result
                total = avg_low + avg_medium + avg_high
                predictions[trait] = {
                    "low_1to4": avg_low / total,
                    "medium_5to7": avg_medium / total,
                    "high_8to11": avg_high / total
                }
                
                confidence_scores[trait] = np.mean([p["confidence"] for p in valid_predictions])
            else:
                # All models failed
                predictions[trait] = {"low_1to4": 0.5, "medium_5to7": 0.4, "high_8to11": 0.1}
                confidence_scores[trait] = 0.2
        
        return {
            "predictions": predictions,
            "confidence_scores": confidence_scores,
            "method": "Real Ensemble LLM",
            "model_results": model_results,
            "models_used": list(model_results.keys()),
            "ensemble_variance": self.calculate_ensemble_variance(model_results)
        }
    
    def calculate_ensemble_variance(self, model_results: Dict) -> Dict[str, float]:
        """Calculate variance across ensemble models."""
        variances = {}
        
        for trait in self.traits:
            values = []
            for model_result in model_results.values():
                if trait in model_result and "error" not in model_result[trait].get("analysis", ""):
                    result = model_result[trait]
                    # Convert to single value for variance calculation
                    value = (result["low_1to4"] * 2.5 + result["medium_5to7"] * 6.0 + result["high_8to11"] * 9.5)
                    values.append(value)
            
            variances[trait] = np.var(values) if len(values) > 1 else 0.0
        
        return variances


class RealLLMComparison:
    """Framework to compare real LLM-assisted methods."""
    
    def __init__(self, baseline_file: str):
        self.baseline_file = baseline_file
        self.traits = ['political_orientation', 'conspiracy_mentality', 'science_denialism', 'narcissism']
        
        # Load baseline data and Twitter data
        with open(baseline_file, 'r') as f:
            self.baseline_data = json.load(f)
        
        self.twitter_data = self.load_twitter_data()
        
        # Initialize real LLM client and predictors
        self.llm_client = UniversalModelClient()
        self.cot_predictor = RealChainOfThoughtPredictor(self.llm_client)
        self.few_shot_predictor = RealFewShotPredictor(self.llm_client)
        self.ensemble_predictor = RealEnsembleLLMPredictor(self.llm_client)
        
    def load_twitter_data(self) -> Dict[str, List[str]]:
        """Load Twitter data."""
        data_file = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
        
        if not Path(data_file).exists():
            logger.error(f"Twitter data not found: {data_file}")
            return {}
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        twitter_data = {}
        for user_data in data:
            user_id = user_data["user_info"]["twitter_id"]
            tweets = [tweet["text"] for tweet in user_data["tweets"] if tweet.get("text", "").strip()]
            if len(tweets) >= 10:
                twitter_data[user_id] = tweets
        
        logger.info(f"Loaded {len(twitter_data)} users with Twitter data")
        return twitter_data
    
    def get_baseline_results(self, user_id: str) -> Dict[str, Any]:
        """Extract baseline results for comparison."""
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
                        avg_dist = {}
                        for key in ["low_1to4", "medium_5to7", "high_8to11"]:
                            avg_dist[key] = np.mean([pred.get(key, 0) for pred in trait_predictions])
                        predictions[trait] = avg_dist
                        
                        probs = list(avg_dist.values())
                        entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
                        confidence_scores[trait] = 1 - (entropy / np.log(3))
                
                return {
                    "predictions": predictions,
                    "confidence_scores": confidence_scores,
                    "method": "Likelihood Ratio (Baseline)"
                }
        return None
    
    def calculate_method_disagreement(self, results_list: List[Dict]) -> Dict[str, float]:
        """Calculate disagreement between methods."""
        disagreement_scores = {}
        
        for trait in self.traits:
            values = []
            for result in results_list:
                if trait in result["predictions"]:
                    dist = result["predictions"][trait]
                    value = (dist.get("low_1to4", 0) * 2.5 + 
                           dist.get("medium_5to7", 0) * 6.0 + 
                           dist.get("high_8to11", 0) * 9.5)
                    values.append(value)
            
            if len(values) >= 2:
                disagreement_scores[trait] = np.std(values) / (np.mean(values) + 1e-10)
            else:
                disagreement_scores[trait] = 0.0
        
        return disagreement_scores
    
    def run_real_llm_comparison(self, max_users: int = 5) -> Dict:
        """Run comparison with real LLM methods."""
        logger.info(f"Running REAL LLM methods comparison on {max_users} users...")
        
        # Find users with both baseline and Twitter data
        baseline_users = set(result["user_id"] for result in self.baseline_data["individual_results"])
        twitter_users = set(self.twitter_data.keys())
        common_users = list(baseline_users & twitter_users)[:max_users]
        
        if not common_users:
            logger.error("No users found with both datasets")
            return {}
        
        results = []
        processing_times = {"baseline": [], "real_cot": [], "real_few_shot": [], "real_ensemble": []}
        
        for i, user_id in enumerate(common_users):
            logger.info(f"Processing user {i+1}/{len(common_users)}: {user_id}")
            
            tweets = self.twitter_data[user_id][:30]  # Limit for LLM processing
            
            # Run all methods
            start_time = time.time()
            baseline_result = self.get_baseline_results(user_id)
            processing_times["baseline"].append(time.time() - start_time)
            
            start_time = time.time()
            cot_result = self.cot_predictor.predict_with_real_cot(user_id, tweets)
            processing_times["real_cot"].append(time.time() - start_time)
            
            start_time = time.time()
            few_shot_result = self.few_shot_predictor.predict_with_real_few_shot(user_id, tweets)
            processing_times["real_few_shot"].append(time.time() - start_time)
            
            start_time = time.time()
            ensemble_result = self.ensemble_predictor.predict_with_real_ensemble(user_id, tweets)
            processing_times["real_ensemble"].append(time.time() - start_time)
            
            # Calculate disagreement
            method_results = [baseline_result, cot_result, few_shot_result, ensemble_result]
            disagreement = self.calculate_method_disagreement(method_results)
            
            user_result = {
                "user_id": user_id,
                "tweets_count": len(tweets),
                "baseline": baseline_result,
                "real_chain_of_thought": cot_result,
                "real_few_shot": few_shot_result,
                "real_ensemble": ensemble_result,
                "disagreement": disagreement
            }
            
            results.append(user_result)
        
        # Generate report
        report = {
            "summary": {
                "users_compared": len(results),
                "methods": ["Likelihood Ratio", "Real Chain-of-Thought LLM", "Real Few-Shot LLM", "Real Ensemble LLM"],
                "real_llm_calls": True,
                "api_model": "gemini-2.5-flash"
            },
            "processing_times": {
                method: {"mean": np.mean(times), "std": np.std(times)}
                for method, times in processing_times.items()
            },
            "disagreement_stats": {},
            "method_descriptions": {
                "baseline": "Bayesian likelihood ratio with LLM probability distributions",
                "real_chain_of_thought": "Step-by-step LLM reasoning with actual API calls to Gemini", 
                "real_few_shot": "Few-shot LLM learning with personality examples via API",
                "real_ensemble": "Ensemble of multiple LLM models (Gemini, GPT, Claude) via API"
            }
        }
        
        # Calculate disagreement statistics
        for trait in self.traits:
            disagreements = [result["disagreement"][trait] for result in results]
            report["disagreement_stats"][trait] = {
                "mean": np.mean(disagreements),
                "std": np.std(disagreements)
            }
        
        return {"results": results, "report": report}


def main():
    """Run real LLM-assisted methods comparison."""
    baseline_file = "../uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json"
    
    if not Path(baseline_file).exists():
        logger.error(f"Baseline file not found: {baseline_file}")
        return False
    
    try:
        logger.info("🚀 Starting REAL LLM-ASSISTED methods comparison...")
        comparator = RealLLMComparison(baseline_file)
        
        results = comparator.run_real_llm_comparison(max_users=5)
        
        if not results:
            logger.error("No results generated")
            return False
        
        report = results["report"]
        
        print("\n" + "="*70)
        print("🎯 REAL LLM-ASSISTED METHODS COMPARISON")
        print("="*70)
        
        print(f"\n📈 Users Analyzed: {report['summary']['users_compared']}")
        print(f"🧠 Traits: {', '.join(comparator.traits)}")
        print(f"⚡ Methods: {', '.join(report['summary']['methods'])}")
        print(f"🤖 Real LLM Calls: {report['summary']['real_llm_calls']}")
        print(f"🔥 API Model: {report['summary']['api_model']}")
        
        print("\n⏱️  PROCESSING TIMES:")
        for method, stats in report["processing_times"].items():
            print(f"   {method:18}: {stats['mean']:.2f}s ± {stats['std']:.2f}s")
        
        print("\n🎲 METHOD DISAGREEMENT (Higher = More Diverse):")
        for trait, stats in report["disagreement_stats"].items():
            print(f"   {trait:20}: {stats['mean']:.3f} ± {stats['std']:.3f}")
        
        print("\n🔬 METHOD DESCRIPTIONS:")
        for method, description in report["method_descriptions"].items():
            print(f"   {method.upper()}:")
            print(f"     {description}")
        
        # Show example reasoning
        if results["results"]:
            example = results["results"][0]
            print(f"\n📊 Example LLM Reasoning for {example['user_id']}:")
            
            if "reasoning" in example["real_chain_of_thought"]:
                cot_reasoning = example["real_chain_of_thought"]["reasoning"]
                trait = list(cot_reasoning.keys())[0]
                if "step1" in cot_reasoning[trait]:
                    print(f"\n   CHAIN-OF-THOUGHT ({trait}):")
                    print(f"     Step 1: {cot_reasoning[trait]['step1'][:100]}...")
                    print(f"     Step 3: {cot_reasoning[trait]['step3'][:100]}...")
        
        # Save results
        output_file = "real_llm_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        print("\n✅ REAL LLM-assisted methods comparison completed!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Real LLM comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()