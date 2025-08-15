#!/usr/bin/env python3
"""
Testing Infrastructure Framework Demonstration

Demonstrates the complete testing infrastructure built for TD.4 including:
- Dependency injection support in tests
- Mock service factories with realistic behavior
- Integration testing with real/mock service combinations
- Performance testing with monitoring
- Automated test discovery and execution
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.testing import (
    BaseTest, AsyncBaseTest, TDDTestBase,
    MockServiceFactory, ServiceFixtures,
    IntegrationTestBase, PerformanceTestBase,
    TestRunner, TestAutomation
)
from src.testing.mock_factory import MockBehavior, MockServiceConfig
from src.testing.integration_test import IntegrationMode
from src.core.dependency_injection import ServiceContainer, ServiceLifecycle
from src.core.interfaces.service_interfaces import (
    IdentityServiceInterface, ProvenanceServiceInterface, QualityServiceInterface
)


async def demo_basic_testing_infrastructure():
    """Demonstrate basic testing infrastructure capabilities"""
    print("🧪 TESTING INFRASTRUCTURE DEMONSTRATION")
    print("=" * 60)
    
    print("\n1. 📋 BASE TEST CLASSES")
    print("-" * 30)
    
    # Demonstrate base test class with async capabilities
    class ExampleUnitTest(AsyncBaseTest):
        async def test_service_registration(self):
            """Test service registration with dependency injection"""
            # Initialize fixtures
            self.fixtures = ServiceFixtures()
            
            # Register a mock service
            mock_service = self.register_mock_service(
                'identity_service',
                IdentityServiceInterface,
                health_check=self.fixtures.create_service_response_fixture()
            )
            
            # Start services
            await self.start_services()
            
            # Test service retrieval
            service = await self.async_get_service('identity_service')
            self.assertIsNotNone(service)
            print("  ✅ Service registration and retrieval working")
            
            # Test standard response format
            response = await service.health_check()
            self.assert_service_response(response, success=True)
            print("  ✅ Service response validation working")
            
            # Stop services
            await self.stop_services()
    
    # Run the unit test
    unit_test = ExampleUnitTest()
    unit_test.setUp()
    try:
        await unit_test.test_service_registration()
        print("  🎯 BaseTest demonstration complete")
    finally:
        unit_test.tearDown()


async def demo_mock_service_factory():
    """Demonstrate intelligent mock service factory"""
    print("\n2. 🎭 MOCK SERVICE FACTORY")
    print("-" * 30)
    
    factory = MockServiceFactory()
    
    # Create different behavior patterns
    behaviors = [
        ("Success Pattern", MockServiceConfig(behavior=MockBehavior.SUCCESS)),
        ("Realistic Pattern", MockServiceConfig(
            behavior=MockBehavior.REALISTIC,
            success_rate=0.8,
            average_delay_ms=15.0
        )),
        ("Failure Pattern", MockServiceConfig(behavior=MockBehavior.FAILURE))
    ]
    
    for pattern_name, config in behaviors:
        print(f"\n  Testing {pattern_name}:")
        
        # Create mock with specific behavior
        mock_service = factory.create_mock_service(IdentityServiceInterface, config)
        
        # Test the mock
        response = await mock_service.health_check()
        print(f"    Health check success: {response.success}")
        
        mention_response = await mock_service.create_mention(
            surface_form="Test Entity",
            confidence=0.9
        )
        print(f"    Create mention success: {mention_response.success}")
        
        if hasattr(mention_response, 'data') and mention_response.data:
            print(f"    Response data: {mention_response.data}")
    
    # Show factory statistics
    stats = factory.get_mock_statistics()
    print(f"\n  📊 Factory Statistics: {stats}")
    print("  🎯 Mock Service Factory demonstration complete")


async def demo_integration_testing():
    """Demonstrate integration testing framework"""
    print("\n3. 🔗 INTEGRATION TESTING")
    print("-" * 30)
    
    class ExampleIntegrationTest(IntegrationTestBase):
        async def test_service_workflow_integration(self):
            """Test integration between multiple services"""
            # Configure services for testing
            self.configure_service('identity_service', use_real=False)
            self.configure_service('provenance_service', use_real=False)
            self.configure_service('quality_service', use_real=False)
            
            # Set integration mode
            self.set_integration_mode(IntegrationMode.ALL_MOCK)
            
            # Set up services
            service_specs = {
                'identity_service': {'interface': IdentityServiceInterface},
                'provenance_service': {'interface': ProvenanceServiceInterface},
                'quality_service': {'interface': QualityServiceInterface}
            }
            
            await self.setup_services(service_specs)
            
            # Test a simple workflow
            workflow_steps = [
                {
                    'name': 'create_mention',
                    'service': 'identity_service',
                    'method': 'create_mention',
                    'params': {'surface_form': 'Test Entity', 'confidence': 0.9}
                },
                {
                    'name': 'record_operation',
                    'service': 'provenance_service',
                    'method': 'record_operation',
                    'params': {'operation_type': 'entity_extraction'}
                },
                {
                    'name': 'assess_quality',
                    'service': 'quality_service',
                    'method': 'assess_quality',
                    'params': {'data_type': 'entity_mention'}
                }
            ]
            
            workflow_result = await self.test_service_workflow('demo_workflow', workflow_steps)
            
            return workflow_result
    
    # Run integration test
    integration_test = ExampleIntegrationTest()
    integration_test.setUp()
    
    result = await integration_test.test_service_workflow_integration()
    
    print(f"  📊 Workflow completed with {len(result['steps'])} steps")
    for step in result['steps']:
        status = "✅" if step['success'] else "❌"
        print(f"    {status} {step['step']}")
    
    await integration_test.stop_services()
    integration_test.tearDown()
    print("  🎯 Integration Testing demonstration complete")


async def demo_performance_testing():
    """Demonstrate performance testing capabilities"""
    print("\n4. ⚡ PERFORMANCE TESTING")
    print("-" * 30)
    
    class ExamplePerformanceTest(PerformanceTestBase):
        async def test_service_performance(self):
            """Benchmark service performance"""
            # Register a mock service for performance testing
            self.register_mock_service(
                'identity_service',
                IdentityServiceInterface
            )
            
            await self.start_services()
            
            # Benchmark service method
            result = await self.benchmark_service_method(
                'identity_service',
                'create_mention',
                {'surface_form': 'Performance Test Entity'},
                iterations=5  # Small number for demo
            )
            
            return result
    
    # Run performance test
    perf_test = ExamplePerformanceTest()
    perf_test.setUp()
    
    benchmark_result = await perf_test.test_service_performance()
    
    print("  📊 Performance Benchmark Results:")
    summary = benchmark_result.get_summary()
    print(f"    Executions: {summary['executions']}")
    print(f"    Avg execution time: {summary['avg_execution_time_ms']:.2f}ms")
    print(f"    Throughput: {summary['throughput_ops_sec']:.2f} ops/sec")
    print(f"    Memory usage: {summary['memory_usage_mb']:.2f}MB")
    
    await perf_test.stop_services()
    perf_test.tearDown()
    print("  🎯 Performance Testing demonstration complete")


async def demo_tdd_testing():
    """Demonstrate TDD testing patterns"""
    print("\n5. 🔄 TDD TESTING PATTERNS")
    print("-" * 30)
    
    class ExampleTDDTest(TDDTestBase):
        async def test_behavior_driven_development(self):
            """Demonstrate TDD behavior-focused testing"""
            
            # Define behavior being tested
            self.define_behavior("Service should create entity mentions with proper validation")
            
            # Arrange - Set up test conditions
            test_data = self.arrange(
                surface_form="Dr. Alice Johnson",
                confidence=0.9,
                expected_result_type="mention"
            )
            
            # Register mock service
            self.register_mock_service('identity_service', IdentityServiceInterface)
            await self.start_services()
            
            # Act - Execute the behavior
            service = await self.async_get_service('identity_service')
            self.act("Creating mention with validation")
            
            result = await service.create_mention(
                surface_form=test_data['surface_form'],
                confidence=test_data['confidence']
            )
            
            # Assert - Verify behavior
            self.assert_behavior(
                result.success,
                "Service successfully creates mentions"
            )
            
            self.assert_behavior(
                'mention_id' in result.data,
                "Result contains mention identifier"
            )
            
            self.assert_behavior_equals(
                result.metadata.get('service'),
                'identity',
                "Result metadata correctly identifies service"
            )
            
            await self.stop_services()
            return self.get_test_summary()
    
    # Run TDD test
    tdd_test = ExampleTDDTest()
    tdd_test.setUp()
    
    test_summary = await tdd_test.test_behavior_driven_development()
    
    print("  📋 TDD Test Results:")
    for result in test_summary:
        print(f"    {result}")
    
    tdd_test.tearDown()
    print("  🎯 TDD Testing demonstration complete")


async def demo_test_automation():
    """Demonstrate automated test discovery and execution"""
    print("\n6. 🤖 TEST AUTOMATION")
    print("-" * 30)
    
    # Create test automation instance
    automation = TestAutomation()
    
    print("  🔍 Test Discovery:")
    
    # Discover tests (this will find tests in the testing module itself)
    discovered_tests = automation.discovery.discover_tests()
    
    print(f"    Discovered {len(discovered_tests)} test cases")
    
    # Group by test type
    by_type = {}
    for test in discovered_tests:
        test_type = test.test_type.value
        by_type[test_type] = by_type.get(test_type, 0) + 1
    
    for test_type, count in by_type.items():
        print(f"    {test_type}: {count} tests")
    
    print("  🎯 Test Automation demonstration complete")


async def demo_service_fixtures():
    """Demonstrate service fixtures for comprehensive test data"""
    print("\n7. 🗂️ SERVICE FIXTURES")
    print("-" * 30)
    
    fixtures = ServiceFixtures()
    
    # Create various test fixtures
    document = fixtures.create_test_document()
    entity = fixtures.create_test_entity("Dr. Alice Johnson", "PERSON")
    mention = fixtures.create_test_mention("Alice Johnson")
    relationship = fixtures.create_test_relationship(entity.entity_id, "entity_456", "WORKS_FOR")
    
    print(f"  📄 Document: {len(document.content)} characters")
    print(f"  👤 Entity: {entity.canonical_name} ({entity.entity_type})")
    print(f"  📍 Mention: '{mention.surface_form}' at pos {mention.start_pos}-{mention.end_pos}")
    print(f"  🔗 Relationship: {relationship.relationship_type}")
    
    # Create connected graph
    graph_data = fixtures.create_connected_graph(5, 7)
    print(f"  🕸️  Connected graph: {len(graph_data['entities'])} entities, {len(graph_data['relationships'])} relationships")
    
    # Create integration test scenario
    scenario = fixtures.create_integration_test_scenario("basic")
    print(f"  🎬 Test scenario: {scenario.get('scenario', 'unnamed')}")
    
    # Get fixture summary
    summary = fixtures.get_fixture_summary()
    print(f"  📊 Fixtures created: {summary}")
    
    print("  🎯 Service Fixtures demonstration complete")


async def main():
    """Run the complete testing infrastructure demonstration"""
    print("🚀 KGAS TESTING INFRASTRUCTURE FRAMEWORK")
    print("Comprehensive testing capabilities with dependency injection support")
    print()
    
    try:
        # Run all demonstrations
        await demo_basic_testing_infrastructure()
        await demo_mock_service_factory()
        await demo_integration_testing()
        await demo_performance_testing()
        await demo_tdd_testing()
        await demo_test_automation()
        await demo_service_fixtures()
        
        print("\n🎉 TESTING INFRASTRUCTURE DEMONSTRATION COMPLETE!")
        print("=" * 60)
        
        print("\n📋 SUMMARY OF CAPABILITIES:")
        capabilities = [
            "✅ Base test classes with dependency injection support",
            "✅ Intelligent mock service factory with realistic behavior patterns",
            "✅ Integration testing with real/mock service combinations",
            "✅ Performance testing with comprehensive monitoring",
            "✅ TDD-focused testing patterns and validation",
            "✅ Automated test discovery and execution",
            "✅ Service fixtures for comprehensive test data generation",
            "✅ Comprehensive test reporting and metrics"
        ]
        
        for capability in capabilities:
            print(f"  {capability}")
        
        print("\n🏆 TD.4 - TESTING INFRASTRUCTURE COMPLETE")
        print("The testing framework provides:")
        print("  • Complete dependency injection integration")
        print("  • Realistic mock service generation")
        print("  • Multiple testing patterns (Unit, Integration, Performance, TDD)")
        print("  • Automated test discovery and execution")
        print("  • Comprehensive reporting and monitoring")
        print("  • Production-ready testing infrastructure")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))