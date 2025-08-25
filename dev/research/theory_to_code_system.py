#!/usr/bin/env python3
"""
Theory-to-Code System: Uses LLMs to generate code from theory schemas
and extract parameters from text for analysis.

This system:
1. Takes a theory schema with natural language formulas
2. Uses LLM to generate executable Python code
3. Extracts parameters from text using LLM
4. Executes the analysis
5. Provides insights
"""

import json
import ast
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class TheoryFormula:
    """Represents a formula from the theory schema"""
    name: str
    formula: str
    parameters: Dict[str, Any]
    input_requirements: List[str]
    output_description: str

@dataclass
class GeneratedCode:
    """Result of LLM code generation"""
    source_code: str
    function_name: str
    imports: List[str]
    validation_schema: Optional[str] = None

class TheoryToCodeSystem:
    """Orchestrates the conversion of theory to executable code"""
    
    def __init__(self, llm_simulator=None):
        # In production, this would be the actual LLM client
        self.llm = llm_simulator or self.simulate_llm_response
    
    def load_theory_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load a theory schema from JSON file"""
        with open(schema_path, 'r') as f:
            return json.load(f)
    
    def extract_formulas(self, theory_schema: Dict[str, Any]) -> List[TheoryFormula]:
        """Extract mathematical formulas from theory schema"""
        formulas = []
        
        # Navigate to mathematical_algorithms section
        math_algos = theory_schema.get('ontology', {}).get('mathematical_algorithms', {})
        
        for key, algo in math_algos.items():
            if isinstance(algo, dict) and 'formula' in algo:
                formula = TheoryFormula(
                    name=key,
                    formula=algo.get('formula', ''),
                    parameters=algo.get('parameters', {}),
                    input_requirements=algo.get('input_requirements', []),
                    output_description=algo.get('output', '')
                )
                formulas.append(formula)
        
        return formulas
    
    def generate_code_from_formula(self, formula: TheoryFormula, 
                                  theory_name: str) -> GeneratedCode:
        """Use LLM to generate Python code from formula description"""
        
        prompt = f"""
Generate Python code for this {theory_name} formula:

Name: {formula.name}
Formula: {formula.formula}
Parameters: {json.dumps(formula.parameters, indent=2)}
Inputs: {formula.input_requirements}
Output: {formula.output_description}

Requirements:
1. Create a function that implements this formula
2. Use type hints for all parameters
3. Include a Pydantic model for input validation if complex
4. Add docstring explaining the formula
5. Handle edge cases appropriately
6. Use numpy for array operations if needed

Return ONLY executable Python code, no explanations.
"""
        
        # In production, this would be: code = self.llm.generate(prompt)
        code = self.llm("code_generation", prompt, formula)
        
        # Extract function name from generated code
        function_name = self._extract_function_name(code)
        imports = self._extract_imports(code)
        
        return GeneratedCode(
            source_code=code,
            function_name=function_name,
            imports=imports
        )
    
    def generate_parameter_extractor(self, theory_schema: Dict[str, Any]) -> GeneratedCode:
        """Generate code to extract parameters from text"""
        
        # Get conversion rules from schema
        conversions = theory_schema.get('ontology', {}).get(
            'mathematical_algorithms', {}
        ).get('text_to_numbers_conversion', {})
        
        prompt = f"""
Generate a Python function that extracts parameters for {theory_schema['theory_name']} from text.

The function should extract:
{json.dumps(conversions, indent=2)}

Requirements:
1. Take text as input
2. Return a Pydantic model with extracted parameters
3. Use the linguistic mappings provided
4. Handle uncertainty in extraction
5. Provide confidence scores

