"""
Safe Tool Wrapper for Graceful Service Failure Handling

Wraps tool operations to handle service failures gracefully.
Enables tools to continue functioning even when services are unavailable.
"""

import time
import logging
from typing import Any, Optional, Callable
from functools import wraps

from src.tools.base_tool import ToolResult, ToolErrorCode

logger = logging.getLogger(__name__)


class SafeServiceOperation:
    """Context manager for safe service operations"""
    
    def __init__(self, operation_name: str, tool_id: str, fallback_value: Any = None):
        self.operation_name = operation_name
        self.tool_id = tool_id
        self.fallback_value = fallback_value
        self.operation_id = None
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.warning(f"Service operation '{self.operation_name}' failed for {self.tool_id}: {exc_val}")
            # Suppress exception and continue
            return True
        return False


def safe_service_call(fallback_value: Any = None):
    """Decorator for safe service method calls"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AttributeError as e:
                if "'NoneType' object has no attribute" in str(e):
                    logger.warning(f"Service not available for {func.__name__}: {e}")
                    return fallback_value
                raise
            except Exception as e:
                logger.warning(f"Service call failed for {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator


class SafeToolPattern:
    """Mixin class for tools to handle service failures gracefully"""
    
    def _safe_start_operation(self, tool_id: str, operation: str, 
                             inputs: Any, parameters: dict) -> str:
        """Safely start operation tracking with fallback"""
        try:
            if hasattr(self, 'services') and self.services:
                # Try to use provenance service if available
                if hasattr(self.services, 'provenance_service'):
                    prov_service = self.services.provenance_service
                    if prov_service:
                        return prov_service.start_operation(
                            tool_id, operation, [inputs], parameters
                        )
        except AttributeError as e:
            if "'NoneType' object has no attribute 'start_operation'" in str(e):
                logger.debug(f"Provenance service not available: {e}")
            else:
                logger.warning(f"Failed to start operation: {e}")
        except Exception as e:
            logger.warning(f"Failed to start operation tracking: {e}")
        
        # Return fallback operation ID
        return f"fallback_op_{tool_id}_{int(time.time())}"
    
    def _safe_complete_operation(self, operation_id: str, outputs: Any = None,
                                success: bool = True, error: str = None) -> bool:
        """Safely complete operation tracking"""
        try:
            if hasattr(self, 'services') and self.services:
                if hasattr(self.services, 'provenance_service'):
                    prov_service = self.services.provenance_service
                    if prov_service:
                        return prov_service.complete_operation(
                            operation_id, outputs, success, error
                        )
        except AttributeError as e:
            if "'NoneType' object has no attribute" in str(e):
                logger.debug(f"Provenance service not available for completion: {e}")
            else:
                logger.warning(f"Failed to complete operation: {e}")
        except Exception as e:
            logger.warning(f"Failed to complete operation tracking: {e}")
        
        return False  # Indicate operation tracking failed but continue
    
    def _safe_assess_quality(self, data: Any, operation_type: str = None) -> float:
        """Safely assess quality with fallback"""
        try:
            if hasattr(self, 'services') and self.services:
                if hasattr(self.services, 'quality_service'):
                    quality_service = self.services.quality_service
                    if quality_service:
                        return quality_service.assess_quality(data, operation_type)
        except AttributeError as e:
            if "'NoneType' object has no attribute" in str(e):
                logger.debug(f"Quality service not available: {e}")
            else:
                logger.warning(f"Failed to assess quality: {e}")
        except Exception as e:
            logger.warning(f"Failed to assess quality: {e}")
        
        # Return default quality score
        return 0.8
    
    def _safe_resolve_entity(self, entity_data: dict) -> str:
        """Safely resolve entity with fallback"""
        try:
            if hasattr(self, 'services') and self.services:
                if hasattr(self.services, 'identity_service'):
                    identity_service = self.services.identity_service
                    if identity_service:
                        # Use actual identity service methods
                        surface_form = entity_data.get('text', '')
                        entity_type = entity_data.get('type', 'UNKNOWN')
                        source_ref = entity_data.get('source_ref', 'unknown')
                        
                        # Try to find similar entities first
                        similar = identity_service.find_similar_entities(
                            surface_form=surface_form,
                            entity_type=entity_type,
                            threshold=0.8
                        )
                        
                        if similar:
                            return similar[0]['entity_id']
                        else:
                            # Create new entity via mention
                            mention_id = identity_service.create_mention(
                                surface_form=surface_form,
                                start_pos=0,
                                end_pos=len(surface_form),
                                source_ref=source_ref,
                                entity_type=entity_type
                            )
                            entity_data = identity_service.get_entity_by_mention(mention_id)
                            return entity_data['entity_id'] if entity_data else self._create_fallback_entity_id(entity_data)
        except AttributeError as e:
            if "'NoneType' object has no attribute" in str(e):
                logger.debug(f"Identity service not available: {e}")
            else:
                logger.warning(f"Failed to resolve entity: {e}")
        except Exception as e:
            logger.warning(f"Failed to resolve entity: {e}")
        
        # Return fallback entity ID
        return self._create_fallback_entity_id(entity_data)
    
    def _create_fallback_entity_id(self, entity_data: dict) -> str:
        """Create fallback entity ID"""
        entity_text = entity_data.get('text', 'unknown')
        entity_type = entity_data.get('type', 'unknown')
        return f"entity_{entity_text}_{entity_type}".replace(" ", "_").lower()
    
    def _create_safe_error_result(self, tool_id: str, error_code: str, 
                                 error_message: str) -> ToolResult:
        """Create error result safely"""
        return ToolResult(
            tool_id=tool_id,
            status="error",
            data=None,
            metadata={"timestamp": time.time()},
            execution_time=0.0,
            memory_used=0,
            error_code=error_code,
            error_message=error_message
        )
    
    def _safe_service_health_check(self) -> dict:
        """Check health of all services safely"""
        health_status = {
            "identity_service": "unknown",
            "provenance_service": "unknown",
            "quality_service": "unknown"
        }
        
        try:
            if hasattr(self, 'services') and self.services:
                # Check identity service
                if hasattr(self.services, 'identity_service'):
                    try:
                        identity = self.services.identity_service
                        if identity and hasattr(identity, 'health_check'):
                            health = identity.health_check()
                            health_status["identity_service"] = health.get("status", "unknown")
                    except:
                        health_status["identity_service"] = "unavailable"
                
                # Check provenance service
                if hasattr(self.services, 'provenance_service'):
                    try:
                        provenance = self.services.provenance_service
                        if provenance and hasattr(provenance, 'health_check'):
                            health = provenance.health_check()
                            health_status["provenance_service"] = health.get("status", "unknown")
                    except:
                        health_status["provenance_service"] = "unavailable"
                
                # Check quality service
                if hasattr(self.services, 'quality_service'):
                    try:
                        quality = self.services.quality_service
                        if quality and hasattr(quality, 'health_check'):
                            health = quality.health_check()
                            health_status["quality_service"] = health.get("status", "unknown")
                    except:
                        health_status["quality_service"] = "unavailable"
        except Exception as e:
            logger.warning(f"Failed to check service health: {e}")
        
        return health_status


def with_safe_services(tool_class):
    """Class decorator to add safe service handling to a tool"""
    
    # Mix in the SafeToolPattern
    class SafeTool(tool_class, SafeToolPattern):
        
        def __init__(self, *args, **kwargs):
            # Initialize parent class
            super().__init__(*args, **kwargs)
            
            # Ensure we have a tool_id
            if not hasattr(self, 'tool_id'):
                self.tool_id = self.__class__.__name__
        
        def execute(self, request):
            """Wrap execute method with safe service handling"""
            # Start operation safely
            operation_id = self._safe_start_operation(
                self.tool_id,
                request.operation,
                request.input_data,
                request.parameters or {}
            )
            
            try:
                # Call parent execute method
                result = super().execute(request)
                
                # Complete operation safely
                self._safe_complete_operation(
                    operation_id,
                    result.data if result else None,
                    result.status == "success" if result else False
                )
                
                return result
                
            except Exception as e:
                # Complete with error
                self._safe_complete_operation(
                    operation_id,
                    None,
                    False,
                    str(e)
                )
                
                # Re-raise the exception
                raise
    
    # Preserve class metadata
    SafeTool.__name__ = tool_class.__name__
    SafeTool.__module__ = tool_class.__module__
    SafeTool.__qualname__ = tool_class.__qualname__
    
    return SafeTool


# Example usage pattern for updating existing tools
def make_tool_safe(tool_instance):
    """Make an existing tool instance safe by adding safe methods"""
    
    # Add safe methods to the instance
    tool_instance._safe_start_operation = SafeToolPattern._safe_start_operation.__get__(tool_instance)
    tool_instance._safe_complete_operation = SafeToolPattern._safe_complete_operation.__get__(tool_instance)
    tool_instance._safe_assess_quality = SafeToolPattern._safe_assess_quality.__get__(tool_instance)
    tool_instance._safe_resolve_entity = SafeToolPattern._safe_resolve_entity.__get__(tool_instance)
    tool_instance._safe_service_health_check = SafeToolPattern._safe_service_health_check.__get__(tool_instance)
    tool_instance._create_safe_error_result = SafeToolPattern._create_safe_error_result.__get__(tool_instance)
    
    return tool_instance