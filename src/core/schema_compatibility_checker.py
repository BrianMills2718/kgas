"""
Schema-Based Compatibility Checker

Checks tool compatibility based on their declared input/output schemas
without running the actual tools.
"""

from typing import Dict, List, Tuple, Any, Optional
import logging
from dataclasses import dataclass
from src.tools.base_tool import BaseTool, ToolContract

logger = logging.getLogger(__name__)


@dataclass
class SchemaCompatibilityIssue:
    """Represents a schema compatibility issue between tools."""
    source_tool: str
    target_tool: str
    issue_type: str  # "missing_required_field", "type_mismatch", "format_incompatible"
    field_name: str
    details: str
    severity: str  # "error", "warning"


class SchemaCompatibilityChecker:
    """
    Checks tool compatibility based on declared schemas.
    
    This is lighter weight than running actual tools and can catch
    obvious incompatibilities at pipeline design time.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.known_field_mappings = self._load_known_mappings()
    
    def check_tool_compatibility(
        self, 
        source_tool: BaseTool, 
        target_tool: BaseTool
    ) -> Tuple[bool, List[SchemaCompatibilityIssue]]:
        """
        Check if source tool output is compatible with target tool input.
        
        Args:
            source_tool: Tool producing output
            target_tool: Tool consuming input
            
        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        issues = []
        
        try:
            # Get contracts
            source_contract = source_tool.get_contract()
            target_contract = target_tool.get_contract()
            
            # Check schema compatibility
            issues = self._check_schema_compatibility(
                source_contract.tool_id,
                source_contract.output_schema,
                target_contract.tool_id,
                target_contract.input_schema
            )
            
        except Exception as e:
            issues.append(SchemaCompatibilityIssue(
                source_tool=source_tool.tool_id,
                target_tool=target_tool.tool_id,
                issue_type="contract_error",
                field_name="",
                details=f"Failed to get contracts: {str(e)}",
                severity="error"
            ))
        
        # Compatible if no error-level issues
        is_compatible = all(issue.severity != "error" for issue in issues)
        
        return is_compatible, issues
    
    def _check_schema_compatibility(
        self,
        source_tool_id: str,
        output_schema: Dict[str, Any],
        target_tool_id: str,
        input_schema: Dict[str, Any]
    ) -> List[SchemaCompatibilityIssue]:
        """Check if output schema satisfies input schema requirements."""
        issues = []
        
        # Get required fields from input schema
        input_required = input_schema.get("required", [])
        input_properties = input_schema.get("properties", {})
        
        # Get available fields from output schema
        output_properties = output_schema.get("properties", {})
        
        # Check each required input field
        for field_name in input_required:
            field_schema = input_properties.get(field_name, {})
            
            # Check if output provides this field
            if field_name in output_properties:
                # Field exists - check type compatibility
                output_field_schema = output_properties[field_name]
                type_issues = self._check_type_compatibility(
                    source_tool_id, target_tool_id,
                    field_name, output_field_schema, field_schema
                )
                issues.extend(type_issues)
                
            else:
                # Field missing - check if there's a known mapping
                mapped_field = self._find_field_mapping(
                    source_tool_id, target_tool_id, field_name
                )
                
                if mapped_field and mapped_field in output_properties:
                    issues.append(SchemaCompatibilityIssue(
                        source_tool=source_tool_id,
                        target_tool=target_tool_id,
                        issue_type="field_name_mismatch",
                        field_name=field_name,
                        details=f"Field '{field_name}' maps to '{mapped_field}' in output",
                        severity="warning"
                    ))
                else:
                    issues.append(SchemaCompatibilityIssue(
                        source_tool=source_tool_id,
                        target_tool=target_tool_id,
                        issue_type="missing_required_field",
                        field_name=field_name,
                        details=f"Required field '{field_name}' not found in output schema",
                        severity="error"
                    ))
        
        # Check for output fields that don't match any input
        output_fields = set(output_properties.keys())
        input_fields = set(input_properties.keys())
        unmapped_outputs = output_fields - input_fields
        
        if unmapped_outputs:
            # Just a warning - extra fields are usually OK
            for field in unmapped_outputs:
                issues.append(SchemaCompatibilityIssue(
                    source_tool=source_tool_id,
                    target_tool=target_tool_id,
                    issue_type="unmapped_output_field",
                    field_name=field,
                    details=f"Output field '{field}' has no corresponding input field",
                    severity="warning"
                ))
        
        return issues
    
    def _check_type_compatibility(
        self,
        source_tool_id: str,
        target_tool_id: str,
        field_name: str,
        output_schema: Dict[str, Any],
        input_schema: Dict[str, Any]
    ) -> List[SchemaCompatibilityIssue]:
        """Check if field types are compatible."""
        issues = []
        
        output_type = output_schema.get("type", "any")
        input_type = input_schema.get("type", "any")
        
        if output_type != input_type:
            # Check if types are compatible
            compatible = self._are_types_compatible(output_type, input_type)
            
            if not compatible:
                issues.append(SchemaCompatibilityIssue(
                    source_tool=source_tool_id,
                    target_tool=target_tool_id,
                    issue_type="type_mismatch",
                    field_name=field_name,
                    details=f"Output type '{output_type}' incompatible with input type '{input_type}'",
                    severity="error"
                ))
        
        # Check array item types
        if output_type == "array" and input_type == "array":
            output_items = output_schema.get("items", {})
            input_items = input_schema.get("items", {})
            
            if output_items and input_items:
                item_issues = self._check_type_compatibility(
                    source_tool_id, target_tool_id,
                    f"{field_name}[items]", output_items, input_items
                )
                issues.extend(item_issues)
        
        # Check object properties
        if output_type == "object" and input_type == "object":
            output_props = output_schema.get("properties", {})
            input_props = input_schema.get("properties", {})
            input_required = input_schema.get("required", [])
            
            for prop_name, prop_schema in input_props.items():
                if prop_name in output_props:
                    prop_issues = self._check_type_compatibility(
                        source_tool_id, target_tool_id,
                        f"{field_name}.{prop_name}",
                        output_props[prop_name], prop_schema
                    )
                    issues.extend(prop_issues)
                elif prop_name in input_required:
                    issues.append(SchemaCompatibilityIssue(
                        source_tool=source_tool_id,
                        target_tool=target_tool_id,
                        issue_type="missing_required_field",
                        field_name=f"{field_name}.{prop_name}",
                        details=f"Required nested field missing",
                        severity="error"
                    ))
        
        return issues
    
    def _are_types_compatible(self, output_type: str, input_type: str) -> bool:
        """Check if two JSON schema types are compatible."""
        # Same type is always compatible
        if output_type == input_type:
            return True
        
        # Any type is compatible with everything
        if output_type == "any" or input_type == "any":
            return True
        
        # Number types are somewhat compatible
        number_types = {"number", "integer"}
        if output_type in number_types and input_type in number_types:
            # Integer can be used as number, but not vice versa
            return not (output_type == "number" and input_type == "integer")
        
        # String and number might be compatible with parsing
        if (output_type == "string" and input_type in number_types) or \
           (output_type in number_types and input_type == "string"):
            return True  # With warning
        
        return False
    
    def _load_known_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load known field mappings between tools."""
        return {
            ("T23C", "T31"): {
                "mentions": "mentions",  # Now matches after our fix
                "surface_form": "text",  # T23C output -> T31 input
            },
            ("T23C", "T34"): {
                "relationships": "relationships",
                "head_entity": "subject.canonical_name",
                "tail_entity": "object.canonical_name",
                "source_id": "subject.entity_id",
                "target_id": "object.entity_id",
                "relationship_type": "relationship_type"
            },
            ("T15A", "T23C"): {
                "chunks": "text",  # chunk list -> text field
                "chunk_id": "chunk_ref"
            }
        }
    
    def _find_field_mapping(
        self, 
        source_tool: str, 
        target_tool: str, 
        field_name: str
    ) -> Optional[str]:
        """Find known field mapping between tools."""
        tool_pair = (source_tool, target_tool)
        if tool_pair in self.known_field_mappings:
            mappings = self.known_field_mappings[tool_pair]
            # Reverse lookup - find source field that maps to target field
            for source_field, target_field in mappings.items():
                if target_field == field_name:
                    return source_field
        return None
    
    def generate_adapter_code(
        self, 
        issues: List[SchemaCompatibilityIssue]
    ) -> str:
        """Generate adapter code to fix compatibility issues."""
        # Group issues by tool pair
        tool_pairs = {}
        for issue in issues:
            pair = (issue.source_tool, issue.target_tool)
            if pair not in tool_pairs:
                tool_pairs[pair] = []
            tool_pairs[pair].append(issue)
        
        adapters = []
        for (source, target), pair_issues in tool_pairs.items():
            adapter = self._generate_single_adapter(source, target, pair_issues)
            adapters.append(adapter)
        
        return "\n\n".join(adapters)
    
    def _generate_single_adapter(
        self,
        source_tool: str,
        target_tool: str,
        issues: List[SchemaCompatibilityIssue]
    ) -> str:
        """Generate adapter code for a specific tool pair."""
        field_mappings = []
        
        for issue in issues:
            if issue.issue_type == "field_name_mismatch":
                # Extract mapping from details
                if "maps to" in issue.details:
                    source_field = issue.details.split("'")[3]
                    target_field = issue.field_name
                    field_mappings.append((source_field, target_field))
        
        adapter_code = f'''
def adapt_{source_tool.lower()}_to_{target_tool.lower()}(source_data: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt {source_tool} output to {target_tool} input format."""
    adapted = {{}}
    
