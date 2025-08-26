# Uncertainty Propagation and Provenance in Type-Based Tool Composition

## Executive Summary

Our type-based framework can seamlessly integrate with KGAS's uncertainty propagation and provenance systems while providing additional capabilities for tracking data lineage through composed tool chains.

## Current KGAS Capabilities

### Provenance System (Partially Implemented)
From our architecture review, KGAS has:
- **ProvenancePersistence** (`/src/core/provenance_persistence.py`) - SQLite storage for tracking
- **ProvenanceService** - Tracks operation history
- **BaseObject.provenance** field in data models
- Operation tracking tables in SQLite

### Uncertainty/Quality System (Partially Implemented)
KGAS includes:
- **QualityService** - Confidence scoring system
- **BaseObject.quality** field with confidence scores
- **Quality tracking** in SQLite schema
- **Theory-aware confidence** propagation (planned)

## How Our Framework Handles These Concerns

### 1. Provenance Through Tool Chains

```python
@dataclass
class ToolContext:
    """Context propagated through tool chains"""
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_execution_id: Optional[str] = None
    chain_position: int = 0
    tool_chain: List[str] = Field(default_factory=list)
    
    # Provenance tracking
    provenance: Dict[str, Any] = Field(default_factory=dict)
    input_checksums: List[str] = Field(default_factory=list)
    output_checksums: List[str] = Field(default_factory=list)
    
    # Uncertainty propagation
    confidence_scores: List[float] = Field(default_factory=list)
    uncertainty_factors: Dict[str, float] = Field(default_factory=dict)
    
    # Timing and performance
    start_time: datetime = Field(default_factory=datetime.now)
    tool_timings: Dict[str, float] = Field(default_factory=dict)

class ExtensibleTool(ABC):
    """Enhanced base tool with provenance and uncertainty"""
    
    def process(self, input_data: Any, context: Optional[ToolContext] = None) -> ToolResult:
        """Process with automatic provenance tracking"""
        if context is None:
            context = ToolContext()
        
        # Record input provenance
        context.input_checksums.append(self._checksum(input_data))
        context.tool_chain.append(self.get_capabilities().tool_id)
        
        # Execute tool
        start = time.perf_counter()
        result = self._execute(input_data, context)
        duration = time.perf_counter() - start
        
        # Record output provenance
        context.output_checksums.append(self._checksum(result.data))
        context.tool_timings[self.get_capabilities().tool_id] = duration
        
        # Propagate uncertainty
        if hasattr(result, 'confidence'):
            context.confidence_scores.append(result.confidence)
            
        # Update provenance
        context.provenance[self.get_capabilities().tool_id] = {
            'input_checksum': context.input_checksums[-1],
            'output_checksum': context.output_checksums[-1],
            'execution_time': duration,
            'timestamp': datetime.now().isoformat(),
            'confidence': getattr(result, 'confidence', 1.0)
        }
        
        return result
```

### 2. Uncertainty Propagation Models

