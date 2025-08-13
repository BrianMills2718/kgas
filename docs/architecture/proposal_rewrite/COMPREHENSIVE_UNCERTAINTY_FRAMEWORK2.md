# KGAS Uncertainty Framework
## 12-Dimension Matrix with IC Bands

**Version**: 2.0  
**Date**: 2025-08-06  
**Purpose**: Human-interpretable uncertainty tracking for KGAS  
**Mathematical Method**: Root-sum-squares propagation with quality gating  

---

## 📊 Uncertainty Measurement Matrix

| **Dimension** | **Origin** | **Measurement** | **Framework** | **Propagation** | **Human Question** | **Config** |
|--------------|------------|----------------|--------------|----------------|-------------------|------------|
| **SOURCE ANALYSIS** |
| Individual Source Credibility | Data ingestion | Author expertise, reliability history | IC-inspired (ICD-206) | Independent (RSS) | Can we trust this source? | Yes |
| Cross-Source Coherence | Multi-source synthesis | Agreement across sources | CERQual-inspired | Coherence weighting | Do sources agree? | Yes |
| Temporal Relevance | Data collection | Age-adjusted decay | Custom decay | Exponential decay | How current is this? | Yes |
| **COMPUTATIONAL** |
| Extraction Completeness | Document processing | Coverage ratio | Coverage Metrics | Independent (RSS) | How much captured? | No |
| Technical Entity Recognition | LLM extraction | LLM confidence scores | LLM Confidence | Independent (RSS) | Entities identified correctly? | No |
| **THEORETICAL** |
| Construct Validity | Theory mapping | Entity-to-construct mapping | Social Science Methodology | Independent (RSS) | Do entities map to constructs? | Yes |
| Theory-Data Fit | Theory application | Theory applicability assessment | Theory Application | Independent (RSS) | Does theory apply? | Yes |
| **METHODOLOGICAL** |
| Methodological Limitations | Source assessment | Study design, method quality | Research Methods | Quality gating | What method limitations? | Yes |
| Sampling Bias | Data collection | Representativeness assessment | Statistical Sampling | Bias correction | Is sample biased? | Yes |
| **EVIDENCE INTEGRATION** |
| Evidence Diagnosticity | Evidence evaluation | Discriminating power | IC Methods | Weight adjustment | Does evidence discriminate? | Yes |
| Evidence Sufficiency | Synthesis | Coverage of requirements | CERQual-inspired | Confidence ceiling | Enough evidence? | Yes |
| **FINAL** |
| Claim Strength | Synthesis | RSS aggregation | IC Probability Bands | RSS Aggregation | How confident in conclusion? | No |

---

## 🎯 IC Probability Bands

| **Range** | **IC Band** | **Usage** |
|-----------|-------------|-----------|
| 0.95-1.00 | almost certain | Peer-reviewed sources, confident LLM extraction |
| 0.80-0.95 | very likely | News outlets, confident mapping |
| 0.55-0.80 | likely | Expert blogs, moderate confidence |
| 0.45-0.55 | roughly even chance | Mixed evidence, unclear theory fit |
| 0.20-0.45 | unlikely | Poor sources, low LLM confidence |
| 0.05-0.20 | very unlikely | Unreliable sources, failed extraction |
| 0.00-0.05 | almost no chance | Spam sources, extraction failure |

---

## ⚙️ Configuration Profiles

| **Profile** | **Dimensions** | **Use Case** |
|------------|---------------|-------------|
| Quick | Extraction, Entity Recognition, Claim Strength | Rapid assessment |
| Standard | + Source Credibility, Construct Validity, Theory-Data Fit | Research analysis |
| Multi-Source | Standard + Cross-Source Coherence, Evidence Sufficiency | Literature synthesis |
| Research Quality | Multi-Source + Methodological Limitations, Sampling Bias | Publication quality |
| Evidence Assessment | Research Quality + Evidence Diagnosticity | Decision making |
| Comprehensive | All 12 dimensions | Dissertation level |

---

## 🔢 Mathematical Framework

### Root-Sum-Squares Propagation
```
Final_Uncertainty = √[(1-C₁)² + (1-C₂)² + ... + (1-Cₙ)²]
Final_Confidence = 1 - Final_Uncertainty
```

