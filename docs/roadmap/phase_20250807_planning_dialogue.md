  🎯 THE CORE VISION: Composable Tool Ecosystem

  What You Want (And What KGAS Should Be)

  # Agent dynamically creates novel DAG for specific analysis
  User: "Compare sentiment evolution across these documents using graph centrality weighted by temporal decay"

  Agent creates:
  T01 → T15A → T23C → T31 → T68 → Custom_Temporal_Weighting → T91 → Sentiment_Analysis → Cross_Modal_Synthesis
        ↘                                                      ↗
         T15B → Vector_Embeddings → Temporal_Clustering ——————↗

  This requires:
  1. Tools that actually compose (outputs match next tool's inputs)
  2. Flexible data transformation (automatic field mapping)
  3. Dynamic pipeline creation (agent can innovate, not just follow templates)

  🔍 CURRENT BLOCKING ISSUES

  1. Rigid Field Names

  # Current problem:
  T01 outputs: {"content": "text", "file_path": "doc.txt"}
  T23C expects: {"text": "text", "chunk_ref": "ref"}
  # FAILS - field names don't match!

  2. Missing Data Transformation Layer

  # What we need:
  class DataTransformer:
      def transform(self, source_output: Dict, target_input_schema: Dict) -> Dict:
          """Intelligently map fields between tools"""
          # Smart mapping: content → text, file_path → chunk_ref
          # Type conversion: string → list, int → float
          # Structure adaptation: flat → nested, single → array

  3. Tools Aren't Truly Modular

  # Current: Tools assume specific predecessors
  class T31EntityBuilder:
      def execute(self, request):
          # Assumes T23C output format specifically!
          entities = request.input_data["entities"]  # Breaks if different tool provides entities

  📋 SOLUTION: Smart Tool Composition Framework

  Phase D.12 Enhanced: Intelligent Tool Composition

  1. Universal Tool Output Format

  @dataclass
  class ToolOutput:
      """Standardized output all tools produce"""
      primary_data: Any  # The main output (text, entities, graph, etc.)
      metadata: Dict[str, Any]  # Source info, confidence, etc.
      data_type: str  # "text", "entities", "graph", "table", "vectors"
      schema: Dict  # JSON schema describing primary_data structure

      def to_dict(self) -> Dict:
          """Convert to dict for next tool"""
          return {
              "data": self.primary_data,
              "metadata": self.metadata,
              "type": self.data_type,
              "schema": self.schema
          }

  2. Intelligent Input Adapter

  class ToolInputAdapter:
      """Automatically adapt any output to any input"""

      def adapt(self, 
                source_output: ToolOutput, 
                target_tool: KGASTool) -> Dict:
          """
          Smart adaptation between tools
          """
          target_schema = target_tool.get_input_schema()

          # 1. Check if types are compatible
          if not self._types_compatible(source_output.data_type, target_schema):
              raise IncompatibleToolsError(
                  f"Cannot connect {source_output.data_type} to {target_tool.tool_id}"
              )

          # 2. Map fields intelligently
          mapped_data = self._map_fields(
              source_output.primary_data,
              target_schema
          )

          # 3. Add required metadata
          if "chunk_ref" in target_schema.get("required", []):
              mapped_data["chunk_ref"] = source_output.metadata.get(
                  "source_ref",
                  f"auto_{uuid.uuid4()}"
              )

          return mapped_data

      def _map_fields(self, source_data: Any, target_schema: Dict) -> Dict:
          """Intelligent field mapping using multiple strategies"""

          # Strategy 1: Direct name match
          # Strategy 2: Semantic similarity (text → content → document)
          # Strategy 3: Type-based inference (only string field → must be text input)
          # Strategy 4: LLM-assisted mapping for complex cases

          mapper = FieldMapper()
          return mapper.map(source_data, target_schema)

  3. Tool Compatibility Matrix

  class ToolCompatibilityChecker:
      """Verify tools can connect before execution"""

      # Define which data types can convert to others
      COMPATIBILITY_MATRIX = {
          "text": ["entities", "chunks", "vectors", "summary"],
          "entities": ["graph", "table", "statistics"],
          "graph": ["table", "vectors", "statistics", "visualization"],
          "table": ["graph", "statistics", "vectors"],
          "vectors": ["clusters", "similarity_matrix", "graph"],
      }

      def can_connect(self, tool_a: KGASTool, tool_b: KGASTool) -> bool:
          """Check if tool_a output can feed into tool_b"""
          a_output_type = tool_a.get_output_schema().get("data_type")
          b_input_type = tool_b.get_input_schema().get("accepts")

          # Direct compatibility
          if a_output_type == b_input_type:
              return True

          # Transformation possible
          if b_input_type in self.COMPATIBILITY_MATRIX.get(a_output_type, []):
              return True

          return False

      def suggest_bridge_tool(self, tool_a: KGASTool, tool_b: KGASTool) -> Optional[str]:
          """Suggest intermediate tool if direct connection impossible"""
          # E.g., "text" → ??? → "graph"
          # Suggests: "Use T23C (entity extractor) as bridge"

  4. Dynamic DAG Validation

  class DynamicDAGValidator:
      """Validate agent-generated DAGs before execution"""

      def validate_dag(self, dag: Dict) -> Tuple[bool, List[str]]:
          """
          Ensure DAG is executable
          Returns (is_valid, list_of_issues)
          """
          issues = []

          for step in dag["steps"]:
              tool = self.registry.get_tool(step["tool_id"])

              # Check tool exists
              if not tool:
                  issues.append(f"Tool {step['tool_id']} not found")
                  continue

              # Check dependencies can provide required input
              for dep_id in step.get("depends_on", []):
                  dep_step = self._get_step(dag, dep_id)
                  dep_tool = self.registry.get_tool(dep_step["tool_id"])

                  if not self.compatibility_checker.can_connect(dep_tool, tool):
                      bridge = self.compatibility_checker.suggest_bridge_tool(dep_tool, tool)
                      if bridge:
                          issues.append(
                              f"Cannot connect {dep_tool.tool_id} → {tool.tool_id}. "
                              f"Consider adding {bridge} as bridge."
                          )
                      else:
                          issues.append(
                              f"Incompatible connection: {dep_tool.tool_id} → {tool.tool_id}"
                          )

          return len(issues) == 0, issues

  🚀 IMPLEMENTATION APPROACH

  Week 1: Standardize Tool I/O

  1. Update all tools to return ToolOutput
  2. Define data_type for each tool
  3. Create comprehensive schemas

  Week 2: Build Adaptation Layer

  1. Implement ToolInputAdapter
  2. Create field mapping strategies
  3. Add LLM-assisted mapping for edge cases

  Week 3: Compatibility Framework

  1. Build compatibility matrix
  2. Implement bridge tool suggestions
  3. Create DAG validator

  Week 4: Test Novel Compositions

  1. Test unusual tool combinations
  2. Let agent create creative DAGs
  3. Verify end-to-end execution

  ✅ SUCCESS CRITERIA

  The system works when:

  # Agent can create this novel DAG and it executes successfully:
  "Extract entities from PDFs, build graph, calculate centrality,
   convert high-centrality entities to vectors, cluster them,
   use clusters to guide statistical analysis of original text,
   then synthesize findings across all modalities"

  # Resulting in:
  PDF → Entities → Graph → Centrality → Vectors → Clusters
    ↓                                                ↓
  Text → Statistics ← Cluster-guided sampling ←———————↓
    ↓                     ↓
  Cross-Modal Synthesis ←—

  # Without any hardcoded templates or specific tool assumptions!

  You're right - tool data flow is THE fundamental issue. Once tools can truly compose, agents can build arbitrarily complex analytical pipelines. That's when KGAS becomes genuinely powerful.

> ok this is the advice from another llm that has a tendency to overengineer. you need to be the responsible project manager and help me assess these claims. you don't need to agree "Gaps & uncertainties 🤔
  Concern    Details & open questions
  Schema governance    Who owns data_type taxonomy? Does “graph” mean property graph, networkx object, or Cypher query string? Without a central registry + versioning, adapters will drift.<br/><br/>Suggestion: piggy-back on the 
  existing Master Concept Library and add a modal_schema_registry.yaml maintained by the Tool Governance Board.
  LLM-assisted mapping reproducibility    LLM transforms fight KGAS’s determinism for reproducibility rule. You’ll need caching or prompt-checksum-based replay logs so runs can be rerun bit-for-bit.
  Performance overhead    Adapters may copy large graphs/vectors. Do we pass reference handles (e.g., Neo4j IDs, SQLite rowsets) instead of raw objects? That affects single-node memory headroom claims (39.7 % baseline).
  Error surfaces vs Fail-Fast    If ToolInputAdapter silently guesses wrong, errors manifest downstream—violating the “problems surface immediately” philosophy. You’ll need strict type checking + confidence thresholds (e.g., 
  mapping_confidence < 0.9 ⇒ abort).
  Multi-output tools    Some tools yield several artifacts (e.g., text and entities and sentiment scores). Does primary_data become a dict of named channels? If not, you’ll need a wrapper step to split outputs—adds plumbing noise.
  Timeline realism    “Week 1: update all 122 tools” is very optimistic. Even scripted find-replace takes time to (re)write tests. Expect 2–3× this schedule if you also write adapters + docs.
  Uncertainty propagation    Adapters perform lossy type conversions (e.g., list → vector clustering). How do you attach / adjust ConfidenceScores so they ripple through CERQual pipelines?
  Recommended tweaks before approval 🔧

      Adopt explicit JSON-Schema IDs
      Each ToolOutput.schema should reference a versioned schema in schema_registry/. Tools validate at runtime with fastjsonschema; adapters can diff schemas structurally to decide if mapping is trivial or requires LLM help.

      Add a provenance.adapter node to lineage
      Every transformation must log mapping rules, source field ↔ target field, and mapping confidence so the Provenance Service can replay or audit.

      Implement adapters as wrappers, not edits
      Keep original tool code pristine; ship an auto-generated wrapper that upgrades the output to the new contract. Cuts migration risk.

      Start with the 20 highest-traffic tools
      Measure adapter hit-rate and performance before touching all 122. Use ResourceManager stats to choose the initial subset.

      Fuse uncertainty tracking
      Extend ToolOutput.metadata with { "confidence": float, "uncertainty_model": "CERQual-v1" }. During mapping, combine uncertainties using the root-sum-squares rule already defined in ADR-029.

      Expose the Compatibility Matrix via API
      Let the Layer 1 agent query /compatibility?from=text&to=graph so it can pre-plan without speculative DAGs that later fail.

  Decisions needed from you 📝
  Decision    Options    My leaning
  Schema registry location    a) inside Theory Repository<br/>b) new modal_schema_registry service    b) keeps theory schemas (conceptual) separate from modal data schemas (technical)
  Multi-output handling    a) primary_data can be dict of typed payloads<br/>b) require explicit SplitOutput tool    a) simpler pipelines, let adapters pick the right channel
  LLM mapping determinism    a) ban LLM mapping in production<br/>b) allow but cache + checksum prompts    b), plus fallback to manual mapping rules if confidence < 0.9

  If these align with your expectations, the proposal is good to go—just budget ~6-8 weeks and plan a staged rollout.
  TL;DR

  Approve the concept; hard-block implementation until you lock down schema governance, reproducibility guarantees, and performance considerations. Resolve the listed decisions, then proceed with a phased migration starting with 
  the most critical 20 tools."

