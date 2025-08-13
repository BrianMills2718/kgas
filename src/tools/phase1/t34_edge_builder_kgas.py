"""T34 Edge Builder - Contract-First Implementation

This tool implements the KGASTool interface for building relationship edges in Neo4j
from extracted relationships, with weight calculation and entity verification.
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
class EdgeBuildResult:
    """Result of edge building operation."""
    edges_created: int
    edges_skipped: int
    total_relationships: int
    neo4j_operations: int
    edges: List[Dict[str, Any]]


class T34EdgeBuilderKGAS(KGASTool):
    """Edge builder implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T34", tool_name="Edge Builder")
        self.service_manager = service_manager
        self.description = "Builds relationship edges in Neo4j from extracted relationships"
        self.category = "graph_construction"
        self.version = "1.0.0"
        
        # Weight calculation parameters
        self.min_weight = 0.1
        self.max_weight = 1.0
        self.confidence_weight_factor = 0.8
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Edge building stats
        self.edges_created = 0
        self.edges_skipped = 0
        self.relationships_processed = 0
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
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            logger.info("Neo4j connection established for T34")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute edge building with Neo4j integration."""
        start_time = datetime.now()
        
        try:
            # Validate and extract input
            relationships = request.input_data.get("relationships", [])
            source_ref = request.input_data.get("source_ref")
            verify_entities = request.input_data.get("verify_entities", True)
            
            if not relationships:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No relationships provided",
                        "error_details": "Relationships are required for edge building"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Relationships are required for edge building"
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
                        "error_details": "Neo4j connection required for edge building"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Neo4j not available"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="edge_building",
                inputs=[source_ref] if source_ref else [],
                parameters={
                    "workflow_id": request.workflow_id,
                    "relationship_count": len(relationships),
                    "verify_entities": verify_entities
                }
            )
            
            # Build edges
            result = self._build_edges(relationships, source_ref, verify_entities)
            
            # Create result data
            result_data = {
                "edges_created": result.edges_created,
                "edges_skipped": result.edges_skipped,
                "total_edges": result.edges_created,
                "total_relationships": result.total_relationships,
                "neo4j_operations": result.neo4j_operations,
                "edges": result.edges,
                "metadata": {
                    "verify_entities": verify_entities,
                    "source_ref": source_ref
                }
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"edge_{e['relationship_id']}" for e in result.edges[:10]],  # Sample for provenance
                success=True,
                metadata={
                    "edges_created": result.edges_created,
                    "edges_skipped": result.edges_skipped,
                    "neo4j_operations": result.neo4j_operations
                }
            )
            
            # Calculate confidence based on success rate
            success_rate = result.edges_created / max(len(relationships), 1)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=success_rate, evidence_weight=len(relationships)),
                metadata={
                    "tool_version": self.version,
                    "relationships_processed": len(relationships),
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
    
    def _build_edges(self, relationships: List[Dict[str, Any]], 
                    source_ref: Optional[str], 
                    verify_entities: bool) -> EdgeBuildResult:
        """Build edges in Neo4j with entity verification."""
        edges_created = 0
        edges_skipped = 0
        total_relationships = len(relationships)
        neo4j_operations = 0
        processed_edges = []
        
        with self.driver.session() as session:
            for rel_data in relationships:
                try:
                    # Extract relationship information
                    # Try multiple field names for compatibility
                    source_id = (rel_data.get("source_entity_id") or 
                               rel_data.get("source_id") or 
                               rel_data.get("source"))
                    target_id = (rel_data.get("target_entity_id") or 
                               rel_data.get("target_id") or 
                               rel_data.get("target"))
                    rel_type = rel_data.get("type", "RELATED_TO")
                    confidence = rel_data.get("confidence", 0.5)
                    properties = rel_data.get("properties", {})
                    evidence_text = rel_data.get("evidence_text", "")
                    
                    if not source_id or not target_id:
                        logger.warning(f"Skipping relationship with missing source or target: {rel_data}")
                        edges_skipped += 1
                        continue
                    
                    # Verify entities exist if requested
                    if verify_entities:
                        # Check source entity - try by entity_id first, then by text
                        result = session.run("""
                            MATCH (e:Entity {entity_id: $entity_id})
                            RETURN e
                        """, entity_id=source_id)
                        neo4j_operations += 1
                        
                        if not result.single():
                            # Try fallback to text search
                            source_text = rel_data.get("source_text") or rel_data.get("source")
                            if source_text:
                                result = session.run("""
                                    MATCH (e:Entity {text: $text})
                                    RETURN e LIMIT 1
                                """, text=source_text)
                                neo4j_operations += 1
                                
                                entity_record = result.single()
                                if entity_record:
                                    # Update source_id to the found entity's ID
                                    entity = entity_record["e"]
                                    source_id = entity.get("entity_id", source_id)
                                    logger.info(f"Found source entity by text: {source_text} -> {source_id}")
                                else:
                                    logger.warning(f"Source entity not found by ID or text: {source_id} / {source_text}")
                                    edges_skipped += 1
                                    continue
                            else:
                                logger.warning(f"Source entity not found: {source_id}")
                                edges_skipped += 1
                                continue
                        
                        # Check target entity - try by entity_id first, then by text
                        result = session.run("""
                            MATCH (e:Entity {entity_id: $entity_id})
                            RETURN e
                        """, entity_id=target_id)
                        neo4j_operations += 1
                        
                        if not result.single():
                            # Try fallback to text search
                            target_text = rel_data.get("target_text") or rel_data.get("target")
                            if target_text:
                                result = session.run("""
                                    MATCH (e:Entity {text: $text})
                                    RETURN e LIMIT 1
                                """, text=target_text)
                                neo4j_operations += 1
                                
                                entity_record = result.single()
                                if entity_record:
                                    # Update target_id to the found entity's ID
                                    entity = entity_record["e"]
                                    target_id = entity.get("entity_id", target_id)
                                    logger.info(f"Found target entity by text: {target_text} -> {target_id}")
                                else:
                                    logger.warning(f"Target entity not found by ID or text: {target_id} / {target_text}")
                                    edges_skipped += 1
                                    continue
                            else:
                                logger.warning(f"Target entity not found: {target_id}")
                                edges_skipped += 1
                                continue
                    
                    # Calculate edge weight
                    weight = self._calculate_weight(confidence)
                    
                    # Create or update relationship
                    rel_id = f"{source_id}_{rel_type}_{target_id}"
                    
                    # Check if relationship exists
                    result = session.run(f"""
                        MATCH (s:Entity {{entity_id: $source_id}})
                        MATCH (t:Entity {{entity_id: $target_id}})
                        MATCH (s)-[r:{rel_type}]->(t)
                        RETURN r
                    """, source_id=source_id, target_id=target_id)
                    neo4j_operations += 1
                    
                    if result.single():
                        # Update existing relationship
                        session.run(f"""
                            MATCH (s:Entity {{entity_id: $source_id}})
                            MATCH (t:Entity {{entity_id: $target_id}})
                            MATCH (s)-[r:{rel_type}]->(t)
                            SET r.weight = CASE 
                                    WHEN r.weight > $weight THEN r.weight 
                                    ELSE $weight 
                                END,
                                r.confidence = CASE 
                                    WHEN r.confidence > $confidence THEN r.confidence 
                                    ELSE $confidence 
                                END,
                                r.last_updated = datetime(),
                                r.evidence_count = COALESCE(r.evidence_count, 0) + 1
                            RETURN r
                        """, 
                            source_id=source_id, 
                            target_id=target_id,
                            weight=weight,
                            confidence=confidence
                        )
                    else:
                        # Create new relationship
                        session.run(f"""
                            MATCH (s:Entity {{entity_id: $source_id}})
                            MATCH (t:Entity {{entity_id: $target_id}})
                            CREATE (s)-[r:{rel_type} {{
                                relationship_id: $relationship_id,
                                weight: $weight,
                                confidence: $confidence,
                                evidence_text: $evidence_text,
                                extraction_method: $extraction_method,
                                created_at: datetime(),
                                last_updated: datetime(),
                                source_ref: $source_ref,
                                evidence_count: 1
                            }}]->(t)
                            RETURN r
                        """, 
                            source_id=source_id, 
                            target_id=target_id,
                            relationship_id=rel_id,
                            weight=weight,
                            confidence=confidence,
                            evidence_text=evidence_text[:500],  # Limit evidence text
                            extraction_method=rel_data.get("extraction_method", "pattern_based"),
                            source_ref=source_ref
                        )
                    
                    neo4j_operations += 1
                    edges_created += 1
                    
                    # Add properties if provided
                    if properties:
                        property_str = ", ".join([f"r.{k} = ${k}" for k in properties.keys()])
                        query = f"""
                            MATCH (s:Entity {{entity_id: $source_id}})
                            MATCH (t:Entity {{entity_id: $target_id}})
                            MATCH (s)-[r:{rel_type}]->(t)
                            SET {property_str}
                            RETURN r
                        """
                        params = {
                            "source_id": source_id,
                            "target_id": target_id
                        }
                        params.update(properties)
                        session.run(query, **params)
                        neo4j_operations += 1
                    
                    # Track processed edge
                    processed_edges.append({
                        "relationship_id": rel_id,
                        "source_id": source_id,
                        "target_id": target_id,
                        "type": rel_type,
                        "weight": weight,
                        "confidence": confidence
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing relationship {rel_data}: {e}")
                    edges_skipped += 1
                    continue
        
        return EdgeBuildResult(
            edges_created=edges_created,
            edges_skipped=edges_skipped,
            total_relationships=total_relationships,
            neo4j_operations=neo4j_operations,
            edges=processed_edges
        )
    
    def _calculate_weight(self, confidence: float) -> float:
        """Calculate edge weight based on confidence."""
        # Weight = confidence * weight_factor, bounded between min and max
        raw_weight = confidence * self.confidence_weight_factor
        return max(self.min_weight, min(raw_weight, self.max_weight))
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required fields."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        if "relationships" not in input_data:
            result.add_error("Missing required field: relationships")
        elif not isinstance(input_data["relationships"], list):
            result.add_error("relationships must be a list")
        elif not input_data["relationships"]:
            result.add_error("relationships cannot be empty")
        else:
            # Validate relationship structure
            for i, rel in enumerate(input_data["relationships"]):
                if not isinstance(rel, dict):
                    result.add_error(f"Relationship at index {i} must be a dictionary")
                else:
                    has_source = rel.get("source_id") or rel.get("source")
                    has_target = rel.get("target_id") or rel.get("target")
                    
                    if not has_source:
                        result.add_error(f"Relationship at index {i} missing source_id or source")
                    if not has_target:
                        result.add_error(f"Relationship at index {i} missing target_id or target")
        
        # Optional fields validation
        if "verify_entities" in input_data:
            if not isinstance(input_data["verify_entities"], bool):
                result.add_warning("verify_entities should be a boolean")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "relationships": {
                    "type": "array",
                    "description": "List of relationships to build as edges in Neo4j",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_id": {"type": "string", "description": "Source entity ID"},
                            "source": {"type": "string", "description": "Alternative to source_id"},
                            "target_id": {"type": "string", "description": "Target entity ID"},
                            "target": {"type": "string", "description": "Alternative to target_id"},
                            "type": {"type": "string", "description": "Relationship type", "default": "RELATED_TO"},
                            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "evidence_text": {"type": "string", "description": "Text evidence for relationship"},
                            "extraction_method": {"type": "string", "description": "Method used to extract"},
                            "properties": {"type": "object", "description": "Additional properties"}
                        },
                        "anyOf": [
                            {"required": ["source_id", "target_id"]},
                            {"required": ["source", "target"]}
                        ]
                    }
                },
                "source_ref": {
                    "type": "string",
                    "description": "Reference to source document"
                },
                "verify_entities": {
                    "type": "boolean",
                    "description": "Whether to verify entities exist before creating edges",
                    "default": True
                }
            },
            "required": ["relationships"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "edges_created": {"type": "integer"},
                "edges_skipped": {"type": "integer"},
                "total_edges": {"type": "integer"},
                "total_relationships": {"type": "integer"},
                "neo4j_operations": {"type": "integer"},
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "relationship_id": {"type": "string"},
                            "source_id": {"type": "string"},
                            "target_id": {"type": "string"},
                            "type": {"type": "string"},
                            "weight": {"type": "number"},
                            "confidence": {"type": "number"}
                        }
                    }
                },
                "metadata": {"type": "object"}
            },
            "required": ["edges_created", "edges_skipped", "total_edges", "edges"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """T34 supports relationship theories."""
        return ["relationship_theory", "graph_theory"]
    
    def cleanup(self):
        """Clean up Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None