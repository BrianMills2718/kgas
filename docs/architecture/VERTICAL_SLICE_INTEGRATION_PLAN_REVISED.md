# Vertical Slice Integration Plan (Revised)

**Date**: 2025-08-28  
**Status**: Revised after architecture investigation  
**Key Change**: Tools wrap services, framework registers tools

## Architectural Clarification

### What Actually Exists
```
Framework → Tools → Services → Databases
         registers  use       access
```

### Correct Pattern
```python
# 1. Service provides functionality
class VectorService:
    def embed(self, text: str) -> np.ndarray:
        # actual embedding logic

# 2. Tool wraps service for framework
class VectorEmbedder:
    def __init__(self, vector_service):
        self.service = vector_service
    
    def process(self, data: str) -> Dict:
        embedding = self.service.embed(data)
        return {'success': True, 'embedding': embedding, 'uncertainty': 0.15}

# 3. Framework registers tool
vector_service = VectorService()
tool = VectorEmbedder(vector_service)
capabilities = ToolCapabilities(
    tool_id="VectorEmbedder",
    input_type=DataType.TEXT,
    output_type=DataType.VECTOR
)
framework.register_tool(tool, capabilities)
```

## Phase 1: Wire Existing Services via Tools (Day 1)

### Current State
- TextLoaderV3, KnowledgeGraphExtractor, GraphPersisterV2 already follow this pattern
- Services exist but aren't fully connected through tools

### 1.1 Create ProvenanceTool to Wrap ProvenanceEnhanced

```python
# /tool_compatability/poc/vertical_slice/tools/provenance_tool.py
class ProvenanceTool:
    def __init__(self, provenance_service, sqlite_path="vertical_slice.db"):
        self.provenance = provenance_service or ProvenanceEnhanced(sqlite_path)
    
    def process(self, data: Dict) -> Dict:
        """Pass-through tool that tracks operations"""
        self.provenance.track_operation(
            tool_id=data.get('tool_id', 'unknown'),
            operation=data.get('operation', 'process'),
            inputs=data.get('inputs', {}),
            outputs=data.get('outputs', {}),
            uncertainty=data.get('uncertainty', 0.0),
            reasoning=data.get('reasoning', ''),
            construct_mapping=data.get('construct_mapping', '')
        )
        return data  # Pass through unchanged
```

### 1.2 Update GraphPersisterV2 to Use Services

```python
# GraphPersisterV2 already has this pattern:
def __init__(self, neo4j_driver, identity_service, crossmodal_service):
    self.neo4j = neo4j_driver
    self.identity = identity_service  # Already injected!
    self.crossmodal = crossmodal_service
```

### 1.3 Test Integration Script

```python
# /tool_compatability/poc/vertical_slice/test_integrated_services.py
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from services.identity_service_v3 import IdentityServiceV3
from services.provenance_enhanced import ProvenanceEnhanced
from services.crossmodal_service import CrossModalService
from tools.provenance_tool import ProvenanceTool

# Initialize services
neo4j_driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
identity = IdentityServiceV3(neo4j_driver)
provenance = ProvenanceEnhanced('vertical_slice.db')
crossmodal = CrossModalService(neo4j_driver, 'vertical_slice.db')

# Create framework
framework = CleanToolFramework(neo4j_driver)

# Register existing tools WITH services
from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
from tools.graph_persister_v2 import GraphPersisterV2

# GraphPersisterV2 with services injected
persister = GraphPersisterV2(neo4j_driver, identity, crossmodal)
framework.register_tool(persister, ToolCapabilities(
    tool_id="GraphPersisterV2",
    input_type=DataType.KNOWLEDGE_GRAPH,
    output_type=DataType.NEO4J_GRAPH
))

# Add provenance tracking tool
provenance_tool = ProvenanceTool(provenance)
framework.register_tool(provenance_tool, ToolCapabilities(
    tool_id="ProvenanceTool",
    input_type=DataType.ANY,  # Pass-through
    output_type=DataType.ANY
))
```

## Phase 2: Create Service+Tool Pairs (Days 2-3)

### 2.1 VectorService + VectorEmbedder Tool

