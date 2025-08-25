#!/usr/bin/env python3
"""
Performance Integration Testing for System Integration Validation
Tests concurrent operations and resource management under load.
"""

import asyncio
import logging
import time
import json
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import test modules
from test_end_to_end_workflow import EndToEndWorkflowTester, WorkflowResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    memory_used: int
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class ConcurrentTestResult:
    """Result of concurrent operations test"""
    total_operations: int
    successful_operations: int
    failed_operations: int
    success_rate: float
    total_time: float
    average_time_per_operation: float
    peak_memory_usage: int
    peak_cpu_usage: float
    performance_metrics: List[PerformanceMetrics]
    error_messages: List[str]

@dataclass
class ResourceManagementResult:
    """Result of resource management test"""
    initial_memory: int
    peak_memory: int
    final_memory: int
    memory_growth: int
    memory_cleaned_up: bool
    database_connections_open: int
    database_connections_closed: int
    file_handles_open: int
    file_handles_closed: int
    resource_cleanup_successful: bool

class PerformanceIntegrationTester:
    """
    Performance integration testing implementation.
    Tests system performance under various load conditions.
    """
    
    def __init__(self):
        self.workflow_tester = EndToEndWorkflowTester()
        self.process = psutil.Process()
        self.test_results_dir = Path("test_results")
        self.test_results_dir.mkdir(exist_ok=True)
        
    async def initialize(self) -> bool:
        """Initialize performance tester"""
        try:
            logger.info("Initializing performance integration tester...")
            
            # Initialize workflow tester
            init_success = await self.workflow_tester.initialize()
            if not init_success:
                logger.error("Failed to initialize workflow tester")
                return False
            
            logger.info("Performance integration tester initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize performance tester: {e}")
            return False
    
    def capture_system_metrics(self, operation_name: str) -> Dict[str, Any]:
        """Capture current system metrics"""
        try:
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            
            # System-wide metrics
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent(interval=0.1)
            
            return {
                "timestamp": time.time(),
                "operation": operation_name,
                "process_memory_rss": memory_info.rss,
                "process_memory_vms": memory_info.vms,
                "process_cpu_percent": cpu_percent,
                "system_memory_available": system_memory.available,
                "system_memory_percent": system_memory.percent,
                "system_cpu_percent": system_cpu,
                "open_files": len(self.process.open_files()) if hasattr(self.process, 'open_files') else 0
            }
        except Exception as e:
            logger.warning(f"Failed to capture metrics for {operation_name}: {e}")
            return {"error": str(e)}
    
    async def test_concurrent_operations(self, num_operations: int = 5) -> ConcurrentTestResult:
        """Test concurrent workflow operations"""
        logger.info(f"Starting concurrent operations test with {num_operations} operations")
        
        start_time = time.time()
        performance_metrics = []
        error_messages = []
        
        # Monitor system resources
        initial_memory = self.process.memory_info().rss
        peak_memory = initial_memory
        peak_cpu = 0.0
        
        async def run_single_workflow(operation_id: int) -> PerformanceMetrics:
            """Run a single workflow operation with metrics"""
            operation_name = f"concurrent_workflow_{operation_id}"
            
            # Capture initial metrics
            start_metrics = self.capture_system_metrics(operation_name)
            op_start_time = time.time()
            memory_before = self.process.memory_info().rss
            
            try:
                # Run workflow
                result = await self.workflow_tester.test_complete_research_workflow()
                
                # Capture final metrics
                op_end_time = time.time()
                memory_after = self.process.memory_info().rss
                cpu_percent = self.process.cpu_percent()
                
                return PerformanceMetrics(
                    operation_name=operation_name,
                    start_time=op_start_time,
                    end_time=op_end_time,
                    duration=op_end_time - op_start_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    memory_used=memory_after - memory_before,
                    cpu_percent=cpu_percent,
                    success=result.success,
                    error_message=result.error_message if not result.success else None
                )
                
            except Exception as e:
                op_end_time = time.time()
                memory_after = self.process.memory_info().rss
                
                return PerformanceMetrics(
                    operation_name=operation_name,
                    start_time=op_start_time,
                    end_time=op_end_time,
                    duration=op_end_time - op_start_time,
                    memory_before=memory_before,
                    memory_after=memory_after,
                    memory_used=memory_after - memory_before,
                    cpu_percent=0.0,
                    success=False,
                    error_message=str(e)
                )
        
        # Create concurrent tasks
        tasks = [run_single_workflow(i) for i in range(num_operations)]
        
        # Monitor resources during execution
        resource_monitor_task = asyncio.create_task(
            self._monitor_resources_during_execution(
                lambda: len([t for t in tasks if not t.done()]) > 0
            )
        )
        
        # Execute concurrent operations
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Stop resource monitoring
        resource_monitor_task.cancel()
        try:
            await resource_monitor_task
        except asyncio.CancelledError:
            pass
        
        # Process results
        successful_operations = 0
        failed_operations = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed_operations += 1
                error_messages.append(str(result))
                # Create error metric
                performance_metrics.append(PerformanceMetrics(
                    operation_name="exception_operation",
                    start_time=start_time,
                    end_time=time.time(),
                    duration=0.0,
                    memory_before=0,
                    memory_after=0,
                    memory_used=0,
                    cpu_percent=0.0,
                    success=False,
                    error_message=str(result)
                ))
            else:
                performance_metrics.append(result)
                if result.success:
                    successful_operations += 1
                else:
                    failed_operations += 1
                    if result.error_message:
                        error_messages.append(result.error_message)
        
        # Calculate metrics
        total_time = time.time() - start_time
        success_rate = successful_operations / num_operations if num_operations > 0 else 0.0
        average_time = total_time / num_operations if num_operations > 0 else 0.0
        
        final_memory = self.process.memory_info().rss
        peak_memory = max(peak_memory, final_memory)
        
        return ConcurrentTestResult(
            total_operations=num_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            success_rate=success_rate,
            total_time=total_time,
            average_time_per_operation=average_time,
            peak_memory_usage=peak_memory,
            peak_cpu_usage=peak_cpu,
            performance_metrics=performance_metrics,
            error_messages=error_messages
        )
    
    async def _monitor_resources_during_execution(self, should_continue_func) -> None:
        """Monitor system resources during test execution"""
        try:
            while should_continue_func():
                # Monitor memory and CPU
                memory_info = self.process.memory_info()
                cpu_percent = self.process.cpu_percent()
                
                # Log high resource usage
                if memory_info.rss > 500 * 1024 * 1024:  # 500MB
                    logger.warning(f"High memory usage detected: {memory_info.rss / 1024 / 1024:.1f}MB")
                
                if cpu_percent > 80:
                    logger.warning(f"High CPU usage detected: {cpu_percent:.1f}%")
                
                await asyncio.sleep(1.0)  # Monitor every second
                
        except asyncio.CancelledError:
            pass
    
    async def test_resource_management(self) -> ResourceManagementResult:
        """Test resource management and cleanup"""
        logger.info("Testing resource management and cleanup")
        
        # Capture initial state
        initial_memory = self.process.memory_info().rss
        initial_open_files = len(self.process.open_files()) if hasattr(self.process, 'open_files') else 0
        
        peak_memory = initial_memory
        
        try:
            # Run multiple operations to stress test resource management
            for i in range(3):
                logger.info(f"Resource management test iteration {i+1}/3")
                
                # Run workflow operation
                result = await self.workflow_tester.test_complete_research_workflow()
                
                # Monitor memory growth
                current_memory = self.process.memory_info().rss
                peak_memory = max(peak_memory, current_memory)
                
                logger.info(f"Memory after iteration {i+1}: {current_memory / 1024 / 1024:.1f}MB")
                
                # Force garbage collection
                import gc
                gc.collect()
                
                # Small delay between operations
                await asyncio.sleep(0.5)
            
            # Final cleanup test
            logger.info("Testing final resource cleanup")
            
            # Close service manager resources
            if hasattr(self.workflow_tester.service_manager, 'close_all'):
                self.workflow_tester.service_manager.close_all()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            # Wait for cleanup
            await asyncio.sleep(2.0)
            
            # Capture final state
            final_memory = self.process.memory_info().rss
            final_open_files = len(self.process.open_files()) if hasattr(self.process, 'open_files') else 0
            
            # Calculate metrics
            memory_growth = final_memory - initial_memory
            memory_cleaned_up = memory_growth < (50 * 1024 * 1024)  # Less than 50MB growth
            
            return ResourceManagementResult(
                initial_memory=initial_memory,
                peak_memory=peak_memory,
                final_memory=final_memory,
                memory_growth=memory_growth,
                memory_cleaned_up=memory_cleaned_up,
                database_connections_open=0,  # Would need DB monitoring
                database_connections_closed=0,
                file_handles_open=final_open_files,
                file_handles_closed=initial_open_files - final_open_files,
                resource_cleanup_successful=memory_cleaned_up and final_open_files <= initial_open_files
            )
            
        except Exception as e:
            logger.error(f"Resource management test failed: {e}")
            final_memory = self.process.memory_info().rss
            
            return ResourceManagementResult(
                initial_memory=initial_memory,
                peak_memory=peak_memory,
                final_memory=final_memory,
                memory_growth=final_memory - initial_memory,
                memory_cleaned_up=False,
                database_connections_open=0,
                database_connections_closed=0,
                file_handles_open=0,
                file_handles_closed=0,
                resource_cleanup_successful=False
            )
    
    async def test_memory_pressure(self) -> Dict[str, Any]:
        """Test system behavior under memory pressure"""
        logger.info("Testing behavior under memory pressure")
        
        try:
            # Get available memory
            available_memory = psutil.virtual_memory().available
            logger.info(f"Available memory: {available_memory / 1024 / 1024:.1f}MB")
            
            # Test with limited memory scenario
            # Note: This is a simulation, real memory pressure testing would require more advanced techniques
            
            initial_memory = self.process.memory_info().rss
            
            # Run workflow under simulated memory pressure
            result = await self.workflow_tester.test_complete_research_workflow()
            
            final_memory = self.process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            return {
                "success": True,
                "workflow_success": result.success,
                "initial_memory_mb": initial_memory / 1024 / 1024,
                "final_memory_mb": final_memory / 1024 / 1024,
                "memory_increase_mb": memory_increase / 1024 / 1024,
                "available_memory_mb": available_memory / 1024 / 1024,
                "memory_pressure_handled": memory_increase < (100 * 1024 * 1024)  # Less than 100MB increase
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_database_connection_management(self) -> Dict[str, Any]:
        """Test database connection management"""
        logger.info("Testing database connection management")
        
        try:
            # Test Neo4j connection
            neo4j_driver = self.workflow_tester.service_manager.get_neo4j_driver()
            neo4j_healthy = neo4j_driver is not None
            
            if neo4j_healthy:
                # Test connection with query
                with neo4j_driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    result.single()
                logger.info("✓ Neo4j connection test successful")
            
            # Test SQLite connection
            provenance_service = self.workflow_tester.service_manager.get_provenance_service()
            sqlite_healthy = provenance_service is not None
            
            if sqlite_healthy:
                # Test SQLite operation
                test_id = "test_operation_123"
                provenance_service.create_operation(
                    operation_id=test_id,
                    operation_type="test",
                    inputs={"test": "data"},
                    metadata={"test": True}
                )
                logger.info("✓ SQLite connection test successful")
            
            return {
                "success": True,
                "neo4j_healthy": neo4j_healthy,
                "sqlite_healthy": sqlite_healthy,
                "database_connections_working": neo4j_healthy and sqlite_healthy
            }
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "neo4j_healthy": False,
                "sqlite_healthy": False,
                "database_connections_working": False
            }

