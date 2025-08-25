#!/usr/bin/env python3
"""
Examine Provenance Data Using ProvenanceService API
Shows how to query provenance data programmatically
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

from src.core.provenance_service import ProvenanceService
import json

def examine_provenance_with_api():
    """Examine provenance data using the ProvenanceService API"""
    
    print("🔍 EXAMINING PROVENANCE DATA VIA API")
    print("=" * 60)
    
    # Create service with persistence enabled
    print("\n1. Loading ProvenanceService with persistence...")
    provenance = ProvenanceService(
        persistence_enabled=True, 
        persistence_path="data/test_provenance.db"
    )
    
    print(f"   Service status: {provenance.service_status}")
    print(f"   Operations loaded: {len(provenance.operations)}")
    print(f"   Objects tracked: {len(provenance.object_to_operations)}")
    
    # 2. Show all operations
    print("\n2. All Operations:")
    print("-" * 40)
    for op_id, operation in provenance.operations.items():
        print(f"\n   Operation: {op_id}")
        print(f"     Type: {operation.operation_type}")
        print(f"     Agent: {operation.agent}")
        print(f"     Status: {operation.status}")
        print(f"     Started: {operation.started_at}")
        print(f"     Completed: {operation.completed_at}")
        print(f"     Inputs: {list(operation.used.keys())}")
        print(f"     Outputs: {operation.generated}")
        
        if operation.completed_at and operation.started_at:
            duration = (operation.completed_at - operation.started_at).total_seconds()
            print(f"     Duration: {duration:.3f}s")
    
    # 3. Query lineage for objects
    print("\n3. Object Lineage:")
    print("-" * 40)
    for obj_ref in provenance.object_to_operations.keys():
        print(f"\n   Object: {obj_ref}")
        
        # Get lineage
        lineage = provenance.get_lineage(obj_ref)
        if lineage['status'] == 'success':
            print(f"     Depth: {lineage['depth']}")
            print(f"     Confidence: {lineage['confidence']:.3f}")
            print(f"     Operations: {len(lineage['lineage'])}")
            
            for i, op in enumerate(lineage['lineage']):
                print(f"       {i+1}. {op['operation_type']} ({op['agent'].get('tool_id', 'Unknown')})")
        else:
            print(f"     Status: {lineage['status']}")
    
    # 4. Tool statistics
    print("\n4. Tool Statistics:")
    print("-" * 40)
    stats = provenance.get_tool_statistics()
    if stats['status'] == 'success':
        for tool_id, tool_stats in stats['tool_statistics'].items():
            print(f"\n   {tool_id}:")
            print(f"     Total calls: {tool_stats['total_calls']}")
            print(f"     Successes: {tool_stats['successes']}")
            print(f"     Failures: {tool_stats['failures']}")
            print(f"     Success rate: {tool_stats['success_rate']:.1%}")
    
    # 5. Get operations for specific objects
    print("\n5. Operations per Object:")
    print("-" * 40)
    for obj_ref in list(provenance.object_to_operations.keys())[:3]:  # First 3 objects
        operations = provenance.get_operations_for_object(obj_ref)
        print(f"\n   {obj_ref}: {len(operations)} operations")
        for op in operations:
            print(f"     - {op['operation_type']} ({op.get('duration_seconds', 'N/A')}s)")
    
    # 6. Query operations from persistence directly
    if provenance.persistence:
        print("\n6. Direct Persistence Queries:")
        print("-" * 40)
        
        # Query by tool
        t01_ops = provenance.persistence.query_operations(tool_id='T01')
        print(f"   T01 operations: {len(t01_ops)}")
        
        t15a_ops = provenance.persistence.query_operations(tool_id='T15A')  
        print(f"   T15A operations: {len(t15a_ops)}")
        
        # Query successful operations
        success_ops = provenance.persistence.query_operations(status='completed')
        print(f"   Successful operations: {len(success_ops)}")
        
        # Get tool statistics from persistence
        db_stats = provenance.persistence.get_tool_statistics()
        print(f"   Tools in database: {list(db_stats.keys())}")
    
    # 7. Export data
    print("\n7. Export Example:")
    print("-" * 40)
    export_success = provenance.export_provenance_data("data/provenance_export_api.json")
    print(f"   Export successful: {export_success}")
    
    if export_success:
        # Show export contents
        try:
            with open("data/provenance_export_api.json", 'r') as f:
                export_data = json.load(f)
                print(f"   Exported operations: {len(export_data['operations'])}")
                print(f"   Exported lineage chains: {len(export_data['lineage_chains'])}")
                print(f"   Exported tool stats: {len(export_data['tool_stats'])}")
        except Exception as e:
            print(f"   Error reading export: {e}")
    
    print("\n✅ API examination complete!")
    return True

if __name__ == "__main__":
    examine_provenance_with_api()