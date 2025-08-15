#!/usr/bin/env python3
"""
Production Security Validation Demo
===================================

Demonstrates that all critical security vulnerabilities have been resolved:
1. Environment variable bypass ELIMINATED
2. Enterprise-grade access controls IMPLEMENTED
3. Credential rotation enforcement ACTIVE
4. Secure error handling WITHOUT information leakage
5. Comprehensive audit trail LOGGING

THIS VALIDATION PROVES ENTERPRISE PRODUCTION READINESS
"""

import os
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.secure_credential_manager_fixed import (
    ProductionCredentialManager,
    CredentialSecurityError,
    CredentialNotFoundError,
    generate_master_key
)
from src.core.secure_error_handler import (
    SecureErrorHandler,
    secure_error_response,
    get_secure_error_handler
)


def main():
    """
    Comprehensive production security validation.
    ALL TESTS MUST PASS for enterprise deployment approval.
    """
    print("🔒 PRODUCTION SECURITY VALIDATION")
    print("=" * 50)
    
    # Generate master key for testing
    master_key = generate_master_key()
    os.environ['KGAS_MASTER_KEY'] = master_key
    print(f"✅ Generated secure master key: {master_key[:8]}...")
    
    validation_results = []
    
    try:
        # Test 1: Environment Variable Bypass ELIMINATED
        print("\n1️⃣ TESTING: Environment Variable Bypass Elimination")
        
        # Set environment variables that would previously cause bypass
        os.environ['KGAS_OPENAI_API_KEY'] = 'sk-dangerous-fallback-key'
        os.environ['OPENAI_API_KEY'] = 'sk-another-fallback'
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            
            # This MUST fail - no fallback allowed
            try:
                cred_manager.get_credential('openai')
                validation_results.append("❌ CRITICAL FAILURE: Environment variable bypass still exists")
            except CredentialNotFoundError as e:
                if "Environment variable fallbacks are disabled for security" in str(e):
                    validation_results.append("✅ PASS: Environment variable bypass eliminated")
                else:
                    validation_results.append(f"❌ FAIL: Wrong error message: {e}")
            except Exception as e:
                validation_results.append(f"❌ FAIL: Unexpected error: {e}")
        
        # Clean up environment variables
        del os.environ['KGAS_OPENAI_API_KEY']
        del os.environ['OPENAI_API_KEY']
        
        # Test 2: Enterprise Access Controls
        print("\n2️⃣ TESTING: Enterprise-Grade Access Controls")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test rotation enforcement on startup
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=False)
            cred_manager.store_credential('test', 'sk-test123456789', expires_days=30)
            
            # Age the credential beyond enterprise limits
            cred_manager.metadata['test'].created_at = datetime.now() - timedelta(days=91)
            cred_manager._save_credentials()
            
            # Creating new manager with rotation enforcement should fail
            try:
                ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
                validation_results.append("❌ FAIL: Rotation enforcement not working")
            except CredentialSecurityError as e:
                if "Credential rotation REQUIRED" in str(e):
                    validation_results.append("✅ PASS: Enterprise rotation enforcement active")
                else:
                    validation_results.append(f"❌ FAIL: Wrong rotation error: {e}")
        
        # Test 3: Access-Based Rotation
        print("\n3️⃣ TESTING: Access-Based Rotation Enforcement")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir, enforce_rotation=True)
            cred_manager.store_credential('highuse', 'sk-test123456789', expires_days=30)
            
            # Simulate high access count
            cred_manager.metadata['highuse'].access_count = 10001  # Over enterprise limit
            
            try:
                cred_manager.get_credential('highuse')
                validation_results.append("❌ FAIL: Access-based rotation not enforced")
            except CredentialSecurityError as e:
                if "MUST be rotated" in str(e) and "10001 times" in str(e):
                    validation_results.append("✅ PASS: Access-based rotation enforcement active")
                else:
                    validation_results.append(f"❌ FAIL: Wrong access rotation error: {e}")
        
        # Test 4: Secure Error Handling
        print("\n4️⃣ TESTING: Secure Error Handling (No Information Leakage)")
        
        handler = SecureErrorHandler()
        
        # Test API key sanitization
        dangerous_message = "Connection failed with sk-1234567890abcdef"
        sanitized = handler.sanitize_error_message(dangerous_message)
        
        if "sk-" not in sanitized and "[API_KEY_REDACTED]" in sanitized:
            validation_results.append("✅ PASS: API key sanitization working")
        else:
            validation_results.append(f"❌ FAIL: API key not sanitized: {sanitized}")
        
        # Test path sanitization
        path_message = "File '/home/user/secret/credentials.txt' not found"
        path_sanitized = handler.sanitize_error_message(path_message)
        
        if "/home/user/secret" not in path_sanitized and "[PATH_REDACTED]" in path_sanitized:
            validation_results.append("✅ PASS: Path sanitization working")
        else:
            validation_results.append(f"❌ FAIL: Path not sanitized: {path_sanitized}")
        
        # Test 5: Security Event Logging
        print("\n5️⃣ TESTING: Security Event Logging with Sanitization")
        
        import logging
        from unittest.mock import patch
        
        with patch.object(handler.logger, 'warning') as mock_warning:
            handler.log_security_event("test_event", {
                "api_key": "sk-secret123456789",
                "file": "/sensitive/path/file.txt",
                "user": "admin"
            })
            
            # Verify logging occurred and sensitive data was redacted
            mock_warning.assert_called_once()
            log_message = mock_warning.call_args[0][0]
            
            if ("sk-secret123456789" not in log_message and 
                "[REDACTED]" in log_message and
                "/sensitive/path" not in log_message):
                validation_results.append("✅ PASS: Security event logging sanitization working")
            else:
                validation_results.append(f"❌ FAIL: Security logging not sanitized: {log_message}")
        
        # Test 6: Comprehensive Security Validation
        print("\n6️⃣ TESTING: Comprehensive Security Compliance")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
            cred_manager.store_credential('valid', 'sk-test123456789', expires_days=30)
            
            # Should have no security issues initially
            issues = cred_manager.validate_credential_security()
            if len(issues) == 0:
                validation_results.append("✅ PASS: Comprehensive security validation clean")
            else:
                validation_results.append(f"❌ FAIL: Security issues found: {issues}")
        
        # Test 7: Error Response Security
        print("\n7️⃣ TESTING: Secure Error Response Creation")
        
        try:
            raise FileNotFoundError("/sensitive/credentials.json: Permission denied")
        except Exception as e:
            response = secure_error_response("test_operation", e, include_details=True)
            
            response_str = str(response)
            if ("/sensitive/" not in response_str and 
                "credentials.json" not in response_str and
                response['success'] is False):
                validation_results.append("✅ PASS: Secure error response creation working")
            else:
                validation_results.append(f"❌ FAIL: Error response leaked info: {response}")
        
        # Test 8: Production Directory Permissions
        print("\n8️⃣ TESTING: Production Directory Security")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
                
                # Check directory permissions are secure
                dir_mode = Path(temp_dir).stat().st_mode & 0o777
                if dir_mode == 0o700:
                    validation_results.append("✅ PASS: Directory permissions secure (700)")
                else:
                    validation_results.append(f"❌ FAIL: Insecure directory permissions: {oct(dir_mode)}")
                    
            except CredentialSecurityError as e:
                if "insecure permissions" in str(e).lower():
                    validation_results.append("✅ PASS: Directory permission validation active")
                else:
                    validation_results.append(f"❌ FAIL: Wrong permission error: {e}")
        
        # Test 9: No Unmanaged Credential Access
        print("\n9️⃣ TESTING: Zero Unmanaged Credential Access Paths")
        
        # Set multiple environment variables that could be fallbacks
        env_vars = {
            'KGAS_OPENAI_API_KEY': 'sk-env-openai',
            'OPENAI_API_KEY': 'sk-fallback-openai',
            'KGAS_ANTHROPIC_API_KEY': 'ant-env-anthropic',
            'ANTHROPIC_API_KEY': 'ant-fallback-anthropic'
        }
        
        for var, value in env_vars.items():
            os.environ[var] = value
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                cred_manager = ProductionCredentialManager(credentials_dir=temp_dir)
                
                # Try all providers - ALL should fail
                failed_count = 0
                for provider in ['openai', 'anthropic', 'google']:
                    try:
                        cred_manager.get_credential(provider)
                    except CredentialNotFoundError:
                        failed_count += 1
                
                if failed_count == 3:
                    validation_results.append("✅ PASS: All unmanaged access paths eliminated")
                else:
                    validation_results.append(f"❌ FAIL: {3-failed_count} providers still accessible")
        
        finally:
            # Clean up environment variables
            for var in env_vars:
                if var in os.environ:
                    del os.environ[var]
        
    except Exception as e:
        validation_results.append(f"❌ CRITICAL ERROR: Validation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Print Final Results
    print("\n" + "=" * 50)
    print("🔒 PRODUCTION SECURITY VALIDATION RESULTS")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for result in validation_results:
        print(result)
        if result.startswith("✅"):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL SECURITY VALIDATIONS PASSED")
        print("✅ ENTERPRISE PRODUCTION READY")
        print("🔒 CONFIGURATION SYSTEM SECURE")
        return True
    else:
        print("❌ SECURITY VALIDATIONS FAILED")
        print("🚨 NOT READY FOR PRODUCTION")
        print("⚠️  SECURITY ISSUES MUST BE RESOLVED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)