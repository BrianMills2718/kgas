# Uncertainty Propagation for Tool Composition Framework

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
│   └── Evidence_Uncertainty_[Task].md    # Current uncertainty work only
├── completed/
│   ├── Evidence_Framework_*.md          # Framework Days 1-7 ✅
│   └── Evidence_Week2_*.md              # Tool integration ✅
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"

---

## 2. Current Goal: Add Uncertainty to Framework

### What We Have ✅
- 20 tools integrated with framework
- Complex DAG chains working
- Real services (Gemini, Neo4j) connected

### What We Need ❌
- Uncertainty propagation through chains
- Reasoning traces for explainability
- Critical services integration
- One complete demo with uncertainty

---

## 3. Codebase Structure

### Planning Documents
- `/tool_compatability/poc/PHD_IMPLEMENTATION_PLAN.md` - 12-week plan
- `/docs/architecture/architecture_review_20250808/SIMPLIFIED_INTEGRATION_PLAN.md` - Integration phases

### Key Entry Points
- `/src/core/composition_service.py` - Main framework bridge
- `/src/core/adapter_factory.py` - Tool adaptation layer
- `/src/core/service_manager.py` - Service coordination
- `/src/core/batch_tool_integration.py` - Tool registration

### Framework Components (POC)
```
/tool_compatability/poc/
├── framework.py          # Core framework
├── data_types.py        # Type definitions (MODIFY THIS)
└── base_tool.py         # Tool base class
```

### Critical Services (Need Integration)
```
/src/core/
├── identity_service.py      # Entity management
├── provenance_service.py    # Operation tracking
├── quality_service.py       # Confidence assessment
└── workflow_state_service.py # Checkpoint management
```

---

## 4. Task: Add Uncertainty to ToolResult

### Objective
Modify the framework to propagate uncertainty scores and reasoning through tool chains.

### Implementation Instructions

#### Step 1: Extend ToolResult with Uncertainty (1 hour)

**File**: Modify `/tool_compatability/poc/data_types.py`

Add these fields to ToolResult class:
```python
from dataclasses import dataclass
from typing import Any, Optional, Dict

@dataclass
class ToolResult:
    success: bool
    data: Any
    error: Optional[str] = None
    uncertainty: float = 0.0  # ADD THIS: 0=certain, 1=uncertain
    reasoning: str = ""       # ADD THIS: Why this uncertainty
    provenance: Dict = None   # ADD THIS: Execution trace
```

**Evidence Required**: `evidence/current/Evidence_Uncertainty_Core.md`
- Show the modified ToolResult class
- Confirm it imports without errors
- Show that existing tools still work

#### Step 2: Update UniversalAdapter to Add Uncertainty (1 hour)

**File**: Modify `/src/core/adapter_factory.py`

Update the process method to ensure uncertainty is always present:
```python
def process(self, input_data: Any, context=None) -> ToolResult:
    """Execute tool and ensure uncertainty is added"""
    try:
        # Get input uncertainty if it exists
        input_uncertainty = 0.0
        if hasattr(input_data, 'uncertainty'):
            input_uncertainty = input_data.uncertainty
        
        # Call the tool
        result = self.execute_method(input_data)
        
        # Ensure result has uncertainty
        if not isinstance(result, ToolResult):
            result = ToolResult(success=True, data=result)
        
        if not hasattr(result, 'uncertainty') or result.uncertainty == 0.0:
            # Add default uncertainty
            result.uncertainty = 0.1  # Default: slightly uncertain
            result.reasoning = "Default uncertainty - tool provided no assessment"
        
        # Simple propagation: increase uncertainty slightly at each step
        if input_uncertainty > 0:
            result.uncertainty = min(1.0, result.uncertainty + (input_uncertainty * 0.1))
            result.reasoning += f" (propagated from input: {input_uncertainty:.2f})"
        
        return result
        
    except Exception as e:
        return ToolResult(
            success=False, 
            data=None,
            error=str(e),
            uncertainty=1.0,  # Failures are maximally uncertain
            reasoning="Error occurred - maximum uncertainty"
        )
```

**Evidence Required**: `evidence/current/Evidence_Uncertainty_Adapter.md`
- Show the modified adapter code
- Test with a simple tool
- Confirm uncertainty propagates

#### Step 3: Test Uncertainty Propagation (2 hours)

**File**: Create `/src/core/test_uncertainty_propagation.py`

