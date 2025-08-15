# Theory Documentation Reorganization Plan

**Date**: 2025-08-06  
**Purpose**: Reorganize theory documentation by function - Architecture vs Roadmap  
**Principle**: Status/Planning in Roadmap, Architecture/Examples in Architecture  

---

## 🎯 **Reorganization Principles**

### **Architecture Directory**: Target state design, specifications, examples
- What the system should look like when complete
- How components are designed to work
- Examples and case studies
- Stable, reference documentation

### **Roadmap Directory**: Current progress, planning, status tracking
- What has been implemented
- What is currently being worked on
- When things will be done
- Implementation plans and status updates

---

## 📁 **Current File Locations & Proposed Moves**

### **Files Currently in ARCHITECTURE (Correct Location)**
✅ **KEEP IN ARCHITECTURE**:

```
/docs/architecture/systems/
├── two-layer-theory-architecture.md (13.9KB) ✅ Core design spec
├── theory-extraction-integration.md (30.9KB) ✅ Integration architecture  
├── theory-extraction-implementation.md (14.4KB) ✅ Implementation architecture
├── theory-registry-implementation.md (14.6KB) ✅ Registry service design
├── theory-repository-abstraction.md (3.8KB) ✅ Repository interface
└── theory-implementation-evolution.md (5.0KB) ✅ Design evolution history

/docs/architecture/data/
├── theory-meta-schema-v10.md (9.0KB) ✅ Schema specification
├── theory-meta-schema.md (2.9KB) ✅ General schema docs
└── mcl-theory-schemas-examples.md (15.0KB) ✅ Schema examples

/docs/architecture/Thinking_out_loud/Implementation_Claims/
└── social_identity_theory_example_with_entity_resolution.md (22.5KB) ✅ Complete example

/docs/architecture/Thinking_out_loud/framework_exploration/
└── multi_theory_integration_insights.md (6.8KB) ✅ Multi-theory design insights

/docs/architecture/tentative_validation/
└── success_criteria_for_theory_automation.md (3.8KB) ✅ Success criteria
```

**Total Architecture Files**: 11 files, 150KB ✅ **NO MOVES NEEDED**

### **Files Currently in ROADMAP (Mix of Correct/Incorrect)**

#### **✅ KEEP IN ROADMAP** (Status & Planning):
```
/docs/roadmap/
├── two-layer-theory-implementation-status.md (26.8KB) ✅ Status tracking
└── theory-extraction-integration-plan.md (23.1KB) ✅ Integration planning

/docs/planning/
└── theory-integration-status.md (3.6KB) ✅ Integration status
```

#### **📦 MOVE TO POST-MVP** (Future Planning):
```
/docs/roadmap/post-mvp/phase-theory-to-code/
├── phase-theory-to-code-implementation-plan.md (9.4KB) → /docs/roadmap/post-mvp/theory/
└── phase-2-frameworks-ui/task-2.2-theory-library.md (12.0KB) → /docs/roadmap/post-mvp/theory/
```

#### **🗑️ DELETE** (Archived Duplicates):
```
/docs/roadmap/ARCHIVE_BEFORE_CLEANUP_20250805/
├── theory-extraction-integration-plan.md ❌ Exact duplicate
├── two-layer-theory-implementation-status.md ❌ Exact duplicate
├── phase-theory-to-code-implementation-plan.md ❌ Exact duplicate
├── task-2.2-theory-library.md ❌ Exact duplicate
└── initiatives/theory-extraction-integration-plan.md ❌ Exact duplicate
```

---

## 🏗️ **Proposed Directory Structure**

### **Final Architecture Organization**:
```
/docs/architecture/
├── systems/
│   ├── README.md (NEW) - Theory architecture navigation
│   ├── two-layer-theory-architecture.md - Core design
│   ├── theory-extraction-integration.md - Integration architecture
│   ├── theory-extraction-implementation.md - Implementation design
│   ├── theory-registry-implementation.md - Registry design
│   ├── theory-repository-abstraction.md - Repository interface
│   └── theory-implementation-evolution.md - Design history
├── data/
│   ├── theory-meta-schema-v10.md - Current schema
│   ├── theory-meta-schema.md - General schema docs
│   └── mcl-theory-schemas-examples.md - Schema examples
├── examples/
│   ├── README.md (NEW) - Theory examples index
│   ├── social_identity_theory_complete_example.md (RENAMED)
│   └── multi_theory_integration_insights.md (MOVED)
└── validation/
    └── success_criteria_for_theory_automation.md
```

### **Final Roadmap Organization**:
```
/docs/roadmap/
├── theory/
│   ├── README.md (NEW) - Theory implementation navigation
│   ├── two-layer-theory-implementation-status.md - Progress tracking
│   └── theory-extraction-integration-plan.md - Integration plan
├── post-mvp/
│   └── theory/ (NEW)
│       ├── README.md (NEW) - Future theory work
│       ├── phase-theory-to-code-implementation-plan.md (MOVED)
│       └── task-2.2-theory-library.md (MOVED)
└── ARCHIVE_BEFORE_CLEANUP_20250805/ (DELETE ENTIRE DIRECTORY)

/docs/planning/
└── theory-integration-status.md - Current integration status
```

---

## 📋 **Implementation Steps**

