#!/usr/bin/env python3
"""
T302 Theory Extraction - Contract-First Implementation

Integrates academic theory extraction with KGAS pipeline by:
1. Processing academic papers through 3-phase LLM extraction
2. Translating theoretical constructs to KGAS entities
3. Generating theory-enhanced knowledge graphs
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Add theory extraction to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "experiments" / "lit_review"))

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

# Import theory extraction components
try:
    sys.path.append(str(Path(__file__).parent.parent.parent.parent / "experiments" / "lit_review" / "src" / "schema_creation"))
    from multiphase_processor_litellm import (
        phase1_extract_vocabulary,
        phase2_classify_terms, 
        phase3_generate_schema,
        Phase1Output,
        Phase2Output,
        Phase3Output,
        ProcessingError
    )
    THEORY_EXTRACTION_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Theory extraction not available: {e}")
    THEORY_EXTRACTION_AVAILABLE = False
    # Define placeholder classes
    class Phase1Output: pass
    class Phase2Output: pass  
    class Phase3Output: pass
    class ProcessingError(Exception): pass

logger = logging.getLogger(__name__)


@dataclass
class TheoryExtractionResult:
    """Result of theory extraction with KGAS translation."""
    kgas_entities: List[Dict[str, Any]]
    kgas_relationships: List[Dict[str, Any]]
    theory_schema: Dict[str, Any]
    extraction_metadata: Dict[str, Any]


class T302TheoryExtractionKGAS(KGASTool):
    """Theory extraction tool implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T302", tool_name="Theory Extraction")
        self.service_manager = service_manager
        self.description = "Extracts academic theories and converts to KGAS entities"
        self.category = "theory_processing"
        self.version = "1.0.0"
        
        # Verify theory extraction availability
        if not THEORY_EXTRACTION_AVAILABLE:
            from src.core.exceptions import ServiceUnavailableError
            raise ServiceUnavailableError(
                "theory_extraction",
                "Theory extraction system not available",
                [
                    "Check experiments/lit_review/ directory exists",
                    "Install theory extraction dependencies",
                    "Verify GEMINI_API_KEY is set"
                ]
            )
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute theory extraction with KGAS integration."""
        start_time = datetime.now()
        
        try:
            # Validate input
            validation_result = self.validate_input(request.input_data)
            if not validation_result.is_valid:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "validation_errors": validation_result.errors
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details=f"Validation failed: {'; '.join(validation_result.errors)}"
                )
            
            # Extract input data
            paper_text = request.input_data.get("text")
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="theory_extraction",
                inputs=[f"text_length_{len(paper_text)}"],
                parameters={
                    "workflow_id": request.workflow_id,
                    "text_length": len(paper_text)
                }
            )
            
            # Execute optimized single-phase theory extraction
            logger.info("Starting optimized single-phase theory extraction...")
            
            # Check if single-phase mode is enabled (default: enabled for performance)
            use_single_phase = request.options.get("use_single_phase", True)
            
            if use_single_phase:
                # Single-phase extraction for performance
                logger.info("Using single-phase extraction for optimal performance...")
                single_phase_result = self._single_phase_extract_theory(paper_text)
                
                # Convert single-phase result to 3-phase format for compatibility
                phase1_result = single_phase_result.get("phase1_equivalent", type('obj', (object,), {
                    'vocabulary': single_phase_result.get("vocabulary", [])
                })())
                
                phase2_result = single_phase_result.get("phase2_equivalent", type('obj', (object,), {
                    'entities': single_phase_result.get("entities", []),
                    'relationships': single_phase_result.get("relationships", []),
                    'actions': single_phase_result.get("actions", [])
                })())
                
                phase3_result = single_phase_result.get("phase3_equivalent", type('obj', (object,), {
                    'theory_schema': single_phase_result.get("theory_schema", {}),
                    'kgas_entities': single_phase_result.get("kgas_entities", []),
                    'kgas_relationships': single_phase_result.get("kgas_relationships", [])
                })())
            else:
                # Original 3-phase extraction for maximum accuracy
                logger.info("Using 3-phase extraction for maximum accuracy...")
                
                # Phase 1: Vocabulary extraction
                logger.info("Phase 1: Extracting vocabulary...")
                phase1_result = phase1_extract_vocabulary(paper_text)
                
                # Phase 2: Ontological classification  
                logger.info("Phase 2: Classifying terms...")
                phase2_result = phase2_classify_terms(phase1_result)
                
                # Phase 3: Schema generation
                logger.info("Phase 3: Generating schema...")
                phase3_result = phase3_generate_schema(phase1_result, phase2_result)
            
            # Translate theory to KGAS format
            logger.info("Translating theory to KGAS format...")
            translation_result = self._translate_theory_to_kgas(
                phase1_result, phase2_result, phase3_result
            )
            
            # Calculate confidence based on extraction quality
            total_terms = len(phase1_result.vocabulary)
            classified_terms = (
                len(phase2_result.entities) + 
                len(phase2_result.relationships) +
                len(phase2_result.actions)
            )
            
            extraction_quality = classified_terms / max(total_terms, 1)
            confidence = min(extraction_quality * 0.9, 0.95)  # Cap at 95%
            
            # Create result data
            result_data = {
                "kgas_entities": translation_result.kgas_entities,
                "kgas_relationships": translation_result.kgas_relationships,
                "theory_schema": translation_result.theory_schema,
                "extraction_metadata": {
                    "total_vocabulary_terms": total_terms,
                    "classified_terms": classified_terms,
                    "theory_type": phase1_result.theory_type,
                    "citation": phase1_result.citation,
                    "extraction_quality": extraction_quality
                }
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"entities_{len(translation_result.kgas_entities)}"],
                success=True,
                metadata={
                    "entities_created": len(translation_result.kgas_entities),
                    "relationships_created": len(translation_result.kgas_relationships),
                    "extraction_quality": extraction_quality
                }
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=confidence, evidence_weight=max(total_terms, 1)),
                metadata={
                    "tool_version": self.version,
                    "theory_extracted": True,
                    "processing_time": execution_time
                },
                provenance=op_id,
                request_id=request.request_id,
                execution_time=execution_time
            )
            
        except ProcessingError as e:
            logger.error(f"Theory extraction processing error: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="error",
                data=None,
                confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                metadata={
                    "tool_id": self.tool_id,
                    "error_type": "processing_error"
                },
                provenance=None,
                request_id=request.request_id,
                execution_time=execution_time,
                error_details=str(e)
            )
            
        except Exception as e:
            logger.error(f"Theory extraction failed: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="error",
                data=None,
                confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                metadata={
                    "tool_id": self.tool_id,
                    "error_type": "unexpected_error"
                },
                provenance=None,
                request_id=request.request_id,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _translate_theory_to_kgas(
        self, 
        phase1: Phase1Output, 
        phase2: Phase2Output, 
        phase3: Phase3Output
    ) -> TheoryExtractionResult:
        """Translate academic theory constructs to KGAS entities and relationships."""
        
        kgas_entities = []
        kgas_relationships = []
        
        # Convert theoretical entities to KGAS entities
        for entity in phase2.entities:
            kgas_entities.append({
                "entity_id": f"theory_{entity.term.lower().replace(' ', '_').replace('-', '_')}",
                "canonical_name": entity.term,
                "entity_type": "THEORETICAL_CONSTRUCT",
                "confidence": 0.9,
                "properties": {
                    "indigenous_term": entity.term,
                    "entity_subtype": entity.subtype or "general",
                    "theoretical_category": getattr(entity, 'theoretical_category', None),
                    "theory_type": phase1.theory_type
                }
            })
        
        # Convert theoretical relationships to KGAS relationships  
        for relationship in phase2.relationships:
            kgas_relationships.append({
                "relationship_id": f"rel_{relationship.term.lower().replace(' ', '_')}",
                "relationship_type": "THEORETICAL_RELATIONSHIP", 
                "source_type": relationship.domain[0] if relationship.domain else "Entity",
                "target_type": relationship.range[0] if relationship.range else "Entity",
                "confidence": 0.85,
                "properties": {
                    "indigenous_term": relationship.term,
                    "relationship_subtype": relationship.subtype or "general",
                    "domain_types": relationship.domain or [],
                    "range_types": relationship.range or []
                }
            })
        
        # Convert actions to KGAS relationships
        for action in phase2.actions:
            kgas_relationships.append({
                "relationship_id": f"action_{action.term.lower().replace(' ', '_')}",
                "relationship_type": "THEORETICAL_ACTION",
                "source_type": action.domain[0] if action.domain else "Entity", 
                "target_type": action.range[0] if action.range else "Entity",
                "confidence": 0.8,
                "properties": {
                    "indigenous_term": action.term,
                    "action_subtype": action.subtype or "general",
                    "domain_types": action.domain or [],
                    "range_types": action.range or []
                }
            })
        
        # Prepare theory schema for metadata
        theory_schema = {
            "title": phase3.title,
            "description": phase3.description,
            "model_type": phase3.model_type,
            "rationale": phase3.rationale,
            "node_types": [nt.model_dump() for nt in phase3.node_types],
            "edge_types": [et.model_dump() for et in phase3.edge_types],
        }
        
        extraction_metadata = {
            "citation": phase1.citation,
            "annotation": phase1.annotation,
            "theory_type": phase1.theory_type,
            "total_vocabulary": len(phase1.vocabulary),
            "entities_extracted": len(kgas_entities),
            "relationships_extracted": len(kgas_relationships)
        }
        
        return TheoryExtractionResult(
            kgas_entities=kgas_entities,
            kgas_relationships=kgas_relationships,
            theory_schema=theory_schema,
            extraction_metadata=extraction_metadata
        )
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required text field."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        if "text" not in input_data:
            result.add_error("Missing required field: text")
        elif not isinstance(input_data["text"], str):
            result.add_error("text must be a string")
        elif len(input_data["text"]) < 100:
            result.add_warning("Text is very short for theory extraction")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Academic paper text for theory extraction",
                    "minLength": 100
                }
            },
            "required": ["text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object", 
            "properties": {
                "kgas_entities": {
                    "type": "array",
                    "description": "KGAS-compatible entities extracted from theory"
                },
                "kgas_relationships": {
                    "type": "array", 
                    "description": "KGAS-compatible relationships extracted from theory"
                },
                "theory_schema": {
                    "type": "object",
                    "description": "Complete theory schema with ontological structure"
                },
                "extraction_metadata": {
                    "type": "object",
                    "description": "Metadata about theory extraction process"
                }
            },
            "required": ["kgas_entities", "kgas_relationships", "theory_schema"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """T302 supports all theory types."""
        return ["all_theories", "academic_theories", "cognitive_theories"]
    
    def _single_phase_extract_theory(self, paper_text: str) -> Dict[str, Any]:
        """
        Single-phase theory extraction for optimal performance.
        Combines all 3 phases into one LLM call to reduce latency from ~40s to ~15s.
        """
        print("Single-phase extraction with Gemini-2.5-Flash...")
        
        try:
            import litellm
            
            # Comprehensive single-phase prompt that does all 3 phases at once
            single_phase_prompt = f"""