### Quality Gating
```
Gated_Confidence = min(
    RSS_Confidence,
    Methodological_Limitations,
    Evidence_Sufficiency
)
```

### Coherence Weighting
```
Adjusted_Source = Individual_Source × Coherence_Modifier

Coherence > 0.8: 1.1× boost
Coherence < 0.4: 0.8× penalty
```

### Temporal Decay
```
Temporal_Relevance = exp(-decay_rate × age_days)

Decay rates by topic:
- Breaking news: 1 day half-life
- Analysis: 30 days
- Academic: 365 days
```

---

## 📋 Assessment Guidelines

### Individual Source Credibility
- almost certain: Peer-reviewed, established author
- very likely: News outlet, verified author
- likely: Known publication, credentials
- roughly even chance: Mixed indicators
- unlikely: Poor quality, unverified
- very unlikely: Questionable, contradicted
- almost no chance: Spam, unreliable

### Cross-Source Coherence
- almost certain: Sources strongly agree
- very likely: Sources mostly agree
- likely: Sources generally agree
- roughly even chance: Sources split
- unlikely: Sources mostly disagree
- very unlikely: Strong disagreement
- almost no chance: Complete contradiction

### Temporal Relevance
- almost certain: Days/weeks old, current topic
- very likely: Months old, current relevance
- likely: 1-2 years, still relevant
- roughly even chance: 3-5 years, mixed relevance
- unlikely: 5+ years, questionable
- very unlikely: 10+ years, poor relevance
- almost no chance: Ancient, outdated

### Extraction Completeness
- almost certain: 95%+ processed
- very likely: 85-95% coverage
- likely: 70-85% coverage
- roughly even chance: 50-70% coverage
- unlikely: 30-50% coverage
- very unlikely: 10-30% coverage
- almost no chance: <10% coverage

### Technical Entity Recognition
- almost certain: LLM confident, clear boundaries
- very likely: LLM confident, minor ambiguities
- likely: LLM moderate confidence
- roughly even chance: LLM uncertain
- unlikely: LLM struggled
- very unlikely: LLM low confidence
- almost no chance: LLM failed

### Construct Validity
- almost certain: Perfect entity-construct mapping
- very likely: Mapping with minor stretches
- likely: Reasonable mapping
- roughly even chance: Questionable mapping
- unlikely: Poor mapping
- very unlikely: Bad mapping
- almost no chance: No valid mapping

### Theory-Data Fit
- almost certain: Theory perfectly applicable
- very likely: Theory fits, minor violations
- likely: Theory generally applicable
- roughly even chance: Applicability uncertain
- unlikely: Theory poorly fits
- very unlikely: Theory inappropriate
- almost no chance: Theory inapplicable

### Methodological Limitations
- almost certain: Gold standard methods
- very likely: Strong methods, minor limitations
- likely: Methods with known limitations
- roughly even chance: Mixed methods
- unlikely: Poor methods
- very unlikely: Methods with limitations
- almost no chance: Flawed methods

### Sampling Bias
- almost certain: Representative sampling
- very likely: Minimal bias concerns
- likely: Some bias possible
- roughly even chance: Bias likely
- unlikely: Bias present
- very unlikely: Bias present
- almost no chance: Biased/unrepresentative

### Evidence Diagnosticity
- almost certain: Strongly discriminates hypotheses
- very likely: Distinguishes alternatives
- likely: Provides discrimination
- roughly even chance: Somewhat helpful
- unlikely: Little discrimination
- very unlikely: Barely helpful
- almost no chance: No discrimination

### Evidence Sufficiency
- almost certain: More than enough evidence
- very likely: Sufficient evidence
- likely: Evidence adequate
- roughly even chance: Borderline sufficiency
- unlikely: Insufficient evidence
- very unlikely: Insufficient evidence
- almost no chance: No evidence

---

## 🏗️ Implementation

### Base Classes
```python
@dataclass
class UncertaintyMeasurement:
    dimension: str
    ic_band: str  # IC probability band
    confidence: float  # 0-1 for calculation
    framework: str
    metadata: Dict

@dataclass 
class UncertaintyProfile:
    measurements: Dict[str, UncertaintyMeasurement]
    configuration: str
    
    def get_claim_strength(self) -> str:
        # Apply RSS + quality gating + coherence weighting
        # Return IC band
```

