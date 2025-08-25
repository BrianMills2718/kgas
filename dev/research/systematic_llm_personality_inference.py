#!/usr/bin/env python3
"""
Systematic LLM-based Personality Inference System
Works backwards from the assumption that LLMs can infer personality self-assessments
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging
import sys

sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PersonalityScale:
    """Represents a personality measurement scale."""
    name: str
    min_value: int
    max_value: int
    question: str
    anchors: Dict[str, str]  # low, medium, high descriptions

# Define the actual survey scales from the dataset
PERSONALITY_SCALES = {
    'political': PersonalityScale(
        name='Political Orientation',
        min_value=1,
        max_value=11,
        question='How would you describe your political orientation?',
        anchors={
            'low': 'Very liberal/left-wing (1-4)',
            'medium': 'Moderate/centrist (5-7)',
            'high': 'Very conservative/right-wing (8-11)'
        }
    ),
    'narcissism': PersonalityScale(
        name='Narcissism',
        min_value=1,
        max_value=7,
        question='To what extent do you agree with statements about self-importance and need for admiration?',
        anchors={
            'low': 'Disagree - humble, focuses on others (1-3)',
            'medium': 'Neutral - balanced self-regard (4-5)',
            'high': 'Agree - strong self-focus, needs admiration (6-7)'
        }
    ),
    'conspiracy': PersonalityScale(
        name='Conspiracy Mentality',
        min_value=1,
        max_value=11,
        question='How much do you believe in hidden agendas and secret plots?',
        anchors={
            'low': 'Skeptical of conspiracy theories (1-4)',
            'medium': 'Some openness to alternative explanations (5-7)',
            'high': 'Strong belief in conspiracies (8-11)'
        }
    ),
    'denialism': PersonalityScale(
        name='Science Denialism',
        min_value=1,
        max_value=7,
        question='How much do you trust scientific consensus and expertise?',
        anchors={
            'low': 'High trust in science (1-3)',
            'medium': 'Moderate skepticism (4-5)',
            'high': 'Strong distrust of scientific authority (6-7)'
        }
    )
}

class SystematicLLMInference:
    """Systematic approach to personality inference using LLMs."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.inference_strategies = {
            'direct_mapping': self.direct_survey_mapping,
            'behavioral_analysis': self.behavioral_pattern_analysis,
            'comparative_assessment': self.comparative_personality_assessment,
            'multi_perspective': self.multi_perspective_inference,
            'iterative_refinement': self.iterative_refinement_inference
        }
    
    def direct_survey_mapping(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Directly ask LLM to predict survey responses based on tweets."""
        
        prompt = f"""You are a psychologist analyzing social media posts to predict how someone would respond to personality questionnaires.

PERSONALITY DIMENSION: {scale.name}
SURVEY QUESTION: {scale.question}
SCALE: {scale.min_value} to {scale.max_value}
- {scale.anchors['low']}
- {scale.anchors['medium']}  
- {scale.anchors['high']}

TWEETS TO ANALYZE:
{self._format_tweets(tweets[:20])}

Based on these tweets, predict:
1. What score (/{scale.min_value}-{scale.max_value}) would this person most likely give themselves?
2. What specific evidence from the tweets supports this inference?
3. How confident are you in this prediction (0-1)?

Respond in JSON format:
{{
  "predicted_score": <number>,
  "evidence": ["specific tweet evidence 1", "specific tweet evidence 2", ...],
  "reasoning": "explanation of how evidence maps to score",
  "confidence": <0-1>,
  "uncertainty_factors": ["what could make this prediction wrong"]
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "predicted_score": {"type": "number", "minimum": scale.min_value, "maximum": scale.max_value},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "reasoning": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "uncertainty_factors": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["predicted_score", "evidence", "reasoning", "confidence", "uncertainty_factors"]
            }
        )
        
        return json.loads(response["response"].choices[0].message.content)
    
    def behavioral_pattern_analysis(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Analyze behavioral patterns that correlate with personality traits."""
        
        prompt = f"""Analyze these tweets for behavioral patterns that correlate with {scale.name}.

TWEETS:
{self._format_tweets(tweets[:20])}

Identify patterns in:
1. Language use (pronouns, certainty, emotion)
2. Topics discussed  
3. Interaction style
4. Temporal patterns
5. Self-presentation

Map these patterns to likely self-assessment on:
{scale.question} (Scale: {scale.min_value}-{scale.max_value})

Respond in JSON:
{{
  "behavioral_patterns": {{
    "language": "description",
    "topics": "description",
    "interaction": "description",
    "temporal": "description",
    "self_presentation": "description"
  }},
  "pattern_interpretation": "how patterns map to trait",
  "predicted_score": <number>,
  "confidence": <0-1>
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "behavioral_patterns": {
                        "type": "object",
                        "properties": {
                            "language": {"type": "string"},
                            "topics": {"type": "string"},
                            "interaction": {"type": "string"},
                            "temporal": {"type": "string"},
                            "self_presentation": {"type": "string"}
                        }
                    },
                    "pattern_interpretation": {"type": "string"},
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["behavioral_patterns", "pattern_interpretation", "predicted_score", "confidence"]
            }
        )
        
        return json.loads(response["response"].choices[0].message.content)
    
    def comparative_personality_assessment(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Compare user to archetypes of high/low scorers."""
        
        prompt = f"""Compare these tweets to typical patterns of people who score HIGH vs LOW on {scale.name}.

TWEETS TO ANALYZE:
{self._format_tweets(tweets[:20])}

TRAIT: {scale.name}
LOW SCORERS ({scale.min_value}-{int(scale.max_value*0.3)}): {scale.anchors['low']}
HIGH SCORERS ({int(scale.max_value*0.7)}-{scale.max_value}): {scale.anchors['high']}

Compare this person's tweets to both archetypes:
1. Similarities to LOW scorers
2. Similarities to HIGH scorers
3. Which archetype fits better?
4. Predicted score on {scale.min_value}-{scale.max_value} scale

Respond in JSON:
{{
  "low_scorer_similarities": ["similarity 1", "similarity 2", ...],
  "high_scorer_similarities": ["similarity 1", "similarity 2", ...],
  "low_scorer_match": <0-1>,
  "high_scorer_match": <0-1>,
  "better_fit": "low" or "high",
  "predicted_score": <number>,
  "confidence": <0-1>
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "low_scorer_similarities": {"type": "array", "items": {"type": "string"}},
                    "high_scorer_similarities": {"type": "array", "items": {"type": "string"}},
                    "low_scorer_match": {"type": "number", "minimum": 0, "maximum": 1},
                    "high_scorer_match": {"type": "number", "minimum": 0, "maximum": 1},
                    "better_fit": {"type": "string", "enum": ["low", "high", "medium"]},
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"}
                },
                "required": ["low_scorer_similarities", "high_scorer_similarities", 
                           "low_scorer_match", "high_scorer_match", "better_fit", 
                           "predicted_score", "confidence"]
            }
        )
        
        return json.loads(response["response"].choices[0].message.content)
    
    def multi_perspective_inference(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Analyze from multiple psychological perspectives."""
        
        prompt = f"""Analyze these tweets from multiple psychological perspectives to infer {scale.name}.

TWEETS:
{self._format_tweets(tweets[:20])}

Analyze from these perspectives:
1. LINGUISTIC: Word choice, sentence structure, communication style
2. COGNITIVE: Thinking patterns, reasoning style, certainty/uncertainty
3. EMOTIONAL: Emotional expression, regulation, valence
4. SOCIAL: Interaction patterns, group identity, social goals
5. MOTIVATIONAL: What drives this person, what they value

Synthesize into prediction for: {scale.question}
Scale: {scale.min_value}-{scale.max_value}

Respond in JSON:
{{
  "linguistic_analysis": "findings",
  "cognitive_analysis": "findings",
  "emotional_analysis": "findings",
  "social_analysis": "findings",
  "motivational_analysis": "findings",
  "synthesis": "how perspectives combine",
  "predicted_score": <number>,
  "confidence": <0-1>,
  "strongest_indicator": "which perspective was most informative"
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "linguistic_analysis": {"type": "string"},
                    "cognitive_analysis": {"type": "string"},
                    "emotional_analysis": {"type": "string"},
                    "social_analysis": {"type": "string"},
                    "motivational_analysis": {"type": "string"},
                    "synthesis": {"type": "string"},
                    "predicted_score": {"type": "number"},
                    "confidence": {"type": "number"},
                    "strongest_indicator": {"type": "string"}
                },
                "required": ["linguistic_analysis", "cognitive_analysis", "emotional_analysis",
                           "social_analysis", "motivational_analysis", "synthesis",
                           "predicted_score", "confidence", "strongest_indicator"]
            }
        )
        
        return json.loads(response["response"].choices[0].message.content)
    
    def iterative_refinement_inference(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Iteratively refine predictions through self-critique."""
        
        # First pass - initial prediction
        initial_prompt = f"""Based on these tweets, predict how this person would score on {scale.name}.

TWEETS:
{self._format_tweets(tweets[:15])}

SCALE: {scale.question} ({scale.min_value}-{scale.max_value})

Make an initial prediction with reasoning."""

        initial_response = self.llm_client.complete(
            messages=[{"role": "user", "content": initial_prompt}],
            model="gemini_2_5_flash"
        )
        
        initial_prediction = initial_response["response"].choices[0].message.content
        
        # Second pass - critique and refine
        critique_prompt = f"""Review and critique this personality prediction:

INITIAL PREDICTION:
{initial_prediction}

ADDITIONAL TWEETS TO CONSIDER:
{self._format_tweets(tweets[15:25])}

Critique the initial prediction:
1. What evidence was overlooked?
2. What alternative interpretations exist?
3. What biases might affect the prediction?
4. How do the additional tweets change things?

Provide refined prediction in JSON:
{{
  "initial_score": <number>,
  "overlooked_evidence": ["item 1", "item 2", ...],
  "alternative_interpretations": ["interpretation 1", ...],
  "potential_biases": ["bias 1", ...],
  "refined_score": <number>,
  "confidence": <0-1>,
  "key_refinements": "what changed and why"
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": critique_prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "initial_score": {"type": "number"},
                    "overlooked_evidence": {"type": "array", "items": {"type": "string"}},
                    "alternative_interpretations": {"type": "array", "items": {"type": "string"}},
                    "potential_biases": {"type": "array", "items": {"type": "string"}},
                    "refined_score": {"type": "number"},
                    "confidence": {"type": "number"},
                    "key_refinements": {"type": "string"}
                },
                "required": ["initial_score", "overlooked_evidence", "alternative_interpretations",
                           "potential_biases", "refined_score", "confidence", "key_refinements"]
            }
        )
        
        result = json.loads(response["response"].choices[0].message.content)
        result['predicted_score'] = result['refined_score']
        return result
    
    def ensemble_inference(self, tweets: List[str], scale: PersonalityScale) -> Dict[str, Any]:
        """Combine multiple inference strategies for robust prediction."""
        
        results = {}
        
        # Run each strategy
        for strategy_name, strategy_func in self.inference_strategies.items():
            try:
                results[strategy_name] = strategy_func(tweets, scale)
            except Exception as e:
                logger.error(f"Strategy {strategy_name} failed: {e}")
                results[strategy_name] = {"predicted_score": scale.min_value + (scale.max_value - scale.min_value) / 2, 
                                        "confidence": 0.1}
        
        # Aggregate predictions
        scores = [r.get('predicted_score', 0) for r in results.values() if 'predicted_score' in r]
        confidences = [r.get('confidence', 0) for r in results.values() if 'confidence' in r]
        
        # Weighted average by confidence
        if sum(confidences) > 0:
            weighted_score = sum(s * c for s, c in zip(scores, confidences)) / sum(confidences)
        else:
            weighted_score = np.mean(scores)
        
        # Calculate ensemble confidence
        score_std = np.std(scores)
        score_range = scale.max_value - scale.min_value
        agreement = 1 - (score_std / score_range)
        ensemble_confidence = np.mean(confidences) * agreement
        
        return {
            'predicted_score': float(weighted_score),
            'confidence': float(ensemble_confidence),
            'strategy_results': results,
            'score_distribution': {
                'mean': float(np.mean(scores)),
                'std': float(score_std),
                'min': float(min(scores)),
                'max': float(max(scores))
            },
            'strategy_agreement': float(agreement)
        }
    
    def analyze_inference_factors(self, tweets: List[str], scale: PersonalityScale, 
                                ground_truth: float) -> Dict[str, Any]:
        """Analyze what factors enable accurate inference."""
        
        # Get ensemble prediction
        prediction = self.ensemble_inference(tweets, scale)
        error = abs(prediction['predicted_score'] - ground_truth)
        
        # Analyze tweet characteristics
        tweet_features = self._analyze_tweet_features(tweets)
        
        # Identify which strategies worked best
        strategy_errors = {}
        for strategy_name, result in prediction['strategy_results'].items():
            if 'predicted_score' in result:
                strategy_errors[strategy_name] = abs(result['predicted_score'] - ground_truth)
        
        best_strategy = min(strategy_errors.items(), key=lambda x: x[1])[0] if strategy_errors else None
        
        # Analyze what made prediction accurate/inaccurate
        analysis_prompt = f"""Analyze why the personality prediction was {'accurate' if error < 1.5 else 'inaccurate'}.

TWEETS ANALYZED:
{self._format_tweets(tweets[:10])}

TRAIT: {scale.name}
TRUE SCORE: {ground_truth}
PREDICTED SCORE: {prediction['predicted_score']:.1f}
ERROR: {error:.1f}

Tweet characteristics:
{json.dumps(tweet_features, indent=2)}

Best performing strategy: {best_strategy}

Analyze:
1. What tweet features correlate with accurate prediction?
2. What's missing that would improve accuracy?
3. What types of tweets are most informative?
4. What biases affect prediction?

Respond in JSON:
{{
  "accuracy_factors": ["factor 1", "factor 2", ...],
  "missing_information": ["what would help", ...],
  "informative_tweet_types": ["type 1", "type 2", ...],
  "identified_biases": ["bias 1", "bias 2", ...],
  "improvement_suggestions": ["suggestion 1", ...]
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": analysis_prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "accuracy_factors": {"type": "array", "items": {"type": "string"}},
                    "missing_information": {"type": "array", "items": {"type": "string"}},
                    "informative_tweet_types": {"type": "array", "items": {"type": "string"}},
                    "identified_biases": {"type": "array", "items": {"type": "string"}},
                    "improvement_suggestions": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["accuracy_factors", "missing_information", "informative_tweet_types",
                           "identified_biases", "improvement_suggestions"]
            }
        )
        
        analysis = json.loads(response["response"].choices[0].message.content)
        
        return {
            'prediction_error': float(error),
            'prediction_details': prediction,
            'tweet_features': tweet_features,
            'best_strategy': best_strategy,
            'strategy_errors': strategy_errors,
            'inference_analysis': analysis
        }
    
    def _format_tweets(self, tweets: List[str]) -> str:
        """Format tweets for prompt."""
        formatted = []
        for i, tweet in enumerate(tweets, 1):
            formatted.append(f"{i}. {tweet}")
        return "\n".join(formatted)
    
    def _analyze_tweet_features(self, tweets: List[str]) -> Dict[str, Any]:
        """Analyze characteristics of tweet set."""
        return {
            'count': len(tweets),
            'avg_length': np.mean([len(t) for t in tweets]),
            'total_words': sum(len(t.split()) for t in tweets),
            'unique_words': len(set(' '.join(tweets).lower().split())),
            'questions': sum('?' in t for t in tweets),
            'exclamations': sum('!' in t for t in tweets),
            'mentions': sum('@' in t for t in tweets),
            'hashtags': sum('#' in t for t in tweets),
            'urls': sum('http' in t for t in tweets),
            'retweets': sum(t.startswith('RT ') for t in tweets),
            'self_references': sum(t.lower().count(' i ') + t.lower().count(" i'") for t in tweets),
            'emotional_words': sum(any(emo in t.lower() for emo in ['love', 'hate', 'angry', 'happy', 'sad']) for t in tweets)
        }


class SystematicValidation:
    """Validate the systematic LLM inference approach."""
    
    def __init__(self, inference_system: SystematicLLMInference):
        self.inference_system = inference_system
        self.results = []
    
    def validate_on_dataset(self, dataset_path: str, num_users: int = 10) -> Dict[str, Any]:
        """Validate on users with ground truth."""
        
        # Load data
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        validation_results = {
            'political': [],
            'narcissism': [],
            'conspiracy': [],
            'denialism': []
        }
        
        # Process each user
        for user_data in data[:num_users]:
            user_info = user_data['user_info']
            tweets = [t['text'] for t in user_data['tweets'] if t.get('text', '').strip()]
            
            if len(tweets) < 20:
                continue
            
            # Get ground truth
            ground_truth = {
                'political': float(user_info.get('political', 5)),
                'narcissism': np.mean([float(user_info.get(f'narcissism_{i}', 4)) for i in range(1, 5)]),
                'conspiracy': np.mean([float(user_info.get(f'conspiracy_{i}', 4)) for i in range(1, 6)]),
                'denialism': np.mean([float(user_info.get(f'denialism_{i}', 4)) for i in range(1, 5)])
            }
            
            # Run inference for each trait
            for trait_key, scale in PERSONALITY_SCALES.items():
                logger.info(f"Inferring {trait_key} for user {user_info['twitter_id']}")
                
                # Get analysis
                analysis = self.inference_system.analyze_inference_factors(
                    tweets, scale, ground_truth[trait_key]
                )
                
                validation_results[trait_key].append({
                    'user_id': user_info['twitter_id'],
                    'ground_truth': ground_truth[trait_key],
                    'prediction': analysis['prediction_details']['predicted_score'],
                    'error': analysis['prediction_error'],
                    'confidence': analysis['prediction_details']['confidence'],
                    'best_strategy': analysis['best_strategy'],
                    'tweet_features': analysis['tweet_features'],
                    'analysis': analysis['inference_analysis']
                })
        
        # Compute aggregate metrics
        summary = {}
        for trait, results in validation_results.items():
            if results:
                errors = [r['error'] for r in results]
                summary[trait] = {
                    'mae': float(np.mean(errors)),
                    'rmse': float(np.sqrt(np.mean(np.array(errors)**2))),
                    'correlation': float(np.corrcoef(
                        [r['ground_truth'] for r in results],
                        [r['prediction'] for r in results]
                    )[0, 1]) if len(results) > 1 else 0.0,
                    'avg_confidence': float(np.mean([r['confidence'] for r in results])),
                    'best_strategies': self._count_best_strategies(results)
                }
        
        return {
            'validation_results': validation_results,
            'summary': summary,
            'overall_mae': float(np.mean([s['mae'] for s in summary.values()])),
            'insights': self._extract_insights(validation_results)
        }
    
    def _count_best_strategies(self, results: List[Dict]) -> Dict[str, int]:
        """Count which strategies performed best."""
        strategy_counts = {}
        for r in results:
            strategy = r.get('best_strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return strategy_counts
    
    def _extract_insights(self, validation_results: Dict[str, List]) -> Dict[str, Any]:
        """Extract insights about what enables accurate inference."""
        
        all_factors = []
        all_missing = []
        all_biases = []
        
        for trait_results in validation_results.values():
            for result in trait_results:
                if 'analysis' in result:
                    all_factors.extend(result['analysis'].get('accuracy_factors', []))
                    all_missing.extend(result['analysis'].get('missing_information', []))
                    all_biases.extend(result['analysis'].get('identified_biases', []))
        
        # Count frequencies
        from collections import Counter
        
        return {
            'top_accuracy_factors': Counter(all_factors).most_common(5),
            'top_missing_information': Counter(all_missing).most_common(5),
            'common_biases': Counter(all_biases).most_common(5),
            'tweet_features_correlation': self._analyze_feature_correlations(validation_results)
        }
    
    def _analyze_feature_correlations(self, validation_results: Dict[str, List]) -> Dict[str, float]:
        """Analyze which tweet features correlate with accuracy."""
        
        features = []
        errors = []
        
        for trait_results in validation_results.values():
            for result in trait_results:
                if 'tweet_features' in result:
                    features.append(result['tweet_features'])
                    errors.append(result['error'])
        
        if not features:
            return {}
        
        # Calculate correlations
        correlations = {}
        feature_names = features[0].keys()
        
        for feature in feature_names:
            values = [f[feature] for f in features]
            if len(set(values)) > 1:  # Only if there's variation
                corr = np.corrcoef(values, errors)[0, 1]
                correlations[feature] = float(corr)
        
        return correlations


def main():
    """Demo systematic LLM personality inference."""
    
    # Initialize system
    llm_client = UniversalModelClient()
    inference_system = SystematicLLMInference(llm_client)
    validator = SystematicValidation(inference_system)
    
    # Run validation
    logger.info("Starting systematic validation...")
    results = validator.validate_on_dataset(
        "../uncertainty_stress_test/100_users_500tweets_dataset.json",
        num_users=5  # Small sample for demo
    )
    
    # Print results
    print("\n" + "="*80)
    print("SYSTEMATIC LLM PERSONALITY INFERENCE RESULTS")
    print("="*80)
    
    print("\nSUMMARY BY TRAIT:")
    for trait, metrics in results['summary'].items():
        print(f"\n{trait.upper()}:")
        print(f"  MAE: {metrics['mae']:.2f}")
        print(f"  Correlation: {metrics['correlation']:.3f}")
        print(f"  Avg Confidence: {metrics['avg_confidence']:.3f}")
        print(f"  Best Strategies: {metrics['best_strategies']}")
    
    print(f"\nOVERALL MAE: {results['overall_mae']:.2f}")
    
    print("\nKEY INSIGHTS:")
    insights = results['insights']
    
    print("\nTop Accuracy Factors:")
    for factor, count in insights['top_accuracy_factors']:
        print(f"  - {factor} (mentioned {count} times)")
    
    print("\nTop Missing Information:")
    for info, count in insights['top_missing_information']:
        print(f"  - {info} (mentioned {count} times)")
    
    print("\nCommon Biases:")
    for bias, count in insights['common_biases']:
        print(f"  - {bias} (mentioned {count} times)")
    
    print("\nTweet Feature Correlations with Error:")
    for feature, corr in sorted(insights['tweet_features_correlation'].items(), 
                               key=lambda x: abs(x[1]), reverse=True)[:5]:
        print(f"  - {feature}: {corr:.3f}")
    
    # Save results
    output_file = "systematic_llm_inference_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to {output_file}")


if __name__ == "__main__":
    main()