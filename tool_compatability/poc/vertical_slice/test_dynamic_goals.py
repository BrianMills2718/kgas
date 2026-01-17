#!/usr/bin/env python3
"""Test Dynamic Goal Composition - Complete TEXT→VECTOR→TABLE→GRAPH Pipeline"""

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.agent_orchestrator import AgentOrchestrator, AgentRequest
from framework.clean_framework import ToolCapabilities, DataType
from services.vector_service import VectorService  
from services.table_service import TableService
from tools.vector_tool import VectorTool
from tools.table_tool import TableTool
from tools.graph_tool import GraphTool

def test_complete_pipeline():
    """Test complete TEXT→VECTOR→TABLE→GRAPH pipeline with agent composition"""
    print("🧪 Testing Complete Cross-Modal Pipeline")
    print("=" * 60)
    
    # Initialize agent orchestrator
    orchestrator = AgentOrchestrator(
        neo4j_uri='bolt://localhost:7687',
        sqlite_path='vertical_slice.db'
    )
    
    # Create services
    vector_service = VectorService()
    table_service = TableService()
    
    # Register all tools with agent orchestrator
    print("\n📝 Registering complete tool suite...")
    
    orchestrator.register_tool(
        VectorTool(vector_service),
        ToolCapabilities(
            tool_id="VectorTool",
            input_type=DataType.TEXT,
            output_type=DataType.VECTOR,
            input_construct="text",
            output_construct="embedding",
            transformation_type="embedding"
        )
    )
    
    orchestrator.register_tool(
        TableTool(table_service),
        ToolCapabilities(
            tool_id="TableTool", 
            input_type=DataType.VECTOR,
            output_type=DataType.TABLE,
            input_construct="embedding",
            output_construct="stored",
            transformation_type="persistence"
        )
    )
    
    # Register GraphTool for both TABLE→GRAPH and VECTOR→GRAPH transformations  
    # First register TABLE→GRAPH capability
    orchestrator.register_tool(
        GraphTool(neo4j_uri='bolt://localhost:7687'),
        ToolCapabilities(
            tool_id="GraphTool",
            input_type=DataType.TABLE,
            output_type=DataType.GRAPH,
            input_construct="stored",
            output_construct="graph",
            transformation_type="graph_creation"
        )
    )
    
    # Register a second GraphTool instance for VECTOR→GRAPH (direct from VectorTool)
    orchestrator.register_tool(
        GraphTool(neo4j_uri='bolt://localhost:7687'),
        ToolCapabilities(
            tool_id="GraphToolDirect",
            input_type=DataType.VECTOR,
            output_type=DataType.GRAPH,
            input_construct="embedding",
            output_construct="graph",
            transformation_type="direct_graph_creation"
        )
    )
    
    print(f"✅ Registered 4 tool capabilities: VectorTool, TableTool, GraphTool, GraphToolDirect")
    
    # Show available chains
    print("\n🔗 Available complete chains:")
    chains = orchestrator.get_available_chains(DataType.TEXT)
    for chain_name, chain_tools in chains.items():
        print(f"   {chain_name}: {' → '.join(chain_tools)}")
    
    # Test different goal types that should trigger different chains
    test_scenarios = [
        {
            "name": "Simple Embedding",
            "request": "Generate embeddings for this text",
            "data": "Machine learning is a subset of artificial intelligence.",
            "expected_chain": ["VectorTool"]
        },
        {
            "name": "Text Analysis and Storage", 
            "request": "Analyze and store this text for later retrieval",
            "data": "Deep learning uses neural networks with multiple layers to learn complex patterns in data.",
            "expected_chain": ["VectorTool", "TableTool"]
        },
        {
            "name": "Knowledge Graph Creation",
            "request": "Create a knowledge graph from this text to understand relationships",
            "data": "Artificial intelligence encompasses machine learning, which includes deep learning. Neural networks are fundamental to deep learning algorithms.",
            "expected_chain": ["VectorTool", "TableTool", "GraphTool"]
        },
        {
            "name": "Complete Analysis Pipeline",
            "request": "Perform complete analysis including graph visualization of concepts",
            "data": "Natural language processing is a branch of AI that helps computers understand human language. It uses techniques from machine learning and computational linguistics.",
            "expected_chain": ["VectorTool", "TableTool", "GraphTool"]
        }
    ]
    
    print(f"\n🚀 Testing Dynamic Goal-Based Chain Composition...")
    
    results = []
    for scenario in test_scenarios:
        print(f"\n{'='*20} {scenario['name']} {'='*20}")
        print(f"Request: '{scenario['request']}'")
        print(f"Data: '{scenario['data'][:60]}...'")
        
        request = AgentRequest(
            request=scenario['request'],
            data=scenario['data'],
            data_type="TEXT"
        )
        
        response = orchestrator.execute_agent_request(request)
        
        if response.success:
            print(f"✅ SUCCESS")
            print(f"   Agent composed: {' → '.join(response.chain_used)}")
            print(f"   Goal type: {response.goal_evaluation.get('goal_type', 'unknown')}")
            print(f"   Complexity: {response.goal_evaluation.get('complexity', 'unknown')}")
            print(f"   Steps executed: {len(response.result.step_uncertainties) if response.result else 0}")
            
            if response.result and response.result.success:
                print(f"   Final uncertainty: {response.result.total_uncertainty:.3f}")
                
                # Show final result details
                if len(response.chain_used) >= 3 and 'GraphTool' in response.chain_used:
                    # Graph creation completed
                    final_data = response.result.data
                    if isinstance(final_data, dict) and 'graph_stats' in final_data:
                        stats = final_data['graph_stats']
                        print(f"   Graph created: {stats['nodes']} nodes, {stats['edges']} edges")
                        print(f"   Graph density: {stats['density']:.3f}")
            
            # Check if agent selected expected chain
            expected = scenario['expected_chain']
            if len(response.chain_used) >= len(expected):
                chain_match = all(exp in response.chain_used for exp in expected)
                print(f"   Chain expectation: {'✅ Met' if chain_match else '⚠️  Different than expected'}")
            
            results.append({
                'scenario': scenario['name'],
                'success': True,
                'chain': response.chain_used,
                'goal_type': response.goal_evaluation.get('goal_type'),
                'steps': len(response.result.step_uncertainties) if response.result else 0
            })
        else:
            print(f"❌ FAILED: {response.error}")
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': response.error
            })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🏁 Dynamic Goal Composition Test Summary")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    for result in successful:
        print(f"   {result['scenario']}: {' → '.join(result['chain'])} ({result['steps']} steps)")
    
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for result in failed:
            print(f"   {result['scenario']}: {result['error']}")
    
    # Agent capability demonstration
    print(f"\n🎯 Agent Capability Analysis:")
    print(f"   Available chains: {len(chains)}")
    print(f"   Maximum chain length: {max(len(chain) for chain in chains.values()) if chains else 0}")
    print(f"   Goal types detected: {set(r.get('goal_type') for r in results if r['success'] and r.get('goal_type'))}")
    
    return len(successful) == len(results)

if __name__ == "__main__":
    success = test_complete_pipeline()
    if success:
        print("\n🎉 All dynamic goal tests passed!")
    else:
        print("\n⚠️  Some tests failed - see details above")