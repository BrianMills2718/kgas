"""
T23A: SpaCy NER - Main Interface

This module provides the main interface for the SpaCy NER tool.
"""

from .t23a_spacy_ner_unified import T23ASpacyNERUnified


class SpacyNER(T23ASpacyNERUnified):
    """T23A: SpaCy NER - Main interface class"""
    
    def __init__(self, services=None):
        """Initialize SpaCy NER with backward compatibility"""
        if services is None:
            from src.core.service_manager import ServiceManager
            services = ServiceManager()
        super().__init__(services)