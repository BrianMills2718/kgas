# IC-Informed Uncertainty Framework - Overview Diagram

## High-Level Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      IC-Informed Uncertainty Framework (ADR-029)                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────┐     ┌────────────────────┐     ┌───────────────────────┐│
│  │ Research Question│     │  Source Evidence   │     │    IC Standards       ││
│  │  & Context       │     │  (Multi-Modal)     │     │  (ICD-203/206)        ││
│  └────────┬─────────┘     └─────────┬──────────┘     └───────────┬───────────┘│
│           │                         │                             │             │
│           └─────────────┬───────────┴─────────────────────────────┘             │
│                         │                                                       │
│                         ▼                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │              Single Integrated LLM Analysis Call                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  1. Key Assumptions Check (criticality rating)                  │   │  │
│  │  │  2. Alternative Hypotheses (ACH methodology)                    │   │  │
│  │  │  3. Diagnostic Evidence Evaluation (ICD-206)                    │   │  │
│  │  │  4. Information Gaps Assessment                                 │   │  │
│  │  │  5. Deception/Manipulation Detection                            │   │  │
│  │  │  6. IC Probability Band Assignment (ICD-203)                    │   │  │
│  │  │  7. Confidence Level Assessment (not probability)               │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────┬──────────────────────────────────────┘  │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │              Mathematical Uncertainty Propagation                        │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  • Root-Sum-Squares (RSS) for Independent Uncertainties         │   │  │
│  │  │    σ_total = √(σ₁² + σ₂² + ... + σₙ²)                         │   │  │
│  │  │                                                                  │   │  │
│  │  │  • Covariance Matrix for Known Dependencies                     │   │  │
│  │  │    When correlations exist between stages                       │   │  │
│  │  │                                                                  │   │  │
│  │  │  • Hard-coded mathematical operations (not LLM)                 │   │  │
│  │  │    Deterministic, transparent, consistent                       │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────┬──────────────────────────────────────┘  │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    Final Uncertainty Assessment                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │  │
│  │  │  • IC Probability Band: [almost_no_chance ... almost_certain]   │   │  │
│  │  │  • Confidence Level: [low / moderate / high]                    │   │  │
│  │  │  • Key Assumptions & Risks                                      │   │  │
│  │  │  • Information Gaps                                             │   │  │
│  │  │  • Alternative Hypotheses                                       │   │  │
│  │  └─────────────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Differences from Superseded Bayesian Approach

| Aspect | Old (Bayesian Network) | New (IC-Informed) |
|--------|------------------------|-------------------|
| **Structure** | Stage-based network with dependencies | Integrated analysis with propagation |
| **LLM Usage** | Multiple calls for parameters | Single comprehensive analysis |
| **Math Model** | Bayesian belief updating | Root-sum-squares propagation |
| **Standards** | Statistical theory | IC proven methodologies |
| **Output** | Posterior probabilities | IC bands + confidence levels |

## Core Components

### 1. IC Standards Integration
- **ICD-203**: Standardized probability expressions (7 bands from 1-99%)
- **ICD-206**: Source quality assessment framework
- **Heuer's Principles**: Information paradox awareness

### 2. Single LLM Analysis
- Comprehensive IC methodology application in one call
- Structured assessment covering all uncertainty dimensions
- No fragmented probability estimations

### 3. Mathematical Propagation
- Hard-coded RSS for independent uncertainties
- Covariance matrix for dependencies
- Transparent, deterministic calculations

### 4. Practical Output
- IC-standard probability bands (not precise percentages)
- Confidence in assessment (not outcome)
- Actionable uncertainty communication