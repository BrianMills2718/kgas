# Tool Compatibility Files Collection

## Main Directory Files
Files moved from experiments/tool_compatability/take4:
- `take4_CLAUDE.md` - Simple explicit contracts solution
- `the_real_problem.md` - Critical analysis of actual issues
- `unresolved_issues.md` - What's still broken

Files already here:
- `TOOL_REALITY_CHECK.md` - Initial analysis
- `ACCURATE_TOOL_INVENTORY.md` - Detailed inventory from 32 tool calls
- `COMPLETE_TOOL_FILE_LIST.md` - Comprehensive file list

## useful_copies/ Subdirectory
Copies of files that remain in their original locations:

### CLAUDE.md Documentation (5 files)
- `tools_CLAUDE.md` - From /src/tools/CLAUDE.md (claims 121 tools)
- `phase1_CLAUDE.md` - From /src/tools/phase1/CLAUDE.md
- `phase2_CLAUDE.md` - From /src/tools/phase2/CLAUDE.md
- `phase3_CLAUDE.md` - From /src/tools/phase3/CLAUDE.md
- `core_CLAUDE.md` - From /src/core/CLAUDE.md
- `root_CLAUDE.md` - From /CLAUDE.md (contract-first migration)

### Architecture & Investigation (1 file)
- `tool_compatibility_investigation.md` - From /docs/architecture/architecture_review_20250808/

### Evidence Files (2 files)
- `Evidence_Phase_Tool_Contract_Standardization.md` - From /evidence/completed/
- `Evidence_Task1_Phase_C_Wrappers.md` - From /evidence/current/

### Registry & Status (2 files)
- `tool_registry.json` - From /data/ (shows 123 tools, 12 implemented)
- `tool-implementation-status.md` - From /docs/roadmap/initiatives/tooling/

### Contract & Protocol Code (3 files)
- `tool_contract.py` - From /src/core/
- `tool_protocol.py` - From /src/core/
- `tool_adapter.py` - From /src/core/

### Example Problem Files (3 files)
- `t23c_llm_entity_extractor.py` - Alias example from /src/tools/phase1/
- `t31_entity_builder.py` - Another alias from /src/tools/phase1/
- `t31_entity_builder_unified.py` - Actual implementation from /src/tools/phase1/

## Total: 25 files collected

## Next Steps

Based on these files, we need to create:

1. **CONSOLIDATION_PLAN.md** - Step-by-step plan to fix the 38 tools
2. **TOOL_CONTRACTS.md** - Document actual inputs/outputs for each tool
3. **REFACTORING_STRATEGY.md** - How to merge T31/T34 into T23C, etc.
4. **PIPELINE_DEFINITIONS.md** - Define the 5-10 standard pipelines

## Key Insights from Files

### The Problems (from the_real_problem.md)
- We don't know what tools input/output without reading code
- Tools are factored wrong (T31/T34 should be in T23C)
- No standardization of field names
- Too many duplicate versions

### The Claims vs Reality
- Documentation claims: 121 tools
- Registry shows: 123 tools with 12 implemented (9.8%)
- We actually found: 38 unique tool IDs with implementations
- Most have 3-5 versions (standalone, unified, neo4j, etc.)

### The Solution Direction (from take4_CLAUDE.md)
- Explicit contracts for each tool
- Simple data dictionary passing
- No complex DAG logic
- Linear execution
- Type safety and validation