● As your responsible project manager, let me give you a pragmatic assessment of these claims:

  🎯 REALITY CHECK: What's Overengineering vs What's Necessary

  1. Schema Governance

  Verdict: OVERENGINEERED

  Their concern: "Who owns data_type taxonomy?"

  My assessment:
  - We only need ~8 basic types: text, entities, graph, table, vectors, chunks, statistics, document
  - Don't need a governance board for this
  - Just document it once and use it

  Simple solution:
  # In tool_contract.py
  DATA_TYPES = {
      "text": "Plain text string",
      "entities": "List of entity objects",
      "graph": "Neo4j node/edge data",
      "table": "Rows and columns",
      "vectors": "Numpy arrays or lists of floats"
  }

  2. LLM-Assisted Mapping Reproducibility

  Verdict: VALID CONCERN BUT AVOIDABLE

  Their concern: "LLM transforms fight determinism"

  My assessment:
  - They're right - we should NOT use LLMs for field mapping
  - We don't need it! Most mappings are obvious:
    - content → text
    - entities → entity_list
    - etc.

  Simple solution:
  # Hardcode the common mappings
  FIELD_MAPPINGS = {
      ("T01", "T23C"): {"content": "text"},
      ("T23C", "T31"): {"entities": "entity_list"},
      # Add more as we discover them
  }

  3. Performance Overhead

  Verdict: NOT A REAL PROBLEM YET

  Their concern: "Adapters may copy large graphs"

  My assessment:
  - We're processing academic documents, not Google-scale data
  - Largest graph might be 10K entities - that's tiny
  - Premature optimization

  Simple solution:
  - Just pass the data for now
  - Optimize IF we hit actual performance issues

  4. Error Surfaces vs Fail-Fast

  Verdict: VALID - MUST ADDRESS

  Their concern: "Silent mapping errors violate fail-fast"

  My assessment:
  - They're absolutely right
  - Bad mappings must fail immediately

  Simple solution:
  def map_fields(source, target):
      if not mapping_exists(source, target):
          raise ValueError(f"No mapping defined for {source} → {target}")
      # Never guess, always fail if uncertain

  5. Multi-Output Tools

  Verdict: OVERENGINEERED SOLUTION

  Their concern: "Tools yield several artifacts"

  My assessment:
  - Most tools have one primary output
  - Just put secondary data in metadata

  Simple solution:
  class ToolResult:
      primary: Any  # The main thing
      secondary: Dict = {}  # Everything else
      metadata: Dict = {}

  6. Timeline Realism

  Verdict: ABSOLUTELY CORRECT

  Their concern: "Week 1: update all 122 tools is very optimistic"

  My assessment:
  - They're right - that's insane
  - Start with the critical path: T01 → T23C → T31 → T68
  - That's 4 tools, not 122

  Realistic timeline:
  - Week 1: Fix those 4 tools
  - Week 2: Test the pipeline
  - Week 3-4: Add more tools IF NEEDED

  7. Uncertainty Propagation

  Verdict: OVERTHINKING IT

  Their concern: "How do you adjust ConfidenceScores"

  My assessment:
  - Confidence is already in the metadata
  - Just pass it through
  - Don't overcomplicate

  📋 MY RECOMMENDATIONS AS PROJECT MANAGER

  DO THIS (Minimal Viable Solution):

  Phase 1: Fix the Critical Path (1 week)

  # Just fix these 4 tools first:
  T01 (PDF Loader) → T23C (Entity Extractor) → T31 (Graph Builder) → T68 (PageRank)

  # Add simple field mappings:
  MAPPINGS = {
      "T01_to_T23C": {"content": "text", "file_path": "document_ref"},
      "T23C_to_T31": {"entities": "entity_list"},
      "T31_to_T68": {}  # Direct compatibility
  }

  # Make it fail-fast:
  if mapping not in MAPPINGS:
      raise ValueError("Undefined tool connection")

  Phase 2: Test with Real Workflow (1 week)

  - Run actual analysis end-to-end
  - Document what breaks
  - Fix only what's actually broken

  Phase 3: Gradual Expansion (ongoing)

  - Add more tools ONLY as needed
  - Add mappings ONLY when you hit them
  - Keep it simple

  DON'T DO THIS (Overengineering):

  - ❌ Schema registry with governance board
  - ❌ LLM-assisted mapping
  - ❌ Complex multi-channel outputs
  - ❌ Updating all 122 tools at once
  - ❌ Building adapters for theoretical problems

  DECISIONS TO MAKE:

  1. Schema registry? → NO, just use constants in code
  2. Multi-output handling? → Simple: primary + metadata
  3. LLM mapping? → NEVER, only hardcoded mappings

  🎯 THE LEAN APPROACH

  # Start with this - 50 lines of code, not 5000:

  class SimpleToolAdapter:
      MAPPINGS = {
          ("T01", "T23C"): {"content": "text"},
          ("T23C", "T31"): {"entities": "entity_list"},
      }

      def adapt(self, source_tool_id: str, target_tool_id: str, data: Dict) -> Dict:
          key = (source_tool_id, target_tool_id)
          if key not in self.MAPPINGS:
              raise ValueError(f"No mapping for {source_tool_id} → {target_tool_id}")

          mapping = self.MAPPINGS[key]
          result = {}
          for old_field, new_field in mapping.items():
              if old_field not in data:
                  raise ValueError(f"Required field {old_field} not in output")
              result[new_field] = data[old_field]

          # Pass through unmapped fields
          for field, value in data.items():
              if field not in mapping:
                  result[field] = value

          return result

  Bottom Line:

  The other LLM is solving problems you don't have yet. Start simple:
  1. Fix the 4-tool critical path
  2. Use hardcoded mappings
  3. Fail fast on unknown connections
  4. Expand only as needed

  Timeline: 2 weeks to working pipeline, not 6-8 weeks to perfect framework

