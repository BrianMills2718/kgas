# Theory Architecture Documentation

This directory contains the core architectural specifications for KGAS theory processing system.

## 📋 Navigation Guide

### **Core Architecture Design**
- **[`two-layer-theory-architecture.md`](two-layer-theory-architecture.md)** - Fundamental two-layer design specification (Layer 1 vs Layer 2)
- **[`theory-extraction-integration.md`](theory-extraction-integration.md)** - Integration architecture connecting experimental system to main KGAS
- **[`theory-extraction-implementation.md`](theory-extraction-implementation.md)** - Internal processing architecture with six-level categorization

### **Service Architecture**
- **[`theory-registry-implementation.md`](theory-registry-implementation.md)** - Theory management service with validation and MCL mapping
- **[`theory-repository-abstraction.md`](theory-repository-abstraction.md)** - Storage abstraction interface for future version control

### **Design Evolution**
- **[`theory-implementation-evolution.md`](theory-implementation-evolution.md)** - Historical development of implementation approaches

---

## 🔗 Related Documentation

### **Implementation Status & Planning**
For current implementation progress and integration plans, see:
- **[`/docs/roadmap/theory/`](../../roadmap/theory/)** - Current status and integration planning

### **Schema Specifications**
For theory schema documentation, see:
- **[`/docs/architecture/data/theory-meta-schema-v10.md`](../data/theory-meta-schema-v10.md)** - Current meta-schema specification
- **[`/docs/architecture/data/mcl-theory-schemas-examples.md`](../data/mcl-theory-schemas-examples.md)** - Schema examples

### **Examples & Case Studies**
For concrete examples, see:
- **[`/docs/architecture/Thinking_out_loud/Implementation_Claims/social_identity_theory_example_with_entity_resolution.md`](../Thinking_out_loud/Implementation_Claims/social_identity_theory_example_with_entity_resolution.md)** - Complete Social Identity Theory case study
- **[`/docs/architecture/Thinking_out_loud/framework_exploration/multi_theory_integration_insights.md`](../Thinking_out_loud/framework_exploration/multi_theory_integration_insights.md)** - Multi-theory integration insights

### **Success Criteria**
- **[`/docs/architecture/tentative_validation/success_criteria_for_theory_automation.md`](../tentative_validation/success_criteria_for_theory_automation.md)** - Theory automation validation criteria

---

## 🎯 Quick Reference

### **New to Theory Architecture?**
Start with **`two-layer-theory-architecture.md`** to understand the fundamental design principles, then review **`theory-extraction-integration.md`** for implementation approach.

### **Implementing Theory Integration?**  
Focus on **`theory-extraction-integration.md`** for architecture patterns, then check **`/docs/roadmap/theory/`** for current implementation plans.

### **Working on Theory Services?**
Review **`theory-registry-implementation.md`** for service design and **`theory-repository-abstraction.md`** for storage interface.

---

## 📊 Architecture Overview

The KGAS theory system uses a **two-layer architecture** that separates:

1. **Layer 1: Theory Structure Extraction** - Extract complete theoretical structure independent of analysis questions
2. **Layer 2: Question-Driven Analysis** - Apply extracted structure to specific research questions

This separation enables:
- **Reusability**: One theory extraction serves multiple analytical questions
- **Flexibility**: Theories can be applied to diverse research contexts  
- **Quality**: Comprehensive theoretical structure capture without question bias

The experimental system (`/experiments/lit_review`) is fully functional with 100% validation success across 10 theories and 7 academic domains. Integration with main KGAS architecture is the current development focus.