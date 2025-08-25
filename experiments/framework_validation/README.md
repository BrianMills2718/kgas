# Framework Validation: Testing KGAS Analytical Frameworks

## Purpose

This directory contains controlled tests to validate different analytical frameworks for the KGAS (Knowledge Graph Analysis System). We are comparing approaches to determine which framework provides better analytical outcomes.

## Background Context

KGAS is a system for analyzing discourse (text) using social science theories. The system works through an LLM chatbot interface where users make analytical requests that need to be clarified and executed.

### The Three Framework Purposes

The analytical framework serves three purposes:

1. **Academic Categorization**: Organize social/behavioral/psychological theories by operational/analytic purpose rather than traditional disciplinary branches
2. **System Guidance**: Help the LLM chatbot clarify vague user requests into computationally tractable analyses  
3. **Theory Discovery**: Aid the system in finding relevant theories to apply given an analytical request

### Framework Under Test

**Original Framework**: Three-dimensional theory classification system
- **Level of Analysis**: Micro/Meso/Macro (individual/group/societal)
- **Component of Influence**: Who/Whom/What/Channel/Effect (speaker/audience/message/medium/outcome)
- **Causal Metatheory**: Agentic/Structural/Interdependent (individual agency/external structures/feedback loops)

**Alternative Framework**: Multi-dimensional analysis matrix from thinking_out_loud documents
- **Object of Study**: Text-as-object vs Text-as-window
- **Type of Claim**: Empirical/Interpretive/Evaluative/Constructive
- **Additional Dimensions**: Temporal orientation, inference levels

### Known Issues

Previous testing revealed analytical failures, specifically:
- Carter speech analysis using Social Identity Theory produced inappropriate results
- Unclear whether failure was due to framework flaws or improper implementation
- Need to determine if original framework was properly applied in its intended role

## Test Methodology

We conduct mock tests where a human manually walks through the complete analytical process:

1. **User Request**: Mock analytical request from researcher
2. **LLM Clarification**: How the framework guides request clarification
3. **Theory Selection**: How theories are chosen based on clarified request
4. **Analysis Execution**: How the analysis is performed
5. **Result Assessment**: Quality and appropriateness of outcomes

### Test Scenarios

Each framework approach is tested on the same analytical scenarios to enable direct comparison.

**Primary Test Case**: Carter speech analysis
- **Source**: Jimmy Carter political speech (specific speech TBD)
- **Initial Request**: "Analyze Carter's speech using Social Identity Theory"
- **Known Failure**: Previous analysis produced inappropriate results

## Files in This Directory

- `README.md` - This overview document
- `test_1_original_framework.md` - Test walkthrough using original three-dimensional framework
- `test_2_alternative_framework.md` - Test walkthrough using thinking_out_loud multi-dimensional framework  
- `test_3_current_system.md` - Control test showing current system behavior
- `carter_speech_text.md` - Source text for analysis (when identified)
- `comparison_analysis.md` - Side-by-side comparison of test results
- `findings_and_recommendations.md` - Conclusions and next steps

## Success Criteria

A framework succeeds if it:
1. **Clarifies user intent effectively** - Helps LLM ask useful clarifying questions
2. **Guides appropriate theory selection** - Leads to theories suitable for the analytical goal
3. **Produces coherent analysis** - Results make sense and address user needs
4. **Avoids known failure modes** - Doesn't repeat problems from previous testing
5. **Scales to real usage** - Approach works for variety of analytical requests

## Next Steps

1. Create mock test walkthroughs for each framework approach
2. Execute tests with systematic documentation
3. Compare results across approaches  
4. Identify strengths, weaknesses, and failure modes
5. Make recommendations for framework selection/modification

## Context for New LLMs

If you are a new LLM picking up this work:
- The goal is to validate analytical frameworks through controlled testing
- Focus on practical outcomes rather than theoretical elegance
- Document both successes and failures clearly
- Be skeptical of claims - verify through concrete testing
- The ultimate goal is improving real analytical outcomes for researchers using KGAS

## Status

- **Created**: 2025-01-27
- **Current Phase**: Initial test setup and Carter speech example preparation
- **Next Milestone**: Complete Test 1 (original framework walkthrough)