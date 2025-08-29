# KGAS Implementation Guide

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only
- **FAIL-FAST**: Surface errors immediately  
- **EVIDENCE-BASED**: Document in evidence/ directory
- **TEST FIRST**: Write tests before implementation

---

## 2. CURRENT SPRINT (2025-08-28)

### 🎯 Today's Focus: Service & Tool Integration
**Time**: 60-90 minutes  
**Primary Guide**: `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`

### Pre-Implementation: Apply Critical Fixes
From `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_CORRECTIONS.md`:
1. Check Python 3.7+ (Section 1)
2. Use `result.data` not `result.final_output` (Section 2)
3. Verify write permissions (Section 5)

### Implementation Checklist
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
```

- [ ] Run pre-flight checks from V2 Step 0 (5 min)
- [ ] Create VectorService per V2 Step 1.1 (10 min)
- [ ] Test VectorService per V2 Step 1.2 (2 min)
- [ ] Create TableService per V2 Step 1.3 (10 min)
- [ ] Test TableService per V2 Step 1.4 (2 min)
- [ ] Create tool wrappers per V2 Part 2 (10 min)
- [ ] Create registration script per V2 Step 3.1 (5 min)
- [ ] Run test_complete_pipeline.py per V2 Step 5.2 (10 min)

### Success Validation
```bash
# Must see: "PIPELINE TESTING COMPLETE" with 5 passing tests
python3 test_complete_pipeline.py | grep -c "✅"  # Should output 5 or more

# If successful, commit:
git add -A && git commit -m "feat: Add VectorService and TableService with tools"
```

### If Any Step Fails
1. Check error message
2. See Troubleshooting in V2 guide
3. If stuck: `git checkout -- .` to reset

### When Complete → Next Phase
Update this Section 2 with Phase 2 from below (Section 5)

---

## 3. PERMANENT REFERENCES

### Implementation Guides (Follow These)
- **Current**: `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`
- **Fixes**: `/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_CORRECTIONS.md`
- **Next Phases**: `/docs/architecture/VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md`

### Design Documents (Reference Only)
- `/docs/architecture/VERTICAL_SLICE_20250826.md` - Original architecture
- `/docs/architecture/UNCERTAINTY_20250825.md` - Uncertainty model
- `/docs/architecture/architecture_review_20250808/` - Service analysis

### Infrastructure
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (vs2_ prefix for new tables)
- **OpenAI**: text-embedding-3-small (see `.env`)
- **Gemini**: gemini-1.5-flash (see `.env`)

---

## 4. Quick Debug Commands

```bash
# Where am I?
pwd  # Should be: .../tool_compatability/poc/vertical_slice

# Is Neo4j running?
python3 -c "from neo4j import GraphDatabase; d=GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','devpassword')); d.verify_connectivity(); print('✅ Neo4j OK')"

# Are services created?
ls -la services/*.py 2>/dev/null | wc -l  # Should be 5+ files

# Does VectorService work?
python3 -c "from services.vector_service import VectorService; s=VectorService(); e=s.embed_text('test'); print(f'✅ Embedding dim: {len(e)}' if e else '❌ Failed')"

# What tools are registered?
python3 -c "from register_services_and_tools import register_all_tools; f=register_all_tools(); print(f'Tools: {list(f.tools.keys())}' if f else '❌ Registration failed')"
```

---

## 5. Future Sprint Templates

### Phase 2: Tool Expansion (Copy this to Section 2 after Phase 1)
**Time**: 2-3 days  
**Focus**: Add analysis tools  
**Guide**: VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md Part 4

- [ ] Create GraphAnalyzer tool (Part 4, Step 4.1)
- [ ] Create StatisticalAnalyzer tool (Part 4, Step 4.2)
- [ ] Test tool chains (Part 5, Step 5.1)
- [ ] Performance benchmarks (Part 5, Step 5.2)

### Phase 3: Integration Testing (After Phase 2)
**Time**: 2 days  
**Focus**: End-to-end workflows  
**Guide**: VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md Part 5

### Phase 4: Production Polish (After Phase 3)
**Time**: 3-5 days  
**Focus**: Documentation, optimization, deployment  
**Guide**: `/docs/PHASE_C_FUTURE_WORK.md`

---

## 6. Emergency Procedures

### Complete Reset
```bash
# Save your work
git add -A && git stash

# Reset to clean state
git checkout -- .
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
rm -f services/vector_service.py services/table_service.py
rm -f tools/vector_embedder.py tools/table_persister.py
rm -f register_services_and_tools.py test_complete_pipeline.py

# Start over with guides
```

### Neo4j Issues
```bash
# Restart Neo4j
sudo systemctl restart neo4j
# OR
neo4j restart

# Clear Neo4j data (warning: deletes everything)
python3 -c "from neo4j import GraphDatabase; d=GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','devpassword')); d.session().run('MATCH (n) DETACH DELETE n')"
```

### API Key Issues
```bash
# Test OpenAI key
python3 -c "from openai import OpenAI; c=OpenAI(); r=c.models.list(); print('✅ API works')"

# Check remaining credits
# Visit: https://platform.openai.com/usage
```

---

## Time Reality Check

**Best Case** (everything works): 60 minutes  
**Realistic** (some debugging): 90 minutes  
**Worst Case** (API issues, typos): 2-3 hours

**Signs you should take a break**:
- Same error 3+ times
- Spent 30+ min on one step
- Getting frustrated

**When stuck**: Post exact error message, not "it doesn't work"

---

*Last Updated: 2025-08-28*  
*Next Update: After Section 2 completion (~90 minutes)*