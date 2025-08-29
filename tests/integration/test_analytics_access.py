#!/usr/bin/env python3
"""Test analytics access point"""

import os
import sys
sys.path.append('/home/brian/projects/Digimons')

# Set environment for Neo4j
os.environ['NEO4J_PASSWORD'] = 'devpassword'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'

print("=" * 60)
print("ANALYTICS ACCESS TEST")
print("=" * 60)

# Test 1: Import analytics_access
print("\n1. Testing analytics_access import...")
try:
    from src.core.analytics_access import (
        get_analytics, 
        get_orchestrator, 
        get_converter,
        list_available_analytics
    )
    print("   ✅ analytics_access imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Test 2: List available analytics
print("\n2. Listing available analytics capabilities...")
capabilities = list_available_analytics()
print(f"   Found {len(capabilities)} analytics capabilities:")
for name, desc in list(capabilities.items())[:5]:  # Show first 5
    print(f"   - {name}: {desc[:50]}...")

# Test 3: Get analytics components without ServiceManager
print("\n3. Testing get_analytics() without ServiceManager...")
try:
    analytics = get_analytics()
    print(f"   ✅ Got {len(analytics)} analytics components:")
    for name in analytics.keys():
        print(f"      - {name}")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Test 4: Get analytics with ServiceManager
print("\n4. Testing get_analytics() with ServiceManager...")
try:
    from src.core.service_manager import ServiceManager
    sm = ServiceManager()
    analytics = get_analytics(sm)
    print(f"   ✅ Got {len(analytics)} components with ServiceManager")
except Exception as e:
    print(f"   ⚠️  ServiceManager integration issue: {e}")

# Test 5: Get individual components
print("\n5. Testing individual component access...")
try:
    orchestrator = get_orchestrator()
    print("   ✅ CrossModalOrchestrator created")
    
    converter = get_converter()
    print("   ✅ CrossModalConverter created")
    
    # Check if they have the expected methods
    if hasattr(orchestrator, 'analyze'):
        print("   ✅ Orchestrator has 'analyze' method")
    if hasattr(converter, 'convert'):
        print("   ✅ Converter has 'convert' method")
        
except Exception as e:
    print(f"   ❌ Component creation failed: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

success_count = 0
if 'analytics_access' in sys.modules:
    success_count += 1
    print("✅ Analytics access module loaded")

if 'analytics' in locals() and len(analytics) > 0:
    success_count += 1
    print(f"✅ {len(analytics)} analytics components accessible")

if 'orchestrator' in locals():
    success_count += 1
    print("✅ CrossModalOrchestrator accessible")

if 'converter' in locals():
    success_count += 1
    print("✅ CrossModalConverter accessible")

print(f"\nResult: {success_count}/4 core components working")
if success_count == 4:
    print("🎉 Analytics infrastructure successfully connected!")
else:
    print("⚠️  Some components need attention")