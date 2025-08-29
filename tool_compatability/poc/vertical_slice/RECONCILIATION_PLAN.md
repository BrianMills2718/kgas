# KGAS Documentation Reconciliation Plan
*Created: 2025-08-29*
*Based on: DOCUMENTATION_AUDIT.md findings*

## 🎯 Goal
Create a single, coherent codebase with accurate documentation that supports the thesis requirements.

## 📊 Current State Summary
- **7 CLAUDE.md files** with conflicting instructions
- **3+ parallel implementations** (src/, experiments/, tool_compatability/)
- **10+ experiments** with unclear relevance
- **Scattered tests** in root and tests/
- **Enterprise features** mixed with academic tool claims

## ✅ What to Keep (Core Value)

### 1. Vertical Slice Approach
**Location**: `/tool_compatability/poc/vertical_slice/`
**Why Keep**: 
- Clean, working implementation
- Proves core concepts (tool chaining, adapters)
- Foundation for thesis requirements
**Action**: Make this the PRIMARY codebase

### 2. Framework Core
**Files**:
- `framework/clean_framework.py` - Tool orchestration
- `services/vector_service.py` - Working service
- `services/table_service.py` - Working service
- Adapter pattern (vector_tool.py, table_tool.py)
**Action**: Continue building on these

### 3. Thesis Evidence
**Location**: `/thesis_evidence/`
**Why Keep**: Ground truth data, metrics collection
**Action**: Enhance with real measurements

### 4. MCP Integration
**File**: `kgas_simple_mcp_server.py`
**Why Keep**: Clean MCP implementation
**Action**: Use simple version, archive complex one

## 🗑️ What to Archive (No Current Value)

### 1. Old CLAUDE Files
**Files**: CLAUDE_FINAL.md, CLAUDE_TRULY_FINAL.md, etc.
**Action**: Move to `/archive/claude_history/`
**Keep Only**: CLAUDE.md (current instructions)

### 2. Enterprise Features
**Directories**: k8s/, docker/
**Files**: sla_config.json, main.py (FastAPI server)
**Action**: Move to `/archive/enterprise_features/`
**Reason**: Not needed for thesis

### 3. Abandoned Experiments
**Review Each**: `/experiments/*/`
**Keep**: Only if directly supports thesis
**Archive**: Everything else

### 4. Duplicate Test Files
**Root Tests**: test_*.py files
**Action**: Move to `/tests/` or `/archive/`

## 🔧 What to Fix (Needs Work)

### 1. Uncertainty Propagation
**Current**: Hardcoded to 0.0
**Needed**: Real uncertainty calculation
**Priority**: HIGH - Core thesis requirement

### 2. Provenance Tracking
**Current**: Code exists, not verified
**Needed**: Verify Neo4j tracking works
**Priority**: HIGH - Core thesis requirement

### 3. Reasoning Traces
**Current**: Template strings
**Needed**: Meaningful explanations
**Priority**: MEDIUM - Important for explainability

### 4. Tool Registry
**Current**: Multiple competing systems
**Needed**: Single registry in vertical_slice
**Priority**: MEDIUM

## 📝 Documentation Strategy

### 1. Create Ground Truth Files
```
/docs/current_state/
├── WHAT_WORKS.md          # Honest assessment
├── ARCHITECTURE_ACTUAL.md  # Real architecture
├── TOOL_INVENTORY.md       # Actual working tools
└── TEST_COVERAGE.md        # What's actually tested
```

### 2. Update Key Files
- **README.md** - Reflect actual state
- **CLAUDE.md** - Current work instructions only
- **ROADMAP_OVERVIEW.md** - Reset to reality

### 3. Archive Historical Docs
```
/archive/historical_docs/
├── old_roadmaps/
├── old_architectures/
└── abandoned_plans/
```

## 🚀 Implementation Steps

### Phase 1: Clean House (1 day)
1. Create archive directories
2. Move old CLAUDE files
3. Move enterprise features
4. Consolidate test files
5. Archive abandoned experiments

### Phase 2: Document Reality (1 day)
1. Write WHAT_WORKS.md
2. Document actual architecture
3. Create honest tool inventory
4. Map test coverage

### Phase 3: Fix Core Issues (3-5 days)
1. Implement real uncertainty
2. Verify provenance
3. Add reasoning traces
4. Test everything

### Phase 4: Build Forward (Ongoing)
1. Add graph tools
2. Add CSV ingestion
3. Build goal evaluator
4. Create dynamic chains

## ⚠️ Critical Decisions Needed

### 1. Primary Codebase
**Recommendation**: Use `/tool_compatability/poc/vertical_slice/` as main
**Alternative**: Try to salvage `/src/`
**Decision**: _______________

### 2. Test Strategy
**Recommendation**: All tests in `/tests/`, organized by component
**Alternative**: Keep integration tests separate
**Decision**: _______________

### 3. Documentation Home
**Recommendation**: `/docs/current_state/` for reality, `/docs/architecture/` for goals
**Alternative**: Complete rewrite
**Decision**: _______________

### 4. Tool Numbering
**Recommendation**: Abandon T01-T91 numbering, use descriptive names
**Alternative**: Maintain numbering for continuity
**Decision**: _______________

## 📋 Success Criteria

### Short Term (1 week)
- [ ] One CLAUDE.md file
- [ ] Clear directory structure
- [ ] Working tests in one location
- [ ] Accurate README.md

### Medium Term (2 weeks)
- [ ] Real uncertainty propagation
- [ ] Verified provenance
- [ ] Graph extraction tool
- [ ] Updated roadmap

### Long Term (1 month)
- [ ] Dynamic tool chains
- [ ] Multi-modal processing
- [ ] Goal evaluation
- [ ] Thesis evidence collection

## 🔴 Risks

1. **Time Sink**: Could spend weeks just organizing
   - **Mitigation**: Timebox to 2 days max
   
2. **Breaking Changes**: Might break working code
   - **Mitigation**: Test everything before moving
   
3. **Lost Work**: Might archive something important
   - **Mitigation**: Archive, don't delete

4. **Scope Creep**: Trying to fix everything
   - **Mitigation**: Focus on thesis requirements only

## 💡 Final Recommendation

**RADICAL SIMPLIFICATION**:
1. Make `/tool_compatability/poc/vertical_slice/` the entire system
2. Archive everything else
3. Build only what thesis requires
4. Document only what exists
5. Test only what matters

This approach:
- Reduces complexity by 90%
- Focuses on thesis goals
- Eliminates confusion
- Enables rapid progress

---

**Next Step**: Review and approve this plan, then execute Phase 1 immediately.