# Comprehensive Context: Uncertainty Framework for Knowledge Graph Analysis System (KGAS)

## Executive Summary

We are designing a comprehensive uncertainty tracking and propagation framework for KGAS (Knowledge Graph Analysis System), a research-oriented system that extracts knowledge from documents, builds knowledge graphs, and performs theory-guided analysis. The core challenge is that every step in this pipeline introduces different types of uncertainty, and we need to track, propagate, and report these uncertainties in ways that are meaningful to different audiences (researchers, policy makers, methodologists).

## 1. Project Context: What is KGAS?

### System Overview
KGAS is an academic research system that:
1. **Ingests documents** (PDFs, academic papers, social media data)
2. **Extracts structured knowledge** using Natural Language Processing (NLP)
3. **Builds knowledge graphs** representing entities and their relationships
4. **Applies theoretical frameworks** (e.g., Social Identity Theory) to analyze the data
5. **Performs cross-modal analysis** switching between graph, table, and vector representations
6. **Answers research questions** with traceable, reproducible results

### Example Use Case: Vaccine Hesitancy Analysis
Imagine a researcher wants to understand vaccine hesitancy patterns on social media:
1. System ingests 7.7 million tweets about vaccines   
2. Extracts entities (people, organizations, claims, sentiments)
3. Builds a network graph of who influences whom
4. Applies Social Identity Theory to identify in-groups and out-groups
5. Analyzes how misinformation spreads between communities
6. Produces findings like "High-identity groups are 2.3x more likely to reject mainstream vaccine information"

### The Critical Problem: Uncertainty Everywhere
Every step introduces uncertainty:
- Did we correctly extract entities from messy social media text?
- Are the people we identified as "same person" actually the same?
- Do network communities actually represent social identity groups?
- When someone tweets "vaccines are totally safe 🙄", are they being sarcastic?
- Is our sample of 7.7M tweets representative of broader population beliefs?

## 2. Why Uncertainty Matters

### Different Stakeholders, Different Needs

**Policy Makers** need to know: "How confident should we be in the finding that high-identity groups reject vaccine information?"
- They care about the **bottom-line confidence** in actionable findings

**Researchers** need to know: "Did we implement Social Identity Theory correctly?"
- They care about **theoretical fidelity** and **methodological rigor**

**Replication Scientists** need to know: "Did we do exactly what the original paper said?"
- They care about **paper fidelity** and **reproducibility**

**Engineers** need to know: "Did our code run correctly without bugs?"
- They care about **implementation quality** and **technical correctness**

### The Core Challenge
We can't just report a single "confidence = 75%" because that collapses multiple distinct types of uncertainty that matter for different purposes. We need a multi-dimensional framework that tracks uncertainties separately and combines them appropriately for each audience.

## 3. The 14 Core Dimensions of Uncertainty

Through analysis of the KGAS pipeline, we've identified 14 distinct dimensions where uncertainty enters the system:

### Dimension 1: Source Credibility
**What it is**: How reliable is the source of information?
**Example**: Is this tweet from a verified medical professional or a bot account?
**Challenge**: "Reliable" means different things for different purposes (factual accuracy vs. genuine belief expression)

### Dimension 2: Cross-Source Coherence
**What it is**: Do multiple sources agree or conflict?
**Example**: If 100 tweets say "vaccines cause autism" and 10,000 say they don't, how do we weight this?
**Challenge**: Volume doesn't equal truth; minority views might be correct

### Dimension 3: Temporal Relevance
**What it is**: How does information value decay over time?
**Example**: A tweet about vaccine safety from 2019 (pre-COVID) vs 2023 (post-COVID)
**Challenge**: Different types of information decay at different rates

### Dimension 4: Extraction Completeness
**What it is**: How much relevant information did we successfully extract?
**Example**: Did our PDF parser capture all the text, or did it miss footnotes, figures, tables?
**Challenge**: We don't know what we don't know (unknown unknowns)

