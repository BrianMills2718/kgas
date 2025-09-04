# KGAS Full System Architecture
*Created: 2025-08-29*
*Status: Future Implementation Target*
*Evolution Path: From Vertical Slice → Full KGAS System*

**Purpose**: Comprehensive architecture specification for the complete Knowledge Graph Analysis System (KGAS), extracted from proposal planning materials and structured for future implementation phases.

---

## 🎯 **SYSTEM OVERVIEW**

### **KGAS Mission**
The Knowledge Graph Analysis System (KGAS) operationalizes theory-first computational social science through dynamic tool generation from academic theory papers. Unlike data-driven systems that find patterns first, KGAS starts with theories to guide analysis and data flow.

### **Core Innovation: Dynamic Tool Generation**
**Key Insight**: Tools are NOT pre-built. They are GENERATED from theory schemas extracted by LLMs.

```
Academic Papers → LLM → Theory Schema → Generated Tools → Analysis
```

### **System Capabilities**
- **Theory Extraction**: Convert academic papers into machine-readable theory schemas
- **Dynamic Tool Generation**: Create executable analysis tools from theory algorithms  
- **Cross-Modal Analysis**: Fluid movement between Graph, Table, and Vector representations
- **Workflow Orchestration**: Complex analytical pipelines through DAG execution
- **Uncertainty Tracking**: Transparent computational reasoning with provenance
- **Reproducibility**: Complete audit trails linking results to theoretical foundations

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Layers**
```
┌─────────────────────────────────────────────────────────────┐
│                  Research Interface Layer                    │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Natural Language Interface | DAG Visualization        │ │
│  │ Theory Selection UI        | Results Dashboard        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Workflow Orchestration Layer                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ WorkflowDAG Engine    │ Execution Patterns            │ │
│  │ Dependency Resolution │ Sequential/Parallel/Iterative │ │
│  │ State Management      │ Checkpoint Recovery           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Dynamic Tool Generation Layer                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Theory Extraction     │ Tool Generator               │ │
│  │ Schema Validation     │ Code Generation via LLM      │ │
│  │ Algorithm Parsing     │ Runtime Tool Registration    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      6 Tool Suites                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐   │
│  │Document  │Graph Ops │Statistical│Vector Ops│Cross-    │   │
│  │Processing│          │Analysis   │          │Modal     │   │
│  │          │          │           │          │Converters│   │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Agent-Based Modeling Suite                │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Data Storage Layer                       │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │     Neo4j              │    │     SQLite             │  │
│  │ • Knowledge Graphs     │    │ • Analysis Results     │  │
│  │ • Theory Schemas       │    │ • Workflow State       │  │
│  │ • Vector Embeddings    │    │ • Statistical Tables   │  │
│  └────────────────────────┘    └────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **THEORY META-SCHEMA ARCHITECTURE**

### **4-Component Theory Representation**

#### **1. Metadata Component**
```json
{
  "metadata": {
    "theory_name": "Social Identity Theory",
    "authors": ["Henri Tajfel", "John Turner"],
    "publication_year": 1979,
    "related_theories": {
      "extends": ["Social Categorization Theory"],
      "synthesizes": ["Self-Categorization Theory"],
      "contradicts": ["Individual Psychology Models"]
    },
    "scope_boundaries": "Intergroup behavior, group membership effects",
    "version": "1.0"
  }
}
```

#### **2. Theoretical Structure Component**  
```json
{
  "theoretical_structure": {
    "entities": [
      {
        "name": "social_identity",
        "definition": "That part of an individual's self-concept derived from knowledge of membership in social groups",
        "properties": ["salience", "valence", "centrality"]
      },
      {
        "name": "in_group",
        "definition": "Social group to which an individual belongs",
        "properties": ["size", "distinctiveness", "status"]
      }
    ],
    "relations": [
      {
        "name": "in_group_favoritism",
        "source": "group_member",
        "target": "in_group",
        "type": "causal",
        "strength": "strong",
        "conditions": ["identity_salience > 0.5"]
      }
    ],
    "modifiers": [
      {
        "name": "intergroup_context",
        "type": "boundary_condition",
        "effect": "amplifies group identity effects"
      }
    ]
  }
}
```

#### **3. Computational Representation Component**
```json
{
  "computational_representations": {
    "graph": {
      "nodes": ["individual", "group", "identity_dimension"],
      "edges": ["membership", "identification", "comparison"],
      "metrics": ["centrality", "clustering", "path_distance"]
    },
    "table": {
      "variables": ["identity_strength", "group_status", "bias_measure"],
      "relationships": ["correlation", "regression", "interaction"],
      "statistics": ["mean_difference", "effect_size", "confidence_interval"]
    },
    "vector": {
      "embeddings": ["identity_vector", "group_prototype"],
      "operations": ["similarity", "clustering", "projection"],
      "metrics": ["cosine_distance", "euclidean_norm"]
    }
  }
}
```

#### **4. Algorithms Component**
```json
{
  "algorithms": {
    "mathematical": [
      {
        "name": "meta_contrast_ratio",
        "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
        "parameters": {
          "x_i": "individual's position vector",
          "x_outgroup": "outgroup members' positions",
          "x_ingroup": "ingroup members' positions"
        },
        "interpretation": "Higher MCR indicates stronger group identification"
      }
    ],
    "logical": [
      {
        "name": "identity_activation",
        "rules": [
          "IF intergroup_context AND identity_salience > threshold THEN activate_group_identity",
          "IF group_threat > individual_threat THEN prioritize_group_identity"
        ]
      }
    ],
    "procedural": [
      {
        "name": "minimal_group_paradigm",
        "steps": [
          "1. Categorize individuals into arbitrary groups",
          "2. Measure pre-categorization attitudes",
          "3. Present intergroup allocation task",
          "4. Measure post-task bias indicators",
          "5. Calculate in-group favoritism metrics"
        ]
      }
    ]
  }
}
```

---

## ⚙️ **DYNAMIC TOOL GENERATION SYSTEM**

### **Theory Extraction Pipeline**
```
Academic Paper → LLM → Theory Schema (JSON) → Tool Generator → Executable Tool
```

### **DynamicToolGenerator Architecture**
```python
class DynamicToolGenerator:
    """Generate executable tools from theory algorithms"""
    
    def __init__(self, llm_service, tool_registry):
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.code_templates = self._load_templates()
    
    def generate_from_theory(self, theory_schema: Dict) -> List[KGASTool]:
        """Generate tools from theory schema algorithms"""
        tools = []
        
        # Generate mathematical tools
        for algorithm in theory_schema.get('algorithms', {}).get('mathematical', []):
            tool_code = self._generate_mathematical_tool(algorithm)
            tool = self._compile_and_register(tool_code)
            tools.append(tool)
        
        # Generate logical tools
        for algorithm in theory_schema.get('algorithms', {}).get('logical', []):
            tool_code = self._generate_logical_tool(algorithm)
            tool = self._compile_and_register(tool_code)
            tools.append(tool)
            
        # Generate procedural tools
        for algorithm in theory_schema.get('algorithms', {}).get('procedural', []):
            tool_code = self._generate_procedural_tool(algorithm)
            tool = self._compile_and_register(tool_code)
            tools.append(tool)
        
        return tools
    
    def _generate_mathematical_tool(self, algorithm: Dict) -> str:
        """Generate code for mathematical algorithm"""
        prompt = f"""
        Generate a KGASTool implementation for:
        Formula: {algorithm['formula']}
        Parameters: {algorithm['parameters']}
        Include execute() method, uncertainty assessment, and error handling.
        Use template: {self.code_templates['mathematical']}
        """
        return self.llm_service.generate_code(prompt)
