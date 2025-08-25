#!/usr/bin/env python3
"""Complete test that validates identity service requirements with proper reset"""

import sys
import os
import json
from datetime import datetime
import subprocess

sys.path.insert(0, '/home/brian/projects/Digimons')

def test_identity_fails_without_neo4j():
    """Test that identity service fails without Neo4j - in subprocess to avoid singleton"""
    test_script = """
import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Remove Neo4j config
os.environ.pop('NEO4J_URI', None)
os.environ.pop('NEO4J_USER', None)
os.environ.pop('NEO4J_PASSWORD', None)

from src.core.service_manager import ServiceManager
sm = ServiceManager()

try:
    identity = sm.get_identity_service()
    print("FAIL: Should have raised exception without Neo4j")
    exit(1)
except RuntimeError as e:
    if "Neo4j" in str(e):
        print("PASS: Correctly fails without Neo4j")
        exit(0)
    else:
        print(f"FAIL: Wrong error: {e}")
        exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    exit(1)
"""
    
    result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True)
    passed = result.returncode == 0
    
    if passed:
        print("✅ Test 1: Identity service correctly fails without Neo4j")
    else:
        print(f"❌ Test 1 failed: {result.stdout} {result.stderr}")
    
    return passed

def test_identity_works_with_neo4j():
    """Test that identity service works with Neo4j - in subprocess to avoid singleton"""
    test_script = """
import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Set Neo4j config
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'devpassword'

from src.core.service_manager import ServiceManager
sm = ServiceManager()

try:
    # Should work with Neo4j
    identity = sm.get_identity_service()
    if identity is None:
        print("FAIL: Got None identity service")
        exit(1)
    
    # MUST implement required methods
    mention = identity.create_mention(
        surface_form="Test Entity",
        start_pos=0,
        end_pos=11,
        source_ref="test_doc",
        entity_type="TEST",
        confidence=0.95
    )
    
    # Handle wrapped response format
    if not isinstance(mention, dict):
        print(f"FAIL: Expected dict, got {type(mention)}")
        exit(1)
    
    if 'success' in mention and 'data' in mention:
        # Wrapped format
        if not mention['success']:
            print(f"FAIL: Mention creation failed: {mention}")
            exit(1)
        mention_data = mention['data']
        if 'mention_id' not in mention_data:
            print(f"FAIL: No mention_id in data: {mention_data}")
            exit(1)
        print(f"PASS: Created mention with ID: {mention_data['mention_id']}")
    else:
        # Direct dict format
        if 'mention_id' not in mention:
            print(f"FAIL: No mention_id in response: {mention}")
            exit(1)
        print(f"PASS: Created mention with ID: {mention['mention_id']}")
    
    exit(0)
    
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
"""
    
    result = subprocess.run([sys.executable, "-c", test_script], capture_output=True, text=True)
    passed = result.returncode == 0
    
    if passed:
        print(f"✅ Test 2: Identity service works with Neo4j")
        print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ Test 2 failed:")
        print(f"   stdout: {result.stdout}")
        print(f"   stderr: {result.stderr}")
    
    return passed

def main():
    """Run all tests and generate evidence"""
    print("=" * 60)
    print("Testing Identity Service Requirements")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "test_name": "identity_service_requirements_complete",
        "tests": []
    }
    
    # Test 1: Fails without Neo4j
    test1_passed = test_identity_fails_without_neo4j()
    results["tests"].append({
        "name": "fails_without_neo4j",
        "passed": test1_passed,
        "description": "Identity service should fail-fast without Neo4j (NO LAZY IMPLEMENTATIONS)"
    })
    
    # Test 2: Works with Neo4j
    test2_passed = test_identity_works_with_neo4j()
    results["tests"].append({
        "name": "works_with_neo4j",
        "passed": test2_passed,
        "description": "Identity service should work with Neo4j"
    })
    
    # Overall result
    results["status"] = "success" if all(t["passed"] for t in results["tests"]) else "failure"
    
    # Save evidence
    os.makedirs('evidence', exist_ok=True)
    evidence_file = 'evidence/identity_requirements_complete.json'
    with open(evidence_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    if results["status"] == "success":
        print("✅ ALL IDENTITY SERVICE TESTS PASSED")
        print(f"✅ Evidence saved to: {evidence_file}")
        print("\nTASK 2 COMPLETE: Identity Service Requirements Fixed")
        print("- Identity service fails fast without Neo4j (NO FALLBACKS)")
        print("- Identity service works correctly with Neo4j")
        print("- Wrapped response format handled properly")
    else:
        print("❌ SOME IDENTITY SERVICE TESTS FAILED")
        print(f"Evidence saved to: {evidence_file}")
    print("=" * 60)
    
    return results["status"] == "success"

if __name__ == "__main__":
    exit(0 if main() else 1)