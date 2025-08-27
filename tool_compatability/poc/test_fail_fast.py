#!/usr/bin/env python3
"""Test that fail-fast behavior works correctly"""

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from adapters.universal_adapter import UniversalAdapter

print("=== Testing Fail-Fast Behavior ===\n")

# Create a tool that will fail
class FailingTool:
    def process(self, data):
        raise ValueError("This tool always fails to test fail-fast")

# Create adapter
tool = FailingTool()
adapter = UniversalAdapter(tool, "failing_tool")

print("Attempting to process with failing tool...")
print("This should raise an exception immediately:\n")

try:
    result = adapter.process("test data")
    print("❌ ERROR: Should have failed but got result:", result)
except RuntimeError as e:
    print("✅ CORRECT: Tool failed fast with RuntimeError")
    print(f"   Error message: {e}")
except Exception as e:
    print(f"⚠️  Unexpected exception type: {type(e).__name__}")
    print(f"   Message: {e}")

print("\n=== Fail-Fast Test Complete ===")