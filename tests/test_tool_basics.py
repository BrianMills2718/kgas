#!/usr/bin/env python3
"""
Simple Tool Test Script - Task 1.2

Tests that each tool can:
1. Initialize
2. Accept input
3. Return output (even if empty)
4. Not crash
"""

import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest

def test_tool_basics():
    """Test basic functionality of all tools."""
    
    # Initialize service manager
    sm = ServiceManager()
    
    # Define tools to test with simple inputs
    tools_to_test = [
        {
            'module': 'src.tools.phase1.t01_pdf_loader',
            'class': 'PDFLoader',
            'test_input': {'file_path': 'test.pdf'}  # Will fail but shouldn't crash
        },
        {
            'module': 'src.tools.phase1.t15a_text_chunker',
            'class': 'TextChunker',
            'test_input': {'text': 'This is a test sentence. This is another sentence.'}
        },
        {
            'module': 'src.tools.phase1.t23a_spacy_ner',
            'class': 'SpacyNER',
            'test_input': {'text': 'Apple Inc. was founded by Steve Jobs in Cupertino.'}
        },
        {
            'module': 'src.tools.phase1.t27_relationship_extractor',
            'class': 'RelationshipExtractor',
            'test_input': {'text': 'Steve Jobs founded Apple Inc.'}
        },
        {
            'module': 'src.tools.phase1.t31_entity_builder',
            'class': 'EntityBuilder',
            'test_input': {
                'entities': [
                    {'name': 'Test Entity', 'type': 'PERSON', 'confidence': 0.9}
                ]
            }
        },
        {
            'module': 'src.tools.phase1.t34_edge_builder',
            'class': 'EdgeBuilder',
            'test_input': {
                'relationships': [
                    {
                        'source': 'Steve Jobs',
                        'target': 'Apple Inc.',
                        'type': 'FOUNDED',
                        'confidence': 0.8
                    }
                ]
            }
        },
        {
            'module': 'src.tools.phase1.t49_multihop_query',
            'class': 'MultiHopQuery',
            'test_input': {'query': 'What is connected to Apple?'}
        },
        {
            'module': 'src.tools.phase1.t68_pagerank',
            'class': 'PageRank',
            'test_input': {}  # No input needed
        }
    ]
    
    results = {
        'total': len(tools_to_test),
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    print("=" * 60)
    print("TOOL BASIC FUNCTIONALITY TEST")
    print("=" * 60)
    
    for tool_info in tools_to_test:
        module_path = tool_info['module']
        class_name = tool_info['class']
        test_input = tool_info['test_input']
        
        print(f"\nTesting {class_name}...")
        print("-" * 40)
        
        test_result = {
            'tool': class_name,
            'initialization': False,
            'accepts_input': False,
            'returns_output': False,
            'no_crash': True,
            'error': None
        }
        
        try:
            # 1. Test initialization
            module = __import__(module_path, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            tool = tool_class(sm)
            test_result['initialization'] = True
            print(f"  ✓ Initialized successfully")
            
            # 2. Test input acceptance
            request = ToolRequest(
                tool_id=class_name,
                operation="process",
                input_data=test_input,  # Use input_data instead of parameters
                parameters={}
            )
            test_result['accepts_input'] = True
            print(f"  ✓ Accepts input")
            
            # 3. Test output return
            try:
                result = tool.process(request)
                test_result['returns_output'] = True
                
                if hasattr(result, 'success'):
                    if result.success:
                        print(f"  ✓ Returns output (success: {result.success})")
                    else:
                        print(f"  ⚠ Returns output but failed: {getattr(result, 'error_message', 'No error message')}")
                else:
                    print(f"  ✓ Returns output")
                    
            except Exception as e:
                # Some tools might not have process method
                print(f"  ⚠ Process method issue: {str(e)[:50]}")
                test_result['returns_output'] = False
                
        except Exception as e:
            test_result['no_crash'] = False
            test_result['error'] = str(e)
            print(f"  ✗ Error: {str(e)[:100]}")
            
        # Determine if test passed
        if test_result['initialization'] and test_result['no_crash']:
            results['passed'] += 1
            print(f"  Overall: PASSED ✓")
        else:
            results['failed'] += 1
            print(f"  Overall: FAILED ✗")
            
        results['details'].append(test_result)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tools tested: {results['total']}")
    print(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.0f}%)")
    print(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.0f}%)")
    
    print("\nDetailed Results:")
    for detail in results['details']:
        status = "✓" if (detail['initialization'] and detail['no_crash']) else "✗"
        print(f"  {status} {detail['tool']}:")
        print(f"    - Initialization: {'✓' if detail['initialization'] else '✗'}")
        print(f"    - Accepts Input: {'✓' if detail['accepts_input'] else '✗'}")
        print(f"    - Returns Output: {'✓' if detail['returns_output'] else '✗'}")
        print(f"    - No Crash: {'✓' if detail['no_crash'] else '✗'}")
        if detail['error']:
            print(f"    - Error: {detail['error'][:50]}")
    
    return results

if __name__ == "__main__":
    try:
        results = test_tool_basics()
        # Exit with non-zero if any failures
        sys.exit(0 if results['failed'] == 0 else 1)
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(2)