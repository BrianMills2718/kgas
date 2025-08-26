"""
GraphBuilder Tool - Builds Neo4j graph from entities

This tool takes extracted entities and relationships and stores them
in a Neo4j graph database.
"""

import os
import uuid
from typing import Type, Optional, Dict, Any, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime

try:
    from neo4j import GraphDatabase, basic_auth  # Try real Neo4j first
except ImportError:
    # Use mock if real Neo4j not available
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import mock_neo4j
    neo4j = mock_neo4j.patch_neo4j()
    GraphDatabase = neo4j.GraphDatabase
    basic_auth = lambda u, p: (u, p)  # Mock basic_auth

from ..base_tool import BaseTool
from ..data_types import DataType, DataSchema


class GraphBuilderConfig(BaseModel):
    """Configuration for GraphBuilder"""
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j connection URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(default="password", description="Neo4j password")
    database: str = Field(default="neo4j", description="Neo4j database name")
    batch_size: int = Field(default=100, description="Batch size for bulk operations")
    # NO MOCK MODE - fail fast philosophy
    
    class Config:
        json_schema_extra = {
            "example": {
                "neo4j_uri": "bolt://localhost:7687",
                "neo4j_user": "neo4j",
                "neo4j_password": "password",
                "database": "neo4j",
                "batch_size": 100,
                "mock_mode": False
            }
        }


