# KGAS Implementation Guide - Optimized

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only
- **FAIL-FAST**: Surface errors immediately
- **EVIDENCE-BASED**: Document in evidence/ directory
- **TEST FIRST**: Write tests before implementation

---

## 2. CURRENT SPRINT (2025-08-28)

### 🎯 Today's Focus: Service & Tool Integration
**Time Estimate**: 45-60 minutes
**Guide**: `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`
**Corrections**: Apply `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_CORRECTIONS.md` first

### Implementation Checklist
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
```

- [ ] Apply corrections from CORRECTIONS.md (5 min)
- [ ] Run pre-flight checks (5 min)
- [ ] Create VectorService (10 min)
- [ ] Create TableService (10 min)  
- [ bowling ] Create tool wrappers (10 min)
- [ ] Run registration script (5 min)
- [ ] Execute test_complete_pipeline.py (10 min)

### Success Criteria
✅ When done: `python3 test_complete_pipeline.py` shows all 5 tests passing

### If Successful → Next Phase
See **Section 5: Next Sprint Planning** for Phase 2

---

## 3. PERMANENT REFERENCES

### Core Plans (Use These)
- **NOW**: `SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md` - Current implementation
- **NEXT**: `VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md` - Phase 2-4 roadmap
- **FUTURE**: `/docs/PHASE_C_FUTURE_WORK.md` - Long-term vision

### Architecture Docs (Reference Only)
- `VERTICAL_SLICE_20250826.md` - Original design
- `UNCERTAINTY_20250825.md` - Uncertainty model
- `architecture_review_20250808/` - Service investigations

### Infrastructure
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (vs2_ tables)
- **APIs**: See `.env` (OpenAI, Gemini)

---

## 4. Quick Validation Commands

```bash
# After implementation, validate with:
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Test services work
python3 -c "from services.vector_service import VectorService; s = VectorService(); print('✅' if s.embed_text('test') else '❌')"

# Test registration
python3 register_services_and_tools.py

# Full validation
python3 test_complete_pipeline.py
```

---

## 5. Next Sprint Planning

### After Current Sprint Completes (Phase 2)
**Time Estimate**: 2-3 days
**Guide**: See Phase 2 in `VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md`

**Objectives**:
1. Add analysis tools (GraphAnalyzer, StatisticalAnalyzer)
2. Expand to 10+ tools
3. Complex workflow testing

**Update CLAUDE.md**: Replace Section 2 with Phase 2 objectives

### Phase 3: Integration Testing
**Time Estimate**: 2 days
**Guide**: See Phase 3 in `VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md`

### Phase 4: Production Readiness
**Time Estimate**: 3-5 days
**Guide**: See `/docs/PHASE_C_FUTURE_WORK.md`

---

## 6. Rollback Safety

If anything breaks:
```bash
git status  # Check what changed
git diff    # Review changes
git checkout -- .  # Rollback everything
```

---

## Time Breakdown for Current Sprint

| Task | Minutes | Cumulative |
|------|---------|------------|
| Read corrections | 5 | 5 |
| Pre-flight checks | 5 | 10 |
| Install dependencies | 3 | 13 |
| Create VectorService | 10 | 23 |
| Test VectorService | 2 | 25 |
| Create TableService | 10 | 35 |
| Test TableService | 2 | 37 |
| Create tool wrappers | 10 | 47 |
| Registration script | 5 | 52 |
| Run full test | 8 | 60 |

**Total: ~60 minutes** if no issues, 90 minutes with debugging

---

*Last Updated: 2025-08-28*
*Next Update: After current sprint completion*