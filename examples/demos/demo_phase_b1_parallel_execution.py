#!/usr/bin/env python3
"""
Demonstration of Phase B.1: Parallel Execution and Tool Skipping
Shows actual dynamic behavior including parallel execution and conditional tool skipping
"""
import asyncio
import logging
from pathlib import Path
import json

# Configure logging to see parallel execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Show more detail for execution
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.DEBUG)
logging.getLogger('src.nlp.tool_chain_generator').setLevel(logging.INFO)

# Reduce noise from some modules
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_parallel_execution():
    """Demonstrate parallel execution and tool skipping"""
    
    print("\n" + "="*80)
    print("PHASE B.1 DEMONSTRATION: Parallel Execution & Tool Skipping")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Test Case 1: Document with relationships (should trigger parallel execution)
    print("\n" + "="*70)
    print("TEST 1: Question requiring relationship analysis (T31 & T34 parallel)")
    print("="*70)
    
    doc_with_relationships = Path("doc_with_relationships.txt")
    doc_with_relationships.write_text("""
    Microsoft partnered with OpenAI to develop advanced AI systems.
    Google competes with Microsoft in the AI space.
    Amazon collaborated with Anthropic for cloud AI services.
    Apple acquired several AI startups to enhance their capabilities.
    
    These tech giants form a complex network of partnerships and competition
    in the rapidly evolving AI landscape of 2024.
    """)
    
    interface.current_document_path = str(doc_with_relationships)
    
    question = "Analyze the relationships and network between companies"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result)
    
    # Test Case 2: Document with single entity (should skip relationship extractor)
    print("\n" + "="*70)
    print("TEST 2: Document with single entity (should skip T27)")
    print("="*70)
    
    doc_single_entity = Path("doc_single_entity.txt")
    doc_single_entity.write_text("""
    Microsoft is a technology company founded in 1975.
    The company develops software, hardware, and cloud services.
    Its headquarters are located in Redmond, Washington.
    """)
    
    interface.current_document_path = str(doc_single_entity)
    
    question = "What relationships exist between companies?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result)
    
    # Test Case 3: Complex multi-tool question
    print("\n" + "="*70)
    print("TEST 3: Complex question requiring full pipeline")
    print("="*70)
    
    interface.current_document_path = str(doc_with_relationships)
    
    question = "Extract all entities, analyze their relationships, and identify the most important ones in the network"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result)
    
    # Cleanup
    doc_with_relationships.unlink(missing_ok=True)
    doc_single_entity.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("PARALLEL EXECUTION & TOOL SKIPPING DEMONSTRATED")
    print("="*80 + "\n")

def print_execution_details(result):
    """Print detailed execution information"""
    if result and hasattr(result, 'execution_metadata') and result.execution_metadata:
        meta = result.execution_metadata
        
        print(f"\nExecution Details:")
        print(f"  - Tools Executed: {result.tools_executed}")
        print(f"  - Execution Strategy: {meta.get('execution_strategy', 'unknown')}")
        print(f"  - Parallelized: {meta.get('parallelized', False)}")
        
        if 'parallel_groups' in meta and meta['parallel_groups']:
            print(f"  - Parallel Groups:")
            for group in meta['parallel_groups']:
                print(f"    - {group['tools']} (time: {group['execution_time']:.3f}s)")
        
        if 'tools_skipped' in meta and meta['tools_skipped']:
            print(f"  - Tools Skipped: {meta['tools_skipped']}")
        
        if 'adapted_parameters' in meta and meta['adapted_parameters']:
            print(f"  - Adapted Parameters:")
            for tool, params in meta['adapted_parameters'].items():
                print(f"    - {tool}: {params}")
        
        print(f"  - Total Execution Time: {meta.get('execution_time', 0):.3f}s")
        
        # Show timing breakdown if available
        if 'execution_times_breakdown' in meta:
            print(f"  - Timing Breakdown:")
            for tool, time in meta['execution_times_breakdown'].items():
                print(f"    - {tool}: {time:.3f}s")
    
    # Show if entities were found
    if hasattr(result, 'entities'):
        print(f"\nEntities Found: {len(result.entities)}")
    
    print(f"\nResponse Preview: {result.response[:150]}...")

if __name__ == "__main__":
    asyncio.run(demonstrate_parallel_execution())