```python
class UncertaintyPropagator:
    """Propagate uncertainty through tool chains"""
    
    @staticmethod
    def multiplicative(confidences: List[float]) -> float:
        """Multiply confidence scores (assumes independence)"""
        return reduce(lambda x, y: x * y, confidences, 1.0)
    
    @staticmethod
    def minimum(confidences: List[float]) -> float:
        """Chain is as strong as weakest link"""
        return min(confidences) if confidences else 0.0
    
    @staticmethod
    def weighted_average(confidences: List[float], weights: Optional[List[float]] = None) -> float:
        """Weighted average based on tool importance"""
        if not confidences:
            return 0.0
        if weights is None:
            weights = [1.0] * len(confidences)
        return sum(c * w for c, w in zip(confidences, weights)) / sum(weights)
    
    @staticmethod
    def bayesian(prior: float, likelihoods: List[float]) -> float:
        """Bayesian uncertainty propagation"""
        posterior = prior
        for likelihood in likelihoods:
            # Bayes' rule update
            posterior = (likelihood * posterior) / (
                likelihood * posterior + (1 - likelihood) * (1 - posterior)
            )
        return posterior

class ToolFramework:
    """Framework with uncertainty and provenance support"""
    
    def __init__(self, 
                 provenance_service: Optional[Any] = None,
                 quality_service: Optional[Any] = None):
        self.provenance_service = provenance_service  # KGAS ProvenanceService
        self.quality_service = quality_service  # KGAS QualityService
        self.uncertainty_model = UncertaintyPropagator.multiplicative  # Default
    
    def execute_chain_with_tracking(self, 
                                   chain: List[str], 
                                   input_data: Any,
                                   track_provenance: bool = True,
                                   propagate_uncertainty: bool = True) -> TrackedResult:
        """Execute chain with full tracking"""
        
        context = ToolContext()
        current_data = input_data
        
        for tool_id in chain:
            tool = self.tools[tool_id]
            result = tool.process(current_data, context)
            
            if not result.success:
                # Record failure in provenance
                if self.provenance_service:
                    self.provenance_service.record_failure(
                        tool_id=tool_id,
                        error=result.error,
                        context=context
                    )
                return TrackedResult(
                    success=False,
                    data=None,
                    error=result.error,
                    provenance=context.provenance,
                    confidence=0.0
                )
            
            current_data = result.data
            
            # Track in KGAS services if available
            if track_provenance and self.provenance_service:
                self.provenance_service.record_operation(
                    operation_type=f"tool_{tool_id}",
                    input_data=context.input_checksums[-1],
                    output_data=context.output_checksums[-1],
                    metadata=context.provenance[tool_id]
                )
        
        # Calculate final confidence
        final_confidence = 1.0
        if propagate_uncertainty and context.confidence_scores:
            final_confidence = self.uncertainty_model(context.confidence_scores)
            
            if self.quality_service:
                self.quality_service.record_confidence(
                    entity_id=context.execution_id,
                    confidence=final_confidence,
                    factors=context.uncertainty_factors
                )
        
        return TrackedResult(
            success=True,
            data=current_data,
            provenance=context.provenance,
            confidence=final_confidence,
            execution_id=context.execution_id,
            tool_chain=context.tool_chain,
            total_time=sum(context.tool_timings.values())
        )
```

### 3. Integration with KGAS Services

```python
class KGASIntegratedFramework(ToolFramework):
    """Framework integrated with KGAS provenance and quality services"""
    
    def __init__(self):
        # Import KGAS services if available
        try:
            from src.core.provenance_service import ProvenanceService
            from src.core.quality_service import QualityService
            
            super().__init__(
                provenance_service=ProvenanceService(),
                quality_service=QualityService()
            )
        except ImportError:
            # Work without KGAS services
            super().__init__()
    
    def get_lineage(self, execution_id: str) -> Dict[str, Any]:
        """Get complete lineage for an execution"""
        if self.provenance_service:
            return self.provenance_service.get_lineage(execution_id)
        return {}
    
    def get_confidence_breakdown(self, execution_id: str) -> Dict[str, float]:
        """Get confidence scores for each step"""
        if self.quality_service:
            return self.quality_service.get_confidence_breakdown(execution_id)
        return {}
```

### 4. Data Lineage Visualization

```python
class LineageVisualizer:
    """Visualize data lineage through tool chains"""
    
    @staticmethod
    def generate_lineage_graph(provenance: Dict[str, Any]) -> nx.DiGraph:
        """Create NetworkX graph of data lineage"""
        G = nx.DiGraph()
        
        for tool_id, prov_data in provenance.items():
            # Add tool node
            G.add_node(tool_id, 
                      type='tool',
                      confidence=prov_data.get('confidence', 1.0),
                      execution_time=prov_data.get('execution_time', 0))
            
            # Add data nodes
            input_node = f"input_{prov_data['input_checksum'][:8]}"
            output_node = f"output_{prov_data['output_checksum'][:8]}"
            
            G.add_node(input_node, type='data')
            G.add_node(output_node, type='data')
            
            # Add edges
            G.add_edge(input_node, tool_id)
            G.add_edge(tool_id, output_node)
        
        return G
    
    @staticmethod
    def export_provenance_json(provenance: Dict[str, Any], 
                               confidence: float,
                               execution_id: str) -> str:
        """Export provenance as W3C PROV-JSON format"""
        prov_doc = {
            "prefix": {
                "kgas": "https://kgas.org/prov/",
                "tool": "https://kgas.org/tool/"
            },
            "entity": {},
            "activity": {},
            "wasGeneratedBy": {},
            "used": {},
            "wasAssociatedWith": {}
        }
        
        for tool_id, prov_data in provenance.items():
            activity_id = f"activity:{execution_id}:{tool_id}"
            
            # Add activity (tool execution)
            prov_doc["activity"][activity_id] = {
                "kgas:tool": tool_id,
                "kgas:confidence": prov_data.get('confidence', 1.0),
                "kgas:startTime": prov_data.get('timestamp'),
                "kgas:duration": prov_data.get('execution_time')
            }
            
            # Add entities (data)
            input_id = f"entity:input:{prov_data['input_checksum']}"
            output_id = f"entity:output:{prov_data['output_checksum']}"
            
            prov_doc["entity"][input_id] = {"kgas:checksum": prov_data['input_checksum']}
            prov_doc["entity"][output_id] = {"kgas:checksum": prov_data['output_checksum']}
            
            # Add relationships
            prov_doc["used"][f"used:{activity_id}:1"] = {
                "activity": activity_id,
                "entity": input_id
            }
            
            prov_doc["wasGeneratedBy"][f"gen:{output_id}:1"] = {
                "entity": output_id,
                "activity": activity_id
            }
        
        return json.dumps(prov_doc, indent=2)
```

