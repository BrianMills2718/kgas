# Extensible Tool Composition Framework - Service Hardening Phase

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
│   └── Evidence_ServiceHardening_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md                         # Archived completed work
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"
- Must test with REAL services (Gemini API, Neo4j)

---

## 2. Codebase Structure

### Framework Core
```
tool_compatability/poc/
├── framework.py              # ✅ Main extensible framework
├── base_tool.py             # Base tool with metrics
├── data_types.py            # 10 semantic types
├── tool_context.py          # Multi-input support
├── schema_versions.py       # Schema versioning
├── semantic_types.py        # Semantic compatibility
├── data_references.py       # Memory management
└── tools/                   # Real and test tools
```

### Service Integration Layer
```
src/core/
├── composition_service.py    # ✅ Bridge between framework and production
├── adapter_factory.py        # ✅ Universal tool wrapper
├── service_bridge.py         # ✅ Connects critical services
├── identity_service.py       # ✅ Entity tracking (INTEGRATED)
├── provenance_service.py     # ✅ Operation tracking (INTEGRATED)
├── quality_service.py        # ⚠️ Confidence assessment (NOT INTEGRATED)
├── workflow_state_service.py # ⚠️ Checkpoints (NOT INTEGRATED)
└── pii_service.py           # ⚠️ PII protection (VALIDATION REMOVED)
```

### Integration Points
- **Gemini API**: via `litellm` in EntityExtractor
- **Neo4j**: via `neo4j-driver` in GraphBuilder
- **Config**: `.env` file with GEMINI_API_KEY

---

## 3. Current Status

### ✅ Completed (Week 3 Day 1)
1. **IdentityService Integration**: Entities tracked through pipelines
2. **Framework Chain Discovery**: Tools connect automatically
3. **Universal Adapter**: All tools wrapped with service bridge
4. **Basic Tests**: Mock tools working end-to-end

### ⚠️ Critical Issues Found
1. **Silent Failures**: Entity tracking failures don't propagate
2. **Mock-Only Testing**: Never tested with real Gemini/Neo4j
3. **No Persistence**: IdentityService loses data on restart
4. **Validation Removed**: PII service accepts invalid input
5. **Rigid Structure**: Only tracks entities in specific format

---

## 4. PHASE 1: Fix Silent Failures (P0 - 30 minutes)

### Objective
Ensure all failures are loud and visible, never silent.

### Task 1.1: Fix Entity Tracking Failures

**File**: `/src/core/adapter_factory.py`

**Current Problem**:
```python
# Line 138-147: Silent failure!
if isinstance(result.data, dict) and 'entities' in result.data:
    for entity in result.data['entities']:
        if isinstance(entity, dict):
            entity_id = self.service_bridge.track_entity(...)  # Can fail!
            entity['entity_id'] = entity_id  # Continues even on failure
```

**Implementation Instructions**:

1. **Add strict_mode parameter to UniversalAdapter**:
```python
def __init__(self, production_tool: Any, service_bridge=None, strict_mode=True):
    """
    Args:
        strict_mode: If True, fail entire operation on tracking failure
    """
    self.strict_mode = strict_mode  # Default to strict!
```

2. **Modify process method to handle failures**:
```python
# Replace lines 138-147 with:
if isinstance(result.data, dict) and 'entities' in result.data:
    tracking_failures = []
    
    for i, entity in enumerate(result.data['entities']):
        if isinstance(entity, dict):
            try:
                entity_id = self.service_bridge.track_entity(
                    surface_form=entity.get('text', entity.get('name', '')),
                    entity_type=entity.get('type', 'UNKNOWN'),
                    confidence=entity.get('confidence', 0.5),
                    source_tool=self.tool_id
                )
                entity['entity_id'] = entity_id
            except Exception as e:
                # Capture failure details
                tracking_failures.append({
                    'index': i,
                    'entity': entity.get('text', 'unknown'),
                    'error': str(e)
                })
    
    # Handle failures based on mode
    if tracking_failures:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to track {len(tracking_failures)} entities: {tracking_failures}")
        
        if self.strict_mode:
            # FAIL LOUDLY
            return ToolResult(
                success=False,
                data=None,
                error=f"Entity tracking failed for {len(tracking_failures)} entities: {tracking_failures}",
                uncertainty=1.0,
                reasoning="Entity tracking failure - maximum uncertainty"
            )
        else:
            # Add warning but continue
            result.reasoning += f" (WARNING: {len(tracking_failures)} entities not tracked)"
            result.uncertainty = min(1.0, result.uncertainty + 0.2)
```

3. **Create test to verify**:

