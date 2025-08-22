# IC-Informed Uncertainty Analysis Components

## Integrated LLM Analysis Components

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Single Integrated LLM Analysis Call                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Input Package:                                                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐          │
│  │Research Question│  │ Evidence Sources │  │ Analysis Context    │          │
│  │ & Objectives    │  │ (Multi-format)   │  │ (Domain, History)   │          │
│  └────────┬────────┘  └────────┬─────────┘  └──────────┬──────────┘          │
│           │                    │                        │                      │
│           └────────────────────┴────────────────────────┘                      │
│                                │                                                │
│                                ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    IC Methodology Components                             │  │
│  ├─────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                          │  │
│  │  1. KEY ASSUMPTIONS CHECK                                              │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Identify all analytical assumptions                        │     │  │
│  │  │ • Rate criticality: low / moderate / high                   │     │  │
│  │  │ • Flag assumptions most affecting conclusions                │     │  │
│  │  │ • Consider "What must be true for this to hold?"            │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  │  2. ALTERNATIVE HYPOTHESES (ACH)                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Generate competing explanations                            │     │  │
│  │  │ • Evaluate evidence diagnosticity                            │     │  │
│  │  │ • Identify confirming vs. disconfirming evidence            │     │  │
│  │  │ • Rate hypotheses: most likely → least likely               │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  │  3. DIAGNOSTIC EVIDENCE EVALUATION                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Apply ICD-206 source quality criteria                     │     │  │
│  │  │ • Assess evidence value (diagnostic vs. consistent)         │     │  │
│  │  │ • Weight by reliability & credibility                       │     │  │
│  │  │ • Flag circular reporting or echo chambers                  │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  │  4. INFORMATION GAPS ASSESSMENT                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Identify missing critical information                     │     │  │
│  │  │ • Assess impact of gaps on conclusions                      │     │  │
│  │  │ • Prioritize collection needs                               │     │  │
│  │  │ • Note "known unknowns" vs "unknown unknowns"              │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  │  5. DECEPTION & MANIPULATION CHECK                                     │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Assess source motivations                                 │     │  │
│  │  │ • Check for deliberate ambiguity                           │     │  │
│  │  │ • Identify potential denial & deception                    │     │  │
│  │  │ • Rate manipulation risk: low / moderate / high            │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  │  6. CONFIDENCE CALIBRATION                                             │  │
│  │  ┌──────────────────────────────────────────────────────────────┐     │  │
│  │  │ • Heuer's Information Paradox check                         │     │  │
│  │  │ • Assess confidence in assessment (not outcome)            │     │  │
│  │  │ • Consider cognitive bias impact                            │     │  │
│  │  │ • Rate: low / moderate / high confidence                   │     │  │
│  │  └──────────────────────────────────────────────────────────────┘     │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  Output Structure:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │{                                                                         │  │
│  │  "assumptions": [...],           // Critical assumptions list           │  │
│  │  "hypotheses": {...},            // Ranked alternative explanations     │  │
│  │  "evidence_quality": {...},      // ICD-206 assessments                 │  │
│  │  "information_gaps": [...],      // Missing critical data               │  │
│  │  "deception_risk": "low",        // Manipulation assessment             │  │
│  │  "ic_probability": "likely",     // ICD-203 band                        │  │
│  │  "confidence_level": "moderate", // Assessment confidence               │  │
│  │  "stage_uncertainties": {...}    // For propagation                     │  │
│  │}                                                                         │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## ICD-203 Probability Standards

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ICD-203 Probability Bands                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Term                    Probability Range    Numeric Center   Usage            │
│  ─────────────────────────────────────────────────────────────────────         │
│  almost no chance        1-5%                 3%              Remote           │
│  very unlikely           5-20%                ~10%            Improbable       │
│  unlikely                20-45%               ~30%            Probably not     │
│  roughly even chance     45-55%               50%             Coin flip        │
│  likely                  55-80%               ~70%            Probable         │
│  very likely             80-95%               ~90%            Highly probable  │
│  almost certain          95-99%               97%             Near certainty   │
│                                                                                 │
│  Note: These are ranges, not point estimates. LLMs assign the band,            │
│        not specific percentages within the band.                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## ICD-206 Source Quality Framework

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ICD-206 Source Evaluation                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  RELIABILITY (History of source)           CREDIBILITY (Current content)       │
│  ┌─────────────────────────────┐          ┌─────────────────────────────┐     │
│  │ A - Completely reliable     │          │ 1 - Confirmed by other      │     │
│  │ B - Usually reliable        │          │ 2 - Probably true            │     │
│  │ C - Fairly reliable         │          │ 3 - Possibly true            │     │
│  │ D - Not usually reliable    │          │ 4 - Doubtful                 │     │
│  │ E - Unreliable              │          │ 5 - Improbable               │     │
│  │ F - Cannot be judged        │          │ 6 - Cannot be judged         │     │
│  └─────────────────────────────┘          └─────────────────────────────┘     │
│                                                                                 │
│  Additional Quality Dimensions:                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ • Relevance: How directly applicable to the research question           │  │
│  │ • Timeliness: How current/recent the information is                     │  │
│  │ • Technical Quality: Methodology, sample size, rigor                    │  │
│  │ • Corroboration: Independent confirmation from other sources            │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```