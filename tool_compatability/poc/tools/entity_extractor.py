"""
EntityExtractor Tool - Extracts entities using Gemini LLM

This tool uses Google's Gemini model to extract named entities
and relationships from text.
"""

import os
import json
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import hashlib
from pathlib import Path

import litellm  # REQUIRED - fail fast if not available

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (Digimons directory)
    env_path = Path(__file__).resolve().parents[3] / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not installed, rely on environment variables being set
    pass

from ..base_tool import BaseTool
from ..data_types import DataType, DataSchema


class EntityExtractorConfig(BaseModel):
    """Configuration for EntityExtractor"""
    model: str = Field(default="gemini/gemini-2.0-flash-exp", description="LLM model to use")
    temperature: float = Field(default=0.1, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Maximum tokens for response")
    confidence_threshold: float = Field(default=0.5, description="Minimum confidence for entities")
    # NO MOCK MODE - fail fast philosophy
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "gemini/gemini-2.0-flash-exp",
                "temperature": 0.1,
                "max_tokens": 4000,
                "confidence_threshold": 0.5,
                "mock_mode": False
            }
        }


class EntityExtractor(BaseTool[DataSchema.TextData, DataSchema.EntitiesData, EntityExtractorConfig]):
    """
    Extracts named entities and relationships from text using LLM.
    
    This tool:
    - Sends text to Gemini for entity extraction
    - Parses structured response into entities and relationships
    - Validates confidence scores
    - Handles API errors gracefully
    """
    
    __version__ = "1.0.0"
    
    # ========== Type Definitions ==========
    
    @property
    def input_type(self) -> DataType:
        return DataType.TEXT
    
    @property
    def output_type(self) -> DataType:
        return DataType.ENTITIES
    
    @property
    def input_schema(self) -> Type[DataSchema.TextData]:
        return DataSchema.TextData
    
    @property
    def output_schema(self) -> Type[DataSchema.EntitiesData]:
        return DataSchema.EntitiesData
    
    @property
    def config_schema(self) -> Type[EntityExtractorConfig]:
        return EntityExtractorConfig
    
    def default_config(self) -> EntityExtractorConfig:
        # FAIL FAST - require API key
        return EntityExtractorConfig()
    
    # ========== Core Implementation ==========
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create prompt for entity extraction"""
        return f"""Extract all named entities and relationships from the following text.

Return ONLY a valid JSON object with this exact structure:
{{
    "entities": [
        {{
            "id": "unique_id",
            "text": "entity text",
            "type": "PERSON|ORG|LOCATION|PRODUCT|EVENT|DATE|OTHER",
            "confidence": 0.0-1.0,
            "context": "surrounding context"
        }}
    ],
    "relationships": [
        {{
            "source_id": "entity_id_1",
            "target_id": "entity_id_2",
            "relation_type": "WORKS_FOR|LOCATED_IN|OWNS|PARTICIPATES_IN|OTHER",
            "confidence": 0.0-1.0,
            "evidence": "text supporting this relationship"
        }}
    ]
}}

Text to analyze:
{text[:3000]}  # Limit to 3000 chars for prompt

Remember: Return ONLY the JSON object, no additional text."""
    
    # NO MOCK EXTRACTION - removed per fail-fast philosophy
    
    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """Call LLM for entity extraction - NO FALLBACKS"""
        # Verify API key is available
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY environment variable is required")
            
        response = litellm.completion(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an expert entity extraction system. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format={"type": "json_object"}
        )
        
        # Parse response - fail if invalid
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _execute(self, input_data: DataSchema.TextData) -> DataSchema.EntitiesData:
        """
        Extract entities from text.
        
        Args:
            input_data: Text to analyze
            
        Returns:
            EntitiesData with extracted entities and relationships
        """
        text = input_data.content
        
        # Create prompt
        prompt = self._create_extraction_prompt(text)
        
        # Call LLM
        self.logger.info(f"Extracting entities using {self.config.model}")
        extraction_result = self._call_llm(prompt)
        
        # Convert to Entity objects
        entities = []
        for e in extraction_result.get("entities", []):
            # Filter by confidence
            if e.get("confidence", 0) >= self.config.confidence_threshold:
                entity = DataSchema.Entity(
                    id=e["id"],
                    text=e["text"],
                    type=e["type"],
                    confidence=e.get("confidence", 0.5),
                    metadata={"context": e.get("context", "")}
                )
                entities.append(entity)
        
        # Convert to Relationship objects
        relationships = []
        for r in extraction_result.get("relationships", []):
            # Filter by confidence
            if r.get("confidence", 0) >= self.config.confidence_threshold:
                relationship = DataSchema.Relationship(
                    source_id=r["source_id"],
                    target_id=r["target_id"],
                    relation_type=r["relation_type"],
                    confidence=r.get("confidence", 0.5),
                    metadata={"evidence": r.get("evidence", "")}
                )
                relationships.append(relationship)
        
        # Log results
        self.logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
        
        # Create result
        return DataSchema.EntitiesData(
            entities=entities,
            relationships=relationships,
            source_checksum=input_data.checksum,
            extraction_model=self.config.model,
            extraction_timestamp=datetime.now().isoformat()
        )
    
    # ========== Utility Methods ==========
    
    @classmethod
    def extract_from_text(cls, text: str, **config_kwargs) -> DataSchema.EntitiesData:
        """
        Convenience method to extract entities directly from text.
        
        Args:
            text: Text to analyze
            **config_kwargs: Configuration overrides
            
        Returns:
            EntitiesData with extracted entities
        """
        # Create text data
        text_data = DataSchema.TextData.from_string(text)
        
        # Create extractor with config
        config = EntityExtractorConfig(**config_kwargs)
        extractor = cls(config)
        
        # Process and return
        result = extractor.process(text_data)
        if result.success:
            return result.data
        else:
            raise RuntimeError(f"Failed to extract entities: {result.error}")