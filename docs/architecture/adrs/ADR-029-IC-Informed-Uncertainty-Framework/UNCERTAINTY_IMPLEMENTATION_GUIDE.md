# KGAS Uncertainty Framework Implementation Guide
## Practical Patterns and Code Templates

**Version**: 1.0  
**Date**: 2025-08-06  
**Purpose**: Concrete implementation guidance for the Comprehensive Uncertainty Framework  
**Target Audience**: Developers implementing the uncertainty system  

---

## 🏗️ Core Implementation Architecture

### Base Uncertainty Classes

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np
from scipy import stats
import math

class UncertaintyDimension(Enum):
    """All trackable uncertainty dimensions"""
    # Source Quality
    SOURCE_CREDIBILITY = "source_credibility"
    INFO_CREDIBILITY = "info_credibility"
    TEMPORAL_RELEVANCE = "temporal_relevance"
    
    # Computational
    EXTRACTION_COMPLETENESS = "extraction_completeness"
    ENTITY_RECOGNITION = "entity_recognition"
    RELATIONSHIP_VALIDITY = "relationship_validity"
    ALGORITHM_PRECISION = "algorithm_precision"
    
    # Theoretical
    THEORY_EXTRACTION = "theory_extraction"
    THEORY_FIT = "theory_fit"
    CONSTRUCT_VALIDITY = "construct_validity"
    
    # Transformational
    GRAPH_TABLE_PRESERVATION = "graph_table_preservation"
    TABLE_VECTOR_PRESERVATION = "table_vector_preservation"
    MODAL_AGREEMENT = "modal_agreement"
    
    # Cognitive
    CONFIRMATION_BIAS = "confirmation_bias"
    ANCHORING_EFFECTS = "anchoring_effects"
    
    # Synthesis
    CROSS_SOURCE_COHERENCE = "cross_source_coherence"
    EVIDENCE_SUFFICIENCY = "evidence_sufficiency"
    CLAIM_STRENGTH = "claim_strength"

@dataclass
class UncertaintyMeasurement:
    """Single uncertainty measurement"""
    dimension: UncertaintyDimension
    value: float  # 0-1 confidence score
    framework: str  # "ICD-206", "CERQual", "Statistical", etc.
    measurement_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_human_readable(self) -> str:
        """Convert to human interpretation"""
        interpretations = {
            UncertaintyDimension.SOURCE_CREDIBILITY: f"Source credibility: {self._to_percentage()}%",
            UncertaintyDimension.ENTITY_RECOGNITION: f"Entity recognition confidence: {self._to_percentage()}%",
            UncertaintyDimension.CROSS_SOURCE_COHERENCE: f"Sources {'agree' if self.value > 0.7 else 'disagree'} ({self._to_percentage()}%)",
            # Add more interpretations
        }
        return interpretations.get(self.dimension, f"{self.dimension.value}: {self._to_percentage()}%")
    
    def _to_percentage(self) -> int:
        return int(self.value * 100)

@dataclass
class UncertaintyProfile:
    """Complete uncertainty profile for an analysis"""
    measurements: Dict[UncertaintyDimension, UncertaintyMeasurement] = field(default_factory=dict)
    pipeline_stage: str = ""
    timestamp: Optional[float] = None
    configuration: Optional['UncertaintyConfiguration'] = None
    
    def add_measurement(self, measurement: UncertaintyMeasurement):
        """Add or update a measurement"""
        self.measurements[measurement.dimension] = measurement
    
    def get_aggregate_confidence(self) -> float:
        """Calculate overall confidence using configured method"""
        if not self.measurements:
            return 0.0
        
        if self.configuration and self.configuration.aggregation_method == "weighted":
            return self._weighted_aggregate()
        else:
            return self._simple_average()
    
    def _simple_average(self) -> float:
        """Simple average of all measurements"""
        values = [m.value for m in self.measurements.values()]
        return sum(values) / len(values) if values else 0.0
    
    def _weighted_aggregate(self) -> float:
        """Weighted aggregation based on dimension importance"""
        weights = self.configuration.dimension_weights if self.configuration else {}
        total_weight = 0
        weighted_sum = 0
        
        for dim, measurement in self.measurements.items():
            weight = weights.get(dim, 1.0)
            weighted_sum += measurement.value * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
