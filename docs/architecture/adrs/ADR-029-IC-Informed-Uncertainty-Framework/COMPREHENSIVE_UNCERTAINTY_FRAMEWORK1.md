# KGAS Comprehensive Uncertainty Framework
## Complete Specification with Unified Measurement Matrix

**Version**: 1.0  
**Date**: 2025-08-06  
**Status**: Comprehensive Design Document  
**Primary Goal**: Human interpretability and understanding of confidence/uncertainty  
**Secondary Goal**: Support autonomous agent decision-making  

---

## 📋 Executive Summary

This document provides the complete specification for KGAS's uncertainty and confidence framework, integrating Intelligence Community (IC) methodologies, academic research standards, and practical implementation considerations. The framework prioritizes human understanding of uncertainty while maintaining mathematical rigor and supporting configurable analysis modes.

### Key Principles
1. **Human-First Design**: All uncertainty must be interpretable by human researchers
2. **Configurable Depth**: Different analysis types require different uncertainty tracking
3. **Mathematical Rigor**: Proper propagation without false precision
4. **Evidence-Based**: Quality over quantity in assessment
5. **Pragmatic Implementation**: Avoid overengineering while maximizing capability

---

## 🎯 Framework Architecture

### Three Conceptual Layers (Not Hierarchical Levels)

