#!/usr/bin/env python3
"""
Debug monitoring issues
"""

import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.monitoring.system_monitor import KGASSystemMonitor, MetricType

def test_metrics_collection_debug():
    """Debug metrics collection"""
    print("Testing metrics collection...")
    
    try:
        monitor = KGASSystemMonitor()
        
        # Test manual metric recording
        monitor._record_metric(
            "test_counter",
            42.0,
            MetricType.COUNTER,
            {"component": "test", "environment": "testing"},
            "Test counter metric"
        )
        
        print(f"Metrics after recording: {len(monitor.metrics)}")
        if monitor.metrics:
            metric = monitor.metrics[0]
            print(f"First metric: name={metric.name}, value={metric.value}, type={metric.metric_type}")
        
        # Test metrics retrieval
        all_metrics = monitor.get_metrics()
        print(f"Retrieved metrics: {len(all_metrics)}")
        
        # Test filtering
        counter_metrics = monitor.get_metrics("test_counter")
        print(f"Counter metrics: {len(counter_metrics)}")
        
        if counter_metrics:
            print(f"Counter metric data: {counter_metrics[0]}")
        
        return True
        
    except Exception as e:
        print(f"Metrics collection debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitoring_thread_debug():
    """Debug monitoring thread"""
    print("Testing monitoring thread...")
    
    try:
        config = {'check_interval': 1}
        monitor = KGASSystemMonitor(config)
        
        # Register a test component
        def test_component():
            print("Health check called")
            return {'status': 'healthy', 'message': 'Test component OK'}
        
        monitor.register_component("thread_test_component", test_component)
        print("Component registered")
        
        # Start monitoring
        print("Starting monitoring...")
        monitor.start_monitoring()
        
        # Wait for monitoring cycles
        print("Waiting for monitoring cycles...")
        time.sleep(3.5)
        
        print(f"Health checks performed: {len(monitor.health_checks)}")
        print(f"Metrics collected: {len(monitor.metrics)}")
        
        # Stop monitoring
        print("Stopping monitoring...")
        monitor.stop_monitoring()
        
        return True
        
    except Exception as e:
        print(f"Monitoring thread debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== DEBUGGING MONITORING ISSUES ===")
    
    print("\n1. Testing metrics collection:")
    test_metrics_collection_debug()
    
    print("\n2. Testing monitoring thread:")
    test_monitoring_thread_debug()
    
    print("\n=== DEBUG COMPLETE ===")