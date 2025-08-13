"""
DEPRECATED: T27 Relationship Extractor - Archived Pattern-Based Extraction

This tool has been archived in favor of T23c (Ontology-Aware Extractor) which 
extracts entities + relationships + properties in a single LLM call.

The pattern-based approach of T27 only finds explicit relationships like 
"X works for Y" and misses implicit relationships that LLMs can understand.

For pattern-based extraction needs, the original implementation is preserved at:
src/tools/phase1/archived_extraction/t27_relationship_extractor.py

To use the recommended approach:
    from src.tools.phase2.t23c_ontology_aware_extractor import OntologyAwareExtractor
    
    extractor = OntologyAwareExtractor()
    result = extractor.extract_entities(text, ontology)
    # result.relationships contains ALL relationships (explicit and implicit)
"""

import warnings
from typing import TYPE_CHECKING

warnings.warn(
    "T27 Relationship Extractor is deprecated. Use T23c OntologyAwareExtractor for "
    "complete entity + relationship extraction with LLM understanding. "
    "Pattern-based extraction misses implicit relationships. "
    "Original code archived at: src/tools/phase1/archived_extraction/",
    DeprecationWarning,
    stacklevel=2
)

# For backwards compatibility, import from archived location
try:
    from .archived_extraction.t27_relationship_extractor import *
    from .archived_extraction.t27_relationship_extractor_unified import T27RelationshipExtractorUnified
except ImportError:
    # Provide stub classes if archive is removed
    class RelationshipExtractor:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(
                "T27 Relationship Extractor has been archived. Use T23c OntologyAwareExtractor instead. "
                "See src/tools/phase1/archived_extraction/ARCHIVED_README.md for details."
            )
    
    T27RelationshipExtractorUnified = RelationshipExtractor

# Type checking support
if TYPE_CHECKING:
    from .archived_extraction.t27_relationship_extractor import RelationshipExtractor
    from .archived_extraction.t27_relationship_extractor_unified import T27RelationshipExtractorUnified