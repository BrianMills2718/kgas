"""T31 Entity Builder - Contract-First Implementation

This tool implements the KGASTool interface for building entity nodes in Neo4j
from extracted entity mentions, with deduplication and quality assessment.
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
from src.core.standard_config import get_database_uri
import os

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

logger = logging.getLogger(__name__)


@dataclass
class EntityBuildResult:
    """Result of entity building operation."""
    entities_created: int
    entities_updated: int
    total_mentions: int
    neo4j_operations: int
    entities: List[Dict[str, Any]]


class T31EntityBuilderKGAS(KGASTool):
    """Entity builder implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T31", tool_name="Entity Builder")
        self.service_manager = service_manager
        self.description = "Builds entity nodes in Neo4j from extracted entities"
        self.category = "graph_construction"
        self.version = "1.0.0"
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Entity processing stats
        self.entities_created = 0
        self.entities_updated = 0
        self.mentions_processed = 0
        self.neo4j_operations = 0
        
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection."""
        if not NEO4J_AVAILABLE:
            logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            return
        
        try:
            # Load environment variables 
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).parent.parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Get Neo4j settings from environment
            neo4j_uri = get_database_uri()
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', '')
            
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
            
            # Test connection and create indexes
            with self.driver.session() as session:
                # Test connection
                session.run("RETURN 1")
                
                # Create indexes for entity_id and canonical_name
                session.run("""
                    CREATE INDEX entity_id_index IF NOT EXISTS
                    FOR (e:Entity) ON (e.entity_id)
                """)
                session.run("""
                    CREATE INDEX canonical_name_index IF NOT EXISTS
                    FOR (e:Entity) ON (e.canonical_name)
                """)
            
            logger.info("Neo4j connection established and indexes created")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute entity building with Neo4j integration."""
        start_time = datetime.now()
        
        try:
            # Validate and extract input
            entities = request.input_data.get("entities", [])
            source_ref = request.input_data.get("source_ref")
            merge_duplicates = request.input_data.get("merge_duplicates", True)
            
            if not entities:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No entities provided",
                        "error_details": "Entities are required for building"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Entities are required for building"
                )
            
            # Check Neo4j availability
            if not self.driver:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "Neo4j not available",
                        "error_details": "Neo4j connection required for entity building"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Neo4j not available"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="entity_building",
                inputs=[source_ref] if source_ref else [],
                parameters={
                    "workflow_id": request.workflow_id,
                    "entity_count": len(entities),
                    "merge_duplicates": merge_duplicates
                }
            )
            
            # Build entities
            result = self._build_entities(entities, source_ref, merge_duplicates)
            
            # Create result data
            result_data = {
                "entities_created": result.entities_created,
                "entities_updated": result.entities_updated,
                "total_entities": result.entities_created + result.entities_updated,
                "total_mentions": result.total_mentions,
                "neo4j_operations": result.neo4j_operations,
                "entities": result.entities,
                "metadata": {
                    "merge_duplicates": merge_duplicates,
                    "source_ref": source_ref
                }
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"entity_{e['entity_id']}" for e in result.entities[:10]],  # Sample for provenance
                success=True,
                metadata={
                    "entities_created": result.entities_created,
                    "entities_updated": result.entities_updated,
                    "neo4j_operations": result.neo4j_operations
                }
            )
            
            # Calculate confidence based on success rate
            success_rate = (result.entities_created + result.entities_updated) / max(len(entities), 1)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=success_rate, evidence_weight=len(entities)),
                metadata={
                    "tool_version": self.version,
                    "entities_processed": len(entities),
                    "building_complete": True
                },
                provenance=op_id,
                request_id=request.request_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
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
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _build_entities(self, entities: List[Dict[str, Any]], 
                       source_ref: Optional[str], 
                       merge_duplicates: bool) -> EntityBuildResult:
        """Build entities in Neo4j with deduplication."""
        entities_created = 0
        entities_updated = 0
        total_mentions = 0
        neo4j_operations = 0
        processed_entities = []
        
        with self.driver.session() as session:
            for entity_data in entities:
                try:
                    # Extract entity information
                    entity_id = entity_data.get("id") or entity_data.get("entity_id")
                    text = entity_data.get("text") or entity_data.get("canonical_name")
                    entity_type = entity_data.get("type", "UNKNOWN")
                    confidence = entity_data.get("confidence", 0.5)
                    properties = entity_data.get("properties", {})
                    
                    if not entity_id or not text:
                        logger.warning(f"Skipping entity with missing id or text: {entity_data}")
                        continue
                    
                    # Check if entity exists
                    result = session.run("""
                        MATCH (e:Entity {entity_id: $entity_id})
                        RETURN e
                    """, entity_id=entity_id)
                    
                    existing_entity = result.single()
                    neo4j_operations += 1
                    
                    if existing_entity and merge_duplicates:
                        # Update existing entity
                        session.run("""
                            MATCH (e:Entity {entity_id: $entity_id})
                            SET e.mention_count = COALESCE(e.mention_count, 0) + 1,
                                e.last_updated = datetime(),
                                e.confidence = CASE 
                                    WHEN e.confidence > $confidence THEN e.confidence 
                                    ELSE $confidence 
                                END
                            RETURN e
                        """, entity_id=entity_id, confidence=confidence)
                        entities_updated += 1
                        neo4j_operations += 1
                        
                    else:
                        # Create new entity
                        session.run("""
                            CREATE (e:Entity {
                                entity_id: $entity_id,
                                canonical_name: $canonical_name,
                                entity_type: $entity_type,
                                confidence: $confidence,
                                mention_count: 1,
                                created_at: datetime(),
                                last_updated: datetime(),
                                source_ref: $source_ref
                            })
                            RETURN e
                        """, 
                            entity_id=entity_id,
                            canonical_name=text,
                            entity_type=entity_type,
                            confidence=confidence,
                            source_ref=source_ref
                        )
                        entities_created += 1
                        neo4j_operations += 1
                    
                    # Add properties if provided
                    if properties:
                        property_str = ", ".join([f"e.{k} = ${k}" for k in properties.keys()])
                        query = f"""
                            MATCH (e:Entity {{entity_id: $entity_id}})
                            SET {property_str}
                            RETURN e
                        """
                        params = {"entity_id": entity_id}
                        params.update(properties)
                        session.run(query, **params)
                        neo4j_operations += 1
                    
                    # Track processed entity
                    processed_entities.append({
                        "entity_id": entity_id,
                        "canonical_name": text,
                        "entity_type": entity_type,
                        "confidence": confidence,
                        "created": not existing_entity or not merge_duplicates
                    })
                    
                    total_mentions += 1
                    
                except Exception as e:
                    logger.error(f"Error processing entity {entity_data}: {e}")
                    continue
        
        return EntityBuildResult(
            entities_created=entities_created,
            entities_updated=entities_updated,
            total_mentions=total_mentions,
            neo4j_operations=neo4j_operations,
            entities=processed_entities
        )
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required fields."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        if "entities" not in input_data:
            result.add_error("Missing required field: entities")
        elif not isinstance(input_data["entities"], list):
            result.add_error("entities must be a list")
        elif not input_data["entities"]:
            result.add_error("entities cannot be empty")
        else:
            # Validate entity structure
            for i, entity in enumerate(input_data["entities"]):
                if not isinstance(entity, dict):
                    result.add_error(f"Entity at index {i} must be a dictionary")
                elif not entity.get("id") and not entity.get("entity_id"):
                    result.add_error(f"Entity at index {i} missing id or entity_id")
                elif not entity.get("text") and not entity.get("canonical_name"):
                    result.add_error(f"Entity at index {i} missing text or canonical_name")
        
        # Optional fields validation
        if "merge_duplicates" in input_data:
            if not isinstance(input_data["merge_duplicates"], bool):
                result.add_warning("merge_duplicates should be a boolean")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "array",
                    "description": "List of entities to build in Neo4j",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "Entity ID"},
                            "entity_id": {"type": "string", "description": "Alternative to id"},
                            "text": {"type": "string", "description": "Entity text"},
                            "canonical_name": {"type": "string", "description": "Alternative to text"},
                            "type": {"type": "string", "description": "Entity type"},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "properties": {"type": "object", "description": "Additional properties"}
                        },
                        "anyOf": [
                            {"required": ["id", "text"]},
                            {"required": ["entity_id", "canonical_name"]}
                        ]
                    }
                },
                "source_ref": {
                    "type": "string",
                    "description": "Reference to source document"
                },
                "merge_duplicates": {
                    "type": "boolean",
                    "description": "Whether to merge duplicate entities",
                    "default": True
                }
            },
            "required": ["entities"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "entities_created": {"type": "integer"},
                "entities_updated": {"type": "integer"},
                "total_entities": {"type": "integer"},
                "total_mentions": {"type": "integer"},
                "neo4j_operations": {"type": "integer"},
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity_id": {"type": "string"},
                            "canonical_name": {"type": "string"},
                            "entity_type": {"type": "string"},
                            "confidence": {"type": "number"},
                            "created": {"type": "boolean"}
                        }
                    }
                },
                "metadata": {"type": "object"}
            },
            "required": ["entities_created", "entities_updated", "total_entities", "entities"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """T31 supports entity theories."""
        return ["entity_theory", "graph_theory"]
    
    def cleanup(self):
        """Clean up Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None