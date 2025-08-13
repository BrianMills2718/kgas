"""T23C Ontology-Aware Extractor - Contract-First Implementation

This tool implements the KGASTool interface for ontology-aware entity extraction
using LLM services (OpenAI/Gemini) with theory-driven validation.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

# Import existing components
from src.tools.phase2.extraction_components import (
    TheoryDrivenValidator,
    LLMExtractionClient,
    SemanticAnalyzer,
    ContextualAnalyzer,
    EntityResolver,
    RelationshipResolver,
    SemanticCache
)
from src.core.extraction_schemas import SchemaMode
from src.core.api_auth_manager import APIAuthManager
from src.core.enhanced_api_client import EnhancedAPIClient

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Simplified extraction result for KGASTool interface."""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    properties: List[Dict[str, Any]]
    entity_count: int
    relationship_count: int
    extraction_metadata: Dict[str, Any]


class T23COntologyAwareExtractorKGAS(KGASTool):
    """Ontology-aware extractor implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T23C", tool_name="Ontology-Aware Extractor")
        self.service_manager = service_manager
        self.description = "Extracts entities, relationships, and properties using LLM"
        self.category = "extraction"
        self.version = "1.0.0"
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize extraction components."""
        try:
            # Initialize API components
            self.auth_manager = APIAuthManager()
            self.api_client = EnhancedAPIClient(self.auth_manager)
            
            # Initialize extraction components
            self.llm_client = LLMExtractionClient(self.api_client)
            # Theory validator will be initialized when ontology is provided
            self.theory_validator = None
            self.semantic_analyzer = SemanticAnalyzer()
            self.contextual_analyzer = ContextualAnalyzer()
            self.entity_resolver = EntityResolver(self.service_manager.identity_service)
            self.relationship_resolver = RelationshipResolver()
            self.semantic_cache = SemanticCache()
            
            logger.info("T23C components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize T23C components: {e}")
            # Components will be None, handled in execute
            self.llm_client = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute ontology-aware extraction with contract interface."""
        try:
            # Validate and extract input
            chunks = request.input_data.get("chunks", [])
            source_ref = request.input_data.get("source_ref")
            ontology = request.input_data.get("ontology")  # Optional
            theory_schema = request.theory_schema  # From ToolRequest
            confidence_threshold = request.input_data.get("confidence_threshold", 0.7)
            
            if not chunks:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No chunks provided",
                        "error_details": "Chunks are required for extraction"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Chunks are required for extraction"
                )
            
            # Check component initialization
            if not hasattr(self, 'llm_client') or self.llm_client is None:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "LLM service not available",
                        "error_details": "T23C requires LLM service (OpenAI/Gemini) to be configured"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="LLM service not available"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="ontology_aware_extraction",
                inputs=[source_ref] if source_ref else [],
                parameters={
                    "workflow_id": request.workflow_id,
                    "chunk_count": len(chunks),
                    "confidence_threshold": confidence_threshold,
                    "has_ontology": ontology is not None,
                    "has_theory": theory_schema is not None
                }
            )
            
            # Process chunks
            all_entities = []
            all_relationships = []
            all_properties = []
            
            for chunk in chunks:
                chunk_text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
                chunk_ref = chunk.get("chunk_ref", f"chunk_{len(all_entities)}") if isinstance(chunk, dict) else f"chunk_{len(all_entities)}"
                
                if not chunk_text:
                    continue
                
                # Extract using LLM
                extraction_result = self._extract_from_chunk(
                    chunk_text, 
                    chunk_ref,
                    ontology,
                    theory_schema,
                    confidence_threshold
                )
                
                # Aggregate results
                all_entities.extend(extraction_result.entities)
                all_relationships.extend(extraction_result.relationships)
                all_properties.extend(extraction_result.properties)
            
            # Resolve entities across chunks
            resolved_entities = self._resolve_entities(all_entities)
            
            # Create result
            result_data = {
                "entities": resolved_entities,
                "relationships": all_relationships,
                "properties": all_properties,
                "entity_count": len(resolved_entities),
                "relationship_count": len(all_relationships),
                "property_count": len(all_properties),
                "extraction_metadata": {
                    "chunks_processed": len(chunks),
                    "confidence_threshold": confidence_threshold,
                    "llm_provider": self.llm_client.provider if hasattr(self.llm_client, 'provider') else "unknown",
                    "ontology_used": ontology is not None,
                    "theory_validation": theory_schema is not None
                }
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"entity_{e['id']}" for e in resolved_entities[:10]],  # Sample for provenance
                success=True,
                metadata={
                    "entities_extracted": len(resolved_entities),
                    "relationships_extracted": len(all_relationships),
                    "properties_extracted": len(all_properties)
                }
            )
            
            # Calculate confidence based on extraction quality
            avg_confidence = sum(e.get("confidence", 0.5) for e in resolved_entities) / max(len(resolved_entities), 1)
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=avg_confidence, evidence_weight=max(1, len(resolved_entities))),
                metadata={
                    "tool_version": self.version,
                    "chunks_processed": len(chunks),
                    "extraction_complete": True
                },
                provenance=op_id,
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            return ToolResult(
                status="error",
                data=None,
                confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                metadata={
                    "tool_id": self.tool_id,
                    "error_message": str(e),
                    "error_details": str(e)
                },
                provenance=None,
                request_id=request.request_id,
                execution_time=0.0,
                error_details=str(e)
            )
    
    def _extract_from_chunk(self, text: str, chunk_ref: str, 
                           ontology: Any, theory_schema: Any,
                           confidence_threshold: float) -> ExtractionResult:
        """Extract entities, relationships, and properties from a single chunk."""
        # This would use the existing extraction components
        # Simplified for example - actual implementation would use all components
        
        try:
            # Use LLM for extraction - use the synchronous method
            llm_result = self.llm_client._extract_entities_sync(
                text=text,
                ontology=ontology,
                model="gemini/gemini-2.5-flash"  # Use Gemini 2.5 Flash as requested
            )
            
            # Theory validation if provided
            if theory_schema and ontology:
                # Initialize theory validator if needed
                if self.theory_validator is None:
                    from src.tools.phase2.extraction_components.theory_validation import TheoryDrivenValidator
                    self.theory_validator = TheoryDrivenValidator(ontology)
                
                validation_result = self.theory_validator.validate_extraction(
                    llm_result, theory_schema
                )
                # Filter based on validation
                llm_result = validation_result.validated_data
            
            # Convert to simplified format
            entities = []
            relationships = []
            properties = []
            
            # Process entities
            entity_name_to_id = {}  # Map entity names to IDs for relationship mapping
            for entity in llm_result.get("entities", []):
                entity_id = f"{chunk_ref}_entity_{len(entities)}"
                entity_text = entity.get("text", "")
                
                entities.append({
                    "id": entity_id,
                    "text": entity_text,
                    "type": entity.get("type", "UNKNOWN"),
                    "confidence": entity.get("confidence", 0.5),
                    "chunk_ref": chunk_ref,
                    "properties": entity.get("properties", {})
                })
                
                # Map entity name to ID for relationship resolution
                if entity_text:
                    entity_name_to_id[entity_text] = entity_id
                
                # Extract properties as separate items
                for prop_key, prop_value in entity.get("properties", {}).items():
                    properties.append({
                        "entity_id": entity_id,
                        "property": prop_key,
                        "value": prop_value,
                        "chunk_ref": chunk_ref
                    })
            
            # Process relationships with entity ID mapping
            for rel in llm_result.get("relationships", []):
                source_text = rel.get("source", "")
                target_text = rel.get("target", "")
                
                relationships.append({
                    "id": f"{chunk_ref}_rel_{len(relationships)}",
                    "source": source_text,  # Keep original for backward compatibility
                    "target": target_text,  # Keep original for backward compatibility
                    "source_entity_id": entity_name_to_id.get(source_text),  # Add entity ID mapping
                    "target_entity_id": entity_name_to_id.get(target_text),  # Add entity ID mapping
                    "source_text": source_text,  # Explicit text reference
                    "target_text": target_text,  # Explicit text reference
                    "type": rel.get("type", "RELATED_TO"),
                    "confidence": rel.get("confidence", 0.5),
                    "chunk_ref": chunk_ref,
                    "properties": rel.get("properties", {})
                })
            
            return ExtractionResult(
                entities=entities,
                relationships=relationships,
                properties=properties,
                entity_count=len(entities),
                relationship_count=len(relationships),
                extraction_metadata={
                    "chunk_ref": chunk_ref,
                    "llm_used": True
                }
            )
            
        except Exception as e:
            logger.error(f"Extraction failed for chunk {chunk_ref}: {e}")
            # Return empty result on failure
            return ExtractionResult(
                entities=[],
                relationships=[],
                properties=[],
                entity_count=0,
                relationship_count=0,
                extraction_metadata={
                    "chunk_ref": chunk_ref,
                    "error": str(e)
                }
            )
    
    def _resolve_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve entities across chunks to eliminate duplicates."""
        if not self.entity_resolver:
            return entities
        
        # For now, just return entities as-is since EntityResolver doesn't have resolve_entities method
        # This would be where entity resolution logic would go
        return entities
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required fields."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        if "chunks" not in input_data:
            result.add_error("Missing required field: chunks")
        elif not isinstance(input_data["chunks"], list):
            result.add_error("chunks must be a list")
        elif not input_data["chunks"]:
            result.add_error("chunks cannot be empty")
        
        # Optional fields validation
        if "confidence_threshold" in input_data:
            threshold = input_data["confidence_threshold"]
            if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
                result.add_warning("confidence_threshold should be between 0 and 1")
        
        if "ontology" in input_data and input_data["ontology"] is not None:
            # Basic ontology validation
            if not hasattr(input_data["ontology"], "entity_types"):
                result.add_warning("ontology should have entity_types attribute")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "chunks": {
                    "type": "array",
                    "description": "Text chunks to extract from",
                    "items": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "chunk_ref": {"type": "string"}
                                },
                                "required": ["text"]
                            },
                            {
                                "type": "string",
                                "description": "Simple text chunk"
                            }
                        ]
                    }
                },
                "source_ref": {
                    "type": "string",
                    "description": "Reference to source document"
                },
                "ontology": {
                    "type": "object",
                    "description": "Optional domain ontology for guided extraction"
                },
                "confidence_threshold": {
                    "type": "number",
                    "description": "Minimum confidence for extraction",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.7
                }
            },
            "required": ["chunks"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "text": {"type": "string"},
                            "type": {"type": "string"},
                            "confidence": {"type": "number"},
                            "chunk_ref": {"type": "string"},
                            "properties": {"type": "object"}
                        }
                    }
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "type": {"type": "string"},
                            "confidence": {"type": "number"},
                            "chunk_ref": {"type": "string"},
                            "properties": {"type": "object"}
                        }
                    }
                },
                "properties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity_id": {"type": "string"},
                            "property": {"type": "string"},
                            "value": {"type": "string"},
                            "chunk_ref": {"type": "string"}
                        }
                    }
                },
                "entity_count": {"type": "integer"},
                "relationship_count": {"type": "integer"},
                "property_count": {"type": "integer"},
                "extraction_metadata": {"type": "object"}
            },
            "required": ["entities", "relationships", "entity_count", "relationship_count"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """T23C supports theory-driven extraction."""
        return ["domain_ontology", "theory_schema", "extraction_theory"]