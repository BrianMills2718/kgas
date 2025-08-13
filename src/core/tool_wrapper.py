"""Tool wrapper to adapt tools to orchestrator interface."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Standard validation result format expected by orchestrator."""
    is_valid: bool
    validation_errors: List[str]
    
    
@dataclass
class ToolResult:
    """Standard result format expected by orchestrator."""
    is_valid: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class ContractWrapper:
    """Wraps dict contracts to provide object interface."""
    
    def __init__(self, contract_dict: Dict[str, Any]):
        self._dict = contract_dict
        
    def __getattr__(self, name):
        """Access dict values as attributes."""
        return self._dict.get(name)
    
    @property
    def input_schema(self):
        """Provide input_schema as property."""
        # Handle both input_schema and input_specification names
        return self._dict.get('input_schema') or self._dict.get('input_specification', {})
    
    @property
    def output_schema(self):
        """Provide output_schema as property."""
        # Handle both output_schema and output_specification names
        return self._dict.get('output_schema') or self._dict.get('output_specification', {})
    
    @property
    def tool_id(self):
        """Provide tool_id as property."""
        return self._dict.get('tool_id', 'unknown')
    
    @property
    def name(self):
        """Provide name as property."""
        return self._dict.get('name', 'Unknown Tool')
    
    @property
    def description(self):
        """Provide description as property."""
        return self._dict.get('description', '')
    
    @property
    def category(self):
        """Provide category as property."""
        return self._dict.get('category', 'uncategorized')
    
    @property
    def dependencies(self):
        """Provide dependencies as property."""
        return self._dict.get('dependencies', [])
    
    @property
    def performance_requirements(self):
        """Provide performance_requirements as property."""
        return self._dict.get('performance_requirements', {})
    
    @property
    def error_conditions(self):
        """Provide error_conditions as property."""
        return self._dict.get('error_conditions', [])


class OrchestratorToolWrapper:
    """Wraps tools to provide interface expected by orchestrator."""
    
    def __init__(self, tool):
        self.tool = tool
        self.tool_id = getattr(tool, 'tool_id', tool.__class__.__name__)
        self._contract = None
        self.logger = logging.getLogger(f"{__name__}.{self.tool_id}")
    
    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped tool."""
        return getattr(self.tool, name)
    
    @property
    def is_valid(self) -> bool:
        """Check if tool is valid and ready to execute."""
        try:
            # Check tool has required methods
            if not hasattr(self.tool, 'execute'):
                return False
            if not hasattr(self.tool, 'get_contract'):
                return False
            
            # Try to get contract
            contract = self.get_contract()
            return contract is not None
        except Exception as e:
            self.logger.error(f"Error checking tool validity: {e}")
            return False
    
    def get_contract(self):
        """Get tool contract with proper interface."""
        if self._contract is None:
            try:
                raw_contract = self.tool.get_contract()
                
                # If it's a dict, wrap it
                if isinstance(raw_contract, dict):
                    self._contract = ContractWrapper(raw_contract)
                else:
                    # It's already an object
                    self._contract = raw_contract
                    
            except Exception as e:
                self.logger.error(f"Error getting contract: {e}")
                return None
                
        return self._contract
    
    def validate_input(self, input_data: Any) -> ValidationResult:
        """Validate input and return standardized result."""
        try:
            # Call the tool's validate_input method
            if hasattr(self.tool, 'validate_input'):
                result = self.tool.validate_input(input_data)
                
                # If it returns a bool, wrap it
                if isinstance(result, bool):
                    if result:
                        return ValidationResult(
                            is_valid=True,
                            validation_errors=[]
                        )
                    else:
                        # Try to provide meaningful error message
                        errors = []
                        if input_data is None:
                            errors.append("Input data is None")
                        elif isinstance(input_data, dict):
                            contract = self.get_contract()
                            if contract:
                                # Get input schema (handle both names)
                                input_spec = None
                                if hasattr(contract, 'input_schema'):
                                    input_spec = contract.input_schema
                                elif hasattr(contract, 'input_specification'):
                                    input_spec = contract.input_specification
                                
                                if input_spec and isinstance(input_spec, dict):
                                    # Check top-level required fields
                                    required = input_spec.get('required', [])
                                    for field in required:
                                        if field not in input_data:
                                            errors.append(f"Missing required field: {field}")
                                    
                                    # Also check properties if they exist
                                    properties = input_spec.get('properties', {})
                                    for prop_name, prop_spec in properties.items():
                                        if isinstance(prop_spec, dict) and prop_spec.get('required', False):
                                            if prop_name not in input_data:
                                                errors.append(f"Missing required property: {prop_name}")
                        
                        if not errors:
                            errors.append("Input validation failed")
                            
                        return ValidationResult(
                            is_valid=False,
                            validation_errors=errors
                        )
                
                # If it already returns the right type, use it
                elif hasattr(result, 'is_valid'):
                    return result
                    
                # Unknown return type
                else:
                    self.logger.warning(f"Unknown validation result type: {type(result)}")
                    return ValidationResult(
                        is_valid=False,
                        validation_errors=[f"Unknown validation result type: {type(result)}"]
                    )
            else:
                # Tool doesn't have validate_input, assume valid
                return ValidationResult(
                    is_valid=True,
                    validation_errors=[]
                )
                
        except Exception as e:
            self.logger.error(f"Error during input validation: {e}")
            return ValidationResult(
                is_valid=False,
                validation_errors=[f"Validation error: {str(e)}"]
            )
    
    def execute(self, input_data: Dict[str, Any]):
        """Execute tool and return result in expected format."""
        try:
            # Check if tool expects ToolRequest
            if hasattr(self.tool, 'execute'):
                # Try to determine if tool expects ToolRequest
                import inspect
                sig = inspect.signature(self.tool.execute)
                params = list(sig.parameters.values())
                
                if params and params[0].annotation.__name__ == 'ToolRequest':
                    # Tool expects ToolRequest, create one
                    from src.tools.base_tool import ToolRequest
                    request = ToolRequest(
                        tool_id=self.tool_id,
                        operation="execute",
                        input_data=input_data,
                        parameters={}
                    )
                    result = self.tool.execute(request)
                else:
                    # Tool expects dict directly
                    result = self.tool.execute(input_data)
            else:
                # Fallback
                result = self.tool.execute(input_data)
            
            # Return the result as-is since tools already return the right format
            return result
                
        except Exception as e:
            self.logger.error(f"Error during tool execution: {e}")
            # Return error in expected format
            return {
                "status": "error",
                "error": str(e),
                "data": {}
            }
    
    def health_check(self):
        """Check tool health."""
        if hasattr(self.tool, 'health_check'):
            return self.tool.health_check()
        else:
            # Default health check
            return {
                "status": "success",
                "data": {
                    "healthy": True,
                    "tool_id": self.tool_id
                }
            }
    
    def get_status(self):
        """Get tool status."""
        if hasattr(self.tool, 'get_status'):
            return self.tool.get_status()
        else:
            return "ready"
    
    def cleanup(self):
        """Clean up tool resources."""
        if hasattr(self.tool, 'cleanup'):
            return self.tool.cleanup()
        else:
            return True