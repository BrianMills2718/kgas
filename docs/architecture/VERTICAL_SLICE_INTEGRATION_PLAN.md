# Vertical Slice Integration Plan

**Date**: 2025-08-28
**Objective**: Complete service integration and tool expansion for working vertical slice
**Timeline**: 7-10 days

## Current State Assessment

### What's Working
- **Tools**: TextLoaderV3, KnowledgeGraphExtractor, GraphPersisterV2
- **Pipeline**: Document → Text → Graph → Neo4j (F1=0.41)
- **Services**: Partially integrated (3 exist, only 1 connected)

### Critical Gaps
1. **Vector Operations**: No embeddings or similarity search
2. **Table Persistence**: CrossModal exports but doesn't save
3. **Service Coordination**: Services work in isolation
4. **Tool Coverage**: Only 3 tools, need 8-10 for full demo

## Phase 1: Complete Core Service Integration (Days 1-2)

### Day 1: Wire Existing Services

#### 1.1 Connect ProvenanceEnhanced to Pipeline
**Location**: `/tool_compatability/poc/vertical_slice/framework/clean_framework.py`
```python
# Add to __init__
self.provenance = ProvenanceEnhanced(sqlite_path)

# Add to execute_chain
self.provenance.track_operation(
    tool_id=tool_id,
    operation=tool.transformation_type,
    inputs=current_data,
    outputs=result,
    uncertainty=result.get('uncertainty', 0.0),
    reasoning=result.get('reasoning', ''),
    construct_mapping=f"{tool.input_construct} → {tool.output_construct}"
)
```

#### 1.2 Wire IdentityService for Deduplication
**Location**: `GraphPersisterV2`
```python
# Add entity resolution before persisting
similar = self.identity_service.find_similar_entities(entity['name'])
if similar and similar[0]['similarity'] > 0.85:
    # Merge with existing entity
    entity['id'] = similar[0]['id']
```

#### 1.3 Test Full Pipeline Integration
```bash
cd /tool_compatability/poc/vertical_slice
python3 test_integrated_pipeline.py
```

### Day 2: Verify CrossModal Bidirectional

#### 2.1 Test Graph→Table Export
```python
# Export graph to SQLite tables
df = crossmodal.graph_to_table(entity_ids)
# Verify vs_entity_metrics and vs_relationships tables created
```

#### 2.2 Implement Table→Graph Import
```python
def table_to_graph(self, table_name: str) -> Dict:
    """Import tabular data back to graph"""
    # Read from SQLite
    # Create nodes and relationships
    # Return graph structure
```

## Phase 2: Add Missing Services (Days 3-5)

### Day 3: VectorService Implementation

#### 3.1 Design VectorService
```python
class VectorService:
    """Embeddings and similarity operations"""
    
    def __init__(self, model='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = self._load_model(model)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Batch embedding for efficiency"""
        
    def find_similar(self, query_vector: np.ndarray, 
                    vectors: np.ndarray, k: int = 10) -> List[int]:
        """Find k most similar vectors"""
```

#### 3.2 Storage Strategy
- **Option A**: Neo4j native vectors (5.13+ supports vectors)
- **Option B**: Separate FAISS index
- **Decision**: Use Neo4j for simplicity, can migrate later

### Day 4: TablePersister Implementation

#### 4.1 Design TablePersister
```python
class TablePersister:
    """Persist and query tabular data"""
    
    def __init__(self, sqlite_path: str):
        self.conn = sqlite3.connect(sqlite_path)
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str):
        """Save DataFrame to SQLite"""
        
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL and return DataFrame"""
        
    def get_statistics(self, table: str, columns: List[str]) -> Dict:
        """Compute descriptive statistics"""
```

#### 4.2 Integration Points
- Connect to CrossModalService output
- Enable statistical analysis workflows
- Support correlation/regression operations

### Day 5: ServiceBridge Coordination Layer

#### 5.1 Design ServiceBridge
```python
class ServiceBridge:
    """Coordinate services for complex operations"""
    
    def __init__(self, identity, provenance, crossmodal, vector, table):
        self.services = {
            'identity': identity,
            'provenance': provenance,
            'crossmodal': crossmodal,
            'vector': vector,
            'table': table
        }
    
    def extract_and_analyze(self, document: str) -> Dict:
        """Full pipeline with all services"""
        # 1. Extract text and entities
        # 2. Generate embeddings
        # 3. Resolve identities
        # 4. Export to tables
        # 5. Compute statistics
        # 6. Track provenance
        return comprehensive_results
```

## Phase 3: Tool Expansion (Days 6-8)

### Day 6: Graph Analysis Tools

