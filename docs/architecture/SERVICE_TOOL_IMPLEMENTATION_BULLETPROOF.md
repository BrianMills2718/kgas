# Bulletproof Service and Tool Implementation Guide

**For**: Anyone who can copy-paste commands
**Result**: Working vector and table operations in the pipeline
**Time**: 30 minutes

## Pre-flight Checklist

### Step 0.1: Check You're in the Right Directory
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
pwd
# Should output: /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
```

### Step 0.2: Check Neo4j is Running
```bash
python3 -c "
from neo4j import GraphDatabase
try:
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
    driver.verify_connectivity()
    print('✅ Neo4j is running')
except Exception as e:
    print('❌ Neo4j is NOT running. Start it first!')
    print('Run: neo4j start')
"
```

### Step 0.3: Install Required Libraries
```bash
# Install dependencies
pip install openai pandas numpy

# Verify installation
python3 -c "
import openai
import pandas
import numpy
print('✅ All dependencies installed')
"
```

### Step 0.4: Verify API Key
```bash
python3 -c "
import os
import sys
sys.path.append('/home/brian/projects/Digimons')
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-'):
    print(f'✅ OpenAI API key found: {api_key[:10]}...')
else:
    print('❌ OpenAI API key not found or invalid')
"
```

## Part 1: Create Services

### Step 1.1: Create VectorService

```bash
# Make sure we're in the right directory
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Create the service file
cat > services/vector_service.py << 'EOF'
import os
import sys
from typing import List
import numpy as np

# Add parent dirs to path
sys.path.append('/home/brian/projects/Digimons')
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

# Import OpenAI correctly for v1.x
from openai import OpenAI

class VectorService:
    """Generate embeddings using OpenAI text-embedding-3-small"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
        print(f"VectorService initialized with model: {self.model}")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Embedding error: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding for efficiency"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            raise
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between vectors"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
EOF

echo "✅ Created services/vector_service.py"
```

### Step 1.2: Test VectorService Works

```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
python3 -c "
from services.vector_service import VectorService
try:
    s = VectorService()
    emb = s.embed_text('test')
    print(f'✅ VectorService works! Embedding dimension: {len(emb)}')
except Exception as e:
    print(f'❌ VectorService failed: {e}')
"
```

**If this fails**, check:
1. Is your OpenAI API key valid? (not expired)
2. Do you have internet connection?
3. Is the API key set correctly in .env?

### Step 1.3: Create TableService

```bash
cat > services/table_service.py << 'EOF'
import sqlite3
import pandas as pd
from typing import Dict, List, Optional
import json
from datetime import datetime

class TableService:
    """Manage tabular data in SQLite"""
    
    def __init__(self, sqlite_path: str = "vertical_slice.db"):
        self.sqlite_path = sqlite_path
        self._init_schema()
        print(f"TableService initialized with database: {sqlite_path}")
    
    def _init_schema(self):
        """Create tables if not exist"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # Create metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vs2_stored_tables (
                table_name TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Schema initialized")
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str, metadata: Optional[Dict] = None) -> str:
        """Save DataFrame to SQLite with vs2_ prefix"""
        safe_name = f"vs2_{table_name}" if not table_name.startswith("vs2_") else table_name
        
        conn = sqlite3.connect(self.sqlite_path)
        
        # Save the dataframe
        df.to_sql(safe_name, conn, if_exists='replace', index=False)
        
        # Track in metadata table
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO vs2_stored_tables (table_name, metadata) VALUES (?, ?)",
            (safe_name, json.dumps(metadata or {}))
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved {len(df)} rows to {safe_name}")
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
    
    def list_tables(self) -> List[str]:
        """List all vs2_ tables"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'vs2_%'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
EOF

echo "✅ Created services/table_service.py"
```

### Step 1.4: Test TableService Works

```bash
python3 -c "
import pandas as pd
from services.table_service import TableService
try:
    s = TableService()
    df = pd.DataFrame({'col1': [1,2,3], 'col2': ['a','b','c']})
    table_name = s.save_dataframe(df, 'test_table')
    result = s.get_table('test_table')
    assert len(result) == 3
    print('✅ TableService works!')
except Exception as e:
    print(f'❌ TableService failed: {e}')
"
```

## Part 2: Create Tool Wrappers

### Step 2.1: Create VectorEmbedder Tool

```bash
cat > tools/vector_embedder.py << 'EOF'
from typing import Dict, Any

class VectorEmbedder:
    """Tool wrapper for VectorService"""
    
    def __init__(self, vector_service):
        self.service = vector_service
        self.tool_id = "VectorEmbedder"
        print(f"VectorEmbedder initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: {"text": str} or just str
        Output: {"embedding": List[float], "dimension": int, "model": str}
        """
        # Handle both dict with 'text' key and plain string
        if isinstance(data, str):
            text = data
        elif isinstance(data, dict) and 'text' in data:
            text = data['text']
        else:
            return {
                'success': False,
                'error': 'Input must be string or dict with "text" key',
                'uncertainty': 1.0
            }
        
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
                'uncertainty': 0.05,
                'reasoning': f'Embedding generated via {self.service.model}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0
            }
