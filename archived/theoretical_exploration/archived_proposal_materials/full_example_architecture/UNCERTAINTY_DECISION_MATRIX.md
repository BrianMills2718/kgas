# KGAS Uncertainty System Decision Matrix

## Documentation Index

### 1. Core Uncertainty Documents
- **ADR-029**: IC-Informed Uncertainty Framework (`/adrs/ADR-029-IC-Informed-Uncertainty-Framework/`)
- **UncertaintyMgr Investigation**: Service architecture review (`/architecture_review_20250808/uncertaintymgr_investigation.md`)
- **Provenance Investigation**: Provenance service uncertainty (`/architecture_review_20250808/provenanceservice_investigation.md`)
- **Debugging Notes**: Implementation issues (`/debugging_20250127/UNCERTAINTY_INVESTIGATION_NOTES.md`)
- **IC Integration**: 30+ IC methodology docs (`/proposal_rewrite/ic_uncerntainty_integration/`)
- **Schema Notes**: Theory schemas (`/proposal_rewrite/uncertainity_and_schema_notes/`)
- **Full Example**: Current working design (`/proposal_rewrite/full_example/`)

### 2. Key Proposals Across Documents

## Decision Matrix: Accept ✅ / Reject ❌

### Mathematical Frameworks

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Dempster-Shafer Theory** | Full Example, ADR-029 | ✅ **ACCEPT** | Simple, handles "don't know", good for evidence combination |
| **Bayesian Probability** | ADR-016, UncertaintyMgr | ❌ **REJECT** | Too complex, requires calibration we don't want |
| **Root-Sum-Squares Propagation** | ADR-029 | ❌ **REJECT** | Assumes independence that doesn't exist in our pipeline |
| **Simple Sequential Combination** | Full Example | ✅ **ACCEPT** | u_total = u_a + u_b(1-u_a), intuitive and sufficient |
| **Hierarchical D-S for Scale** | Full Example | ❌ **REJECT** | Over-engineered, D-S is already O(n) and fast |

### IC Methodologies

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **ICD-203 Probability Bands** | ADR-029 | ❌ **REJECT** | Prescriptive categories limit LLM flexibility |
| **ICD-206 Source Quality** | ADR-029 | ❌ **REJECT** | Over-structured for academic sources |
| **ACH (Analysis of Competing Hypotheses)** | Full Example | ✅ **ACCEPT** (Optional) | Useful structure for complex entity resolution |
| **Key Assumptions Check** | Full Example | ✅ **ACCEPT** (Optional) | Good for theory applicability assessment |
| **Heuer's Cognitive Bias Awareness** | ADR-029 | ❌ **REJECT** | Too prescriptive, let LLM reason naturally |

### Uncertainty Dimensions

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **7 Core Dimensions** | Full Example | ✅ **ACCEPT** | Comprehensive coverage of uncertainty sources |
| **CERQual 4 Dimensions** | UncertaintyMgr | ❌ **REJECT** | Too academic/rigid for proof of concept |
| **14 Uncertainty Dimensions** | IC Integration | ❌ **REJECT** | Overcomplicated for initial implementation |
| **Single Reasoning Field** | Full Example | ✅ **ACCEPT** | Flexible, lets LLM identify relevant factors |

### Implementation Architecture

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Central UncertaintyMgr Service** | ADR-029 | ❌ **REJECT** | Over-engineered for proof of concept |
| **Distributed Confidence (15+ components)** | UncertaintyMgr | ❌ **REJECT** | Too fragmented, hard to maintain |
| **Dynamic Tool Self-Assessment** | Full Example | ✅ **ACCEPT** | Each generated tool assesses its own uncertainty |
| **Unified Provenance Tracking** | Full Example | ✅ **ACCEPT** | Essential for debugging and transparency |

### Data Structures

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **BeliefMass Schema** | Full Example | ✅ **ACCEPT** | Clean Pydantic schema for D-S |
| **ToolUncertainty Schema** | Full Example | ✅ **ACCEPT** | Universal output for all tools |
| **Complex CERQual Assessment** | UncertaintyMgr | ❌ **REJECT** | Too structured for our needs |
| **Temporal Decay Models** | UncertaintyMgr | ❌ **REJECT** | Not needed for initial system |

### Prompting Strategies

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Expert Role Prompting** | Our Discussion | ✅ **ACCEPT** | LLM as expert making subjective assessments |
| **Prescriptive Examples** | IC Docs | ❌ **REJECT** | Causes tunnel vision in LLMs |
| **Structured Output Schemas** | Our Discussion | ✅ **ACCEPT** | Pydantic ensures consistent output format |
| **Prompt Evolution/Learning** | Critiqued | ❌ **REJECT** | Over-complication for proof of concept |

