"""
KGAS Comprehensive Error Handler - Phase 9.1

Centralized error handling, recovery, and reporting system.
Manages all KGAS exceptions with fail-fast behavior and recovery strategies.

DEVELOPMENT MODE: Fallback recovery disabled for fail-fast development.
POST-DEVELOPMENT: To enable graceful degradation in production:
1. Uncomment FALLBACK = "fallback" in RecoveryStrategy enum
2. Uncomment fallback recovery strategy registration (PDF processing)
3. Uncomment fallback recovery execution in _execute_recovery()
4. Implement _fallback_recovery() method for graceful degradation logic
"""

import logging
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from .kgas_exceptions import (
    KGASException, ErrorSeverity, ErrorCategory, ErrorContext,
    PDFProcessingError, EntityExtractionError, DatabaseError,
    ServiceInitializationError, ConfigurationError, ValidationError,
    ResourceExhaustionError, NetworkError, SecurityError, IntegrationError
)


class RecoveryStrategy(Enum):
    """Available recovery strategies"""
    RETRY = "retry"
    # FALLBACK = "fallback"  # DISABLED FOR DEVELOPMENT - Enable post-development for production graceful degradation
    RESET = "reset"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    TERMINATE = "terminate"


@dataclass
class RecoveryAction:
    """Recovery action configuration"""
    strategy: RecoveryStrategy
    max_attempts: int
    backoff_seconds: float
    success_condition: Optional[Callable] = None
    recovery_function: Optional[Callable] = None
    escalation_threshold: int = 3


@dataclass
class ErrorStats:
    """Error statistics for monitoring"""
    error_code: str
    count: int
    first_occurrence: datetime
    last_occurrence: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    recovery_attempts: int
    recovery_successes: int
    recovery_failures: int


