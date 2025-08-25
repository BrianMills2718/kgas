"""
Type-Based Tool Composition POC

This package implements a proof of concept for type-based tool composition,
demonstrating automatic discovery and execution of tool chains.
"""

from .data_types import DataType, DataSchema, are_types_compatible
from .base_tool import BaseTool, ToolMetrics, ToolResult
from .registry import ToolRegistry

__all__ = [
    'DataType',
    'DataSchema', 
    'are_types_compatible',
    'BaseTool',
    'ToolMetrics',
    'ToolResult',
    'ToolRegistry'
]