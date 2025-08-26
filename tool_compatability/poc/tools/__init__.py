"""
Tools package for the Type-Based Tool Composition POC
"""

# Comment out old tools that have import issues
# from .text_loader import TextLoader
# from .entity_extractor import EntityExtractor
# from .graph_builder import GraphBuilder

# Export native tools
try:
    from .streaming_file_loader import StreamingFileLoader
    __all__ = ['StreamingFileLoader']
except ImportError:
    __all__ = []