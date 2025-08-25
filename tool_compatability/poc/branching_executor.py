#!/usr/bin/env python3
"""
Branching Executor - Enable split-process-merge patterns
PhD Research: Advanced composition patterns
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.data_types import DataType

class BranchingExecutor:
    """Execute branching tool compositions"""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_history = []
    
    def execute_branching(
        self,
        input_data: Any,
        branches: Dict[str, List[str]],
        merge_strategy: str = "combine"
    ) -> Dict[str, Any]:
        """
        Execute multiple branches in parallel
        
        Args:
            input_data: Initial input for all branches
            branches: Dict of branch_name -> tool_chain
            merge_strategy: How to combine results
            
        Returns:
            Combined results from all branches
        """
        
        print(f"\n{'='*60}")
        print(f"BRANCHING EXECUTION: {len(branches)} branches")
        print(f"{'='*60}")
        
        results = {}
        
        # Execute branches in parallel
        with ThreadPoolExecutor(max_workers=len(branches)) as executor:
            futures = {}
            
            for branch_name, tool_chain in branches.items():
                print(f"\nBranch '{branch_name}': {' → '.join(tool_chain)}")
                future = executor.submit(
                    self._execute_chain,
                    tool_chain,
                    input_data,
                    branch_name
                )
                futures[future] = branch_name
            
            # Collect results as they complete
            for future in as_completed(futures):
                branch_name = futures[future]
                try:
                    result = future.result()
                    results[branch_name] = result
                    print(f"✅ Branch '{branch_name}' completed")
                except Exception as e:
                    print(f"❌ Branch '{branch_name}' failed: {e}")
                    results[branch_name] = {"error": str(e)}
        
        # Merge results based on strategy
        merged = self._merge_results(results, merge_strategy)
        
        print(f"\n{'='*60}")
        print(f"MERGE COMPLETE: Strategy={merge_strategy}")
        print(f"{'='*60}")
        
        return merged
    
    def _execute_chain(
        self,
        tool_chain: List[str],
        input_data: Any,
        branch_name: str
    ) -> Any:
        """Execute a single tool chain"""
        
        current_data = input_data
        
        for tool_id in tool_chain:
            tool = self.registry.tools.get(tool_id)
            if not tool:
                raise ValueError(f"Tool {tool_id} not found")
            
            result = tool.process(current_data)
            if not result.success:
                raise RuntimeError(f"Tool {tool_id} failed: {result.error}")
            
            current_data = result.data
        
        return current_data
    
    def _merge_results(
        self,
        results: Dict[str, Any],
        strategy: str
    ) -> Dict[str, Any]:
        """Merge results from multiple branches"""
        
        if strategy == "combine":
            # Simply combine all results
            return {
                "branches": results,
                "merge_strategy": strategy,
                "timestamp": time.time()
            }
        
        elif strategy == "aggregate":
            # Aggregate similar fields
            aggregated = {}
            for branch_name, result in results.items():
                if hasattr(result, '__dict__'):
                    for key, value in result.__dict__.items():
                        if key not in aggregated:
                            aggregated[key] = []
                        aggregated[key].append(value)
            return aggregated
        
        elif strategy == "consensus":
            # Find consensus among branches
            # (Implement voting, averaging, etc.)
            pass
        
        else:
            return results
    
    def find_alternative_paths(
        self,
        start_type: DataType,
        end_type: DataType,
        failed_chain: List[str]
    ) -> List[List[str]]:
        """Find alternative paths when one fails"""
        
        all_chains = self.registry.find_chains(start_type, end_type)
        
        # Filter out the failed chain
        alternatives = [
            chain for chain in all_chains
            if chain != failed_chain
        ]
        
        return alternatives
    
    def execute_with_fallback(
        self,
        input_data: Any,
        start_type: DataType,
        end_type: DataType,
        max_attempts: int = 3
    ) -> Any:
        """Execute with automatic fallback to alternative paths"""
        
        chains = self.registry.find_chains(start_type, end_type)
        
        if not chains:
            raise ValueError(f"No chains found from {start_type} to {end_type}")
        
        for i, chain in enumerate(chains[:max_attempts]):
            print(f"\nAttempt {i+1}: {' → '.join(chain)}")
            
            try:
                result = self._execute_chain(chain, input_data, f"attempt_{i+1}")
                print(f"✅ Success on attempt {i+1}")
                return result
            
            except Exception as e:
                print(f"❌ Failed: {e}")
                
                if i < len(chains) - 1 and i < max_attempts - 1:
                    print("Trying alternative path...")
                else:
                    raise RuntimeError(f"All {i+1} attempts failed")
        
        raise RuntimeError("No valid chains succeeded")


def demo_branching():
    """Demonstrate branching execution"""
    
    from poc.tools.text_loader import TextLoader
    from poc.tools.entity_extractor import EntityExtractor
    from poc.tools.graph_builder import GraphBuilder
    from poc.data_types import DataSchema
    import os
    
    # Setup
    registry = ToolRegistry()
    registry.register(TextLoader())
    registry.register(EntityExtractor())
    registry.register(GraphBuilder())
    
    executor = BranchingExecutor(registry)
    
    # Create test file
    test_content = """
    Apple Inc. announced new products in Cupertino.
    Microsoft Corp. released updates in Seattle.
    Google LLC expanded operations in Mountain View.
    """
    
    test_file = "/tmp/branching_test.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Define branches
    branches = {
        "entity_analysis": ["TextLoader", "EntityExtractor"],
        "graph_creation": ["TextLoader", "EntityExtractor", "GraphBuilder"],
    }
    
    # Execute branches
    file_data = DataSchema.FileData(
        path=test_file,
        size_bytes=os.path.getsize(test_file),
        mime_type="text/plain"
    )
    
    results = executor.execute_branching(file_data, branches)
    
    print("\nResults from branches:")
    for branch_name, result in results["branches"].items():
        print(f"\n{branch_name}:")
        if hasattr(result, 'entities'):
            print(f"  Found {len(result.entities)} entities")
        elif hasattr(result, 'graph_id'):
            print(f"  Created graph: {result.graph_id}")
    
    # Demo fallback execution
    print("\n" + "="*60)
    print("FALLBACK EXECUTION DEMO")
    print("="*60)
    
    try:
        result = executor.execute_with_fallback(
            file_data,
            DataType.FILE,
            DataType.GRAPH
        )
        print(f"\nFinal result: Graph with {result.node_count} nodes")
    except Exception as e:
        print(f"\nFallback failed: {e}")


if __name__ == "__main__":
    demo_branching()