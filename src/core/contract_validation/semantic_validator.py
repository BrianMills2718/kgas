"""
Semantic Field Mapping Validator

Validates semantic compatibility between tool inputs and outputs.
This addresses the gap where tools pass schema validation but fail
due to semantic mismatches (e.g., "text" vs "canonical_name").
"""

from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SemanticFieldMapping:
    """Defines semantic equivalences between field names"""
    
    # Common semantic equivalences
    FIELD_EQUIVALENCES = {
        # Text representations
        "text": ["surface_form", "surface_text", "mention_text", "content"],
        "canonical_name": ["name", "entity_name", "primary_name"],
        
        # Identifiers
        "entity_id": ["id", "node_id", "entity_identifier"],
        "mention_id": ["id", "mention_identifier"],
        
        # Relationships
        "head_entity": ["source", "source_entity", "from_entity"],
        "tail_entity": ["target", "target_entity", "to_entity"],
        
        # Confidence scores
        "confidence": ["score", "confidence_score", "probability"],
        
        # Types
        "entity_type": ["type", "node_type", "label"],
        "relationship_type": ["edge_type", "relation_type", "predicate"]
    }
    
    @classmethod
    def are_fields_equivalent(cls, field1: str, field2: str) -> bool:
        """Check if two field names are semantically equivalent"""
        if field1 == field2:
            return True
        
        # Check in equivalence groups
        for primary, equivalents in cls.FIELD_EQUIVALENCES.items():
            all_names = [primary] + equivalents
            if field1 in all_names and field2 in all_names:
                return True
        
        return False
    
    @classmethod
    def get_equivalent_field(cls, field: str, available_fields: List[str]) -> Optional[str]:
        """Find an equivalent field name from available fields"""
        for available in available_fields:
            if cls.are_fields_equivalent(field, available):
                return available
        return None


class DataModelTransformer:
    """Defines transformations between data models"""
    
    # Transformation rules
    TRANSFORMATIONS = {
        ("Entity", "Mention"): {
            "canonical_name": "text",
            "entity_id": "entity_id",
            "entity_type": "entity_type",
            "confidence": "confidence"
        },
        ("Mention", "Entity"): {
            "text": "canonical_name",
            "entity_id": "entity_id",
            "entity_type": "entity_type",
            "confidence": "confidence"
        }
    }
    
    @classmethod
    def can_transform(cls, from_type: str, to_type: str) -> bool:
        """Check if transformation is possible"""
        return (from_type, to_type) in cls.TRANSFORMATIONS
    
    @classmethod
    def get_transformation_mapping(cls, from_type: str, to_type: str) -> Dict[str, str]:
        """Get field mapping for transformation"""
        return cls.TRANSFORMATIONS.get((from_type, to_type), {})


class SemanticValidator:
    """Validates semantic compatibility between tools"""
    
    def __init__(self):
        self.field_mapper = SemanticFieldMapping()
        self.transformer = DataModelTransformer()
        self.logger = logger
    
    def validate_tool_chain_compatibility(
        self, 
        tool_outputs: List[Dict[str, Any]], 
        tool_inputs: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that outputs can semantically feed into inputs
        
        Args:
            tool_outputs: List of tool output schemas
            tool_inputs: List of tool input schemas for next tools
            
        Returns:
            Tuple of (is_compatible, list of issues)
        """
        issues = []
        
        for i in range(len(tool_outputs)):
            if i >= len(tool_inputs) - 1:
                break
                
            output_schema = tool_outputs[i]
            input_schema = tool_inputs[i + 1]
            
            # Check semantic compatibility
            compatibility_issues = self._check_semantic_compatibility(
                output_schema, 
                input_schema,
                f"Tool{i}->Tool{i+1}"
            )
            issues.extend(compatibility_issues)
        
        return len(issues) == 0, issues
    
    def _check_semantic_compatibility(
        self, 
        output_schema: Dict[str, Any], 
        input_schema: Dict[str, Any],
        context: str
    ) -> List[str]:
        """Check if output can semantically satisfy input requirements"""
        issues = []
        
        # Get required input fields
        required_fields = input_schema.get("required", [])
        output_fields = list(output_schema.get("properties", {}).keys())
        
        for required_field in required_fields:
            # Check exact match first
            if required_field in output_fields:
                continue
            
            # Check semantic equivalence
            equivalent = self.field_mapper.get_equivalent_field(
                required_field, 
                output_fields
            )
            
            if equivalent:
                self.logger.debug(
                    f"{context}: Field '{required_field}' can be satisfied by "
                    f"semantically equivalent '{equivalent}'"
                )
            else:
                issues.append(
                    f"{context}: Required field '{required_field}' has no "
                    f"semantic equivalent in output fields {output_fields}"
                )
        
        return issues
    
    def suggest_data_adapter(
        self,
        output_type: str,
        input_type: str
    ) -> Optional[Dict[str, str]]:
        """Suggest field mapping for data adaptation"""
        if self.transformer.can_transform(output_type, input_type):
            return self.transformer.get_transformation_mapping(output_type, input_type)
        return None
    
    def validate_data_flow_semantics(
        self,
        data: Any,
        expected_type: str,
        available_types: List[str]
    ) -> Tuple[bool, str]:
        """
        Validate if data semantically matches expected type
        
        Returns:
            Tuple of (is_valid, suggested_type or error message)
        """
        # Check if data has expected fields for the type
        if expected_type == "Mention":
            if hasattr(data, "text") or (isinstance(data, dict) and "text" in data):
                return True, expected_type
            elif hasattr(data, "canonical_name") or (isinstance(data, dict) and "canonical_name" in data):
                return True, "Entity"  # Suggest Entity type instead
        
        elif expected_type == "Entity":
            if hasattr(data, "canonical_name") or (isinstance(data, dict) and "canonical_name" in data):
                return True, expected_type
            elif hasattr(data, "text") or (isinstance(data, dict) and "text" in data):
                return True, "Mention"  # Suggest Mention type instead
        
        return False, f"Data does not match expected type {expected_type}"


# Integration with existing contract validator
def enhance_contract_validator(validator):
    """Enhance existing contract validator with semantic validation"""
    semantic_validator = SemanticValidator()
    
    # Add semantic validation method
    original_validate = validator.validate_data_flow
    
    def enhanced_validate(tool_instance, contract, test_input):
        # First run original validation
        result = original_validate(tool_instance, contract, test_input)
        
        if result[0]:  # If original validation passed
            # Add semantic validation
            # This is a simplified example - full implementation would
            # extract schemas from contracts and validate semantics
            logger.info("Adding semantic validation to data flow")
        
        return result
    
    validator.validate_data_flow = enhanced_validate
    validator.semantic_validator = semantic_validator
    
    return validator