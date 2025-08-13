"""
MCP Tool Registry - Organized Tool Discovery and Mapping

Provides a structured way to organize and discover the 121 KGAS tools
through clear, descriptive names and capability-based organization.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class MCPToolMapping:
    """Mapping between MCP operation and internal tool"""
    mcp_name: str
    tool_id: str
    description: str
    category: str
    subcategory: str
    parameter_mapping: Dict[str, str]
    implementation_type: str  # e.g., "spacy", "llm", "hybrid"

class MCPToolRegistry:
    """Registry for organizing and discovering MCP-exposed tools"""
    
    def __init__(self):
        self.tools: Dict[str, MCPToolMapping] = {}
        self.categories: Dict[str, Dict[str, List[str]]] = {}
        self._load_tool_mappings()
    
    def _load_tool_mappings(self):
        """Load tool mappings from configuration"""
        # For now, define core mappings directly
        # Later: load from YAML files
        self._register_extraction_tools()
        self._register_graph_tools()
        self._register_document_tools()
        self._build_category_index()
    
    def _register_extraction_tools(self):
        """Register entity and relationship extraction tools"""
        extractions = [
            MCPToolMapping(
                mcp_name="extract_entities_spacy",
                tool_id="T23A_SPACY_NER",
                description="Extract named entities using spaCy NLP (fast, reliable)",
                category="extraction",
                subcategory="entities",
                parameter_mapping={
                    "text": "input_data.text",
                    "confidence_threshold": "parameters.confidence_threshold",
                    "source_ref": "input_data.source_ref"
                },
                implementation_type="spacy"
            ),
            MCPToolMapping(
                mcp_name="extract_entities_ontology_aware",
                tool_id="T23C_ONTOLOGY_AWARE_EXTRACTOR", 
                description="Extract entities with ontology validation and LLM enhancement",
                category="extraction",
                subcategory="entities",
                parameter_mapping={
                    "text": "input_data.text",
                    "source_ref": "input_data.source_ref",
                    "ontology_filter": "parameters.ontology_filter"
                },
                implementation_type="hybrid"
            ),
            MCPToolMapping(
                mcp_name="extract_relationships_pattern",
                tool_id="T27_RELATIONSHIP_EXTRACTOR",
                description="Extract relationships using pattern matching and NLP",
                category="extraction", 
                subcategory="relationships",
                parameter_mapping={
                    "text": "input_data.text",
                    "entities": "input_data.entities",
                    "relationship_types": "parameters.relationship_types"
                },
                implementation_type="pattern"
            )
        ]
        
        for tool in extractions:
            self.tools[tool.mcp_name] = tool
    
    def _register_graph_tools(self):
        """Register graph analysis and manipulation tools"""
        graph_tools = [
            MCPToolMapping(
                mcp_name="build_graph_entities",
                tool_id="T31_ENTITY_BUILDER",
                description="Build graph nodes from extracted entities",
                category="graph",
                subcategory="build",
                parameter_mapping={
                    "entities": "input_data.entities",
                    "merge_strategy": "parameters.merge_strategy"
                },
                implementation_type="neo4j"
            ),
            MCPToolMapping(
                mcp_name="build_graph_relationships", 
                tool_id="T34_EDGE_BUILDER",
                description="Build graph edges from extracted relationships",
                category="graph",
                subcategory="build", 
                parameter_mapping={
                    "relationships": "input_data.relationships",
                    "weight_strategy": "parameters.weight_strategy"
                },
                implementation_type="neo4j"
            ),
            MCPToolMapping(
                mcp_name="analyze_graph_pagerank",
                tool_id="T68_PAGERANK",
                description="Calculate PageRank centrality scores for graph nodes",
                category="graph",
                subcategory="analyze",
                parameter_mapping={
                    "iterations": "parameters.iterations",
                    "damping_factor": "parameters.damping_factor"
                },
                implementation_type="networkx"
            ),
            MCPToolMapping(
                mcp_name="query_graph_multihop",
                tool_id="T49_MULTIHOP_QUERY", 
                description="Execute multi-hop queries across graph relationships",
                category="graph",
                subcategory="query",
                parameter_mapping={
                    "query_text": "input_data.query_text",
                    "max_hops": "parameters.max_hops",
                    "result_limit": "parameters.result_limit"
                },
                implementation_type="cypher"
            ),
            MCPToolMapping(
                mcp_name="analyze_graph_communities",
                tool_id="T50_COMMUNITY_DETECTION",
                description="Detect communities and clusters in graph structure",
                category="graph", 
                subcategory="analyze",
                parameter_mapping={
                    "algorithm": "parameters.algorithm",
                    "resolution": "parameters.resolution"
                },
                implementation_type="networkx"
            )
        ]
        
        for tool in graph_tools:
            self.tools[tool.mcp_name] = tool
    
    def _register_document_tools(self):
        """Register document loading and processing tools"""
        doc_tools = [
            MCPToolMapping(
                mcp_name="load_document_pdf",
                tool_id="T01_PDF_LOADER",
                description="Load and extract text from PDF documents",
                category="documents",
                subcategory="load",
                parameter_mapping={
                    "file_path": "input_data.file_path",
                    "extract_images": "parameters.extract_images"
                },
                implementation_type="pypdf"
            ),
            MCPToolMapping(
                mcp_name="load_document_text",
                tool_id="T03_TEXT_LOADER", 
                description="Load plain text documents with encoding detection",
                category="documents",
                subcategory="load",
                parameter_mapping={
                    "file_path": "input_data.file_path",
                    "encoding": "parameters.encoding"
                },
                implementation_type="file"
            ),
            MCPToolMapping(
                mcp_name="process_text_chunk",
                tool_id="T15A_TEXT_CHUNKER",
                description="Split text into overlapping chunks for processing",
                category="documents",
                subcategory="process", 
                parameter_mapping={
                    "text": "input_data.text",
                    "chunk_size": "parameters.chunk_size",
                    "overlap": "parameters.overlap"
                },
                implementation_type="nltk"
            )
        ]
        
        for tool in doc_tools:
            self.tools[tool.mcp_name] = tool
    
    def _build_category_index(self):
        """Build searchable category index"""
        for tool in self.tools.values():
            if tool.category not in self.categories:
                self.categories[tool.category] = {}
            if tool.subcategory not in self.categories[tool.category]:
                self.categories[tool.category][tool.subcategory] = []
            self.categories[tool.category][tool.subcategory].append(tool.mcp_name)
    
    def get_tool_by_name(self, mcp_name: str) -> Optional[MCPToolMapping]:
        """Get tool mapping by MCP name"""
        return self.tools.get(mcp_name)
    
    def get_tool_id(self, mcp_name: str) -> Optional[str]:
        """Get internal tool ID for MCP name"""
        tool = self.get_tool_by_name(mcp_name)
        return tool.tool_id if tool else None
    
    def list_tools_by_category(self, category: str, subcategory: str = None) -> List[str]:
        """List tools by category and optional subcategory"""
        if category not in self.categories:
            return []
        
        if subcategory:
            return self.categories[category].get(subcategory, [])
        else:
            # Return all tools in category
            all_tools = []
            for subcat_tools in self.categories[category].values():
                all_tools.extend(subcat_tools)
            return all_tools
    
    def search_tools(self, query: str) -> List[MCPToolMapping]:
        """Search tools by description or name"""
        query_lower = query.lower()
        matches = []
        
        for tool in self.tools.values():
            if (query_lower in tool.mcp_name.lower() or 
                query_lower in tool.description.lower() or
                query_lower in tool.implementation_type.lower()):
                matches.append(tool)
        
        return matches
    
    def get_parameter_mapping(self, mcp_name: str) -> Dict[str, str]:
        """Get parameter mapping for MCP tool"""
        tool = self.get_tool_by_name(mcp_name)
        return tool.parameter_mapping if tool else {}
    
    def list_all_categories(self) -> Dict[str, List[str]]:
        """Get all categories and subcategories"""
        return {cat: list(subcats.keys()) for cat, subcats in self.categories.items()}
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_tools": len(self.tools),
            "categories": len(self.categories),
            "tools_by_category": {
                cat: len(self.list_tools_by_category(cat)) 
                for cat in self.categories.keys()
            },
            "implementation_types": {
                impl_type: len([t for t in self.tools.values() if t.implementation_type == impl_type])
                for impl_type in set(t.implementation_type for t in self.tools.values())
            }
        }


# Global registry instance
_mcp_registry = None

def get_mcp_tool_registry() -> MCPToolRegistry:
    """Get global MCP tool registry instance"""
    global _mcp_registry
    if _mcp_registry is None:
        _mcp_registry = MCPToolRegistry()
    return _mcp_registry


# Convenience functions for MCP integration
def resolve_mcp_tool(mcp_name: str) -> Optional[str]:
    """Resolve MCP tool name to internal tool ID"""
    registry = get_mcp_tool_registry()
    return registry.get_tool_id(mcp_name)

def map_mcp_parameters(mcp_name: str, mcp_params: Dict[str, Any]) -> Dict[str, Any]:
    """Map MCP parameters to internal tool format"""
    registry = get_mcp_tool_registry()
    mapping = registry.get_parameter_mapping(mcp_name)
    
    if not mapping:
        return mcp_params  # No mapping available, return as-is
    
    # Transform parameters according to mapping
    result = {"input_data": {}, "parameters": {}}
    
    for mcp_param, internal_path in mapping.items():
        if mcp_param in mcp_params:
            # Parse internal path (e.g., "input_data.text" -> result["input_data"]["text"])
            path_parts = internal_path.split('.')
            if len(path_parts) == 2:
                section, key = path_parts
                result[section][key] = mcp_params[mcp_param]
            else:
                # Simple mapping
                result[internal_path] = mcp_params[mcp_param]
    
    return result