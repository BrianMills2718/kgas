# Service and Tool Implementation Plan - FINAL

**Date**: 2025-08-28
**Status**: Ready for implementation
**Architecture**: Tools wrap Services, Framework registers Tools

## Architecture Alignment

### Pattern We're Following
```
Framework → Tools → Services → External APIs/DBs
         registers  wrap       access
```

### Key Architectural Decisions
1. **Tools are plain classes** with `process(data: Dict) -> Dict` method
2. **Services are injected** into tools at construction
3. **Framework uses BFS** to find tool chains automatically
4. **DataType enum** already has TABLE and VECTOR defined
5. **Uncertainty combines** using RSS (root sum of squares): √(Σu²)

## Service Specifications

### 1. VectorService
**Purpose**: Generate embeddings using OpenAI API
**Location**: `/tool_compatability/poc/vertical_slice/services/vector_service.py`

```python
import os
import openai
from typing import List, Dict
import numpy as np

class VectorService:
    """Generate embeddings using OpenAI text-embedding-3-small"""
    
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        response = openai.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding for efficiency"""
        response = openai.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
```

### 2. TableService
**Purpose**: Persist and query tabular data in SQLite
**Location**: `/tool_compatability/poc/vertical_slice/services/table_service.py`

```python
import sqlite3
import pandas as pd
from typing import Dict, List
import json

class TableService:
    """Manage tabular data in SQLite"""
    
    def __init__(self, sqlite_path: str = "vertical_slice.db"):
        self.sqlite_path = sqlite_path
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if not exist"""
        conn = sqlite3.connect(self.sqlite_path)
        # Use vs2_ prefix to avoid conflicts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vs2_stored_tables (
                table_name TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str, metadata: Dict = None):
        """Save DataFrame to SQLite with vs2_ prefix"""
        safe_name = f"vs2_{table_name}"
        conn = sqlite3.connect(self.sqlite_path)
        df.to_sql(safe_name, conn, if_exists='replace', index=False)
        
        # Track table
        conn.execute(
            "INSERT OR REPLACE INTO vs2_stored_tables (table_name, metadata) VALUES (?, ?)",
            (safe_name, json.dumps(metadata or {}))
        )
        conn.commit()
        conn.close()
        return safe_name
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL and return DataFrame"""
        conn = sqlite3.connect(self.sqlite_path)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    
    def get_table(self, table_name: str) -> pd.DataFrame:
        """Get table by name"""
        safe_name = f"vs2_{table_name}" if not table_name.startswith("vs2_") else table_name
        return self.query(f"SELECT * FROM {safe_name}")
```

## Tool Specifications

### 1. VectorEmbedder Tool
**Location**: `/tool_compatability/poc/vertical_slice/tools/vector_embedder.py`

```python
from typing import Dict, Any

class VectorEmbedder:
    """Tool wrapper for VectorService"""
    
    def __init__(self, vector_service):
        self.service = vector_service
        self.tool_id = "VectorEmbedder"
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: {"text": str, ...}
        Output: {"embedding": List[float], "dimension": int, "model": str, ...}
        """
        text = data.get('text', '')
        if not text:
            return {
                'success': False,
                'error': 'No text provided',
                'uncertainty': 1.0
            }
        
        try:
            embedding = self.service.embed_text(text)
            return {
                'success': True,
                'embedding': embedding,
                'dimension': len(embedding),
                'model': self.service.model,
                'uncertainty': 0.05,  # Low uncertainty for embeddings
                'reasoning': 'Embedding generated via API'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0
            }
```

### 2. TablePersister Tool
**Location**: `/tool_compatability/poc/vertical_slice/tools/table_persister.py`

