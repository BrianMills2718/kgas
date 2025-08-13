# KGAS Vertical Slice MVP - Concrete Implementation Plan
## Date: 2025-01-27
## Goal: Demonstrate complete cross-modal analysis workflow

## 🎯 MVP Definition: Cross-Modal Analysis Demo

**User Story**: 
"As a researcher, I want to upload a PDF document, extract entities into a knowledge graph, identify the most important entities using graph analysis, export them to a table for statistical analysis, and see the complete provenance trail."

**Success Criteria**:
1. PDF → Entities → Graph (Neo4j)
2. Graph analysis → Top 100 central entities
3. Export to table (SQLite) 
4. Statistical analysis on table
5. Complete provenance tracking showing lineage

## Day 1: Environment Setup & Basic Pipeline

### Morning: Get Databases Running
```bash
# Step 1: Start Neo4j and verify
cd /home/brian/projects/Digimons/config/environments
docker-compose up -d
docker ps  # Verify neo4j container running

# Step 2: Test Neo4j connection
docker exec -it super_digimon_neo4j cypher-shell -u neo4j -p ${NEO4J_PASSWORD}
# Run: RETURN 1;  # Should return 1

# Step 3: Verify SQLite
python -c "
import sqlite3
conn = sqlite3.connect('kgas_provenance.db')
print('SQLite working')
conn.close()
"
```

### Afternoon: Basic Document Processing
```python
# vertical_slice_test.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.core.service_manager import ServiceManager

# Step 1: Initialize services
service_manager = ServiceManager()

# Step 2: Load test document
pdf_loader = PDFLoader()
text = "Apple Inc. was founded by Steve Jobs in Cupertino. The company developed the iPhone."

# Step 3: Extract entities
spacy_ner = SpacyNER()
entities = spacy_ner.extract_entities(text)
print(f"Extracted {len(entities)} entities")

# Verify output
for entity in entities[:5]:
    print(f"- {entity['text']} ({entity['type']})")
```

## Day 2: Graph Creation & Analysis

### Morning: Build Knowledge Graph
```python
# graph_creation.py
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.core.neo4j_manager import Neo4jManager

# Step 1: Build graph from entities
entity_builder = EntityBuilder()
nodes = entity_builder.build_entities(entities)

edge_builder = EdgeBuilder()
relationships = edge_builder.build_edges(entities, text)

# Step 2: Store in Neo4j
neo4j_manager = Neo4jManager()
for node in nodes:
    neo4j_manager.create_node(node)
    
for rel in relationships:
    neo4j_manager.create_relationship(rel)

print(f"Created {len(nodes)} nodes and {len(relationships)} relationships")
```

### Afternoon: Graph Analysis
```python
# graph_analysis.py
from src.tools.phase2.t68_pagerank import PageRankCalculator

# Calculate centrality
pagerank = PageRankCalculator()
centrality_scores = pagerank.calculate(neo4j_manager)

# Get top 100 most central entities
top_entities = sorted(centrality_scores.items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:100]

print(f"Top 10 most central entities:")
for entity, score in top_entities[:10]:
    print(f"- {entity}: {score:.4f}")
```

## Day 3: Cross-Modal Transfer

