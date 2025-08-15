#!/usr/bin/env python3
"""
Complete Provenance Demonstration
Shows full provenance tracking with actual data
"""
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from src.core.service_manager import ServiceManager
from src.interface.nl_interface import NaturalLanguageInterface

async def demo_with_provenance():
    """Run demo and capture provenance data"""
    print("🔍 PROVENANCE TRACKING DEMONSTRATION")
    print("=" * 80)
    
    # Create test document
    test_file = Path("provenance_demo.txt")
    test_content = """
    Microsoft leads AI innovation with OpenAI partnership.
    Google competes with Bard and DeepMind projects.
    Amazon dominates cloud with AWS infrastructure.
    """
    test_file.write_text(test_content)
    
    provenance_data = {
        "demo_start": datetime.now().isoformat(),
        "operations": [],
        "tool_executions": {}
    }
    
    try:
        # Initialize
        print("🔧 INITIALIZATION PHASE")
        service_manager = ServiceManager()
        provenance = service_manager.provenance_service
        
        # Track initialization
        init_op = provenance.start_operation(
            operation_type="system_initialization",
            used={},
            agent_details={"component": "demo"}
        )
        
        interface = NaturalLanguageInterface(service_manager)
        await interface.initialize()
        
        provenance.complete_operation(
            operation_id=init_op,
            generated={"system": "initialized"},
            metadata={"success": True}
        )
        
        provenance_data["operations"].append({
            "type": "initialization",
            "id": init_op,
            "timestamp": datetime.now().isoformat()
        })
        
        print("✅ System initialized with provenance tracking\n")
        
        # Load document
        print("📄 DOCUMENT LOADING")
        doc_op = provenance.start_operation(
            operation_type="document_load",
            used={"file": str(test_file)},
            agent_details={"component": "nl_interface"}
        )
        
        success = await interface.load_document(str(test_file))
        
        provenance.complete_operation(
            operation_id=doc_op,
            generated={"document_id": "provenance_demo"},
            metadata={"success": success, "size": len(test_content)}
        )
        
        provenance_data["operations"].append({
            "type": "document_load",
            "id": doc_op,
            "timestamp": datetime.now().isoformat(),
            "file": str(test_file),
            "size": len(test_content)
        })
        
        print(f"✅ Document loaded: {test_file}\n")
        
        # Process questions
        print("🤖 QUESTION PROCESSING")
        print("-" * 80)
        
        questions = [
            "What companies are mentioned?",
            "How do they compete in AI?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            
            # Track question
            q_op = provenance.start_operation(
                operation_type="question_processing",
                used={"question": question},
                agent_details={"component": "nl_interface", "question_num": i}
            )
            
            start_time = time.time()
            response = await interface.ask_question(question)
            duration = time.time() - start_time
            
            provenance.complete_operation(
                operation_id=q_op,
                generated={"response_length": len(response)},
                metadata={
                    "duration": duration,
                    "success": True
                }
            )
            
            provenance_data["operations"].append({
                "type": "question",
                "id": q_op,
                "question": question,
                "response_length": len(response),
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ Processed in {duration:.2f}s")
            print(f"Response preview: {response[:100]}...")
        
        # Get tool statistics
        print("\n\n📊 CAPTURED PROVENANCE DATA")
        print("=" * 80)
        
        tool_stats = provenance.get_tool_statistics()
        if tool_stats.get('status') == 'success':
            provenance_data["tool_executions"] = tool_stats.get('tool_statistics', {})
            
            print("\n1️⃣ TOOL EXECUTION STATISTICS")
            print("-" * 40)
            
            for tool_id, stats in provenance_data["tool_executions"].items():
                if stats['total_calls'] > 0:
                    print(f"\n📦 {tool_id}:")
                    print(f"   • Executions: {stats['total_calls']}")
                    print(f"   • Success rate: {stats['success_rate']:.1%}")
                    print(f"   • Successes: {stats['successes']}")
                    print(f"   • Failures: {stats['failures']}")
        
        # Show operation tracking
        print("\n\n2️⃣ OPERATION TRACKING")
        print("-" * 40)
        
        for op in provenance_data["operations"]:
            print(f"\n🔸 {op['type'].upper()}")
            print(f"   • ID: {op['id'][:16]}...")
            print(f"   • Timestamp: {op['timestamp']}")
            
            if 'duration' in op:
                print(f"   • Duration: {op['duration']:.3f}s")
            
            if 'file' in op:
                print(f"   • File: {op['file']}")
            
            if 'question' in op:
                print(f"   • Question: {op['question']}")
        
        # Get detailed operation data
        print("\n\n3️⃣ DETAILED OPERATION DATA")
        print("-" * 40)
        
        # Show one complete operation
        if provenance_data["operations"]:
            last_op_id = provenance_data["operations"][-1]["id"]
            op_details = provenance.get_operation(last_op_id)
            
            if op_details:
                print(f"\nDetailed view of last operation:")
                print(json.dumps(op_details, indent=2, default=str))
        
        # Data lineage
        print("\n\n4️⃣ DATA LINEAGE")
        print("-" * 40)
        
        # Show lineage for document
        doc_lineage = provenance.get_lineage("provenance_demo")
        if doc_lineage.get('status') == 'success':
            lineage = doc_lineage.get('lineage', {})
            if lineage:
                print(f"\nDocument 'provenance_demo' lineage:")
                print(f"   • Total operations: {lineage.get('total_operations', 0)}")
                
                if 'operations' in lineage:
                    for op in lineage['operations'][:3]:
                        print(f"   → {op.get('operation_type', 'unknown')} at {op.get('start_time', 'unknown')}")
        
        # Export complete provenance report
        print("\n\n5️⃣ EXPORTING PROVENANCE REPORT")
        print("-" * 40)
        
        provenance_data["demo_end"] = datetime.now().isoformat()
        provenance_data["summary"] = {
            "total_operations": len(provenance_data["operations"]),
            "questions_processed": len([op for op in provenance_data["operations"] if op["type"] == "question"]),
            "tools_executed": sum(stats['total_calls'] for stats in provenance_data["tool_executions"].values())
        }
        
        report_file = f"provenance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(provenance_data, f, indent=2)
        
        print(f"✅ Complete provenance report saved to: {report_file}")
        
        # Show what's tracked
        print("\n\n6️⃣ PROVENANCE TRACKING SUMMARY")
        print("-" * 40)
        print(f"""
        Tracked in this demo:
        • Operations: {provenance_data['summary']['total_operations']}
        • Questions: {provenance_data['summary']['questions_processed']}
        • Tool executions: {provenance_data['summary']['tools_executed']}
        
        Each operation includes:
        • Unique operation ID
        • Start/end timestamps
        • Input data (used)
        • Output data (generated)
        • Success/failure status
        • Component/agent details
        • Custom metadata
        
        Full audit trail preserved for reproducibility!
        """)
        
        print("\n✅ PROVENANCE DEMONSTRATION COMPLETE")
        print("=" * 80)
        
    finally:
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.WARNING)
    
    asyncio.run(demo_with_provenance())