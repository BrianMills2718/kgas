"""
Tool Schema Registry

Registry of all tool schemas for compatibility checking.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ToolSchemaRegistry:
    """Registry of all tool schemas for compatibility checking."""
    
    def __init__(self):
        self.schemas = {}
        self.logger = logging.getLogger(__name__)
        self._load_schemas()
    
    def _load_schemas(self):
        """Load schemas from tools or cached files."""
        # Try to load from each tool directly
        tool_modules = [
            # Phase 1 Tools
            ("T01", "src.tools.phase1.t01_pdf_loader_unified", "PDFLoaderUnified"),
            ("T15A", "src.tools.phase1.t15a_text_chunker_unified", "T15ATextChunkerUnified"),
            ("T23A", "src.tools.phase1.t23a_spacy_ner_unified", "SpacyNERUnified"), 
            ("T23C", "src.tools.phase2.t23c_ontology_aware_extractor_unified", "OntologyAwareExtractor"),
            ("T27", "src.tools.phase1.t27_relationship_extractor_unified", "RelationshipExtractorUnified"),
            ("T31", "src.tools.phase1.t31_entity_builder_unified", "T31EntityBuilderUnified"),
            ("T34", "src.tools.phase1.t34_edge_builder_unified", "T34EdgeBuilderUnified"),
            ("T49", "src.tools.phase1.t49_multihop_query_unified", "MultiHopQueryUnified"),
            ("T68", "src.tools.phase1.t68_pagerank_unified", "PageRankUnified"),
            
            # Phase 2 Tools
            ("T50", "src.tools.phase2.t50_community_detection_unified", "CommunityDetectionUnified"),
            ("T51", "src.tools.phase2.t51_centrality_analysis_unified", "CentralityAnalysisUnified"),
            ("T52", "src.tools.phase2.t52_graph_clustering_unified", "GraphClusteringUnified"),
            ("T53", "src.tools.phase2.t53_network_motifs_unified", "NetworkMotifsUnified"),
            ("T54", "src.tools.phase2.t54_graph_visualization_unified", "GraphVisualizationUnified"),
            ("T55", "src.tools.phase2.t55_temporal_analysis_unified", "TemporalAnalysisUnified"),
            ("T56", "src.tools.phase2.t56_graph_metrics_unified", "GraphMetricsUnified"),
            ("T57", "src.tools.phase2.t57_path_analysis_unified", "PathAnalysisUnified"),
            ("T58", "src.tools.phase2.t58_graph_comparison_unified", "GraphComparisonUnified"),
            ("T59", "src.tools.phase2.t59_scale_free_analysis_unified", "ScaleFreeAnalysisUnified"),
            ("T60", "src.tools.phase2.t60_graph_export_unified", "GraphExportUnified"),
            
            # Cross-modal Tools
            ("GraphTableExporter", "src.tools.cross_modal.graph_table_exporter", "GraphTableExporter"),
            ("VectorEmbedder", "src.tools.cross_modal.vector_embedder", "VectorEmbedder"),
        ]
        
        # Also load known schemas for tools we can't import
        self._load_known_schemas()
        
        for tool_id, module_path, class_name in tool_modules:
            try:
                # Try to import and get contract
                module = __import__(module_path, fromlist=[class_name])
                tool_class = getattr(module, class_name)
                
                # Try to get contract without instantiating if possible
                if hasattr(tool_class, 'get_contract_static'):
                    contract = tool_class.get_contract_static()
                else:
                    # Need to instantiate - provide minimal args
                    try:
                        tool = tool_class(service_manager=None)
                        if hasattr(tool, 'get_contract'):
                            contract = tool.get_contract()
                            self.schemas[tool_id] = {
                                "input": contract.input_schema,
                                "output": contract.output_schema
                            }
                    except:
                        pass
                        
            except Exception as e:
                self.logger.debug(f"Could not load schema for {tool_id}: {e}")
    
    def _load_known_schemas(self):
        """Load known schemas for common tools."""
        # T23C output schema
        self.schemas["T23C"] = {
            "input": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "chunk_ref": {"type": "string"},
                    "source_ref": {"type": "string"},
                    "extraction_schema": {"type": "string"}
                },
                "required": ["text"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "entities": {"type": "array"},
                    "relationships": {"type": "array"},
                    "mentions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "mention_id": {"type": "string"},
                                "surface_form": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "entity_id": {"type": "string"},
                                "confidence": {"type": "number"},
                                "source_ref": {"type": "string"}
                            }
                        }
                    },
                    "entity_count": {"type": "integer"},
                    "relationship_count": {"type": "integer"}
                },
                "required": ["entities", "relationships", "mentions"]
            }
        }
        
        # T31 input/output schemas
        self.schemas["T31"] = {
            "input": {
                "type": "object",
                "properties": {
                    "mentions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"},
                                "entity_type": {"type": "string"},
                                "entity_id": {"type": "string"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["text", "entity_type"]
                        }
                    },
                    "source_refs": {"type": "array"}
                },
                "required": ["mentions", "source_refs"]
            },
            "output": {
                "type": "object", 
                "properties": {
                    "entities": {"type": "array"},
                    "entity_count": {"type": "integer"},
                    "mention_count": {"type": "integer"}
                },
                "required": ["entity_count"]
            }
        }
        
        # T34 input schema
        self.schemas["T34"] = {
            "input": {
                "type": "object",
                "properties": {
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subject": {
                                    "type": "object",
                                    "properties": {
                                        "entity_id": {"type": "string"},
                                        "canonical_name": {"type": "string"},
                                        "text": {"type": "string"},
                                        "entity_type": {"type": "string"}
                                    }
                                },
                                "object": {
                                    "type": "object",
                                    "properties": {
                                        "entity_id": {"type": "string"},
                                        "canonical_name": {"type": "string"},
                                        "text": {"type": "string"},
                                        "entity_type": {"type": "string"}
                                    }
                                },
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"}
                            },
                            "required": ["subject", "object", "relationship_type"]
                        }
                    },
                    "source_refs": {"type": "array"}
                },
                "required": ["relationships", "source_refs"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "edge_count": {"type": "integer"},
                    "relationships": {"type": "array"}
                }
            }
        }
        
        # T15A schemas
        self.schemas["T15A"] = {
            "input": {
                "type": "object",
                "properties": {
                    "document_ref": {"type": "string"},
                    "text": {"type": "string"},
                    "document_confidence": {"type": "number"}
                },
                "required": ["document_ref", "text"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "chunks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chunk_id": {"type": "string"},
                                "text": {"type": "string"},
                                "start_pos": {"type": "integer"},
                                "end_pos": {"type": "integer"}
                            }
                        }
                    },
                    "chunk_count": {"type": "integer"}
                }
            }
        }
    
    def get_schema(self, tool_id: str) -> Dict[str, Any]:
        """Get input/output schemas for a tool."""
        return self.schemas.get(tool_id, {"input": {}, "output": {}})
    
    def get_all_tool_ids(self) -> List[str]:
        """Get all registered tool IDs."""
        return list(self.schemas.keys())
    
    def save_schemas(self, path: Path):
        """Save schemas to file for documentation."""
        with open(path, 'w') as f:
            json.dump(self.schemas, f, indent=2)
    
    def validate_tool_pair(self, source_tool: str, target_tool: str) -> Dict[str, Any]:
        """Check if source tool output is compatible with target tool input."""
        source_schema = self.get_schema(source_tool)
        target_schema = self.get_schema(target_tool)
        
        if not source_schema["output"] or not target_schema["input"]:
            return {
                "compatible": False,
                "reason": "Missing schema information"
            }
        
        # Check if output properties match input requirements
        output_props = source_schema["output"].get("properties", {})
        input_props = target_schema["input"].get("properties", {})
        input_required = target_schema["input"].get("required", [])
        
        missing_fields = []
        for required_field in input_required:
            if required_field not in output_props:
                # Check for known mappings
                if not self._has_field_mapping(source_tool, target_tool, required_field):
                    missing_fields.append(required_field)
        
        return {
            "compatible": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "needs_adapter": len(missing_fields) > 0
        }
    
    def _has_field_mapping(self, source_tool: str, target_tool: str, field: str) -> bool:
        """Check if there's a known field mapping."""
        known_mappings = {
            ("T23C", "T31", "text"): "surface_form",  # T23C outputs surface_form, T31 expects text
            ("T23C", "T34", "subject"): "head_entity",  # T23C outputs head_entity, T34 expects subject
            ("T23C", "T34", "object"): "tail_entity",  # T23C outputs tail_entity, T34 expects object
        }
        
        return (source_tool, target_tool, field) in known_mappings


def validate_pipeline_schemas(tool_sequence: List[str]) -> Dict[str, Any]:
    """Validate schemas for a pipeline of tools."""
    registry = ToolSchemaRegistry()
    validation_results = []
    
    for i in range(len(tool_sequence) - 1):
        source = tool_sequence[i]
        target = tool_sequence[i + 1]
        
        result = registry.validate_tool_pair(source, target)
        validation_results.append({
            "source": source,
            "target": target,
            "compatible": result["compatible"],
            "issues": result.get("missing_fields", [])
        })
    
    return {
        "valid": all(r["compatible"] for r in validation_results),
        "results": validation_results
    }