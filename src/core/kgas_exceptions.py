"""
KGAS Comprehensive Error Handling Framework - Phase 9.1

Custom exception classes for all KGAS system components.
Follows fail-fast principle - no silent failures, all errors properly categorized and reported.
"""

import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Error severity levels for proper escalation"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Error categories for proper handling and recovery"""
    VALIDATION = "validation"
    PROCESSING = "processing"
    STORAGE = "storage"
    NETWORK = "network"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    INTEGRATION = "integration"


@dataclass
class ErrorContext:
    """Comprehensive error context for debugging and recovery"""
    operation: str
    component: str
    input_data: Dict[str, Any]
    system_state: Dict[str, Any]
    trace_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class KGASException(Exception):
    """
    Base exception for KGAS system.
    
    All KGAS exceptions inherit from this to provide:
    - Structured error information
    - Proper categorization and severity
    - Rich context for debugging
    - Recovery strategy hints
    """
    
    def __init__(self, 
                 message: str, 
                 error_code: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 category: ErrorCategory = ErrorCategory.PROCESSING,
                 context: Optional[ErrorContext] = None,
                 details: Optional[Dict[str, Any]] = None,
                 recovery_hint: Optional[str] = None,
                 caused_by: Optional[Exception] = None):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context
        self.details = details or {}
        self.recovery_hint = recovery_hint
        self.caused_by = caused_by
        self.timestamp = datetime.now().isoformat()
        self.stack_trace = traceback.format_exc()
        
        # Create comprehensive error message
        full_message = self._build_full_message()
        super().__init__(full_message)
    
    def _build_full_message(self) -> str:
        """Build comprehensive error message with all context"""
        parts = [
            f"[{self.error_code}] {self.message}",
            f"Severity: {self.severity.value}",
            f"Category: {self.category.value}",
            f"Timestamp: {self.timestamp}"
        ]
        
        if self.context:
            parts.extend([
                f"Operation: {self.context.operation}",
                f"Component: {self.context.component}"
            ])
        
        if self.recovery_hint:
            parts.append(f"Recovery: {self.recovery_hint}")
        
        if self.caused_by:
            parts.append(f"Caused by: {type(self.caused_by).__name__}: {str(self.caused_by)}")
        
        return "\n".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "context": self.context.__dict__ if self.context else None,
            "details": self.details,
            "recovery_hint": self.recovery_hint,
            "caused_by": str(self.caused_by) if self.caused_by else None,
            "stack_trace": self.stack_trace
        }


# Tool-Specific Exceptions

class PDFProcessingError(KGASException):
    """Raised when PDF processing fails"""
    
    def __init__(self, message: str, file_path: str, error_code: str = "PDF_PROCESSING_FAILED", **kwargs):
        self.file_path = file_path
        details = kwargs.get('details', {})
        details['file_path'] = file_path
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.PROCESSING,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check file format, permissions, and availability"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class EntityExtractionError(KGASException):
    """Raised when entity extraction fails"""
    
    def __init__(self, message: str, text_sample: str = "", error_code: str = "ENTITY_EXTRACTION_FAILED", **kwargs):
        self.text_sample = text_sample[:200] + "..." if len(text_sample) > 200 else text_sample
        details = kwargs.get('details', {})
        details['text_sample'] = self.text_sample
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.PROCESSING,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check text quality, NLP model availability, and input format"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class DatabaseError(KGASException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: str, error_code: str = "DATABASE_OPERATION_FAILED", **kwargs):
        self.operation = operation
        details = kwargs.get('details', {})
        details['database_operation'] = operation
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.STORAGE,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check database connectivity, permissions, and query syntax"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class ServiceInitializationError(KGASException):
    """Raised when service initialization fails"""
    
    def __init__(self, message: str, service_name: str, error_code: str = "SERVICE_INIT_FAILED", **kwargs):
        self.service_name = service_name
        details = kwargs.get('details', {})
        details['service_name'] = service_name
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.CONFIGURATION,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check service dependencies, configuration, and resource availability"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class ConfigurationError(KGASException):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str, config_key: str = "", error_code: str = "CONFIGURATION_ERROR", **kwargs):
        self.config_key = config_key
        details = kwargs.get('details', {})
        details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.CONFIGURATION,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check configuration file format, required keys, and value types"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class ValidationError(KGASException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field_name: str = "", expected: str = "", actual: str = "", 
                 error_code: str = "VALIDATION_FAILED", **kwargs):
        self.field_name = field_name
        self.expected = expected
        self.actual = actual
        
        details = kwargs.get('details', {})
        details.update({
            'field_name': field_name,
            'expected': expected,
            'actual': actual
        })
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.VALIDATION,
            severity=kwargs.get('severity', ErrorSeverity.WARNING),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', f"Provide valid {field_name}: expected {expected}, got {actual}"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class ResourceExhaustionError(KGASException):
    """Raised when system resources are exhausted"""
    
    def __init__(self, message: str, resource_type: str, current_usage: str = "", 
                 limit: str = "", error_code: str = "RESOURCE_EXHAUSTED", **kwargs):
        self.resource_type = resource_type
        self.current_usage = current_usage
        self.limit = limit
        
        details = kwargs.get('details', {})
        details.update({
            'resource_type': resource_type,
            'current_usage': current_usage,
            'limit': limit
        })
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.RESOURCE,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', f"Free up {resource_type} resources or increase limits"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class NetworkError(KGASException):
    """Raised when network operations fail"""
    
    def __init__(self, message: str, endpoint: str = "", operation: str = "", 
                 error_code: str = "NETWORK_ERROR", **kwargs):
        self.endpoint = endpoint
        self.operation = operation
        
        details = kwargs.get('details', {})
        details.update({
            'endpoint': endpoint,
            'operation': operation
        })
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.NETWORK,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check network connectivity, endpoint availability, and authentication"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class SecurityError(KGASException):
    """Raised when security violations occur"""
    
    def __init__(self, message: str, security_context: str = "", error_code: str = "SECURITY_VIOLATION", **kwargs):
        self.security_context = security_context
        details = kwargs.get('details', {})
        details['security_context'] = security_context
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.SECURITY,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check authentication, authorization, and access permissions"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


