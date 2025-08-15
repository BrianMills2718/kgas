#!/usr/bin/env python3
"""
KGAS System Monitoring Test - Phase 9.2

Tests comprehensive system monitoring capabilities:
- Health monitoring of components
- Performance metrics collection
- Alert generation and management
- Monitoring reports and dashboard data

NO MOCKS - Tests real monitoring functionality with actual system metrics.
"""

import os
import sys
import time
import tempfile
import json
import threading
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.monitoring.system_monitor import (
    KGASSystemMonitor, HealthStatus, MetricType, HealthCheck, Metric,
    get_system_monitor, start_system_monitoring
)


class SystemMonitoringTests:
    """Comprehensive test suite for system monitoring"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = Path(tempfile.mkdtemp())
        print(f"Test temp directory: {self.temp_dir}")
    
    def run_all_tests(self) -> bool:
        """Run all system monitoring tests"""
        print("=" * 70)
        print("KGAS SYSTEM MONITORING COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        test_methods = [
            self.test_monitor_initialization,
            self.test_component_registration,
            self.test_health_checks,
            self.test_metrics_collection,
            self.test_alert_generation,
            self.test_system_metrics,
            self.test_monitoring_thread,
            self.test_performance_tracking,
            self.test_monitoring_reports,
            self.test_dashboard_data,
            self.test_concurrent_monitoring,
            self.test_monitoring_persistence
        ]
        
        for test_method in test_methods:
            try:
                print(f"\nRunning {test_method.__name__}...")
                result = test_method()
                self.test_results.append({
                    "test": test_method.__name__,
                    "success": result,
                    "timestamp": datetime.now().isoformat()
                })
                status = "✅" if result else "❌"
                print(f"{status} {test_method.__name__}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                print(f"❌ {test_method.__name__}: FAILED with exception: {e}")
                self.test_results.append({
                    "test": test_method.__name__,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Generate test report
        self.generate_test_report()
        
        # Return overall success
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"\n" + "=" * 70)
        print(f"TEST SUMMARY: {passed_tests}/{total_tests} tests passed")
        print("=" * 70)
        
        return passed_tests == total_tests
    
    def test_monitor_initialization(self) -> bool:
        """Test system monitor initialization"""
        try:
            # Test default initialization
            monitor = KGASSystemMonitor()
            assert monitor.monitoring_enabled == True
            assert monitor.check_interval == 30
            assert monitor.metric_retention_hours == 24
            
            # Test custom configuration
            config = {
                'monitoring_enabled': True,
                'check_interval': 10,
                'metric_retention_hours': 48,
                'alert_threshold_cpu': 75.0,
                'output_dir': str(self.temp_dir / 'monitoring_test')
            }
            
            custom_monitor = KGASSystemMonitor(config)
            assert custom_monitor.check_interval == 10
            assert custom_monitor.metric_retention_hours == 48
            assert custom_monitor.alert_threshold_cpu == 75.0
            
            # Test global monitor
            global_monitor = get_system_monitor()
            assert global_monitor is not None
            
            # Test that subsequent calls return same instance
            same_monitor = get_system_monitor()
            assert global_monitor is same_monitor
            
            return True
            
        except Exception as e:
            print(f"Monitor initialization test failed: {e}")
            return False
    
    def test_component_registration(self) -> bool:
        """Test component registration for monitoring"""
        try:
            monitor = KGASSystemMonitor()
            
            # Test component registration
            def test_health_check():
                return {
                    'status': 'healthy',
                    'message': 'Component is working',
                    'metrics': {'response_time': 0.1}
                }
            
            monitor.register_component(
                "test_component",
                test_health_check,
                "Test component for monitoring"
            )
            
            assert "test_component" in monitor.components
            component_info = monitor.components["test_component"]
            assert component_info['description'] == "Test component for monitoring"
            assert component_info['check_count'] == 0
            assert component_info['failure_count'] == 0
            
            # Test multiple component registration
            def another_health_check():
                return True  # Simple boolean result
            
            monitor.register_component("another_component", another_health_check)
            assert len(monitor.components) == 2
            
            return True
            
        except Exception as e:
            print(f"Component registration test failed: {e}")
            return False
    
    def test_health_checks(self) -> bool:
        """Test health check functionality"""
        try:
            monitor = KGASSystemMonitor()
            
            # Register healthy component
            def healthy_component():
                return {
                    'status': 'healthy',
                    'message': 'All systems operational',
                    'metrics': {'cpu_usage': 25.5, 'memory_usage': 60.0}
                }
            
            # Register unhealthy component
            def unhealthy_component():
                return {
                    'status': 'unhealthy',
                    'message': 'Service unavailable',
                    'error_details': 'Connection timeout after 5 seconds'
                }
            
            # Register component that throws exception
            def failing_component():
                raise RuntimeError("Component crashed")
            
            monitor.register_component("healthy_service", healthy_component)
            monitor.register_component("unhealthy_service", unhealthy_component)
            monitor.register_component("failing_service", failing_component)
            
            # Perform health checks manually
            monitor._perform_health_checks()
            
            # Verify health checks were recorded
            assert len(monitor.health_checks) >= 3
            
            # Find health check results
            healthy_check = None
            unhealthy_check = None
            failing_check = None
            
            for hc in monitor.health_checks:
                if hc.component == "healthy_service":
                    healthy_check = hc
                elif hc.component == "unhealthy_service":
                    unhealthy_check = hc
                elif hc.component == "failing_service":
                    failing_check = hc
            
            # Verify healthy component
            assert healthy_check is not None
            assert healthy_check.status == HealthStatus.HEALTHY
            assert "All systems operational" in healthy_check.message
            assert healthy_check.metrics['cpu_usage'] == 25.5
            
            # Verify unhealthy component
            assert unhealthy_check is not None
            assert unhealthy_check.status == HealthStatus.UNHEALTHY
            assert "Service unavailable" in unhealthy_check.message
            assert "Connection timeout" in unhealthy_check.error_details
            
            # Verify failing component
            assert failing_check is not None
            assert failing_check.status == HealthStatus.CRITICAL
            assert "Component crashed" in failing_check.error_details
            
            # Verify component statistics were updated
            healthy_info = monitor.components["healthy_service"]
            assert healthy_info['check_count'] == 1
            assert healthy_info['failure_count'] == 0
            assert healthy_info['last_status'] == HealthStatus.HEALTHY
            
            unhealthy_info = monitor.components["unhealthy_service"]
            assert unhealthy_info['failure_count'] == 1
            assert unhealthy_info['last_status'] == HealthStatus.UNHEALTHY
            
            return True
            
        except Exception as e:
            print(f"Health checks test failed: {e}")
            return False
    
    def test_metrics_collection(self) -> bool:
        """Test metrics collection functionality"""
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
            
            monitor._record_metric(
                "test_gauge",
                85.5,
                MetricType.GAUGE,
                {"component": "test"},
                "Test gauge metric"
            )
            
            monitor._record_metric(
                "test_timer",
                1.234,
                MetricType.TIMER,
                {"operation": "test_operation"}
            )
            
            # Verify metrics were recorded
            assert len(monitor.metrics) == 3
            
            # Find specific metrics
            counter_metric = next((m for m in monitor.metrics if m.name == "test_counter"), None)
            gauge_metric = next((m for m in monitor.metrics if m.name == "test_gauge"), None)
            timer_metric = next((m for m in monitor.metrics if m.name == "test_timer"), None)
            
            assert counter_metric is not None
            assert counter_metric.value == 42.0
            assert counter_metric.metric_type == MetricType.COUNTER
            assert counter_metric.tags["component"] == "test"
            assert counter_metric.description == "Test counter metric"
            
            assert gauge_metric is not None
            assert gauge_metric.value == 85.5
            assert gauge_metric.metric_type == MetricType.GAUGE
            
            assert timer_metric is not None
            assert timer_metric.value == 1.234
            assert timer_metric.metric_type == MetricType.TIMER
            assert timer_metric.tags["operation"] == "test_operation"
            
            # Test metrics retrieval
            all_metrics = monitor.get_metrics()
            assert len(all_metrics) == 3
            
            # Test filtering by metric name
            counter_metrics = monitor.get_metrics("test_counter")
            assert len(counter_metrics) == 1
            assert counter_metrics[0]["name"] == "test_counter"
            
            # Test filtering by time range
            recent_metrics = monitor.get_metrics(time_range_hours=1)
            assert len(recent_metrics) == 3  # All should be recent
            
            old_metrics = monitor.get_metrics(time_range_hours=0)  # No metrics in past 0 hours
            assert len(old_metrics) == 0
            
            return True
            
        except Exception as e:
            print(f"Metrics collection test failed: {e}")
            return False
    
    def test_alert_generation(self) -> bool:
        """Test alert generation and management"""
        try:
            # Use lower thresholds for testing
            config = {
                'alert_threshold_cpu': 50.0,
                'alert_threshold_memory': 60.0,
                'alert_threshold_disk': 70.0
            }
            
            monitor = KGASSystemMonitor(config)
            
            # Test manual alert generation
            monitor._generate_alert(
                "test_alert",
                "This is a test alert",
                {"severity": "warning", "component": "test"}
            )
            
            # Verify alert was generated
            assert len(monitor.alerts) == 1
            alert = monitor.alerts[0]
            assert alert["type"] == "test_alert"
            assert alert["message"] == "This is a test alert"
            assert alert["details"]["component"] == "test"
            
            # Test alert condition checking with high CPU
            monitor._record_metric("cpu_percent", 75.0, MetricType.GAUGE, {"type": "system"})
            monitor._check_alert_conditions()
            
            # Should have generated CPU alert
            cpu_alerts = [a for a in monitor.alerts if a["type"] == "high_cpu_usage"]
            assert len(cpu_alerts) >= 1
            
            # Test alert condition checking with high memory
            monitor._record_metric("memory_percent", 85.0, MetricType.GAUGE, {"type": "system"})
            monitor._check_alert_conditions()
            
            # Should have generated memory alert
            memory_alerts = [a for a in monitor.alerts if a["type"] == "high_memory_usage"]
            assert len(memory_alerts) >= 1
            
            # Test getting alerts
            all_alerts = monitor.get_alerts()
            assert len(all_alerts) >= 3
            
            active_alerts = monitor.get_alerts(active_only=True)
            assert len(active_alerts) >= 3  # All should be recent
            
            return True
            
        except Exception as e:
            print(f"Alert generation test failed: {e}")
            return False
    
    def test_system_metrics(self) -> bool:
        """Test system metrics collection"""
        try:
            monitor = KGASSystemMonitor()
            
            # Collect system metrics
            monitor._collect_system_metrics()
            
            # Verify system metrics were collected
            expected_metrics = [
                "cpu_percent", "memory_percent", "memory_used_mb", "memory_available_mb",
                "disk_percent", "disk_used_gb", "disk_free_gb", "process_count",
                "current_process_cpu", "current_process_memory", "current_process_threads"
            ]
            
            collected_metric_names = set([m.name for m in monitor.metrics])
            
            for expected_metric in expected_metrics:
                assert expected_metric in collected_metric_names, f"Missing metric: {expected_metric}"
            
            # Verify metric values are reasonable
            cpu_metric = monitor._get_latest_metric("cpu_percent")
            assert cpu_metric is not None
            assert 0 <= cpu_metric.value <= 100
            
            memory_metric = monitor._get_latest_metric("memory_percent")
            assert memory_metric is not None
            assert 0 <= memory_metric.value <= 100
            
            disk_metric = monitor._get_latest_metric("disk_percent")
            assert disk_metric is not None
            assert 0 <= disk_metric.value <= 100
            
            process_count = monitor._get_latest_metric("process_count")
            assert process_count is not None
            assert process_count.value > 0  # Should have at least some processes
            
            return True
            
        except Exception as e:
            print(f"System metrics test failed: {e}")
            return False
    
    def test_monitoring_thread(self) -> bool:
        """Test continuous monitoring thread"""
        try:
            # Use short interval for testing
            config = {'check_interval': 1}  # 1 second interval
            monitor = KGASSystemMonitor(config)
            
            # Register a test component
            def test_component():
                return {'status': 'healthy', 'message': 'Test component OK'}
            
            monitor.register_component("thread_test_component", test_component)
            
            # Start monitoring
            monitor.start_monitoring()
            
            # Wait for a few monitoring cycles
            time.sleep(3.5)  # Should complete 3 cycles
            
            # Stop monitoring
            monitor.stop_monitoring()
            
            # Verify monitoring occurred
            assert len(monitor.health_checks) >= 3  # At least 3 health checks
            assert len(monitor.metrics) > 0  # Should have collected metrics
            
            # Verify component was checked multiple times
            component_checks = [hc for hc in monitor.health_checks if hc.component == "thread_test_component"]
            assert len(component_checks) >= 3
            
            # Verify system metrics were collected
            cpu_metrics = [m for m in monitor.metrics if m.name == "cpu_percent"]
            assert len(cpu_metrics) >= 3
            
            return True
            
        except Exception as e:
            print(f"Monitoring thread test failed: {e}")
            return False
    
    def test_performance_tracking(self) -> bool:
        """Test performance tracking functionality"""
        try:
            monitor = KGASSystemMonitor()
            
            # Test document processing tracking
            monitor.record_document_processed(processing_time=1.5, entities_count=25)
            monitor.record_document_processed(processing_time=2.0, entities_count=30)
            monitor.record_document_processed(processing_time=1.0, entities_count=20)
            
            assert monitor.documents_processed == 3
            assert monitor.entities_extracted == 75
            assert 1.0 <= monitor.average_processing_time <= 2.0
            
            # Test database operation tracking
            monitor.record_database_operation("insert", True, 0.1)
            monitor.record_database_operation("select", True, 0.05)
            monitor.record_database_operation("update", False, 0.2)
            
            assert monitor.database_operations == 3
            
            # Test error tracking
            monitor.record_error("validation_error", {"severity": "warning"})
            monitor.record_error("connection_error", {"severity": "error"})
            
            assert monitor.errors_count == 2
            
            # Verify metrics were recorded
            doc_metrics = [m for m in monitor.metrics if m.name == "documents_processed"]
            assert len(doc_metrics) == 3
            
            entity_metrics = [m for m in monitor.metrics if m.name == "entities_extracted"]
            assert len(entity_metrics) == 3
            
            db_metrics = [m for m in monitor.metrics if m.name == "database_operations"]
            assert len(db_metrics) == 3
            
            error_metrics = [m for m in monitor.metrics if m.name == "errors_count"]
            assert len(error_metrics) == 2
            
            return True
            
        except Exception as e:
            print(f"Performance tracking test failed: {e}")
            return False
    
    def test_monitoring_reports(self) -> bool:
        """Test monitoring report generation"""
        try:
            config = {'output_dir': str(self.temp_dir / 'monitoring_reports')}
            monitor = KGASSystemMonitor(config)
            
            # Add some test data
            monitor.record_document_processed(1.5, 20)
            monitor.record_database_operation("insert", True, 0.1)
            monitor.record_error("test_error", {"severity": "warning"})
            
            def test_component():
                return {'status': 'healthy', 'message': 'Test OK'}
            
            monitor.register_component("report_test_component", test_component)
            monitor._perform_health_checks()
            
            # Generate report
            report_file = monitor.generate_monitoring_report("test_monitoring_report")
            
            assert report_file.exists()
            assert report_file.suffix == ".json"
            
            # Read and validate report
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            required_sections = [
                "report_name", "generated_at", "monitoring_period",
                "health_status", "metrics_summary", "alerts_summary",
                "component_health", "system_performance"
            ]
            
            for section in required_sections:
                assert section in report_data, f"Missing report section: {section}"
            
            # Validate specific data
            assert report_data["health_status"]["metrics_summary"]["documents_processed"] == 1
            assert report_data["health_status"]["metrics_summary"]["entities_extracted"] == 20
            assert report_data["health_status"]["metrics_summary"]["errors_count"] == 1
            
            assert "report_test_component" in report_data["component_health"]
            component_health = report_data["component_health"]["report_test_component"]
            assert component_health["status"] == "healthy"
            assert component_health["success_rate"] == 1.0
            
            return True
            
        except Exception as e:
            print(f"Monitoring reports test failed: {e}")
            return False
    
    def test_dashboard_data(self) -> bool:
        """Test dashboard data generation"""
        try:
            monitor = KGASSystemMonitor()
            
            # Add test data for dashboard
            for i in range(5):
                monitor._record_metric("cpu_percent", 20.0 + i * 5, MetricType.GAUGE, {"type": "system"})
                monitor._record_metric("memory_percent", 50.0 + i * 2, MetricType.GAUGE, {"type": "system"})
                monitor._record_metric("processing_time", 1.0 + i * 0.1, MetricType.TIMER, {"component": "processor"})
            
            monitor.record_document_processed(1.5, 25)
            monitor.record_error("dashboard_test_error", {"severity": "warning"})
            
            # Generate alert for dashboard
            monitor._generate_alert("dashboard_test_alert", "Test alert for dashboard", {"test": True})
            
            # Get dashboard data
            dashboard_data = monitor.get_dashboard_data()
            
            # Validate dashboard structure
            required_sections = ["health_status", "charts", "alerts", "summary"]
            for section in required_sections:
                assert section in dashboard_data, f"Missing dashboard section: {section}"
            
            # Validate charts data
            charts = dashboard_data["charts"]
            assert "cpu_usage" in charts
            assert "memory_usage" in charts
            assert "processing_times" in charts
            
            # Verify chart data points
            cpu_chart = charts["cpu_usage"]
            assert len(cpu_chart) > 0
            assert all("timestamp" in point and "value" in point for point in cpu_chart)
            
            memory_chart = charts["memory_usage"]
            assert len(memory_chart) > 0
            
            processing_chart = charts["processing_times"]
            assert len(processing_chart) > 0
            
            # Validate summary data
            summary = dashboard_data["summary"]
            assert summary["total_documents"] == 1
            assert summary["total_errors"] == 1
            assert summary["uptime_hours"] > 0
            
            # Validate alerts
            alerts = dashboard_data["alerts"]
            assert len(alerts) >= 1  # Should include our test alert
            
            return True
            
        except Exception as e:
            print(f"Dashboard data test failed: {e}")
            return False
    
    def test_concurrent_monitoring(self) -> bool:
        """Test monitoring under concurrent access"""
        try:
            monitor = KGASSystemMonitor()
            
            # Function to simulate concurrent activity
            def simulate_activity(thread_id: int):
                for i in range(10):
                    monitor.record_document_processed(1.0 + thread_id * 0.1, 10 + i)
                    monitor.record_database_operation(f"op_{thread_id}", True, 0.1)
                    if i % 3 == 0:
                        monitor.record_error(f"error_{thread_id}", {"severity": "warning"})
                    time.sleep(0.01)
            
            # Start multiple threads
            threads = []
            for thread_id in range(3):
                thread = threading.Thread(target=simulate_activity, args=(thread_id,))
                threads.append(thread)
            
            # Start all threads
            for thread in threads:
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify all operations were recorded correctly
            assert monitor.documents_processed == 30  # 3 threads * 10 operations
            assert monitor.database_operations == 30
            assert monitor.errors_count == 12  # 3 threads * 4 errors each (every 3rd iteration)
            
            # Verify metrics were recorded
            doc_metrics = [m for m in monitor.metrics if m.name == "documents_processed"]
            assert len(doc_metrics) == 30
            
            return True
            
        except Exception as e:
            print(f"Concurrent monitoring test failed: {e}")
            return False
    
    def test_monitoring_persistence(self) -> bool:
        """Test monitoring data persistence and cleanup"""
        try:
            config = {'metric_retention_hours': 24}
            monitor = KGASSystemMonitor(config)
            
            # Add metrics with different timestamps
            current_time = datetime.now()
            
            # Recent metric (should be kept)
            recent_metric = Metric(
                name="recent_test",
                value=42.0,
                metric_type=MetricType.COUNTER,
                timestamp=current_time,
                tags={"type": "test"}
            )
            monitor.metrics.append(recent_metric)
            
            # Old metric (should be cleaned up)
            old_metric = Metric(
                name="old_test",
                value=24.0,
                metric_type=MetricType.COUNTER,
                timestamp=current_time - timedelta(hours=25),  # Older than retention
                tags={"type": "test"}
            )
            monitor.metrics.append(old_metric)
            
            # Perform cleanup
            monitor._cleanup_old_metrics()
            
            # Verify old metric was removed, recent kept
            metric_names = [m.name for m in monitor.metrics]
            assert "recent_test" in metric_names
            assert "old_test" not in metric_names
            
            # Test health check cleanup
            recent_hc = HealthCheck(
                component="test_component",
                status=HealthStatus.HEALTHY,
                message="Recent check",
                timestamp=current_time,
                metrics={}
            )
            monitor.health_checks.append(recent_hc)
            
            old_hc = HealthCheck(
                component="test_component",
                status=HealthStatus.HEALTHY,
                message="Old check",
                timestamp=current_time - timedelta(hours=25),
                metrics={}
            )
            monitor.health_checks.append(old_hc)
            
            # Perform cleanup
            monitor._cleanup_old_data()
            
            # Verify old health check was removed
            hc_messages = [hc.message for hc in monitor.health_checks]
            assert "Recent check" in hc_messages
            assert "Old check" not in hc_messages
            
            return True
            
        except Exception as e:
            print(f"Monitoring persistence test failed: {e}")
            return False
    
    def generate_test_report(self) -> None:
        """Generate comprehensive test report"""
        report_file = self.temp_dir / "system_monitoring_test_report.json"
        
        report_data = {
            "test_suite": "KGAS System Monitoring Comprehensive Tests",
            "executed_at": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["success"]]),
            "failed_tests": len([r for r in self.test_results if not r["success"]]),
            "success_rate": len([r for r in self.test_results if r["success"]]) / len(self.test_results),
            "test_results": self.test_results,
            "temp_directory": str(self.temp_dir)
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📊 Test report generated: {report_file}")


def main():
    """Main test execution"""
    try:
        test_suite = SystemMonitoringTests()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 ALL SYSTEM MONITORING TESTS PASSED!")
            print("✅ Phase 9.2: System monitoring implementation complete")
            return 0
        else:
            print("\n❌ SOME SYSTEM MONITORING TESTS FAILED!")
            print("🔧 Review test results and fix failing components")
            return 1
            
    except Exception as e:
        print(f"\n💥 TEST SUITE EXECUTION FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())