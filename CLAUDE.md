# Type-Based Tool Composition - Phase 2 Production Framework

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them  
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files
- **TEST DRIVEN DESIGN**: Write tests first, then implementation
- **DIRECT DATA PASSING**: Pass actual data, not references (except graphs in Neo4j)

### Evidence Requirements
Every implementation MUST generate evidence files:
```
evidence/
├── current/
│   └── Evidence_PHASE2_[Component].md  # Current Phase 2 work only
├── completed/
│   ├── Evidence_POC_Registry.md        # ✅ POC Phase 1 completed
│   ├── Evidence_POC_Tools.md           # ✅ POC Phase 1 completed
│   ├── Evidence_POC_Integration.md     # ✅ POC Phase 1 completed
│   └── Evidence_KGAS_Pipeline.md       # ✅ KGAS implementation
```

Evidence files must contain:
- Raw execution logs (not summaries)
- Actual error messages when things fail
- Performance metrics with timestamps
- No success claims without demonstrable proof

---

## 2. Codebase Structure

### Completed: KGAS Pipeline
```
src/
├── tools/phase2/
│   └── t23c_llm_extractor.py      # Real Gemini LLM extraction (no mocks)
├── pipeline/
│   └── kgas_pipeline.py           # Document → LLM → Neo4j → Query
└── tests/
    └── test_real_llm_pipeline.py  # End-to-end validation

evidence/completed/
├── pipeline_end_to_end.json       # Test results with metrics
├── llm_extraction_nexora.json     # Raw LLM responses
└── DOUBLECHECK_KGAS_IMPLEMENTATION.md
```

**Status**: ✅ Working with Gemini-2.0-flash-exp, Neo4j storage, query system functional

### Completed: POC Foundation (Phase 1) ✅
```
tool_compatability/poc/
├── data_types.py           # 10 semantic types (FILE, TEXT, ENTITIES, etc.)
├── base_tool.py            # Base class with metrics, fail-fast
├── registry.py             # Tool registry with chain discovery
├── tools/
│   ├── text_loader.py      # FILE → TEXT (working)
│   ├── entity_extractor.py # TEXT → ENTITIES (Gemini API, no fallback)
│   └── graph_builder.py    # ENTITIES → GRAPH (Neo4j, no fallback)
└── tests/
    ├── test_registry.py    # 11 tests passing
    └── test_integration.py # 12 tests passing
```

### In Progress: Production Framework (Phase 2)
```
src/tools/composition/       # NEW - Production implementation
├── types/
│   ├── type_registry.py    # TODO: Plugin-based type system
│   ├── schema_versions.py  # TODO: Schema versioning & migration
│   └── namespaces.py       # TODO: Entity schema namespaces
├── execution/
│   ├── pipeline_context.py # TODO: State management across chains
│   ├── chain_selector.py   # TODO: Multiple chain selection strategies
│   └── retry_policy.py     # TODO: Smart retry with checkpointing
├── resources/
│   ├── connection_pool.py  # TODO: Neo4j connection pooling
│   ├── rate_limiter.py     # TODO: API rate limiting
│   └── cache.py            # TODO: TTL cache for expensive ops
└── composer/
    └── tool_composer.py     # TODO: Merge/split/wrap tools
```

---

## 3. Phase 2 Mission: Production-Ready Framework

### Phase 1 Achievements ✅
- Type-based composition proven to work
- Automatic chain discovery via NetworkX
- Real service integration (Gemini, Neo4j)
- Fail-fast implementation (no mocks/fallbacks)
- Performance overhead <5% with real services

### Phase 2 Goals
1. **Schema Namespaces**: Handle different entity schemas (military, medical, etc.)
2. **Pipeline Context**: Stateful execution with checkpoints
3. **Chain Selection**: 5 strategies (shortest, fastest, cheapest, quality, LLM-guided)
4. **Resource Management**: Connection pooling, rate limiting, caching
5. **Error Recovery**: Smart retry for transient failures only
6. **Migration Path**: Audit and map all 38 existing tools

---

## 4. Phase 2 Implementation Instructions

### Task 1: Type Registry with Schema Namespaces (Day 1-2)

**Problem**: Different tools produce "ENTITIES" with incompatible schemas.

**Solution**: Implement schema namespaces that Neo4j can query via labels.

**File**: `src/tools/composition/types/type_registry.py`

