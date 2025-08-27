#!/usr/bin/env python3
"""Test PII service validation"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_pii_validation():
    """Test that PII service validates inputs properly"""
    from src.core.pii_service import PiiService
    
    # Create service
    pii = PiiService("test_password", b"test_salt_12345")
    
    # Test empty string encryption
    try:
        pii.encrypt("")
        assert False, "Should have raised ValueError for empty string"
    except ValueError as e:
        assert "cannot be empty" in str(e)
        print("✅ Empty string rejected for encrypt")
    
    # Test wrong type
    try:
        pii.encrypt(123)
        assert False, "Should have raised TypeError for non-string"
    except TypeError as e:
        assert "must be str" in str(e)
        print("✅ Non-string rejected for encrypt")
    
    # Test valid encryption
    result = pii.encrypt("valid data")
    assert "pii_id" in result
    assert "ciphertext_b64" in result
    assert "nonce_b64" in result
    print("✅ Valid encryption works")
    
    # Test decrypt with empty strings
    try:
        pii.decrypt("", "valid_nonce")
        assert False, "Should have raised ValueError for empty ciphertext"
    except ValueError as e:
        assert "must be non-empty" in str(e)
        print("✅ Empty ciphertext rejected")
    
    try:
        pii.decrypt("valid_cipher", "")
        assert False, "Should have raised ValueError for empty nonce"
    except ValueError as e:
        assert "must be non-empty" in str(e)
        print("✅ Empty nonce rejected")
    
    # Test valid decrypt
    plaintext = pii.decrypt(result["ciphertext_b64"], result["nonce_b64"])
    assert plaintext == "valid data"
    print("✅ Valid decryption works")

if __name__ == "__main__":
    test_pii_validation()
    print("\n🎉 PII validation tests passed!")