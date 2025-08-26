# Tool Composition Framework Integration - Implementation Guide

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
│   └── Evidence_Framework_[Task].md    # Current framework integration work only
├── completed/
│   └── Evidence_Phase[1-3]_*.md        # Previous phase work (DO NOT MODIFY)
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"
- Must test with REAL services (Gemini API, Neo4j)

---

## 2. Codebase Structure

### Planning Documents
- `/tool_compatability/poc/PHD_IMPLEMENTATION_PLAN.md` - 12-week PhD thesis plan
- `/tool_compatability/poc/CRITICAL_ISSUES_POC_PLAN.md` - 5 critical issues to solve
- `/docs/architecture/architecture_review_20250808/SIMPLIFIED_INTEGRATION_PLAN.md` - Phases 1-3 ✅ COMPLETE

### Framework Components (POC - Needs Integration)
```
/tool_compatability/poc/
├── framework.py              # 🎯 MAIN: Extensible Tool Composition Framework
├── base_tool.py             # Base class with metrics
├── base_tool_v2.py          # Enhanced with ToolContext support
├── data_types.py            # 10 semantic types
├── tool_context.py          # ✅ Multi-input support (Week 1 feature)
├── schema_versions.py       # ✅ Schema versioning (Week 1 feature)
├── semantic_types.py        # ✅ Semantic compatibility (Week 1 feature)
├── data_references.py       # ✅ Memory management (Week 1 feature)
└── tools/                   # Example tools (mostly mocks - REPLACE WITH REAL)
```

### Production System (Working)
```
/src/
├── core/
│   ├── service_manager.py        # ServiceManager for dependency injection
│   ├── tool_contract.py         # Production tool registry
│   ├── analytics_access.py      # ✅ NEW: Simple analytics access
│   └── neo4j_manager.py         # Neo4j connection management
├── tools/                        # 37+ production tools
│   ├── cross_modal/             # 5 registered cross-modal tools
│   └── phase1/                  # Various analytical tools
├── analytics/                    # Sophisticated analytics (8 components)
│   ├── cross_modal_orchestrator.py  # Orchestrates workflows
│   └── cross_modal_converter.py     # Format conversions
└── agents/
    └── register_tools_for_workflow.py  # Tool registration script
```

### Integration Points
- **ServiceManager**: Central service coordination (`/src/core/service_manager.py`)
- **Tool Registry**: Production registry (`/src/core/tool_contract.py`)
- **Framework Registry**: POC registry (needs bridging)
- **Neo4j**: `bolt://localhost:7687` (neo4j/devpassword)
- **Gemini API**: via litellm, key in `.env`

---

## 3. Current Status

### ✅ Completed (Phases 1-3)
1. **5 cross-modal tools** registered and working
2. **62KB enterprise code** archived
3. **8 analytics components** connected
4. **Framework POC** exists with 4 features implemented

### ❌ Integration Gap
**The framework and production tools don't work together**

### Problem Statement
```python
# Framework expects:          # Production has:
ExtensibleTool               → Various base classes
get_capabilities()           → Different method names  
process(context)             → execute(), run(), process()
ToolContext                  → Direct parameters
Framework registry           → tool_contract registry
```

---

## 4. Task: Tool Composition Framework Integration

### Objective
Create a **bridge** that allows the framework and production tools to work together, enabling dynamic tool composition for arbitrary analytical pipelines.

### Success Criteria
1. One complete chain works: File → Entities → Graph
2. Both registries accessible (federated, not replaced)
3. Real services used (Gemini, Neo4j)
4. Performance overhead < 20%
5. 10+ tools integrated by end of Week 1

---

## 5. Implementation Instructions

### Day 1: Create the Composition Service (8 hours)

#### Task 1.1: Create CompositionService (2 hours)

**File**: Create `/src/core/composition_service.py`

