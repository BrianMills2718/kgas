#!/usr/bin/env python3
"""
Demonstration of Phase B.1: Dynamic Tool Skipping
Shows tools being skipped based on insufficient data
"""
import asyncio
import logging
from pathlib import Path

# Configure logging to see tool skipping
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Show execution details
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.INFO)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_tool_skipping():
    """Demonstrate dynamic tool skipping based on data conditions"""
    
    print("\n" + "="*80)
    print("PHASE B.1 DEMONSTRATION: Dynamic Tool Skipping")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Test Case 1: Document with single entity (should skip T27)
    print("\n" + "="*70)
    print("TEST 1: Document with single entity (should skip T27_RELATIONSHIP_EXTRACTOR)")
    print("="*70)
    
    doc_single_entity = Path("doc_single_entity.txt")
    doc_single_entity.write_text("""
    The weather is nice today.
    It is sunny outside.
    """)
    
    interface.current_document_path = str(doc_single_entity)
    
    question = "What relationships exist between companies?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result, expected_skip="T27_RELATIONSHIP_EXTRACTOR")
    
    # Test Case 2: Document with no entities (should skip multiple tools)
    print("\n" + "="*70)
    print("TEST 2: Document with no clear entities (should skip multiple tools)")
    print("="*70)
    
    doc_no_entities = Path("doc_no_entities.txt")
    doc_no_entities.write_text("""
    The weather today is quite pleasant.
    Birds are singing in the trees.
    The sun is shining brightly.
    """)
    
    interface.current_document_path = str(doc_no_entities)
    
    question = "Analyze the network and relationships"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result, expected_skip=["T27_RELATIONSHIP_EXTRACTOR", "T68_PAGE_RANK"])
    
    # Test Case 3: Document with entities but no relationships
    print("\n" + "="*70)
    print("TEST 3: Document with entities but no relationships (should skip T34 effects)")
    print("="*70)
    
    doc_no_relationships = Path("doc_no_relationships.txt")
    doc_no_relationships.write_text("""
    Microsoft is a company.
    Google is a company.
    Amazon is a company.
    Apple is a company.
    """)
    
    interface.current_document_path = str(doc_no_relationships)
    
    question = "Find the most important companies and their connections"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_execution_details(result, expected_skip=["T49_MULTI_HOP_QUERY"])
    
    # Cleanup
    doc_single_entity.unlink(missing_ok=True)
    doc_no_entities.unlink(missing_ok=True)
    doc_no_relationships.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("DYNAMIC TOOL SKIPPING DEMONSTRATED")
    print("="*80 + "\n")

def print_execution_details(result, expected_skip=None):
    """Print execution details with focus on skipped tools"""
    if result and hasattr(result, 'execution_metadata') and result.execution_metadata:
        meta = result.execution_metadata
        
        print(f"\nExecution Details:")
        print(f"  - Tools Executed: {result.tools_executed}")
        
        if 'tools_skipped' in meta and meta['tools_skipped']:
            print(f"\n  ✓ Tools Skipped: {meta['tools_skipped']}")
            print("    Dynamic tool skipping is working!")
            
            # Check if expected tools were skipped
            if expected_skip:
                if isinstance(expected_skip, str):
                    expected_skip = [expected_skip]
                
                for tool in expected_skip:
                    if tool in meta['tools_skipped']:
                        print(f"    ✓ {tool} was correctly skipped")
                    else:
                        print(f"    ✗ {tool} was expected to be skipped but wasn't")
        else:
            print(f"  - No tools were skipped")
            
            # Check if we expected skips
            if expected_skip:
                print(f"    ✗ Expected {expected_skip} to be skipped")
        
        # Show why tools might have been executed or skipped
        if hasattr(result, 'entities'):
            print(f"\n  - Entities Found: {len(result.entities)}")
            if len(result.entities) < 2:
                print("    → Insufficient entities for relationship extraction")
        
        # Show execution time
        print(f"\n  - Total Execution Time: {meta.get('execution_time', 0):.3f}s")

if __name__ == "__main__":
    asyncio.run(demonstrate_tool_skipping())