# KGAS MVP Day 1 Implementation Guide
## Cross-Modal Analysis Vertical Slice - Environment Setup & Basic Pipeline

## 🎯 Today's Goal
Get databases running and demonstrate basic document → entity extraction pipeline.

## 📋 Day 1 Checklist

### Morning Tasks (Environment Setup)
- [ ] Start Neo4j database with Docker
- [ ] Verify Neo4j connection
- [ ] Test SQLite database
- [ ] Verify Python environment

### Afternoon Tasks (Basic Pipeline)
- [ ] Load test document
- [ ] Extract entities with SpaCy
- [ ] Initialize ServiceManager
- [ ] Save results to file

## 🚀 Step-by-Step Implementation

### Step 1: Start Neo4j Database (30 minutes)

```bash
# 1.1 Navigate to project root
cd /home/brian/projects/Digimons

# 1.2 Check if Docker is running
docker --version
# If not installed: sudo apt-get install docker.io docker-compose

# 1.3 Start Neo4j using existing config
cd config/environments
docker-compose up -d

# 1.4 Wait for Neo4j to be ready (important!)
echo "Waiting for Neo4j to start..."
sleep 30

# 1.5 Verify Neo4j is running
docker ps | grep neo4j
# Should see: super_digimon_neo4j container running
```

### Step 2: Test Neo4j Connection (15 minutes)

```bash
# 2.1 Test with cypher-shell
docker exec -it super_digimon_neo4j cypher-shell \
  -u neo4j \
  -p ${NEO4J_PASSWORD:-password123}

# In cypher-shell, run:
RETURN "Neo4j is working!" as message;
# Type :exit to quit

# 2.2 Alternative: Test with browser
open http://localhost:7474
# Login with neo4j / password123
```

### Step 3: Verify SQLite (15 minutes)

Create `test_sqlite.py`:
```python
#!/usr/bin/env python3
"""Test SQLite database functionality"""

import sqlite3
import os
from datetime import datetime

# Create test database
db_path = "kgas_test.db"
print(f"Creating SQLite database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create test table
cursor.execute("""
CREATE TABLE IF NOT EXISTS test_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert test data
test_data = [
    ("Apple Inc.", "ORG"),
    ("Steve Jobs", "PERSON"),
    ("Cupertino", "LOC")
]

for name, entity_type in test_data:
    cursor.execute(
        "INSERT INTO test_entities (name, type) VALUES (?, ?)",
        (name, entity_type)
    )

conn.commit()

# Verify data
cursor.execute("SELECT * FROM test_entities")
results = cursor.fetchall()

print(f"\n✅ SQLite working! Found {len(results)} entities:")
for row in results:
    print(f"  - {row[1]} ({row[2]})")

conn.close()
```

Run it:
```bash
python test_sqlite.py
```

### Step 4: Set Up Python Environment (30 minutes)

Create `setup_environment.py`:
```python
#!/usr/bin/env python3
"""Verify Python environment and dependencies"""

import sys
import os

# Add project to path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

print(f"Python version: {sys.version}")
print(f"Project root: {project_root}")

# Test critical imports
try:
    import neo4j
    print("✅ neo4j package available")
except ImportError:
    print("❌ Missing neo4j - run: pip install neo4j")

try:
    import spacy
    print("✅ spacy package available")
except ImportError:
    print("❌ Missing spacy - run: pip install spacy")
    
try:
    import pandas
    print("✅ pandas package available")
except ImportError:
    print("❌ Missing pandas - run: pip install pandas")

# Test project imports
try:
    from src.core.service_manager import ServiceManager
    print("✅ ServiceManager importable")
except ImportError as e:
    print(f"❌ Cannot import ServiceManager: {e}")

try:
    from src.tools.phase1.t23a_spacy_ner import SpacyNER
    print("✅ SpacyNER importable")
except ImportError as e:
    print(f"❌ Cannot import SpacyNER: {e}")

print("\nEnvironment check complete!")
```

### Step 5: Basic Document Processing Pipeline (1 hour)

