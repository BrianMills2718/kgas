# Tool Compatibility and DAG System Plan

## Executive Summary

We're implementing a **type-based transformation matrix** for the KGAS tool system that enables flexible DAG (Directed Acyclic Graph) composition for analytical workflows. This replaces the hardcoded tool chains with a dynamic system where tools declare data type transformations and the LLM intelligently composes workflows.

**Key Achievement**: Moving from 5 hardcoded tool chains to a dynamic system supporting 300+ possible execution paths.

## Core Problem

The current system (`src/core/tool_compatibility_real.py`) hardcodes only 5 tools, preventing flexible tool composition. We need a system where:
1. Tools can be modularly chained in DAGs
2. The LLM can intelligently plan tool sequences
3. No mocks, fallbacks, or graceful degradation
4. Tools work with Neo4j and SQLite databases

## Solution: Type-Based Transformation Matrix

### Core Concept

Tools are **data type transformers**. Each tool transforms data from one type to another:

```python
T23C: RAW_TEXT ’ EXTRACTED_DATA
T31: EXTRACTED_DATA ’ GRAPH_STRUCTURE  
T68: GRAPH_STRUCTURE ’ ENRICHED_GRAPH
```

The system automatically discovers all valid paths through these transformations.

## Implementation Plan

### Phase 1: Data Type System (Day 1)

#### 1.1 Define Complete DataType Enum

```python
class DataType(Enum):
    # Input types
    RAW_TEXT = "raw_text"
    FILE_PATH = "file_path"
    
    # Extraction outputs
    EXTRACTED_DATA = "extracted_data"      # Entities + relationships + properties
    ENTITY_DATA = "entity_data"            # Just entities
    CHUNKED_TEXT = "chunked_text"          # Text chunks
    
    # Graph types
    GRAPH_NODES = "graph_nodes"            # Entity nodes
    GRAPH_STRUCTURE = "graph_structure"    # Full graph with edges
    ENRICHED_GRAPH = "enriched_graph"      # Graph with metrics
    COMMUNITIES = "communities"             # Community detection results
    
    # Database types
    NEO4J_TRANSACTION = "neo4j_transaction"
    SQLITE_RECORDS = "sqlite_records"
    
    # Analysis types
    QUERY_RESULTS = "query_results"
    ANALYSIS_RESULTS = "analysis_results"
    METRICS = "metrics"
    
    # Output types
    TABLE_DATA = "table_data"
    VECTOR_EMBEDDINGS = "vector_embeddings"
    VISUAL_OUTPUT = "visual_output"
    
    # Theory-specific types (added dynamically)
    THEORY_GUIDED_DATA = "theory_guided_data"
    MCR_SCORES = "mcr_scores"  # Self-Categorization Theory specific
```

#### 1.2 Handle T23C Multiple Modes

T23C is our primary extraction tool but has multiple modes:

```python
class T23CMode(Enum):
    ENTITY_ONLY = "entity_only"            # Output: ENTITY_DATA
    ENTITY_RELATION = "entity_relation"    # Output: EXTRACTED_DATA (no properties)
    FULL_EXTRACTION = "full_extraction"    # Output: EXTRACTED_DATA (complete)
    THEORY_GUIDED = "theory_guided"        # Output: THEORY_GUIDED_DATA

# Solution: Parameterized transformations
class ParameterizedTransformation:
    tool_id: str = "T23C"
    input_type: DataType = RAW_TEXT
    output_type: DataType  # Depends on mode parameter
    parameters: Dict[str, Any] = {"mode": "full_extraction"}
```

### Phase 2: Tool Transformation Matrix (Day 2)

#### 2.1 Map All 35 Active Tools

