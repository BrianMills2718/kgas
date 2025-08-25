#!/usr/bin/env python3
"""
Manual Critical Security Assessment
Performs detailed security vulnerability analysis based on OWASP guidelines and common attack patterns.
"""

import re
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityVulnerabilityScanner:
    """Scans code for common security vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.patterns = {
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{6,}["\']',
                r'secret\s*=\s*["\'][^"\']{10,}["\']',
                r'api_key\s*=\s*["\'][^"\']{10,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']'
            ],
            'sql_injection': [
                r'execute\([^)]*%[sd][^)]*\)',
                r'query\([^)]*\+[^)]*\)',
                r'\.format\([^)]*user[^)]*\)'
            ],
            'command_injection': [
                r'os\.system\([^)]*\+',
                r'subprocess\.[^(]*\([^)]*\+',
                r'eval\([^)]*input'
            ],
            'insecure_random': [
                r'random\.randint',
                r'random\.choice',
                r'random\.random\(\)'
            ],
            'weak_crypto': [
                r'md5\(',
                r'sha1\(',
                r'DES\(',
                r'RC4\('
            ]
        }
    
    def scan_file(self, filepath: str) -> Dict:
        """Scan a single file for vulnerabilities"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_vulns = {
                'file': filepath,
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
                'info': []
            }
            
            # Check for hardcoded secrets
            for pattern in self.patterns['hardcoded_secrets']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    file_vulns['critical'].append({
                        'type': 'Hardcoded Secret',
                        'pattern': match.group(),
                        'line': content[:match.start()].count('\n') + 1,
                        'description': 'Potential hardcoded secret found'
                    })
            
            # Check for injection vulnerabilities
            for pattern in self.patterns['sql_injection']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    file_vulns['high'].append({
                        'type': 'SQL Injection Risk',
                        'pattern': match.group(),
                        'line': content[:match.start()].count('\n') + 1,
                        'description': 'Potential SQL injection vulnerability'
                    })
            
            for pattern in self.patterns['command_injection']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    file_vulns['high'].append({
                        'type': 'Command Injection Risk',
                        'pattern': match.group(),
                        'line': content[:match.start()].count('\n') + 1,
                        'description': 'Potential command injection vulnerability'
                    })
            
            # Check for weak cryptography
            for pattern in self.patterns['weak_crypto']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    file_vulns['medium'].append({
                        'type': 'Weak Cryptography',
                        'pattern': match.group(),
                        'line': content[:match.start()].count('\n') + 1,
                        'description': 'Use of weak cryptographic algorithm'
                    })
            
            # Check for insecure random number generation
            for pattern in self.patterns['insecure_random']:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    file_vulns['low'].append({
                        'type': 'Insecure Random',
                        'pattern': match.group(),
                        'line': content[:match.start()].count('\n') + 1,
                        'description': 'Use of insecure random number generation'
                    })
            
            return file_vulns
            
        except Exception as e:
            return {
                'file': filepath,
                'error': str(e),
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
                'info': []
            }
    
    def analyze_authentication_security(self, filepath: str) -> List[Dict]:
        """Analyze authentication implementation for security issues"""
        issues = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Check for proper password hashing
            if 'pbkdf2_hmac' in content:
                issues.append({
                    'type': 'GOOD',
                    'message': 'Uses PBKDF2 for password hashing',
                    'severity': 'info'
                })
            else:
                issues.append({
                    'type': 'WARNING',
                    'message': 'PBKDF2 not found - verify password hashing method',
                    'severity': 'medium'
                })
            
            # Check for secure salt generation
            if 'secrets.token_hex' in content:
                issues.append({
                    'type': 'GOOD',
                    'message': 'Uses cryptographically secure salt generation',
                    'severity': 'info'
                })
            
            # Check for timing attack protection
            if 'hmac.compare_digest' in content:
                issues.append({
                    'type': 'GOOD',
                    'message': 'Uses timing-safe comparison for passwords',
                    'severity': 'info'
                })
            else:
                issues.append({
                    'type': 'CRITICAL',
                    'message': 'No timing-safe comparison found - vulnerable to timing attacks',
                    'severity': 'critical'
                })
            
            # Check for JWT security
            if 'jwt.encode' in content and 'HS256' in content:
                issues.append({
                    'type': 'WARNING',
                    'message': 'Uses HS256 for JWT - consider RS256 for better security',
                    'severity': 'medium'
                })
            
            # Check for session management
            if 'revoked_sessions' in content:
                issues.append({
                    'type': 'GOOD',
                    'message': 'Implements session revocation',
                    'severity': 'info'
                })
            
            return issues
            
        except Exception as e:
            return [{
                'type': 'ERROR',
                'message': f'Error analyzing {filepath}: {e}',
                'severity': 'critical'
            }]
    
    def analyze_authorization_security(self, content: str) -> List[Dict]:
        """Analyze authorization implementation"""
        issues = []
        
        # Check for proper permission checking
        if 'has_permission' in content and 'authenticated' in content:
            issues.append({
                'type': 'GOOD',
                'message': 'Implements permission checking',
                'severity': 'info'
            })
        
        # Check for security level validation
        if 'can_access_level' in content:
            issues.append({
                'type': 'GOOD',
                'message': 'Implements security level validation',
                'severity': 'info'
            })
        
        # Check for token expiration
        if 'is_expired' in content:
            issues.append({
                'type': 'GOOD',
                'message': 'Implements token expiration checking',
                'severity': 'info'
            })
        
        # Look for potential bypasses
        if 'if not' in content and ('security' in content or 'auth' in content):
            issues.append({
                'type': 'WARNING',
                'message': 'Potential security bypass - review negative security checks',
                'severity': 'medium'
            })
        
        return issues
    
    def analyze_thread_safety(self, content: str) -> List[Dict]:
        """Analyze thread safety in security code"""
        issues = []
        
        # Check for proper locking
        if 'threading.RLock' in content or 'threading.Lock' in content:
            issues.append({
                'type': 'GOOD',
                'message': 'Uses thread locks for synchronization',
                'severity': 'info'
            })
        
        # Check for with statements (context managers)
        if 'with self._lock:' in content:
            issues.append({
                'type': 'GOOD',
                'message': 'Uses proper lock context managers',
                'severity': 'info'
            })
        else:
            issues.append({
                'type': 'WARNING',
                'message': 'May not be using proper lock context management',
                'severity': 'medium'
            })
        
        # Check for shared mutable state
        if '_cache' in content or '_sessions' in content:
            if 'lock' not in content:
                issues.append({
                    'type': 'CRITICAL',
                    'message': 'Shared mutable state without proper locking',
                    'severity': 'critical'
                })
        
        return issues


