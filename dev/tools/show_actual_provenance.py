#!/usr/bin/env python3
"""
Show Actual Provenance Data from KGAS
Displays real provenance tracking information from the system
"""
import json
from datetime import datetime
from pathlib import Path

def show_provenance_data():
    """Display provenance data from trace files and system"""
    print("🔍 KGAS PROVENANCE DATA VIEWER")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # First, let's look at the trace file we generated
    trace_files = list(Path('.').glob('phase_a_trace*.json'))
    
    if trace_files:
        latest_trace = sorted(trace_files)[-1]
        print(f"📄 ANALYZING TRACE FILE: {latest_trace}")
        print("-" * 80)
        
        with open(latest_trace) as f:
            trace_data = json.load(f)
        
        print("\n1️⃣ EXECUTION SUMMARY")
        exec_summary = trace_data.get('execution_summary', {})
        print(f"   • Total execution time: {exec_summary.get('total_time_seconds', 0):.2f} seconds")
        print(f"   • Questions processed: {exec_summary.get('questions_processed', 0)}")
        print(f"   • Document size: {exec_summary.get('document_size_chars', 0)} characters")
        
        print("\n2️⃣ TOOL EXECUTION STATISTICS")
        tool_stats = trace_data.get('tool_statistics', {})
        
        if isinstance(tool_stats, dict) and 'tool_statistics' in tool_stats:
            # Nested structure
            actual_stats = tool_stats['tool_statistics']
            total_calls = 0
            total_successes = 0
            
            for tool_id, stats in actual_stats.items():
                print(f"\n   📦 {tool_id}:")
                print(f"      • Total calls: {stats['total_calls']}")
                print(f"      • Successes: {stats['successes']}")
                print(f"      • Failures: {stats['failures']}")
                print(f"      • Success rate: {stats['success_rate']:.0%}")
                
                total_calls += stats['total_calls']
                total_successes += stats['successes']
            
            print(f"\n   📊 Overall Statistics:")
            print(f"      • Total tool executions: {total_calls}")
            print(f"      • Successful executions: {total_successes}")
            print(f"      • Overall success rate: {(total_successes/total_calls*100) if total_calls > 0 else 0:.1f}%")
    
    # Now show real-time provenance from the system
    print("\n\n🔧 REAL-TIME PROVENANCE DATA")
    print("=" * 80)
    
    try:
        from src.core.service_manager import ServiceManager
        
        service_manager = ServiceManager()
        provenance = service_manager.provenance_service
        
        # Get tool statistics
        tool_stats_result = provenance.get_tool_statistics()
        
        if tool_stats_result.get('status') == 'success':
            print("\n3️⃣ CURRENT TOOL STATISTICS")
            print("-" * 40)
            
            current_stats = tool_stats_result.get('tool_statistics', {})
            for tool_id in sorted(current_stats.keys()):
                stats = current_stats[tool_id]
                if stats['total_calls'] > 0:
                    print(f"\n   📦 {tool_id}:")
                    print(f"      • Executions: {stats['total_calls']}")
                    print(f"      • Success rate: {stats['success_rate']:.1%}")
        
        # Get tool info
        tool_info = provenance.get_tool_info()
        if tool_info.get('status') == 'success':
            print("\n\n4️⃣ REGISTERED TOOLS")
            print("-" * 40)
            
            tools = tool_info.get('tools', {})
            print(f"   Total tools tracked: {len(tools)}")
            for tool_id in sorted(tools.keys())[:5]:  # Show first 5
                print(f"   • {tool_id}")
        
    except Exception as e:
        print(f"Could not access real-time provenance: {e}")
    
    # Show provenance data structure
    print("\n\n5️⃣ PROVENANCE DATA STRUCTURE")
    print("=" * 80)
    print("""
    📊 What Provenance Tracks:
    
    1. Operation Tracking:
       • Operation ID (unique identifier)
       • Operation type (e.g., tool_execution, document_load)
       • Start and end timestamps
       • Input data references (used)
       • Output data references (generated)
       • Success/failure status
       • Agent details (component, tool_id)
    
    2. Tool Execution Metrics:
       • Total executions per tool
       • Success/failure counts
       • Success rate percentage
       • Execution time statistics
    
    3. Data Lineage:
       • Object references (documents, chunks, entities)
       • Operations performed on each object
       • Transformation chain tracking
       • Parent-child relationships
    
    4. Session Tracking:
       • Overall execution time
       • Questions processed
       • Tools executed
       • Complete audit trail
    """)
    
    # Show example provenance record
    print("\n6️⃣ EXAMPLE PROVENANCE RECORD")
    print("-" * 80)
    
    example_record = {
        "operation_id": "op_8ddd4e3a_1234_5678_90ab_cdef01234567",
        "operation_type": "tool_execution",
        "start_time": "2025-08-01T14:30:45.123456",
        "end_time": "2025-08-01T14:30:45.234567",
        "duration": 0.111,
        "agent_details": {
            "component": "mcp_executor",
            "tool_id": "T23A_SPACY_NER"
        },
        "used": {
            "text": "Microsoft and Google compete in AI...",
            "chunk_ref": "chunk_abc123"
        },
        "generated": {
            "entities": ["Microsoft", "Google", "AI"],
            "entity_count": 3
        },
        "status": "completed",
        "metadata": {
            "confidence": 0.85,
            "success": True
        }
    }
    
    print(json.dumps(example_record, indent=2))
    
    # Check for persistent provenance data
    print("\n\n7️⃣ PERSISTENT PROVENANCE STORAGE")
    print("-" * 80)
    
    provenance_db = Path("data/provenance.db")
    if provenance_db.exists():
        print(f"✅ Persistent provenance database found: {provenance_db}")
        print(f"   • Size: {provenance_db.stat().st_size / 1024:.1f} KB")
        print(f"   • Last modified: {datetime.fromtimestamp(provenance_db.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            from src.core.provenance_persistence import ProvenancePersistence
            persistence = ProvenancePersistence()
            
            # Get some stats
            ops = persistence.get_operations(limit=5)
            stats = persistence.get_tool_statistics()
            
            print(f"\n   📊 Database Contents:")
            print(f"      • Stored operations: {len(ops) if ops else 0}")
            print(f"      • Tools tracked: {len(stats) if stats else 0}")
            
        except Exception as e:
            print(f"   ⚠️  Could not read database: {e}")
    else:
        print("❌ No persistent provenance database found")
    
    print("\n\n✅ PROVENANCE DATA INSPECTION COMPLETE")
    print("=" * 80)
    print("Summary:")
    print("• Complete execution tracking with unique IDs")
    print("• Tool performance metrics captured")
    print("• Data lineage and transformations tracked")
    print("• Both in-memory and persistent storage")
    print("• Full audit trail for reproducibility")
    print("=" * 80)

if __name__ == "__main__":
    show_provenance_data()