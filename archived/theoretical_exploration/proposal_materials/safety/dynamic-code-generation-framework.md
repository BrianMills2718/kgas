# Safe Dynamic Code Generation Framework
*Extracted from proposal materials - 2025-08-29*  
*Status: Safety Architecture - Phase 2 Implementation*

## Overview

This document specifies a comprehensive safety framework for dynamic tool generation in KGAS Phase 2 implementation. The framework enables LLM-generated executable analysis tools while maintaining research-grade security and reliability standards.

**Purpose**: Enable theory-driven dynamic tool generation without compromising system security or research integrity.

## Core Safety Principles

1. **Restricted Operations**: Limited to mathematical/analytical operations
2. **Sandboxed Execution**: Isolated environment with resource limits  
3. **Code Validation**: Pre-execution safety checks
4. **Type Safety**: Strong typing and validation
5. **Audit Trail**: Complete logging of generation and execution

## Architecture Components

### 1. Code Generation Templates

```python
class ToolCodeTemplate:
    """Safe templates for LLM code generation"""
    
    BASE_TEMPLATE = '''
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from src.core.tool_contract import KGASTool, ToolRequest, ToolResult

class Generated{name}Tool(KGASTool):
    """Auto-generated tool for {description}"""
    
    ALLOWED_OPERATIONS = ['add', 'subtract', 'multiply', 'divide', 'mean', 'sum', 'norm']
    
    def __init__(self, service_manager):
        super().__init__(service_manager)
        self.tool_id = "{tool_id}"
        self.formula = "{formula}"
        
    def execute(self, request: ToolRequest) -> ToolResult:
        try:
            # Validate input
            self._validate_input(request.input_data)
            
            # Execute calculation
            result = self._calculate(request.input_data)
            
            # Assess uncertainty
            uncertainty = self._assess_uncertainty(request.input_data, result)
            
            return ToolResult(
                status="success",
                data=result,
                metadata={{"uncertainty": uncertainty, "formula": self.formula}}
            )
        except Exception as e:
            return ToolResult(
                status="error",
                error_details={{"message": str(e), "type": type(e).__name__}}
            )
    
    def _validate_input(self, data: Dict) -> None:
        """Validate input data structure"""
        required_fields = {required_fields}
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {{field}}")
    
    def _calculate(self, data: Dict) -> Dict:
        """Perform the calculation"""
        {calculation_code}
    
    def _assess_uncertainty(self, input_data: Dict, result: Dict) -> Dict:
        """Assess calculation uncertainty"""
        {uncertainty_code}
'''
```

#### Example: Meta-Contrast Ratio Generator

```python
@staticmethod
def generate_mcr_calculation_code(formula_spec: Dict) -> str:
    """Generate safe MCR calculation from formula specification"""
    return '''
    individuals = data['individuals']
    positions = data['position_vectors']
    groups = data['group_assignments']
    
    results = {}
    for ind_id in individuals:
        if ind_id not in positions:
            continue
            
        ind_pos = np.array(positions[ind_id])
        ind_group = groups.get(ind_id)
        
        # Calculate with numpy (safe operations only)
        ingroup_distances = []
        outgroup_distances = []
        
        for other_id in individuals:
            if other_id == ind_id or other_id not in positions:
                continue
            other_pos = np.array(positions[other_id])
            distance = np.linalg.norm(ind_pos - other_pos)
            
            if groups.get(other_id) == ind_group:
                ingroup_distances.append(distance)
            else:
                outgroup_distances.append(distance)
        
        # Safe division with zero check
        in_sum = np.sum(ingroup_distances) if ingroup_distances else 0
        out_sum = np.sum(outgroup_distances) if outgroup_distances else 0
        
        if in_sum > 0:
            results[ind_id] = out_sum / in_sum
        else:
            results[ind_id] = np.inf
            
    return {"scores": results}
    '''
```

### 2. Code Validator

