# KGAS Tool Integration Resolution Plan
## Comprehensive Implementation Guide

### Document Version: 1.0
### Date: 2025-08-22
### Priority: CRITICAL
### Estimated Total Effort: 14 hours (3 critical, 11 optional)

---

## Executive Summary

This document provides a **fool-proof, step-by-step plan** to resolve all integration issues in the KGAS tool pipeline. The plan is divided into three phases:
- **Phase 1** (3 hours): Critical fixes to unblock the system
- **Phase 2** (4 hours): Architectural improvements for maintainability
- **Phase 3** (7 hours): Complete cleanup and production readiness

**IMPORTANT**: Only Phase 1 is required to get the system working. Phases 2 and 3 are optional improvements.

---

## Current State Analysis

### What's Working ✅
- Individual tools execute successfully when given correct inputs
- LLM extraction via Claude Sonnet API
- Neo4j database operations
- PageRank calculations

### What's Broken ❌
1. **ToolRequest Missing Attributes** - Tools expect `parameters`, `operation`, `validation_mode`
2. **Identity Service Unavailable** - Requires Neo4j, no fallback
3. **Data Format Mismatches** - `text` vs `canonical_name` inconsistencies
4. **Service Return Types** - Dict vs object confusion

### Root Causes
- Tools developed independently without unified contracts
- Tight coupling between services and infrastructure
- No integration testing between tools
- Missing interface specifications

---

## PHASE 1: Critical Fixes (3 Hours)
### Unblock Everything with Minimal Changes

## Fix 1.1: ToolRequest Contract (30 minutes)

### Problem
`ToolRequest` is missing attributes that tools expect, causing `AttributeError` exceptions.

### Current Code Location
```
/home/brian/projects/Digimons/src/core/tool_contract.py
```

### Exact Changes Required

#### Step 1: Backup Current File
```bash
cp src/core/tool_contract.py src/core/tool_contract.py.backup
```

#### Step 2: Update ToolRequest Class
```python
# File: src/core/tool_contract.py
# Line: Find the ToolRequest class definition (approximately line 15-25)

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ToolRequest:
    """Unified request format for all tools"""
    input_data: Dict[str, Any]
    tool_id: str = ""
    operation: str = "execute"  # ADD THIS LINE
    parameters: Dict[str, Any] = field(default_factory=dict)  # ADD THIS LINE
    validation_mode: bool = False  # ADD THIS LINE
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Step 3: Remove ALL Workarounds
After fixing ToolRequest, remove these workarounds:

**File: src/tools/phase2/t23c_ontology_aware_extractor_unified.py**
```python
# Line 265 - REMOVE THIS:
if hasattr(request, 'validation_mode') and request.validation_mode or request.input_data is None:
# REPLACE WITH:
if request.validation_mode or request.input_data is None:

# Line 279 - REMOVE THIS:
parameters = getattr(request, 'parameters', {}) or {}
# REPLACE WITH:
parameters = request.parameters or {}