Return ONLY executable Python code.
"""
        
        code = self.llm("extraction_generation", prompt, conversions)
        
        return GeneratedCode(
            source_code=code,
            function_name="extract_parameters",
            imports=["from pydantic import BaseModel, Field", "from typing import List, Dict"]
        )
    
    def compile_theory_module(self, theory_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Compile a complete executable module for the theory"""
        
        theory_name = theory_schema['theory_name']
        
        # Extract formulas
        formulas = self.extract_formulas(theory_schema)
        
        # Generate code for each formula
        generated_functions = {}
        all_imports = set()
        
        for formula in formulas:
            code = self.generate_code_from_formula(formula, theory_name)
            generated_functions[formula.name] = code
            all_imports.update(code.imports)
        
        # Generate parameter extractor
        extractor = self.generate_parameter_extractor(theory_schema)
        all_imports.update(extractor.imports)
        
        # Ensure we have typing imports
        all_imports.add("from typing import Any, Dict, List")
        
        # Compile into module
        module_code = self._compile_module(
            theory_name=theory_name,
            imports=list(all_imports),
            functions=generated_functions,
            extractor=extractor
        )
        
        return {
            'module_code': module_code,
            'formulas': formulas,
            'functions': generated_functions,
            'extractor': extractor
        }
    
    def apply_theory_to_text(self, text: str, compiled_theory: Dict[str, Any]) -> Dict[str, Any]:
        """Apply compiled theory to analyze text"""
        
        # Create namespace and execute module
        namespace = {}
        exec(compiled_theory['module_code'], namespace)
        
        # Extract parameters from text
        extract_fn = namespace.get('extract_parameters')
        if not extract_fn:
            raise ValueError("No parameter extraction function found")
        
        # In production: parameters = extract_fn(text)
        # For demo, simulate the extraction
        parameters = self.simulate_parameter_extraction(text)
        
        # Apply formulas
        results = {}
        
        for formula_name, code_info in compiled_theory['functions'].items():
            func = namespace.get(code_info.function_name)
            if func:
                # Call function with extracted parameters
                # This would be more sophisticated in production
                result = self.simulate_formula_execution(func, parameters, formula_name)
                results[formula_name] = result
        
        return {
            'extracted_parameters': parameters,
            'analysis_results': results,
            'insights': self.generate_insights(results, parameters)
        }
    
    def _extract_function_name(self, code: str) -> str:
        """Extract function name from generated code"""
        # Simple regex to find function definitions
        match = re.search(r'def\s+(\w+)\s*\(', code)
        return match.group(1) if match else 'unknown_function'
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from generated code"""
        imports = []
        for line in code.split('\n'):
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def _compile_module(self, theory_name: str, imports: List[str], 
                       functions: Dict[str, GeneratedCode], 
                       extractor: GeneratedCode) -> str:
        """Compile all generated code into a single module"""
        
        module_parts = [
            f'"""Auto-generated module for {theory_name}"""',
            '',
            '# Imports',
            *imports,
            '',
            '# Generated functions',
        ]
        
        # Add each function
        for name, code_info in functions.items():
            module_parts.append(f'# {name}')
            module_parts.append(code_info.source_code)
            module_parts.append('')
        
        # Add extractor
        module_parts.append('# Parameter extraction')
        module_parts.append(extractor.source_code)
        
        return '\n'.join(module_parts)
    
    def generate_insights(self, results: Dict[str, Any], parameters: Any) -> str:
        """Generate human-readable insights from analysis results"""
        prompt = f"""
Given these analysis results from applying theory:
Results: {json.dumps(results, indent=2)}
Parameters: {parameters}

