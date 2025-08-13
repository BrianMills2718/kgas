# Services Module - CLAUDE.md

## Overview
The `src/services/` directory contains specialized services that provide core functionality for the KGAS pipeline, including analytics, entity resolution, provenance tracking, and quality assessment.

## Current Services Architecture (2025-08-04)

### Implemented Services
The following services are currently implemented and functional:

#### Services in `/src/services/` (6 services)
- **AnalyticsService** (`analytics_service.py`): Graph analytics with performance and safety gates
- **IdentityService** (`identity_service.py`): Entity identity management and resolution  
- **ProvenanceService** (`provenance_service.py`): Operation tracking and lineage management
- **QualityService** (`quality_service.py`): Confidence assessment and quality metrics
- **CrossDocumentEntityResolver** (`cross_document_entity_resolver.py`): Multi-document entity resolution
- **EnhancedEntityResolution** (`enhanced_entity_resolution.py`): Advanced entity resolution capabilities

#### Core Services in Other Locations (3 services)
- **PipelineOrchestrator** (`src/core/orchestration/pipeline_orchestrator.py`): Workflow coordination and execution
- **ToolRegistry** (`src/core/tool_registry.py`): Tool discovery and management
- **WorkflowStateService** (`src/core/workflow_state_service.py`): Workflow state management

#### Architecture Note
**Total: 9 services implemented** across different directories. Future consolidation may move core services to `/src/services/` for consistency, but current distributed structure reflects organic development and functional separation.

### Performance-First Design
All services prioritize performance and safety:
- **Safety Gates**: Prevent resource exhaustion
- **Performance Monitoring**: Track resource usage
- **Graceful Degradation**: Fallback to approximate methods
- **Memory Management**: Monitor and manage memory usage

## Individual Service Patterns

### AnalyticsService (`analytics_service.py`)
**Purpose**: Graph analytics with performance and safety gates

**Key Patterns**:
- **Safety Gates**: Prevent resource exhaustion on large graphs
- **Performance Optimization**: Use approximate methods for large graphs
- **Memory Management**: Monitor available memory and project usage
- **Graph Analysis**: Analyze graph properties for optimization decisions

**Usage**:
```python
from src.services.analytics_service import AnalyticsService

analytics = AnalyticsService()

# Check if PageRank should be gated
should_gate = analytics.should_gate_pagerank(graph, available_memory_gb=8.0)

# Run PageRank with automatic strategy selection
result = analytics.run_pagerank(graph)
print(f"Method: {result['method']}")
print(f"Nodes processed: {result['nodes_processed']}")
```

**Core Components**:

#### Safety Gate Analysis
```python
def should_gate_pagerank(self, graph: nx.DiGraph, available_memory_gb: float = None) -> bool:
    """Determines if PageRank should use approximate method"""
```

**Gate Criteria**:
- **Size Check**: Gate if > 50,000 nodes
- **Memory Projection**: Gate if projected memory > 50% available
- **Graph Diameter**: Gate if diameter > 15 (slow convergence)
- **Edge Weight Skew**: Gate if skew > 2.0 (convergence issues)
- **Connectivity**: Gate if graph not strongly connected

#### PageRank Strategies
```python
def run_pagerank(self, graph: nx.DiGraph) -> dict:
    """Runs PageRank with appropriate strategy based on gating checks"""
```

**Strategies**:
- **Full PageRank**: Standard NetworkX PageRank for small graphs
- **Approximate PageRank**: Limited iterations with top-K results for large graphs

### IdentityService (`identity_service.py`)
**Purpose**: Real entity identity management using Neo4j database

**Key Features**:
- **No Mocks**: Production-ready service with real Neo4j operations
- **Entity Management**: Create, resolve, and manage entity identities
- **Mention Tracking**: Track entity mentions across documents
- **Neo4j Integration**: Direct Neo4j driver integration for persistence

**Usage**:
```python
from src.services.identity_service import IdentityService

# Requires Neo4j driver
identity_service = IdentityService(neo4j_driver)

# Create entity mention
mention_id = identity_service.create_mention(
    surface_form="John Smith",
    start_pos=0,
    end_pos=10,
    source_ref="document_1"
)
```

### ProvenanceService (`provenance_service.py`)
**Purpose**: Real operation tracking and lineage using SQLite database

**Key Features**:
- **No Mocks**: Production-ready service with real SQLite operations
- **Operation Tracking**: Track all pipeline operations and their results
- **Lineage Management**: Maintain complete data lineage
- **SQLite Integration**: Lightweight database for provenance data
- **JSON Storage**: Store complex operation metadata as JSON