'''
        
        for source_field, target_field in field_mappings:
            adapter_code += f'''    # Map {source_field} to {target_field}
    if "{source_field}" in source_data:
        adapted["{target_field}"] = source_data["{source_field}"]
    
'''
        
        adapter_code += '''    return adapted
'''
        
        return adapter_code


def check_pipeline_compatibility(tool_sequence: List[str]) -> Dict[str, Any]:
    """
    Check compatibility of a tool pipeline based on schemas.
    
    Args:
        tool_sequence: List of tool IDs in execution order
        
    Returns:
        Compatibility report with issues and suggestions
    """
    checker = SchemaCompatibilityChecker()
    report = {
        "pipeline": tool_sequence,
        "is_compatible": True,
        "issues": [],
        "adapters_needed": [],
        "suggested_code": ""
    }
    
    # Check each adjacent pair
    for i in range(len(tool_sequence) - 1):
        source_tool_id = tool_sequence[i]
        target_tool_id = tool_sequence[i + 1]
        
        # Load tool contracts (this is where we'd get the actual schemas)
        # For now, using known schemas
        issues = checker._check_schema_compatibility(
            source_tool_id,
            get_known_output_schema(source_tool_id),
            target_tool_id,
            get_known_input_schema(target_tool_id)
        )
        
        if issues:
            report["issues"].extend(issues)
            if any(issue.severity == "error" for issue in issues):
                report["is_compatible"] = False
                report["adapters_needed"].append((source_tool_id, target_tool_id))
    
    # Generate adapter code if needed
    if report["adapters_needed"]:
        report["suggested_code"] = checker.generate_adapter_code(report["issues"])
    
    return report


def get_known_output_schema(tool_id: str) -> Dict[str, Any]:
    """Get known output schema for a tool."""
    # This would come from tool contracts in reality
    schemas = {
        "T23C": {
            "type": "object",
            "properties": {
                "entities": {"type": "array"},
                "relationships": {"type": "array"},
                "mentions": {"type": "array"},
                "entity_count": {"type": "integer"},
                "relationship_count": {"type": "integer"}
            },
            "required": ["entities", "relationships", "mentions"]
        },
        "T31": {
            "type": "object", 
            "properties": {
                "entity_count": {"type": "integer"},
                "mention_count": {"type": "integer"},
                "entities": {"type": "array"}
            },
            "required": ["entity_count"]
        }
    }
    return schemas.get(tool_id, {})


def get_known_input_schema(tool_id: str) -> Dict[str, Any]:
    """Get known input schema for a tool."""
    schemas = {
        "T31": {
            "type": "object",
            "properties": {
                "mentions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "entity_type": {"type": "string"},
                            "confidence": {"type": "number"}
                        },
                        "required": ["text", "entity_type"]
                    }
                },
                "source_refs": {"type": "array"}
            },
            "required": ["mentions", "source_refs"]
        },
        "T34": {
            "type": "object",
            "properties": {
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "subject": {"type": "object"},
                            "object": {"type": "object"},
                            "relationship_type": {"type": "string"}
                        },
                        "required": ["subject", "object", "relationship_type"]
                    }
                },
                "source_refs": {"type": "array"}
            },
            "required": ["relationships", "source_refs"]
        }
    }
    return schemas.get(tool_id, {})