# Digimon/KGAS Idea Inventory

Cross-variant catalog of unique ideas, implementations, and artifacts worth preserving.
Created 2026-02-14 from systematic review of all 6 variants + digimons_old.

See also: `~/projects/ARCHIVE_INDEX.md` (detailed per-variant inventories)

---

## Status Key

- **EXTRACT** — Worth pulling into main Digimons as reference/implementation
- **POINTER** — Leave in archive, ARCHIVE_INDEX.md pointer is sufficient
- **DISCUSS** — Needs decision on whether/how to use

---

## A. Architectural Ideas

### A1. ExecutionPlan Schema + PlanningAgent (Digimon_for_KG_application)

**What**: Typed JSON execution plans with loops, conditionals, named outputs, inter-step data flow. PlanningAgent generates plans from NL queries via LLM, with ReAct mode for iterative reasoning.

**Why it matters**: Most sophisticated agent planning in any variant. The ExecutionPlan schema is a real contribution — typed, validated, composable.

**Key files**:
- `Digimon_for_KG_application/Core/AgentBrain/agent_brain.py` (1,540 lines) — PlanningAgent with plan generation, ReAct loop
- `Digimon_for_KG_application/Core/AgentSchema/plan.py` (131 lines) — ExecutionPlan, ExecutionStep, ToolCall, ToolInputSource
- `Digimon_for_KG_application/Core/AgentOrchestrator/` — 6 orchestrator variants

**Status**: DISCUSS — This is the most complete agent architecture. Main Digimons has simpler WorkflowAgent. Question: adopt this architecture, or treat as reference?

---

### A2. 6 Orchestrator Implementations (Digimon_for_KG_application)

**What**: Same interface, 6 strategies: base sequential, async streaming (v1 + v2), parallel (read-only parallelization), enhanced (advanced context), memory-enhanced (persistent context).

**Key files**:
- `Digimon_for_KG_application/Core/AgentOrchestrator/orchestrator.py` (25KB)
- `Digimon_for_KG_application/Core/AgentOrchestrator/async_streaming_orchestrator.py` (26KB)
- `Digimon_for_KG_application/Core/AgentOrchestrator/parallel_orchestrator.py` (9KB)
- `Digimon_for_KG_application/Core/AgentOrchestrator/enhanced_orchestrator.py` (16KB)
- `Digimon_for_KG_application/Core/AgentOrchestrator/memory_enhanced_orchestrator.py` (10KB)

**Status**: DISCUSS — Valuable patterns. Main Digimons only has simple orchestration. Could extract the parallel + memory-enhanced as reference implementations.

---

### A3. Dynamic Tool Registry with Capabilities (Digimon_for_KG_application)

**What**: `DynamicToolRegistry` with ToolCategory (READ_ONLY, WRITE, BUILD, TRANSFORM, ANALYZE) and ToolCapability (ENTITY_DISCOVERY, RELATIONSHIP_ANALYSIS, GRAPH_CONSTRUCTION, etc.) enums. Capability-based discovery, parallelizability detection, chain validation.

**Key files**:
- `Digimon_for_KG_application/Core/AgentTools/tool_registry.py` (708 lines)

**Status**: DISCUSS — 46 registered tools with metadata. Main Digimons has a simpler registry. This is the more mature design.

---

### A4. Contract-First Tool Architecture (digimon_core_sparse)

**What**: YAML specifications for all tools defining inputs, outputs, dependencies, quality metrics, error codes. JSON schema validation. Tools declare behavior at design time.

**Key files**:
- `archive/digimon_core_sparse/contracts/tools/` — 10 YAML tool contracts (T01-T85)
- `archive/digimon_core_sparse/contracts/schemas/tool_contract_schema.yaml` — Validation schema
- `archive/digimon_core_sparse/src/core/tool_contract.py` — KGASTool base class

**Status**: POINTER — Interesting design but never completed migration (4-week plan documented, not executed). The idea of formal tool contracts is worth noting but the implementation is partial.

---

### A5. 24 Composable Operators (Digimon_for_KG_application)

**What**: Modular operators in 6 categories (entity, relationship, chunk, subgraph, community, meta) that replace monolithic retrieval methods. Operators compose into pipelines via ExecutionPlan.