### Morning: Export Graph to Table
```python
# cross_modal_export.py
from src.tools.cross_modal.graph_table_exporter import GraphTableExporter
from src.core.provenance_service import ProvenanceService
import sqlite3

# Step 1: Initialize provenance tracking
provenance = ProvenanceService()
operation_id = provenance.start_operation(
    tool_id="cross_modal_export",
    operation_type="graph_to_table",
    inputs={"graph_nodes": len(top_entities)},
    parameters={"export_format": "sqlite"}
)

# Step 2: Export to SQLite table
exporter = GraphTableExporter()
table_data = exporter.export_to_table(
    entities=top_entities,
    source_graph="neo4j://localhost:7687/entities"
)

# Step 3: Store in SQLite
conn = sqlite3.connect('kgas_analysis.db')
cursor = conn.cursor()

# Create analysis table
cursor.execute("""
CREATE TABLE IF NOT EXISTS central_entities (
    entity_id TEXT PRIMARY KEY,
    entity_name TEXT,
    entity_type TEXT,
    centrality_score REAL,
    source_graph TEXT,
    export_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Insert data
for entity_id, score in top_entities:
    entity_data = neo4j_manager.get_node(entity_id)
    cursor.execute("""
        INSERT INTO central_entities 
        (entity_id, entity_name, entity_type, centrality_score, source_graph)
        VALUES (?, ?, ?, ?, ?)
    """, (entity_id, entity_data['name'], entity_data['type'], 
          score, "neo4j://localhost:7687/entities"))

conn.commit()

# Step 4: Record provenance
provenance.complete_operation(
    operation_id=operation_id,
    outputs={"table_rows": len(top_entities)},
    success=True
)

print(f"Exported {len(top_entities)} entities to SQLite table")
```

### Afternoon: Statistical Analysis
```python
# statistical_analysis.py
import pandas as pd
import sqlite3
from scipy import stats

# Step 1: Load data from SQLite
conn = sqlite3.connect('kgas_analysis.db')
df = pd.read_sql_query("SELECT * FROM central_entities", conn)

# Step 2: Perform statistical analysis
print("\n=== Statistical Analysis ===")
print(f"Total entities: {len(df)}")
print(f"Mean centrality: {df['centrality_score'].mean():.4f}")
print(f"Std deviation: {df['centrality_score'].std():.4f}")
print(f"Median centrality: {df['centrality_score'].median():.4f}")

# Entity type distribution
type_dist = df['entity_type'].value_counts()
print("\nEntity Type Distribution:")
for entity_type, count in type_dist.items():
    print(f"- {entity_type}: {count} ({count/len(df)*100:.1f}%)")

# Identify outliers (entities with exceptional centrality)
z_scores = stats.zscore(df['centrality_score'])
outliers = df[abs(z_scores) > 2]
print(f"\nOutliers (z-score > 2): {len(outliers)} entities")
```

## Day 4: Provenance & Visualization

### Morning: Complete Provenance Chain
```python
# provenance_visualization.py
from src.core.provenance_service import ProvenanceService

provenance = ProvenanceService()

# Get complete lineage
lineage = provenance.get_lineage(
    entity_id=top_entities[0][0]  # Trace top entity
)

print("=== Complete Data Lineage ===")
for step in lineage:
    print(f"""
Step: {step['operation_type']}
Tool: {step['tool_id']}
Timestamp: {step['timestamp']}
Input: {step['inputs']}
Output: {step['outputs']}
---""")

# Verify cross-modal provenance
print("\n=== Cross-Modal Transformation Tracking ===")
transformations = provenance.get_transformations(
    from_format="graph",
    to_format="table"
)

for t in transformations:
    print(f"Graph → Table: {t['timestamp']}")
    print(f"  Source: {t['source_uri']}")
    print(f"  Target: {t['target_table']}")
    print(f"  Entities: {t['entity_count']}")
```

### Afternoon: Create Demo Dashboard
```python
# demo_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from neo4j import GraphDatabase

st.title("KGAS Cross-Modal Analysis Demo")

# Section 1: Document Input
st.header("1. Document Processing")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
if uploaded_file:
    st.success(f"Loaded: {uploaded_file.name}")
    # Process document...

# Section 2: Graph Visualization
st.header("2. Knowledge Graph")
# Show Neo4j graph visualization
# Display entity count, relationship count

# Section 3: Centrality Analysis
st.header("3. Graph Analysis Results")
df = pd.read_sql_query("SELECT * FROM central_entities", conn)
fig = px.bar(df.head(20), x='entity_name', y='centrality_score',
             title="Top 20 Most Central Entities")
st.plotly_chart(fig)

# Section 4: Statistical Results
st.header("4. Statistical Analysis")
col1, col2, col3 = st.columns(3)
col1.metric("Total Entities", len(df))
col2.metric("Mean Centrality", f"{df['centrality_score'].mean():.4f}")
col3.metric("Outliers", len(outliers))

# Section 5: Provenance Trail
st.header("5. Complete Provenance")
st.json(lineage)
```