```python
import pandas as pd
from typing import Dict, Any

class TablePersister:
    """Tool wrapper for TableService"""
    
    def __init__(self, table_service):
        self.service = table_service
        self.tool_id = "TablePersister"
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: {"dataframe": dict or DataFrame, "table_name": str, ...}
        Output: {"table_name": str, "rows": int, "columns": List[str], ...}
        """
        # Handle different input formats
        if 'dataframe' in data:
            df_data = data['dataframe']
            if isinstance(df_data, pd.DataFrame):
                df = df_data
            elif isinstance(df_data, dict):
                df = pd.DataFrame(df_data)
            else:
                return {'success': False, 'error': 'Invalid dataframe format'}
        elif 'records' in data:
            df = pd.DataFrame(data['records'])
        else:
            return {'success': False, 'error': 'No data to persist'}
        
        table_name = data.get('table_name', 'default_table')
        metadata = data.get('metadata', {})
        
        try:
            safe_name = self.service.save_dataframe(df, table_name, metadata)
            return {
                'success': True,
                'table_name': safe_name,
                'rows': len(df),
                'columns': list(df.columns),
                'uncertainty': 0.0,  # No uncertainty in storage
                'reasoning': 'Data persisted to SQLite'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0
            }
```

### 3. CrossModalConverter Tool (Update)
**Location**: `/tool_compatability/poc/vertical_slice/tools/crossmodal_converter.py`

```python
class CrossModalConverter:
    """Enhanced wrapper for CrossModalService"""
    
    def __init__(self, crossmodal_service):
        self.service = crossmodal_service
        self.tool_id = "CrossModalConverter"
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modes:
        - graph_to_table: {"mode": "graph_to_table", "entity_ids": [...]}
        - table_to_graph: {"mode": "table_to_graph", "table_name": str}
        """
        mode = data.get('mode', 'graph_to_table')
        
        try:
            if mode == 'graph_to_table':
                entity_ids = data.get('entity_ids', [])
                df = self.service.graph_to_table(entity_ids)
                return {
                    'success': True,
                    'dataframe': df.to_dict('records'),
                    'rows': len(df),
                    'columns': list(df.columns),
                    'uncertainty': 0.1,
                    'reasoning': 'Graph structure mapped to tabular format'
                }
            
            elif mode == 'table_to_graph':
                table_name = data['table_name']
                graph = self.service.table_to_graph(table_name)
                return {
                    'success': True,
                    'entities': graph['entities'],
                    'relationships': graph['relationships'],
                    'uncertainty': 0.1,
                    'reasoning': 'Tabular data reconstructed as graph'
                }
            
            else:
                return {'success': False, 'error': f'Unknown mode: {mode}'}
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0
            }
```

## Tool Registration

**Location**: `/tool_compatability/poc/vertical_slice/register_services_and_tools.py`

```python
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

# Initialize services
from services.vector_service import VectorService
from services.table_service import TableService
from services.identity_service_v3 import IdentityServiceV3
from services.provenance_enhanced import ProvenanceEnhanced
from services.crossmodal_service import CrossModalService

# Initialize tools
from tools.vector_embedder import VectorEmbedder
from tools.table_persister import TablePersister
from tools.crossmodal_converter import CrossModalConverter

def register_all_tools():
    """Register all tools with framework"""
    
    # Initialize framework
    neo4j_driver = GraphDatabase.driver(
        'bolt://localhost:7687', 
        auth=('neo4j', 'devpassword')
    )
    framework = CleanToolFramework(neo4j_driver)
    
    # Initialize services
    vector_service = VectorService()
    table_service = TableService('vertical_slice.db')
    identity_service = IdentityServiceV3(neo4j_driver)
    provenance_service = ProvenanceEnhanced('vertical_slice.db')
    crossmodal_service = CrossModalService(neo4j_driver, 'vertical_slice.db')
    
    # Register existing tools (already working)
    from tools.text_loader_v3 import TextLoaderV3
    from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
    from tools.graph_persister_v2 import GraphPersisterV2
    
    framework.register_tool(
        TextLoaderV3(),
        ToolCapabilities(
            tool_id="TextLoaderV3",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="character_sequence",
            transformation_type="text_extraction"
        )
    )
    
    # ... register other existing tools ...
    
    # Register new tools
    framework.register_tool(
        VectorEmbedder(vector_service),
        ToolCapabilities(
            tool_id="VectorEmbedder",
            input_type=DataType.TEXT,
            output_type=DataType.VECTOR,
            input_construct="character_sequence",
            output_construct="embedding_vector",
            transformation_type="vectorization"
        )
    )
    
    framework.register_tool(
        TablePersister(table_service),
        ToolCapabilities(
            tool_id="TablePersister",
            input_type=DataType.TABLE,
            output_type=DataType.TABLE,
            input_construct="dataframe",
            output_construct="persisted_table",
            transformation_type="persistence"
        )
    )
    
    framework.register_tool(
        CrossModalConverter(crossmodal_service),
        ToolCapabilities(
            tool_id="CrossModalConverter",
            input_type=DataType.NEO4J_GRAPH,
            output_type=DataType.TABLE,
            input_construct="neo4j_graph",
            output_construct="dataframe",
            transformation_type="cross_modal_conversion"
        )
    )
    
    return framework
```

