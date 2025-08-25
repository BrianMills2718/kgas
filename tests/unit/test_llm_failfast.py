#!/usr/bin/env python3
"""Test LLM integration fail-fast behavior when APIs are truly unavailable."""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_llm_failfast():
    """Test that LLM integration properly fails fast when no APIs available."""
    print("=== TESTING LLM INTEGRATION FAIL-FAST BEHAVIOR ===")
    print("Testing with APIs truly unavailable (not just claiming unavailable)...")
    
    try:
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        from src.core.api_auth_manager import APIAuthManager
        from src.core.enhanced_api_client import EnhancedAPIClient
        from src.ontology_generator import DomainOntology, EntityType
        
        # Create a mock auth manager that reports no services available
        class NoAPIAuthManager(APIAuthManager):
            def is_service_available(self, service: str) -> bool:
                """Report all services as unavailable."""
                return False
            
            def get_credentials(self, service: str):
                """Return None for all services."""
                return None
        
        # Create client with no API access
        auth_manager = NoAPIAuthManager()
        api_client = EnhancedAPIClient(auth_manager)
        
        # Force the client to have no API access
        client = LLMExtractionClient(api_client=api_client, auth_manager=auth_manager)
        client.openai_available = False
        client.google_available = False
        
        # Create test ontology
        ontology = DomainOntology(
            domain_name='test_domain',
            domain_description='Test domain for fail-fast verification',
            entity_types=[
                EntityType(name='PERSON', description='People', attributes=['name'], examples=['John Doe'])
            ],
            relationship_types=[],
            extraction_patterns=[]
        )
        
        # Test 1: Async extract_entities should fail fast
        print("\nTest 1: Testing async extract_entities...")
        try:
            result = await client.extract_entities('Test text for extraction', ontology)
            print(f"❌ WRONG: Should have raised RuntimeError, got result: {result}")
            return False
        except RuntimeError as e:
            if 'LLM' in str(e) and ('fail' in str(e).lower() or 'services' in str(e).lower()):
                print(f"✅ CORRECT: Async extraction fails fast: {e}")
            else:
                print(f"❌ WRONG: Unexpected error: {e}")
                return False
        
        # Test 2: Direct _extract_entities_legacy should fail fast
        print("\nTest 2: Testing _extract_entities_legacy directly...")
        try:
            result = await client._extract_entities_legacy('Test text', ontology, None)
            print(f"❌ WRONG: Should have raised RuntimeError, got result: {result}")
            return False
        except RuntimeError as e:
            if 'LLM' in str(e) and ('fail' in str(e).lower() or 'services' in str(e).lower()):
                print(f"✅ CORRECT: Legacy extraction fails fast: {e}")
            else:
                print(f"❌ WRONG: Unexpected error: {e}")
                return False
        except Exception as e:
            # Might fail with other errors due to no API access
            if 'API' in str(e) or 'service' in str(e).lower():
                print(f"✅ CORRECT: Legacy extraction fails with API error: {e}")
            else:
                print(f"❌ WRONG: Unexpected error: {e}")
                return False
        
        print("\n✅ ALL LLM INTEGRATION FAIL-FAST TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_failfast())
    sys.exit(0 if success else 1)