# Computational Theory Selection Framework - DEPRECATED

## Concept Summary
Automated theory selection using DEPI taxonomy (Describe, Explain, Predict, Intervene) combined with Lasswell's communication model for systematic theory-to-research-question mapping.

## Why Deprecated
- **Complex Algorithm**: Requires sophisticated NLP and theory matching
- **Missing Dependencies**: Needs theory database that doesn't exist
- **Current System Works**: User-specified theories and ontologies work fine
- **Over-Engineering**: Complex solution for simple configuration problem

## KISS Assessment
**Current System**: Users specify theories or ontologies directly
- Simple configuration-based approach
- Users know what theories they want to use
- Direct, transparent, controllable

**Automated Selection**: System selects theories based on research questions
- Complex NLP to parse research intent
- Theory database with capability mappings
- Matching algorithms and scoring
- Potential for incorrect selections

## Implementation Reality
This would require:
1. Natural language processing for question analysis
2. Comprehensive theory database with DEPI classifications
3. Theory capability matching algorithms
4. Research question to theory mapping logic
5. User interfaces for theory selection refinement
6. Validation that automated selections are appropriate

**Estimated Complexity**: 300+ lines of complex matching logic
**Current Alternative**: User configuration (1-10 lines in config file)

## User Experience Reality
**Current**: User says "I want to use Social Identity Theory"
**Automated**: User describes research question, system guesses appropriate theory

The current approach is:
- More transparent (user knows what theory is being used)
- More reliable (no algorithmic mismatches)
- More controllable (user can change theory easily)
- Simpler to implement and maintain

## Decision
**PERMANENTLY DEPRECATED** - Solves a problem users don't have with unnecessary complexity.

Users are capable of specifying which theories they want to use, and this provides better control and transparency than automated selection.