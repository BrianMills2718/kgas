# Simple Service Implementation Plan

**Time**: 1 hour
**Goal**: Add vector embeddings and table storage capabilities
**Principle**: KISS - Keep It Simple, Stupid

## Why This Exists
The V2 guide is over-engineered. This is the simple version that just works.

## Part 1: Setup (5 minutes)

### Single Verification Script
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Create one check script
cat > verify_setup.py << 'EOF'
#!/usr/bin/env python3
"""Single script to verify everything is ready"""
import sys
import os

def check_all():
    errors = []
    
    # Check location
    if not os.path.exists('framework/clean_framework.py'):
        errors.append("Wrong directory - must be in vertical_slice/")
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
        driver.verify_connectivity()
        driver.close()
    except:
        errors.append("Neo4j not running - run: sudo systemctl start neo4j")
    
    # Check dependencies
    try:
        import openai
        import pandas
        import numpy
        import litellm
        from dotenv import load_dotenv
    except ImportError as e:
        errors.append(f"Missing package: {e} - run: pip install openai pandas numpy litellm python-dotenv")
    
    # Check API keys
    sys.path.append('/home/brian/projects/Digimons')
    from dotenv import load_dotenv
    load_dotenv('/home/brian/projects/Digimons/.env')
    
    if not os.getenv('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY not set in .env")
    if not os.getenv('GEMINI_API_KEY'):
        errors.append("GEMINI_API_KEY not set in .env")
    
    # Report
    if errors:
        print("❌ Setup problems found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All checks passed - ready to proceed")
        return True

if __name__ == "__main__":
    if not check_all():
        sys.exit(1)
EOF

python3 verify_setup.py
```

## Part 2: Create Services (20 minutes)

### 2.1 VectorService (Simple)
```python
# services/vector_service.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('/home/brian/projects/Digimons/.env')

class VectorService:
    """Simple vector embedding service"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "text-embedding-3-small"
    
    def embed_text(self, text: str) -> list:
        """Get embedding for text"""
        if not text:
            return [0.0] * 1536  # Return zero vector for empty text
        
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
```

### 2.2 TableService (Simple)
```python
# services/table_service.py
import sqlite3
import json
from typing import Dict, Any, List

class TableService:
    """Simple table storage service"""
    
    def __init__(self, db_path: str = 'vertical_slice.db'):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vs2_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS vs2_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def save_embedding(self, text: str, embedding: list) -> int:
        """Save an embedding"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO vs2_embeddings (text, embedding) VALUES (?, ?)',
                (text, json.dumps(embedding))
            )
            return cursor.lastrowid
    
    def save_data(self, key: str, value: Any) -> int:
        """Save arbitrary data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'INSERT INTO vs2_data (key, value) VALUES (?, ?)',
                (key, json.dumps(value))
            )
            return cursor.lastrowid
    
    def get_embeddings(self, limit: int = 10) -> List[Dict]:
        """Get recent embeddings"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM vs2_embeddings ORDER BY id DESC LIMIT ?',
                (limit,)
            ).fetchall()
            return [dict(row) for row in rows]
```

## Part 3: Service Dependency Injection Pattern (15 minutes)

### 3.1 Tools Wrap Services Architecture
Following the **Tools → Services → Databases** pattern, tools wrap services for framework compatibility:

```python
# services/integrated_services.py
"""Service initialization and dependency injection"""
from neo4j import GraphDatabase
from services.vector_service import VectorService
from services.table_service import TableService
from services.identity_service_v3 import IdentityServiceV3
from services.provenance_enhanced import ProvenanceEnhanced
from services.crossmodal_service import CrossModalService