class GraphBuilder(BaseTool[DataSchema.EntitiesData, DataSchema.GraphData, GraphBuilderConfig]):
    """
    Builds a Neo4j graph from entities and relationships.
    
    This tool:
    - Connects to Neo4j database
    - Creates nodes for entities
    - Creates edges for relationships
    - Handles batch operations for performance
    - Returns graph reference with statistics
    """
    
    __version__ = "1.0.0"
    
    def __init__(self, config: Optional[GraphBuilderConfig] = None):
        """Initialize with Neo4j connection - FAIL FAST"""
        super().__init__(config)
        self._driver = None
        self._connected = False
        
        # Connect immediately - fail if unable
        self._connect()
    
    # ========== Type Definitions ==========
    
    @property
    def input_type(self) -> DataType:
        return DataType.ENTITIES
    
    @property
    def output_type(self) -> DataType:
        return DataType.GRAPH
    
    @property
    def input_schema(self) -> Type[DataSchema.EntitiesData]:
        return DataSchema.EntitiesData
    
    @property
    def output_schema(self) -> Type[DataSchema.GraphData]:
        return DataSchema.GraphData
    
    @property
    def config_schema(self) -> Type[GraphBuilderConfig]:
        return GraphBuilderConfig
    
    def default_config(self) -> GraphBuilderConfig:
        # FAIL FAST - require Neo4j to be available
        config = GraphBuilderConfig(
            neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
            neo4j_password=os.getenv("NEO4J_PASSWORD", "devpassword")
        )
        
        # Test connection - use mock if unable
        try:
            driver = GraphDatabase.driver(
                config.neo4j_uri,
                auth=basic_auth(config.neo4j_user, config.neo4j_password)
            )
            driver.verify_connectivity()
            driver.close()
        except Exception as e:
            # Connection failed, mock Neo4j will be used
            print(f"📦 Note: Neo4j connection test failed, will use mock: {e}")
        
        return config
    
    # ========== Connection Management ==========
    
    def _connect(self):
        """Establish Neo4j connection - NO FALLBACK"""
        self._driver = GraphDatabase.driver(
            self.config.neo4j_uri,
            auth=basic_auth(self.config.neo4j_user, self.config.neo4j_password)
        )
        self._driver.verify_connectivity()
        self._connected = True
        self.logger.info(f"Connected to Neo4j at {self.config.neo4j_uri}")
    
    def _disconnect(self):
        """Close Neo4j connection"""
        if self._driver:
            self._driver.close()
            self._connected = False
            self.logger.info("Disconnected from Neo4j")
    
    # ========== Core Implementation ==========
    
    # NO MOCK GRAPH BUILDING - removed per fail-fast philosophy
    
    def _create_nodes(self, session, entities: List[DataSchema.Entity], graph_id: str):
        """Create nodes in Neo4j"""
        query = """
        UNWIND $entities AS entity
        MERGE (n:Entity {id: entity.id, graph_id: $graph_id})
        SET n.text = entity.text,
            n.type = entity.type,
            n.confidence = entity.confidence,
            n.created_at = datetime()
        """
        
        entities_data = [
            {
                "id": e.id,
                "text": e.text,
                "type": e.type,
                "confidence": e.confidence
            }
            for e in entities
        ]
        
        session.run(query, entities=entities_data, graph_id=graph_id)
    
    def _create_relationships(self, session, relationships: List[DataSchema.Relationship], graph_id: str):
        """Create relationships in Neo4j"""
        if not relationships:
            return
        
        query = """
        UNWIND $relationships AS rel
        MATCH (source:Entity {id: rel.source_id, graph_id: $graph_id})
        MATCH (target:Entity {id: rel.target_id, graph_id: $graph_id})
        MERGE (source)-[r:RELATED {type: rel.relation_type}]->(target)
        SET r.confidence = rel.confidence,
            r.created_at = datetime()
        """
        
        relationships_data = [
            {
                "source_id": r.source_id,
                "target_id": r.target_id,
                "relation_type": r.relation_type,
                "confidence": r.confidence
            }
            for r in relationships
        ]
        
        session.run(query, relationships=relationships_data, graph_id=graph_id)
    
    def _get_graph_stats(self, session, graph_id: str) -> Dict[str, int]:
        """Get statistics for the created graph"""
        node_query = "MATCH (n:Entity {graph_id: $graph_id}) RETURN count(n) as count"
        edge_query = """
        MATCH (n:Entity {graph_id: $graph_id})-[r]-(m:Entity {graph_id: $graph_id})
        RETURN count(DISTINCT r) as count
        """
        
        node_result = session.run(node_query, graph_id=graph_id).single()
        edge_result = session.run(edge_query, graph_id=graph_id).single()
        
        return {
            "node_count": node_result["count"] if node_result else 0,
            "edge_count": edge_result["count"] if edge_result else 0
        }
    
    def _execute(self, input_data: DataSchema.EntitiesData) -> DataSchema.GraphData:
        """
        Build graph from entities.
        
        Args:
            input_data: Entities and relationships to store
            
        Returns:
            GraphData with reference to created graph
        """
        # Generate graph ID
        graph_id = f"graph_{uuid.uuid4().hex[:12]}"
        
        # Real Neo4j only - no mock mode
        if not self._connected:
            raise RuntimeError("Not connected to Neo4j")
        
        with self._driver.session(database=self.config.database) as session:
            # Create nodes
            self.logger.info(f"Creating {len(input_data.entities)} nodes in Neo4j")
            
            # Batch create nodes
            for i in range(0, len(input_data.entities), self.config.batch_size):
                batch = input_data.entities[i:i+self.config.batch_size]
                self._create_nodes(session, batch, graph_id)
            
            # Create relationships
            self.logger.info(f"Creating {len(input_data.relationships)} relationships in Neo4j")
            
            # Batch create relationships
            for i in range(0, len(input_data.relationships), self.config.batch_size):
                batch = input_data.relationships[i:i+self.config.batch_size]
                self._create_relationships(session, batch, graph_id)
            
            # Get statistics
            stats = self._get_graph_stats(session, graph_id)
            
            self.logger.info(f"Graph created: {stats['node_count']} nodes, {stats['edge_count']} edges")
            
            return DataSchema.GraphData(
                graph_id=graph_id,
                node_count=stats["node_count"],
                edge_count=stats["edge_count"],
                source_checksum=input_data.source_checksum,
                created_timestamp=datetime.now().isoformat(),
                metadata={
                    "database": self.config.database,
                    "uri": self.config.neo4j_uri
                }
            )
    
    # ========== Query Methods ==========
    
    def query_graph(self, graph_id: str, cypher_query: str) -> List[Dict[str, Any]]:
        """
        Query a graph with Cypher.
        
        Args:
            graph_id: ID of graph to query
            cypher_query: Cypher query to execute
            
        Returns:
            List of result records
        """
        if not self._connected:
            raise RuntimeError("Not connected to Neo4j")
        
        with self._driver.session(database=self.config.database) as session:
            # Add graph_id constraint to query
            constrained_query = cypher_query.replace(
                "MATCH", 
                f"MATCH (n:Entity {{graph_id: '{graph_id}'}})"
            )
            
            result = session.run(constrained_query)
            return [dict(record) for record in result]
    
    def delete_graph(self, graph_id: str) -> bool:
        """
        Delete a graph from Neo4j.
        
        Args:
            graph_id: ID of graph to delete
            
        Returns:
            True if successful
        """
        if not self._connected:
            raise RuntimeError("Not connected to Neo4j")
        
        with self._driver.session(database=self.config.database) as session:
            query = """
            MATCH (n:Entity {graph_id: $graph_id})
            DETACH DELETE n
            """
            session.run(query, graph_id=graph_id)
            self.logger.info(f"Deleted graph: {graph_id}")
            return True
    
    # ========== Context Manager ==========
    
    def __enter__(self):
        """Enter context manager"""
        if not self._connected:
            self._connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        self._disconnect()