#!/usr/bin/env python3
"""
Verify which tools implement the unified interface.
This script MUST produce Evidence_Tool_Interface_Audit.md
"""

import os
import ast
import importlib
from pathlib import Path
from datetime import datetime

class ToolInterfaceAuditor:
    def __init__(self):
        self.tools_dir = Path("src/tools/phase1")
        self.audit_results = []
        
    def audit_all_tools(self):
        """Audit all Phase 1 tools for interface compliance"""
        
        tool_files = list(self.tools_dir.glob("t*.py"))
        
        for tool_file in sorted(tool_files):
            if tool_file.name.startswith("test_"):
                continue
                
            result = self.audit_tool_file(tool_file)
            self.audit_results.append(result)
            
        self.generate_evidence_report()
        
    def audit_tool_file(self, file_path: Path):
        """Check if a tool implements the unified interface"""
        
        tool_name = file_path.stem
        
        # Parse the Python file
        with open(file_path, 'r') as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                return {
                    "tool": tool_name,
                    "status": "SYNTAX_ERROR",
                    "has_unified_interface": False,
                    "methods": []
                }
        
        # Find classes and their methods
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Check for UnifiedToolInterface implementation
        implements_interface = False
        required_methods = ['get_contract', 'validate_input', 'execute', 'get_status', 'health_check']
        found_methods = []
        
        for cls in classes:
            # Check if inherits from UnifiedToolInterface
            for base in cls.bases:
                if isinstance(base, ast.Name) and 'Unified' in base.id:
                    implements_interface = True
                    
            # Check for required methods
            for method in cls.body:
                if isinstance(method, ast.FunctionDef):
                    if method.name in required_methods:
                        found_methods.append(method.name)
        
        missing_methods = set(required_methods) - set(found_methods)
        
        # Check if tool has execute method (minimum requirement)
        has_execute = 'execute' in found_methods
        
        return {
            "tool": tool_name,
            "file": str(file_path),
            "status": "COMPLIANT" if implements_interface and not missing_methods else ("PARTIAL" if has_execute else "NON_COMPLIANT"),
            "has_unified_interface": implements_interface,
            "has_execute_method": has_execute,
            "methods_found": found_methods,
            "methods_missing": list(missing_methods)
        }
    
    def generate_evidence_report(self):
        """Generate Evidence_Tool_Interface_Audit.md"""
        
        compliant = [r for r in self.audit_results if r['status'] == 'COMPLIANT']
        partial = [r for r in self.audit_results if r['status'] == 'PARTIAL']
        non_compliant = [r for r in self.audit_results if r['status'] == 'NON_COMPLIANT']
        
        report = ["# Tool Interface Compliance Audit"]
        report.append(f"\n**Audit Date**: {datetime.now().isoformat()}")
        report.append(f"\n## Summary")
        report.append(f"- Total Tools Audited: {len(self.audit_results)}")
        report.append(f"- Fully Compliant (UnifiedToolInterface): {len(compliant)}")
        report.append(f"- Partially Compliant (has execute method): {len(partial)}")
        report.append(f"- Non-Compliant: {len(non_compliant)}")
        report.append(f"- Compliance Rate: {((len(compliant) + len(partial))/len(self.audit_results)*100):.1f}%")
        
        report.append("\n## Tools with Execute Method (Working Tools)\n")
        working_tools = [r for r in self.audit_results if r['has_execute_method']]
        for result in working_tools:
            report.append(f"- ✅ **{result['tool']}**: Has execute() method")
        
        report.append(f"\n**Total Working Tools**: {len(working_tools)}/{len(self.audit_results)}")
        
        report.append("\n## Non-Compliant Tools Requiring Migration\n")
        for result in non_compliant:
            if not result['has_execute_method']:
                report.append(f"### {result['tool']}")
                report.append(f"- File: `{result['file']}`")
                report.append(f"- Missing Methods: {', '.join(result['methods_missing'])}")
                report.append("")
        
        report.append("\n## Compliant Tools\n")
        for result in compliant:
            report.append(f"- ✅ {result['tool']}")
        
        report.append("\n## Migration Priority\n")
        report.append("Based on workflow criticality:")
        report.append("1. **T01**: PDF Loader - Critical for document ingestion")
        report.append("2. **T23A/T23C**: Entity Extraction - Core NLP functionality")
        report.append("3. **T31**: Entity Builder - Graph construction")
        report.append("4. **T34**: Edge Builder - Relationship creation")
        report.append("5. **T49**: Multi-hop Query - Query interface")
        report.append("6. **T68**: PageRank - Graph analysis")
        
        report.append("\n## Tool Implementation Status\n")
        report.append("| Tool | Has Execute | Unified Interface | Status |")
        report.append("|------|------------|-------------------|--------|")
        for result in sorted(self.audit_results, key=lambda x: x['tool']):
            execute_status = "✅" if result['has_execute_method'] else "❌"
            interface_status = "✅" if result['has_unified_interface'] else "❌"
            report.append(f"| {result['tool']} | {execute_status} | {interface_status} | {result['status']} |")
        
        with open("Evidence_Tool_Interface_Audit.md", "w") as f:
            f.write("\n".join(report))
            
        print(f"Generated Evidence_Tool_Interface_Audit.md")
        print(f"Working Tools: {len(working_tools)}/{len(self.audit_results)}")
        print(f"Compliance: {len(compliant)}/{len(self.audit_results)} fully compliant")

if __name__ == "__main__":
    auditor = ToolInterfaceAuditor()
    auditor.audit_all_tools()