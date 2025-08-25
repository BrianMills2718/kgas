"""
Pipeline Data Accumulation System

Core data structure that accumulates results as data flows through tool pipeline.
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class StageMetadata:
    """Metadata for a pipeline stage"""
    stage_name: str
    tool_id: str
    timestamp: str
    data_type: str  # Type hint for what's stored
    size_bytes: int
    dependencies: List[str] = field(default_factory=list)  # Stages this depended on


class PipelineData:
    """
    Accumulates data as it flows through a tool pipeline.
    
    Each tool adds its output as a new "stage" that subsequent tools can access.
    """
    
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        """Initialize pipeline with optional initial data"""
        self._stages: Dict[str, Any] = {}
        self._metadata: Dict[str, StageMetadata] = {}
        self._stage_order: List[str] = []  # Tracks execution order
        
        if initial_data:
            for key, value in initial_data.items():
                self.add_stage(key, value, tool_id="initial")
    
    def add_stage(self, 
                  stage_name: str, 
                  data: Any, 
                  tool_id: str,
                  dependencies: Optional[List[str]] = None) -> None:
        """
        Add output from a pipeline stage.
        
        Args:
            stage_name: Unique name for this stage (e.g., "extraction", "graph_nodes")
            data: The actual data from this stage
            tool_id: ID of the tool that created this data
            dependencies: List of stage names this stage depends on
        """
        if stage_name in self._stages:
            raise ValueError(f"Stage '{stage_name}' already exists. Use update_stage() to modify.")
        
        self._stages[stage_name] = data
        self._stage_order.append(stage_name)
        
        # Track metadata
        self._metadata[stage_name] = StageMetadata(
            stage_name=stage_name,
            tool_id=tool_id,
            timestamp=datetime.now().isoformat(),
            data_type=type(data).__name__,
            size_bytes=self._estimate_size(data),
            dependencies=dependencies or []
        )
    
    def get_stage(self, stage_name: str) -> Any:
        """
        Get data from a specific stage.
        
        Args:
            stage_name: Name of the stage to retrieve
            
        Returns:
            Data from that stage
            
        Raises:
            KeyError: If stage doesn't exist
        """
        if stage_name not in self._stages:
            available = list(self._stages.keys())
            raise KeyError(
                f"Stage '{stage_name}' not found. "
                f"Available stages: {available}"
            )
        return self._stages[stage_name]
    
    def has_stage(self, stage_name: str) -> bool:
        """Check if a stage exists"""
        return stage_name in self._stages
    
    def get_latest(self) -> Any:
        """Get the most recently added stage's data"""
        if not self._stage_order:
            return None
        latest_stage = self._stage_order[-1]
        return self._stages[latest_stage]
    
    def get_latest_stage_name(self) -> Optional[str]:
        """Get the name of the most recently added stage"""
        return self._stage_order[-1] if self._stage_order else None
    
    def list_stages(self) -> List[str]:
        """List all stage names in order of execution"""
        return self._stage_order.copy()
    
    def get_stage_metadata(self, stage_name: str) -> StageMetadata:
        """Get metadata about a stage"""
        if stage_name not in self._metadata:
            raise KeyError(f"No metadata for stage '{stage_name}'")
        return self._metadata[stage_name]
    
    def validate_dependencies(self, required_stages: List[str]) -> bool:
        """
        Check if required stages exist.
        
        Args:
            required_stages: List of stage names that must exist
            
        Returns:
            True if all required stages exist
            
        Raises:
            ValueError: If any required stage is missing
        """
        missing = [s for s in required_stages if s not in self._stages]
        if missing:
            raise ValueError(
                f"Missing required stages: {missing}. "
                f"Available: {list(self._stages.keys())}"
            )
        return True
    
    def get_lineage(self, stage_name: str) -> List[str]:
        """
        Get the lineage (dependency chain) for a stage.
        
        Args:
            stage_name: Stage to get lineage for
            
        Returns:
            List of stages in dependency order
        """
        if stage_name not in self._metadata:
            raise KeyError(f"Stage '{stage_name}' not found")
        
        lineage = []
        visited = set()
        
        def trace_deps(name: str):
            if name in visited:
                return
            visited.add(name)
            
            meta = self._metadata.get(name)
            if meta:
                for dep in meta.dependencies:
                    trace_deps(dep)
                lineage.append(name)
        
        trace_deps(stage_name)
        return lineage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary for serialization"""
        return {
            "stages": self._stages,
            "metadata": {
                name: {
                    "tool_id": meta.tool_id,
                    "timestamp": meta.timestamp,
                    "data_type": meta.data_type,
                    "dependencies": meta.dependencies
                }
                for name, meta in self._metadata.items()
            },
            "stage_order": self._stage_order
        }
    
    def _estimate_size(self, data: Any) -> int:
        """Estimate size of data in bytes"""
        try:
            # Simple estimation using JSON serialization
            return len(json.dumps(data, default=str).encode())
        except:
            # Fallback for non-serializable objects
            return 0
    
    def __repr__(self) -> str:
        stages_summary = ", ".join(self._stage_order[:5])
        if len(self._stage_order) > 5:
            stages_summary += f", ... ({len(self._stage_order)} total)"
        return f"PipelineData(stages=[{stages_summary}])"


# Example stage data structures (what tools actually work with)

@dataclass
class ExtractionResult:
    """Standard extraction output format"""
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence: float = 1.0
    
@dataclass  
class GraphNodes:
    """Graph node collection"""
    nodes: List[Dict[str, Any]]
    node_count: int
    
@dataclass
class PageRankResult:
    """PageRank analysis output"""
    scores: Dict[str, float]
    iterations: int
    convergence_delta: float