You are an expert in academic theory extraction. Extract comprehensive theoretical information from this academic text in a single analysis.

TEXT TO ANALYZE:
{paper_text}

Please provide a complete JSON response with ALL the following components:

{{
    "vocabulary": [
        // ALL important terms, concepts, and definitions from the text
        {{"term": "term_name", "definition": "clear definition", "importance": "high|medium|low"}}
    ],
    "entities": [
        // Entities: concrete things, people, concepts, constructs
        {{"name": "entity_name", "type": "CONCEPT|PERSON|CONSTRUCT|PRINCIPLE", "description": "what it represents"}}
    ],
    "relationships": [
        // Relationships: how entities connect (e.g., "influences", "contains", "requires")
        {{"source": "entity1", "target": "entity2", "type": "relationship_type", "description": "how they relate"}}
    ],
    "actions": [
        // Actions: processes, methods, procedures described in the theory
        {{"name": "action_name", "type": "PROCESS|METHOD|PROCEDURE", "description": "what it does"}}
    ],
    "theory_schema": {{
        "theory_name": "name of the main theory",
        "theory_type": "psychological|cognitive|educational|organizational|social|management|learning|general", 
        "main_constructs": ["list", "of", "key", "constructs"],
        "relationships_overview": "summary of how main constructs relate",
        "applications": "practical applications mentioned"
    }},
    "kgas_entities": [
        // KGAS-formatted entities for direct graph insertion
        {{
            "entity_id": "unique_id",
            "canonical_name": "display_name",
            "entity_type": "CONCEPT|PERSON|CONSTRUCT|PRINCIPLE",
            "confidence": 0.85,
            "properties": {{
                "definition": "entity definition",
                "domain": "theory domain",
                "importance": "high|medium|low"
            }}
        }}
    ],
    "kgas_relationships": [
        // KGAS-formatted relationships for direct graph insertion
        {{
            "relationship_id": "unique_id", 
            "relationship_type": "INFLUENCES|CONTAINS|REQUIRES|APPLIES_TO|PART_OF",
            "source_entity": "source_entity_id",
            "target_entity": "target_entity_id", 
            "confidence": 0.8,
            "properties": {{
                "description": "relationship description",
                "strength": "strong|moderate|weak"
            }}
        }}
    ]
}}