```python
import ast
import re

class CodeValidator:
    """Validate generated code for safety"""
    
    FORBIDDEN_BUILTINS = [
        'exec', 'eval', 'compile', '__import__', 
        'open', 'file', 'input', 'raw_input',
        'execfile', 'reload', 'globals', 'locals'
    ]
    
    FORBIDDEN_MODULES = [
        'os', 'sys', 'subprocess', 'socket', 
        'urllib', 'requests', 'pickle', 'shelve'
    ]
    
    ALLOWED_MODULES = [
        'numpy', 'pandas', 'scipy', 'math', 
        'typing', 'dataclasses', 'enum'
    ]
    
    def validate(self, code: str) -> tuple[bool, List[str]]:
        """Validate code for safety issues"""
        issues = []
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]
        
        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_allowed_import(alias.name):
                        issues.append(f"Forbidden import: {alias.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if not self._is_allowed_import(node.module):
                    issues.append(f"Forbidden import from: {node.module}")
            
            # Check for dangerous function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_BUILTINS:
                        issues.append(f"Forbidden builtin: {node.func.id}")
        
        # Check for file operations
        if re.search(r'\bopen\s*\(', code):
            issues.append("File operations not allowed")
        
        # Check for network operations
        if any(module in code for module in ['socket', 'urllib', 'requests']):
            issues.append("Network operations not allowed")
        
        return len(issues) == 0, issues
    
    def _is_allowed_import(self, module_name: str) -> bool:
        """Check if module is allowed"""
        if not module_name:
            return False
        
        # Check forbidden modules
        if any(forbidden in module_name for forbidden in self.FORBIDDEN_MODULES):
            return False
        
        # Check allowed modules and submodules
        return any(module_name.startswith(allowed) for allowed in self.ALLOWED_MODULES)
```

### 3. Sandboxed Executor

```python
import subprocess
import tempfile
import json
import timeout_decorator

class SandboxedExecutor:
    """Execute generated code in sandboxed environment"""
    
    def __init__(self, max_memory_mb=512, max_cpu_seconds=5):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.max_cpu = max_cpu_seconds
    
    def execute_tool(self, tool_code: str, input_data: Dict) -> Dict:
        """Execute tool code with resource limits"""
        
        # Create execution wrapper
        wrapper_code = self._create_wrapper(tool_code, input_data)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(wrapper_code)
            temp_file = f.name
        
        try:
            # Execute with resource limits
            result = self._run_with_limits(temp_file)
            return json.loads(result)
        finally:
            # Clean up
            import os
            os.unlink(temp_file)
    
    def _create_wrapper(self, tool_code: str, input_data: Dict) -> str:
        """Create wrapper script for execution"""
        return f'''
import json
import sys
import resource

# Set resource limits
resource.setrlimit(resource.RLIMIT_AS, ({self.max_memory}, {self.max_memory}))
resource.setrlimit(resource.RLIMIT_CPU, ({self.max_cpu}, {self.max_cpu}))

# Import required modules
import numpy as np
import pandas as pd
from dataclasses import dataclass

# Mock tool infrastructure
@dataclass
class ToolRequest:
    input_data: dict

@dataclass  
class ToolResult:
    status: str
    data: dict = None
    metadata: dict = None
    error_details: dict = None

class KGASTool:
    def __init__(self, service_manager=None):
        self.service_manager = service_manager

# Generated tool code
{tool_code}

# Execute tool
try:
    tool = GeneratedTool(None)
    request = ToolRequest(input_data={json.dumps(input_data)})
    result = tool.execute(request)
    
    output = {{
        "status": result.status,
        "data": result.data,
        "metadata": result.metadata
    }}
    print(json.dumps(output))
except Exception as e:
    output = {{
        "status": "error",
        "error": str(e)
    }}
    print(json.dumps(output))
'''
    
    @timeout_decorator.timeout(10)  # Hard timeout
    def _run_with_limits(self, script_path: str) -> str:
        """Run script with subprocess and limits"""
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            check=False,
            env={'PYTHONPATH': ''}  # Clean environment
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Execution failed: {result.stderr}")
        
        return result.stdout
```

### 4. Complete Generation Pipeline

```python
class SafeCodeGenerationPipeline:
    """Complete pipeline for safe code generation"""
    
    def __init__(self, llm_client, validator, executor):
        self.llm = llm_client
        self.validator = validator
        self.executor = executor
        self.audit_log = []
    
    def generate_and_execute(self, algorithm_spec: Dict, input_data: Dict) -> Dict:
        """Generate, validate, and execute tool code"""
        
        # Step 1: Generate code
        code = self._generate_code(algorithm_spec)
        self._log("code_generated", {"algorithm": algorithm_spec['name']})
        
        # Step 2: Validate code
        is_valid, issues = self.validator.validate(code)
        if not is_valid:
            self._log("validation_failed", {"issues": issues})
            raise ValueError(f"Code validation failed: {issues}")
        self._log("code_validated", {"algorithm": algorithm_spec['name']})
        
        # Step 3: Execute in sandbox
        try:
            result = self.executor.execute_tool(code, input_data)
            self._log("execution_success", {"algorithm": algorithm_spec['name']})
            return result
        except Exception as e:
            self._log("execution_failed", {"error": str(e)})
            raise
    
    def _generate_code(self, algorithm_spec: Dict) -> str:
        """Generate code using LLM with safety constraints"""
        
        prompt = f"""
        Generate Python code for this algorithm:
        {json.dumps(algorithm_spec, indent=2)}
        
        Requirements:
        1. Use only numpy, pandas for calculations
        2. No file I/O, network operations, or system calls
        3. Include input validation
        4. Return results as dictionary
        5. Assess uncertainty based on data completeness
        
        Use this template structure:
        - Class inheriting from KGASTool
        - execute() method taking ToolRequest
        - Returns ToolResult with data and uncertainty
        """
        
        code = self.llm.generate(prompt, temperature=0.1)  # Low temperature for consistency
        return code
    
    def _log(self, event: str, details: Dict):
        """Audit logging"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "details": details
        })
```

