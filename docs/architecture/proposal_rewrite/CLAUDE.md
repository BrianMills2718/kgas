# Dissertation Proposal Writing Guidance

## Core Research Positioning

### What This Research IS
- **Testing feasibility**: Exploring whether computational methods CAN extract theoretically meaningful patterns from discourse
- **Establishing baselines**: Creating initial metrics for future systems to improve upon
- **Proof of concept**: Demonstrating that theory-aware computational social science is possible
- **Infrastructure building**: Creating frameworks that future research can build upon
- **Methodological contribution**: Providing systematic approaches for computational theory application

### What This Research IS NOT
- **Not claiming perfect accuracy**: Acknowledging LLM limitations and non-determinism
- **Not predicting offline behavior definitively**: Testing correlations, not claiming causation
- **Not a production system**: Academic research prototype, not enterprise software
- **Not theory generation yet**: Currently extracting and applying existing theories, but the system provides groundwork for future theory generation capabilities

## Writing Style Requirements

### Tense Usage
- **Future tense for proposed work**: "The system will demonstrate..." not "The system demonstrates..."
- **Present tense for existing facts**: "Current methods require..." not "Current methods will require..."
- **Past tense for completed work**: "Prototype plugins demonstrated..." not "Prototype plugins demonstrate..."

### Example Framing
- Always use "such as" or "for example" when listing examples
- Use parentheses for inline examples: "theories (such as Social Identity Theory, Diffusion of Innovations)"
- **IMPORTANT**: All theory mentions are exemplars only - not committing to specific theories
- **Usage Pattern**: "For example, Social Identity Theory would guide..." not "Social Identity Theory guides..."
- **Flexibility Message**: System works with any theory that can be formalized
- Always frame theories as concrete examples to help readers understand, not as locked-in choices
- Avoid "like" for examples - too informal

### Precision in Claims
- **Avoid absolutes**: "can help identify" not "identifies"
- **Acknowledge complexity**: "testing whether" not "proving that"
- **Maintain humility**: "initial capabilities" not "comprehensive solution"

### Positive Framing
- **Describe what the system WILL DO**: Focus on proposed capabilities and approach
- **Avoid "not" statements**: Don't define by negation
- **Example**: "Theory-guided data flow" not "This is not three separate analyses"
- **Remember**: System is proposed work, not yet functional

## Content Principles

### Avoid Redundancy
- **Introduce concepts once fully**, then reference briefly
- **Each section should have distinct contribution**
- **Don't re-explain core concepts** in every section
- Key concepts to introduce once:
  - Theory application capabilities (1.2)
  - Cross-modal analysis (1.2)
  - Low-code interface (1.2)
  - Policy relevance (1.1)
  - Validation approach (1.3 for COVID, 1.6 for general)

### Maintain Consistency
- **Theory mentions**: All theories mentioned are examples only - system is theory-agnostic
- **Three modalities**: Graph, Table, Vector (all primary)
  - **CRITICAL**: These are NOT three parallel analyses but **cross-modal data flow**
  - Theories specify how data flows between modalities (e.g., Social Identity Theory requires graph communities → table psychology → vector language)
  - Outputs from one modality become inputs to another based on theoretical requirements
  - The innovation is theory-guided data routing, not just "analyze three ways"
  - **Key Innovation**: Theories become computational routing instructions that determine how data flows
  - **Example Flow Patterns**:
    - Social Identity: Graph(communities) → Table(psychology) → Vector(language patterns)
    - Network Contagion: Graph(cascade paths) → Table(adopter characteristics) → Vector(message evolution)
    - Motivated Reasoning: Table(psychological profiles) → Graph(information consumption) → Vector(confirmation bias)
- **Three levels of analysis** (from Larson et al. framework):
  - Individual level
  - Group level
  - Mass public level
- **Three essays**:
  - Essay 1: Exploring what to build to maximize value from LLMs for computational social science (Chapters 1-3)
  - Essay 2: Implementation (KGAS system architecture) (Chapters 4-6)
  - Essay 3: Demonstration (COVID dataset application) (Chapters 7-9)

### Technical Accuracy
- **KGAS development status**: Many tools/capabilities have been developed in isolation and are currently being integrated into the system
- **Prototype plugins exist**: Qualitative coding and process tracing plugins demonstrate feasibility
- **All other development framed as future work**: Except for the existing plugins and isolated tool development
- **Uncertainty propagation is automatic**: Built into every tool, not a separate step
- **Entity/relation extraction happens together**: One step, not two
- **Tools are modular and composable**: Can be reordered based on needs
- **Cross-modal data flow**: Data passes between modalities based on theoretical requirements
  - Example: Graph identifies communities → those user IDs flow to table for psych analysis → high-identity users flow to vector for language analysis
  - This is NOT three separate analyses but integrated hypothesis testing

## Specific Terminology