def initialize_all_services():
    """Initialize all services with proper dependencies"""
    # Database connections
    neo4j_driver = GraphDatabase.driver(
        'bolt://localhost:7687', 
        auth=('neo4j', 'devpassword')
    )
    sqlite_path = 'vertical_slice.db'
    
    # Initialize services
    vector_service = VectorService()
    table_service = TableService(sqlite_path)
    identity_service = IdentityServiceV3(neo4j_driver)
    provenance_service = ProvenanceEnhanced(sqlite_path)
    crossmodal_service = CrossModalService(neo4j_driver, sqlite_path)
    
    return {
        'vector': vector_service,
        'table': table_service,
        'identity': identity_service,
        'provenance': provenance_service,
        'crossmodal': crossmodal_service,
        'neo4j_driver': neo4j_driver
    }
```

### 3.2 Tool Registration with Service Injection
```python
# register_tools_with_services.py
"""Register tools with proper service dependencies"""
from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from tools.vector_embedder import VectorEmbedder
from tools.table_persister import TablePersister
from tools.graph_persister_v2 import GraphPersisterV2

def register_all_tools():
    """Register tools with injected services"""
    # Initialize services
    services = initialize_all_services()
    
    # Create framework
    framework = CleanToolFramework(services['neo4j_driver'])
    
    # Register tools with service dependencies
    framework.register_tool(
        VectorEmbedder(services['vector']),
        ToolCapabilities(
            tool_id="VectorEmbedder",
            input_type=DataType.TEXT,
            output_type=DataType.VECTOR
        )
    )
    
    framework.register_tool(
        TablePersister(services['table']),
        ToolCapabilities(
            tool_id="TablePersister",
            input_type=DataType.TABLE,
            output_type=DataType.TABLE
        )
    )
    
    # GraphPersisterV2 with multiple service dependencies
    framework.register_tool(
        GraphPersisterV2(
            services['neo4j_driver'],
            services['identity'],
            services['crossmodal']
        ),
        ToolCapabilities(
            tool_id="GraphPersisterV2",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH
        )
    )
    
    return framework, services
```

## Part 4: Testing (15 minutes)

### 3.1 Unit Tests
```python
# test_services.py
#!/usr/bin/env python3
"""Simple, systematic tests for services"""

import sys
import json
sys.path.append('/home/brian/projects/Digimons')

def test_vector_service():
    """Test VectorService"""
    print("\nTesting VectorService...")
    errors = []
    
    try:
        from services.vector_service import VectorService
        service = VectorService()
        
        # Test 1: Basic embedding
        embedding = service.embed_text("test")
        if len(embedding) != 1536:
            errors.append(f"Wrong embedding size: {len(embedding)}")
        
        # Test 2: Empty text
        empty_embedding = service.embed_text("")
        if len(empty_embedding) != 1536:
            errors.append("Empty text should return zero vector")
        
        # Test 3: Different texts give different embeddings
        emb1 = service.embed_text("hello")
        emb2 = service.embed_text("goodbye")
        if emb1 == emb2:
            errors.append("Different texts gave same embedding")
            
    except Exception as e:
        errors.append(f"VectorService failed: {e}")
    
    if errors:
        print("❌ VectorService tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ VectorService: All tests passed")
        return True

def test_table_service():
    """Test TableService"""
    print("\nTesting TableService...")
    errors = []
    
    try:
        from services.table_service import TableService
        service = TableService('test.db')  # Use test database
        
        # Test 1: Save embedding
        emb_id = service.save_embedding("test", [1.0, 2.0, 3.0])
        if not emb_id:
            errors.append("Failed to save embedding")
        
        # Test 2: Save data
        data_id = service.save_data("test_key", {"value": 123})
        if not data_id:
            errors.append("Failed to save data")
        
        # Test 3: Retrieve embeddings
        embeddings = service.get_embeddings(1)
        if not embeddings or embeddings[0]['text'] != 'test':
            errors.append("Failed to retrieve embedding")
            
    except Exception as e:
        errors.append(f"TableService failed: {e}")
    finally:
        # Cleanup test database
        import os
        if os.path.exists('test.db'):
            os.remove('test.db')
    
    if errors:
        print("❌ TableService tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ TableService: All tests passed")
        return True

