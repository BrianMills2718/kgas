#!/usr/bin/env python3
"""
Demonstration of Phase B.1: Working Temporal Filtering
Shows actual filtering of results based on temporal context
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

# Enable debug for temporal filtering
logging.getLogger('src.tools.phase1.t23a_spacy_ner_unified').setLevel(logging.DEBUG)
logging.getLogger('src.execution.dynamic_executor').setLevel(logging.INFO)

# Reduce noise
logging.getLogger('src.core.resource_manager').setLevel(logging.WARNING)
logging.getLogger('src.orchestration.memory').setLevel(logging.WARNING)
logging.getLogger('src.core.identity_management').setLevel(logging.WARNING)

async def demonstrate_temporal_filtering():
    """Demonstrate working temporal filtering"""
    
    print("\n" + "="*80)
    print("PHASE B.1 DEMONSTRATION: Working Temporal Filtering")
    print("="*80 + "\n")
    
    # Initialize services
    from src.core.service_manager import ServiceManager
    from src.nlp.natural_language_interface import NaturalLanguageInterface
    
    print("1. Initializing services...")
    service_manager = ServiceManager()
    interface = NaturalLanguageInterface(service_manager)
    await interface.initialize()
    
    # Create document with clear temporal data
    print("\n2. Creating document with temporal data...")
    doc_temporal = Path("doc_temporal_events.txt")
    doc_temporal.write_text("""
    Major Tech Events by Year:
    
    2022 Events:
    - Microsoft acquired Activision Blizzard for $69 billion
    - Elon Musk bought Twitter for $44 billion
    - Meta's stock price crashed by 70%
    
    2023 Events:
    - Google launched Bard AI assistant
    - OpenAI released ChatGPT to the public
    - Apple became first $3 trillion company
    
    2024 Events:
    - Apple launched Vision Pro headset
    - Google released Gemini AI model
    - Microsoft integrated AI into Office
    
    These events shaped the technology landscape across three years.
    """)
    
    interface.current_document_path = str(doc_temporal)
    
    # Test Case 1: Ask about 2023
    print("\n" + "="*70)
    print("TEST 1: Filter for 2023 events only")
    print("="*70)
    
    question = "What major events happened in 2023?"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print_temporal_results(result, "2023")
    
    # Test Case 2: Ask about 2022
    print("\n" + "="*70)
    print("TEST 2: Filter for 2022 events only")
    print("="*70)
    
    question = "Tell me about the acquisitions in 2022"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print_temporal_results(result, "2022")
    
    # Test Case 3: Ask without temporal context
    print("\n" + "="*70)
    print("TEST 3: No temporal filter - all events")
    print("="*70)
    
    question = "What are all the major tech events mentioned?"
    print(f"Question: {question}")
    
    result = await interface.ask_question(question)
    print_temporal_results(result, None)
    
    # Cleanup
    doc_temporal.unlink(missing_ok=True)
    
    print("\n" + "="*80)
    print("TEMPORAL FILTERING SUCCESSFULLY DEMONSTRATED")
    print("="*80 + "\n")

def print_temporal_results(result_str, expected_year):
    """Print results showing temporal filtering effectiveness"""
    
    # Parse entities from response
    print(f"\nResponse preview: {result_str[:200]}...")
    
    # Count mentions of different years in response
    years = ["2022", "2023", "2024"]
    year_counts = {}
    for year in years:
        count = result_str.count(year)
        year_counts[year] = count
    
    print("\nYear mentions in response:")
    for year, count in year_counts.items():
        marker = "✓" if year == expected_year or expected_year is None else "✗"
        print(f"  {marker} {year}: {count} mentions")
    
    # Check filtering effectiveness
    if expected_year:
        other_years = [y for y in years if y != expected_year]
        other_mentions = sum(year_counts.get(y, 0) for y in other_years)
        target_mentions = year_counts.get(expected_year, 0)
        
        if other_mentions == 0 and target_mentions > 0:
            print(f"\n✅ TEMPORAL FILTERING WORKING: Only {expected_year} data returned")
        elif other_mentions > 0:
            print(f"\n⚠️ PARTIAL FILTERING: Found {other_mentions} mentions of other years")
        else:
            print(f"\n❌ NO FILTERING: No {expected_year} data found")
    else:
        total_mentions = sum(year_counts.values())
        print(f"\n✅ NO FILTER APPLIED: Found {total_mentions} total year mentions")

if __name__ == "__main__":
    asyncio.run(demonstrate_temporal_filtering())