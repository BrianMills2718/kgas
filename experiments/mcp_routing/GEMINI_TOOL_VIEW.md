# 🔍 What Gemini Sees: Complete Tool Catalog

**Generated**: 2025-08-04  
**Total Tools**: 100  
**Categories**: 8  

This document shows exactly what information Gemini receives when selecting tools for workflow generation.

---

## 📊 **Tool Categories Overview**

| Category | Count | Description |
|----------|-------|-------------|
| **document_loaders** | 12 | Load various document formats |
| **text_processing** | 15 | Clean, chunk, and process text |
| **entity_extraction** | 18 | Extract entities with various methods |
| **relationship_analysis** | 16 | Analyze relationships between entities |
| **graph_operations** | 14 | Build and manipulate knowledge graphs |
| **query_systems** | 10 | Query and search graph data |
| **analytics** | 8 | Analyze patterns and metrics |
| **export_visualization** | 7 | Export and visualize results |

---

## 📋 **Complete Tool Catalog**

### 📂 **Document Loaders (12 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `load_document_pdf` | Extract text and metadata from PDF documents | 0.3 | - | document_ref |
| `load_document_docx` | Load and parse Microsoft Word documents | 0.3 | - | document_ref |
| `load_document_txt` | Load plain text files with encoding detection | 0.3 | - | document_ref |
| `load_document_csv` | Parse CSV files with configurable delimiters | 0.3 | - | document_ref |
| `load_document_json` | Load and validate JSON documents | 0.3 | - | document_ref |
| `load_document_xml` | Parse XML documents with schema validation | 0.3 | - | document_ref |
| `load_document_html` | Extract content from HTML documents | 0.3 | - | document_ref |
| `load_document_xlsx` | Load Excel spreadsheets with multiple sheets | 0.3 | - | document_ref |
| `load_document_pptx` | Extract text from PowerPoint presentations | 0.3 | - | document_ref |
| `load_document_epub` | Load eBook content from EPUB files | 0.3 | - | document_ref |
| `load_document_rtf` | Parse Rich Text Format documents | 0.3 | - | document_ref |
| `load_document_odt` | Load OpenDocument text files | 0.3 | - | document_ref |

### 📝 **Text Processing (15 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `chunk_text_fixed` | Split text into fixed-size chunks | 0.2 | document_ref, text_ref | text_ref, chunks_ref |
| `chunk_text_semantic` | Split text using semantic boundaries | 0.4 | document_ref, text_ref | text_ref, chunks_ref |
| `chunk_text_sliding` | Create overlapping text chunks | 0.3 | document_ref, text_ref | text_ref, chunks_ref |
| `clean_text_basic` | Remove noise and normalize text | 0.2 | document_ref, text_ref | text_ref, chunks_ref |
| `clean_text_aggressive` | Intensive text cleaning and normalization | 0.4 | document_ref, text_ref | text_ref, chunks_ref |
| `tokenize_words` | Split text into word tokens | 0.1 | document_ref, text_ref | text_ref, chunks_ref |
| `tokenize_sentences` | Split text into sentence tokens | 0.2 | document_ref, text_ref | text_ref, chunks_ref |
| `extract_keywords` | Extract important keywords and phrases | 0.5 | document_ref, text_ref | text_ref, chunks_ref |
| `normalize_text` | Standardize text format and encoding | 0.2 | document_ref, text_ref | text_ref, chunks_ref |
| `remove_stopwords` | Filter out common stop words | 0.1 | document_ref, text_ref | text_ref, chunks_ref |
| `stem_words` | Reduce words to root forms | 0.3 | document_ref, text_ref | text_ref, chunks_ref |
| `lemmatize_text` | Convert words to dictionary forms | 0.4 | document_ref, text_ref | text_ref, chunks_ref |
| `detect_language` | Identify document language | 0.2 | document_ref, text_ref | text_ref, chunks_ref |
| `translate_text` | Translate text between languages | 0.7 | document_ref, text_ref | text_ref, chunks_ref |
| `extract_ngrams` | Extract n-gram patterns from text | 0.3 | document_ref, text_ref | text_ref, chunks_ref |