### Preferred Terms
- "Computational constructs" not "measures" (acknowledging they're approximations)
- "Discourse patterns" not "text features"
- "Theory-aware" not "theory-driven" (the system uses theories, isn't controlled by them)
- "Fringe discourse" not "extremist content" (more neutral)
- "Workflow generation" not "pipeline creation" (emphasizes flexibility)
- "Agentic" not "automated" (emphasizes intelligent adaptation)

### Avoid These Terms
- "Pipeline" (implies rigid sequence) → use "workflow"
- "Ground truth" (rarely exists for complex constructs) → use "validation measures"
- "Detect" extremism → use "identify patterns associated with"
- "Prove" → use "test" or "evaluate"
- "Solution" → use "approach" or "system"

## Structure Guidelines

### Chapter Flow
- **Concise bridges required**: Each chapter must link to previous chapters while minimizing redundancy
- Bridge format: "Where Chapter X established Y, this chapter will explore Z"
- Briefly acknowledge what has been explained so far and how it relates to upcoming content
- Each chapter should be readable standalone but explicitly build on previous
- Avoid forward references unless essential

### Figure Requirements (RAND Style)
- Number figures sequentially: Figure 1.1, Figure 1.2
- Include NOTE lines explaining non-obvious aspects
- Don't include SOURCE lines for author-generated content
- Place figures immediately after first reference

### Citation Style
- Author-date in text: (Larson et al., 2009)
- Superscript numbers for footnotes only when necessary
- Full references in bibliography

## Scope Management

### In Scope
- COVID conspiracy discourse as demonstration case for the dissertation (system itself is not limited to fringe discourse)
- Multiple theoretical frameworks as examples (not locked into specific theories)
- Graph, table, and vector as primary modalities
- Validation against psychological measures
- Baselines for future improvement
- Agent-based modeling (Essay 3)
- Structural equation modeling (Essay 3)

### Timeline Considerations
- **Target Defense**: February 2026 (6-month timeline from August 2025)
- **Compressed Schedule**: Aggressive timeline requires focused scope
- **Key Milestones**: Should align with 6-month timeline
- **Validation Scope**: Full 14-dimension framework described, flexible implementation

### Out of Scope (but acknowledge as future work)
- Theory generation (though system provides groundwork)
- Causal inference
- Offline behavior prediction (testing correlation only)
- Production deployment

## Validation Framing

### What We're Validating
- **Construct validity**: Do computational constructs correlate with psychological measures?
- **Extraction accuracy**: Can the system identify entities and relationships?
- **Cross-modal data flow**: Does theory-guided data routing produce expected patterns?
- **Theory application**: Can theories be systematically operationalized?
- **14 Uncertainty Dimensions**: System's ability to assess evidence quality across dimensions like source credibility, cross-source coherence, temporal relevance, extraction completeness, entity recognition, construct validity, theory-data fit, study limitations, sampling bias, diagnosticity, sufficiency, confidence calibration, entity identity resolution, and reasoning chain validity

### Validation Methods Available
- **Davis's 5-Dimensional Framework**: Description, Causal Explanation, Postdiction, Exploratory, Prediction
- **Inter-LLM Agreement**: Consistency checking across multiple models
- **Human Expert Comparison**: Expert ratings as ground truth
- **Crowd Coding**: Mechanical Turk for simple tasks
- **Ground Truth Datasets**: Where objective truth exists (e.g., CoNLL-2003, HotPotQA)
- **Correlation Analysis**: Compare to validated psychological measures
- **Theory Replication**: Extract theory → Apply to paper's data → Compare findings

### What We're NOT Validating
- Absolute truth of findings
- Causal relationships
- Generalization beyond online discourse
- Superiority over human analysts

## Key Messages to Maintain

### For Policy Audiences
- Enables analysis at scale previously impossible
- Provides systematic approach vs. ad-hoc analysis
- Offers transparency and reproducibility
- Reduces time from months to minutes

### For Academic Audiences
- Methodological contribution to computational social science
- Systematic framework for theory operationalization
- Empirical validation with psychological ground truth
- Foundation for future research

### For Technical Audiences
- Novel integration of LLMs with structured analysis
- Cross-modal architecture with provenance tracking
- Uncertainty propagation throughout workflow
- Modular, composable tool architecture

## Common Pitfalls to Avoid

### Overstatement
- Don't claim to solve misinformation
- Don't promise perfect prediction
- Don't suggest replacing human analysts
- Don't claim universal applicability

### Understatement
- Don't minimize the technical achievement
- Don't apologize for limitations excessively
- Don't undervalue the policy contributions
- Don't ignore successful validations

### Inconsistency
- Keep theory names consistent throughout
- Maintain same level of technical detail
- Use same examples across chapters
- Apply same validation standards throughout

## Review Checklist

Before finalizing any section, verify:
- [ ] Future tense for proposed work
- [ ] Examples use "such as" or "for example"
- [ ] No redundant explanations of core concepts
- [ ] Consistent with multiple theories (as examples), three modalities, three levels
- [ ] Acknowledges complexity without undermining contribution
- [ ] Aligns with RAND style guide for figures and citations
- [ ] Each section has distinct contribution
- [ ] Appropriate scope boundaries maintained
- [ ] Key messages preserved
- [ ] Technical accuracy maintained
- [ ] Cross-modal data flow (not parallel analyses) is clear

## Document Evolution Notes

This guidance should be updated when:
- New scope decisions are made
- Terminology preferences change
- Additional constraints are identified
- Validation approaches are refined

Last Updated: 2025-08-07
Primary Purpose: Ensure consistency and appropriate positioning throughout dissertation proposal
Target Length: ~15,000 words for full proposal