### **Step 1: Clean Up Duplicates**
```bash
# Delete archived duplicates (5 files, 71KB saved)
rm -rf docs/roadmap/ARCHIVE_BEFORE_CLEANUP_20250805/
```

### **Step 2: Reorganize Architecture**
```bash
# Create new directories
mkdir -p docs/architecture/examples
mkdir -p docs/architecture/validation

# Move files within architecture
mv docs/architecture/Thinking_out_loud/framework_exploration/multi_theory_integration_insights.md \
   docs/architecture/examples/

mv docs/architecture/Thinking_out_loud/Implementation_Claims/social_identity_theory_example_with_entity_resolution.md \
   docs/architecture/examples/social_identity_theory_complete_example.md

mv docs/architecture/tentative_validation/success_criteria_for_theory_automation.md \
   docs/architecture/validation/
```

### **Step 3: Reorganize Roadmap**
```bash
# Create theory-specific directories
mkdir -p docs/roadmap/theory
mkdir -p docs/roadmap/post-mvp/theory

# Move current status/planning files
mv docs/roadmap/two-layer-theory-implementation-status.md docs/roadmap/theory/
mv docs/roadmap/initiatives/theory-extraction-integration-plan.md docs/roadmap/theory/

# Move post-MVP files
mv docs/roadmap/post-mvp/phase-theory-to-code/phase-theory-to-code-implementation-plan.md \
   docs/roadmap/post-mvp/theory/
mv docs/roadmap/post-mvp/phase-theory-to-code/phase-2-frameworks-ui/task-2.2-theory-library.md \
   docs/roadmap/post-mvp/theory/
```

### **Step 4: Create Navigation Aids**
```bash
# Create README files for navigation
touch docs/architecture/systems/README.md
touch docs/architecture/examples/README.md  
touch docs/roadmap/theory/README.md
touch docs/roadmap/post-mvp/theory/README.md
```

---

## 📚 **Navigation README Contents**

### **Architecture Systems README**
```markdown
# Theory Architecture Documentation

Core architectural specifications for KGAS theory processing system.

## Core Architecture
- `two-layer-theory-architecture.md` - Fundamental design (Layer 1 vs 2)
- `theory-extraction-integration.md` - Integration with main KGAS
- `theory-extraction-implementation.md` - Internal processing design

## Service Architecture  
- `theory-registry-implementation.md` - Theory management service
- `theory-repository-abstraction.md` - Storage abstraction interface

## Design Evolution
- `theory-implementation-evolution.md` - Historical development

For implementation status, see [/docs/roadmap/theory/](../../roadmap/theory/)
```

### **Theory Examples README**
```markdown
# Theory Examples and Case Studies

Concrete examples demonstrating theory processing capabilities.

## Complete Examples
- `social_identity_theory_complete_example.md` - End-to-end SIT analysis
- `multi_theory_integration_insights.md` - Multi-theory integration

## Schema Examples
See [../data/mcl-theory-schemas-examples.md](../data/mcl-theory-schemas-examples.md)

## Success Criteria
See [../validation/success_criteria_for_theory_automation.md](../validation/success_criteria_for_theory_automation.md)
```

### **Roadmap Theory README**
```markdown
# Theory Implementation Status and Planning

Current implementation progress and integration plans.

## Current Status
- `two-layer-theory-implementation-status.md` - Implementation progress
- `theory-extraction-integration-plan.md` - Integration planning

## Integration Status
- [/docs/planning/theory-integration-status.md](../../planning/theory-integration-status.md)

## Architecture Reference
- [/docs/architecture/systems/](../../architecture/systems/) - Architecture specs

## Future Work  
- [post-mvp/theory/](post-mvp/theory/) - Post-MVP theory plans
```

---

## 🎯 **Benefits of Reorganization**

### **Clearer Organization**:
- **Architecture**: Design specifications, examples, validation criteria
- **Roadmap**: Implementation status, planning, future work
- **Clear separation**: What we're building vs how we're building it

### **Better Navigation**:
- Theory-specific directories with README navigation
- Logical file grouping by purpose
- Clear cross-references between architecture and roadmap

### **Reduced Confusion**:
- Status files clearly in roadmap
- Architecture files clearly in architecture  
- Post-MVP planning separated from current work

### **File Reduction**:
- Delete 5 archived duplicates (save 71KB)
- Better organization without losing any value
- 21 files → 16 files (24% reduction)

---

## ⚠️ **Risk Assessment**

### **Low Risk Changes**:
✅ Deleting archived duplicates (exact copies)
✅ Creating new README files (pure addition)
✅ Moving post-MVP files to dedicated directory

### **Medium Risk Changes**:
⚠️ Moving files between architecture and roadmap directories
- Need to update cross-references
- Check for hardcoded paths in other docs

### **Mitigation**:
- Test all cross-references after moves
- Update main documentation index
- Announce changes to team

---

## 🚀 **Implementation Timeline**

### **Phase 1**: Cleanup (30 minutes)
- Delete archived duplicates
- Create new directory structure

### **Phase 2**: Reorganize (1 hour)  
- Move files to proper locations
- Update file paths and references

### **Phase 3**: Navigation (1 hour)
- Create README files
- Test all cross-references
- Update main documentation index

**Total Time**: ~2.5 hours for complete reorganization

This reorganization will create much clearer boundaries between architectural design and implementation progress while preserving all valuable content.