### 🏷️ **Entity Extraction (18 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `extract_entities_spacy_sm` | SpaCy small model entity extraction | 0.3 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_spacy_md` | SpaCy medium model entity extraction | 0.4 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_spacy_lg` | SpaCy large model entity extraction | 0.5 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_spacy_trf` | SpaCy transformer model extraction | 0.7 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_llm_gemini` | Gemini based entity extraction | 0.8 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_llm_claude` | Claude based entity extraction | 0.8 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_llm_gemini` | Gemini based entity extraction | 0.8 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_llm_local` | Local LLM entity extraction | 0.6 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_basic` | Basic pattern-based entity extraction | 0.2 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_regex` | Regular expression entity extraction | 0.3 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_scientific` | Scientific domain entity extraction | 0.6 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_business` | Business domain entity extraction | 0.5 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_medical` | Medical domain entity extraction | 0.7 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_legal` | Legal domain entity extraction | 0.6 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_financial` | Financial domain entity extraction | 0.6 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_ensemble` | Ensemble of multiple extraction methods | 0.8 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_active` | Active learning entity extraction | 0.7 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |
| `extract_entities_custom` | Custom model entity extraction | 0.6 | document_ref, text_ref, chunks_ref | entities_ref, annotations_ref |

### 🔗 **Relationship Analysis (16 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `extract_relationships_pattern` | Pattern-based relationship extraction | 0.4 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_dependency` | Dependency parsing relationships | 0.5 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_coreference` | Coreference-based relationships | 0.6 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_semantic` | Semantic similarity relationships | 0.7 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_llm` | LLM-based relationship extraction | 0.8 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_graph` | Graph-based relationship inference | 0.7 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_temporal` | Temporal relationship extraction | 0.6 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_spatial` | Spatial relationship extraction | 0.5 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_causal` | Causal relationship identification | 0.8 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_hierarchical` | Hierarchical relationship extraction | 0.6 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_network` | Network-based relationship analysis | 0.7 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_knowledge` | Knowledge-based relationship extraction | 0.8 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_statistical` | Statistical relationship analysis | 0.6 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_machine_learning` | ML-based relationship extraction | 0.7 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_rule_based` | Rule-based relationship extraction | 0.5 | entities_ref, chunks_ref | relationships_ref, edges_ref |
| `extract_relationships_hybrid` | Hybrid relationship extraction approach | 0.8 | entities_ref, chunks_ref | relationships_ref, edges_ref |

### 🕸️ **Graph Operations (14 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `build_graph_entities` | Build graph from entity data | 0.4 | entities_ref | graph_ref, nodes_ref |
| `build_graph_relationships` | Build graph from relationship data | 0.5 | relationships_ref, edges_ref | graph_ref, nodes_ref |
| `merge_graphs` | Merge multiple graphs | 0.6 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `filter_graph` | Filter graph by criteria | 0.3 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `prune_graph` | Remove low-importance nodes/edges | 0.4 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `cluster_graph` | Cluster graph into communities | 0.7 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `enrich_graph` | Add metadata to graph elements | 0.5 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `validate_graph` | Validate graph structure and data | 0.3 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `optimize_graph` | Optimize graph for performance | 0.6 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `transform_graph` | Transform graph structure | 0.7 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `compare_graphs` | Compare multiple graphs | 0.8 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `sample_graph` | Sample subgraph from large graph | 0.4 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `align_graphs` | Align entities across graphs | 0.8 | graph_ref, nodes_ref | graph_ref, nodes_ref |
| `project_graph` | Project graph to different structure | 0.7 | graph_ref, nodes_ref | graph_ref, nodes_ref |

### 🔍 **Query Systems (10 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `query_graph_multihop` | Multi-hop graph traversal queries | 0.7 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_semantic` | Semantic similarity queries | 0.6 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_temporal` | Time-based graph queries | 0.5 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_spatial` | Spatial graph queries | 0.5 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_similarity` | Entity similarity queries | 0.6 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_pattern` | Pattern matching queries | 0.7 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_path` | Path finding queries | 0.6 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_subgraph` | Subgraph extraction queries | 0.5 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_aggregation` | Aggregation queries | 0.4 | graph_ref, nodes_ref | results_ref, paths_ref |
| `query_graph_recommendation` | Recommendation queries | 0.8 | graph_ref, nodes_ref | results_ref, paths_ref |