def test_integration():
    """Test services working together"""
    print("\nTesting Integration...")
    errors = []
    
    try:
        from services.vector_service import VectorService
        from services.table_service import TableService
        
        vector_svc = VectorService()
        table_svc = TableService('test_integration.db')
        
        # Generate embedding and store it
        text = "Integration test"
        embedding = vector_svc.embed_text(text)
        row_id = table_svc.save_embedding(text, embedding)
        
        # Verify storage
        stored = table_svc.get_embeddings(1)
        if not stored:
            errors.append("Failed to store/retrieve embedding")
        else:
            stored_emb = json.loads(stored[0]['embedding'])
            if len(stored_emb) != 1536:
                errors.append("Stored embedding has wrong size")
                
    except Exception as e:
        errors.append(f"Integration failed: {e}")
    finally:
        import os
        if os.path.exists('test_integration.db'):
            os.remove('test_integration.db')
    
    if errors:
        print("❌ Integration tests failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Integration: All tests passed")
        return True

if __name__ == "__main__":
    all_pass = True
    all_pass &= test_vector_service()
    all_pass &= test_table_service()
    all_pass &= test_integration()
    
    print("\n" + "="*50)
    if all_pass:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
```

## Part 4: Simple Integration (15 minutes)

### 4.1 Direct Usage (No wrappers needed!)
```python
# simple_pipeline.py
#!/usr/bin/env python3
"""Simple pipeline using services directly"""

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from services.vector_service import VectorService
from services.table_service import TableService
from tools.text_loader_v3 import TextLoaderV3

def process_document(filepath: str):
    """Simple document processing pipeline"""
    
    # Initialize services
    vector_svc = VectorService()
    table_svc = TableService()
    text_loader = TextLoaderV3()
    
    # Load document
    print(f"Loading {filepath}...")
    result = text_loader.process(filepath)
    text = result.get('text', '')
    
    if not text:
        print("❌ No text extracted")
        return False
    
    print(f"✅ Extracted {len(text)} characters")
    
    # Generate embedding
    print("Generating embedding...")
    embedding = vector_svc.embed_text(text[:1000])  # First 1000 chars
    print(f"✅ Generated {len(embedding)}-dimensional embedding")
    
    # Store in table
    print("Storing in database...")
    row_id = table_svc.save_embedding(filepath, embedding)
    print(f"✅ Stored with ID {row_id}")
    
    # Store metadata
    metadata = {
        'filepath': filepath,
        'text_length': len(text),
        'embedding_dims': len(embedding)
    }
    table_svc.save_data(f"metadata_{filepath}", metadata)
    print("✅ Metadata stored")
    
    return True

if __name__ == "__main__":
    # Test with a simple file
    with open('test_doc.txt', 'w') as f:
        f.write("This is a test document for the simple pipeline.")
    
    if process_document('test_doc.txt'):
        print("\n✅ Pipeline successful!")
    else:
        print("\n❌ Pipeline failed!")
```

## Summary

### What We Built (Simple!)
1. **VectorService**: 20 lines - just calls OpenAI
2. **TableService**: 40 lines - just saves to SQLite  
3. **Tests**: Actual unit and integration tests
4. **Pipeline**: Direct service usage, no wrappers

### What We Removed (Unnecessary!)
- ❌ Tool wrappers (VectorEmbedder, TablePersister)
- ❌ BFS chain discovery
- ❌ Complex registration
- ❌ Evidence directories
- ❌ Multiple verification scripts

### Testing Plan (Systematic!)
```
1. Unit Tests
   - VectorService: embedding generation
   - TableService: data storage
   
2. Integration Tests  
   - Services working together
   - End-to-end pipeline
   
3. Error Tests
   - API failures
   - Empty inputs
   - Database errors
```

### Time Breakdown
- Setup & verification: 5 min
- Create services: 20 min
- Write tests: 20 min
- Integration: 15 min
- **Total: 1 hour**

This is KISS-compliant and has proper testing. No over-engineering, just working code.