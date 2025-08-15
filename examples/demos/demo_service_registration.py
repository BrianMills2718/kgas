#!/usr/bin/env python3
"""
Service Registration Demonstration

Shows how to use the ServiceRegistry and dependency injection container
to manage all KGAS services including UniversalLLMService.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append('/home/brian/projects/Digimons')

from src.core.service_registry import get_service_registry, initialize_all_services
from src.core.dependency_injection import get_container


def demo_basic_service_registration():
    """Demonstrate basic service registration and retrieval"""
    print("🔧 Basic Service Registration Demo")
    print("="*50)
    
    # Get the service registry (automatically registers all core services)
    registry = get_service_registry()
    
    # Show registered services
    print(f"📋 Registered Services: {len(registry.registered_services)}")
    for service_name, definition in registry.registered_services.items():
        print(f"  • {service_name} ({definition.lifecycle.value})")
    
    print("\n✅ All core services automatically registered")


def demo_service_instantiation():
    """Demonstrate service instantiation with dependency injection"""
    print("\n🔧 Service Instantiation Demo")
    print("="*50)
    
    container = get_container()
    
    # Get services (automatically created with dependencies)
    print("📦 Getting services from container...")
    
    config_manager = container.get("config_manager")
    print(f"  • ConfigurationManager: {type(config_manager).__name__}")
    
    identity_service = container.get("identity_service")
    print(f"  • IdentityService: {type(identity_service).__name__}")
    
    universal_llm_service = container.get("universal_llm_service")
    print(f"  • UniversalLLMService: {type(universal_llm_service).__name__}")
    
    print("\n✅ All services instantiated successfully with dependencies")


def demo_service_configuration():
    """Demonstrate service configuration injection"""
    print("\n🔧 Service Configuration Demo")
    print("="*50)
    
    # Initialize with custom configuration
    custom_config = {
        "llm": {
            "default_provider": "openai",
            "fallback_providers": ["gemini", "anthropic"],
            "max_retries": 5
        },
        "services": {
            "identity": {
                "embedding_service_enabled": True,
                "persistence_layer_enabled": True
            },
            "provenance": {
                "storage_backend": "sqlite",
                "retention_days": 30
            }
        }
    }
    
    registry = initialize_all_services(custom_config)
    container = registry.container
    
    print("⚙️  Configuration injected into services:")
    print(f"  • Container config sections: {len(container._configuration)}")
    
    # Test configuration access
    config_manager = container.get("config_manager")
    llm_config = config_manager.get_config_section("llm")
    identity_config = config_manager.get_config_section("services.identity")
    
    print(f"  • LLM config provider: {llm_config.get('default_provider', 'not set')}")
    print(f"  • Identity embedding enabled: {identity_config.get('embedding_service_enabled', False)}")
    
    print("\n✅ Configuration properly injected into services")


async def demo_async_service_lifecycle():
    """Demonstrate async service lifecycle management"""
    print("\n🔧 Async Service Lifecycle Demo")
    print("="*50)
    
    registry = get_service_registry()
    
    print("🚀 Starting all services...")
    await registry.startup_all_services()
    print("  ✅ All services started")
    
    # Get service status
    status = registry.get_service_status()
    healthy_services = 0
    for s in status.values():
        if isinstance(s, dict):
            health = s.get('health', {})
            if isinstance(health, dict) and health.get('status') != 'error':
                healthy_services += 1
    
    print(f"📊 Service Health Check: {healthy_services}/{len(status)} healthy")
    for service_name, service_status in status.items():
        if isinstance(service_status, dict):
            health = service_status.get('health', {})
            if isinstance(health, dict):
                health_status = health.get('status', 'unknown')
            else:
                health_status = str(health)
        else:
            health_status = 'unknown'
        print(f"  • {service_name}: {health_status}")
    
    print("\n🛑 Shutting down all services...")
    await registry.shutdown_all_services()
    print("  ✅ All services shut down cleanly")


def demo_universal_llm_integration():
    """Demonstrate UniversalLLMService integration through registry"""
    print("\n🔧 UniversalLLMService Integration Demo")
    print("="*50)
    
    container = get_container()
    
    # Get UniversalLLMService through dependency injection
    llm_service = container.get("universal_llm_service")
    
    print(f"🤖 UniversalLLMService type: {type(llm_service).__name__}")
    print(f"   • Initialized: {hasattr(llm_service, 'config_manager')}")
    print(f"   • Has rate limiter: {hasattr(llm_service, 'rate_limiter')}")
    print(f"   • Has circuit breaker: {hasattr(llm_service, 'circuit_breaker')}")
    
    # Show that it's a singleton
    llm_service_2 = container.get("universal_llm_service")
    print(f"   • Singleton behavior: {llm_service is llm_service_2}")
    
    print("\n✅ UniversalLLMService properly integrated with dependency injection")


def demo_service_registry_benefits():
    """Demonstrate the benefits of using service registry"""
    print("\n🔧 Service Registry Benefits Demo")
    print("="*50)
    
    registry = get_service_registry()
    
    print("🎯 Key Benefits:")
    print("  • Automatic service discovery and registration")
    print("  • Dependency injection with proper ordering")
    print("  • Configuration injection per service")
    print("  • Lifecycle management (startup/shutdown)")
    print("  • Health monitoring and status reporting")
    print("  • Singleton pattern enforcement")
    print("  • Graceful fallback to mock services")
    
    print("\n📈 Before vs After:")
    print("  Before: Manual service creation, no dependency management")
    print("  After: Centralized registry with automatic dependency resolution")
    
    # Show dependency order
    dependency_order = registry._get_dependency_order()
    print(f"\n🔗 Dependency Order (6 services):")
    for i, service_name in enumerate(dependency_order, 1):
        definition = registry.registered_services[service_name]
        deps = definition.dependencies or []
        dep_str = f" (depends on: {', '.join(deps)})" if deps else " (no dependencies)"
        print(f"  {i}. {service_name}{dep_str}")
    
    print("\n✅ Service registry provides comprehensive service management")


async def main():
    """Run comprehensive service registration demonstration"""
    print("🚀 KGAS Service Registration System Demonstration")
    print("="*60)
    
    # Run all demonstrations
    demo_basic_service_registration()
    demo_service_instantiation()
    demo_service_configuration()
    await demo_async_service_lifecycle()
    demo_universal_llm_integration()
    demo_service_registry_benefits()
    
    print("\n🎉 Service Registration System Successfully Demonstrated!")
    print("="*60)
    print("The service registry provides:")
    print("  ✅ Automatic service registration")
    print("  ✅ Dependency injection")
    print("  ✅ Configuration management")
    print("  ✅ Lifecycle management")
    print("  ✅ UniversalLLMService integration")
    print("  ✅ Production-ready service management")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()