## Safety Guarantees

### Security Restrictions
1. **No System Access**: Forbidden `os`, `sys`, `subprocess` modules
2. **No Network Operations**: Blocked `urllib`, `requests`, `socket`
3. **No File I/O**: Prevented `open`, file operations
4. **Resource Limits**: Memory (512MB) and CPU (5 seconds) constraints
5. **Timeout Protection**: Hard execution timeout (10 seconds)
6. **Input Validation**: Required fields verification
7. **Error Isolation**: Exceptions caught and safely reported

### Execution Environment
- **Clean Python Environment**: No system modules available
- **Limited Module Set**: Only numpy, pandas, scipy, math, typing
- **Subprocess Isolation**: Generated code runs in separate process
- **Resource Monitoring**: Memory and CPU usage constraints
- **Automatic Cleanup**: Temporary files removed after execution

## Usage Example

```python
# Initialize pipeline
pipeline = SafeCodeGenerationPipeline(
    llm_client=LLMClient(),
    validator=CodeValidator(),
    executor=SandboxedExecutor()
)

# Generate and execute MCR tool
algorithm = {
    "name": "meta_contrast_ratio",
    "formula": "MCR = sum(out_distances) / sum(in_distances)",
    "parameters": ["positions", "groups"],
    "description": "Calculate meta-contrast ratio for Self-Categorization Theory"
}

input_data = {
    "individuals": ["A", "B", "C"],
    "position_vectors": {"A": [1, 2], "B": [2, 3], "C": [5, 6]},
    "group_assignments": {"A": 1, "B": 1, "C": 2}
}

try:
    result = pipeline.generate_and_execute(algorithm, input_data)
    print(f"MCR calculation result: {result}")
except Exception as e:
    print(f"Generation/execution failed: {e}")
```

## Security Considerations

### Defense in Depth
- **Multiple Validation Layers**: AST parsing, regex checks, runtime limits
- **Least Privilege**: Minimal permissions in sandbox environment
- **Audit Trail**: Complete logging of generation, validation, execution
- **Fail Secure**: Default to rejection on any security doubt
- **Regular Updates**: Keep forbidden module lists current

### Risk Mitigation
- **Code Review**: Generated code can be inspected before execution
- **Version Control**: All generated tools tracked and versioned
- **Performance Monitoring**: Resource usage tracking and alerts
- **Error Reporting**: Detailed failure analysis for debugging
- **Rollback Capability**: Ability to disable problematic generated tools

## Integration with KGAS Architecture

### Phase 2 Implementation
- **Theory Extraction**: LLM extracts algorithms from academic papers
- **Schema Validation**: Algorithm specs validated against theory meta-schema
- **Tool Generation**: Safe code generation from validated algorithm specs
- **Runtime Integration**: Generated tools integrate with existing KGASTool interface
- **Uncertainty Assessment**: Generated tools assess their own reliability

### Workflow Integration
```python
# Phase 2 Dynamic Tool Workflow
theory_schema = extract_theory_from_paper(pdf_file)
algorithms = theory_schema['algorithms']['mathematical']

for algorithm in algorithms:
    # Generate safe tool implementation
    generated_tool = pipeline.generate_and_execute(algorithm, test_data)
    
    # Register with tool framework
    tool_registry.register_generated_tool(generated_tool)
    
    # Enable in workflow orchestration
    workflow_dag.add_tool_option(generated_tool.tool_id)
```

### Quality Assurance
- **Test Suite**: Comprehensive testing of generated tools
- **Validation Benchmarks**: Known algorithm implementations for comparison
- **Research Standards**: Generated tools meet academic research quality requirements
- **Reproducibility**: Generated tools produce consistent results across runs

---

**Status**: Safety framework ready for Phase 2 implementation. Provides research-grade security for LLM-generated executable analysis tools while maintaining KGAS integration compatibility.

**Next Steps**: Integrate with theory extraction pipeline and tool registry when Phase 1 demonstrates architectural feasibility.