```python
# /tool_compatability/poc/vertical_slice/services/vector_service.py
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorService:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        return self.model.encode(texts)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# /tool_compatability/poc/vertical_slice/tools/vector_embedder.py
class VectorEmbedder:
    def __init__(self, vector_service):
        self.service = vector_service
    
    def process(self, text: str) -> Dict:
        embedding = self.service.embed_text(text)
        return {
            'success': True,
            'embedding': embedding.tolist(),
            'dimension': len(embedding),
            'uncertainty': 0.05  # Low uncertainty for embeddings
        }
```

### 2.2 TableService + TablePersister Tool

```python
# /tool_compatability/poc/vertical_slice/services/table_service.py
import sqlite3
import pandas as pd

class TableService:
    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str):
        conn = sqlite3.connect(self.sqlite_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
    
    def query(self, sql: str) -> pd.DataFrame:
        conn = sqlite3.connect(self.sqlite_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df

# /tool_compatability/poc/vertical_slice/tools/table_persister.py
class TablePersister:
    def __init__(self, table_service):
        self.service = table_service
    
    def process(self, data: Dict) -> Dict:
        df = pd.DataFrame(data['records'])
        table_name = data.get('table_name', 'default_table')
        self.service.save_dataframe(df, table_name)
        return {
            'success': True,
            'table_name': table_name,
            'rows': len(df),
            'columns': list(df.columns),
            'uncertainty': 0.0  # No uncertainty in storage
        }
```

### 2.3 Update CrossModalService + Create CrossModalConverter Tool

```python
# /tool_compatability/poc/vertical_slice/tools/crossmodal_converter.py
class CrossModalConverter:
    def __init__(self, crossmodal_service):
        self.service = crossmodal_service
    
    def process(self, data: Dict) -> Dict:
        mode = data.get('mode', 'graph_to_table')
        
        if mode == 'graph_to_table':
            entity_ids = data.get('entity_ids', [])
            df = self.service.graph_to_table(entity_ids)
            return {
                'success': True,
                'dataframe': df.to_dict('records'),
                'rows': len(df),
                'uncertainty': 0.1
            }
        elif mode == 'table_to_graph':
            table_name = data['table_name']
            graph = self.service.table_to_graph(table_name)
            return {
                'success': True,
                'graph': graph,
                'nodes': len(graph['nodes']),
                'edges': len(graph['edges']),
                'uncertainty': 0.1
            }
```

## Phase 3: Tool Registration and Chaining (Day 4)

### 3.1 Complete Tool Registration

```python
# /tool_compatability/poc/vertical_slice/register_all_tools.py
def register_all_tools(framework):
    """Register all tools with proper DataType mappings"""
    
    # Define DataTypes if not exist
    DataType.VECTOR = "vector"
    DataType.TABLE = "table"
    
    # Text → Vector
    framework.register_tool(
        VectorEmbedder(vector_service),
        ToolCapabilities(
            tool_id="VectorEmbedder",
            input_type=DataType.TEXT,
            output_type=DataType.VECTOR
        )
    )
    
    # Graph → Table
    framework.register_tool(
        CrossModalConverter(crossmodal_service),
        ToolCapabilities(
            tool_id="CrossModalConverter",
            input_type=DataType.NEO4J_GRAPH,
            output_type=DataType.TABLE
        )
    )
    
    # Table → Storage
    framework.register_tool(
        TablePersister(table_service),
        ToolCapabilities(
            tool_id="TablePersister",
            input_type=DataType.TABLE,
            output_type=DataType.TABLE  # Stored table
        )
    )
```

### 3.2 Test Tool Chains

```python
# Test automatic chain discovery
chain = framework.find_chain(DataType.FILE, DataType.VECTOR)
# Should return: ['TextLoaderV3', 'VectorEmbedder']

chain = framework.find_chain(DataType.FILE, DataType.TABLE)
# Should return: ['TextLoaderV3', 'KnowledgeGraphExtractor', 'GraphPersisterV2', 'CrossModalConverter']
```

## Phase 4: Add Analysis Tools (Days 5-6)

### 4.1 Graph Analysis Tools