```
┌─────────────────────────────────────────────────────────┐
│                    Human Interface                       │
│  Natural language confidence narratives, visualizations  │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│              Unified Uncertainty Tracking                │
│  Multiple parallel dimensions, configurable features     │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│              Mathematical Propagation Engine             │
│  Beta distributions, covariance tracking, Monte Carlo    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Unified Uncertainty Measurement Matrix

### Complete Dimension Specification

| **Uncertainty Dimension** | **Origin Point** | **Measurement Method** | **Framework** | **Propagation** | **Human Interpretation** | **Configurable?** | **Priority** |
|--------------------------|------------------|----------------------|--------------|----------------|-------------------------|------------------|--------------|
| **SOURCE QUALITY - INDIVIDUAL** | | | | | | | |
| Source Credibility | Data ingestion | Credibility indicators, expertise | ICD-206 | Weights aggregation | "Can we trust this source?" | Yes | Core |
| Information Credibility | Data ingestion | Corroboration, plausibility | ICD-206 | Per-claim basis | "Is this believable?" | Yes | Core |
| Source Reliability History | Data ingestion | Track record, accuracy | ICD-206 | Historical weighting | "Has source been reliable?" | Yes | Advanced |
| Source Access/Placement | Data ingestion | Proximity to information | ICD-206 | Credibility modifier | "How close to the event?" | Yes | Advanced |
| Temporal Relevance | Data ingestion | Publication date, decay | Custom | Decay function | "How current is this?" | Yes | Core |
| **SOURCE QUALITY - SYNTHESIS** | | | | | | | |
| Methodological Limitations | Synthesis | Study design, sampling | CERQual | Quality gates | "What are the limitations?" | Yes | Core |
| Coherence Across Sources | Synthesis | Pattern consistency | CERQual | Convergence bonus | "Do sources agree?" | Yes | Core |
| Adequacy of Data | Synthesis | Saturation, sufficiency | CERQual | Confidence ceiling | "Is there enough evidence?" | Yes | Core |
| Relevance to Question | Synthesis | Applicability | CERQual | Relevance filter | "Does this apply?" | Yes | Core |
| **COMPUTATIONAL** | | | | | | | |
| Extraction Completeness | T01 (PDF/Text) | Coverage ratio | Statistical | Multiplicative | "How much captured?" | No | Core |
| Entity Recognition | T23A (NER) | Model confidence | IC Bands | Root-sum-squares | "How sure about entities?" | No | Core |
| Entity Boundary Uncertainty | T23A | Span confidence | NER Models | Local propagation | "Where does entity end?" | No | Advanced |
| Coreference Ambiguity | Resolution | Multiple candidates | NLP | Graph propagation | "Which entity is 'they'?" | No | Advanced |
| Relationship Validity | T27, T31, T34 | Edge confidence | Statistical | Graph structure | "Are connections real?" | Yes | Core |
| Algorithm Precision | T68, T49 | Algorithm metrics | Statistical | Result confidence | "How accurate is analysis?" | No | Core |
| **THEORETICAL** | | | | | | | |
| Theory Extraction Quality | Theory System | Completeness scores | Custom | Foundational | "How well captured theory?" | Yes | Advanced |
| Theory-Data Fit | Analysis | Goodness-of-fit | Statistical | Multiplicative | "Does theory apply?" | Yes | Advanced |
| Construct Validity | Measurement | Theory validation | Academic | Interpretation | "Measuring right thing?" | Yes | Advanced |
| Competing Theories | Synthesis | Comparative fit | Bayesian | Reconciliation | "Which theory better?" | Yes | Advanced |
| **TRANSFORMATIONAL** | | | | | | | |
| Graph→Table Preservation | Cross-modal | Retention ratio | Info Theory | Tracks loss | "What was lost?" | No | Core |
| Table→Vector Preservation | Cross-modal | Semantic similarity | Cosine | Tracks loss | "Meaning preserved?" | No | Core |
| Modal Agreement | Cross-modal | Cross-validation | Statistical | Highlights conflicts | "Do views agree?" | Yes | Core |
| Information Redundancy | Integration | Uniqueness score | Info Theory | Adjust weights | "Is this new info?" | Yes | Advanced |
| **COGNITIVE & BIAS** | | | | | | | |
| Confirmation Bias Risk | Analysis | Hypothesis diversity | Heuer/ACH | Interpretation bias | "Seeing what we expect?" | Yes | Core |
| Anchoring Effects | Initial analysis | First impression weight | IC Methods | Skews analysis | "Stuck on first idea?" | Yes | Advanced |
| Availability Heuristic | Evidence selection | Recency/salience | Cognitive | Evidence bias | "Overweighting recent?" | Yes | Advanced |
| Mirror Imaging | Interpretation | Cultural assumptions | IC Methods | Distorts understanding | "Projecting our context?" | Yes | Advanced |
| **TEMPORAL & EVOLUTION** | | | | | | | |
| Temporal Decay | Collection | Age-adjusted relevance | Custom | Exponential decay | "How stale is data?" | Yes | Core |
| Concept Drift | Longitudinal | Semantic shift | NLP | Comparability | "Has meaning changed?" | Yes | Advanced |
| Event Sequencing | Timeline | Ordering confidence | Statistical | Causality claims | "Is order correct?" | Yes | Advanced |
| **ASSUMPTIONS & HYPOTHESES** | | | | | | | |
| Key Assumptions | All stages | Criticality assessment | ACH | Foundational | "What are we assuming?" | No | Core |
| Alternative Hypotheses | Synthesis | Competing explanations | ACH/Bayesian | Reconciliation | "What else explains?" | Yes | Core |
| Assumption Violation Impact | Analysis | Sensitivity analysis | What-If | Changes conclusions | "What if wrong?" | Yes | Advanced |
| **DIAGNOSTIC VALUE** | | | | | | | |
| Evidence Diagnosticity | Assessment | Discriminating power | ACH | Importance weight | "Does this discriminate?" | Yes | Core |
| Signal vs Noise | Analysis | SNR metrics | Statistical | Filters importance | "Signal or noise?" | Yes | Advanced |
| **AGGREGATION** | | | | | | | |
| Aggregation Method Sensitivity | Synthesis | Method comparison | Statistical | Final score | "How sensitive to method?" | Yes | Advanced |
| Correlation Structure | Multi-source | Dependency matrix | Statistical | Non-independent | "Are sources correlated?" | Yes | Advanced |
| Weighting Scheme Impact | Integration | Weight sensitivity | Sensitivity | Conclusions | "How do weights affect?" | Yes | Advanced |
| **CALIBRATION** | | | | | | | |
| Calibration Error | Predictions | Predicted vs actual | Statistical | Systematic bias | "Over/under confident?" | No | Advanced |
| Out-of-Distribution | Input | Distribution distance | ML Metrics | Reliability boundary | "Outside training?" | Yes | Advanced |
| Ground Truth Availability | Validation | Verification possibility | Empirical | Enables calibration | "Can we verify?" | Yes | Core |
| **DECISION CONTEXT** | | | | | | | |
| Decision Criticality | Output | Impact assessment | Decision Theory | Threshold adjustment | "How important?" | Yes | Core |
| Risk Tolerance | Application | Acceptable error | User-defined | Gates actions | "Risk appetite?" | Yes | Core |
| Action Reversibility | Decision | Undo cost | Decision Theory | Caution level | "Can we undo?" | Yes | Advanced |
| **SYNTHESIS** | | | | | | | |
| Cross-Source Coherence | Integration | Agreement metrics | CERQual | Weighted average | "Do sources agree?" | Yes | Core |
| Multi-Theory Consistency | Integration | Theory alignment | Custom | Resolution required | "Do theories conflict?" | Yes | Advanced |
| Evidence Sufficiency | Final analysis | Coverage requirements | CERQual | Gates confidence | "Enough evidence?" | Yes | Core |
| Claim Strength | Output | Aggregated confidence | IC Bands | Final score | "How confident?" | No | Core |

---

## 🔧 Configuration Profiles

### Analysis Type Configurations

| **Profile** | **Use Case** | **Enabled Dimensions** | **Typical Timeline** |
|------------|-------------|----------------------|-------------------|
| **Quick Analysis** | Rapid assessment | Core only | < 1 hour |
| **Standard Research** | Academic paper | Core + ICD-206 + CERQual | Days |
| **Multi-Source Synthesis** | Diverse sources (tweets+papers) | Core + Full source assessment | Days-Weeks |
| **Theory Testing** | Theory validation | Core + Theoretical + ACH | Weeks |
| **Deep Investigation** | Complete analysis | All dimensions | Weeks-Months |
| **Exploratory** | Initial exploration | Core + Cognitive bias | Hours-Days |

### Configuration Schema

```python
@dataclass
class UncertaintyConfiguration:
    """Configurable uncertainty tracking settings"""
    
    # Core features (always enabled)
    track_computational: bool = True
    track_extraction: bool = True
    track_basic_source: bool = True
    
    # Source assessment
    use_icd206_individual: bool = True  # Individual source assessment
    use_cerqual_synthesis: bool = True  # Multi-source synthesis
    track_temporal_decay: bool = True
    
    # Advanced tracking
    track_cognitive_bias: bool = False
    track_assumptions: bool = True
    track_alternatives: bool = True
    
    # Theory integration
    use_theory_extraction: bool = False
    track_theory_fit: bool = False
    track_competing_theories: bool = False
    
    # Cross-modal
    track_transformation_loss: bool = True
    track_modal_agreement: bool = True
    
    # Mathematical rigor
    use_distributions: bool = False  # vs point estimates
    track_correlations: bool = False
    use_monte_carlo: bool = False
    
    # Performance trade-offs
    lazy_evaluation: bool = True
    cache_calculations: bool = True
    batch_propagation: bool = True