**Usage**:
```python
from src.services.provenance_service import ProvenanceService

provenance_service = ProvenanceService()

# Start operation tracking
operation_id = provenance_service.start_operation(
    tool_id="T01_PDF_LOADER",
    operation_type="document_processing",
    inputs=["document.pdf"],
    parameters={"page_limit": 10}
)

# Complete operation tracking
provenance_service.complete_operation(
    operation_id=operation_id,
    outputs={"extracted_text": "content..."},
    metadata={"pages_processed": 10}
)
```

### QualityService (`quality_service.py`)
**Purpose**: Confidence assessment and quality metrics for pipeline operations

**Key Features**:
- **Quality Assessment**: Evaluate quality of extracted data
- **Confidence Scoring**: Assign confidence scores to operations
- **Metrics Tracking**: Track quality metrics across pipeline stages
- **Real Implementation**: No mocks, production-ready service

### EnhancedEntityResolution (`enhanced_entity_resolution.py`)
**Purpose**: Production-ready LLM-powered entity resolution with >60% F1 score

**Key Features**:
- **LLM-Powered**: Uses structured LLM service for entity resolution
- **Production-Ready**: Designed for >60% F1 score performance
- **Structured Output**: Uses Pydantic schemas for reliable extraction
- **Async Processing**: Supports asynchronous entity resolution
- **Phase D.2 Implementation**: Advanced entity resolution capabilities

**Usage**:
```python
from src.services.enhanced_entity_resolution import EnhancedEntityResolution

resolver = EnhancedEntityResolution()

# Resolve entities with structured output
entities = await resolver.resolve_entities(
    text="John Smith works at Acme Corp",
    document_id="doc_1"
)
```

### CrossDocumentEntityResolver (`cross_document_entity_resolver.py`)
**Purpose**: Multi-document entity resolution and cross-reference management

**Key Features**:
- **Cross-Document Resolution**: Resolve entities across multiple documents
- **Entity Linking**: Link related entities across document boundaries
- **Advanced Resolution**: Sophisticated entity matching algorithms
- **Multi-Document Support**: Handle complex multi-document scenarios

#### Full PageRank Implementation
```python
def _run_full_pagerank(self, graph: nx.DiGraph, **kwargs) -> dict:
    """Runs the standard, full NetworkX PageRank"""
    scores = nx.pagerank(graph, **kwargs)
    return {
        "method": "full",
        "scores": scores,
        "nodes_processed": graph.number_of_nodes()
    }
```

**Features**:
- **Standard Algorithm**: Uses NetworkX PageRank implementation
- **Complete Results**: Returns scores for all nodes
- **Performance Tracking**: Tracks nodes processed

#### Approximate PageRank Implementation
```python
def _run_approximate_pagerank(self, graph: nx.DiGraph, top_k: int = 1000, **kwargs) -> dict:
    """Runs PageRank with limited iterations and returns only top K results"""
```

**Features**:
- **Limited Iterations**: Max 20 iterations for speed
- **Early Stopping**: Tolerance-based convergence
- **Top-K Results**: Returns only top 1000 results by default
- **Memory Efficient**: Reduces memory usage for large graphs

## Performance Optimization Patterns

### Memory Management
```python
# Memory projection heuristic
projected_memory_gb = (node_count / 1000) * 0.1
if projected_memory_gb > (available_memory_gb * 0.5):
    return True  # Gate the operation
```

**Memory Patterns**:
- **Projection**: Estimate memory usage based on graph size
- **Safety Margin**: Use 50% of available memory as threshold
- **Monitoring**: Use psutil to get actual available memory
- **Heuristics**: ~0.1 GB per 1000 nodes as rough estimate

### Graph Analysis
```python
# Graph diameter check
if node_count > 1000:
    try:
        diameter = nx.diameter(graph)
        if diameter > 15:  # Heuristic threshold
            return True
    except nx.NetworkXError:
        return True  # Graph not connected
```

**Analysis Patterns**:
- **Size Thresholds**: Only analyze graphs above certain sizes
- **Error Handling**: Handle NetworkX errors gracefully
- **Heuristic Thresholds**: Use empirical thresholds for decisions
- **Connectivity Checks**: Ensure graph is strongly connected

### Edge Weight Analysis
```python
# Edge-weight skew check
weights = [data.get('weight', 1.0) for _, _, data in graph.edges(data=True)]
if weights:
    weight_skew = skew(np.array(weights))
    if weight_skew > 2.0:  # Heuristic threshold
        return True
```

