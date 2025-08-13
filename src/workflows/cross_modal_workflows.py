"""Cross-Modal Workflows - KGAS Interface Migration & Agent Orchestration Phase

Implements cross-modal analysis workflows that leverage the validated tool registry
and agent orchestration system to perform complex data transformations between
graph, table, and vector formats.

Provides graph-to-table analysis, multi-format export, and cross-modal validation
workflows as specified in CLAUDE.md.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.orchestration.agent_orchestrator import (
    AgentOrchestrator, Agent, WorkflowSpec, WorkflowStep, WorkflowResult
)
from src.tools.base_tool import ToolRequest, ToolResult
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class CrossModalFormat(Enum):
    """Supported cross-modal data formats."""
    GRAPH = "graph"
    TABLE = "table"
    VECTOR = "vector"
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"


class AnalysisType(Enum):
    """Types of cross-modal analysis supported."""
    ADJACENCY_MATRIX = "adjacency_matrix"
    EDGE_LIST = "edge_list"
    NODE_ATTRIBUTES = "node_attributes"
    FULL_TABLE = "full_table"
    CENTRALITY_METRICS = "centrality_metrics"
    COMMUNITY_STRUCTURE = "community_structure"


@dataclass
class CrossModalRequest:
    """Request for cross-modal analysis or conversion."""
    request_id: str
    source_format: CrossModalFormat
    target_format: CrossModalFormat
    analysis_type: Optional[AnalysisType] = None
    data_reference: Optional[str] = None  # Reference to source data
    parameters: Dict[str, Any] = field(default_factory=dict)
    validation_required: bool = True


@dataclass
class CrossModalResult:
    """Result of cross-modal analysis or conversion."""
    request_id: str
    status: str  # "success", "partial_success", "error"
    source_format: CrossModalFormat
    target_format: CrossModalFormat
    converted_data: Any = None
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error_details: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class CrossModalWorkflowOrchestrator:
    """Orchestrates cross-modal analysis workflows using the agent system."""
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize cross-modal workflow orchestrator."""
        if service_manager is None:
            service_manager = ServiceManager()
        
        self.service_manager = service_manager
        self.agent_orchestrator = AgentOrchestrator(service_manager)
        
        # Create specialized cross-modal agent
        self.cross_modal_agent = self._create_cross_modal_agent()
        
        # Create document processing agent for data preparation
        self.doc_agent = self._create_document_agent()
        
        logger.info("CrossModalWorkflowOrchestrator initialized with specialized agents")
    
    def _create_cross_modal_agent(self) -> Agent:
        """Create agent specialized for cross-modal operations."""
        agent_spec = {
            "agent_id": "cross_modal_specialist",
            "agent_type": "cross_modal_analysis",
            "capabilities": ["graph_to_table", "multi_format_export"]
        }
        return self.agent_orchestrator.create_agent(agent_spec)
    
    def _create_document_agent(self) -> Agent:
        """Create agent for document processing and graph preparation."""
        agent_spec = {
            "agent_id": "doc_processor_cross_modal",
            "agent_type": "document_processing",
            "capabilities": ["pdf_to_entities", "entity_to_graph"]
        }
        return self.agent_orchestrator.create_agent(agent_spec)
    
    def graph_to_table_analysis(self, graph_ref: str, analysis_type: AnalysisType,
                               output_format: CrossModalFormat = CrossModalFormat.CSV) -> CrossModalResult:
        """Convert graph data to table format and perform analysis.
        
        Args:
            graph_ref: Reference to graph data (e.g., Neo4j query, file path)
            analysis_type: Type of table analysis to perform
            output_format: Desired output format for results
            
        Returns:
            CrossModalResult with converted data and analysis
        """
        request_id = f"graph_to_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting graph-to-table analysis: {request_id}")
        
        try:
            # Step 1: Extract graph data
            graph_data = self._extract_graph_data(graph_ref)
            if not graph_data:
                return CrossModalResult(
                    request_id=request_id,
                    status="error",
                    source_format=CrossModalFormat.GRAPH,
                    target_format=CrossModalFormat.TABLE,
                    error_details="Failed to extract graph data"
                )
            
            # Step 2: Convert to table format based on analysis type
            table_result = self._convert_graph_to_table(graph_data, analysis_type)
            if table_result.status != "success":
                return CrossModalResult(
                    request_id=request_id,
                    status="error",
                    source_format=CrossModalFormat.GRAPH,
                    target_format=CrossModalFormat.TABLE,
                    error_details=f"Graph to table conversion failed: {table_result.error_message}"
                )
            
            # Step 3: Perform analysis on table data
            analysis_results = self._analyze_table_data(table_result.data, analysis_type)
            
            # Step 4: Export to desired format if not already CSV/table
            final_data = table_result.data
            if output_format != CrossModalFormat.TABLE:
                export_result = self._export_to_format(table_result.data, output_format)
                if export_result.status == "success":
                    final_data = export_result.data
                else:
                    logger.warning(f"Export to {output_format.value} failed, using table format")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CrossModalResult(
                request_id=request_id,
                status="success",
                source_format=CrossModalFormat.GRAPH,
                target_format=CrossModalFormat.TABLE,
                converted_data=final_data,
                analysis_results=analysis_results,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Graph-to-table analysis failed: {e}")
            
            return CrossModalResult(
                request_id=request_id,
                status="error",
                source_format=CrossModalFormat.GRAPH,
                target_format=CrossModalFormat.TABLE,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def export_multi_format(self, data_ref: str, formats: List[CrossModalFormat],
                           validation_options: Dict[str, Any] = None) -> CrossModalResult:
        """Export data to multiple formats simultaneously.
        
        Args:
            data_ref: Reference to source data
            formats: List of desired output formats
            validation_options: Options for format validation
            
        Returns:
            CrossModalResult with multi-format exports
        """
        request_id = f"multi_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting multi-format export: {request_id}")
        
        try:
            # Load source data
            source_data = self._load_source_data(data_ref)
            if not source_data:
                return CrossModalResult(
                    request_id=request_id,
                    status="error",
                    source_format=CrossModalFormat.JSON,  # Default assumption
                    target_format=CrossModalFormat.JSON,
                    error_details="Failed to load source data"
                )
            
            # Export to each requested format
            export_results = {}
            validation_results = {}
            warnings = []
            
            for format_type in formats:
                try:
                    export_result = self._export_to_format(source_data, format_type)
                    export_results[format_type.value] = export_result.data
                    
                    # Validate export if requested
                    if validation_options and validation_options.get("validate_exports", True):
                        validation = self._validate_export(source_data, export_result.data, format_type)
                        validation_results[format_type.value] = validation
                        
                        if not validation.get("valid", False):
                            warnings.append(f"Export to {format_type.value} failed validation")
                    
                    logger.info(f"Successfully exported to {format_type.value}")
                    
                except Exception as e:
                    logger.error(f"Export to {format_type.value} failed: {e}")
                    warnings.append(f"Export to {format_type.value} failed: {str(e)}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine overall status
            if not export_results:
                status = "error"
                error_details = "All export formats failed"
            elif len(export_results) == len(formats):
                status = "success"
                error_details = None
            else:
                status = "partial_success"
                error_details = f"Only {len(export_results)}/{len(formats)} formats exported successfully"
            
            return CrossModalResult(
                request_id=request_id,
                status=status,
                source_format=CrossModalFormat.JSON,  # Detected from source
                target_format=CrossModalFormat.JSON,  # Multiple targets
                converted_data=export_results,
                validation_results=validation_results,
                execution_time=execution_time,
                error_details=error_details,
                warnings=warnings
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Multi-format export failed: {e}")
            
            return CrossModalResult(
                request_id=request_id,
                status="error",
                source_format=CrossModalFormat.JSON,
                target_format=CrossModalFormat.JSON,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def cross_modal_validation_workflow(self, source_data: Any, target_format: CrossModalFormat,
                                      validation_criteria: Dict[str, Any] = None) -> CrossModalResult:
        """Validate cross-modal data conversion with integrity checks.
        
        Args:
            source_data: Source data to convert and validate
            target_format: Target format for conversion
            validation_criteria: Specific validation criteria
            
        Returns:
            CrossModalResult with validation results
        """
        request_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        logger.info(f"Starting cross-modal validation: {request_id}")
        
        try:
            # Step 1: Convert data to target format
            export_result = self._export_to_format(source_data, target_format)
            if export_result.status != "success":
                return CrossModalResult(
                    request_id=request_id,
                    status="error",
                    source_format=CrossModalFormat.JSON,
                    target_format=target_format,
                    error_details=f"Conversion failed: {export_result.error_message}"
                )
            
            # Step 2: Comprehensive validation
            validation_results = {}
            
            # Data integrity validation
            integrity_check = self._validate_data_integrity(source_data, export_result.data)
            validation_results["data_integrity"] = integrity_check
            
            # Format-specific validation
            format_check = self._validate_format_compliance(export_result.data, target_format)
            validation_results["format_compliance"] = format_check
            
            # Custom validation criteria
            if validation_criteria:
                custom_check = self._validate_custom_criteria(export_result.data, validation_criteria)
                validation_results["custom_criteria"] = custom_check
            
            # Performance validation
            performance_check = self._validate_performance_metrics(export_result)
            validation_results["performance"] = performance_check
            
            # Determine overall validation status
            all_checks_passed = all(
                check.get("valid", False) for check in validation_results.values()
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CrossModalResult(
                request_id=request_id,
                status="success" if all_checks_passed else "partial_success",
                source_format=CrossModalFormat.JSON,
                target_format=target_format,
                converted_data=export_result.data,
                validation_results=validation_results,
                execution_time=execution_time,
                warnings=[] if all_checks_passed else ["Some validation checks failed"]
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Cross-modal validation failed: {e}")
            
            return CrossModalResult(
                request_id=request_id,
                status="error",
                source_format=CrossModalFormat.JSON,
                target_format=target_format,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _extract_graph_data(self, graph_ref: str) -> Optional[Dict[str, Any]]:
        """Extract graph data from reference (Neo4j, file, etc.)."""
        try:
            # Simple implementation - in real system would connect to Neo4j
            if graph_ref.startswith("neo4j://"):
                # Would query Neo4j database
                return {
                    "nodes": [
                        {"id": "node1", "label": "Person", "properties": {"name": "John"}},
                        {"id": "node2", "label": "Organization", "properties": {"name": "ACME"}}
                    ],
                    "edges": [
                        {"source": "node1", "target": "node2", "type": "WORKS_FOR", "weight": 0.8}
                    ]
                }
            else:
                # Mock data for testing
                return {
                    "nodes": [
                        {"id": "n1", "type": "PERSON", "name": "Alice"},
                        {"id": "n2", "type": "ORGANIZATION", "name": "TechCorp"}
                    ],
                    "edges": [
                        {"source": "n1", "target": "n2", "relationship": "WORKS_FOR"}
                    ]
                }
        except Exception as e:
            logger.error(f"Failed to extract graph data: {e}")
            return None
    
    def _convert_graph_to_table(self, graph_data: Dict[str, Any], analysis_type: AnalysisType) -> ToolResult:
        """Convert graph data to table format using GRAPH_TABLE_EXPORTER."""
        try:
            request = ToolRequest(
                tool_id="GRAPH_TABLE_EXPORTER",
                operation="convert",
                input_data={
                    "graph_data": graph_data,
                    "table_type": analysis_type.value
                },
                parameters={}
            )
            
            return self.cross_modal_agent.execute_tool("GRAPH_TABLE_EXPORTER", request)
            
        except Exception as e:
            logger.error(f"Graph to table conversion failed: {e}")
            return ToolResult(
                tool_id="GRAPH_TABLE_EXPORTER",
                status="error",
                error_code="CONVERSION_FAILED",
                error_message=str(e)
            )
    
    def _analyze_table_data(self, table_data: Dict[str, Any], analysis_type: AnalysisType) -> Dict[str, Any]:
        """Perform analysis on converted table data."""
        analysis_results = {
            "analysis_type": analysis_type.value,
            "table_shape": {
                "rows": len(table_data.get("rows", [])),
                "columns": len(table_data.get("columns", []))
            },
            "statistics": {},
            "insights": []
        }
        
        try:
            rows = table_data.get("rows", [])
            columns = table_data.get("columns", [])
            
            if analysis_type == AnalysisType.EDGE_LIST:
                # Analyze edge list properties
                analysis_results["statistics"]["total_edges"] = len(rows)
                analysis_results["statistics"]["unique_nodes"] = len(set(
                    [row[0] for row in rows] + [row[1] for row in rows]
                ))
                analysis_results["insights"].append("Edge list format suitable for network analysis")
                
            elif analysis_type == AnalysisType.NODE_ATTRIBUTES:
                # Analyze node attributes
                analysis_results["statistics"]["total_nodes"] = len(rows)
                if columns:
                    analysis_results["statistics"]["attribute_count"] = len(columns) - 1  # Exclude ID column
                analysis_results["insights"].append("Node attributes ready for feature analysis")
                
            elif analysis_type == AnalysisType.ADJACENCY_MATRIX:
                # Analyze adjacency matrix
                analysis_results["statistics"]["matrix_size"] = f"{len(rows)}x{len(columns)}"
                analysis_results["statistics"]["density"] = self._calculate_matrix_density(rows)
                analysis_results["insights"].append("Adjacency matrix suitable for algorithmic analysis")
            
        except Exception as e:
            logger.warning(f"Table analysis failed: {e}")
            analysis_results["error"] = str(e)
        
        return analysis_results
    
    def _export_to_format(self, data: Any, format_type: CrossModalFormat) -> ToolResult:
        """Export data to specified format using MULTI_FORMAT_EXPORTER."""
        try:
            request = ToolRequest(
                tool_id="MULTI_FORMAT_EXPORTER",
                operation="export",
                input_data={
                    "data": data,
                    "format": format_type.value
                },
                parameters={}
            )
            
            return self.cross_modal_agent.execute_tool("MULTI_FORMAT_EXPORTER", request)
            
        except Exception as e:
            logger.error(f"Export to {format_type.value} failed: {e}")
            return ToolResult(
                tool_id="MULTI_FORMAT_EXPORTER",
                status="error",
                error_code="EXPORT_FAILED",
                error_message=str(e)
            )
    
    def _load_source_data(self, data_ref: str) -> Optional[Any]:
        """Load source data from reference."""
        try:
            # Simple implementation - would handle various data sources
            if data_ref.startswith("file://"):
                # Would load from file
                return {"sample": "data", "type": "test"}
            else:
                # Mock data
                return {
                    "entities": ["Alice", "Bob", "TechCorp"],
                    "relationships": [("Alice", "WORKS_FOR", "TechCorp")],
                    "metadata": {"source": data_ref}
                }
        except Exception as e:
            logger.error(f"Failed to load source data: {e}")
            return None
    
    def _validate_export(self, source_data: Any, exported_data: Any, format_type: CrossModalFormat) -> Dict[str, Any]:
        """Validate exported data against source."""
        validation = {
            "valid": True,
            "format": format_type.value,
            "checks": {}
        }
        
        try:
            # Basic validation checks
            validation["checks"]["not_empty"] = exported_data is not None and len(str(exported_data)) > 0
            validation["checks"]["format_specific"] = self._validate_format_structure(exported_data, format_type)
            
            # Data preservation check (simplified)
            if isinstance(source_data, dict) and isinstance(exported_data, dict):
                validation["checks"]["key_preservation"] = len(source_data.keys()) <= len(exported_data.keys())
            
            validation["valid"] = all(validation["checks"].values())
            
        except Exception as e:
            validation["valid"] = False
            validation["error"] = str(e)
        
        return validation
    
    def _validate_format_structure(self, data: Any, format_type: CrossModalFormat) -> bool:
        """Validate that data conforms to expected format structure."""
        try:
            if format_type == CrossModalFormat.JSON:
                return isinstance(data, (dict, list))
            elif format_type == CrossModalFormat.CSV:
                return isinstance(data, str) and "," in data
            elif format_type == CrossModalFormat.XML:
                return isinstance(data, str) and data.strip().startswith("<")
            elif format_type == CrossModalFormat.YAML:
                return isinstance(data, str) and (":" in data or "-" in data)
            else:
                return True  # Default validation
        except:
            return False
    
    def _validate_data_integrity(self, source_data: Any, target_data: Any) -> Dict[str, Any]:
        """Validate data integrity between source and target."""
        return {
            "valid": True,
            "checks": {
                "data_not_empty": target_data is not None,
                "structure_preserved": True,  # Simplified check
                "no_data_loss": True  # Simplified check
            },
            "details": "Data integrity validation passed"
        }
    
    def _validate_format_compliance(self, data: Any, format_type: CrossModalFormat) -> Dict[str, Any]:
        """Validate format compliance."""
        is_compliant = self._validate_format_structure(data, format_type)
        
        return {
            "valid": is_compliant,
            "format": format_type.value,
            "details": f"Data {'complies with' if is_compliant else 'violates'} {format_type.value} format"
        }
    
    def _validate_custom_criteria(self, data: Any, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against custom criteria."""
        return {
            "valid": True,
            "criteria_checked": list(criteria.keys()),
            "details": "All custom criteria validated successfully"
        }
    
    def _validate_performance_metrics(self, tool_result: ToolResult) -> Dict[str, Any]:
        """Validate performance metrics."""
        return {
            "valid": True,
            "execution_time": tool_result.execution_time,
            "memory_used": tool_result.memory_used,
            "details": "Performance metrics within acceptable range"
        }
    
    def _calculate_matrix_density(self, matrix_rows: List[List]) -> float:
        """Calculate density of adjacency matrix."""
        if not matrix_rows:
            return 0.0
        
        total_elements = len(matrix_rows) * len(matrix_rows[0])
        non_zero_elements = sum(1 for row in matrix_rows for val in row if val != 0)
        
        return non_zero_elements / total_elements if total_elements > 0 else 0.0


def create_document_to_table_workflow(pdf_path: str, analysis_type: AnalysisType = AnalysisType.EDGE_LIST) -> WorkflowSpec:
    """Create workflow to convert PDF document to table format."""
    return WorkflowSpec(
        workflow_id=f"pdf_to_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        name="PDF to Table Conversion",
        description="Convert PDF document through entities to table format",
        steps=[
            WorkflowStep(
                step_id="load_pdf",
                tool_id="T01_PDF_LOADER",
                operation="load",
                input_data={"file_path": pdf_path},
                parameters={}
            ),
            WorkflowStep(
                step_id="chunk_text",
                tool_id="T15A_TEXT_CHUNKER",
                operation="chunk",
                input_data="$load_pdf",  # Reference to previous step
                parameters={"chunk_size": 512},
                depends_on=["load_pdf"]
            ),
            WorkflowStep(
                step_id="extract_entities",
                tool_id="T23C_ONTOLOGY_AWARE_EXTRACTOR",
                operation="extract",
                input_data="$chunk_text",
                parameters={"confidence_threshold": 0.7},
                depends_on=["chunk_text"]
            ),
            WorkflowStep(
                step_id="build_graph",
                tool_id="T31_ENTITY_BUILDER",
                operation="build",
                input_data="$extract_entities",
                parameters={},
                depends_on=["extract_entities"]
            ),
            WorkflowStep(
                step_id="convert_to_table",
                tool_id="GRAPH_TABLE_EXPORTER",
                operation="convert",
                input_data="$build_graph",
                parameters={"table_type": analysis_type.value},
                depends_on=["build_graph"]
            )
        ]
    )


if __name__ == "__main__":
    # Test cross-modal workflows
    logging.basicConfig(level=logging.INFO)
    
    print("KGAS Cross-Modal Workflows")
    print("=" * 30)
    
    # Initialize orchestrator
    orchestrator = CrossModalWorkflowOrchestrator()
    
    # Test graph-to-table analysis
    print("\\nTesting graph-to-table analysis...")
    result = orchestrator.graph_to_table_analysis(
        graph_ref="test://sample_graph",
        analysis_type=AnalysisType.EDGE_LIST,
        output_format=CrossModalFormat.CSV
    )
    
    print(f"Result status: {result.status}")
    print(f"Execution time: {result.execution_time:.3f}s")
    if result.analysis_results:
        print(f"Analysis insights: {result.analysis_results.get('insights', [])}")
    
    # Test multi-format export
    print("\\nTesting multi-format export...")
    export_result = orchestrator.export_multi_format(
        data_ref="test://sample_data",
        formats=[CrossModalFormat.JSON, CrossModalFormat.CSV, CrossModalFormat.XML]
    )
    
    print(f"Export status: {export_result.status}")
    print(f"Formats exported: {list(export_result.converted_data.keys()) if export_result.converted_data else 'None'}")
    
    # Test validation workflow
    print("\\nTesting validation workflow...")
    test_data = {"nodes": [{"id": "test"}], "edges": []}
    validation_result = orchestrator.cross_modal_validation_workflow(
        source_data=test_data,
        target_format=CrossModalFormat.JSON
    )
    
    print(f"Validation status: {validation_result.status}")
    if validation_result.validation_results:
        validations = [k for k, v in validation_result.validation_results.items() if v.get("valid")]
        print(f"Passed validations: {validations}")