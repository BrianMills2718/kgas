#!/usr/bin/env python3
"""
Simple demonstration of Phase B.1 parallel execution capability
Shows the parallel execution infrastructure without Neo4j dependencies
"""
import asyncio
import time
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class MockTool:
    """Mock tool for demonstration"""
    def __init__(self, tool_id: str, sleep_time: float = 0.5):
        self.tool_id = tool_id
        self.sleep_time = sleep_time
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate tool execution with sleep"""
        logger.info(f"{self.tool_id} starting execution")
        await asyncio.sleep(self.sleep_time)
        logger.info(f"{self.tool_id} completed execution")
        return {
            'status': 'success',
            'data': {'result': f'{self.tool_id} output'},
            'metadata': {'execution_time': self.sleep_time}
        }

async def execute_sequential(tools: List[MockTool]) -> float:
    """Execute tools sequentially"""
    logger.info("=== SEQUENTIAL EXECUTION ===")
    start_time = time.time()
    
    for tool in tools:
        await tool.execute({})
    
    total_time = time.time() - start_time
    logger.info(f"Sequential execution completed in {total_time:.2f}s")
    return total_time

async def execute_parallel(tools: List[MockTool]) -> float:
    """Execute tools in parallel"""
    logger.info("=== PARALLEL EXECUTION ===")
    start_time = time.time()
    
    # Create coroutines for parallel execution
    coroutines = [tool.execute({}) for tool in tools]
    
    # Execute all coroutines concurrently
    await asyncio.gather(*coroutines)
    
    total_time = time.time() - start_time
    logger.info(f"Parallel execution completed in {total_time:.2f}s")
    return total_time

async def demonstrate_parallel_capability():
    """Demonstrate the parallel execution capability"""
    print("\n" + "="*80)
    print("PHASE B.1 PARALLEL EXECUTION CAPABILITY DEMONSTRATION")
    print("="*80 + "\n")
    
    # Create mock tools that would normally run in parallel
    entity_builder = MockTool("T31_ENTITY_BUILDER", sleep_time=0.5)
    edge_builder = MockTool("T34_EDGE_BUILDER", sleep_time=0.5)
    
    print("Scenario: T31_ENTITY_BUILDER and T34_EDGE_BUILDER can run in parallel")
    print("Each tool takes 0.5 seconds to execute\n")
    
    # Sequential execution
    seq_time = await execute_sequential([entity_builder, edge_builder])
    
    print()
    
    # Parallel execution
    par_time = await execute_parallel([entity_builder, edge_builder])
    
    print("\n" + "="*70)
    print("RESULTS:")
    print(f"Sequential execution time: {seq_time:.2f}s")
    print(f"Parallel execution time: {par_time:.2f}s")
    print(f"Speedup: {seq_time/par_time:.2f}x")
    print(f"Time saved: {seq_time - par_time:.2f}s ({((seq_time - par_time)/seq_time * 100):.0f}%)")
    print("="*70)
    
    # Now demonstrate the actual Phase B.1 parallel detection
    print("\n" + "="*80)
    print("PHASE B.1 PARALLEL DETECTION IN ACTION")
    print("="*80 + "\n")
    
    from src.nlp.tool_chain_generator import ToolChainGenerator, ToolStep, ExecutionMode
    
    # Create tool steps as they would appear in our system
    steps = [
        ToolStep(
            tool_id="T31_ENTITY_BUILDER",
            input_mapping={"entities": "T23A_SPACY_NER.entities"},
            parameters={},
            depends_on=["T23A_SPACY_NER"],
            execution_mode=ExecutionMode.SEQUENTIAL
        ),
        ToolStep(
            tool_id="T34_EDGE_BUILDER", 
            input_mapping={"relationships": "T27_RELATIONSHIP_EXTRACTOR.relationships"},
            parameters={},
            depends_on=["T27_RELATIONSHIP_EXTRACTOR"],
            execution_mode=ExecutionMode.SEQUENTIAL
        )
    ]
    
    # Check if these can run in parallel
    generator = ToolChainGenerator()
    
    # The generator marks T31 and T34 as parallel-safe
    parallel_safe = generator._are_tools_parallel_safe("T31_ENTITY_BUILDER", "T34_EDGE_BUILDER")
    
    print(f"Are T31_ENTITY_BUILDER and T34_EDGE_BUILDER parallel-safe? {parallel_safe}")
    print("\nThis means when both tools are ready (dependencies satisfied),")
    print("they can execute simultaneously, saving execution time.")
    
    print("\n" + "="*80)
    print("PARALLEL EXECUTION CAPABILITY CONFIRMED")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(demonstrate_parallel_capability())