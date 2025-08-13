# KGAS Critical Gap Resolution Plan

## 🚨 CRITICAL: System Reality vs Documentation Gap

**Discovery Date**: 2025-08-02  
**Severity**: CRITICAL - System claims don't match implementation

### The Problem
- **Documentation describes**: Sophisticated DAG execution with multi-modal analysis
- **Reality**: Basic linear pipeline with 24% F1 entity extraction that barely works
- **Demos**: ✅ **RESOLVED** - Core system now uses fail-fast architecture with real implementations
- **Tools**: Won't even initialize due to service_manager dependencies

## 📋 WEEK 1: Fix Basic Pipeline (Due: 2025-08-09)

### Task 1.1: Fix service_manager dependency ⏳
**Problem**: All tools fail on initialization
```python
# Current state - ALL FAIL:
PDFLoader()  # ❌ missing 1 required positional argument: 'service_manager'
TextChunker()  # ❌ missing 1 required positional argument: 'service_manager'
SpacyNER()  # ❌ missing 1 required positional argument: 'service_manager'
```

**Solution**:
1. Add optional service_manager parameter with None default
2. Create lazy initialization for services
3. Allow tools to work standalone

**Test Command**:
```bash
python -c "from src.tools.phase1.t01_pdf_loader import PDFLoader; loader = PDFLoader(); print('✅ Tool initialized')"
```

### Task 1.2: Test complete linear pipeline ⏳
**Goal**: Verify T01 → T15A → T23A → T27 → T31 → T34 → T68 → T49 chain works

**Implementation**:
```python
# test_real_pipeline.py
def test_actual_pipeline():
    # Load actual document (fail-fast implementation)
    loader = PDFLoader()
    chunks = TextChunker()
    entities = SpacyNER()
    # ... etc
    # Must produce real Neo4j graph
```

**Success Criteria**:
- Processes carter_anapolis.txt end-to-end
- Creates real entities in Neo4j
- Returns actual query results

### Task 1.3: Fix file format flexibility ⏳
**Problem**: T01 only handles PDFs, but test files are .txt

**Solution**:
- Implement format detection
- Route to appropriate loader (T01 for PDF, T03 for TXT)
- ✅ **COMPLETED** - Implement fail-fast error handling with clear error messages

## 📋 WEEK 2: Real DAG Execution (Due: 2025-08-16)

### Task 2.1: Complete real_dag_orchestrator.py ⏳
**File**: `src/orchestration/real_dag_orchestrator.py` (already created)

**Fixes Needed**:
1. Handle service_manager initialization
2. Add retry logic for failed nodes
3. Implement timeout handling

### Task 2.2: Implement parallel execution ⏳
**Goal**: True parallel branches, not sequential

**Test DAG**:
```
        Input
          |
    [Split to 3 branches]
      /      |      \
   NLP    Vector   Table
      \      |      /
       [Join point]
          |
        Output
```

**Success Metric**: >1.5x speedup vs sequential

### Task 2.3: Real provenance tracking ⏳
**Requirements**:
- Actual operation IDs (not "op_001", "op_002")
- Real timestamps from system clock
- Actual execution durations
- Data lineage with hashes

## 📋 WEEK 3: Phase C Integration (Due: 2025-08-23)

### Task 3.1: Wire Phase C to tool interfaces ⏳
**Problem**: Phase C uses string.count() instead of tools

**Fix**:
```python
# WRONG (current):
military_terms = content.count('military')

# RIGHT (needed):
entities = entity_extractor.extract(content)
military_entities = [e for e in entities if e.type == 'MILITARY']
```

### Task 3.2: Implement cross-modal converters ⏳
**Missing Tools**:
- T91: Graph-to-Table (create from scratch)
- T92: Vector-to-Table (create from scratch)
- T93: Multi-modal fusion (create from scratch)

### Task 3.3: Integration testing ⏳
- Process 5+ documents simultaneously
- Verify cross-modal data flow
- Measure actual vs claimed performance

## 📋 WEEK 4: LLM Entity Extraction (Due: 2025-08-30)

### Task 4.1: Implement T23C LLM Entity Extractor ⏳
**Goal**: >60% F1 score (up from 24%)

**Implementation**:
```python
class LLMEntityExtractor:
    def extract_entities(self, text):
        # Use OpenAI/Anthropic API
        # Implement caching
        # Track costs
```

### Task 4.2: Entity resolution improvements ⏳
- Coreference resolution
- Cross-document entity linking
- Disambiguation

### Task 4.3: Performance optimization ⏳
- Batch API calls
- Implement caching
- Cost tracking

## 📊 Success Metrics

### Week 1 Success:
- [ ] All Phase 1 tools initialize without service_manager
- [ ] Linear pipeline processes real document end-to-end
- [ ] Both PDF and TXT files can be processed

### Week 2 Success:
- [ ] DAG orchestrator executes with parallel branches
- [ ] Provenance shows real timestamps and operations
- [ ] >1.5x speedup from parallelization

### Week 3 Success:
- [ ] Phase C uses actual tool calls, not string operations
- [ ] Cross-modal converters implemented and tested
- [ ] Multi-document processing actually works

### Week 4 Success:
- [ ] Entity extraction F1 score >60%
- [ ] LLM integration with cost tracking
- [ ] Full pipeline with LLM extraction works

## 🚫 What NOT to Do

1. **✅ COMPLETED - NO MORE MOCK DEMOS**: Core system now uses fail-fast architecture with real implementations
2. **NO FICTIONAL PROVENANCE**: Use actual execution tracking
3. **NO ASCII ART DAGS**: Show real parallel execution
4. **NO "WOULD DO X"**: Either it works or it doesn't
5. **NO CONCEPTUAL ARCHITECTURE**: Build working code

## 📝 Evidence Requirements

For each completed task, provide:
1. **Execution logs** showing actual tool invocations
2. **Performance metrics** with real measurements
3. **Test results** from actual test files
4. **Before/after comparisons** showing improvements

## 🎯 Final Goal

By end of Week 4, the system should:
- Actually execute tools in a DAG structure
- Process multiple documents with real parallelization
- Extract entities with >60% F1 score using LLMs
- Have honest documentation matching capabilities

This is achievable but requires focused effort on implementation, not architecture diagrams.