# Week 3: Critical Services Integration & Real Pipeline

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **TEST DRIVEN DESIGN**: Write tests first where possible

### Evidence Requirements
```
evidence/
├── current/
│   └── Evidence_Services_[Task].md      # Current service integration work
├── completed/
│   ├── Evidence_Uncertainty_*.md        # MVP uncertainty work ✅
│   └── Evidence_Framework_*.md          # Framework integration ✅
```

---

## 2. Project Status & Goals

### Strategic Context
**PhD Thesis Goal**: Demonstrate dynamic tool composition with uncertainty propagation enables new computational social science analyses.

**12-Week Timeline Position**: Week 3 of 12

### What's Complete ✅
1. **Tool Composition Framework** - 20 tools integrated, DAG chains working
2. **Uncertainty Propagation** - Float-based (0-1), simple formula
3. **ProvenanceService** - Tracking all operations
4. **MVP Pipeline** - File → Text → Entities → Graph

### What's Needed (Week 3) 🔄
1. **3 Critical Services** - Identity, Quality, WorkflowState
2. **Real Pipeline** - Actual analytical workflow with real data
3. **Refined Uncertainty** - Better propagation model
4. **Thesis Evidence** - Performance metrics, flexibility analysis

---

## 3. Codebase Structure

### Core Systems
```
/src/core/
├── composition_service.py      # Framework bridge ✅
├── adapter_factory.py          # Tool adaptation with uncertainty ✅
├── service_bridge.py           # Service connection point ✅
├── identity_service.py         # Entity tracking (TO INTEGRATE)
├── quality_service.py          # Confidence assessment (TO INTEGRATE)
├── workflow_state_service.py   # Checkpoint management (TO INTEGRATE)
└── test_*.py                   # Test suites
```

### Framework
```
/tool_compatability/poc/
├── framework.py               # Core with ToolResult + uncertainty ✅
└── data_types.py             # Type definitions
```

### Tools
```
/src/tools/
├── simple_text_loader.py      # ✅ Working
├── gemini_entity_extractor.py # ✅ Working
├── neo4j_graph_builder.py     # ✅ Working
└── [17 other integrated tools]
```

---

## 4. Priority Task: Integrate IdentityService

### Why IdentityService First
- Most relevant for social science (entity tracking across analyses)
- Similar integration pattern to ProvenanceService (proven approach)
- Enables entity-based uncertainty (different confidence per entity)

### Implementation Instructions

#### Step 1: Extend ServiceBridge (1 hour)

**File**: Modify `/src/core/service_bridge.py`

Add IdentityService support:
```python
def get_identity_service(self) -> IdentityService:
    """Get or create identity service"""
    if 'identity' not in self._services:
        self._services['identity'] = IdentityService()
    return self._services['identity']

def track_entity(self, surface_form: str, entity_type: str, 
                confidence: float, source_tool: str) -> str:
    """Track entity mention and return entity_id"""
    identity = self.get_identity_service()
    
    # Create mention
    mention_id = identity.create_mention(
        surface_form=surface_form,
        start_pos=0,  # Simplified for now
        end_pos=len(surface_form),
        source_ref=source_tool,
        entity_type=entity_type,
        confidence=confidence
    )
    
    # Get or create entity
    entity_id = identity.get_entity_by_mention(mention_id)
    
    return entity_id
```

#### Step 2: Update Adapter for Entity Tracking (1 hour)

**File**: Modify `/src/core/adapter_factory.py`

Track entities found during tool execution:
```python
# In process() method, after tool execution:
if self.service_bridge and isinstance(result.data, dict):
    # Check if tool produced entities
    if 'entities' in result.data:
        for entity in result.data['entities']:
            entity_id = self.service_bridge.track_entity(
                surface_form=entity.get('text', ''),
                entity_type=entity.get('type', 'UNKNOWN'),
                confidence=entity.get('confidence', 0.5),
                source_tool=self.tool_id
            )
            entity['entity_id'] = entity_id
```

#### Step 3: Test Entity Tracking (1 hour)