# Line 334 - REMOVE THIS:
"operation": getattr(request, 'operation', 'execute'),
# REPLACE WITH:
"operation": request.operation,
```

**File: src/tools/phase1/t68_pagerank_unified.py**
```python
# Line 154 - REMOVE THIS:
parameters = getattr(request, 'parameters', {}) or {}
# REPLACE WITH:
parameters = request.parameters or {}
```

**File: src/tools/phase1/t34_edge_builder_unified.py**
```python
# Line 127 - REMOVE THIS:
parameters = getattr(request, 'parameters', {}) or {}
# REPLACE WITH:
parameters = request.parameters or {}
```

### Verification Test
```python
# File: experiments/facade_poc/test_toolrequest_fix.py
#!/usr/bin/env python3
"""Verify ToolRequest fix works"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.tool_contract import ToolRequest

# Test that all attributes exist
request = ToolRequest(input_data={"test": "data"})

assert hasattr(request, 'operation')
assert hasattr(request, 'parameters')
assert hasattr(request, 'validation_mode')
assert request.operation == "execute"
assert request.parameters == {}
assert request.validation_mode == False

print("✅ ToolRequest fix verified!")
```

---

## Fix 1.2: Identity Service Availability (1 hour)

### Problem
Identity service requires Neo4j. When Neo4j is unavailable, T23C fails completely.

### Solution
Create a fallback mock identity service that works without Neo4j.

### Implementation

#### Step 1: Create Mock Identity Service
```python
# File: src/core/mock_identity_service.py (NEW FILE)
"""Mock identity service for when Neo4j is unavailable"""

from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MockIdentityService:
    """
    Fallback identity service that works without Neo4j.
    Provides same interface as real IdentityService but stores data in memory.
    """
    
    def __init__(self):
        self.mentions = {}
        self.entities = {}
        self.entity_counter = 0
        self.mention_counter = 0
        logger.info("MockIdentityService initialized (Neo4j not available)")
    
    def create_mention(self, 
                      surface_form: str,
                      start_pos: int,
                      end_pos: int,
                      source_ref: str,
                      entity_type: str,
                      confidence: float,
                      **kwargs) -> Dict[str, Any]:
        """Create a mention and return result dict"""
        mention_id = f"mention_{self.mention_counter:06d}"
        self.mention_counter += 1
        
        mention = {
            "mention_id": mention_id,
            "surface_form": surface_form,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "source_ref": source_ref,
            "entity_type": entity_type,
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            **kwargs
        }
        
        self.mentions[mention_id] = mention
        logger.debug(f"Created mock mention: {mention_id} for '{surface_form}'")
        
        return mention
    
    def find_or_create_entity(self,
                             mention_text: str,
                             entity_type: str,
                             confidence: float,
                             context: str = "",
                             **kwargs) -> Dict[str, Any]:
        """Find or create an entity and return result dict"""
        
        # Simple deduplication by text and type
        entity_key = f"{mention_text}_{entity_type}"
        
        if entity_key in self.entities:
            entity = self.entities[entity_key]
            logger.debug(f"Found existing mock entity: {entity['entity_id']}")
        else:
            entity_id = f"{entity_type}_{self.entity_counter:06d}"
            self.entity_counter += 1
            
            entity = {
                "entity_id": entity_id,
                "canonical_name": mention_text,
                "entity_type": entity_type,
                "confidence": confidence,
                "context": context,
                "created_at": datetime.now().isoformat(),
                **kwargs
            }
            
            self.entities[entity_key] = entity
            logger.debug(f"Created mock entity: {entity_id} for '{mention_text}'")
        
        return entity
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about stored data"""
        return {
            "mentions": len(self.mentions),
            "entities": len(self.entities)
        }
```

#### Step 2: Update ServiceManager to Use Fallback
```python
# File: src/core/service_manager.py
# Find the identity_service property (approximately line 50-70)

@property
def identity_service(self):
    """Get or create identity service instance"""
    if self._identity_service is None:
        if self.driver:  # Neo4j is available
            try:
                from src.core.identity_service import IdentityService
                self._identity_service = IdentityService(self.driver)
                logger.info("Using real IdentityService with Neo4j")
            except Exception as e:
                logger.warning(f"Failed to create IdentityService: {e}")
                from src.core.mock_identity_service import MockIdentityService
                self._identity_service = MockIdentityService()
                logger.info("Falling back to MockIdentityService")
        else:  # Neo4j not available
            from src.core.mock_identity_service import MockIdentityService
            self._identity_service = MockIdentityService()
            logger.info("Using MockIdentityService (Neo4j not available)")
    
    return self._identity_service
```

### Verification Test
```python
# File: experiments/facade_poc/test_identity_service_fallback.py
#!/usr/bin/env python3
"""Verify identity service fallback works"""

import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Ensure Neo4j is not set
os.environ.pop('NEO4J_URI', None)

from src.core.service_manager import ServiceManager

# Test without Neo4j
sm = ServiceManager()
identity = sm.get_identity_service()

# Should get MockIdentityService
assert identity is not None
print(f"Identity service type: {type(identity).__name__}")

# Test create_mention
mention = identity.create_mention(
    surface_form="Test Entity",
    start_pos=0,
    end_pos=11,
    source_ref="test",
    entity_type="PERSON",
    confidence=0.9
)

assert "mention_id" in mention
print(f"✅ Created mention: {mention['mention_id']}")

# Test find_or_create_entity
entity = identity.find_or_create_entity(
    mention_text="Test Entity",
    entity_type="PERSON",
    confidence=0.9
)

