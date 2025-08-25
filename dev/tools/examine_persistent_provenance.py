#!/usr/bin/env python3
"""
Examine Persistent Provenance Data
Direct examination of the SQLite provenance database
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def examine_persistent_provenance(db_path="data/provenance.db"):
    """Examine provenance data directly from SQLite database"""
    
    print("🔍 EXAMINING PERSISTENT PROVENANCE DATA")
    print("=" * 60)
    
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"\n❌ Database file not found: {db_path}")
        print("Run some operations with persistence enabled first.")
        return False
    
    print(f"\n📁 Database: {db_path}")
    print(f"   Size: {db_file.stat().st_size} bytes")
    print(f"   Modified: {datetime.fromtimestamp(db_file.stat().st_mtime)}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 1. Check operations table
        print("\n📊 OPERATIONS TABLE:")
        print("-" * 40)
        
        cursor = conn.execute("SELECT COUNT(*) as count FROM operations")
        op_count = cursor.fetchone()['count']
        print(f"Total operations: {op_count}")
        
        if op_count > 0:
            # Show recent operations
            cursor = conn.execute("""
                SELECT operation_id, operation_type, tool_id, status, 
                       started_at, completed_at
                FROM operations 
                ORDER BY started_at DESC 
                LIMIT 10
            """)
            
            print("\nRecent Operations:")
            for row in cursor:
                duration = "N/A"
                if row['completed_at'] and row['started_at']:
                    try:
                        start = datetime.fromisoformat(row['started_at'])
                        end = datetime.fromisoformat(row['completed_at'])
                        duration = f"{(end - start).total_seconds():.2f}s"
                    except:
                        pass
                
                print(f"  {row['operation_id']}: {row['operation_type']} ({row['tool_id']}) - {row['status']} - {duration}")
        
        # 2. Check operation inputs/outputs
        print("\n📥 OPERATION INPUTS:")
        print("-" * 40)
        cursor = conn.execute("SELECT COUNT(*) as count FROM operation_inputs")
        input_count = cursor.fetchone()['count']
        print(f"Total inputs: {input_count}")
        
        if input_count > 0:
            cursor = conn.execute("""
                SELECT operation_id, input_ref, input_type 
                FROM operation_inputs 
                LIMIT 5
            """)
            print("\nSample Inputs:")
            for row in cursor:
                print(f"  {row['operation_id']}: {row['input_ref']} ({row['input_type']})")
        
        print("\n📤 OPERATION OUTPUTS:")
        print("-" * 40)
        cursor = conn.execute("SELECT COUNT(*) as count FROM operation_outputs")
        output_count = cursor.fetchone()['count']
        print(f"Total outputs: {output_count}")
        
        if output_count > 0:
            cursor = conn.execute("""
                SELECT operation_id, output_ref, output_type 
                FROM operation_outputs 
                LIMIT 5
            """)
            print("\nSample Outputs:")
            for row in cursor:
                print(f"  {row['operation_id']}: {row['output_ref']} ({row['output_type']})")
        
        # 3. Check tool statistics
        print("\n🔧 TOOL STATISTICS:")
        print("-" * 40)
        cursor = conn.execute("SELECT * FROM tool_stats ORDER BY total_calls DESC")
        tool_stats = cursor.fetchall()
        
        if tool_stats:
            for row in tool_stats:
                success_rate = (row['successful_calls'] / row['total_calls'] * 100) if row['total_calls'] > 0 else 0
                avg_duration = row['total_duration'] / row['total_calls'] if row['total_calls'] > 0 else 0
                print(f"  {row['tool_id']}:")
                print(f"    Calls: {row['total_calls']} (Success: {row['successful_calls']}, Failed: {row['failed_calls']})")
                print(f"    Success Rate: {success_rate:.1f}%")
                print(f"    Avg Duration: {avg_duration:.3f}s")
                print(f"    Last Used: {row['last_used']}")
        else:
            print("No tool statistics found")
        
        # 4. Check lineage chains
        print("\n🔗 LINEAGE CHAINS:")
        print("-" * 40)
        cursor = conn.execute("SELECT COUNT(*) as count FROM lineage_chains")
        chain_count = cursor.fetchone()['count']
        print(f"Total lineage chains: {chain_count}")
        
        if chain_count > 0:
            cursor = conn.execute("""
                SELECT object_ref, depth, confidence, created_at 
                FROM lineage_chains 
                ORDER BY depth DESC 
                LIMIT 5
            """)
            print("\nDeepest Lineage Chains:")
            for row in cursor:
                print(f"  {row['object_ref']}: depth={row['depth']}, confidence={row['confidence']:.3f}")
        
        # 5. Show data flow example
        if op_count > 0:
            print("\n🔄 DATA FLOW EXAMPLE:")
            print("-" * 40)
            
            # Find an operation with both inputs and outputs
            cursor = conn.execute("""
                SELECT DISTINCT o.operation_id, o.operation_type, o.tool_id
                FROM operations o
                JOIN operation_inputs i ON o.operation_id = i.operation_id
                JOIN operation_outputs out ON o.operation_id = out.operation_id
                LIMIT 1
            """)
            
            flow_op = cursor.fetchone()
            if flow_op:
                op_id = flow_op['operation_id']
                print(f"\nOperation: {flow_op['operation_type']} ({flow_op['tool_id']})")
                
                # Show inputs
                cursor = conn.execute("""
                    SELECT input_ref, input_type 
                    FROM operation_inputs 
                    WHERE operation_id = ?
                """, (op_id,))
                inputs = cursor.fetchall()
                print("  Inputs:")
                for inp in inputs:
                    print(f"    ← {inp['input_ref']} ({inp['input_type']})")
                
                # Show outputs  
                cursor = conn.execute("""
                    SELECT output_ref, output_type 
                    FROM operation_outputs 
                    WHERE operation_id = ?
                """, (op_id,))
                outputs = cursor.fetchall()
                print("  Outputs:")
                for out in outputs:
                    print(f"    → {out['output_ref']} ({out['output_type']})")
        
        # 6. Database schema info
        print("\n📋 DATABASE SCHEMA:")
        print("-" * 40)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table['name']
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  {table_name}: {count} rows")
        
        conn.close()
        
        print("\n✅ Database examination complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error examining database: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_test_databases():
    """Show available test databases"""
    print("\n🗄️ AVAILABLE DATABASES:")
    print("-" * 40)
    
    data_dir = Path("data")
    if data_dir.exists():
        db_files = list(data_dir.glob("*.db"))
        if db_files:
            for db_file in db_files:
                size = db_file.stat().st_size
                modified = datetime.fromtimestamp(db_file.stat().st_mtime)
                print(f"  {db_file}: {size} bytes, modified {modified}")
        else:
            print("  No .db files found in data/ directory")
    else:
        print("  data/ directory does not exist")

if __name__ == "__main__":
    show_test_databases()
    
    # Check different possible database locations
    db_paths = [
        "data/provenance.db",
        "data/test_provenance.db"
    ]
    
    for db_path in db_paths:
        if Path(db_path).exists():
            print(f"\n{'='*60}")
            examine_persistent_provenance(db_path)
            break
    else:
        print("\n❌ No provenance databases found. Run some tests first:")
        print("   python test_provenance_persistence.py")