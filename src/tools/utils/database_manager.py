import uuid
from neo4j import GraphDatabase
from datetime import datetime

class DatabaseSessionManager:
    """Manage isolated database sessions"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        self.session_id = str(uuid.uuid4())[:8]
        self.session_prefix = f"TEST_{self.session_id}_"
    
    def cleanup_session(self):
        """Remove all nodes/edges from current session"""
        with self.driver.session() as session:
            # Delete only nodes with our session prefix
            session.run(f"""
                MATCH (n) 
                WHERE n.session_id = $session_id
                DETACH DELETE n
            """, session_id=self.session_id)
    
    def cleanup_all(self):
        """Complete database cleanup (use with caution)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def get_node_count(self):
        """Get count of nodes in current session"""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n)
                WHERE n.session_id = $session_id
                RETURN count(n) as count
            """, session_id=self.session_id)
            return result.single()["count"]