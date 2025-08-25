# Tool Compatibility Folder Review and Cleanup Plan

## Current Files Assessment

### ✅ **KEEP - Core Strategy Documents** (Still Relevant)

#### ORM Implementation Documents
- `thinking_through_orm.md` - **CORE**: Our ORM approach foundation
- `methodical_implementation_plan.md` - **CORE**: 28-day implementation plan
- `tool_disposition_plan.md` - **CORE**: Which tools become which operators
- `kgas_digimon_structgpt_alignment.md` - **CORE**: How we compare to reference systems

#### Updated Overview
- `tool_refactoring_overview.md` - **KEEP**: Updated with ORM strategy

### ⚠️ **UPDATE - Inventory Documents** (Need ORM Context)

- `ACCURATE_TOOL_INVENTORY.md` - **UPDATE**: Add column for "Target Operator"
- `COMPLETE_TOOL_FILE_LIST.md` - **UPDATE**: Mark which files will be wrapped vs deprecated
- `FILES_COLLECTED.md` - **UPDATE**: Note which are still relevant for ORM

### 📝 **CONSOLIDATE - Problem Analysis** (Merge into One)

These all describe the same problems from different angles:
- `TOOL_REALITY_CHECK.md` - Initial problem discovery
- `the_real_problem.md` - Deeper analysis
- `unresolved_issues.md` - List of specific issues
- `take4_CLAUDE.md` - Another iteration of the problem

**Action**: Merge into `PROBLEM_ANALYSIS_ARCHIVE.md` with header noting "Pre-ORM Analysis"

### 📁 **REVIEW - Useful Copies Subfolder**

#### Keep for Reference
- `tool_contract.py` - Needed for ORM wrapper implementation
- `tool_protocol.py` - Need to understand what to replace
- `tool_adapter.py` - Shows current adaptation approach
- `tool_registry.json` - Reference for all planned tools

#### Keep as Examples
- `t23c_llm_entity_extractor.py` - Example tool to wrap
- `t31_entity_builder.py` - Tool that gets merged into T23
- `t31_entity_builder_unified.py` - Another version to consider

#### Archive as Historical
- All CLAUDE.md files - Historical documentation
- All Evidence files - Past implementation attempts
- `tool-implementation-status.md` - Outdated status
- `tool_compatibility_investigation.md` - Superseded by ORM approach

## Proposed New Structure

```
/tool_compatability/
├── 📂 active/                      # Current ORM implementation
│   ├── thinking_through_orm.md
│   ├── methodical_implementation_plan.md
│   ├── tool_disposition_plan.md
│   ├── kgas_digimon_structgpt_alignment.md
│   ├── tool_refactoring_overview.md
│   └── UPDATED_TOOL_INVENTORY.md   # With ORM mappings
│
├── 📂 reference/                    # Code we need to reference
│   ├── tool_contract.py
│   ├── tool_protocol.py
│   ├── tool_adapter.py
│   ├── tool_registry.json
│   └── example_tools/
│       ├── t23c_llm_entity_extractor.py
│       ├── t31_entity_builder.py
│       └── t31_entity_builder_unified.py
│
└── 📂 archive/                      # Historical analysis
    ├── PROBLEM_ANALYSIS_CONSOLIDATED.md  # Merged problems
    ├── pre_orm_analysis/
    │   ├── TOOL_REALITY_CHECK.md
    │   ├── the_real_problem.md
    │   ├── unresolved_issues.md
    │   └── take4_CLAUDE.md
    └── old_documentation/
        ├── All CLAUDE.md files
        ├── All Evidence files
        └── old status files
```

## Documents to Create/Update

### 1. `UPDATED_TOOL_INVENTORY.md`
Add columns:
- Target Operator (which ORM operator this becomes)
- Phase (1, 2, 3, or Deferred)
- Wrapper Status (Not Started, In Progress, Complete)

### 2. `PROBLEM_ANALYSIS_CONSOLIDATED.md`
Merge all problem documents with structure:
```markdown
# Tool Compatibility Problem Analysis (Pre-ORM)
## Summary of Issues Found
## Why Field Matching Failed  
## Why Tool Boundaries Were Wrong
## How ORM Solves These Issues
```

### 3. `ORM_IMPLEMENTATION_STATUS.md`
New tracking document:
```markdown
# ORM Implementation Status

## Phase 0: Proof of Concept
- [ ] T03 → T15A → T23C test chain
- [ ] ORM wrapper prototype
- [ ] Performance benchmarks

## Phase 1: Core Operators (Week 1)
- [ ] T01_UniversalLoader
- [ ] T23_GraphExtractor
[etc...]
```

## Immediate Actions

1. **Create folder structure**:
```bash
mkdir -p tool_compatability/active
mkdir -p tool_compatability/reference/example_tools
mkdir -p tool_compatability/archive/pre_orm_analysis
mkdir -p tool_compatability/archive/old_documentation
```

2. **Move files to appropriate folders**

3. **Create the three new documents**

4. **Add README.md** to tool_compatability/:
```markdown
# Tool Compatibility - ORM Implementation

## Current Focus
Implementing Object Role Modeling (ORM) for semantic tool compatibility.
See `active/` folder for current work.

## Folder Structure
- `active/` - Current ORM implementation documents
- `reference/` - Code and specs we reference
- `archive/` - Historical analysis and old approaches

## Start Here
1. Read `active/thinking_through_orm.md` for concept
2. Follow `active/methodical_implementation_plan.md` for execution
3. Check `active/tool_disposition_plan.md` for tool mappings
```

## What Gets Deleted?

Nothing gets deleted - everything moves to `archive/` with clear labels. This preserves history while keeping workspace clean.

## Final Check

After reorganization, the `active/` folder should contain only:
- 5 core ORM documents
- 1 updated inventory
- 1 new status tracker

Everything else is reference or archive.