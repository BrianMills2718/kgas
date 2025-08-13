"""
Custom exceptions for the core service layer.

This module defines exceptions used throughout the core services
for error handling and service coordination.
"""


class ServiceException(Exception):
    """Base exception for all service-related errors."""
    pass


class ServiceUnavailableError(ServiceException):
    """Raised when a required service is unavailable."""
    def __init__(self, service_name: str, message: str = None, remediation_steps: list = None):
        self.service_name = service_name
        self.remediation_steps = remediation_steps or []
        
        error_msg = message or f"Service '{service_name}' is unavailable"
        if self.remediation_steps:
            error_msg += "\n\nRemediation steps:"
            for i, step in enumerate(self.remediation_steps, 1):
                error_msg += f"\n{i}. {step}"
        
        super().__init__(error_msg)


class WorkflowExecutionError(ServiceException):
    """Raised when workflow execution fails."""
    def __init__(self, workflow_id: str, message: str = None):
        self.workflow_id = workflow_id
        super().__init__(message or f"Workflow '{workflow_id}' execution failed")


class CheckpointRestoreError(ServiceException):
    """Raised when checkpoint restoration fails."""
    def __init__(self, checkpoint_id: str, message: str = None):
        self.checkpoint_id = checkpoint_id
        super().__init__(message or f"Failed to restore from checkpoint '{checkpoint_id}'")


class ServiceConfigurationError(ServiceException):
    """Raised when service configuration is invalid."""
    pass


class ServiceInitializationError(ServiceException):
    """Raised when service initialization fails."""
    pass


class ResourceExhaustedError(ServiceException):
    """Raised when system resources are exhausted."""
    pass


class ServiceTimeoutError(ServiceException):
    """Raised when a service operation times out."""
    def __init__(self, operation: str, timeout_seconds: float):
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Operation '{operation}' timed out after {timeout_seconds} seconds")


class CircuitBreakerError(ServiceException):
    """Raised when circuit breaker is open and prevents operation execution."""
    def __init__(self, service_name: str, message: str = None):
        self.service_name = service_name
        super().__init__(message or f"Circuit breaker is open for service '{service_name}'")