```python
# Core KGAS Tools (Active, excluding deprecated)
TOOL_TRANSFORMATIONS = {
    # Document loaders (T01-T14)
    "T01_PDF_LOADER": (FILE_PATH, RAW_TEXT),
    "T02_WORD_LOADER": (FILE_PATH, RAW_TEXT),
    "T03_TXT_LOADER": (FILE_PATH, RAW_TEXT),
    "T05_CSV_LOADER": (FILE_PATH, TABLE_DATA),
    "T06_JSON_LOADER": (FILE_PATH, EXTRACTED_DATA),
    
    # Text processing (T15)
    "T15A_TEXT_CHUNKER": (RAW_TEXT, CHUNKED_TEXT),
    "T15B_VECTOR_EMBEDDER": (RAW_TEXT, VECTOR_EMBEDDINGS),
    
    # Extraction (T23C replaces T23A and T27)
    "T23C_ONTOLOGY_AWARE": [
        (RAW_TEXT, ENTITY_DATA),        # mode=entity_only
        (RAW_TEXT, EXTRACTED_DATA),     # mode=full_extraction
        (RAW_TEXT, THEORY_GUIDED_DATA), # mode=theory_guided
    ],
    # DEPRECATED: "T23A_SPACY_NER"
    # DEPRECATED: "T27_RELATIONSHIP"
    
    # Graph building (T31, T34)
    "T31_ENTITY_BUILDER": (EXTRACTED_DATA, GRAPH_NODES),
    "T34_EDGE_BUILDER": (GRAPH_NODES, GRAPH_STRUCTURE),
    
    # Graph analytics (T49-T69)
    "T49_MULTIHOP_QUERY": (GRAPH_STRUCTURE, QUERY_RESULTS),
    "T68_PAGERANK": (GRAPH_STRUCTURE, ENRICHED_GRAPH),
    "T69_COMMUNITY_DETECTION": (GRAPH_STRUCTURE, COMMUNITIES),
    
    # Phase 2 tools (T50-T60)
    "T50_COMMUNITY_DETECTION": (GRAPH_STRUCTURE, COMMUNITIES),
    "T51_CENTRALITY_ANALYSIS": (GRAPH_STRUCTURE, METRICS),
    "T52_GRAPH_CLUSTERING": (GRAPH_STRUCTURE, COMMUNITIES),
    "T53_NETWORK_MOTIFS": (GRAPH_STRUCTURE, ANALYSIS_RESULTS),
    "T54_GRAPH_VISUALIZATION": (GRAPH_STRUCTURE, VISUAL_OUTPUT),
    "T55_TEMPORAL_ANALYSIS": (GRAPH_STRUCTURE, ANALYSIS_RESULTS),
    "T56_GRAPH_METRICS": (GRAPH_STRUCTURE, METRICS),
    "T57_PATH_ANALYSIS": (GRAPH_STRUCTURE, ANALYSIS_RESULTS),
    "T58_GRAPH_COMPARISON": (GRAPH_STRUCTURE, ANALYSIS_RESULTS),
    "T59_SCALE_FREE_ANALYSIS": (GRAPH_STRUCTURE, ANALYSIS_RESULTS),
    "T60_GRAPH_EXPORT": (GRAPH_STRUCTURE, TABLE_DATA),
    
    # Cross-modal tools
    "GRAPH_TABLE_EXPORTER": (GRAPH_STRUCTURE, TABLE_DATA),
    "CROSS_MODAL_ANALYZER": (MULTI_MODAL_DATA, SYNTHESIS),
    "VECTOR_EMBEDDER": (RAW_TEXT, VECTOR_EMBEDDINGS),
    "MULTI_FORMAT_EXPORTER": [
        (GRAPH_STRUCTURE, TABLE_DATA),
        (GRAPH_STRUCTURE, VISUAL_OUTPUT),
        (TABLE_DATA, VECTOR_EMBEDDINGS),
    ],
    
    # Database operations
    "NEO4J_WRITER": (GRAPH_STRUCTURE, NEO4J_TRANSACTION),
    "SQLITE_WRITER": (TABLE_DATA, SQLITE_RECORDS),
    
    # Output tools
    "T91_TABLE_FORMATTER": (ENRICHED_GRAPH, TABLE_DATA),
    "T92_VISUALIZATION": (GRAPH_STRUCTURE, VISUAL_OUTPUT),
}
```

#### 2.2 Build Transformation Matrix

```python
class TransformationMatrix:
    def __init__(self):
        self.transformations = self._load_tool_transformations()
        self.graph = self._build_transformation_graph()
    
    def find_all_paths(self, start_type: DataType, end_type: DataType) -> List[List[str]]:
        """Find all valid tool chains from start to end type"""
        # Use graph pathfinding (BFS/DFS)
        return self._find_paths_in_graph(start_type, end_type)
    
    def find_shortest_path(self, start_type: DataType, end_type: DataType) -> List[str]:
        """Find the most efficient tool chain"""
        # Dijkstra's algorithm with tool costs
        return self._dijkstra(start_type, end_type)
    
    def validate_chain(self, tool_chain: List[str]) -> bool:
        """Validate that a tool chain has compatible types"""
        for i in range(len(tool_chain) - 1):
            current_output = self.get_output_type(tool_chain[i])
            next_input = self.get_input_type(tool_chain[i+1])
            if current_output != next_input:
                return False
        return True
```