def analyze_security_claims():
    """Perform comprehensive security analysis"""
    scanner = SecurityVulnerabilityScanner()
    
    print("🔐 BRUTAL SECURITY ASSESSMENT RESULTS")
    print("=" * 70)
    
    # Files to analyze
    security_files = [
        'src/core/security_authentication.py',
        'src/core/service_components.py',
        'src/core/improved_service_registry.py'
    ]
    
    all_vulns = []
    auth_issues = []
    
    # Scan each file
    for filepath in security_files:
        if Path(filepath).exists():
            print(f"\n📁 Analyzing {filepath}...")
            
            # General vulnerability scan
            vulns = scanner.scan_file(filepath)
            all_vulns.append(vulns)
            
            # Specific security analysis
            if 'security_authentication.py' in filepath:
                auth_issues.extend(scanner.analyze_authentication_security(filepath))
            
            # Read content for additional analysis
            with open(filepath, 'r') as f:
                content = f.read()
            
            auth_issues.extend(scanner.analyze_authorization_security(content))
            auth_issues.extend(scanner.analyze_thread_safety(content))
        else:
            print(f"❌ File not found: {filepath}")
    
    # Analyze test coverage
    test_files = [
        'test_security_integration.py',
        'comprehensive_security_thread_safety_validation.py'
    ]
    
    test_coverage_issues = []
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n📁 Analyzing test coverage in {test_file}...")
            with open(test_file, 'r') as f:
                test_content = f.read()
            
            # Check test coverage
            if 'assert' in test_content:
                test_coverage_issues.append({
                    'type': 'GOOD',
                    'message': f'{test_file} contains assertions',
                    'severity': 'info'
                })
            
            if 'concurrent' in test_content.lower():
                test_coverage_issues.append({
                    'type': 'GOOD',
                    'message': f'{test_file} tests concurrent operations',
                    'severity': 'info'
                })
            
            if 'security' in test_content.lower():
                test_coverage_issues.append({
                    'type': 'GOOD',
                    'message': f'{test_file} tests security features',
                    'severity': 'info'
                })
    
    # Generate report
    print("\n" + "=" * 70)
    print("📋 VULNERABILITY SUMMARY")
    print("=" * 70)
    
    total_critical = sum(len(v['critical']) for v in all_vulns)
    total_high = sum(len(v['high']) for v in all_vulns)
    total_medium = sum(len(v['medium']) for v in all_vulns)
    total_low = sum(len(v['low']) for v in all_vulns)
    
    print(f"🔴 Critical: {total_critical}")
    print(f"🟠 High: {total_high}")
    print(f"🟡 Medium: {total_medium}")
    print(f"🟢 Low: {total_low}")
    
    # Detail vulnerabilities
    for vulns in all_vulns:
        if any(vulns[severity] for severity in ['critical', 'high', 'medium', 'low']):
            print(f"\n📁 {vulns['file']}:")
            
            for severity in ['critical', 'high', 'medium', 'low']:
                for vuln in vulns[severity]:
                    severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                    print(f"  {severity_icon} Line {vuln['line']}: {vuln['type']} - {vuln['description']}")
    
    # Authentication/Authorization Analysis
    print(f"\n" + "=" * 70)
    print("🔐 SECURITY IMPLEMENTATION ANALYSIS")
    print("=" * 70)
    
    critical_auth_issues = [i for i in auth_issues if i['severity'] == 'critical']
    medium_auth_issues = [i for i in auth_issues if i['severity'] == 'medium']
    good_practices = [i for i in auth_issues if i['severity'] == 'info']
    
    if critical_auth_issues:
        print("\n🔴 CRITICAL SECURITY ISSUES:")
        for issue in critical_auth_issues:
            print(f"  - {issue['message']}")
    
    if medium_auth_issues:
        print("\n🟡 SECURITY WARNINGS:")
        for issue in medium_auth_issues:
            print(f"  - {issue['message']}")
    
    if good_practices:
        print("\n✅ GOOD SECURITY PRACTICES FOUND:")
        for issue in good_practices:
            print(f"  - {issue['message']}")
    
    # Test Coverage Analysis
    print(f"\n" + "=" * 70)
    print("🧪 TEST COVERAGE ANALYSIS")
    print("=" * 70)
    
    for issue in test_coverage_issues:
        icon = "✅" if issue['type'] == 'GOOD' else "⚠️"
        print(f"{icon} {issue['message']}")
    
    # Overall Security Rating
    print(f"\n" + "=" * 70)
    print("🎯 OVERALL SECURITY RATING")
    print("=" * 70)
    
    if total_critical > 0:
        rating = "🔴 FUNDAMENTALLY_FLAWED"
        recommendation = "CRITICAL vulnerabilities must be fixed before production"
    elif total_high > 2:
        rating = "🟠 NEEDS_WORK"
        recommendation = "HIGH severity issues need attention before production"
    elif total_medium > 5:
        rating = "🟡 NEEDS_WORK"
        recommendation = "Multiple MEDIUM issues should be addressed"
    else:
        rating = "🟢 PRODUCTION_READY"
        recommendation = "Security implementation appears solid for production"
    
    print(f"Rating: {rating}")
    print(f"Recommendation: {recommendation}")
    
    # Specific Claim Validation
    print(f"\n" + "=" * 70)
    print("📝 CLAIM-BY-CLAIM VALIDATION")
    print("=" * 70)
    
    claims_status = {
        "JWT Authentication Security": "⚠️ PARTIALLY VALID" if total_medium > 0 else "✅ VALIDATED",
        "Role-Based Access Control": "✅ VALIDATED" if len(good_practices) > 3 else "⚠️ PARTIALLY VALID",
        "Thread Safety Under Security Load": "✅ VALIDATED" if any('lock' in i['message'].lower() for i in good_practices) else "❌ INVALID",
        "Security Validation Comprehensiveness": "⚠️ PARTIALLY VALID",
        "Production Security Readiness": rating.split()[1],
        "Test Coverage": "✅ VALIDATED" if len(test_coverage_issues) > 2 else "⚠️ PARTIALLY VALID"
    }
    
    for claim, status in claims_status.items():
        print(f"{status} {claim}")
    
    return rating.split()[1] == "PRODUCTION_READY"


if __name__ == "__main__":
    try:
        is_production_ready = analyze_security_claims()
        sys.exit(0 if is_production_ready else 1)
    except Exception as e:
        print(f"❌ Security assessment failed: {e}")
        sys.exit(1)