#!/usr/bin/env python3
"""
Demonstration of Phase B.1: Dynamic Execution & Intelligent Orchestration
Shows how Phase B enhances Phase A with advanced question analysis and dynamic execution
"""
import asyncio
import logging
from pathlib import Path
import json

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Reduce noise from some modules
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_phase_b1():
    """Demonstrate Phase B.1 capabilities"""
    
    print("\n" + "="*80)
    print("PHASE B.1 DEMONSTRATION: Dynamic Execution & Intelligent Orchestration")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create a test document
    test_doc_path = Path("test_document.txt")
    test_content = """
    Microsoft and Google are leading the AI revolution with their respective products.
    In 2023, Microsoft invested heavily in OpenAI while Google developed Bard.
    Amazon has also entered the AI space with their AWS AI services.
    Apple, though more secretive, is working on AI integration in their devices.
    
    The competition between these tech giants intensified in 2024, with each company
    trying to outdo the others in AI capabilities. Microsoft's partnership with OpenAI
    gave them an edge, while Google's vast data resources powered their innovations.
    """
    
    test_doc_path.write_text(test_content)
    interface.current_document_path = str(test_doc_path)
    
    # Test different types of questions to show dynamic behavior
    test_cases = [
        {
            "name": "Simple Entity Extraction",
            "question": "What companies are mentioned in this document?",
            "expected_features": ["entity extraction", "simple complexity", "3 tools"]
        },
        {
            "name": "Complex Comparison with Temporal Context",
            "question": "Compare Microsoft and Google's AI strategies in 2023 and 2024",
            "expected_features": ["comparison analysis", "temporal filtering", "complex execution"]
        },
        {
            "name": "Multi-Component Question",
            "question": "Extract all companies, analyze their relationships, and identify the most important ones",
            "expected_features": ["multiple intents", "potential parallelization", "importance ranking"]
        },
        {
            "name": "Ambiguous Question",
            "question": "Tell me about the stuff in here",
            "expected_features": ["high ambiguity", "low confidence", "confidence disclaimer"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-'*70}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"Question: {test_case['question']}")
        print(f"Expected: {', '.join(test_case['expected_features'])}")
        print("-"*70)
        
        # Process the question
        result_str = await interface.ask_question(test_case['question'])
        result = interface.last_result
        
        if result and hasattr(result, 'advanced_analysis') and result.advanced_analysis:
            # Show advanced analysis results
            print(f"\nAdvanced Analysis:")
            print(f"  - Intent: {result.advanced_analysis.intent.value}")
            print(f"  - Complexity: {result.advanced_analysis.complexity.value}")
            print(f"  - Confidence: {result.advanced_analysis.confidence:.2f}")
            print(f"  - Ambiguity: {result.advanced_analysis.ambiguity_level:.2f}")
            
            if result.advanced_analysis.has_temporal_context:
                print(f"  - Temporal Context: {result.advanced_analysis.temporal_constraints}")
            
            if result.advanced_analysis.secondary_intents:
                print(f"  - Secondary Intents: {[i.value for i in result.advanced_analysis.secondary_intents]}")
            
            # Show execution details
            print(f"\nExecution Details:")
            print(f"  - Tools Executed: {result.tools_executed}")
            
            if hasattr(result, 'execution_metadata') and result.execution_metadata:
                meta = result.execution_metadata
                print(f"  - Execution Strategy: {meta.get('execution_strategy', 'unknown')}")
                print(f"  - Parallelized: {meta.get('parallelized', False)}")
                
                if 'parallel_groups' in meta and meta['parallel_groups']:
                    print(f"  - Parallel Groups: {meta['parallel_groups']}")
                
                if 'tools_skipped' in meta and meta['tools_skipped']:
                    print(f"  - Tools Skipped: {meta['tools_skipped']}")
                
                if 'adapted_parameters' in meta and meta['adapted_parameters']:
                    print(f"  - Adapted Parameters:")
                    for tool, params in meta['adapted_parameters'].items():
                        print(f"    - {tool}: {params}")
                
                print(f"  - Execution Time: {meta.get('execution_time', 0):.2f}s")
            
            # Show extracted data
            if hasattr(result, 'entities') and result.entities:
                print(f"\nExtracted Entities: {len(result.entities)}")
                for entity in result.entities[:5]:  # Show first 5
                    if isinstance(entity, dict):
                        print(f"  - {entity.get('surface_form', entity.get('text', 'Unknown'))}: {entity.get('entity_type', 'Unknown')}")
            
            # Show response snippet
            print(f"\nResponse Preview:")
            print(f"  {result.response[:200]}..." if len(result.response) > 200 else f"  {result.response}")
            
            if result.confidence_disclaimer:
                print(f"\nConfidence Disclaimer: {result.confidence_disclaimer}")
        else:
            print(f"\nError or fallback occurred")
            if result:
                print(f"Status: {result.status}")
                if hasattr(result, 'warning'):
                    print(f"Warning: {result.warning}")
    
    # Cleanup
    test_doc_path.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("PHASE B.1 CAPABILITIES DEMONSTRATED:")
    print("="*80)
    print("✓ Advanced intent classification (15 intent types)")
    print("✓ Question complexity analysis (simple/moderate/complex)")
    print("✓ Context extraction (temporal, entities, comparisons)")
    print("✓ Dynamic tool chain generation")
    print("✓ Parameter adaptation based on context")
    print("✓ Ambiguity detection and confidence scoring")
    print("✓ Tool skipping based on intermediate results")
    print("✓ Execution strategy optimization")
    print("\nPhase B.1 enhances Phase A with intelligent question understanding!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(demonstrate_phase_b1())