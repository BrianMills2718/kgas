#!/usr/bin/env python3
"""
Test the Fail-Fast Monitoring System
Validates that monitoring correctly tracks fail-fast behaviors
"""

import time
import json
from pathlib import Path

# Add to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.monitoring.fail_fast_monitor import (
    FailFastMonitor, 
    record_service_call,
    record_fallback_violation,
    get_monitor
)

def test_monitoring_system():
    """Test the fail-fast monitoring system"""
    print("="*60)
    print("FAIL-FAST MONITORING SYSTEM TEST")
    print("="*60)
    
    # Create a monitor
    monitor = FailFastMonitor(
        metrics_dir="logs/test_metrics",
        alert_threshold=0.3,  # 30% failure rate triggers alert
        window_size=10
    )
    
    # Register an alert handler
    alerts_received = []
    def alert_handler(alert):
        alerts_received.append(alert)
        print(f"  Alert: {alert['type']} - {alert['message']}")
    
    monitor.register_alert_handler(alert_handler)
    
    print("\n1. Testing normal service calls...")
    # Simulate successful calls
    for i in range(5):
        monitor.record_call(
            service="gemini_api",
            operation="extract_entities",
            success=True
        )
    print("  ✅ 5 successful calls recorded")
    
    print("\n2. Testing fail-fast events...")
    # Simulate fail-fast events (no fallback)
    for i in range(3):
        monitor.record_call(
            service="gemini_api",
            operation="extract_entities",
            success=False,
            error=Exception("API key invalid"),
            context={"attempt": i+1}
        )
    print("  ✅ 3 fail-fast events recorded")
    
    print("\n3. Testing fallback violation detection...")
    # This should trigger a critical alert
    monitor.record_fallback_attempt(
        service="gemini_api",
        operation="extract_entities"
    )
    print("  ✅ Fallback violation recorded (should trigger alert)")
    
    print("\n4. Testing Neo4j failures...")
    # Simulate Neo4j connection failures
    for i in range(2):
        monitor.record_call(
            service="neo4j",
            operation="query",
            success=False,
            error=Exception("Connection refused")
        )
    print("  ✅ Neo4j failures recorded")
    
    print("\n5. Testing recovery tracking...")
    # Record a recovery
    monitor.record_recovery("gemini_api", recovery_time=5.2)
    monitor.record_recovery("neo4j", recovery_time=2.1)
    print("  ✅ Recovery times recorded")
    
    # Get metrics
    print("\n6. Getting metrics...")
    metrics = monitor.get_metrics()
    
    print("\n  Service Metrics:")
    for service, data in metrics['services'].items():
        print(f"    {service}:")
        print(f"      Total calls: {data['total_calls']}")
        print(f"      Failed calls: {data['failed_calls']}")
        print(f"      Fail-fast events: {data['fail_fast_events']}")
        print(f"      Failure rate: {data['failure_rate']:.1%}")
        if data['fallback_attempts'] > 0:
            print(f"      ⚠️ FALLBACK ATTEMPTS: {data['fallback_attempts']}")
    
    print("\n  Policy Violations:")
    violations = metrics['policy_violations']['fallback_attempts']
    if violations > 0:
        print(f"    ⚠️ Fallback attempts: {violations}")
    else:
        print(f"    ✅ No fallback attempts")
    
    print("\n  Alerts Triggered:")
    for alert in alerts_received:
        print(f"    {alert['severity']}: {alert['type']}")
    
    # Save metrics
    print("\n7. Saving metrics...")
    monitor.save_metrics()
    print("  ✅ Metrics saved to logs/test_metrics/")
    
    # Generate report
    print("\n8. Generating report...")
    report = monitor.generate_report()
    print("\n" + report)
    
    # Test the global convenience functions
    print("\n9. Testing global convenience functions...")
    record_service_call(
        service="test_service",
        operation="test_op",
        success=True
    )
    record_fallback_violation(
        service="test_service",
        operation="test_op"
    )
    print("  ✅ Global functions working")
    
    # Final validation
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    success_count = 0
    total_count = 6
    
    # Check metrics were recorded
    if metrics['services']['gemini_api']['total_calls'] == 8:
        print("✅ Service calls tracked correctly")
        success_count += 1
    else:
        print("❌ Service call tracking incorrect")
    
    # Check fail-fast events
    if metrics['services']['gemini_api']['fail_fast_events'] == 3:
        print("✅ Fail-fast events tracked correctly")
        success_count += 1
    else:
        print("❌ Fail-fast event tracking incorrect")
    
    # Check fallback violations
    if violations == 1:
        print("✅ Fallback violations detected")
        success_count += 1
    else:
        print("❌ Fallback violation detection failed")
    
    # Check alerts
    if len(alerts_received) > 0:
        print("✅ Alert system working")
        success_count += 1
    else:
        print("❌ No alerts triggered")
    
    # Check critical alert for fallback
    critical_alerts = [a for a in alerts_received if a['severity'] == 'CRITICAL']
    if len(critical_alerts) > 0:
        print("✅ Critical alert for fallback violation")
        success_count += 1
    else:
        print("❌ No critical alert for fallback violation")
    
    # Check metrics file exists
    metrics_files = list(Path("logs/test_metrics").glob("metrics_*.json"))
    if len(metrics_files) > 0:
        print("✅ Metrics saved to file")
        success_count += 1
    else:
        print("❌ Metrics file not created")
    
    print("\n" + "="*60)
    if success_count == total_count:
        print(f"🎉 ALL TESTS PASSED ({success_count}/{total_count})")
    else:
        print(f"⚠️ SOME TESTS FAILED ({success_count}/{total_count})")
    print("="*60)
    
    return success_count == total_count

if __name__ == "__main__":
    success = test_monitoring_system()
    exit(0 if success else 1)