### Propagation Engine
```python
def propagate_uncertainty(profile: UncertaintyProfile) -> float:
    # Extract confidences
    confidences = [m.confidence for m in profile.measurements.values()]
    
    # RSS calculation
    uncertainties = [(1 - c) for c in confidences]
    combined_uncertainty = math.sqrt(sum(u**2 for u in uncertainties))
    rss_confidence = 1 - combined_uncertainty
    
    # Quality gating
    quality_gates = [
        profile.measurements.get('methodological_limitations', {}).confidence,
        profile.measurements.get('evidence_sufficiency', {}).confidence
    ]
    gated_confidence = min([rss_confidence] + [g for g in quality_gates if g])
    
    # Coherence weighting (if multi-source)
    coherence = profile.measurements.get('cross_source_coherence')
    if coherence:
        if coherence.confidence > 0.8:
            gated_confidence *= 1.1
        elif coherence.confidence < 0.4:
            gated_confidence *= 0.8
    
    return min(1.0, gated_confidence)
```

### Human Interface
```python
def generate_narrative(profile: UncertaintyProfile) -> str:
    claim_strength = profile.get_claim_strength()
    
    narrative = f"Assessment confidence: {claim_strength}\n\n"
    
    # Identify issues
    low_dims = [d for d in profile.measurements.values() if d.confidence < 0.6]
    if low_dims:
        narrative += "Factors reducing confidence:\n"
        for dim in low_dims:
            narrative += f"• {dim.dimension}: {dim.ic_band}\n"
    
    return narrative
```

---

## 🎯 Usage Patterns

### Single Source Analysis
```python
config = "standard"
profile = assess_document(document, config)
narrative = generate_narrative(profile)
# Output: "Assessment confidence: likely"
```

### Multi-Source Synthesis  
```python
config = "multi_source"
profile = assess_documents(documents, config)
# Includes cross-source coherence
narrative = generate_narrative(profile)
```

### Research Publication
```python
config = "research_quality" 
profile = assess_research(documents, theory, config)
# Includes methodological assessment
narrative = generate_narrative(profile)
```

---

## 🔄 Key Assumptions

1. **Independence**: RSS assumes dimensions are independent (noted limitation)
2. **IC Bands**: Map 0-1 confidence to IC probability bands
3. **Quality Gating**: Poor methods/evidence limit confidence regardless of other factors
4. **Coherence Effect**: Source agreement/disagreement modifies confidence
5. **LLM Reliability**: LLM confidence scores are meaningful for entity recognition

---

## 📊 Dimension Summary

**Total**: 12 dimensions
**Always Enabled**: 5 (Extraction, Entity Recognition, Source Credibility, Theory elements, Claim Strength)
**Configurable**: 7 (Multi-source, methodological, evidence assessment)
**Mathematical**: RSS with quality gating and coherence weighting
**Output**: IC probability bands for human interpretation

---

# Appendix: Uncertainty Quantification Framework

Social science research synthesis using automated systems requires systematic uncertainty quantification to maintain research integrity. This work implements a multi-dimensional framework that tracks uncertainty across source assessment, computational processing, theoretical application, and evidence integration phases.

## Framework Structure

The uncertainty framework encompasses twelve dimensions organized across five categories:

**Source Analysis:** Individual source credibility assessment using ICD-206 standards, cross-source coherence evaluation, and temporal relevance decay functions.

**Computational Processing:** Document extraction completeness measurement and LLM entity recognition confidence tracking.

**Theoretical Application:** Construct validity assessment for entity-theory mapping and theory-data fit evaluation.

**Methodological Assessment:** Source methodology limitation evaluation and sampling bias detection.

**Evidence Integration:** Evidence diagnosticity measurement and sufficiency assessment for research claims.

**Final Assessment:** Claim strength determination through mathematical uncertainty propagation.

## Uncertainty Measurement Matrix

