#!/usr/bin/env python3
"""
Simple access to sophisticated analytics infrastructure

This module provides a clean, simple interface to the sophisticated analytics
capabilities that have been discovered and unlocked in the KGAS system.
"""

from typing import Dict, Any, Optional
import logging

# Import sophisticated analytics components
from src.analytics.cross_modal_orchestrator import CrossModalOrchestrator
from src.analytics.cross_modal_converter import CrossModalConverter
from src.analytics.mode_selection_service import ModeSelectionService
from src.analytics.cross_modal_validator import CrossModalValidator

# Import cross-modal tools (now registered and accessible)
try:
    from src.tools.cross_modal.graph_table_exporter import GraphTableExporter
    from src.tools.cross_modal.multi_format_exporter import MultiFormatExporter
    from src.tools.phase_c.cross_modal_tool import CrossModalTool
    from src.tools.phase1.t41_async_text_embedder import AsyncTextEmbedder
except ImportError as e:
    logging.warning(f"Some cross-modal tools not available: {e}")

logger = logging.getLogger(__name__)


def get_analytics(service_manager=None) -> Dict[str, Any]:
    """
    Get analytics capabilities with optional ServiceManager integration
    
    Returns a dictionary of initialized analytics components:
    - orchestrator: Orchestrates cross-modal analysis workflows
    - converter: Converts between graph/table/vector formats
    - mode_selector: Intelligently selects optimal analysis mode
    - validator: Validates cross-modal conversions
    
    Args:
        service_manager: Optional ServiceManager instance for integration
        
    Returns:
        Dict containing initialized analytics components
    """
    components = {}
    
    try:
        # Initialize core analytics infrastructure
        components['orchestrator'] = CrossModalOrchestrator(service_manager)
        components['converter'] = CrossModalConverter(service_manager)
        components['mode_selector'] = ModeSelectionService(service_manager)
        
        # Initialize validator with converter dependency
        components['validator'] = CrossModalValidator(
            components['converter'], 
            service_manager
        )
        
        # Add cross-modal tools if available
        try:
            components['graph_table_exporter'] = GraphTableExporter()
            logger.info("GraphTableExporter loaded successfully")
        except Exception as e:
            logger.warning(f"GraphTableExporter not available: {e}")
            
        try:
            components['multi_format_exporter'] = MultiFormatExporter()
            logger.info("MultiFormatExporter loaded successfully")
        except Exception as e:
            logger.warning(f"MultiFormatExporter not available: {e}")
            
        try:
            components['cross_modal_tool'] = CrossModalTool(service_manager)
            logger.info("CrossModalTool loaded successfully")
        except Exception as e:
            logger.warning(f"CrossModalTool not available: {e}")
            
        try:
            components['async_embedder'] = AsyncTextEmbedder()
            logger.info("AsyncTextEmbedder loaded successfully")
        except Exception as e:
            logger.warning(f"AsyncTextEmbedder not available: {e}")
            
        logger.info(f"Analytics infrastructure initialized with {len(components)} components")
        
    except Exception as e:
        logger.error(f"Failed to initialize analytics infrastructure: {e}")
        raise
        
    return components


def get_orchestrator(service_manager=None) -> CrossModalOrchestrator:
    """
    Get configured CrossModalOrchestrator instance
    
    Args:
        service_manager: Optional ServiceManager for integration
        
    Returns:
        Initialized CrossModalOrchestrator
    """
    return CrossModalOrchestrator(service_manager)


def get_converter(service_manager=None) -> CrossModalConverter:
    """
    Get configured CrossModalConverter instance
    
    Args:
        service_manager: Optional ServiceManager for integration
        
    Returns:
        Initialized CrossModalConverter
    """
    return CrossModalConverter(service_manager)


def list_available_analytics() -> Dict[str, str]:
    """
    List all available analytics capabilities
    
    Returns:
        Dict mapping component names to descriptions
    """
    capabilities = {
        # Core Analytics Infrastructure
        'CrossModalOrchestrator': 'Intelligent orchestration of cross-modal analysis workflows',
        'CrossModalConverter': 'Convert between graph, table, and vector formats',
        'ModeSelectionService': 'Intelligently select optimal analysis mode',
        'CrossModalValidator': 'Validate cross-modal conversions and ensure quality',
        
        # Cross-Modal Tools (if registered)
        'GraphTableExporter': 'Export graph data to table format for statistical analysis',
        'MultiFormatExporter': 'Export to multiple formats (CSV, JSON, Parquet, etc.)',
        'CrossModalTool': 'Comprehensive cross-modal analysis capabilities',
        'AsyncTextEmbedder': 'High-performance async text embedding (15-20% faster)',
        'CrossModalConverter': 'Full conversion matrix between all formats',
        
        # Analytics Categories
        'Graph Analytics': 'Community detection, centrality, path analysis',
        'Table Analytics': 'Statistics, regression, correlation analysis',
        'Vector Analytics': 'Similarity, clustering, semantic search',
    }
    
    return capabilities


def quick_analysis(data: Any, question: str, service_manager=None) -> Dict[str, Any]:
    """
    Quick cross-modal analysis with automatic mode selection
    
    Args:
        data: Input data (graph, table, or vector)
        question: Research question to answer
        service_manager: Optional ServiceManager for integration
        
    Returns:
        Analysis results with provenance
    """
    try:
        orchestrator = get_orchestrator(service_manager)
        
        # Let the orchestrator handle the full workflow
        # It will automatically:
        # 1. Detect input format
        # 2. Select optimal analysis mode
        # 3. Convert as needed
        # 4. Run analysis
        # 5. Validate results
        
        from src.analytics.cross_modal_orchestrator import AnalysisRequest, DataFormat
        import uuid
        
        # Create analysis request
        request = AnalysisRequest(
            request_id=str(uuid.uuid4()),
            research_question=question,
            data=data,
            source_format=DataFormat.UNKNOWN,  # Let it auto-detect
        )
        
        # Run orchestrated analysis
        result = orchestrator.analyze(request)
        
        return {
            'success': result.success,
            'result': result.primary_result,
            'metadata': result.analysis_metadata,
            'performance': result.performance_metrics,
            'recommendations': result.recommendations
        }
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'result': None
        }


# Module initialization message
logger.info("Analytics access module loaded - sophisticated capabilities now accessible")