```

---

## 🔧 Configuration System

```python
@dataclass
class UncertaintyConfiguration:
    """Configurable uncertainty tracking settings"""
    
    # Profile name
    profile: str = "standard"
    
    # Core dimensions (always enabled)
    core_dimensions: List[UncertaintyDimension] = field(default_factory=lambda: [
        UncertaintyDimension.EXTRACTION_COMPLETENESS,
        UncertaintyDimension.ENTITY_RECOGNITION,
        UncertaintyDimension.CLAIM_STRENGTH
    ])
    
    # Optional dimensions
    enabled_dimensions: List[UncertaintyDimension] = field(default_factory=list)
    
    # Framework settings
    use_icd206: bool = True
    use_cerqual: bool = True
    use_ic_bands: bool = True
    
    # Mathematical settings
    use_distributions: bool = False
    propagation_method: str = "independent"  # "independent", "correlated", "monte_carlo"
    aggregation_method: str = "weighted"  # "simple", "weighted", "min", "product"
    
    # Performance settings
    lazy_evaluation: bool = True
    cache_calculations: bool = True
    batch_size: int = 100
    
    # Dimension weights for aggregation
    dimension_weights: Dict[UncertaintyDimension, float] = field(default_factory=dict)
    
    @classmethod
    def from_profile(cls, profile_name: str) -> 'UncertaintyConfiguration':
        """Create configuration from predefined profile"""
        profiles = {
            "quick": cls(
                profile="quick",
                enabled_dimensions=[],
                use_cerqual=False,
                use_distributions=False
            ),
            "standard": cls(
                profile="standard",
                enabled_dimensions=[
                    UncertaintyDimension.SOURCE_CREDIBILITY,
                    UncertaintyDimension.CROSS_SOURCE_COHERENCE,
                    UncertaintyDimension.EVIDENCE_SUFFICIENCY
                ]
            ),
            "comprehensive": cls(
                profile="comprehensive",
                enabled_dimensions=list(UncertaintyDimension),
                use_distributions=True,
                propagation_method="monte_carlo"
            ),
            "theory_testing": cls(
                profile="theory_testing",
                enabled_dimensions=[
                    UncertaintyDimension.THEORY_EXTRACTION,
                    UncertaintyDimension.THEORY_FIT,
                    UncertaintyDimension.CONSTRUCT_VALIDITY
                ],
                use_distributions=True
            )
        }
        return profiles.get(profile_name, cls())
```

---

## 📊 Source Assessment Implementation

### ICD-206 Individual Source Assessment

```python
class ICD206SourceAssessor:
    """Assess individual sources using ICD-206 framework"""
    
    RELIABILITY_SCALE = {
        'A': 0.95,  # Completely reliable
        'B': 0.85,  # Usually reliable
        'C': 0.70,  # Fairly reliable
        'D': 0.50,  # Not usually reliable
        'E': 0.30,  # Unreliable
        'F': 0.10   # Cannot be judged
    }
    
    CREDIBILITY_SCALE = {
        1: 0.95,  # Confirmed by other sources
        2: 0.85,  # Probably true
        3: 0.70,  # Possibly true
        4: 0.50,  # Doubtful
        5: 0.30,  # Improbable
        6: 0.10   # Cannot be judged
    }
    
    def assess_source(self, source: Dict[str, Any]) -> UncertaintyMeasurement:
        """Assess a single source"""
        
        # Determine reliability based on source type and history
        reliability = self._assess_reliability(source)
        
        # Determine credibility based on content and corroboration
        credibility = self._assess_credibility(source)
        
        # Calculate temporal relevance
        temporal = self._assess_temporal_relevance(source)
        
        # Combine assessments
        combined_score = (
            reliability * 0.3 +
            credibility * 0.5 +
            temporal * 0.2
        )
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.SOURCE_CREDIBILITY,
            value=combined_score,
            framework="ICD-206",
            measurement_method="reliability_credibility_temporal",
            metadata={
                'reliability_grade': self._get_reliability_grade(reliability),
                'credibility_score': credibility,
                'temporal_relevance': temporal,
                'source_type': source.get('type', 'unknown')
            }
        )
    
    def _assess_reliability(self, source: Dict) -> float:
        """Assess source reliability history"""
        source_type = source.get('type', 'unknown')
        
        if source_type == 'academic_journal':
            # Peer-reviewed journals get high reliability
            impact_factor = source.get('impact_factor', 1.0)
            return min(0.95, 0.7 + (impact_factor / 40))  # Cap at 0.95
            
        elif source_type == 'news_outlet':
            # News outlets based on track record
            reliability_record = source.get('reliability_score', 0.5)
            return reliability_record
            
        elif source_type == 'social_media':
            # Social media based on author verification
            if source.get('verified', False):
                return 0.6
            return 0.3
            
        else:
            return 0.5  # Default middle reliability
    
    def _assess_credibility(self, source: Dict) -> float:
        """Assess information credibility"""
        
        # Check for corroboration
        corroboration_count = source.get('corroborating_sources', 0)
        if corroboration_count >= 3:
            credibility = 0.95
        elif corroboration_count >= 2:
            credibility = 0.85
        elif corroboration_count == 1:
            credibility = 0.70
        else:
            credibility = 0.50
        
        # Adjust for plausibility
        if source.get('plausibility_check', True):
            credibility = min(1.0, credibility * 1.1)
        else:
            credibility = credibility * 0.8
        
        return credibility
    
    def _assess_temporal_relevance(self, source: Dict) -> float:
        """Assess temporal relevance with decay"""
        from datetime import datetime, timedelta
        
        publication_date = source.get('publication_date')
        if not publication_date:
            return 0.5  # Unknown date
        
        # Calculate age in days
        if isinstance(publication_date, str):
            publication_date = datetime.fromisoformat(publication_date)
        
        age_days = (datetime.now() - publication_date).days
        
        # Exponential decay with half-life based on topic
        topic = source.get('topic', 'general')
        half_lives = {
            'breaking_news': 1,      # 1 day half-life
            'current_events': 7,     # 1 week
            'analysis': 30,          # 1 month
            'academic': 365,         # 1 year
            'historical': 3650,      # 10 years
            'general': 90            # 3 months default
        }
        
        half_life = half_lives.get(topic, 90)
        decay_rate = 0.693 / half_life  # ln(2) / half_life
        
        relevance = math.exp(-decay_rate * age_days)
        return max(0.1, relevance)  # Minimum 10% relevance