```

### **Example: Generated MCR Calculator Tool**
```python
# Generated by DynamicToolGenerator from Social Identity Theory schema
class GeneratedMCRTool(KGASTool):
    """Meta-Contrast Ratio calculator from Social Identity Theory"""
    
    def __init__(self, service_manager):
        super().__init__(service_manager)
        self.tool_id = "GENERATED_MCR_CALCULATOR"
        self.theory_source = "Social Identity Theory (Tajfel & Turner, 1979)"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Calculate meta-contrast ratio for group identification"""
        try:
            individual_pos = request.data['individual_position']
            ingroup_positions = request.data['ingroup_positions'] 
            outgroup_positions = request.data['outgroup_positions']
            
            # MCR = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|
            outgroup_distances = [
                abs(individual_pos - pos) for pos in outgroup_positions
            ]
            ingroup_distances = [
                abs(individual_pos - pos) for pos in ingroup_positions  
            ]
            
            mcr = sum(outgroup_distances) / sum(ingroup_distances)
            
            return ToolResult(
                success=True,
                data={'mcr_score': mcr, 'interpretation': self._interpret_mcr(mcr)},
                uncertainty=0.05,  # Mathematical calculation uncertainty
                reasoning=f"MCR calculated using Social Identity Theory formula"
            )
            
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

---

## 📊 **6 TOOL SUITES ARCHITECTURE**

### **1. Document Processing Suite**
```python
class DocumentProcessingSuite:
    """Multi-format document extraction and preprocessing"""
    
    tools = [
        'PDFExtractor',           # Academic papers, reports
        'WebContentExtractor',    # Online articles, social media
        'TextPreprocessor',       # Cleaning, normalization
        'MetadataExtractor',      # Authors, dates, citations
        'ReferenceParser',        # Bibliography extraction
        'LanguageDetector',       # Multi-language support
        'ContentSegmenter'        # Section/paragraph parsing
    ]
```

### **2. Graph Operations Suite**
```python
class GraphOperationsSuite:
    """Network construction and analysis tools"""
    
    tools = [
        'TheoryGuidedEntityExtractor',  # Theory-specific entity identification
        'RelationshipBuilder',          # Multi-type network construction
        'CentralityCalculator',         # Betweenness, eigenvector, PageRank
        'CommunityDetector',           # Louvain, Girvan-Newman algorithms
        'PathAnalyzer',                # Shortest paths, network distance
        'MotifFinder',                 # Structural pattern detection
        'GraphTransformer',            # Format conversion, projection
        'NetworkVisualizer'            # Interactive graph visualization
    ]
```

### **3. Statistical Analysis Suite**
```python
class StatisticalAnalysisSuite:
    """Comprehensive statistical modeling and testing"""
    
    tools = [
        'DescriptiveStatsCalculator',   # Summary statistics, distributions
        'HypothesisTestRunner',         # t-tests, ANOVA, chi-square
        'RegressionModeler',            # Linear, logistic, multilevel
        'SEMAnalyzer',                  # Structural equation modeling
        'FactorAnalyzer',              # EFA, CFA, reliability analysis
        'TimeSeriesAnalyzer',          # ARIMA, VAR, Granger causality
        'BayesianModeler',             # Bayesian inference, MCMC
        'EffectSizeCalculator'         # Cohen's d, eta-squared, etc.
    ]
```

### **4. Vector Operations Suite**
```python
class VectorOperationsSuite:
    """Embedding generation and similarity analysis"""
    
    tools = [
        'MultiModalEmbedder',          # Text, image, graph embeddings
        'SimilarityCalculator',        # Cosine, Euclidean, custom metrics  
        'SemanticClusterer',          # K-means, hierarchical, DBSCAN
        'DimensionalityReducer',      # PCA, t-SNE, UMAP
        'VectorSearchEngine',         # Efficient similarity search
        'EmbeddingVisualizer',        # 2D/3D embedding plots
        'ConceptMapper',              # Concept relationship mapping
        'AnalogicalReasoner'          # Vector arithmetic reasoning
    ]
```

### **5. Cross-Modal Converters Suite**
```python
class CrossModalConvertersSuite:
    """Bidirectional conversion between data representations"""
    
    tools = [
        'GraphToTableConverter',       # Network metrics → DataFrame
        'TableToGraphConverter',       # Correlation → Network
        'GraphToVectorConverter',      # Node embeddings, graph2vec
        'VectorToGraphConverter',      # Similarity networks
        'TableToVectorConverter',      # Statistical embeddings
        'VectorToTableConverter',      # Cluster assignments, similarity matrices
        'HybridRepresentationBuilder', # Multi-modal data structures
        'RepresentationValidator'      # Cross-modal consistency checking
    ]
```

### **6. Agent-Based Modeling Suite**
```python
class AgentBasedModelingSuite:
    """Theory-driven simulation and modeling"""
    
    tools = [
        'TheoryBasedAgentGenerator',   # Agent parameterization from theory
        'BehaviorRuleEngine',         # Theory-derived decision mechanisms
        'NetworkDynamicsSimulator',   # Evolving interaction patterns
        'SimulationController',       # Time steps, convergence, intervention
        'AgentTrajectoryAnalyzer',    # Individual agent paths
        'AggregateMetricsCalculator', # Population-level outcomes
        'InterventionTester',         # Policy/treatment simulation
        'ModelValidator'              # Simulation-reality comparison
    ]
```

---

## 🔄 **WORKFLOW ORCHESTRATION ARCHITECTURE**

### **WorkflowDAG Implementation**
```python
class WorkflowDAG:
    """Orchestrates complex analytical workflows through directed acyclic graphs"""
    
    def __init__(self):
        self.nodes = {}          # Analytical operations  
        self.edges = {}          # Data dependencies
        self.state = {}          # Execution state
        self.checkpoints = {}    # Recovery points
        self.metadata = {}       # Workflow provenance
        
    def add_node(self, node_id: str, operation: str, parameters: Dict):
        """Add analytical operation to workflow"""
        self.nodes[node_id] = {
            'operation': operation,
            'parameters': parameters,
            'status': 'pending',
            'created_at': datetime.now(),
            'dependencies': []
        }
        
    def add_edge(self, from_node: str, to_node: str, data_mapping: Dict):
        """Define data flow between operations"""
        self.edges[(from_node, to_node)] = {
            'mapping': data_mapping,
            'data_type': data_mapping.get('type'),
            'transformation': data_mapping.get('transform')
        }
        self.nodes[to_node]['dependencies'].append(from_node)
        
    def execute(self) -> WorkflowResult:
        """Execute workflow with dependency management"""
        try:
            execution_order = self.topological_sort()
            self._validate_execution_plan(execution_order)
            
            for node_id in execution_order:
                result = self._execute_node_with_recovery(node_id)
                if not result.success:
                    return self._handle_execution_failure(node_id, result)
                    
            return WorkflowResult(
                success=True,
                final_data=self.state,
                execution_trace=self._build_trace(),
                performance_metrics=self._calculate_metrics()
            )
            
        except Exception as e:
            return WorkflowResult(success=False, error=str(e))
            
    def _execute_node_with_recovery(self, node_id: str) -> ToolResult:
        """Execute node with checkpoint and recovery support"""
        node = self.nodes[node_id]
        
        # Create checkpoint before execution
        checkpoint = self._create_checkpoint(node_id)
        
        try:
            # Gather inputs from dependent nodes
            inputs = self._gather_inputs(node_id)
            
            # Execute the operation
            tool = self._get_tool(node['operation'])
            result = tool.execute(ToolRequest(data=inputs, parameters=node['parameters']))
            
            # Store result and update state
            self.state[node_id] = result
            node['status'] = 'completed' if result.success else 'failed'
            
            return result
            
        except Exception as e:
            # Attempt recovery from checkpoint
            self._restore_checkpoint(checkpoint)
            node['status'] = 'failed'
            return ToolResult(success=False, error=str(e))
```

### **Execution Patterns**

#### **Sequential Execution**
```python
def create_sequential_workflow(operations: List[str]) -> WorkflowDAG:
    """Create linear dependency chain"""
    dag = WorkflowDAG()
    
    for i, operation in enumerate(operations):
        dag.add_node(f"step_{i}", operation, {})
        if i > 0:
            dag.add_edge(f"step_{i-1}", f"step_{i}", {'type': 'direct'})
    
    return dag
```

#### **Parallel Execution**  
```python
def create_parallel_workflow(operations: List[str], aggregator: str) -> WorkflowDAG:
    """Create parallel processing with aggregation"""
    dag = WorkflowDAG()
    
    # Parallel operations
    for i, operation in enumerate(operations):
        dag.add_node(f"parallel_{i}", operation, {})
    
    # Aggregation step
    dag.add_node("aggregator", aggregator, {})
    for i in range(len(operations)):
        dag.add_edge(f"parallel_{i}", "aggregator", {'type': 'collect'})
        
    return dag
```

#### **Conditional Branching**
```python
def create_conditional_workflow(condition_tool: str, branches: Dict) -> WorkflowDAG:
    """Create theory-based decision points"""
    dag = WorkflowDAG()
    
    dag.add_node("condition", condition_tool, {})
    
    for condition_value, operations in branches.items():
        branch_dag = create_sequential_workflow(operations)
        dag.merge_conditional_branch(condition_value, branch_dag)
        
    return dag
```

### **Automatic DAG Generation**
```python
class AutoDAGGenerator:
    """Generate workflows from research questions and theory selection"""
    
    def generate_from_question(self, question: str, theory: str) -> WorkflowDAG:
        """Generate analytical workflow from research question"""
        
        # 1. Parse research question for analytical goals
        goals = self.question_parser.extract_goals(question)
        
        # 2. Match relevant theoretical framework
        theory_schema = self.theory_repository.get_schema(theory)
        
        # 3. Select appropriate analysis operations  
        operations = self.operation_selector.select_for_goals(goals, theory_schema)
        
        # 4. Resolve execution dependencies
        dependencies = self.dependency_resolver.build_graph(operations)
        
        # 5. Generate parameterized workflow
        dag = self.workflow_builder.build_dag(operations, dependencies)
        
        return dag
```

---

## 🗄️ **DATA STORAGE ARCHITECTURE**

### **Neo4j Schema for KGAS**
```cypher
// Theory Schemas
CREATE CONSTRAINT theory_id FOR (t:Theory) REQUIRE t.theory_id IS UNIQUE;

(:Theory {
    theory_id: string,
    name: string,
    authors: [string],
    publication_year: integer,
    schema_version: string,
    extraction_date: datetime
})-[:HAS_ENTITY]->(:TheoryEntity {
    entity_id: string,
    name: string,
    definition: string,
    properties: map
})

(:Theory)-[:HAS_RELATION]->(:TheoryRelation {
    relation_id: string,
    name: string,
    type: string,
    strength: string,
    conditions: [string]
})

(:Theory)-[:HAS_ALGORITHM]->(:TheoryAlgorithm {
    algorithm_id: string,
    name: string,
    type: string, // mathematical, logical, procedural
    formula: string,
    parameters: map,
    implementation: string
})

// Generated Tools  
(:GeneratedTool {
    tool_id: string,
    theory_source: string,
    generated_code: string,
    compilation_status: string,
    performance_metrics: map
})-[:IMPLEMENTS]->(:TheoryAlgorithm)

// Knowledge Graphs (Analysis Results)
(:Entity {
    entity_id: string,
    canonical_name: string,
    entity_type: string,
    theory_context: string,
    confidence: float,
    embedding: vector[384]
})-[:RELATIONSHIP]->(:Entity)

// Workflow Execution
(:WorkflowExecution {
    workflow_id: string,
    research_question: string,
    theory_used: string,
    execution_time: datetime,
    status: string,
    performance_metrics: map
})-[:EXECUTED_STEP]->(:StepExecution {
    step_id: string,
    tool_used: string,
    inputs: map,
    outputs: map,
    uncertainty: float,
    execution_duration: duration
})
```

### **SQLite Schema for Analysis Results**
```sql
-- Workflow Management
CREATE TABLE workflow_executions (
    workflow_id TEXT PRIMARY KEY,
    research_question TEXT NOT NULL,
    theory_used TEXT,
    dag_structure JSON,
    execution_status TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_duration INTEGER,
    final_results JSON
);

CREATE TABLE step_executions (
    step_id TEXT PRIMARY KEY,
    workflow_id TEXT REFERENCES workflow_executions(workflow_id),
    tool_used TEXT,
    step_order INTEGER,
    inputs JSON,
    outputs JSON,
    uncertainty REAL,
    reasoning TEXT,
    execution_duration INTEGER,
    status TEXT
);

-- Theory Management
CREATE TABLE theory_schemas (
    theory_id TEXT PRIMARY KEY,
    theory_name TEXT,
    authors TEXT,
    extraction_date TIMESTAMP,
    schema_json JSON,
    validation_status TEXT,
    generated_tools_count INTEGER
);

CREATE TABLE generated_tools (
    tool_id TEXT PRIMARY KEY,
    theory_id TEXT REFERENCES theory_schemas(theory_id),
    tool_name TEXT,
    algorithm_type TEXT,
    generated_code TEXT,
    compilation_status TEXT,
    usage_count INTEGER,
    average_execution_time REAL
);

-- Analysis Results Storage
CREATE TABLE statistical_results (
    result_id TEXT PRIMARY KEY,
    workflow_id TEXT REFERENCES workflow_executions(workflow_id),
    analysis_type TEXT,
    variables JSON,
    statistics JSON,
    p_values JSON,
    effect_sizes JSON,
    confidence_intervals JSON,
    interpretation TEXT
);

CREATE TABLE network_metrics (
    metric_id TEXT PRIMARY KEY,
    workflow_id TEXT REFERENCES workflow_executions(workflow_id),
    network_type TEXT,
    node_count INTEGER,
    edge_count INTEGER,
    density REAL,
    centrality_measures JSON,
    community_structure JSON,
    clustering_coefficient REAL
);

CREATE TABLE embeddings_analysis (
    embedding_id TEXT PRIMARY KEY,
    workflow_id TEXT REFERENCES workflow_executions(workflow_id),
    embedding_model TEXT,
    dimensionality INTEGER,
    similarity_matrix JSON,
    cluster_assignments JSON,
    explained_variance REAL
);
```

---

## 🔐 **SYSTEM INTEGRATION PATTERNS**

### **Tool Registration and Discovery**
```python
class KGASToolRegistry:
    """Manages both static and dynamically generated tools"""
    
    def __init__(self):
        self.static_tools = {}      # Pre-built tools
        self.generated_tools = {}   # LLM-generated tools  
        self.tool_cache = {}        # Compiled tool cache
        self.usage_metrics = {}     # Performance tracking
        
    def register_generated_tool(self, theory_id: str, algorithm: Dict, generated_code: str):
        """Register dynamically generated tool"""
        tool_id = f"GENERATED_{theory_id}_{algorithm['name'].upper()}"
        
        # Compile and validate generated code
        compiled_tool = self._compile_tool_code(generated_code)
        validation_result = self._validate_tool_interface(compiled_tool)
        
        if validation_result.success:
            self.generated_tools[tool_id] = {
                'theory_source': theory_id,
                'algorithm': algorithm,
                'compiled_tool': compiled_tool,
                'generation_timestamp': datetime.now(),
                'usage_count': 0
            }
            self.tool_cache[tool_id] = compiled_tool
            
        return ValidationResult(success=validation_result.success, tool_id=tool_id)
        
    def discover_tools_for_theory(self, theory_schema: Dict) -> List[str]:
        """Find all applicable tools for a theory"""
        applicable_tools = []
        
        # Check static tools with theory compatibility
        for tool_id, tool in self.static_tools.items():
            if self._is_theory_compatible(tool, theory_schema):
                applicable_tools.append(tool_id)
                
        # Check generated tools from same theory
        for tool_id, tool_info in self.generated_tools.items():
            if tool_info['theory_source'] == theory_schema['metadata']['theory_name']:
                applicable_tools.append(tool_id)
                
        return applicable_tools
```

### **Cross-Modal Analysis Orchestration**
```python
class CrossModalOrchestrator:
    """Coordinates analysis across Graph, Table, and Vector representations"""
    
    def __init__(self, tool_registry, converter_suite):
        self.tools = tool_registry
        self.converters = converter_suite
        self.analysis_history = []
        
    def orchestrate_multimodal_analysis(self, 
                                      data: Any, 
                                      analysis_goals: List[str],
                                      theory_schema: Dict) -> MultiModalResult:
        """Execute analysis across optimal data representations"""
        
        results = {}
        
        for goal in analysis_goals:
            # Determine optimal representation for this goal
            optimal_format = self._determine_optimal_format(goal, theory_schema)
            
            # Convert data to optimal format if needed
            formatted_data = self._ensure_format(data, optimal_format)
            
            # Select and execute appropriate tools
            tools = self._select_tools_for_goal(goal, optimal_format, theory_schema)
            goal_results = []
            
            for tool_id in tools:
                tool = self.tools.get_tool(tool_id)
                result = tool.execute(ToolRequest(data=formatted_data))
                goal_results.append(result)
                
            results[goal] = goal_results
            
        # Aggregate cross-modal results
        aggregated_results = self._aggregate_multimodal_results(results)
        
        return MultiModalResult(
            results=aggregated_results,
            formats_used=list(set(self._get_formats_used(results))),
            conversion_trace=self._build_conversion_trace(),
            cross_modal_consistency=self._assess_consistency(results)
        )
        
    def _determine_optimal_format(self, goal: str, theory_schema: Dict) -> str:
        """Determine best data representation for analysis goal"""
        format_preferences = {
            'centrality_analysis': 'graph',
            'community_detection': 'graph',
            'path_analysis': 'graph',
            'correlation_analysis': 'table', 
            'regression_modeling': 'table',
            'statistical_testing': 'table',
            'similarity_search': 'vector',
            'clustering_analysis': 'vector',
            'semantic_analysis': 'vector'
        }
        
        return format_preferences.get(goal, 'graph')  # Default to graph
```

---

## 📈 **EVOLUTION PATH FROM VERTICAL SLICE**

### **Phase 1: Current Vertical Slice** 
```
TextLoader → KnowledgeGraphExtractor → GraphPersister
(3 static tools, basic cross-modal, simple uncertainty)
```

### **Phase 2: Tool Suite Expansion**
```
Vertical Slice + Statistical Analysis Suite + Vector Operations Suite
(~15 static tools, enhanced cross-modal conversion)
```

### **Phase 3: Theory Integration** 
```
Tool Suites + Theory Meta-Schema + Basic Theory Extraction
(static tools + theory-guided analysis)
```

### **Phase 4: Dynamic Tool Generation**
```
Full System + LLM Tool Generation + WorkflowDAG
(dynamic tools generated from theory schemas)
```

### **Phase 5: Advanced Orchestration**
```
Complete KGAS + Agent-Based Modeling + Advanced Analytics
(autonomous theory-driven research system)
```

---

## ⚡ **PERFORMANCE & SCALABILITY CONSIDERATIONS**

### **Tool Generation Performance**
- **Code Generation Caching**: Cache generated tools by theory algorithm hash
- **Compilation Optimization**: Pre-compile common algorithm patterns  
- **Runtime Efficiency**: Generated tools should match static tool performance
- **Memory Management**: Unload unused generated tools, lazy loading

### **Workflow Execution Scaling**
- **Parallel Execution**: Independent DAG branches execute concurrently
- **Checkpoint Recovery**: Resume long workflows from intermediate states
- **Resource Management**: Monitor memory/CPU usage, implement resource limits
- **Streaming Results**: Process large datasets in chunks

### **Data Storage Optimization**
- **Neo4j Performance**: Proper indexing on theory_id, entity_id, workflow_id
- **SQLite Optimization**: Partitioned tables for large analysis results
- **Caching Strategy**: Redis cache for frequently accessed theory schemas
- **Archive Management**: Automated cleanup of old workflow executions

---

## 🛡️ **SYSTEM RELIABILITY & VALIDATION**

### **Generated Tool Validation**
```python
class GeneratedToolValidator:
    """Validates LLM-generated tools for safety and correctness"""
    
    def validate_tool(self, generated_code: str, algorithm_spec: Dict) -> ValidationResult:
        """Multi-layer validation of generated tool code"""
        
        # 1. Syntax validation
        syntax_result = self._validate_syntax(generated_code)
        if not syntax_result.valid:
            return ValidationResult(False, "Syntax error: " + syntax_result.error)
            
        # 2. Interface compliance  
        interface_result = self._validate_interface(generated_code)
        if not interface_result.valid:
            return ValidationResult(False, "Interface error: " + interface_result.error)
            
        # 3. Algorithm correctness
        algorithm_result = self._validate_algorithm(generated_code, algorithm_spec)
        if not algorithm_result.valid:
            return ValidationResult(False, "Algorithm error: " + algorithm_result.error)
            
        # 4. Security validation
        security_result = self._validate_security(generated_code)
        if not security_result.valid:
            return ValidationResult(False, "Security error: " + security_result.error)
            
        # 5. Performance testing
        performance_result = self._test_performance(generated_code)
        
        return ValidationResult(
            valid=True,
            performance_metrics=performance_result.metrics,
            validation_timestamp=datetime.now()
        )
```

### **Theory Schema Validation**
- **Schema Compliance**: Validate against theory meta-schema specification
- **Logical Consistency**: Check for contradictory theoretical relationships  
- **Completeness**: Ensure required components (entities, relations, algorithms)
- **Academic Validity**: Cross-reference with known theory databases

### **Workflow Integrity**
- **DAG Validation**: Ensure acyclic nature, detect circular dependencies
- **Data Flow Validation**: Type checking between tool inputs/outputs
- **Resource Limits**: Prevent infinite loops, memory exhaustion
- **Failure Recovery**: Graceful handling of tool execution failures

---

**Status**: This document captures the complete KGAS architecture extracted from proposal planning materials. It represents the target system that the current vertical slice will evolve toward through systematic implementation phases.

**Next Steps**: Implementation proceeds through the defined evolution path, starting with current vertical slice completion before advancing to tool suite expansion and dynamic generation capabilities.