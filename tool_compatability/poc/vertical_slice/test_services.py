#!/usr/bin/env python3
"""Simple, systematic tests for services"""

import sys
import json
sys.path.append('/home/brian/projects/Digimons')

def test_vector_service():
    """Test VectorService"""
    print("\nTesting VectorService...")
    errors = []
    
    try:
        from services.vector_service import VectorService
        service = VectorService()
        
        # Test 1: Basic embedding
        embedding = service.embed_text("test")
        if len(embedding) != 1536:
            errors.append(f"Wrong embedding size: {len(embedding)}")
        
        # Test 2: Empty text
        empty_embedding = service.embed_text("")
        if len(empty_embedding) != 1536:
            errors.append("Empty text should return zero vector")
        
        # Test 3: Different texts give different embeddings
        emb1 = service.embed_text("hello")
        emb2 = service.embed_text("goodbye")
        if emb1 == emb2:
            errors.append("Different texts gave same embedding")
            
    except Exception as e:
        errors.append(f"VectorService failed: {e}")
    
    if errors:
        print("❌ VectorService tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ VectorService: All tests passed")
        return True

def test_table_service():
    """Test TableService"""
    print("\nTesting TableService...")
    errors = []
    
    try:
        from services.table_service import TableService
        service = TableService('test.db')  # Use test database
        
        # Test 1: Save embedding
        emb_id = service.save_embedding("test", [1.0, 2.0, 3.0])
        if not emb_id:
            errors.append("Failed to save embedding")
        
        # Test 2: Save data
        data_id = service.save_data("test_key", {"value": 123})
        if not data_id:
            errors.append("Failed to save data")
        
        # Test 3: Retrieve embeddings
        embeddings = service.get_embeddings(1)
        if not embeddings or embeddings[0]['text'] != 'test':
            errors.append("Failed to retrieve embedding")
            
    except Exception as e:
        errors.append(f"TableService failed: {e}")
    finally:
        # Cleanup test database
        import os
        if os.path.exists('test.db'):
            os.remove('test.db')
    
    if errors:
        print("❌ TableService tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ TableService: All tests passed")
        return True

def test_integration():
    """Test services working together"""
    print("\nTesting Integration...")
    errors = []
    
    try:
        from services.vector_service import VectorService
        from services.table_service import TableService
        
        vector_svc = VectorService()
        table_svc = TableService('test_integration.db')
        
        # Generate embedding and store it
        text = "Integration test"
        embedding = vector_svc.embed_text(text)
        row_id = table_svc.save_embedding(text, embedding)
        
        # Verify storage
        stored = table_svc.get_embeddings(1)
        if not stored:
            errors.append("Failed to store/retrieve embedding")
        else:
            stored_emb = json.loads(stored[0]['embedding'])
            if len(stored_emb) != 1536:
                errors.append("Stored embedding has wrong size")
                
    except Exception as e:
        errors.append(f"Integration failed: {e}")
    finally:
        import os
        if os.path.exists('test_integration.db'):
            os.remove('test_integration.db')
    
    if errors:
        print("❌ Integration tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Integration: All tests passed")
        return True

if __name__ == "__main__":
    all_pass = True
    all_pass &= test_vector_service()
    all_pass &= test_table_service()
    all_pass &= test_integration()
    
    print("\n" + "="*50)
    if all_pass:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)