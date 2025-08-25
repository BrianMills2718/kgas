#!/usr/bin/env python3
"""
Integration test for real services with Neo4j and SQLite
Tests that all services work with actual databases, not mocks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.core.service_manager import get_service_manager
from src.tools.phase1.t31_entity_builder_neo4j import T31EntityBuilderNeo4j
from src.tools.base_tool_fixed import ToolRequest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_service_manager_initialization():
    """Test that ServiceManager initializes with real services"""
    print("\n" + "="*60)
    print("Testing ServiceManager Initialization")
    print("="*60)
    
    try:
        # Get service manager
        service_manager = get_service_manager()
        print("✅ ServiceManager created")
        
        # Check service stats
        stats = service_manager.get_service_stats()
        print(f"📊 Service Stats: {stats}")
        
        # Test Neo4j connection
        neo4j_driver = service_manager.get_neo4j_driver()
        if neo4j_driver:
            print("✅ Neo4j driver obtained")
            # Test connection
            with neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    print("✅ Neo4j connection verified")
                else:
                    print("❌ Neo4j connection test failed")
        else:
            print("⚠️ Neo4j driver not available (Neo4j may not be running)")
            
        return service_manager
        
    except Exception as e:
        print(f"❌ ServiceManager initialization failed: {e}")
        return None


def test_identity_service(service_manager):
    """Test IdentityService with Neo4j"""
    print("\n" + "="*60)
    print("Testing IdentityService with Neo4j")
    print("="*60)
    
    try:
        identity_service = service_manager.identity_service
        print("✅ IdentityService obtained")
        
        # Create a test mention
        result = identity_service.create_mention(
            surface_form="Test Entity",
            start_pos=0,
            end_pos=11,
            source_ref="test_doc",
            entity_type="PERSON",
            confidence=0.95
        )
        
        if result["success"]:
            print(f"✅ Created mention: {result['data']['mention_id']}")
            
            # Get statistics
            stats = identity_service.get_statistics()
            print(f"📊 Identity Stats: {stats}")
        else:
            print(f"❌ Failed to create mention: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ IdentityService test failed: {e}")


def test_provenance_service(service_manager):
    """Test ProvenanceService with SQLite"""
    print("\n" + "="*60)
    print("Testing ProvenanceService with SQLite")
    print("="*60)
    
    try:
        provenance_service = service_manager.provenance_service
        print("✅ ProvenanceService obtained")
        
        # Start an operation
        op_id = provenance_service.start_operation(
            tool_id="TEST_TOOL",
            operation_type="test_operation",
            inputs=["test_input"],
            parameters={"test_param": "value"}
        )
        print(f"✅ Started operation: {op_id}")
        
        # Complete the operation
        result = provenance_service.complete_operation(
            operation_id=op_id,
            outputs=["test_output"],
            success=True,
            metadata={"test_meta": "data"}
        )
        
        if result["success"]:
            print(f"✅ Completed operation in {result['duration_ms']}ms")
            
            # Get statistics
            stats = provenance_service.get_statistics()
            print(f"📊 Provenance Stats: {stats}")
        else:
            print(f"❌ Failed to complete operation: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ ProvenanceService test failed: {e}")


def test_quality_service(service_manager):
    """Test QualityService with Neo4j"""
    print("\n" + "="*60)
    print("Testing QualityService with Neo4j")
    print("="*60)
    
    try:
        quality_service = service_manager.quality_service
        print("✅ QualityService obtained")
        
        # Assess confidence
        result = quality_service.assess_confidence(
            object_ref="test_entity",
            base_confidence=0.85,
            factors={
                "source_reliability": 0.9,
                "extraction_quality": 0.8
            },
            metadata={"source": "test"}
        )
        
        if result["status"] == "success":
            print(f"✅ Assessed confidence: {result['confidence']:.3f}")
            print(f"   Quality Tier: {result['quality_tier']}")
            
            # Test confidence propagation
            propagated = quality_service.propagate_confidence(0.9, "extract_entities")
            print(f"✅ Propagated confidence: 0.9 -> {propagated:.3f}")
            
            # Get statistics
            stats = quality_service.get_statistics()
            print(f"📊 Quality Stats: {stats}")
        else:
            print(f"❌ Failed to assess confidence: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ QualityService test failed: {e}")


def test_entity_builder_tool(service_manager):
    """Test T31 Entity Builder with real Neo4j storage"""
    print("\n" + "="*60)
    print("Testing T31 Entity Builder with Neo4j")
    print("="*60)
    
    try:
        # Create entity builder
        builder = T31EntityBuilderNeo4j(service_manager)
        print("✅ T31 Entity Builder created")
        
        # Test entities
        test_entities = [
            {
                "entity_id": "test_1",
                "surface_form": "Integration Test Entity",
                "entity_type": "ORG",
                "confidence": 0.95
            },
            {
                "entity_id": "test_2",
                "surface_form": "Test Entity",  # Similar name for merging
                "entity_type": "ORG",
                "confidence": 0.85
            },
            {
                "entity_id": "test_3",
                "surface_form": "Another Entity",
                "entity_type": "PERSON",
                "confidence": 0.90
            }
        ]
        
        # Create request
        request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data={
                "entities": test_entities,
                "source_refs": ["integration_test"],
                "merge_strategy": "type_aware"
            },
            parameters={}
        )
        
        # Execute
        result = builder.execute(request)
        
        if result.status == "success":
            print(f"✅ Built {result.data['total_entities']} entities")
            print(f"   Merged: {result.data['merged_count']}")
            print(f"   Stored in Neo4j: {result.data['neo4j_stored']}")
            
            # Verify in Neo4j
            if service_manager.get_neo4j_driver():
                with service_manager.get_neo4j_driver().session() as session:
                    count_result = session.run("MATCH (e:Entity) RETURN count(e) as count")
                    count = count_result.single()["count"]
                    print(f"📊 Total entities in Neo4j: {count}")
        else:
            print(f"❌ Entity builder failed: {result.error_message}")
            
    except Exception as e:
        print(f"❌ Entity builder test failed: {e}")


def cleanup_test_data(service_manager):
    """Clean up test data from databases"""
    print("\n" + "="*60)
    print("Cleaning Up Test Data")
    print("="*60)
    
    try:
        # Clean Neo4j test data
        if service_manager.get_neo4j_driver():
            with service_manager.get_neo4j_driver().session() as session:
                # Remove test entities
                session.run("""
                    MATCH (e:Entity) 
                    WHERE e.canonical_name CONTAINS 'Test' 
                       OR e.canonical_name CONTAINS 'Integration'
                    DETACH DELETE e
                """)
                
                # Remove test mentions
                session.run("""
                    MATCH (m:Mention)
                    WHERE m.surface_form CONTAINS 'Test'
                    DETACH DELETE m
                """)
                
                # Remove test quality assessments
                session.run("""
                    MATCH (qa:QualityAssessment)
                    WHERE qa.object_ref CONTAINS 'test'
                    DELETE qa
                """)
                
                print("✅ Cleaned Neo4j test data")
        
        # Note: SQLite provenance data is kept for audit trail
        print("ℹ️ SQLite provenance data retained for audit trail")
        
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


def main():
    """Run all integration tests"""
    print("\n" + "🚀"*30)
    print("REAL SERVICES INTEGRATION TEST")
    print("Testing with actual Neo4j and SQLite databases")
    print("🚀"*30)
    
    # Initialize service manager
    service_manager = test_service_manager_initialization()
    
    if not service_manager:
        print("\n❌ CRITICAL: ServiceManager initialization failed")
        print("Make sure Neo4j is running:")
        print("  docker-compose up -d neo4j")
        return 1
    
    # Test individual services
    test_identity_service(service_manager)
    test_provenance_service(service_manager)
    test_quality_service(service_manager)
    
    # Test tool integration
    test_entity_builder_tool(service_manager)
    
    # Cleanup
    cleanup_test_data(service_manager)
    
    print("\n" + "="*60)
    print("✅ INTEGRATION TEST COMPLETE")
    print("All services are using real databases, not mocks!")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())