### 5. Theory-Aware Uncertainty (Future Integration)

```python
class TheoryAwareUncertainty:
    """Integrate with KGAS's theory-aware components"""
    
    def __init__(self, theory_service: Optional[Any] = None):
        self.theory_service = theory_service  # KGAS TheoryService when available
    
    def calculate_theory_confidence(self, 
                                   tool_chain: List[str],
                                   domain: str) -> float:
        """Calculate confidence based on theoretical soundness"""
        if not self.theory_service:
            return 1.0  # Default confidence without theory service
        
        # Get theory alignments for each tool
        theory_scores = []
        for tool_id in tool_chain:
            alignment = self.theory_service.get_theory_alignment(
                tool_id=tool_id,
                domain=domain
            )
            theory_scores.append(alignment.confidence)
        
        # Combine theory-based confidence scores
        return UncertaintyPropagator.weighted_average(
            theory_scores,
            weights=[1.0] * len(theory_scores)  # Could weight by importance
        )
```

## Benefits of Our Approach

### 1. **Automatic Provenance Tracking**
- Every tool execution automatically tracked
- No manual instrumentation needed
- Complete lineage through chains

### 2. **Flexible Uncertainty Models**
- Multiple propagation strategies
- Pluggable uncertainty models
- Domain-specific confidence calculation

### 3. **KGAS Service Integration**
- Works with or without KGAS services
- Enhances existing provenance/quality systems
- Provides missing chain-level tracking

### 4. **Standards Compliance**
- W3C PROV-JSON export
- Compatible with provenance standards
- Interoperable with external systems

### 5. **Performance Tracking**
- Execution time per tool
- Memory usage tracking
- Performance regression detection

## Implementation Status

### What We Have Now
- ✅ Basic ToolContext for propagation
- ✅ Checksum-based data tracking
- ✅ Execution timing metrics
- ✅ Framework structure for integration

### What We Need to Add
- ⏳ Full uncertainty propagation models
- ⏳ KGAS service connectors
- ⏳ Lineage visualization
- ⏳ W3C PROV export
- ⏳ Theory-aware confidence

## Integration Example

```python
# Using our framework with KGAS services
framework = KGASIntegratedFramework()

# Register tools
framework.register_tool(TextLoader())
framework.register_tool(EntityExtractor())
framework.register_tool(GraphBuilder())

# Execute with full tracking
result = framework.execute_chain_with_tracking(
    chain=["TextLoader", "EntityExtractor", "GraphBuilder"],
    input_data=file_data,
    track_provenance=True,
    propagate_uncertainty=True
)

# Access tracking information
print(f"Execution ID: {result.execution_id}")
print(f"Final confidence: {result.confidence:.2%}")
print(f"Total time: {result.total_time:.3f}s")

# Get detailed lineage from KGAS
lineage = framework.get_lineage(result.execution_id)
confidence_breakdown = framework.get_confidence_breakdown(result.execution_id)

# Export for external analysis
prov_json = LineageVisualizer.export_provenance_json(
    result.provenance,
    result.confidence,
    result.execution_id
)
```

## Conclusion

Our type-based framework naturally supports uncertainty propagation and provenance tracking through:

1. **Context propagation** through tool chains
2. **Automatic tracking** without manual instrumentation  
3. **Flexible integration** with KGAS services when available
4. **Standards compliance** for interoperability
5. **Performance awareness** built into the framework

This enhances KGAS's existing capabilities by providing the missing chain-level tracking and making provenance/uncertainty first-class concerns in tool composition.