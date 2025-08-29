# KGAS Implementation Guide

## 1. Coding Philosophy (MANDATORY)
- **NO LAZY IMPLEMENTATIONS**: Full implementations only, no mocking/stubs/fallbacks
- **FAIL-FAST**: Surface errors immediately, don't hide them
- **KISS**: Keep It Simple - but include necessary architectural patterns
- **TEST DRIVEN**: Write tests first where possible
- **EVIDENCE-BASED**: All claims require raw evidence in structured evidence files

---

## 2. CODEBASE OVERVIEW (Post-Cleanup 2025-08-29)

### 🎯 **Current System Architecture**
**Primary Development**: `/tool_compatability/poc/vertical_slice/` - Clean tool framework with working adapters
**Main Codebase**: `/src/` - Full system with 37+ tools, analytics, UI components
**Thesis Goal**: Extensible modular tool suite for dynamic analysis chain creation

### **Key Directories**
```
/tool_compatability/poc/vertical_slice/  # Active development (FOCUS HERE)
├── framework/          # Tool orchestration engine  
├── services/          # VectorService, TableService (working)
├── tools/             # VectorTool, TableTool adapters (working)
└── thesis_evidence/   # Ground truth data collection

/src/                  # Main system implementation
├── tools/            # 37+ production tools  
├── analytics/        # Cross-modal analysis
├── mcp/             # MCP protocol layer
└── ui/              # Current UI system

/docs/               # Documentation & schemas
/tests/integration/  # 60+ integration tests (needs audit)
/experiments/        # Research experiments (keep)
```

### **Entry Points** 
- `main.py` - Production FastAPI server
- `streamlit_app.py` - Academic UI for ontology generation  
- `kgas_mcp_server.py` - Full MCP server (37+ tools)
- `kgas_simple_mcp_server.py` - Simple MCP server (testing)

### **What Actually Works**
✅ Basic tool chaining (text → embedding → database)
✅ Tool registration with capabilities  
✅ Chain discovery (TEXT→VECTOR→TABLE)
✅ Adapter pattern integration
✅ Neo4j + SQLite storage

### **What Needs Implementation**
❌ Real uncertainty propagation (currently hardcoded 0.0)
❌ Meaningful reasoning traces (currently templates)  
❌ Verified provenance tracking
❌ Multi-modal pipelines (text+table+graph)
❌ Dynamic goal evaluation
❌ Graph operations integration

---

## 3. CURRENT SPRINT (2025-08-29 - Documentation Audit COMPLETE)

### ✅ **Major Accomplishments**
1. **Root Directory Organized** - Eliminated file chaos, archived duplicates
2. **"4 Entry Points" Problem SOLVED** - `apps/` directory duplication was the source
3. **Enterprise Cruft Removed** - Archived k8s/, SLA configs (not thesis-relevant)
4. **Clear System Architecture** - Identified vertical_slice as primary development
5. **Thesis Requirements Documented** - Clear goals in THESIS_REQUIREMENTS.md

### **Files Organized/Archived**
- ✅ 6 CLAUDE*.md variants → archived (kept only current)
- ✅ Test files → moved to `/tests/integration/`
- ✅ Config files → moved to `/config/build/`
- ✅ Schema files → moved to `/docs/schemas/`
- ✅ Enterprise files → archived (SLA, k8s, performance monitoring)

### **Next Priority Tasks**
1. **Test Suite Audit** - 60+ integration tests need consolidation  
2. **UI Strategy Decision** - Current `/src/ui/` vs recovered React components
3. **Real Uncertainty Implementation** - Replace hardcoded 0.0 values
4. **Graph Tools Integration** - Add text→graph, graph analysis capabilities

---

## 4. INFRASTRUCTURE

### **Working Directory**
`/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice/`

### **Database Configuration**
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **SQLite**: `vertical_slice.db` (vs2_ prefix for tables)
- **OpenAI**: text-embedding-3-small via OPENAI_API_KEY in .env
- **Gemini**: gemini/gemini-1.5-flash via GEMINI_API_KEY in .env

### **Quick Verification Commands**
```bash
# Test working adapters
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
python3 register_with_framework.py  # Should show "Chain found: ['VectorTool', 'TableTool']"
python3 test_integration.py         # Should show "✅ Integration successful"

# Check database
python3 -c "
import sqlite3
conn = sqlite3.connect('vertical_slice.db')
count = conn.execute('SELECT COUNT(*) FROM vs2_embeddings').fetchone()[0]
print(f'Embeddings in database: {count}')
"
```

---

## 5. DOCUMENTATION REFERENCES

### **Key Documents**
- `/tool_compatability/poc/vertical_slice/THESIS_REQUIREMENTS.md` - Clear system goals
- `/tool_compatability/poc/vertical_slice/DOCUMENTATION_AUDIT.md` - Complete cleanup record
- `/tool_compatability/poc/vertical_slice/RECONCILIATION_PLAN.md` - Architecture decisions

### **Evidence Files**
- `/tool_compatability/poc/vertical_slice/evidence/current/Evidence_ServiceIntegration.md` - Working adapter proof

### **Working Implementation** (Completed Previous Sprint)
- VectorTool & TableTool adapters (text → embedding → database)
- Framework registration with capabilities
- Chain discovery and execution  
- Error handling for API failures

---

*Last Updated: 2025-08-29 (Documentation Audit Complete)*
*Next Phase: Feature Development (uncertainty, graph tools, dynamic chains)*