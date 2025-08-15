#!/usr/bin/env python3
"""
Tool Interface Audit Script - Phase 6.1

This script audits all existing tools to check compliance with the BaseTool interface.
It generates a comprehensive report of which tools properly implement the standardized interface.
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.base_tool import BaseTool, ToolRequest, ToolResult, ToolContract


@dataclass
class ToolAuditResult:
    """Results of auditing a single tool"""
    tool_path: str
    tool_class: Optional[str]
    has_execute: bool
    execute_signature_correct: bool
    returns_tool_result: bool
    handles_tool_request: bool
    inherits_base_tool: bool
    has_get_contract: bool
    has_validate_input: bool
    has_health_check: bool
    error_handling: bool
    instantiation_works: bool
    error_messages: List[str]


class ToolInterfaceAuditor:
    """Auditor for tool interface compliance"""
    
    def __init__(self):
        self.results: Dict[str, ToolAuditResult] = {}
        self.tool_paths = [
            # Phase 1 core tools
            'src.tools.phase1.t01_pdf_loader.PDFLoader',
            'src.tools.phase1.t15a_text_chunker.TextChunker', 
            'src.tools.phase1.t23a_spacy_ner.SpacyNER',
            'src.tools.phase1.t27_relationship_extractor.RelationshipExtractor',
            'src.tools.phase1.t31_entity_builder.EntityBuilder',
            'src.tools.phase1.t34_edge_builder.EdgeBuilder',
            'src.tools.phase1.t49_multihop_query.MultiHopQuery',
            'src.tools.phase1.t68_pagerank.PageRank',
            
            # Phase 1 unified tools (newer implementations)
            'src.tools.phase1.t01_pdf_loader_unified.T01PDFLoaderUnified',
            'src.tools.phase1.t15a_text_chunker_unified.T15ATextChunkerUnified',
            'src.tools.phase1.t23a_spacy_ner_unified.T23ASpacyNERUnified',
            'src.tools.phase1.t27_relationship_extractor_unified.T27RelationshipExtractorUnified',
            'src.tools.phase1.t31_entity_builder_unified.T31EntityBuilderUnified',
            'src.tools.phase1.t34_edge_builder_unified.T34EdgeBuilderUnified',
            'src.tools.phase1.t49_multihop_query_unified.T49MultiHopQueryUnified',
            'src.tools.phase1.t68_pagerank_unified.T68PageRankCalculatorUnified',
            
            # Additional document loaders
            'src.tools.phase1.t02_word_loader_unified.T02WordLoaderUnified',
            'src.tools.phase1.t03_text_loader_unified.T03TextLoaderUnified',
            'src.tools.phase1.t04_markdown_loader_unified.T04MarkdownLoaderUnified',
            'src.tools.phase1.t05_csv_loader_unified.T05CSVLoaderUnified',
            'src.tools.phase1.t06_json_loader_unified.T06JSONLoaderUnified',
            'src.tools.phase1.t07_html_loader_unified.T07HTMLLoaderUnified',
            'src.tools.phase1.t08_xml_loader_unified.T08XMLLoaderUnified',
            'src.tools.phase1.t09_yaml_loader_unified.T09YAMLLoaderUnified',
            'src.tools.phase1.t10_excel_loader_unified.T10ExcelLoaderUnified',
            'src.tools.phase1.t11_powerpoint_loader_unified.T11PowerPointLoaderUnified',
            'src.tools.phase1.t12_zip_loader_unified.T12ZipLoaderUnified',
            'src.tools.phase1.t13_web_scraper_unified.T13WebScraperUnified',
            'src.tools.phase1.t14_email_parser_unified.T14EmailParserUnified',
            
            # Phase 2 tools
            'src.tools.phase2.t50_community_detection_unified.T50CommunityDetectionUnified',
            'src.tools.phase2.t51_centrality_analysis_unified.T51CentralityAnalysisUnified',
            'src.tools.phase2.t59_scale_free_analysis_unified.T59ScaleFreeAnalysisUnified',
            'src.tools.phase2.t60_graph_export_unified.T60GraphExportUnified',
            
            # Phase 3 tools
            'src.tools.phase3.t301_multi_document_fusion.MultiDocumentFusion',
            
            # Cross modal tools
            'src.tools.cross_modal.multi_format_exporter.MultiFormatExporter',
            
            # Special tools
            'src.tools.phase1.t85_twitter_explorer.TwitterExplorer',
        ]
    
    def audit_all_tools(self) -> Dict[str, ToolAuditResult]:
        """Audit all tools for interface compliance"""
        print("Starting tool interface audit...")
        print(f"Auditing {len(self.tool_paths)} tools")
        print("=" * 60)
        
        for tool_path in self.tool_paths:
            try:
                print(f"\nAuditing: {tool_path}")
                result = self._audit_single_tool(tool_path)
                self.results[tool_path] = result
                self._print_tool_result(result)
            except Exception as e:
                print(f"ERROR auditing {tool_path}: {e}")
                self.results[tool_path] = ToolAuditResult(
                    tool_path=tool_path,
                    tool_class=None,
                    has_execute=False,
                    execute_signature_correct=False,
                    returns_tool_result=False,
                    handles_tool_request=False,
                    inherits_base_tool=False,
                    has_get_contract=False,
                    has_validate_input=False,
                    has_health_check=False,
                    error_handling=False,
                    instantiation_works=False,
                    error_messages=[f"Failed to audit: {str(e)}"]
                )
        
        return self.results
    
    def _audit_single_tool(self, tool_path: str) -> ToolAuditResult:
        """Audit a single tool for interface compliance"""
        error_messages = []
        
        # Try to import the tool
        try:
            module_path, class_name = tool_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
        except Exception as e:
            error_messages.append(f"Failed to import: {str(e)}")
            return ToolAuditResult(
                tool_path=tool_path,
                tool_class=None,
                has_execute=False,
                execute_signature_correct=False,
                returns_tool_result=False,
                handles_tool_request=False,
                inherits_base_tool=False,
                has_get_contract=False,
                has_validate_input=False,
                has_health_check=False,
                error_handling=False,
                instantiation_works=False,
                error_messages=error_messages
            )
        
        # Re-import classes to ensure same reference
        from src.tools.base_tool import BaseTool as AuditBaseTool, ToolRequest as AuditToolRequest, ToolResult as AuditToolResult
        
        # Check if it inherits from BaseTool
        try:
            inherits_base_tool = issubclass(tool_class, AuditBaseTool)
            if not inherits_base_tool:
                error_messages.append("Does not inherit from BaseTool")
        except Exception as e:
            inherits_base_tool = False
            error_messages.append(f"Error checking BaseTool inheritance: {str(e)}")
        
        # Check for required methods
        has_execute = hasattr(tool_class, 'execute')
        has_get_contract = hasattr(tool_class, 'get_contract')
        has_validate_input = hasattr(tool_class, 'validate_input')
        has_health_check = hasattr(tool_class, 'health_check')
        
        if not has_execute:
            error_messages.append("Missing execute() method")
        if not has_get_contract:
            error_messages.append("Missing get_contract() method")
        if not has_validate_input:
            error_messages.append("Missing validate_input() method")
        if not has_health_check:
            error_messages.append("Missing health_check() method")
        
        # Check execute method signature
        execute_signature_correct = False
        if has_execute:
            try:
                sig = inspect.signature(tool_class.execute)
                params = list(sig.parameters.keys())
                # Should be: self, request
                if len(params) == 2 and params[1] == 'request':
                    # Check parameter annotation
                    param = sig.parameters['request']
                    if (param.annotation == AuditToolRequest or 
                        param.annotation == 'ToolRequest' or 
                        str(param.annotation).endswith('ToolRequest')):
                        execute_signature_correct = True
                    else:
                        error_messages.append(f"execute() parameter 'request' should be annotated as ToolRequest, got: {param.annotation}")
                else:
                    error_messages.append(f"execute() should have signature: execute(self, request: ToolRequest), got params: {params}")
            except Exception as e:
                error_messages.append(f"Error checking execute signature: {str(e)}")
        
        # Try to instantiate the tool
        instantiation_works = False
        returns_tool_result = False
        handles_tool_request = False
        error_handling = False
        
        try:
            # Create a mock service manager for testing
            class MockServiceManager:
                def __init__(self):
                    self.identity_service = None
                    self.provenance_service = None
                    self.quality_service = None
                    self.neo4j_service = None
                    self.sqlite_service = None
                
                def health_check(self):
                    return {"mock": True}
            
            mock_services = MockServiceManager()
            tool_instance = tool_class(mock_services)
            instantiation_works = True
            
            # Test execute method with sample request
            if has_execute:
                try:
                    # Create a minimal test request
                    test_request = AuditToolRequest(
                        tool_id="TEST",
                        operation="test",
                        input_data={"test": "data"},
                        parameters={}
                    )
                    
                    # Call execute - we expect it to return a ToolResult
                    result = tool_instance.execute(test_request)
                    
                    if isinstance(result, AuditToolResult) or str(type(result)).endswith('ToolResult'):
                        returns_tool_result = True
                        handles_tool_request = True
                        
                        # Check if it has proper error handling
                        if hasattr(result, 'status') and result.status in ["success", "error"]:
                            error_handling = True
                        else:
                            error_messages.append(f"execute() returned ToolResult with invalid status: {getattr(result, 'status', 'unknown')}")
                    else:
                        error_messages.append(f"execute() should return ToolResult, got: {type(result)}")
                        
                except Exception as e:
                    # This is expected for many tools that require specific inputs
                    # But we can still check if the error is handled properly
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in ['validation', 'invalid', 'missing', 'required']):
                        error_handling = True
                        handles_tool_request = True  # It at least tried to process
                    error_messages.append(f"execute() test failed (expected for some tools): {str(e)}")
        
        except Exception as e:
            error_messages.append(f"Failed to instantiate tool: {str(e)}")
        
        return ToolAuditResult(
            tool_path=tool_path,
            tool_class=class_name,
            has_execute=has_execute,
            execute_signature_correct=execute_signature_correct,
            returns_tool_result=returns_tool_result,
            handles_tool_request=handles_tool_request,
            inherits_base_tool=inherits_base_tool,
            has_get_contract=has_get_contract,
            has_validate_input=has_validate_input,
            has_health_check=has_health_check,
            error_handling=error_handling,
            instantiation_works=instantiation_works,
            error_messages=error_messages
        )
    
    def _print_tool_result(self, result: ToolAuditResult):
        """Print the audit result for a single tool"""
        status = "✅ PASS" if self._is_compliant(result) else "❌ FAIL"
        print(f"  Status: {status}")
        
        if result.inherits_base_tool:
            print("  ✅ Inherits BaseTool")
        else:
            print("  ❌ Does not inherit BaseTool")
        
        if result.has_execute:
            print("  ✅ Has execute() method")
            if result.execute_signature_correct:
                print("    ✅ Correct signature")
            else:
                print("    ❌ Incorrect signature")
        else:
            print("  ❌ Missing execute() method")
        
        if result.has_get_contract:
            print("  ✅ Has get_contract() method")
        else:
            print("  ❌ Missing get_contract() method")
        
        if result.instantiation_works:
            print("  ✅ Can be instantiated")
        else:
            print("  ❌ Cannot be instantiated")
        
        if result.error_messages:
            print("  Issues:")
            for msg in result.error_messages:
                print(f"    - {msg}")
    
    def _is_compliant(self, result: ToolAuditResult) -> bool:
        """Check if a tool is fully compliant with the interface"""
        return (result.inherits_base_tool and 
                result.has_execute and 
                result.execute_signature_correct and
                result.has_get_contract and 
                result.has_validate_input and
                result.has_health_check and
                result.instantiation_works)
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of the audit"""
        total_tools = len(self.results)
        compliant_tools = sum(1 for result in self.results.values() if self._is_compliant(result))
        
        # Count specific issues
        missing_execute = sum(1 for result in self.results.values() if not result.has_execute)
        wrong_signature = sum(1 for result in self.results.values() if result.has_execute and not result.execute_signature_correct)
        no_base_tool = sum(1 for result in self.results.values() if not result.inherits_base_tool)
        missing_contract = sum(1 for result in self.results.values() if not result.has_get_contract)
        cant_instantiate = sum(1 for result in self.results.values() if not result.instantiation_works)
        
        summary = {
            "total_tools": total_tools,
            "compliant_tools": compliant_tools,
            "compliance_rate": compliant_tools / total_tools if total_tools > 0 else 0.0,
            "issues": {
                "missing_execute": missing_execute,
                "wrong_signature": wrong_signature,
                "no_base_tool": no_base_tool,
                "missing_contract": missing_contract,
                "cant_instantiate": cant_instantiate
            },
            "non_compliant_tools": [
                path for path, result in self.results.items() 
                if not self._is_compliant(result)
            ]
        }
        
        return summary
    
    def print_summary_report(self):
        """Print the summary report"""
        summary = self.generate_summary_report()
        
        print("\n" + "=" * 60)
        print("TOOL INTERFACE AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total tools audited: {summary['total_tools']}")
        print(f"Compliant tools: {summary['compliant_tools']}")
        print(f"Compliance rate: {summary['compliance_rate']:.1%}")
        
        print("\nIssue breakdown:")
        for issue, count in summary['issues'].items():
            print(f"  {issue.replace('_', ' ').title()}: {count}")
        
        if summary['non_compliant_tools']:
            print(f"\nNon-compliant tools ({len(summary['non_compliant_tools'])}):")
            for tool_path in summary['non_compliant_tools']:
                print(f"  - {tool_path}")
        
        print("\n" + "=" * 60)
        
        return summary


