#!/usr/bin/env python3
"""
Detailed Technical Assessment of Service Registration Implementation

Performs deep code analysis and architectural review to validate claims
and identify any issues masked by the initial assessment.
"""

import sys
import re
from pathlib import Path

# Add project root to path
sys.path.append('/home/brian/projects/Digimons')

def analyze_code_quality(file_path):
    """Analyze code quality metrics"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "docstring_lines": len(re.findall(r'""".*?"""', content, re.DOTALL)),
            "function_count": len(re.findall(r'def \w+', content)),
            "class_count": len(re.findall(r'class \w+', content)),
            "async_functions": len(re.findall(r'async def \w+', content)),
            "error_handling": content.count('try:'),
            "exception_catches": content.count('except'),
            "logging_statements": content.count('logger.'),
            "type_hints": content.count(': '),
            "imports": len(re.findall(r'^(from|import)', content, re.MULTILINE))
        }
        
        return metrics
    except Exception as e:
        return {"error": str(e)}

def analyze_dependency_injection_quality():
    """Analyze dependency injection implementation quality"""
    print("🔍 DEPENDENCY INJECTION QUALITY ANALYSIS")
    print("=" * 50)
    
    di_file = "/home/brian/projects/Digimons/src/core/dependency_injection.py"
    registry_file = "/home/brian/projects/Digimons/src/core/service_registry.py"
    
    # Analyze dependency injection code
    di_metrics = analyze_code_quality(di_file)
    registry_metrics = analyze_code_quality(registry_file)
    
    print(f"📊 Dependency Injection Metrics:")
    print(f"  • Total lines: {di_metrics['total_lines']}")
    print(f"  • Functions: {di_metrics['function_count']}")
    print(f"  • Classes: {di_metrics['class_count']}")
    print(f"  • Async functions: {di_metrics['async_functions']}")
    print(f"  • Error handling blocks: {di_metrics['error_handling']}")
    print(f"  • Exception handlers: {di_metrics['exception_catches']}")
    print(f"  • Logging statements: {di_metrics['logging_statements']}")
    print(f"  • Type hints: {di_metrics['type_hints']}")
    
    print(f"\n📊 Service Registry Metrics:")
    print(f"  • Total lines: {registry_metrics['total_lines']}")
    print(f"  • Functions: {registry_metrics['function_count']}")
    print(f"  • Classes: {registry_metrics['class_count']}")
    print(f"  • Async functions: {registry_metrics['async_functions']}")
    print(f"  • Error handling blocks: {registry_metrics['error_handling']}")
    print(f"  • Exception handlers: {registry_metrics['exception_catches']}")
    print(f"  • Logging statements: {registry_metrics['logging_statements']}")
    
    # Quality assessment
    quality_issues = []
    
    if di_metrics['error_handling'] < 3:
        quality_issues.append("Insufficient error handling in dependency injection")
    
    if registry_metrics['logging_statements'] < 5:
        quality_issues.append("Insufficient logging in service registry")
    
    if di_metrics['type_hints'] < 20:
        quality_issues.append("Limited type hints in dependency injection")
    
    quality_score = 10 - len(quality_issues)
    
    print(f"\n📈 Quality Assessment:")
    print(f"  • Quality Score: {quality_score}/10")
    if quality_issues:
        print(f"  • Issues found:")
        for issue in quality_issues:
            print(f"    ⚠️ {issue}")
    else:
        print(f"  • ✅ No major quality issues detected")
    
    return quality_score, quality_issues

def analyze_test_coverage():
    """Analyze test coverage and quality"""
    print("\n🧪 TEST COVERAGE ANALYSIS")
    print("=" * 50)
    
    test_file = "/home/brian/projects/Digimons/test_service_registration.py"
    test_metrics = analyze_code_quality(test_file)
    
    print(f"📊 Test Suite Metrics:")
    print(f"  • Total lines: {test_metrics['total_lines']}")
    print(f"  • Test functions: {test_metrics['function_count']}")
    print(f"  • Async tests: {test_metrics['async_functions']}")
    print(f"  • Error handling: {test_metrics['error_handling']}")
    print(f"  • Assertions: counted in code review")
    
    # Analyze test content
    try:
        with open(test_file, 'r') as f:
            test_content = f.read()
        
        test_analysis = {
            "assertion_count": test_content.count('assert'),
            "test_functions": len(re.findall(r'def test_\w+', test_content)),
            "async_tests": len(re.findall(r'async def test_\w+', test_content)),
            "mock_usage": test_content.count('mock'),
            "integration_tests": test_content.count('integration'),
            "edge_case_tests": test_content.count('edge') + test_content.count('error'),
            "performance_tests": test_content.count('performance') + test_content.count('stress')
        }
        
        print(f"\n📊 Test Analysis:")
        print(f"  • Test functions: {test_analysis['test_functions']}")
        print(f"  • Async tests: {test_analysis['async_tests']}")
        print(f"  • Assertions: {test_analysis['assertion_count']}")
        print(f"  • Mock usage: {test_analysis['mock_usage']}")
        print(f"  • Integration tests: {test_analysis['integration_tests']}")
        print(f"  • Edge case tests: {test_analysis['edge_case_tests']}")
        print(f"  • Performance tests: {test_analysis['performance_tests']}")
        
        # Test quality assessment
        test_issues = []
        
        if test_analysis['assertion_count'] < 20:
            test_issues.append("Low assertion count suggests superficial testing")
        
        if test_analysis['edge_case_tests'] < 3:
            test_issues.append("Insufficient edge case testing")
        
        if test_analysis['performance_tests'] == 0:
            test_issues.append("No performance testing detected")
        
        if test_analysis['mock_usage'] > test_analysis['assertion_count'] / 2:
            test_issues.append("Heavy mock usage may mask real implementation issues")
        
        test_score = 10 - len(test_issues)
        
        print(f"\n📈 Test Quality Assessment:")
        print(f"  • Test Quality Score: {test_score}/10")
        if test_issues:
            print(f"  • Issues found:")
            for issue in test_issues:
                print(f"    ⚠️ {issue}")
        else:
            print(f"  • ✅ Test quality appears adequate")
        
        return test_score, test_issues
        
    except Exception as e:
        print(f"  ❌ Error analyzing tests: {e}")
        return 0, ["Failed to analyze test file"]

def analyze_production_readiness():
    """Analyze production readiness"""
    print("\n🚀 PRODUCTION READINESS ANALYSIS")
    print("=" * 50)
    
    files_to_check = [
        "/home/brian/projects/Digimons/src/core/dependency_injection.py",
        "/home/brian/projects/Digimons/src/core/service_registry.py"
    ]
    
    production_issues = []
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            file_name = Path(file_path).name
            
            # Check for production readiness indicators
            checks = {
                "error_handling": content.count('try:') >= 3,
                "logging": content.count('logger.') >= 5,
                "type_safety": content.count(': ') >= 10,
                "documentation": content.count('"""') >= 5,
                "thread_safety": 'Lock' in content or 'threading' in content,
                "resource_cleanup": 'cleanup' in content.lower() or 'close' in content.lower(),
                "configuration": 'config' in content.lower(),
                "monitoring": 'health' in content.lower() or 'status' in content.lower()
            }
            
            print(f"\n📊 {file_name} Production Readiness:")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check.replace('_', ' ').title()}")
                
                if not passed:
                    production_issues.append(f"{file_name}: {check.replace('_', ' ')}")
        
        except Exception as e:
            production_issues.append(f"Failed to analyze {file_path}: {e}")
    
    production_score = max(0, 10 - len(production_issues))
    
    print(f"\n📈 Production Readiness Score: {production_score}/10")
    if production_issues:
        print(f"Issues found ({len(production_issues)}):")
        for issue in production_issues:
            print(f"  ⚠️ {issue}")
    
    return production_score, production_issues

