"""Pipeline Orchestrator - Main coordinator (<200 lines)

Coordinates workflow execution across different engines and monitors.
Provides unified interface for all pipeline operations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from ..logging_config import get_logger
from ..config_manager import ConfigurationManager, get_config
from ..tool_protocol import Tool
from .workflow_engines import SequentialEngine, ParallelEngine, AnyIOEngine
from .workflow_engines.theory_enhanced_engine import TheoryEnhancedWorkflow
from .execution_monitors import ProgressMonitor, ErrorMonitor, PerformanceMonitor
from .result_aggregators import SimpleAggregator, GraphAggregator

logger = get_logger("core.orchestration.pipeline_orchestrator")


class OptimizationLevel(Enum):
    """Different optimization levels for pipeline execution"""
    STANDARD = "standard"
    OPTIMIZED = "optimized" 
    ENHANCED = "enhanced"


class Phase(Enum):
    """Supported pipeline phases"""
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution"""
    tools: List[Tool]
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    phase: Phase = Phase.PHASE1
    neo4j_uri: Optional[str] = None
    neo4j_user: Optional[str] = None
    neo4j_password: Optional[str] = None
    confidence_threshold: float = 0.7
    workflow_storage_dir: Optional[str] = None


@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    status: str
    entities: List[Any]
    relationships: List[Any]
    graph_created: bool
    query_enabled: bool
    text_chunks: List[str]
    error: Optional[str] = None


