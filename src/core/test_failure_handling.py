#!/usr/bin/env python3
"""Test that failures are loud, not silent"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

def test_entity_tracking_failure_strict_mode():
    """Verify entity tracking failures cause tool failure in strict mode"""
    from src.core.adapter_factory import UniversalAdapter
    from framework import ToolResult
    
    # Create mock tool that returns entities - BUT not an ExtensibleTool
    mock_tool = MagicMock()
    mock_tool.tool_id = 'TestTool'
    # Remove get_capabilities so it's not treated as ExtensibleTool
    del mock_tool.get_capabilities
    # Set execute as the main method (UniversalAdapter will detect this)
    mock_tool.execute = MagicMock(return_value={
        'entities': [{'text': 'Test Entity', 'type': 'TEST'}]
    })
    
    # Create service bridge that fails
    mock_bridge = MagicMock()
    mock_bridge.track_execution.return_value = {'operation_id': 'test'}
    mock_bridge.track_entity.side_effect = Exception('Database connection lost!')
    
    # Test strict mode (default)
    adapter = UniversalAdapter(mock_tool, mock_bridge, strict_mode=True)
    result = adapter.process('test input', context=None)
    
    print(f"Result success: {result.success}")
    print(f"Result error: {result.error}")
    print(f"Result uncertainty: {result.uncertainty}")
    print(f"Service bridge track_entity called: {mock_bridge.track_entity.called}")
    
    assert result.success == False, f"Should fail in strict mode, got: success={result.success}, error={result.error}"
    assert 'Entity tracking failed' in result.error
    assert result.uncertainty == 1.0
    print("✅ Strict mode: Failures are loud")
    
    # Test lenient mode
    adapter_lenient = UniversalAdapter(mock_tool, mock_bridge, strict_mode=False)
    result_lenient = adapter_lenient.process('test input')
    
    assert result_lenient.success == True, "Should continue in lenient mode"
    assert 'WARNING' in result_lenient.reasoning
    assert result_lenient.uncertainty > 0.1
    print("✅ Lenient mode: Warnings added but continues")

if __name__ == "__main__":
    test_entity_tracking_failure_strict_mode()
    print("\n🎉 Failure handling tests passed!")