Create `day1_basic_pipeline.py`:
```python
#!/usr/bin/env python3
"""
Day 1: Basic document processing pipeline
Goal: Text → Entities → Display
"""

import sys
import os
import json
from datetime import datetime

# Fix imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_basic_extraction():
    """Test basic entity extraction without database dependencies"""
    
    print("=== KGAS Day 1: Basic Pipeline Test ===\n")
    
    # Step 1: Prepare test document
    test_document = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976.
    The company is headquartered in Cupertino, California. Apple's CEO Tim Cook announced 
    the new iPhone at the event in San Francisco. The company's market cap exceeded 
    $3 trillion in 2024, making it one of the most valuable companies alongside Microsoft 
    and Google. Apple Park, the company's headquarters, is located at One Apple Park Way.
    """
    
    print("Step 1: Test Document")
    print("-" * 50)
    print(test_document[:200] + "...")
    print()
    
    # Step 2: Try to extract entities with SpaCy
    print("Step 2: Entity Extraction")
    print("-" * 50)
    
    try:
        # Try SpaCy NER first
        import spacy
        
        # Load model (download with: python -m spacy download en_core_web_sm)
        try:
            nlp = spacy.load("en_core_web_sm")
        except:
            print("SpaCy model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        
        # Process document
        doc = nlp(test_document)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        print(f"✅ Extracted {len(entities)} entities:\n")
        
        # Group by type
        from collections import defaultdict
        by_type = defaultdict(list)
        for ent in entities:
            by_type[ent["type"]].append(ent["text"])
        
        for entity_type, names in by_type.items():
            print(f"{entity_type}:")
            for name in set(names):  # Unique names
                print(f"  - {name}")
            print()
            
    except Exception as e:
        print(f"❌ SpaCy extraction failed: {e}")
        print("Falling back to simple extraction...")
        
        # Simple pattern-based extraction as fallback
        import re
        
        # Find capitalized words (potential entities)
        pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
        matches = re.findall(pattern, test_document)
        
        entities = []
        for match in set(matches):
            entities.append({
                "text": match,
                "type": "UNKNOWN",
                "start": test_document.find(match),
                "end": test_document.find(match) + len(match)
            })
        
        print(f"✅ Extracted {len(entities)} potential entities:")
        for ent in entities[:10]:
            print(f"  - {ent['text']}")
    
    # Step 3: Save results
    print("\nStep 3: Saving Results")
    print("-" * 50)
    
    output_file = f"day1_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "document_length": len(test_document),
        "entities_found": len(entities),
        "entities": entities,
        "entity_types": list(by_type.keys()) if 'by_type' in locals() else ["UNKNOWN"]
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    
    # Step 4: Summary
    print("\nStep 4: Summary")
    print("-" * 50)
    print(f"Document length: {len(test_document)} characters")
    print(f"Entities found: {len(entities)}")
    print(f"Unique entities: {len(set(e['text'] for e in entities))}")
    print(f"Entity types: {len(set(e['type'] for e in entities))}")
    
    return entities

def test_service_manager():
    """Test ServiceManager initialization"""
    print("\n=== Testing ServiceManager ===\n")
    
    try:
        from src.core.service_manager import ServiceManager
        
        # Try with fallback mode
        os.environ['KGAS_FALLBACK_MODE'] = 'true'
        
        sm = ServiceManager()
        print("✅ ServiceManager initialized")
        
        # Check available services
        services = []
        if hasattr(sm, 'provenance_service'):
            services.append("provenance")
        if hasattr(sm, 'identity_service'):
            services.append("identity")
        if hasattr(sm, 'quality_service'):
            services.append("quality")
            
        print(f"Available services: {', '.join(services)}")
        
    except Exception as e:
        print(f"⚠️ ServiceManager initialization failed: {e}")
        print("This is expected without Neo4j. Continuing with basic pipeline...")

if __name__ == "__main__":
    # Run basic extraction
    entities = test_basic_extraction()
    
    # Try ServiceManager (may fail without Neo4j)
    test_service_manager()
    
    print("\n" + "=" * 50)
    print("Day 1 Complete! 🎉")
    print("=" * 50)
    print("\nNext Steps (Day 2):")
    print("1. Store entities in Neo4j")
    print("2. Build relationships")
    print("3. Run graph analysis")
    print("\nTo continue, ensure Neo4j is running:")
    print("  docker ps | grep neo4j")
```

### Step 6: Verify Everything Works (30 minutes)

Create `day1_verification.sh`:
```bash
#!/bin/bash

echo "=== Day 1 Verification Script ==="
echo

# Check Docker
echo "1. Checking Docker..."
if docker ps | grep -q neo4j; then
    echo "✅ Neo4j is running"
else
    echo "❌ Neo4j not running. Starting..."
    cd config/environments && docker-compose up -d
    sleep 30
fi
echo

# Check Python
echo "2. Checking Python environment..."
python setup_environment.py
echo

# Test SQLite
echo "3. Testing SQLite..."
python test_sqlite.py
echo

# Run pipeline
echo "4. Running basic pipeline..."
python day1_basic_pipeline.py
echo

echo "=== Day 1 Verification Complete ==="
echo
echo "If all checks passed, you're ready for Day 2!"
echo "If any failed, fix the issues and run this script again."
```

Make it executable and run:
```bash
chmod +x day1_verification.sh
./day1_verification.sh
```

## 🔧 Troubleshooting

### Problem: Docker not installed
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Problem: Neo4j won't start
```bash
# Check logs
docker logs super_digimon_neo4j

# Common fix: Remove old data
docker-compose down -v
docker-compose up -d
```

### Problem: Python import errors
```bash
# Install dependencies
pip install neo4j spacy pandas numpy scipy

# Download SpaCy model
python -m spacy download en_core_web_sm
```

### Problem: ServiceManager fails
```python
# Use fallback mode (no Neo4j required)
os.environ['KGAS_FALLBACK_MODE'] = 'true'
```

## 📊 Success Criteria for Day 1

### ✅ Must Have
- [ ] Neo4j container running
- [ ] SQLite database created
- [ ] Basic entity extraction working
- [ ] Results saved to JSON file

### 🎯 Nice to Have
- [ ] ServiceManager initialized
- [ ] All Python imports working
- [ ] Neo4j browser accessible

## 📝 Day 1 Deliverables

By end of Day 1, you should have:
1. **Running Neo4j** database (docker container)
2. **Working SQLite** test database
3. **Entity extraction results** in JSON file
4. **Verification script** showing all components work

## 🚀 Next: Day 2 Preview

Tomorrow we'll:
1. Store extracted entities in Neo4j
2. Build relationships between entities
3. Run PageRank to find important entities
4. Visualize the knowledge graph

## 💡 Key Insights

The goal of Day 1 is to **prove the basic pipeline works** without worrying about:
- Perfect entity extraction
- All services working
- Production features

Focus on getting **something working end-to-end**, then improve iteratively.

## 📚 References

- Main plan: `/docs/architecture/debugging_20250127/VERTICAL_SLICE_MVP_PLAN.md`
- System overview: `/docs/architecture/debugging_20250127/SYSTEM_COMPLETENESS_SUMMARY.md`
- Original investigation: `/docs/architecture/debugging_20250127/README.md`