class KGASErrorHandler:
    """
    Comprehensive error handler for the KGAS system.
    
    Features:
    - Centralized error logging and reporting
    - Automatic recovery strategies
    - Error pattern analysis
    - Performance impact monitoring
    - Fail-fast behavior with proper escalation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Error tracking
        self.error_stats: Dict[str, ErrorStats] = {}
        self.error_history: List[KGASException] = []
        self.recovery_strategies: Dict[str, RecoveryAction] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration
        self.max_history_size = self.config.get('max_history_size', 1000)
        self.error_threshold_window = self.config.get('error_threshold_window', 300)  # 5 minutes
        self.critical_error_threshold = self.config.get('critical_error_threshold', 5)
        self.auto_recovery_enabled = self.config.get('auto_recovery_enabled', True)
        
        # Initialize default recovery strategies
        self._setup_default_recovery_strategies()
        
        # Error reporting
        self.error_reports_dir = Path(self.config.get('error_reports_dir', 'error_reports'))
        self.error_reports_dir.mkdir(exist_ok=True)
    
    def _setup_default_recovery_strategies(self) -> None:
        """Setup default recovery strategies for common error types"""
        
        # Database connection errors - retry with backoff
        self.register_recovery_strategy(
            "DATABASE_CONNECTION_FAILED",
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=3,
                backoff_seconds=2.0,
                escalation_threshold=3
            )
        )
        
        # PDF processing errors - DEVELOPMENT: fail fast, POST-DEVELOPMENT: enable fallback to text extraction
        # DISABLED FOR DEVELOPMENT - Uncomment and change TERMINATE to FALLBACK post-development:
        # self.register_recovery_strategy(
        #     "PDF_PROCESSING_FAILED",
        #     RecoveryAction(
        #         strategy=RecoveryStrategy.FALLBACK,
        #         max_attempts=1,
        #         backoff_seconds=0.0,
        #         escalation_threshold=2
        #     )
        # )
        
        # DEVELOPMENT MODE: PDF processing errors terminate with clear message
        self.register_recovery_strategy(
            "PDF_PROCESSING_FAILED",
            RecoveryAction(
                strategy=RecoveryStrategy.TERMINATE,
                max_attempts=1,
                backoff_seconds=0.0,
                escalation_threshold=1
            )
        )
        
        # Memory exhaustion - reset and clear caches
        self.register_recovery_strategy(
            "RESOURCE_EXHAUSTED",
            RecoveryAction(
                strategy=RecoveryStrategy.RESET,
                max_attempts=2,
                backoff_seconds=1.0,
                escalation_threshold=1
            )
        )
        
        # Network timeouts - retry with exponential backoff
        self.register_recovery_strategy(
            "NETWORK_TIMEOUT",
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=3,
                backoff_seconds=1.0,
                escalation_threshold=3
            )
        )
        
        # Configuration errors - terminate immediately
        self.register_recovery_strategy(
            "CONFIGURATION_ERROR",
            RecoveryAction(
                strategy=RecoveryStrategy.TERMINATE,
                max_attempts=0,
                backoff_seconds=0.0,
                escalation_threshold=1
            )
        )
        
        # Security violations - terminate immediately
        self.register_recovery_strategy(
            "SECURITY_VIOLATION",
            RecoveryAction(
                strategy=RecoveryStrategy.TERMINATE,
                max_attempts=0,
                backoff_seconds=0.0,
                escalation_threshold=1
            )
        )
    
    def handle_error(self, error: KGASException, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle error with appropriate response and recovery.
        
        Returns True if error was recovered, False if escalation needed.
        """
        with self._lock:
            try:
                # Log the error immediately
                self._log_error(error, context)
                
                # Update error statistics
                self._update_error_stats(error)
                
                # Add to error history
                self._add_to_history(error)
                
                # Check for error patterns that require immediate escalation
                if self._should_escalate_immediately(error):
                    self._escalate_error(error, "Immediate escalation required")
                    return False
                
                # Attempt recovery if enabled and strategy exists
                if self.auto_recovery_enabled:
                    recovery_successful = self._attempt_recovery(error, context)
                    if recovery_successful:
                        self.logger.info(f"Successfully recovered from error: {error.error_code}")
                        return True
                
                # Check if we've exceeded error thresholds
                if self._error_threshold_exceeded(error):
                    self._escalate_error(error, "Error threshold exceeded")
                    return False
                
                # If we get here, error was logged but not recovered
                return False
                
            except Exception as handler_error:
                # Error handler itself failed - this is critical
                self.logger.critical(f"Error handler failed: {handler_error}", exc_info=True)
                self._escalate_critical_failure(error, handler_error)
                return False
    
    def register_recovery_strategy(self, error_code: str, recovery_action: RecoveryAction) -> None:
        """Register a recovery strategy for specific error type"""
        with self._lock:
            self.recovery_strategies[error_code] = recovery_action
            self.logger.debug(f"Registered recovery strategy for {error_code}: {recovery_action.strategy.value}")
    
    def _log_error(self, error: KGASException, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error with appropriate level and context"""
        error_dict = error.to_dict()
        if context:
            error_dict['handler_context'] = context
        
        # Rename 'message' key to avoid conflict with logging system
        if 'message' in error_dict:
            error_dict['error_message'] = error_dict.pop('message')
        
        # Log based on severity
        if error.severity == ErrorSeverity.FATAL:
            self.logger.critical(f"FATAL ERROR: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.ERROR:
            self.logger.error(f"ERROR: {error.message}", extra=error_dict)
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(f"WARNING: {error.message}", extra=error_dict)
        else:
            self.logger.info(f"INFO: {error.message}", extra=error_dict)
    
    def _update_error_stats(self, error: KGASException) -> None:
        """Update error statistics"""
        error_code = error.error_code
        now = datetime.now()
        
        if error_code in self.error_stats:
            stats = self.error_stats[error_code]
            stats.count += 1
            stats.last_occurrence = now
        else:
            self.error_stats[error_code] = ErrorStats(
                error_code=error_code,
                count=1,
                first_occurrence=now,
                last_occurrence=now,
                severity=error.severity,
                category=error.category,
                recovery_attempts=0,
                recovery_successes=0,
                recovery_failures=0
            )
    
    def _add_to_history(self, error: KGASException) -> None:
        """Add error to history with size limit"""
        self.error_history.append(error)
        
        # Maintain history size limit
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _should_escalate_immediately(self, error: KGASException) -> bool:
        """Check if error should be escalated immediately"""
        # Always escalate fatal and security errors
        if error.severity in [ErrorSeverity.FATAL, ErrorSeverity.CRITICAL]:
            return True
        
        if error.category == ErrorCategory.SECURITY:
            return True
        
        # Escalate if error has no recovery strategy and is severe
        if error.error_code not in self.recovery_strategies and error.severity == ErrorSeverity.ERROR:
            return True
        
        return False
    
    def _attempt_recovery(self, error: KGASException, context: Optional[Dict[str, Any]] = None) -> bool:
        """Attempt to recover from error using registered strategy"""
        recovery_action = self.recovery_strategies.get(error.error_code)
        if not recovery_action:
            self.logger.debug(f"No recovery strategy for error: {error.error_code}")
            return False
        
        # Update recovery attempt statistics
        if error.error_code in self.error_stats:
            self.error_stats[error.error_code].recovery_attempts += 1
        
        try:
            success = False
            
            if recovery_action.strategy == RecoveryStrategy.RETRY:
                success = self._retry_recovery(error, recovery_action, context)
            # elif recovery_action.strategy == RecoveryStrategy.FALLBACK:  # DISABLED FOR DEVELOPMENT
            #     success = self._fallback_recovery(error, recovery_action, context)  # Enable post-development
            elif recovery_action.strategy == RecoveryStrategy.RESET:
                success = self._reset_recovery(error, recovery_action, context)
            elif recovery_action.strategy == RecoveryStrategy.IGNORE:
                success = True  # Ignore the error
            elif recovery_action.strategy == RecoveryStrategy.TERMINATE:
                self._terminate_recovery(error, recovery_action, context)
                return False
            elif recovery_action.strategy == RecoveryStrategy.ESCALATE:
                self._escalate_error(error, "Recovery strategy: escalate")
                return False
            
            # Update success/failure statistics
            if error.error_code in self.error_stats:
                if success:
                    self.error_stats[error.error_code].recovery_successes += 1
                else:
                    self.error_stats[error.error_code].recovery_failures += 1
            
            return success
            
        except Exception as recovery_error:
            self.logger.error(f"Recovery attempt failed: {recovery_error}", exc_info=True)
            if error.error_code in self.error_stats:
                self.error_stats[error.error_code].recovery_failures += 1
            return False
    
    def _retry_recovery(self, error: KGASException, recovery_action: RecoveryAction, 
                       context: Optional[Dict[str, Any]] = None) -> bool:
        """Implement retry recovery strategy"""
        for attempt in range(recovery_action.max_attempts):
            self.logger.info(f"Retry attempt {attempt + 1}/{recovery_action.max_attempts} for {error.error_code}")
            
            if attempt > 0:
                # Apply backoff
                backoff_time = recovery_action.backoff_seconds * (2 ** (attempt - 1))  # Exponential backoff
                time.sleep(backoff_time)
            
            # If custom recovery function is provided, use it
            if recovery_action.recovery_function:
                try:
                    result = recovery_action.recovery_function(error, context)
                    if result:
                        return True
                except Exception as retry_error:
                    self.logger.warning(f"Retry function failed: {retry_error}")
                    continue
            
            # Default retry logic - check if success condition is met
            if recovery_action.success_condition:
                try:
                    if recovery_action.success_condition():
                        return True
                except Exception as condition_error:
                    self.logger.warning(f"Success condition check failed: {condition_error}")
        
        self.logger.warning(f"All retry attempts failed for {error.error_code}")
        return False
    
    # DEVELOPMENT MODE: _fallback_recovery method disabled for fail-fast development
    # POST-DEVELOPMENT: Re-implement this method to enable graceful degradation in production
    # No fallback recovery during development - errors must be resolved at source
    
    def _reset_recovery(self, error: KGASException, recovery_action: RecoveryAction,
                       context: Optional[Dict[str, Any]] = None) -> bool:
        """Implement reset recovery strategy"""
        self.logger.info(f"Attempting reset recovery for {error.error_code}")
        
        if recovery_action.recovery_function:
            try:
                return recovery_action.recovery_function(error, context)
            except Exception as reset_error:
                self.logger.error(f"Reset recovery failed: {reset_error}")
                return False
        
        # Default reset logic - clear error history for this type
        self.error_history = [e for e in self.error_history if e.error_code != error.error_code]
        self.logger.info(f"Cleared error history for {error.error_code}")
        return True
    
    def _terminate_recovery(self, error: KGASException, recovery_action: RecoveryAction,
                           context: Optional[Dict[str, Any]] = None) -> None:
        """Implement terminate recovery strategy"""
        self.logger.critical(f"TERMINATING due to error: {error.error_code}")
        
        # Generate final error report
        self.generate_error_report(f"TERMINATION_REPORT_{error.error_code}")
        
        # If custom termination function is provided, use it
        if recovery_action.recovery_function:
            try:
                recovery_action.recovery_function(error, context)
            except Exception as term_error:
                self.logger.critical(f"Termination function failed: {term_error}")
        
        # Raise the original error to terminate
        raise error
    
    def _error_threshold_exceeded(self, error: KGASException) -> bool:
        """Check if error threshold has been exceeded"""
        now = datetime.now()
        threshold_window = timedelta(seconds=self.error_threshold_window)
        
        # Count recent errors of the same type
        recent_errors = [
            e for e in self.error_history
            if e.error_code == error.error_code and 
               now - datetime.fromisoformat(e.timestamp) <= threshold_window
        ]
        
        # Check if we've exceeded the threshold
        if len(recent_errors) >= self.critical_error_threshold:
            return True
        
        # Check critical error patterns
        critical_errors = [
            e for e in self.error_history
            if e.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL] and
               now - datetime.fromisoformat(e.timestamp) <= threshold_window
        ]
        
        return len(critical_errors) >= 3  # More than 3 critical errors in window
    
    def _escalate_error(self, error: KGASException, reason: str) -> None:
        """Escalate error to higher level"""
        escalation_message = f"ERROR ESCALATION: {reason} - {error.error_code}: {error.message}"
        self.logger.critical(escalation_message)
        
        # Generate escalation report
        self.generate_error_report(f"ESCALATION_{error.error_code}_{int(time.time())}")
        
        # In a production system, this would notify administrators
        # For now, we log the escalation
        self.logger.critical(f"ESCALATED: {error.to_dict()}")
    
    def _escalate_critical_failure(self, original_error: KGASException, handler_error: Exception) -> None:
        """Escalate critical failure of error handler itself"""
        critical_message = f"CRITICAL: Error handler failed while processing {original_error.error_code}: {handler_error}"
        self.logger.critical(critical_message)
        
        # This is a system-level failure - may need to terminate
        try:
            self.generate_error_report("CRITICAL_HANDLER_FAILURE")
        except Exception:
            pass  # Can't even generate report
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        with self._lock:
            return {
                "total_errors": len(self.error_history),
                "unique_error_codes": len(self.error_stats),
                "error_by_severity": self._count_by_severity(),
                "error_by_category": self._count_by_category(),
                "most_common_errors": self._get_most_common_errors(),
                "recovery_statistics": self._get_recovery_statistics(),
                "recent_error_rate": self._calculate_recent_error_rate(),
                "system_health_score": self._calculate_health_score()
            }
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count errors by severity"""
        severity_counts = {}
        for error in self.error_history:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
    
    def _count_by_category(self) -> Dict[str, int]:
        """Count errors by category"""
        category_counts = {}
        for error in self.error_history:
            category = error.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        return category_counts
    
    def _get_most_common_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common error codes"""
        sorted_stats = sorted(
            self.error_stats.values(),
            key=lambda x: x.count,
            reverse=True
        )
        return [asdict(stat) for stat in sorted_stats[:limit]]
    
    def _get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery attempt statistics"""
        total_attempts = sum(stat.recovery_attempts for stat in self.error_stats.values())
        total_successes = sum(stat.recovery_successes for stat in self.error_stats.values())
        
        return {
            "total_recovery_attempts": total_attempts,
            "total_recovery_successes": total_successes,
            "recovery_success_rate": total_successes / max(total_attempts, 1),
            "strategies_registered": len(self.recovery_strategies)
        }
    
    def _calculate_recent_error_rate(self) -> float:
        """Calculate recent error rate (errors per minute)"""
        if not self.error_history:
            return 0.0
        
        now = datetime.now()
        recent_window = timedelta(minutes=5)
        
        recent_errors = [
            e for e in self.error_history
            if now - datetime.fromisoformat(e.timestamp) <= recent_window
        ]
        
        return len(recent_errors) / 5.0  # errors per minute
    
    def _calculate_health_score(self) -> float:
        """Calculate system health score (0-100)"""
        if not self.error_history:
            return 100.0
        
        # Factors affecting health score
        recent_error_rate = self._calculate_recent_error_rate()
        critical_error_count = len([e for e in self.error_history if e.severity == ErrorSeverity.CRITICAL])
        recovery_stats = self._get_recovery_statistics()
        recovery_rate = recovery_stats['recovery_success_rate']
        
        # Calculate health score
        base_score = 100.0
        base_score -= min(recent_error_rate * 10, 50)  # Recent errors reduce score
        base_score -= min(critical_error_count * 5, 30)  # Critical errors reduce score
        base_score += recovery_rate * 20  # Good recovery rate increases score
        
        return max(0.0, min(100.0, base_score))
    
    def generate_error_report(self, report_name: str) -> Path:
        """Generate comprehensive error report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.error_reports_dir / f"{report_name}_{timestamp}.json"
        
        report_data = {
            "report_name": report_name,
            "generated_at": datetime.now().isoformat(),
            "statistics": self.get_error_statistics(),
            "recent_errors": [e.to_dict() for e in self.error_history[-50:]],  # Last 50 errors
            "error_stats": {code: asdict(stat) for code, stat in self.error_stats.items()},
            "recovery_strategies": {
                code: {
                    "strategy": action.strategy.value,
                    "max_attempts": action.max_attempts,
                    "backoff_seconds": action.backoff_seconds,
                    "escalation_threshold": action.escalation_threshold
                }
                for code, action in self.recovery_strategies.items()
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            self.logger.info(f"Error report generated: {report_file}")
            return report_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate error report: {e}")
            raise
    
    def clear_history(self) -> None:
        """Clear error history and statistics"""
        with self._lock:
            self.error_history.clear()
            self.error_stats.clear()
            self.logger.info("Error history and statistics cleared")


# Global error handler instance
_global_error_handler: Optional[KGASErrorHandler] = None
_handler_lock = threading.Lock()


def get_error_handler(config: Optional[Dict[str, Any]] = None) -> KGASErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    
    if _global_error_handler is None:
        with _handler_lock:
            if _global_error_handler is None:
                _global_error_handler = KGASErrorHandler(config)
    
    return _global_error_handler


def handle_kgas_error(error: KGASException, context: Optional[Dict[str, Any]] = None) -> bool:
    """Convenience function to handle KGAS errors"""
    handler = get_error_handler()
    return handler.handle_error(error, context)


if __name__ == "__main__":
    # Test the error handler
    handler = KGASErrorHandler()
    
    # Test various error types
    try:
        raise PDFProcessingError(
            message="Test PDF processing error",
            file_path="/test/path.pdf",
            context=ErrorContext(
                operation="test_pdf_processing",
                component="T01_PDF_LOADER",
                input_data={"file_path": "/test/path.pdf"},
                system_state={}
            )
        )
    except PDFProcessingError as e:
        recovery_success = handler.handle_error(e)
        print(f"PDF Error Recovery: {recovery_success}")
    
    # Generate statistics
    stats = handler.get_error_statistics()
    print(f"Error Statistics: {stats}")
    
    # Generate error report
    report_file = handler.generate_error_report("TEST_REPORT")
    print(f"Error report generated: {report_file}")
    
    print("✅ Error handler tests completed")