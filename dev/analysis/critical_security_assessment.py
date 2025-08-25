#!/usr/bin/env python3
"""
Critical Security Assessment using Gemini
Performs a brutal, no-mercy assessment of security implementation claims.
"""

import os
import sys
import google.generativeai as genai
from pathlib import Path

def read_file_content(filepath):
    """Read file content safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

def main():
    # Configure Gemini
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("Please export GEMINI_API_KEY=your_api_key")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Read security implementation files
    security_files = [
        'src/core/security_authentication.py',
        'src/core/service_components.py', 
        'src/core/improved_service_registry.py',
        'test_security_integration.py',
        'comprehensive_security_thread_safety_validation.py'
    ]
    
    codebase = ""
    for file_path in security_files:
        if Path(file_path).exists():
            content = read_file_content(file_path)
            codebase += f"\n\n=== FILE: {file_path} ===\n{content}\n"
        else:
            codebase += f"\n\n=== FILE: {file_path} ===\nFILE NOT FOUND\n"
    
    # Create brutal security assessment prompt
    prompt = f"""
CRITICAL SECURITY IMPLEMENTATION ASSESSMENT

You are a senior security auditor tasked with performing a BRUTAL, no-mercy critical assessment of security implementation claims. Be skeptical, thorough, and unforgiving in your analysis.

CODEBASE TO ANALYZE:
{codebase}

CLAIMS TO VALIDATE WITH EXTREME SCRUTINY:

1. **JWT Authentication Security**
   - CLAIM: "JWT-based authentication with PBKDF2 password hashing"
   - VALIDATE: Are passwords actually hashed with PBKDF2? Is salt handling secure? Are there timing attack vulnerabilities?
   - VALIDATE: JWT implementation - is it using secure algorithms? Are tokens properly validated? Can they be forged?
   - VALIDATE: Session management - can sessions be hijacked? Are revoked tokens properly handled?

2. **Role-Based Access Control**
   - CLAIM: "Role-based permissions with security levels"
   - VALIDATE: Is RBAC actually enforced at every access point? Can permissions be bypassed?
   - VALIDATE: Are security levels consistently applied? Can low-privilege users escalate privileges?
   - VALIDATE: Are there any backdoors or admin-only bypasses that could be exploited?

3. **Thread Safety Under Security Load**
   - CLAIM: "Thread-safe security validation and audit logging"
   - VALIDATE: Are there race conditions in security checks? Can concurrent access bypass security?
   - VALIDATE: Is audit logging actually thread-safe or could logs be corrupted/lost?
   - VALIDATE: Can high concurrency cause security validation to fail open rather than fail closed?

4. **Security Validation Comprehensiveness**
   - CLAIM: "Service class validation for malicious code patterns"
   - VALIDATE: What specific patterns are detected? Are there obvious bypass methods?
   - VALIDATE: Is input validation comprehensive or are there injection possibilities?
   - VALIDATE: Are there any unvalidated code paths that could be exploited?

5. **Production Security Readiness**
   - CLAIM: "Production-ready with enterprise-grade security"
   - VALIDATE: Are there hardcoded secrets, weak encryption, or other security anti-patterns?
   - VALIDATE: Is error handling secure (no information leakage)?
   - VALIDATE: Are all attack vectors (CSRF, XSS, injection, etc.) properly mitigated?

6. **Test Coverage Reality Check**
   - CLAIM: "Comprehensive test coverage with real-world scenarios"
   - VALIDATE: Do tests actually cover security edge cases and attack scenarios?
   - VALIDATE: Are tests realistic or do they use oversimplified mocks?
   - VALIDATE: Are there untested security-critical code paths?

SECURITY VULNERABILITIES TO LOOK FOR:
- Hardcoded secrets or weak secret generation
- Timing attacks in authentication
- Session fixation vulnerabilities
- Token forgery possibilities
- Race conditions in security checks
- Information disclosure in error messages
- SQL injection, code injection, command injection
- Cross-site scripting (XSS) vectors
- Cross-site request forgery (CSRF) vulnerabilities
- Insecure direct object references
- Broken authentication and session management
- Security misconfiguration
- Insufficient logging and monitoring
- Using components with known vulnerabilities

ASSESSMENT CRITERIA:
- Give NO BENEFIT OF THE DOUBT
- Point out EVERY potential security flaw, no matter how minor
- Identify gaps between claims and actual implementation
- Look for common security anti-patterns and vulnerabilities
- Assess whether this would pass a professional security audit
- Rate overall security maturity as: PRODUCTION_READY, NEEDS_WORK, or FUNDAMENTALLY_FLAWED

REQUIRED OUTPUT FORMAT:

## BRUTAL SECURITY ASSESSMENT RESULTS

### OVERALL SECURITY RATING: [PRODUCTION_READY / NEEDS_WORK / FUNDAMENTALLY_FLAWED]

### CLAIM-BY-CLAIM ANALYSIS:

**CLAIM 1: JWT Authentication Security**
- Status: [✅ VALIDATED / ⚠️ PARTIALLY VALID / ❌ INVALID]
- Issues Found: [List specific vulnerabilities]
- Evidence: [Code snippets and line numbers]

**CLAIM 2: Role-Based Access Control**
- Status: [✅ VALIDATED / ⚠️ PARTIALLY VALID / ❌ INVALID]
- Issues Found: [List specific vulnerabilities]
- Evidence: [Code snippets and line numbers]

[Continue for all claims...]

### CRITICAL SECURITY VULNERABILITIES FOUND:
1. [Vulnerability 1 with severity and impact]
2. [Vulnerability 2 with severity and impact]
...

### RECOMMENDATIONS FOR PRODUCTION READINESS:
1. [Required fix 1]
2. [Required fix 2]
...

### CONCLUSION:
[Ruthless assessment of whether this system is actually production-ready from a security perspective]

Be absolutely ruthless in finding flaws. Point out every potential attack vector.
"""
    
    try:
        print("🔐 RUNNING CRITICAL SECURITY ASSESSMENT...")
        print("=" * 70)
        print("Using Gemini to perform brutal security code review...")
        print()
        
        response = model.generate_content(prompt)
        print(response.text)
        
        print("\n" + "=" * 70)
        print("🎯 CRITICAL SECURITY ASSESSMENT COMPLETE")
        
    except Exception as e:
        print(f"❌ Error during security assessment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()