```python
#!/usr/bin/env python3
"""
Test uncertainty propagation through tool chains
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.composition_service import CompositionService
from src.core.batch_tool_integration import create_simple_tools_for_testing

def test_linear_propagation():
    """Test uncertainty increases through chain"""
    print("\n" + "="*60)
    print("TEST: Linear Uncertainty Propagation")
    print("="*60)
    
    service = CompositionService()
    
    # Create and register tools
    tools = create_simple_tools_for_testing()
    for tool in tools[:3]:  # Use first 3 tools
        service.register_any_tool(tool)
    
    # Start with certain data
    initial_data = "Test data for uncertainty"
    
    # Execute chain and track uncertainty
    print("\nStep | Tool | Uncertainty | Reasoning")
    print("-" * 60)
    
    current_data = initial_data
    current_uncertainty = 0.0
    
    for i, tool in enumerate(tools[:3], 1):
        result = tool.execute(current_data)
        
        # Check if result has uncertainty
        uncertainty = getattr(result, 'uncertainty', 0.1)
        reasoning = getattr(result, 'reasoning', 'No reasoning provided')
        
        print(f"{i} | {tool.name} | {uncertainty:.2f} | {reasoning[:40]}...")
        
        current_data = result
        current_uncertainty = uncertainty
    
    print(f"\nFinal uncertainty: {current_uncertainty:.2f}")
    
    # Verify uncertainty increased
    if current_uncertainty > 0.0:
        print("✅ Uncertainty propagated through chain")
        return True
    else:
        print("❌ Uncertainty did not propagate")
        return False

def test_branching_uncertainty():
    """Test uncertainty in branching DAG"""
    print("\n" + "="*60)
    print("TEST: Branching Uncertainty")
    print("="*60)
    
    # Test two branches with different uncertainties
    branch1_uncertainty = 0.3
    branch2_uncertainty = 0.5
    
    # Simple average for merge
    merged_uncertainty = (branch1_uncertainty + branch2_uncertainty) / 2
    
    print(f"Branch 1 uncertainty: {branch1_uncertainty:.2f}")
    print(f"Branch 2 uncertainty: {branch2_uncertainty:.2f}") 
    print(f"Merged uncertainty: {merged_uncertainty:.2f}")
    
    if merged_uncertainty == 0.4:
        print("✅ Branching uncertainty correctly merged")
        return True
    else:
        print("❌ Incorrect merge calculation")
        return False

def main():
    """Run uncertainty tests"""
    print("="*60)
    print("UNCERTAINTY PROPAGATION TESTS")
    print("="*60)
    
    tests = [
        test_linear_propagation,
        test_branching_uncertainty
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ Uncertainty propagation working!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

**Evidence Required**: `evidence/current/Evidence_Uncertainty_Propagation.md`
- Full test output showing uncertainty values
- Confirmation that uncertainty increases through chain
- Evidence of reasoning strings

---

## 5. Next Task: Connect ProvenanceService

### Objective
Integrate ProvenanceService to track tool execution paths automatically.

### Implementation Instructions

#### Step 1: Create Service Bridge (1 hour)

**File**: Create `/src/core/service_bridge.py`

```python
#!/usr/bin/env python3
"""
Bridge to connect critical services to framework
"""

from typing import Dict, Any, Optional
from src.core.provenance_service import ProvenanceService
from src.core.service_manager import ServiceManager

class ServiceBridge:
    """Connects framework to critical services"""
    
    def __init__(self, service_manager: ServiceManager = None):
        self.service_manager = service_manager or ServiceManager()
        self._services = {}
        
    def get_provenance_service(self) -> ProvenanceService:
        """Get or create provenance service"""
        if 'provenance' not in self._services:
            self._services['provenance'] = ProvenanceService()
        return self._services['provenance']
    
    def track_execution(self, tool_id: str, input_data: Any, output_data: Any):
        """Track tool execution in provenance"""
        provenance = self.get_provenance_service()
        
        # Record the execution
        provenance.track_operation(
            operation_type="tool_execution",
            tool_id=tool_id,
            input_hash=str(hash(str(input_data)))[:8],
            output_hash=str(hash(str(output_data)))[:8],
            timestamp=time.time()
        )
        
        return provenance.get_current_trace()
```

#### Step 2: Inject Service into Adapter (1 hour)

**File**: Modify `/src/core/adapter_factory.py`

Add service injection to UniversalAdapter:
```python
def __init__(self, production_tool: Any, service_bridge=None):
    self.tool = production_tool
    self.tool_id = getattr(production_tool, 'tool_id', 
                           production_tool.__class__.__name__)
    self.service_bridge = service_bridge  # ADD THIS
    self.execute_method = self._detect_execute_method()

def process(self, input_data: Any, context=None) -> ToolResult:
    """Execute with provenance tracking"""
    try:
        # Track execution start
        if self.service_bridge:
            self.service_bridge.track_execution(
                self.tool_id, 
                input_data, 
                None  # Output not yet known
            )
        
        # Execute tool
        result = self.execute_method(input_data)
        
        # Track execution complete
        if self.service_bridge:
            trace = self.service_bridge.track_execution(
                self.tool_id,
                input_data,
                result
            )
            result.provenance = trace
        
        return result
```

#### Step 3: Test Service Integration (1 hour)

**File**: Create `/src/core/test_service_integration.py`

Write tests to verify ProvenanceService tracks executions properly.

**Evidence Required**: `evidence/current/Evidence_Service_Integration.md`
- Show ProvenanceService connecting
- Demonstrate execution tracking
- Verify provenance appears in ToolResult

---

## 6. Success Criteria

### Minimum Viable Uncertainty
- [ ] ToolResult has uncertainty and reasoning fields
- [ ] Uncertainty propagates through chains
- [ ] ProvenanceService tracks executions
- [ ] One complete pipeline with uncertainty

### Evidence Requirements
For each task, create evidence file showing:
1. Code changes made
2. Test execution output
3. Confirmation feature works

---

## 7. DO NOT

- ❌ Implement complex uncertainty models (keep it simple floats)
- ❌ Optimize performance (MVP first)
- ❌ Add more tools (20 is enough)
- ❌ Use Dempster-Shafer (unless specifically needed)
- ❌ Skip evidence collection

---

## 8. Quick Reference

### Test Current Framework
```bash
python3 src/core/test_complex_chains.py
```

### Test Uncertainty
```bash
python3 src/core/test_uncertainty_propagation.py
```

### Check Evidence
```bash
ls -la evidence/current/Evidence_Uncertainty_*.md
```

---

*Last Updated: 2025-08-26*
*Phase: Uncertainty Integration*
*Status: Adding uncertainty to framework*
*Next: Connect critical services*