```python
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import importlib.util

class TypeSpec(BaseModel):
    """Specification for a data type with schema"""
    type: DataType
    schema: Optional[str] = None  # e.g., "military", "medical"
    version: str = "1.0"
    
    def is_compatible_with(self, other: 'TypeSpec') -> bool:
        """Check if this type can connect to another"""
        if self.type != other.type:
            return False
        if self.schema and other.schema:
            return self.schema == other.schema
        return True  # Generic can connect to specific

class TypePlugin:
    """Base class for type plugins"""
    def register_types(self) -> List[DataType]:
        raise NotImplementedError
    
    def register_schemas(self) -> Dict[DataType, List[str]]:
        raise NotImplementedError

class TypeRegistry:
    def __init__(self):
        self.types = {}
        self.schemas = {}
        self.plugins = []
    
    def load_plugin(self, plugin_path: str):
        """Load plugin from file - FAIL FAST if invalid"""
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        if not spec or not spec.loader:
            raise RuntimeError(f"Invalid plugin: {plugin_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find and instantiate plugin class
        found = False
        for item in dir(module):
            obj = getattr(module, item)
            if isinstance(obj, type) and issubclass(obj, TypePlugin) and obj != TypePlugin:
                plugin = obj()
                self.register_plugin(plugin)
                found = True
        
        if not found:
            raise RuntimeError(f"No TypePlugin found in {plugin_path}")
    
    def validate_connection(self, output_spec: TypeSpec, input_spec: TypeSpec) -> bool:
        """Validate if two type specs can connect"""
        return output_spec.is_compatible_with(input_spec)
```

**Test First**: Create `tests/test_type_registry.py`
```python
def test_schema_namespace_compatibility():
    military_entities = TypeSpec(type=DataType.ENTITIES, schema="military")
    generic_entities = TypeSpec(type=DataType.ENTITIES, schema=None)
    medical_entities = TypeSpec(type=DataType.ENTITIES, schema="medical")
    
    registry = TypeRegistry()
    assert registry.validate_connection(military_entities, military_entities)  # Same schema
    assert registry.validate_connection(generic_entities, military_entities)   # Generic to specific
    assert not registry.validate_connection(military_entities, medical_entities)  # Different schemas

def test_neo4j_label_integration():
    """Test that schema namespaces map to Neo4j labels"""
    # Create entities with military schema
    # Store in Neo4j with :Entity:Military labels
    # Query with MATCH (n:Entity:Military)
    # Verify only military entities returned
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_TypeRegistry.md`
- Show schema namespaces working
- Demonstrate Neo4j label queries working with namespaces
- Plugin loading functioning

### Task 2: Pipeline Context & State Management (Day 3-4)

**Problem**: Tools need shared state and configuration through chains.

**File**: `src/tools/composition/execution/pipeline_context.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass
class Checkpoint:
    tool_id: str
    output: Any
    timestamp: datetime
    
class PipelineContext:
    """Context that flows through tool chain"""
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.checkpoints: List[Checkpoint] = []
        self.config_overrides: Dict[str, Dict] = {}
    
    def checkpoint(self, tool_id: str, output: Any):
        """Save checkpoint for recovery"""
        self.checkpoints.append(
            Checkpoint(tool_id=tool_id, output=output, timestamp=datetime.now())
        )
    
    def get_last_checkpoint(self) -> Optional[Checkpoint]:
        return self.checkpoints[-1] if self.checkpoints else None
    
    def can_resume_from(self, tool_id: str) -> bool:
        """Check if we can resume from a specific tool"""
        return any(cp.tool_id == tool_id for cp in self.checkpoints)
```

**Test First**: Create `tests/test_pipeline_context.py`
```python
def test_checkpoint_recovery():
    context = PipelineContext()
    context.checkpoint("TextLoader", {"content": "test"})
    context.checkpoint("EntityExtractor", {"entities": []})
    
    assert context.can_resume_from("EntityExtractor")
    last = context.get_last_checkpoint()
    assert last.tool_id == "EntityExtractor"

def test_config_override_propagation():
    context = PipelineContext()
    context.config_overrides["EntityExtractor"] = {"temperature": 0.5}
    assert context.config_overrides["EntityExtractor"]["temperature"] == 0.5
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_PipelineContext.md`
- Show checkpoint/resume working
- Demonstrate config override propagation
- Test failure recovery mid-chain

### Task 3: Smart Chain Selection (Day 5)

**Problem**: Multiple valid chains exist, need selection strategies.

**File**: `src/tools/composition/execution/chain_selector.py`

