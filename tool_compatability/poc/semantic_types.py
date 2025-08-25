"""
Semantic Type Compatibility System
PhD Research: Beyond simple type matching to semantic understanding
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from pydantic import BaseModel, Field
from enum import Enum
from abc import ABC, abstractmethod


class Domain(str, Enum):
    """High-level domains for semantic classification"""
    GENERAL = "general"
    MEDICAL = "medical"
    FINANCIAL = "financial"
    SOCIAL = "social"
    SCIENTIFIC = "scientific"
    LEGAL = "legal"
    TECHNICAL = "technical"
    BUSINESS = "business"


class SemanticContext(BaseModel):
    """
    Context information for semantic type checking.
    
    Provides domain, constraints, and metadata for understanding
    what kind of data is being processed.
    """
    
    domain: Domain = Domain.GENERAL
    sub_domain: Optional[str] = None
    constraints: Dict[str, Any] = Field(default_factory=dict)
    required_fields: List[str] = Field(default_factory=list)
    forbidden_fields: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def is_compatible_with(self, other: "SemanticContext") -> bool:
        """Check if this context is compatible with another"""
        
        # Same domain is always compatible
        if self.domain == other.domain:
            return True
        
        # General domain is compatible with everything
        if self.domain == Domain.GENERAL or other.domain == Domain.GENERAL:
            return True
        
        # Check compatibility matrix
        return self._check_domain_compatibility(other)
    
    def _check_domain_compatibility(self, other: "SemanticContext") -> bool:
        """Check if two different domains can work together"""
        
        # Define compatible domain pairs
        compatible_pairs = {
            (Domain.MEDICAL, Domain.SCIENTIFIC),
            (Domain.FINANCIAL, Domain.BUSINESS),
            (Domain.TECHNICAL, Domain.SCIENTIFIC),
            (Domain.BUSINESS, Domain.LEGAL),
        }
        
        # Check both directions
        pair1 = (self.domain, other.domain)
        pair2 = (other.domain, self.domain)
        
        return pair1 in compatible_pairs or pair2 in compatible_pairs


class SemanticType(BaseModel):
    """
    Enhanced type information with semantic meaning.
    
    Goes beyond simple type names to include domain,
    structure, and compatibility information.
    """
    
    base_type: str  # e.g., "GRAPH", "ENTITIES", "TEXT"
    semantic_tag: str  # e.g., "social_network", "knowledge_graph", "medical_records"
    context: SemanticContext
    schema_version: str = "1.0.0"
    
    @property
    def full_type(self) -> str:
        """Get full semantic type identifier"""
        return f"{self.base_type}:{self.semantic_tag}:{self.context.domain.value}"
    
    def is_compatible_with(self, other: "SemanticType") -> Tuple[bool, Optional[str]]:
        """
        Check if this type is semantically compatible with another.
        
        Returns:
            (is_compatible, reason_if_not)
        """
        
        # Check base type compatibility
        if not self._base_types_compatible(self.base_type, other.base_type):
            return False, f"Base types incompatible: {self.base_type} vs {other.base_type}"
        
        # Check semantic compatibility
        if not self._semantic_tags_compatible(self.semantic_tag, other.semantic_tag):
            return False, f"Semantic tags incompatible: {self.semantic_tag} vs {other.semantic_tag}"
        
        # Check context compatibility
        if not self.context.is_compatible_with(other.context):
            return False, f"Contexts incompatible: {self.context.domain} vs {other.context.domain}"
        
        return True, None
    
    def _base_types_compatible(self, type1: str, type2: str) -> bool:
        """Check if base types can connect"""
        
        # Same type is always compatible
        if type1 == type2:
            return True
        
        # Define valid transformations
        valid_transformations = {
            ("TEXT", "ENTITIES"),
            ("ENTITIES", "GRAPH"),
            ("GRAPH", "METRICS"),
            ("TEXT", "SUMMARY"),
            ("ENTITIES", "RELATIONSHIPS"),
            ("RELATIONSHIPS", "GRAPH"),
        }
        
        return (type1, type2) in valid_transformations
    
    def _semantic_tags_compatible(self, tag1: str, tag2: str) -> bool:
        """Check if semantic tags are compatible"""
        
        # Same tag is compatible
        if tag1 == tag2:
            return True
        
        # Define compatible tag pairs
        compatible_tags = {
            ("medical_records", "medical_entities"),
            ("medical_entities", "medical_knowledge_graph"),
            ("social_posts", "social_network"),
            ("financial_reports", "financial_entities"),
            ("financial_entities", "financial_graph"),
            ("scientific_papers", "citation_network"),
            ("legal_documents", "legal_entities"),
            ("code_files", "dependency_graph"),
            ("code_files", "code_entities"),
            ("general_text", "general_entities"),
        }
        
        return (tag1, tag2) in compatible_tags or (tag2, tag1) in compatible_tags


class SemanticValidator(ABC):
    """Base class for semantic validators"""
    
    @abstractmethod
    def validate(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """
        Validate that data matches expected semantic type.
        
        Returns:
            (is_valid, error_message_if_not)
        """
        pass


class EntitySemanticValidator(SemanticValidator):
    """Validates entity data against semantic expectations"""
    
    def validate(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate entities match expected semantic type"""
        
        if semantic_type.base_type != "ENTITIES":
            return False, f"Expected ENTITIES type, got {semantic_type.base_type}"
        
        # Check domain-specific entity types
        if semantic_type.context.domain == Domain.MEDICAL:
            return self._validate_medical_entities(data, semantic_type)
        elif semantic_type.context.domain == Domain.FINANCIAL:
            return self._validate_financial_entities(data, semantic_type)
        elif semantic_type.context.domain == Domain.SOCIAL:
            return self._validate_social_entities(data, semantic_type)
        
        # General entities - minimal validation
        return True, None
    
    def _validate_medical_entities(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate medical entities"""
        
        required_types = {"DISEASE", "SYMPTOM", "MEDICATION", "PROCEDURE"}
        
        if hasattr(data, 'entities'):
            entity_types = {e.type for e in data.entities if hasattr(e, 'type')}
            
            # Check if we have at least one medical entity type
            if not entity_types.intersection(required_types):
                return False, f"No medical entity types found. Expected at least one of {required_types}"
        
        return True, None
    
    def _validate_financial_entities(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate financial entities"""
        
        required_types = {"COMPANY", "TICKER", "AMOUNT", "CURRENCY", "TRANSACTION"}
        
        if hasattr(data, 'entities'):
            entity_types = {e.type for e in data.entities if hasattr(e, 'type')}
            
            # Check for financial entity types
            if not entity_types.intersection(required_types):
                return False, f"No financial entity types found. Expected at least one of {required_types}"
        
        return True, None
    
    def _validate_social_entities(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate social entities"""
        
        required_types = {"PERSON", "ORGANIZATION", "EVENT", "LOCATION"}
        
        if hasattr(data, 'entities'):
            entity_types = {e.type for e in data.entities if hasattr(e, 'type')}
            
            # Check for social entity types
            if not entity_types.intersection(required_types):
                return False, f"No social entity types found. Expected at least one of {required_types}"
        
        return True, None


class GraphSemanticValidator(SemanticValidator):
    """Validates graph data against semantic expectations"""
    
    def validate(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate graph matches expected semantic type"""
        
        if semantic_type.base_type != "GRAPH":
            return False, f"Expected GRAPH type, got {semantic_type.base_type}"
        
        # Check graph structure based on semantic tag
        if "social" in semantic_type.semantic_tag:
            return self._validate_social_graph(data, semantic_type)
        elif "knowledge" in semantic_type.semantic_tag:
            return self._validate_knowledge_graph(data, semantic_type)
        elif "dependency" in semantic_type.semantic_tag:
            return self._validate_dependency_graph(data, semantic_type)
        
        return True, None
    
    def _validate_social_graph(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate social network graph"""
        
        # Check for expected relationship types
        expected_rels = {"FOLLOWS", "FRIEND", "LIKES", "MENTIONS", "REPLIES_TO"}
        
        if hasattr(data, 'edges'):
            edge_types = {e.type for e in data.edges if hasattr(e, 'type')}
            
            if not edge_types.intersection(expected_rels):
                return False, f"No social relationship types found. Expected {expected_rels}"
        
        return True, None
    
    def _validate_knowledge_graph(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate knowledge graph"""
        
        # Check for knowledge relationships
        expected_rels = {"IS_A", "PART_OF", "RELATED_TO", "CAUSES", "TREATS"}
        
        if hasattr(data, 'edges'):
            edge_types = {e.type for e in data.edges if hasattr(e, 'type')}
            
            if not edge_types.intersection(expected_rels):
                return False, f"No knowledge relationship types found. Expected {expected_rels}"
        
        return True, None
    
    def _validate_dependency_graph(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate dependency graph"""
        
        # Check for dependency relationships
        expected_rels = {"DEPENDS_ON", "IMPORTS", "CALLS", "EXTENDS", "IMPLEMENTS"}
        
        if hasattr(data, 'edges'):
            edge_types = {e.type for e in data.edges if hasattr(e, 'type')}
            
            if not edge_types.intersection(expected_rels):
                return False, f"No dependency relationship types found. Expected {expected_rels}"
        
        return True, None


class SemanticTypeRegistry:
    """Registry for semantic types and validators"""
    
    def __init__(self):
        self.types: Dict[str, SemanticType] = {}
        self.validators: Dict[str, SemanticValidator] = {
            "ENTITIES": EntitySemanticValidator(),
            "GRAPH": GraphSemanticValidator(),
        }
    
    def register_type(self, semantic_type: SemanticType):
        """Register a semantic type"""
        self.types[semantic_type.full_type] = semantic_type
    
    def register_validator(self, base_type: str, validator: SemanticValidator):
        """Register a validator for a base type"""
        self.validators[base_type] = validator
    
    def validate_data(self, data: Any, semantic_type: SemanticType) -> Tuple[bool, Optional[str]]:
        """Validate data against semantic type"""
        
        validator = self.validators.get(semantic_type.base_type)
        if not validator:
            return True, None  # No validator = pass by default
        
        return validator.validate(data, semantic_type)
    
    def check_compatibility(self, type1: SemanticType, type2: SemanticType) -> Tuple[bool, Optional[str]]:
        """Check if two semantic types are compatible"""
        return type1.is_compatible_with(type2)
    
    def find_compatible_tools(self, 
                            input_type: SemanticType,
                            available_tools: List[Tuple[str, SemanticType, SemanticType]]) -> List[str]:
        """
        Find tools that can process the given semantic type.
        
        Args:
            input_type: The semantic type of input data
            available_tools: List of (tool_id, input_semantic_type, output_semantic_type)
            
        Returns:
            List of compatible tool IDs
        """
        compatible = []
        
        for tool_id, tool_input_type, tool_output_type in available_tools:
            is_compat, _ = input_type.is_compatible_with(tool_input_type)
            if is_compat:
                compatible.append(tool_id)
        
        return compatible


# Predefined semantic types for common use cases

MEDICAL_RECORDS = SemanticType(
    base_type="TEXT",
    semantic_tag="medical_records",
    context=SemanticContext(
        domain=Domain.MEDICAL,
        required_fields=["patient_id", "diagnosis", "treatment"]
    )
)

MEDICAL_ENTITIES = SemanticType(
    base_type="ENTITIES",
    semantic_tag="medical_entities",
    context=SemanticContext(
        domain=Domain.MEDICAL,
        required_fields=["entity_type", "medical_code"]
    )
)

MEDICAL_KNOWLEDGE_GRAPH = SemanticType(
    base_type="GRAPH",
    semantic_tag="medical_knowledge_graph",
    context=SemanticContext(
        domain=Domain.MEDICAL,
        constraints={"relationship_types": ["TREATS", "CAUSES", "CONTRAINDICATED"]}
    )
)

SOCIAL_POSTS = SemanticType(
    base_type="TEXT",
    semantic_tag="social_posts",
    context=SemanticContext(
        domain=Domain.SOCIAL,
        required_fields=["author", "timestamp", "content"]
    )
)

SOCIAL_NETWORK = SemanticType(
    base_type="GRAPH",
    semantic_tag="social_network",
    context=SemanticContext(
        domain=Domain.SOCIAL,
        constraints={"relationship_types": ["FOLLOWS", "FRIEND", "LIKES"]}
    )
)

FINANCIAL_REPORTS = SemanticType(
    base_type="TEXT",
    semantic_tag="financial_reports",
    context=SemanticContext(
        domain=Domain.FINANCIAL,
        required_fields=["company", "period", "revenue"]
    )
)

FINANCIAL_ENTITIES = SemanticType(
    base_type="ENTITIES",
    semantic_tag="financial_entities",
    context=SemanticContext(
        domain=Domain.FINANCIAL,
        required_fields=["ticker", "amount", "currency"]
    )
)

CODE_FILES = SemanticType(
    base_type="TEXT",
    semantic_tag="code_files",
    context=SemanticContext(
        domain=Domain.TECHNICAL,
        required_fields=["language", "file_path"]
    )
)

DEPENDENCY_GRAPH = SemanticType(
    base_type="GRAPH",
    semantic_tag="dependency_graph",
    context=SemanticContext(
        domain=Domain.TECHNICAL,
        constraints={"relationship_types": ["DEPENDS_ON", "IMPORTS", "CALLS"]}
    )
)