class PipelineOrchestrator:
    """Main pipeline orchestrator with modular architecture
    
    Coordinates execution across specialized engines and monitors.
    Provides single interface for all pipeline operations.
    """
    
    def __init__(self, config: PipelineConfig = None, config_manager: ConfigurationManager = None):
        """Initialize orchestrator with configuration"""
        self.config = config
        self.logger = get_logger("core.orchestration.pipeline_orchestrator")
        self.config_manager = config_manager or get_config()
        
        # Initialize pipeline validator
        from ..pipeline_validator import PipelineValidator
        self.pipeline_validator = PipelineValidator()
        
        # Initialize workflow engines
        self._initialize_engines()
        
        # Initialize execution monitors
        self._initialize_monitors()
        
        # Initialize result aggregators
        self._initialize_aggregators()
        
        # Select engine based on optimization level
        self._select_execution_engine()
        
        # Validate pipeline if config provided
        if self.config and self.config.tools:
            self._validate_pipeline()
        
    def _initialize_engines(self):
        """Initialize workflow execution engines"""
        self.sequential_engine = SequentialEngine(self.config_manager)
        self.parallel_engine = ParallelEngine(self.config_manager)
        self.anyio_engine = AnyIOEngine(self.config_manager)
        
    def _initialize_monitors(self):
        """Initialize execution monitoring components"""
        self.progress_monitor = ProgressMonitor()
        self.error_monitor = ErrorMonitor()
        self.performance_monitor = PerformanceMonitor()
        
    def _initialize_aggregators(self):
        """Initialize result aggregation components"""
        self.simple_aggregator = SimpleAggregator()
        self.graph_aggregator = GraphAggregator()
        
    def _select_execution_engine(self):
        """Select execution engine based on optimization level"""
        if not self.config:
            self.execution_engine = self.sequential_engine
            return
            
        if self.config.optimization_level == OptimizationLevel.STANDARD:
            self.execution_engine = self.sequential_engine
        elif self.config.optimization_level == OptimizationLevel.OPTIMIZED:
            self.execution_engine = self.parallel_engine
        else:  # ENHANCED
            self.execution_engine = self.anyio_engine
    
    def _validate_pipeline(self):
        """Validate pipeline configuration before execution"""
        is_valid, errors = self.pipeline_validator.validate_pipeline(self.config.tools)
        
        if not is_valid:
            error_msg = "Pipeline validation failed:\n"
            for error in errors:
                error_msg += f"  - {error}\n"
            
            # Get suggestions
            suggestions = self.pipeline_validator.suggest_fixes(errors)
            if suggestions:
                error_msg += "\nSuggestions:\n"
                for suggestion in suggestions:
                    error_msg += f"  - {suggestion}\n"
            
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.info(f"Pipeline validated successfully with {len(self.config.tools)} tools")
            
    def execute(self, document_paths: List[str], queries: List[str] = None) -> Dict[str, Any]:
        """Execute pipeline with configured tools
        
        Args:
            document_paths: List of document paths to process
            queries: Optional list of queries to execute
            
        Returns:
            Complete pipeline execution result with metadata
        """
        # Input validation
        if not document_paths:
            raise ValueError("document_paths cannot be empty")
            
        start_time = time.time()
        
        # Setup execution context
        execution_context = {
            "document_paths": document_paths,
            "queries": queries or [],
            "workflow_id": f"{self.config.phase.value}_{int(start_time)}",
            "start_time": start_time
        }
        
        try:
            # Start monitoring
            self.progress_monitor.start_execution(execution_context)
            self.performance_monitor.start_monitoring()
            
            # Execute pipeline using selected engine
            results = self.execution_engine.execute_pipeline(
                tools=self.config.tools,
                input_data=execution_context,
                monitors=[self.progress_monitor, self.error_monitor, self.performance_monitor]
            )
            
            # Aggregate results
            if self.config.phase == Phase.PHASE1:
                final_results = self.simple_aggregator.aggregate(results)
            else:
                final_results = self.graph_aggregator.aggregate(results)
            
            # Finalize execution
            execution_time = time.time() - start_time
            final_results.update({
                "execution_metadata": {
                    "total_time": execution_time,
                    "success": True,
                    "phase": self.config.phase.value,
                    "optimization_level": self.config.optimization_level.value
                }
            })
            
            return final_results
            
        except Exception as e:
            self.error_monitor.record_error(e)
            execution_time = time.time() - start_time
            
            return {
                "status": "error",
                "error": str(e),
                "execution_metadata": {
                    "total_time": execution_time,
                    "success": False,
                    "phase": self.config.phase.value if self.config else "unknown",
                    "optimization_level": self.config.optimization_level.value if self.config else "unknown"
                }
            }
        finally:
            self.progress_monitor.complete_execution()
            self.performance_monitor.stop_monitoring()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        return {
            "progress": self.progress_monitor.get_progress(),
            "errors": self.error_monitor.get_error_summary(),
            "performance": self.performance_monitor.get_metrics()
        }
    
    def execute_theory_enhanced_workflow(self, pdf_path: str) -> Dict[str, Any]:
        """Execute theory-enhanced workflow for academic papers"""
        
        logger.info(f"Starting theory-enhanced workflow for: {pdf_path}")
        
        try:
            result = TheoryEnhancedWorkflow.execute_theory_pipeline(self, pdf_path)
            
            if result["status"] == "success":
                logger.info("✅ Theory-enhanced workflow completed successfully")
                logger.info(f"   Theory type: {result['theory_metadata']['theory_type']}")
                logger.info(f"   Entities: {result['theory_metadata']['entities_created']}")
                logger.info(f"   Relationships: {result['theory_metadata']['relationships_created']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Theory-enhanced workflow failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_results": {}
            }
    
    def execute_tool(self, tool_id: str, request: 'ToolRequest') -> 'ToolResult':
        """Execute a specific tool by ID"""
        # Tool registry mapping
        tool_map = {
            "T01_PDF_LOADER": self._get_pdf_loader_tool,
            "T302_THEORY_EXTRACTION": self._get_theory_extraction_tool,
            "T15A_TEXT_CHUNKER": self._get_text_chunker_tool,
            "T31_ENTITY_BUILDER": self._get_entity_builder_tool,
            "T34_EDGE_BUILDER": self._get_edge_builder_tool,
            "T68_PAGERANK": self._get_pagerank_tool,
            "T49_MULTIHOP_QUERY": self._get_multihop_query_tool
        }
        
        if tool_id not in tool_map:
            from ...core.tool_contract import ToolResult
            from ...core.confidence_scoring.data_models import ConfidenceScore
            return ToolResult(
                status="error",
                data=None,
                confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                metadata={"tool_id": tool_id},
                provenance=None,
                request_id=request.request_id,
                execution_time=0.0,
                error_details=f"Unknown tool ID: {tool_id}"
            )
        
        tool = tool_map[tool_id]()
        return tool.execute(request)
    
    def _get_theory_extraction_tool(self):
        """Get T302 theory extraction tool instance"""
        from ...tools.phase3.t302_theory_extraction_kgas import T302TheoryExtractionKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T302TheoryExtractionKGAS(service_manager)
    
    def _get_pdf_loader_tool(self):
        """Get T01 PDF loader tool instance"""
        from ...tools.phase1.t01_pdf_loader_kgas import T01PDFLoaderKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        
        # Wrapper to handle data key mapping (content -> text)
        class PDFLoaderWrapper:
            def __init__(self, loader):
                self.loader = loader
            
            def execute(self, request):
                result = self.loader.execute(request)
                
                # Map "content" to "text" for pipeline compatibility
                if result.status == "success" and "content" in result.data:
                    result.data["text"] = result.data["content"]
                
                return result
        
        return PDFLoaderWrapper(T01PDFLoaderKGAS(service_manager))
    
    def _get_text_chunker_tool(self):
        """Get T15A text chunker tool instance"""
        from ...tools.phase1.t15a_text_chunker_kgas import T15ATextChunkerKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T15ATextChunkerKGAS(service_manager)
    
    def _get_entity_builder_tool(self):
        """Get T31 entity builder tool instance"""
        from ...tools.phase1.t31_entity_builder_kgas import T31EntityBuilderKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T31EntityBuilderKGAS(service_manager)
    
    def _get_edge_builder_tool(self):
        """Get T34 edge builder tool instance"""
        from ...tools.phase1.t34_edge_builder_kgas import T34EdgeBuilderKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T34EdgeBuilderKGAS(service_manager)
    
    def _get_pagerank_tool(self):
        """Get T68 PageRank tool instance"""
        from ...tools.phase1.t68_pagerank_kgas import T68PageRankKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T68PageRankKGAS(service_manager)
    
    def _get_multihop_query_tool(self):
        """Get T49 multihop query tool instance"""
        from ...tools.phase1.t49_multihop_query_kgas import T49MultiHopQueryKGAS
        from ...core.service_manager import ServiceManager
        service_manager = getattr(self.config, 'service_manager', None) or ServiceManager()
        return T49MultiHopQueryKGAS(service_manager)

    def health_check(self) -> Dict[str, bool]:
        """Check health of all orchestrator components"""
        return {
            "sequential_engine": self.sequential_engine.health_check(),
            "parallel_engine": self.parallel_engine.health_check(),
            "anyio_engine": self.anyio_engine.health_check(),
            "progress_monitor": self.progress_monitor.health_check(),
            "error_monitor": self.error_monitor.health_check(),
            "performance_monitor": self.performance_monitor.health_check()
        }