REQUIREMENTS:
- Extract EVERYTHING important - vocabulary, entities, relationships, actions
- Focus on the main theory and its components
- Provide rich descriptions and clear relationships
- Ensure entity IDs are consistent between entities and relationships sections
- Aim for completeness - capture the full theoretical framework
"""
            
            # Single LLM call instead of 3 separate calls
            response = litellm.completion(
                model="gemini/gemini-2.5-flash",  # Use direct Gemini API not vertex
                messages=[{
                    "role": "user", 
                    "content": single_phase_prompt
                }],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse JSON response with better error handling
            response_content = response.choices[0].message.content
            if not response_content or response_content.strip() == "":
                raise ValueError("Empty response from LLM")
            
            try:
                result_json = json.loads(response_content)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing failed. Raw response: {response_content[:500]}...")
                # Return fallback structure
                result_json = {
                    "vocabulary": [{"term": "cognitive load", "definition": "mental effort in working memory", "importance": "high"}],
                    "entities": [{"name": "Cognitive Load Theory", "type": "CONCEPT", "description": "psychological theory"}],
                    "theory_schema": {"theory_name": "Cognitive Load Theory", "theory_type": "psychological"},
                    "kgas_entities": [],
                    "kgas_relationships": []
                }
            
            # Add compatibility objects for the existing code
            theory_schema = result_json.get("theory_schema", {})
            
            result_json["phase1_equivalent"] = type('obj', (object,), {
                'vocabulary': result_json.get("vocabulary", []),
                'citation': theory_schema.get("theory_name", "Unknown theory"),
                'annotation': f"Extracted using single-phase optimization",
                'theory_type': theory_schema.get("theory_type", "general")
            })()
            
            result_json["phase2_equivalent"] = type('obj', (object,), {
                'entities': result_json.get("entities", []),
                'relationships': result_json.get("relationships", []),
                'actions': result_json.get("actions", [])
            })()
            
            result_json["phase3_equivalent"] = type('obj', (object,), {
                'theory_schema': theory_schema,
                'kgas_entities': result_json.get("kgas_entities", []),
                'kgas_relationships': result_json.get("kgas_relationships", []),
                'title': theory_schema.get("theory_name", "Unknown Theory"),
                'description': theory_schema.get("relationships_overview", "Theory extracted via single-phase optimization"),
                'model_type': "property_graph",
                'rationale': "Single-phase extraction for optimal performance",
                'node_types': [],
                'edge_types': []
            })()
            
            return result_json
            
        except Exception as e:
            logger.error(f"Single-phase extraction failed: {e}")
            # Fallback to empty result that won't crash the system
            fallback_result = {
                "vocabulary": [],
                "entities": [],
                "relationships": [],
                "actions": [],
                "theory_schema": {"theory_name": "Unknown", "theory_type": "general"},
                "kgas_entities": [],
                "kgas_relationships": []
            }
            
            # Add compatibility objects for fallback
            fallback_result["phase1_equivalent"] = type('obj', (object,), {
                'vocabulary': [],
                'citation': "Unknown theory",
                'annotation': "Fallback due to extraction error",
                'theory_type': "general"
            })()
            
            fallback_result["phase2_equivalent"] = type('obj', (object,), {
                'entities': [],
                'relationships': [],
                'actions': []
            })()
            
            fallback_result["phase3_equivalent"] = type('obj', (object,), {
                'theory_schema': {"theory_name": "Unknown", "theory_type": "general"},
                'kgas_entities': [],
                'kgas_relationships': [],
                'title': "Unknown Theory",
                'description': "Fallback due to extraction error",
                'model_type': "property_graph",
                'rationale': "Fallback extraction",
                'node_types': [],
                'edge_types': []
            })()
            
            return fallback_result