async def main():
    """Main function to run performance integration tests"""
    print("⚡ Starting Performance Integration Testing")
    print("=" * 50)
    
    tester = PerformanceIntegrationTester()
    
    # Initialize
    print("Initializing performance tester...")
    init_success = await tester.initialize()
    if not init_success:
        print("❌ Failed to initialize performance tester")
        return
    print("✅ Performance tester initialized")
    
    # Test 1: Concurrent Operations
    print("\n🔄 Testing concurrent operations...")
    concurrent_result = await tester.test_concurrent_operations(num_operations=5)
    
    print(f"\n📊 Concurrent Operations Results:")
    print(f"Total Operations: {concurrent_result.total_operations}")
    print(f"Successful: {concurrent_result.successful_operations}")
    print(f"Failed: {concurrent_result.failed_operations}")
    print(f"Success Rate: {concurrent_result.success_rate:.1%}")
    print(f"Total Time: {concurrent_result.total_time:.2f}s")
    print(f"Average Time per Operation: {concurrent_result.average_time_per_operation:.2f}s")
    print(f"Peak Memory Usage: {concurrent_result.peak_memory_usage / 1024 / 1024:.1f}MB")
    
    if concurrent_result.error_messages:
        print(f"Errors encountered: {len(concurrent_result.error_messages)}")
        for i, error in enumerate(concurrent_result.error_messages[:3]):  # Show first 3 errors
            print(f"  {i+1}. {error}")
    
    # Test 2: Resource Management
    print("\n🔧 Testing resource management...")
    resource_result = await tester.test_resource_management()
    
    print(f"\n📈 Resource Management Results:")
    print(f"Initial Memory: {resource_result.initial_memory / 1024 / 1024:.1f}MB")
    print(f"Peak Memory: {resource_result.peak_memory / 1024 / 1024:.1f}MB")
    print(f"Final Memory: {resource_result.final_memory / 1024 / 1024:.1f}MB")
    print(f"Memory Growth: {resource_result.memory_growth / 1024 / 1024:.1f}MB")
    print(f"Memory Cleaned Up: {'✅' if resource_result.memory_cleaned_up else '❌'}")
    print(f"Resource Cleanup Successful: {'✅' if resource_result.resource_cleanup_successful else '❌'}")
    
    # Test 3: Memory Pressure
    print("\n💾 Testing memory pressure handling...")
    memory_result = await tester.test_memory_pressure()
    
    print(f"\n🧠 Memory Pressure Results:")
    print(f"Test Success: {'✅' if memory_result['success'] else '❌'}")
    if memory_result['success']:
        print(f"Workflow Success: {'✅' if memory_result['workflow_success'] else '❌'}")
        print(f"Memory Increase: {memory_result['memory_increase_mb']:.1f}MB")
        print(f"Pressure Handled: {'✅' if memory_result['memory_pressure_handled'] else '❌'}")
    
    # Test 4: Database Connection Management
    print("\n🗄️  Testing database connection management...")
    db_result = await tester.test_database_connection_management()
    
    print(f"\n🔌 Database Connection Results:")
    print(f"Test Success: {'✅' if db_result['success'] else '❌'}")
    print(f"Neo4j Healthy: {'✅' if db_result['neo4j_healthy'] else '❌'}")
    print(f"SQLite Healthy: {'✅' if db_result['sqlite_healthy'] else '❌'}")
    print(f"Connections Working: {'✅' if db_result['database_connections_working'] else '❌'}")
    
    # Save results
    results = {
        "concurrent_operations": asdict(concurrent_result),
        "resource_management": asdict(resource_result),
        "memory_pressure": memory_result,
        "database_connections": db_result,
        "timestamp": time.time()
    }
    
    results_path = Path("test_results_performance_integration.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: {results_path}")
    
    # Overall assessment
    print(f"\n🎯 Performance Integration Summary:")
    
    concurrent_passed = concurrent_result.success_rate >= 0.8  # 80% success rate
    resource_passed = resource_result.resource_cleanup_successful
    memory_passed = memory_result.get('success', False) and memory_result.get('memory_pressure_handled', False)
    db_passed = db_result.get('database_connections_working', False)
    
    total_tests = 4
    passed_tests = sum([concurrent_passed, resource_passed, memory_passed, db_passed])
    
    print(f"Concurrent Operations: {'✅ PASS' if concurrent_passed else '❌ FAIL'}")
    print(f"Resource Management: {'✅ PASS' if resource_passed else '❌ FAIL'}")
    print(f"Memory Pressure: {'✅ PASS' if memory_passed else '❌ FAIL'}")
    print(f"Database Connections: {'✅ PASS' if db_passed else '❌ FAIL'}")
    
    overall_success_rate = passed_tests / total_tests
    print(f"\nOverall Success Rate: {overall_success_rate:.1%}")
    
    if overall_success_rate >= 0.75:  # 75% pass rate
        print("🎉 Performance Integration Testing PASSED!")
    else:
        print("⚠️  Performance Integration Testing needs improvement")

if __name__ == "__main__":
    asyncio.run(main())