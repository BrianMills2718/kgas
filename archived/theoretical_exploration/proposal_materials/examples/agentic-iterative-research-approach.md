# Agentic Iterative Research Approach for KGAS
*Extracted from proposal materials - 2025-08-29*  
*Status: Advanced Research Method - Future Phase 3+*

## Overview

This document presents an innovative StructGPT-inspired approach for KGAS where LLM agents iteratively explore data through theory-driven interfaces rather than following fixed analytical pipelines. This represents a paradigm shift from predetermined analysis sequences to adaptive, reasoning-guided research.

**Key Innovation**: Theory schemas generate executable interfaces that LLM agents use to iteratively explore data, following evidence-driven paths rather than rigid workflows.

## Conceptual Framework

### Traditional Fixed Pipeline Approach
```
Theory → Extract → Graph → Table → Vector → Synthesis
(Linear, predetermined sequence)
```

### Agentic Iterative Approach  
```
Theory → Generate Interfaces → LOOP[Reason → Invoke → Analyze → Update] → Answer
(Dynamic, LLM-driven sequence)
```

## Architecture Components

### 1. Interface Generation from Theory

**Theory Interfaces**: Generated from Self-Categorization Theory schema
```python
interfaces = {
    "get_group_identities": "Extract_SCT_Groups(text) → groups",
    "calculate_meta_contrast": "Compute_MCR(users, groups) → prototypes", 
    "track_depersonalization": "Monitor_I_We_Shifts(tweets, time) → shifts",
    "measure_prototype_influence": "Calculate_Influence(prototype, group) → metrics",
    "test_salience_triggers": "Detect_Threat_Events(timeline) → events"
}
```

**Data Interfaces**: Generated from schema discovery
```python
data_interfaces = {
    "get_user_tweets": "Retrieve_Tweets(user_id, date_range) → tweets",
    "get_psychology_scores": "Get_Psych_Profile(user_id) → scores",
    "get_network_connections": "Get_Network(user_id, depth) → connections", 
    "get_source_credibility": "Check_Source_Quality(url) → credibility"
}
```

### 2. Agent Architecture

**LLM Agent Components**:
- **Persistent Memory**: Maintains knowledge state across iterations
- **Reasoning Engine**: Decides what to explore next based on current findings
- **Interface Invoker**: Executes theory and data interfaces
- **Evidence Tracker**: Accumulates findings for final synthesis

## Worked Example: Vaccine Hesitancy Analysis

**Research Question**: "Why do vaccine hesitant groups reject mainstream health information?"  
**Theory**: Self-Categorization Theory (Turner & Oakes, 1986)  
**Dataset**: 7.7M tweets from 2,506 users with psychological profiles

### Iteration 1: Initial Group Discovery

**[REASONING]**  
Agent: "To understand vaccine hesitancy through SCT, I first need to identify the social groups in the discourse. Let me search for group identities."

**[INTERFACE INVOCATION]**  
`→ invoke: get_group_identities(sample_tweets[0:10000])`

**[EXECUTION & RESULT]**  
T23C_ONTOLOGY_AWARE_EXTRACTOR processes sample  
Found 4 potential group identities with markers:
- "we don't trust" (vaccine hesitant)
- "they're trying to control us" (anti-vaxxers)  
- "follow the science" (pro-vaccine)
- "CDC recommends" (mainstream)

**[AGENT UPDATE]**  
Knowledge State += {groups_identified: 4, need_full_analysis: true}

### Iteration 2: Full Group Analysis

**[REASONING]**  
Agent: "I found 4 groups in the sample. Now I need to analyze the full dataset to understand their sizes and boundaries. Also need to resolve if 'vaccine hesitant' and 'anti-vaxxers' are the same group."

**[INTERFACE INVOCATION]**  
`→ invoke: get_group_identities(all_tweets)`  
`→ invoke: get_user_tweets(user_sample, "2020-01-01", "2020-12-31")`

**[EXECUTION & RESULT]**  
Processes 7.7M tweets (with intelligent sampling/batching)  
Entity resolution: "vaccine hesitant" ≈ "anti-vaxxers" → merged  