**Weight Analysis**:
- **Skew Calculation**: Use scipy.stats.skew for distribution analysis
- **Default Weights**: Use 1.0 as default weight for unweighted edges
- **High Skew Detection**: Identify graphs with convergence issues
- **Threshold-Based**: Use empirical threshold of 2.0

## Common Commands & Workflows

### Service Testing Commands
```bash
# Test analytics service
python -c "from src.services.analytics_service import AnalyticsService; import networkx as nx; print(AnalyticsService().should_gate_pagerank(nx.DiGraph()))"

# Test provenance service (SQLite-based)
python -c "from src.services.provenance_service import ProvenanceService; ps = ProvenanceService(); print('ProvenanceService initialized')"

# Test enhanced entity resolution
python -c "from src.services.enhanced_entity_resolution import EnhancedEntityResolution; print('EnhancedEntityResolution available')"

# Test quality service
python -c "from src.services.quality_service import QualityService; print('QualityService available')"
```

### Service Integration Commands
```bash
# Test provenance operation tracking
python -c "
from src.services.provenance_service import ProvenanceService
ps = ProvenanceService()
op_id = ps.start_operation('TEST_TOOL', 'test_op', ['input'], {})
print(f'Operation started: {op_id}')
"

# Test cross-document entity resolution
python -c "from src.services.cross_document_entity_resolver import CrossDocumentEntityResolver; print('CrossDocumentEntityResolver available')"
```

### Performance Testing Commands
```bash
# Test memory projection
python -c "from src.services.analytics_service import AnalyticsService; print(AnalyticsService().should_gate_pagerank(nx.DiGraph(), available_memory_gb=1.0))"

# Test graph diameter analysis
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.path_graph(2000, create_using=nx.DiGraph); print(AnalyticsService().should_gate_pagerank(g))"

# Test edge weight skew
python -c "import networkx as nx; from src.services.analytics_service import AnalyticsService; g = nx.DiGraph(); g.add_edge(0,1,weight=0.1); g.add_edge(1,2,weight=10.0); print(AnalyticsService().should_gate_pagerank(g))"
```

### Debugging Commands
```bash
# Check memory usage
python -c "import psutil; print(f'Available memory: {psutil.virtual_memory().available / (1024**3):.2f} GB')"

# Test graph connectivity
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2)]); print(f'Strongly connected: {nx.is_strongly_connected(g)}')"

# Test PageRank convergence
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2), (2,0)]); print(nx.pagerank(g, max_iter=20, tol=1e-4))"
```

## Code Style & Conventions

### Service Design Patterns
- **Single Responsibility**: Each service has one clear purpose
- **Performance First**: Optimize for speed and memory efficiency
- **Safety Gates**: Prevent resource exhaustion
- **Graceful Degradation**: Fallback to approximate methods

### Naming Conventions
- **Service Names**: Use `Service` suffix for service classes
- **Method Names**: Use descriptive names for analysis methods
- **Variable Names**: Use descriptive names for thresholds and parameters
- **Constants**: Use UPPER_CASE for magic numbers and thresholds

### Error Handling Patterns
- **Graceful Degradation**: Fallback to approximate methods
- **Exception Handling**: Handle NetworkX errors gracefully
- **Safety Checks**: Check resources before expensive operations
- **Validation**: Validate inputs before processing

### Logging Patterns
- **Performance Logging**: Log method selection and performance metrics
- **Resource Logging**: Log memory usage and projections
- **Graph Analysis Logging**: Log graph properties and analysis results
- **Error Logging**: Log errors with context and fallback decisions

## Integration Points

### Core Services Integration
- **Enhanced Service Manager**: Integration with production service manager
- **Pipeline Orchestrator**: Integration with workflow execution
- **Structured LLM Service**: Integration with LLM service infrastructure
- **Logging**: Integration with core logging configuration
- **Configuration**: Integration with core configuration system
- **Error Handling**: Integration with centralized error handling

### Database Integration
- **Neo4j**: Identity service uses Neo4j for entity management
- **SQLite**: Provenance service uses SQLite for operation tracking
- **Connection Management**: Integration with database connection pools
- **Performance Monitoring**: Database performance tracking integration

### LLM Integration
- **Structured LLM Service**: Enhanced entity resolution uses structured LLM calls
- **Async Processing**: Support for asynchronous LLM operations
- **Pydantic Schemas**: Structured output validation with Pydantic
- **Multi-Provider Support**: LLM client with provider fallback