## Day 5: Testing & Documentation

### Morning: End-to-End Test
```python
# test_vertical_slice.py
def test_complete_workflow():
    """Test the entire cross-modal pipeline"""
    
    # 1. Load document
    assert load_document("test.pdf")
    
    # 2. Extract entities
    entities = extract_entities()
    assert len(entities) > 0
    
    # 3. Build graph
    graph = build_graph(entities)
    assert graph.node_count > 0
    
    # 4. Calculate centrality
    scores = calculate_centrality(graph)
    assert len(scores) > 0
    
    # 5. Export to table
    table = export_to_table(scores[:100])
    assert len(table) == 100
    
    # 6. Run statistics
    stats = calculate_statistics(table)
    assert stats['mean'] > 0
    
    # 7. Verify provenance
    lineage = get_provenance()
    assert len(lineage) > 5  # Multiple steps tracked
    
    print("✅ All tests passed!")
```

### Afternoon: Create Demo Script
```bash
#!/bin/bash
# run_demo.sh

echo "=== KGAS Cross-Modal Analysis Demo ==="

# 1. Start services
echo "Starting databases..."
docker-compose up -d
sleep 10

# 2. Run pipeline
echo "Processing document..."
python vertical_slice_test.py

echo "Creating knowledge graph..."
python graph_creation.py

echo "Analyzing graph..."
python graph_analysis.py

echo "Exporting to table..."
python cross_modal_export.py

echo "Running statistics..."
python statistical_analysis.py

echo "Showing provenance..."
python provenance_visualization.py

# 3. Launch dashboard
echo "Starting dashboard..."
streamlit run demo_dashboard.py

echo "Demo complete! Dashboard at http://localhost:8501"
```

## Success Metrics

### Functional Requirements
- [ ] PDF loads successfully
- [ ] Entities extracted (>10 entities)
- [ ] Graph created in Neo4j
- [ ] Centrality calculated
- [ ] Top 100 exported to SQLite
- [ ] Statistics computed
- [ ] Provenance complete

### Performance Targets
- [ ] Document processing: <30 seconds
- [ ] Graph analysis: <10 seconds
- [ ] Export to table: <5 seconds
- [ ] Statistical analysis: <2 seconds

### Quality Metrics
- [ ] Entity extraction accuracy: >80%
- [ ] Graph connectivity: >50% entities connected
- [ ] Provenance completeness: 100% operations tracked

## Troubleshooting Guide

### Common Issues & Solutions

1. **Neo4j Connection Failed**
   ```bash
   # Check container
   docker ps
   docker logs super_digimon_neo4j
   # Restart if needed
   docker-compose restart neo4j
   ```

2. **Import Errors**
   ```python
   # Add to script start
   import sys
   sys.path.insert(0, '/home/brian/projects/Digimons')
   ```

3. **Service Manager Issues**
   ```python
   # Use fallback mode
   os.environ['KGAS_FALLBACK_MODE'] = 'true'
   ```

4. **Memory Issues**
   ```python
   # Enable chunking
   from src.core.memory_manager import MemoryManager
   mm = MemoryManager()
   mm.config.chunk_size_mb = 10  # Smaller chunks
   ```

## Next Steps After MVP

Once vertical slice works:

1. **Week 2**: Performance optimization
   - Add caching
   - Optimize queries
   - Parallel processing

2. **Week 3**: Production hardening
   - Add error recovery
   - Implement monitoring
   - Create deployment scripts

3. **Week 4**: Feature expansion
   - Multi-document support
   - Advanced analytics
   - API endpoints

## Deliverables

By end of Day 5, we'll have:
1. ✅ Working cross-modal pipeline
2. ✅ Demo dashboard
3. ✅ Test suite
4. ✅ Documentation
5. ✅ Runnable demo script

This demonstrates the core value proposition of KGAS: seamless transformation between data representations with complete provenance tracking.