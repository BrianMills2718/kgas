#!/usr/bin/env python3
"""
Debug tool dependencies to understand parallel execution
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

# Focus on tool chain generator
logging.getLogger('src.nlp.tool_chain_generator').setLevel(logging.DEBUG)
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.DEBUG)

# Reduce noise
logging.getLogger('src.core').setLevel(logging.WARNING)
logging.getLogger('src.tools').setLevel(logging.WARNING)

async def debug_dependencies():
    """Debug tool dependencies"""
    
    print("\n" + "="*80)
    print("DEBUGGING TOOL DEPENDENCIES FOR PARALLEL EXECUTION")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create document
    doc_path = Path("doc_deps_test.txt")
    doc_path.write_text("Microsoft and Google are major tech companies.")
    interface.current_document_path = str(doc_path)
    
    # Test with graph building question
    print("\n2. Testing graph building question...")
    question = "Build a knowledge graph of all companies and analyze their network structure"
    result = await interface.ask_question(question)
    
    # Check the generated tool chain
    if hasattr(interface, 'last_result'):
        result_obj = interface.last_result
        
        # Check advanced analysis
        if hasattr(result_obj, 'advanced_analysis'):
            analysis = result_obj.advanced_analysis
            if hasattr(analysis, 'tool_chain'):
                chain = analysis.tool_chain
                print("\n3. Tool Chain Analysis:")
                print(f"   - Can parallelize: {chain.can_parallelize}")
                print(f"   - Number of steps: {len(chain.steps)}")
                
                print("\n4. Tool Dependencies:")
                for step in chain.steps:
                    print(f"   - {step.tool_id}: depends on {step.depends_on}")
                
                # Analyze parallel opportunities
                print("\n5. Parallel Analysis:")
                
                # Check T31 and T34
                t31_step = next((s for s in chain.steps if s.tool_id == 'T31_ENTITY_BUILDER'), None)
                t34_step = next((s for s in chain.steps if s.tool_id == 'T34_EDGE_BUILDER'), None)
                    
                if t31_step and t34_step:
                    t31_deps = set(t31_step.depends_on)
                    t34_deps = set(t34_step.depends_on)
                        
                    print(f"   - T31_ENTITY_BUILDER depends on: {t31_deps}")
                    print(f"   - T34_EDGE_BUILDER depends on: {t34_deps}")
                    
                    # Check if they have same dependencies (can run together)
                    if t31_deps == t34_deps:
                        print("   ✓ T31 and T34 have same dependencies - CAN run in parallel!")
                    else:
                        print("   ✗ T31 and T34 have different dependencies - CANNOT run in parallel")
                        print(f"     Difference: {t31_deps.symmetric_difference(t34_deps)}")
    
    # Cleanup
    doc_path.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("DEPENDENCY DEBUG COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(debug_dependencies())