Final 3 distinct communities:
- Community A: 512 users (vaccine hesitant/anti-vax)
- Community B: 887 users (mainstream/pro-science)  
- Community C: 1107 users (undecided/questioning)

**[AGENT UPDATE]**  
Knowledge State += {final_groups: 3, sizes: [512, 887, 1107]}

### Iteration 3: Prototype Identification

**[REASONING]**  
Agent: "SCT says groups have prototypes with highest meta-contrast ratios. I need to calculate MCR for users in each community to find prototypes."

**[INTERFACE INVOCATION]**  
`→ invoke: get_psychology_scores(community_A_users)`  
`→ invoke: calculate_meta_contrast(community_A_users, all_groups)`

**[EXECUTION & RESULT]**  
T51_META_CONTRAST_CALCULATOR computes:  
MCR_i = Σ|features_i - features_outgroup| / Σ|features_i - features_ingroup|

Community A prototypes:
- user_047: MCR = 0.94 (highest)
- user_091: MCR = 0.89
- user_238: MCR = 0.87

**[AGENT UPDATE]**  
Knowledge State += {prototypes_identified: true, community_A_prototype: "user_047"}

### Iteration 4: Temporal Dynamics Analysis

**[REASONING]**  
Agent: "SCT predicts depersonalization (shift from 'I' to 'we'). Let me check if this happens over time, especially for high-identity users."

**[INTERFACE INVOCATION]**  
`→ invoke: track_depersonalization(community_A_users, "2020-01-01", "2020-12-31")`

**[EXECUTION & RESULT]**  
T52_TEMPORAL_ANALYZER tracks pronoun usage monthly  
Identifies shifts in language patterns

Found 237 I→We transitions:
- January: 12 transitions
- March (pandemic start): 48 transitions  
- November (vaccine announcement): 89 transitions  
**Pattern**: Threat events trigger depersonalization

**[AGENT UPDATE]**  
Knowledge State += {depersonalization_confirmed: true, threat_correlation: high, temporal_pattern: "accelerating"}

### Iteration 5: Prototype Influence Testing

**[REASONING]**  
Agent: "SCT says influence flows from prototypical members. Let me test if user_047 (highest MCR) influences Community A more than others."

**[INTERFACE INVOCATION]**  
`→ invoke: get_network_connections("user_047", depth=2)`  
`→ invoke: measure_prototype_influence("user_047", community_A)`

**[EXECUTION & RESULT]**  
T68_PAGERANK calculates influence scores  
Correlation analysis: MCR vs PageRank

user_047 influence metrics:
- PageRank: 0.023 (top 5% of network)
- Retweet rate: 3.2x average  
- Message adoption: 67% of group uses similar language within 48hrs  
**Correlation**: MCR ↔ Influence: r=0.72

**[AGENT UPDATE]**  
Knowledge State += {prototype_influence_confirmed: true, influence_mechanism: "language_adoption"}

### Iteration 6: Cross-Modal Synthesis

**[REASONING]**  
Agent: "I've confirmed several SCT predictions. Now let me synthesize across modalities to understand the full picture of information rejection."

**[INTERFACE INVOCATION]**  
`→ invoke: get_source_credibility(rejected_sources)`  
`→ invoke: correlate(depersonalization_events, rejection_events)`  
`→ invoke: analyze_language_patterns(high_identity_users)`

**[EXECUTION & RESULT]**  
CROSS_MODAL_ANALYZER integrates:
- Graph: Community structure
- Table: Psychology scores  
- Vector: Language embeddings
- Temporal: Process dynamics

Synthesis findings:
- Depersonalization → Rejection: 48hr lag, r=0.81
- High MCR users reject 3.2x more mainstream sources
- Language convergence within groups: 0.31→0.23 similarity  
- Threat events trigger cascade: threat→salience→depersonalization→rejection

**[AGENT UPDATE]**  
Knowledge State += {theory_validation: "supported", mechanism_identified: "cascade", policy_implications: computed}

### Final Answer Synthesis

**[CONVERGENCE REASONING]**  
Agent: "I have sufficient evidence to answer the research question with theoretical grounding."

