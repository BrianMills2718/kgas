#!/usr/bin/env python3
"""
Comprehensive Error Handling System Test - Phase 9.1

Tests all aspects of the KGAS error handling framework:
- Custom exception classes
- Error handler recovery strategies
- Error reporting and statistics
- Integration with existing tools

NO MOCKS - Tests real error conditions and recovery mechanisms.
"""

import os
import sys
import time
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.kgas_exceptions import (
    KGASException, ErrorSeverity, ErrorCategory, ErrorContext,
    PDFProcessingError, EntityExtractionError, DatabaseError,
    ServiceInitializationError, ConfigurationError, ValidationError,
    ResourceExhaustionError, NetworkError, SecurityError, IntegrationError,
    validate_not_none, validate_not_empty, validate_type, validate_range,
    ErrorCollector
)

from src.core.error_handler import (
    KGASErrorHandler, RecoveryStrategy, RecoveryAction, 
    get_error_handler, handle_kgas_error
)


class ErrorHandlingTests:
    """Comprehensive test suite for error handling framework"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = Path(tempfile.mkdtemp())
        print(f"Test temp directory: {self.temp_dir}")
    
    def run_all_tests(self) -> bool:
        """Run all error handling tests"""
        print("=" * 70)
        print("KGAS ERROR HANDLING COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        test_methods = [
            self.test_exception_creation,
            self.test_exception_serialization,
            self.test_validation_functions,
            self.test_error_collector,
            self.test_error_handler_initialization,
            self.test_error_logging_and_stats,
            self.test_recovery_strategies,
            self.test_error_escalation,
            self.test_error_reporting,
            self.test_concurrent_error_handling,
            self.test_integration_with_tools,
            self.test_performance_under_load
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
    
    def test_exception_creation(self) -> bool:
        """Test custom exception creation and properties"""
        try:
            # Test base KGASException
            context = ErrorContext(
                operation="test_operation",
                component="test_component",
                input_data={"test": "data"},
                system_state={"memory": "normal"}
            )
            
            base_error = KGASException(
                message="Test base error",
                error_code="TEST_ERROR",
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.PROCESSING,
                context=context,
                details={"test_detail": "value"},
                recovery_hint="Try again"
            )
            
            assert base_error.message == "Test base error"
            assert base_error.error_code == "TEST_ERROR"
            assert base_error.severity == ErrorSeverity.ERROR
            assert base_error.category == ErrorCategory.PROCESSING
            assert base_error.recovery_hint == "Try again"
            assert base_error.context == context
            assert "test_detail" in base_error.details
            
            # Test PDF processing error
            pdf_error = PDFProcessingError(
                message="Failed to process PDF",
                file_path="/test/file.pdf",
                severity=ErrorSeverity.ERROR
            )
            
            assert pdf_error.file_path == "/test/file.pdf"
            assert pdf_error.category == ErrorCategory.PROCESSING
            assert "file_path" in pdf_error.details
            
            # Test Entity extraction error
            entity_error = EntityExtractionError(
                message="NLP model not found",
                text_sample="This is a test sample for entity extraction",
                error_code="NLP_MODEL_MISSING"
            )
            
            assert entity_error.error_code == "NLP_MODEL_MISSING"
            assert len(entity_error.text_sample) > 0
            assert "text_sample" in entity_error.details
            
            # Test Database error
            db_error = DatabaseError(
                message="Connection timeout",
                operation="insert",
                error_code="DB_TIMEOUT"
            )
            
            assert db_error.operation == "insert"
            assert db_error.error_code == "DB_TIMEOUT"
            assert db_error.category == ErrorCategory.STORAGE
            
            return True
            
        except Exception as e:
            print(f"Exception creation test failed: {e}")
            return False
    
    def test_exception_serialization(self) -> bool:
        """Test exception serialization to dict/JSON"""
        try:
            context = ErrorContext(
                operation="serialization_test",
                component="test_component",
                input_data={"data": "test"},
                system_state={}
            )
            
            error = ValidationError(
                message="Invalid input",
                field_name="test_field",
                expected="string",
                actual="integer",
                context=context
            )
            
            # Test to_dict conversion
            error_dict = error.to_dict()
            
            required_keys = [
                "error_code", "message", "severity", "category", 
                "timestamp", "context", "details", "recovery_hint"
            ]
            
            for key in required_keys:
                assert key in error_dict, f"Missing key: {key}"
            
            # Test JSON serialization
            json_str = json.dumps(error_dict, default=str)
            parsed_back = json.loads(json_str)
            
            assert parsed_back["error_code"] == error.error_code
            assert parsed_back["message"] == error.message
            
            return True
            
        except Exception as e:
            print(f"Serialization test failed: {e}")
            return False
    
    def test_validation_functions(self) -> bool:
        """Test validation utility functions"""
        try:
            # Test validate_not_none
            try:
                validate_not_none(None, "test_field", "test_operation")
                return False  # Should have raised exception
            except ValidationError as e:
                assert e.field_name == "test_field"
                assert "None" in e.message
            
            # Test validate_not_empty
            try:
                validate_not_empty("", "empty_field", "test_operation")
                return False  # Should have raised exception
            except ValidationError as e:
                assert e.field_name == "empty_field"
                assert "empty" in e.message
            
            # Test validate_type
            try:
                validate_type("string", int, "type_field", "test_operation")
                return False  # Should have raised exception
            except ValidationError as e:
                assert e.field_name == "type_field"
                assert "int" in e.expected
                assert "str" in e.actual
            
            # Test validate_range
            try:
                validate_range(150, 0, 100, "range_field", "test_operation")
                return False  # Should have raised exception
            except ValidationError as e:
                assert e.field_name == "range_field"
                assert "100" in e.expected
                assert "150" in e.actual
            
            # Test successful validation
            validate_not_none("value", "good_field")
            validate_not_empty("not empty", "good_field")
            validate_type(42, int, "good_field")
            validate_range(50, 0, 100, "good_field")
            
            return True
            
        except Exception as e:
            print(f"Validation functions test failed: {e}")
            return False
    
    def test_error_collector(self) -> bool:
        """Test error collector functionality"""
        try:
            collector = ErrorCollector()
            
            # Add various errors
            collector.add_error(ValidationError("Test validation", "field1"))
            collector.add_error(DatabaseError("Test database error", "select"))
            collector.add_error(PDFProcessingError("Test PDF error", "/test.pdf", 
                                                  severity=ErrorSeverity.CRITICAL))
            
            # Test has_errors
            assert collector.has_errors() == True
            
            # Test has_critical_errors
            assert collector.has_critical_errors() == True
            
            # Test summary
            summary = collector.get_summary()
            assert summary["total_errors"] == 3
            assert summary["criticals"] == 1
            assert summary["errors"] == 1  # Database error
            assert summary["warnings"] == 1  # Validation error
            
            # Test error codes
            assert "VALIDATION_FAILED" in summary["error_codes"]
            assert "DATABASE_OPERATION_FAILED" in summary["error_codes"]
            assert "PDF_PROCESSING_FAILED" in summary["error_codes"]
            
            # Test categories
            assert "validation" in summary["categories"]
            assert "storage" in summary["categories"]
            assert "processing" in summary["categories"]
            
            # Test clear
            collector.clear()
            assert collector.has_errors() == False
            assert collector.get_summary()["total_errors"] == 0
            
            return True
            
        except Exception as e:
            print(f"Error collector test failed: {e}")
            return False
    
    def test_error_handler_initialization(self) -> bool:
        """Test error handler initialization and configuration"""
        try:
            # Test default initialization
            handler = KGASErrorHandler()
            assert handler.auto_recovery_enabled == True
            assert handler.max_history_size == 1000
            assert len(handler.recovery_strategies) > 0
            
            # Test custom configuration
            custom_config = {
                'max_history_size': 500,
                'error_threshold_window': 600,
                'critical_error_threshold': 3,
                'auto_recovery_enabled': False,
                'error_reports_dir': str(self.temp_dir / 'error_reports')
            }
            
            custom_handler = KGASErrorHandler(custom_config)
            assert custom_handler.max_history_size == 500
            assert custom_handler.error_threshold_window == 600
            assert custom_handler.auto_recovery_enabled == False
            
            # Test global handler
            global_handler = get_error_handler()
            assert global_handler is not None
            
            # Test that subsequent calls return same instance
            same_handler = get_error_handler()
            assert global_handler is same_handler
            
            return True
            
        except Exception as e:
            print(f"Error handler initialization test failed: {e}")
            return False
    
    def test_error_logging_and_stats(self) -> bool:
        """Test error logging and statistics tracking"""
        try:
            handler = KGASErrorHandler()
            
            # Create and handle multiple errors
            errors = [
                ValidationError("Test validation 1", "field1"),
                ValidationError("Test validation 2", "field2"),
                DatabaseError("Test database error", "insert"),
                PDFProcessingError("Test PDF error", "/test.pdf")
            ]
            
            for error in errors:
                handler.handle_error(error)
            
            # Test error statistics
            stats = handler.get_error_statistics()
            
            assert stats["total_errors"] == 4
            assert stats["unique_error_codes"] == 3  # 2 validation, 1 db, 1 pdf
            
            # Test error counts by severity
            severity_counts = stats["error_by_severity"]
            assert "warning" in severity_counts  # Validation errors
            assert "error" in severity_counts     # Database and PDF errors
            
            # Test error counts by category
            category_counts = stats["error_by_category"]
            assert "validation" in category_counts
            assert "storage" in category_counts
            assert "processing" in category_counts
            
            # Test most common errors
            most_common = stats["most_common_errors"]
            assert len(most_common) > 0
            assert most_common[0]["count"] == 2  # Validation errors are most common
            
            # Test system health score
            health_score = stats["system_health_score"]
            assert 0 <= health_score <= 100
            
            return True
            
        except Exception as e:
            print(f"Error logging and stats test failed: {e}")
            return False
    
    def test_recovery_strategies(self) -> bool:
        """Test error recovery strategies"""
        try:
            handler = KGASErrorHandler()
            
            # Test custom recovery strategy registration
            recovery_count = 0
            
            def custom_recovery_function(error, context):
                nonlocal recovery_count
                recovery_count += 1
                return True  # Simulate successful recovery
            
            custom_recovery = RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=2,
                backoff_seconds=0.1,
                recovery_function=custom_recovery_function
            )
            
            handler.register_recovery_strategy("CUSTOM_ERROR", custom_recovery)
            
            # Create custom error type
            custom_error = KGASException(
                message="Test custom error",
                error_code="CUSTOM_ERROR",
                severity=ErrorSeverity.ERROR
            )
            
            # Handle the error (should trigger recovery)
            recovery_success = handler.handle_error(custom_error)
            assert recovery_success == True
            assert recovery_count > 0
            
            # Test recovery statistics
            stats = handler.get_error_statistics()
            recovery_stats = stats["recovery_statistics"]
            assert recovery_stats["total_recovery_attempts"] > 0
            assert recovery_stats["total_recovery_successes"] > 0
            assert recovery_stats["recovery_success_rate"] > 0
            
            # Test default recovery strategies exist
            default_strategies = [
                "DATABASE_CONNECTION_FAILED",
                "PDF_PROCESSING_FAILED",
                "RESOURCE_EXHAUSTED",
                "NETWORK_TIMEOUT",
                "CONFIGURATION_ERROR",
                "SECURITY_VIOLATION"
            ]
            
            for strategy in default_strategies:
                assert strategy in handler.recovery_strategies
            
            return True
            
        except Exception as e:
            print(f"Recovery strategies test failed: {e}")
            return False
    
    def test_error_escalation(self) -> bool:
        """Test error escalation logic"""
        try:
            handler = KGASErrorHandler()
            
            # Test immediate escalation for critical errors
            critical_error = KGASException(
                message="Critical system failure",
                error_code="SYSTEM_FAILURE",
                severity=ErrorSeverity.CRITICAL
            )
            
            # Should not recover critical errors
            recovery_success = handler.handle_error(critical_error)
            assert recovery_success == False
            
            # Test security error escalation
            security_error = SecurityError(
                message="Unauthorized access attempt",
                security_context="login"
            )
            
            recovery_success = handler.handle_error(security_error)
            assert recovery_success == False
            
            # Test threshold-based escalation
            # Create multiple errors of same type to trigger threshold
            for i in range(6):  # Exceed default threshold of 5
                threshold_error = KGASException(
                    message=f"Threshold test error {i}",
                    error_code="THRESHOLD_TEST",
                    severity=ErrorSeverity.ERROR
                )
                handler.handle_error(threshold_error)
            
            # Check that error statistics tracked the threshold
            stats = handler.get_error_statistics()
            assert stats["total_errors"] >= 6
            
            return True
            
        except Exception as e:
            print(f"Error escalation test failed: {e}")
            return False
    
    def test_error_reporting(self) -> bool:
        """Test error report generation"""
        try:
            # Use custom error reports directory
            reports_dir = self.temp_dir / "test_error_reports"
            config = {"error_reports_dir": str(reports_dir)}
            handler = KGASErrorHandler(config)
            
            # Generate some errors to report on
            errors = [
                ValidationError("Report test validation", "field1"),
                DatabaseError("Report test database", "select"),
                PDFProcessingError("Report test PDF", "/report_test.pdf")
            ]
            
            for error in errors:
                handler.handle_error(error)
            
            # Generate error report
            report_file = handler.generate_error_report("TEST_REPORT")
            
            assert report_file.exists()
            assert report_file.suffix == ".json"
            
            # Read and validate report content
            with open(report_file, 'r') as f:
                report_data = json.load(f)
            
            required_sections = [
                "report_name", "generated_at", "statistics", 
                "recent_errors", "error_stats", "recovery_strategies"
            ]
            
            for section in required_sections:
                assert section in report_data, f"Missing report section: {section}"
            
            # Validate statistics section
            stats = report_data["statistics"]
            assert stats["total_errors"] == 3
            assert stats["unique_error_codes"] == 3
            
            # Validate recent errors section
            recent_errors = report_data["recent_errors"]
            assert len(recent_errors) == 3
            assert all("error_code" in error for error in recent_errors)
            
            return True
            
        except Exception as e:
            print(f"Error reporting test failed: {e}")
            return False
    
    def test_concurrent_error_handling(self) -> bool:
        """Test error handling under concurrent access"""
        try:
            import threading
            import random
            
            handler = KGASErrorHandler()
            errors_handled = []
            
            def error_generator(thread_id: int):
                """Generate errors from multiple threads"""
                for i in range(10):
                    error_type = random.choice([
                        ValidationError, DatabaseError, PDFProcessingError
                    ])
                    
                    if error_type == ValidationError:
                        error = ValidationError(f"Thread {thread_id} validation {i}", f"field_{i}")
                    elif error_type == DatabaseError:
                        error = DatabaseError(f"Thread {thread_id} database {i}", f"operation_{i}")
                    else:
                        error = PDFProcessingError(f"Thread {thread_id} PDF {i}", f"/test_{i}.pdf")
                    
                    handler.handle_error(error)
                    errors_handled.append(error)
                    time.sleep(0.01)  # Small delay
            
            # Create multiple threads
            threads = []
            for thread_id in range(5):
                thread = threading.Thread(target=error_generator, args=(thread_id,))
                threads.append(thread)
            
            # Start threads
            for thread in threads:
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Verify all errors were handled
            stats = handler.get_error_statistics()
            assert stats["total_errors"] == 50  # 5 threads * 10 errors each
            
            # Verify thread safety by checking no data corruption
            assert len(errors_handled) == 50
            assert stats["unique_error_codes"] == 3
            
            return True
            
        except Exception as e:
            print(f"Concurrent error handling test failed: {e}")
            return False
    
    def test_integration_with_tools(self) -> bool:
        """Test error handling integration with KGAS tools"""
        try:
            handler = get_error_handler()
            
            # Test tool-specific errors with proper context
            context = ErrorContext(
                operation="pdf_processing",
                component="T01_PDF_LOADER",
                input_data={"file_path": "/nonexistent.pdf"},
                system_state={"memory_usage": "normal"}
            )
            
            pdf_error = PDFProcessingError(
                message="File not found",
                file_path="/nonexistent.pdf",
                error_code="PDF_FILE_NOT_FOUND",
                context=context
            )
            
            # Use convenience function
            recovery_success = handle_kgas_error(pdf_error, {"additional": "context"})
            
            # Verify error was handled
            stats = handler.get_error_statistics()
            assert stats["total_errors"] >= 1
            
            # Test entity extraction error
            entity_context = ErrorContext(
                operation="entity_extraction",
                component="T23A_SPACY_NER",
                input_data={"text": "Test text for entity extraction"},
                system_state={"model_loaded": False}
            )
            
            entity_error = EntityExtractionError(
                message="SpaCy model not loaded",
                text_sample="Test text for entity extraction",
                error_code="SPACY_MODEL_NOT_LOADED",
                context=entity_context
            )
            
            handle_kgas_error(entity_error)
            
            # Test database error
            db_context = ErrorContext(
                operation="data_storage",
                component="T31_ENTITY_BUILDER",
                input_data={"entities": []},
                system_state={"database_connected": False}
            )
            
            db_error = DatabaseError(
                message="Neo4j connection lost",
                operation="create_entity",
                error_code="NEO4J_CONNECTION_LOST",
                context=db_context
            )
            
            handle_kgas_error(db_error)
            
            # Verify all errors were tracked
            final_stats = handler.get_error_statistics()
            assert final_stats["total_errors"] >= 3
            
            return True
            
        except Exception as e:
            print(f"Tool integration test failed: {e}")
            return False
    
    def test_performance_under_load(self) -> bool:
        """Test error handling performance under load"""
        try:
            handler = KGASErrorHandler()
            
            # Measure performance of error handling
            start_time = time.time()
            
            # Generate 1000 errors rapidly
            for i in range(1000):
                error = ValidationError(f"Load test error {i}", f"field_{i % 10}")
                handler.handle_error(error)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Performance requirements
            max_time_per_error = 0.01  # 10ms per error maximum
            actual_time_per_error = total_time / 1000
            
            print(f"  Performance: {actual_time_per_error*1000:.2f}ms per error")
            
            # Verify performance is acceptable
            assert actual_time_per_error < max_time_per_error, \
                f"Error handling too slow: {actual_time_per_error*1000:.2f}ms > {max_time_per_error*1000}ms"
            
            # Verify all errors were tracked
            stats = handler.get_error_statistics()
            assert stats["total_errors"] == 1000
            
            # Verify memory usage is reasonable
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            print(f"  Memory usage: {memory_mb:.1f}MB")
            
            # Memory should be less than 100MB for 1000 errors
            assert memory_mb < 100, f"Memory usage too high: {memory_mb:.1f}MB"
            
            return True
            
        except Exception as e:
            print(f"Performance test failed: {e}")
            return False
    
    def generate_test_report(self) -> None:
        """Generate comprehensive test report"""
        report_file = self.temp_dir / "error_handling_test_report.json"
        
        report_data = {
            "test_suite": "KGAS Error Handling Comprehensive Tests",
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
        test_suite = ErrorHandlingTests()
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 ALL ERROR HANDLING TESTS PASSED!")
            print("✅ Phase 9.1: Comprehensive error handling implementation complete")
            return 0
        else:
            print("\n❌ SOME ERROR HANDLING TESTS FAILED!")
            print("🔧 Review test results and fix failing components")
            return 1
            
    except Exception as e:
        print(f"\n💥 TEST SUITE EXECUTION FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())