```python
# /tool_compatability/poc/vertical_slice/tools/graph_analyzer.py
import networkx as nx

class GraphAnalyzer:
    def __init__(self, neo4j_driver):
        self.neo4j = neo4j_driver
    
    def process(self, data: Dict) -> Dict:
        # Get graph from Neo4j
        with self.neo4j.session() as session:
            result = session.run("""
                MATCH (n:VSEntity)-[r]-(m:VSEntity)
                RETURN n.entity_id as source, m.entity_id as target, type(r) as rel_type
            """)
            
            # Build NetworkX graph
            G = nx.Graph()
            for record in result:
                G.add_edge(record['source'], record['target'])
            
            # Compute metrics
            metrics = {
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'components': nx.number_connected_components(G),
                'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
            }
            
            return {
                'success': True,
                'metrics': metrics,
                'uncertainty': 0.05
            }
```

### 4.2 Statistical Analysis Tool

```python
# /tool_compatability/poc/vertical_slice/tools/statistical_analyzer.py
class StatisticalAnalyzer:
    def __init__(self, table_service):
        self.table_service = table_service
    
    def process(self, data: Dict) -> Dict:
        table_name = data['table_name']
        df = self.table_service.query(f"SELECT * FROM {table_name}")
        
        # Compute statistics
        stats = {
            'shape': df.shape,
            'columns': list(df.columns),
            'numeric_summary': df.describe().to_dict() if not df.empty else {},
            'correlations': df.corr().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 1 else {}
        }
        
        return {
            'success': True,
            'statistics': stats,
            'uncertainty': 0.0
        }
```

## Phase 5: Integration Testing (Days 7-8)

### 5.1 End-to-End Test Scenarios

```python
# /tool_compatability/poc/vertical_slice/test_e2e_workflows.py

def test_document_to_statistics():
    """Document → Text → Graph → Table → Statistics"""
    
    # Execute chain
    result = framework.execute_chain(
        chain=['TextLoaderV3', 'KnowledgeGraphExtractor', 'GraphPersisterV2', 
               'CrossModalConverter', 'TablePersister', 'StatisticalAnalyzer'],
        input_data='test_document.txt'
    )
    
    assert result.success
    assert 'statistics' in result.final_output

def test_similarity_search():
    """Text → Embedding → Find Similar"""
    
    # Embed query
    result = framework.execute_chain(
        chain=['VectorEmbedder'],
        input_data="Find similar documents about machine learning"
    )
    
    query_embedding = result.final_output['embedding']
    
    # Search in vector store (Neo4j or separate index)
    # ... similarity search logic

def test_graph_analysis_pipeline():
    """Graph → Analysis → Table → Visualization"""
    
    result = framework.execute_chain(
        chain=['GraphAnalyzer', 'CrossModalConverter', 'TablePersister'],
        input_data={'graph_id': 'test_graph'}
    )
    
    assert result.success
    assert 'metrics' in result.intermediate_results[0]
```

### 5.2 Performance Benchmarks

```python
def benchmark_pipeline():
    import time
    
    times = {}
    
    # Benchmark each tool
    for tool_id in framework.tools.keys():
        start = time.time()
        # Run tool with sample data
        times[tool_id] = time.time() - start
    
    print(f"Tool Performance:")
    for tool, duration in times.items():
        print(f"  {tool}: {duration:.3f}s")
```

## Key Differences from Original Plan

1. **Tools wrap services** - Not services directly in framework
2. **Manual service injection** - Pass services to tool constructors
3. **Standard process() interface** - All tools have same method signature
4. **DataType extension** - Add VECTOR, TABLE types to enum
5. **Chain discovery works** - Framework's BFS finds tool chains automatically

## Success Criteria

### Phase 1: ✓ Services connected via tools
### Phase 2: ✓ New service+tool pairs created  
### Phase 3: ✓ All tools registered and chaining
### Phase 4: ✓ Analysis tools operational
### Phase 5: ✓ E2E workflows tested

## Next Steps

1. Implement ProvenanceTool wrapper
2. Create VectorService + VectorEmbedder
3. Test tool chain discovery
4. Run integrated pipeline test

This revised plan aligns with the actual architecture where tools wrap services and the framework manages tool registration and chaining.