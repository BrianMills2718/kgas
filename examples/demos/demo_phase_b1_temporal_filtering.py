#!/usr/bin/env python3
"""
Demonstration of Phase B.1: Temporal Filtering
Shows how temporal parameters are adapted based on question context
"""
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Show execution details
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.INFO)
logging.getLogger('src.nlp.context_extractor').setLevel(logging.INFO)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_temporal_filtering():
    """Demonstrate temporal filtering based on question context"""
    
    print("\n" + "="*80)
    print("PHASE B.1 DEMONSTRATION: Temporal Filtering")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create a document with temporal information
    print("\n2. Creating document with temporal data...")
    doc_temporal = Path("doc_temporal_data.txt")
    doc_temporal.write_text("""
    In 2022, Microsoft acquired Activision Blizzard for $69 billion.
    In 2023, Google announced its Bard AI to compete with ChatGPT.
    In 2024, Apple launched the Vision Pro mixed reality headset.
    
    Microsoft's revenue in 2022 was $198 billion.
    Google's revenue in 2023 reached $282 billion.
    Apple's revenue in 2024 is projected to exceed $400 billion.
    
    The AI revolution began accelerating in 2022 with GPT-3.
    In 2023, generative AI became mainstream with ChatGPT.
    By 2024, AI was integrated into most major tech products.
    """)
    
    interface.current_document_path = str(doc_temporal)
    
    # Test Case 1: Question with specific year
    print("\n" + "="*70)
    print("TEST 1: Question with specific year (2023)")
    print("="*70)
    
    question = "What happened with Google in 2023?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_temporal_filtering_details(result, expected_temporal="2023")
    
    # Test Case 2: Question with multiple years
    print("\n" + "="*70)
    print("TEST 2: Question with year range (2022-2024)")
    print("="*70)
    
    question = "Compare the major tech events from 2022 to 2024"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_temporal_filtering_details(result, expected_temporal=["2022", "2023", "2024"])
    
    # Test Case 3: Question without temporal context
    print("\n" + "="*70)
    print("TEST 3: Question without temporal context")
    print("="*70)
    
    question = "What are the major tech companies mentioned?"
    print(f"Question: {question}")
    
    result_str = await interface.ask_question(question)
    result = interface.last_result
    
    print_temporal_filtering_details(result, expected_temporal=None)
    
    # Cleanup
    doc_temporal.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("TEMPORAL FILTERING DEMONSTRATED")
    print("="*80 + "\n")

def print_temporal_filtering_details(result, expected_temporal=None):
    """Print temporal filtering details"""
    if result and hasattr(result, 'execution_metadata') and result.execution_metadata:
        meta = result.execution_metadata
        
        print(f"\nExecution Details:")
        
        # Check adapted parameters
        if 'adapted_parameters' in meta and meta['adapted_parameters']:
            print(f"\n  ✓ Adapted Parameters:")
            
            temporal_adapted = False
            for tool, params in meta['adapted_parameters'].items():
                print(f"    - {tool}: {params}")
                
                # Check for temporal filtering
                if 'temporal_filtering_enabled' in params:
                    temporal_adapted = True
                    print(f"      → Temporal filtering ENABLED")
                    
                    if 'time_filter' in params:
                        print(f"      → Time filter: {params['time_filter']}")
                        
                        # Check if it matches expected
                        if expected_temporal:
                            if isinstance(expected_temporal, str):
                                if params['time_filter'] == expected_temporal:
                                    print(f"      ✓ Correct temporal filter applied")
                                else:
                                    print(f"      ✗ Expected {expected_temporal}, got {params['time_filter']}")
                            elif isinstance(expected_temporal, list):
                                if params['time_filter'] in expected_temporal:
                                    print(f"      ✓ Temporal filter in expected range")
            
            if not temporal_adapted and expected_temporal:
                print(f"\n  ✗ Expected temporal filtering but none was applied")
        else:
            print(f"  - No parameter adaptation occurred")
        
        # Show question analysis
        if 'original_question' in meta:
            print(f"\n  - Original Question: {meta['original_question']}")
        
        # Show execution time
        print(f"  - Total Execution Time: {meta.get('execution_time', 0):.3f}s")
        
        # Show response preview
        if hasattr(result, 'response'):
            print(f"\n  - Response Preview: {result.response[:200]}...")

if __name__ == "__main__":
    asyncio.run(demonstrate_temporal_filtering())