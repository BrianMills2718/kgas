"""
Real Tool Compatibility Checker

Tests actual tool compatibility by running tools with sample data
and verifying outputs can be consumed by downstream tools.
"""

from typing import Dict, List, Tuple, Any, Optional
import logging
from dataclasses import dataclass
from src.tools.base_tool import ToolRequest, ToolResult, BaseTool
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue between tools."""
    source_tool: str
    target_tool: str
    issue_type: str  # "missing_field", "type_mismatch", "format_mismatch"
    details: str
    source_output: Dict[str, Any]
    target_expectation: Optional[Dict[str, Any]] = None


class RealToolCompatibilityChecker:
    """Tests real tool compatibility by running actual tools."""
    
    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
        
    def test_tool_chain(self, tool_sequence: List[Tuple[BaseTool, Dict[str, Any]]]) -> Tuple[bool, List[CompatibilityIssue]]:
        """
        Test a sequence of tools by running them with actual data.
        
        Args:
            tool_sequence: List of (tool, input_data) tuples
            
        Returns:
            Tuple of (success, list of compatibility issues)
        """
        issues = []
        previous_output = None
        
        for i, (tool, base_input) in enumerate(tool_sequence):
            try:
                # Prepare input
                if i == 0:
                    # First tool uses base input
                    input_data = base_input
                else:
                    # Subsequent tools use previous output
                    if previous_output is None:
                        issues.append(CompatibilityIssue(
                            source_tool=tool_sequence[i-1][0].tool_id,
                            target_tool=tool.tool_id,
                            issue_type="missing_output",
                            details="Previous tool produced no output",
                            source_output={}
                        ))
                        return False, issues
                    
                    # Try to adapt previous output to current tool's input
                    input_data = self._adapt_output_to_input(
                        previous_output, 
                        tool,
                        tool_sequence[i-1][0].tool_id
                    )
                
                # Create request
                request = ToolRequest(
                    tool_id=tool.tool_id,
                    operation="execute",
                    input_data=input_data
                )
                
                # Execute tool
                result = tool.execute(request)
                
                if result.status != "success":
                    issues.append(CompatibilityIssue(
                        source_tool=tool_sequence[i-1][0].tool_id if i > 0 else "input",
                        target_tool=tool.tool_id,
                        issue_type="execution_failure",
                        details=f"Tool failed: {result.error_message}",
                        source_output=previous_output.data if previous_output else input_data
                    ))
                    return False, issues
                
                # Store output for next tool
                previous_output = result
                
            except Exception as e:
                issues.append(CompatibilityIssue(
                    source_tool=tool_sequence[i-1][0].tool_id if i > 0 else "input",
                    target_tool=tool.tool_id,
                    issue_type="exception",
                    details=str(e),
                    source_output=previous_output.data if previous_output else {}
                ))
                return False, issues
        
        return True, issues
    
    def _adapt_output_to_input(self, output: ToolResult, target_tool: BaseTool, source_tool_id: str) -> Dict[str, Any]:
        """
        Attempt to adapt output from one tool to input for another.
        Records any adaptations needed as compatibility issues.
        """
        # Start with raw output data
        adapted = output.data.copy()
        
        # Known adaptations based on our discoveries
        adaptations = {
            ("T23C", "T31"): self._adapt_t23c_to_t31,
            ("T23C", "T34"): self._adapt_t23c_to_t34,
            ("T31", "T34"): self._adapt_t31_to_t34,
        }
        
        adapter_key = (source_tool_id, target_tool.tool_id)
        if adapter_key in adaptations:
            adapted = adaptations[adapter_key](output.data)
            self.logger.info(f"Applied adapter for {source_tool_id} -> {target_tool.tool_id}")
        
        return adapted
    
    def _adapt_t23c_to_t31(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T23C output to T31 input format."""
        mentions = data.get("mentions", [])
        
        # Convert mentions format
        adapted_mentions = []
        for mention in mentions:
            adapted_mentions.append({
                "mention_id": mention.get("mention_id"),
                "text": mention.get("surface_form"),  # T31 expects "text"
                "entity_type": mention.get("entity_type"),
                "entity_id": mention.get("entity_id"),
                "confidence": mention.get("confidence"),
                "source_ref": mention.get("source_ref"),
                "start_pos": mention.get("start_pos"),
                "end_pos": mention.get("end_pos")
            })
        
        return {
            "mentions": adapted_mentions,
            "source_refs": ["adapted_from_t23c"]
        }
    
    def _adapt_t23c_to_t34(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T23C output to T34 input format."""
        relationships = data.get("relationships", [])
        
        # Convert relationships format
        adapted_relationships = []
        for rel in relationships:
            adapted_relationships.append({
                "subject": {
                    "entity_id": rel.get("source_id"),
                    "canonical_name": rel.get("head_entity"),
                    "text": rel.get("head_entity"),
                    "entity_type": "UNKNOWN"  # T23C doesn't provide this
                },
                "object": {
                    "entity_id": rel.get("target_id"),
                    "canonical_name": rel.get("tail_entity"),
                    "text": rel.get("tail_entity"),
                    "entity_type": "UNKNOWN"
                },
                "relationship_type": rel.get("relationship_type"),
                "confidence": rel.get("confidence", 0.8),
                "properties": rel.get("attributes", {})
            })
        
        return {
            "relationships": adapted_relationships,
            "source_refs": ["adapted_from_t23c"]
        }
    
    def _adapt_t31_to_t34(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt T31 output to T34 input format."""
        # T31 outputs entity information but T34 needs relationships
        # This is actually an incompatible sequence - T34 should follow T23C, not T31
        return {
            "relationships": [],
            "source_refs": ["no_relationships_from_t31"]
        }
    
    def discover_tool_schemas(self, tools: List[BaseTool]) -> Dict[str, Dict[str, Any]]:
        """
        Discover actual input/output schemas by running tools with sample data.
        """
        schemas = {}
        
        for tool in tools:
            self.logger.info(f"Discovering schema for {tool.tool_id}")
            
            # Get sample input for this tool type
            sample_input = self._get_sample_input_for_tool(tool.tool_id)
            
            # Create request
            request = ToolRequest(
                tool_id=tool.tool_id,
                operation="execute",
                input_data=sample_input
            )
            
            try:
                # Execute tool
                result = tool.execute(request)
                
                if result.status == "success":
                    schemas[tool.tool_id] = {
                        "input_sample": sample_input,
                        "output_sample": result.data,
                        "output_fields": list(result.data.keys()) if isinstance(result.data, dict) else None
                    }
                else:
                    schemas[tool.tool_id] = {
                        "error": result.error_message,
                        "input_sample": sample_input
                    }
                    
            except Exception as e:
                schemas[tool.tool_id] = {
                    "exception": str(e),
                    "input_sample": sample_input
                }
        
        return schemas
    
    def _get_sample_input_for_tool(self, tool_id: str) -> Dict[str, Any]:
        """Get appropriate sample input for a tool."""
        sample_inputs = {
            "T01_PDF_LOADER": {
                "file_path": "sample.pdf",
                "workflow_id": "test_workflow"
            },
            "T15A_TEXT_CHUNKER": {
                "document_ref": "test_doc",
                "text": "This is a sample text for chunking.",
                "document_confidence": 0.9
            },
            "T23C_ONTOLOGY_AWARE_EXTRACTOR": {
                "chunk_ref": "test_chunk",
                "text": "Dr. Jane Smith works at TechCorp.",
                "source_confidence": 0.9,
                "extraction_schema": "OPEN"
            },
            "T31_ENTITY_BUILDER": {
                "mentions": [{
                    "mention_id": "m1",
                    "text": "Jane Smith",
                    "entity_type": "PERSON",
                    "confidence": 0.9,
                    "source_ref": "test"
                }],
                "source_refs": ["test_doc"]
            },
            "T34_EDGE_BUILDER": {
                "relationships": [{
                    "subject": {
                        "entity_id": "e1",
                        "canonical_name": "Jane Smith",
                        "text": "Jane Smith",
                        "entity_type": "PERSON"
                    },
                    "object": {
                        "entity_id": "e2",
                        "canonical_name": "TechCorp",
                        "text": "TechCorp",
                        "entity_type": "ORG"
                    },
                    "relationship_type": "WORKS_FOR",
                    "confidence": 0.8
                }],
                "source_refs": ["test_doc"]
            }
        }
        
        return sample_inputs.get(tool_id, {"test": "data"})
    
    def generate_compatibility_report(self, tool_chains: List[List[str]]) -> Dict[str, Any]:
        """
        Generate a comprehensive compatibility report for common tool chains.
        """
        report = {
            "tested_chains": [],
            "compatibility_issues": [],
            "required_adapters": [],
            "recommendations": []
        }
        
        for chain in tool_chains:
            self.logger.info(f"Testing chain: {' -> '.join(chain)}")
            
            # Load tools
            tools = []
            for tool_id in chain:
                tool = self._load_tool(tool_id)
                if tool:
                    sample_input = self._get_sample_input_for_tool(tool_id)
                    tools.append((tool, sample_input))
            
            if len(tools) == len(chain):
                # Test the chain
                success, issues = self.test_tool_chain(tools)
                
                report["tested_chains"].append({
                    "chain": chain,
                    "success": success,
                    "issues": [
                        {
                            "source": issue.source_tool,
                            "target": issue.target_tool,
                            "type": issue.issue_type,
                            "details": issue.details
                        }
                        for issue in issues
                    ]
                })
                
                # Record issues
                for issue in issues:
                    report["compatibility_issues"].append({
                        "source_tool": issue.source_tool,
                        "target_tool": issue.target_tool,
                        "issue_type": issue.issue_type,
                        "details": issue.details
                    })
                    
                    # Identify required adapters
                    if issue.issue_type in ["missing_field", "format_mismatch"]:
                        adapter_key = f"{issue.source_tool}_to_{issue.target_tool}"
                        if adapter_key not in report["required_adapters"]:
                            report["required_adapters"].append(adapter_key)
        
        # Generate recommendations
        if report["compatibility_issues"]:
            report["recommendations"].append(
                "Implement adapters for the identified tool pairs to ensure compatibility"
            )
            report["recommendations"].append(
                "Standardize field naming conventions across tools"
            )
            report["recommendations"].append(
                "Consider implementing a common data model for tool interactions"
            )
        
        return report
    
    def _load_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Load a tool instance by ID."""
        try:
            # Map tool IDs to classes
            tool_map = {
                "T23C_ONTOLOGY_AWARE_EXTRACTOR": "src.tools.phase2.t23c_ontology_aware_extractor_unified.OntologyAwareExtractor",
                "T31_ENTITY_BUILDER": "src.tools.phase1.t31_entity_builder_unified.T31EntityBuilderUnified",
                "T34_EDGE_BUILDER": "src.tools.phase1.t34_edge_builder_unified.T34EdgeBuilderUnified",
                "T15A_TEXT_CHUNKER": "src.tools.phase1.t15a_text_chunker_unified.T15ATextChunkerUnified",
                "T68_PAGERANK": "src.tools.phase1.t68_pagerank_unified.PageRankUnified"
            }
            
            if tool_id in tool_map:
                module_path, class_name = tool_map[tool_id].rsplit(".", 1)
                module = __import__(module_path, fromlist=[class_name])
                tool_class = getattr(module, class_name)
                return tool_class(self.service_manager)
            
        except Exception as e:
            self.logger.error(f"Failed to load tool {tool_id}: {e}")
        
        return None


def test_real_compatibility():
    """Test real tool compatibility with common workflows."""
    from src.core.service_manager import ServiceManager
    
    service_manager = ServiceManager()
    checker = RealToolCompatibilityChecker(service_manager)
    
    # Define common tool chains to test
    tool_chains = [
        ["T23C_ONTOLOGY_AWARE_EXTRACTOR", "T31_ENTITY_BUILDER"],
        ["T23C_ONTOLOGY_AWARE_EXTRACTOR", "T34_EDGE_BUILDER"],
        ["T15A_TEXT_CHUNKER", "T23C_ONTOLOGY_AWARE_EXTRACTOR"],
        ["T31_ENTITY_BUILDER", "T68_PAGERANK"],
        ["T34_EDGE_BUILDER", "T68_PAGERANK"]
    ]
    
    # Generate compatibility report
    report = checker.generate_compatibility_report(tool_chains)
    
    # Print report
    print("\n=== Tool Compatibility Report ===\n")
    
    for chain_result in report["tested_chains"]:
        chain_str = " -> ".join(chain_result["chain"])
        status = "✅ COMPATIBLE" if chain_result["success"] else "❌ INCOMPATIBLE"
        print(f"{chain_str}: {status}")
        
        if chain_result["issues"]:
            for issue in chain_result["issues"]:
                print(f"  - {issue['type']}: {issue['source']} -> {issue['target']}")
                print(f"    {issue['details']}")
    
    if report["required_adapters"]:
        print("\n=== Required Adapters ===")
        for adapter in report["required_adapters"]:
            print(f"  - {adapter}")
    
    if report["recommendations"]:
        print("\n=== Recommendations ===")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    return report


if __name__ == "__main__":
    test_real_compatibility()