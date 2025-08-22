# Dynamic Tool Integration Example: MCR Calculator

## Complete Working Example

### Step 1: Theory Schema Input
```json
{
  "theory_name": "Self-Categorization Theory",
  "algorithms": {
    "mathematical": [{
      "name": "meta_contrast_ratio",
      "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
      "parameters": {
        "x_i": "individual's position vector",
        "x_outgroup": "outgroup members' positions",
        "x_ingroup": "ingroup members' positions"
      }
    }]
  }
}
```

### Step 2: LLM Generates Tool Code
```python
# Prompt to LLM
prompt = """
Generate a KGASTool implementation for:
Formula: MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|
Include execute() method and uncertainty assessment.
"""

# LLM generates this code:
generated_code = '''
import numpy as np
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult

class GeneratedMCRTool(KGASTool):
    def __init__(self, service_manager):
        super().__init__(service_manager)
        self.tool_id = "GENERATED_MCR_CALCULATOR"
        
    def execute(self, request: ToolRequest) -> ToolResult:
        individuals = request.input_data['individuals']
        group_assignments = request.input_data['group_assignments']
        position_vectors = request.input_data['position_vectors']
        
        mcr_scores = {}
        for ind_id, ind_pos in position_vectors.items():
            ind_group = group_assignments[ind_id]
            ingroup = [i for i, g in group_assignments.items() 
                      if g == ind_group and i != ind_id]
            outgroup = [i for i, g in group_assignments.items() 
                       if g != ind_group]
            
            out_dist = sum(np.linalg.norm(ind_pos - position_vectors[o]) 
                          for o in outgroup if o in position_vectors)
            in_dist = sum(np.linalg.norm(ind_pos - position_vectors[i]) 
                         for i in ingroup if i in position_vectors)
            
            mcr_scores[ind_id] = out_dist / in_dist if in_dist > 0 else float('inf')
        
        uncertainty = self._assess_uncertainty(len(individuals), len(position_vectors))
        
        return ToolResult(
            status="success",
            data={"mcr_scores": mcr_scores},
            metadata={"uncertainty": uncertainty}
        )
    
    def _assess_uncertainty(self, total, complete):
        coverage = complete / total if total > 0 else 0
        return {
            "score": 0.15 if coverage > 0.9 else 0.30 if coverage > 0.7 else 0.50,
            "justification": f"Data coverage: {coverage:.1%}"
        }
'''
```

### Step 3: Wrapper Integration
```python
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult
import types
import sys

class DynamicToolWrapper(KGASTool):
    """Wrapper that integrates generated code with KGAS infrastructure"""
    
    def __init__(self, service_manager, generated_code: str, algorithm_spec: dict):
        super().__init__(service_manager)
        self.algorithm_spec = algorithm_spec
        self.tool_id = f"DYNAMIC_{algorithm_spec['name'].upper()}"
        
        # Compile and instantiate generated tool
        self.generated_tool = self._compile_and_create(generated_code)
        
    def _compile_and_create(self, code: str):
        """Safely compile and instantiate generated code"""
        # Create module for generated code
        module = types.ModuleType('generated_tool')
        module.__dict__.update({
            'np': __import__('numpy'),
            'KGASTool': KGASTool,
            'ToolRequest': ToolRequest,
            'ToolResult': ToolResult
        })
        
        # Execute code in module namespace
        exec(code, module.__dict__)
        
        # Find and instantiate the tool class
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and issubclass(obj, KGASTool) and obj != KGASTool:
                return obj(self.service_manager)
        
        raise ValueError("No KGASTool subclass found in generated code")
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute with provenance and uncertainty tracking"""
        # Record provenance
        provenance = self.provenance_service.record_activity(
            activity_type="dynamic_tool_execution",
            entity_id=self.tool_id,
            metadata={
                "algorithm": self.algorithm_spec,
                "input_summary": self._summarize_input(request.input_data)
            }
        )
        
        # Execute generated tool
        result = self.generated_tool.execute(request)
        
        # Enhance with contextual uncertainty assessment
        enhanced_uncertainty = self._enhance_uncertainty(
            result.metadata.get('uncertainty', {}),
            request,
            result
        )
        
        # Return enhanced result
        result.metadata['enhanced_uncertainty'] = enhanced_uncertainty
        result.provenance = provenance
        return result
    
    def _enhance_uncertainty(self, base_uncertainty, request, result):
        """LLM enhances uncertainty with contextual assessment"""
        prompt = f"""
        Tool: {self.algorithm_spec['name']}
        Formula: {self.algorithm_spec['formula']}
        Data coverage: {base_uncertainty.get('justification', 'Unknown')}
        Input size: {len(request.input_data.get('individuals', []))}
        
        Assess uncertainty considering:
        - Theory-construct alignment
        - Measurement validity
        - Data completeness
        - Algorithm assumptions
        
        Provide Dempster-Shafer belief masses.
        """
        
        # In practice, this would call LLM
        return {
            "belief_masses": {
                "support": 0.7,
                "reject": 0.1,
                "uncertain": 0.2
            },
            "justification": base_uncertainty.get('justification', ''),
            "contextual_factors": [
                "High theory-construct alignment",
                "Moderate data coverage",
                "Valid algorithm assumptions"
            ]
        }
```

