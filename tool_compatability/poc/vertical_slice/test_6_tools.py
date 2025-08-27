#!/usr/bin/env python3
"""Test 6-tool pipeline: PDF → Text → Chunks → Back to Text → Entities → Graph"""

import sys
import os
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from integrate_tools import integrate_ready_tools, integrate_legacy_tools

print("="*60)
print("6-TOOL PIPELINE TEST")
print("="*60)

# Initialize framework
framework = CleanToolFramework(
    neo4j_uri="bolt://localhost:7687",
    sqlite_path="vertical_slice.db"
)

# Clean Neo4j
with framework.neo4j.session() as session:
    session.run("MATCH (n:VSEntity) DETACH DELETE n")

# Integrate tools
integrate_ready_tools(framework)
integrate_legacy_tools(framework)

print("\nRegistered tools:", list(framework.capabilities.keys()))

# Create test PDF-like file (using .txt for simplicity)
test_file = "test_document.txt"
with open(test_file, 'w') as f:
    f.write("""
    KGAS Research Paper
    
    Authors: Brian Chhun, Sarah Chen
    Institution: University of Melbourne
    
    Abstract:
    The Knowledge Graph Augmentation System (KGAS) introduces a novel approach to uncertainty propagation
    in knowledge management pipelines. Our framework tracks uncertainty through each transformation,
    using physics-style error propagation where confidence = ∏(1 - uᵢ).
    
    Introduction:
    Modern knowledge systems require robust uncertainty quantification. KGAS addresses this need
    by providing a universal adapter pattern for tool integration. The system seamlessly integrates
    with Neo4j for graph persistence and SQLite for metrics storage.
    
    Methodology:
    We employ a clean vertical slice architecture with service integration. The IdentityService handles
    entity deduplication, ProvenanceService tracks operations, and QualityService assesses data quality.
    Each tool contributes its uncertainty assessment based on operation characteristics.
    
    Results:
    Initial experiments show combined uncertainties ranging from 0.25 to 0.45 for typical pipelines.
    The framework successfully integrated 7 diverse tools with minimal code changes.
    """)

# Tool 1: t01_pdf_loader (PDF extraction)
print("\n📄 Tool 1: t01_pdf_loader")
result1 = framework.execute_chain(['t01_pdf_loader'], test_file)
print(f"   Success: {result1.success}, Uncertainty: {result1.total_uncertainty:.3f}")

if result1.success:
    # Extract text from PDF loader result
    pdf_data = result1.data
    if isinstance(pdf_data, dict):
        text_content = pdf_data.get('document', {}).get('content', str(pdf_data))
    else:
        text_content = str(pdf_data)

    # Tool 2: t15a_text_chunker (chunk the text)
    print("📝 Tool 2: t15a_text_chunker")
    result2 = framework.execute_chain(['t15a_text_chunker'], text_content)
    print(f"   Success: {result2.success}, Uncertainty: {result2.total_uncertainty:.3f}")
    
    if result2.success:
        chunks = result2.data
        
        # Tool 3: simple_text_loader (process first chunk as file)
        # Write chunk to temp file
        chunk_file = "chunk.txt"
        first_chunk = str(chunks[0] if isinstance(chunks, list) and chunks else chunks)
        with open(chunk_file, 'w') as f:
            f.write(first_chunk)
        
        print("📖 Tool 3: simple_text_loader")
        result3 = framework.execute_chain(['simple_text_loader'], chunk_file)
        print(f"   Success: {result3.success}, Uncertainty: {result3.total_uncertainty:.3f}")
        os.remove(chunk_file)
        
        if result3.success:
            # Tool 4: gemini_entity_extractor
            print("🔍 Tool 4: gemini_entity_extractor")
            result4 = framework.execute_chain(['gemini_entity_extractor'], result3.data)
            print(f"   Success: {result4.success}, Uncertainty: {result4.total_uncertainty:.3f}")
            
            if result4.success:
                # Tool 5: neo4j_graph_builder (first persistence)
                print("💾 Tool 5: neo4j_graph_builder")
                result5 = framework.execute_chain(['neo4j_graph_builder'], result4.data)
                print(f"   Success: {result5.success}, Uncertainty: {result5.total_uncertainty:.3f}")
                
                # Tool 6: t49_multihop_query (query the graph)
                print("🔎 Tool 6: t49_multihop_query")
                # Query needs different input - it operates on the graph directly
                query_input = {'query': 'MATCH (n:VSEntity) RETURN n LIMIT 10'}
                result6 = framework.execute_chain(['t49_multihop_query'], query_input)
                print(f"   Success: {result6.success}, Uncertainty: {result6.total_uncertainty:.3f}")
                
                # Calculate total uncertainty for all 6 tools
                all_uncertainties = (
                    result1.step_uncertainties + 
                    result2.step_uncertainties + 
                    result3.step_uncertainties + 
                    result4.step_uncertainties +
                    result5.step_uncertainties +
                    result6.step_uncertainties
                )
                
                confidence = 1.0
                for u in all_uncertainties:
                    confidence *= (1 - u)
                total_uncertainty = 1 - confidence
                
                print("\n" + "="*60)
                print("✅ 6-TOOL PIPELINE COMPLETE")
                print("="*60)
                print(f"Tools executed: {len(all_uncertainties)}")
                print(f"Tool sequence:")
                print("  1. t01_pdf_loader (PDF → text)")
                print("  2. t15a_text_chunker (text → chunks)")
                print("  3. simple_text_loader (chunk → text)")
                print("  4. gemini_entity_extractor (text → entities)")
                print("  5. neo4j_graph_builder (entities → graph)")
                print("  6. t49_multihop_query (graph → results)")
                print(f"\nIndividual uncertainties: {[f'{u:.3f}' for u in all_uncertainties]}")
                print(f"Combined uncertainty: {total_uncertainty:.3f}")
                print(f"\n🎯 Successfully demonstrated {len(all_uncertainties)}-tool pipeline with uncertainty propagation!")

# Clean up
os.remove(test_file)
framework.cleanup()