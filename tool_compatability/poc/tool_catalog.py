#!/usr/bin/env python3
"""
Tool Catalog: Scan and analyze all 37 existing tools
Generates inventory for integration into KGAS framework
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class ToolInfo:
    """Information about a discovered tool"""
    tool_id: str
    file_path: str
    class_name: str
    methods: List[str]
    dependencies: List[str]
    has_process_method: bool
    has_run_method: bool
    input_type: str  # Inferred from code
    output_type: str  # Inferred from code
    transformation_type: str  # Inferred from docstring
    integration_status: str  # ready, needs_adapter, complex

class ToolCatalog:
    """Scan and catalog existing tools for framework integration"""
    
    def __init__(self, tools_dir: str = "/home/brian/projects/Digimons/src/tools"):
        self.tools_dir = Path(tools_dir)
        self.tools: Dict[str, ToolInfo] = {}
        
    def scan_tools(self) -> Dict[str, ToolInfo]:
        """Scan all Python files in tools directory"""
        print("=== Tool Catalog Scanner ===\n")
        
        for py_file in sorted(self.tools_dir.glob("*.py")):
            if py_file.name.startswith("__"):
                continue
                
            tool_id = py_file.stem
            print(f"Scanning {tool_id}...")
            
            try:
                tool_info = self._analyze_tool_file(py_file)
                if tool_info:
                    self.tools[tool_id] = tool_info
                    print(f"  ✅ {tool_info.class_name} - {tool_info.integration_status}")
            except Exception as e:
                print(f"  ❌ Error analyzing {tool_id}: {e}")
        
        return self.tools
    
    def _analyze_tool_file(self, file_path: Path) -> ToolInfo:
        """Analyze a single tool file using AST"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return None
        
        # Find main class
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if not classes:
            return None
        
        main_class = classes[0]  # Assume first class is the main tool
        
        # Extract methods
        methods = []
        has_process = False
        has_run = False
        
        for node in main_class.body:
            if isinstance(node, ast.FunctionDef):
                methods.append(node.name)
                if node.name == "process":
                    has_process = True
                elif node.name == "run":
                    has_run = True
        
        # Extract imports (dependencies)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Infer input/output types from method signatures and docstrings
        input_type, output_type = self._infer_data_types(main_class)
        
        # Determine transformation type from docstring
        transformation = self._extract_transformation_type(main_class)
        
        # Determine integration status
        if has_process:
            status = "ready"  # Can use directly
        elif has_run:
            status = "needs_adapter"  # Need to wrap run() method
        else:
            status = "complex"  # Needs custom integration
        
        return ToolInfo(
            tool_id=file_path.stem,
            file_path=str(file_path),
            class_name=main_class.name,
            methods=methods[:10],  # Limit to first 10 methods
            dependencies=list(set(imports))[:10],  # Unique, limited
            has_process_method=has_process,
            has_run_method=has_run,
            input_type=input_type,
            output_type=output_type,
            transformation_type=transformation,
            integration_status=status
        )
    
    def _infer_data_types(self, class_node: ast.ClassDef) -> tuple:
        """Infer input/output types from method signatures"""
        input_type = "unknown"
        output_type = "unknown"
        
        # Check for process or run method
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name in ["process", "run"]:
                    # Check parameters
                    if len(node.args.args) > 1:  # Skip 'self'
                        param = node.args.args[1]
                        if hasattr(param, 'annotation'):
                            # Has type hint
                            input_type = ast.unparse(param.annotation) if hasattr(ast, 'unparse') else "typed"
                        else:
                            # Infer from parameter name
                            param_name = param.arg
                            if "text" in param_name.lower():
                                input_type = "text"
                            elif "file" in param_name.lower():
                                input_type = "file"
                            elif "data" in param_name.lower():
                                input_type = "data"
                            elif "graph" in param_name.lower():
                                input_type = "graph"
                    
                    # Check return type
                    if node.returns:
                        output_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else "typed"
                    else:
                        # Check for return statements
                        for child in ast.walk(node):
                            if isinstance(child, ast.Return) and child.value:
                                if isinstance(child.value, ast.Dict):
                                    output_type = "dict"
                                elif isinstance(child.value, ast.List):
                                    output_type = "list"
                                elif isinstance(child.value, ast.Str):
                                    output_type = "str"
                                break
        
        return input_type, output_type
    
    def _extract_transformation_type(self, class_node: ast.ClassDef) -> str:
        """Extract transformation type from class docstring"""
        docstring = ast.get_docstring(class_node)
        if not docstring:
            return "unknown"
        
        # Look for keywords in docstring
        docstring_lower = docstring.lower()
        
        if "extract" in docstring_lower:
            if "entity" in docstring_lower or "knowledge" in docstring_lower:
                return "entity_extraction"
            elif "text" in docstring_lower:
                return "text_extraction"
            else:
                return "extraction"
        elif "embed" in docstring_lower or "vector" in docstring_lower:
            return "vectorization"
        elif "persist" in docstring_lower or "store" in docstring_lower:
            return "persistence"
        elif "load" in docstring_lower or "read" in docstring_lower:
            return "data_loading"
        elif "process" in docstring_lower:
            return "processing"
        elif "analyze" in docstring_lower:
            return "analysis"
        elif "convert" in docstring_lower or "transform" in docstring_lower:
            return "conversion"
        else:
            return "processing"
    
    def generate_report(self, output_path: str = "tool_inventory.json"):
        """Generate inventory report"""
        if not self.tools:
            print("No tools scanned yet. Run scan_tools() first.")
            return
        
        # Statistics
        total = len(self.tools)
        ready = sum(1 for t in self.tools.values() if t.integration_status == "ready")
        needs_adapter = sum(1 for t in self.tools.values() if t.integration_status == "needs_adapter")
        complex_integration = sum(1 for t in self.tools.values() if t.integration_status == "complex")
        
        print("\n=== Tool Inventory Report ===")
        print(f"Total tools discovered: {total}")
        print(f"Ready for integration: {ready}")
        print(f"Need adapter: {needs_adapter}")
        print(f"Complex integration: {complex_integration}")
        
        # Group by transformation type
        by_transformation = {}
        for tool in self.tools.values():
            if tool.transformation_type not in by_transformation:
                by_transformation[tool.transformation_type] = []
            by_transformation[tool.transformation_type].append(tool.tool_id)
        
        print("\n=== Tools by Transformation Type ===")
        for trans_type, tool_ids in sorted(by_transformation.items()):
            print(f"{trans_type}: {len(tool_ids)} tools")
            for tid in tool_ids[:5]:  # Show first 5
                print(f"  - {tid}")
            if len(tool_ids) > 5:
                print(f"  ... and {len(tool_ids) - 5} more")
        
        # Group by input type
        by_input = {}
        for tool in self.tools.values():
            if tool.input_type not in by_input:
                by_input[tool.input_type] = []
            by_input[tool.input_type].append(tool.tool_id)
        
        print("\n=== Tools by Input Type ===")
        for input_type, tool_ids in sorted(by_input.items()):
            print(f"{input_type}: {len(tool_ids)} tools")
        
        # Save to JSON
        report = {
            "statistics": {
                "total_tools": total,
                "ready": ready,
                "needs_adapter": needs_adapter,
                "complex": complex_integration
            },
            "by_transformation": by_transformation,
            "by_input": by_input,
            "tools": {k: asdict(v) for k, v in self.tools.items()}
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved to {output_path}")
        
        # Generate integration priority list
        print("\n=== Integration Priority ===")
        print("Phase 1 (Ready tools):")
        for tool_id, tool in list(self.tools.items())[:10]:
            if tool.integration_status == "ready":
                print(f"  {tool_id}: {tool.class_name} - {tool.transformation_type}")
        
        print("\nPhase 2 (Need adapter):")
        for tool_id, tool in list(self.tools.items())[:10]:
            if tool.integration_status == "needs_adapter":
                print(f"  {tool_id}: {tool.class_name} - {tool.transformation_type}")
        
        return report
    
    def generate_integration_code(self, tool_id: str) -> str:
        """Generate integration code snippet for a specific tool"""
        if tool_id not in self.tools:
            return f"Tool {tool_id} not found"
        
        tool = self.tools[tool_id]
        
        code = f"""
# Integration code for {tool_id}
from src.tools.{tool_id} import {tool.class_name}
from tool_compatability.poc.vertical_slice.framework.clean_framework import DataType, ToolCapabilities

# Create tool instance
tool = {tool.class_name}()

# Determine data types based on analysis
input_type = DataType.{self._map_to_datatype(tool.input_type)}
output_type = DataType.{self._map_to_datatype(tool.output_type)}

# Register with framework
capabilities = ToolCapabilities(
    tool_id="{tool_id}",
    input_type=input_type,
    output_type=output_type,
    input_construct="{tool.input_type}_data",
    output_construct="{tool.output_type}_data",
    transformation_type="{tool.transformation_type}"
)

framework.register_tool(tool, capabilities)
"""
        
        if tool.integration_status == "needs_adapter":
            code += f"""
# Note: This tool needs an adapter to wrap the run() method
class {tool.class_name}Adapter:
    def __init__(self):
        self.tool = {tool.class_name}()
    
    def process(self, data):
        # Adapter to convert run() to process()
        result = self.tool.run(data)
        return {{
            'success': True,
            'data': result,
            'uncertainty': 0.1,  # Configure based on tool
            'reasoning': '{tool.transformation_type} operation',
            'construct_mapping': '{tool.input_type} → {tool.output_type}'
        }}

# Use adapter instead
adapted_tool = {tool.class_name}Adapter()
framework.register_tool(adapted_tool, capabilities)
"""
        
        return code
    
    def _map_to_datatype(self, type_str: str) -> str:
        """Map inferred type to DataType enum"""
        type_map = {
            "text": "TEXT",
            "str": "TEXT",
            "file": "FILE",
            "graph": "KNOWLEDGE_GRAPH",
            "dict": "TABLE",
            "list": "TABLE",
            "vector": "VECTOR",
            "data": "TABLE"
        }
        return type_map.get(type_str.lower(), "TEXT")


def main():
    """Run tool catalog scan and generate report"""
    # Scan current tools
    print("=== Scanning Current Tools ===")
    catalog_current = ToolCatalog("/home/brian/projects/Digimons/src/tools")
    current_tools = catalog_current.scan_tools()
    
    # Scan legacy tools (T01-T85)
    print("\n=== Scanning Legacy Tools (T01-T85) ===")
    catalog_legacy = ToolCatalog("/home/brian/projects/Digimons/archive/archived/legacy_tools_2025_07_23")
    legacy_tools = catalog_legacy.scan_tools()
    
    # Combine catalogs
    catalog = ToolCatalog()
    catalog.tools = {**current_tools, **legacy_tools}
    
    # Generate combined report
    catalog.generate_report("combined_tool_inventory.json")
    
    # Show sample integration code
    print("\n=== Sample Integration Code ===")
    # Get some T-series tools for examples
    t_tools = [k for k in catalog.tools.keys() if k.startswith('t')][:3]
    for tool_id in t_tools:
        print(f"\n--- {tool_id} ---")
        print(catalog.generate_integration_code(tool_id))
        print()
    
    return catalog

if __name__ == "__main__":
    catalog = main()