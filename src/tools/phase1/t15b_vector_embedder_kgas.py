"""T15B Vector Embedder - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import numpy as np
from datetime import datetime

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)

# No optional imports - we require OpenAI API for embeddings


class T15BVectorEmbedderKGAS(KGASTool):
    """Vector embedder implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T15B", tool_name="Vector Embedder")
        self.service_manager = service_manager
        self.description = "Generates vector embeddings from text chunks"
        self.category = "vector_processor"
        self.version = "1.0.0"
        
        # Embedding parameters
        self.model_name = "text-embedding-3-small"  # OpenAI embedding model
        self.embedding_dimension = 1536  # Dimension for text-embedding-3-small
        self.batch_size = 32
        
        # Initialize API client for embeddings
        self.api_client = None
        self._initialize_api_client()
        
    def _initialize_api_client(self):
        """Initialize check for OpenAI embeddings."""
        try:
            import os
            
            # Check if OpenAI API key is available
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("OpenAI API key not configured for embeddings")
                raise RuntimeError("OpenAI API key required for text-embedding-3-small. System will fail fast without embeddings.")
            
            logger.info(f"OpenAI API key found for {self.model_name} embeddings")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding setup: {e}")
            raise RuntimeError(f"Failed to initialize embedding setup: {e}")
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute vector embedding with contract interface."""
        try:
            # Validate and extract input
            chunks = request.input_data.get("chunks")
            source_ref = request.input_data.get("source_ref")
            
            if not chunks:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No chunks provided",
                        "error_details": "Chunks are required for embedding"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Chunks are required for embedding"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="vector_embedding",
                inputs=[source_ref] if source_ref else [],
                parameters={
                    "workflow_id": request.workflow_id,
                    "model_name": self.model_name,
                    "chunk_count": len(chunks)
                }
            )
            
            # Extract texts from chunks
            texts = []
            chunk_refs = []
            for chunk in chunks:
                if isinstance(chunk, dict):
                    text = chunk.get("text", "")
                    chunk_ref = chunk.get("chunk_ref", f"chunk_{len(texts)}")
                else:
                    # Handle simple string chunks
                    text = str(chunk)
                    chunk_ref = f"chunk_{len(texts)}"
                
                if text:
                    texts.append(text)
                    chunk_refs.append(chunk_ref)
            
            if not texts:
                # Complete with error
                self.service_manager.provenance_service.complete_operation(
                    operation_id=op_id,
                    outputs=[],
                    success=False,
                    metadata={"error": "No text content in chunks"}
                )
                
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No text content found in chunks"
                    },
                    provenance=op_id,
                    request_id=request.request_id
                )
            
            # Generate embeddings
            embeddings = self._generate_embeddings(texts)
            
            # Create embedding records
            embedding_records = []
            for i, (text, chunk_ref, embedding) in enumerate(zip(texts, chunk_refs, embeddings)):
                # Store embedding metadata (in production, would store to vector DB)
                embedding_ref = f"{chunk_ref}/embedding"
                
                # Calculate quality based on text length and model confidence
                text_length = len(text)
                quality_score = min(1.0, text_length / 1000.0) * 0.95  # Simple heuristic
                
                # Quality assessment
                quality_result = self.service_manager.quality_service.assess_confidence(
                    object_ref=embedding_ref,
                    base_confidence=quality_score,
                    factors={
                        "model_quality": 0.9,  # Model is well-regarded
                        "text_length": min(1.0, text_length / 500.0)
                    }
                )
                
                embedding_records.append({
                    "embedding_ref": embedding_ref,
                    "chunk_ref": chunk_ref,
                    "vector": embedding.tolist(),  # Convert numpy array to list
                    "dimension": len(embedding),
                    "model": self.model_name,
                    "confidence": quality_result.get("final_confidence", quality_score)
                })
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[e["embedding_ref"] for e in embedding_records],
                success=True,
                metadata={
                    "embeddings_created": len(embedding_records),
                    "embedding_dimension": self.embedding_dimension,
                    "model_name": self.model_name
                }
            )
            
            # Return result
            return ToolResult(
                status="success",
                data={
                    "embeddings": embedding_records,
                    "embedding_count": len(embedding_records),
                    "source_ref": source_ref,
                    "embedding_params": {
                        "model_name": self.model_name,
                        "dimension": self.embedding_dimension,
                        "batch_size": self.batch_size
                    }
                },
                confidence=ConfidenceScore(value=0.95, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "chunk_count": len(chunks),
                    "embeddings_created": len(embedding_records)
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
    
    def _generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for texts using OpenAI API directly."""
        try:
            import openai
            import os
            
            # Set OpenAI API key
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if not openai.api_key:
                raise RuntimeError("OPENAI_API_KEY not set in environment")
            
            all_embeddings = []
            
            # Process in batches to respect API limits
            for i in range(0, len(texts), self.batch_size):
                batch = texts[i:i + self.batch_size]
                
                # Make embedding request directly to OpenAI
                response = openai.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                
                # Extract embeddings from response
                for item in response.data:
                    embedding = np.array(item.embedding)
                    all_embeddings.append(embedding)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}. System will fail fast without embeddings.")
    
    
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
        else:
            # Validate chunk format
            for i, chunk in enumerate(input_data["chunks"]):
                if isinstance(chunk, dict):
                    if "text" not in chunk:
                        result.add_warning(f"Chunk {i} missing 'text' field")
                elif not isinstance(chunk, str):
                    result.add_error(f"Chunk {i} must be a dictionary or string")
        
        # Optional source_ref validation
        if "source_ref" in input_data:
            if not isinstance(input_data["source_ref"], str):
                result.add_warning("source_ref should be a string")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "chunks": {
                    "type": "array",
                    "description": "Text chunks to embed",
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
                }
            },
            "required": ["chunks"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "embeddings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "embedding_ref": {"type": "string"},
                            "chunk_ref": {"type": "string"},
                            "vector": {
                                "type": "array",
                                "items": {"type": "number"}
                            },
                            "dimension": {"type": "integer"},
                            "model": {"type": "string"},
                            "confidence": {"type": "number"}
                        }
                    }
                },
                "embedding_count": {"type": "integer"},
                "source_ref": {"type": "string"},
                "embedding_params": {"type": "object"}
            },
            "required": ["embeddings", "embedding_count", "embedding_params"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic embedder."""
        return []