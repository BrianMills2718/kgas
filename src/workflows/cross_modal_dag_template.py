"""
Cross-Modal DAG Template

Standard template for cross-modal analysis workflows that integrate
graph, table, and vector data representations for comprehensive analysis.
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class CrossModalDAGTemplate:
    """Standard template for cross-modal analysis workflows"""
    
    @staticmethod
    def create_graph_table_vector_synthesis_dag(
        source_data_ref: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Create DAG for graph→table→vector→synthesis analysis"""
        
        dag = {
            "dag_id": f"cross_modal_analysis_{analysis_type}",
            "description": "Cross-modal analysis with format transfers and synthesis",
            "steps": [
                {
                    "step_id": "load_source_data",
                    "tool_id": "T01_PDF_LOADER",  # Or appropriate loader
                    "operation": "load",
                    "input_data": {"file_path": source_data_ref},
                    "parameters": {}
                },
                {
                    "step_id": "extract_entities",
                    "tool_id": "T23A_SPACY_NER", 
                    "operation": "extract",
                    "input_data": "$load_source_data.text",
                    "parameters": {"confidence_threshold": 0.8},
                    "depends_on": ["load_source_data"]
                },
                {
                    "step_id": "build_graph",
                    "tool_id": "T31_ENTITY_BUILDER",
                    "operation": "build", 
                    "input_data": "$extract_entities.entities",
                    "parameters": {},
                    "depends_on": ["extract_entities"]
                },
                {
                    "step_id": "convert_graph_to_table",
                    "tool_id": "GRAPH_TABLE_EXPORTER",
                    "operation": "convert",
                    "input_data": {
                        "graph_data": "$build_graph.graph",
                        "table_type": "edge_list"
                    },
                    "parameters": {},
                    "depends_on": ["build_graph"]
                },
                {
                    "step_id": "generate_vectors",
                    "tool_id": "VECTOR_EMBEDDER",
                    "operation": "embed",
                    "input_data": {
                        "text_data": "$load_source_data.text",
                        "entities": "$extract_entities.entities"
                    },
                    "parameters": {"embedding_model": "sentence-transformers"},
                    "depends_on": ["extract_entities"]
                },
                {
                    "step_id": "cross_modal_synthesis",
                    "tool_id": "CROSS_MODAL_ANALYZER", 
                    "operation": "integrate",
                    "input_data": {
                        "graph_data": "$build_graph.graph",
                        "table_data": "$convert_graph_to_table.table_data", 
                        "vector_data": "$generate_vectors.embeddings"
                    },
                    "parameters": {"integration_mode": "comprehensive"},
                    "depends_on": ["build_graph", "convert_graph_to_table", "generate_vectors"]
                },
                {
                    "step_id": "export_results",
                    "tool_id": "MULTI_FORMAT_EXPORTER", 
                    "operation": "export",
                    "input_data": {
                        "data": "$cross_modal_synthesis.integrated_results",
                        "format": "json",
                        "include_provenance": True
                    },
                    "parameters": {"format": "json", "export_type": "comprehensive"},
                    "depends_on": ["cross_modal_synthesis"]
                }
            ]
        }
        
        return dag

    @staticmethod
    def create_simple_cross_modal_dag(
        source_data_ref: str,
        target_format: str = "all"
    ) -> Dict[str, Any]:
        """Create simplified cross-modal DAG for testing"""
        
        dag = {
            "dag_id": f"simple_cross_modal_{target_format}",
            "description": f"Simple cross-modal conversion to {target_format}",
            "steps": [
                {
                    "step_id": "load_data",
                    "tool_id": "T01_PDF_LOADER",
                    "operation": "load",
                    "input_data": {"file_path": source_data_ref},
                    "parameters": {}
                },
                {
                    "step_id": "extract_entities",
                    "tool_id": "T23A_SPACY_NER",
                    "operation": "extract", 
                    "input_data": "$load_data.text",
                    "parameters": {},
                    "depends_on": ["load_data"]
                },
                {
                    "step_id": "build_graph",
                    "tool_id": "T31_ENTITY_BUILDER",
                    "operation": "build",
                    "input_data": "$extract_entities.entities", 
                    "parameters": {},
                    "depends_on": ["extract_entities"]
                }
            ]
        }
        
        # Add format-specific conversion steps
        if target_format in ["table", "all"]:
            dag["steps"].append({
                "step_id": "convert_to_table",
                "tool_id": "GRAPH_TABLE_EXPORTER",
                "operation": "convert",
                "input_data": {
                    "graph_data": "$build_graph.graph",
                    "table_type": "node_list"
                },
                "parameters": {},
                "depends_on": ["build_graph"]
            })
        
        if target_format in ["vector", "all"]:
            dag["steps"].append({
                "step_id": "generate_embeddings",
                "tool_id": "VECTOR_EMBEDDER", 
                "operation": "embed",
                "input_data": {
                    "text_data": "$load_data.text",
                    "entities": "$extract_entities.entities"
                },
                "parameters": {},
                "depends_on": ["extract_entities"]
            })
        
        if target_format == "all":
            dag["steps"].append({
                "step_id": "cross_modal_integration",
                "tool_id": "CROSS_MODAL_ANALYZER",
                "operation": "integrate",
                "input_data": {
                    "graph_data": "$build_graph.graph",
                    "table_data": "$convert_to_table.table_data",
                    "vector_data": "$generate_embeddings.embeddings"
                },
                "parameters": {"integration_mode": "simple"},
                "depends_on": ["build_graph", "convert_to_table", "generate_embeddings"]
            })
            
        return dag

    @staticmethod
    def get_cross_modal_tool_requirements() -> List[str]:
        """Get list of cross-modal tools required for these workflows"""
        return [
            "GRAPH_TABLE_EXPORTER",
            "CROSS_MODAL_ANALYZER", 
            "VECTOR_EMBEDDER",
            "MULTI_FORMAT_EXPORTER",
            "T01_PDF_LOADER",
            "T23A_SPACY_NER",
            "T31_ENTITY_BUILDER"
        ]

    @staticmethod
    def validate_dag_tool_availability(dag: Dict[str, Any]) -> Dict[str, bool]:
        """Validate that all tools in a DAG are available in the registry"""
        from ..core.tool_contract import get_tool_registry
        
        registry = get_tool_registry()
        available_tools = set(registry.list_tools())
        
        tool_availability = {}
        for step in dag.get("steps", []):
            tool_id = step.get("tool_id")
            if tool_id:
                tool_availability[tool_id] = tool_id in available_tools
        
        return tool_availability