## Data Flow Specifications

### Text → Vector Flow
```
Input: {"text": "Some text to embed"}
↓ VectorEmbedder
Output: {"embedding": [0.1, 0.2, ...], "dimension": 1536, "model": "text-embedding-3-small"}
```

### Graph → Table → Storage Flow
```
Input: {"entity_ids": ["e1", "e2"]}
↓ CrossModalConverter (graph_to_table)
Output: {"dataframe": [...], "rows": 10, "columns": ["id", "name", ...]}
↓ TablePersister
Output: {"table_name": "vs2_entities", "rows": 10}
```

### Chain Discovery Examples
```python
# Framework automatically finds these chains:
framework.find_chain(DataType.TEXT, DataType.VECTOR)
# Returns: ['VectorEmbedder']

framework.find_chain(DataType.FILE, DataType.VECTOR)
# Returns: ['TextLoaderV3', 'VectorEmbedder']

framework.find_chain(DataType.NEO4J_GRAPH, DataType.TABLE)
# Returns: ['CrossModalConverter']
```

## Implementation Checklist

### Pre-Implementation
- [x] OpenAI API key in .env
- [x] EMBEDDING_MODEL set to text-embedding-3-small
- [x] DataType.VECTOR and DataType.TABLE already defined
- [x] Framework supports construct mapping
- [x] Git commit current state for rollback

### Implementation Order
1. [ ] Create `services/vector_service.py`
2. [ ] Create `services/table_service.py`  
3. [ ] Create `tools/vector_embedder.py`
4. [ ] Create `tools/table_persister.py`
5. [ ] Update `tools/crossmodal_converter.py`
6. [ ] Create `register_services_and_tools.py`
7. [ ] Test chain discovery
8. [ ] Test end-to-end workflows

### Validation Tests
```python
# Test 1: Vector embedding works
python3 -c "
from services.vector_service import VectorService
s = VectorService()
emb = s.embed_text('test')
assert len(emb) == 1536  # text-embedding-3-small dimension
print('✅ VectorService works')
"

# Test 2: Table persistence works
python3 -c "
import pandas as pd
from services.table_service import TableService
s = TableService()
df = pd.DataFrame({'a': [1,2], 'b': [3,4]})
s.save_dataframe(df, 'test')
result = s.get_table('test')
assert len(result) == 2
print('✅ TableService works')
"

# Test 3: Chain discovery works
python3 -c "
from register_services_and_tools import register_all_tools
framework = register_all_tools()
chain = framework.find_chain(DataType.TEXT, DataType.VECTOR)
assert 'VectorEmbedder' in chain
print('✅ Chain discovery works')
"

# Test 4: End-to-end pipeline
python3 -c "
from register_services_and_tools import register_all_tools
framework = register_all_tools()
result = framework.execute_chain(
    ['TextLoaderV3', 'VectorEmbedder'],
    'test_doc.txt'
)
assert result.success
assert 'embedding' in result.final_output
print('✅ End-to-end works')
"
```

## No Ambiguity Remaining

- **Exact file locations** specified
- **Exact code** for each component
- **Exact test commands** to validate
- **Service initialization order** defined
- **Error handling** returns success=False
- **Uncertainty values** specified (0.05 for vectors, 0.0 for storage, 0.1 for conversion)
- **Table naming** uses vs2_ prefix to avoid conflicts
- **Dependencies** only openai and pandas (both pip installable)

This plan is ready for implementation with zero ambiguity.