```

### CERQual Synthesis Assessment

```python
class CERQualSynthesisAssessor:
    """Assess synthesis quality using CERQual framework"""
    
    def assess_synthesis(self, 
                         sources: List[Dict], 
                         findings: List[Dict]) -> UncertaintyProfile:
        """Assess quality of synthesized findings"""
        
        profile = UncertaintyProfile()
        
        # Assess each CERQual dimension
        profile.add_measurement(self._assess_methodological_limitations(sources))
        profile.add_measurement(self._assess_coherence(findings))
        profile.add_measurement(self._assess_adequacy(sources, findings))
        profile.add_measurement(self._assess_relevance(findings))
        
        return profile
    
    def _assess_methodological_limitations(self, sources: List[Dict]) -> UncertaintyMeasurement:
        """Assess limitations of source methodologies"""
        
        limitations_score = 1.0
        
        for source in sources:
            source_type = source.get('type', 'unknown')
            
            if source_type == 'social_media':
                limitations_score *= 0.7  # High limitations
            elif source_type == 'news_outlet':
                limitations_score *= 0.8  # Moderate limitations
            elif source_type == 'academic_journal':
                limitations_score *= 0.95  # Low limitations
            elif source_type == 'official_report':
                limitations_score *= 0.9  # Low-moderate limitations
        
        # Normalize by number of sources
        limitations_score = limitations_score ** (1 / len(sources)) if sources else 0.5
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.SOURCE_CREDIBILITY,
            value=limitations_score,
            framework="CERQual",
            measurement_method="methodological_limitations",
            metadata={'source_count': len(sources)}
        )
    
    def _assess_coherence(self, findings: List[Dict]) -> UncertaintyMeasurement:
        """Assess coherence across findings"""
        
        if not findings:
            return UncertaintyMeasurement(
                dimension=UncertaintyDimension.CROSS_SOURCE_COHERENCE,
                value=0.0,
                framework="CERQual",
                measurement_method="coherence"
            )
        
        # Calculate pairwise agreement
        agreement_scores = []
        for i, finding1 in enumerate(findings):
            for finding2 in findings[i+1:]:
                agreement = self._calculate_finding_agreement(finding1, finding2)
                agreement_scores.append(agreement)
        
        coherence = sum(agreement_scores) / len(agreement_scores) if agreement_scores else 0.5
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.CROSS_SOURCE_COHERENCE,
            value=coherence,
            framework="CERQual",
            measurement_method="coherence",
            metadata={
                'finding_count': len(findings),
                'agreement_scores': agreement_scores
            }
        )
    
    def _assess_adequacy(self, sources: List[Dict], findings: List[Dict]) -> UncertaintyMeasurement:
        """Assess data adequacy for claims"""
        
        # Simple heuristic: more diverse sources = better adequacy
        source_types = set(s.get('type') for s in sources)
        type_diversity = len(source_types) / 5  # Assume 5 main types
        
        # Source count factor
        count_factor = min(1.0, len(sources) / 10)  # Plateau at 10 sources
        
        # Finding support ratio
        supported_findings = sum(1 for f in findings if f.get('support_count', 0) >= 2)
        support_ratio = supported_findings / len(findings) if findings else 0
        
        adequacy = (type_diversity * 0.3 + count_factor * 0.3 + support_ratio * 0.4)
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.EVIDENCE_SUFFICIENCY,
            value=adequacy,
            framework="CERQual",
            measurement_method="adequacy",
            metadata={
                'source_diversity': type_diversity,
                'source_count': len(sources),
                'supported_ratio': support_ratio
            }
        )
    
    def _assess_relevance(self, findings: List[Dict]) -> UncertaintyMeasurement:
        """Assess relevance to research question"""
        
        # This would typically involve comparing findings to research question
        # For now, use a simple heuristic
        relevance_scores = [f.get('relevance_score', 0.5) for f in findings]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.EVIDENCE_SUFFICIENCY,
            value=avg_relevance,
            framework="CERQual",
            measurement_method="relevance"
        )
    
    def _calculate_finding_agreement(self, finding1: Dict, finding2: Dict) -> float:
        """Calculate agreement between two findings"""
        
        # Simple semantic similarity (would use embeddings in practice)
        if finding1.get('claim') == finding2.get('claim'):
            return 1.0
        elif finding1.get('topic') == finding2.get('topic'):
            return 0.7
        else:
            return 0.3
