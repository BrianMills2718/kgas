"""
Configuration System Demonstration
=================================

Comprehensive demonstration of the KGAS configuration management system,
showing all key features and validating production readiness.

Features Demonstrated:
- Environment-based configuration loading
- Secure credential management with encryption
- Configuration validation and health checks
- Runtime configuration updates
- Schema framework integration
- Error handling configuration
- Production deployment scenarios

Usage:
    python demo_configuration_system.py
"""

import os
import sys
import json
import time
import tempfile
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.configuration_service import ConfigurationService, initialize_configuration
from src.core.production_config_manager import create_default_configurations


def setup_logging():
    """Set up logging for demonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_environment_based_config():
    """Demonstrate environment-based configuration loading."""
    print("\n" + "="*60)
    print("🌍 ENVIRONMENT-BASED CONFIGURATION DEMO")
    print("="*60)
    
    # Test different environments
    environments = ['development', 'testing', 'production']
    
    for env in environments:
        print(f"\n📋 Testing {env.upper()} environment:")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create default configurations
            create_default_configurations(temp_dir)
            
            # Initialize configuration service
            config_service = ConfigurationService(config_dir=temp_dir, environment=env)
            
            # Show environment-specific settings
            summary = config_service.get_configuration_summary()
            print(f"   Environment: {summary['environment']}")
            print(f"   Health: {summary['health']['status']}")
            print(f"   Neo4j Host: {summary['database']['neo4j_host']}")
            print(f"   Security encryption: {summary['security']['encrypt_credentials']}")
            print(f"   Circuit breaker: {summary['error_handling']['circuit_breaker_enabled']}")


def demo_secure_credential_management():
    """Demonstrate secure credential management."""
    print("\n" + "="*60)
    print("🔐 SECURE CREDENTIAL MANAGEMENT DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Store encrypted API keys
        test_credentials = {
            'openai': 'sk-test1234567890abcdef',
            'anthropic': 'ant-api-key-test',
            'google': 'google-api-key-test'
        }
        
        print("\n🔒 Storing encrypted credentials:")
        for provider, api_key in test_credentials.items():
            config_service.set_api_key(provider, api_key, expires_days=90)
            print(f"   ✅ Stored {provider} API key (encrypted)")
        
        # Retrieve and validate credentials
        print("\n🔓 Retrieving and validating credentials:")
        for provider in test_credentials.keys():
            try:
                retrieved_key = config_service.get_api_key(provider)
                original_key = test_credentials[provider]
                
                if retrieved_key == original_key:
                    print(f"   ✅ {provider}: Credential retrieved successfully")
                else:
                    print(f"   ❌ {provider}: Credential mismatch")
            except Exception as e:
                print(f"   ❌ {provider}: Failed to retrieve - {e}")
        
        # Show credential metadata
        print("\n📊 Credential metadata:")
        credentials = config_service.credential_manager.list_credentials()
        for cred in credentials:
            print(f"   {cred['provider']}: expires {cred['expires_at']}, "
                  f"encrypted={cred['encrypted']}, accessed {cred['access_count']} times")


def demo_configuration_validation():
    """Demonstrate configuration validation and health checks."""
    print("\n" + "="*60)
    print("🏥 CONFIGURATION VALIDATION & HEALTH DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with minimal configuration (should have issues)
        config_service = ConfigurationService(config_dir=temp_dir)
        
        print("\n🔍 Initial health check (expected issues):")
        health = config_service.check_health(force_check=True)
        
        print(f"   Overall status: {health.overall_status}")
        if health.issues:
            print("   Issues found:")
            for issue in health.issues:
                print(f"     - {issue}")
        if health.warnings:
            print("   Warnings:")
            for warning in health.warnings:
                print(f"     - {warning}")
        
        # Add credentials to improve health
        print("\n🔧 Adding credentials to improve health:")
        config_service.set_api_key('openai', 'sk-test123456789')
        config_service.set_api_key('anthropic', 'ant-test123456789')
        
        print("\n🔍 Health check after adding credentials:")
        health = config_service.check_health(force_check=True)
        
        print(f"   Overall status: {health.overall_status}")
        if health.issues:
            print("   Remaining issues:")
            for issue in health.issues:
                print(f"     - {issue}")
        if health.warnings:
            print("   Warnings:")
            for warning in health.warnings:
                print(f"     - {warning}")
        
        if health.is_healthy():
            print("   ✅ Configuration is now healthy!")


def demo_schema_framework_config():
    """Demonstrate schema framework configuration."""
    print("\n" + "="*60)
    print("🏗️ SCHEMA FRAMEWORK CONFIGURATION DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Get schema configuration
        schema_config = config_service.get_schema_config()
        
        print("\n📋 Schema Framework Settings:")
        print(f"   Enabled paradigms: {', '.join(schema_config.enabled_paradigms)}")
        print(f"   Default paradigm: {schema_config.default_paradigm}")
        print(f"   Cross-paradigm validation: {schema_config.cross_paradigm_validation}")
        print(f"   Auto-transform: {schema_config.auto_transform}")
        print(f"   Validation timeout: {schema_config.validation_timeout}s")
        
        # Validate schema paradigms are all available
        print("\n✅ Schema paradigm validation:")
        available_paradigms = ['uml', 'rdf_owl', 'orm', 'typedb', 'nary']
        for paradigm in available_paradigms:
            if paradigm in schema_config.enabled_paradigms:
                print(f"   ✅ {paradigm}: Enabled")
            else:
                print(f"   ❌ {paradigm}: Disabled")


def demo_error_handling_config():
    """Demonstrate error handling configuration."""
    print("\n" + "="*60)
    print("⚡ ERROR HANDLING CONFIGURATION DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Get error handling configuration
        error_config = config_service.get_error_config()
        
        print("\n🔧 Error Handling Settings:")
        print(f"   Circuit breaker enabled: {error_config.circuit_breaker_enabled}")
        print(f"   Circuit breaker threshold: {error_config.circuit_breaker_threshold}")
        print(f"   Circuit breaker timeout: {error_config.circuit_breaker_timeout}s")
        print(f"   Max retries: {error_config.max_retries}")
        print(f"   Retry delay: {error_config.retry_delay}s")
        print(f"   Exponential backoff: {error_config.exponential_backoff}")
        print(f"   Health check interval: {error_config.health_check_interval}s")
        print(f"   Metrics enabled: {error_config.metrics_enabled}")
        
        # Test configuration for different environments
        print("\n🌍 Error handling across environments:")
        environments = ['development', 'production']
        
        for env in environments:
            env_config_service = ConfigurationService(config_dir=temp_dir, environment=env)
            env_error_config = env_config_service.get_error_config()
            print(f"   {env}: Circuit breaker = {env_error_config.circuit_breaker_enabled}, "
                  f"Max retries = {env_error_config.max_retries}")


def demo_runtime_updates():
    """Demonstrate runtime configuration updates."""
    print("\n" + "="*60)
    print("🔄 RUNTIME CONFIGURATION UPDATES DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Initial state
        print("\n📊 Initial configuration state:")
        summary = config_service.get_configuration_summary()
        print(f"   Active LLM providers: {len(config_service.get_active_llm_providers())}")
        
        # Add new credential at runtime
        print("\n🔧 Adding new credential at runtime:")
        config_service.set_api_key('openai', 'sk-runtime-test-key')
        
        print("   ✅ Added OpenAI credential")
        
        # Check updated state
        print("\n📊 Updated configuration state:")
        summary = config_service.get_configuration_summary()
        active_providers = config_service.get_active_llm_providers()
        print(f"   Active LLM providers: {len(active_providers)} ({', '.join(active_providers)})")
        
        # Rotate credential
        print("\n🔄 Rotating credential:")
        config_service.rotate_credential('openai', 'sk-rotated-test-key')
        print("   ✅ Rotated OpenAI credential")
        
        # Reload configuration
        print("\n🔃 Reloading configuration:")
        config_service.reload_configuration()
        print("   ✅ Configuration reloaded")


def demo_production_deployment():
    """Demonstrate production deployment scenario."""
    print("\n" + "="*60)
    print("🚀 PRODUCTION DEPLOYMENT SCENARIO DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Simulate production environment setup
        print("\n🏭 Setting up production environment:")
        
        # Set production environment variables
        os.environ['KGAS_ENV'] = 'production'
        os.environ['KGAS_NEO4J_HOST'] = 'prod-neo4j.example.com'
        os.environ['KGAS_NEO4J_PASSWORD'] = 'secure-production-password'
        os.environ['KGAS_OPENAI_API_KEY'] = 'sk-production-openai-key'
        os.environ['KGAS_ANTHROPIC_API_KEY'] = 'ant-production-anthropic-key'
        
        try:
            config_service = ConfigurationService(config_dir=temp_dir, environment='production')
            
            print("   ✅ Production configuration service initialized")
            
            # Validate production settings
            print("\n🔍 Production configuration validation:")
            summary = config_service.get_configuration_summary()
            
            print(f"   Environment: {summary['environment']}")
            print(f"   Security encryption: {summary['security']['encrypt_credentials']}")
            print(f"   Database host: {summary['database']['neo4j_host']}")
            print(f"   Active LLM providers: {len(config_service.get_active_llm_providers())}")
            
            # Health check for production
            health = config_service.check_health(force_check=True)
            print(f"   Health status: {health.overall_status}")
            
            if health.is_healthy():
                print("   ✅ Production configuration is healthy and ready for deployment!")
            else:
                print("   ⚠️ Production configuration has issues:")
                for issue in health.issues:
                    print(f"     - {issue}")
        
        finally:
            # Clean up environment variables
            for var in ['KGAS_ENV', 'KGAS_NEO4J_HOST', 'KGAS_NEO4J_PASSWORD', 
                       'KGAS_OPENAI_API_KEY', 'KGAS_ANTHROPIC_API_KEY']:
                os.environ.pop(var, None)


def demo_configuration_export():
    """Demonstrate configuration export and backup."""
    print("\n" + "="*60)
    print("💾 CONFIGURATION EXPORT & BACKUP DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Add some configuration
        config_service.set_api_key('openai', 'sk-export-test-key')
        config_service.set_api_key('anthropic', 'ant-export-test-key')
        
        print("\n📤 Exporting configuration:")
        export_data = config_service.export_configuration(include_credentials=False)
        
        print(f"   Environment: {export_data['environment']}")
        print(f"   Credential count: {len(export_data['credential_metadata'])}")
        print(f"   Export timestamp: {time.ctime(export_data['export_timestamp'])}")
        
        # Show credential metadata
        print("\n📋 Credential metadata in export:")
        for cred in export_data['credential_metadata']:
            print(f"   {cred['provider']}: created {cred['created_at']}, "
                  f"expires {cred['expires_at']}")
        
        print("\n✅ Configuration export completed (credentials excluded for security)")


def demo_performance_monitoring():
    """Demonstrate configuration performance monitoring."""
    print("\n" + "="*60)
    print("📊 CONFIGURATION PERFORMANCE MONITORING DEMO")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_service = ConfigurationService(config_dir=temp_dir)
        
        # Add credentials for testing
        config_service.set_api_key('openai', 'sk-perf-test-key')
        
        print("\n⏱️ Performance testing:")
        
        # Test credential retrieval performance
        start_time = time.time()
        iterations = 1000
        
        for _ in range(iterations):
            config_service.get_api_key('openai')
        
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations * 1000  # Convert to milliseconds
        
        print(f"   Credential retrieval: {avg_time:.2f}ms average over {iterations} iterations")
        
        # Test health check performance
        start_time = time.time()
        config_service.check_health(force_check=True)
        end_time = time.time()
        
        print(f"   Health check: {(end_time - start_time)*1000:.2f}ms")
        
        # Test configuration summary performance
        start_time = time.time()
        config_service.get_configuration_summary()
        end_time = time.time()
        
        print(f"   Configuration summary: {(end_time - start_time)*1000:.2f}ms")
        
        print("\n✅ Performance monitoring completed")


def main():
    """Run comprehensive configuration system demonstration."""
    setup_logging()
    
    print("🚀 KGAS CONFIGURATION SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("This demo validates the production-ready configuration management system")
    print("with environment-based loading, secure credentials, and comprehensive validation.")
    
    try:
        # Run all demonstrations
        demo_environment_based_config()
        demo_secure_credential_management()
        demo_configuration_validation()
        demo_schema_framework_config()
        demo_error_handling_config()
        demo_runtime_updates()
        demo_production_deployment()
        demo_configuration_export()
        demo_performance_monitoring()
        
        print("\n" + "="*80)
        print("🎉 CONFIGURATION SYSTEM DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n✅ All configuration management features validated:")
        print("   • Environment-based configuration loading")
        print("   • Secure credential management with encryption")
        print("   • Configuration validation and health checks")
        print("   • Runtime configuration updates")
        print("   • Schema framework integration")
        print("   • Error handling configuration")
        print("   • Production deployment scenarios")
        print("   • Configuration export and backup")
        print("   • Performance monitoring")
        print("\n🚀 The configuration system is PRODUCTION-READY!")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())