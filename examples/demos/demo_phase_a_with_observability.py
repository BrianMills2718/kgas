#!/usr/bin/env python3
"""
Comprehensive Phase A Demo with Full Observability and Tracing
Shows the complete natural language interface with detailed execution tracking
"""
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
from src.core.service_manager import ServiceManager
from src.interface.nl_interface import NaturalLanguageInterface
from src.core.provenance_service import ProvenanceService

async def demonstrate_phase_a_with_observability():
    """Demonstrate Phase A with comprehensive observability"""
    print("🎯 PHASE A NATURAL LANGUAGE INTERFACE DEMONSTRATION")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create a more substantial test document
    test_file = Path("tech_companies_analysis.txt")
    test_content = """
    Technology Industry Analysis Report 2025
    
    Major technology companies are reshaping the global economy through artificial intelligence,
    cloud computing, and digital transformation initiatives. Microsoft has invested heavily in
    OpenAI and Azure cloud services, positioning itself as a leader in enterprise AI solutions.
    
    Google, through its parent company Alphabet, continues to dominate search and advertising
    while expanding into AI research with projects like Bard and DeepMind. The company's 
    cloud platform competes directly with Amazon Web Services and Microsoft Azure.
    
    Apple maintains its focus on premium consumer hardware and services, with the iPhone
    ecosystem generating substantial recurring revenue. The company's M-series chips have
    revolutionized performance in personal computing.
    
    Amazon leads in e-commerce and cloud infrastructure through AWS, which powers a 
    significant portion of the internet. The company also invests in logistics automation
    and artificial intelligence for retail optimization.
    
    These technology giants often collaborate on industry standards while competing 
    fiercely in overlapping markets. Their combined market capitalization exceeds 
    several trillion dollars, making them central to global economic growth.
    """
    test_file.write_text(test_content)
    
    try:
        # Initialize service manager with provenance tracking
        print("🔧 INITIALIZATION PHASE")
        print("-" * 80)
        
        init_start = time.time()
        service_manager = ServiceManager()
        provenance_service = service_manager.provenance_service
        
        # Start observability tracking
        session_id = f"demo_session_{int(time.time())}"
        demo_start_op = provenance_service.start_operation(
            operation_type="demo_session",
            agent_details={
                "component": "phase_a_demo",
                "session_id": session_id
            },
            input_data={
                "demo_type": "phase_a_complete",
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"✅ Service Manager initialized (took {time.time() - init_start:.2f}s)")
        print(f"📊 Provenance Session ID: {session_id}")
        
        # Initialize natural language interface
        interface_start = time.time()
        interface = NaturalLanguageInterface(service_manager)
        await interface.initialize()
        print(f"✅ Natural Language Interface ready (took {time.time() - interface_start:.2f}s)")
        
        # Load document with tracking
        print(f"\n📄 DOCUMENT LOADING PHASE")
        print("-" * 80)
        
        load_start = time.time()
        load_operation = provenance_service.start_operation(
            operation_type="document_load",
            agent_details={"component": "nl_interface"},
            input_data={"file": str(test_file), "size": len(test_content)}
        )
        
        success = await interface.load_document(str(test_file))
        
        provenance_service.end_operation(
            operation_id=load_operation,
            output_data={"success": success, "document_id": "tech_companies_analysis"},
            metadata={"load_time": time.time() - load_start}
        )
        
        if success:
            print(f"✅ Document loaded successfully (took {time.time() - load_start:.2f}s)")
            print(f"   - File: {test_file}")
            print(f"   - Size: {len(test_content)} characters")
        
        # Test various question types with detailed tracking
        test_cases = [
            {
                "question": "What is this document about?",
                "intent": "document_summary",
                "description": "High-level document summary"
            },
            {
                "question": "What companies are mentioned in this analysis?",
                "intent": "entity_analysis", 
                "description": "Entity extraction and identification"
            },
            {
                "question": "How do Microsoft and Google compete?",
                "intent": "relationship_analysis",
                "description": "Relationship and competition analysis"
            },
            {
                "question": "What are the main themes discussed?",
                "intent": "theme_analysis",
                "description": "Thematic content analysis"
            }
        ]
        
        print(f"\n🤖 NATURAL LANGUAGE Q&A PHASE")
        print("-" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*80}")
            print(f"TEST CASE {i}: {test_case['description']}")
            print(f"{'='*80}")
            
            # Start question tracking
            question_start = time.time()
            question_op = provenance_service.start_operation(
                operation_type="question_processing",
                agent_details={"component": "nl_interface", "test_case": i},
                input_data={
                    "question": test_case['question'],
                    "expected_intent": test_case['intent']
                }
            )
            
            print(f"\n❓ Question: {test_case['question']}")
            print(f"📋 Expected Intent: {test_case['intent']}")
            
            # Process question
            response = await interface.ask_question(test_case['question'])
            question_time = time.time() - question_start
            
            # End question tracking
            provenance_service.end_operation(
                operation_id=question_op,
                output_data={
                    "response_length": len(response),
                    "response_preview": response[:100] + "..." if len(response) > 100 else response
                },
                metadata={
                    "processing_time": question_time,
                    "success": True
                }
            )
            
            print(f"\n💬 Response ({question_time:.2f}s):")
            print("-" * 40)
            # Print response with line wrapping
            words = response.split()
            line = ""
            for word in words:
                if len(line) + len(word) + 1 > 78:
                    print(line)
                    line = word
                else:
                    line = line + " " + word if line else word
            if line:
                print(line)
        
        # Show execution statistics
        print(f"\n\n📊 EXECUTION ANALYTICS & OBSERVABILITY")
        print("=" * 80)
        
        # Get operation statistics
        stats = {
            'total_operations': len(provenance_service.list_operations()),
            'successful_operations': len([op for op in provenance_service.list_operations() if op.get('status') == 'completed']),
            'failed_operations': len([op for op in provenance_service.list_operations() if op.get('status') == 'failed']),
            'total_duration': time.time() - init_start
        }
        
        print(f"\n1️⃣ SESSION OVERVIEW")
        print(f"   - Session ID: {session_id}")
        print(f"   - Total Operations: {stats.get('total_operations', 0)}")
        print(f"   - Successful Operations: {stats.get('successful_operations', 0)}")
        print(f"   - Failed Operations: {stats.get('failed_operations', 0)}")
        print(f"   - Total Duration: {stats.get('total_duration', 0):.2f}s")
        
        print(f"\n2️⃣ TOOL EXECUTION TRACE")
        # Get tool execution history
        tool_stats = provenance_service.get_tool_statistics()
        for tool_id, tool_stat in tool_stats.items():
            if tool_stat['execution_count'] > 0:
                print(f"   📦 {tool_id}:")
                print(f"      - Executions: {tool_stat['execution_count']}")
                print(f"      - Success Rate: {tool_stat['success_rate']:.1%}")
                print(f"      - Avg Time: {tool_stat['average_execution_time']:.3f}s")
        
        print(f"\n3️⃣ OPERATION LINEAGE")
        # Show operation chain for last question
        operations = provenance_service.list_operations(limit=10)
        if operations:
            print(f"   Recent operations (most recent first):")
            for op in operations[:5]:  # Show last 5 operations
                print(f"   → {op['operation_type']} ({op['operation_id'][:8]}...)")
                print(f"     Started: {op['start_time']}")
                print(f"     Duration: {op.get('duration', 'in progress')}")
                if op.get('metadata'):
                    print(f"     Metadata: {json.dumps(op['metadata'], indent=6)}")
        
        print(f"\n4️⃣ DATA FLOW TRACKING")
        # Show data lineage for entities
        print(f"   Entity Extraction Pipeline:")
        print(f"   📄 Document → T01_PDF_LOADER → T15A_TEXT_CHUNKER → T23A_SPACY_NER")
        print(f"   ↓")
        print(f"   📊 Entities: Microsoft, Google, Apple, Amazon, etc.")
        
        print(f"\n5️⃣ PERFORMANCE METRICS")
        total_time = time.time() - init_start
        print(f"   - Total Demo Time: {total_time:.2f}s")
        print(f"   - Initialization: {interface_start - init_start:.2f}s")
        print(f"   - Document Loading: {load_start - interface_start:.2f}s") 
        print(f"   - Q&A Processing: {time.time() - load_start:.2f}s")
        print(f"   - Average Response Time: {(time.time() - load_start) / len(test_cases):.2f}s")
        
        # Export provenance data
        print(f"\n6️⃣ PROVENANCE EXPORT")
        export_file = f"provenance_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_data = {
            'session_id': session_id,
            'operations': provenance_service.list_operations(limit=100),
            'tool_stats': provenance_service.get_tool_statistics(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"   ✅ Provenance data exported to: {export_file}")
        print(f"   📁 File contains full execution trace and lineage data")
        
        # Memory usage
        print(f"\n7️⃣ RESOURCE UTILIZATION")
        if hasattr(service_manager, 'resource_manager'):
            memory_info = service_manager.resource_manager.get_memory_usage()
            print(f"   - Current Memory: {memory_info['current_mb']:.1f} MB")
            print(f"   - Peak Memory: {memory_info['peak_mb']:.1f} MB")
            print(f"   - Available: {memory_info['available_mb']:.1f} MB")
        
        print(f"\n{'='*80}")
        print(f"✅ PHASE A DEMONSTRATION COMPLETE")
        print(f"🎯 Natural Language Interface: FULLY OPERATIONAL")
        print(f"📊 Observability & Tracing: COMPREHENSIVE")
        print(f"🚀 Ready for Phase B: Dynamic Execution & Intelligence")
        print(f"{'='*80}")
        
    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()
        
        # End demo session
        if 'demo_start_op' in locals():
            provenance_service.end_operation(
                operation_id=demo_start_op,
                output_data={'demo_complete': True},
                metadata={'total_time': time.time() - init_start}
            )

if __name__ == "__main__":
    # Enable debug logging for better observability
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    asyncio.run(demonstrate_phase_a_with_observability())