```

---

## 📐 Mathematical Framework

### Core Propagation Rules

#### 1. Independent Uncertainties (Root-Sum-Squares)
```python
def propagate_independent(uncertainties: List[float]) -> float:
    """
    For independent uncertainty sources
    σ_total = √(σ₁² + σ₂² + ... + σₙ²)
    """
    variances = [(1 - conf)**2 for conf in uncertainties]
    combined_variance = sum(variances)
    return 1 - math.sqrt(combined_variance)
```

#### 2. Dependent Uncertainties (Covariance)
```python
def propagate_dependent(uncertainties: List[float], 
                       correlation_matrix: np.ndarray) -> float:
    """
    For correlated uncertainty sources
    Requires correlation structure
    """
    n = len(uncertainties)
    combined_variance = 0
    
    for i in range(n):
        for j in range(n):
            var_i = (1 - uncertainties[i])**2
            var_j = (1 - uncertainties[j])**2
            correlation = correlation_matrix[i, j]
            combined_variance += correlation * math.sqrt(var_i * var_j)
    
    return 1 - math.sqrt(combined_variance)
```

#### 3. Beta Distribution for Bounded Confidence
```python
class BetaConfidence:
    """
    Maintain full distribution instead of point estimates
    Beta distribution natural for [0,1] bounded confidence
    """
    def __init__(self, successes: int, failures: int):
        self.alpha = successes + 1  # Laplace smoothing
        self.beta = failures + 1
    
    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def variance(self) -> float:
        ab = self.alpha + self.beta
        return (self.alpha * self.beta) / (ab**2 * (ab + 1))
    
    @property
    def confidence_interval(self, level=0.95) -> Tuple[float, float]:
        return stats.beta.interval(level, self.alpha, self.beta)
