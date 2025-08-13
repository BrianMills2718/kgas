"""
T27: Relationship Extractor - Main Interface

DEPRECATED: Use T23C (Ontology-Aware Extractor) instead.
T23C extracts entities, relationships, and properties in a single LLM call
with superior context understanding and accuracy.

This tool is kept for backwards compatibility only and will be removed in a future version.
"""

import warnings
from .t27_relationship_extractor_unified import T27RelationshipExtractorUnified

# Issue deprecation warning when module is imported
warnings.warn(
    "T27 Relationship Extractor is deprecated. Use T23C (Ontology-Aware Extractor) instead. "
    "T23C extracts relationships along with entities and properties in one LLM call with better accuracy.",
    DeprecationWarning,
    stacklevel=2
)


class RelationshipExtractor(T27RelationshipExtractorUnified):
    """T27: Relationship Extractor - Main interface class"""
    
    def __init__(self, services=None):
        """Initialize Relationship Extractor with backward compatibility"""
        if services is None:
            from src.core.service_manager import ServiceManager
            services = ServiceManager()
        super().__init__(services)