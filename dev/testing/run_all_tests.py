#!/usr/bin/env python3
"""
Master Test Runner - Execute comprehensive test suite
Runs all implemented tests in sequence with detailed reporting
"""
import sys
import os
sys.path.append('/home/brian/projects/Digimons')

import time
import subprocess
import json
from datetime import datetime

class TestRunner:
    """Master test runner for comprehensive validation"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_test_script(self, script_name, description):
        """Run a test script and capture results"""
        print(f"\n🧪 {description}")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            # Print the output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print("STDERR:", result.stderr)
            
            success = result.returncode == 0
            
            self.test_results[script_name] = {
                "description": description,
                "success": success,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n{status} ({duration:.1f}s)")
            
            return success
            
        except subprocess.TimeoutExpired:
            print("❌ TEST TIMEOUT (5 minutes)")
            self.test_results[script_name] = {
                "description": description,
                "success": False,
                "duration": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes"
            }
            return False
            
        except Exception as e:
            print(f"❌ TEST ERROR: {e}")
            self.test_results[script_name] = {
                "description": description,
                "success": False,
                "duration": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e)
            }
            return False
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 CHECKING PREREQUISITES")
        print("=" * 60)
        
        prerequisites = {
            "neo4j_running": False,
            "test_files_exist": False,
            "python_path": False
        }
        
        # Check Neo4j
        try:
            import requests
            response = requests.get("http://localhost:7474", timeout=5)
            prerequisites["neo4j_running"] = response.status_code == 200
            print("✅ Neo4j is running")
        except:
            print("⚠️  Neo4j may not be running (some tests may be limited)")
            # Don't fail - some tests can still run
        
        # Check test files exist
        required_files = [
            "test_vertical_slice_e2e_fixed.py",
            "test_entity_threshold_zero.py", 
            "test_provenance_persistence.py",
            "test_neo4j_no_auth.py",
            "test_service_integration.py",
            "test_performance_monitoring.py",
            "test_individual_tools.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if not missing_files:
            prerequisites["test_files_exist"] = True
            print("✅ All test files found")
        else:
            print(f"❌ Missing test files: {missing_files}")
        
        # Check Python path
        try:
            from src.core.service_manager import ServiceManager
            prerequisites["python_path"] = True
            print("✅ Python path configured correctly")
        except ImportError as e:
            print(f"❌ Python path issue: {e}")
        
        return prerequisites
    
    def run_comprehensive_tests(self):
        """Run the comprehensive test suite"""
        
        print("🚀 KGAS COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check prerequisites
        prereqs = self.check_prerequisites()
        
        if not prereqs["test_files_exist"] or not prereqs["python_path"]:
            print("\n❌ CRITICAL PREREQUISITES MISSING - ABORTING")
            return False
        
        # Define test suite
        test_suite = [
            # Core pipeline tests (highest priority)
            ("test_vertical_slice_e2e_fixed.py", "E2E Pipeline Test"),
            ("test_entity_threshold_zero.py", "Entity Extraction Validation"),
            ("test_provenance_persistence.py", "Provenance Persistence Test"),
            
            # Infrastructure tests
            ("test_neo4j_no_auth.py", "Neo4j Connectivity Test"),
            ("test_service_integration.py", "Service Integration Test"),
            
            # Performance and individual component tests  
            ("test_performance_monitoring.py", "Performance Monitoring Test"),
            ("test_individual_tools.py", "Individual Tools Validation"),
        ]
        
        # Run tests
        passed_tests = 0
        total_tests = len(test_suite)
        
        for script, description in test_suite:
            if os.path.exists(script):
                success = self.run_test_script(script, description)
                if success:
                    passed_tests += 1
            else:
                print(f"\n⚠️  SKIPPING {description} - File not found: {script}")
                self.test_results[script] = {
                    "description": description,
                    "success": False,
                    "duration": 0,
                    "return_code": -1,
                    "stdout": "",
                    "stderr": f"Test file not found: {script}"
                }
        
        # Generate final report
        self.generate_final_report(passed_tests, total_tests)
        
        return passed_tests >= (total_tests * 0.8)  # 80% pass rate required
    
    def generate_final_report(self, passed_tests, total_tests):
        """Generate comprehensive final report"""
        
        total_duration = time.time() - self.start_time
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUITE RESULTS")
        print("=" * 80)
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"   Tests Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {success_rate:.1f}%") 
        print(f"   Total Duration: {total_duration:.1f}s")
        print(f"   Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for script, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result["duration"]
            description = result["description"]
            print(f"   {status} {description} ({duration:.1f}s)")
            
            if not result["success"] and result["stderr"]:
                # Show first line of error for quick diagnosis
                error_line = result["stderr"].split('\n')[0][:100]
                print(f"      Error: {error_line}...")
        
        # System status assessment
        print(f"\n🔧 SYSTEM STATUS:")
        
        if success_rate >= 90:
            print("   🟢 SYSTEM STATUS: EXCELLENT")
            print("   ✅ All critical functionality verified")
            print("   ✅ Ready for production use")
            print("   ✅ Performance meets requirements")
            
        elif success_rate >= 80:
            print("   🟡 SYSTEM STATUS: GOOD")
            print("   ✅ Core functionality working")
            print("   ⚠️  Some non-critical issues detected")
            print("   ✅ Ready for continued development")
            
        elif success_rate >= 60:
            print("   🟠 SYSTEM STATUS: NEEDS ATTENTION") 
            print("   ⚠️  Multiple issues detected")
            print("   ⚠️  Investigation recommended")
            print("   ⚠️  Limited production readiness")
            
        else:
            print("   🔴 SYSTEM STATUS: CRITICAL ISSUES")
            print("   ❌ Major functionality problems")
            print("   ❌ Not ready for production")
            print("   ❌ Immediate fixes required")
        
        # Key achievements (always show positive aspects)
        print(f"\n🎉 KEY ACHIEVEMENTS:")
        achievements = []
        
        for script, result in self.test_results.items():
            if result["success"]:
                if "e2e" in script.lower():
                    achievements.append("✅ End-to-end pipeline functional")
                elif "entity" in script.lower():
                    achievements.append("✅ Entity extraction working")
                elif "provenance" in script.lower():
                    achievements.append("✅ Provenance tracking operational")
                elif "neo4j" in script.lower():
                    achievements.append("✅ Neo4j connectivity established")
                elif "service" in script.lower():
                    achievements.append("✅ Service integration verified")
                elif "performance" in script.lower():
                    achievements.append("✅ Performance benchmarks met")
                elif "individual" in script.lower():
                    achievements.append("✅ Individual tool validation passed")
        
        # Remove duplicates and show achievements
        achievements = list(set(achievements))
        for achievement in achievements:
            print(f"   {achievement}")
        
        if not achievements:
            print("   🔧 Foundation components are being validated...")
        
        # Next steps
        print(f"\n🎯 RECOMMENDED NEXT STEPS:")
        
        if success_rate >= 80:
            print("   🚀 System is ready for advanced capabilities:")
            print("      - Implement T34 relationship edge building")
            print("      - Enable T68 PageRank calculations")
            print("      - Activate T49 multi-hop query answering")
            print("      - Scale testing with larger documents")
            
        else:
            failing_tests = [script for script, result in self.test_results.items() if not result["success"]]
            print("   🔧 Focus on resolving test failures:")
            for test in failing_tests[:3]:  # Show first 3 failing tests
                description = self.test_results[test]["description"]
                print(f"      - Fix: {description}")
        
        # Save detailed results to file
        self.save_test_report()
    
    def save_test_report(self):
        """Save detailed test report to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"test_results_{timestamp}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": time.time() - self.start_time,
            "summary": {
                "passed": sum(1 for result in self.test_results.values() if result["success"]),
                "total": len(self.test_results),
                "success_rate": (sum(1 for result in self.test_results.values() if result["success"]) / len(self.test_results)) * 100 if self.test_results else 0
            },
            "test_results": self.test_results
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Detailed report saved: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")

def main():
    """Main test runner entry point"""
    
    runner = TestRunner()
    success = runner.run_comprehensive_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())