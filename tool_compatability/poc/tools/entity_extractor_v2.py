"""
EntityExtractor V2 - Enhanced with multi-input support for custom ontologies
PhD Research: Tool composition with domain-specific extraction
"""

import os
import json
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import hashlib
from pathlib import Path

import litellm  # For LLM calls

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parents[3] / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

from ..base_tool_v2 import BaseToolV2
from ..data_types import DataType, DataSchema
from ..tool_context import ToolContext


class EntityExtractorV2Config(BaseModel):
    """Configuration for EntityExtractorV2"""
    model: str = Field(default="gemini/gemini-2.0-flash-exp", description="LLM model to use")
    temperature: float = Field(default=0.1, description="Model temperature")
    max_tokens: int = Field(default=4000, description="Maximum tokens for response")
    confidence_threshold: float = Field(default=0.5, description="Minimum confidence for entities")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "gemini/gemini-2.0-flash-exp",
                "temperature": 0.1,
                "max_tokens": 4000,
                "confidence_threshold": 0.5
            }
        }


class EntityExtractorV2(BaseToolV2[DataSchema.TextData, DataSchema.EntitiesData, EntityExtractorV2Config]):
    """
    Enhanced entity extractor with multi-input support.
    
    Key features:
    - Accepts custom ontologies via context
    - Uses extraction rules from context
    - Supports domain-specific entity types
    """
    
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
    
    def default_config(self) -> EntityExtractorV2Config:
        return EntityExtractorV2Config()
    
    def _execute(self, input_data: DataSchema.TextData, context: ToolContext) -> DataSchema.EntitiesData:
        """
        Extract entities using custom ontology from context.
        
        Args:
            input_data: Text to extract entities from
            context: Contains ontology and extraction rules
        """
        
        # Check for API key
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY environment variable is required")
        
        # Get custom ontology from context
        ontology = context.get_param(self.tool_id, "ontology", default={})
        extraction_rules = context.get_param(self.tool_id, "rules", default={})
        
        # Build prompt with ontology
        prompt = self._build_prompt(input_data.content, ontology, extraction_rules)
        
        # Store prompt for testing
        self.last_prompt = prompt
        
        # Call LLM
        entities, relationships = self._extract_with_llm(prompt)
        
        # Apply confidence threshold from rules
        threshold = extraction_rules.get("confidence_threshold", self.config.confidence_threshold)
        filtered_entities = [e for e in entities if e.confidence >= threshold]
        
        # Create result
        return DataSchema.EntitiesData(
            entities=filtered_entities,
            relationships=relationships,
            source_checksum=input_data.checksum if hasattr(input_data, 'checksum') else "",
            extraction_model=self.config.model,
            extraction_timestamp=datetime.now().isoformat()
        )
    
    def _build_prompt(self, text: str, ontology: Dict[str, Any], rules: Dict[str, Any]) -> str:
        """Build extraction prompt with custom ontology."""
        
        prompt = f"""Extract named entities from the following text according to the provided ontology.

ONTOLOGY:
{json.dumps(ontology, indent=2)}

EXTRACTION RULES:
{json.dumps(rules, indent=2)}

TEXT TO ANALYZE:
{text}

INSTRUCTIONS:
1. Identify all entities that match the types defined in the ontology
2. For each entity, extract the properties specified in the ontology
3. Assign confidence scores (0.0 to 1.0) based on how certain you are
4. Include entity positions if requested in rules
5. Extract relationships between entities if requested

Return the results as JSON with this structure:
{{
    "entities": [
        {{
            "id": "unique_id",
            "text": "entity text",
            "type": "ENTITY_TYPE",
            "confidence": 0.95,
            "start_pos": 0,
            "end_pos": 10,
            "properties": {{}}
        }}
    ],
    "relationships": [
        {{
            "source_id": "entity1_id",
            "target_id": "entity2_id",
            "relation_type": "RELATIONSHIP_TYPE",
            "confidence": 0.9
        }}
    ]
}}
"""
        return prompt
    
    def _extract_with_llm(self, prompt: str) -> tuple[List[DataSchema.Entity], List[DataSchema.Relationship]]:
        """Call LLM and parse response."""
        
        try:
            # Call LLM
            response = litellm.completion(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are an expert entity extraction system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Parse response
            response_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback parsing
                self.logger.warning("Failed to parse JSON, using fallback")
                result = {"entities": [], "relationships": []}
            
            # Convert to our schema
            entities = []
            for i, ent in enumerate(result.get("entities", [])):
                entity = DataSchema.Entity(
                    id=ent.get("id", f"e{i+1}"),
                    text=ent.get("text", ""),
                    type=ent.get("type", "UNKNOWN"),
                    confidence=float(ent.get("confidence", 0.5)),
                    start_pos=ent.get("start_pos"),
                    end_pos=ent.get("end_pos"),
                    metadata=ent.get("properties", {})
                )
                entities.append(entity)
            
            relationships = []
            for rel in result.get("relationships", []):
                relationship = DataSchema.Relationship(
                    source_id=rel.get("source_id", ""),
                    target_id=rel.get("target_id", ""),
                    relation_type=rel.get("relation_type", "RELATED"),
                    confidence=float(rel.get("confidence", 0.5)),
                    metadata=rel.get("metadata", {})
                )
                relationships.append(relationship)
            
            return entities, relationships
            
        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            # Return empty results on failure
            return [], []