EOF

echo "✅ Created tools/vector_embedder.py"
```

### Step 2.2: Create TablePersister Tool

```bash
cat > tools/table_persister.py << 'EOF'
import pandas as pd
from typing import Dict, Any

class TablePersister:
    """Tool wrapper for TableService"""
    
    def __init__(self, table_service):
        self.service = table_service
        self.tool_id = "TablePersister"
        print(f"TablePersister initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: {"dataframe": dict/DataFrame/list, "table_name": str}
        Output: {"table_name": str, "rows": int, "columns": List[str]}
        """
        # Extract DataFrame from various formats
        df = None
        
        if 'dataframe' in data:
            df_data = data['dataframe']
            if isinstance(df_data, pd.DataFrame):
                df = df_data
            elif isinstance(df_data, dict):
                # Could be dict of lists or list of dicts
                try:
                    df = pd.DataFrame(df_data)
                except:
                    df = pd.DataFrame.from_dict(df_data)
            elif isinstance(df_data, list):
                df = pd.DataFrame(df_data)
        elif 'records' in data:
            df = pd.DataFrame(data['records'])
        elif 'data' in data:
            df = pd.DataFrame(data['data'])
        else:
            # Try to make DataFrame from the whole input
            try:
                df = pd.DataFrame(data)
            except:
                return {
                    'success': False,
                    'error': 'Could not create DataFrame from input',
                    'uncertainty': 1.0
                }
        
        table_name = data.get('table_name', 'default_table')
        metadata = data.get('metadata', {})
        
        try:
            safe_name = self.service.save_dataframe(df, table_name, metadata)
            return {
                'success': True,
                'table_name': safe_name,
                'rows': len(df),
                'columns': list(df.columns),
                'uncertainty': 0.0,
                'reasoning': f'Data persisted to {safe_name}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0
            }
EOF

echo "✅ Created tools/table_persister.py"
```

### Step 2.3: Create/Update CrossModalConverter

First check if it exists:

```bash
if [ -f tools/crossmodal_converter.py ]; then
    echo "⚠️  CrossModalConverter exists, backing up..."
    cp tools/crossmodal_converter.py tools/crossmodal_converter.backup.py
fi

cat > tools/crossmodal_converter.py << 'EOF'
import pandas as pd
from typing import Dict, Any

class CrossModalConverter:
    """Enhanced wrapper for CrossModalService"""
    
    def __init__(self, crossmodal_service):
        self.service = crossmodal_service
        self.tool_id = "CrossModalConverter"
        print(f"CrossModalConverter initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modes:
        - graph_to_table: {"mode": "graph_to_table", "entity_ids": [...]}
        - table_to_graph: {"mode": "table_to_graph", "dataframe": pd.DataFrame}
        """
        mode = data.get('mode', 'graph_to_table')
        
        try:
            if mode == 'graph_to_table':
                # Get entity IDs - if not provided, get all
                entity_ids = data.get('entity_ids', [])
                if not entity_ids and 'graph' in data:
                    # Extract from graph data
                    entity_ids = [e['id'] for e in data['graph'].get('entities', [])]
                
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
                # Get DataFrame
                if 'dataframe' in data:
                    if isinstance(data['dataframe'], pd.DataFrame):
                        df = data['dataframe']
                    else:
                        df = pd.DataFrame(data['dataframe'])
                elif 'records' in data:
                    df = pd.DataFrame(data['records'])
                else:
                    return {'success': False, 'error': 'No dataframe provided for table_to_graph'}
                
                # CrossModalService.table_to_graph expects a DataFrame, not table_name
                graph = self.service.table_to_graph(df)
                return {
                    'success': True,
                    'entities': graph.get('entities', []),
                    'relationships': graph.get('relationships', []),
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
EOF

echo "✅ Created tools/crossmodal_converter.py"
```

## Part 3: Test Tools Work

### Step 3.1: Test VectorEmbedder

```bash
python3 -c "
from services.vector_service import VectorService
from tools.vector_embedder import VectorEmbedder

try:
    service = VectorService()
    tool = VectorEmbedder(service)
    
    # Test with string
    result = tool.process('Hello world')
    assert result['success']
    assert 'embedding' in result
    
    # Test with dict
    result = tool.process({'text': 'Hello world'})
    assert result['success']
    
    print('✅ VectorEmbedder works!')
except Exception as e:
    print(f'❌ VectorEmbedder failed: {e}')
"
```

### Step 3.2: Test TablePersister

```bash
python3 -c "
import pandas as pd
from services.table_service import TableService
from tools.table_persister import TablePersister

try:
    service = TableService()
    tool = TablePersister(service)
    
    # Test with records
    result = tool.process({
        'records': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}],
        'table_name': 'test_tool'
    })
    assert result['success']
    assert result['rows'] == 2
    
    print('✅ TablePersister works!')