**[COMPREHENSIVE ANSWER]**  
**Question**: "Why do vaccine hesitant groups reject mainstream health information?"

**Answer**: Through SCT lens, vaccine hesitant groups (n=512) reject mainstream health information through a depersonalization cascade:

1. **Threat Triggers**: Pandemic events and vaccine mandates increase group salience
2. **Identity Shift**: Users shift from individual to group identity (237 I→We transitions)  
3. **Prototype Influence**: Prototypical members (MCR>0.9) become primary influence sources
4. **Group Convergence**: Community adopts prototype's rejection stance (48hr lag)
5. **Systematic Rejection**: Mainstream sources coded as "outgroup" are rejected

**Mechanism**: Identity-protective cognition, not information deficit  
**Policy Implication**: Use in-group messengers, not external authorities

## Key Advantages Over Fixed Pipelines

### Adaptive Exploration
- **Responds to Findings**: Next iteration based on current evidence
- **Handles Missing Data**: Adapts when expected data unavailable
- **Follows Interesting Patterns**: Explores unexpected discoveries
- **Efficient Resource Use**: Skips irrelevant analyses

### Enhanced Explainability  
- **Clear Reasoning Chain**: Each iteration shows decision logic
- **Theory Connection**: Direct link between theoretical predictions and empirical tests
- **Evidence Trail**: Complete path from question to answer
- **Methodological Transparency**: All analytical decisions justified

### Research Quality
- **Theory-Driven**: Maintains theoretical coherence throughout
- **Evidence-Based**: Each step grounded in accumulated findings
- **Comprehensive**: Tests all relevant theoretical predictions  
- **Robust**: Handles partial data and ambiguous results

## Implementation Requirements

### 1. Agent Architecture
- **LLM with Memory**: Persistent knowledge state across iterations
- **Reasoning Engine**: Logic for deciding next analytical steps  
- **Interface System**: Theory and data interface invocation
- **Convergence Criteria**: When to stop and synthesize

### 2. Interface Generation
- **Theory→Interface Mapping**: Convert theory schemas to executable interfaces
- **Data→Interface Mapping**: Generate data access patterns from schemas
- **Interface→Tool Connection**: Link interfaces to actual KGAS tools

### 3. Orchestration System
- **Dynamic Tool Invocation**: Execute tools based on agent decisions
- **Result Integration**: Accumulate findings across iterations  
- **State Management**: Track knowledge evolution
- **Performance Monitoring**: Resource usage and convergence tracking

## Execution Comparison

| Aspect | Fixed Pipeline | Agentic Approach |
|--------|----------------|------------------|
| **Iterations** | 13 phases (predetermined) | 7 iterations (adaptive) |
| **Compute Efficiency** | 100% (all phases run) | ~60% (skipped irrelevant analyses) |  
| **Adaptability** | None (fixed sequence) | High (responds to findings) |
| **Explainability** | Implicit (phase flow) | Explicit (reasoned decisions) |
| **Theory Integration** | Loose (phases independent) | Tight (theory guides exploration) |
| **Discovery Potential** | Limited (predetermined path) | High (follows evidence) |

## Future Enhancements

### Advanced Reasoning
- **Multi-Theory Integration**: Handle competing theoretical frameworks
- **Uncertainty-Guided Exploration**: Focus efforts where uncertainty is highest  
- **Collaborative Agents**: Multiple agents exploring different theoretical angles
- **Meta-Learning**: Improve reasoning patterns from previous analyses

### Enhanced Interfaces
- **Richer Theory Interfaces**: Support procedural and logical algorithms
- **Dynamic Interface Generation**: Create new interfaces during exploration
- **Cross-Modal Interfaces**: Direct graph↔table↔vector operations
- **Simulation Interfaces**: Agent-based modeling and counterfactual analysis

---

**Status**: Advanced research methodology for Phase 3+ KGAS implementation. Represents paradigm shift from fixed analytical pipelines to adaptive, theory-guided exploration.

**Research Impact**: Demonstrates how computational social science can become truly iterative and theory-driven, mimicking human research processes while leveraging computational scale and rigor.