#### 6.1 GraphAnalyzer
```python
class GraphAnalyzer(ExtensibleTool):
    """Compute graph metrics and properties"""
    
    def process(self, graph_data: Dict) -> Dict:
        # Centrality measures
        # Community detection
        # Path analysis
        return metrics
```

#### 6.2 CommunityDetector
```python
class CommunityDetector(ExtensibleTool):
    """Detect communities in graph"""
    
    def process(self, graph_data: Dict) -> Dict:
        # Louvain algorithm
        # Return community assignments
```

### Day 7: Table Analysis Tools

#### 7.1 CSVProcessor
```python
class CSVProcessor(ExtensibleTool):
    """Load and process CSV files"""
    
    def process(self, file_path: str) -> pd.DataFrame:
        # Load CSV
        # Clean data
        # Return DataFrame
```

#### 7.2 TableJoiner
```python
class TableJoiner(ExtensibleTool):
    """Join multiple tables"""
    
    def process(self, tables: List[pd.DataFrame]) -> pd.DataFrame:
        # Smart join on common columns
        # Handle conflicts
        return joined_table
```

#### 7.3 StatisticalAnalyzer
```python
class StatisticalAnalyzer(ExtensibleTool):
    """Run statistical analyses"""
    
    def process(self, df: pd.DataFrame) -> Dict:
        # Correlations
        # Regression
        # ANOVA
        return statistics
```

### Day 8: Vector Analysis Tools

#### 8.1 EmbeddingGenerator
```python
class EmbeddingGenerator(ExtensibleTool):
    """Generate embeddings for various inputs"""
    
    def process(self, data: Any) -> np.ndarray:
        # Text, entities, or documents
        # Return embeddings
```

#### 8.2 SimilaritySearch
```python
class SimilaritySearch(ExtensibleTool):
    """Find similar items by embeddings"""
    
    def process(self, query: str, corpus: List) -> List:
        # Embed query
        # Search corpus
        # Return ranked results
```

## Phase 4: Integration Testing (Days 9-10)

### Day 9: End-to-End Workflows

#### 9.1 Document Analysis Workflow
```
PDF → Text → Entities → Graph → Embeddings → Communities → Table → Statistics
```

#### 9.2 Cross-Modal Analysis Workflow
```
Graph → Table → Regression → Results → Graph Visualization
```

#### 9.3 Similarity Search Workflow
```
Query → Embedding → Vector Search → Similar Documents → Extract Entities
```

### Day 10: Performance and Documentation

#### 10.1 Performance Testing
- Measure throughput for each tool
- Identify bottlenecks
- Optimize critical paths

#### 10.2 Documentation
- Update CLAUDE.md with integrated services
- Create workflow examples
- Document API interfaces

## Success Criteria

### Phase 1 Success
- [ ] All 3 services connected to pipeline
- [ ] Provenance tracks every operation
- [ ] Identity resolution reduces duplicates by 30%
- [ ] CrossModal bidirectional conversion works

### Phase 2 Success
- [ ] VectorService generates embeddings
- [ ] TablePersister saves/queries data
- [ ] ServiceBridge coordinates all services
- [ ] Can do graph→table→vector workflows

### Phase 3 Success
- [ ] 8-10 tools operational
- [ ] Each modality has 2+ tools
- [ ] Tools chain automatically
- [ ] Complex workflows execute successfully

### Phase 4 Success
- [ ] 3+ end-to-end workflows tested
- [ ] Performance benchmarks documented
- [ ] All interfaces documented
- [ ] Demo-ready system

## Risk Mitigation

### Technical Risks
1. **Neo4j vector performance**: Have FAISS fallback ready
2. **Service coupling**: Keep services loosely coupled
3. **Tool chain complexity**: Start with simple chains

### Timeline Risks
1. **Scope creep**: Stick to MVP features
2. **Integration issues**: Test incrementally
3. **Performance problems**: Profile early and often

## Dependencies

### Required Libraries
```bash
pip install sentence-transformers  # For embeddings
pip install faiss-cpu            # Backup vector search
pip install networkx              # Graph algorithms
pip install scikit-learn         # Statistical analysis
```

### Infrastructure
- Neo4j 5.13+ (for vector support)
- SQLite (already in use)
- 8GB RAM minimum (for embeddings)

## Next Steps

1. **Immediate**: Start Phase 1 - Wire existing services
2. **Tomorrow**: Test integrated pipeline
3. **This Week**: Complete Phase 2 services
4. **Next Week**: Expand tool set and test workflows

## Conclusion

This plan provides a clear path from our current partial integration to a fully functional vertical slice with:
- All services integrated and coordinating
- Graph, table, and vector operations
- 8-10 tools covering all modalities
- End-to-end workflows demonstrated

The phased approach ensures we maintain working code at each step while building toward the complete vision.