```python
from enum import Enum
from typing import List, Dict, Optional
import litellm  # REQUIRED - no fallbacks
import time

class ChainSelectionStrategy(Enum):
    SHORTEST = "shortest"
    FASTEST = "speed"
    CHEAPEST = "cost"
    HIGHEST_QUALITY = "quality"
    LLM_GUIDED = "llm"

class ChainSelector:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history = {}  # Track historical performance
    
    def select_chain(
        self,
        chains: List[List[str]], 
        strategy: ChainSelectionStrategy,
        context: Optional[Dict] = None
    ) -> List[str]:
        if not chains:
            raise ValueError("No valid chains found")
            
        if strategy == ChainSelectionStrategy.SHORTEST:
            return min(chains, key=len)
        
        elif strategy == ChainSelectionStrategy.FASTEST:
            return self._select_by_speed(chains)
        
        elif strategy == ChainSelectionStrategy.LLM_GUIDED:
            if not os.getenv("GEMINI_API_KEY"):
                raise RuntimeError("GEMINI_API_KEY required for LLM-guided selection")
            return self._llm_select(chains, context)
        
        # Other strategies...
    
    def _llm_select(self, chains: List[List[str]], context: Dict) -> List[str]:
        """Use LLM to select best chain based on context - NO MOCKS"""
        prompt = f"""Given these tool chains and context, select the best one.
        
        Chains:
        {chains}
        
        Context:
        {context}
        
        Return ONLY the index (0-based) of the best chain."""
        
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        index = int(response.choices[0].message.content.strip())
        return chains[index]
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_ChainSelector.md`
- Test all 5 selection strategies
- Show LLM-guided selection with real API
- Performance comparison of strategies

---

### Task 4: Resource Management (Day 6)

**Problem**: Need connection pooling, rate limiting, caching.

**File**: `src/tools/composition/resources/connection_pool.py`

```python
from neo4j import GraphDatabase, Session
from threading import Lock
from queue import Queue
import time

class Neo4jConnectionPool:
    def __init__(self, uri: str, auth: tuple, max_connections: int = 10):
        self.uri = uri
        self.auth = auth
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create initial connections - FAIL FAST if Neo4j unavailable"""
        for _ in range(self.max_connections):
            driver = GraphDatabase.driver(self.uri, auth=self.auth)
            driver.verify_connectivity()  # Fail fast
            self.pool.put(driver)
    
    def acquire(self) -> Session:
        """Get a session from pool"""
        driver = self.pool.get()
        return driver.session()
    
    def release(self, session: Session):
        """Return session to pool"""
        session.close()
        self.pool.put(session._driver)
```

**File**: `src/tools/composition/resources/rate_limiter.py`

```python
class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def check(self) -> bool:
        """Check if we can make a call"""
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < 60]
        
        if len(self.calls) < self.calls_per_minute:
            self.calls.append(now)
            return True
        return False
    
    def wait_if_needed(self):
        """Block until rate limit allows"""
        while not self.check():
            time.sleep(0.1)
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_Resources.md`
- Connection pool handling concurrent requests
- Rate limiter preventing API throttling
- Cache hit/miss ratios

---

### Task 5: Error Recovery & Retries (Day 7)

**File**: `src/tools/composition/execution/retry_policy.py`

```python
from typing import List, Type
import time

class RetryPolicy:
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        retryable_errors: List[Type[Exception]] = None
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retryable_errors = retryable_errors or [
            ConnectionError,
            TimeoutError,
            # RateLimitError - when we implement it
        ]
    
    def should_retry(self, exception: Exception) -> bool:
        return type(exception) in self.retryable_errors
    
    def get_wait_time(self, attempt: int) -> float:
        return self.backoff_factor ** attempt

class ChainExecutor:
    def execute_with_recovery(
        self,
        chain: List[str],
        input_data: Any,
        context: PipelineContext
    ):
        # Try to resume from checkpoint if exists
        start_index = 0
        if context.checkpoints:
            last_checkpoint = context.checkpoints[-1]
            if last_checkpoint.tool_id in chain:
                start_index = chain.index(last_checkpoint.tool_id) + 1
                current_data = last_checkpoint.output
                print(f"Resuming from checkpoint: {last_checkpoint.tool_id}")
        
        for i in range(start_index, len(chain)):
            tool_id = chain[i]
            tool = self.get_tool(tool_id)
            retry_policy = tool.retry_policy
            
            for attempt in range(retry_policy.max_retries):
                try:
                    result = tool.process(current_data, context=context)
                    context.checkpoint(tool_id, result.data)
                    break
                except Exception as e:
                    if retry_policy.should_retry(e) and attempt < retry_policy.max_retries - 1:
                        wait_time = retry_policy.get_wait_time(attempt)
                        print(f"Retrying {tool_id} in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        raise  # Fail fast for non-retryable or max attempts
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_ErrorRecovery.md`
- Show retry working for transient errors
- Show fail-fast for permanent errors
- Checkpoint resume after failure

---

### Task 6: Integration & Migration (Day 8)

Create migration guide for existing 38 tools:

**File**: `src/tools/composition/migration/audit_tools.py`

