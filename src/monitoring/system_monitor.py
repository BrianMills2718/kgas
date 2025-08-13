"""
KGAS System Monitor - Phase 9.2

Comprehensive system monitoring and health tracking for KGAS components.
Provides real-time metrics, health checks, and performance monitoring.
"""

import os
import time
import psutil
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Types of metrics tracked"""
    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"
    HISTOGRAM = "histogram"


@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    error_details: Optional[str] = None


@dataclass
class Metric:
    """System metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str]
    description: str = ""


@dataclass
class SystemStats:
    """System-wide statistics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_free_gb: float
    process_count: int
    thread_count: int
    network_io: Dict[str, int]
    timestamp: datetime


class KGASSystemMonitor:
    """
    Comprehensive system monitor for KGAS infrastructure.
    
    Features:
    - Real-time health monitoring of all components
    - Performance metrics collection and analysis
    - System resource monitoring
    - Alert generation for critical conditions
    - Historical data tracking and reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monitoring state
        self.components: Dict[str, Dict[str, Any]] = {}
        self.metrics: List[Metric] = []
        self.health_checks: List[HealthCheck] = []
        self.alerts: List[Dict[str, Any]] = []
        
        # Configuration
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.check_interval = self.config.get('check_interval', 30)  # seconds
        self.metric_retention_hours = self.config.get('metric_retention_hours', 24)
        self.health_check_timeout = self.config.get('health_check_timeout', 10)
        self.alert_threshold_cpu = self.config.get('alert_threshold_cpu', 80.0)
        self.alert_threshold_memory = self.config.get('alert_threshold_memory', 85.0)
        self.alert_threshold_disk = self.config.get('alert_threshold_disk', 90.0)
        
        # Monitoring thread
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.RLock()
        
        # Performance tracking
        self.documents_processed = 0
        self.entities_extracted = 0
        self.database_operations = 0
        self.errors_count = 0
        self.average_processing_time = 0.0
        self.start_time = datetime.now()
        
        # Output directory
        self.output_dir = Path(self.config.get('output_dir', 'monitoring_output'))
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger.info("System monitor initialized")
    
    def start_monitoring(self) -> None:
        """Start continuous system monitoring"""
        if not self.monitoring_enabled:
            self.logger.info("Monitoring is disabled")
            return
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("Monitoring thread already running")
            return
        
        self._stop_monitoring.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="KGASSystemMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        self._stop_monitoring.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("System monitoring stopped")
    
    def register_component(self, name: str, health_check_func: Callable[[], Dict[str, Any]], 
                          description: str = "") -> None:
        """Register a component for monitoring"""
        with self._lock:
            self.components[name] = {
                'health_check_func': health_check_func,
                'description': description,
                'last_check': None,
                'last_status': HealthStatus.UNKNOWN,
                'check_count': 0,
                'failure_count': 0
            }
        self.logger.info(f"Registered component for monitoring: {name}")
    
    def record_document_processed(self, processing_time: float, entities_count: int) -> None:
        """Record document processing metrics"""
        with self._lock:
            self.documents_processed += 1
            self.entities_extracted += entities_count
            
            # Update average processing time
            if self.documents_processed == 1:
                self.average_processing_time = processing_time
            else:
                self.average_processing_time = (
                    (self.average_processing_time * (self.documents_processed - 1) + processing_time) / 
                    self.documents_processed
                )
            
            # Record metrics
            self._record_metric(
                "documents_processed",
                self.documents_processed,
                MetricType.COUNTER,
                {"component": "document_processor"}
            )
            
            self._record_metric(
                "entities_extracted",
                self.entities_extracted,
                MetricType.COUNTER,
                {"component": "entity_extractor"}
            )
            
            self._record_metric(
                "processing_time",
                processing_time,
                MetricType.TIMER,
                {"component": "document_processor"}
            )
    
    def record_database_operation(self, operation_type: str, success: bool, duration: float) -> None:
        """Record database operation metrics"""
        with self._lock:
            self.database_operations += 1
            
            status = "success" if success else "failure"
            self._record_metric(
                "database_operations",
                1,
                MetricType.COUNTER,
                {"operation": operation_type, "status": status}
            )
            
            self._record_metric(
                "database_operation_duration",
                duration,
                MetricType.TIMER,
                {"operation": operation_type}
            )
    
    def record_error(self, error_type: str, error_details: Dict[str, Any]) -> None:
        """Record error occurrence"""
        with self._lock:
            self.errors_count += 1
            
            self._record_metric(
                "errors_count",
                1,
                MetricType.COUNTER,
                {"error_type": error_type}
            )
            
            # Generate alert for critical errors
            if error_details.get('severity') in ['critical', 'fatal']:
                self._generate_alert(
                    "critical_error",
                    f"Critical error occurred: {error_type}",
                    {"error_details": error_details}
                )
    
    def _record_metric(self, name: str, value: float, metric_type: MetricType, 
                      tags: Dict[str, str], description: str = "") -> None:
        """Record a metric data point"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags,
            description=description
        )
        
        self.metrics.append(metric)
        
        # Clean up old metrics
        self._cleanup_old_metrics()
    
    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics beyond retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                # Perform system health checks
                self._perform_health_checks()
                
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check alert conditions
                self._check_alert_conditions()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Wait for next check
                self._stop_monitoring.wait(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(5)  # Brief pause before retrying
    
    def _perform_health_checks(self) -> None:
        """Perform health checks on all registered components"""
        for component_name, component_info in self.components.items():
            try:
                health_check_func = component_info['health_check_func']
                
                start_time = time.time()
                result = health_check_func()
                check_duration = time.time() - start_time
                
                # Determine health status
                if isinstance(result, dict):
                    status = HealthStatus(result.get('status', 'unknown'))
                    message = result.get('message', 'No message')
                    metrics = result.get('metrics', {})
                    error_details = result.get('error_details')
                else:
                    # Assume boolean result
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "Health check passed" if result else "Health check failed"
                    metrics = {}
                    error_details = None
                
                # Record health check
                health_check = HealthCheck(
                    component=component_name,
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    metrics=metrics,
                    error_details=error_details
                )
                
                with self._lock:
                    self.health_checks.append(health_check)
                    
                    # Update component info
                    component_info['last_check'] = datetime.now()
                    component_info['last_status'] = status
                    component_info['check_count'] += 1
                    
                    if status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                        component_info['failure_count'] += 1
                        
                        # Generate alert for unhealthy components
                        self._generate_alert(
                            "component_unhealthy",
                            f"Component {component_name} is {status.value}",
                            {
                                "component": component_name,
                                "status": status.value,
                                "message": message,
                                "error_details": error_details
                            }
                        )
                
                # Record health check metric
                self._record_metric(
                    "health_check_duration",
                    check_duration,
                    MetricType.TIMER,
                    {"component": component_name}
                )
                
                self._record_metric(
                    "health_check_status",
                    1 if status == HealthStatus.HEALTHY else 0,
                    MetricType.GAUGE,
                    {"component": component_name}
                )
                
            except Exception as e:
                self.logger.error(f"Health check failed for {component_name}: {e}")
                
                # Record failed health check
                health_check = HealthCheck(
                    component=component_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Health check exception: {str(e)}",
                    timestamp=datetime.now(),
                    metrics={},
                    error_details=str(e)
                )
                
                with self._lock:
                    self.health_checks.append(health_check)
                    component_info['last_status'] = HealthStatus.CRITICAL
                    component_info['failure_count'] += 1
    
    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1.0)
            self._record_metric("cpu_percent", cpu_percent, MetricType.GAUGE, {"type": "system"})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._record_metric("memory_percent", memory.percent, MetricType.GAUGE, {"type": "system"})
            self._record_metric("memory_used_mb", memory.used / (1024*1024), MetricType.GAUGE, {"type": "system"})
            self._record_metric("memory_available_mb", memory.available / (1024*1024), MetricType.GAUGE, {"type": "system"})
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._record_metric("disk_percent", disk_percent, MetricType.GAUGE, {"type": "system"})
            self._record_metric("disk_used_gb", disk.used / (1024**3), MetricType.GAUGE, {"type": "system"})
            self._record_metric("disk_free_gb", disk.free / (1024**3), MetricType.GAUGE, {"type": "system"})
            
            # Process metrics
            process_count = len(psutil.pids())
            self._record_metric("process_count", process_count, MetricType.GAUGE, {"type": "system"})
            
            # Current process metrics
            current_process = psutil.Process()
            self._record_metric("current_process_cpu", current_process.cpu_percent(), MetricType.GAUGE, {"type": "process"})
            self._record_metric("current_process_memory", current_process.memory_info().rss / (1024*1024), MetricType.GAUGE, {"type": "process"})
            self._record_metric("current_process_threads", current_process.num_threads(), MetricType.GAUGE, {"type": "process"})
            
            # Network I/O
            network = psutil.net_io_counters()
            if network:
                self._record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER, {"type": "network"})
                self._record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER, {"type": "network"})
            
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
    
    def _check_alert_conditions(self) -> None:
        """Check for alert conditions based on current metrics"""
        try:
            # Get latest system metrics
            latest_cpu = self._get_latest_metric("cpu_percent")
            latest_memory = self._get_latest_metric("memory_percent") 
            latest_disk = self._get_latest_metric("disk_percent")
            
            # CPU alert
            if latest_cpu and latest_cpu.value > self.alert_threshold_cpu:
                self._generate_alert(
                    "high_cpu_usage",
                    f"CPU usage is {latest_cpu.value:.1f}% (threshold: {self.alert_threshold_cpu}%)",
                    {"cpu_percent": latest_cpu.value, "threshold": self.alert_threshold_cpu}
                )
            
            # Memory alert
            if latest_memory and latest_memory.value > self.alert_threshold_memory:
                self._generate_alert(
                    "high_memory_usage",
                    f"Memory usage is {latest_memory.value:.1f}% (threshold: {self.alert_threshold_memory}%)",
                    {"memory_percent": latest_memory.value, "threshold": self.alert_threshold_memory}
                )
            
            # Disk alert
            if latest_disk and latest_disk.value > self.alert_threshold_disk:
                self._generate_alert(
                    "high_disk_usage",
                    f"Disk usage is {latest_disk.value:.1f}% (threshold: {self.alert_threshold_disk}%)",
                    {"disk_percent": latest_disk.value, "threshold": self.alert_threshold_disk}
                )
            
            # Component failure alerts
            for component_name, component_info in self.components.items():
                if component_info['last_status'] in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]:
                    failure_rate = component_info['failure_count'] / max(component_info['check_count'], 1)
                    if failure_rate > 0.5:  # More than 50% failure rate
                        self._generate_alert(
                            "component_high_failure_rate",
                            f"Component {component_name} has high failure rate: {failure_rate:.1%}",
                            {
                                "component": component_name,
                                "failure_rate": failure_rate,
                                "failure_count": component_info['failure_count'],
                                "check_count": component_info['check_count']
                            }
                        )
            
        except Exception as e:
            self.logger.error(f"Failed to check alert conditions: {e}")
    
    def _get_latest_metric(self, metric_name: str) -> Optional[Metric]:
        """Get the latest metric by name"""
        matching_metrics = [m for m in self.metrics if m.name == metric_name]
        if matching_metrics:
            return max(matching_metrics, key=lambda x: x.timestamp)
        return None
    
    def _generate_alert(self, alert_type: str, message: str, details: Dict[str, Any]) -> None:
        """Generate an alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        with self._lock:
            self.alerts.append(alert)
        
        self.logger.warning(f"ALERT [{alert_type}]: {message}")
    
    def _cleanup_old_data(self) -> None:
        """Clean up old monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
        
        with self._lock:
            # Clean up health checks
            self.health_checks = [hc for hc in self.health_checks if hc.timestamp > cutoff_time]
            
            # Clean up alerts (keep for longer - 7 days)
            alert_cutoff = datetime.now() - timedelta(days=7)
            self.alerts = [
                a for a in self.alerts 
                if datetime.fromisoformat(a["timestamp"]) > alert_cutoff
            ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status"""
        with self._lock:
            overall_status = HealthStatus.HEALTHY
            component_statuses = {}
            
            for component_name, component_info in self.components.items():
                status = component_info['last_status']
                component_statuses[component_name] = {
                    'status': status.value,
                    'last_check': component_info['last_check'].isoformat() if component_info['last_check'] else None,
                    'check_count': component_info['check_count'],
                    'failure_count': component_info['failure_count'],
                    'description': component_info['description']
                }
                
                # Update overall status based on worst component status
                if status == HealthStatus.CRITICAL:
                    overall_status = HealthStatus.CRITICAL
                elif status == HealthStatus.UNHEALTHY and overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.UNHEALTHY
                elif status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "overall_status": overall_status.value,
                "uptime_seconds": uptime,
                "components": component_statuses,
                "metrics_summary": {
                    "documents_processed": self.documents_processed,
                    "entities_extracted": self.entities_extracted,
                    "database_operations": self.database_operations,
                    "errors_count": self.errors_count,
                    "average_processing_time": self.average_processing_time
                },
                "system_metrics": self._get_current_system_metrics(),
                "active_alerts": len([a for a in self.alerts if self._is_recent_alert(a)]),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_current_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        try:
            cpu_metric = self._get_latest_metric("cpu_percent")
            memory_metric = self._get_latest_metric("memory_percent")
            disk_metric = self._get_latest_metric("disk_percent")
            
            return {
                "cpu_percent": cpu_metric.value if cpu_metric else 0.0,
                "memory_percent": memory_metric.value if memory_metric else 0.0,
                "disk_percent": disk_metric.value if disk_metric else 0.0
            }
        except Exception:
            return {"cpu_percent": 0.0, "memory_percent": 0.0, "disk_percent": 0.0}
    
    def _is_recent_alert(self, alert: Dict[str, Any]) -> bool:
        """Check if alert is recent (within last hour)"""
        alert_time = datetime.fromisoformat(alert["timestamp"])
        return (datetime.now() - alert_time) <= timedelta(hours=1)
    
    def get_metrics(self, metric_name: Optional[str] = None, 
                   time_range_hours: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get metrics data"""
        with self._lock:
            metrics = self.metrics.copy()
        
        # Filter by metric name if specified
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        # Filter by time range if specified
        if time_range_hours:
            cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
            metrics = [m for m in metrics if m.timestamp > cutoff_time]
        
        # Convert to serializable format
        return [asdict(m) for m in metrics]
    
    def get_alerts(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get alerts"""
        with self._lock:
            alerts = self.alerts.copy()
        
        if active_only:
            alerts = [a for a in alerts if self._is_recent_alert(a)]
        
        return alerts
    
    def generate_monitoring_report(self, report_name: str = "system_monitoring_report") -> Path:
        """Generate comprehensive monitoring report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"{report_name}_{timestamp}.json"
        
        report_data = {
            "report_name": report_name,
            "generated_at": datetime.now().isoformat(),
            "monitoring_period": {
                "start_time": self.start_time.isoformat(),
                "duration_hours": (datetime.now() - self.start_time).total_seconds() / 3600
            },
            "health_status": self.get_health_status(),
            "metrics_summary": {
                "total_metrics": len(self.metrics),
                "unique_metric_names": len(set([m.name for m in self.metrics])),
                "metric_types": list(set([m.metric_type.value for m in self.metrics])),
                "latest_metrics": {
                    metric_name: self._get_latest_metric(metric_name).value
                    for metric_name in set([m.name for m in self.metrics[-50:]])  # Last 50 unique metrics
                    if self._get_latest_metric(metric_name)
                }
            },
            "alerts_summary": {
                "total_alerts": len(self.alerts),
                "active_alerts": len([a for a in self.alerts if self._is_recent_alert(a)]),
                "alert_types": list(set([a["type"] for a in self.alerts])),
                "recent_alerts": [a for a in self.alerts if self._is_recent_alert(a)]
            },
            "component_health": {
                name: {
                    "status": info['last_status'].value if info['last_status'] else 'unknown',
                    "check_count": info['check_count'],
                    "failure_count": info['failure_count'],
                    "success_rate": (info['check_count'] - info['failure_count']) / max(info['check_count'], 1)
                }
                for name, info in self.components.items()
            },
            "system_performance": {
                "documents_per_hour": self.documents_processed / max((datetime.now() - self.start_time).total_seconds() / 3600, 1),
                "entities_per_hour": self.entities_extracted / max((datetime.now() - self.start_time).total_seconds() / 3600, 1),
                "average_processing_time": self.average_processing_time,
                "error_rate": self.errors_count / max(self.documents_processed, 1)
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Monitoring report generated: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate monitoring report: {e}")
            raise
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        health_status = self.get_health_status()
        
        # Get recent metrics for charts
        recent_cpu = [m for m in self.metrics if m.name == "cpu_percent"][-20:]  # Last 20 points
        recent_memory = [m for m in self.metrics if m.name == "memory_percent"][-20:]
        recent_processing_times = [m for m in self.metrics if m.name == "processing_time"][-20:]
        
        return {
            "health_status": health_status,
            "charts": {
                "cpu_usage": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in recent_cpu
                ],
                "memory_usage": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in recent_memory
                ],
                "processing_times": [
                    {"timestamp": m.timestamp.isoformat(), "value": m.value}
                    for m in recent_processing_times
                ]
            },
            "alerts": self.get_alerts(active_only=True),
            "summary": {
                "total_documents": self.documents_processed,
                "total_entities": self.entities_extracted,
                "total_errors": self.errors_count,
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
                "avg_processing_time": self.average_processing_time
            }
        }


# Global monitor instance
_global_monitor: Optional[KGASSystemMonitor] = None
_monitor_lock = threading.Lock()


def get_system_monitor(config: Optional[Dict[str, Any]] = None) -> KGASSystemMonitor:
    """Get global system monitor instance"""
    global _global_monitor
    
    if _global_monitor is None:
        with _monitor_lock:
            if _global_monitor is None:
                _global_monitor = KGASSystemMonitor(config)
    
    return _global_monitor


def start_system_monitoring(config: Optional[Dict[str, Any]] = None) -> KGASSystemMonitor:
    """Start system monitoring and return monitor instance"""
    monitor = get_system_monitor(config)
    monitor.start_monitoring()
    return monitor


if __name__ == "__main__":
    # Test the system monitor
    print("Testing KGAS System Monitor...")
    
    # Create monitor with test configuration
    config = {
        'check_interval': 5,  # Check every 5 seconds for testing
        'output_dir': 'test_monitoring_output'
    }
    
    monitor = KGASSystemMonitor(config)
    
    # Register test components
    def test_component_health():
        return {
            'status': 'healthy',
            'message': 'Test component is working',
            'metrics': {'test_metric': 42}
        }
    
    def failing_component_health():
        return {
            'status': 'unhealthy',
            'message': 'Test component is failing',
            'error_details': 'Simulated failure for testing'
        }
    
    monitor.register_component("test_component", test_component_health, "Test component for monitoring")
    monitor.register_component("failing_component", failing_component_health, "Component that fails for testing")
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Simulate some activity
        print("Simulating system activity...")
        
        for i in range(5):
            # Simulate document processing
            monitor.record_document_processed(processing_time=1.5, entities_count=10)
            
            # Simulate database operations
            monitor.record_database_operation("insert", True, 0.1)
            monitor.record_database_operation("query", True, 0.05)
            
            # Simulate an error
            if i == 2:
                monitor.record_error("test_error", {"severity": "warning", "details": "Test error"})
            
            time.sleep(2)
        
        # Get health status
        health_status = monitor.get_health_status()
        print(f"Health Status: {health_status['overall_status']}")
        print(f"Components: {len(health_status['components'])}")
        print(f"Documents Processed: {health_status['metrics_summary']['documents_processed']}")
        
        # Generate report
        report_file = monitor.generate_monitoring_report("test_report")
        print(f"Generated report: {report_file}")
        
        # Get dashboard data
        dashboard_data = monitor.get_dashboard_data()
        print(f"Dashboard alerts: {len(dashboard_data['alerts'])}")
        
        print("✅ System monitor tests completed successfully")
        
    finally:
        # Stop monitoring
        monitor.stop_monitoring()
        print("Monitoring stopped")