**File**: Create `/src/core/test_failure_handling.py`
```python
#!/usr/bin/env python3
"""Test that failures are loud, not silent"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_entity_tracking_failure_strict_mode():
    """Verify entity tracking failures cause tool failure in strict mode"""
    from src.core.adapter_factory import UniversalAdapter
    
    # Create mock tool that returns entities
    mock_tool = MagicMock()
    mock_tool.tool_id = 'TestTool'
    mock_tool.get_capabilities.return_value = MagicMock(
        input_type='text', 
        output_type='entities'
    )
    mock_tool.process.return_value = MagicMock(
        success=True,
        data={'entities': [{'text': 'Test Entity', 'type': 'TEST'}]},
        uncertainty=0.1,
        reasoning='test'
    )
    
    # Create service bridge that fails
    mock_bridge = MagicMock()
    mock_bridge.track_entity.side_effect = Exception('Database connection lost!')
    
    # Test strict mode (default)
    adapter = UniversalAdapter(mock_tool, mock_bridge, strict_mode=True)
    result = adapter.process('test input')
    
    assert result.success == False, "Should fail in strict mode"
    assert 'Entity tracking failed' in result.error
    assert result.uncertainty == 1.0
    print("✅ Strict mode: Failures are loud")
    
    # Test lenient mode
    adapter_lenient = UniversalAdapter(mock_tool, mock_bridge, strict_mode=False)
    result_lenient = adapter_lenient.process('test input')
    
    assert result_lenient.success == True, "Should continue in lenient mode"
    assert 'WARNING' in result_lenient.reasoning
    assert result_lenient.uncertainty > 0.1
    print("✅ Lenient mode: Warnings added but continues")

if __name__ == "__main__":
    test_entity_tracking_failure_strict_mode()
    print("\n🎉 Failure handling tests passed!")
```

**Evidence Required**: `evidence/current/Evidence_ServiceHardening_FailureHandling.md`
- Show test output proving failures are caught
- Show both strict and lenient mode behavior
- Include logging output showing warnings

### Task 1.2: Add PII Service Validation

**File**: `/src/core/pii_service.py`

**Replace icontract with explicit validation** (lines 31-35):

```python
def encrypt(self, plaintext: str) -> dict:
    """
    Encrypts the plaintext PII.
    
    Raises:
        TypeError: If plaintext is not a string
        ValueError: If plaintext is empty
    """
    # Manual validation (replaces @icontract decorators)
    if not isinstance(plaintext, str):
        raise TypeError(f"plaintext must be str, got {type(plaintext).__name__}")
    if len(plaintext) == 0:
        raise ValueError("plaintext cannot be empty")
    
    # Existing encryption code continues...
    aesgcm = AESGCM(self._key)
    # ...
```

**Similarly for decrypt** (lines 56-60):
```python
def decrypt(self, ciphertext_b64: str, nonce_b64: str) -> str:
    """
    Decrypts the ciphertext to retrieve the original PII.
    
    Raises:
        ValueError: If inputs are empty or invalid
    """
    # Validation
    if not ciphertext_b64 or not isinstance(ciphertext_b64, str):
        raise ValueError("ciphertext_b64 must be non-empty string")
    if not nonce_b64 or not isinstance(nonce_b64, str):
        raise ValueError("nonce_b64 must be non-empty string")
    
    # Existing decryption code...
```

---

## 5. PHASE 2: Test with Real Services (P1 - 1 hour)

### Objective
Prove the system works with actual Gemini API and Neo4j, not just mocks.

### Task 2.1: Create Real Service Test Suite

**File**: Create `/src/core/test_real_services.py`

