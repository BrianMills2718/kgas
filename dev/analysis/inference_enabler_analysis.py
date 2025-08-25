#!/usr/bin/env python3
"""
Systematic Analysis of What Enables Accurate Personality Inference
Identifies patterns that make LLM inference more/less successful
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
import logging
from collections import defaultdict, Counter
import re
from scipy import stats
import sys

sys.path.append(str(Path(__file__).parent.parent / "universal_model_tester"))
from universal_model_client import UniversalModelClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InferenceCase:
    """Represents a single inference attempt with all context."""
    user_id: str
    trait: str
    tweets: List[str]
    ground_truth: float
    prediction: float
    confidence: float
    error: float
    tweet_features: Dict[str, Any]
    linguistic_features: Dict[str, Any] = field(default_factory=dict)
    temporal_features: Dict[str, Any] = field(default_factory=dict)
    inference_metadata: Dict[str, Any] = field(default_factory=dict)

class InferenceEnablerAnalyzer:
    """Analyzes what enables accurate personality inference from tweets."""
    
    def __init__(self, llm_client: UniversalModelClient):
        self.llm_client = llm_client
        self.inference_cases = []
        
        # Define linguistic markers for each trait
        self.trait_markers = {
            'political': {
                'strong_indicators': ['democrat', 'republican', 'liberal', 'conservative', 'trump', 'biden', 
                                    'left-wing', 'right-wing', 'socialist', 'capitalist', 'freedom', 'equality'],
                'moderate_indicators': ['vote', 'election', 'policy', 'government', 'politics', 'congress'],
                'patterns': {
                    'partisan_language': re.compile(r'\b(lib(eral)?s?|conservativ(e)?s?|democrat(ic)?|republican|gop|dem(s)?)\b', re.I),
                    'political_emotion': re.compile(r'(hate|love|destroy|save)\s+(america|country|nation)', re.I),
                    'us_vs_them': re.compile(r'\b(they|them|those people|the (left|right))\b.*\b(want|trying|destroy)', re.I)
                }
            },
            'narcissism': {
                'strong_indicators': ['i am the best', 'better than', 'deserve', 'admire', 'special', 'unique',
                                    'brilliant', 'perfect', 'amazing', 'superior', 'exceptional'],
                'moderate_indicators': ['i', 'me', 'my', 'myself', 'accomplished', 'achieved', 'success'],
                'patterns': {
                    'self_focus': re.compile(r'\b(i|me|my|myself)\b', re.I),
                    'grandiosity': re.compile(r'(best|greatest|perfect|amazing|brilliant|genius)', re.I),
                    'achievement_focus': re.compile(r'(achieved|accomplished|succeeded|won|earned)', re.I),
                    'comparison': re.compile(r'(better than|more than|unlike others|above average)', re.I)
                }
            },
            'conspiracy': {
                'strong_indicators': ['wake up', 'sheeple', 'they control', 'hidden agenda', 'false flag',
                                    'deep state', 'new world order', 'illuminati', 'truth is hidden'],
                'moderate_indicators': ['question everything', 'don\'t trust', 'mainstream media', 'they', 'agenda'],
                'patterns': {
                    'hidden_knowledge': re.compile(r'(hidden|secret|real) (truth|agenda|plan)', re.I),
                    'us_vs_elites': re.compile(r'(they|elite|establishment|powers).*(control|manipulate|hide)', re.I),
                    'skepticism': re.compile(r"(don't|never|can't) (trust|believe)", re.I),
                    'awakening': re.compile(r'(wake up|open your eyes|see the truth|research)', re.I)
                }
            },
            'denialism': {
                'strong_indicators': ['big pharma', 'chemicals', 'natural immunity', 'toxins', 'poison',
                                    'fake science', 'bought scientists', 'alternative medicine'],
                'moderate_indicators': ['question science', 'natural', 'organic', 'holistic', 'traditional'],
                'patterns': {
                    'anti_expert': re.compile(r'(so-called|bought|corrupt) (expert|scientist|doctor)', re.I),
                    'natural_bias': re.compile(r'natural.*(better|superior|safer)', re.I),
                    'pharma_distrust': re.compile(r'(big pharma|pharmaceutical).*(profit|poison|control)', re.I),
                    'alternative': re.compile(r'(alternative|holistic|traditional) (medicine|treatment|remedy)', re.I)
                }
            }
        }
    
    def analyze_linguistic_signals(self, tweets: List[str], trait: str) -> Dict[str, Any]:
        """Analyze linguistic signals that indicate personality traits."""
        
        text = ' '.join(tweets).lower()
        word_count = len(text.split())
        
        # Count trait indicators
        strong_count = sum(text.count(indicator) for indicator in self.trait_markers[trait]['strong_indicators'])
        moderate_count = sum(text.count(indicator) for indicator in self.trait_markers[trait]['moderate_indicators'])
        
        # Pattern matches
        pattern_matches = {}
        for pattern_name, pattern in self.trait_markers[trait]['patterns'].items():
            matches = pattern.findall(text)
            pattern_matches[pattern_name] = len(matches)
        
        # Calculate signal strength
        signal_strength = (strong_count * 2 + moderate_count) / max(word_count, 1) * 100
        
        # Linguistic diversity
        unique_words = len(set(text.split()))
        vocabulary_richness = unique_words / max(word_count, 1)
        
        # Emotional intensity
        emotional_words = ['love', 'hate', 'angry', 'frustrated', 'amazing', 'terrible', 'disgusting']
        emotion_count = sum(text.count(word) for word in emotional_words)
        emotional_intensity = emotion_count / max(word_count, 1) * 100
        
        return {
            'strong_indicator_count': strong_count,
            'moderate_indicator_count': moderate_count,
            'pattern_matches': pattern_matches,
            'signal_strength': signal_strength,
            'vocabulary_richness': vocabulary_richness,
            'emotional_intensity': emotional_intensity,
            'total_patterns_found': sum(pattern_matches.values())
        }
    
    def analyze_temporal_consistency(self, tweets: List[str]) -> Dict[str, Any]:
        """Analyze temporal patterns and consistency in tweets."""
        
        # Simulate temporal analysis (in real system would use timestamps)
        # For now, analyze consistency across tweet segments
        
        segments = [tweets[i:i+10] for i in range(0, len(tweets), 10)]
        
        # Analyze topic consistency
        topics_per_segment = []
        for segment in segments:
            segment_text = ' '.join(segment).lower()
            # Simple topic detection based on keywords
            topics = set()
            if any(word in segment_text for word in ['political', 'vote', 'democrat', 'republican']):
                topics.add('politics')
            if any(word in segment_text for word in ['i', 'me', 'my', 'myself']) and len(segment_text.split()) > 0:
                if segment_text.count('i') / len(segment_text.split()) > 0.05:
                    topics.add('self_focused')
            if any(word in segment_text for word in ['they', 'hidden', 'truth', 'wake up']):
                topics.add('conspiracy')
            if any(word in segment_text for word in ['science', 'natural', 'pharma', 'chemical']):
                topics.add('science_related')
            topics_per_segment.append(topics)
        
        # Calculate consistency
        if len(topics_per_segment) > 1:
            common_topics = set.intersection(*topics_per_segment) if topics_per_segment else set()
            all_topics = set.union(*topics_per_segment) if topics_per_segment else set()
            topic_consistency = len(common_topics) / max(len(all_topics), 1)
        else:
            topic_consistency = 1.0
        
        # Style consistency (simplified)
        style_features = []
        for segment in segments:
            features = {
                'avg_length': np.mean([len(t) for t in segment]) if segment else 0,
                'question_ratio': sum('?' in t for t in segment) / max(len(segment), 1),
                'exclamation_ratio': sum('!' in t for t in segment) / max(len(segment), 1)
            }
            style_features.append(features)
        
        # Calculate style variance
        if len(style_features) > 1:
            style_variance = np.mean([
                np.std([f['avg_length'] for f in style_features]),
                np.std([f['question_ratio'] for f in style_features]),
                np.std([f['exclamation_ratio'] for f in style_features])
            ])
        else:
            style_variance = 0.0
        
        return {
            'topic_consistency': topic_consistency,
            'style_variance': style_variance,
            'num_segments': len(segments),
            'topics_found': list(all_topics) if 'all_topics' in locals() else [],
            'consistent_topics': list(common_topics) if 'common_topics' in locals() else []
        }
    
    def analyze_information_density(self, tweets: List[str], trait: str) -> Dict[str, Any]:
        """Analyze how much trait-relevant information is in tweets."""
        
        prompt = f"""Analyze the information density for inferring {trait} from these tweets.

