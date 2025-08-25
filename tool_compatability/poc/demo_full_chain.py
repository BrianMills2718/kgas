#!/usr/bin/env python3
"""
Full Chain Demo - Shows complete FILE → TEXT → ENTITIES → GRAPH pipeline

This script demonstrates:
1. All three tools working together
2. Automatic chain discovery
3. End-to-end pipeline execution
4. Performance metrics collection
"""

import sys
import logging
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools import TextLoader, EntityExtractor, GraphBuilder
from poc.data_types import DataType, DataSchema


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_test_document() -> Path:
    """Create a test document with rich entity content"""
    test_file = Path("/tmp/poc_entities_test.txt")
    
    content = """
    Nexora Corporation Announces Strategic Partnership with TechVentures

    SAN FRANCISCO, CA - January 25, 2025 - Nexora Corporation, a leading provider of 
    advanced AI solutions, today announced a strategic partnership with TechVentures 
    International to develop next-generation quantum computing applications.

    Sarah Mitchell, CEO of Nexora, stated: "This partnership with TechVentures represents 
    a significant milestone in our journey to democratize quantum computing. Together with 
    John Anderson and his team at TechVentures, we will accelerate the development of 
    practical quantum applications for enterprise customers."

    The partnership will focus on three key areas:
    1. Quantum machine learning algorithms for financial modeling
    2. Drug discovery applications in partnership with BioPharma Labs
    3. Cryptographic security solutions for government agencies

    TechVentures, headquartered in London, UK, brings extensive experience in quantum 
    hardware development. Their research facility in Cambridge has produced several 
    breakthrough innovations in quantum error correction.

    Dr. Emily Chen, Chief Technology Officer at Nexora, will lead the joint research 
    team based in Palo Alto, California. The team expects to deliver its first commercial 
    product, QuantumML Pro, by Q3 2025.

    About Nexora Corporation:
    Nexora is a San Francisco-based technology company specializing in artificial 
    intelligence and quantum computing solutions. Founded in 2020 by Sarah Mitchell 
    and Dr. Emily Chen, the company has raised $150 million in Series B funding led 
    by Global Ventures Capital.

    About TechVentures International:
    TechVentures is a London-based quantum computing company founded by John Anderson 
    in 2018. The company operates research facilities in Cambridge, UK and Munich, Germany.
    """
    
    test_file.write_text(content)
    return test_file