```python
#!/usr/bin/env python3
"""
Test with REAL services - NO MOCKS
This is critical for thesis evidence
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tool_compatability" / "poc"))

# Load environment
load_dotenv(project_root / '.env')

def test_real_gemini_api():
    """Test EntityExtractor with actual Gemini API"""
    print("\n" + "="*60)
    print("TEST: Real Gemini API Entity Extraction")
    print("="*60)
    
    # Import real tool
    from tool_compatability.poc.tools.entity_extractor import EntityExtractor
    from src.core.composition_service import CompositionService
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    # Create service and register real tool
    service = CompositionService()
    extractor = EntityExtractor()
    service.register_any_tool(extractor)
    
    # Test text with known entities
    test_text = """
    Apple CEO Tim Cook announced new AI features at WWDC 2024.
    Google's Sundar Pichai responded with Gemini updates.
    Microsoft CEO Satya Nadella discussed Copilot integration.
    """
    
    # Process through real API
    start = time.time()
    result = extractor.process({"text": test_text})
    duration = time.time() - start
    
    if not result.success:
        print(f"❌ Extraction failed: {result.error}")
        return False
    
    # Verify entities found
    entities = result.data.get('entities', [])
    print(f"\n📊 Results:")
    print(f"  - API call duration: {duration:.2f}s")
    print(f"  - Entities found: {len(entities)}")
    
    # Check if tracked
    entities_with_ids = [e for e in entities if 'entity_id' in e]
    print(f"  - Entities with IDs: {len(entities_with_ids)}")
    
    # Show some entities
    print(f"\n  Extracted entities:")
    for entity in entities[:5]:
        id_str = entity.get('entity_id', 'NO ID')
        print(f"    - {entity.get('text')} ({entity.get('type')}) → {id_str}")
    
    return len(entities) > 0

def test_real_neo4j():
    """Test GraphBuilder with actual Neo4j"""
    print("\n" + "="*60)
    print("TEST: Real Neo4j Graph Building")
    print("="*60)
    
    from tool_compatability.poc.tools.graph_builder import GraphBuilder
    from neo4j import GraphDatabase
    
    # Test Neo4j connection
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        driver.verify_connectivity()
        print("✅ Neo4j connected")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("  Try: docker run -d -p 7687:7687 -p 7474:7474 -e NEO4J_AUTH=neo4j/devpassword neo4j")
        return False
    
    # Create test entities
    test_entities = [
        {"text": "Apple", "type": "ORGANIZATION", "confidence": 0.95},
        {"text": "Tim Cook", "type": "PERSON", "confidence": 0.90},
        {"text": "Microsoft", "type": "ORGANIZATION", "confidence": 0.93},
    ]
    
    # Build graph
    builder = GraphBuilder()
    result = builder.process({"entities": test_entities})
    
    if not result.success:
        print(f"❌ Graph building failed: {result.error}")
        return False
    
    # Verify nodes in Neo4j
    with driver.session() as session:
        count_result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = count_result.single()["count"]
    
    driver.close()
    
    print(f"\n📊 Results:")
    print(f"  - Nodes in database: {node_count}")
    print(f"  - Graph result: {result.data}")
    
    return node_count > 0

def test_real_pipeline():
    """Test complete pipeline with real services"""
    print("\n" + "="*60)
    print("TEST: Real End-to-End Pipeline")
    print("="*60)
    
    from src.core.composition_service import CompositionService
    from tool_compatability.poc.tools.text_loader import TextLoader
    from tool_compatability.poc.tools.entity_extractor import EntityExtractor
    from tool_compatability.poc.tools.graph_builder import GraphBuilder
    from data_types import DataType
    
    # Create test file
    test_file = Path("test_data/real_test.txt")
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("""
    In 2024, major tech companies are investing heavily in AI.
    Apple's Tim Cook unveiled Apple Intelligence at WWDC.
    Google CEO Sundar Pichai announced Gemini 2.0.
    Microsoft's Satya Nadella integrated AI into Office 365.
    """)
    
    # Setup composition service
    service = CompositionService()
    
    # Register REAL tools
    service.register_any_tool(TextLoader())
    service.register_any_tool(EntityExtractor())
    service.register_any_tool(GraphBuilder())
    
    # Find chain
    chains = service.find_chains(DataType.FILE, DataType.GRAPH)
    if not chains:
        print("❌ No chains found")
        return False
    
    chain = chains[0]
    print(f"  Chain: {' → '.join(chain)}")
    
    # Execute with timing
    start = time.time()
    result = service.execute_chain(chain, str(test_file))
    duration = time.time() - start
    
    if not result.success:
        print(f"❌ Pipeline failed: {result.error}")
        return False
    
    print(f"\n📊 Pipeline Metrics:")
    print(f"  - Total duration: {duration:.2f}s")
    print(f"  - Final uncertainty: {result.uncertainty:.3f}")
    print(f"  - Reasoning: {result.reasoning}")
    
    # Check for thesis evidence
    metrics = service.get_metrics()
    print(f"\n📈 Thesis Evidence:")
    print(f"  - Tools adapted: {metrics['tools_adapted']}")
    print(f"  - Chains discovered: {metrics['chains_discovered']}")
    print(f"  - Execution times: {metrics['execution_time']}")
    
    return True

def main():
    """Run all real service tests"""
    print("="*60)
    print("REAL SERVICE INTEGRATION TESTS")
    print("NO MOCKS - ACTUAL APIS")
    print("="*60)
    
    tests = [
        ("Gemini API", test_real_gemini_api),
        ("Neo4j Database", test_real_neo4j),
        ("Full Pipeline", test_real_pipeline),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("REAL SERVICE TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All real service tests passed!")
        print("THESIS EVIDENCE: System works with actual services")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Cannot claim real-world viability without these passing")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

**Evidence Required**: `evidence/current/Evidence_ServiceHardening_RealServices.md`
- Full execution log from test run
- Actual Gemini API response times
- Neo4j node counts
- End-to-end pipeline timing
- NO MOCKS - must show real API calls

---

## 6. PHASE 3: Service Configuration (45 minutes)

### Task 3.1: Add Configuration Support

**File**: Update `/src/core/service_bridge.py`

Add configuration support to ServiceBridge:

```python
def __init__(self, service_manager: ServiceManager = None, config: Dict = None):
    """
    Initialize with optional configuration
    
    Args:
        config: Dictionary with service configurations
            Example: {
                'identity': {'persistence': True, 'db_path': 'identity.db'},
                'provenance': {'backend': 'sqlite'}
            }
    """
    self.service_manager = service_manager or ServiceManager()
    self._services = {}
    self.config = config or {}