```python
#!/usr/bin/env python3
"""
Composition Service - Bridge between framework and production tools
CRITICAL: This is the convergence point for all tool systems
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ToolFramework, ExtensibleTool
from src.core.tool_contract import get_tool_registry
from src.core.service_manager import ServiceManager
from src.analytics.cross_modal_orchestrator import CrossModalOrchestrator


class CompositionService:
    """Single source of truth for tool composition"""
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize with both framework and production systems"""
        self.service_manager = service_manager or ServiceManager()
        self.framework = ToolFramework()
        self.production_registry = get_tool_registry()
        self.orchestrator = CrossModalOrchestrator(service_manager)
        self.adapter_factory = None  # Will create in Task 1.2
        
        # Metrics for thesis evidence
        self.composition_metrics = {
            'chains_discovered': 0,
            'tools_adapted': 0,
            'execution_time': [],
            'overhead_percentage': []
        }
        
    def register_any_tool(self, tool: Any) -> bool:
        """
        Register ANY tool regardless of interface
        Returns True if successful
        """
        try:
            # Will implement with adapter factory
            if not self.adapter_factory:
                raise NotImplementedError("Adapter factory not yet created")
                
            adapted = self.adapter_factory.wrap(tool)
            self.framework.register_tool(adapted)
            
            self.composition_metrics['tools_adapted'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to register {tool}: {e}")
            return False
            
    def discover_chains(self, input_type: str, output_type: str) -> List[List[str]]:
        """
        Discover all possible chains from both systems
        """
        # Get chains from framework
        framework_chains = self.framework.find_chains(input_type, output_type)
        
        # TODO: Also query production registry
        
        self.composition_metrics['chains_discovered'] += len(framework_chains)
        return framework_chains
        
    def execute_chain(self, chain: List[str], input_data: Any) -> Any:
        """
        Execute a discovered chain with performance tracking
        """
        start_time = time.time()
        
        # Will implement execution logic
        result = None  # Placeholder
        
        execution_time = time.time() - start_time
        self.composition_metrics['execution_time'].append(execution_time)
        
        return result
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get composition metrics for thesis evidence"""
        return self.composition_metrics
```

**Evidence Required**: `evidence/current/Evidence_Framework_CompositionService.md`
- Show file created
- Show it imports successfully
- Show ServiceManager integration

#### Task 1.2: Create Universal Adapter Factory (2 hours)

**File**: Create `/src/core/adapter_factory.py`

```python
#!/usr/bin/env python3
"""
Universal Adapter Factory - Wraps any tool for framework compatibility
"""

import inspect
from typing import Any, Dict, Callable
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType


class UniversalAdapter(ExtensibleTool):
    """Adapts any production tool to framework interface"""
    
    def __init__(self, production_tool: Any):
        self.tool = production_tool
        self.tool_id = getattr(production_tool, 'tool_id', 
                               production_tool.__class__.__name__)
        
        # Detect the execution method
        self.execute_method = self._detect_execute_method()
        
    def _detect_execute_method(self) -> Callable:
        """Find the main execution method"""
        # Try common method names
        for method_name in ['execute', 'run', 'process', '__call__']:
            if hasattr(self.tool, method_name):
                method = getattr(self.tool, method_name)
                if callable(method):
                    return method
        
        raise ValueError(f"No execution method found in {self.tool}")
        
    def get_capabilities(self) -> ToolCapabilities:
        """Generate capabilities from tool inspection"""
        return ToolCapabilities(
            tool_id=self.tool_id,
            name=getattr(self.tool, 'name', self.tool_id),
            description=getattr(self.tool, '__doc__', 'Adapted tool'),
            input_type=self._detect_input_type(),
            output_type=self._detect_output_type(),
        )
        
    def _detect_input_type(self) -> DataType:
        """Detect input type from tool signature or attributes"""
        # Simple detection - enhance as needed
        if hasattr(self.tool, 'input_type'):
            return self.tool.input_type
        return DataType.ANY  # Fallback
        
    def _detect_output_type(self) -> DataType:
        """Detect output type from tool"""
        if hasattr(self.tool, 'output_type'):
            return self.tool.output_type
        return DataType.ANY  # Fallback
        
    def process(self, input_data: Any, context=None) -> ToolResult:
        """Execute the tool with framework interface"""
        try:
            # Call the detected method
            result = self.execute_method(input_data)
            
            # Wrap result in ToolResult
            if isinstance(result, ToolResult):
                return result
            else:
                return ToolResult(success=True, data=result)
                
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class UniversalAdapterFactory:
    """Factory for creating adapters"""
    
    def wrap(self, tool: Any) -> ExtensibleTool:
        """
        Wrap any tool with appropriate adapter
        Returns framework-compatible tool
        """
        # If already framework compatible, return as-is
        if isinstance(tool, ExtensibleTool):
            return tool
            
        # Otherwise wrap with universal adapter
        return UniversalAdapter(tool)
        
    def bulk_wrap(self, tools: List[Any]) -> List[ExtensibleTool]:
        """Wrap multiple tools"""
        return [self.wrap(tool) for tool in tools]
```