def analyze_architectural_patterns():
    """Analyze architectural patterns and design quality"""
    print("\n🏗️ ARCHITECTURAL PATTERN ANALYSIS")
    print("=" * 50)
    
    registry_file = "/home/brian/projects/Digimons/src/core/service_registry.py"
    di_file = "/home/brian/projects/Digimons/src/core/dependency_injection.py"
    
    architectural_issues = []
    
    try:
        with open(registry_file, 'r') as f:
            registry_content = f.read()
        
        with open(di_file, 'r') as f:
            di_content = f.read()
        
        # Check architectural patterns
        patterns = {
            "Dependency Injection": "container.get(" in registry_content,
            "Factory Pattern": "factory" in registry_content.lower(),
            "Singleton Pattern": "singleton" in di_content.lower(),
            "Service Locator": "get_service" in registry_content,
            "Observer Pattern": "event" in registry_content.lower() or "notify" in registry_content.lower(),
            "Strategy Pattern": "strategy" in registry_content.lower(),
            "Template Method": "template" in registry_content.lower(),
            "Builder Pattern": "builder" in registry_content.lower()
        }
        
        print("📊 Architectural Patterns Detected:")
        for pattern, detected in patterns.items():
            status = "✅" if detected else "❌"
            print(f"  {status} {pattern}")
        
        # Check for anti-patterns
        anti_patterns = {
            "God Object": registry_content.count('def ') > 20,
            "Tight Coupling": registry_content.count('import') > 15,
            "Magic Numbers": bool(re.search(r'\b\d{2,}\b', registry_content)),
            "Long Parameter Lists": bool(re.search(r'def \w+\([^)]{80,}\)', registry_content)),
            "Deep Nesting": registry_content.count('    ') > 50  # Rough estimate
        }
        
        print(f"\n📊 Anti-Pattern Detection:")
        for anti_pattern, detected in anti_patterns.items():
            status = "⚠️" if detected else "✅"
            print(f"  {status} {anti_pattern}: {'Detected' if detected else 'Not detected'}")
            
            if detected:
                architectural_issues.append(f"Anti-pattern detected: {anti_pattern}")
        
        # Analyze SOLID principles adherence
        solid_analysis = {
            "Single Responsibility": len(re.findall(r'class \w+', registry_content)) >= 2,
            "Open/Closed": "ABC" in registry_content or "Protocol" in registry_content,
            "Liskov Substitution": "isinstance" in registry_content,
            "Interface Segregation": "Protocol" in registry_content or "ABC" in registry_content,
            "Dependency Inversion": "injection" in registry_content.lower()
        }
        
        print(f"\n📊 SOLID Principles Analysis:")
        for principle, follows in solid_analysis.items():
            status = "✅" if follows else "⚠️"
            print(f"  {status} {principle}")
            
            if not follows:
                architectural_issues.append(f"SOLID principle concern: {principle}")
        
        arch_score = max(0, 10 - len(architectural_issues))
        
        print(f"\n📈 Architectural Quality Score: {arch_score}/10")
        if architectural_issues:
            print(f"Issues found ({len(architectural_issues)}):")
            for issue in architectural_issues:
                print(f"  ⚠️ {issue}")
        
        return arch_score, architectural_issues
        
    except Exception as e:
        print(f"❌ Error analyzing architecture: {e}")
        return 0, ["Failed to analyze architectural patterns"]