### 📈 **Analytics (8 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `calculate_pagerank` | Calculate PageRank importance scores | 0.5 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `detect_anomalies` | Identify anomalous patterns | 0.7 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `perform_clustering` | Cluster similar entities | 0.6 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `calculate_centrality` | Calculate node centrality measures | 0.5 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `find_communities` | Detect community structure | 0.7 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `measure_influence` | Measure entity influence | 0.6 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `calculate_similarity` | Calculate entity similarities | 0.5 | graph_ref, nodes_ref | metrics_ref, scores_ref |
| `find_shortest_paths` | Find shortest paths between entities | 0.4 | graph_ref, nodes_ref | metrics_ref, scores_ref |

### 📊 **Export & Visualization (7 tools)**

| Tool Name | Description | Complexity | Inputs | Outputs |
|-----------|-------------|------------|---------|---------|
| `export_json` | Export data as JSON | 0.2 | All types | - |
| `export_csv` | Export tabular data as CSV | 0.2 | All types | - |
| `export_graphml` | Export graph as GraphML | 0.3 | graph_ref, nodes_ref | - |
| `export_gephi` | Export for Gephi visualization | 0.3 | graph_ref, nodes_ref | - |
| `visualize_network` | Create network visualization | 0.6 | graph_ref, nodes_ref | - |
| `generate_report` | Generate analysis report | 0.7 | All types | - |
| `create_dashboard` | Create interactive dashboard | 0.8 | All types | - |

---

## 🎯 **Example JSON Format Sent to Gemini**

```json
[
  {
    "name": "extract_entities_llm_gemini",
    "description": "Gemini based entity extraction",
    "category": "entity_extraction",
    "inputs": ["document_ref", "text_ref", "chunks_ref"],
    "outputs": ["entities_ref", "annotations_ref"],
    "complexity": 0.8
  },
  {
    "name": "chunk_text_semantic", 
    "description": "Split text using semantic boundaries",
    "category": "text_processing",
    "inputs": ["document_ref", "text_ref"],
    "outputs": ["text_ref", "chunks_ref"],
    "complexity": 0.4
  },
  {
    "name": "build_knowledge_graph",
    "description": "Build comprehensive knowledge graph",
    "category": "graph_operations", 
    "inputs": ["entities_ref", "relationships_ref"],
    "outputs": ["graph_ref", "nodes_ref"],
    "complexity": 0.7
  }
]
```

---

## 🧠 **Gemini's Cognitive Challenge**

When Gemini sees this tool catalog, it must:

### **1. Parse Tool Capabilities**
- Understand what each tool does from description alone
- Infer quality levels from complexity scores (0.1 = simple, 0.8 = advanced)
- Recognize domain specializations (scientific, business, financial)

### **2. Build Workflow Logic**
- Chain tools using input/output compatibility
- Understand logical sequences (load → process → extract → analyze)
- Balance multiple valid approaches

### **3. Optimize Trade-offs**
- **Efficiency vs Completeness**: Fewer steps vs thorough analysis
- **General vs Specialized**: Powerful LLM tools vs domain-specific tools
- **Certainty vs Performance**: Basic reliable tools vs advanced complex tools

### **4. Match Task Requirements**
- Parse natural language prompts for technical requirements
- Identify implicit workflow needs (relationships, graphs, exports)
- Handle varying levels of task complexity

---

## 🔍 **Key Insights**

### **Tool Selection Patterns**
- **18 entity extraction options** from basic (0.2) to LLM (0.8)
- **Multiple text processing approaches** with different trade-offs
- **Domain-specific vs general tools** for specialized tasks

### **Workflow Reasoning**
- Must infer logical sequences from 100+ unordered options
- No explicit templates - pure semantic reasoning required
- Input/output types provide dependency constraints

### **Intelligence Required**
- **Semantic understanding** of tool purposes
- **Dependency reasoning** for workflow construction  
- **Quality assessment** from descriptions and complexity scores
- **Efficiency optimization** across valid workflow options

**The fact that Gemini performs well at this task demonstrates sophisticated workflow reasoning capabilities beyond simple tool selection.**