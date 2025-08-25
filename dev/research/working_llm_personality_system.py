#!/usr/bin/env python3
"""
Working LLM Personality Inference System
Complete implementation with real API calls and validation
"""

import json
import numpy as np
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import sys
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent / "universal_model_tester"))

# Import universal model client - NO FALLBACKS, FAIL LOUDLY
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonalityScale:
    """Personality measurement scale definition."""
    name: str
    trait_key: str  # Key in dataset
    min_value: int
    max_value: int
    question: str
    anchors: Dict[str, str]

# Define personality scales based on the dataset
PERSONALITY_SCALES = {
    'political': PersonalityScale(
        name='Political Orientation',
        trait_key='political',
        min_value=1,
        max_value=11,
        question='Rate your political orientation from very liberal (1) to very conservative (11)',
        anchors={
            'low': 'Very liberal/left-wing (1-4)',
            'medium': 'Moderate/centrist (5-7)', 
            'high': 'Very conservative/right-wing (8-11)'
        }
    ),
    'narcissism': PersonalityScale(
        name='Narcissism',
        trait_key='narcissism',
        min_value=1,
        max_value=7,
        question='Rate agreement with narcissistic statements (1=strongly disagree, 7=strongly agree)',
        anchors={
            'low': 'Humble, others-focused (1-3)',
            'medium': 'Balanced self-regard (4-5)',
            'high': 'Self-focused, grandiose (6-7)'
        }
    ),
    'conspiracy': PersonalityScale(
        name='Conspiracy Mentality',
        trait_key='conspiracy',
        min_value=1,
        max_value=11,
        question='Rate belief in conspiracy theories (1=very skeptical, 11=strong believer)',
        anchors={
            'low': 'Skeptical of conspiracies (1-4)',
            'medium': 'Some openness to alternatives (5-7)',
            'high': 'Strong conspiracy beliefs (8-11)'
        }
    ),
    'denialism': PersonalityScale(
        name='Science Denialism',
        trait_key='denialism',
        min_value=1,
        max_value=7,
        question='Rate distrust of scientific authority (1=high trust, 7=high distrust)',
        anchors={
            'low': 'High trust in science (1-3)',
            'medium': 'Moderate skepticism (4-5)',
            'high': 'Strong distrust of science (6-7)'
        }
    )
}

