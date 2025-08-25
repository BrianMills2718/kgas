#!/usr/bin/env python3
"""Test that ToolRequest has all required attributes"""

import sys
import json
from datetime import datetime

sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.tool_contract import ToolRequest

def test_toolrequest_has_all_attributes():
    request = ToolRequest(input_data={"test": "data"})
    
    # These MUST all pass after fix
    assert hasattr(request, 'operation')
    assert hasattr(request, 'parameters') 
    assert hasattr(request, 'validation_mode')
    assert request.operation == "execute"
    assert request.parameters == {}
    assert request.validation_mode == False
    
    # Generate evidence
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "toolrequest_attributes",
        "status": "success",
        "assertions": [
            {"test": "has_operation", "passed": True, "actual": "execute", "expected": "execute"},
            {"test": "has_parameters", "passed": True, "actual": {}, "expected": {}},
            {"test": "has_validation_mode", "passed": True, "actual": False, "expected": False}
        ]
    }
    
    import os
    os.makedirs('evidence', exist_ok=True)
    
    with open('evidence/toolrequest_fix.json', 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print("✅ ToolRequest fix verified")

if __name__ == "__main__":
    test_toolrequest_has_all_attributes()