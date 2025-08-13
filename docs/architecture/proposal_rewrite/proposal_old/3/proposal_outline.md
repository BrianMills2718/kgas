CORE STRUCTURE: 20 Pages + Appendices

  ---
  1. OVERVIEW & RESEARCH DEMONSTRATION (2 pages)

  Purpose: Concrete example before abstract discussion

  1.1 COVID Conspiracy Belief Analysis Example

  - Research Question: "Can computational methods extract psychological construct estimates from discourse that correlate with validated self-report measures?"
  - Dataset: 2,506 Twitter users with psychological profiles + 7.7M behavioral interactions
  - Process: Theory extraction → Construct estimation → Correlation validation
  - Expected Result: Significant correlations between KGAS construct estimates and validated psychological scales

  1.2 System Capabilities Demonstration

  - Theory Integration: 8 radicalization theories → unified computational framework
  - Cross-Modal Analysis: Graph (network influence) + Table (regression models) + Vector (semantic trajectories)
  - Validation: Agent-based simulation testing theoretical predictions
  - Timeline: 10 days vs. 29 months traditional analysis

  ---
  2. RESEARCH QUESTIONS & CONTRIBUTIONS (2 pages)

  2.1 Primary Research Questions

  1. Theory Application: Can systematic computational frameworks improve theory selection and application in social science research?
  2. Construct Validation: Can automated systems extract theoretically meaningful construct estimates from discourse that correlate with validated measures?
  3. Cross-Modal Integration: How do findings differ across analytical modalities (graph, table, vector) and what insights emerge from integration?

  2.2 Academic Contributions

  - Methodological: First systematic framework for computational theory selection and application
  - Technical: Theory Meta-Schema enabling machine-readable social science theories
  - Empirical: Validation using psychological construct correlation with behavioral data
  - Practical: Demonstrated application to policy-relevant social phenomena (radicalization, intervention design)

  2.3 Scope and Limitations

  - Bounded Context: Online discourse analysis, not comprehensive social behavior prediction
  - Validation Focus: Construct estimation accuracy, not causal inference about offline behavior
  - Research Risk: Offline factors may drive attitude shifts not captured in online data

  ---
  3. THEORETICAL FRAMEWORK (3 pages)

  3.1 Theory Selection Problem

  - Current Challenge: Fragmented theoretical landscape, inconsistent theory application
  - Proposed Solution: Three-dimensional organizing framework

  3.2 DEPI×Level×Component Framework

  - Analytical Goals: Describe, Explain, Predict, Intervene
  - Levels of Analysis: Individual, Group, Society
  - Communication Components: Who, What, To Whom, Channel, Settings, Effect

  3.3 Theory Meta-Schema Architecture

  Four core components enabling computational theory application:
  - Identity: Bibliographic metadata and theoretical relationships
  - Classification: Automated dispatch keys for theory selection
  - Ontology: Entities, relationships, and properties for extraction
  - Execution Logic: Mathematical formulas, logical rules, procedural steps

  3.4 Example: Social Identity Theory Implementation

  - Classification: Meso-level, Individual Logic, Receiver-focused, Explanatory
  - Ontology: In-group/out-group entities, identification relationships, favoritism properties
  - Execution: In-group favoritism score = COUNT(favorable) - COUNT(derogatory)
  - Validation: Correlation with self-reported group identification measures

  ---
  4. SYSTEM ARCHITECTURE (4 pages)

  4.1 Positioning Relative to Existing Systems

  - GraphRAG Comparison: KGAS as theory-aware GraphRAG vs. data-driven graph construction
  - Standard RAG Limitations: Inability to represent multi-hop theoretical relationships
  - Innovation: Dynamic graph construction based on theoretical frameworks rather than semantic similarity

  4.2 Cross-Modal Analysis Architecture

  Research Question → Theory Selection → Multi-Modal Application
      ↓                    ↓                    ↓
  Framework Mapping → Theory Meta-Schema → Graph + Table + Vector Analysis
      ↓                    ↓                    ↓
  DEPI Classification → Executable Code → Integrated Results + Uncertainty

  4.3 Technical Infrastructure

  - Hardware: 8 vCPU / 32 GB RAM VM for single-node academic research
  - Data Architecture: Neo4j (graph analysis) + SQLite (statistical operations)
  - LLM Integration: Structured output with Pydantic schema validation
  - Uncertainty Framework: 12-dimension IC-informed confidence tracking

  4.4 Implementation Approach

  - Development Strategy: Well-developed prototype demonstrating methodology
  - Academic Focus: Designed for research reproducibility and theoretical rigor
  - Validation Priority: Construct estimation accuracy over system performance optimization

  ---
  5. ESSAY 1 METHOD: THEORY INTEGRATION APPROACH (2 pages)

  5.1 Literature Synthesis Methodology

  - Scope: Systematic review of influence theories across communication, psychology, sociology
  - Framework Population: Map existing theories to DEPI×Level×Component dimensions
  - Meta-Schema Development: Create computational specifications for 20+ core theories

  5.2 Theory Organization Process

  1. Theory Identification: Literature search and expert consultation
  2. Dimensional Mapping: Classify theories by analytical capability and scope
  3. Schema Creation: Convert theoretical structures to machine-readable format
  4. Validation: Expert review of theoretical fidelity and computational accuracy

  5.3 Expected Deliverables

  - Three-dimensional theory typology organized by function rather than academic discipline
  - Theory Meta-Schema specification with implementation examples
  - Populated theory library with 20+ social science theories in computational format

  ---
  6. ESSAY 2 METHOD: SYSTEM DEVELOPMENT & VALIDATION (2 pages)

  6.1 Dataset Specification

  - Primary: COVID conspiracy discourse (Kunst et al., 2024) - 2,506 users with psychological profiles + 7.7M interactions
  - Data Elements: Post texts, user interactions (likes, replies, reposts), psychological scale scores
  - Network Definition: Interaction-based networks, not follower relationships
  - Cross-Platform: Twitter-focused with potential Reddit expansion

  6.2 Validation Strategy (Two-Level Framework)

  Level 1: Basic Extraction Accuracy
  - Method: Crowd worker coding of 500 posts for entities and sentiment
  - Metrics: Precision, Recall, F1-scores for entity extraction and stance classification
  - Target: F1 > 0.80 for foundational extraction tasks
  - Protocol: HotPotQA-style multi-hop reasoning tests for complex queries

  Level 2: Construct Estimation Validation
  - Method: Correlation analysis between KGAS construct estimates and validated psychological scales
  - Measures: Conspiracy mentality, narcissism, need for chaos, misinformation susceptibility
  - Analysis: Pearson correlations with significance testing and effect size reporting
  - Target: Significant correlations (r > 0.30) demonstrating construct validity

  6.3 Data Processing Pipeline

  - Filtering: Bot detection, language filtering, content relevance screening
  - Cleaning: Text normalization, spam removal, duplicate detection
  - Quality Assurance: Manual spot-checking, automated consistency validation

  ---
  7. ESSAY 3 METHOD: ANALYSIS & ABM PARAMETER EXTRACTION (2 pages)

  7.1 Cross-Modal Theory Application

  - Graph Analysis: Social network analysis using theory-specified centrality measures
  - Table Analysis: Regression modeling with theory-derived variable specifications
  - Vector Analysis: Semantic analysis using theory-informed clustering and trajectory mapping
  - Integration: Multi-modal convergence analysis with uncertainty preservation

  7.2 Agent-Based Modeling Framework

  Reference: Park et al. (2023) Generative Agents, Google Concordia (Vezhnevets et al., 2023)
  Innovation: Empirical agent parameterization from real behavioral data

  Agent Architecture:
  - Granularity: Individual-level agents with psychological archetypes
  - Initialization: Belief states from discourse analysis, network from interaction data
  - Behavioral Rules: Theory-derived probabilistic functions (e.g., Social Learning influence equations)
  - Interactions: Message sharing, belief updating, network evolution

  Calibration Protocol:
  - Network Structure: Match observed clustering coefficients and path lengths
  - Behavioral Patterns: Validate against empirical adoption curves
  - Sensitivity Analysis: Monte Carlo sampling over uncertainty distributions
  - Validation: Compare simulation outcomes to held-out behavioral data

  7.3 Research Risk Mitigation

  - Offline Behavior Limitation: Acknowledge that online data may miss key causal factors
  - Self-Contained Validation: Focus on COVID dataset correlations as proof-of-concept
  - Bounded Claims: Frame findings as online discourse patterns, not comprehensive social prediction

  ---
  8. VALIDATION STRATEGY (2 pages)

  8.1 Construct Estimation Validation

  Primary Validation: COVID Dataset Correlation Analysis
  - Hypothesis: KGAS construct estimates correlate significantly with validated psychological measures
  - Statistical Approach: Pearson correlations with Bonferroni correction for multiple comparisons
  - Effect Size: Target r > 0.30 (medium effect) for meaningful construct validity
  - Robustness: Cross-validation using random data splits and bootstrap confidence intervals

  8.2 Cross-Modal Consistency Testing

  - Convergence Analysis: Compare findings across graph, table, and vector modalities
  - Theoretical Prediction Testing: Validate specific theoretical predictions (e.g., 3-degree network influence)
  - Integration Assessment: Measure added value of multi-modal vs. single-modal analysis

  8.3 Uncertainty Quantification Validation

  12-Dimension Framework Application:
  - Source Analysis: Individual credibility, cross-source coherence, temporal relevance
  - Computational: Extraction completeness, entity recognition accuracy
  - Theoretical: Construct validity, theory-data fit
  - Methodological: Study limitations, sampling bias
  - Evidence Integration: Diagnosticity, sufficiency
  - Output: IC probability bands (almost certain, very likely, likely, etc.)

  ---
  9. TIMELINE & LIMITATIONS (1 page)

  9.1 18-Month Implementation Timeline

  - Months 1-6: Theory integration and meta-schema development
  - Months 7-12: System implementation and validation framework
  - Months 13-18: Analysis, ABM validation, and dissertation writing

  9.2 Known Limitations

  - Scope: Online discourse analysis, not comprehensive social behavior prediction
  - Causal Inference: Correlation validation, not causal mechanism verification
  - Platform Coverage: Twitter-focused with limited cross-platform generalization
  - Theory Coverage: 20+ theories, not exhaustive coverage of social science

  9.3 Success Criteria

  - Technical: F1 > 0.80 for basic extraction tasks
  - Theoretical: Significant correlations (r > 0.30) between construct estimates and validated measures
  - Methodological: Demonstrated improvement over single-theory approaches
  - Academic: Reproducible methodology with clear validation protocols

  ---
  APPENDICES

  Appendix A: Complete Theory Typology Tables

  - Full DEPI×Level×Component mapping for all three causal logics
  - Social Identity Theory detailed walkthrough
  - Theory Meta-Schema JSON specification examples

  Appendix B: Technical Implementation Details

  - System architecture diagrams
  - Technology stack specifications
  - Database schema designs
  - API interface documentation

  Appendix C: Validation Protocols

  - Crowd worker coding instructions
  - Statistical analysis plans
  - Agent-based modeling calibration procedures
  - Uncertainty assessment guidelines

  Appendix D: Literature Review

  - Comprehensive theory mapping across disciplines
  - GraphRAG comparison analysis
  - Computational social science methodology review

  ---
  KEY INTEGRATION NOTES

  Resolved Prateek Critiques

  - GraphRAG Comparison: Positioned as theory-aware extension
  - Dataset Structure: Detailed specification of data elements and cross-platform considerations
  - Validation Strategy: Two-level framework with specific metrics and protocols
  - ABM Details: Agent architecture, calibration, and sensitivity analysis protocols
  - Research Risk: Acknowledged offline behavior limitation with mitigation strategy

  Maintained Academic Integrity

  - No Functionality Claims: All capabilities described as "designed to" demonstrate methodology
  - Evidence-Based Validation: Specific, testable validation approaches without assumed results
  - Realistic Scope: Bounded claims about what system can and cannot demonstrate
  - Reproducible Methods: Clear protocols that other researchers can implement and validate
