#!/usr/bin/env python3
"""
Test Gemini Entity Extractor Integration
REAL API TEST - No mocks
"""

import sys
from pathlib import Path
sys.path.append('/home/brian/projects/Digimons')

from src.core.composition_service import CompositionService
from src.core.adapter_factory import UniversalAdapterFactory
from src.tools.gemini_entity_extractor import GeminiEntityExtractor

def test_gemini_integration():
    """Test GeminiEntityExtractor through composition service"""
    
    print("="*60)
    print("GEMINI ENTITY EXTRACTOR INTEGRATION TEST")
    print("="*60)
    
    # 1. Create composition service
    service = CompositionService()
    service.adapter_factory = UniversalAdapterFactory()
    print("✅ CompositionService created")
    
    try:
        # 2. Create Gemini entity extractor
        extractor = GeminiEntityExtractor()
        print("✅ GeminiEntityExtractor instantiated (API key loaded)")
    except ValueError as e:
        print(f"❌ Failed to create extractor: {e}")
        return False
    
    # 3. Register it
    print("\n1. Registering GeminiEntityExtractor...")
    success = service.register_any_tool(extractor)
    
    if success:
        print("   ✅ GeminiEntityExtractor registered successfully")
    else:
        print("   ❌ Registration failed")
        return False
    
    # 4. Test with real text
    print("\n2. Testing with REAL Gemini API...")
    
    test_text = """
    Apple Inc. CEO Tim Cook announced today in Cupertino, California that the company 
    will invest $1 billion in artificial intelligence research. The announcement came 
    during a meeting with President Biden at the White House on January 15, 2024.
    Microsoft's Satya Nadella and Google's Sundar Pichai were also present.
    """
    
    print(f"   Input text: {test_text[:100]}...")
    
    try:
        # Call Gemini directly to show it works
        result = extractor.process(test_text)
        
        print("\n3. REAL Gemini API Response:")
        print(f"   Entities found: {result['entity_count']}")
        print(f"   Model used: {result['model']}")
        
        if result['entities']:
            print("\n   Extracted Entities:")
            for entity in result['entities'][:5]:  # Show first 5
                print(f"      - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')}) - confidence: {entity.get('confidence', 'N/A')}")
        
        print(f"\n   Raw API response (first 200 chars):")
        print(f"   {result['api_response'][:200]}")
        
        # Success if we got entities
        if result['entity_count'] > 0:
            print("\n   ✅ Gemini API successfully extracted entities")
        else:
            print("\n   ⚠️  No entities extracted (but API call succeeded)")
            
    except Exception as e:
        print(f"\n   ❌ Gemini API call failed: {e}")
        return False
    
    # 5. Check framework integration
    print("\n4. Framework Integration Check:")
    
    # Check if registered in framework
    if "GeminiEntityExtractor" in service.framework.tools:
        print("   ✅ GeminiEntityExtractor in framework registry")
        
        # Check capabilities
        adapted_tool = service.framework.tools.get("GeminiEntityExtractor")
        if adapted_tool:
            caps = adapted_tool.get_capabilities()
            print(f"   Input Type: {caps.input_type}")
            print(f"   Output Type: {caps.output_type}")
    else:
        print("   ❌ Not found in framework registry")
    
    # 6. Show metrics
    print("\n5. Metrics:")
    metrics = service.get_metrics()
    print(f"   Tools adapted: {metrics['tools_adapted']}")
    
    print("\n" + "="*60)
    print("GEMINI INTEGRATION TEST COMPLETE")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)