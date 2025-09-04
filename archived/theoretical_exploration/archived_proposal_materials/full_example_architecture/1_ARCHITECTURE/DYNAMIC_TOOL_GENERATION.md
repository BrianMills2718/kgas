# Dynamic Tool Generation Architecture

## Core Insight
Tools are NOT pre-built. They are GENERATED from theory schemas extracted by LLMs.

## The Flow

### 1. Theory Extraction
```
Turner 1986 Paper → LLM → Theory Schema (meta_schema_v13)
                           ├── Entities
                           ├── Relations  
                           └── Algorithms
                               ├── Mathematical (formulas)
                               ├── Logical (rules)
                               └── Procedural (steps)
```

### 2. Dynamic Tool Generation

When the theory schema contains algorithms, we dynamically generate tools:

```python
class DynamicToolGenerator:
    """Generate executable tools from theory algorithms"""
    
    def generate_from_theory(self, theory_schema: Dict) -> List[KGASTool]:
        tools = []
        
        # Generate mathematical tools
        for algo in theory_schema.get('algorithms', {}).get('mathematical', []):
            tool_code = self.llm_generate_tool(algo)
            tool_class = self.compile_tool(tool_code)
            tools.append(tool_class)
        
        # Generate logical rule tools
        for rule_set in theory_schema.get('algorithms', {}).get('logical', []):
            tool_code = self.llm_generate_rule_engine(rule_set)
            tool_class = self.compile_tool(tool_code)
            tools.append(tool_class)
        
        # Generate procedural tools
        for procedure in theory_schema.get('algorithms', {}).get('procedural', []):
            tool_code = self.llm_generate_procedure(procedure)
            tool_class = self.compile_tool(tool_code)
            tools.append(tool_class)
        
        return tools
    
    def llm_generate_tool(self, algorithm_spec: Dict) -> str:
        """LLM generates Python code for the algorithm"""
        
        prompt = f"""
        Generate a Python tool class that implements this algorithm:
        
        Name: {algorithm_spec['name']}
        Formula: {algorithm_spec['formula']}
        Parameters: {algorithm_spec['parameters']}
        
        The tool should:
        1. Inherit from KGASTool
        2. Implement execute(request: ToolRequest) -> ToolResult
        3. Apply the formula to the input data
        4. Include uncertainty assessment
        
        Generate complete, executable Python code.
        """
        
        return llm.generate(prompt)
```

### 3. Example: MCR Calculator Generation

**Input from Theory Schema:**
```json
{
  "name": "meta_contrast_ratio",
  "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
  "parameters": {
    "x_i": "individual's position vector",
    "x_outgroup": "outgroup members' positions",
    "x_ingroup": "ingroup members' positions"
  }
}
```

**LLM Generates Tool:**
```python
class MetaContrastRatioTool(KGASTool):
    """Auto-generated tool for meta_contrast_ratio calculation"""
    
    def __init__(self, service_manager):
        super().__init__(service_manager)
        self.tool_id = "MCR_CALCULATOR"
        self.formula = "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|"
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Calculate MCR for each individual"""
        
        # Extract data
        individuals = request.input_data['individuals']
        group_assignments = request.input_data['group_assignments']
        position_vectors = request.input_data['position_vectors']
        
        mcr_scores = {}
        
        for ind_id, ind_pos in position_vectors.items():
            # Identify in-group and out-group
            ind_group = group_assignments[ind_id]
            ingroup_members = [i for i, g in group_assignments.items() 
                              if g == ind_group and i != ind_id]
            outgroup_members = [i for i, g in group_assignments.items() 
                               if g != ind_group]
            
            # Calculate distances
            outgroup_distances = sum(
                np.linalg.norm(ind_pos - position_vectors[out_id])
                for out_id in outgroup_members
            )
            
            ingroup_distances = sum(
                np.linalg.norm(ind_pos - position_vectors[in_id])
                for in_id in ingroup_members
            )
            
            # Apply formula
            if ingroup_distances > 0:
                mcr_scores[ind_id] = outgroup_distances / ingroup_distances
            else:
                mcr_scores[ind_id] = float('inf')
        
        # Assess uncertainty
        uncertainty = self.assess_uncertainty(
            len(individuals),
            len([i for i in position_vectors if i is not None])
        )
        
        return ToolResult(
            status="success",
            data={"mcr_scores": mcr_scores},
            confidence=uncertainty,
            metadata={"formula": self.formula}
        )
    
    def assess_uncertainty(self, total_individuals, complete_data):
        """LLM assesses uncertainty in MCR calculation"""
        
        coverage = complete_data / total_individuals
        
        if coverage > 0.9:
            uncertainty = 0.15
            justification = f"High data coverage ({coverage:.1%}), MCR calculation reliable"
        elif coverage > 0.7:
            uncertainty = 0.30
            justification = f"Moderate data coverage ({coverage:.1%}), some uncertainty in MCR"
        else:
            uncertainty = 0.50
            justification = f"Low data coverage ({coverage:.1%}), high uncertainty in MCR"
        
        return {
            "uncertainty": uncertainty,
            "justification": justification,
            "data_coverage": coverage
        }
```

## Key Principles

1. **Theory-Driven Tool Generation**: Tools are created from theory specifications, not pre-built
2. **LLM as Programmer**: LLM generates executable code from formulas/rules
3. **Dynamic Registration**: Generated tools are registered at runtime
4. **Uncertainty Built-In**: Each generated tool includes uncertainty assessment
5. **Flexible Execution**: Tools adapt to the specific theory being applied

## Uncertainty in Generated Tools

Each dynamically generated tool assesses uncertainty based on:
- Data completeness for its specific calculation
- Validity of assumptions in the formula
- Quality of input data
- Appropriateness of the algorithm for the context

## Benefits

1. **Theory-Agnostic**: Works for ANY theory that can be formalized
2. **No Pre-Building**: Don't need to anticipate all possible algorithms
3. **Faithful Implementation**: Direct translation from theory to code
4. **Adaptable**: Can generate variations based on context
5. **Traceable**: Clear lineage from theory paper to executable tool

## Integration with DAG

```python
# Step 1: Extract theory
theory_schema = theory_extractor.extract("Turner_1986.pdf")

# Step 2: Generate tools from theory
generator = DynamicToolGenerator()
theory_tools = generator.generate_from_theory(theory_schema)

# Step 3: Register generated tools
for tool in theory_tools:
    tool_registry.register(tool)

# Step 4: Execute DAG with generated tools
dag_executor.run(dag, tool_registry)
```

## This Changes Everything

We don't need:
- Pre-built MCR calculator
- Pre-built theory-specific tools
- Rigid tool contracts for theory algorithms

We need:
- Dynamic tool generation framework
- LLM code generation capabilities
- Runtime tool compilation and registration
- Flexible uncertainty assessment per generated tool