#!/usr/bin/env python3
"""
Examine Provenance Data from Vertical Slice Execution
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import json
from datetime import datetime

def examine_provenance():
    """Examine provenance data from tool executions"""
    
    print("🔍 PROVENANCE EXAMINATION")
    print("=" * 60)
    
    try:
        from src.core.service_manager import ServiceManager
        
        # Get provenance service
        sm = ServiceManager()
        provenance = sm.provenance_service
        
        print(f"\n📊 Provenance Service Status: {provenance.service_status}")
        print(f"Total operations tracked: {len(provenance.operations)}")
        
        # 1. Show all operations
        print("\n📋 ALL TRACKED OPERATIONS:")
        print("-" * 60)
        
        for op_id, operation in provenance.operations.items():
            print(f"\nOperation ID: {op_id}")
            print(f"  Type: {operation.operation_type}")
            print(f"  Agent: {operation.agent}")
            print(f"  Status: {operation.status}")
            print(f"  Started: {operation.started_at}")
            if operation.completed_at:
                duration = (operation.completed_at - operation.started_at).total_seconds()
                print(f"  Duration: {duration:.2f}s")
            print(f"  Inputs: {list(operation.used.keys()) if operation.used else 'None'}")
            print(f"  Outputs: {operation.generated}")
            if operation.error_message:
                print(f"  Error: {operation.error_message}")
        
        # 2. Show lineage chains
        print("\n🔗 LINEAGE CHAINS:")
        print("-" * 60)
        
        # Get all objects that have operations
        all_objects = set()
        for op in provenance.operations.values():
            all_objects.update(op.generated)
        
        for obj_ref in sorted(all_objects):
            if obj_ref in provenance.object_to_operations:
                print(f"\nObject: {obj_ref}")
                op_ids = provenance.object_to_operations[obj_ref]
                print(f"  Created by {len(op_ids)} operations: {list(op_ids)}")
                
                # Try to get lineage
                try:
                    lineage = provenance.get_lineage(obj_ref)
                    if lineage:
                        print(f"  Lineage depth: {lineage.get('depth', 'Unknown')}")
                        print(f"  Chain confidence: {lineage.get('confidence', 'Unknown')}")
                except:
                    pass
        
        # 3. Show tool statistics
        print("\n📊ub001 TOOL STATISTICS:")
        print("-" * 60)
        
        for tool_id, stats in provenance.tool_stats.items():
            print(f"\nTool: {tool_id}")
            print(f"  Total calls: {stats.get('calls', 0)}")
            print(f"  Successes: {stats.get('successes', 0)}")
            print(f"  Failures: {stats.get('failures', 0)}")
            if stats.get('calls', 0) > 0:
                success_rate = (stats.get('successes', 0) / stats.get('calls', 0)) * 100
                print(f"  Success rate: {success_rate:.1f}%")
        
        # 4. Show data flow
        print("\n🔄 DATA FLOW TRACE:")
        print("-" * 60)
        
        # Find document operations
        doc_ops = [op for op in provenance.operations.values() 
                   if 'document' in str(op.generated).lower()]
        
        if doc_ops:
            print("\nDocument Processing Flow:")
            for op in sorted(doc_ops, key=lambda x: x.started_at):
                print(f"  {op.started_at.strftime('%H:%M:%S')} - {op.agent.get('tool_id', 'Unknown')}: {op.operation_type}")
                if op.generated:
                    print(f"    → Generated: {op.generated[0]}")
        
        # 5. Performance metrics
        if provenance.performance_metrics:
            print("\n⚡ PERFORMANCE METRICS:")
            print("-" * 60)
            metrics = provenance.performance_metrics
            print(f"  Total operations: {metrics.get('total_operations', 0)}")
            if metrics.get('operation_durations'):
                avg_duration = sum(metrics['operation_durations']) / len(metrics['operation_durations'])
                print(f"  Average operation duration: {avg_duration:.3f}s")
        
        # 6. Generate audit report
        print("\n📄 AUDIT TRAIL SUMMARY:")
        print("-" * 60)
        
        # Count operations by type
        op_types = {}
        for op in provenance.operations.values():
            op_type = op.operation_type
            op_types[op_type] = op_types.get(op_type, 0) + 1
        
        print("\nOperations by type:")
        for op_type, count in sorted(op_types.items()):
            print(f"  {op_type}: {count}")
        
        # Count operations by status
        statuses = {}
        for op in provenance.operations.values():
            status = op.status
            statuses[status] = statuses.get(status, 0) + 1
        
        print("\nOperations by status:")
        for status, count in sorted(statuses.items()):
            print(f"  {status}: {count}")
        
        print("\n✅ Provenance examination complete!")
        
        return {
            "total_operations": len(provenance.operations),
            "total_objects": len(all_objects),
            "tool_count": len(provenance.tool_stats),
            "success_rate": sum(s.get('successes', 0) for s in provenance.tool_stats.values()) / 
                           max(1, sum(s.get('calls', 0) for s in provenance.tool_stats.values())) * 100
        }
        
    except Exception as e:
        print(f"\n❌ Error examining provenance: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = examine_provenance()
    if result:
        print(f"\n📦 Summary: {json.dumps(result, indent=2)}")