### Dimension 5: Entity Recognition Confidence
**What it is**: How well did we identify entities in text?
**Example**: Is "Johnson & Johnson" a company, two people, or a legal case?
**Challenge**: Context-dependent meanings, ambiguous references

### Dimension 6: Construct Validity
**What it is**: Does our measurement actually capture what we think it captures?
**Example**: Do Twitter "communities" (network clusters) actually represent "identity groups" (psychological concept)?
**Challenge**: Gap between what we can measure and what theory discusses

### Dimension 7: Theory-Data Fit
**What it is**: How well does the selected theory explain the observed data?
**Example**: Does Social Identity Theory explain vaccine hesitancy better than Cognitive Dissonance Theory?
**Challenge**: Multiple theories might partially explain the same phenomenon

### Dimension 8: Study Limitations
**What it is**: Known constraints and biases in the research design
**Example**: Twitter users aren't representative of general population
**Challenge**: Some limitations we know, others we don't

### Dimension 9: Sampling Bias
**What it is**: How representative is our sample?
**Example**: We only see public tweets, not private conversations
**Challenge**: Selection bias, survival bias, platform bias

### Dimension 10: Diagnosticity
**What it is**: How well does evidence discriminate between hypotheses?
**Example**: "People in tight-knit communities share similar beliefs" - supports many theories
**Challenge**: Evidence might support multiple competing explanations

### Dimension 11: Sufficiency
**What it is**: Do we have enough evidence to draw conclusions?
**Example**: 100 tweets might be insufficient to characterize a community of 10,000
**Challenge**: Statistical power, rare event detection

### Dimension 12: Confidence Calibration
**What it is**: Are our confidence estimates accurate?
**Example**: When we say "80% confident", are we right 80% of the time?
**Challenge**: Overconfidence bias, need for calibration data

### Dimension 13: Entity Identity Resolution
**What it is**: Are different mentions actually the same entity?
**Example**: Are @johnsmith123 and @jsmith_official the same person?
**Challenge**: People have multiple accounts, names change, ambiguous references

### Dimension 14: Reasoning Chain Validity
**What it is**: Is our logical chain of inference sound?
**Example**: "High identity → reject out-group info → vaccine hesitancy" - are all links valid?
**Challenge**: Long inference chains accumulate uncertainty

## 4. Intelligence Community (IC) Methods Explained

The IC has developed sophisticated methods for handling uncertainty in intelligence analysis. We're adapting these for academic research:

### Analysis of Competing Hypotheses (ACH)
**What it is**: A systematic method for evaluating multiple explanations against evidence
**How it works**:
1. List all reasonable hypotheses (e.g., "Vaccine hesitancy is due to: identity, misinformation, or distrust")
2. List all relevant evidence
3. Create a matrix: which evidence supports/contradicts which hypothesis
4. Identify which hypothesis has least evidence against it (not most evidence for it)

**Why it matters**: Helps avoid confirmation bias by forcing consideration of alternatives

### Key Assumptions Check
**What it is**: Explicitly identifying and testing assumptions underlying analysis
**Example assumptions**:
- "Twitter users express genuine beliefs" (might be false due to trolling)
- "Network connections indicate influence" (might just be entertainment following)
**How it works**: List assumptions, rate their validity, test them when possible

### Quality of Information Check (ICD-206 Standard)
**What it is**: Systematic assessment of source reliability and information credibility

**Source Reliability Scale**:
- A: Completely reliable (peer-reviewed journal)
- B: Usually reliable (established news outlet)
- C: Fairly reliable (verified social media account)
- D: Not usually reliable (anonymous account)
- E: Unreliable (known disinformation source)
- F: Cannot be judged (insufficient history)

**Information Credibility Scale**:
- 1: Confirmed by independent sources
- 2: Probably true (consistent with known facts)
- 3: Possibly true (reasonably logical)
- 4: Doubtful (possible but not logical)
- 5: Improbable (highly unlikely)
- 6: Cannot be judged

