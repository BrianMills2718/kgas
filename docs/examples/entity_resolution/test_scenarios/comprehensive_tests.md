# Entity Resolution Comprehensive Test Scenarios

**Consolidated from**: stress_tests.md, advanced_stress_tests.md, complex_scenarios.md  
**Purpose**: Comprehensive test scenarios for entity resolution across different theories and discourse patterns  
**Last Updated**: 2025-08-06

---

## Overview

This document consolidates comprehensive test scenarios designed to validate the entity resolution framework across:
- Multiple theoretical frameworks (Social Movement, Organizational, Critical Discourse)
- Complex discourse patterns (coalition dynamics, nested references, temporal shifts)
- Real-world scenarios (multi-party negotiations, evolving identities)

---

## Test Suite 1: Social Movement Theory with Coalition Dynamics

### Theory Schema
```json
{
  "theory_name": "Social Movement Theory",
  "constructs": [
    {
      "name": "movement_identity",
      "definition": "Collective identity of social movement participants",
      "observable_indicators": ["we/us/our + movement terms", "collective action language"],
      "requires_entity_tracking": true
    },
    {
      "name": "coalition_dynamics",
      "definition": "Relationships between allied movement groups",
      "observable_indicators": ["partnership language", "joint action references"],
      "requires_entity_tracking": true
    },
    {
      "name": "opponent_framing",
      "definition": "How movements characterize their opposition",
      "observable_indicators": ["they/them + negative characterization"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse
```
Speaker_001 (Environmental Activist): "We need to unite all environmental groups. The oil companies have divided us for too long."
Speaker_002 (Labor Representative): "Our union stands with you. They told us environmentalists were against workers, but we know they lied."
Speaker_003 (Indigenous Leader): "My people have fought them for generations. We welcome this coalition, though we've been betrayed before."
Speaker_001: "Together, we represent millions. They can't ignore us anymore."
Speaker_002: "When we march next week, they'll see our combined strength."
```

### Expected Resolution Challenges
- **"We"** shifts from single group to coalition
- **"They/them"** ambiguity between oil companies and other opponents
- **Coalition formation** creates new collective entities mid-discourse
- **Historical vs present** entity references ("fought them for generations")

---

## Test Suite 2: Organizational Theory with Boundary Spanning

### Theory Schema
```json
{
  "theory_name": "Organizational Theory",
  "constructs": [
    {
      "name": "organizational_identity",
      "definition": "How organizations define themselves",
      "observable_indicators": ["we/our + organizational terms"],
      "requires_entity_tracking": true
    },
    {
      "name": "boundary_spanning",
      "definition": "Activities that cross organizational boundaries",
      "observable_indicators": ["cross-functional", "inter-departmental", "partnership"],
      "requires_entity_tracking": true
    },
    {
      "name": "institutional_pressure",
      "definition": "External forces on organizations",
      "observable_indicators": ["they require", "regulators demand", "market forces"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse
```
CEO: "We at TechCorp believe in innovation. They say we're too disruptive, but they don't understand our vision."
VP_Engineering: "Our engineering team works closely with them in marketing. We've learned they have different priorities."
VP_Marketing: "When we say 'customer-centric,' they hear 'expensive.' They in finance always push back."
CEO: "The board wants us to be more like them - our competitors. But we're not them."
External_Consultant: "You keep saying 'they' but you mean different groups each time."
```

### Expected Resolution Challenges
- **"They"** refers to critics, departments, finance, competitors within same conversation
- **"We"** scales from company to department to team
- **Meta-commentary** about entity resolution itself
- **Self-referential confusion** ("we're not them" where them = we in different context)

---

## Test Suite 3: Critical Discourse Analysis

### Theory Schema
```json
{
  "theory_name": "Critical Discourse Analysis",
  "constructs": [
    {
      "name": "power_relations",
      "definition": "How power dynamics manifest in discourse",
      "observable_indicators": ["domination language", "resistance language"],
      "requires_entity_tracking": true
    },
    {
      "name": "ideological_positioning",
      "definition": "How speakers position themselves ideologically",
      "observable_indicators": ["we believe", "they claim", "our values"],
      "requires_entity_tracking": true
    },
    {
      "name": "discourse_coalitions",
      "definition": "Groups united by shared discourse patterns",
      "observable_indicators": ["shared terminology", "aligned framing"],
      "requires_entity_tracking": true
    }
  ]
}
```

### Example Discourse
```
Academic_A: "We critical scholars challenge their hegemonic discourse."
Journalist_B: "When you say 'we,' are you speaking for all academics?"
Academic_A: "Those who understand power structures. They - the mainstream - ignore systemic issues."
Policy_Maker_C: "We need practical solutions. They in academia offer only critique."
Academic_B: "I'm an academic but I don't agree with them. We applied researchers work differently."
Activist_D: "You're all 'they' to us on the ground. We see the real impacts."
```

### Expected Resolution Challenges
- **Contested group membership** (who is "we critical scholars")
- **Dynamic repositioning** (Academic_B switches from "them" to "we")
- **Perspective-dependent entities** ("they" changes based on speaker position)
- **Meta-level critique** of entity categories themselves

---

## Test Suite 4: Nested Reference Complexity

### Scenario: Multi-level Organizational Meeting
```
Director: "We need to decide if they should continue their project."
Manager_A: "When you say 'they,' do you mean my team or theirs?"
Manager_B: "Our team has concerns about their approach."
Director: "I mean the joint team - the one where your people and their people work together."
Manager_A: "So when they meet tomorrow, should we tell them about our concerns?"
Director: "Tell them - the joint team - that we - leadership - support them, but they - the client - has concerns."
```

### Resolution Challenges
- **Nested group references** (teams within teams)
- **Ambiguous antecedents** with multiple valid interpretations
- **Shifting group boundaries** (joint team as new entity)
- **Multiple valid parses** of the same pronouns

---

## Test Suite 5: Temporal Entity Evolution

### Scenario: Historical Analysis
```
Historian: "We must understand how they evolved. In 1990, they were a small movement. By 2000, they had become mainstream."
Student: "But didn't they split in 1995?"
Historian: "Yes, they became two groups. The radicals kept the name, but they - the moderates - had more influence."
Student: "So when we say 'they won,' which they do we mean?"
Historian: "By 2010, they had reunited, so 'they' means the reformed coalition."
```

### Resolution Challenges
- **Entity splitting and merging** over time
- **Name inheritance** (who keeps the original identifier)
- **Temporal scoping** (which "they" at which time)
- **Historical continuity** vs discontinuity

---

## Test Suite 6: Contested Definitions

### Scenario: Political Debate
```
Progressive: "We progressives support universal healthcare."
Moderate: "You don't speak for all of us. We progressive moderates have a different approach."
Conservative: "They call themselves progressives, but they're really socialists."
Progressive: "When they say 'socialist,' they mean anyone who disagrees with them."
Moderate: "Can we stop arguing about who 'we' and 'they' are and focus on policy?"
```

### Resolution Challenges
- **Contested group boundaries** (who counts as "progressive")
- **Labeling disputes** (external vs self-identification)
- **Meta-discourse** about entity definition itself
- **Strategic ambiguity** in group claims

---

## Validation Metrics

For each test scenario, measure:

1. **Resolution Accuracy**
   - Correct entity identification rate
   - Ambiguity preservation (when appropriate)
   - Coreference chain accuracy

2. **Uncertainty Quantification**
   - Confidence score calibration
   - Uncertainty type classification
   - Distribution quality for ambiguous cases

3. **Theoretical Validity**
   - Construct measurement accuracy
   - Theory-appropriate entity types
   - Relationship extraction quality

4. **Performance Metrics**
   - Processing time
   - Memory usage
   - Scalability with document size

---

## Success Criteria

The entity resolution system should:

1. **Handle Ambiguity**: Preserve uncertainty rather than forcing resolution
2. **Track Context**: Maintain speaker and temporal context
3. **Support Multiple Interpretations**: Allow probability distributions
4. **Scale Appropriately**: Process real-world document sizes
5. **Maintain Theoretical Validity**: Respect theory-specific requirements

---

## Notes on Test Design

These tests are designed to:
- Expose fundamental challenges in entity resolution
- Validate the framework against real-world complexity
- Ensure theoretical constructs can be measured
- Test system behavior at edge cases
- Provide benchmarks for improvement

Each test should be run with multiple LLM backends to ensure consistency across models.