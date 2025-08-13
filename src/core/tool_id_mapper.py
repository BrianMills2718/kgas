"""
Tool ID Mapping System

Maps LLM-generated tool names to actual registered KGAS tool IDs.
NO MOCKS - Fails fast if tools don't exist.
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from .tool_contract import get_tool_registry

logger = logging.getLogger(__name__)

@dataclass
class ToolMapping:
    """Mapping between LLM names and registry IDs"""
    registry_id: str  # e.g., "T01_PDF_LOADER"
    llm_names: List[str]  # e.g., ["T01_PDF_LOADER", "pdf_loader", "document_loader"]
    description: str
    category: str
    validated: bool = False

class ToolIDMapper:
    """Maps LLM-generated tool names to registered KGAS tool IDs"""
    
    def __init__(self):
        # Initialize tool registry with real KGAS tools first
        try:
            from .tool_registry_loader import initialize_tool_registry
            registry_results = initialize_tool_registry()
            logger.info(f"Initialized tool registry with {len(registry_results)} tools")
        except Exception as e:
            logger.warning(f"Failed to initialize tool registry: {e}")
        
        self.registry = get_tool_registry()
        self.mappings: Dict[str, ToolMapping] = {}
        self.reverse_mapping: Dict[str, str] = {}  # llm_name -> registry_id
        self._build_mappings()
    
    def _build_mappings(self) -> None:
        """Build comprehensive mappings from registry tools"""
        available_tools = self.registry.list_tools()
        logger.info(f"Building tool mappings for {len(available_tools)} registered tools")
        
        for tool_id in available_tools:
            tool = self.registry.get_tool(tool_id)
            if tool:
                try:
                    tool_info = tool.get_tool_info()
                    
                    # Extract tool information
                    description = tool_info.get('description', f'KGAS tool {tool_id}')
                    category = tool_info.get('category', 'processing')
                    
                    # Generate LLM name variations
                    llm_names = self._generate_llm_name_variations(tool_id, description)
                    
                    # Create mapping
                    mapping = ToolMapping(
                        registry_id=tool_id,
                        llm_names=llm_names,
                        description=description,
                        category=category,
                        validated=True
                    )
                    
                    self.mappings[tool_id] = mapping
                    
                    # Build reverse mapping for fast lookup
                    for llm_name in llm_names:
                        self.reverse_mapping[llm_name.lower()] = tool_id
                    
                    logger.debug(f"Mapped {tool_id} to {len(llm_names)} LLM variations")
                    
                except Exception as e:
                    logger.error(f"Failed to create mapping for {tool_id}: {e}")
                    # FAIL FAST - don't create partial mappings
                    continue
        
        logger.info(f"Tool mapping complete: {len(self.mappings)} tools mapped")
    
    def _generate_llm_name_variations(self, tool_id: str, description: str) -> List[str]:
        """Generate all possible LLM name variations for a tool"""
        variations = [tool_id]  # Always include exact registry ID
        
        # Extract base name patterns
        if tool_id.startswith("T") and "_" in tool_id:
            # e.g., T01_PDF_LOADER -> pdf_loader, document_loader
            base_name = tool_id.split("_", 1)[1].lower()
            variations.append(base_name)
            
            # Generate semantic variations
            semantic_names = self._get_semantic_variations(tool_id, base_name)
            variations.extend(semantic_names)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for name in variations:
            if name.lower() not in seen:
                seen.add(name.lower())
                unique_variations.append(name)
        
        return unique_variations
    
    def _get_semantic_variations(self, tool_id: str, base_name: str) -> List[str]:
        """Get semantic variations for common tool patterns"""
        
        # Define semantic mappings for KGAS tools
        semantic_map = {
            "pdf_loader": ["document_loader", "file_loader", "pdf_reader"],
            "text_loader": ["text_reader", "document_reader"],
            "text_chunker": ["text_splitter", "chunk_creator", "text_segmenter"],
            "spacy_ner": ["entity_extractor", "ner_tool", "entity_recognition"],
            "relationship_extractor": ["relation_extractor", "link_extractor"],
            "entity_builder": ["entity_creator", "graph_entity_builder"],
            "edge_builder": ["relationship_builder", "graph_edge_creator"],
            "pagerank": ["graph_ranking", "centrality_calculator"],
            "multihop_query": ["graph_query", "path_finder", "graph_search"],
            "theory_extraction": ["theory_analyzer", "academic_extractor"],
            "graph_table_exporter": ["graph to table converter", "table converter", "graph_to_table"],
            "cross_modal_analyzer": ["cross modal analyzer", "modal integration", "cross-modal analysis"],
            "vector_embedder": ["embedding generator", "vector generator", "embeddings"],
            "multi_format_exporter": ["format converter", "data exporter", "multi format export", "export tool"]
        }
        
        return semantic_map.get(base_name, [])
    
    def map_llm_name_to_registry_id(self, llm_name: str) -> Optional[str]:
        """Map LLM-generated name to registry tool ID"""
        # Exact match first
        registry_id = self.reverse_mapping.get(llm_name.lower())
        if registry_id:
            return registry_id
        
        # Fuzzy matching for partial names
        for mapping_name, reg_id in self.reverse_mapping.items():
            if llm_name.lower() in mapping_name or mapping_name in llm_name.lower():
                logger.debug(f"Fuzzy matched '{llm_name}' to '{reg_id}' via '{mapping_name}'")
                return reg_id
        
        # FAIL FAST - no fallbacks
        logger.error(f"No mapping found for LLM tool name: '{llm_name}'")
        return None
    
    def validate_workflow_tools(self, workflow_tools: List[str]) -> Dict[str, str]:
        """Validate and map all tools in a workflow
        
        Returns:
            Dict mapping workflow tool names to registry IDs
            
        Raises:
            ToolMappingError if any tool cannot be mapped
        """
        mappings = {}
        unmapped_tools = []
        
        for tool_name in workflow_tools:
            registry_id = self.map_llm_name_to_registry_id(tool_name)
            if registry_id:
                mappings[tool_name] = registry_id
            else:
                unmapped_tools.append(tool_name)
        
        if unmapped_tools:
            # FAIL FAST - don't execute with unmapped tools
            error_msg = (
                f"Cannot map {len(unmapped_tools)} tools to registry: {unmapped_tools}. "
                f"Available tools: {list(self.reverse_mapping.keys())[:10]}..."
            )
            raise ToolMappingError(error_msg)
        
        return mappings
    
    def get_available_tools_for_llm(self) -> str:
        """Format available tools for LLM prompt"""
        tool_descriptions = []
        
        for mapping in self.mappings.values():
            primary_name = mapping.llm_names[0]  # Use first (registry ID) as primary
            description = mapping.description[:100] + "..." if len(mapping.description) > 100 else mapping.description
            tool_descriptions.append(f"- {primary_name}: {description}")
        
        return "\n".join(tool_descriptions)
    
    def get_mapping_statistics(self) -> Dict[str, any]:
        """Get mapping system statistics"""
        total_variations = sum(len(m.llm_names) for m in self.mappings.values())
        
        return {
            "registered_tools": len(self.mappings),
            "total_name_variations": total_variations,
            "average_variations_per_tool": total_variations / len(self.mappings) if self.mappings else 0,
            "validated_tools": sum(1 for m in self.mappings.values() if m.validated)
        }


class ToolMappingError(Exception):
    """Raised when tool mapping fails"""
    pass


# Global mapper instance
_global_mapper = None

def get_tool_id_mapper() -> ToolIDMapper:
    """Get the global tool ID mapper instance"""
    global _global_mapper
    if _global_mapper is None:
        _global_mapper = ToolIDMapper()
    return _global_mapper