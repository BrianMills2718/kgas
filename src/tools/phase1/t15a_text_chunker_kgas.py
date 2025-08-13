"""T15A Text Chunker - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any
import logging

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T15ATextChunkerKGAS(KGASTool):
    """Text chunker implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T15A", tool_name="Text Chunker")
        self.service_manager = service_manager
        self.description = "Splits text into overlapping chunks for processing"
        self.category = "text_processor"
        self.version = "1.0.0"
        
        # Chunking parameters (from config or defaults)
        self.chunk_size = 512  # tokens
        self.overlap_size = 50  # tokens
        self.min_chunk_size = 100  # tokens
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute text chunking with contract interface."""
        try:
            # Validate and extract input
            text_content = request.input_data.get("text_content")
            source_ref = request.input_data.get("source_ref")
            source_confidence = request.input_data.get("confidence", 1.0)
            
            if not text_content:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No text content provided",
                        "error_details": "Text content is required for chunking"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Text content is required for chunking"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="text_chunking",
                inputs=[source_ref],
                parameters={
                    "workflow_id": request.workflow_id,
                    "chunk_size": self.chunk_size,
                    "overlap_size": self.overlap_size
                }
            )
            
            # Perform chunking
            chunks = self._chunk_text(text_content)
            
            # Create chunk records with provenance
            chunk_records = []
            for i, chunk in enumerate(chunks):
                # Create chunk reference
                chunk_ref = f"{source_ref}/chunk_{i}"
                
                # Calculate chunk confidence (slight degradation)
                chunk_confidence = source_confidence * 0.98
                
                # Add quality assessment
                quality_result = self.service_manager.quality_service.assess_confidence(
                    object_ref=chunk_ref,
                    base_confidence=chunk_confidence,
                    factors={
                        "evidence_count": 1,
                        "source_reliability": 0.9
                    }
                )
                
                chunk_records.append({
                    "chunk_ref": chunk_ref,
                    "chunk_index": i,
                    "text": chunk["text"],
                    "start_pos": chunk["start_pos"],
                    "end_pos": chunk["end_pos"],
                    "token_count": chunk["token_count"],
                    "confidence": chunk_confidence,
                    "quality_score": quality_result.get("final_confidence", 0.9)
                })
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[c["chunk_ref"] for c in chunk_records],
                success=True,
                metadata={
                    "chunks_created": len(chunk_records),
                    "total_tokens": sum(c["token_count"] for c in chunk_records)
                }
            )
            
            # Return result
            return ToolResult(
                status="success",
                data={
                    "chunks": chunk_records,
                    "chunk_count": len(chunk_records),
                    "source_ref": source_ref,
                    "chunking_params": {
                        "chunk_size": self.chunk_size,
                        "overlap_size": self.overlap_size,
                        "min_chunk_size": self.min_chunk_size
                    }
                },
                confidence=ConfidenceScore(value=0.98, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "text_length": len(text_content),
                    "chunks_created": len(chunk_records)
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
    
    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        # Simple whitespace tokenization
        tokens = text.split()
        chunks = []
        
        for i in range(0, len(tokens), self.chunk_size - self.overlap_size):
            chunk_tokens = tokens[i:i + self.chunk_size]
            
            # Skip if chunk is too small
            if len(chunk_tokens) < self.min_chunk_size and i > 0:
                break
            
            chunk_text = " ".join(chunk_tokens)
            
            # Calculate character positions
            start_pos = len(" ".join(tokens[:i])) + (1 if i > 0 else 0)
            end_pos = start_pos + len(chunk_text)
            
            chunks.append({
                "text": chunk_text,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "token_count": len(chunk_tokens)
            })
        
        return chunks
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required fields."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        if "text_content" not in input_data:
            result.add_error("Missing required field: text_content")
        elif not isinstance(input_data["text_content"], str):
            result.add_error("text_content must be a string")
        elif not input_data["text_content"].strip():
            result.add_error("text_content cannot be empty")
        
        if "source_ref" not in input_data:
            result.add_error("Missing required field: source_ref")
        elif not isinstance(input_data["source_ref"], str):
            result.add_error("source_ref must be a string")
        
        # Optional confidence validation
        if "confidence" in input_data:
            conf = input_data["confidence"]
            if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                result.add_warning("confidence should be a number between 0 and 1")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "text_content": {
                    "type": "string",
                    "description": "Text content to chunk"
                },
                "source_ref": {
                    "type": "string",
                    "description": "Reference to source document"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score from source",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["text_content", "source_ref"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "chunks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "chunk_ref": {"type": "string"},
                            "chunk_index": {"type": "integer"},
                            "text": {"type": "string"},
                            "start_pos": {"type": "integer"},
                            "end_pos": {"type": "integer"},
                            "token_count": {"type": "integer"},
                            "confidence": {"type": "number"},
                            "quality_score": {"type": "number"}
                        }
                    }
                },
                "chunk_count": {"type": "integer"},
                "source_ref": {"type": "string"},
                "chunking_params": {"type": "object"}
            },
            "required": ["chunks", "chunk_count", "source_ref", "chunking_params"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic chunker."""
        return []