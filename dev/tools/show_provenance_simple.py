#!/usr/bin/env python3
"""
Simple Provenance Data Display
Shows what provenance data looks like in KGAS
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime

def show_provenance_data():
    """Display provenance data from the system"""
    print("🔍 KGAS PROVENANCE DATA DISPLAY")
    print("=" * 80)
    print(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check provenance database
    provenance_db = Path("data/provenance.db")
    
    if provenance_db.exists():
        print("📊 PERSISTENT PROVENANCE DATABASE")
        print("-" * 80)
        print(f"Database: {provenance_db}")
        print(f"Size: {provenance_db.stat().st_size / 1024:.1f} KB\n")
        
        try:
            # Connect to database
            conn = sqlite3.connect(provenance_db)
            cursor = conn.cursor()
            
            # Show tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("Database Tables:")
            for table in tables:
                print(f"   • {table[0]}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"     Records: {count}")
            
            # Show some operations
            print("\n\n📝 RECENT OPERATIONS")
            print("-" * 80)
            
            cursor.execute("""
                SELECT operation_id, operation_type, start_time, end_time, status
                FROM operations
                ORDER BY start_time DESC
                LIMIT 5
            """)
            
            operations = cursor.fetchall()
            if operations:
                for op in operations:
                    print(f"\n🔸 Operation: {op[1]}")
                    print(f"   ID: {op[0][:20]}...")
                    print(f"   Started: {op[2]}")
                    print(f"   Status: {op[4]}")
            else:
                print("No operations found in database")
            
            # Show tool statistics
            print("\n\n📦 TOOL STATISTICS")
            print("-" * 80)
            
            cursor.execute("""
                SELECT tool_id, execution_count, success_count, 
                       failure_count, total_execution_time
                FROM tool_statistics
                WHERE execution_count > 0
                ORDER BY execution_count DESC
            """)
            
            tool_stats = cursor.fetchall()
            if tool_stats:
                for tool in tool_stats:
                    success_rate = (tool[2] / tool[1] * 100) if tool[1] > 0 else 0
                    avg_time = tool[4] / tool[1] if tool[1] > 0 else 0
                    
                    print(f"\n📦 {tool[0]}:")
                    print(f"   • Executions: {tool[1]}")
                    print(f"   • Success rate: {success_rate:.1f}%")
                    print(f"   • Average time: {avg_time:.3f}s")
            else:
                print("No tool statistics found in database")
            
            conn.close()
            
        except Exception as e:
            print(f"Error reading database: {e}")
    else:
        print("❌ No provenance database found at data/provenance.db")
    
    # Show provenance data structure
    print("\n\n📋 PROVENANCE DATA STRUCTURE")
    print("=" * 80)
    
    print("""
    What KGAS Provenance Tracks:
    
    1. OPERATIONS
       Every action is tracked as an operation with:
       • Unique operation ID (UUID)
       • Operation type (e.g., tool_execution, document_load, question_processing)
       • Start and end timestamps
       • Input data references ("used")
       • Output data references ("generated")
       • Success/failure status
       • Error messages if failed
       • Agent/component details
       • Custom metadata
    
    2. TOOL EXECUTIONS
       For each tool:
       • Total execution count
       • Success count
       • Failure count
       • Total execution time
       • Average execution time
       • Success rate percentage
    
    3. DATA LINEAGE
       Tracks object transformations:
       • Document → Chunks → Entities → Relationships
       • Each object has a unique reference
       • Operations are linked to objects they use/generate
       • Complete transformation chain preserved
    
    4. AUDIT TRAIL
       Complete history for:
       • Reproducibility of results
       • Performance analysis
       • Error tracking and debugging
       • Compliance and verification
    """)
    
    # Show example provenance flow
    print("\n📊 EXAMPLE PROVENANCE FLOW")
    print("-" * 80)
    print("""
    User asks: "What companies are mentioned?"
    
    1. OPERATION: question_processing
       • ID: op_abc123...
       • Input: {"question": "What companies are mentioned?"}
       • Component: nl_interface
    
    2. OPERATION: tool_execution (T01_PDF_LOADER)
       • ID: op_def456...
       • Input: {"file_path": "document.txt"}
       • Output: {"document_id": "doc_789"}
       • Duration: 0.012s
    
    3. OPERATION: tool_execution (T15A_TEXT_CHUNKER)
       • ID: op_ghi789...
       • Input: {"document_id": "doc_789"}
       • Output: {"chunks": ["chunk_001", "chunk_002"]}
       • Duration: 0.008s
    
    4. OPERATION: tool_execution (T23A_SPACY_NER)
       • ID: op_jkl012...
       • Input: {"chunks": ["chunk_001", "chunk_002"]}
       • Output: {"entities": ["Microsoft", "Google", "Apple"]}
       • Duration: 0.025s
    
    5. OPERATION: response_generation
       • ID: op_mno345...
       • Input: {"entities": ["Microsoft", "Google", "Apple"]}
       • Output: {"response": "I found 3 companies..."}
       • Duration: 0.003s
    
    Total execution time: 0.048s
    Complete audit trail preserved!
    """)
    
    print("\n✅ PROVENANCE DATA DISPLAY COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    show_provenance_data()