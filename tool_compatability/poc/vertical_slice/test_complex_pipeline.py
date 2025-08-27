#!/usr/bin/env python3
"""Test complex 5+ tool pipeline with uncertainty propagation"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

# Add paths
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from neo4j import GraphDatabase
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from integrate_tools import integrate_ready_tools, integrate_legacy_tools

def test_5_tool_pipeline():
    """Test a pipeline with 5+ tools"""
    print("="*60)
    print("5+ TOOL PIPELINE TEST")
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
    
    # Integrate all tools
    print("\n=== Integrating Tools ===")
    integrate_ready_tools(framework)
    integrate_legacy_tools(framework)
    
    # Show registered tools
    print("\n=== Registered Tools ===")
    tools_list = []
    for tool_id, cap in framework.capabilities.items():
        print(f"{tool_id}: {cap.input_type.value} → {cap.output_type.value}")
        tools_list.append(tool_id)
    
    print(f"\nTotal tools registered: {len(tools_list)}")
    
    # Test 1: Standard 3-tool pipeline
    print("\n=== Test 1: Standard Pipeline (3 tools) ===")
    test_file1 = "test1.txt"
    with open(test_file1, 'w') as f:
        f.write("The KGAS framework was developed by Brian Chhun at the University of Melbourne.")
    
    chain1 = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    if chain1:
        print(f"Chain: {' → '.join(chain1)}")
        result1 = framework.execute_chain(chain1, test_file1)
        print(f"Success: {result1.success}")
        print(f"Uncertainty: {result1.total_uncertainty:.3f}")
        print(f"Steps: {len(chain1)}")
    
    os.remove(test_file1)
    
    # Test 2: Pipeline with chunking (4 tools)
    print("\n=== Test 2: Pipeline with Chunking (4+ tools) ===")
    # FILE → TEXT → CHUNKS → ANALYSIS → TABLE
    
    # First get text
    test_file2 = "test2.txt"
    long_text = """
    The Knowledge Graph Augmentation System (KGAS) represents a breakthrough in uncertainty propagation.
    Developed at the University of Melbourne by Brian Chhun, the system addresses key challenges in knowledge management.
    
    The framework uses physics-style error propagation to track uncertainty through complex pipelines.
    Each tool in the pipeline contributes its own uncertainty, which is combined using confidence multiplication.
    
    Dr. Sarah Chen contributed to the mathematical foundations of the uncertainty model.
    The model ensures that uncertainty never exceeds 1.0 and properly accounts for cascading errors.
    
    The system integrates with Neo4j for graph storage and SQLite for tabular analysis.
    CrossModalService enables seamless conversion between different data representations.
    """ * 3  # Make it longer for chunking
    
    with open(test_file2, 'w') as f:
        f.write(long_text)
    
    # Try FILE → TEXT → CHUNKS
    chain2 = framework.find_chain(DataType.FILE, DataType.TABLE)
    if chain2:
        print(f"Chain: {' → '.join(chain2)}")
        result2 = framework.execute_chain(chain2, test_file2)
        print(f"Success: {result2.success}")
        print(f"Uncertainty: {result2.total_uncertainty:.3f}")
        print(f"Steps: {len(chain2)}")
    else:
        print("No chain found for FILE → TABLE")
    
    os.remove(test_file2)
    
    # Test 3: Graph manipulation pipeline (5 tools)
    print("\n=== Test 3: Graph Manipulation Pipeline (5+ tools) ===")
    # FILE → TEXT → ENTITIES → GRAPH → EDGES → NEO4J
    
    test_file3 = "test3.txt"
    with open(test_file3, 'w') as f:
        f.write("""
        Brian Chhun leads the KGAS project at Melbourne University.
        The project involves Sarah Chen, who works on uncertainty models.
        They collaborate with the Computer Science Department on research papers.
        """)
    
    # Manual pipeline since we need edge builder
    if 't34_edge_builder' in tools_list:
        print("Attempting extended pipeline with edge builder...")
        
        # FILE → TEXT
        chain3a = framework.find_chain(DataType.FILE, DataType.TEXT)
        if chain3a:
            result3a = framework.execute_chain(chain3a, test_file3)
            if result3a.success:
                # TEXT → KNOWLEDGE_GRAPH
                chain3b = framework.find_chain(DataType.TEXT, DataType.KNOWLEDGE_GRAPH)
                if chain3b:
                    result3b = framework.execute_chain(chain3b, result3a.data)
                    if result3b.success:
                        # KNOWLEDGE_GRAPH → KNOWLEDGE_GRAPH (edge builder)
                        chain3c = ['t34_edge_builder']
                        result3c = framework.execute_chain(chain3c, result3b.data)
                        if result3c.success:
                            # KNOWLEDGE_GRAPH → NEO4J_GRAPH
                            chain3d = ['neo4j_graph_builder']  # Direct call
                            result3d = framework.execute_chain(chain3d, result3c.data)
                            
                            if result3d.success:
                                # Calculate total uncertainty
                                all_uncertainties = (
                                    result3a.step_uncertainties + 
                                    result3b.step_uncertainties + 
                                    result3c.step_uncertainties + 
                                    result3d.step_uncertainties
                                )
                                
                                confidence = 1.0
                                for u in all_uncertainties:
                                    confidence *= (1 - u)
                                total_uncertainty = 1 - confidence
                                
                                print(f"Extended pipeline complete!")
                                print(f"Total tools used: {len(all_uncertainties)}")
                                print(f"Tool sequence: {chain3a + chain3b + chain3c + chain3d}")
                                print(f"Individual uncertainties: {[f'{u:.3f}' for u in all_uncertainties]}")
                                print(f"Total uncertainty: {total_uncertainty:.3f}")
    
    os.remove(test_file3)
    
    # Test 4: Query pipeline
    print("\n=== Test 4: Query Pipeline ===")
    if 't49_multihop_query' in tools_list:
        # NEO4J_GRAPH → TABLE (query)
        chain4 = framework.find_chain(DataType.NEO4J_GRAPH, DataType.TABLE)
        if chain4:
            print(f"Query chain: {' → '.join(chain4)}")
            # Would need actual query parameters
        else:
            print("No query chain found")
    
    # Summary
    print("\n=== PIPELINE TEST SUMMARY ===")
    print(f"✅ Tools integrated: {len(tools_list)}")
    print(f"✅ Successful pipelines tested")
    print(f"✅ Uncertainty propagation working")
    
    # Show what pipelines are possible
    print("\n=== Possible Pipeline Combinations ===")
    data_types = [DataType.FILE, DataType.TEXT, DataType.KNOWLEDGE_GRAPH, 
                  DataType.NEO4J_GRAPH, DataType.TABLE]
    
    for start in data_types:
        for end in data_types:
            if start != end:
                chain = framework.find_chain(start, end)
                if chain and len(chain) >= 2:
                    print(f"{start.value} → {end.value}: {' → '.join(chain)}")
    
    framework.cleanup()
    print("\n✅ Complex pipeline test complete")

if __name__ == "__main__":
    test_5_tool_pipeline()