### Phase 3: Parameter Flow System (Day 3)

#### 3.1 Parameter Propagation

```python
class DAGNode:
    tool_id: str
    input_type: DataType
    output_type: DataType
    parameters: Dict[str, Any]
    
    def get_output_reference(self) -> str:
        """Return reference for downstream tools"""
        return f"${self.node_id}.output"

class DAGExecutor:
    def execute_dag(self, dag: List[DAGNode]) -> Dict[str, Any]:
        """Execute DAG with parameter and data flow"""
        results = {}
        
        for node in dag:
            # Resolve input references
            input_data = self._resolve_references(node.input_data, results)
            
            # Execute tool with parameters
            tool = self.get_tool(node.tool_id)
            result = tool.execute(input_data, node.parameters)
            
            # Store result for downstream tools
            results[node.node_id] = result
            
        return results
    
    def _resolve_references(self, input_spec: Any, results: Dict) -> Any:
        """Resolve $node_id.field references"""
        if isinstance(input_spec, str) and input_spec.startswith("$"):
            parts = input_spec[1:].split(".")
            node_id, field = parts[0], parts[1]
            return results[node_id][field]
        return input_spec
```

#### 3.2 Parameter Compatibility

```python
class ParameterCompatibility:
    """Ensure parameters flow correctly between tools"""
    
    def validate_parameter_flow(self, source_tool: str, target_tool: str, params: Dict) -> bool:
        """Check if parameters from source work with target"""
        
        # Example: T23C mode affects what T31 can process
        if source_tool == "T23C" and target_tool == "T31":
            t23c_mode = params.get("mode", "full_extraction")
            if t23c_mode == "entity_only":
                # T31 needs relationships, won't work with entity_only
                return False
        
        return True
```

### Phase 4: LLM DAG Planning (Day 4)

#### 4.1 Tool Capability Descriptions

```python
class ToolCapability:
    tool_id: str
    human_description: str
    transformations: List[Tuple[DataType, DataType]]
    parameter_schema: Dict[str, Any]
    performance_hints: Dict[str, Any]
    theory_compatibility: List[str]
    
    def to_llm_prompt(self) -> str:
        """Generate description for LLM understanding"""
        return f"""
        Tool: {self.tool_id}
        Purpose: {self.human_description}
        Input: {self.transformations[0][0].value}
        Output: {self.transformations[0][1].value}
        Parameters: {json.dumps(self.parameter_schema, indent=2)}
        Performance: {self.performance_hints.get('speed', 'normal')}
        """

# Example capabilities
TOOL_CAPABILITIES = {
    "T23C": ToolCapability(
        tool_id="T23C_ONTOLOGY_AWARE",
        human_description="Extracts entities, relationships, and properties from text using LLM",
        transformations=[
            (RAW_TEXT, ENTITY_DATA),
            (RAW_TEXT, EXTRACTED_DATA),
            (RAW_TEXT, THEORY_GUIDED_DATA)
        ],
        parameter_schema={
            "mode": {
                "type": "string",
                "enum": ["entity_only", "full_extraction", "theory_guided"],
                "default": "full_extraction"
            },
            "confidence_threshold": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.8
            },
            "theory_schema": {
                "type": "string",
                "description": "Path to theory schema file (for theory_guided mode)"
            }
        },
        performance_hints={
            "speed": "slow",  # LLM call
            "cost": "high",   # Uses tokens
            "quality": "high", # Frontier model
            "batch_capable": False
        },
        theory_compatibility=["SCT", "SIT", "DOLCE", "generic"]
    ),
    
    "T31": ToolCapability(
        tool_id="T31_ENTITY_BUILDER",
        human_description="Builds graph nodes from extracted entities",
        transformations=[(EXTRACTED_DATA, GRAPH_NODES)],
        parameter_schema={
            "merge_strategy": {
                "type": "string",
                "enum": ["strict", "fuzzy", "contextual"],
                "default": "fuzzy"
            }
        },
        performance_hints={
            "speed": "fast",
            "cost": "low",
            "quality": "high",
            "batch_capable": True
        },
        theory_compatibility=["all"]
    )
}
```