class IntegrationError(KGASException):
    """Raised when system integration fails"""
    
    def __init__(self, message: str, integration_point: str, error_code: str = "INTEGRATION_FAILED", **kwargs):
        self.integration_point = integration_point
        details = kwargs.get('details', {})
        details['integration_point'] = integration_point
        
        super().__init__(
            message=message,
            error_code=error_code,
            category=ErrorCategory.INTEGRATION,
            severity=kwargs.get('severity', ErrorSeverity.ERROR),
            details=details,
            recovery_hint=kwargs.get('recovery_hint', "Check integration configuration, compatibility, and dependencies"),
            **{k: v for k, v in kwargs.items() if k not in ['details', 'severity', 'recovery_hint']}
        )


# Convenience functions for common error patterns

def validate_not_none(value: Any, field_name: str, operation: str = "operation") -> None:
    """Validate that a value is not None"""
    if value is None:
        raise ValidationError(
            message=f"Required field '{field_name}' cannot be None",
            field_name=field_name,
            expected="non-None value",
            actual="None",
            context=ErrorContext(
                operation=operation,
                component="validation",
                input_data={field_name: value},
                system_state={}
            )
        )


def validate_not_empty(value: str, field_name: str, operation: str = "operation") -> None:
    """Validate that a string value is not empty"""
    if not value or not value.strip():
        raise ValidationError(
            message=f"Required field '{field_name}' cannot be empty",
            field_name=field_name,
            expected="non-empty string",
            actual=f"'{value}'",
            context=ErrorContext(
                operation=operation,
                component="validation",
                input_data={field_name: value},
                system_state={}
            )
        )


def validate_type(value: Any, expected_type: type, field_name: str, operation: str = "operation") -> None:
    """Validate that a value is of the expected type"""
    if not isinstance(value, expected_type):
        raise ValidationError(
            message=f"Field '{field_name}' must be of type {expected_type.__name__}",
            field_name=field_name,
            expected=expected_type.__name__,
            actual=type(value).__name__,
            context=ErrorContext(
                operation=operation,
                component="validation",
                input_data={field_name: value},
                system_state={}
            )
        )


def validate_range(value: float, min_val: float, max_val: float, field_name: str, operation: str = "operation") -> None:
    """Validate that a numeric value is within range"""
    if not (min_val <= value <= max_val):
        raise ValidationError(
            message=f"Field '{field_name}' must be between {min_val} and {max_val}",
            field_name=field_name,
            expected=f"value between {min_val} and {max_val}",
            actual=str(value),
            context=ErrorContext(
                operation=operation,
                component="validation",
                input_data={field_name: value},
                system_state={}
            )
        )


# Error collection and reporting utilities

class ErrorCollector:
    """Collect and categorize errors for batch reporting"""
    
    def __init__(self):
        self.errors: List[KGASException] = []
        self.warnings: List[KGASException] = []
        self.criticals: List[KGASException] = []
    
    def add_error(self, error: KGASException) -> None:
        """Add error to appropriate collection based on severity"""
        if error.severity == ErrorSeverity.CRITICAL or error.severity == ErrorSeverity.FATAL:
            self.criticals.append(error)
        elif error.severity == ErrorSeverity.WARNING:
            self.warnings.append(error)
        else:
            self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Check if any errors were collected"""
        return len(self.errors) > 0 or len(self.warnings) > 0 or len(self.criticals) > 0
    
    def has_critical_errors(self) -> bool:
        """Check if any critical errors were collected"""
        return len(self.criticals) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collected errors"""
        return {
            "total_errors": len(self.errors) + len(self.warnings) + len(self.criticals),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "criticals": len(self.criticals),
            "error_codes": [e.error_code for e in self.errors + self.warnings + self.criticals],
            "categories": list(set([e.category.value for e in self.errors + self.warnings + self.criticals]))
        }
    
    def raise_if_critical(self) -> None:
        """Raise the first critical error if any exist"""
        if self.criticals:
            raise self.criticals[0]
    
    def clear(self) -> None:
        """Clear all collected errors"""
        self.errors.clear()
        self.warnings.clear()
        self.criticals.clear()


if __name__ == "__main__":
    # Test the error handling framework
    try:
        # Test validation error
        validate_not_none(None, "test_field", "test_operation")
    except ValidationError as e:
        print("Validation Error Test:", e.to_dict())
    
    try:
        # Test PDF processing error
        raise PDFProcessingError(
            message="Failed to extract text from corrupted PDF",
            file_path="/path/to/test.pdf",
            context=ErrorContext(
                operation="pdf_extraction",
                component="T01_PDF_LOADER",
                input_data={"file_path": "/path/to/test.pdf"},
                system_state={"memory_usage": "high"}
            )
        )
    except PDFProcessingError as e:
        print("PDF Processing Error Test:", e.to_dict())
    
    # Test error collector
    collector = ErrorCollector()
    collector.add_error(ValidationError("Test validation error", "test_field"))
    collector.add_error(DatabaseError("Test database error", "insert"))
    print("Error Collector Summary:", collector.get_summary())
    
    print("✅ Error handling framework tests completed")