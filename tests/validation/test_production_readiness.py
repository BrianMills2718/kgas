#!/usr/bin/env python3
"""
Production Readiness Validation for System Integration
Final database connectivity tests and system health validation.
"""

import asyncio
import logging
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Core services
from src.core.service_manager import ServiceManager
from src.services.analytics_service import AnalyticsService

# Monitoring
try:
    from src.monitoring.structured_output_monitor import get_monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("WARNING: Monitoring not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseHealthResult:
    """Result of database health check"""
    database_name: str
    connected: bool
    connection_time: float
    query_successful: bool
    query_time: float
    error_message: Optional[str] = None

@dataclass
class SystemHealthResult:
    """Result of comprehensive system health check"""
    overall_healthy: bool
    database_results: List[DatabaseHealthResult]
    service_manager_healthy: bool
    monitoring_available: bool
    critical_issues: List[str]
    warnings: List[str]
    performance_summary: Dict[str, Any]

class ProductionReadinessTester:
    """
    Production readiness validation implementation.
    Tests database connectivity and overall system health.
    """
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.analytics_service = AnalyticsService()
        self.monitor = get_monitor() if MONITORING_AVAILABLE else None
        
    async def initialize(self) -> bool:
        """Initialize production readiness tester"""
        try:
            logger.info("Initializing production readiness tester...")
            logger.info("Production readiness tester initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize production readiness tester: {e}")
            return False
    
    async def test_neo4j_connectivity(self) -> DatabaseHealthResult:
        """Test Neo4j database connectivity and operations"""
        logger.info("Testing Neo4j connectivity...")
        
        start_time = time.time()
        
        try:
            # Test connection
            neo4j_driver = self.service_manager.get_neo4j_driver()
            connection_time = time.time() - start_time
            
            if not neo4j_driver:
                return DatabaseHealthResult(
                    database_name="Neo4j",
                    connected=False,
                    connection_time=connection_time,
                    query_successful=False,
                    query_time=0.0,
                    error_message="Neo4j driver not available"
                )
            
            # Test basic query
            query_start = time.time()
            with neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test, datetime() as timestamp")
                record = result.single()
                if record:
                    test_value = record["test"]
                    timestamp = record["timestamp"]
                    logger.info(f"Neo4j query successful: test={test_value}, timestamp={timestamp}")
                
            query_time = time.time() - query_start
            
            # Test database info
            with neo4j_driver.session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
                records = list(result)
                if records:
                    for record in records:
                        logger.info(f"Neo4j component: {record['name']} v{record['version']} ({record['edition']})")
            
            logger.info("✅ Neo4j connectivity test successful")
            return DatabaseHealthResult(
                database_name="Neo4j",
                connected=True,
                connection_time=connection_time,
                query_successful=True,
                query_time=query_time
            )
            
        except Exception as e:
            connection_time = time.time() - start_time
            logger.error(f"❌ Neo4j connectivity test failed: {e}")
            return DatabaseHealthResult(
                database_name="Neo4j",
                connected=False,
                connection_time=connection_time,
                query_successful=False,
                query_time=0.0,
                error_message=str(e)
            )
    
    async def test_sqlite_connectivity(self) -> DatabaseHealthResult:
        """Test SQLite database connectivity and operations"""
        logger.info("Testing SQLite connectivity...")
        
        start_time = time.time()
        
        try:
            # Test provenance service (which uses SQLite)
            provenance_service = self.service_manager.get_provenance_service()
            connection_time = time.time() - start_time
            
            if not provenance_service:
                return DatabaseHealthResult(
                    database_name="SQLite",
                    connected=False,
                    connection_time=connection_time,
                    query_successful=False,
                    query_time=0.0,
                    error_message="Provenance service not available"
                )
            
            # Test basic operations
            query_start = time.time()
            
            # Create test operation
            test_operation_id = provenance_service.start_operation(
                tool_id="production_test",
                operation_type="production_test",
                inputs=["connectivity_test"],
                parameters={"timestamp": time.time()}
            )
            
            # Verify the operation was created (operation_id should be returned)
            if not test_operation_id:
                raise Exception("Failed to create test operation")
            
            # Test completion
            provenance_service.complete_operation(
                operation_id=test_operation_id,
                outputs=["success"],
                success=True,
                metadata={"test_completed": True}
            )
            
            query_time = time.time() - query_start
            
            logger.info("✅ SQLite connectivity test successful")
            return DatabaseHealthResult(
                database_name="SQLite",
                connected=True,
                connection_time=connection_time,
                query_successful=True,
                query_time=query_time
            )
            
        except Exception as e:
            connection_time = time.time() - start_time
            logger.error(f"❌ SQLite connectivity test failed: {e}")
            return DatabaseHealthResult(
                database_name="SQLite",
                connected=False,
                connection_time=connection_time,
                query_successful=False,
                query_time=0.0,
                error_message=str(e)
            )
    
    async def test_service_manager_health(self) -> Dict[str, Any]:
        """Test service manager health and service availability"""
        logger.info("Testing service manager health...")
        
        try:
            # Get service statistics
            service_stats = self.service_manager.get_service_stats()
            
            # Test individual services
            service_health = {}
            
            # Test identity service
            try:
                identity_service = self.service_manager.get_identity_service()
                service_health["identity_service"] = identity_service is not None
            except Exception as e:
                service_health["identity_service"] = False
                logger.warning(f"Identity service not available: {e}")
            
            # Test provenance service
            try:
                provenance_service = self.service_manager.get_provenance_service()
                service_health["provenance_service"] = provenance_service is not None
            except Exception as e:
                service_health["provenance_service"] = False
                logger.warning(f"Provenance service not available: {e}")
            
            # Test quality service
            try:
                quality_service = self.service_manager.get_quality_service()
                service_health["quality_service"] = quality_service is not None
            except Exception as e:
                service_health["quality_service"] = False
                logger.warning(f"Quality service not available: {e}")
            
            # Test Neo4j manager
            try:
                neo4j_manager = self.service_manager.get_neo4j_manager()
                service_health["neo4j_manager"] = neo4j_manager is not None
            except Exception as e:
                service_health["neo4j_manager"] = False
                logger.warning(f"Neo4j manager not available: {e}")
            
            healthy_services = sum(service_health.values())
            total_services = len(service_health)
            
            logger.info(f"Service manager health: {healthy_services}/{total_services} services healthy")
            
            return {
                "healthy": healthy_services >= total_services * 0.75,  # 75% of services must be healthy
                "service_stats": service_stats,
                "service_health": service_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_percentage": healthy_services / total_services if total_services > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Service manager health test failed: {e}")
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def test_monitoring_system_health(self) -> Dict[str, Any]:
        """Test monitoring system health and performance summary"""
        logger.info("Testing monitoring system health...")
        
        if not MONITORING_AVAILABLE or not self.monitor:
            return {
                "available": False,
                "error": "Monitoring system not available"
            }
        
        try:
            # Get performance summary
            performance_summary = self.monitor.get_performance_summary()
            
            # Validate system health based on monitoring data
            overall_stats = performance_summary.get("overall_stats", {})
            success_rate = overall_stats.get("success_rate", 0.0)
            avg_response_time = overall_stats.get("avg_response_time_ms", 0.0)
            
            # Check for critical issues
            critical_issues = []
            if success_rate < 0.8:  # Less than 80% success rate
                critical_issues.append(f"Low success rate: {success_rate:.1%}")
            
            if avg_response_time > 10000:  # More than 10 seconds average
                critical_issues.append(f"High response time: {avg_response_time:.0f}ms")
            
            # Get recent metrics
            recent_metrics = self.monitor.metrics_history[-10:] if len(self.monitor.metrics_history) >= 10 else self.monitor.metrics_history
            recent_failures = [m for m in recent_metrics if not m.success]
            
            if len(recent_failures) > 5:  # More than 5 failures in recent metrics
                critical_issues.append(f"High recent failure rate: {len(recent_failures)}/{len(recent_metrics)}")
            
            logger.info(f"Monitoring system health: {len(critical_issues)} critical issues")
            
            return {
                "available": True,
                "healthy": len(critical_issues) == 0,
                "performance_summary": performance_summary,
                "critical_issues": critical_issues,
                "recent_metrics_count": len(recent_metrics),
                "recent_failures": len(recent_failures),
                "success_rate": success_rate,
                "avg_response_time_ms": avg_response_time
            }
            
        except Exception as e:
            logger.error(f"Monitoring system health test failed: {e}")
            return {
                "available": True,
                "healthy": False,
                "error": str(e)
            }
    
    async def run_comprehensive_system_health_check(self) -> SystemHealthResult:
        """Run comprehensive system health check"""
        logger.info("Running comprehensive system health check...")
        
        critical_issues = []
        warnings = []
        database_results = []
        
        # Test database connectivity
        neo4j_result = await self.test_neo4j_connectivity()
        database_results.append(neo4j_result)
        
        sqlite_result = await self.test_sqlite_connectivity()
        database_results.append(sqlite_result)
        
        # Check database health
        if not neo4j_result.connected:
            critical_issues.append(f"Neo4j not connected: {neo4j_result.error_message}")
        elif neo4j_result.connection_time > 5.0:
            warnings.append(f"Neo4j slow connection: {neo4j_result.connection_time:.2f}s")
        
        if not sqlite_result.connected:
            critical_issues.append(f"SQLite not connected: {sqlite_result.error_message}")
        elif sqlite_result.connection_time > 2.0:
            warnings.append(f"SQLite slow connection: {sqlite_result.connection_time:.2f}s")
        
        # Test service manager
        service_health = await self.test_service_manager_health()
        service_manager_healthy = service_health.get("healthy", False)
        
        if not service_manager_healthy:
            critical_issues.append("Service manager not healthy")
        
        # Test monitoring system
        monitoring_health = await self.test_monitoring_system_health()
        monitoring_available = monitoring_health.get("available", False)
        
        if monitoring_available and not monitoring_health.get("healthy", True):
            monitoring_issues = monitoring_health.get("critical_issues", [])
            critical_issues.extend(monitoring_issues)
        
        # Overall health assessment
        overall_healthy = (
            len(critical_issues) == 0 and
            neo4j_result.connected and
            sqlite_result.connected and
            service_manager_healthy
        )
        
        # Performance summary
        performance_summary = {
            "neo4j_connection_time": neo4j_result.connection_time,
            "sqlite_connection_time": sqlite_result.connection_time,
            "neo4j_query_time": neo4j_result.query_time,
            "sqlite_query_time": sqlite_result.query_time,
            "service_health_percentage": service_health.get("health_percentage", 0.0)
        }
        
        if monitoring_available:
            monitoring_perf = monitoring_health.get("performance_summary", {})
            performance_summary.update({
                "monitoring_success_rate": monitoring_health.get("success_rate", 0.0),
                "monitoring_avg_response_time": monitoring_health.get("avg_response_time_ms", 0.0)
            })
        
        return SystemHealthResult(
            overall_healthy=overall_healthy,
            database_results=database_results,
            service_manager_healthy=service_manager_healthy,
            monitoring_available=monitoring_available,
            critical_issues=critical_issues,
            warnings=warnings,
            performance_summary=performance_summary
        )
    
    def check_environment_configuration(self) -> Dict[str, Any]:
        """Check environment configuration and required variables"""
        logger.info("Checking environment configuration...")
        
        required_vars = [
            ("NEO4J_PASSWORD", "Neo4j database password"),
            ("GEMINI_API_KEY", "Gemini API key for LLM operations")
        ]
        
        optional_vars = [
            ("NEO4J_URI", "Neo4j connection URI"),
            ("NEO4J_USERNAME", "Neo4j username"),
            ("LOG_LEVEL", "Logging level")
        ]
        
        env_status = {
            "required_present": {},
            "required_missing": [],
            "optional_present": {},
            "optional_missing": []
        }
        
        # Check required variables
        for var_name, description in required_vars:
            value = os.getenv(var_name)
            if value:
                env_status["required_present"][var_name] = f"Present ({len(value)} chars)"
            else:
                env_status["required_missing"].append((var_name, description))
        
        # Check optional variables
        for var_name, description in optional_vars:
            value = os.getenv(var_name)
            if value:
                env_status["optional_present"][var_name] = value
            else:
                env_status["optional_missing"].append((var_name, description))
        
        # Check configuration files
        config_files = [
            "config/default.yaml",
            "config/schemas/tool_contract_schema.yaml"
        ]
        
        config_status = {}
        for config_file in config_files:
            config_path = Path(config_file)
            config_status[config_file] = {
                "exists": config_path.exists(),
                "readable": config_path.is_file() if config_path.exists() else False
            }
        
        # Overall configuration health
        config_healthy = (
            len(env_status["required_missing"]) == 0 and
            all(status["exists"] and status["readable"] for status in config_status.values())
        )
        
        return {
            "healthy": config_healthy,
            "environment_variables": env_status,
            "configuration_files": config_status
        }

async def main():
    """Main function to run production readiness validation"""
    print("🏭 Starting Production Readiness Validation")
    print("=" * 50)
    
    tester = ProductionReadinessTester()
    
    # Initialize
    print("Initializing production readiness tester...")
    init_success = await tester.initialize()
    if not init_success:
        print("❌ Failed to initialize production readiness tester")
        return
    print("✅ Production readiness tester initialized")
    
    # Check environment configuration
    print("\n🔧 Checking environment configuration...")
    env_config = tester.check_environment_configuration()
    
    print(f"Environment Configuration: {'✅ HEALTHY' if env_config['healthy'] else '❌ ISSUES'}")
    
    required_missing = env_config["environment_variables"]["required_missing"]
    if required_missing:
        print("❌ Missing required environment variables:")
        for var_name, description in required_missing:
            print(f"   - {var_name}: {description}")
    
    config_issues = [f for f, status in env_config["configuration_files"].items() if not (status["exists"] and status["readable"])]
    if config_issues:
        print("❌ Configuration file issues:")
        for config_file in config_issues:
            print(f"   - {config_file}")
    
    # Run comprehensive system health check
    print("\n🏥 Running comprehensive system health check...")
    health_result = await tester.run_comprehensive_system_health_check()
    
    print(f"\n📋 System Health Results:")
    print(f"Overall Health: {'✅ HEALTHY' if health_result.overall_healthy else '❌ UNHEALTHY'}")
    
    # Database results
    print(f"\n🗄️  Database Connectivity:")
    for db_result in health_result.database_results:
        status = "✅ CONNECTED" if db_result.connected else "❌ DISCONNECTED"
        print(f"  {db_result.database_name}: {status}")
        print(f"    Connection Time: {db_result.connection_time:.3f}s")
        if db_result.connected:
            print(f"    Query Time: {db_result.query_time:.3f}s")
        if db_result.error_message:
            print(f"    Error: {db_result.error_message}")
    
    # Service manager
    print(f"\n⚙️  Service Manager: {'✅ HEALTHY' if health_result.service_manager_healthy else '❌ UNHEALTHY'}")
    
    # Monitoring
    print(f"📊 Monitoring: {'✅ AVAILABLE' if health_result.monitoring_available else '❌ UNAVAILABLE'}")
    
    # Critical issues
    if health_result.critical_issues:
        print(f"\n🚨 Critical Issues ({len(health_result.critical_issues)}):")
        for issue in health_result.critical_issues:
            print(f"   - {issue}")
    
    # Warnings
    if health_result.warnings:
        print(f"\n⚠️  Warnings ({len(health_result.warnings)}):")
        for warning in health_result.warnings:
            print(f"   - {warning}")
    
    # Performance summary
    print(f"\n⚡ Performance Summary:")
    perf = health_result.performance_summary
    for key, value in perf.items():
        if isinstance(value, float):
            if "time" in key.lower():
                print(f"  {key}: {value:.3f}s")
            elif "rate" in key.lower() or "percentage" in key.lower():
                print(f"  {key}: {value:.1%}")
            else:
                print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Save results
    results = {
        "system_health": asdict(health_result),
        "environment_configuration": env_config,
        "timestamp": time.time()
    }
    
    results_path = Path("test_results_production_readiness.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_path}")
    
    # Final assessment
    print(f"\n🎯 Production Readiness Assessment:")
    
    # Calculate readiness score
    checks = [
        ("Environment Configuration", env_config["healthy"]),
        ("Database Connectivity", all(db.connected for db in health_result.database_results)),
        ("Service Manager", health_result.service_manager_healthy),
        ("No Critical Issues", len(health_result.critical_issues) == 0)
    ]
    
    passed_checks = sum(1 for _, passed in checks if passed)
    total_checks = len(checks)
    readiness_score = passed_checks / total_checks
    
    for check_name, passed in checks:
        print(f"  {check_name}: {'✅ PASS' if passed else '❌ FAIL'}")
    
    print(f"\nReadiness Score: {readiness_score:.1%}")
    
    if readiness_score >= 0.9:  # 90% or higher
        print("🎉 System is PRODUCTION READY!")
    elif readiness_score >= 0.75:  # 75% or higher
        print("⚠️  System is MOSTLY READY - Address warnings before production")
    else:
        print("❌ System is NOT READY for production - Critical issues must be resolved")

if __name__ == "__main__":
    asyncio.run(main())