**Evidence Required**: `evidence/current/Evidence_Framework_AdapterFactory.md`
- Show factory can wrap a simple tool
- Show it detects execution method
- Show it returns framework-compatible interface

#### Task 1.3: Integrate First Real Tool (2 hours)

**File**: Create `/src/core/test_integration.py`

```python
#!/usr/bin/env python3
"""
Test integration of first real tool through CompositionService
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.composition_service import CompositionService
from src.core.adapter_factory import UniversalAdapterFactory
from src.tools.text_loader import TextLoader  # Real production tool

def test_first_integration():
    """Test TextLoader through composition service"""
    
    print("="*60)
    print("FIRST TOOL INTEGRATION TEST")
    print("="*60)
    
    # 1. Create composition service
    service = CompositionService()
    service.adapter_factory = UniversalAdapterFactory()
    
    # 2. Get a real production tool
    text_loader = TextLoader()
    
    # 3. Register it
    print("\n1. Registering TextLoader...")
    success = service.register_any_tool(text_loader)
    
    if success:
        print("   ✅ TextLoader registered successfully")
    else:
        print("   ❌ Registration failed")
        return False
    
    # 4. Check if discoverable
    print("\n2. Testing discovery...")
    chains = service.discover_chains("FILE", "TEXT")
    
    if chains:
        print(f"   ✅ Found {len(chains)} chains")
        for chain in chains:
            print(f"      {' → '.join(chain)}")
    else:
        print("   ❌ No chains discovered")
    
    # 5. Test execution (if we have a test file)
    test_file = Path("test_data/sample.txt")
    if test_file.exists():
        print("\n3. Testing execution...")
        # This will need implementation in execute_chain
        print("   ⚠️  Execution not yet implemented")
    
    # 6. Show metrics
    print("\n4. Composition Metrics:")
    metrics = service.get_metrics()
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    return True

if __name__ == "__main__":
    success = test_first_integration()
    sys.exit(0 if success else 1)
```

**Evidence Required**: `evidence/current/Evidence_Framework_FirstTool.md`
- Full execution log
- Show TextLoader registered
- Show discovery working
- Show metrics collected

#### Task 1.4: Create Evidence Documentation (1 hour)

Create comprehensive evidence showing Day 1 success.

---

### Day 2: Bridge Both Registries (8 hours)

#### Task 2.1: Create Registry Federation (3 hours)

**File**: Create `/src/core/registry_federation.py`

```python
#!/usr/bin/env python3
"""
Registry Federation - Query both framework and production registries
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ToolFramework
from src.core.tool_contract import get_tool_registry


class FederatedRegistry:
    """
    Federated registry that queries both systems
    Does NOT replace either registry - queries both
    """
    
    def __init__(self, framework: ToolFramework = None):
        self.framework = framework or ToolFramework()
        self.production = get_tool_registry()
        
    def discover_all_chains(self, input_type: str, output_type: str) -> Dict[str, List]:
        """
        Discover chains from both registries
        Returns dict with 'framework', 'production', and 'mixed' chains
        """
        results = {
            'framework': [],
            'production': [],
            'mixed': []
        }
        
        # Get framework chains
        try:
            framework_chains = self.framework.find_chains(input_type, output_type)
            results['framework'] = framework_chains
        except Exception as e:
            print(f"Framework discovery error: {e}")
        
        # Get production chains (needs implementation based on production registry API)
        # TODO: Implement production chain discovery
        
        # Find mixed chains (framework + production tools)
        # TODO: Implement mixed chain discovery
        
        return results
        
    def get_tool(self, tool_id: str) -> Optional[Any]:
        """Get tool from either registry"""
        # Try framework first
        if tool_id in self.framework.tools:
            return self.framework.tools[tool_id]
        
        # Try production
        try:
            return self.production.get_tool(tool_id)
        except:
            return None
            
    def list_all_tools(self) -> Dict[str, List[str]]:
        """List tools from both registries"""
        return {
            'framework': list(self.framework.tools.keys()),
            'production': self.production.list_tools()
        }
```

