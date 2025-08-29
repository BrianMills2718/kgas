# KGAS Implementation Guide - Corrected

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only
- **FAIL-FAST**: Surface errors immediately  
- **EVIDENCE-BASED**: Document in evidence/ directory
- **TEST FIRST**: Write tests before implementation

---

## 2. CURRENT SPRINT (2025-08-28)

### 🎯 Today's Focus: Add Vector and Table Services
**Realistic Time**: 2-3 hours (including reading/understanding)  
**Location**: Always in `/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice`

### Reference Guide
**V2** = `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`

### Implementation Checklist (Part.Step from V2)

#### Part 0: Pre-Flight (15 min)
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
```
- [ ] 0.1: Verify you're in vertical_slice directory
- [ ] 0.2: Check Neo4j is running (must see "✅ Neo4j is running")
- [ ] 0.3: Install dependencies: `pip install openai pandas numpy litellm python-dotenv`
- [ ] 0.4: Verify API keys work (must see "✅" for both OpenAI and Gemini)

**STOP if any ❌ appears - fix before continuing**

#### Part 1: Create Services (30 min)
- [ ] 1.1: Create `services/vector_service.py` (copy entire code from V2)
- [ ] 1.2: Test VectorService (must see "✅ VectorService works!")
- [ ] 1.3: Create `services/table_service.py` (copy entire code from V2)
- [ ] 1.4: Test TableService (must see "✅ TableService works!")

**STOP if tests fail - debug before continuing**

#### Part 2: Create Tool Wrappers (20 min)
- [ ] 2.1: Create `tools/vector_embedder.py` (copy entire code from V2)
- [ ] 2.2: Create `tools/table_persister.py` (copy entire code from V2)
- [ ] 2.3: Create/update `tools/crossmodal_converter.py` (copy entire code from V2)

#### Part 3: Registration (20 min)
- [ ] 3.1: Create `register_services_and_tools.py` (copy entire code from V2)
- [ ] 3.2: Run registration (must see "REGISTRATION COMPLETE" and list of tools)

**STOP if registration fails - check error messages**

#### Part 4: Test Data (5 min)
- [ ] 4.1: Create `test_entities.txt` with entity-rich content (copy from V2)

#### Part 5: End-to-End Testing (30 min)
- [ ] 5.1: Create `test_complete_pipeline.py` (copy entire code from V2)
- [ ] 5.2: Run pipeline test: `python3 test_complete_pipeline.py`

### Success Criteria
```bash
# You should see at minimum:
# - TEST 1: ✅ (VectorEmbedder)
# - TEST 2: ✅ (Pipeline) 
# - TEST 3: ✅ (Chain)
# - TEST 4: ✅ (Table)
# - TEST 5: ✅ or ❌ (CrossModal - may fail, that's OK)

# Count successes
python3 test_complete_pipeline.py 2>&1 | grep -c "✅"
# If 4+ then SUCCESS (CrossModal might fail due to empty graph)
```

### After Success
```bash
# Commit your work
git add -A
git commit -m "feat: Add VectorService and TableService with working tools"

# Update Section 2 of this file with Phase 2 content from Section 5 below
```

### If Tests Fail - Apply Fixes
Only if you see specific errors:

**Error: "result.final_output"**
→ Edit test_complete_pipeline.py: Replace `result.final_output` with `result.data`

**Error: "table_to_graph missing columns"**  
→ See CORRECTIONS.md Section 3

**Error: "No module named X"**
→ Check you ran pip install in Part 0

---

## 3. PERMANENT REFERENCES

### Guides
| Guide | Path | Purpose |
|-------|------|---------|
| V2 Implementation | `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md` | Step-by-step code |
| Corrections | `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_CORRECTIONS.md` | Known fixes |
| Next Phases | `/home/brian/projects/Digimons/docs/architecture/VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md` | After today |

### Configuration
- **Working Dir**: `/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice`
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (tables use vs2_ prefix)
- **APIs**: Check `/home/brian/projects/Digimons/.env`

---

## 4. Quick Checks

```bash
# Am I in the right place?
pwd
# MUST show: /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# What files exist?
ls services/*.py 2>/dev/null | wc -l  # Should increase as you create them
ls tools/*.py 2>/dev/null | wc -l     # Should increase as you create them

# Is Neo4j still running?
python3 -c "from neo4j import GraphDatabase; GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','devpassword')).verify_connectivity(); print('✅')"

# After creating VectorService, does it work?
python3 -c "import sys; sys.path.append('.'); from services.vector_service import VectorService; VectorService(); print('✅')"
```

---

## 5. Next Phases (After Today)

### Phase 2: Tool Expansion (Replace Section 2 with this)
```markdown
## 2. CURRENT SPRINT (Phase 2 - Tool Expansion)

### 🎯 Focus: Add Analysis Tools
**Time**: 2-3 days
**Guide**: See Part 4 of VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md

- [ ] Create GraphAnalyzer tool
- [ ] Create StatisticalAnalyzer tool
- [ ] Test complex chains
- [ ] Performance benchmarks
```

### Phase 3: Integration Testing
**Time**: 2 days  
**Focus**: Complex workflows

### Phase 4: Production
**Time**: 3-5 days  
**Focus**: Polish and deploy

---

## 6. Troubleshooting

### Start Over Completely
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Remove everything we created
rm -rf services/vector_service.py services/table_service.py
rm -rf tools/vector_embedder.py tools/table_persister.py tools/crossmodal_converter.py  
rm -rf register_services_and_tools.py test_complete_pipeline.py test_entities.txt

# Begin again at Part 0
```

### Common Issues

| Error | Fix |
|-------|-----|
| ModuleNotFoundError | Run: `pip install [module_name]` |
| Neo4j connection failed | Run: `sudo systemctl start neo4j` |
| OPENAI_API_KEY not found | Check: `cat /home/brian/projects/Digimons/.env \| grep OPENAI` |
| Permission denied | Check: `ls -la` and use `chmod 755 [file]` if needed |
| Can't import services | Make sure you're in vertical_slice directory |

---

## Time Expectations

**Reading & Understanding**: 30-45 minutes  
**Implementation**: 90-120 minutes  
**Debugging**: 30-60 minutes  
**Total Realistic**: 2.5-3.5 hours

**Take a break if**:
- You've been on one step for >30 minutes
- You see the same error 3+ times  
- It's been 2+ hours

---

*Updated: 2025-08-28*  
*Next Update: After all Part 5 tests show ✅ (or 4+ successes)*