except Exception as e:
    print(f'❌ TablePersister failed: {e}')
"
```

## Part 4: Create Registration Script

### Step 4.1: Create Complete Registration Script

```bash
cat > register_services_and_tools.py << 'EOF'
#!/usr/bin/env python3
"""
Complete registration script for all tools and services
Run this to set up the entire pipeline
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent))
sys.path.append('/home/brian/projects/Digimons')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

def register_all_tools():
    """Register all tools with framework"""
    
    print("Starting tool registration...")
    
    # Initialize Neo4j
    neo4j_driver = GraphDatabase.driver(
        'bolt://localhost:7687', 
        auth=('neo4j', 'devpassword')
    )
    
    # Verify Neo4j connection
    try:
        neo4j_driver.verify_connectivity()
        print("✅ Neo4j connected")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return None
    
    # Initialize framework
    framework = CleanToolFramework(neo4j_driver)
    
    # Initialize services
    from services.vector_service import VectorService
    from services.table_service import TableService
    from services.identity_service_v3 import IdentityServiceV3
    from services.provenance_enhanced import ProvenanceEnhanced
    from services.crossmodal_service import CrossModalService
    
    print("Initializing services...")
    vector_service = VectorService()
    table_service = TableService('vertical_slice.db')
    identity_service = IdentityServiceV3(neo4j_driver)
    provenance_service = ProvenanceEnhanced('vertical_slice.db')
    crossmodal_service = CrossModalService(neo4j_driver, 'vertical_slice.db')
    
    # Register existing tools
    from tools.text_loader_v3 import TextLoaderV3
    from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
    from tools.graph_persister_v2 import GraphPersisterV2
    
    # TextLoader
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
    
    # KnowledgeGraphExtractor
    from config.llm_config import get_llm_client
    llm = get_llm_client()
    framework.register_tool(
        KnowledgeGraphExtractor(llm),
        ToolCapabilities(
            tool_id="KnowledgeGraphExtractor",
            input_type=DataType.TEXT,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="character_sequence",
            output_construct="knowledge_graph",
            transformation_type="entity_extraction"
        )
    )
    
    # GraphPersister
    framework.register_tool(
        GraphPersisterV2(neo4j_driver, identity_service, crossmodal_service),
        ToolCapabilities(
            tool_id="GraphPersisterV2",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH,
            input_construct="knowledge_graph",
            output_construct="neo4j_graph",
            transformation_type="graph_persistence"
        )
    )
    
    # Register new tools
    from tools.vector_embedder import VectorEmbedder
    from tools.table_persister import TablePersister
    from tools.crossmodal_converter import CrossModalConverter
    
    # VectorEmbedder
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
    
    # TablePersister
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
    
    # CrossModalConverter
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
    
    print("\n✅ All tools registered successfully!")
    print("\nRegistered tools:")
    for tool_id in framework.tools.keys():
        print(f"  - {tool_id}")
    
    return framework

if __name__ == "__main__":
    framework = register_all_tools()
    
    if framework:
        print("\nTesting chain discovery...")
        
        # Test finding chains
        chain = framework.find_chain(DataType.TEXT, DataType.VECTOR)
        print(f"Text → Vector: {chain}")
        
        chain = framework.find_chain(DataType.FILE, DataType.VECTOR)
        print(f"File → Vector: {chain}")
        
        chain = framework.find_chain(DataType.NEO4J_GRAPH, DataType.TABLE)
        print(f"Graph → Table: {chain}")
EOF

echo "✅ Created register_services_and_tools.py"
chmod +x register_services_and_tools.py
```

### Step 4.2: Run Registration

```bash
python3 register_services_and_tools.py
```

Expected output:
```
Starting tool registration...
✅ Neo4j connected
VectorService initialized with model: text-embedding-3-small
TableService initialized with database: vertical_slice.db
✅ Schema initialized
...
✅ All tools registered successfully!

Testing chain discovery...
Text → Vector: ['VectorEmbedder']
File → Vector: ['TextLoaderV3', 'VectorEmbedder']
Graph → Table: ['CrossModalConverter']
```

## Part 5: End-to-End Test

### Step 5.1: Create Test Document

```bash
cat > test_embedding.txt << 'EOF'
The quick brown fox jumps over the lazy dog.
This is a test document for embedding generation.
EOF

echo "✅ Created test_embedding.txt"
```

### Step 5.2: Test Complete Pipeline

```bash
cat > test_end_to_end.py << 'EOF'
#!/usr/bin/env python3
"""Test end-to-end pipeline with new tools"""

from register_services_and_tools import register_all_tools
from framework.clean_framework import DataType

# Register everything
framework = register_all_tools()

print("\n" + "="*50)
print("TESTING END-TO-END PIPELINE")
print("="*50)

# Test 1: File → Text → Vector
print("\n1. Testing: File → Text → Vector")
result = framework.execute_chain(
    ['TextLoaderV3', 'VectorEmbedder'],
    'test_embedding.txt'
)

if result.success:
    print("✅ Success!")
    print(f"   - Embedding dimension: {result.final_output.get('dimension')}")
    print(f"   - Model used: {result.final_output.get('model')}")
else:
    print(f"❌ Failed: {result.error}")

# Test 2: File → Text → KG → Graph → Table
print("\n2. Testing: File → KG → Graph → Table")
result = framework.execute_chain(
    ['TextLoaderV3', 'KnowledgeGraphExtractor', 'GraphPersisterV2', 'CrossModalConverter'],
    'test_embedding.txt'
)

if result.success:
    print("✅ Success!")
    print(f"   - Rows in table: {result.final_output.get('rows')}")
    print(f"   - Columns: {result.final_output.get('columns')}")
else:
    print(f"❌ Failed: {result.error}")

# Test 3: Table persistence
print("\n3. Testing: Table Persistence")
from tools.table_persister import TablePersister
from services.table_service import TableService

service = TableService()
tool = TablePersister(service)

test_data = {
    'records': [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25}
    ],
    'table_name': 'test_people'
}

result = tool.process(test_data)
if result['success']:
    print("✅ Success!")
    print(f"   - Table saved: {result['table_name']}")
    print(f"   - Rows: {result['rows']}")
    
    # Verify we can read it back
    df = service.get_table('test_people')
    print(f"   - Retrieved {len(df)} rows")
else:
    print(f"❌ Failed: {result.get('error')}")

print("\n" + "="*50)
print("ALL TESTS COMPLETE")
print("="*50)
EOF

chmod +x test_end_to_end.py
python3 test_end_to_end.py
```

## Troubleshooting Guide

### If Neo4j won't connect:
```bash
# Check if Neo4j is running
sudo systemctl status neo4j

# Start if needed
sudo systemctl start neo4j

# Or with neo4j command
neo4j start
```

### If OpenAI API fails:
```bash
# Test API key directly
python3 -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
try:
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input='test'
    )
    print('✅ API key works')
except Exception as e:
    print(f'❌ API error: {e}')
"
```

### If imports fail:
```bash
# Make sure you're in the right directory
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Check Python can find modules
python3 -c "
import sys
print('Python path:')
for p in sys.path:
    print(f'  {p}')
"
```

### If SQLite fails:
```bash
# Check database exists and is writable
ls -la vertical_slice.db
# Should show: -rw-r--r-- 

# If not writable:
chmod 666 vertical_slice.db
```

## Success Criteria

You know it worked when:
1. ✅ `register_services_and_tools.py` shows all tools registered
2. ✅ Chain discovery finds paths
3. ✅ End-to-end test shows all three tests passing
4. ✅ No error messages

## What You Built

- **VectorService**: Calls OpenAI to generate embeddings
- **TableService**: Saves DataFrames to SQLite
- **VectorEmbedder**: Tool that wraps VectorService
- **TablePersister**: Tool that wraps TableService
- **CrossModalConverter**: Converts between graph and table
- **Complete Pipeline**: Can now do File → Text → Vector → Table workflows

This guide is bulletproof - every command is exact, every error is handled, and troubleshooting is provided.