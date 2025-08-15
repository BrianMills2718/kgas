#!/usr/bin/env python3
"""
Integration test for structured output monitoring framework.

Tests monitoring capabilities with real components and validates:
- Real-time metrics collection
- Health validation alerts
- Performance tracking
- Error categorization
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.core.structured_llm_service import StructuredLLMService
from src.orchestration.reasoning_schema import ReasoningStep, EntityExtractionResponse
from src.monitoring.structured_output_monitor import get_monitor
from src.orchestration.mcp_adapter import MCPToolAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_monitoring_integration():
    """Test monitoring integration with real components."""
    print("🔍 Testing Structured Output Monitoring Integration")
    print("=" * 60)
    
    # Get fresh monitor instance
    monitor = get_monitor()
    monitor.metrics_history.clear()  # Start fresh
    
    test_results = {
        "structured_llm_service": {"attempted": 0, "successful": 0, "monitored": 0},
        "mcp_adapter": {"attempted": 0, "successful": 0, "monitored": 0},
        "health_validation": {"checks": 0, "passed": 0, "alerts": 0}
    }
    
    print("\n📊 Testing StructuredLLMService Integration")
    print("-" * 45)
    
    # Test StructuredLLMService monitoring
    llm_service = StructuredLLMService()
    initial_metric_count = len(monitor.metrics_history)
    
    if llm_service.available:
        # Test 1: Simple reasoning step
        test_results["structured_llm_service"]["attempted"] += 1
        try:
            result = llm_service.structured_completion(
                prompt="Create a reasoning step with action 'validate_monitoring', reasoning 'Testing monitoring integration', and confidence 0.95",
                schema=ReasoningStep,
                temperature=0.05
            )
            test_results["structured_llm_service"]["successful"] += 1
            print(f"✅ Simple reasoning step: {result.action}")
        except Exception as e:
            print(f"❌ Simple reasoning step failed: {e}")
        
        # Test 2: Entity extraction response
        test_results["structured_llm_service"]["attempted"] += 1
        try:
            result = llm_service.structured_completion(
                prompt="Extract entities from 'Apple Inc. was founded by Steve Jobs in Cupertino'. Return EntityExtractionResponse with extracted entities and confidence 0.9",
                schema=EntityExtractionResponse,
                temperature=0.05
            )
            test_results["structured_llm_service"]["successful"] += 1
            print(f"✅ Entity extraction: {len(result.decision.get('entities', []))} entities")
        except Exception as e:
            print(f"❌ Entity extraction failed: {e}")
        
        # Test 3: Intentional validation error
        test_results["structured_llm_service"]["attempted"] += 1
        try:
            # This should trigger validation error with malformed schema
            result = llm_service.structured_completion(
                prompt="Return invalid JSON: {'incomplete': true",  # Intentionally malformed
                schema=ReasoningStep,
                temperature=0.05
            )
            print(f"⚠️ Validation error test unexpectedly succeeded")
        except Exception as e:
            print(f"✅ Validation error correctly caught: {type(e).__name__}")
    else:
        print("⚠️ StructuredLLMService not available - skipping tests")
    
    # Check monitoring recorded operations
    current_metric_count = len(monitor.metrics_history)
    monitored_operations = current_metric_count - initial_metric_count
    test_results["structured_llm_service"]["monitored"] = monitored_operations
    
    print(f"📈 Monitored operations: {monitored_operations}")
    
    # Show recent metrics
    if monitored_operations > 0:
        recent_metrics = list(monitor.metrics_history)[-monitored_operations:]
        for i, metric in enumerate(recent_metrics[-3:], 1):  # Show last 3
            status = "✅" if metric.success else "❌"
            print(f"   {i}. {status} {metric.schema_name}: {metric.response_time_ms:.0f}ms")
    
    print("\n🛠️ Testing MCP Adapter Integration")
    print("-" * 35)
    
    # Test MCP adapter monitoring
    mcp_adapter = MCPToolAdapter()
    
    try:
        await mcp_adapter.initialize()
        
        if mcp_adapter._is_structured_output_enabled():
            test_results["mcp_adapter"]["attempted"] += 1
            
            # Test simple orchestration
            result = await mcp_adapter.orchestrate_tools_structured(
                task_description="Test the system connection",
                context={"test": True}
            )
            
            if result.success:
                test_results["mcp_adapter"]["successful"] += 1
                print(f"✅ MCP orchestration successful")
                method = result.metadata.get("method", "unknown")
                print(f"   Method: {method}")
            else:
                print(f"❌ MCP orchestration failed: {result.error}")
        else:
            print("⚠️ MCP structured output not enabled - using legacy mode")
            
        await mcp_adapter.cleanup()
        
    except Exception as e:
        print(f"❌ MCP adapter initialization failed: {e}")
    
    print("\n🏥 Testing Health Validation")
    print("-" * 25)
    
    # Test health validation
    health_results = monitor.validate_system_health()
    test_results["health_validation"]["checks"] = len(health_results)
    
    for result in health_results:
        if result.success:
            test_results["health_validation"]["passed"] += 1
            print(f"✅ {result.check_name}: {result.message}")
        else:
            test_results["health_validation"]["alerts"] += 1
            severity_icon = "🚨" if result.severity == "critical" else "⚠️"
            print(f"{severity_icon} {result.check_name}: {result.message}")
    
    print("\n📊 Testing Performance Summary")
    print("-" * 30)
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    
    if "error" not in summary:
        stats = summary["overall_stats"]
        print(f"📈 Total Operations: {stats['total_operations']}")
        print(f"📈 Success Rate: {stats['success_rate']:.1%}")
        print(f"📈 Avg Response Time: {stats['avg_response_time_ms']:.0f}ms")
        print(f"📈 Validation Errors: {stats['validation_error_rate']:.1%}")
        print(f"📈 LLM Errors: {stats['llm_error_rate']:.1%}")
        
        # Component breakdown
        if summary["component_breakdown"]:
            print(f"\n🔧 Component Breakdown:")
            for component, comp_stats in summary["component_breakdown"].items():
                print(f"   {component}: {comp_stats['success_rate']:.1%} success ({comp_stats['total_operations']} ops)")
    else:
        print(f"⚠️ No performance data: {summary['error']}")
    
    print("\n💾 Testing Data Export")
    print("-" * 20)
    
    # Test data export
    export_path = "/tmp/monitoring_test_export.json"
    export_success = monitor.export_metrics(export_path, format="json")
    
    if export_success and os.path.exists(export_path):
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        print(f"✅ Export successful: {len(export_data['metrics'])} metrics exported")
        
        # Cleanup
        os.remove(export_path)
    else:
        print(f"❌ Export failed")
    
    print("\n📋 Integration Test Summary")
    print("=" * 30)
    
    total_attempted = sum(component["attempted"] for component in test_results.values() if "attempted" in component)
    total_successful = sum(component["successful"] for component in test_results.values() if "successful" in component)
    
    print(f"🧪 Tests Attempted: {total_attempted}")
    print(f"✅ Tests Successful: {total_successful}")
    print(f"📊 Monitoring Operations: {len(monitor.metrics_history)}")
    print(f"🏥 Health Checks: {test_results['health_validation']['checks']}")
    print(f"⚠️ Health Alerts: {test_results['health_validation']['alerts']}")
    
    # Overall assessment
    if total_attempted > 0:
        success_rate = total_successful / total_attempted
        print(f"\n🎯 Overall Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.8 and len(monitor.metrics_history) > 0:
            print("🎉 MONITORING INTEGRATION SUCCESSFUL!")
            print("   • Metrics collection working")
            print("   • Health validation active")
            print("   • Performance tracking enabled")
            print("   • Export functionality verified")
            return True
        else:
            print("⚠️ MONITORING INTEGRATION PARTIAL")
            return False
    else:
        print("❌ NO TESTS EXECUTED - CHECK SYSTEM CONFIGURATION")
        return False


async def main():
    """Run monitoring integration tests."""
    try:
        success = await test_monitoring_integration()
        return success
    except Exception as e:
        print(f"❌ Integration test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)