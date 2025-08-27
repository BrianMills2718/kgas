#!/usr/bin/env python3
"""
Tool Integration: Use UniversalAdapter to integrate existing tools
Tests with real tools from the inventory
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

# Add paths for imports
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from neo4j import GraphDatabase
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from adapters.universal_adapter import UniversalAdapter, adapt_tool

def integrate_ready_tools(framework: CleanToolFramework):
    """Integrate the 3 tools that are ready (have process method)"""
    print("\n=== Integrating Ready Tools ===\n")
    
    # 1. Simple Text Loader
    try:
        from src.tools.simple_text_loader import SimpleTextLoader
        text_loader = SimpleTextLoader()
        adapted = UniversalAdapter(
            tool=text_loader,
            tool_id="simple_text_loader",
            method_name="process",
            uncertainty_config={
                'base': 0.02,
                'reasoning': 'Text file loading with minimal uncertainty'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="simple_text_loader",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="character_sequence",
            transformation_type="text_loading"
        ))
        print("✅ Integrated simple_text_loader")
    except Exception as e:
        print(f"❌ Failed to integrate simple_text_loader: {e}")
    
    # 2. Gemini Entity Extractor
    try:
        from src.tools.gemini_entity_extractor import GeminiEntityExtractor
        extractor = GeminiEntityExtractor()
        adapted = UniversalAdapter(
            tool=extractor,
            tool_id="gemini_entity_extractor",
            method_name="process",
            uncertainty_config={
                'base': 0.25,
                'reasoning': 'LLM-based entity extraction with inherent uncertainty'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="gemini_entity_extractor",
            input_type=DataType.TEXT,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="character_sequence",
            output_construct="knowledge_graph",
            transformation_type="entity_extraction"
        ))
        print("✅ Integrated gemini_entity_extractor")
    except Exception as e:
        print(f"❌ Failed to integrate gemini_entity_extractor: {e}")
    
    # 3. Neo4j Graph Builder
    try:
        from src.tools.neo4j_graph_builder import Neo4jGraphBuilder
        # Neo4j builder gets connection from environment
        builder = Neo4jGraphBuilder()  # No parameters needed
        adapted = UniversalAdapter(
            tool=builder,
            tool_id="neo4j_graph_builder",
            method_name="process",
            uncertainty_config={
                'base': 0.0,
                'success_uncertainty': 0.0,
                'failure_uncertainty': 1.0,
                'reasoning': 'Graph persistence with zero uncertainty on success'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="neo4j_graph_builder",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH,
            input_construct="knowledge_graph",
            output_construct="persisted_graph",
            transformation_type="graph_persistence"
        ))
        print("✅ Integrated neo4j_graph_builder")
    except Exception as e:
        print(f"❌ Failed to integrate neo4j_graph_builder: {e}")

def integrate_legacy_tools(framework: CleanToolFramework):
    """Integrate T-series legacy tools that need adapters"""
    print("\n=== Integrating Legacy Tools (T-series) ===\n")
    
    # T01 PDF Loader
    try:
        from archive.archived.legacy_tools_2025_07_23.t01_pdf_loader import PDFLoader
        pdf_loader = PDFLoader()
        adapted = UniversalAdapter(
            tool=pdf_loader,
            tool_id="t01_pdf_loader",
            uncertainty_config={
                'base': 0.15,
                'reasoning': 'PDF extraction with OCR and formatting uncertainty'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="t01_pdf_loader",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="character_sequence",
            transformation_type="pdf_extraction"
        ))
        print("✅ Integrated t01_pdf_loader")
    except Exception as e:
        print(f"❌ Failed to integrate t01_pdf_loader: {e}")
    
    # T15a Text Chunker
    try:
        from archive.archived.legacy_tools_2025_07_23.t15a_text_chunker import TextChunker
        chunker = TextChunker()
        adapted = UniversalAdapter(
            tool=chunker,
            tool_id="t15a_text_chunker",
            uncertainty_config={
                'base': 0.03,
                'reasoning': 'Deterministic text chunking with minimal uncertainty'
            }
        )
        
        # Text chunker takes text and outputs list of chunks
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="t15a_text_chunker",
            input_type=DataType.TEXT,
            output_type=DataType.TABLE,  # List of chunks as table
            input_construct="character_sequence",
            output_construct="text_chunks",
            transformation_type="text_chunking"
        ))
        print("✅ Integrated t15a_text_chunker")
    except Exception as e:
        print(f"❌ Failed to integrate t15a_text_chunker: {e}")
    
    # T23a SpaCy NER - SKIPPED (uses deprecated spacy)
    print("⚠️  Skipping t23a_spacy_ner - uses deprecated spacy library")
    
    # T27 Relationship Extractor - SKIPPED (uses deprecated spacy)
    print("⚠️  Skipping t27_relationship_extractor - uses deprecated spacy library")
    
    # T31 Entity Builder
    try:
        from archive.archived.legacy_tools_2025_07_23.t31_entity_builder import EntityBuilder
        entity_builder = EntityBuilder()
        adapted = UniversalAdapter(
            tool=entity_builder,
            tool_id="t31_entity_builder",
            uncertainty_config={
                'base': 0.10,
                'reasoning': 'Entity construction and normalization'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="t31_entity_builder",
            input_type=DataType.TABLE,  # Takes entity data
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="entity_data",
            output_construct="entity_graph",
            transformation_type="entity_building"
        ))
        print("✅ Integrated t31_entity_builder")
    except Exception as e:
        print(f"❌ Failed to integrate t31_entity_builder: {e}")
    
    # T34 Edge Builder
    try:
        from archive.archived.legacy_tools_2025_07_23.t34_edge_builder import EdgeBuilder
        edge_builder = EdgeBuilder()
        adapted = UniversalAdapter(
            tool=edge_builder,
            tool_id="t34_edge_builder",
            uncertainty_config={
                'base': 0.12,
                'reasoning': 'Relationship edge construction'
            }
        )
        
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="t34_edge_builder",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="entity_graph",
            output_construct="connected_graph",
            transformation_type="edge_building"
        ))
        print("✅ Integrated t34_edge_builder")
    except Exception as e:
        print(f"❌ Failed to integrate t34_edge_builder: {e}")
    
    # T49 MultiHop Query
    try:
        from archive.archived.legacy_tools_2025_07_23.t49_multihop_query import MultiHopQueryEngine
        query_engine = MultiHopQueryEngine()
        adapted = UniversalAdapter(
            tool=query_engine,
            tool_id="t49_multihop_query",
            uncertainty_config={
                'base': 0.20,
                'reasoning': 'Multi-hop graph traversal and query'
            }
        )
        
        # This tool queries existing graphs
        framework.register_tool(adapted, ToolCapabilities(
            tool_id="t49_multihop_query",
            input_type=DataType.NEO4J_GRAPH,
            output_type=DataType.TABLE,
            input_construct="graph_query",
            output_construct="query_results",
            transformation_type="graph_querying"
        ))
        print("✅ Integrated t49_multihop_query")
    except Exception as e:
        print(f"❌ Failed to integrate t49_multihop_query: {e}")

def test_integrated_pipeline(framework: CleanToolFramework):
    """Test a pipeline with integrated tools"""
    print("\n=== Testing Integrated Pipeline ===\n")
    
    # Create a test file
    test_file = "test_integration.txt"
    with open(test_file, 'w') as f:
        f.write("""
        Brian Chhun is developing the KGAS system at the University of Melbourne.
        The system uses uncertainty propagation for knowledge graph augmentation.
        Dr. Sarah Chen contributed to the uncertainty model design.
        """)
    
    print(f"Created test file: {test_file}")
    
    # Try to find a chain
    chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    
    if chain:
        print(f"Found chain: {' → '.join(chain)}")
        
        # Execute the chain
        result = framework.execute_chain(chain, test_file)
        
        if result.success:
            print(f"\n✅ Pipeline executed successfully!")
            print(f"Total uncertainty: {result.total_uncertainty:.3f}")
            print(f"Step uncertainties: {result.step_uncertainties}")
        else:
            print(f"\n❌ Pipeline failed: {result.error}")
    else:
        print("❌ No chain found from FILE to NEO4J_GRAPH")
    
    # Clean up
    import os
    os.remove(test_file)

def main():
    """Main integration test"""
    print("="*60)
    print("TOOL INTEGRATION WITH UNIVERSAL ADAPTER")
    print("="*60)
    
    # Initialize framework
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="vertical_slice.db"
    )
    
    # Clean Neo4j
    with framework.neo4j.session() as session:
        session.run("MATCH (n:VSEntity) DETACH DELETE n")
        print("✅ Neo4j cleaned")
    
    # Integrate tools
    integrate_ready_tools(framework)
    integrate_legacy_tools(framework)
    
    # Test pipeline
    test_integrated_pipeline(framework)
    
    # Show registered tools
    print("\n=== Registered Tools ===")
    for tool_id, cap in framework.capabilities.items():
        print(f"{tool_id}: {cap.input_type.value} → {cap.output_type.value}")
    
    framework.cleanup()
    print("\n✅ Integration test complete")

if __name__ == "__main__":
    main()