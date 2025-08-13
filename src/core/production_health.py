"""
Production Health Checker for KGAS System
Comprehensive health checking for production deployment
"""

import os
import time
import psutil
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """System health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentHealth:
    """Health status for a system component"""
    
    def __init__(self, name: str, status: HealthStatus, 
                 message: str = "", details: Dict[str, Any] = None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class ProductionHealthChecker:
    """Comprehensive health checking for production deployment"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._last_check_time = None
        self._health_history = []
        self._alert_thresholds = {
            'memory_percent': 85,
            'cpu_percent': 80,
            'disk_percent': 90,
            'response_time_ms': 1000,
            'error_rate_percent': 5
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        start_time = time.time()
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': HealthStatus.UNKNOWN.value,
            'components': {},
            'performance_metrics': {},
            'system_resources': {},
            'recommendations': [],
            'alerts': []
        }
        
        try:
            # Check all system components
            health_report['components'] = {
                'service_manager': self._check_service_manager(),
                'tools': self._check_all_tools(),
                'dependencies': self._check_dependencies(),
                'database': self._check_database_connections(),
                'resources': self._check_system_resources()
            }
            
            # Collect performance metrics
            health_report['performance_metrics'] = self._collect_performance_metrics()
            
            # Collect system resource usage
            health_report['system_resources'] = self._collect_resource_usage()
            
            # Determine overall status
            health_report['overall_status'] = self._calculate_overall_status(
                health_report['components']
            )
            
            # Generate recommendations
            health_report['recommendations'] = self._generate_recommendations(
                health_report
            )
            
            # Check for alerts
            health_report['alerts'] = self._check_alerts(health_report)
            
            # Record check time
            health_report['check_duration_ms'] = (time.time() - start_time) * 1000
            
            # Store in history
            self._health_history.append(health_report)
            if len(self._health_history) > 100:  # Keep last 100 checks
                self._health_history.pop(0)
            
            self._last_check_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            health_report['overall_status'] = HealthStatus.CRITICAL.value
            health_report['error'] = str(e)
        
        return health_report
    
    def _check_service_manager(self) -> Dict[str, Any]:
        """Check ServiceManager health"""
        try:
            from src.core.service_manager import ServiceManager
            
            sm = ServiceManager()
            stats = sm.get_service_stats()
            
            # Check if services are available
            services_healthy = all([
                stats.get('identity_service_active', False),
                stats.get('provenance_service_active', False),
                stats.get('quality_service_active', False)
            ])
            
            # Check individual service health
            service_health = {}
            for service_name in ['identity', 'provenance', 'quality']:
                health_key = f"{service_name}_health"
                if health_key in stats:
                    service_health[service_name] = stats[health_key].get('status', 'unknown')
                else:
                    service_health[service_name] = 'unknown'
            
            # Determine status
            if services_healthy and all(s == 'healthy' for s in service_health.values()):
                status = HealthStatus.HEALTHY.value
            elif stats.get('system_mode') == 'offline':
                status = HealthStatus.DEGRADED.value
            elif services_healthy:
                status = HealthStatus.DEGRADED.value
            else:
                status = HealthStatus.UNHEALTHY.value
            
            return {
                'status': status,
                'system_mode': stats.get('system_mode', 'unknown'),
                'services_available': sum(1 for k, v in stats.items() 
                                        if k.endswith('_active') and v),
                'service_health': service_health,
                'neo4j_connected': stats.get('neo4j_driver_active', False)
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'error': str(e)
            }
    
    def _check_all_tools(self) -> Dict[str, Any]:
        """Check health of all available tools"""
        tool_health = {
            'total_tools': 0,
            'healthy_tools': 0,
            'degraded_tools': 0,
            'failed_tools': 0,
            'tool_status': {}
        }
        
        # List of critical tools to check
        critical_tools = [
            ('PDF Loader', 'src.tools.phase1.t01_pdf_loader', 'PDFLoader'),
            ('Text Chunker', 'src.tools.phase1.t15a_text_chunker', 'TextChunker'),
            ('SpaCy NER', 'src.tools.phase1.t23a_spacy_ner', 'SpacyNER'),
        ]
        
        for tool_name, module_path, class_name in critical_tools:
            tool_health['total_tools'] += 1
            
            try:
                # Try to import and check tool
                module = __import__(module_path, fromlist=[class_name])
                tool_class = getattr(module, class_name)
                
                # Check if tool can be instantiated
                from src.core.service_manager import ServiceManager
                sm = ServiceManager()
                tool = tool_class(services=sm)
                
                # Check tool health if method exists
                if hasattr(tool, 'health_check'):
                    health_result = tool.health_check()
                    if health_result.status == 'success':
                        tool_health['healthy_tools'] += 1
                        tool_health['tool_status'][tool_name] = 'healthy'
                    else:
                        tool_health['degraded_tools'] += 1
                        tool_health['tool_status'][tool_name] = 'degraded'
                else:
                    tool_health['healthy_tools'] += 1
                    tool_health['tool_status'][tool_name] = 'available'
                
            except Exception as e:
                tool_health['failed_tools'] += 1
                tool_health['tool_status'][tool_name] = f'failed: {str(e)[:50]}'
        
        # Determine overall tool health
        if tool_health['failed_tools'] == 0:
            status = HealthStatus.HEALTHY.value
        elif tool_health['failed_tools'] < tool_health['total_tools'] / 2:
            status = HealthStatus.DEGRADED.value
        else:
            status = HealthStatus.UNHEALTHY.value
        
        tool_health['status'] = status
        return tool_health
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check external dependencies"""
        dependencies = {
            'status': HealthStatus.HEALTHY.value,
            'python_version': None,
            'required_packages': {},
            'optional_packages': {}
        }
        
        try:
            import sys
            dependencies['python_version'] = sys.version
            
            # Check required packages
            required = ['neo4j', 'spacy', 'pandas', 'numpy', 'psutil']
            for package in required:
                try:
                    __import__(package)
                    dependencies['required_packages'][package] = 'installed'
                except ImportError:
                    dependencies['required_packages'][package] = 'missing'
                    dependencies['status'] = HealthStatus.UNHEALTHY.value
            
            # Check optional packages
            optional = ['pypdf', 'networkx', 'scipy', 'sklearn']
            for package in optional:
                try:
                    __import__(package)
                    dependencies['optional_packages'][package] = 'installed'
                except ImportError:
                    dependencies['optional_packages'][package] = 'missing'
                    if dependencies['status'] == HealthStatus.HEALTHY.value:
                        dependencies['status'] = HealthStatus.DEGRADED.value
            
            # Check spaCy model
            try:
                import spacy
                nlp = spacy.load("en_core_web_sm")
                dependencies['spacy_model'] = 'loaded'
            except:
                dependencies['spacy_model'] = 'missing'
                if dependencies['status'] == HealthStatus.HEALTHY.value:
                    dependencies['status'] = HealthStatus.DEGRADED.value
            
        except Exception as e:
            dependencies['status'] = HealthStatus.CRITICAL.value
            dependencies['error'] = str(e)
        
        return dependencies
    
    def _check_database_connections(self) -> Dict[str, Any]:
        """Check database connectivity"""
        db_health = {
            'status': HealthStatus.UNKNOWN.value,
            'neo4j': {'status': 'unknown'},
            'sqlite': {'status': 'unknown'}
        }
        
        # Check Neo4j
        try:
            from neo4j import GraphDatabase
            
            # Try default connection
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", os.environ.get("NEO4J_PASSWORD", "password"))
            )
            
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            driver.close()
            db_health['neo4j'] = {
                'status': 'connected',
                'uri': 'bolt://localhost:7687'
            }
            
        except Exception as e:
            db_health['neo4j'] = {
                'status': 'disconnected',
                'error': str(e)[:100]
            }
        
        # Check SQLite
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path("data/provenance.db")
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                cursor.fetchone()
                conn.close()
                
                db_health['sqlite'] = {
                    'status': 'connected',
                    'path': str(db_path)
                }
            else:
                db_health['sqlite'] = {
                    'status': 'not_initialized',
                    'path': str(db_path)
                }
                
        except Exception as e:
            db_health['sqlite'] = {
                'status': 'error',
                'error': str(e)[:100]
            }
        
        # Determine overall database health
        if db_health['neo4j']['status'] == 'connected' and \
           db_health['sqlite']['status'] in ['connected', 'not_initialized']:
            db_health['status'] = HealthStatus.HEALTHY.value
        elif db_health['sqlite']['status'] in ['connected', 'not_initialized']:
            db_health['status'] = HealthStatus.DEGRADED.value
        else:
            db_health['status'] = HealthStatus.UNHEALTHY.value
        
        return db_health
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resources = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 * 1024),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024 * 1024 * 1024)
            }
            
            # Check against thresholds
            issues = []
            if cpu_percent > self._alert_thresholds['cpu_percent']:
                issues.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > self._alert_thresholds['memory_percent']:
                issues.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > self._alert_thresholds['disk_percent']:
                issues.append(f"Low disk space: {disk.percent}% used")
            
            # Determine status
            if not issues:
                status = HealthStatus.HEALTHY.value
            elif len(issues) == 1:
                status = HealthStatus.DEGRADED.value
            else:
                status = HealthStatus.UNHEALTHY.value
            
            return {
                'status': status,
                'metrics': resources,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'error': str(e)
            }
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'response_times': {},
            'throughput': {}
        }
        
        try:
            # Test service response times
            from src.core.service_manager import ServiceManager
            sm = ServiceManager()
            
            # Measure identity service
            start = time.time()
            if hasattr(sm.identity_service, 'health_check'):
                sm.identity_service.health_check()
            metrics['response_times']['identity_service_ms'] = (time.time() - start) * 1000
            
            # Measure provenance service
            start = time.time()
            op_id = sm.provenance_service.start_operation("HEALTH", "test", [], {})
            sm.provenance_service.complete_operation(op_id, None, True)
            metrics['response_times']['provenance_operation_ms'] = (time.time() - start) * 1000
            
            # Calculate throughput (operations per second)
            ops_count = 10
            start = time.time()
            for i in range(ops_count):
                op_id = sm.provenance_service.start_operation("PERF", f"op_{i}", [], {})
                sm.provenance_service.complete_operation(op_id, None, True)
            duration = time.time() - start
            metrics['throughput']['operations_per_second'] = ops_count / duration if duration > 0 else 0
            
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def _collect_resource_usage(self) -> Dict[str, Any]:
        """Collect detailed resource usage"""
        try:
            process = psutil.Process()
            
            return {
                'process': {
                    'pid': process.pid,
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / (1024 * 1024),
                    'threads': process.num_threads(),
                    'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
                },
                'system': {
                    'cpu_count': psutil.cpu_count(),
                    'total_memory_gb': psutil.virtual_memory().total / (1024 * 1024 * 1024),
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_overall_status(self, components: Dict[str, Any]) -> str:
        """Calculate overall system status from component health"""
        statuses = []
        
        for component_name, component_data in components.items():
            if isinstance(component_data, dict) and 'status' in component_data:
                status_str = component_data['status']
                
                # Map string status to HealthStatus enum
                try:
                    status = HealthStatus(status_str)
                except ValueError:
                    # Handle non-standard status values
                    if status_str in ['connected', 'available']:
                        status = HealthStatus.HEALTHY
                    elif status_str in ['disconnected', 'degraded']:
                        status = HealthStatus.DEGRADED
                    else:
                        status = HealthStatus.UNKNOWN
                
                statuses.append(status)
        
        if not statuses:
            return HealthStatus.UNKNOWN.value
        
        # Determine overall status
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY.value
        elif any(s == HealthStatus.CRITICAL for s in statuses):
            return HealthStatus.CRITICAL.value
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY.value
        elif any(s == HealthStatus.DEGRADED for s in statuses):
            return HealthStatus.DEGRADED.value
        else:
            return HealthStatus.HEALTHY.value
    
    def _generate_recommendations(self, health_report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health report"""
        recommendations = []
        
        # Check service manager
        sm_health = health_report['components'].get('service_manager', {})
        if sm_health.get('system_mode') == 'offline':
            recommendations.append("System running in offline mode. Enable services for full functionality.")
        
        # Check tools
        tools_health = health_report['components'].get('tools', {})
        if tools_health.get('failed_tools', 0) > 0:
            recommendations.append(f"Fix {tools_health['failed_tools']} failed tools.")
        
        # Check dependencies
        deps = health_report['components'].get('dependencies', {})
        missing_required = [k for k, v in deps.get('required_packages', {}).items() if v == 'missing']
        if missing_required:
            recommendations.append(f"Install missing packages: {', '.join(missing_required)}")
        
        if deps.get('spacy_model') == 'missing':
            recommendations.append("Install spaCy model: python -m spacy download en_core_web_sm")
        
        # Check databases
        db_health = health_report['components'].get('database', {})
        if db_health.get('neo4j', {}).get('status') != 'connected':
            recommendations.append("Neo4j not connected. Start Neo4j or enable fallback mode.")
        
        # Check resources
        resources = health_report['components'].get('resources', {})
        if resources.get('issues'):
            for issue in resources['issues']:
                recommendations.append(f"Resource issue: {issue}")
        
        # Performance recommendations
        metrics = health_report.get('performance_metrics', {})
        response_times = metrics.get('response_times', {})
        for service, time_ms in response_times.items():
            if time_ms > self._alert_thresholds['response_time_ms']:
                recommendations.append(f"Optimize {service}: response time {time_ms:.1f}ms")
        
        return recommendations
    
    def _check_alerts(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # Critical status alert
        if health_report['overall_status'] == HealthStatus.CRITICAL.value:
            alerts.append({
                'level': 'critical',
                'message': 'System in critical state',
                'timestamp': datetime.now().isoformat()
            })
        
        # Resource alerts
        resources = health_report['components'].get('resources', {})
        metrics = resources.get('metrics', {})
        
        if metrics.get('memory_percent', 0) > self._alert_thresholds['memory_percent']:
            alerts.append({
                'level': 'warning',
                'message': f"Memory usage high: {metrics['memory_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        if metrics.get('cpu_percent', 0) > self._alert_thresholds['cpu_percent']:
            alerts.append({
                'level': 'warning',
                'message': f"CPU usage high: {metrics['cpu_percent']}%",
                'timestamp': datetime.now().isoformat()
            })
        
        # Database alerts
        db_health = health_report['components'].get('database', {})
        if db_health.get('neo4j', {}).get('status') == 'disconnected':
            alerts.append({
                'level': 'warning',
                'message': 'Neo4j database disconnected',
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of recent health checks"""
        if not self._health_history:
            return {'message': 'No health checks performed yet'}
        
        recent_checks = self._health_history[-10:]  # Last 10 checks
        
        status_counts = {}
        for check in recent_checks:
            status = check.get('overall_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_checks': len(self._health_history),
            'recent_checks': len(recent_checks),
            'status_distribution': status_counts,
            'last_check': self._health_history[-1]['timestamp'],
            'current_status': self._health_history[-1]['overall_status']
        }


# Convenience function
def check_production_health() -> Dict[str, Any]:
    """Quick health check function"""
    checker = ProductionHealthChecker()
    return checker.check_system_health()