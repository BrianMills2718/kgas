#!/usr/bin/env python3
"""
Debug why parallel execution isn't triggering
"""
import asyncio
import logging
from pathlib import Path

# Configure logging to see execution details
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Focus on dynamic executor
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.DEBUG)
logging.getLogger('src.execution.execution_planner').setLevel(logging.DEBUG)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)
logging.getLogger('src.tools').setLevel(logging.WARNING)

async def debug_parallel_execution():
    """Debug parallel execution logic"""
    
    print("\n" + "="*80)
    print("DEBUGGING PARALLEL EXECUTION")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create document with sufficient data for parallel execution
    print("\n2. Creating document with data that should trigger parallel execution...")
    doc_path = Path("doc_parallel_test.txt")
    doc_path.write_text("""
    Microsoft, Google, Amazon, Apple, and Facebook are the major tech companies.
    Microsoft competes with Google in cloud services.
    Amazon dominates e-commerce while Apple leads in consumer hardware.
    Facebook focuses on social media and virtual reality.
    All these companies have significant AI investments.
    Microsoft's Azure competes with Amazon's AWS and Google Cloud.
    Apple's privacy stance differs from Google and Facebook's ad models.
    """)
    
    interface.current_document_path = str(doc_path)
    
    # Test with a question that should trigger parallel execution
    print("\n3. Asking question that should trigger parallel tools...")
    question = "Build a knowledge graph of all companies and analyze their network structure"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    
    # Check execution metadata
    if hasattr(interface, 'last_result') and interface.last_result:
        result_obj = interface.last_result
        if hasattr(result_obj, 'execution_metadata'):
            meta = result_obj.execution_metadata
            
            print("\n4. Execution Metadata:")
            print(f"   - Parallel opportunities: {meta.get('parallel_opportunities', 'N/A')}")
            print(f"   - Execution groups: {meta.get('execution_groups', 'N/A')}")
            total_time = meta.get('total_time', 'N/A')
            if isinstance(total_time, (int, float)):
                print(f"   - Total execution time: {total_time:.2f}s")
            else:
                print(f"   - Total execution time: {total_time}")
            
            # Check tool execution order
            if 'tool_execution_order' in meta:
                print("\n5. Tool Execution Order:")
                for i, tool in enumerate(meta['tool_execution_order']):
                    print(f"   {i+1}. {tool}")
    
    # Cleanup
    doc_path.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("PARALLEL EXECUTION DEBUG COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(debug_parallel_execution())