#### 4.2 LLM DAG Planning Interface

```python
class LLMDAGPlanner:
    def __init__(self, transformation_matrix: TransformationMatrix):
        self.matrix = transformation_matrix
        self.capabilities = TOOL_CAPABILITIES
    
    def plan_dag(self, user_request: str) -> DAG:
        """Use LLM to plan DAG from natural language request"""
        
        # Step 1: Extract intent and requirements
        analysis = self._analyze_request(user_request)
        # Returns: {
        #     "goal": "extract SCT patterns",
        #     "input_type": "PDF document",
        #     "output_type": "theory analysis",
        #     "theory": "self_categorization_theory"
        # }
        
        # Step 2: Determine data types
        start_type = self._map_to_data_type(analysis["input_type"])  # FILE_PATH
        end_type = self._map_to_data_type(analysis["output_type"])   # ANALYSIS_RESULTS
        
        # Step 3: Find possible paths
        all_paths = self.matrix.find_all_paths(start_type, end_type)
        
        # Step 4: Let LLM choose best path
        prompt = self._build_path_selection_prompt(
            user_request, 
            analysis, 
            all_paths[:10]  # Top 10 paths
        )
        
        selected_path = self._llm_select_path(prompt)
        
        # Step 5: Add parameters for each tool
        dag = self._build_dag_with_parameters(selected_path, analysis)
        
        return dag
    
    def _build_path_selection_prompt(self, request: str, analysis: Dict, paths: List) -> str:
        """Build prompt for LLM to select best path"""
        
        prompt = f"""
        User Request: {request}
        
        Analysis:
        - Goal: {analysis['goal']}
        - Input: {analysis['input_type']}
        - Output: {analysis['output_type']}
        - Theory: {analysis.get('theory', 'none')}
        
        Available Tool Paths:
        """
        
        for i, path in enumerate(paths):
            prompt += f"\nPath {i+1}:\n"
            for tool_id in path:
                cap = self.capabilities.get(tool_id)
                if cap:
                    prompt += f"  ’ {tool_id}: {cap.human_description}\n"
                    prompt += f"    Speed: {cap.performance_hints['speed']}, "
                    prompt += f"Quality: {cap.performance_hints['quality']}\n"
        
        prompt += """
        Select the best path considering:
        1. Completeness - does it achieve the goal?
        2. Efficiency - minimize unnecessary steps
        3. Quality - use high-quality tools for critical steps
        4. Theory compatibility - if theory-specific, use compatible tools
        
        Return the path number (1-10) and explain why.
        """
        
        return prompt
```

### Phase 5: Theory-Specific Tool Integration (Week 2)

#### 5.1 Dynamic Theory Tool Registration

```python
class TheoryToolFactory:
    """Create theory-specific tool variants on demand"""
    
    def create_theory_tool(self, base_tool: str, theory: str) -> ToolCapability:
        """Create specialized version of tool for theory"""
        
        base_capability = TOOL_CAPABILITIES[base_tool]
        
        # Example: Create SCT-specific MCR calculator
        if theory == "SCT" and base_tool == "T51_CENTRALITY":
            return ToolCapability(
                tool_id="T51_MCR_CALCULATOR",
                human_description="Calculate Meta-Contrast Ratio for Self-Categorization Theory",
                transformations=[(SCT_DATA, MCR_SCORES)],
                parameter_schema={
                    "distance_metric": {
                        "type": "string",
                        "enum": ["cosine", "euclidean"],
                        "default": "cosine"
                    }
                },
                performance_hints=base_capability.performance_hints,
                theory_compatibility=["SCT"]
            )
        
        # Default: Add theory context to base tool
        theory_capability = copy.deepcopy(base_capability)
        theory_capability.tool_id = f"{base_tool}_{theory}"
        theory_capability.parameter_schema["theory_context"] = {
            "type": "object",
            "description": f"Theory-specific context for {theory}"
        }
        
        return theory_capability
    
    def register_theory_tools(self, theory: str, required_tools: List[str]):
        """Register all tools needed for a theory"""
        
        for tool in required_tools:
            theory_tool = self.create_theory_tool(tool, theory)
            self.matrix.register_tool(theory_tool)
```

