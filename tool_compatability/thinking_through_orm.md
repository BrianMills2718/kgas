# Thinking Through Object Role Modeling for Tool Compatibility

## The Core Insight

Object Role Modeling (ORM) treats everything as **facts** - n-ary relationships between objects playing specific roles. This maps perfectly to tool chains where data flows through transformations.

Instead of fighting with field names, data structures, and type mismatches, ORM focuses on **what role each piece of data plays** in a tool's operation.

## Why ORM Solves Our Tool Compatibility Problem

### Current Problems (from unresolved_issues.md)
1. **Field name mismatches** - "entities" vs "extracted_entities" 
2. **Semantic ambiguity** - Same field name, different meanings
3. **Structure variations** - {"id": "e1"} vs {"entity_id": "e1"}
4. **Optional fields** - What's required vs optional unclear
5. **N-ary relationships** - Tools need multiple inputs/outputs
6. **Type specificity** - "list" isn't specific enough

### How ORM Addresses Each Problem

1. **No field names** - Only roles matter
2. **Explicit semantics** - Each role has clear meaning
3. **Structure-agnostic** - Internal format doesn't matter
4. **Cardinality constraints** - "1", "0..1", "1..*" explicit
5. **N-ary native** - Facts can have any number of roles
6. **Semantic types** - Not Python types but domain concepts

## Core ORM Concepts Applied to KGAS

### Facts
Each tool execution is a fact stating relationships between data objects:
- "T23C extracts entities from text"
- "T31 builds graph nodes from entities"
- "T34 creates edges from relationships"

### Objects
The actual data elements:
- A text document
- A list of entities
- A graph structure
- A vector embedding

### Roles
What each object does in the fact:
- `input_document` - Text being analyzed
- `extracted_entities` - Entities found in text
- `built_nodes` - Graph nodes created
- `connected_edges` - Relationships established

### Constraints
Rules about role relationships:
- Uniqueness: One input produces one output
- Mandatory: Tool requires this role filled
- Cardinality: How many objects can play this role

## The Three Representations

### 1. Graph View
Objects as nodes, roles as typed edges:

```
[Document] --plays_role:input_text--> [T23C_Execution]
[T23C_Execution] --produces_role:entities--> [EntityList]
[EntityList] --plays_role:input_entities--> [T31_Execution]
[T31_Execution] --produces_role:nodes--> [GraphNodes]
```

### 2. Table View  
Facts as rows, roles as columns:

```
| Fact_ID | Tool | Input_Role      | Input_Object | Output_Role | Output_Object |
|---------|------|-----------------|--------------|-------------|---------------|
| f1      | T23C | input_text      | doc.txt      | entities    | [e1,e2,e3]    |
| f2      | T31  | input_entities  | [e1,e2,e3]   | nodes       | [n1,n2,n3]    |
| f3      | T34  | input_relations | [r1,r2]      | edges       | [edge1,edge2] |
```

### 3. Vector View
Role embeddings for semantic similarity:

```python
role_vectors = {
    "extracted_entities": [0.8, 0.2, 0.1, ...],
    "input_entities": [0.85, 0.18, 0.12, ...],  # Similar!
    "raw_text": [0.1, 0.9, 0.3, ...],            # Different!
}

# Compatibility = cosine similarity > threshold
compatible = cosine_sim(role_vectors["extracted_entities"], 
                        role_vectors["input_entities"]) > 0.9
```

## Practical Implementation

### Tool Definition with ORM

```python
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

class Cardinality(Enum):
    ONE = "1"              # Exactly one
    ZERO_OR_ONE = "0..1"   # Optional
    ONE_OR_MORE = "1..*"   # At least one
    ZERO_OR_MORE = "0..*"  # Any number

@dataclass
class Role:
    """A role that data can play in a tool fact."""
    name: str                    # Internal role name
    semantic_type: str           # Domain concept
    cardinality: Cardinality     # How many allowed
    description: str             # Human-readable purpose
    constraints: List[str] = None # Additional rules

@dataclass  
class ToolFact:
    """Definition of what a tool does in ORM terms."""
    tool_id: str
    fact_type: str              # "extraction", "transformation", "analysis"
    input_roles: Dict[str, Role]
    output_roles: Dict[str, Role]
    
    def describes_fact(self) -> str:
        """Natural language description of the fact."""
        inputs = ", ".join(self.input_roles.keys())
        outputs = ", ".join(self.output_roles.keys())
        return f"{self.tool_id} takes {inputs} and produces {outputs}"
```

### Example Tool Definitions