### What-If Analysis
**What it is**: Testing how conclusions change with different assumptions
**Example**: "What if community detection resolution parameter is 0.5 vs 2.0?"
**Purpose**: Identifies which uncertainties actually matter for conclusions

### Devil's Advocacy
**What it is**: Deliberately arguing against the preferred conclusion
**Example**: "We think identity drives vaccine hesitancy, but what's the strongest case against this?"
**Purpose**: Reveals weak points in reasoning, reduces overconfidence

## 5. Types of Uncertainty We Must Handle

### Epistemic vs Aleatory Uncertainty
**Epistemic** (Knowledge Uncertainty):
- Reducible through more research
- Example: "We don't know the best community detection algorithm" - could test and find out
- Action: Invest in research to reduce

**Aleatory** (Random Uncertainty):
- Irreducible natural variation
- Example: "Humans naturally vary in their beliefs" - inherent randomness
- Action: Accept and account for in analysis

### Why This Distinction Matters
If uncertainty is epistemic, we can reduce it by:
- Collecting more data
- Using better models
- Optimizing parameters

If uncertainty is aleatory, we must:
- Accept it as a fundamental limit
- Report ranges rather than points
- Use robust methods

## 6. The Tool Pipeline and Uncertainty Propagation

### The KGAS Tool Chain
```
T01_PDF_LOADER → T15A_TEXT_CHUNKER → T23A_SPACY_NER
                                             ↓
  T68_PAGERANK ← T34_EDGE_BUILDER ← T31_ENTITY_BUILDER
```

### How Uncertainty Propagates

#### Sequential Propagation
When tools run in sequence, uncertainties multiply (compound):
- PDF Loader: 98% accurate (2% OCR errors)
- Text Chunker: 95% preserves meaning (5% context loss)
- NER: 75% entity recognition (25% missed/wrong entities)
- Combined: 0.98 × 0.95 × 0.75 = 70% confidence

#### Parallel Propagation
When independent analyses combine, uncertainties can partially cancel:
- Twitter analysis: 70% confidence
- Survey data: 85% confidence
- Combined (independent): Better than worst, not as good as best

#### Correlated Propagation
When analyses share data/methods, uncertainties are correlated:
- Two analyses of same communities
- Can't reduce uncertainty below shared component
- Need to account for correlation in combination

## 7. Multi-Level Fidelity Framework

We track four distinct types of fidelity:

### 1. Paper Fidelity
**Question**: Did we do exactly what the research paper specified?
**Example**: Paper says "use Louvain with resolution 1.0", we used Louvain with resolution 1.0
**Score**: 100% (perfect match)
**Audience**: Replication researchers

### 2. Theory Fidelity
**Question**: Does what the paper says actually achieve what the theory intends?
**Example**: Theory says "identify cohesive groups", paper uses Louvain - does Louvain find cohesive groups?
**Score**: 85% (pretty good but not perfect)
**Audience**: Theorists

### 3. Construct Validity
**Question**: Does our measurement capture the theoretical construct?
**Example**: Do "network communities" actually represent "social identity groups"?
**Score**: 70% (moderate correspondence)
**Audience**: Methodologists

### 4. Implementation Quality
**Question**: Did our code execute correctly without bugs?
**Example**: Algorithm ran successfully, no crashes, correct output format
**Score**: 100% (no bugs)
**Audience**: Engineers

## 8. The Statement/Belief Problem

A critical challenge in social media analysis: **statements ≠ beliefs**

### Why Statements Don't Equal Beliefs
1. **Sarcasm**: "Vaccines are totally safe 🙄" (might mean opposite)
2. **Strategic messaging**: Politicians saying what polls well
3. **Social signaling**: Expressing group membership, not personal belief
4. **Trolling**: Deliberately provocative false statements
5. **Social desirability**: Saying what's acceptable, not what's believed

