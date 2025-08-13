"""
DEPRECATED: T23a SpaCy NER - Archived Pattern-Based Entity Extraction

This tool has been archived in favor of T23c (Ontology-Aware Extractor) which 
extracts entities + relationships + properties in a single LLM call.

For pattern-based extraction needs, the original implementation is preserved at:
src/tools/phase1/archived_extraction/t23a_spacy_ner.py

To use the recommended approach:
    from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
    
    extractor = OntologyAwareExtractor()
    result = extractor.extract_entities(text, ontology)
    # result contains entities AND relationships
"""

import warnings
from typing import TYPE_CHECKING

warnings.warn(
    "T23a SpaCy NER is deprecated. Use T23c OntologyAwareExtractor for complete "
    "entity + relationship extraction in one LLM call. "
    "Original code archived at: src/tools/phase1/archived_extraction/",
    DeprecationWarning,
    stacklevel=2
)

# For backwards compatibility, import from archived location
try:
    from .archived_extraction.t23a_spacy_ner import *
except ImportError:
    # Provide a stub class if archive is removed
    class SpacyNER:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "T23a SpaCy NER has been archived. Use T23c OntologyAwareExtractor instead. "
                "See src/tools/phase1/archived_extraction/ARCHIVED_README.md for details."
            )

# Type checking support
if TYPE_CHECKING:
    from .archived_extraction.t23a_spacy_ner import SpacyNER