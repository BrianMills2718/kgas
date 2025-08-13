"""
Tool Registry Loader

Automatically discovers and registers all KGAS tools in the system.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Type, Any
from src.core.tool_contract import KGASTool, register_tool, get_tool_registry

logger = logging.getLogger(__name__)

class ToolRegistryLoader:
    """Loads and registers all KGAS tools automatically"""
    
    def __init__(self):
        self.tool_classes: Dict[str, Type[KGASTool]] = {}
        self.tool_instances: Dict[str, KGASTool] = {}
    
    def discover_and_register_all_tools(self) -> Dict[str, str]:
        """Discover and register all KGAS tools in the system"""
        registry_results = {}
        
        # Tool discovery paths
        tool_paths = [
            "src.tools.phase1",
            "src.tools.phase2", 
            "src.tools.phase3",
            "src.tools.cross_modal",
            "src.tools.phase_c"
        ]
        
        for tool_path in tool_paths:
            try:
                discovered = self._discover_tools_in_module(tool_path)
                registry_results.update(discovered)
                logger.info(f"Discovered {len(discovered)} tools in {tool_path}")
            except Exception as e:
                logger.error(f"Failed to discover tools in {tool_path}: {e}")
        
        return registry_results
    
    def _discover_tools_in_module(self, module_path: str) -> Dict[str, str]:
        """Discover tools in a specific module"""
        discovered_tools = {}
        
        try:
            # Get the module directory
            if module_path == "src.tools.phase1":
                tool_dir = Path("src/tools/phase1")
                priority_tools = self._get_priority_phase1_tools()
            elif module_path == "src.tools.phase2":
                tool_dir = Path("src/tools/phase2")
                priority_tools = self._get_priority_phase2_tools()
            elif module_path == "src.tools.phase3":
                tool_dir = Path("src/tools/phase3")
                priority_tools = self._get_priority_phase3_tools()
            elif module_path == "src.tools.cross_modal":
                tool_dir = Path("src/tools/cross_modal")
                priority_tools = self._get_cross_modal_tools()
            elif module_path == "src.tools.phase_c":
                tool_dir = Path("src/tools/phase_c")
                priority_tools = self._get_phase_c_tools()
            else:
                return discovered_tools
            
            # Discover and register priority tools first
            for tool_file, tool_id in priority_tools.items():
                try:
                    result = self._register_tool_from_file(tool_dir / tool_file, tool_id)
                    if result:
                        discovered_tools[tool_id] = result
                except Exception as e:
                    logger.warning(f"Failed to register {tool_id} from {tool_file}: {e}")
            
            return discovered_tools
            
        except Exception as e:
            logger.error(f"Module discovery failed for {module_path}: {e}")
            return discovered_tools
    
    def _get_priority_phase1_tools(self) -> Dict[str, str]:
        """Get priority Phase 1 tools for vertical slice"""
        return {
            # Working KGAS tools with proper KGASTool interface
            "t01_pdf_loader_kgas.py": "T01_PDF_LOADER",
            "t15a_text_chunker_kgas.py": "T15A_TEXT_CHUNKER",
            "t31_entity_builder_kgas.py": "T31_ENTITY_BUILDER",
            "t68_pagerank_kgas.py": "T68_PAGERANK"
            # Note: T34 and T49 need KGAS wrappers to be created
        }
    
    def _get_priority_phase2_tools(self) -> Dict[str, str]:
        """Get priority Phase 2 tools"""
        return {
            "t23c_ontology_aware_extractor_kgas.py": "T23C_ONTOLOGY_AWARE",
            "t50_community_detection_unified.py": "T50_COMMUNITY_DETECTION",
            "t51_centrality_analysis.py": "T51_CENTRALITY_ANALYSIS"
        }
    
    def _get_priority_phase3_tools(self) -> Dict[str, str]:
        """Get priority Phase 3 tools"""
        return {
            "t302_theory_extraction_kgas.py": "T302_THEORY_EXTRACTION",
            "t301_multi_document_fusion.py": "T301_MULTI_DOCUMENT_FUSION"
        }
    
    def _get_cross_modal_tools(self) -> Dict[str, str]:
        """Get cross-modal tools for registry integration"""
        return {
            # Use base implementations (working) instead of unified (broken)
            "graph_table_exporter.py": "GRAPH_TABLE_EXPORTER", 
            "multi_format_exporter.py": "MULTI_FORMAT_EXPORTER"
        }
    
    def _get_phase_c_tools(self) -> Dict[str, str]:
        """Get phase C tools for registry integration"""
        return {
            "cross_modal_tool.py": "CROSS_MODAL_ANALYZER"
        }
    
    def _register_tool_from_file(self, file_path: Path, tool_id: str) -> str:
        """Register a tool from a specific file"""
        try:
            if not file_path.exists():
                return None
                
            # Convert file path to module path
            module_path = str(file_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find the tool class in the module
            tool_class = self._find_tool_class_in_module(module, tool_id)
            
            if tool_class:
                try:
                    # Create tool instance for registry
                    tool_instance = self._create_tool_instance(tool_class, tool_id)
                    
                    if tool_instance:
                        # Register with global registry
                        registry = get_tool_registry()
                        registry.register_tool(tool_instance)
                        
                        self.tool_classes[tool_id] = tool_class
                        self.tool_instances[tool_id] = tool_instance
                        
                        logger.debug(f"Registered tool {tool_id} from {file_path}")
                        return f"Registered {tool_id}"
                    else:
                        logger.warning(f"Failed to create instance for {tool_id}")
                        return None
                except Exception as e:
                    logger.error(f"Failed to instantiate {tool_id}: {e}")
                    return None
            else:
                logger.warning(f"No tool class found in {file_path} for {tool_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to register tool from {file_path}: {e}")
            return None
    
    def _find_tool_class_in_module(self, module: Any, tool_id: str) -> Type[KGASTool]:
        """Find the main tool class in a module"""
        
        # Common class naming patterns for each tool (KGAS-compatible classes)
        class_patterns = {
            # Working KGAS tools
            "T01_PDF_LOADER": ["T01PDFLoaderKGAS"],
            "T15A_TEXT_CHUNKER": ["T15ATextChunkerKGAS"],
            "T23C_ONTOLOGY_AWARE": ["T23COntologyAwareExtractorKGAS"],
            "T31_ENTITY_BUILDER": ["T31EntityBuilderKGAS"],
            "T68_PAGERANK": ["T68PageRankKGAS"],
            # Working cross-modal tools (base implementations)
            "GRAPH_TABLE_EXPORTER": ["GraphTableExporter"],
            "MULTI_FORMAT_EXPORTER": ["MultiFormatExporter"],
            # Removed broken/deprecated tools
        }
        
        patterns = class_patterns.get(tool_id, [])
        
        # Look for classes by pattern
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name in patterns:
                return obj
        
        # Fallback: look for any class that might be a tool
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, 'tool_id'):
                return obj
                
        return None
    
    def _create_tool_registry_entry(self, tool_class: Type[KGASTool], tool_id: str) -> Dict[str, Any]:
        """Create a registry entry for a tool class"""
        
        # Tool descriptions
        descriptions = {
            "T01_PDF_LOADER": "Extract text content from PDF documents",
            "T03_TEXT_LOADER": "Load plain text documents and files",
            "T15A_TEXT_CHUNKER": "Split text into manageable chunks for processing",
            "VECTOR_EMBEDDER": "Generate vector embeddings for text and entities",
            "T23A_SPACY_NER": "Extract named entities using spaCy NLP models",
            "T27_RELATIONSHIP_EXTRACTOR": "Extract relationships between entities",
            "T31_ENTITY_BUILDER": "Build graph entities from extracted mentions",
            "T34_EDGE_BUILDER": "Create graph edges from extracted relationships",
            "T49_MULTIHOP_QUERY": "Perform multi-hop queries on knowledge graphs",
            "T68_PAGERANK": "Calculate PageRank centrality scores for entities",
            "T302_THEORY_EXTRACTION": "Extract academic theories from documents",
            "T301_MULTI_DOCUMENT_FUSION": "Fuse knowledge from multiple documents",
            "GRAPH_TABLE_EXPORTER": "Convert graph data to table format for analysis",
            "CROSS_MODAL_ANALYZER": "Integrate and analyze across multiple data modalities",
            "MULTI_FORMAT_EXPORTER": "Export data to multiple formats (JSON, CSV, XML, LaTeX)"
        }
        
        # Tool categories
        categories = {
            "T01_PDF_LOADER": "document_loader",
            "T03_TEXT_LOADER": "document_loader", 
            "T15A_TEXT_CHUNKER": "text_processing",
            "VECTOR_EMBEDDER": "vector_processing",
            "T23A_SPACY_NER": "entity_extraction",
            "T27_RELATIONSHIP_EXTRACTOR": "relationship_extraction",
            "T31_ENTITY_BUILDER": "graph_construction",
            "T34_EDGE_BUILDER": "graph_construction",
            "T49_MULTIHOP_QUERY": "graph_query",
            "T68_PAGERANK": "graph_analysis",
            "T302_THEORY_EXTRACTION": "theory_processing",
            "T301_MULTI_DOCUMENT_FUSION": "document_fusion",
            "GRAPH_TABLE_EXPORTER": "cross_modal_conversion",
            "CROSS_MODAL_ANALYZER": "cross_modal_integration",
            "MULTI_FORMAT_EXPORTER": "data_export"
        }
        
        return {
            "tool_id": tool_id,
            "name": tool_class.__name__ if hasattr(tool_class, '__name__') else tool_id,
            "description": descriptions.get(tool_id, f"KGAS tool {tool_id}"),
            "category": categories.get(tool_id, "processing"),
            "tool_class": tool_class,
            "file_path": inspect.getfile(tool_class) if tool_class else None
        }
    
    def get_registered_tools(self) -> List[str]:
        """Get list of registered tool IDs"""
        return list(self.tool_classes.keys())
    
    def get_tool_class(self, tool_id: str) -> Type[KGASTool]:
        """Get tool class by ID"""
        return self.tool_classes.get(tool_id)
    
    def _create_tool_instance(self, tool_class: Type[KGASTool], tool_id: str) -> KGASTool:
        """Create a tool instance from tool class for registry"""
        try:
            # Get service manager for KGAS tools
            from ..core.service_manager import get_service_manager
            service_manager = get_service_manager()
            
            # Try different constructor patterns based on tool type and class name
            import inspect
            signature = inspect.signature(tool_class.__init__)
            params = list(signature.parameters.keys())[1:]  # Skip 'self'
            
            # Pattern 1: service_manager parameter (KGAS tools only)
            if ('service_manager' in params or 
                tool_id.endswith("_KGAS") or "KGAS" in str(tool_class.__name__)):
                return tool_class(service_manager=service_manager)
            
            # Pattern 2: services parameter (some archived tools)
            elif 'services' in params:
                return tool_class(services=service_manager)
            
            # Pattern 3: Individual service parameters (legacy tools)
            elif all(param in params for param in ['identity_service', 'provenance_service', 'quality_service']):
                return tool_class(
                    identity_service=service_manager.identity_service,
                    provenance_service=service_manager.provenance_service,
                    quality_service=service_manager.quality_service
                )
            
            # Pattern 4: No parameters (standalone tools and cross-modal tools)
            elif (not params or all(p.default != inspect.Parameter.empty for p in signature.parameters.values() if p.name != 'self') or
                  tool_id in ["GRAPH_TABLE_EXPORTER", "MULTI_FORMAT_EXPORTER", "CROSS_MODAL_ANALYZER"]):
                return tool_class()
            
            else:
                # Log the parameters for debugging
                logger.debug(f"Unknown constructor pattern for {tool_id}: {params}")
                # Try with service_manager first, then fall back
                try:
                    return tool_class(service_manager=service_manager)
                except TypeError:
                    return tool_class()
            
        except Exception as e:
            logger.error(f"Failed to create instance of {tool_id}: {e}")
            logger.debug(f"Tool class: {tool_class}, Parameters: {params if 'params' in locals() else 'unknown'}")
            return None

    def create_tool_instance(self, tool_id: str) -> KGASTool:
        """Create an instance of a tool"""
        tool_class = self.tool_classes.get(tool_id)
        if tool_class:
            try:
                # Try to create instance with service manager
                from src.core.service_manager import get_service_manager
                service_manager = get_service_manager()
                
                # Different tools have different constructor patterns
                if tool_id in ["T01_PDF_LOADER", "T03_TEXT_LOADER"]:
                    return tool_class()  # These don't need service manager
                else:
                    return tool_class(
                        identity_service=service_manager.identity_service,
                        provenance_service=service_manager.provenance_service,
                        quality_service=service_manager.quality_service
                    )
            except Exception as e:
                logger.error(f"Failed to create instance of {tool_id}: {e}")
                # Fallback: try without services
                return tool_class()
        return None


# Global registry loader
_global_registry_loader = None

def get_tool_registry_loader() -> ToolRegistryLoader:
    """Get the global tool registry loader"""
    global _global_registry_loader
    if _global_registry_loader is None:
        _global_registry_loader = ToolRegistryLoader()
    return _global_registry_loader

def initialize_tool_registry() -> Dict[str, str]:
    """Initialize the tool registry with all discovered tools"""
    loader = get_tool_registry_loader()
    return loader.discover_and_register_all_tools()