| Dimension | Origin Point | Measurement Method | Framework | Human Interpretation |
|-----------|--------------|-------------------|-----------|-------------------|
| Individual Source Credibility | Data ingestion | Author expertise, reliability history | ICD-206 | Can we trust this source? |
| Cross-Source Coherence | Multi-source synthesis | Agreement across sources | CERQual | Do sources agree? |
| Temporal Relevance | Data collection | Age-adjusted decay function | Custom | How current is this? |
| Extraction Completeness | Document processing | Coverage ratio | Statistical | How much captured? |
| Technical Entity Recognition | LLM extraction | LLM confidence scores | LLM-based | Entities identified correctly? |
| Construct Validity | Theory mapping | Entity-to-construct mapping | Social Science | Do entities map to constructs? |
| Theory-Data Fit | Theory application | Theory applicability assessment | Academic | Does theory apply? |
| Methodological Limitations | Source assessment | Study design, method quality | Research Methods | What method limitations? |
| Sampling Bias | Data collection | Representativeness assessment | Statistical | Is sample biased? |
| Evidence Diagnosticity | Evidence evaluation | Discriminating power assessment | IC Methods | Does evidence discriminate? |
| Evidence Sufficiency | Synthesis | Coverage of claim requirements | CERQual | Enough evidence? |
| Claim Strength | Final synthesis | RSS aggregation | IC Bands | How confident in conclusion? |

## Mathematical Propagation

Uncertainty propagation uses root-sum-squares for independent uncertainties:

*Final_Uncertainty = √[(1-C₁)² + (1-C₂)² + ... + (1-Cₙ)²]*

Quality gating mechanisms ensure methodological limitations and evidence sufficiency constrain final confidence. Cross-source coherence applies multiplicative weighting to source-related measurements.

## Output Expression

All confidence measurements map to Intelligence Community probability bands (almost certain, very likely, likely, roughly even chance, unlikely, very unlikely, almost no chance) to avoid false precision while maintaining human interpretability.

## Configuration Examples

**Standard Research:** Source credibility, construct validity, theory-data fit, extraction completeness, entity recognition, claim strength.

**Multi-Source Synthesis:** Standard configuration plus cross-source coherence and evidence sufficiency evaluation.

**Publication Quality:** Multi-source configuration plus methodological limitations assessment and sampling bias detection.

---

## 📖 Human-Readable Summary

### Core Question
The table addresses: "How confident should I be in this analysis?"

### 12 Dimensions Explained
**SOURCE ANALYSIS** (3 dimensions)  
- Individual Source Credibility: Trust level of each source
- Cross-Source Coherence: Agreement between sources  
- Temporal Relevance: How current the information is

**COMPUTATIONAL** (2 dimensions)
- Extraction Completeness: How much data captured
- Technical Entity Recognition: Accuracy of entity identification

**THEORETICAL** (2 dimensions)
- Construct Validity: Do entities match theoretical concepts
- Theory-Data Fit: Does theory apply to this data

**METHODOLOGICAL** (2 dimensions)  
- Methodological Limitations: Quality of research methods
- Sampling Bias: Representativeness of sample

**EVIDENCE INTEGRATION** (2 dimensions)
- Evidence Diagnosticity: Does evidence help choose between options
- Evidence Sufficiency: Enough evidence for claims

**FINAL** (1 dimension)
- Claim Strength: Overall confidence in conclusion

### Configuration Profiles
Users select profile based on analysis needs:
- **Quick**: 3 dimensions for rapid assessment
- **Standard**: 6 dimensions for research
- **Multi-Source**: 8 dimensions for literature synthesis  
- **Research Quality**: 10 dimensions for publication
- **Evidence Assessment**: 11 dimensions for decisions
- **Comprehensive**: 12 dimensions for dissertation work

### IC Probability Bands
System outputs confidence using Intelligence Community standards:
- almost certain (95-100%)
- very likely (80-95%)
- likely (55-80%)
- roughly even chance (45-55%)
- unlikely (20-45%)
- very unlikely (5-20%)
- almost no chance (0-5%)

### Mathematical Approach
1. Each dimension assessed individually using IC bands
2. Dimensions combined using root-sum-squares
3. Quality gates limit confidence based on methods/evidence
4. Source coherence modifies confidence up/down
5. Final result expressed as IC probability band

### Usage
1. Select configuration profile
2. System assesses each enabled dimension
3. Dimensions combined mathematically
4. Output: "Assessment confidence: [IC band]"
5. Explanation provided for confidence level

### Key Benefits
- No false precision (no "87.3% confidence")
- Human-interpretable output
- Configurable complexity
- Mathematically sound propagation
- Based on proven Intelligence Community methods