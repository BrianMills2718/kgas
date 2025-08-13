"""
Enhanced Reasoning Trace Store - SQLite Backend

Provides persistent storage and retrieval for reasoning traces with efficient
querying, indexing, and analysis capabilities.

NO MOCKS - Production-ready SQLite implementation for reasoning trace persistence.
"""

import sqlite3
import json
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import logging

from .reasoning_trace import ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType

logger = logging.getLogger(__name__)


class ReasoningTraceStore:
    """SQLite-based storage for reasoning traces with full CRUD operations"""
    
    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        """Initialize the reasoning trace store
        
        Args:
            db_path: Path to SQLite database file. If None, uses 'reasoning_traces.db'
        """
        self.db_path = Path(db_path) if db_path else Path("reasoning_traces.db")
        self.conn = None
        self.owns_connection = True
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Performance tracking
        self._query_count = 0
        self._total_query_time_ms = 0
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"ReasoningTraceStore initialized with database: {self.db_path}")
    
    def _initialize_database(self) -> None:
        """Initialize SQLite database with required tables and indexes"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
            
            self._create_tables()
            self._create_indexes()
            
            logger.info("Reasoning trace database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize reasoning trace database: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Create database tables for reasoning traces"""
        
        # Reasoning traces table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                trace_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                operation_id TEXT,
                session_id TEXT,
                root_step_ids TEXT,  -- JSON array
                total_steps INTEGER DEFAULT 0,
                total_duration_ms INTEGER,
                overall_confidence REAL DEFAULT 0.0,
                success BOOLEAN DEFAULT TRUE,
                initial_context TEXT,  -- JSON
                final_outputs TEXT,    -- JSON
                metadata TEXT,         -- JSON
                completed_at TEXT,
                error_message TEXT
            )
        """)
        
        # Reasoning steps table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS reasoning_steps (
                step_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                decision_level TEXT NOT NULL,
                reasoning_type TEXT NOT NULL,
                decision_point TEXT NOT NULL,
                context TEXT,              -- JSON
                options_considered TEXT,   -- JSON array
                decision_made TEXT,        -- JSON
                reasoning_text TEXT,
                confidence_score REAL DEFAULT 0.0,
                parent_step_id TEXT,
                child_step_ids TEXT,       -- JSON array
                duration_ms INTEGER,
                metadata TEXT,             -- JSON
                error_occurred BOOLEAN DEFAULT FALSE,
                error_message TEXT,
                FOREIGN KEY (trace_id) REFERENCES reasoning_traces(trace_id),
                FOREIGN KEY (parent_step_id) REFERENCES reasoning_steps(step_id)
            )
        """)
        
        # Query performance metrics table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS query_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_type TEXT NOT NULL,
                execution_time_ms INTEGER,
                rows_affected INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """)
        
        self.conn.commit()
    
    def _create_indexes(self) -> None:
        """Create database indexes for performance optimization"""
        
        indexes = [
            # Reasoning traces indexes
            "CREATE INDEX IF NOT EXISTS idx_traces_operation_type ON reasoning_traces(operation_type)",
            "CREATE INDEX IF NOT EXISTS idx_traces_operation_id ON reasoning_traces(operation_id)",
            "CREATE INDEX IF NOT EXISTS idx_traces_session_id ON reasoning_traces(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_traces_created_at ON reasoning_traces(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_traces_success ON reasoning_traces(success)",
            "CREATE INDEX IF NOT EXISTS idx_traces_completed_at ON reasoning_traces(completed_at)",
            
            # Reasoning steps indexes
            "CREATE INDEX IF NOT EXISTS idx_steps_trace_id ON reasoning_steps(trace_id)",
            "CREATE INDEX IF NOT EXISTS idx_steps_decision_level ON reasoning_steps(decision_level)",
            "CREATE INDEX IF NOT EXISTS idx_steps_reasoning_type ON reasoning_steps(reasoning_type)",
            "CREATE INDEX IF NOT EXISTS idx_steps_parent_id ON reasoning_steps(parent_step_id)",
            "CREATE INDEX IF NOT EXISTS idx_steps_timestamp ON reasoning_steps(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_steps_confidence ON reasoning_steps(confidence_score)",
            "CREATE INDEX IF NOT EXISTS idx_steps_error ON reasoning_steps(error_occurred)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_traces_type_success ON reasoning_traces(operation_type, success)",
            "CREATE INDEX IF NOT EXISTS idx_steps_trace_level ON reasoning_steps(trace_id, decision_level)",
            "CREATE INDEX IF NOT EXISTS idx_steps_trace_type ON reasoning_steps(trace_id, reasoning_type)"
        ]
        
        for index_sql in indexes:
            self.conn.execute(index_sql)
        
        self.conn.commit()
    
    def store_trace(self, trace: ReasoningTrace) -> bool:
        """Store a complete reasoning trace
        
        Args:
            trace: ReasoningTrace to store
            
        Returns:
            Success status
        """
        start_time = datetime.now()
        
        try:
            with self._lock:
                # Store trace record
                self.conn.execute("""
                    INSERT OR REPLACE INTO reasoning_traces (
                        trace_id, created_at, operation_type, operation_id, session_id,
                        root_step_ids, total_steps, total_duration_ms, overall_confidence,
                        success, initial_context, final_outputs, metadata, completed_at, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trace.trace_id,
                    trace.created_at,
                    trace.operation_type,
                    trace.operation_id,
                    trace.session_id,
                    json.dumps(trace.root_step_ids),
                    trace.total_steps,
                    trace.total_duration_ms,
                    trace.overall_confidence,
                    trace.success,
                    json.dumps(trace.initial_context),
                    json.dumps(trace.final_outputs),
                    json.dumps(trace.metadata),
                    trace.completed_at,
                    trace.error_message
                ))
                
                # Store all reasoning steps
                for step in trace.all_steps.values():
                    self.conn.execute("""
                        INSERT OR REPLACE INTO reasoning_steps (
                            step_id, trace_id, timestamp, decision_level, reasoning_type,
                            decision_point, context, options_considered, decision_made,
                            reasoning_text, confidence_score, parent_step_id, child_step_ids,
                            duration_ms, metadata, error_occurred, error_message
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        step.step_id,
                        trace.trace_id,
                        step.timestamp,
                        step.decision_level.value,
                        step.reasoning_type.value,
                        step.decision_point,
                        json.dumps(step.context),
                        json.dumps(step.options_considered),
                        json.dumps(step.decision_made),
                        step.reasoning_text,
                        step.confidence_score,
                        step.parent_step_id,
                        json.dumps(step.child_step_ids),
                        step.duration_ms,
                        json.dumps(step.metadata),
                        step.error_occurred,
                        step.error_message
                    ))
                
                self.conn.commit()
                
                # Record metrics
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._record_query_metric("store_trace", execution_time, trace.total_steps)
                
                logger.debug(f"Stored reasoning trace {trace.trace_id} with {trace.total_steps} steps")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store reasoning trace {trace.trace_id}: {e}")
            self.conn.rollback()
            
            # Record error metric
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._record_query_metric("store_trace", execution_time, 0, False, str(e))
            return False
    
    def get_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Retrieve a reasoning trace by ID
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            ReasoningTrace if found, None otherwise
        """
        start_time = datetime.now()
        
        try:
            with self._lock:
                # Get trace record
                cursor = self.conn.execute("""
                    SELECT * FROM reasoning_traces WHERE trace_id = ?
                """, (trace_id,))
                
                trace_row = cursor.fetchone()
                if not trace_row:
                    return None
                
                # Convert row to dict
                columns = [desc[0] for desc in cursor.description]
                trace_data = dict(zip(columns, trace_row))
                
                # Parse JSON fields
                trace_data['root_step_ids'] = json.loads(trace_data['root_step_ids'] or '[]')
                trace_data['initial_context'] = json.loads(trace_data['initial_context'] or '{}')
                trace_data['final_outputs'] = json.loads(trace_data['final_outputs'] or '{}')
                trace_data['metadata'] = json.loads(trace_data['metadata'] or '{}')
                
                # Get all steps for this trace
                cursor = self.conn.execute("""
                    SELECT * FROM reasoning_steps WHERE trace_id = ? ORDER BY timestamp
                """, (trace_id,))
                
                steps = {}
                for step_row in cursor:
                    step_columns = [desc[0] for desc in cursor.description]
                    step_data = dict(zip(step_columns, step_row))
                    
                    # Parse JSON fields and convert enums
                    step_data['context'] = json.loads(step_data['context'] or '{}')
                    step_data['options_considered'] = json.loads(step_data['options_considered'] or '[]')
                    step_data['decision_made'] = json.loads(step_data['decision_made'] or '{}')
                    step_data['child_step_ids'] = json.loads(step_data['child_step_ids'] or '[]')
                    step_data['metadata'] = json.loads(step_data['metadata'] or '{}')
                    step_data['decision_level'] = DecisionLevel(step_data['decision_level'])
                    step_data['reasoning_type'] = ReasoningType(step_data['reasoning_type'])
                    
                    # Remove trace_id from step data (not in ReasoningStep constructor)
                    step_data.pop('trace_id', None)
                    
                    step = ReasoningStep(**step_data)
                    steps[step.step_id] = step
                
                # Create trace object
                trace_data['all_steps'] = steps
                trace = ReasoningTrace(**trace_data)
                
                # Record metrics
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._record_query_metric("get_trace", execution_time, len(steps))
                
                return trace
                
        except Exception as e:
            logger.error(f"Failed to retrieve reasoning trace {trace_id}: {e}")
            
            # Record error metric
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._record_query_metric("get_trace", execution_time, 0, False, str(e))
            return None
    
    def query_traces(
        self,
        operation_type: Optional[str] = None,
        operation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        success_only: Optional[bool] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ReasoningTrace]:
        """Query reasoning traces with filters
        
        Args:
            operation_type: Filter by operation type
            operation_id: Filter by operation ID
            session_id: Filter by session ID
            success_only: Filter by success status
            since: Filter traces created after this time
            until: Filter traces created before this time
            limit: Maximum number of results
            offset: Results offset for pagination
            
        Returns:
            List of matching ReasoningTrace objects
        """
        start_time = datetime.now()
        
        try:
            with self._lock:
                # Build query
                conditions = []
                params = []
                
                if operation_type:
                    conditions.append("operation_type = ?")
                    params.append(operation_type)
                
                if operation_id:
                    conditions.append("operation_id = ?")
                    params.append(operation_id)
                
                if session_id:
                    conditions.append("session_id = ?")
                    params.append(session_id)
                
                if success_only is not None:
                    conditions.append("success = ?")
                    params.append(success_only)
                
                if since:
                    conditions.append("created_at >= ?")
                    params.append(since.isoformat())
                
                if until:
                    conditions.append("created_at <= ?")
                    params.append(until.isoformat())
                
                # Build final query
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                query = f"""
                    SELECT trace_id FROM reasoning_traces
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                params.extend([limit, offset])
                
                cursor = self.conn.execute(query, params)
                trace_ids = [row[0] for row in cursor]
                
                # Get full traces
                traces = []
                for trace_id in trace_ids:
                    trace = self.get_trace(trace_id)
                    if trace:
                        traces.append(trace)
                
                # Record metrics
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._record_query_metric("query_traces", execution_time, len(traces))
                
                logger.debug(f"Found {len(traces)} traces matching query")
                return traces
                
        except Exception as e:
            logger.error(f"Failed to query reasoning traces: {e}")
            
            # Record error metric
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._record_query_metric("query_traces", execution_time, 0, False, str(e))
            return []
    
    def query_steps(
        self,
        trace_id: Optional[str] = None,
        decision_level: Optional[DecisionLevel] = None,
        reasoning_type: Optional[ReasoningType] = None,
        confidence_threshold: Optional[float] = None,
        errors_only: bool = False,
        limit: int = 100
    ) -> List[ReasoningStep]:
        """Query reasoning steps with filters
        
        Args:
            trace_id: Filter by trace ID
            decision_level: Filter by decision level
            reasoning_type: Filter by reasoning type
            confidence_threshold: Minimum confidence score
            errors_only: Only return steps with errors
            limit: Maximum number of results
            
        Returns:
            List of matching ReasoningStep objects
        """
        start_time = datetime.now()
        
        try:
            with self._lock:
                # Build query
                conditions = []
                params = []
                
                if trace_id:
                    conditions.append("trace_id = ?")
                    params.append(trace_id)
                
                if decision_level:
                    conditions.append("decision_level = ?")
                    params.append(decision_level.value)
                
                if reasoning_type:
                    conditions.append("reasoning_type = ?")
                    params.append(reasoning_type.value)
                
                if confidence_threshold is not None:
                    conditions.append("confidence_score >= ?")
                    params.append(confidence_threshold)
                
                if errors_only:
                    conditions.append("error_occurred = TRUE")
                
                # Build final query
                where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
                query = f"""
                    SELECT * FROM reasoning_steps
                    {where_clause}
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                params.append(limit)
                
                cursor = self.conn.execute(query, params)
                
                steps = []
                for row in cursor:
                    columns = [desc[0] for desc in cursor.description]
                    step_data = dict(zip(columns, row))
                    
                    # Parse JSON fields and convert enums
                    step_data['context'] = json.loads(step_data['context'] or '{}')
                    step_data['options_considered'] = json.loads(step_data['options_considered'] or '[]')
                    step_data['decision_made'] = json.loads(step_data['decision_made'] or '{}')
                    step_data['child_step_ids'] = json.loads(step_data['child_step_ids'] or '[]')
                    step_data['metadata'] = json.loads(step_data['metadata'] or '{}')
                    step_data['decision_level'] = DecisionLevel(step_data['decision_level'])
                    step_data['reasoning_type'] = ReasoningType(step_data['reasoning_type'])
                    
                    # Remove trace_id (not in ReasoningStep constructor)
                    step_data.pop('trace_id', None)
                    
                    step = ReasoningStep(**step_data)
                    steps.append(step)
                
                # Record metrics
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._record_query_metric("query_steps", execution_time, len(steps))
                
                return steps
                
        except Exception as e:
            logger.error(f"Failed to query reasoning steps: {e}")
            
            # Record error metric
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._record_query_metric("query_steps", execution_time, 0, False, str(e))
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reasoning trace statistics
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with self._lock:
                stats = {}
                
                # Total traces
                cursor = self.conn.execute("SELECT COUNT(*) FROM reasoning_traces")
                stats['total_traces'] = cursor.fetchone()[0]
                
                # Successful vs failed traces
                cursor = self.conn.execute("SELECT success, COUNT(*) FROM reasoning_traces GROUP BY success")
                success_stats = {bool(row[0]): row[1] for row in cursor}
                stats['successful_traces'] = success_stats.get(True, 0)
                stats['failed_traces'] = success_stats.get(False, 0)
                
                # Total steps
                cursor = self.conn.execute("SELECT COUNT(*) FROM reasoning_steps")
                stats['total_steps'] = cursor.fetchone()[0]
                
                # Steps by decision level
                cursor = self.conn.execute("""
                    SELECT decision_level, COUNT(*) FROM reasoning_steps GROUP BY decision_level
                """)
                stats['steps_by_level'] = {row[0]: row[1] for row in cursor}
                
                # Steps by reasoning type
                cursor = self.conn.execute("""
                    SELECT reasoning_type, COUNT(*) FROM reasoning_steps GROUP BY reasoning_type
                """)
                stats['steps_by_type'] = {row[0]: row[1] for row in cursor}
                
                # Average confidence
                cursor = self.conn.execute("SELECT AVG(confidence_score) FROM reasoning_steps")
                avg_confidence = cursor.fetchone()[0]
                stats['average_confidence'] = avg_confidence if avg_confidence else 0.0
                
                # Error statistics
                cursor = self.conn.execute("SELECT COUNT(*) FROM reasoning_steps WHERE error_occurred = TRUE")
                stats['steps_with_errors'] = cursor.fetchone()[0]
                
                # Query performance
                stats['total_queries'] = self._query_count
                stats['average_query_time_ms'] = (self._total_query_time_ms / max(1, self._query_count))
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def delete_trace(self, trace_id: str) -> bool:
        """Delete a reasoning trace and all its steps
        
        Args:
            trace_id: Trace to delete
            
        Returns:
            Success status
        """
        try:
            with self._lock:
                # Delete steps first (foreign key constraint)
                self.conn.execute("DELETE FROM reasoning_steps WHERE trace_id = ?", (trace_id,))
                
                # Delete trace
                cursor = self.conn.execute("DELETE FROM reasoning_traces WHERE trace_id = ?", (trace_id,))
                
                self.conn.commit()
                
                success = cursor.rowcount > 0
                logger.debug(f"Deleted reasoning trace {trace_id}: {success}")
                return success
                
        except Exception as e:
            logger.error(f"Failed to delete reasoning trace {trace_id}: {e}")
            self.conn.rollback()
            return False
    
    def cleanup_old_traces(self, older_than_days: int = 30) -> int:
        """Clean up old reasoning traces
        
        Args:
            older_than_days: Delete traces older than this many days
            
        Returns:
            Number of traces deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            with self._lock:
                # Get trace IDs to delete
                cursor = self.conn.execute("""
                    SELECT trace_id FROM reasoning_traces 
                    WHERE created_at < ? AND completed_at IS NOT NULL
                """, (cutoff_date.isoformat(),))
                
                trace_ids = [row[0] for row in cursor]
                
                # Delete traces and steps
                deleted_count = 0
                for trace_id in trace_ids:
                    if self.delete_trace(trace_id):
                        deleted_count += 1
                
                logger.info(f"Cleaned up {deleted_count} old reasoning traces")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old traces: {e}")
            return 0
    
    def _record_query_metric(
        self, 
        query_type: str, 
        execution_time_ms: int, 
        rows_affected: int,
        success: bool = True, 
        error_message: Optional[str] = None
    ) -> None:
        """Record query performance metrics"""
        try:
            self.conn.execute("""
                INSERT INTO query_metrics 
                (timestamp, query_type, execution_time_ms, rows_affected, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                query_type,
                execution_time_ms,
                rows_affected,
                success,
                error_message
            ))
            
            # Update in-memory counters
            self._query_count += 1
            self._total_query_time_ms += execution_time_ms
            
        except Exception as e:
            logger.warning(f"Failed to record query metrics: {e}")
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn and self.owns_connection:
            self.conn.close()
            logger.info("ReasoningTraceStore connection closed")


# Factory function
def create_reasoning_trace_store(db_path: Optional[Union[str, Path]] = None) -> ReasoningTraceStore:
    """Create and initialize a reasoning trace store
    
    Args:
        db_path: Optional database path
        
    Returns:
        Initialized ReasoningTraceStore
    """
    return ReasoningTraceStore(db_path)