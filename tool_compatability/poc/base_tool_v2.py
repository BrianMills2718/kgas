"""
Base Tool V2 - Enhanced with multi-input support via ToolContext
PhD Research: Tool composition with multiple inputs
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any, Type, Union
from pydantic import BaseModel, ValidationError
import time
import traceback
import logging
from dataclasses import dataclass

from .data_types import DataType
from .tool_context import ToolContext
from .base_tool import ToolResult, ToolMetrics

# Type variables
InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)
ConfigT = TypeVar('ConfigT', bound=BaseModel)


class BaseToolV2(ABC, Generic[InputT, OutputT, ConfigT]):
    """
    Enhanced base class for tools with multi-input support.
    
    Key improvements:
    - Accepts ToolContext for multiple inputs
    - Backward compatible with single-input tools
    - Access to parameters, shared context, and metadata
    """
    
    def __init__(self, config: Optional[ConfigT] = None, collect_metrics: bool = False):
        """
        Initialize tool with optional config.
        
        Args:
            config: Tool-specific configuration
            collect_metrics: Whether to collect performance metrics (default False for performance)
        """
        self.config = config or self.default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.collect_metrics = collect_metrics
        self._tool_id = self.__class__.__name__
        
        # For testing - capture last prompt if dealing with LLM
        self.last_prompt = None
    
    @property
    def tool_id(self) -> str:
        """Unique identifier for this tool"""
        return self._tool_id
    
    @property
    @abstractmethod
    def input_type(self) -> DataType:
        """The data type this tool accepts"""
        pass
    
    @property
    @abstractmethod
    def output_type(self) -> DataType:
        """The data type this tool produces"""
        pass
    
    @property
    def input_schema(self) -> Type[InputT]:
        """The Pydantic schema for input validation"""
        # Can be overridden by subclasses
        return BaseModel
    
    @property
    def output_schema(self) -> Type[OutputT]:
        """The Pydantic schema for output validation"""
        # Can be overridden by subclasses
        return BaseModel
    
    def default_config(self) -> ConfigT:
        """Default configuration for this tool"""
        return BaseModel()
    
    def process(self, input_data: Union[InputT, ToolContext]) -> Union[ToolResult[OutputT], ToolContext]:
        """
        Process input data with multi-input support.
        
        Args:
            input_data: Either raw input data (backward compatible) or ToolContext
            
        Returns:
            Either ToolResult (backward compatible) or updated ToolContext
        """
        start_time = time.time()
        
        # Determine if we're using context or raw data
        using_context = isinstance(input_data, ToolContext)
        
        # Extract actual data and context
        if using_context:
            context = input_data
            actual_input = context.primary_data
        else:
            # Backward compatibility - wrap in context
            context = ToolContext(primary_data=input_data)
            actual_input = input_data
        
        # Initialize metrics if needed
        if self.collect_metrics:
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024
        else:
            memory_before = 0
        
        # Initialize metrics
        metrics = ToolMetrics(
            tool_name=self.tool_id,
            start_time=start_time,
            end_time=0,
            duration_seconds=0,
            memory_before_mb=memory_before,
            memory_after_mb=0,
            memory_used_mb=0,
            success=False,
            error=None
        )
        
        try:
            # Log execution start
            self.logger.info(f"Starting {self.tool_id} execution")
            
            # Validate input if needed
            if hasattr(self, 'validate_input'):
                validated_input = self.validate_input(actual_input)
            else:
                validated_input = actual_input
            
            # Execute tool logic with context access
            output = self._execute(validated_input, context)
            
            # Update context with output
            if using_context:
                context.primary_data = output
                context.add_metadata(f"{self.tool_id}_completed", True)
            
            # Collect final metrics
            end_time = time.time()
            
            if self.collect_metrics:
                import psutil
                process = psutil.Process()
                memory_after = process.memory_info().rss / 1024 / 1024
            else:
                memory_after = memory_before
            
            metrics.end_time = end_time
            metrics.duration_seconds = end_time - start_time
            metrics.memory_after_mb = memory_after
            metrics.memory_used_mb = memory_after - memory_before
            metrics.success = True
            
            # Log success
            self.logger.info(f"✓ {self.tool_id}: {metrics.duration_seconds:.2f}s, "
                           f"Memory: {metrics.memory_used_mb:.1f}MB")
            
            # Return appropriate type
            if using_context:
                return context
            else:
                return ToolResult(
                    data=output,
                    metrics=metrics,
                    success=True,
                    error=None
                )
            
        except Exception as e:
            # Handle errors
            end_time = time.time()
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            if self.collect_metrics:
                import psutil
                process = psutil.Process()
                memory_after = process.memory_info().rss / 1024 / 1024
            else:
                memory_after = memory_before
            
            metrics.end_time = end_time
            metrics.duration_seconds = end_time - start_time
            metrics.memory_after_mb = memory_after
            metrics.memory_used_mb = memory_after - memory_before
            metrics.success = False
            metrics.error = error_msg
            
            # Log error with traceback
            self.logger.error(f"Tool execution failed: {error_msg}")
            self.logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            if using_context:
                context.add_metadata(f"{self.tool_id}_error", error_msg)
                raise
            else:
                return ToolResult(
                    data=None,
                    metrics=metrics,
                    success=False,
                    error=error_msg
                )
    
    @abstractmethod
    def _execute(self, input_data: InputT, context: ToolContext) -> OutputT:
        """
        Execute the tool's logic with access to context.
        
        Args:
            input_data: The validated primary input data
            context: The tool context with parameters and shared data
            
        Returns:
            The output data
        """
        pass
    
    def validate_input(self, input_data: Any) -> InputT:
        """Validate and convert input to expected schema"""
        if isinstance(input_data, self.input_schema):
            return input_data
        
        try:
            return self.input_schema(**input_data)
        except (ValidationError, TypeError) as e:
            raise ValueError(f"Input validation failed: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "tool_id": self.tool_id,
            "input_type": self.input_type.value,
            "output_type": self.output_type.value,
            "supports_context": True,
            "config": self.config.dict() if hasattr(self.config, 'dict') else {}
        }