```python
# T23C: Entity Extractor
T23C_FACT = ToolFact(
    tool_id="T23C",
    fact_type="extraction",
    input_roles={
        "document": Role(
            name="document",
            semantic_type="text_content",
            cardinality=Cardinality.ONE,
            description="Text document to analyze"
        ),
        "config": Role(
            name="config",
            semantic_type="extraction_config",
            cardinality=Cardinality.ZERO_OR_ONE,
            description="Optional extraction parameters"
        )
    },
    output_roles={
        "entities": Role(
            name="entities",
            semantic_type="named_entities",
            cardinality=Cardinality.ZERO_OR_MORE,
            description="Extracted named entities"
        ),
        "relationships": Role(
            name="relationships", 
            semantic_type="entity_relationships",
            cardinality=Cardinality.ZERO_OR_MORE,
            description="Relationships between entities"
        )
    }
)

# T31: Node Builder
T31_FACT = ToolFact(
    tool_id="T31",
    fact_type="transformation",
    input_roles={
        "entities": Role(
            name="entities",
            semantic_type="named_entities",  # Matches T23C output!
            cardinality=Cardinality.ONE_OR_MORE,
            description="Entities to convert to nodes"
        )
    },
    output_roles={
        "nodes": Role(
            name="nodes",
            semantic_type="graph_nodes",
            cardinality=Cardinality.ONE_OR_MORE,
            description="Graph nodes for Neo4j"
        )
    }
)

# T34: Edge Builder  
T34_FACT = ToolFact(
    tool_id="T34",
    fact_type="transformation",
    input_roles={
        "relationships": Role(
            name="relationships",
            semantic_type="entity_relationships",  # Matches T23C output!
            cardinality=Cardinality.ONE_OR_MORE,
            description="Relationships to convert"
        ),
        "nodes": Role(
            name="nodes",
            semantic_type="graph_nodes",  # Matches T31 output!
            cardinality=Cardinality.ONE_OR_MORE,
            description="Nodes to connect"
        )
    },
    output_roles={
        "edges": Role(
            name="edges",
            semantic_type="graph_edges",
            cardinality=Cardinality.ZERO_OR_MORE,
            description="Graph edges for Neo4j"
        )
    }
)
```

### Compatibility Checking

```python
class ORMCompatibilityChecker:
    """Check if tools can be chained based on role compatibility."""
    
    def can_chain(self, producer: ToolFact, consumer: ToolFact) -> Dict[str, str]:
        """
        Check if producer's outputs can fulfill consumer's inputs.
        Returns mapping of compatible roles or empty dict if incompatible.
        """
        role_mappings = {}
        
        # For each input role the consumer needs
        for input_name, input_role in consumer.input_roles.items():
            # Find matching output role from producer
            match_found = False
            for output_name, output_role in producer.output_roles.items():
                if self.roles_compatible(output_role, input_role):
                    role_mappings[output_name] = input_name
                    match_found = True
                    break
            
            # If required role not fulfilled, tools incompatible
            if not match_found and input_role.cardinality in [
                Cardinality.ONE, Cardinality.ONE_OR_MORE
            ]:
                return {}  # Incompatible
        
        return role_mappings
    
    def roles_compatible(self, output: Role, input: Role) -> bool:
        """Check if an output role can fulfill an input role."""
        # Primary check: semantic types must match
        if output.semantic_type != input.semantic_type:
            return False
        
        # Cardinality check
        if not self.cardinality_compatible(output.cardinality, input.cardinality):
            return False
        
        # Additional constraint checks could go here
        return True
    
    def cardinality_compatible(self, output: Cardinality, input: Cardinality) -> bool:
        """Check if output cardinality satisfies input requirements."""
        # If input requires at least one, output must produce at least one
        if input in [Cardinality.ONE, Cardinality.ONE_OR_MORE]:
            return output in [Cardinality.ONE, Cardinality.ONE_OR_MORE]
        # Optional input accepts any output
        return True
```

### Building Tool Chains

```python
class ORMChainBuilder:
    """Build valid tool chains using ORM compatibility."""
    
    def __init__(self, tools: List[ToolFact]):
        self.tools = {t.tool_id: t for t in tools}
        self.checker = ORMCompatibilityChecker()
    
    def find_chain(self, start_semantic: str, goal_semantic: str) -> List[str]:
        """
        Find a tool chain that transforms start semantic type to goal.
        Returns list of tool IDs or empty list if impossible.
        """
        # Find tools that accept start_semantic
        possible_starts = [
            tool_id for tool_id, tool in self.tools.items()
            if any(role.semantic_type == start_semantic 
                   for role in tool.input_roles.values())
        ]
        
        # BFS to find path to goal_semantic
        from collections import deque
        
        queue = deque([(tool, [tool]) for tool in possible_starts])
        visited = set()
        
        while queue:
            current_tool, path = queue.popleft()
            
            if current_tool in visited:
                continue
            visited.add(current_tool)
            
            current_fact = self.tools[current_tool]
            
            # Check if we've reached goal
            if any(role.semantic_type == goal_semantic 
                   for role in current_fact.output_roles.values()):
                return path
            
            # Find compatible next tools
            for next_tool_id, next_fact in self.tools.items():
                if next_tool_id not in visited:
                    if self.checker.can_chain(current_fact, next_fact):
                        queue.append((next_tool_id, path + [next_tool_id]))
        
        return []  # No chain found
```