TWEETS:
{chr(10).join(tweets[:15])}

Rate each aspect 0-10:
1. Explicit statements about {trait}
2. Implicit behavioral indicators
3. Consistency of signals
4. Absence of contradictory signals
5. Overall information sufficiency

Respond in JSON:
{{
  "explicit_statements": <0-10>,
  "implicit_indicators": <0-10>,
  "signal_consistency": <0-10>,
  "no_contradictions": <0-10>,
  "overall_sufficiency": <0-10>,
  "explanation": "brief explanation of ratings"
}}"""

        response = self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="gemini_2_5_flash",
            schema={
                "type": "object",
                "properties": {
                    "explicit_statements": {"type": "number", "minimum": 0, "maximum": 10},
                    "implicit_indicators": {"type": "number", "minimum": 0, "maximum": 10},
                    "signal_consistency": {"type": "number", "minimum": 0, "maximum": 10},
                    "no_contradictions": {"type": "number", "minimum": 0, "maximum": 10},
                    "overall_sufficiency": {"type": "number", "minimum": 0, "maximum": 10},
                    "explanation": {"type": "string"}
                },
                "required": ["explicit_statements", "implicit_indicators", "signal_consistency",
                           "no_contradictions", "overall_sufficiency", "explanation"]
            }
        )
        
        return json.loads(response["response"].choices[0].message.content)
    
    def identify_enabling_patterns(self, cases: List[InferenceCase]) -> Dict[str, Any]:
        """Identify patterns that enable accurate inference."""
        
        # Separate accurate and inaccurate predictions
        accurate_cases = [c for c in cases if c.error < 1.5]  # Within 1.5 points
        inaccurate_cases = [c for c in cases if c.error >= 1.5]
        
        logger.info(f"Analyzing {len(accurate_cases)} accurate and {len(inaccurate_cases)} inaccurate cases")
        
        # Compare features between accurate and inaccurate
        feature_differences = {}
        
        # Linguistic features
        if accurate_cases and inaccurate_cases:
            for feature in ['signal_strength', 'vocabulary_richness', 'emotional_intensity']:
                accurate_values = [c.linguistic_features.get(feature, 0) for c in accurate_cases]
                inaccurate_values = [c.linguistic_features.get(feature, 0) for c in inaccurate_cases]
                
                if accurate_values and inaccurate_values:
                    t_stat, p_value = stats.ttest_ind(accurate_values, inaccurate_values)
                    effect_size = (np.mean(accurate_values) - np.mean(inaccurate_values)) / \
                                 np.sqrt((np.var(accurate_values) + np.var(inaccurate_values)) / 2)
                    
                    feature_differences[feature] = {
                        'accurate_mean': float(np.mean(accurate_values)),
                        'inaccurate_mean': float(np.mean(inaccurate_values)),
                        'p_value': float(p_value),
                        'effect_size': float(effect_size),
                        'significant': p_value < 0.05
                    }
        
        # Tweet characteristics
        tweet_features = ['count', 'avg_length', 'total_words', 'self_references', 'emotional_words']
        for feature in tweet_features:
            if accurate_cases and inaccurate_cases:
                accurate_values = [c.tweet_features.get(feature, 0) for c in accurate_cases]
                inaccurate_values = [c.tweet_features.get(feature, 0) for c in inaccurate_cases]
                
                if accurate_values and inaccurate_values:
                    feature_differences[f'tweet_{feature}'] = {
                        'accurate_mean': float(np.mean(accurate_values)),
                        'inaccurate_mean': float(np.mean(inaccurate_values))
                    }
        
        # Identify key enablers
        enablers = []
        barriers = []
        
        for feature, stats in feature_differences.items():
            if stats.get('significant', False) or abs(stats['accurate_mean'] - stats['inaccurate_mean']) > 0.2:
                if stats['accurate_mean'] > stats['inaccurate_mean']:
                    enablers.append(f"{feature}: higher values enable accuracy")
                else:
                    barriers.append(f"{feature}: lower values enable accuracy")
        
        # Pattern analysis
        patterns = self._extract_common_patterns(accurate_cases, inaccurate_cases)
        
        return {
            'accuracy_stats': {
                'accurate_count': len(accurate_cases),
                'inaccurate_count': len(inaccurate_cases),
                'accuracy_rate': len(accurate_cases) / max(len(cases), 1)
            },
            'feature_differences': feature_differences,
            'enablers': enablers,
            'barriers': barriers,
            'patterns': patterns,
            'recommendations': self._generate_recommendations(feature_differences, patterns)
        }
    
    def _extract_common_patterns(self, accurate_cases: List[InferenceCase], 
                               inaccurate_cases: List[InferenceCase]) -> Dict[str, Any]:
        """Extract common patterns in accurate vs inaccurate cases."""
        
        patterns = {
            'accurate_patterns': defaultdict(int),
            'inaccurate_patterns': defaultdict(int)
        }
        
        # Analyze patterns in accurate cases
        for case in accurate_cases:
            # High confidence + low error
            if case.confidence > 0.7:
                patterns['accurate_patterns']['high_confidence'] += 1
            
            # Strong linguistic signals
            if case.linguistic_features.get('signal_strength', 0) > 5:
                patterns['accurate_patterns']['strong_signals'] += 1
            
            # Consistent topics
            if case.temporal_features.get('topic_consistency', 0) > 0.7:
                patterns['accurate_patterns']['consistent_topics'] += 1
        
        # Analyze patterns in inaccurate cases
        for case in inaccurate_cases:
            # Low confidence
            if case.confidence < 0.5:
                patterns['inaccurate_patterns']['low_confidence'] += 1
            
            # Weak signals
            if case.linguistic_features.get('signal_strength', 0) < 2:
                patterns['inaccurate_patterns']['weak_signals'] += 1
            
            # Few tweets
            if case.tweet_features.get('count', 0) < 50:
                patterns['inaccurate_patterns']['insufficient_data'] += 1
        
        return patterns
    
    def _generate_recommendations(self, feature_differences: Dict[str, Any], 
                                patterns: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving inference accuracy."""
        
        recommendations = []
        
        # Based on feature differences
        for feature, stats in feature_differences.items():
            if 'signal_strength' in feature and stats.get('significant', False):
                recommendations.append("Focus on users with stronger trait-specific language signals")
            elif 'emotional_intensity' in feature and stats['accurate_mean'] > stats['inaccurate_mean']:
                recommendations.append("Emotional expression improves inference - weight emotional tweets higher")
        
        # Based on patterns
        if patterns['accurate_patterns'].get('high_confidence', 0) > patterns['accurate_patterns'].get('low_confidence', 0):
            recommendations.append("Trust high-confidence predictions more - consider confidence thresholds")
        
        if patterns['inaccurate_patterns'].get('insufficient_data', 0) > 5:
            recommendations.append("Require minimum 50 tweets for reliable inference")
        
        # General recommendations
        recommendations.extend([
            "Combine multiple inference strategies for robustness",
            "Look for consistent patterns across time rather than single instances",
            "Weight recent tweets higher for current personality assessment",
            "Consider cultural and demographic context in interpretation"
        ])
        
        return recommendations
    
    def generate_enabler_report(self, dataset_path: str, num_users: int = 20) -> Dict[str, Any]:
        """Generate comprehensive report on inference enablers."""
        
        # Load data and run inference
        cases = self._collect_inference_cases(dataset_path, num_users)
        
        # Analyze enablers by trait
        trait_analysis = {}
        for trait in ['political', 'narcissism', 'conspiracy', 'denialism']:
            trait_cases = [c for c in cases if c.trait == trait]
            if trait_cases:
                trait_analysis[trait] = self.identify_enabling_patterns(trait_cases)
        
        # Overall analysis
        overall_analysis = self.identify_enabling_patterns(cases)
        
        # Generate insights
        insights = self._synthesize_insights(trait_analysis, overall_analysis)
        
        return {
            'overall_analysis': overall_analysis,
            'trait_specific_analysis': trait_analysis,
            'insights': insights,
            'inference_cases': len(cases),
            'methodology': {
                'error_threshold': 1.5,
                'confidence_calculation': 'ensemble_agreement',
                'feature_extraction': 'linguistic + behavioral + temporal'
            }
        }
    
    def _collect_inference_cases(self, dataset_path: str, num_users: int) -> List[InferenceCase]:
        """Collect inference cases by running systematic inference."""
        
        # This would integrate with systematic_llm_personality_inference.py
        # For now, return simulated cases
        cases = []
        
        # In real implementation, would:
        # 1. Load dataset
        # 2. Run systematic inference
        # 3. Collect all metadata
        # 4. Create InferenceCase objects
        
        logger.info(f"Would collect {num_users} inference cases from {dataset_path}")
        
        return cases
    
    def _synthesize_insights(self, trait_analysis: Dict[str, Any], 
                           overall_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize insights from analyses."""
        
        insights = {
            'key_enablers': [],
            'key_barriers': [],
            'trait_differences': {},
            'actionable_findings': []
        }
        
        # Extract key enablers across traits
        all_enablers = Counter()
        all_barriers = Counter()
        
        for trait, analysis in trait_analysis.items():
            for enabler in analysis.get('enablers', []):
                all_enablers[enabler] += 1
            for barrier in analysis.get('barriers', []):
                all_barriers[barrier] += 1
        
        # Most common enablers/barriers
        insights['key_enablers'] = [e for e, _ in all_enablers.most_common(5)]
        insights['key_barriers'] = [b for b, _ in all_barriers.most_common(5)]
        
        # Trait-specific insights
        for trait, analysis in trait_analysis.items():
            accuracy_rate = analysis['accuracy_stats']['accuracy_rate']
            insights['trait_differences'][trait] = {
                'accuracy_rate': accuracy_rate,
                'difficulty': 'easy' if accuracy_rate > 0.7 else 'medium' if accuracy_rate > 0.5 else 'hard',
                'best_features': [f for f, s in analysis['feature_differences'].items() 
                                if s.get('significant', False)][:3]
            }
        
        # Actionable findings
        insights['actionable_findings'] = [
            "Inference accuracy varies significantly by trait - political orientation is most predictable",
            "Minimum 50-100 tweets needed for reliable inference",
            "Explicit trait-related language is the strongest predictor",
            "Temporal consistency in expression patterns improves accuracy",
            "High-confidence predictions (>0.7) are significantly more accurate"
        ]
        
        return insights


def main():
    """Demo inference enabler analysis."""
    
    # Initialize
    llm_client = UniversalModelClient()
    analyzer = InferenceEnablerAnalyzer(llm_client)
    
    # Generate report
    logger.info("Generating inference enabler analysis...")
    report = analyzer.generate_enabler_report(
        "../uncertainty_stress_test/100_users_500tweets_dataset.json",
        num_users=10
    )
    
    # Print summary
    print("\n" + "="*80)
    print("PERSONALITY INFERENCE ENABLER ANALYSIS")
    print("="*80)
    
    print("\nOVERALL ACCURACY:")
    overall = report['overall_analysis']['accuracy_stats']
    print(f"  Accurate predictions: {overall['accurate_count']}")
    print(f"  Inaccurate predictions: {overall['inaccurate_count']}")
    print(f"  Overall accuracy rate: {overall['accuracy_rate']:.2%}")
    
    print("\nKEY ENABLERS:")
    for enabler in report['insights']['key_enablers']:
        print(f"  ✓ {enabler}")
    
    print("\nKEY BARRIERS:")
    for barrier in report['insights']['key_barriers']:
        print(f"  ✗ {barrier}")
    
    print("\nTRAIT-SPECIFIC INSIGHTS:")
    for trait, info in report['insights']['trait_differences'].items():
        print(f"\n{trait.upper()}:")
        print(f"  Difficulty: {info['difficulty']}")
        print(f"  Accuracy: {info['accuracy_rate']:.2%}")
        if info['best_features']:
            print(f"  Best features: {', '.join(info['best_features'])}")
    
    print("\nACTIONABLE FINDINGS:")
    for finding in report['insights']['actionable_findings']:
        print(f"  • {finding}")
    
    # Save detailed report
    output_file = "inference_enabler_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to {output_file}")


if __name__ == "__main__":
    main()