"""T68 PageRank Calculator - Contract-First Implementation

This tool implements the KGASTool interface for calculating PageRank centrality
scores for entities in the Neo4j graph using NetworkX.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
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
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

logger = logging.getLogger(__name__)


@dataclass
class PageRankResult:
    """Result of PageRank calculation."""
    entities_processed: int
    scores_calculated: int
    top_entities: List[Tuple[str, float]]
    graph_metrics: Dict[str, Any]
    iterations_used: int
    convergence_achieved: bool


class T68PageRankKGAS(KGASTool):
    """PageRank calculator implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T68", tool_name="PageRank Calculator")
        self.service_manager = service_manager
        self.description = "Calculates PageRank centrality scores for entities in graph"
        self.category = "graph_analysis"
        self.version = "1.0.0"
        
        # PageRank algorithm parameters
        self.damping_factor = 0.85
        self.max_iterations = 100
        self.tolerance = 1e-6
        self.min_score = 0.0001
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Check NetworkX availability
        if not NETWORKX_AVAILABLE:
            logger.warning("NetworkX not available. Install with: pip install networkx")
        
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
            
            logger.info("Neo4j connection established for T68")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute PageRank calculation."""
        start_time = datetime.now()
        
        try:
            # Validate requirements
            if not NETWORKX_AVAILABLE:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "NetworkX not available",
                        "error_details": "NetworkX required for PageRank calculation. Install with: pip install networkx"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="NetworkX not available"
                )
            
            if not self.driver:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "Neo4j not available",
                        "error_details": "Neo4j connection required for PageRank calculation"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Neo4j not available"
                )
            
            # Extract parameters
            entity_type = request.input_data.get("entity_type")  # Optional filter
            top_k = request.input_data.get("top_k", 20)
            damping = request.input_data.get("damping_factor", self.damping_factor)
            store_scores = request.input_data.get("store_scores", True)
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="pagerank_calculation",
                inputs=[],
                parameters={
                    "workflow_id": request.workflow_id,
                    "entity_type": entity_type,
                    "top_k": top_k,
                    "damping_factor": damping,
                    "store_scores": store_scores
                }
            )
            
            # Load graph from Neo4j
            nx_graph = self._load_graph_from_neo4j(entity_type)
            
            if nx_graph.number_of_nodes() == 0:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No nodes in graph",
                        "error_details": "Graph is empty, cannot calculate PageRank"
                    },
                    provenance=op_id,
                    request_id=request.request_id,
                    execution_time=(datetime.now() - start_time).total_seconds(),
                    error_details="No nodes in graph"
                )
            
            # Calculate PageRank
            result = self._calculate_pagerank(nx_graph, damping, top_k)
            
            # Store scores in Neo4j if requested
            if store_scores:
                self._store_scores_in_neo4j(result.top_entities, entity_type)
            
            # Create result data
            result_data = {
                "entities_processed": result.entities_processed,
                "scores_calculated": result.scores_calculated,
                "top_entities": [
                    {
                        "entity_id": entity_id,
                        "canonical_name": self._get_entity_name(entity_id),
                        "pagerank_score": score,
                        "rank": rank + 1
                    }
                    for rank, (entity_id, score) in enumerate(result.top_entities)
                ],
                "graph_metrics": result.graph_metrics,
                "algorithm_metrics": {
                    "iterations_used": result.iterations_used,
                    "convergence_achieved": result.convergence_achieved,
                    "damping_factor": damping,
                    "tolerance": self.tolerance
                },
                "scores_stored": store_scores
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"pagerank_{e['entity_id']}" for e in result_data['top_entities'][:10]],
                success=True,
                metadata={
                    "entities_processed": result.entities_processed,
                    "top_score": result.top_entities[0][1] if result.top_entities else 0
                }
            )
            
            # Calculate confidence based on convergence
            confidence_value = 0.95 if result.convergence_achieved else 0.8
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=confidence_value, evidence_weight=result.entities_processed),
                metadata={
                    "tool_version": self.version,
                    "calculation_complete": True,
                    "graph_loaded": True
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
    
    def _load_graph_from_neo4j(self, entity_type: Optional[str] = None) -> nx.Graph:
        """Load graph from Neo4j into NetworkX."""
        nx_graph = nx.Graph()
        
        with self.driver.session() as session:
            # Load nodes
            if entity_type:
                node_query = """
                    MATCH (e:Entity {entity_type: $entity_type})
                    RETURN e.entity_id AS id, e.canonical_name AS name, 
                           e.entity_type AS type, e.confidence AS confidence
                """
                nodes = session.run(node_query, entity_type=entity_type)
            else:
                node_query = """
                    MATCH (e:Entity)
                    RETURN e.entity_id AS id, e.canonical_name AS name, 
                           e.entity_type AS type, e.confidence AS confidence
                """
                nodes = session.run(node_query)
            
            # Add nodes to graph
            for node in nodes:
                if node['id'] is not None:  # Skip nodes with null entity_id
                    nx_graph.add_node(
                        node['id'],
                        name=node['name'] or "Unknown",
                        type=node['type'] or "UNKNOWN",
                        confidence=node['confidence'] or 0.5
                    )
            
            # Load edges
            edge_query = """
                MATCH (s:Entity)-[r]->(t:Entity)
                WHERE s.entity_id IN $node_ids AND t.entity_id IN $node_ids
                RETURN s.entity_id AS source, t.entity_id AS target, 
                       type(r) AS type, r.weight AS weight
            """
            
            node_ids = list(nx_graph.nodes())
            if node_ids:
                edges = session.run(edge_query, node_ids=node_ids)
                
                # Add edges to graph
                for edge in edges:
                    weight = edge['weight'] if edge['weight'] else 0.5
                    nx_graph.add_edge(
                        edge['source'],
                        edge['target'],
                        type=edge['type'],
                        weight=weight
                    )
        
        logger.info(f"Loaded graph with {nx_graph.number_of_nodes()} nodes and {nx_graph.number_of_edges()} edges")
        return nx_graph
    
    def _calculate_pagerank(self, graph: nx.Graph, damping: float, top_k: int) -> PageRankResult:
        """Calculate PageRank scores using NetworkX."""
        # Calculate PageRank
        try:
            pagerank_scores = nx.pagerank(
                graph,
                alpha=damping,
                max_iter=self.max_iterations,
                tol=self.tolerance
            )
            convergence_achieved = True
            iterations_used = self.max_iterations  # NetworkX doesn't expose actual iterations
        except nx.PowerIterationFailedConvergence as e:
            pagerank_scores = e.pagerank
            convergence_achieved = False
            iterations_used = self.max_iterations
            logger.warning(f"PageRank did not converge after {iterations_used} iterations")
        
        # Filter out very low scores
        filtered_scores = {
            node: score for node, score in pagerank_scores.items()
            if score >= self.min_score
        }
        
        # Sort by score
        sorted_scores = sorted(
            filtered_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Get top K
        top_entities = sorted_scores[:top_k]
        
        # Calculate graph metrics
        graph_metrics = {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "density": nx.density(graph),
            "is_connected": nx.is_connected(graph),
            "number_of_components": nx.number_connected_components(graph),
            "average_degree": sum(dict(graph.degree()).values()) / max(graph.number_of_nodes(), 1)
        }
        
        return PageRankResult(
            entities_processed=len(pagerank_scores),
            scores_calculated=len(filtered_scores),
            top_entities=top_entities,
            graph_metrics=graph_metrics,
            iterations_used=iterations_used,
            convergence_achieved=convergence_achieved
        )
    
    def _store_scores_in_neo4j(self, top_entities: List[Tuple[str, float]], entity_type: Optional[str]):
        """Store PageRank scores back to Neo4j."""
        with self.driver.session() as session:
            # Clear existing scores
            if entity_type:
                session.run("""
                    MATCH (e:Entity {entity_type: $entity_type})
                    REMOVE e.pagerank_score
                """, entity_type=entity_type)
            else:
                session.run("""
                    MATCH (e:Entity)
                    REMOVE e.pagerank_score
                """)
            
            # Store new scores
            for entity_id, score in top_entities:
                session.run("""
                    MATCH (e:Entity {entity_id: $entity_id})
                    SET e.pagerank_score = $score,
                        e.pagerank_updated = datetime()
                """, entity_id=entity_id, score=score)
    
    def _get_entity_name(self, entity_id: str) -> str:
        """Get canonical name for entity."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {entity_id: $entity_id})
                RETURN e.canonical_name AS name
            """, entity_id=entity_id)
            
            record = result.single()
            return record['name'] if record else entity_id
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input parameters."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        # Optional parameters validation
        if "entity_type" in input_data:
            if not isinstance(input_data["entity_type"], str):
                result.add_warning("entity_type should be a string")
        
        if "top_k" in input_data:
            top_k = input_data["top_k"]
            if not isinstance(top_k, int) or top_k < 1:
                result.add_warning("top_k should be a positive integer")
        
        if "damping_factor" in input_data:
            damping = input_data["damping_factor"]
            if not isinstance(damping, (int, float)) or damping < 0 or damping > 1:
                result.add_warning("damping_factor should be between 0 and 1")
        
        if "store_scores" in input_data:
            if not isinstance(input_data["store_scores"], bool):
                result.add_warning("store_scores should be a boolean")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "entity_type": {
                    "type": "string",
                    "description": "Optional entity type filter"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of top entities to return",
                    "minimum": 1,
                    "default": 20
                },
                "damping_factor": {
                    "type": "number",
                    "description": "PageRank damping factor",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.85
                },
                "store_scores": {
                    "type": "boolean",
                    "description": "Whether to store scores in Neo4j",
                    "default": True
                }
            },
            "required": []  # All parameters are optional
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "entities_processed": {"type": "integer"},
                "scores_calculated": {"type": "integer"},
                "top_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "entity_id": {"type": "string"},
                            "canonical_name": {"type": "string"},
                            "pagerank_score": {"type": "number"},
                            "rank": {"type": "integer"}
                        }
                    }
                },
                "graph_metrics": {
                    "type": "object",
                    "properties": {
                        "total_nodes": {"type": "integer"},
                        "total_edges": {"type": "integer"},
                        "density": {"type": "number"},
                        "is_connected": {"type": "boolean"},
                        "number_of_components": {"type": "integer"},
                        "average_degree": {"type": "number"}
                    }
                },
                "algorithm_metrics": {
                    "type": "object",
                    "properties": {
                        "iterations_used": {"type": "integer"},
                        "convergence_achieved": {"type": "boolean"},
                        "damping_factor": {"type": "number"},
                        "tolerance": {"type": "number"}
                    }
                },
                "scores_stored": {"type": "boolean"}
            },
            "required": ["entities_processed", "scores_calculated", "top_entities", "graph_metrics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """T68 supports graph theories."""
        return ["graph_theory", "centrality_theory"]
    
    def cleanup(self):
        """Clean up Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None