```python
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any

def audit_existing_tools() -> Dict[str, Any]:
    """Audit all 38 existing tools and map to semantic types"""
    tools_to_audit = [
        "src/tools/phase2/t23c_llm_extractor.py",
        "src/tools/phase3/t31_entity_builder.py",
        "src/tools/phase3/t34_validator.py",
        # ... all 38 tools
    ]
    
    results = {}
    for tool_path in tools_to_audit:
        path = Path(tool_path)
        if not path.exists():
            results[tool_path] = {"error": "File not found"}
            continue
            
        with open(path) as f:
            tree = ast.parse(f.read())
        
        # Analyze tool
        tool_info = {
            "classes": [],
            "input_types": [],
            "output_types": [],
            "dependencies": [],
            "boundary_issues": [],
            "migration_difficulty": "unknown"
        }
        
        # Extract class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                tool_info["classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    tool_info["dependencies"].append(alias.name)
        
        # Determine migration plan
        if "t31" in tool_path or "t34" in tool_path:
            tool_info["boundary_issues"].append("Should be internal to t23c")
            tool_info["migration_difficulty"] = "merge_required"
        
        results[tool_path] = tool_info
    
    return results
```

**Evidence Required**: `evidence/current/Evidence_PHASE2_Migration.md`
- Audit results for all 38 tools
- Type mapping decisions
- Tools that need merging/splitting
- Migration timeline

## 5. Testing Protocol

Every component needs:
1. Unit tests (test-first development)
2. Integration tests with real services
3. Performance benchmarks
4. Failure scenario tests

```bash
# Run all Phase 2 tests
cd /home/brian/projects/Digimons
python -m pytest src/tools/composition/tests/ -v

# Verify no mocks
grep -r "mock" src/tools/composition/ --include="*.py"
# Should return nothing except comments
```

---

## 6. Daily Checklist

### Day 1-2: Type Registry
- [ ] Create type_registry.py with plugin support
- [ ] Implement schema namespaces
- [ ] Test Neo4j label integration
- [ ] Generate Evidence_PHASE2_TypeRegistry.md

### Day 3-4: Pipeline Context
- [ ] Create pipeline_context.py
- [ ] Implement checkpointing
- [ ] Test recovery scenarios
- [ ] Generate Evidence_PHASE2_PipelineContext.md

### Day 5: Chain Selection
- [ ] Create chain_selector.py
- [ ] Implement all 5 strategies
- [ ] Test with real Gemini API
- [ ] Generate Evidence_PHASE2_ChainSelector.md

### Day 6: Resource Management
- [ ] Create connection pool
- [ ] Implement rate limiter
- [ ] Add caching layer
- [ ] Generate Evidence_PHASE2_Resources.md

### Day 7: Error Recovery
- [ ] Create retry_policy.py
- [ ] Test transient vs permanent failures
- [ ] Implement checkpoint resume
- [ ] Generate Evidence_PHASE2_ErrorRecovery.md

### Day 8: Migration Planning
- [ ] Audit all 38 tools
- [ ] Map to semantic types
- [ ] Identify merge/split candidates
- [ ] Generate Evidence_PHASE2_Migration.md

---

## 7. Success Criteria

Phase 2 succeeds if:
- ✓ Type registry with plugins works
- ✓ Schema namespaces integrate with Neo4j
- ✓ Pipeline context enables stateful execution
- ✓ Chain selection supports all 5 strategies
- ✓ Resource management prevents overload
- ✓ Error recovery handles transient failures
- ✓ Migration path clear for 38 tools

## 8. Environment Requirements

```bash
# Required environment variables
export GEMINI_API_KEY="your-key-here"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="devpassword"

# Required services
docker ps | grep neo4j  # Must be running

# Python requirements
pip install litellm neo4j pydantic networkx pytest
```

---

## 9. Architecture Decisions from Phase 1 Analysis

Based on Phase 1 learnings, these decisions are made:

1. **Schema Namespaces**: Use Neo4j labels for ontology (e.g., `:Entity:Military`)
2. **LLM Chain Selection**: Let agents handle complex selection with metadata hints
3. **Pipeline Context**: Implement stateful execution with checkpoints
4. **Plugin System**: Most flexible for type extensibility
5. **Tool Granularity**: Support merge/split/wrap patterns with ToolComposer
6. **Smart Retry**: Only for transient errors, fail-fast for permanent

## 10. Key Learnings from Phase 1

### What Works
- Type-based composition with ~10 semantic types
- Automatic chain discovery via NetworkX
- Performance overhead <5% with real services
- Fail-fast philosophy prevents hidden failures

### Remaining Challenges
- Schema compatibility between tools
- State management across chains
- Resource management at scale
- Migration of 38 existing tools

---

*Last Updated: 2025-01-25*
*Phase 1: COMPLETED ✅*
*Phase 2 Timeline: 8 days from start*
*Migration to follow after Phase 2 validation*