### Tool Generation

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Dynamic Tool Generation** | Full Example | ✅ **ACCEPT** | Core innovation of the system |
| **Code Sandboxing** | Critiqued | ❌ **REJECT** | Research environment, not production |
| **Tool Validation Against Examples** | Critiqued | ❌ **REJECT** | Too complex for proof of concept |
| **Fail-Fast Philosophy** | Full Example | ✅ **ACCEPT** | Appropriate for research prototype |
| **Complete Provenance Capture** | Full Example | ✅ **ACCEPT** | Essential for debugging generated code |

### Aggregation Patterns

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Tweet→User→Community** | Full Example | ✅ **ACCEPT** | Natural hierarchy for social media |
| **Temporal Window Aggregation** | Full Example | ✅ **ACCEPT** (Future) | Good pattern but not immediate priority |
| **Cross-Modal Convergence** | Full Example | ✅ **ACCEPT** | Key validation mechanism |
| **Weighted D-S by Influence** | Full Example | ❌ **REJECT** | Adds complexity without clear benefit |

### Uncertainty Interpretation

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Calibrated Probabilities** | ADR-016 | ❌ **REJECT** | Impossible for social constructs |
| **Subjective Expert Assessment** | Full Example | ✅ **ACCEPT** | Matches social science epistemology |
| **Categorical (Low/Med/High)** | Alternative | ❌ **REJECT** | Less informative than 0-1 scores |
| **Numeric with Reasoning** | Full Example | ✅ **ACCEPT** | Best of both worlds |

### System Philosophy

| Proposal | Source | Decision | Justification |
|----------|--------|----------|---------------|
| **Human-in-the-Loop** | IC Docs | ❌ **REJECT** | Fully autonomous system |
| **Transparency Over Precision** | Full Example | ✅ **ACCEPT** | Core principle |
| **Localized Uncertainty** | Full Example | ✅ **ACCEPT** | Missing data doesn't contaminate everything |
| **Theory-Reality Mismatch as Uncertainty** | Full Example | ✅ **ACCEPT** | Makes limitations transparent |

## Final Accepted Components (PURE LLM INTELLIGENCE APPROACH)

### Core System (What We're Building)
1. **Universal uncertainty (0-1)** for ALL operations
2. **Single UniversalUncertainty schema** everywhere
3. **Dynamic tool generation** with self-assessment
4. **Expert role prompting** without prescriptive examples
5. **Single assess_uncertainty() method** that handles everything
6. **Complete provenance** tracking
7. **Fail-fast** development philosophy
8. **7 dimensions as concepts** (not prescribed, LLM considers as relevant)
9. **Localized uncertainty** (missing data has limited impact)
10. **LLM intelligence** for all uncertainty logic (no magic numbers)

### Pure LLM Rules
- **Individual tools**: LLM assesses uncertainty contextually
- **Aggregation**: LLM recognizes agreement/conflict naturally
- **Cross-modal synthesis**: LLM sees convergence patterns
- **Sequential chains**: LLM understands propagation effects

### Optional Enhancements (Can Add Later)
1. **ACH structure** for complex entity resolution
2. **Key assumptions check** for theory applicability
3. **Temporal aggregation** when needed
4. **Cross-modal routing specs** when implementing

### Explicitly Rejected (Not Building)
1. ❌ IC probability bands and source quality metrics
2. ❌ CERQual framework
3. ❌ Bayesian methods
4. ❌ Temporal decay models
5. ❌ Calibrated probabilities
6. ❌ Central UncertaintyMgr service
7. ❌ Human review checkpoints
8. ❌ Code sandboxing
9. ❌ Prompt evolution systems
10. ❌ Complex hierarchical aggregation

## Implementation Priority

### Phase 1 (Immediate)
- BeliefMass and ToolUncertainty schemas
- Basic D-S combination function
- Expert role prompts in /prompts/ folder
- Dynamic tool generation with uncertainty

### Phase 2 (Next)
- Aggregation tools (Tweet→User)
- Cross-modal convergence assessment
- Provenance tracking integration

### Phase 3 (Future)
- Optional IC methods (ACH, assumptions)
- Temporal patterns
- Performance optimization

## Key Insight

The existing KGAS uncertainty infrastructure is **over-engineered** for our proof of concept. We're building a **simpler, more elegant system** that:
- Embraces subjective expert assessment
- Uses D-S for evidence combination
- Generates tools that assess their own uncertainty
- Maintains complete transparency through reasoning and provenance

This approach is **philosophically aligned** with social science methodology while being **practically implementable** for a research prototype.