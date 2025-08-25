#!/usr/bin/env python3
"""
Kill-Switch Test: Test if T31 accepts synthetic mentions
This determines if the facade approach is viable before building more.
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.core.tool_contract import ToolRequest

def test_t31_synthetic_mentions():
    """Test if T31 accepts synthetic mentions like facade translator would produce"""
    
    print("=" * 60)
    print("KILL-SWITCH TEST: T31 Synthetic Mentions")
    print("=" * 60)
    
    try:
        # Initialize
        print("🔧 Initializing ServiceManager and T31...")
        service_manager = ServiceManager()
        t31 = T31EntityBuilderUnified(service_manager)
        
        # Create synthetic mentions like facade translator would produce
        print("📝 Creating synthetic mentions...")
        synthetic_mentions = [
            {
                "text": "Apple Inc.",
                "entity_type": "ORGANIZATION", 
                "start_pos": 0,  # Synthetic position
                "end_pos": 10,   # Synthetic position
                "confidence": 0.95,
                "entity_id": "apple_inc_001",
                "canonical_name": "Apple Inc.",
                "source_chunk": "test_chunk_001"
            },
            {
                "text": "Tim Cook",
                "entity_type": "PERSON",
                "start_pos": 20,  # Synthetic position
                "end_pos": 28,   # Synthetic position
                "confidence": 0.90,
                "entity_id": "tim_cook_001", 
                "canonical_name": "Tim Cook",
                "source_chunk": "test_chunk_001"
            }
        ]
        
        print(f"   Created {len(synthetic_mentions)} synthetic mentions")
        
        # Test if T31 accepts this
        print("🧪 Testing T31 with synthetic mentions...")
        request = ToolRequest(
            input_data={"mentions": synthetic_mentions}
        )
        
        result = t31.execute(request)
        
        print("\n📊 RESULTS:")
        print(f"   Status: {result.status}")
        print(f"   Data keys: {list(result.data.keys()) if result.data else 'None'}")
        
        if result.status == "success":
            entities_count = len(result.data.get("entities", []))
            print(f"   Entities created: {entities_count}")
            
            print("\n✅ SUCCESS: T31 accepts synthetic mentions!")
            print("   → Facade approach is VIABLE")
            print("   → Continue with facade implementation")
            return True
            
        else:
            print(f"   Error: {result.error_message}")
            print(f"   Error code: {result.error_code}")
            
            print("\n❌ FAILURE: T31 rejects synthetic mentions")
            print("   → Facade approach is NOT viable")
            print("   → Need Plan B/C/D from CLAUDE.md")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   → Missing dependencies - check installation")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("   → System issue - investigate further")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_t31_synthetic_mentions()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 NEXT STEP: Build real facade (3 days)")
        print("   1. Day 1: Get ONE real tool working") 
        print("   2. Day 2: Connect T23C → T31")
        print("   3. Day 3: Complete facade")
    else:
        print("🔀 NEXT STEP: Alternative approaches")
        print("   Plan B: Modify T23C to output mentions")
        print("   Plan C: Merge T23C+T31+T34") 
        print("   Plan D: Accept incompatibility")
    print("=" * 60)
    
    sys.exit(0 if success else 1)