def get_identity_service(self) -> IdentityService:
    """Get or create configured identity service"""
    if 'identity' not in self._services:
        identity_config = self.config.get('identity', {})
        
        # Configure based on settings
        if identity_config.get('persistence', False):
            db_path = identity_config.get('db_path', 'data/identity.db')
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self._services['identity'] = IdentityService(
                enable_persistence=True,
                db_path=db_path
            )
            print(f"✅ IdentityService with persistence: {db_path}")
        else:
            self._services['identity'] = IdentityService()
            print("⚠️ IdentityService without persistence (in-memory only)")
    
    return self._services['identity']
```

**File**: Create `/config/services.yaml`
```yaml
# Service configuration
services:
  identity:
    persistence: true
    db_path: "data/identity.db"
    embeddings: false  # Requires OpenAI API key
    
  provenance:
    backend: "sqlite"
    db_path: "data/provenance.db"
    
  quality:
    thresholds:
      high_confidence: 0.8
      medium_confidence: 0.5
      low_confidence: 0.2
      
  workflow:
    checkpoint_dir: "data/checkpoints"
    auto_save: true
    save_interval: 300  # seconds
```

**File**: Create `/src/core/config_loader.py`
```python
"""Load service configuration"""
import yaml
from pathlib import Path

def load_service_config(config_path: str = "config/services.yaml") -> dict:
    """Load service configuration from YAML"""
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️ No config file at {config_path}, using defaults")
        return {}
    
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    return config.get('services', {})
```

**Update CompositionService** to use configuration:
```python
def __init__(self, service_manager: ServiceManager = None, config_path: str = None):
    """Initialize with configuration"""
    from src.core.config_loader import load_service_config
    
    self.service_manager = service_manager or ServiceManager()
    
    # Load configuration
    config = load_service_config(config_path) if config_path else {}
    
    # Create service bridge with config
    self.service_bridge = ServiceBridge(self.service_manager, config)
    
    # ... rest of initialization
```

---

## 7. Success Criteria

Each phase must produce evidence files showing:

### Phase 1: Failure Handling
- [ ] Test showing strict mode fails loudly
- [ ] Test showing lenient mode adds warnings
- [ ] PII validation rejecting empty strings

### Phase 2: Real Services  
- [ ] Gemini API actually called (show response times)
- [ ] Neo4j nodes actually created (show counts)
- [ ] End-to-end pipeline with real services

### Phase 3: Configuration
- [ ] Config loaded from YAML
- [ ] Persistence working (survives restart)
- [ ] Different configs produce different behavior

---

## 8. Testing Commands

```bash
# Phase 1: Test failure handling
python3 src/core/test_failure_handling.py

# Phase 2: Test real services (requires .env with GEMINI_API_KEY)
python3 src/core/test_real_services.py

# Phase 3: Test configuration
python3 -c "
from src.core.composition_service import CompositionService
cs = CompositionService(config_path='config/services.yaml')
print('Config loaded:', cs.service_bridge.config)
"

# Run all integration tests
python3 src/core/test_identity_integration.py
```

---

## 9. Troubleshooting

### If Gemini API fails
```bash
# Check API key
cat .env | grep GEMINI

# Test directly with curl
curl -X POST \
  https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: YOUR_KEY" \
  -d '{"contents":[{"parts":[{"text":"Extract entities from: Apple CEO Tim Cook"}]}]}'
```

### If Neo4j fails
```bash
# Start Neo4j container
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest

# Test connection
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
driver.verify_connectivity()
print('✅ Connected')
"
```

---

*Last Updated: 2025-08-26*
*Phase: Service Hardening*
*Priority: Fix silent failures, test with real services*
*Next: QualityService and WorkflowStateService integration*