def main():
    """Main demo function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("Type-Based Tool Composition - Full Chain Demo")
    print("=" * 80)
    print()
    
    # Create test document
    print("1. Creating Test Document")
    print("-" * 40)
    test_file = create_test_document()
    print(f"Created: {test_file}")
    print(f"Size: {test_file.stat().st_size} bytes")
    print()
    
    # Initialize registry
    print("2. Initializing Registry and Tools")
    print("-" * 40)
    registry = ToolRegistry()
    
    # Register all tools
    text_loader = TextLoader()
    entity_extractor = EntityExtractor()
    graph_builder = GraphBuilder()
    
    registry.register(text_loader)
    registry.register(entity_extractor)
    registry.register(graph_builder)
    
    print(f"Registered {len(registry.tools)} tools:")
    for tool_id, tool in registry.tools.items():
        print(f"  - {tool_id}: {tool.input_type.value} → {tool.output_type.value}")
    print()
    
    # Show compatibility matrix
    print("3. Tool Compatibility Matrix")
    print("-" * 40)
    print(registry.visualize_compatibility())
    print()
    
    # Discover chains
    print("4. Chain Discovery")
    print("-" * 40)
    
    # Find chains from FILE to GRAPH
    chains = registry.find_chains(DataType.FILE, DataType.GRAPH)
    print(f"Chains from FILE to GRAPH: {len(chains)} found")
    for i, chain in enumerate(chains, 1):
        print(f"  Chain {i}: {' → '.join(chain)}")
    
    # Find chains from FILE to ENTITIES
    chains_to_entities = registry.find_chains(DataType.FILE, DataType.ENTITIES)
    print(f"\nChains from FILE to ENTITIES: {len(chains_to_entities)} found")
    for i, chain in enumerate(chains_to_entities, 1):
        print(f"  Chain {i}: {' → '.join(chain)}")
    print()
    
    # Execute full chain
    print("5. Executing Full Chain: FILE → TEXT → ENTITIES → GRAPH")
    print("-" * 40)
    
    # Prepare input
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=test_file.stat().st_size,
        mime_type="text/plain"
    )
    
    # Find the chain
    chain_to_execute = registry.find_shortest_chain(DataType.FILE, DataType.GRAPH)
    
    if chain_to_execute:
        print(f"Executing chain: {' → '.join(chain_to_execute)}")
        print()
        
        # Execute chain
        result = registry.execute_chain(chain_to_execute, file_data)
        
        if result.success:
            print("✓ Chain executed successfully!")
            print(f"  Total duration: {result.duration_seconds:.3f}s")
            print(f"  Total memory: {result.memory_used_mb:.2f}MB")
            print()
            
            # Show intermediate results
            print("Intermediate Results:")
            for step in result.intermediate_results:
                print(f"  - {step['tool']}: {step['duration']:.3f}s, {step['memory']:.2f}MB")
            print()
            
            # Show final output
            if isinstance(result.final_output, DataSchema.GraphData):
                print("Final Graph Statistics:")
                print(f"  Graph ID: {result.final_output.graph_id}")
                print(f"  Nodes: {result.final_output.node_count}")
                print(f"  Edges: {result.final_output.edge_count}")
                print(f"  Created: {result.final_output.created_timestamp}")
        else:
            print(f"✗ Chain failed: {result.error}")
    else:
        print("No chain found from FILE to GRAPH")
        print("Executing tools individually for demonstration...")
        print()
        
        # Execute individually
        print("Step 1: FILE → TEXT")
        text_result = text_loader.process(file_data)
        if text_result.success:
            print(f"  ✓ Text loaded: {text_result.data.char_count} characters")
            print(f"  Preview: {text_result.data.truncated_preview(60)}...")
        print()
        
        print("Step 2: TEXT → ENTITIES")
        if text_result.success:
            entities_result = entity_extractor.process(text_result.data)
            if entities_result.success:
                print(f"  ✓ Entities extracted:")
                print(f"    - Total entities: {len(entities_result.data.entities)}")
                print(f"    - Total relationships: {len(entities_result.data.relationships)}")
                
                # Show entity breakdown
                entity_counts = entities_result.data.entity_count_by_type()
                print(f"    - By type: {entity_counts}")
                
                # Show sample entities
                print("\n  Sample entities:")
                for entity in entities_result.data.entities[:5]:
                    print(f"    - {entity.text} ({entity.type}, confidence: {entity.confidence:.2f})")
        print()
        
        print("Step 3: ENTITIES → GRAPH")
        if entities_result.success:
            graph_result = graph_builder.process(entities_result.data)
            if graph_result.success:
                print(f"  ✓ Graph built:")
                print(f"    - Graph ID: {graph_result.data.graph_id}")
                print(f"    - Nodes: {graph_result.data.node_count}")
                print(f"    - Edges: {graph_result.data.edge_count}")
    
    print()
    
    # Export graph for visualization
    print("6. Exporting Registry Graph")
    print("-" * 40)
    graph_file = Path("/tmp/poc_registry_graph.json")
    registry.export_graph(str(graph_file))
    print(f"Registry graph exported to: {graph_file}")
    print()
    
    # Show statistics
    print("7. Registry Statistics")
    print("-" * 40)
    stats = registry.get_statistics()
    print(json.dumps(stats, indent=2))
    print()
    
    print("=" * 80)
    print("Full Chain Demo Complete!")
    print("=" * 80)
    
    # Clean up
    if test_file.exists():
        test_file.unlink()
        print("\n(Test file cleaned up)")


if __name__ == "__main__":
    main()