### External Dependencies
- **NetworkX**: Graph processing and analysis (AnalyticsService)
- **NumPy**: Numerical computations and array operations
- **SciPy**: Statistical analysis including skew calculation
- **psutil**: System resource monitoring and memory management
- **Neo4j Driver**: Direct Neo4j database operations (IdentityService)
- **SQLite3**: Lightweight database operations (ProvenanceService)
- **Pydantic**: Data validation and structured output (EnhancedEntityResolution)
- **asyncio**: Asynchronous processing support

## Performance Considerations

### Memory Optimization
- **Memory Projection**: Estimate memory usage before operations
- **Top-K Results**: Return only top results for large graphs
- **Limited Iterations**: Use fewer iterations for approximate methods
- **Resource Monitoring**: Monitor available system resources

### Speed Optimization
- **Early Stopping**: Stop iterations when convergence is reached
- **Approximate Methods**: Use faster approximate algorithms
- **Size-Based Decisions**: Choose methods based on graph size
- **Caching**: Cache analysis results when possible

### Safety Optimization
- **Safety Gates**: Prevent resource exhaustion
- **Graceful Degradation**: Fallback to safer methods
- **Resource Limits**: Respect system resource limits
- **Error Recovery**: Recover gracefully from errors

## Testing Patterns

### Unit Testing
- **Service Isolation**: Test each service independently
- **Method Testing**: Test individual analysis methods
- **Threshold Testing**: Test safety gate thresholds
- **Performance Testing**: Test performance characteristics

### Integration Testing
- **Graph Integration**: Test with various graph types
- **Resource Integration**: Test with different resource levels
- **Algorithm Integration**: Test algorithm selection logic
- **Error Integration**: Test error handling and recovery

### Performance Testing
- **Large Graph Testing**: Test with large graphs
- **Memory Testing**: Test memory usage and projections
- **Speed Testing**: Test algorithm execution speed
- **Resource Testing**: Test resource consumption

## Troubleshooting

### Common Issues
1. **Memory Exhaustion**: Reduce graph size or use approximate methods
2. **Slow Convergence**: Check graph diameter and edge weight distribution
3. **NetworkX Errors**: Handle disconnected or invalid graphs
4. **Performance Issues**: Use appropriate algorithm for graph size

### Debug Commands
```bash
# Check graph properties
python -c "import networkx as nx; g = nx.DiGraph([(0,1), (1,2)]); print(f'Nodes: {g.number_of_nodes()}, Edges: {g.number_of_edges()}, Connected: {nx.is_strongly_connected(g)}')"

# Test memory projection
python -c "node_count = 50000; projected_memory = (node_count / 1000) * 0.1; print(f'Projected memory: {projected_memory:.2f} GB')"

# Test edge weight skew
python -c "import numpy as np; from scipy.stats import skew; weights = [0.1, 0.1, 10.0]; print(f'Skew: {skew(np.array(weights)):.2f}')"
```

## Service Architecture Patterns

### Production Service Patterns
All services in this module follow these established patterns:

#### Real Implementation Pattern
- **No Mocks**: All services use real database connections and operations
- **Production Ready**: Services are designed for production use
- **Error Handling**: Comprehensive error handling and recovery
- **Resource Management**: Proper resource cleanup and management

#### Database Integration Pattern
- **Database Specific**: Each service uses appropriate database technology
  - **Neo4j**: Complex graph operations (IdentityService)
  - **SQLite**: Lightweight operations (ProvenanceService)
- **Connection Management**: Proper connection lifecycle management
- **Transaction Support**: Database transaction support where needed

#### Async Processing Pattern
- **Async Support**: Services support asynchronous operations where beneficial
- **LLM Integration**: Async LLM calls for entity resolution
- **Performance**: Non-blocking operations for better performance
- **Scalability**: Designed for concurrent operation handling

### Service Quality Standards

#### Performance Standards
- **Memory Efficiency**: Services monitor and optimize memory usage
- **Speed Optimization**: Fast response times for common operations  
- **Resource Management**: Proper cleanup of system resources
- **Scalability**: Design for handling increasing load

#### Reliability Standards
- **Error Recovery**: Graceful handling of error conditions
- **Data Integrity**: Maintain data consistency across operations
- **Monitoring**: Built-in performance and health monitoring
- **Logging**: Comprehensive operation logging for debugging

#### Integration Standards
- **Service Manager**: Integration with enhanced service manager
- **Configuration**: Centralized configuration management
- **Orchestration**: Integration with pipeline orchestrator
- **Monitoring**: Integration with system health monitoring 