# Architecture Decision Records (ADRs)

This directory contains all Architecture Decision Records for the KGAS system, documenting key architectural choices and their rationale.

## Quick Navigation by Theme

### 🔧 Tool & Interface Architecture
- [ADR-001: Phase Interface Design](ADR-001-Phase-Interface-Design.md) - Tool interface standardization
- [ADR-028: Tool Interface Layer Architecture](ADR-028-Tool-Interface-Layer-Architecture.md) - Interface layer design

### 💾 Data & Storage Architecture  
- [ADR-003: Vector Store Consolidation](ADR-003-Vector-Store-Consolidation.md) - Vector storage strategy
- [ADR-009: Bi-Store Database Strategy](ADR-009-Bi-Store-Database-Strategy.md) - Dual database approach
- [ADR-030: PostgreSQL Migration Strategy](ADR-030-PostgreSQL-Migration-Strategy.md) - Database migration

### 🔬 Analysis & Processing Architecture
- [ADR-006: Cross-Modal Analysis](ADR-006-cross-modal-analysis.md) - Cross-modal analysis design
- [ADR-007: Uncertainty Metrics](ADR-007-uncertainty-metrics.md) - Uncertainty quantification
- [ADR-010: Quality System Design](ADR-010-Quality-System-Design.md) - Quality assessment system
- [ADR-015: Cross-Modal Orchestration](ADR-015-Cross-Modal-Orchestration.md) - Orchestration patterns
- [ADR-018: Analysis Version Control](ADR-018-Analysis-Version-Control.md) - Analysis versioning
- [ADR-021: Statistical Analysis Integration](ADR-021-Statistical-Analysis-Integration.md) - Statistical capabilities
- [ADR-025: Entity Resolution Architecture](ADR-025-Entity-Resolution-Architecture.md) - Entity resolution
- [ADR-026: Cross-Modal REST API](ADR-026-Cross-Modal-REST-API.md) - API design
- [ADR-027: Analytical Purpose Clarification](ADR-027-Analytical-Purpose-Clarification.md) - Analysis clarity

### 🔗 Integration & Protocol Architecture
- [ADR-013: MCP Protocol Integration](ADR-013-MCP-Protocol-Integration.md) - MCP integration strategy
- [ADR-017: IC Analytical Techniques Integration](ADR-017-IC-Analytical-Techniques-Integration.md) - IC techniques
- [ADR-020: Agent-Based Modeling Integration](ADR-020-Agent-Based-Modeling-Integration.md) - ABM integration
- [ADR-029: IC-Informed Uncertainty Framework](ADR-029-IC-Informed-Uncertainty-Framework/) - Uncertainty framework
- [ADR-031: MCP Tool Exposure Strategy](ADR-031-MCP-Tool-Exposure-Strategy.md) - Tool exposure

### 🎓 Research & System Architecture
- [ADR-002: Pipeline Orchestrator Architecture](ADR-002-Pipeline-Orchestrator-Architecture.md) - Pipeline design
- [ADR-004: Normative Confidence Score Ontology](ADR-004-Normative-Confidence-Score-Ontology.md) - Confidence scoring
- [ADR-005: Buy vs Build Strategy](ADR-005-buy-vs-build-strategy.md) - Component strategy
- [ADR-005: Fail-Fast Architecture Strategic Decisions](ADR-005-Fail-Fast-Architecture-Strategic-Decisions.md) - Fail-fast design
- [ADR-008: Core Service Architecture](ADR-008-Core-Service-Architecture.md) - Core services
- [ADR-011: Academic Research Focus](ADR-011-Academic-Research-Focus.md) - Research orientation
- [ADR-012: Single Node Design](ADR-012-Single-Node-Design.md) - Deployment architecture
- [ADR-014: Error Handling Strategy](ADR-014-Error-Handling-Strategy.md) - Error management
- [ADR-016: Programmatic Dependency Analysis](ADR-016-Programmatic-Dependency-Analysis.md) - Dependency analysis
- [ADR-016: System Optimization Strategy](ADR-016-System-Optimization-Strategy.md) - Optimization approach
- [ADR-017: Structured Output Migration](ADR-017-Structured-Output-Migration.md) - Output migration
- [ADR-019: Research Assistant Personas](ADR-019-Research-Assistant-Personas.md) - User personas
- [ADR-022: Theory Selection Architecture](ADR-022-Theory-Selection-Architecture.md) - Theory selection
- [ADR-023: Comprehensive Schema Modeling Ecosystem](ADR-023-Comprehensive-Schema-Modeling-Ecosystem.md) - Schema ecosystem
- [ADR-024: Internal Tool Ecosystem Priority](ADR-024-Internal-Tool-Ecosystem-Priority.md) - Tool priorities

## Decision Impact Classification

### 🔴 Foundation Decisions (System-Wide Impact)
Critical decisions that affect the entire system architecture:
- **ADR-001**: Tool Interface Design (affects all tools)
- **ADR-003**: Vector Store Strategy (affects data architecture) 
- **ADR-009**: Bi-Store Database Strategy (affects all data operations)
- **ADR-012**: Single Node Design (affects deployment)

### 🟠 Core Architecture Decisions (Major Component Impact)
Decisions that affect major system components:
- **ADR-008**: Core Service Architecture
- **ADR-010**: Quality System Design  
- **ADR-015**: Cross-Modal Orchestration
- **ADR-025**: Entity Resolution Architecture

### 🟡 Enhancement Decisions (Specific Capability Impact)
Decisions that add specific capabilities or integrations:
- **ADR-013**: MCP Protocol Integration
- **ADR-020**: Agent-Based Modeling Integration
- **ADR-021**: Statistical Analysis Integration
- **ADR-029**: IC-Informed Uncertainty Framework

### 🟢 Research & Quality Decisions (Workflow Impact)
Decisions that affect research workflows and quality:
- **ADR-011**: Academic Research Focus
- **ADR-017**: IC Analytical Techniques Integration  
- **ADR-018**: Analysis Version Control
- **ADR-019**: Research Assistant Personas
- **ADR-027**: Analytical Purpose Clarification

## Chronological Index

All ADRs in numerical order:
- ADR-001 through ADR-031+ (see individual files)

## Related Documentation

- [Architecture Overview](../ARCHITECTURE_OVERVIEW.md) - System architecture overview
- [Specifications](../specifications/) - Detailed specifications
- [Systems](../systems/) - System component documentation