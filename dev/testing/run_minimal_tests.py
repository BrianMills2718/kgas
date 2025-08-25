#!/usr/bin/env python3
"""
Minimal Viable Test Suite Runner
Focus on essential production functionality only
"""
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, description):
    """Run a command and track timing"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED ({elapsed:.1f}s)")
            # Show test summary
            lines = result.stdout.strip().split('\n')
            summary_line = [line for line in lines if 'passed' in line and ('failed' in line or 'error' in line or 'passed in' in line)]
            if summary_line:
                print(f"Result: {summary_line[-1]}")
            return True
        else:
            print(f"❌ {description} - FAILED ({elapsed:.1f}s)")
            # Show error summary
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                summary_line = [line for line in lines if ('failed' in line or 'error' in line or 'FAILED' in line)]
                if summary_line:
                    print(f"Error summary: {summary_line[-1]}")
            if result.stderr:
                print(f"Error details: {result.stderr.strip()[:200]}...")
            return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def run_core_tests():
    """Run core system tests (essential functionality)"""
    return run_command(
        ["python", "-m", "pytest", "tests/unit/core/", "-v", "--tb=short"],
        "Core System Tests (Essential)"
    )

def run_critical_tools():
    """Run critical tool tests (core functionality)"""
    return run_command(
        ["python", "-m", "pytest", 
         "tests/unit/test_t01_pdf_loader_unified.py",
         "tests/unit/test_t15a_text_chunker_unified.py", 
         "tests/unit/test_t23a_spacy_ner_unified.py",
         "-v", "--tb=short"],
        "Critical Tool Tests (PDF, Chunker, NER)"
    )

def run_security_tests():
    """Run security tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/security/", "-v", "--tb=short"],
        "Security Tests (Production Safety)"
    )

def run_minimal_collection_test():
    """Test that minimal suite collects properly"""
    return run_command(
        ["python", "-m", "pytest", 
         "tests/unit/core/", 
         "tests/security/",
         "--collect-only", "-q"],
        "Minimal Suite Collection Test"
    )

def main():
    """Run minimal viable test suite"""
    print("🚀 Running Minimal Viable Test Suite")
    print("Focus: Essential production functionality only\n")
    
    # Start with collection test
    success = run_minimal_collection_test()
    if not success:
        print("\n💥 Test collection failed - cannot run tests")
        sys.exit(1)
    
    results = []
    
    # Core tests
    results.append(("Core System", run_core_tests()))
    
    # Critical tools
    results.append(("Critical Tools", run_critical_tools()))
    
    # Security
    results.append(("Security", run_security_tests()))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 MINIMAL TEST SUITE RESULTS")
    print(f"{'='*50}")
    
    passed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} test categories passed")
    
    if passed == len(results):
        print("\n🎉 Minimal viable test suite PASSED!")
        print("✅ Core functionality is working")
        sys.exit(0)
    else:
        print(f"\n⚠️  {len(results)-passed} test categories failed")
        print("🔧 Focus on fixing these essential areas first")
        sys.exit(1)

if __name__ == "__main__":
    main()