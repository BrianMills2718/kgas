#!/usr/bin/env python3
"""
Reference Registry for MCP Routing Experiments

Simulates the provenance system with reference-based data tracking.
Provides lightweight simulation of KGAS's provenance service for testing.
"""

import uuid
import time
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class DataType(Enum):
    DOCUMENT = "document"
    TEXT = "text"
    CHUNKS = "chunks"
    ENTITIES = "entities"
    RELATIONSHIPS = "relationships"
    GRAPH = "graph"
    ANALYSIS = "analysis"
    QUERY_RESULTS = "query_results"
    EXPORT = "export"


@dataclass
class DataReference:
    """A reference to data stored in the registry"""
    ref_id: str
    data_type: DataType
    created_at: datetime
    created_by: str  # tool_id that created this
    source_refs: List[str] = field(default_factory=list)  # Input references used
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.85  # Simulated quality
    size_bytes: int = 1000  # Simulated data size
    confidence: float = 0.9  # Confidence in the data


@dataclass
class OperationRecord:
    """Record of a tool operation"""
    operation_id: str
    tool_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    input_refs: List[str] = field(default_factory=list)
    output_refs: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    memory_used_mb: float = 10.0  # Simulated memory usage


class MockReferenceRegistry:
    """
    Mock implementation of reference-based data registry
    Simulates KGAS provenance system for experimental purposes
    """
    
    def __init__(self):
        self.references: Dict[str, DataReference] = {}
        self.operations: Dict[str, OperationRecord] = {}
        
        # Performance tracking
        self.stats = {
            'total_references': 0,
            'total_operations': 0,
            'total_data_size_mb': 0.0,
            'avg_operation_time_ms': 0.0,
            'operations_by_tool': {},
            'lineage_depths': []
        }
        
        # Lineage tracking
        self.lineage_cache: Dict[str, List[str]] = {}  # ref_id -> operation chain
        
    def create_reference(self, 
                        data_type: DataType, 
                        created_by: str,
                        source_refs: List[str] = None,
                        metadata: Dict[str, Any] = None,
                        simulated_size_mb: float = 1.0) -> str:
        """Create a new data reference"""
        
        ref_id = f"{data_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Simulate quality degradation through processing chain
        base_quality = 0.95
        if source_refs:
            source_qualities = [self.references[ref].quality_score 
                              for ref in source_refs if ref in self.references]
            if source_qualities:
                base_quality = min(source_qualities) * 0.98  # Slight quality loss
        
        reference = DataReference(
            ref_id=ref_id,
            data_type=data_type,
            created_at=datetime.now(),
            created_by=created_by,
            source_refs=source_refs or [],
            metadata=metadata or {},
            quality_score=base_quality,
            size_bytes=int(simulated_size_mb * 1024 * 1024),
            confidence=min(0.99, base_quality + 0.05)
        )
        
        self.references[ref_id] = reference
        self.stats['total_references'] += 1
        self.stats['total_data_size_mb'] += simulated_size_mb
        
        # Update lineage cache
        self._update_lineage_cache(ref_id, source_refs or [])
        
        return ref_id
    
    def start_operation(self, tool_id: str, input_refs: List[str] = None, 
                       parameters: Dict[str, Any] = None) -> str:
        """Start tracking a tool operation"""
        
        operation_id = f"op_{uuid.uuid4().hex[:8]}"
        
        operation = OperationRecord(
            operation_id=operation_id,
            tool_id=tool_id,
            started_at=datetime.now(),
            input_refs=input_refs or [],
            parameters=parameters or {}
        )
        
        self.operations[operation_id] = operation
        
        # Update tool stats
        if tool_id not in self.stats['operations_by_tool']:
            self.stats['operations_by_tool'][tool_id] = 0
        self.stats['operations_by_tool'][tool_id] += 1
        
        return operation_id
    
    def complete_operation(self, 
                          operation_id: str, 
                          output_refs: List[str],
                          success: bool = True,
                          error_message: Optional[str] = None,
                          simulated_execution_time_ms: float = None) -> bool:
        """Complete a tool operation"""
        
        if operation_id not in self.operations:
            return False
            
        operation = self.operations[operation_id]
        operation.completed_at = datetime.now()
        operation.output_refs = output_refs
        operation.success = success
        operation.error_message = error_message
        
        # Calculate or use simulated execution time
        if simulated_execution_time_ms is not None:
            operation.execution_time_ms = simulated_execution_time_ms
        else:
            # Simulate based on complexity and data size
            input_size = sum(self.references[ref].size_bytes 
                           for ref in operation.input_refs 
                           if ref in self.references)
            operation.execution_time_ms = max(100, input_size / 10000)  # Simple simulation
        
        # Update stats
        self.stats['total_operations'] += 1
        total_time = sum(op.execution_time_ms for op in self.operations.values() 
                        if op.execution_time_ms > 0)
        self.stats['avg_operation_time_ms'] = total_time / self.stats['total_operations']
        
        return True
    
    def get_reference(self, ref_id: str) -> Optional[DataReference]:
        """Get reference information"""
        return self.references.get(ref_id)
    
    def get_lineage(self, ref_id: str) -> List[str]:
        """Get the complete lineage chain for a reference"""
        return self.lineage_cache.get(ref_id, [])
    
    def get_lineage_depth(self, ref_id: str) -> int:
        """Get the depth of processing for a reference"""
        return len(self.get_lineage(ref_id))
    
    def _update_lineage_cache(self, ref_id: str, source_refs: List[str]):
        """Update lineage cache for a new reference"""
        if not source_refs:
            self.lineage_cache[ref_id] = []
            self.stats['lineage_depths'].append(0)
            return
        
        # Find longest source lineage
        max_lineage = []
        for source_ref in source_refs:
            source_lineage = self.lineage_cache.get(source_ref, [])
            if len(source_lineage) > len(max_lineage):
                max_lineage = source_lineage
        
        # Add current reference to lineage
        new_lineage = max_lineage + [ref_id]
        self.lineage_cache[ref_id] = new_lineage
        self.stats['lineage_depths'].append(len(new_lineage))
    
    def simulate_data_access(self, ref_id: str) -> Dict[str, Any]:
        """Simulate accessing data through reference (for testing)"""
        reference = self.get_reference(ref_id)
        if not reference:
            return {"error": f"Reference {ref_id} not found"}
        
        # Return simulated data based on type
        simulated_data = {
            "ref_id": ref_id,
            "data_type": reference.data_type.value,
            "quality_score": reference.quality_score,
            "confidence": reference.confidence,
            "created_by": reference.created_by,
            "lineage_depth": self.get_lineage_depth(ref_id),
            "size_mb": reference.size_bytes / (1024 * 1024)
        }
        
        # Add type-specific simulated data
        if reference.data_type == DataType.DOCUMENT:
            simulated_data["content"] = f"Mock document content for {ref_id}"
            simulated_data["page_count"] = 10
        elif reference.data_type == DataType.ENTITIES:
            simulated_data["entity_count"] = 25
            simulated_data["entities"] = [f"Entity_{i}" for i in range(5)]
        elif reference.data_type == DataType.GRAPH:
            simulated_data["node_count"] = 50
            simulated_data["edge_count"] = 75
            
        return simulated_data
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        return {
            **self.stats,
            'references_by_type': {
                data_type.value: len([r for r in self.references.values() 
                                    if r.data_type == data_type])
                for data_type in DataType
            },
            'avg_lineage_depth': (sum(self.stats['lineage_depths']) / 
                                 len(self.stats['lineage_depths'])) 
                                if self.stats['lineage_depths'] else 0,
            'max_lineage_depth': max(self.stats['lineage_depths']) 
                               if self.stats['lineage_depths'] else 0,
            'quality_distribution': self._get_quality_distribution()
        }
    
    def _get_quality_distribution(self) -> Dict[str, int]:
        """Get distribution of data quality scores"""
        quality_ranges = {
            'high (0.9-1.0)': 0,
            'good (0.8-0.9)': 0,
            'medium (0.7-0.8)': 0,
            'low (0.0-0.7)': 0
        }
        
        for ref in self.references.values():
            if ref.quality_score >= 0.9:
                quality_ranges['high (0.9-1.0)'] += 1
            elif ref.quality_score >= 0.8:
                quality_ranges['good (0.8-0.9)'] += 1
            elif ref.quality_score >= 0.7:
                quality_ranges['medium (0.7-0.8)'] += 1
            else:
                quality_ranges['low (0.0-0.7)'] += 1
                
        return quality_ranges
    
    def export_lineage_graph(self, ref_id: str) -> Dict[str, Any]:
        """Export lineage as graph structure"""
        lineage = self.get_lineage(ref_id)
        if not lineage:
            return {"nodes": [], "edges": []}
        
        nodes = []
        edges = []
        
        for i, current_ref in enumerate(lineage):
            reference = self.get_reference(current_ref)
            if reference:
                nodes.append({
                    "id": current_ref,
                    "type": reference.data_type.value,
                    "created_by": reference.created_by,
                    "quality": reference.quality_score
                })
                
                if i > 0:
                    edges.append({
                        "source": lineage[i-1],
                        "target": current_ref,
                        "relationship": "derived_from"
                    })
        
        return {"nodes": nodes, "edges": edges}
    
    def save_state(self, filepath: str):
        """Save registry state to file"""
        state = {
            "references": {ref_id: asdict(ref) for ref_id, ref in self.references.items()},
            "operations": {op_id: asdict(op) for op_id, op in self.operations.items()},
            "stats": self.stats,
            "lineage_cache": self.lineage_cache
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def clear_registry(self):
        """Clear all data (for testing)"""
        self.references.clear()
        self.operations.clear()
        self.lineage_cache.clear()
        self.stats = {
            'total_references': 0,
            'total_operations': 0,
            'total_data_size_mb': 0.0,
            'avg_operation_time_ms': 0.0,
            'operations_by_tool': {},
            'lineage_depths': []
        }


# Global registry instance for experiments
mock_registry = MockReferenceRegistry()


if __name__ == "__main__":
    # Test the registry
    registry = MockReferenceRegistry()
    
    # Simulate a workflow
    print("Testing mock reference registry...")
    
    # 1. Load document
    doc_ref = registry.create_reference(
        DataType.DOCUMENT, 
        "load_document_pdf",
        simulated_size_mb=5.0
    )
    print(f"Created document reference: {doc_ref}")
    
    # 2. Extract entities
    op_id = registry.start_operation("extract_entities_spacy", [doc_ref])
    entities_ref = registry.create_reference(
        DataType.ENTITIES,
        "extract_entities_spacy", 
        source_refs=[doc_ref],
        simulated_size_mb=1.0
    )
    registry.complete_operation(op_id, [entities_ref])
    print(f"Created entities reference: {entities_ref}")
    
    # 3. Build graph
    op_id = registry.start_operation("build_graph_entities", [entities_ref])
    graph_ref = registry.create_reference(
        DataType.GRAPH,
        "build_graph_entities",
        source_refs=[entities_ref],
        simulated_size_mb=2.0
    )
    registry.complete_operation(op_id, [graph_ref])
    print(f"Created graph reference: {graph_ref}")
    
    # Print stats
    print(f"\nRegistry Statistics:")
    stats = registry.get_registry_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Test lineage
    print(f"\nLineage for {graph_ref}: {registry.get_lineage(graph_ref)}")
    print(f"Lineage depth: {registry.get_lineage_depth(graph_ref)}")
    
    # Test data access
    print(f"\nSimulated data access:")
    data = registry.simulate_data_access(graph_ref)
    print(json.dumps(data, indent=2))