```

---

## 🔄 Propagation Patterns

### Through Tool Pipeline

```python
def propagate_through_pipeline(stages: List[Dict]) -> Dict:
    """
    Track uncertainty through complete analytical pipeline
    """
    uncertainty_trace = []
    current_uncertainty = 0.0
    
    for stage in stages:
        # Add stage-specific uncertainty
        stage_uncertainty = stage['uncertainty']
        
        if stage['type'] == 'extraction':
            # Additive for extraction errors
            current_uncertainty = propagate_independent(
                [current_uncertainty, stage_uncertainty]
            )
        elif stage['type'] == 'transformation':
            # Track information loss
            info_retained = stage.get('retention_ratio', 0.95)
            current_uncertainty = current_uncertainty / info_retained
        elif stage['type'] == 'synthesis':
            # Can reduce uncertainty through corroboration
            if stage.get('corroboration_factor', 1.0) > 1:
                current_uncertainty = current_uncertainty / stage['corroboration_factor']
        
        uncertainty_trace.append({
            'stage': stage['name'],
            'uncertainty': current_uncertainty,
            'type': stage['type']
        })
    
    return {
        'final_uncertainty': current_uncertainty,
        'final_confidence': 1 - current_uncertainty,
        'trace': uncertainty_trace
    }
```

### Cross-Modal Propagation

```python
class CrossModalUncertaintyTracker:
    """
    Track uncertainty across Graph ↔ Table ↔ Vector transformations
    """
    
    TRANSFORMATION_LOSS = {
        ('graph', 'table'): {
            'structural_loss': 0.05,      # 5% typical loss
            'relationship_loss': 0.10,     # Complex relationships lost
            'attribute_preservation': 0.95  # Most attributes preserved
        },
        ('table', 'vector'): {
            'semantic_preservation': 0.90,  # Some semantic loss
            'structure_loss': 0.15,         # Table structure lost
            'numerical_preservation': 0.85  # Numerical precision loss
        },
        ('graph', 'vector'): {
            'topology_loss': 0.20,          # Graph structure lost
            'semantic_preservation': 0.85,   # Semantic meaning preserved
            'relationship_encoding': 0.70    # Relationships partially encoded
        }
    }
    
    def track_transformation(self, 
                           source_confidence: float,
                           source_type: str,
                           target_type: str) -> Dict:
        """
        Track what's lost in transformation
        """
        key = (source_type, target_type)
        if key not in self.TRANSFORMATION_LOSS:
            # Reverse transformation
            key = (target_type, source_type)
            loss_factors = self.TRANSFORMATION_LOSS.get(key, {})
            # Reverse transformations may have different loss
            loss_factors = {k: v * 0.9 for k, v in loss_factors.items()}
        else:
            loss_factors = self.TRANSFORMATION_LOSS[key]
        
        # Calculate aggregate preservation
        total_preservation = np.prod(list(loss_factors.values()))
        
        return {
            'output_confidence': source_confidence * total_preservation,
            'information_retained': total_preservation,
            'specific_losses': loss_factors,
            'transformation': f"{source_type}→{target_type}"
        }
```

---

## 🎭 Framework Application Patterns

### Pattern 1: Individual Source Assessment (ICD-206)

```python
def assess_individual_source(source: DataSource) -> SourceAssessment:
    """
    Apply ICD-206 to individual source as it enters system
    """
    assessment = {
        'reliability': assess_reliability_history(source),  # A-F scale
        'credibility': assess_author_credibility(source),   # 1-6 scale
        'access': assess_information_access(source),
        'corroboration': check_independent_confirmation(source),
        'plausibility': assess_logical_consistency(source),
        'timeliness': calculate_temporal_relevance(source)
    }
    
    # Convert to weight for aggregation
    weight = icd206_to_weight(assessment)
    
    return SourceAssessment(
        source_id=source.id,
        assessment=assessment,
        weight=weight,
        framework='ICD-206'
    )
