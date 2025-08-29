# KGAS Implementation Guide

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only
- **FAIL-FAST**: Surface errors immediately  
- **EVIDENCE-BASED**: Document in evidence/ directory
- **TEST FIRST**: Write tests before implementation

---

## 2. CURRENT SPRINT (2025-08-28)

### 🎯 Today's Focus: Service & Tool Integration
**Time**: 90-120 minutes  
**Working Directory**: `/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice`

### Implementation Order (EXACT)

#### A. Setup (10 min)
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
```

Follow **V2 guide** = `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`

- [ ] V2 Step 0.1: Verify directory
- [ ] V2 Step 0.2: Check Neo4j running
- [ ] V2 Step 0.3: Install dependencies (`pip install openai pandas numpy litellm python-dotenv`)
- [ ] V2 Step 0.4: Verify API keys

#### B. Create Services (25 min)
- [ ] V2 Step 1.1: Create services/vector_service.py (copy ENTIRE code block)
- [ ] V2 Step 1.2: Test VectorService works
- [ ] V2 Step 1.3: Create services/table_service.py (copy ENTIRE code block)
- [ ] V2 Step 1.4: Test TableService works

#### C. Create Tools (15 min)
- [ ] V2 Step 2.1: Create tools/vector_embedder.py (copy ENTIRE code block)
- [ ] V2 Step 2.2: Create tools/table_persister.py (copy ENTIRE code block)
- [ ] V2 Step 2.3: Create tools/crossmodal_converter.py (copy ENTIRE code block)

#### D. Test Tools (10 min)
- [ ] V2 Step 3.1: Test VectorEmbedder
- [ ] V2 Step 3.2: Test TablePersister

#### E. Registration & Testing (30 min)
- [ ] V2 Step 3.1: Create register_services_and_tools.py (copy ENTIRE code block)
- [ ] V2 Step 3.2: Run registration
- [ ] V2 Step 4.1: Create test_entities.txt
- [ ] V2 Step 5.1: Create test_complete_pipeline.py (copy ENTIRE code block)
- [ ] V2 Step 5.2: Run complete test

### Success Criteria
```bash
# Should see "PIPELINE TESTING COMPLETE" and multiple ✅
python3 test_complete_pipeline.py

# Count successes (should be 5+)
python3 test_complete_pipeline.py 2>&1 | grep -c "✅"

# If all pass, commit:
git add -A && git commit -m "feat: Add VectorService and TableService with tools"
```

### Apply Corrections AFTER Testing
If tests show errors with `result.final_output`, then apply from **CORRECTIONS.md**:
- Fix ChainResult access (Section 2) in test_complete_pipeline.py
- Fix table_to_graph usage (Section 3) if CrossModal fails
- Other fixes as needed based on actual errors

---

## 3. PERMANENT REFERENCES

### Guides (Full Paths)
- **V2 Guide**: `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_BULLETPROOF_V2.md`
- **Corrections**: `/home/brian/projects/Digimons/docs/architecture/SERVICE_TOOL_IMPLEMENTATION_CORRECTIONS.md`
- **Next Phases**: `/home/brian/projects/Digimons/docs/architecture/VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md`

### Infrastructure
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (vs2_ prefix)
- **OpenAI**: text-embedding-3-small
- **Gemini**: gemini-1.5-flash

---

## 4. Quick Diagnostics

```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Check location
pwd  # Must show: /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Check Neo4j
python3 -c "from neo4j import GraphDatabase; d=GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','devpassword')); d.verify_connectivity(); print('✅ Neo4j running')"

# Check files created
ls services/vector_service.py services/table_service.py  # Both should exist
ls tools/vector_embedder.py tools/table_persister.py  # Both should exist

# Test VectorService (after creating it)
python3 -c "
import sys; sys.path.append('.')
from services.vector_service import VectorService
try:
    s = VectorService()
    e = s.embed_text('test')
    print(f'✅ Embedding works, dimension: {len(e)}')
except Exception as ex:
    print(f'❌ VectorService error: {ex}')
"

# Test OpenAI API (with proper env loading)
python3 -c "
import os, sys
sys.path.append('/home/brian/projects/Digimons')
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')
from openai import OpenAI
try:
    client = OpenAI()
    client.models.list()
    print('✅ OpenAI API works')
except Exception as e:
    print(f'❌ OpenAI error: {e}')
"
```

---

## 5. When Current Sprint Done

### Next Sprint (Phase 2): Tool Expansion
After Section 2 is complete and committed:

1. Copy this to replace Section 2:
```markdown
## 2. CURRENT SPRINT (Phase 2)

### 🎯 Focus: Analysis Tools
**Time**: 2-3 days
**Guide**: VERTICAL_SLICE_INTEGRATION_PLAN_REVISED.md Part 4

- [ ] Create GraphAnalyzer (Step 4.1)
- [ ] Create StatisticalAnalyzer (Step 4.2)  
- [ ] Test chains (Part 5, Step 5.1)
- [ ] Benchmark (Part 5, Step 5.2)
```

2. Continue with Phase 3, 4 as described in planning docs

---

## 6. If Things Go Wrong

### Reset Everything
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Delete created files
rm -f services/vector_service.py services/table_service.py
rm -f tools/vector_embedder.py tools/table_persister.py tools/crossmodal_converter.py
rm -f register_services_and_tools.py test_complete_pipeline.py test_entities.txt

# Start over with V2 guide Step 0.1
```

### Common Errors

**"ModuleNotFoundError: openai"**
```bash
pip install openai
```

**"Neo4j not connected"**
```bash
sudo systemctl start neo4j
# OR
neo4j start
```

**"OPENAI_API_KEY not found"**
```bash
# Check .env file exists and has key
cat /home/brian/projects/Digimons/.env | grep OPENAI_API_KEY
```

**"Permission denied"**
```bash
# Check write permissions
touch test.tmp && rm test.tmp && echo "✅ Can write" || echo "❌ Cannot write"
```

---

## Time Reality

**If everything works perfectly**: 90 minutes
**With normal debugging**: 2 hours
**If API/Neo4j issues**: 3+ hours

**Stop and ask for help if**:
- Stuck on same error for 20+ minutes
- Completed steps but tests fail repeatedly
- Unsure which V2 step to follow

---

*Updated: 2025-08-28*
*Next Update: After completing all checkboxes in Section 2*