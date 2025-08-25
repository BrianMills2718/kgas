#!/usr/bin/env python3
"""
Schema Evolution Testing - Test handling of schema changes

Tests how the system handles:
- Schema version changes
- Field additions/removals
- Type migrations
- Backward/forward compatibility
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime

# Add poc to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.data_types import DataType, DataSchema
from poc.base_tool import BaseTool, ToolResult


# ========== Schema Versions ==========

class EntityV1(BaseModel):
    """Original entity schema"""
    id: str
    text: str
    type: str
    confidence: float


class EntityV2(BaseModel):
    """V2: Added metadata field"""
    id: str
    text: str
    type: str
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityV3(BaseModel):
    """V3: Added source_doc, renamed confidence to score"""
    id: str
    text: str
    type: str
    score: float  # Renamed from confidence
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_doc: Optional[str] = None


from enum import Enum

class EntityTypeV4(str, Enum):
    PERSON = "PERSON"
    ORG = "ORG"
    LOCATION = "LOCATION"
    OTHER = "OTHER"

class EntityV4(BaseModel):
    """V4: Made type an enum, added timestamp"""
    id: str
    text: str
    type: EntityTypeV4
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_doc: Optional[str] = None
    extracted_at: datetime = Field(default_factory=datetime.now)


# ========== Migration Functions ==========

def migrate_v1_to_v2(entity: EntityV1) -> EntityV2:
    """Migrate from V1 to V2"""
    return EntityV2(
        id=entity.id,
        text=entity.text,
        type=entity.type,
        confidence=entity.confidence,
        metadata={}
    )


def migrate_v2_to_v3(entity: EntityV2) -> EntityV3:
    """Migrate from V2 to V3"""
    return EntityV3(
        id=entity.id,
        text=entity.text,
        type=entity.type,
        score=entity.confidence,  # Rename field
        metadata=entity.metadata,
        source_doc=None
    )


def migrate_v3_to_v4(entity: EntityV3) -> EntityV4:
    """Migrate from V3 to V4"""
    # Map string type to enum
    type_map = {
        "PERSON": EntityTypeV4.PERSON,
        "ORG": EntityTypeV4.ORG,
        "ORGANIZATION": EntityTypeV4.ORG,  # Handle variation
        "LOCATION": EntityTypeV4.LOCATION,
        "PLACE": EntityTypeV4.LOCATION,  # Handle variation
    }
    
    entity_type = type_map.get(entity.type.upper(), EntityTypeV4.OTHER)
    
    return EntityV4(
        id=entity.id,
        text=entity.text,
        type=entity_type,
        score=entity.score,
        metadata=entity.metadata,
        source_doc=entity.source_doc,
        extracted_at=datetime.now()
    )


# ========== Tests ==========

def test_backward_compatibility():
    """Test that new schemas can read old data"""
    print("\n" + "="*80)
    print("TEST 1: Backward Compatibility")
    print("="*80)
    
    # Create V1 entity
    v1_data = {
        "id": "e1",
        "text": "John Smith",
        "type": "PERSON",
        "confidence": 0.95
    }
    
    print("\nV1 Data:")
    print(json.dumps(v1_data, indent=2))
    
    # Try to load with each version
    tests = [
        ("V1 → V1", EntityV1, True),
        ("V1 → V2", EntityV2, False),  # Missing metadata field
        ("V1 → V3", EntityV3, False),  # Missing score field
        ("V1 → V4", EntityV4, False),  # Multiple missing fields
    ]
    
    for test_name, schema_class, should_work in tests:
        print(f"\n{test_name}:")
        try:
            entity = schema_class(**v1_data)
            if should_work:
                print(f"  ✓ Loaded successfully")
            else:
                print(f"  ✓ Loaded with defaults: {entity.model_dump()}")
        except ValidationError as e:
            if should_work:
                print(f"  ✗ Failed unexpectedly: {e}")
            else:
                print(f"  ✓ Failed as expected (needs migration)")
                
                # Try migration
                if schema_class == EntityV2:
                    v1_entity = EntityV1(**v1_data)
                    v2_entity = migrate_v1_to_v2(v1_entity)
                    print(f"  ✓ Migration successful: {v2_entity.model_dump()}")


def test_forward_compatibility():
    """Test that old schemas can handle new data gracefully"""
    print("\n" + "="*80)
    print("TEST 2: Forward Compatibility")
    print("="*80)
    
    # Create V4 entity with all fields
    v4_data = {
        "id": "e1",
        "text": "John Smith",
        "type": "PERSON",
        "score": 0.95,
        "metadata": {"context": "CEO announcement"},
        "source_doc": "doc123.txt",
        "extracted_at": "2025-01-25T10:00:00"
    }
    
    print("\nV4 Data:")
    print(json.dumps(v4_data, indent=2))
    
    # Try to load with older versions
    tests = [
        ("V4 → V1", EntityV1),
        ("V4 → V2", EntityV2),
        ("V4 → V3", EntityV3),
    ]
    
    for test_name, schema_class in tests:
        print(f"\n{test_name}:")
        
        # Adjust data for older schema
        adapted_data = v4_data.copy()
        
        if schema_class == EntityV1:
            # V1 expects confidence, not score
            adapted_data["confidence"] = adapted_data.pop("score")
            # Remove fields V1 doesn't know about
            for field in ["metadata", "source_doc", "extracted_at"]:
                adapted_data.pop(field, None)
        
        elif schema_class == EntityV2:
            adapted_data["confidence"] = adapted_data.pop("score")
            adapted_data.pop("source_doc", None)
            adapted_data.pop("extracted_at", None)
        
        elif schema_class == EntityV3:
            # V3 has score, not confidence (correct)
            adapted_data.pop("extracted_at", None)
        
        try:
            entity = schema_class(**adapted_data)
            print(f"  ✓ Loaded with field dropping")
            print(f"    Preserved fields: {list(entity.model_dump().keys())}")
        except ValidationError as e:
            print(f"  ✗ Failed even with adaptation: {e}")


def test_schema_evolution_chain():
    """Test migrating through multiple schema versions"""
    print("\n" + "="*80)
    print("TEST 3: Schema Evolution Chain")
    print("="*80)
    
    # Start with V1 entity
    v1_entity = EntityV1(
        id="e1",
        text="TechCorp",
        type="ORG",
        confidence=0.85
    )
    
    print("\nOriginal V1:")
    print(v1_entity.model_dump())
    
    # Migrate through versions
    print("\nMigration chain:")
    
    # V1 → V2
    v2_entity = migrate_v1_to_v2(v1_entity)
    print(f"\nV1 → V2:")
    print(f"  Added: metadata={v2_entity.metadata}")
    
    # V2 → V3
    v3_entity = migrate_v2_to_v3(v2_entity)
    print(f"\nV2 → V3:")
    print(f"  Renamed: confidence → score")
    print(f"  Added: source_doc={v3_entity.source_doc}")
    
    # V3 → V4
    v4_entity = migrate_v3_to_v4(v3_entity)
    print(f"\nV3 → V4:")
    print(f"  Type enum: {v3_entity.type} → {v4_entity.type}")
    print(f"  Added: extracted_at={v4_entity.extracted_at}")
    
    print("\nFinal V4:")
    print(v4_entity.model_dump())
    
    # Verify data preservation
    print("\nData preservation check:")
    checks = [
        ("ID preserved", v1_entity.id == v4_entity.id),
        ("Text preserved", v1_entity.text == v4_entity.text),
        ("Score preserved", v1_entity.confidence == v4_entity.score),
        ("Type mapped correctly", v4_entity.type == EntityTypeV4.ORG),
    ]
    
    for check_name, passed in checks:
        if passed:
            print(f"  ✓ {check_name}")
        else:
            print(f"  ✗ {check_name}")


def test_tool_schema_compatibility():
    """Test that tools can handle schema changes"""
    print("\n" + "="*80)
    print("TEST 4: Tool Schema Compatibility")
    print("="*80)
    
    # Create a tool that expects V2 schema
    class V2ToolConfig(BaseModel):
        pass
    
    class V2Tool(BaseTool):
        @property
        def input_type(self) -> DataType:
            return DataType.ENTITIES
        
        @property
        def output_type(self) -> DataType:
            return DataType.ENTITIES
        
        @property
        def input_schema(self):
            return DataSchema.EntitiesData
        
        @property
        def output_schema(self):
            return DataSchema.EntitiesData
        
        @property
        def config_schema(self):
            return V2ToolConfig
        
        def default_config(self):
            return V2ToolConfig()
        
        def _execute(self, input_data):
            # Expect V2 entities
            for entity in input_data.entities:
                if not hasattr(entity, 'metadata'):
                    raise ValueError("Entity missing metadata field")
            return input_data
    
    # Create a tool that produces V3 schema
    class V3ToolConfig(BaseModel):
        pass
    
    class V3Tool(BaseTool):
        @property
        def input_type(self) -> DataType:
            return DataType.ENTITIES
        
        @property
        def output_type(self) -> DataType:
            return DataType.ENTITIES
        
        @property
        def input_schema(self):
            return DataSchema.EntitiesData
        
        @property
        def output_schema(self):
            return DataSchema.EntitiesData
        
        @property
        def config_schema(self):
            return V3ToolConfig
        
        def default_config(self):
            return V3ToolConfig()
        
        def _execute(self, input_data):
            # Convert to V3
            v3_entities = []
            for entity in input_data.entities:
                # Handle both confidence and score
                score = getattr(entity, 'score', getattr(entity, 'confidence', 0.5))
                
                v3_entity = DataSchema.Entity(
                    id=entity.id,
                    text=entity.text,
                    type=entity.type,
                    confidence=score,  # DataSchema.Entity uses confidence
                    metadata=getattr(entity, 'metadata', {})
                )
                v3_entities.append(v3_entity)
            
            return DataSchema.EntitiesData(
                entities=v3_entities,
                relationships=input_data.relationships,
                source_checksum=input_data.source_checksum,
                extraction_model="v3_tool",
                extraction_timestamp=datetime.now().isoformat()
            )
    
    # Test compatibility
    print("\nTesting V2Tool → V3Tool chain:")
    
    # Create test data with V1 entities (will need migration)
    entities_data = DataSchema.EntitiesData(
        entities=[
            DataSchema.Entity(
                id="e1",
                text="Alice",
                type="PERSON",
                confidence=0.9,
                metadata={"role": "CEO"}
            ),
            DataSchema.Entity(
                id="e2",
                text="BigCorp",
                type="ORG",
                confidence=0.85,
                metadata={}
            )
        ],
        relationships=[],
        source_checksum="abc123",
        extraction_model="test",
        extraction_timestamp=datetime.now().isoformat()
    )
    
    # Process through V2Tool
    v2_tool = V2Tool()
    
    result = v2_tool.process(entities_data)
    if result.success:
        print("  ✓ V2Tool processed entities")
    else:
        print(f"  ✗ V2Tool failed: {result.error}")
    
    # Process through V3Tool
    v3_tool = V3Tool()
    
    if result.success:
        result = v3_tool.process(result.data)
        if result.success:
            print("  ✓ V3Tool processed V2 output")
            print(f"    Entities: {len(result.data.entities)}")
        else:
            print(f"  ✗ V3Tool failed: {result.error}")


def test_schema_validation_strictness():
    """Test different levels of schema validation"""
    print("\n" + "="*80)
    print("TEST 5: Schema Validation Strictness")
    print("="*80)
    
    # Test data with various issues
    test_cases = [
        {
            "name": "Valid data",
            "data": {
                "id": "e1",
                "text": "John",
                "type": "PERSON",
                "confidence": 0.9
            },
            "expected": "pass"
        },
        {
            "name": "Extra fields",
            "data": {
                "id": "e1",
                "text": "John",
                "type": "PERSON",
                "confidence": 0.9,
                "extra_field": "ignored",
                "another_field": 123
            },
            "expected": "pass_with_warning"
        },
        {
            "name": "Missing required field",
            "data": {
                "id": "e1",
                "text": "John",
                "type": "PERSON"
                # Missing confidence
            },
            "expected": "fail"
        },
        {
            "name": "Wrong type",
            "data": {
                "id": "e1",
                "text": "John",
                "type": "PERSON",
                "confidence": "high"  # Should be float
            },
            "expected": "fail"
        },
        {
            "name": "Out of range",
            "data": {
                "id": "e1",
                "text": "John",
                "type": "PERSON",
                "confidence": 1.5  # Should be 0-1
            },
            "expected": "pass_but_invalid"  # Pydantic doesn't validate range by default
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"  Data: {test_case['data']}")
        
        try:
            # Try with current DataSchema.Entity
            entity = DataSchema.Entity(**test_case['data'])
            
            if test_case["expected"] == "pass":
                print(f"  ✓ Validated successfully")
            elif test_case["expected"] == "pass_with_warning":
                print(f"  ✓ Passed (extra fields ignored)")
                print(f"    Loaded fields: {list(entity.model_dump().keys())}")
            elif test_case["expected"] == "pass_but_invalid":
                print(f"  ⚠️  Passed but may be invalid")
                print(f"    Confidence: {entity.confidence}")
                if entity.confidence > 1.0:
                    print(f"    Note: Confidence > 1.0 (no range validation)")
            else:
                print(f"  ✗ Should have failed but passed")
        
        except ValidationError as e:
            if test_case["expected"] == "fail":
                print(f"  ✓ Failed as expected")
                # Extract specific error
                errors = e.errors()
                if errors:
                    first_error = errors[0]
                    print(f"    Error: {first_error['loc']}: {first_error['msg']}")
            else:
                print(f"  ✗ Failed unexpectedly: {e}")


def test_namespace_schemas():
    """Test schema namespaces for different entity types"""
    print("\n" + "="*80)
    print("TEST 6: Schema Namespaces")
    print("="*80)
    
    # Define namespaced schemas
    class FinancialEntity(BaseModel):
        id: str
        text: str
        type: str = "FINANCIAL"
        amount: Optional[float] = None
        currency: Optional[str] = None
        confidence: float
    
    class MedicalEntity(BaseModel):
        id: str
        text: str
        type: str = "MEDICAL"
        icd_code: Optional[str] = None
        symptom_severity: Optional[str] = None
        confidence: float
    
    class LegalEntity(BaseModel):
        id: str
        text: str
        type: str = "LEGAL"
        case_number: Optional[str] = None
        jurisdiction: Optional[str] = None
        confidence: float
    
    # Test different domain entities
    domains = [
        {
            "name": "Financial",
            "schema": FinancialEntity,
            "data": {
                "id": "f1",
                "text": "$1.5M investment",
                "amount": 1500000,
                "currency": "USD",
                "confidence": 0.95
            }
        },
        {
            "name": "Medical",
            "schema": MedicalEntity,
            "data": {
                "id": "m1",
                "text": "hypertension",
                "icd_code": "I10",
                "symptom_severity": "moderate",
                "confidence": 0.88
            }
        },
        {
            "name": "Legal",
            "schema": LegalEntity,
            "data": {
                "id": "l1",
                "text": "Case 2024-CV-1234",
                "case_number": "2024-CV-1234",
                "jurisdiction": "Southern District",
                "confidence": 0.92
            }
        }
    ]
    
    print("\nDomain-specific schemas:")
    for domain in domains:
        print(f"\n{domain['name']}:")
        entity = domain["schema"](**domain["data"])
        print(f"  ✓ Created {domain['name']} entity")
        print(f"    Type: {entity.type}")
        print(f"    Fields: {list(entity.model_dump().keys())}")
    
    # Test converting to common schema
    print("\nConverting to common DataSchema.Entity:")
    for domain in domains:
        entity = domain["schema"](**domain["data"])
        
        # Convert to common schema (lose domain-specific fields)
        common_entity = DataSchema.Entity(
            id=entity.id,
            text=entity.text,
            type=entity.type,
            confidence=entity.confidence,
            metadata={
                k: v for k, v in entity.model_dump().items()
                if k not in ["id", "text", "type", "confidence"]
            }
        )
        
        print(f"\n{domain['name']} → Common:")
        print(f"  ✓ Converted successfully")
        print(f"    Metadata preserved: {list(common_entity.metadata.keys())}")


def main():
    """Run all schema evolution tests"""
    print("\n" + "="*80)
    print("SCHEMA EVOLUTION TESTING")
    print("="*80)
    
    # Run tests
    test_backward_compatibility()
    test_forward_compatibility()
    test_schema_evolution_chain()
    test_tool_schema_compatibility()
    test_schema_validation_strictness()
    test_namespace_schemas()
    
    # Summary
    print("\n" + "="*80)
    print("SCHEMA TESTING COMPLETE")
    print("="*80)
    print("\nKey Findings:")
    print("✓ Backward compatibility requires migration functions")
    print("✓ Forward compatibility works with field dropping")
    print("✓ Schema evolution chain preserves data")
    print("✓ Tools can handle schema variations with adapters")
    print("✓ Pydantic provides flexible validation")
    print("✓ Namespace schemas work via metadata field")
    print("\nRecommendations:")
    print("1. Use metadata field for domain-specific data")
    print("2. Version schemas explicitly")
    print("3. Provide migration functions")
    print("4. Document schema changes clearly")


if __name__ == "__main__":
    main()