```

### Pattern 2: Multi-Source Synthesis (CERQual)

```python
def assess_synthesis_quality(sources: List[DataSource], 
                            findings: List[Finding]) -> SynthesisAssessment:
    """
    Apply CERQual when synthesizing multiple sources
    """
    # Individual source weights from ICD-206
    source_weights = [s.icd206_weight for s in sources]
    
    # CERQual dimensions for synthesis
    cerqual = {
        'methodological_limitations': assess_collective_limitations(sources),
        'coherence': calculate_cross_source_agreement(findings),
        'adequacy': evaluate_data_sufficiency(sources, findings),
        'relevance': assess_applicability_to_question(findings)
    }
    
    # Combine frameworks
    synthesis_confidence = combine_assessments(
        icd206_weights=source_weights,
        cerqual_assessment=cerqual
    )
    
    return SynthesisAssessment(
        confidence=synthesis_confidence,
        cerqual=cerqual,
        source_count=len(sources),
        framework='ICD-206 + CERQual'
    )
```

### Pattern 3: Cognitive Bias Detection (IC Methods)

```python
def detect_cognitive_biases(analysis: Analysis) -> BiasAssessment:
    """
    Apply IC cognitive bias detection methods
    """
    biases_detected = []
    
    # Confirmation Bias
    hypothesis_diversity = calculate_hypothesis_diversity(analysis)
    if hypothesis_diversity < 0.3:
        biases_detected.append({
            'type': 'confirmation_bias',
            'severity': 'high',
            'evidence': 'Limited alternative hypotheses considered',
            'mitigation': 'Generate competing explanations'
        })
    
    # Anchoring
    first_impression_weight = analyze_initial_influence(analysis)
    if first_impression_weight > 0.5:
        biases_detected.append({
            'type': 'anchoring',
            'severity': 'medium',
            'evidence': 'Early evidence overly influential',
            'mitigation': 'Re-evaluate without initial evidence'
        })
    
    # Availability Heuristic
    recency_bias = calculate_recency_weighting(analysis)
    if recency_bias > 0.6:
        biases_detected.append({
            'type': 'availability_heuristic',
            'severity': 'medium',
            'evidence': 'Recent events overweighted',
            'mitigation': 'Include historical perspective'
        })
    
    return BiasAssessment(
        biases=biases_detected,
        overall_bias_risk=calculate_aggregate_bias_risk(biases_detected),
        recommended_mitigations=generate_mitigation_plan(biases_detected)
    )
```

### Pattern 4: Theory-Driven Uncertainty

```python
def assess_theory_uncertainty(theory: ExtractedTheory,
                             data: Dataset) -> TheoryAssessment:
    """
    Assess uncertainty in theory application
    """
    return {
        'extraction_quality': theory.extraction_confidence,
        'theory_data_fit': calculate_goodness_of_fit(theory, data),
        'construct_validity': assess_measurement_validity(theory, data),
        'competing_theories': evaluate_alternative_theories(theory, data),
        'applicability': assess_theory_applicability(theory, data.context)
    }
