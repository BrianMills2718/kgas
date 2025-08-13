"""Tool Compatibility Checker - Programmatically verify tool compatibility."""

import inspect
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue between tools."""
    source_tool: str
    target_tool: str
    issue_type: str  # "field_mismatch", "type_mismatch", "missing_field", "method_signature"
    details: str
    suggestion: str


class ToolCompatibilityChecker:
    """Check compatibility between tools in a pipeline."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_pipeline_compatibility(self, tools: List[Any]) -> List[CompatibilityIssue]:
        """Check compatibility between sequential tools in a pipeline."""
        issues = []
        
        for i in range(len(tools) - 1):
            source_tool = tools[i]
            target_tool = tools[i + 1]
            
            # Check output->input compatibility
            tool_issues = self.check_tool_compatibility(source_tool, target_tool)
            issues.extend(tool_issues)
        
        return issues
    
    def check_tool_compatibility(self, source_tool: Any, target_tool: Any) -> List[CompatibilityIssue]:
        """Check if source tool output is compatible with target tool input."""
        issues = []
        
        # Get contracts
        source_contract = self._get_tool_contract(source_tool)
        target_contract = self._get_tool_contract(target_tool)
        
        if not source_contract or not target_contract:
            return issues
        
        # Check output->input schema compatibility
        output_schema = source_contract.get('output_schema') or source_contract.get('output_specification', {})
        input_schema = target_contract.get('input_schema') or target_contract.get('input_specification', {})
        
        # Check field compatibility
        field_issues = self._check_field_compatibility(
            source_tool.__class__.__name__,
            target_tool.__class__.__name__,
            output_schema,
            input_schema
        )
        issues.extend(field_issues)
        
        # Check method signatures (for service dependencies)
        method_issues = self._check_method_compatibility(source_tool, target_tool)
        issues.extend(method_issues)
        
        return issues
    
    def _check_field_compatibility(self, source_name: str, target_name: str, 
                                  output_schema: Dict, input_schema: Dict) -> List[CompatibilityIssue]:
        """Check field-level compatibility between schemas."""
        issues = []
        
        # Get output fields
        output_props = output_schema.get('properties', {})
        
        # Get required input fields
        input_props = input_schema.get('properties', {})
        required_inputs = input_schema.get('required', [])
        
        # Check for missing required fields
        for field in required_inputs:
            if field not in output_props:
                # Check for common naming variations
                suggestion = self._suggest_field_mapping(field, list(output_props.keys()))
                
                issues.append(CompatibilityIssue(
                    source_tool=source_name,
                    target_tool=target_name,
                    issue_type="missing_field",
                    details=f"Target requires field '{field}' but source doesn't provide it",
                    suggestion=suggestion or f"Add field adapter mapping for '{field}'"
                ))
        
        # Check for type mismatches
        for field in input_props:
            if field in output_props:
                input_type = input_props[field].get('type', 'any')
                output_type = output_props[field].get('type', 'any')
                
                if input_type != output_type and input_type != 'any' and output_type != 'any':
                    issues.append(CompatibilityIssue(
                        source_tool=source_name,
                        target_tool=target_name,
                        issue_type="type_mismatch",
                        details=f"Field '{field}' type mismatch: source provides '{output_type}', target expects '{input_type}'",
                        suggestion=f"Add type conversion in field adapter"
                    ))
        
        return issues
    
    def _check_method_compatibility(self, source_tool: Any, target_tool: Any) -> List[CompatibilityIssue]:
        """Check method signature compatibility for shared services."""
        issues = []
        
        # Example: Check if T23C calls methods that don't exist or have wrong signatures
        if hasattr(target_tool, 'service_manager'):
            # Check EntityResolver method signatures
            if 'T23' in source_tool.__class__.__name__ and hasattr(target_tool.service_manager, 'identity_service'):
                entity_resolver = getattr(target_tool.service_manager.identity_service, 'entity_resolver', None)
                if entity_resolver:
                    # Check create_mention signature
                    try:
                        sig = inspect.signature(entity_resolver.create_mention)
                        params = list(sig.parameters.keys())
                        
                        # Known issue: T23C passes entity_id but create_mention doesn't accept it
                        if 'entity_id' not in params:
                            issues.append(CompatibilityIssue(
                                source_tool=source_tool.__class__.__name__,
                                target_tool="EntityResolver",
                                issue_type="method_signature",
                                details="create_mention() doesn't accept 'entity_id' parameter that T23C provides",
                                suggestion="Remove entity_id parameter from T23C call or update EntityResolver.create_mention() to accept it"
                            ))
                    except:
                        pass
        
        return issues
    
    def _suggest_field_mapping(self, target_field: str, source_fields: List[str]) -> Optional[str]:
        """Suggest possible field mappings based on common patterns."""
        # Common field name mappings
        common_mappings = {
            'text': ['surface_form', 'content', 'value'],
            'surface_form': ['text', 'name', 'value'],
            'mentions': ['entities', 'entity_mentions'],
            'relationships': ['edges', 'relations', 'links'],
            'source_entity': ['head_entity', 'from_entity', 'subject'],
            'target_entity': ['tail_entity', 'to_entity', 'object'],
        }
        
        # Check if target field has known mappings
        if target_field in common_mappings:
            for possible_source in common_mappings[target_field]:
                if possible_source in source_fields:
                    return f"Map '{possible_source}' to '{target_field}'"
        
        # Check reverse mappings
        for source_field in source_fields:
            if source_field in common_mappings:
                if target_field in common_mappings[source_field]:
                    return f"Map '{source_field}' to '{target_field}'"
        
        return None
    
    def _get_tool_contract(self, tool: Any) -> Dict[str, Any]:
        """Get tool contract, handling different formats."""
        if hasattr(tool, 'get_contract'):
            contract = tool.get_contract()
            if isinstance(contract, dict):
                return contract
            elif hasattr(contract, '__dict__'):
                return contract.__dict__
            else:
                # Try to extract attributes
                return {
                    'tool_id': getattr(contract, 'tool_id', None),
                    'input_schema': getattr(contract, 'input_schema', {}),
                    'output_schema': getattr(contract, 'output_schema', {})
                }
        return {}
    
    def generate_compatibility_report(self, issues: List[CompatibilityIssue]) -> str:
        """Generate a human-readable compatibility report."""
        if not issues:
            return "✅ No compatibility issues found!"
        
        report = ["🔍 Tool Compatibility Issues Found:\n"]
        
        # Group by tool pair
        by_pair = {}
        for issue in issues:
            pair = f"{issue.source_tool} → {issue.target_tool}"
            if pair not in by_pair:
                by_pair[pair] = []
            by_pair[pair].append(issue)
        
        for pair, pair_issues in by_pair.items():
            report.append(f"\n{pair}:")
            for issue in pair_issues:
                report.append(f"  ❌ {issue.issue_type}: {issue.details}")
                report.append(f"     💡 Suggestion: {issue.suggestion}")
        
        return "\n".join(report)
    
    def suggest_field_adapters(self, issues: List[CompatibilityIssue]) -> Dict[Tuple[str, str], Dict[str, str]]:
        """Suggest field adapter mappings based on compatibility issues."""
        adapters = {}
        
        for issue in issues:
            if issue.issue_type == "missing_field" and "Map" in issue.suggestion:
                # Extract mapping from suggestion
                pair = (issue.source_tool, issue.target_tool)
                if pair not in adapters:
                    adapters[pair] = {}
                
                # Parse suggestion like "Map 'surface_form' to 'text'"
                if "'" in issue.suggestion:
                    parts = issue.suggestion.split("'")
                    if len(parts) >= 4:
                        source_field = parts[1]
                        target_field = parts[3]
                        adapters[pair][source_field] = target_field
        
        return adapters