## Solving the Real Problems

### Problem 1: Field Name Mismatches
**ORM Solution**: Fields don't matter, only semantic types matter.

```python
# T23C might output {"extracted_entities": [...]}
# T31 might expect {"entities": [...]}
# Doesn't matter! Both have semantic_type="named_entities"
```

### Problem 2: Internal Structure Differences
**ORM Solution**: Internal structure is opaque, only role fulfillment matters.

```python
# T23C outputs: {"id": "e1", "text": "John"}
# T31 expects: {"entity_id": "e1", "label": "John"}
# Doesn't matter! Both fulfill role with semantic_type="named_entities"
```

### Problem 3: Optional vs Required
**ORM Solution**: Cardinality constraints make this explicit.

```python
# T34 requires relationships (cardinality=ONE_OR_MORE)
# T23C might not produce them (cardinality=ZERO_OR_MORE)
# Checker detects incompatibility when T23C has no relationships
```

### Problem 4: Multi-Input Tools
**ORM Solution**: Multiple input roles are natural in ORM.

```python
T34_FACT = ToolFact(
    input_roles={
        "relationships": Role(...),  # From T23C
        "nodes": Role(...),          # From T31
    }
)
# Chain builder ensures both roles fulfilled
```

### Problem 5: State Management
**ORM Solution**: State is just another role.

```python
T68_PAGERANK = ToolFact(
    input_roles={
        "graph": Role(semantic_type="graph_structure", ...),
        "previous_scores": Role(
            semantic_type="pagerank_scores",
            cardinality=Cardinality.ZERO_OR_ONE  # Optional for first iteration
        )
    },
    output_roles={
        "scores": Role(semantic_type="pagerank_scores", ...)
    }
)
```

## Why This Is Better Than Current Approaches

### Current Approach: Field Matching
```python
# Brittle, syntactic, prone to false positives
if "entities" in output and "entities" in input:
    return "compatible"  # But are they really?
```

### ORM Approach: Semantic Role Matching
```python
# Robust, semantic, explicit
if output_role.semantic_type == input_role.semantic_type:
    return "compatible"  # Yes, they fulfill same role
```

### Current Approach: Hardcoded Chains
```python
chains = [
    ["T23C", "T31", "T34"],  # Works but inflexible
]
```

### ORM Approach: Dynamic Discovery
```python
chain = find_chain(
    start_semantic="text_content",
    goal_semantic="graph_edges"
)
# Returns: ["T23C", "T31", "T34"] or any valid path
```

## Implementation Strategy

### Phase 1: Define Tool Facts (Week 1)
1. Create ToolFact for each of 38 tools
2. Identify semantic types across system
3. Document role constraints

### Phase 2: Build Compatibility Checker (Week 2)
1. Implement role compatibility logic
2. Add semantic type registry
3. Create validation tests

### Phase 3: Migrate Tools (Week 3)
1. Wrap existing tools with ORM adapter
2. Map current fields to roles
3. Test compatibility detection

### Phase 4: Enable Dynamic Chains (Week 4)
1. Implement chain builder
2. Create chain optimization (shortest path)
3. Add chain validation and testing

## The Key Advantages

1. **No Breaking Changes**: Existing tools keep their internals
2. **Semantic Clarity**: Roles make intent explicit
3. **Extensibility**: New tools just need ToolFact definition
4. **LLM-Friendly**: Semantic types are understandable
5. **Type-Safe**: Cardinality and constraints prevent errors

## Example: Complete T23C → T31 → T34 Chain

```python
# Define the tools
tools = [T23C_FACT, T31_FACT, T34_FACT]

# Initialize chain builder
builder = ORMChainBuilder(tools)

# Find chain from text to graph
chain = builder.find_chain(
    start_semantic="text_content",
    goal_semantic="graph_edges"
)
print(f"Chain: {chain}")  # ["T23C", "T31", "T34"]

# Execute chain with ORM wrapper
executor = ORMExecutor(tools)
result = executor.execute_chain(
    chain=chain,
    initial_data={"document": "John Smith is CEO of TechCorp"},
    initial_role="document"
)

# Result contains graph edges, regardless of internal format
```

## Conclusion

ORM solves the tool compatibility problem by:

1. **Eliminating field name dependencies** through semantic roles
2. **Making compatibility explicit** through semantic types
3. **Supporting complex flows** through n-ary facts
4. **Enabling dynamic discovery** through role matching

This isn't just a band-aid fix - it's a fundamental rethinking of how tools relate to each other. Instead of brittle syntactic matching, we get robust semantic compatibility.

The beauty is that **we don't need to rewrite the tools** - we just need to describe what roles their inputs and outputs play. The ORM layer handles the rest.