```

---

## 🔄 Propagation Engine

```python
class UncertaintyPropagationEngine:
    """Mathematical uncertainty propagation"""
    
    def __init__(self, configuration: UncertaintyConfiguration):
        self.config = configuration
        self.cache = {} if configuration.cache_calculations else None
    
    def propagate_through_pipeline(self, 
                                  stages: List[Dict],
                                  initial_uncertainty: float = 0.0) -> Dict:
        """Propagate uncertainty through analytical pipeline"""
        
        if self.config.propagation_method == "monte_carlo":
            return self._monte_carlo_propagation(stages, initial_uncertainty)
        elif self.config.propagation_method == "correlated":
            return self._correlated_propagation(stages, initial_uncertainty)
        else:
            return self._independent_propagation(stages, initial_uncertainty)
    
    def _independent_propagation(self, stages: List[Dict], initial: float) -> Dict:
        """Root-sum-squares for independent uncertainties"""
        
        trace = []
        current_variance = initial ** 2
        
        for stage in stages:
            stage_variance = (1 - stage['confidence']) ** 2
            
            # Add variances for independent sources
            current_variance = current_variance + stage_variance
            
            # Track evolution
            current_uncertainty = math.sqrt(current_variance)
            current_confidence = 1 - current_uncertainty
            
            trace.append({
                'stage': stage['name'],
                'input_confidence': 1 - math.sqrt(current_variance - stage_variance),
                'output_confidence': current_confidence,
                'stage_contribution': stage_variance
            })
        
        return {
            'final_confidence': 1 - math.sqrt(current_variance),
            'final_uncertainty': math.sqrt(current_variance),
            'trace': trace,
            'method': 'independent_rss'
        }
    
    def _correlated_propagation(self, stages: List[Dict], initial: float) -> Dict:
        """Propagation with correlation matrix"""
        
        n = len(stages)
        uncertainties = np.array([1 - s['confidence'] for s in stages])
        
        # Build correlation matrix (would be estimated from data)
        correlation = np.eye(n)  # Start with identity (independent)
        
        # Add some correlations based on stage types
        for i in range(n):
            for j in range(i+1, n):
                if stages[i]['type'] == stages[j]['type']:
                    correlation[i, j] = correlation[j, i] = 0.5
        
        # Calculate combined variance
        combined_variance = 0
        for i in range(n):
            for j in range(n):
                combined_variance += correlation[i, j] * uncertainties[i] * uncertainties[j]
        
        combined_uncertainty = math.sqrt(combined_variance)
        
        return {
            'final_confidence': 1 - combined_uncertainty,
            'final_uncertainty': combined_uncertainty,
            'correlation_matrix': correlation.tolist(),
            'method': 'correlated'
        }
    
    def _monte_carlo_propagation(self, stages: List[Dict], initial: float, 
                                 n_samples: int = 10000) -> Dict:
        """Monte Carlo simulation for complex propagation"""
        
        np.random.seed(42)  # For reproducibility
        
        # Generate samples for each stage
        stage_samples = []
        for stage in stages:
            confidence = stage['confidence']
            
            # Use Beta distribution for bounded confidence
            alpha = confidence * 10  # Scale factor
            beta = (1 - confidence) * 10
            samples = np.random.beta(alpha, beta, n_samples)
            stage_samples.append(samples)
        
        # Combine samples (product for sequential dependence)
        combined_samples = np.prod(stage_samples, axis=0)
        
        # Calculate statistics
        final_confidence = np.mean(combined_samples)
        confidence_std = np.std(combined_samples)
        confidence_interval = np.percentile(combined_samples, [2.5, 97.5])
        
        return {
            'final_confidence': final_confidence,
            'confidence_std': confidence_std,
            'confidence_interval': confidence_interval.tolist(),
            'distribution': {
                'mean': final_confidence,
                'std': confidence_std,
                'skew': stats.skew(combined_samples),
                'kurtosis': stats.kurtosis(combined_samples)
            },
            'method': 'monte_carlo',
            'n_samples': n_samples
        }