```

---

## 💬 Human Interpretation Layer

### Natural Language Confidence Expression

```python
class HumanReadableConfidence:
    """
    Convert technical confidence scores to human-friendly narratives
    """
    
    IC_BANDS = {
        (0.95, 1.00): "almost certain",
        (0.80, 0.95): "very likely",
        (0.55, 0.80): "likely",
        (0.45, 0.55): "roughly even chance",
        (0.20, 0.45): "unlikely",
        (0.05, 0.20): "very unlikely",
        (0.00, 0.05): "almost no chance"
    }
    
    def generate_confidence_narrative(self, result: AnalysisResult) -> str:
        """
        Create human-readable confidence explanation
        """
        confidence = result.final_confidence
        ic_term = self.confidence_to_ic_term(confidence)
        
        # Identify main uncertainty sources
        top_uncertainties = self.identify_top_uncertainties(result)
        
        # Generate narrative
        narrative = f"""
        Based on the analysis, we assess with {result.assessment_confidence} confidence 
        that {result.claim} is {ic_term}.
        
        Key factors affecting confidence:
        """
        
        for uncertainty in top_uncertainties[:3]:
            narrative += f"\n• {uncertainty.dimension}: {uncertainty.human_explanation}"
        
        if result.has_corroboration:
            narrative += f"\n\nMultiple sources corroborate this finding, increasing confidence."
        
        if result.has_competing_explanations:
            narrative += f"\n\nAlternative explanations exist that could account for the evidence."
        
        narrative += f"\n\nRecommendation: {self.generate_recommendation(result)}"
        
        return narrative
    
    def generate_visual_confidence(self, result: AnalysisResult) -> Dict:
        """
        Generate visualization-friendly confidence data
        """
        return {
            'overall_confidence': {
                'value': result.final_confidence,
                'band': self.confidence_to_ic_term(result.final_confidence),
                'color': self.confidence_to_color(result.final_confidence)
            },
            'dimension_breakdown': [
                {
                    'dimension': dim.name,
                    'confidence': dim.confidence,
                    'weight': dim.weight,
                    'contribution': dim.confidence * dim.weight
                }
                for dim in result.uncertainty_dimensions
            ],
            'pipeline_trace': [
                {
                    'stage': stage.name,
                    'confidence_in': stage.input_confidence,
                    'confidence_out': stage.output_confidence,
                    'delta': stage.output_confidence - stage.input_confidence
                }
                for stage in result.pipeline_stages
            ]
        }
```

---

## 🎯 Implementation Guidelines

### 1. Core Implementation (Phase 1)
- Implement basic computational confidence tracking
- Add ICD-206 individual source assessment
- Enable IC probability bands for output
- Track extraction and recognition confidence

### 2. Synthesis Enhancement (Phase 2)
- Add CERQual for multi-source synthesis
- Implement correlation detection
- Enable cross-source coherence checking
- Add evidence sufficiency assessment

### 3. Advanced Features (Phase 3)
- Cognitive bias detection
- Theory-driven uncertainty
- Beta distributions instead of point estimates
- Monte Carlo propagation for complex cases

### 4. Optimization (Phase 4)
- Lazy evaluation for expensive calculations
- Caching for repeated assessments
- Batch propagation for efficiency
- Configurable dimension selection

---

## 📊 Usage Examples

### Example 1: Multi-Source Research Synthesis

```python
# Configure for academic research with diverse sources
config = UncertaintyConfiguration(
    use_icd206_individual=True,   # Assess each source
    use_cerqual_synthesis=True,   # Synthesis quality
    track_cognitive_bias=True,    # Academic rigor
    track_assumptions=True,        # Research transparency
    use_theory_extraction=True    # Theory-guided analysis
)

# Process sources with individual assessment
sources = []
for document in documents:
    source_assessment = assess_individual_source(document)  # ICD-206
    sources.append(source_assessment)

# Extract and synthesize findings
findings = extract_findings(sources)
synthesis = assess_synthesis_quality(sources, findings)  # CERQual

# Generate human-readable report
narrative = generate_confidence_narrative(synthesis)
```

### Example 2: Quick Analysis

```python
# Minimal configuration for speed
config = UncertaintyConfiguration(
    use_icd206_individual=False,  # Skip detailed source assessment
    use_cerqual_synthesis=False,  # Skip synthesis assessment
    track_cognitive_bias=False,   # Skip bias detection
    track_assumptions=False       # Skip assumption tracking
)

# Fast processing with core confidence only
result = quick_analysis(documents, config)
confidence = result.computational_confidence  # Basic confidence only
```

### Example 3: Theory Testing

```python
# Configure for theory validation
config = UncertaintyConfiguration(
    use_theory_extraction=True,
    track_theory_fit=True,
    track_competing_theories=True,
    track_assumptions=True,
    use_distributions=True  # Full distributions for theory testing
)

