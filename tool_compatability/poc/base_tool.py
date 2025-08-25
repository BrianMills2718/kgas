"""
Base Tool Class for Tool Composition POC

This module provides the base class that all tools must inherit from.
It handles validation, metrics collection, error handling, and provides
a consistent interface for all tools.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any, Type, List
from pydantic import BaseModel, ValidationError
import time
import traceback
import psutil
import logging
from dataclasses import dataclass

from .data_types import DataType


# Type variables for generic tool inputs/outputs
InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)
ConfigT = TypeVar('ConfigT', bound=BaseModel)


class ToolMetrics(BaseModel):
    """Performance metrics collected during tool execution"""
    tool_name: str
    start_time: float
    end_time: float
    duration_seconds: float
    memory_before_mb: float
    memory_after_mb: float
    memory_used_mb: float
    input_size_bytes: Optional[int] = None
    output_size_bytes: Optional[int] = None
    success: bool
    error: Optional[str] = None
    
    def summary(self) -> str:
        """Get human-readable summary"""
        status = "✓" if self.success else "✗"
        return (f"{status} {self.tool_name}: {self.duration_seconds:.2f}s, "
                f"Memory: {self.memory_used_mb:.1f}MB")


class ToolResult(BaseModel, Generic[OutputT]):
    """
    Wrapper for tool output with metadata.
    
    This provides a consistent structure for all tool outputs,
    including success/failure status and performance metrics.
    """
    data: Optional[OutputT]
    metrics: ToolMetrics
    success: bool
    error: Optional[str] = None
    warnings: List[str] = []
    
    def unwrap(self) -> OutputT:
        """Get data or raise if failed"""
        if not self.success or self.data is None:
            raise ValueError(f"Tool failed: {self.error}")
        return self.data


@dataclass
class ToolInfo:
    """Metadata about a tool"""
    name: str
    version: str
    description: str
    input_type: DataType
    output_type: DataType
    config_schema: Type[BaseModel]
    author: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.name} v{self.version}: {self.input_type.value} → {self.output_type.value}"


class BaseTool(ABC, Generic[InputT, OutputT, ConfigT]):
    """
    Base class for all tools in the system.
    
    This provides:
    - Input/output validation
    - Performance metrics collection
    - Error handling and recovery
    - Consistent logging
    - Configuration management
    """
    
    def __init__(self, config: Optional[ConfigT] = None):
        """
        Initialize tool with optional configuration.
        
        Args:
            config: Tool-specific configuration
        """
        self.config = config or self.default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.execution_count = 0
        self.total_execution_time = 0.0
        self._validate_config()
    
    # ========== Abstract Properties (Must Override) ==========
    
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
    @abstractmethod
    def input_schema(self) -> Type[InputT]:
        """The Pydantic model for input validation"""
        pass
    
    @property
    @abstractmethod
    def output_schema(self) -> Type[OutputT]:
        """The Pydantic model for output validation"""
        pass
    
    @property
    @abstractmethod
    def config_schema(self) -> Type[ConfigT]:
        """The Pydantic model for configuration"""
        pass
    
    @abstractmethod
    def default_config(self) -> ConfigT:
        """Default configuration for the tool"""
        pass
    
    @abstractmethod
    def _execute(self, input_data: InputT, **kwargs) -> OutputT:
        """
        Core execution logic - implement this in subclasses.
        
        Args:
            input_data: Validated input data
            **kwargs: Additional parameters from config
            
        Returns:
            Output data
            
        Raises:
            Any exception on failure
        """
        pass
    
    # ========== Tool Metadata ==========
    
    @property
    def tool_info(self) -> ToolInfo:
        """Get tool metadata"""
        return ToolInfo(
            name=self.__class__.__name__,
            version=getattr(self, '__version__', '1.0.0'),
            description=self.__class__.__doc__ or "No description",
            input_type=self.input_type,
            output_type=self.output_type,
            config_schema=self.config_schema
        )
    
    @property
    def tool_id(self) -> str:
        """Unique identifier for this tool"""
        return self.__class__.__name__
    
    # ========== Configuration Management ==========
    
    def _validate_config(self):
        """Validate configuration against schema"""
        try:
            if self.config and self.config_schema:
                # Re-parse to validate
                if hasattr(self.config, 'dict'):
                    self.config = self.config_schema(**self.config.dict())
                else:
                    # Config is already a dict
                    self.config = self.config_schema(**self.config)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}")
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        config_dict = self.config.dict()
        config_dict.update(kwargs)
        self.config = self.config_schema(**config_dict)
        self._validate_config()
    
    # ========== Input Validation ==========
    
    def validate_input(self, data: Any) -> InputT:
        """
        Validate and parse input data.
        
        Args:
            data: Raw input data
            
        Returns:
            Validated input matching schema
            
        Raises:
            ValueError: If validation fails
        """
        try:
            if isinstance(data, dict):
                return self.input_schema(**data)
            elif isinstance(data, self.input_schema):
                return data
            elif isinstance(data, BaseModel):
                # Try to convert from another Pydantic model
                return self.input_schema(**data.dict())
            else:
                raise ValueError(f"Invalid input type: {type(data)}")
        except ValidationError as e:
            self.logger.error(f"Input validation failed: {e}")
            raise ValueError(f"Input validation failed: {e}")
    
    # ========== Main Processing Method ==========
    
    def process(self, input_data: Any, **kwargs) -> ToolResult[OutputT]:
        """
        Main entry point for tool execution.
        
        This method:
        1. Validates input
        2. Collects metrics
        3. Executes tool logic
        4. Handles errors
        5. Returns wrapped result
        
        Args:
            input_data: Input data (will be validated)
            **kwargs: Additional parameters
            
        Returns:
            ToolResult with output data and metrics
        """
        # Start metrics collection
        process = psutil.Process()
        start_time = time.time()
        memory_before = process.memory_info().rss / 1024 / 1024
        
        # Initialize metrics
        metrics = ToolMetrics(
            tool_name=self.tool_id,
            start_time=start_time,
            end_time=0,
            duration_seconds=0,
            memory_before_mb=memory_before,
            memory_after_mb=0,
            memory_used_mb=0,
            success=False
        )
        
        warnings = []
        
        try:
            # Log execution start
            self.logger.info(f"Starting {self.tool_id} execution")
            
            # Validate input
            validated_input = self.validate_input(input_data)
            
            # Calculate input size
            if hasattr(validated_input, 'content'):
                metrics.input_size_bytes = len(str(validated_input.content))
            
            # Execute tool logic
            output = self._execute(validated_input, **kwargs)
            
            # Validate output type
            if not isinstance(output, self.output_schema):
                # Try to convert
                if isinstance(output, dict):
                    output = self.output_schema(**output)
                else:
                    raise ValueError(
                        f"Output type mismatch. Expected {self.output_schema}, "
                        f"got {type(output)}"
                    )
            
            # Calculate output size
            if hasattr(output, 'content'):
                metrics.output_size_bytes = len(str(output.content))
            elif hasattr(output, '__len__'):
                metrics.output_size_bytes = len(str(output))
            
            # Collect final metrics
            end_time = time.time()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            metrics.end_time = end_time
            metrics.duration_seconds = end_time - start_time
            metrics.memory_after_mb = memory_after
            metrics.memory_used_mb = memory_after - memory_before
            metrics.success = True
            
            # Update statistics
            self.execution_count += 1
            self.total_execution_time += metrics.duration_seconds
            
            # Log success
            self.logger.info(metrics.summary())
            
            return ToolResult(
                data=output,
                metrics=metrics,
                success=True,
                warnings=warnings
            )
            
        except Exception as e:
            # Collect error metrics
            end_time = time.time()
            memory_after = process.memory_info().rss / 1024 / 1024
            
            metrics.end_time = end_time
            metrics.duration_seconds = end_time - start_time
            metrics.memory_after_mb = memory_after
            metrics.memory_used_mb = memory_after - memory_before
            metrics.error = str(e)
            
            # Log error with traceback
            self.logger.error(
                f"Tool execution failed: {e}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            
            return ToolResult(
                data=None,
                metrics=metrics,
                success=False,
                error=str(e),
                warnings=warnings
            )
    
    # ========== Statistics ==========
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        avg_time = (self.total_execution_time / self.execution_count 
                   if self.execution_count > 0 else 0)
        
        return {
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time
        }
    
    def reset_statistics(self):
        """Reset execution statistics"""
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    # ========== Context Manager Support ==========
    
    def __enter__(self):
        """Support using tool as context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit"""
        # Override in subclasses if cleanup needed
        pass
    
    # ========== String Representation ==========
    
    def __str__(self) -> str:
        return str(self.tool_info)
    
    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"input={self.input_type.value}, "
                f"output={self.output_type.value})")