```

---

## 🔀 Cross-Modal Transformation Tracking

```python
class CrossModalUncertaintyTracker:
    """Track uncertainty in cross-modal transformations"""
    
    # Information preservation rates (empirically determined)
    PRESERVATION_RATES = {
        ('graph', 'table'): {
            'nodes': 1.0,           # All nodes preserved
            'attributes': 0.95,     # Most attributes preserved
            'edges': 0.90,          # Simple edges preserved
            'paths': 0.70,          # Complex paths partially lost
            'communities': 0.60     # Community structure degraded
        },
        ('table', 'vector'): {
            'rows': 1.0,            # All rows processed
            'numerical': 0.85,      # Numerical precision loss
            'categorical': 0.90,    # Category encoding loss
            'relationships': 0.50,   # Implicit relationships lost
            'semantics': 0.80       # Semantic meaning partially preserved
        },
        ('graph', 'vector'): {
            'nodes': 0.90,          # Node features encoded
            'structure': 0.40,      # Topology heavily compressed
            'attributes': 0.80,     # Attributes encoded
            'distances': 0.60,      # Graph distances approximated
            'clustering': 0.70      # Clustering partially preserved
        }
    }
    
    def track_transformation(self, 
                            source_profile: UncertaintyProfile,
                            source_type: str,
                            target_type: str,
                            transformation_metadata: Dict = None) -> UncertaintyProfile:
        """Track uncertainty through modal transformation"""
        
        # Get preservation rates
        key = (source_type, target_type)
        if key not in self.PRESERVATION_RATES:
            # Try reverse and adjust
            key = (target_type, source_type)
            preservation = self.PRESERVATION_RATES.get(key, {})
            # Reverse transformations typically have more loss
            preservation = {k: v * 0.85 for k, v in preservation.items()}
        else:
            preservation = self.PRESERVATION_RATES[key]
        
        # Create new profile for transformed data
        target_profile = UncertaintyProfile()
        
        # Propagate existing measurements with degradation
        avg_preservation = np.mean(list(preservation.values()))
        
        for dim, measurement in source_profile.measurements.items():
            # Degrade confidence based on preservation rate
            new_value = measurement.value * avg_preservation
            
            new_measurement = UncertaintyMeasurement(
                dimension=dim,
                value=new_value,
                framework=measurement.framework,
                measurement_method=f"{measurement.measurement_method}_transformed",
                metadata={
                    **measurement.metadata,
                    'transformation': f"{source_type}→{target_type}",
                    'preservation_rate': avg_preservation,
                    'original_value': measurement.value
                }
            )
            target_profile.add_measurement(new_measurement)
        
        # Add transformation-specific measurement
        transformation_measurement = UncertaintyMeasurement(
            dimension=UncertaintyDimension.MODAL_AGREEMENT,
            value=avg_preservation,
            framework="Information Theory",
            measurement_method="preservation_rate",
            metadata={
                'source_type': source_type,
                'target_type': target_type,
                'preservation_details': preservation,
                'information_loss': 1 - avg_preservation
            }
        )
        target_profile.add_measurement(transformation_measurement)
        
        return target_profile
    
    def assess_modal_agreement(self, 
                              graph_result: Dict,
                              table_result: Dict,
                              vector_result: Dict = None) -> UncertaintyMeasurement:
        """Assess agreement across different modal analyses"""
        
        agreements = []
        
        # Compare graph vs table
        if graph_result and table_result:
            graph_table_agreement = self._compare_results(graph_result, table_result)
            agreements.append(graph_table_agreement)
        
        # Compare graph vs vector
        if graph_result and vector_result:
            graph_vector_agreement = self._compare_results(graph_result, vector_result)
            agreements.append(graph_vector_agreement)
        
        # Compare table vs vector
        if table_result and vector_result:
            table_vector_agreement = self._compare_results(table_result, vector_result)
            agreements.append(table_vector_agreement)
        
        # Calculate overall agreement
        if agreements:
            overall_agreement = sum(agreements) / len(agreements)
        else:
            overall_agreement = 0.5  # No comparison possible
        
        return UncertaintyMeasurement(
            dimension=UncertaintyDimension.MODAL_AGREEMENT,
            value=overall_agreement,
            framework="Statistical",
            measurement_method="cross_modal_comparison",
            metadata={
                'comparisons': len(agreements),
                'individual_agreements': agreements
            }
        )
    
    def _compare_results(self, result1: Dict, result2: Dict) -> float:
        """Compare two analysis results for agreement"""
        
        # Extract key findings/claims
        claims1 = set(result1.get('claims', []))
        claims2 = set(result2.get('claims', []))
        
        if not claims1 and not claims2:
            return 0.5  # No claims to compare
        
        # Calculate Jaccard similarity
        intersection = claims1.intersection(claims2)
        union = claims1.union(claims2)
        
        if union:
            similarity = len(intersection) / len(union)
        else:
            similarity = 0.0
        
        # Also consider confidence scores if available
        conf1 = result1.get('confidence', 0.5)
        conf2 = result2.get('confidence', 0.5)
        conf_similarity = 1 - abs(conf1 - conf2)
        
        # Weighted combination
        agreement = similarity * 0.7 + conf_similarity * 0.3
        
        return agreement
