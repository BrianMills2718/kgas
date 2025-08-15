#!/usr/bin/env python3
"""
Advanced demonstration of Phase B.1: Parallel Execution
Shows PageRank and Multi-hop Query running in parallel
"""
import asyncio
import logging
from pathlib import Path

# Configure logging to see parallel execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Show detail for execution
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.DEBUG)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_advanced_parallel():
    """Demonstrate parallel execution with PageRank and Multi-hop Query"""
    
    print("\n" + "="*80)
    print("PHASE B.1 ADVANCED PARALLEL EXECUTION DEMONSTRATION")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create a document with rich network structure
    print("\n2. Creating document with complex network structure...")
    doc_network = Path("doc_network_analysis.txt")
    doc_network.write_text("""
    Microsoft partnered with OpenAI to develop advanced AI systems.
    Google competes with Microsoft in the AI space.
    Amazon collaborated with Anthropic for cloud AI services.
    Apple acquired several AI startups to enhance their capabilities.
    
    Microsoft also invested heavily in Azure AI infrastructure.
    Google's DeepMind division pioneered many AI breakthroughs.
    Amazon Web Services provides AI compute resources to many companies.
    Apple focuses on on-device AI processing for privacy.
    
    OpenAI collaborates with multiple cloud providers for compute.
    Anthropic emphasizes AI safety in their research.
    DeepMind works closely with Google Research teams.
    
    The AI landscape shows intense competition and strategic partnerships.
    Companies form alliances while competing in different market segments.
    """)
    
    interface.current_document_path = str(doc_network)
    
    # Test advanced question that triggers PageRank and Multi-hop Query
    print("\n" + "="*70)
    print("TEST: Complex network analysis (should trigger T68 & T49 parallel)")
    print("="*70)
    
    question = "Analyze the network of AI companies and identify the most important players and their connection paths"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result)
    
    # Cleanup
    doc_network.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("ADVANCED PARALLEL EXECUTION DEMONSTRATED")
    print("="*80 + "\n")

def print_execution_details(result):
    """Print detailed execution information with focus on parallelization"""
    if result and hasattr(result, 'execution_metadata') and result.execution_metadata:
        meta = result.execution_metadata
        
        print(f"\nExecution Details:")
        print(f"  - Tools Executed: {result.tools_executed}")
        print(f"  - Execution Strategy: {meta.get('execution_strategy', 'unknown')}")
        print(f"  - Parallelized: {meta.get('parallelized', False)}")
        
        if meta.get('parallelized'):
            print("\n  🚀 PARALLEL EXECUTION DETECTED! 🚀")
            
        if 'parallel_groups' in meta and meta['parallel_groups']:
            print(f"\n  - Parallel Groups:")
            for group in meta['parallel_groups']:
                if isinstance(group, dict) and 'tools' in group:
                    print(f"    - {group['tools']} (time: {group.get('execution_time', 0):.3f}s)")
                    if 'speedup' in group:
                        print(f"      Theoretical speedup: {group['speedup']}x")
        
        if 'tools_skipped' in meta and meta['tools_skipped']:
            print(f"\n  - Tools Skipped: {meta['tools_skipped']}")
            print("    ✓ Dynamic tool skipping working!")
        
        if 'adapted_parameters' in meta and meta['adapted_parameters']:
            print(f"\n  - Adapted Parameters:")
            for tool, params in meta['adapted_parameters'].items():
                print(f"    - {tool}: {params}")
        
        print(f"\n  - Total Execution Time: {meta.get('execution_time', 0):.3f}s")
        
        # Check if PageRank and Multi-hop were executed
        if 'T68_PAGE_RANK' in result.tools_executed and 'T49_MULTI_HOP_QUERY' in result.tools_executed:
            print("\n  ✓ Both T68_PAGE_RANK and T49_MULTI_HOP_QUERY were executed")
            
            # Check if they ran in parallel
            breakdown = meta.get('execution_times_breakdown', {})
            t68_time = breakdown.get('T68_PAGE_RANK', 0)
            t49_time = breakdown.get('T49_MULTI_HOP_QUERY', 0)
            
            if t68_time > 0 and t49_time > 0:
                # If they ran in parallel, their combined time should be close to the max
                # rather than the sum
                max_time = max(t68_time, t49_time)
                sum_time = t68_time + t49_time
                
                print(f"\n  - T68_PAGE_RANK time: {t68_time:.3f}s")
                print(f"  - T49_MULTI_HOP_QUERY time: {t49_time:.3f}s")
                print(f"  - If sequential: {sum_time:.3f}s")
                print(f"  - If parallel: ~{max_time:.3f}s")

if __name__ == "__main__":
    asyncio.run(demonstrate_advanced_parallel())