"""
T23A SpaCy NER KGAS Wrapper

DEPRECATED: Use T23C (Ontology-Aware Extractor) instead.
T23C provides superior LLM-based extraction that extracts entities, relationships, 
and properties in a single pass with better context understanding.

This tool is kept for backwards compatibility only and will be removed in a future version.
"""

from typing import Dict, Any, Optional
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
from src.core.service_manager import ServiceManager
import spacy
import logging
import warnings

logger = logging.getLogger(__name__)

# Issue deprecation warning when module is imported
warnings.warn(
    "T23A SpaCy NER is deprecated. Use T23C (Ontology-Aware Extractor) instead. "
    "T23C provides better extraction with entities, relationships, and properties in one LLM call.",
    DeprecationWarning,
    stacklevel=2
)

class T23ASpacyNERKGAS(KGASTool):
    """KGAS wrapper for T23A SpaCy NER"""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.tool_id = "T23A"
        self.nlp = None
        self._initialize_spacy()
    
    def _initialize_spacy(self):
        """Initialize spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("SpaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Return tool information"""
        return {
            "tool_id": self.tool_id,
            "name": "SpaCy Named Entity Recognition",
            "description": "Extract named entities using spaCy",
            "version": "1.0.0",
            "category": "entity_extraction"
        }
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity extraction"""
        try:
            text = request.input_data.get("text", "")
            chunk_ref = request.input_data.get("chunk_ref", "unknown")
            
            if not self.nlp:
                return ToolResult(
                    tool_id=self.tool_id,
                    status="error",
                    data={},
                    error_details="SpaCy model not loaded"
                )
            
            # Process with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "name": ent.text,
                    "entity_type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.85  # Default confidence
                })
            
            return ToolResult(
                tool_id=self.tool_id,
                status="success",
                data={"entities": entities, "entity_count": len(entities)},
                error_details=None
            )
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return ToolResult(
                tool_id=self.tool_id,
                status="error",
                data={},
                error_details=str(e)
            )