def main():
    """Main entry point for the audit script"""
    auditor = ToolInterfaceAuditor()
    
    # Run the audit
    results = auditor.audit_all_tools()
    
    # Print summary
    summary = auditor.print_summary_report()
    
    # Write detailed results to file
    with open("tool_interface_audit_results.txt", "w") as f:
        f.write("DETAILED TOOL INTERFACE AUDIT RESULTS\n")
        f.write("=" * 60 + "\n\n")
        
        for tool_path, result in results.items():
            f.write(f"Tool: {tool_path}\n")
            f.write(f"Class: {result.tool_class}\n")
            f.write(f"Compliant: {'✅ YES' if auditor._is_compliant(result) else '❌ NO'}\n")
            f.write(f"Inherits BaseTool: {'✅' if result.inherits_base_tool else '❌'}\n")
            f.write(f"Has execute(): {'✅' if result.has_execute else '❌'}\n")
            f.write(f"Correct signature: {'✅' if result.execute_signature_correct else '❌'}\n")
            f.write(f"Returns ToolResult: {'✅' if result.returns_tool_result else '❌'}\n")
            f.write(f"Has get_contract(): {'✅' if result.has_get_contract else '❌'}\n")
            f.write(f"Can instantiate: {'✅' if result.instantiation_works else '❌'}\n")
            
            if result.error_messages:
                f.write("Issues:\n")
                for msg in result.error_messages:
                    f.write(f"  - {msg}\n")
            
            f.write("\n" + "-" * 40 + "\n\n")
        
        f.write("SUMMARY:\n")
        f.write(f"Total tools: {summary['total_tools']}\n")
        f.write(f"Compliant tools: {summary['compliant_tools']}\n")
        f.write(f"Compliance rate: {summary['compliance_rate']:.1%}\n")
    
    print(f"\nDetailed results written to: tool_interface_audit_results.txt")
    
    # Return non-zero exit code if not all tools are compliant
    if summary['compliance_rate'] < 1.0:
        print(f"\n⚠️  WARNING: Only {summary['compliance_rate']:.1%} of tools are compliant!")
        print("Non-compliant tools need to be fixed before proceeding to Phase 6.2")
        return 1
    else:
        print(f"\n🎉 SUCCESS: All tools are compliant with the BaseTool interface!")
        return 0


if __name__ == "__main__":
    exit(main())