### How We Handle This
- Track multiple interpretations with probabilities
- Use context clues (emojis, history, consistency)
- Apply IC's ACH method at extraction time
- Flag high-ambiguity statements for human review
- Never assume statement = belief without evidence

## 9. Goals of Our Uncertainty Framework

### Primary Goals

1. **Track Multiple Uncertainty Dimensions Separately**
   - Don't collapse into single number
   - Maintain granularity for different uses
   - Enable detailed troubleshooting

2. **Enable Appropriate Combination for Different Audiences**
   - Policy makers: Combined bottom-line confidence
   - Researchers: Theory and method fidelity
   - Engineers: Implementation quality
   - Reviewers: Full uncertainty breakdown

3. **Support Uncertainty Propagation Through Complex Workflows**
   - Handle sequential, parallel, and correlated propagation
   - Account for error accumulation
   - Identify uncertainty bottlenecks

4. **Integrate IC Methods Throughout Execution**
   - Not just at beginning/end
   - Each tool can perform local ACH
   - Continuous assumption checking

5. **Maintain Full Provenance and Traceability**
   - Every uncertainty estimate is justified
   - Can trace back to sources
   - Reproducible uncertainty calculations

### Secondary Goals

6. **Guide Improvement Efforts**
   - Identify largest uncertainty contributors
   - Distinguish reducible from irreducible
   - Prioritize research investments

7. **Support Decision Making Under Uncertainty**
   - Provide ranges, not false precision
   - Identify when more data won't help
   - Flag when uncertainty too high for conclusions

8. **Enable Sensitivity Analysis**
   - Which uncertainties matter for conclusions?
   - How robust are findings?
   - What would change the results?

## 10. Implementation Approach

### Phase 1: Enhanced Provenance Service
- Extend existing SQLite provenance system
- Add multi-dimensional uncertainty tracking
- Store in JSON metadata field (no schema changes)

### Phase 2: Tool-Level IC Integration
- Add ACH capability to each tool
- Implement assumption checking
- Calculate tool-specific uncertainties

### Phase 3: Propagation Framework
- Implement sequential propagation (multiplication)
- Implement parallel propagation (independent combination)
- Implement correlated propagation (accounting for shared uncertainty)

### Phase 4: Reporting and Visualization
- Different views for different audiences
- Uncertainty budgets showing contributions
- Sensitivity analysis dashboards

## 11. Key Innovations

1. **Multi-dimensional uncertainty** instead of single confidence scores
2. **IC methods integrated throughout** pipeline, not just at endpoints
3. **Epistemic/aleatory distinction** to guide improvement efforts
4. **Social bias adjustments** for statement/belief disambiguation
5. **Uncertainty budgets** to prioritize improvements
6. **Interval representations** instead of false precision
7. **Monte Carlo propagation** for complex non-linear relationships

## 12. Success Criteria

The framework succeeds when:
1. Researchers can trust confidence estimates
2. Different stakeholders get appropriate uncertainty information
3. We can identify and prioritize improvements
4. Findings are robust to reasonable uncertainty variations
5. All uncertainty claims are traceable and justified
6. The system guides users away from overconfident conclusions

## 13. Challenges and Open Questions

1. **Validation**: How do we know our uncertainty estimates are accurate?
2. **Complexity**: How do we keep this tractable and usable?
3. **Communication**: How do we explain uncertainty to non-technical users?
4. **Unknown unknowns**: How do we handle uncertainties we haven't anticipated?
5. **Cultural factors**: How do uncertainties vary across cultures/contexts?

## Conclusion

We're building a comprehensive uncertainty framework for KGAS that goes far beyond simple confidence scores. By tracking multiple dimensions of uncertainty, integrating IC analytical methods, and providing appropriate views for different audiences, we aim to produce research findings that are both rigorous and honest about their limitations. This framework will help researchers understand not just what we know, but how well we know it, what we don't know, and what we can't know - enabling more informed decisions and more credible research.