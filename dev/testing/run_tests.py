#!/usr/bin/env python3
"""
Targeted Test Execution Script for Organized Test Suite
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
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED ({elapsed:.1f}s)")
            print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def run_fast_tests():
    """Run fast unit tests for immediate feedback"""
    return run_command(
        ["python", "-m", "pytest", "tests/unit/", "-x", "-v", "--tb=short"],
        "Fast Unit Tests (69 files)"
    )

def run_validation_tests():
    """Run critical validation tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/validation/", "-v"],
        "Validation Tests (10 files)"
    )

def run_integration_tests():
    """Run integration tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/integration/", "-v"],
        "Integration Tests (42 files)"
    )

def run_functional_tests():
    """Run functional tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/functional/", "-v"],
        "Functional Tests (38 files)"
    )

def run_performance_tests():
    """Run performance tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/performance/", "-v", "--durations=10"],
        "Performance Tests (10 files)"
    )

def run_security_tests():
    """Run security tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/security/", "-v"],
        "Security Tests (5 files)"
    )

def run_error_scenario_tests():
    """Run error scenario tests"""
    return run_command(
        ["python", "-m", "pytest", "tests/error_scenarios/", "-v"],
        "Error Scenario Tests (8 files)"
    )

def run_full_organized_suite():
    """Run full organized test suite (excluding archived)"""
    return run_command(
        ["python", "-m", "pytest", "tests/", "-v", "--ignore=tests/archived_experimental/"],
        "Full Organized Test Suite (236 files)"
    )

def main():
    """Main test execution"""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [fast|validation|integration|functional|performance|security|errors|full]")
        print("\nAvailable test suites:")
        print("  fast        - Unit tests (69 files, ~5 min)")
        print("  validation  - Validation tests (10 files, ~2 min)")
        print("  integration - Integration tests (42 files, ~10 min)")
        print("  functional  - Functional tests (38 files, ~8 min)")
        print("  performance - Performance tests (10 files, ~5 min)")
        print("  security    - Security tests (5 files, ~2 min)")
        print("  errors      - Error scenario tests (8 files, ~3 min)")
        print("  full        - All organized tests (236 files, ~30 min)")
        sys.exit(1)

    suite = sys.argv[1].lower()
    
    suite_map = {
        'fast': run_fast_tests,
        'validation': run_validation_tests,
        'integration': run_integration_tests,
        'functional': run_functional_tests,
        'performance': run_performance_tests,
        'security': run_security_tests,
        'errors': run_error_scenario_tests,
        'full': run_full_organized_suite
    }
    
    if suite not in suite_map:
        print(f"Unknown test suite: {suite}")
        sys.exit(1)
    
    print(f"🚀 Running {suite} test suite...")
    success = suite_map[suite]()
    
    if success:
        print(f"\n🎉 {suite.title()} tests completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 {suite.title()} tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()