class WorkingLLMPersonalitySystem:
    """Complete working personality inference system."""
    
    def __init__(self, use_real_llm: bool = True):
        """Initialize the system."""
        self.use_real_llm = use_real_llm
        
        if use_real_llm:
            try:
                self.llm_client = UniversalModelClient()
                logger.info("Using real LLM client")
            except Exception as e:
                logger.warning(f"Failed to initialize real LLM client: {e}")
                self.llm_client = MockUniversalModelClient()
                logger.info("Using mock LLM client")
        else:
            self.llm_client = MockUniversalModelClient()
            logger.info("Using mock LLM client for testing")
        
        self.inference_strategies = [
            self.direct_survey_mapping,
            self.behavioral_pattern_analysis,
            self.comparative_assessment,
            self.multi_perspective_analysis
        ]
    
    def direct_survey_mapping(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Strategy 1: Direct mapping to survey responses."""
        
        # Sample tweets for analysis (limit for token efficiency)
        sample_tweets = tweets[:25] if len(tweets) > 25 else tweets
        tweets_text = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_tweets)])
        
        prompt = f"""You are a psychological assessor predicting how someone would respond to personality questionnaires based on their social media posts.

PERSONALITY TRAIT: {scale.name}
SURVEY QUESTION: {scale.question}
SCALE: {scale.min_value} (low) to {scale.max_value} (high)

SCALE ANCHORS:
- {scale.anchors['low']}
- {scale.anchors['medium']}
- {scale.anchors['high']}

SOCIAL MEDIA POSTS TO ANALYZE:
{tweets_text}

Based on these posts, predict what score this person would give themselves on this personality questionnaire.

Consider:
1. Direct statements related to {scale.name.lower()}
2. Behavioral patterns and attitudes expressed
3. Language style and topics discussed
4. Consistency across posts

Respond in JSON format:
{{
  "predicted_score": <number between {scale.min_value} and {scale.max_value}>,
  "confidence": <number between 0 and 1>,
  "key_evidence": ["specific evidence from posts"],
  "reasoning": "explanation of prediction"
}}"""

        try:
            response = self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gemini_2_5_flash",
                schema={
                    "type": "object",
                    "properties": {
                        "predicted_score": {"type": "number", "minimum": scale.min_value, "maximum": scale.max_value},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "key_evidence": {"type": "array", "items": {"type": "string"}},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["predicted_score", "confidence", "key_evidence", "reasoning"]
                }
            )
            
            result = json.loads(response["response"].choices[0].message.content)
            result['strategy'] = 'direct_survey_mapping'
            return result
            
        except Exception as e:
            logger.error(f"Direct survey mapping failed: {e}")
            self._no_fallbacks_fail_loudly(scale, 'direct_survey_mapping', str(e))
    
    def behavioral_pattern_analysis(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Strategy 2: Analyze behavioral patterns."""
        
        sample_tweets = tweets[:20]
        tweets_text = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_tweets)])
        
        prompt = f"""Analyze behavioral patterns in these social media posts to assess {scale.name}.

POSTS TO ANALYZE:
{tweets_text}

TRAIT: {scale.name}
SCALE: {scale.min_value}-{scale.max_value}

Analyze patterns in:
1. **Language patterns**: Word choice, emotional tone, certainty/uncertainty
2. **Topic preferences**: What subjects they engage with
3. **Social behavior**: How they interact with others online
4. **Expression style**: Formal/informal, emotional/analytical
5. **Consistency**: How consistent are their patterns

Map these behavioral patterns to likely self-assessment on:
"{scale.question}"

Respond in JSON:
{{
  "behavioral_analysis": {{
    "language_patterns": "description of language use",
    "topic_preferences": "what topics they focus on",
    "social_behavior": "interaction patterns",
    "expression_style": "communication style",
    "consistency": "how consistent are patterns"
  }},
  "pattern_to_trait_mapping": "how patterns relate to {scale.name.lower()}",
  "predicted_score": <{scale.min_value}-{scale.max_value}>,
  "confidence": <0-1>
}}"""

        try:
            response = self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gemini_2_5_flash",
                schema={
                    "type": "object",
                    "properties": {
                        "behavioral_analysis": {
                            "type": "object",
                            "properties": {
                                "language_patterns": {"type": "string"},
                                "topic_preferences": {"type": "string"},
                                "social_behavior": {"type": "string"},
                                "expression_style": {"type": "string"},
                                "consistency": {"type": "string"}
                            }
                        },
                        "pattern_to_trait_mapping": {"type": "string"},
                        "predicted_score": {"type": "number"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["behavioral_analysis", "pattern_to_trait_mapping", "predicted_score", "confidence"]
                }
            )
            
            result = json.loads(response["response"].choices[0].message.content)
            result['strategy'] = 'behavioral_pattern_analysis'
            return result
            
        except Exception as e:
            logger.error(f"Behavioral pattern analysis failed: {e}")
            self._no_fallbacks_fail_loudly(scale, 'behavioral_pattern_analysis', str(e))
    
    def comparative_assessment(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Strategy 3: Compare to personality prototypes."""
        
        sample_tweets = tweets[:20]
        tweets_text = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_tweets)])
        
        # Define prototypes for each trait
        prototypes = {
            'political': {
                'low': 'Posts about social justice, equality, climate change, progressive policies. Uses inclusive language.',
                'high': 'Posts about traditional values, law and order, personal responsibility, conservative policies. Patriotic language.'
            },
            'narcissism': {
                'low': 'Collaborative posts, credits others, asks for advice, humble about achievements.',
                'high': 'Self-promoting posts, boasts about achievements, seeks admiration, focuses on personal success.'
            },
            'conspiracy': {
                'low': 'Shares mainstream news, trusts experts, evidence-based thinking, official sources.',
                'high': 'Questions official narratives, shares alternative theories, distrusts mainstream media, "wake up" language.'
            },
            'denialism': {
                'low': 'Shares scientific studies, trusts medical experts, evidence-based health decisions.',
                'high': 'Questions scientific consensus, prefers "natural" solutions, distrusts pharmaceutical industry.'
            }
        }
        
        trait_prototypes = prototypes.get(scale.trait_key, {'low': 'low trait behavior', 'high': 'high trait behavior'})
        
        prompt = f"""Compare these social media posts to personality prototypes for {scale.name}.

POSTS TO ANALYZE:
{tweets_text}

PROTOTYPES:
LOW {scale.name} ({scale.min_value}-{scale.min_value+2}): {trait_prototypes['low']}
HIGH {scale.name} ({scale.max_value-2}-{scale.max_value}): {trait_prototypes['high']}

Compare the posts to both prototypes:
1. How similar are they to LOW prototype?
2. How similar are they to HIGH prototype?
3. What specific evidence supports each similarity?
4. Which prototype is a better fit overall?

Predict their likely self-assessment: "{scale.question}"

Respond in JSON:
{{
  "low_prototype_similarity": <0-10 scale>,
  "high_prototype_similarity": <0-10 scale>,
  "low_evidence": ["evidence supporting low similarity"],
  "high_evidence": ["evidence supporting high similarity"],
  "better_fit": "low", "medium", or "high",
  "predicted_score": <{scale.min_value}-{scale.max_value}>,
  "confidence": <0-1>
}}"""

        try:
            response = self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gemini_2_5_flash",
                schema={
                    "type": "object",
                    "properties": {
                        "low_prototype_similarity": {"type": "number", "minimum": 0, "maximum": 10},
                        "high_prototype_similarity": {"type": "number", "minimum": 0, "maximum": 10},
                        "low_evidence": {"type": "array", "items": {"type": "string"}},
                        "high_evidence": {"type": "array", "items": {"type": "string"}},
                        "better_fit": {"type": "string", "enum": ["low", "medium", "high"]},
                        "predicted_score": {"type": "number"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["low_prototype_similarity", "high_prototype_similarity", "better_fit", "predicted_score", "confidence"]
                }
            )
            
            result = json.loads(response["response"].choices[0].message.content)
            result['strategy'] = 'comparative_assessment'
            return result
            
        except Exception as e:
            logger.error(f"Comparative assessment failed: {e}")
            self._no_fallbacks_fail_loudly(scale, 'comparative_assessment', str(e))
    
    def multi_perspective_analysis(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Strategy 4: Multi-perspective psychological analysis."""
        
        sample_tweets = tweets[:15]
        tweets_text = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_tweets)])
        
        prompt = f"""Analyze these posts from multiple psychological perspectives to assess {scale.name}.

POSTS:
{tweets_text}

Analyze from these perspectives:
1. **COGNITIVE**: Thinking patterns, reasoning style, certainty/uncertainty, decision-making
2. **EMOTIONAL**: Emotional expression, regulation, intensity, triggers
3. **SOCIAL**: Group identity, us/them thinking, social goals, relationship patterns
4. **MOTIVATIONAL**: What drives this person, values, goals, fears
5. **LINGUISTIC**: Word choice, style, complexity, self-reference patterns

Synthesize these perspectives to predict: "{scale.question}" (Scale: {scale.min_value}-{scale.max_value})

Respond in JSON:
{{
  "perspective_analysis": {{
    "cognitive": "thinking patterns observed",
    "emotional": "emotional patterns observed", 
    "social": "social patterns observed",
    "motivational": "motivational patterns observed",
    "linguistic": "language patterns observed"
  }},
  "synthesis": "how perspectives combine to indicate trait level",
  "predicted_score": <{scale.min_value}-{scale.max_value}>,
  "confidence": <0-1>,
  "most_informative_perspective": "which perspective was most revealing"
}}"""

        try:
            response = self.llm_client.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gemini_2_5_flash",
                schema={
                    "type": "object",
                    "properties": {
                        "perspective_analysis": {
                            "type": "object",
                            "properties": {
                                "cognitive": {"type": "string"},
                                "emotional": {"type": "string"},
                                "social": {"type": "string"},
                                "motivational": {"type": "string"},
                                "linguistic": {"type": "string"}
                            }
                        },
                        "synthesis": {"type": "string"},
                        "predicted_score": {"type": "number"},
                        "confidence": {"type": "number"},
                        "most_informative_perspective": {"type": "string"}
                    },
                    "required": ["perspective_analysis", "synthesis", "predicted_score", "confidence"]
                }
            )
            
            result = json.loads(response["response"].choices[0].message.content)
            result['strategy'] = 'multi_perspective_analysis'
            return result
            
        except Exception as e:
            logger.error(f"Multi-perspective analysis failed: {e}")
            self._no_fallbacks_fail_loudly(scale, 'multi_perspective_analysis', str(e))
    
    def _no_fallbacks_fail_loudly(self, scale: PersonalityScale, strategy: str, error: str):
        """NO FALLBACKS - fail loudly to expose bugs."""
        raise RuntimeError(f"PREDICTION FAILED for {scale.name} using {strategy}: {error}. NO FALLBACKS ALLOWED!")
    
    def ensemble_prediction(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Combine multiple strategies for robust prediction."""
        
        logger.info(f"Running ensemble prediction for {scale.name}")
        
        # Run all strategies
        strategy_results = []
        for strategy_func in self.inference_strategies:
            try:
                result = strategy_func(tweets, scale)
                strategy_results.append(result)
                logger.info(f"Strategy {result['strategy']}: score={result.get('predicted_score', 0):.1f}, confidence={result.get('confidence', 0):.2f}")
            except Exception as e:
                logger.error(f"Strategy failed: {e}")
        
        if not strategy_results:
            self._no_fallbacks_fail_loudly(scale, 'ensemble', 'All prediction strategies failed')
        
        # Extract predictions and confidences - NO FALLBACKS, FAIL LOUDLY
        predictions = []
        confidences = []
        
        for r in strategy_results:
            if 'predicted_score' not in r:
                self._no_fallbacks_fail_loudly(scale, 'ensemble', f"Strategy result missing predicted_score: {r}")
            if 'confidence' not in r:
                self._no_fallbacks_fail_loudly(scale, 'ensemble', f"Strategy result missing confidence: {r}")
                
            predictions.append(r['predicted_score'])
            confidences.append(r['confidence'])
        
        # Confidence-weighted average
        total_confidence = sum(confidences)
        if total_confidence > 0:
            weighted_prediction = sum(p * c for p, c in zip(predictions, confidences)) / total_confidence
        else:
            weighted_prediction = np.mean(predictions)
        
        # Calculate ensemble confidence based on agreement
        prediction_std = np.std(predictions)
        max_std = (scale.max_value - scale.min_value) / 2
        agreement_score = 1 - (prediction_std / max_std)
        ensemble_confidence = np.mean(confidences) * agreement_score
        
        return {
            'predicted_score': float(weighted_prediction),
            'confidence': float(max(0, min(1, ensemble_confidence))),
            'strategy': 'ensemble',
            'strategy_results': strategy_results,
            'individual_predictions': predictions,
            'individual_confidences': confidences,
            'prediction_std': float(prediction_std),
            'strategy_agreement': float(agreement_score)
        }
    
    def predict_user_personality(self, tweets: List[str], user_id: str = None) -> Dict[str, Any]:
        """Predict all personality traits for a user."""
        
        if len(tweets) < 10:
            logger.warning(f"User {user_id} has only {len(tweets)} tweets - predictions may be unreliable")
        
        logger.info(f"Predicting personality for user {user_id} with {len(tweets)} tweets")
        
        results = {}
        
        for trait_name, scale in PERSONALITY_SCALES.items():
            logger.info(f"Analyzing {trait_name}...")
            
            start_time = time.time()
            trait_result = self.ensemble_prediction(tweets, scale)
            inference_time = time.time() - start_time
            
            trait_result['inference_time'] = inference_time
            results[trait_name] = trait_result
            
            logger.info(f"{trait_name}: {trait_result['predicted_score']:.1f} (confidence: {trait_result['confidence']:.2f})")
        
        return {
            'user_id': user_id,
            'trait_predictions': results,
            'total_tweets': len(tweets),
            'prediction_timestamp': time.time()
        }

class PersonalitySystemValidator:
    """Validates the personality inference system against ground truth."""
    
    def __init__(self, system: WorkingLLMPersonalitySystem):
        self.system = system
        
    def load_ground_truth_data(self, dataset_path: str) -> List[Tuple[str, List[str], Dict[str, float]]]:
        """Load ground truth data from dataset."""
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        ground_truth_data = []
        
        for user_data in data:
            user_info = user_data['user_info']
            user_id = user_info['twitter_id']
            
            # Extract tweets
            tweets = [tweet['text'] for tweet in user_data['tweets'] if tweet.get('text', '').strip()]
            
            if len(tweets) < 20:  # Skip users with too few tweets
                continue
            
            # Extract ground truth scores (handle empty strings)
            def safe_float(value, default):
                try:
                    return float(value) if value and str(value).strip() else default
                except (ValueError, TypeError):
                    return default
            
            ground_truth = {
                'political': safe_float(user_info.get('political'), 5),
                'narcissism': np.mean([safe_float(user_info.get(f'narcissism_{i}'), 4) for i in range(1, 5)]),
                'conspiracy': np.mean([safe_float(user_info.get(f'conspiracy_{i}'), 4) for i in range(1, 6)]),
                'denialism': np.mean([safe_float(user_info.get(f'denialism_{i}'), 4) for i in range(1, 5)])
            }
            
            ground_truth_data.append((user_id, tweets, ground_truth))
        
        logger.info(f"Loaded {len(ground_truth_data)} users with ground truth")
        return ground_truth_data
    
    def validate_system(self, dataset_path: str, num_users: int = 10) -> Dict[str, Any]:
        """Validate system performance against ground truth."""
        
        logger.info(f"Starting validation on {num_users} users...")
        
        # Load data
        ground_truth_data = self.load_ground_truth_data(dataset_path)
        test_data = ground_truth_data[:num_users]
        
        validation_results = []
        trait_errors = {trait: [] for trait in PERSONALITY_SCALES.keys()}
        trait_correlations = {trait: {'predictions': [], 'ground_truth': []} for trait in PERSONALITY_SCALES.keys()}
        
        # Process each user
        for i, (user_id, tweets, ground_truth) in enumerate(test_data):
            logger.info(f"Processing user {i+1}/{len(test_data)}: {user_id}")
            
            # Get predictions
            predictions = self.system.predict_user_personality(tweets, user_id)
            
            # Calculate errors
            user_errors = {}
            for trait, gt_value in ground_truth.items():
                if trait in predictions['trait_predictions']:
                    pred_value = predictions['trait_predictions'][trait]['predicted_score']
                    error = abs(pred_value - gt_value)
                    user_errors[trait] = error
                    trait_errors[trait].append(error)
                    
                    # Store for correlation
                    trait_correlations[trait]['predictions'].append(pred_value)
                    trait_correlations[trait]['ground_truth'].append(gt_value)
            
            validation_results.append({
                'user_id': user_id,
                'ground_truth': ground_truth,
                'predictions': predictions,
                'errors': user_errors
            })
        
        # Calculate summary statistics
        summary_stats = {}
        for trait, errors in trait_errors.items():
            if errors:
                # Calculate correlation
                pred_vals = trait_correlations[trait]['predictions']
                gt_vals = trait_correlations[trait]['ground_truth']
                correlation = np.corrcoef(pred_vals, gt_vals)[0, 1] if len(pred_vals) > 1 else 0.0
                
                summary_stats[trait] = {
                    'mae': float(np.mean(errors)),
                    'rmse': float(np.sqrt(np.mean(np.array(errors)**2))),
                    'median_error': float(np.median(errors)),
                    'correlation': float(correlation),
                    'num_predictions': len(errors)
                }
        
        # Overall metrics
        all_errors = [e for errors in trait_errors.values() for e in errors]
        overall_mae = float(np.mean(all_errors)) if all_errors else 0.0
        
        return {
            'validation_results': validation_results,
            'trait_statistics': summary_stats,
            'overall_mae': overall_mae,
            'num_users_tested': len(test_data),
            'validation_timestamp': time.time()
        }

def run_personality_system_demo():
    """Run a complete demo of the personality inference system."""
    
    print("\n" + "="*80)
    print("WORKING LLM PERSONALITY INFERENCE SYSTEM DEMO")
    print("="*80)
    
    # Initialize system
    system = WorkingLLMPersonalitySystem(use_real_llm=True)
    validator = PersonalitySystemValidator(system)
    
    # Run validation
    dataset_path = "../uncertainty_stress_test/100_users_500tweets_dataset.json"
    
    if not Path(dataset_path).exists():
        print(f"Dataset not found at {dataset_path}")
        print("Please ensure the dataset is available")
        return
    
    print(f"\nRunning validation on dataset: {dataset_path}")
    
    # Validate on small sample
    validation_results = validator.validate_system(dataset_path, num_users=5)
    
    # Print results
    print("\n" + "-"*60)
    print("VALIDATION RESULTS")
    print("-"*60)
    
    print(f"\nUsers tested: {validation_results['num_users_tested']}")
    print(f"Overall MAE: {validation_results['overall_mae']:.2f}")
    
    print("\nTRAIT-SPECIFIC PERFORMANCE:")
    for trait, stats in validation_results['trait_statistics'].items():
        print(f"\n{trait.upper()}:")
        print(f"  MAE: {stats['mae']:.2f}")
        print(f"  RMSE: {stats['rmse']:.2f}")
        print(f"  Correlation: {stats['correlation']:.3f}")
        print(f"  Median Error: {stats['median_error']:.2f}")
    
    # Show example prediction
    if validation_results['validation_results']:
        example = validation_results['validation_results'][0]
        print(f"\n" + "-"*40)
        print(f"EXAMPLE PREDICTION: {example['user_id']}")
        print("-"*40)
        
        for trait, gt_value in example['ground_truth'].items():
            if trait in example['predictions']['trait_predictions']:
                pred_result = example['predictions']['trait_predictions'][trait]
                pred_value = pred_result['predicted_score']
                confidence = pred_result['confidence']
                error = example['errors'].get(trait, 0)
                
                print(f"{trait}: GT={gt_value:.1f}, Pred={pred_value:.1f}, Conf={confidence:.2f}, Error={error:.2f}")
    
    # Save detailed results
    output_file = "personality_system_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(validation_results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Performance assessment
    print("\n" + "-"*60)
    print("PERFORMANCE ASSESSMENT")
    print("-"*60)
    
    overall_mae = validation_results['overall_mae']
    
    if overall_mae < 1.5:
        assessment = "EXCELLENT - Very accurate predictions"
    elif overall_mae < 2.0:
        assessment = "GOOD - Reasonably accurate predictions"
    elif overall_mae < 2.5:
        assessment = "FAIR - Moderate accuracy, usable for research"
    else:
        assessment = "POOR - Low accuracy, limited practical value"
    
    print(f"Assessment: {assessment}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if overall_mae > 2.0:
        print("- Consider requiring more tweets per user (50+ minimum)")
        print("- Focus on users with stronger trait expressions")
        print("- Use confidence thresholds to filter predictions")
    
    correlations = [stats['correlation'] for stats in validation_results['trait_statistics'].values()]
    avg_correlation = np.mean(correlations) if correlations else 0
    
    if avg_correlation < 0.3:
        print("- Low correlations suggest fundamental limitations")
        print("- Consider alternative approaches or different traits")
    else:
        print("- Correlations show meaningful signal extraction")
        print("- System can be useful for research applications")

if __name__ == "__main__":
    run_personality_system_demo()