# Extract theory and test against data
theory = extract_theory(theoretical_documents)
theory_assessment = assess_theory_uncertainty(theory, empirical_data)
competing = evaluate_competing_theories([theory1, theory2, theory3], data)
```

---

## 🔍 Validation and Calibration

### Calibration Monitoring

```python
class CalibrationMonitor:
    """
    Track prediction vs actual to detect systematic bias
    """
    
    def track_prediction(self, prediction: Prediction):
        """Store prediction for later validation"""
        self.predictions.append({
            'id': prediction.id,
            'confidence': prediction.confidence,
            'timestamp': datetime.now(),
            'claim': prediction.claim
        })
    
    def validate_prediction(self, prediction_id: str, actual: bool):
        """Compare prediction to ground truth"""
        prediction = self.get_prediction(prediction_id)
        error = prediction.confidence - (1.0 if actual else 0.0)
        
        self.calibration_errors.append({
            'predicted': prediction.confidence,
            'actual': actual,
            'error': error,
            'timestamp': datetime.now()
        })
    
    def calculate_calibration_metrics(self) -> Dict:
        """Compute calibration statistics"""
        if not self.calibration_errors:
            return {'status': 'insufficient_data'}
        
        errors = [e['error'] for e in self.calibration_errors]
        
        return {
            'mean_calibration_error': np.mean(errors),
            'systematic_bias': 'overconfident' if np.mean(errors) > 0 else 'underconfident',
            'calibration_rmse': np.sqrt(np.mean([e**2 for e in errors])),
            'sample_size': len(errors),
            'recommendation': self.generate_calibration_recommendation(errors)
        }
```

---

## 📋 Decision Support Matrix

### When to Use Which Configuration

| **Research Question Type** | **Source Diversity** | **Time Available** | **Recommended Config** | **Key Dimensions** |
|---------------------------|---------------------|-------------------|----------------------|-------------------|
| Exploratory | Unknown | Hours | Quick Analysis | Core only |
| Confirmatory | Academic | Days | Standard Research | Core + ICD-206 + CERQual |
| Mixed Methods | Diverse | Weeks | Multi-Source Synthesis | Full source assessment |
| Theory Testing | Academic | Weeks | Theory Testing | Theory + ACH |
| Investigation | All types | Flexible | Deep Investigation | All dimensions |
| Real-time | Social media | Minutes | Quick + Temporal | Core + decay |

---

## 🚀 Future Enhancements

### Planned Improvements
1. **Active Learning**: Use calibration data to improve confidence estimates
2. **Uncertainty-Aware Search**: Prioritize evidence that reduces uncertainty
3. **Adaptive Configuration**: Automatically adjust based on data characteristics
4. **Uncertainty Budgets**: Allocate acceptable uncertainty across pipeline
5. **Confidence-Guided Decisions**: Automatic method selection based on confidence

### Research Directions
1. **Causal Uncertainty**: Propagation through causal inference
2. **Temporal Dynamics**: Time-varying confidence models
3. **Multi-Modal Fusion**: Optimal combination of different data types
4. **Adversarial Robustness**: Confidence under adversarial inputs
5. **Explanation Generation**: Natural language uncertainty explanations

---

## 📚 References

### Intelligence Community Standards
- ICD-203: Analytic Standards
- ICD-206: Sourcing Requirements
- Heuer, R. J. (1999). Psychology of Intelligence Analysis

### Academic Frameworks
- CERQual: Confidence in Evidence from Reviews of Qualitative research
- GRADE: Grading of Recommendations Assessment, Development and Evaluation

### Mathematical Foundations
- Propagation of Uncertainty (ISO/IEC Guide 98-3)
- Bayesian Methods for Statistical Analysis
- Information Theory and Statistical Mechanics

---

## 📝 Document Metadata

**Version Control**
- Version 1.0: Initial comprehensive specification
- Last Updated: 2025-08-06
- Next Review: After Phase 1 implementation

**Approval Status**
- Technical Review: Pending
- Stakeholder Review: Pending
- Implementation Ready: Pending

**Related Documents**
- ADR-029: IC-Informed Uncertainty Framework
- Comprehensive7: Mathematical Framework Details
- Theory Extraction Integration Plan

---

This document serves as the authoritative specification for KGAS's uncertainty and confidence framework, providing comprehensive coverage while maintaining practical implementability and human interpretability as the primary goal.