**Key files**:
- `Digimon_for_KG_application/Core/Operators/` — 24 operators

**Status**: POINTER — Tightly coupled to the KG_application architecture. Not easily extractable without the whole system.

---

## B. Theoretical Frameworks

### B1. Six-Level Theory Automation (digimon_core_sparse)

**What**: Framework for converting social science theories into executable code at 6 levels: formulas (implemented), algorithms, procedures, rules (OWL2), sequences (FSM), frameworks (classifiers).

**Why it matters**: This is the most ambitious theoretical contribution. Level 1 (formulas) works. Others are architecturally defined but not implemented.

**Key files**:
- `archive/digimon_core_sparse/docs/architecture/Thinking_out_loud/Architectural_Exploration/SIX_LEVEL_THEORY_AUTOMATION_ARCHITECTURE.md`
- `archive/digimon_core_sparse/docs/architecture/Thinking_out_loud/Implementation_Claims/THEORY_TO_CODE_WORKFLOW.md`

**Status**: EXTRACT — This is genuinely novel. The architecture doc should live in main Digimons as a design reference.

---

### B2. Theory Meta-Schema Evolution (digimon_core_sparse → theory-forge)

**What**: Theory representation schemas v9 → v13. Each version adds capabilities: v10 adds execution framework, v12 adds component categorization for 6-level architecture, v13 is the final comprehensive version.

**Key files**:
- `archive/digimon_core_sparse/config/schemas/theory_meta_schema_v9.json` through `v12.json` — historical evolution
- **theory-forge owns v13**: `/home/brian/projects/theory-forge/src/theory_forge/schemas/meta_schema_v13.json`
- Archive copies in `Digimons_docs/docs/schemas/` are redundant
- `archive/digimon_core_sparse/config/schemas/` — 11 example theory schemas (prospect theory, social identity, etc.)

**Status**: POINTER — theory-forge already owns v13. Archive copies are redundant. The 11 example theory schemas in core_sparse are valuable reference material but theory-forge has its own 13 bundled schemas.

---

### B3. IC-Informed Uncertainty Framework (digimon_core_sparse)