**Evidence Required**: `evidence/current/Evidence_Framework_Federation.md`
- Show both registries queryable
- Show tool counts from each
- Show no interference between registries

#### Task 2.2: Test Cross-Registry Discovery (2 hours)

Write tests showing tools from both registries can be discovered.

#### Task 2.3: Performance Baseline (3 hours)

Measure overhead of adapter layer vs direct execution.

---

### Day 3-5: Complete Integration Pipeline

#### Task 3.1: Entity Extractor Integration (Day 3)

Integrate EntityExtractor with REAL Gemini API:
- No mocks allowed
- Must extract real entities
- Must show Gemini API response

#### Task 3.2: Graph Builder Integration (Day 4)

Integrate GraphBuilder with REAL Neo4j:
- Must create real nodes
- Must verify with Cypher query
- Show node count before/after

#### Task 3.3: End-to-End Chain (Day 5)

Execute complete chain:
```
TextLoader → EntityExtractor → GraphBuilder
```

Success criteria:
- Real file processed
- Real entities extracted via Gemini
- Real nodes created in Neo4j
- Performance metrics collected

---

## 6. Validation Requirements

### Required Evidence Files

Each day MUST produce evidence:

**Day 1**: `Evidence_Framework_Day1_Complete.md`
- CompositionService created ✓
- AdapterFactory working ✓  
- First tool integrated ✓
- Metrics collected ✓

**Day 2**: `Evidence_Framework_Day2_Federation.md`
- Registry federation working ✓
- Both registries accessible ✓
- No interference proven ✓

**Day 3-5**: `Evidence_Framework_Pipeline_Complete.md`
- Full chain execution log ✓
- Gemini API response shown ✓
- Neo4j nodes verified ✓
- Performance < 20% overhead ✓

### Performance Requirements

```python
# Measure overhead
direct_time = measure_direct_execution()
framework_time = measure_framework_execution()
overhead = (framework_time - direct_time) / direct_time * 100

assert overhead < 20, f"Overhead {overhead}% exceeds 20% limit"
```

---

## 7. Common Issues & Solutions

### Issue: "No module named 'framework'"
```bash
# Add to Python path in your script
sys.path.insert(0, '/home/brian/projects/Digimons/tool_compatability/poc')
```

### Issue: "Neo4j authentication failed"
```bash
export NEO4J_PASSWORD=devpassword
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
```

### Issue: "Gemini API not working"
```bash
# Check .env file
cat /home/brian/projects/Digimons/.env | grep GEMINI
# Key should be there, loaded by python-dotenv
```

---

## 8. Success Metrics

### Day 1 Success
- [ ] CompositionService class created and working
- [ ] At least 1 tool successfully adapted
- [ ] Metrics collection functional

### Day 5 Success  
- [ ] 10+ tools integrated
- [ ] Complete chain executing with real services
- [ ] Performance overhead < 20%
- [ ] All evidence files created

### Week 2 Target
- [ ] 20+ tools in framework
- [ ] Complex DAG workflows executing
- [ ] Ready for uncertainty integration

---

## 9. DO NOT

- ❌ Use mocks or stubs - ONLY real services
- ❌ Claim success without evidence files
- ❌ Replace existing registries - federate them
- ❌ Modify production tools - wrap them
- ❌ Skip performance measurements
- ❌ Hide errors - fail fast with clear messages

---

*Last Updated: 2025-08-26*
*Phase: Tool Composition Framework Integration*
*Prerequisites: Phases 1-3 complete ✅*
*Next: Uncertainty propagation (after framework works)*