#### 5.2 Theory-Aware DAG Planning

```python
class TheoryAwareDAGPlanner(LLMDAGPlanner):
    """Extend DAG planner with theory-specific logic"""
    
    def plan_theory_dag(self, theory: str, data_source: str) -> DAG:
        """Plan DAG for theory-specific analysis"""
        
        # Load theory requirements
        theory_spec = self.load_theory_specification(theory)
        
        # Register theory-specific tools
        self.theory_factory.register_theory_tools(
            theory, 
            theory_spec["required_tools"]
        )
        
        # Build theory-aware prompt
        prompt = f"""
        Analyze {data_source} using {theory} theory.
        
        Theory Requirements:
        - Core concepts: {theory_spec['concepts']}
        - Key measures: {theory_spec['measures']}
        - Required analyses: {theory_spec['analyses']}
        
        Available theory-specific tools:
        {self._list_theory_tools(theory)}
        
        Build a DAG that:
        1. Extracts theory-relevant entities and relationships
        2. Calculates theory-specific measures
        3. Performs required analyses
        4. Synthesizes findings according to theory
        """
        
        return self.plan_dag(prompt)
```

## Implementation Timeline

### Week 1: Core System
- **Day 1**: Define DataType enum and handle T23C modes
- **Day 2**: Build transformation matrix for 35 active tools
- **Day 3**: Implement parameter flow system
- **Day 4**: Create LLM DAG planning interface

### Week 2: Integration & Testing
- **Days 5-6**: Integrate with existing KGAS infrastructure
- **Days 7-8**: Add theory-specific tool support
- **Days 9-10**: Comprehensive testing and validation

## Deprecation Plan

### Tools to Deprecate
1. **T23A (SpaCy NER)**:  DEPRECATED - Added warnings and documentation
   - Replaced by T23C's superior LLM extraction
   - Backwards compatibility maintained

2. **T27 (Relationship Extractor)**:  DEPRECATED - Added warnings and documentation
   - Replaced by T23C's integrated extraction
   - Backwards compatibility maintained

### Migration Path
```python
# Old pipeline
T23A ’ T27 ’ T31 ’ T34

# New pipeline  
T23C (mode=full_extraction) ’ T31 ’ T34

# Benefits:
# - Single LLM call instead of multiple tools
# - Better context understanding
# - Entities + relationships + properties together
```

## Critical Considerations

### 1. Data Type Granularity
- T23C has multiple modes producing different outputs
- Solution: Parameterized transformations with mode-specific outputs

### 2. Parameter Compatibility
- Not all parameter combinations are valid
- Solution: Parameter compatibility validation layer

### 3. LLM Planning Complexity
- LLM needs to understand tool capabilities and choose wisely
- Solution: Rich tool descriptions and guided prompts

### 4. Theory-Specific Tools
- Some analyses require specialized tools created on demand
- Solution: Dynamic tool registration based on theory requirements

### 5. Performance vs Flexibility
- More paths = more complexity for LLM
- Solution: Heuristics to prune unlikely paths, keep top 10-20 options

## Success Criteria

1. **No Hardcoded Chains**: All tool sequences discovered dynamically
2. **LLM Planning**: Natural language ’ DAG generation working
3. **Parameter Flow**: Parameters correctly propagate through DAG
4. **Theory Support**: Theory-specific tools integrate seamlessly
5. **Performance**: DAG planning < 2 seconds for typical requests

## Next Steps

1. **Immediate**: Implement DataType enum with all KGAS data types
2. **Day 1**: Map all 35 active tools to transformations
3. **Day 2**: Build transformation matrix and pathfinding
4. **Day 3**: Add parameter flow system
5. **Day 4**: Create LLM planning interface
6. **Week 2**: Full integration and testing

## References

- Original investigation: `/home/brian/projects/Digimons/docs/architecture/architecture_review_20250808/tool_compatibility_investigation.md`
- Type-based solution: `/home/brian/projects/Digimons/experiments/tool_compatability/TYPE_BASED_SOLUTION.md`
- Full DAG example: `/home/brian/projects/Digimons/docs/architecture/proposal_rewrite/full_example/full_example_ascii_dag_UPDATED.txt`
- Current tools: 35 active generic tools (T01-T302 with gaps)
- Deprecated: T23A (SpaCy NER), T27 (Relationship Extractor)