**File**: Create `/src/core/test_identity_integration.py`

Test that entities are tracked across tools and uncertainty is entity-specific.

**Evidence Required**: `evidence/current/Evidence_Services_Identity.md`
- Show entities being tracked
- Demonstrate entity resolution
- Verify entity-specific confidence

---

## 5. Next Task: Build Real Analytical Pipeline

### Target: News Article Analysis Pipeline

**Data Flow**:
```
News Articles (RSS/Web) →
  TextLoader →
  TextCleaner →
  EntityExtractor (Gemini) →
  SentimentAnalyzer →
  GraphBuilder (Neo4j) →
  CommunityDetector →
  UncertaintyAggregator →
  ReportGenerator
```

### Implementation Steps

1. **Create Pipeline Orchestrator** (`/src/pipelines/news_analysis.py`)
2. **Add Real Data Source** (RSS feed or web scraping)
3. **Implement Missing Tools** (SentimentAnalyzer, CommunityDetector)
4. **Track Uncertainty End-to-End**
5. **Generate Analysis Report**

**Evidence Required**: `evidence/current/Evidence_Real_Pipeline.md`
- Complete execution log
- Uncertainty progression through pipeline
- Actual insights generated
- Performance metrics

---

## 6. Service Integration Schedule

### Day 1-2: IdentityService ⏳
- Entity mention tracking
- Cross-tool entity resolution
- Entity-specific uncertainty

### Day 3: QualityService
- Replace simple float uncertainty
- Confidence intervals
- Quality metrics per operation

### Day 4: WorkflowStateService  
- Save/resume pipelines
- Checkpoint management
- Error recovery

### Day 5: Real Pipeline & Evidence
- Complete news analysis pipeline
- Collect performance metrics
- Document thesis evidence

---

## 7. Success Criteria for Week 3

### Minimum Success
- [ ] IdentityService integrated and tracking entities
- [ ] One real pipeline processing actual data
- [ ] Uncertainty helping identify issues

### Target Success
- [ ] All 3 services integrated
- [ ] Pipeline generating insights
- [ ] Performance metrics collected
- [ ] Refined uncertainty model

### Stretch Goals
- [ ] Multiple pipeline variants compared
- [ ] Uncertainty visualization
- [ ] Automated pipeline discovery

---

## 8. Thesis Evidence Collection

### Metrics to Track
```python
# In every pipeline execution:
metrics = {
    'pipeline_length': len(tools),
    'execution_time': total_seconds,
    'memory_usage': max_memory_mb,
    'uncertainty_progression': [0.1, 0.15, 0.23, ...],
    'entities_tracked': entity_count,
    'insights_generated': insight_count,
    'errors_caught_by_uncertainty': error_count
}
```

### Comparison Baselines
- Hardcoded pipeline (no flexibility)
- Pipeline without uncertainty (no confidence tracking)
- Manual analysis (human baseline)

---

## 9. DO NOT

- ❌ Skip service integration to work on new features
- ❌ Use mock data when real data is available
- ❌ Ignore uncertainty in favor of just getting results
- ❌ Forget to collect metrics for thesis
- ❌ Over-engineer when simple solutions work

---

## 10. Quick Reference

### Run Tests
```bash
# Uncertainty tests (should pass)
python3 src/core/test_uncertainty_propagation.py

# Service integration tests
python3 src/core/test_service_integration.py

# Complete MVP test
python3 src/core/test_complete_mvp.py

# Identity integration (after implementation)
python3 src/core/test_identity_integration.py
```

### Check Status
```bash
# See what services are connected
grep "def get_.*_service" src/core/service_bridge.py

# Count integrated tools
python3 -c "from src.core.composition_service import CompositionService; s=CompositionService(); print(f'Tools: {s.composition_metrics[\"tools_adapted\"]}')"
```

---

*Last Updated: 2025-08-26*
*Phase: Week 3 - Critical Services Integration*
*Priority: IdentityService → Real Pipeline → Evidence Collection*
*Deadline: End of Week 3 (5 days)*