def perform_comprehensive_assessment():
    """Perform comprehensive technical assessment"""
    print("🔥 COMPREHENSIVE TECHNICAL ASSESSMENT")
    print("=" * 60)
    
    # Run all analyses
    quality_score, quality_issues = analyze_dependency_injection_quality()
    test_score, test_issues = analyze_test_coverage()
    production_score, production_issues = analyze_production_readiness()
    arch_score, arch_issues = analyze_architectural_patterns()
    
    # Calculate overall score
    overall_score = (quality_score + test_score + production_score + arch_score) / 4
    
    # Summarize findings
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE ASSESSMENT SUMMARY")
    print("=" * 60)
    
    print(f"\n📊 DETAILED SCORES:")
    print(f"  • Code Quality: {quality_score}/10")
    print(f"  • Test Coverage: {test_score}/10") 
    print(f"  • Production Readiness: {production_score}/10")
    print(f"  • Architectural Quality: {arch_score}/10")
    print(f"  • OVERALL SCORE: {overall_score:.1f}/10")
    
    # Determine assessment level
    if overall_score >= 8.5:
        assessment = "EXCELLENT - Production Ready"
        recommendation = "APPROVE for immediate deployment"
    elif overall_score >= 7.0:
        assessment = "GOOD - Minor improvements needed"
        recommendation = "APPROVE with minor hardening"
    elif overall_score >= 5.5:
        assessment = "ADEQUATE - Some concerns exist"
        recommendation = "CONDITIONAL APPROVE - address concerns"
    else:
        assessment = "NEEDS WORK - Significant issues"
        recommendation = "REJECT - major improvements required"
    
    print(f"\n🎯 FINAL ASSESSMENT: {assessment}")
    print(f"📋 RECOMMENDATION: {recommendation}")
    
    # List all issues
    all_issues = quality_issues + test_issues + production_issues + arch_issues
    if all_issues:
        print(f"\n⚠️ ISSUES TO ADDRESS ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\n✅ NO SIGNIFICANT ISSUES IDENTIFIED")
    
    return {
        "overall_score": overall_score,
        "assessment": assessment,
        "recommendation": recommendation,
        "scores": {
            "quality": quality_score,
            "testing": test_score,
            "production": production_score,
            "architecture": arch_score
        },
        "issues": all_issues
    }

def main():
    """Run comprehensive assessment"""
    try:
        results = perform_comprehensive_assessment()
        return results["overall_score"] >= 6.0
    except Exception as e:
        print(f"\n❌ Assessment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)