### Step 4: Runtime Registration
```python
class DynamicToolRegistry:
    """Registry for dynamically generated tools"""
    
    def __init__(self, base_registry):
        self.base_registry = base_registry
        self.dynamic_tools = {}
        
    def register_dynamic_tool(self, algorithm_spec: dict, generated_code: str):
        """Register a dynamically generated tool"""
        # Create wrapper
        wrapper = DynamicToolWrapper(
            self.base_registry.service_manager,
            generated_code,
            algorithm_spec
        )
        
        # Register in both registries
        tool_id = wrapper.tool_id
        self.dynamic_tools[tool_id] = wrapper
        self.base_registry.register(tool_id, wrapper)
        
        return tool_id
    
    def get_tool(self, tool_id: str):
        """Get tool from either registry"""
        if tool_id in self.dynamic_tools:
            return self.dynamic_tools[tool_id]
        return self.base_registry.get(tool_id)
```

### Step 5: Aggregation Integration
```python
class TweetUserAggregator(KGASTool):
    """Aggregates tweet-level MCR scores to user level"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        tweet_mcr_results = request.input_data['tweet_mcr_results']
        
        # Group by user
        user_evidence = {}
        for tweet_id, mcr_data in tweet_mcr_results.items():
            user_id = mcr_data['user_id']
            if user_id not in user_evidence:
                user_evidence[user_id] = []
            user_evidence[user_id].append(mcr_data['uncertainty'])
        
        # Aggregate using Dempster-Shafer
        user_beliefs = {}
        for user_id, evidences in user_evidence.items():
            combined = self._dempster_shafer_combine(evidences)
            user_beliefs[user_id] = combined
            
        return ToolResult(
            status="success",
            data={"user_beliefs": user_beliefs},
            metadata={"aggregation_method": "dempster_shafer"}
        )
    
    def _dempster_shafer_combine(self, evidences):
        """Combine multiple evidence sources"""
        if not evidences:
            return {"support": 0, "reject": 0, "uncertain": 1}
        
        combined = evidences[0]
        for evidence in evidences[1:]:
            # Calculate conflict
            K = (combined["support"] * evidence["reject"] + 
                 combined["reject"] * evidence["support"])
            
            if K >= 1:  # Complete conflict
                continue
                
            factor = 1 / (1 - K)
            
            # Combine beliefs
            new_combined = {
                "support": factor * (
                    combined["support"] * evidence["support"] +
                    combined["support"] * evidence["uncertain"] +
                    combined["uncertain"] * evidence["support"]
                ),
                "reject": factor * (
                    combined["reject"] * evidence["reject"] +
                    combined["reject"] * evidence["uncertain"] +
                    combined["uncertain"] * evidence["reject"]
                ),
                "uncertain": factor * combined["uncertain"] * evidence["uncertain"]
            }
            combined = new_combined
            
        return combined
```

### Step 6: Complete DAG Execution
```python
# Initialize registries
base_registry = ToolRegistry()
dynamic_registry = DynamicToolRegistry(base_registry)

# Extract theory and generate tool
theory_schema = extract_theory("Turner_1986.pdf")
mcr_algorithm = theory_schema['algorithms']['mathematical'][0]
generated_code = llm_generate_tool_code(mcr_algorithm)

# Register dynamic tool
mcr_tool_id = dynamic_registry.register_dynamic_tool(mcr_algorithm, generated_code)

# Create DAG with dynamic tool
dag = {
    "steps": [
        {
            "tool_id": "T01_PDF_LOADER",
            "operation": "load",
            "input": {"file": "twitter_data.pdf"}
        },
        {
            "tool_id": mcr_tool_id,  # Dynamic tool!
            "operation": "calculate",
            "input": "$previous.data"
        },
        {
            "tool_id": "TWEET_USER_AGGREGATOR",
            "operation": "aggregate",
            "input": "$previous.mcr_scores"
        }
    ]
}

# Execute DAG
executor = DAGExecutor(dynamic_registry)
result = executor.execute(dag)
```

## Key Integration Points

1. **ServiceManager Integration**: All tools (static and dynamic) get service access
2. **Provenance Tracking**: Wrapper records tool generation and execution
3. **Uncertainty Enhancement**: Base calculation + contextual assessment
4. **Registry Compatibility**: Dynamic tools work with existing registry
5. **Aggregation Pipeline**: Seamless flow from instance to population level

## Safety Considerations

```python
class SafeDynamicExecution:
    """Safety wrapper for dynamic code execution"""
    
    ALLOWED_IMPORTS = ['numpy', 'pandas', 'scipy']
    FORBIDDEN_OPERATIONS = ['exec', 'eval', '__import__', 'open', 'file']
    
    def validate_code(self, code: str) -> bool:
        """Validate generated code for safety"""
        # Check for forbidden operations
        for forbidden in self.FORBIDDEN_OPERATIONS:
            if forbidden in code:
                raise SecurityError(f"Forbidden operation: {forbidden}")
        
        # Validate imports
        import_lines = [l for l in code.split('\n') if 'import' in l]
        for line in import_lines:
            if not any(allowed in line for allowed in self.ALLOWED_IMPORTS):
                raise SecurityError(f"Unauthorized import: {line}")
        
        return True
    
    def sandboxed_execution(self, code: str, timeout: int = 5):
        """Execute in sandboxed environment with timeout"""
        # Would use subprocess with restricted permissions
        # and resource limits in production
        pass
```

## This Integration Enables

1. **Theory-agnostic execution**: Any formalized theory works
2. **Dynamic adaptation**: Tools generated as needed
3. **Consistent uncertainty**: All tools assess and propagate uncertainty
4. **Full traceability**: From paper → theory → code → execution → results
5. **Flexible aggregation**: Instance → population at any level