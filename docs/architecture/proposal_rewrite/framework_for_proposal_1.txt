# Computational Theory Selection Framework for Social Science Research

## Abstract

This framework addresses the challenge of systematic theory selection and application in computational social science research. The proposed system organizes theoretical knowledge through a structured schema that enables automated matching of research questions to appropriate theoretical frameworks. The framework operationalizes the DEPI taxonomy (Describe, Explain, Predict, Intervene) across multiple analysis levels and discourse elements, providing researchers with systematic guidance for theory-driven computational analysis.

## Problem Statement

Current approaches to theory selection in computational social science lack systematic organization, leading to inconsistent theory application and missed analytical opportunities. Researchers often apply familiar theories without considering alternatives that might better address their research questions. This results in suboptimal theoretical frameworks and reduced analytical rigor.

## Proposed Framework

### Theoretical Foundation

The framework builds on Lasswell's communication model (who says what to whom in what channel in what setting with what effect) integrated with the DEPI analytical taxonomy. This creates a structured space for mapping research questions to theoretical capabilities.

### Framework Architecture

```
┌───────────────┐    ┌─────────────────────────────────────────┐    
│  RESEARCH     │───▶│           FRAMEWORK MAPPING             │    
│  QUESTION     │    │                                         │    
│               │    │  ┌─────────────┐  ┌─────────────────┐   │    
│ "Why did...?" │    │  │    GOAL     │  │     LEVEL       │   │    
└───────────────┘    │  │ Describe    │  │ Individual      │   │    
                     │  │ Explain     │×│ Group           │×  │    
                     │  │ Predict     │  │ Society         │   │    
                     │  │ Intervene   │  └─────────────────┘   │    
                     │  └─────────────┘                        │    
                     │                                         │    
                     │  ┌───────────────────────────────────┐  │    
                     │  │        DISCOURSE ELEMENTS          │  │    
                     │  │ Who│What│Whom│Channel│Settings│Effect│  │    
                     │  └───────────────────────────────────┘  │    
                     └─────────────────────────────────────────┘    
                                        │                           
                                        ▼                           
                     ┌─────────────────────────────────────────┐    
                     │            THEORY SELECTION             │    
                     │                                         │    
                     │   Match specification to theory         │    
                     │   that fits analytical requirements     │    
                     └─────────────────────────────────────────┘    
                                        │                           
                                        ▼                           
┌────────────────┐   ┌─────────────────────────────────────────┐    
│  INTERPRETED   │   │         THEORY WITH COMPONENTS          │    
│   RESULTS      │   │                                         │    
│                │   │ THEORETICAL STRUCTURE:                  │    
│Context-aware   │   │ • Entities: core concepts               │    
│insights        │   │ • Relations: how concepts connect       │    
│addressing      │   │ • Modifiers: conditional qualifiers     │    
│original        │   │             ↓                           │    
│question        │   │ DATA FORMAT:                            │    
└───────▲────────┘   │ • Graph/Table/Matrix/Vector/Tree        │    
        │            │             ↓                           │    
        │            │ METHODS:                                │    
        │            │ • Mathematical: formulas, equations     │    
        │            │ • Logical: if-then rules, conditions    │    
        │            │ • Procedural: step sequences, protocols │    
        │            └─────────────────────────────────────────┘    
        │                               │                           
        │                               ▼                           
        │            ┌─────────────────────────────────────────┐    
        └────────────│           METHOD APPLICATION            │    
                     │                                         │    
                     │ Apply theory's methods to data in       │    
                     │ specified format, generate results      │    
                     │ using mathematical formulas, logical    │    
                     │ rules, and procedural steps             │    
                     └─────────────────────────────────────────┘    
```

### Core Components

**1. Framework Mapping**
The system maps research questions across three dimensions:
- **Analytical Goals (DEPI)**: Describe (pattern identification), Explain (causal mechanisms), Predict (forecasting), Intervene (change protocols)
- **Analysis Levels**: Individual, Group, Society
- **Discourse Elements**: Who, What, Whom, Channel, Settings, Effect

**2. Theory Schema**
Each theory contains:
- **Theoretical Structure**: Entities (core concepts), Relations (connections between concepts), Modifiers (conditional qualifiers)
- **Computational Representation**: Native data format (Graph, Table, Matrix, Vector, Tree, Sequence)
- **Methods**: Mathematical formulas, Logical rules, Procedural steps

**3. Systematic Matching**
The framework matches research specifications to theories based on:
- Use case compatibility (DEPI capabilities)
- Analysis level appropriateness
- Methodological capabilities
- Data format requirements

## Case Study: Social Identity Theory Application

**Research Question**: "Why did vaccination become a group identity marker during COVID?"

**Framework Mapping**:
- Goal: Explain (causal mechanisms)
- Level: Group (collective identity dynamics)
- Discourse: Who (vaccinated/unvaccinated groups), What (identity rhetoric), Effect (societal polarization)

**Theory Application**:
- Selected Theory: Social Identity Theory
- Structure: In-group/out-group entities, threat→categorization→bias relations
- Data Format: Graph (group networks)
- Method: Logical rule (IF threat THEN categorize → bias)
- Result: "Health threat triggered identity-protective categorization, creating vaccination tribes"

## Implementation

### Theory Database Structure
The system maintains theories in structured schemas containing:
- Theoretical components (entities, relations, modifiers)
- Computational specifications (data formats, algorithms)
- Use case mappings (DEPI capabilities)
- Validation criteria (structural tests, empirical evidence)

### Automated Processing
1. **Question Analysis**: Natural language processing to extract analytical intent
2. **Specification Generation**: Map to DEPI×Level×Discourse framework
3. **Theory Ranking**: Score theories by specification match
4. **Method Execution**: Apply selected theory's computational methods
5. **Result Interpretation**: Generate insights addressing original question

## Expected Contributions

This framework provides:
1. **Systematic Theory Organization**: Structured approach to cataloging theoretical knowledge
2. **Automated Theory Selection**: Computational matching of research questions to theories
3. **Multi-Theory Integration**: Framework for combining complementary theoretical perspectives
4. **Methodological Transparency**: Clear specification of theoretical assumptions and methods
5. **Reproducible Analysis**: Consistent application of theoretical frameworks across studies

The framework enables more rigorous theory-driven computational social science research through systematic organization and automated application of theoretical knowledge.