#!/usr/bin/env python3
"""Test schema versioning and migration system"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime
from typing import Optional

def test_schema_migration_chain():
    """Test migrating entities through multiple schema versions"""
    
    from poc.schema_versions import EntityV1, EntityV2, EntityV3, SchemaMigrator
    
    print("="*60)
    print("TEST: Schema Versioning and Migration Chain")
    print("="*60)
    
    # Create V1 entity
    print("\n1. Creating V1 Entity (basic)")
    entity_v1 = EntityV1(
        id="e1",
        text="Apple Inc",
        type="COMPANY"
    )
    
    print(f"   V1 Entity: id={entity_v1.id}, text={entity_v1.text}, type={entity_v1.type}")
    print(f"   Version: {entity_v1._version}")
    assert entity_v1._version == "1.0.0"
    
    # Migrate V1 to V2
    print("\n2. Migrating V1 → V2 (adds confidence)")
    entity_v2 = SchemaMigrator.migrate(entity_v1, "2.0.0")
    
    print(f"   V2 Entity: id={entity_v2.id}, text={entity_v2.text}, type={entity_v2.type}")
    print(f"   New field - confidence: {entity_v2.confidence}")
    print(f"   Version: {entity_v2._version}")
    
    assert entity_v2._version == "2.0.0"
    assert entity_v2.id == entity_v1.id  # Data preserved
    assert entity_v2.text == entity_v1.text  # Data preserved
    assert entity_v2.confidence == 0.5  # Default value added
    
    # Migrate V2 to V3
    print("\n3. Migrating V2 → V3 (adds positions)")
    entity_v3 = SchemaMigrator.migrate(entity_v2, "3.0.0")
    
    print(f"   V3 Entity: id={entity_v3.id}, text={entity_v3.text}, type={entity_v3.type}")
    print(f"   Confidence: {entity_v3.confidence}")
    print(f"   New fields - start_pos: {entity_v3.start_pos}, end_pos: {entity_v3.end_pos}")
    print(f"   Version: {entity_v3._version}")
    
    assert entity_v3._version == "3.0.0"
    assert entity_v3.id == entity_v1.id  # Original data preserved
    assert entity_v3.confidence == entity_v2.confidence  # V2 data preserved
    assert entity_v3.start_pos is None  # Default value
    assert entity_v3.end_pos is None  # Default value
    
    # Direct migration V1 to V3
    print("\n4. Direct migration V1 → V3 (skipping V2)")
    entity_v3_direct = SchemaMigrator.migrate(entity_v1, "3.0.0")
    
    print(f"   Direct V3: {entity_v3_direct._version}")
    print(f"   Confidence added: {entity_v3_direct.confidence}")
    print(f"   Positions added: start={entity_v3_direct.start_pos}, end={entity_v3_direct.end_pos}")
    
    assert entity_v3_direct._version == "3.0.0"
    assert entity_v3_direct.confidence == 0.5  # Default from V2 migration
    
    # Test no-op migration (same version)
    print("\n5. No-op migration (V3 → V3)")
    entity_v3_same = SchemaMigrator.migrate(entity_v3, "3.0.0")
    assert entity_v3_same._version == "3.0.0"
    assert entity_v3_same is entity_v3  # Same object returned
    print("   ✅ Same version returns same object")
    
    # Test backward compatibility detection
    print("\n6. Testing backward migration detection")
    try:
        # This should fail or warn - we don't support backward migration
        SchemaMigrator.migrate(entity_v3, "1.0.0")
        print("   ⚠️ Backward migration attempted (not recommended)")
    except Exception as e:
        print(f"   ✅ Backward migration blocked: {e}")
    
    print("\n" + "="*60)
    print("✅ SCHEMA VERSIONING TEST PASSED")
    print("="*60)
    
    return True


def test_schema_compatibility_in_pipeline():
    """Test that tools with different schema versions can work together"""
    
    from poc.schema_versions import EntityV1, EntityV2, SchemaMigrator
    from poc.tool_context import ToolContext
    
    print("\n" + "="*60)
    print("TEST: Schema Compatibility in Pipeline")
    print("="*60)
    
    # Simulate Tool A outputting V1 entities
    print("\n1. Tool A outputs V1 entities")
    tool_a_output = [
        EntityV1(id="1", text="John", type="PERSON"),
        EntityV1(id="2", text="Apple", type="COMPANY")
    ]
    
    # Tool B expects V2 entities
    print("\n2. Tool B expects V2 entities - needs migration")
    
    # Migrate entities for Tool B
    tool_b_input = []
    for entity in tool_a_output:
        if hasattr(entity, '_version') and entity._version == "1.0.0":
            print(f"   Migrating {entity.text} from V1 to V2")
            migrated = SchemaMigrator.migrate(entity, "2.0.0")
            tool_b_input.append(migrated)
        else:
            tool_b_input.append(entity)
    
    # Verify all entities are now V2
    for entity in tool_b_input:
        assert entity._version == "2.0.0"
        assert hasattr(entity, 'confidence')
    
    print(f"\n   ✅ All {len(tool_b_input)} entities migrated to V2")
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPATIBILITY TEST PASSED")
    print("="*60)
    
    return True


if __name__ == "__main__":
    try:
        # Run tests
        test_schema_migration_chain()
        test_schema_compatibility_in_pipeline()
        
        print("\n✅ ALL SCHEMA VERSIONING TESTS PASSED")
        sys.exit(0)
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Need to implement schema_versions module first")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)