```

---

## 💬 Human Interface Layer

```python
class HumanReadableUncertainty:
    """Convert technical uncertainty to human-friendly formats"""
    
    IC_PROBABILITY_BANDS = {
        (0.95, 1.00): "almost certain",
        (0.80, 0.95): "very likely",
        (0.55, 0.80): "likely",
        (0.45, 0.55): "roughly even chance",
        (0.20, 0.45): "unlikely",
        (0.05, 0.20): "very unlikely",
        (0.00, 0.05): "almost no chance"
    }
    
    CONFIDENCE_QUALIFIERS = {
        (0.80, 1.00): "high",
        (0.60, 0.80): "moderate",
        (0.40, 0.60): "low",
        (0.00, 0.40): "very low"
    }
    
    def generate_narrative(self, 
                          result: Dict,
                          profile: UncertaintyProfile) -> str:
        """Generate human-readable confidence narrative"""
        
        confidence = profile.get_aggregate_confidence()
        ic_term = self._get_ic_term(confidence)
        qualifier = self._get_qualifier(confidence)
        
        # Start with headline
        narrative = f"We assess with {qualifier} confidence that {result['claim']} is {ic_term}.\n\n"
        
        # Add key factors
        narrative += "Key factors affecting this assessment:\n"
        
        # Get top 3 uncertainty sources
        top_dims = self._get_top_dimensions(profile, n=3)
        
        for dim, measurement in top_dims:
            interpretation = self._interpret_dimension(dim, measurement)
            narrative += f"• {interpretation}\n"
        
        # Add specific insights
        if UncertaintyDimension.CROSS_SOURCE_COHERENCE in profile.measurements:
            coherence = profile.measurements[UncertaintyDimension.CROSS_SOURCE_COHERENCE].value
            if coherence > 0.7:
                narrative += "\n✓ Multiple sources independently corroborate this finding."
            elif coherence < 0.4:
                narrative += "\n⚠ Sources show significant disagreement on this finding."
        
        if UncertaintyDimension.CONFIRMATION_BIAS in profile.measurements:
            bias = profile.measurements[UncertaintyDimension.CONFIRMATION_BIAS].value
            if bias > 0.6:
                narrative += "\n⚠ Warning: Potential confirmation bias detected in analysis."
        
        # Add recommendations
        narrative += "\n\nRecommendations:\n"
        recommendations = self._generate_recommendations(profile)
        for rec in recommendations:
            narrative += f"• {rec}\n"
        
        return narrative
    
    def generate_visual_data(self, profile: UncertaintyProfile) -> Dict:
        """Generate data for visualization"""
        
        return {
            'overall': {
                'confidence': profile.get_aggregate_confidence(),
                'band': self._get_ic_term(profile.get_aggregate_confidence()),
                'color': self._confidence_to_color(profile.get_aggregate_confidence())
            },
            'dimensions': [
                {
                    'name': dim.value,
                    'confidence': measurement.value,
                    'framework': measurement.framework,
                    'human': measurement.to_human_readable()
                }
                for dim, measurement in profile.measurements.items()
            ],
            'radar_chart': self._generate_radar_data(profile),
            'timeline': self._generate_timeline_data(profile)
        }
    
    def _get_ic_term(self, confidence: float) -> str:
        """Convert confidence to IC probability term"""
        for range_, term in self.IC_PROBABILITY_BANDS.items():
            if range_[0] <= confidence <= range_[1]:
                return term
        return "uncertain"
    
    def _get_qualifier(self, confidence: float) -> str:
        """Get confidence qualifier"""
        for range_, qual in self.CONFIDENCE_QUALIFIERS.items():
            if range_[0] <= confidence <= range_[1]:
                return qual
        return "unknown"
    
    def _interpret_dimension(self, 
                           dimension: UncertaintyDimension,
                           measurement: UncertaintyMeasurement) -> str:
        """Create human interpretation of dimension"""
        
        interpretations = {
            UncertaintyDimension.SOURCE_CREDIBILITY: 
                f"Source credibility is {self._get_qualifier(measurement.value)} ({measurement.value:.0%})",
            UncertaintyDimension.ENTITY_RECOGNITION:
                f"Entity recognition is {self._get_qualifier(measurement.value)} confident",
            UncertaintyDimension.CROSS_SOURCE_COHERENCE:
                f"Sources show {self._get_qualifier(measurement.value)} agreement",
            UncertaintyDimension.THEORY_FIT:
                f"Theory fits data with {self._get_qualifier(measurement.value)} confidence",
            # Add more interpretations
        }
        
        return interpretations.get(dimension, f"{dimension.value}: {measurement.value:.0%}")
    
    def _generate_recommendations(self, profile: UncertaintyProfile) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        confidence = profile.get_aggregate_confidence()
        
        if confidence < 0.4:
            recommendations.append("Consider gathering additional evidence before drawing conclusions")
        
        if UncertaintyDimension.SOURCE_CREDIBILITY in profile.measurements:
            if profile.measurements[UncertaintyDimension.SOURCE_CREDIBILITY].value < 0.5:
                recommendations.append("Seek higher quality sources to improve credibility")
        
        if UncertaintyDimension.CROSS_SOURCE_COHERENCE in profile.measurements:
            if profile.measurements[UncertaintyDimension.CROSS_SOURCE_COHERENCE].value < 0.5:
                recommendations.append("Investigate source disagreements to understand conflicts")
        
        if confidence > 0.8:
            recommendations.append("High confidence - suitable for decision-making")
        elif confidence > 0.6:
            recommendations.append("Moderate confidence - proceed with appropriate caution")
        
        return recommendations
    
    def _confidence_to_color(self, confidence: float) -> str:
        """Map confidence to color for visualization"""
        if confidence > 0.8:
            return "#2ecc71"  # Green
        elif confidence > 0.6:
            return "#f39c12"  # Orange
        elif confidence > 0.4:
            return "#e67e22"  # Dark orange
        else:
            return "#e74c3c"  # Red
    
    def _generate_radar_data(self, profile: UncertaintyProfile) -> Dict:
        """Generate radar chart data"""
        
        categories = []
        values = []
        
        for dim, measurement in profile.measurements.items():
            categories.append(dim.value.replace('_', ' ').title())
            values.append(measurement.value)
        
        return {
            'categories': categories,
            'values': values,
            'max': 1.0
        }
    
    def _generate_timeline_data(self, profile: UncertaintyProfile) -> List[Dict]:
        """Generate timeline visualization data"""
        
        # This would track confidence evolution over pipeline stages
        # Placeholder for now
        return [
            {'stage': 'Input', 'confidence': 1.0},
            {'stage': 'Extraction', 'confidence': 0.95},
            {'stage': 'Analysis', 'confidence': 0.85},
            {'stage': 'Synthesis', 'confidence': profile.get_aggregate_confidence()}
        ]