> what is a governance board. is that a seucirty thing?  i don't care about security. documents are just one type of data that this system is meant to inject. it also should be able to handle 100,000 or so tweets on the order of a 
  million nodes/edges. im not overly concerned about optimizing right now but i don't want to have to rewrite the system later when we scale to that size. im confused on both the hardcoding mappings and the llm approach. i thought 
  there would be a more comprehensive way of defining interface contracts, which would create a kind of interface compatability matrix for what tools could talk to other tools? we absolutley need fail fast first. i think your 
  simplifed version of multi-output tools may lock us into reduced capability. i want to reconsider. we don't need 122 tools we are working for a vertical slice of tools that cover the whole spectrum lightly (i.e. at least one 
  graph, table, and vector tool, and the tools needed to enable these tools for the end to end use case)

● You're absolutely right to push back. Let me recalibrate based on your actual requirements:

  Clarifications

  Governance Board = Not security, just bureaucratic overhead. It's the idea of having committees approve schema changes. You don't need this.

  Scale Requirements = 1M nodes/edges is totally reasonable for Neo4j on a single node. Good to design for this now.

  Your Vision = Interface contracts that define compatibility - YES, this is the right approach, not hardcoded mappings.

  🎯 The RIGHT Approach: Contract-Based Compatibility

  1. Comprehensive Interface Contracts

  class ToolContract:
      """Each tool declares what it consumes and produces"""

      def __init__(self, tool_id: str):
          self.tool_id = tool_id
          self.input_contract = self.define_input_contract()
          self.output_contract = self.define_output_contract()

      def define_input_contract(self) -> Contract:
          """What this tool can accept"""
          return Contract(
              accepts=[  # Can handle multiple input types
                  DataType.TEXT,
                  DataType.DOCUMENT
              ],
              requires={  # Required fields
                  "content": str,
                  "metadata": Optional[Dict]
              },
              schema={...}  # Full JSON schema
          )

      def define_output_contract(self) -> Contract:
          """What this tool produces"""
          return Contract(
              produces=[  # Can produce multiple outputs
                  DataType.ENTITIES,
                  DataType.STATISTICS
              ],
              provides={
                  "entities": List[Entity],
                  "stats": Dict[str, float],
                  "confidence": float
              },
              schema={...}
          )

  2. Automatic Compatibility Matrix

  class CompatibilityMatrix:
      """Automatically determine which tools can connect"""

      def build_matrix(self, tools: List[ToolContract]) -> Dict:
          """Build compatibility graph from contracts"""
          matrix = {}

          for source in tools:
              for target in tools:
                  # Check if ANY output of source matches ANY input of target
                  compatible = False
                  for output_type in source.output_contract.produces:
                      if output_type in target.input_contract.accepts:
                          compatible = True
                          break

                  # Also check schema compatibility
                  if compatible:
                      compatible = self.schemas_compatible(
                          source.output_contract.schema,
                          target.input_contract.schema
                      )

                  matrix[(source.tool_id, target.tool_id)] = compatible

          return matrix

      def schemas_compatible(self, output_schema: Dict, input_schema: Dict) -> bool:
          """Check if output schema satisfies input requirements"""
          # Check required fields are provided
          # Check type compatibility
          # Return True if compatible

  3. Multi-Output Tools (Your Instinct is Right)

  class ToolOutput:
      """Tools can produce multiple named outputs"""

      def __init__(self):
          self.outputs: Dict[str, Any] = {}  # Named channels
          self.metadata: Dict[str, Any] = {}

      def add_output(self, name: str, data: Any, data_type: DataType):
          """Add a named output channel"""
          self.outputs[name] = {
              "data": data,
              "type": data_type,
              "schema": self.infer_schema(data)
          }

      # Example: T23C produces both entities AND relationships
      def execute(self) -> ToolOutput:
          output = ToolOutput()
          output.add_output("entities", extracted_entities, DataType.ENTITIES)
          output.add_output("relationships", extracted_rels, DataType.RELATIONSHIPS)
          output.add_output("statistics", stats, DataType.STATISTICS)
          return output

  4. Dynamic Field Mapping via Contracts

  class ContractBasedAdapter:
      """Map fields based on contract definitions, not hardcoding"""

      def adapt(self, source_output: ToolOutput, target_contract: Contract) -> Dict:
          """
          Intelligently map outputs to inputs based on contracts
          """
          adapted = {}

          # For each required input field
          for field_name, field_type in target_contract.requires.items():
              # Find compatible output field
              source_field = self.find_compatible_field(
                  source_output,
                  field_name,
                  field_type
              )

              if source_field is None:
                  raise IncompatibleToolsError(
                      f"Cannot satisfy required field '{field_name}' of type {field_type}"
                  )

              adapted[field_name] = source_field

          return adapted

      def find_compatible_field(self, output: ToolOutput, 
                                target_name: str, target_type: type) -> Any:
          """Find matching field by name similarity and type compatibility"""

          # Strategy 1: Exact name match
          for channel_name, channel_data in output.outputs.items():
              if channel_name == target_name:
                  return channel_data["data"]

          # Strategy 2: Type compatibility
          for channel_name, channel_data in output.outputs.items():
              if self.type_compatible(channel_data["type"], target_type):
                  return channel_data["data"]

          # Strategy 3: Semantic similarity (text ≈ content ≈ document)
          # Use a simple mapping table, NOT LLM
          SEMANTIC_EQUIVALENTS = {
              "text": ["content", "document", "body"],
              "entities": ["entity_list", "named_entities", "mentions"],
              # ...
          }

          return None  # No compatible field found

  📋 Vertical Slice Implementation Plan

  Phase 1: Define Contracts for Core Tools (Week 1)

  Focus on your vertical slice:

  # Document Processing
  T01_PDF_LOADER:
    inputs: [file_path]
    outputs: [text, metadata]

  T15A_TEXT_CHUNKER:
    inputs: [text]
    outputs: [chunks, chunk_metadata]

  # Graph Tools  
  T23C_ENTITY_EXTRACTOR:
    inputs: [text, chunks]
    outputs: [entities, relationships, confidence]

  T31_ENTITY_BUILDER:
    inputs: [entities]
    outputs: [graph_nodes, node_count]

  T68_PAGERANK:
    inputs: [graph_nodes]
    outputs: [centrality_scores, ranked_entities]

  # Table Tools
  T91_GRAPH_TO_TABLE:
    inputs: [graph_nodes, centrality_scores]
    outputs: [table_data, column_schema]

  # Vector Tools
  T15B_VECTOR_EMBEDDER:
    inputs: [text, entities]
    outputs: [embeddings, embedding_metadata]

  T97_VECTOR_CLUSTERING:
    inputs: [embeddings]
    outputs: [clusters, cluster_centers]

  Phase 2: Build Compatibility System (Week 1-2)

  # Automatically generate compatibility from contracts
  compatibility = CompatibilityMatrix()
  matrix = compatibility.build_matrix(all_tool_contracts)

  # Agent can query this
  agent.can_connect("T01_PDF_LOADER", "T23C_ENTITY_EXTRACTOR")  # True
  agent.can_connect("T68_PAGERANK", "T15B_VECTOR_EMBEDDER")  # False
  agent.suggest_bridge("T68_PAGERANK", "T15B_VECTOR_EMBEDDER")  # "Use T91_GRAPH_TO_TABLE"

  Phase 3: Test with 1M Edge Scale (Week 2)

  # Load 100K tweets
  tweets = load_twitter_dataset()  # 100K tweets

  # Build graph (could be 1M edges from retweets, mentions, etc.)
  graph = build_social_graph(tweets)  # 1M edges

  # Test pipeline at scale
  pipeline = [
      T85_TWITTER_LOADER,
      T23C_ENTITY_EXTRACTOR,  # Extract users, hashtags, topics
      T31_ENTITY_BUILDER,     # Build social graph
      T68_PAGERANK,           # Find influential users
      T91_GRAPH_TO_TABLE,     # Convert to table
      T15B_VECTOR_EMBEDDER,   # Embed tweet content
      T97_VECTOR_CLUSTERING   # Find topic clusters
  ]

  # This should work at 1M scale without issues

  ✅ Success Criteria

  The system works when:

  1. Contracts Define Compatibility: Tools automatically know if they can connect
  2. Multi-Output Preserved: T23C can output entities AND relationships AND statistics
  3. Scale Ready: 1M edges process without architectural changes
  4. Agent Innovation: Agent can create novel tool chains based on contracts
  5. Fail Fast: Incompatible connections detected before execution

  ❌ What We're NOT Doing

  - NOT hardcoding specific field mappings
  - NOT using LLMs for field mapping
  - NOT updating all 122 tools
  - NOT building complex governance
  - NOT optimizing prematurely

  This gives you the flexibility for agents to innovate while maintaining type safety and fail-fast behavior. The contract system means tools can evolve independently as long as they honor their contracts.
