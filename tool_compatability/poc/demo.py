#!/usr/bin/env python3
"""
POC Demo - Shows type-based tool composition

This script demonstrates:
1. Tool registration
2. Automatic compatibility detection
3. Chain discovery
4. Basic tool execution
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from poc.registry import ToolRegistry
from poc.tools import TextLoader
from poc.data_types import DataType, DataSchema


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main demo function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("Type-Based Tool Composition POC Demo")
    print("=" * 60)
    print()
    
    # Initialize registry
    print("1. Initializing Registry")
    print("-" * 40)
    registry = ToolRegistry()
    print(f"Created: {registry}")
    print()
    
    # Register tools
    print("2. Registering Tools")
    print("-" * 40)
    
    # Register TextLoader
    text_loader = TextLoader()
    registry.register(text_loader)
    print(f"Registered: {text_loader}")
    print()
    
    # Show registry stats
    print("3. Registry Statistics")
    print("-" * 40)
    stats = registry.get_statistics()
    print(f"Total tools: {stats['tool_count']}")
    print(f"Total connections: {stats['edge_count']}")
    print("\nTools:")
    for tool_id, tool_stats in stats['tools'].items():
        print(f"  - {tool_id}: {tool_stats['input_type']} → {tool_stats['output_type']}")
    print()
    
    # Show compatibility matrix
    print("4. Compatibility Matrix")
    print("-" * 40)
    print(registry.visualize_compatibility())
    print()
    
    # Test chain discovery (limited for now with just one tool)
    print("5. Chain Discovery")
    print("-" * 40)
    
    # Find chains from FILE to TEXT
    chains = registry.find_chains(DataType.FILE, DataType.TEXT)
    print(f"Chains from FILE to TEXT: {len(chains)} found")
    for i, chain in enumerate(chains, 1):
        print(f"  Chain {i}: {' → '.join(chain)}")
    
    if not chains:
        print("  (No chains found - this is expected with only one tool)")
    print()
    
    # Test tool execution
    print("6. Tool Execution Test")
    print("-" * 40)
    
    # Create a test file
    test_file = Path("/tmp/poc_test.txt")
    test_content = "This is a test document for the POC.\nIt contains multiple lines.\nTesting the TextLoader tool."
    
    print(f"Creating test file: {test_file}")
    test_file.write_text(test_content)
    
    # Create FileData
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=len(test_content),
        mime_type="text/plain"
    )
    
    print(f"Input data: FileData(path={test_file}, size={len(test_content)} bytes)")
    
    # Execute TextLoader
    print("\nExecuting TextLoader...")
    result = text_loader.process(file_data)
    
    if result.success:
        print(f"✓ Success!")
        print(f"  Duration: {result.metrics.duration_seconds:.3f}s")
        print(f"  Memory used: {result.metrics.memory_used_mb:.1f}MB")
        print(f"  Output preview: {result.data.truncated_preview(50)}...")
        print(f"  Checksum: {result.data.checksum}")
    else:
        print(f"✗ Failed: {result.error}")
    print()
    
    # Test chain execution (if we have a chain)
    if chains:
        print("7. Chain Execution Test")
        print("-" * 40)
        chain = chains[0]
        print(f"Executing chain: {' → '.join(chain)}")
        
        chain_result = registry.execute_chain(chain, file_data)
        
        if chain_result.success:
            print(f"✓ Chain executed successfully!")
            print(f"  Total duration: {chain_result.duration_seconds:.3f}s")
            print(f"  Total memory: {chain_result.memory_used_mb:.1f}MB")
            print(f"  Steps executed: {len(chain_result.intermediate_results)}")
        else:
            print(f"✗ Chain failed: {chain_result.error}")
    else:
        print("7. Chain Execution Test")
        print("-" * 40)
        print("  (Skipped - no chains available with single tool)")
    
    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    
    # Clean up
    if test_file.exists():
        test_file.unlink()
        print("\n(Test file cleaned up)")


if __name__ == "__main__":
    main()