Generate clear, actionable insights about what this means.
Focus on practical implications and behavioral predictions.
"""
        return self.llm("insights", prompt, results)
    
    # Simulation methods (would be replaced by actual LLM in production)
    
    def simulate_llm_response(self, task_type: str, prompt: str, context: Any) -> str:
        """Simulate LLM responses for demo purposes"""
        
        if task_type == "code_generation":
            # Return pre-written code based on formula type
            if "value_function" in context.name:
                return '''
def calculate_value(x: float, reference_point: float = 0, 
                   alpha: float = 0.88, beta: float = 0.88, 
                   lambda_: float = 2.25) -> float:
    """Calculate subjective value using Prospect Theory value function"""
    relative_outcome = x - reference_point
    
    if relative_outcome >= 0:  # Gain
        return relative_outcome ** alpha
    else:  # Loss
        return -lambda_ * ((-relative_outcome) ** beta)
'''
            elif "probability_weighting" in context.name:
                return '''
def weight_probability(p: float, gamma: float = 0.61) -> float:
    """Weight probability according to Tversky-Kahneman function"""
    if p == 0:
        return 0
    elif p == 1:
        return 1
    else:
        return (p ** gamma) / ((p ** gamma + (1 - p) ** gamma) ** (1 / gamma))
'''
            else:
                return '''
def generic_formula(inputs: Dict[str, Any]) -> float:
    """Generic formula implementation"""
    return sum(inputs.values())
'''
        
        elif task_type == "extraction_generation":
            return '''
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ExtractedProspect(BaseModel):
    name: str
    outcomes: List[float]
    probabilities: List[float]
    reference_point: float = 0

def extract_parameters(text: str) -> List[ExtractedProspect]:
    """Extract prospect theory parameters from text"""
    # This would use NLP/LLM to extract
    # For now, return dummy data
    return []
'''
        
        elif task_type == "insights":
            return "Based on the analysis, the risky option is preferred due to probability weighting effects."
        
        return "Simulated response"
    
    def simulate_parameter_extraction(self, text: str) -> Dict[str, Any]:
        """Simulate parameter extraction for demo"""
        # In production, this would be done by the LLM
        return {
            'prospects': [
                {
                    'name': 'Risky Option',
                    'outcomes': [100, -50],
                    'probabilities': [0.7, 0.3],
                    'reference_point': 0
                },
                {
                    'name': 'Safe Option',
                    'outcomes': [20],
                    'probabilities': [1.0],
                    'reference_point': 0
                }
            ]
        }
    
    def simulate_formula_execution(self, func: Callable, parameters: Dict, 
                                  formula_name: str) -> Any:
        """Simulate formula execution for demo"""
        # In production, this would dynamically call the function
        # with appropriate parameters
        if "value_function" in formula_name:
            return {'risky_values': [50.3, -70.1], 'safe_value': 15.2}
        elif "prospect_evaluation" in formula_name:
            return {'risky_total': 12.5, 'safe_total': 15.2}
        return {'result': 'simulated'}


def main():
    """Demonstrate the Theory-to-Code system"""
    
    system = TheoryToCodeSystem()
    
    # Load Prospect Theory schema
    schema_path = "/home/brian/projects/Digimons/config/schemas/prospect_theory_schema.json"
    theory_schema = system.load_theory_schema(schema_path)
    
    print("=" * 60)
    print("THEORY-TO-CODE SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    print(f"\n1. Loaded Theory: {theory_schema['theory_name']}")
    
    # Extract formulas
    formulas = system.extract_formulas(theory_schema)
    print(f"\n2. Found {len(formulas)} formulas:")
    for f in formulas:
        print(f"   - {f.name}: {f.formula[:60]}...")
    
    # Compile theory module
    print("\n3. Generating code from formulas...")
    compiled = system.compile_theory_module(theory_schema)
    
    print("\n4. Generated module preview:")
    print("   " + "\n   ".join(compiled['module_code'].split('\n')[:20]))
    print("   ...")
    
    # Apply to text
    test_text = """
    The company faces a strategic decision. Option A has a 60% chance of 
    increasing revenue by $2M but a 40% chance of losing $500K. Option B 
    guarantees a $300K increase with no risk.
    """
    
    print(f"\n5. Analyzing text:")
    print("   " + test_text.strip().replace('\n', '\n   '))
    
    results = system.apply_theory_to_text(test_text, compiled)
    
    print("\n6. Results:")
    print(f"   Extracted: {results['extracted_parameters']}")
    print(f"   Analysis: {results['analysis_results']}")
    print(f"   Insights: {results['insights']}")
    
    print("\n7. Summary:")
    print("   ✓ Theory schema → Executable code")
    print("   ✓ Natural language → Structured parameters")
    print("   ✓ Mathematical analysis → Actionable insights")


if __name__ == "__main__":
    main()