**What**: Intelligence Community uncertainty methods (ICD-203/206, Heuer's info paradox, CERQual) adapted for academic research. Root-sum-squares propagation. Probability bands instead of point estimates. Full audit trail.

**Key files**:
- `archive/digimon_core_sparse/docs/architecture/adrs/ADR-029-IC-Informed-Uncertainty-Framework/`
- `archive/digimon_core_sparse/docs/architecture/adrs/ADR-017-IC-Analytical-Techniques-Integration.md`
- `archive/digimon_core_sparse/src/core/confidence_scoring/` — cerqual_assessment.py, confidence_calculator.py, temporal_range_methods.py, combination_methods.py

**Status**: EXTRACT — Both the design docs (ADR-029, ADR-017) and the confidence_scoring implementation are unique and valuable.

---

### B4. Thinking Out Loud — Analysis Philosophy (digimon_core_sparse)

**What**: Philosophical explorations on what "analysis" means at different levels. Key question: "When we apply Prospect Theory to text, what are we actually analyzing — the text, the world, the effects, or the design?"

**Key files**:
- `archive/digimon_core_sparse/docs/architecture/Thinking_out_loud/Analysis_Philosophy/ANALYTIC_TIER_BOUNDARY_CONFUSION.md`
- `archive/digimon_core_sparse/docs/architecture/Thinking_out_loud/Analysis_Philosophy/ANALYTIC_TIER_MULTIPLE_MEANINGS.md`
- `archive/digimon_core_sparse/docs/architecture/Thinking_out_loud/Architectural_Exploration/TWO_STAGE_APPROACH_CRITIQUE.md`

**Status**: EXTRACT — These are genuine intellectual contributions that inform the system design. Should be preserved as design philosophy docs.

---

### B5. Master Concept Library with DOLCE Grounding (Digimons_clean_for_real)

**What**: YAML-based ontology library with 80+ entity types grounded in social science theories (Tajfel & Turner, Moscovici, Bandura). DOLCE-aligned with FOAF/SIOC/PROV extensions.

**Key files**:
- `archive/Digimons_clean_for_real/src/ontology_library/concepts/entities.yaml` — 80+ entity types
- `archive/Digimons_clean_for_real/src/ontology_library/concepts/connections.yaml`
- `archive/Digimons_clean_for_real/src/ontology_library/concepts/properties.yaml`
- `archive/Digimons_clean_for_real/src/ontology_library/concepts/modifiers.yaml`
- `archive/Digimons_clean_for_real/src/ontology_library/example_theory_schemas/social_identity_theory.yaml`

**Status**: DISCUSS — Main Digimons may already have this (it was in the codebase before cleanup). Need to check if main's `src/ontology_library/` has the same content.

---

## C. Working Demos & Evidence

### C1. Discourse Analysis Demos (Digimon_for_KG_application)

**What**: COVID conspiracy analysis with 5 interrogative questions (WHO, SAYS WHAT, TO WHOM, IN WHAT SETTING, WITH WHAT EFFECT). Policy discourse analysis. Uses DiscourseEnhancedPlanner + social media executor.

**Key files**:
- `Digimon_for_KG_application/scripts/demos/demo_discourse_analysis_final.py`
- `Digimon_for_KG_application/scripts/demos/demo_policy_discourse_analysis.py`
- `Digimon_for_KG_application/Data/Social_Discourse_Test/` — 10 actors, 20 posts

**Status**: POINTER — These work within KG_application's architecture. Value is as reference for what discourse analysis looks like in practice.

---

### C2. Ground Truth Paired Datasets (Digimons_minimal)

**What**: 15 documents in 3 variants each (clean, OCR-degraded, heavily-processed) for thesis validation. Plus 10 diverse test docs.

**Key files**:
- `archive/Digimons_minimal/tool_compatability/poc/vertical_slice/thesis_evidence/ground_truth_paired/`
- `archive/Digimons_minimal/tool_compatability/poc/vertical_slice/thesis_evidence/ground_truth_data/`

**Status**: DISCUSS — Main Digimons may already have copies in its own tool_compatability/poc/ directory.

---

### C3. 13 Architectural Investigation Documents (Digimons_minimal)

**What**: Reality audits documenting what works vs. what was claimed. Thesis requirements, architecture extraction, reconciliation plans.

**Key files**:
- `archive/Digimons_minimal/tool_compatability/poc/vertical_slice/THESIS_REQUIREMENTS.md`
- `archive/Digimons_minimal/tool_compatability/poc/vertical_slice/RECONCILIATION_PLAN.md`
- Plus 11 more investigation docs

**Status**: POINTER — Main Digimons has its own investigation/ directory with 20 similar files. These may be earlier versions.

---

## D. Documentation-Only Artifacts

### D1. Theory Meta-Schema v13 (Digimons_docs)

**What**: Final version of theory representation schema. Archive copy is redundant — theory-forge owns the canonical v13.

**Key file**: `archive/Digimons_docs/docs/schemas/theory_meta_schema_v13.json` (redundant copy)
**Canonical**: `/home/brian/projects/theory-forge/src/theory_forge/schemas/meta_schema_v13.json`

**Status**: POINTER — theory-forge already owns this. Archive copy can be ignored.

---

### D2. 5 Schema Paradigms (Digimons_docs)

**What**: Complete modeling in UML, RDF/OWL, ORM, TypeDB, and N-ary relations.

**Key file**: `archive/Digimons_docs/docs/architecture/data/SCHEMA_MANAGEMENT.md`

**Status**: POINTER — Reference material. Not actionable code.

---

### D3. Architecture Review 2025-08-08 (Digimons_docs)

**What**: 20 detailed investigation documents analyzing each system component independently.

**Key files**: `archive/Digimons_docs/docs/architecture/architecture_review_20250808/`

**Status**: POINTER — Historical. Main Digimons has its own later investigation/ directory.

---

### D4. 30 Architecture Decision Records (Digimons_docs)

**What**: ADR-001 through ADR-031 covering major design decisions.

**Key files**: `archive/Digimons_docs/docs/architecture/adrs/`

**Status**: DISCUSS — Main Digimons likely has copies. Need to check if any ADRs are missing from main.

---

## E. From digimons_old (Pre-KGAS, already in ARCHIVE_INDEX.md)

### E1. Sparse KG API (StructGPT)
**Path**: `archive/digimons_old/StructGPT/KG_sparse_api.py`
**Status**: POINTER

### E2. Graph Counselor — Reflexion Pattern (ACL 2025 paper, not our code)
**Path**: `archive/digimons_old/Graph-Counselor/`
**Paper**: Gao et al., arXiv:2506.03939 — "Adaptive Graph Exploration via Multi-Agent Synergy"
**Status**: REFERENCE — not our implementation, cloned research code

**What it does**: Three-agent system (Planning, Thought, Execution) with self-reflection on failure. Uses Reflexion strategy: if the answer is wrong, the agent generates a reflection ("what went wrong?") and retries with that reflection as added context. Actions: Retrieve, Neighbor, Feature, Degree, Finish.

**What's useful for us**: The reflexion-on-failure pattern is generic and could be bolted onto any retrieval method. It's ~20 lines on top of PlanningAgent: after `meta.generate_answer`, add a verification step ("does this answer the question?"), and if not, generate a reflection and re-run the pipeline with the reflection prepended to the query. This is independent of which method (basic_local, tog, etc.) is used.

**Not worth porting**: The implementation is messy research code hardcoded to specific model paths (Llama, Qwen, Gemma, etc.). The pattern itself is trivial to reimplement.

**Implementation sketch** (for future reference):
```
1. Run any method pipeline → get answer
2. LLM judge: "Given question Q and answer A, is this a complete answer?" → yes/no
3. If no: LLM reflect: "What went wrong? What information is missing?"
4. Prepend reflection to query, re-run pipeline (max N retries)
```

### E3. RetrieverFactory Pattern (GraphRAG_fresh) — SUPERSEDED
**Path**: `archive/digimons_old/GraphRAG_fresh/Core/Retriever/RetrieverFactory.py`
**Status**: DEAD — strictly less capable than OperatorRegistry

**What it was**: 52-line string-keyed dictionary (`{type: {method_name: func}}`) with decorator registration. No type safety, no I/O compatibility checking, no chain discovery.

**Why it's dead**: `Digimon_for_KG_application/Core/Operators/registry.py` (OperatorRegistry) is a strict superset — typed SlotKind I/O, `get_compatible_successors/predecessors`, `find_chains_to_goal` (BFS), `validate_connection`, CostTier metadata. Nothing to salvage.

### E4. N-ary Reification
**Path**: `archive/digimons_old/future_work_not_for_v1/n_ary_reification.py`
**Status**: POINTER

### E5. 121-Tool Taxonomy
**Path**: `archive/digimons_old/Digimons_2025.06161927/`
**Status**: POINTER

---

## Extraction Plan (Draft)

Files to copy into `Digimons/reference/` or appropriate location:

| Item | Source | Destination | Size |
|------|--------|-------------|------|
| B1: Six-Level Theory Automation | core_sparse Thinking_out_loud/ | `docs/reference/theory-automation/` | ~50KB |
| ~~B2: Theory Meta-Schema v13~~ | ~~Digimons_docs schemas/~~ | theory-forge already owns v13 | N/A |
| B2: Example theory schemas (11) | core_sparse config/schemas/ | `config/schemas/examples/` (or leave as pointer) | ~100KB |
| B3: IC Uncertainty ADRs | core_sparse adrs/ | `docs/architecture/adrs/` | ~50KB |
| B3: confidence_scoring module | core_sparse src/core/ | `src/core/confidence_scoring/` | ~200KB |
| B4: Analysis Philosophy docs | core_sparse Thinking_out_loud/ | `docs/reference/analysis-philosophy/` | ~30KB |

**Items needing discussion first (A1-A3, B5, C2, D4)** — these either overlap with main or require architectural decisions.

---

## Open Questions

1. **A1-A3**: Should main Digimons adopt KG_application's agent architecture (ExecutionPlan + orchestrators + registry), or keep its own simpler approach?
2. **B5**: Does main Digimons already have the MCL YAML files?
3. **C2**: Does main Digimons already have the ground truth paired datasets?
4. **D4**: Which ADRs are missing from main's docs/architecture/adrs/?