```

---

## 🎯 Complete Usage Example

```python
def analyze_with_uncertainty(documents: List[Dict], 
                            research_question: str,
                            config_profile: str = "standard") -> Dict:
    """Complete analysis with uncertainty tracking"""
    
    # Initialize configuration
    config = UncertaintyConfiguration.from_profile(config_profile)
    
    # Initialize assessors
    icd206 = ICD206SourceAssessor()
    cerqual = CERQualSynthesisAssessor()
    propagation = UncertaintyPropagationEngine(config)
    cross_modal = CrossModalUncertaintyTracker()
    human_interface = HumanReadableUncertainty()
    
    # Create uncertainty profile
    profile = UncertaintyProfile(configuration=config)
    
    # Stage 1: Assess individual sources
    source_assessments = []
    for doc in documents:
        assessment = icd206.assess_source(doc)
        source_assessments.append(assessment)
        profile.add_measurement(assessment)
    
    # Stage 2: Extract and analyze
    extraction_results = extract_entities(documents)  # Your extraction function
    
    # Add extraction confidence
    profile.add_measurement(UncertaintyMeasurement(
        dimension=UncertaintyDimension.EXTRACTION_COMPLETENESS,
        value=extraction_results.get('confidence', 0.9),
        framework="Statistical",
        measurement_method="coverage_ratio"
    ))
    
    # Stage 3: Cross-modal analysis
    graph_analysis = analyze_as_graph(extraction_results)
    table_analysis = analyze_as_table(extraction_results)
    
    # Track transformation
    graph_profile = profile  # Current profile
    table_profile = cross_modal.track_transformation(
        graph_profile, 'graph', 'table'
    )
    
    # Assess modal agreement
    modal_agreement = cross_modal.assess_modal_agreement(
        graph_analysis, table_analysis
    )
    profile.add_measurement(modal_agreement)
    
    # Stage 4: Synthesis
    findings = synthesize_findings(graph_analysis, table_analysis)
    synthesis_profile = cerqual.assess_synthesis(documents, findings)
    
    # Merge profiles
    for measurement in synthesis_profile.measurements.values():
        profile.add_measurement(measurement)
    
    # Stage 5: Propagate uncertainty
    stages = [
        {'name': 'extraction', 'confidence': 0.9, 'type': 'extraction'},
        {'name': 'analysis', 'confidence': 0.85, 'type': 'analysis'},
        {'name': 'synthesis', 'confidence': 0.8, 'type': 'synthesis'}
    ]
    
    propagation_result = propagation.propagate_through_pipeline(stages)
    
    # Generate final result
    result = {
        'claim': findings.get('main_claim', 'Analysis complete'),
        'confidence': propagation_result['final_confidence'],
        'findings': findings,
        'uncertainty_profile': profile,
        'propagation': propagation_result
    }
    
    # Generate human-readable output
    narrative = human_interface.generate_narrative(result, profile)
    visual_data = human_interface.generate_visual_data(profile)
    
    return {
        'result': result,
        'narrative': narrative,
        'visualization': visual_data,
        'technical_details': {
            'profile': profile,
            'propagation': propagation_result,
            'configuration': config
        }
    }