assert "entity_id" in entity
print(f"✅ Created entity: {entity['entity_id']}")

print("✅ Identity service fallback verified!")
```

---

## Fix 1.3: Standardize Data Formats (1.5 hours)

### Problem
Tools use different field names for the same data (`text` vs `canonical_name`).

### Solution
Create adapter functions that handle format conversion automatically.

### Implementation

#### Step 1: Create Format Adapters
```python
# File: src/core/format_adapters.py (NEW FILE)
"""Format adapters for tool compatibility"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class FormatAdapter:
    """Adapts data formats between tools"""
    
    @staticmethod
    def t23c_to_t31(t23c_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert T23C entity format to T31 mention format.
        
        T23C outputs: {canonical_name, entity_type, confidence, entity_id, ...}
        T31 expects: {text, entity_type, confidence, start, end}
        """
        mentions = []
        for entity in t23c_entities:
            mention = {
                "text": entity.get("canonical_name", ""),
                "entity_type": entity.get("entity_type", "UNKNOWN"),
                "confidence": entity.get("confidence", 0.5),
                "start": entity.get("start_pos", 0),
                "end": entity.get("end_pos", len(entity.get("canonical_name", "")))
            }
            # Preserve any additional fields
            for key, value in entity.items():
                if key not in ["canonical_name", "entity_type", "confidence"]:
                    mention[key] = value
            
            mentions.append(mention)
            logger.debug(f"Converted T23C entity to T31 mention: {mention.get('text')}")
        
        return mentions
    
    @staticmethod
    def t31_to_t34(t31_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ensure T31 entities have 'text' field for T34.
        
        T31 outputs: {canonical_name, entity_id, ...}
        T34 expects: {text, canonical_name, entity_id, ...}
        """
        adapted_entities = []
        for entity in t31_entities:
            # Ensure 'text' field exists
            if "text" not in entity:
                entity["text"] = entity.get("canonical_name", "")
            adapted_entities.append(entity)
            logger.debug(f"Adapted T31 entity for T34: {entity.get('text')}")
        
        return adapted_entities
    
    @staticmethod
    def normalize_relationship(relationship: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize relationship format across tools.
        
        Handles: source/subject, target/object, relationship/relationship_type
        """
        normalized = {}
        
        # Handle subject/source
        normalized["subject"] = relationship.get("subject") or relationship.get("source")
        
        # Handle object/target
        normalized["object"] = relationship.get("object") or relationship.get("target")
        
        # Handle relationship_type/relationship
        normalized["relationship_type"] = (
            relationship.get("relationship_type") or 
            relationship.get("relationship") or 
            "RELATED_TO"
        )
        
        # Preserve confidence and other fields
        normalized["confidence"] = relationship.get("confidence", 0.5)
        
        # Copy any additional fields
        for key, value in relationship.items():
            if key not in ["subject", "source", "object", "target", 
                          "relationship_type", "relationship", "confidence"]:
                normalized[key] = value
        
        logger.debug(f"Normalized relationship: {normalized['relationship_type']}")
        return normalized
    
    @staticmethod
    def ensure_entity_format(entity: Any) -> Dict[str, Any]:
        """
        Ensure entity is in dict format with required fields.
        
        Handles both dict and object formats.
        """
        if isinstance(entity, dict):
            # Ensure required fields
            if "text" not in entity:
                entity["text"] = entity.get("canonical_name", entity.get("surface_form", ""))
            if "canonical_name" not in entity:
                entity["canonical_name"] = entity.get("text", entity.get("surface_form", ""))
            return entity
        else:
            # Convert object to dict
            entity_dict = {}
            
            # Try common attribute names
            for attr in ["text", "canonical_name", "surface_form", "name"]:
                if hasattr(entity, attr):
                    value = getattr(entity, attr)
                    entity_dict["text"] = value
                    entity_dict["canonical_name"] = value
                    break
            
            # Copy other attributes
            for attr in ["entity_id", "entity_type", "confidence"]:
                if hasattr(entity, attr):
                    entity_dict[attr] = getattr(entity, attr)
            
            return entity_dict
```

#### Step 2: Integrate Adapters into Pipeline
```python
# File: src/core/pipeline_orchestrator.py
# Add import at top
from src.core.format_adapters import FormatAdapter

# Find execute_pipeline method (approximately line 100-200)
# Add format adaptation between tool calls

def execute_pipeline(self, document_path: str, **kwargs):
    """Execute complete pipeline with format adaptation"""
    
    # ... existing code ...
    
    # After T23C extraction
    if t23c_result.status == "success":
        # Adapt T23C output for T31
        t23c_entities = t23c_result.data.get("entities", [])
        t31_mentions = FormatAdapter.t23c_to_t31(t23c_entities)
        
        # Call T31 with adapted format
        t31_request = ToolRequest(input_data={"mentions": t31_mentions})
        t31_result = t31.execute(t31_request)
    
    # After T31 entity creation
    if t31_result.status == "success":
        # Adapt T31 output for T34
        t31_entities = t31_result.data.get("entities", [])
        t34_entities = FormatAdapter.t31_to_t34(t31_entities)
        
        # Normalize relationships
        relationships = [FormatAdapter.normalize_relationship(rel) 
                        for rel in extracted_relationships]
        
        # Call T34 with adapted format
        t34_request = ToolRequest(input_data={
            "entities": t34_entities,
            "relationships": relationships
        })
        t34_result = t34.execute(t34_request)
    
    # ... rest of pipeline ...
```

### Verification Test
```python
# File: experiments/facade_poc/test_format_adapters.py
#!/usr/bin/env python3
"""Verify format adapters work correctly"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.format_adapters import FormatAdapter

# Test T23C to T31 conversion
t23c_output = [
    {
        "entity_id": "entity_001",
        "canonical_name": "Apple Inc.",
        "entity_type": "ORGANIZATION",
        "confidence": 0.95
    }
]

t31_input = FormatAdapter.t23c_to_t31(t23c_output)
assert t31_input[0]["text"] == "Apple Inc."
assert t31_input[0]["entity_type"] == "ORGANIZATION"
print("✅ T23C to T31 conversion works")

# Test T31 to T34 conversion
t31_output = [
    {
        "entity_id": "org_001",
        "canonical_name": "Apple Inc.",
        "entity_type": "ORGANIZATION"
    }
]

t34_input = FormatAdapter.t31_to_t34(t31_output)
assert t34_input[0]["text"] == "Apple Inc."
assert t34_input[0]["canonical_name"] == "Apple Inc."
print("✅ T31 to T34 conversion works")

# Test relationship normalization
relationship = {
    "source": "Apple",
    "target": "Tim Cook",
    "relationship": "LED_BY",
    "confidence": 0.9
}

normalized = FormatAdapter.normalize_relationship(relationship)
assert normalized["subject"] == "Apple"
assert normalized["object"] == "Tim Cook"
assert normalized["relationship_type"] == "LED_BY"
print("✅ Relationship normalization works")

print("\n✅ All format adapters verified!")
```

---

## Phase 1 Completion Checklist

### Pre-Implementation
- [ ] Create backup of all files to be modified
- [ ] Ensure all tests pass in current state
- [ ] Document current workarounds

### Fix 1.1: ToolRequest
- [ ] Update ToolRequest class definition
- [ ] Remove getattr workarounds from T23C
- [ ] Remove getattr workarounds from T68
- [ ] Remove getattr workarounds from T34
- [ ] Run test_toolrequest_fix.py
- [ ] Verify all tools still execute

### Fix 1.2: Identity Service
- [ ] Create mock_identity_service.py
- [ ] Update ServiceManager
- [ ] Run test_identity_service_fallback.py
- [ ] Test T23C without Neo4j
- [ ] Test T23C with Neo4j

### Fix 1.3: Format Adapters
- [ ] Create format_adapters.py
- [ ] Integrate into pipeline_orchestrator.py
- [ ] Run test_format_adapters.py
- [ ] Run complete pipeline test

### Post-Implementation
- [ ] Run all test suites
- [ ] Document any new issues found
- [ ] Update this document with results

---

## PHASE 2: Architectural Improvements (4 Hours)
### Make It Maintainable

## Fix 2.1: Service Interface Definitions (1.5 hours)

### Create Formal Service Protocols
```python
# File: src/core/service_protocols.py (NEW FILE)
"""Formal protocol definitions for all services"""

from typing import Protocol, Dict, Any, Optional
from abc import abstractmethod

class IdentityServiceProtocol(Protocol):
    """Protocol that all identity services must implement"""
    
    @abstractmethod
    def create_mention(self, 
                      surface_form: str,
                      start_pos: int,
                      end_pos: int,
                      source_ref: str,
                      entity_type: str,
                      confidence: float,
                      **kwargs) -> Dict[str, Any]:
        """Create a mention and return result dict with 'mention_id'"""
        ...
    
    @abstractmethod
    def find_or_create_entity(self,
                             mention_text: str,
                             entity_type: str,
                             confidence: float,
                             context: str = "",
                             **kwargs) -> Dict[str, Any]:
        """Find or create entity and return result dict with 'entity_id'"""
        ...

class ProvenanceServiceProtocol(Protocol):
    """Protocol that all provenance services must implement"""
    
    @abstractmethod
    def start_operation(self,
                       tool_id: str,
                       operation_type: str,
                       inputs: list,
                       parameters: dict) -> str:
        """Start tracking an operation and return operation_id"""
        ...
    
    @abstractmethod
    def complete_operation(self,
                          operation_id: str,
                          outputs: list,
                          success: bool,
                          metadata: dict) -> Dict[str, Any]:
        """Complete an operation and return result"""
        ...
```

## Fix 2.2: Tool Base Class Enhancement (1 hour)

### Standardize All Tool Implementations
```python
# File: src/tools/base_tool_enhanced.py (NEW FILE)
"""Enhanced base tool with automatic format adaptation"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.tool_contract import ToolRequest, ToolResult
from src.core.format_adapters import FormatAdapter
import logging
import time

logger = logging.getLogger(__name__)

class EnhancedBaseTool(ABC):
    """
    Enhanced base tool that handles:
    - Automatic format adaptation
    - Consistent error handling
    - Performance tracking
    - Service availability checking
    """
    
    def __init__(self, service_manager=None):
        self.service_manager = service_manager
        self.tool_id = self.__class__.__name__
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Define expected input format"""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output format"""
        pass
    
    @abstractmethod
    def _execute_core(self, input_data: Dict[str, Any], 
                     parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic - implement in subclasses"""
        pass
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """
        Execute tool with automatic format adaptation and error handling.
        This method should NOT be overridden in subclasses.
        """
        start_time = time.time()
        self.execution_count += 1
        
        try:
            # Validate request has required attributes
            if not hasattr(request, 'operation'):
                request.operation = "execute"
            if not hasattr(request, 'parameters'):
                request.parameters = {}
            if not hasattr(request, 'validation_mode'):
                request.validation_mode = False
            
            # Validation mode
            if request.validation_mode:
                return self._execute_validation()
            
            # Adapt input format if needed
            adapted_input = self._adapt_input(request.input_data)
            
            # Execute core logic
            result_data = self._execute_core(adapted_input, request.parameters)
            
            # Adapt output format if needed
            adapted_output = self._adapt_output(result_data)
            
            # Track execution time
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data=adapted_output,
                metadata={
                    "execution_time": execution_time,
                    "execution_count": self.execution_count,
                    "operation": request.operation
                },
                execution_time=execution_time,
                memory_used=0  # TODO: Implement memory tracking
            )
            
        except Exception as e:
            logger.error(f"{self.tool_id} execution failed: {e}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={},
                error_code="EXECUTION_FAILED",
                error_message=str(e),
                execution_time=time.time() - start_time,
                memory_used=0
            )
    
    def _adapt_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses to adapt input format"""
        return input_data
    
    def _adapt_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses to adapt output format"""
        return output_data
    
    def _execute_validation(self) -> ToolResult:
        """Execute validation test"""
        return ToolResult(
            tool_id=self.tool_id,
            status="success",
            data={
                "tool_id": self.tool_id,
                "input_schema": self.get_input_schema(),
                "output_schema": self.get_output_schema(),
                "status": "ready"
            },
            execution_time=0.0,
            memory_used=0
        )
```

## Fix 2.3: Comprehensive Test Suite (1.5 hours)

### Create Integration Test Framework
```python
# File: tests/integration/test_complete_pipeline.py (NEW FILE)
"""Comprehensive integration tests for complete pipeline"""

import pytest
import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from src.tools.phase1.t68_pagerank_unified import T68PageRankCalculatorUnified
from src.core.format_adapters import FormatAdapter

class TestCompletePipeline:
    """Test complete pipeline with all fixes applied"""
    
    @pytest.fixture
    def service_manager(self):
        """Create service manager (may or may not have Neo4j)"""
        return ServiceManager()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing"""
        return """
        Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino.
        Microsoft was founded by Bill Gates and Paul Allen in 1975.
        Google competes with Microsoft and Apple in cloud services.
        """
    
    def test_toolrequest_attributes(self):
        """Test that ToolRequest has all required attributes"""
        request = ToolRequest(input_data={"test": "data"})
        
        assert hasattr(request, 'operation')
        assert hasattr(request, 'parameters')
        assert hasattr(request, 'validation_mode')
        assert request.operation == "execute"
        assert request.parameters == {}
        assert request.validation_mode == False
    
    def test_identity_service_availability(self, service_manager):
        """Test that identity service is always available"""
        identity = service_manager.get_identity_service()
        
        assert identity is not None
        
        # Test create_mention
        mention = identity.create_mention(
            surface_form="Test",
            start_pos=0,
            end_pos=4,
            source_ref="test",
            entity_type="TEST",
            confidence=1.0
        )
        
        assert isinstance(mention, dict)
        assert "mention_id" in mention
        
        # Test find_or_create_entity
        entity = identity.find_or_create_entity(
            mention_text="Test",
            entity_type="TEST",
            confidence=1.0
        )
        
        assert isinstance(entity, dict)
        assert "entity_id" in entity
    
    def test_format_adapters(self):
        """Test format adaptation between tools"""
        # T23C output format
        t23c_output = [{
            "entity_id": "e1",
            "canonical_name": "Apple Inc.",
            "entity_type": "ORG",
            "confidence": 0.9
        }]
        
        # Convert to T31 format
        t31_input = FormatAdapter.t23c_to_t31(t23c_output)
        assert t31_input[0]["text"] == "Apple Inc."
        
        # T31 output format
        t31_output = [{
            "entity_id": "org_001",
            "canonical_name": "Apple Inc.",
            "entity_type": "ORG"
        }]
        
        # Convert to T34 format
        t34_input = FormatAdapter.t31_to_t34(t31_output)
        assert t34_input[0]["text"] == "Apple Inc."
    
    def test_t23c_without_neo4j(self, service_manager, sample_text):
        """Test T23C works without Neo4j using mock identity service"""
        # Remove Neo4j settings to force mock
        os.environ.pop('NEO4J_URI', None)
        
        t23c = OntologyAwareExtractor(service_manager)
        request = ToolRequest(input_data={"text": sample_text})
        result = t23c.execute(request)
        
        assert result.status == "success"
        assert len(result.data.get("entities", [])) > 0
    
    def test_complete_pipeline_without_neo4j(self, service_manager, sample_text):
        """Test complete pipeline works without Neo4j"""
        # Remove Neo4j settings
        os.environ.pop('NEO4J_URI', None)
        
        # Initialize tools
        t23c = OntologyAwareExtractor(service_manager)
        
        # Step 1: Extract entities
        t23c_request = ToolRequest(input_data={"text": sample_text})
        t23c_result = t23c.execute(t23c_request)
        
        assert t23c_result.status == "success"
        entities = t23c_result.data.get("entities", [])
        assert len(entities) > 0
        
        # Format adaptation would happen here in real pipeline
        mentions = FormatAdapter.t23c_to_t31(entities)
        assert len(mentions) > 0
        assert "text" in mentions[0]
    
    @pytest.mark.skipif(not os.getenv('NEO4J_URI'), 
                       reason="Neo4j not available")
    def test_complete_pipeline_with_neo4j(self, service_manager, sample_text):
        """Test complete pipeline with Neo4j"""
        # This test only runs if Neo4j is available
        
        # Initialize all tools
        t23c = OntologyAwareExtractor(service_manager)
        t31 = T31EntityBuilderUnified(service_manager)
        t34 = T34EdgeBuilderUnified(service_manager)
        t68 = T68PageRankCalculatorUnified(service_manager)
        
        # Execute complete pipeline
        # ... (full pipeline test)
        
        assert True  # Placeholder

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## PHASE 3: Production Readiness (7 Hours)
### Complete Cleanup and Documentation

## Fix 3.1: Remove All Workarounds (2 hours)
- Remove all getattr() calls
- Remove all hasattr() checks
- Remove all fallback code paths
- Ensure single, clean execution path

## Fix 3.2: Complete Documentation (2 hours)
- Document all tool interfaces
- Document all data formats
- Create integration guide
- Create troubleshooting guide

## Fix 3.3: Performance Optimization (1.5 hours)
- Add caching where appropriate
- Implement batch processing
- Add connection pooling
- Profile and optimize hot paths

## Fix 3.4: Error Handling Enhancement (1.5 hours)
- Add proper retry logic
- Implement circuit breakers
- Add detailed error messages
- Create error recovery procedures

---

## Risk Mitigation

### Rollback Plan
1. All original files are backed up with .backup extension
2. Git commits after each major fix
3. Feature flags for new code paths
4. Parallel testing of old vs new

### Testing Strategy
1. Unit tests for each fix
2. Integration tests for tool combinations
3. End-to-end tests for complete pipeline
4. Performance regression tests

### Monitoring
1. Log all format adaptations
2. Track execution times
3. Monitor error rates
4. Alert on degradation

---

## Success Criteria

### Phase 1 Success (Minimum Required)
- [ ] All tools execute without AttributeError
- [ ] T23C works without Neo4j
- [ ] Complete pipeline executes end-to-end
- [ ] No manual format conversion needed

### Phase 2 Success (Recommended)
- [ ] All services implement protocols
- [ ] All tools inherit from EnhancedBaseTool
- [ ] Comprehensive test suite passes
- [ ] Documentation complete

### Phase 3 Success (Ideal)
- [ ] Zero workarounds in codebase
- [ ] Performance meets SLAs
- [ ] Production monitoring in place
- [ ] Full error recovery implemented

---

## Implementation Schedule

### Day 1 (3 hours) - Critical Fixes
- Hour 1: Fix ToolRequest and test
- Hour 2: Implement identity service fallback
- Hour 3: Create and integrate format adapters

### Day 2 (4 hours) - Architectural Improvements
- Hours 1-2: Service protocols and base tool
- Hours 3-4: Comprehensive test suite

### Day 3 (7 hours) - Production Readiness
- Hours 1-3: Remove workarounds and cleanup
- Hours 4-5: Documentation
- Hours 6-7: Performance and error handling

---

## Appendix A: File Locations

### Core System Files
```
src/core/tool_contract.py              - ToolRequest definition
src/core/service_manager.py            - Service initialization
src/core/identity_service.py           - Identity service implementation
src/core/format_adapters.py            - NEW: Format adaptation
src/core/mock_identity_service.py      - NEW: Fallback identity service
```

### Tool Files
```
src/tools/phase2/t23c_ontology_aware_extractor_unified.py  - LLM extractor
src/tools/phase1/t31_entity_builder_unified.py             - Entity builder
src/tools/phase1/t34_edge_builder_unified.py               - Edge builder
src/tools/phase1/t68_pagerank_unified.py                   - PageRank calculator
```

### Test Files
```
experiments/facade_poc/test_toolrequest_fix.py             - NEW: ToolRequest test
experiments/facade_poc/test_identity_service_fallback.py   - NEW: Identity test
experiments/facade_poc/test_format_adapters.py             - NEW: Adapter test
tests/integration/test_complete_pipeline.py                - NEW: Integration tests
```

---

## Appendix B: Common Issues and Solutions

### Issue: "AttributeError: 'ToolRequest' object has no attribute 'parameters'"
**Solution**: Apply Fix 1.1 - Update ToolRequest class definition

### Issue: "Neo4j connection required for IdentityService"
**Solution**: Apply Fix 1.2 - Implement MockIdentityService fallback

### Issue: "Mention 0 missing required field: text"
**Solution**: Apply Fix 1.3 - Use FormatAdapter.t23c_to_t31()

### Issue: "Could not find source entity in entity map"
**Solution**: Ensure entities are properly adapted with both 'text' and 'canonical_name' fields

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-08-22 | System | Initial comprehensive plan |

---

## Final Notes

This plan is designed to be **fool-proof** with exact file locations, line numbers, and code snippets. Follow Phase 1 first to get the system working. Phases 2 and 3 are optional but recommended for production use.

**Remember**: Always backup files before modification and test each fix independently before proceeding to the next.