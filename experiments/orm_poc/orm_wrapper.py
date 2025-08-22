"""
ORM Wrapper for Tool Compatibility

Provides a minimal wrapper to add semantic roles to existing tools.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import time

from role_definitions import Role
from semantic_types import SemanticTypeRegistry


@dataclass
class ToolExecutionResult:
    """Result of tool execution with role information."""
    success: bool
    data: Any
    output_roles: List[Role]
    execution_time_ms: float
    error: Optional[str] = None


class ORMWrapper:
    """
    Wrapper that adds semantic role information to existing tools.
    
    This wrapper:
    1. Declares input/output roles for semantic matching
    2. Validates inputs against declared roles
    3. Executes the original tool unchanged
    4. Tags outputs with semantic role information
    """
    
    def __init__(
        self,
        tool: Any,
        tool_id: str,
        input_roles: List[Role],
        output_roles: List[Role],
        execute_method: str = "execute",
        field_mapping: Optional[Dict[str, str]] = None
    ):
        """
        Initialize ORM wrapper.
        
        Args:
            tool: The original tool instance
            tool_id: Unique identifier for this tool
            input_roles: List of input roles this tool accepts
            output_roles: List of output roles this tool produces
            execute_method: Name of method to call on tool for execution
            field_mapping: Optional mapping from role names to tool field names
        """
        self.tool = tool
        self.tool_id = tool_id
        self.input_roles = input_roles
        self.output_roles = output_roles
        self.execute_method = execute_method
        self.field_mapping = field_mapping or {}
        
    def can_connect_to(self, other: 'ORMWrapper') -> bool:
        """
        Check if this tool's output can connect to another tool's input.
        
        Uses semantic type matching to determine compatibility.
        """
        # For each output role from this tool
        for out_role in self.output_roles:
            # Check if it matches any input role of the other tool
            for in_role in other.input_roles:
                if SemanticTypeRegistry.are_compatible(
                    out_role.semantic_type,
                    in_role.semantic_type
                ):
                    return True
        return False
    
    def get_connection_mapping(self, other: 'ORMWrapper') -> Dict[str, str]:
        """
        Get the field mapping between this tool's output and another's input.
        
        Returns:
            Dictionary mapping output field names to input field names
        """
        mapping = {}
        
        for out_role in self.output_roles:
            for in_role in other.input_roles:
                if SemanticTypeRegistry.are_compatible(
                    out_role.semantic_type,
                    in_role.semantic_type
                ):
                    out_field = out_role.field_name or out_role.name
                    in_field = in_role.field_name or in_role.name
                    mapping[out_field] = in_field
                    
        return mapping
    
    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate that input data satisfies declared input roles.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        for role in self.input_roles:
            field_name = role.field_name or role.name
            
            # Check required fields
            if role.is_required() and field_name not in data:
                return False, f"Missing required field: {field_name}"
            
            # Could add type checking here if needed
            
        return True, None
    
    def execute(self, input_data: Dict[str, Any]) -> ToolExecutionResult:
        """
        Execute the wrapped tool with role validation.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            ToolExecutionResult with output data and role information
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            return ToolExecutionResult(
                success=False,
                data=None,
                output_roles=self.output_roles,
                execution_time_ms=0,
                error=error
            )
        
        # Map input fields if needed
        tool_input = {}
        for role in self.input_roles:
            orm_field = role.field_name or role.name
            tool_field = self.field_mapping.get(orm_field, orm_field)
            
            if orm_field in input_data:
                tool_input[tool_field] = input_data[orm_field]
        
        # Execute the tool
        start_time = time.time()
        try:
            # Get the execute method
            execute_fn = getattr(self.tool, self.execute_method)
            result = execute_fn(tool_input)
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return ToolExecutionResult(
                success=True,
                data=result,
                output_roles=self.output_roles,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ToolExecutionResult(
                success=False,
                data=None,
                output_roles=self.output_roles,
                execution_time_ms=execution_time,
                error=str(e)
            )
    
    def describe(self) -> str:
        """Generate human-readable description of tool's roles."""
        inputs = ", ".join([f"{r.name}({r.semantic_type.value})" for r in self.input_roles])
        outputs = ", ".join([f"{r.name}({r.semantic_type.value})" for r in self.output_roles])
        return f"{self.tool_id}: {inputs} → {outputs}"
    
    def __repr__(self):
        return f"ORMWrapper({self.tool_id})"