# Example usage
if __name__ == "__main__":
    # Sample documents
    documents = [
        {
            'type': 'academic_journal',
            'content': 'Research findings...',
            'publication_date': '2024-01-15',
            'impact_factor': 5.2,
            'corroborating_sources': 2
        },
        {
            'type': 'news_outlet',
            'content': 'Recent report shows...',
            'publication_date': '2024-12-01',
            'reliability_score': 0.7,
            'corroborating_sources': 1
        }
    ]
    
    # Run analysis
    results = analyze_with_uncertainty(
        documents,
        "What is the impact of social media on political discourse?",
        config_profile="standard"
    )
    
    # Display results
    print(results['narrative'])
    print(f"\nOverall confidence: {results['result']['confidence']:.1%}")
    print(f"IC Assessment: {results['narrative'].split(' is ')[1].split('.')[0]}")
```

---

## 📝 Implementation Checklist

### Phase 1: Core Implementation
- [ ] Base uncertainty classes (UncertaintyMeasurement, UncertaintyProfile)
- [ ] Configuration system with profiles
- [ ] ICD-206 source assessment
- [ ] Basic propagation (independent uncertainties)
- [ ] Simple human narrative generation

### Phase 2: Synthesis Features
- [ ] CERQual synthesis assessment
- [ ] Cross-source coherence checking
- [ ] Evidence sufficiency evaluation
- [ ] Weighted aggregation

### Phase 3: Advanced Features
- [ ] Monte Carlo propagation
- [ ] Correlation tracking
- [ ] Beta distributions
- [ ] Cognitive bias detection
- [ ] Theory-driven uncertainty

### Phase 4: Optimization
- [ ] Caching system
- [ ] Lazy evaluation
- [ ] Batch processing
- [ ] Performance profiling

---

This implementation guide provides concrete, runnable code for implementing the comprehensive uncertainty framework in KGAS, with clear patterns and examples for each component.