#!/usr/bin/env python3
"""
MCP-Compliant Tool Generator

Generates realistic MCP tools following the official MCP specification:
https://modelcontextprotocol.io/docs/concepts/tools
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

class ToolDomain(Enum):
    DOCUMENT_LOADING = "document_loading"
    TEXT_PROCESSING = "text_processing" 
    ENTITY_EXTRACTION = "entity_extraction"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    GRAPH_OPERATIONS = "graph_operations"
    QUERY_SYSTEMS = "query_systems"
    ANALYTICS = "analytics"
    EXPORT_VISUALIZATION = "export_visualization"

@dataclass
class MCPToolSpec:
    """MCP-compliant tool specification"""
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    annotations: Dict[str, Any]
    domain: ToolDomain

class MCPCompliantToolGenerator:
    """Generate realistic MCP tools following official specification"""
    
    def __init__(self):
        self.entity_types = [
            "PERSON", "ORG", "LOC", "DATE", "TIME", "MONEY", "PERCENT", 
            "METHOD", "ALGORITHM", "DATASET", "METRIC", "RESULT", "CITATION",
            "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"
        ]
        
        self.relationship_types = [
            "PART_OF", "LOCATED_IN", "WORKS_FOR", "CREATED_BY", "USES", 
            "ACHIEVES", "OUTPERFORMS", "TRAINED_ON", "EVALUATED_ON",
            "CAUSES", "ENABLES", "REQUIRES", "SIMILAR_TO"
        ]
    
    def generate_all_tools(self) -> List[MCPToolSpec]:
        """Generate complete set of MCP-compliant tools"""
        
        tools = []
        
        # Document Loading Tools
        tools.extend(self._generate_document_loading_tools())
        
        # Text Processing Tools  
        tools.extend(self._generate_text_processing_tools())
        
        # Entity Extraction Tools
        tools.extend(self._generate_entity_extraction_tools())
        
        # Relationship Analysis Tools
        tools.extend(self._generate_relationship_analysis_tools())
        
        # Graph Operations Tools
        tools.extend(self._generate_graph_operations_tools())
        
        # Query Systems Tools
        tools.extend(self._generate_query_systems_tools())
        
        # Analytics Tools
        tools.extend(self._generate_analytics_tools())
        
        # Export & Visualization Tools
        tools.extend(self._generate_export_visualization_tools())
        
        return tools
    
    def _generate_document_loading_tools(self) -> List[MCPToolSpec]:
        """Generate document loading tools"""
        
        tools = [
            MCPToolSpec(
                name="load_document_pdf",
                title="PDF Document Loader",
                description="Load and extract text content from PDF documents with optional metadata and structure preservation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the PDF document to process"
                        },
                        "extract_metadata": {
                            "type": "boolean",
                            "description": "Whether to extract document metadata (author, title, creation date)",
                            "default": True
                        },
                        "preserve_structure": {
                            "type": "boolean", 
                            "description": "Maintain document structure including headings, paragraphs, and tables",
                            "default": False
                        },
                        "page_range": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "integer", "minimum": 1},
                                "end": {"type": "integer", "minimum": 1}
                            },
                            "description": "Optional page range to extract (if not specified, extracts all pages)"
                        }
                    },
                    "required": ["file_path"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.DOCUMENT_LOADING
            ),
            
            MCPToolSpec(
                name="load_document_docx",
                title="Word Document Loader",
                description="Load and parse Microsoft Word documents (.docx) with formatting and metadata extraction",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Word document (.docx) to process"
                        },
                        "include_comments": {
                            "type": "boolean",
                            "description": "Whether to include document comments and tracked changes",
                            "default": False
                        },
                        "extract_tables": {
                            "type": "boolean",
                            "description": "Extract tables as structured data",
                            "default": True
                        }
                    },
                    "required": ["file_path"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.DOCUMENT_LOADING
            ),
            
            MCPToolSpec(
                name="load_document_html",
                title="HTML Document Loader",
                description="Extract clean text content from HTML documents with optional element filtering",
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to HTML file or URL to process"
                        },
                        "remove_scripts": {
                            "type": "boolean",
                            "description": "Remove JavaScript and CSS content",
                            "default": True
                        },
                        "extract_links": {
                            "type": "boolean",
                            "description": "Extract and preserve hyperlinks",
                            "default": False
                        },
                        "target_elements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific HTML elements to extract (e.g., ['p', 'h1', 'h2'])"
                        }
                    },
                    "required": ["file_path"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.DOCUMENT_LOADING
            )
        ]
        
        # Add more document loading tools
        additional_loaders = [
            ("load_document_csv", "CSV Document Loader", "Parse and load CSV files with configurable delimiters and data type inference"),
            ("load_document_json", "JSON Document Loader", "Load and validate JSON documents with schema validation"),
            ("load_document_xml", "XML Document Loader", "Parse XML documents with namespace and schema support"),
            ("load_document_txt", "Text Document Loader", "Load plain text files with encoding detection and normalization"),
            ("load_document_xlsx", "Excel Document Loader", "Load Excel spreadsheets with multiple sheet support"),
            ("load_document_pptx", "PowerPoint Loader", "Extract text and metadata from PowerPoint presentations"),
            ("load_document_epub", "EPUB Document Loader", "Load eBook content from EPUB files with chapter structure"),
            ("load_document_rtf", "RTF Document Loader", "Parse Rich Text Format documents with formatting preservation"),
            ("load_document_odt", "OpenDocument Loader", "Load OpenDocument text files with style preservation"),
            ("load_document_markdown", "Markdown Document Loader", "Parse Markdown documents with metadata extraction"),
            ("load_web_content", "Web Content Loader", "Fetch and extract content from web URLs with cleaning"),
            ("load_email_content", "Email Content Loader", "Extract text and metadata from email messages")
        ]
        
        for name, title, description in additional_loaders:
            tools.append(MCPToolSpec(
                name=name,
                title=title, 
                description=description,
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to the document to process"},
                        "extract_metadata": {"type": "boolean", "description": "Extract document metadata", "default": True}
                    },
                    "required": ["file_path"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.DOCUMENT_LOADING
            ))
        
        return tools
    
    def _generate_text_processing_tools(self) -> List[MCPToolSpec]:
        """Generate text processing tools"""
        
        return [
            MCPToolSpec(
                name="chunk_text_semantic",
                title="Semantic Text Chunker",
                description="Split text into semantically coherent chunks that respect sentence and paragraph boundaries for optimal processing",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text content to split into chunks"
                        },
                        "chunk_size": {
                            "type": "integer",
                            "minimum": 100,
                            "maximum": 10000,
                            "description": "Target size for each chunk in characters",
                            "default": 1000
                        },
                        "overlap": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 500,
                            "description": "Character overlap between consecutive chunks to maintain context",
                            "default": 100
                        },
                        "respect_boundaries": {
                            "type": "boolean",
                            "description": "Whether to avoid splitting across sentence boundaries",
                            "default": True
                        },
                        "min_chunk_size": {
                            "type": "integer",
                            "minimum": 50,
                            "description": "Minimum allowed chunk size",
                            "default": 200
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.TEXT_PROCESSING
            ),
            
            MCPToolSpec(
                name="clean_text_advanced",
                title="Advanced Text Cleaner",
                description="Comprehensive text cleaning with normalization, noise removal, and formatting standardization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text content to clean and normalize"
                        },
                        "remove_html": {
                            "type": "boolean",
                            "description": "Remove HTML tags and entities",
                            "default": True
                        },
                        "normalize_whitespace": {
                            "type": "boolean",
                            "description": "Normalize spacing and line breaks",
                            "default": True
                        },
                        "remove_special_chars": {
                            "type": "boolean",
                            "description": "Remove non-alphanumeric characters except basic punctuation",
                            "default": False
                        },
                        "fix_encoding": {
                            "type": "boolean",
                            "description": "Attempt to fix common encoding issues",
                            "default": True
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "es", "fr", "de", "auto"],
                            "description": "Language for language-specific cleaning rules",
                            "default": "auto"
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.TEXT_PROCESSING
            ),
            
            MCPToolSpec(
                name="extract_keywords_tfidf",
                title="TF-IDF Keyword Extractor",
                description="Extract important keywords and phrases using TF-IDF scoring with configurable parameters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text content to analyze for keywords"
                        },
                        "max_keywords": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "description": "Maximum number of keywords to extract",
                            "default": 20
                        },
                        "min_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Minimum TF-IDF score threshold",
                            "default": 0.1
                        },
                        "ngram_range": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "integer", "minimum": 1, "maximum": 3},
                                "max": {"type": "integer", "minimum": 1, "maximum": 5}
                            },
                            "description": "N-gram range for phrase extraction",
                            "default": {"min": 1, "max": 2}
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.TEXT_PROCESSING
            )
        ]
    
    def _generate_entity_extraction_tools(self) -> List[MCPToolSpec]:
        """Generate entity extraction tools"""
        
        return [
            MCPToolSpec(
                name="extract_entities_llm_gemini",
                title="Gemini Entity Extractor",
                description="Extract named entities using Gemini's advanced language understanding with customizable entity types and confidence filtering",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text content to analyze for named entities"
                        },
                        "entity_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": self.entity_types
                            },
                            "description": "Specific entity types to extract",
                            "default": ["PERSON", "ORG", "LOC", "DATE"]
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Minimum confidence score for entity extraction",
                            "default": 0.7
                        },
                        "context_window": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 500,
                            "description": "Number of characters around entity to include as context",
                            "default": 50
                        },
                        "max_entities": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "description": "Maximum number of entities to extract",
                            "default": 100
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.ENTITY_EXTRACTION
            ),
            
            MCPToolSpec(
                name="extract_entities_scientific",
                title="Scientific Entity Extractor",
                description="Specialized entity extraction for scientific and academic texts, focusing on methods, datasets, and research artifacts",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Scientific text content to analyze"
                        },
                        "entity_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["METHOD", "ALGORITHM", "DATASET", "METRIC", "RESULT", "CITATION", "AUTHOR"]
                            },
                            "description": "Scientific entity types to extract",
                            "default": ["METHOD", "DATASET", "METRIC"]
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Minimum confidence for scientific entity extraction",
                            "default": 0.8
                        },
                        "include_abbreviations": {
                            "type": "boolean",
                            "description": "Whether to extract and expand abbreviations",
                            "default": True
                        },
                        "domain_vocabulary": {
                            "type": "string",
                            "enum": ["general", "computer_science", "biology", "chemistry", "physics"],
                            "description": "Domain-specific vocabulary to use",
                            "default": "general"
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.ENTITY_EXTRACTION
            ),
            
            MCPToolSpec(
                name="extract_entities_spacy_large", 
                title="SpaCy Large Model Extractor",
                description="High-accuracy entity extraction using SpaCy's large language model with custom entity recognition",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to process for entity extraction"
                        },
                        "model": {
                            "type": "string",
                            "enum": ["en_core_web_lg", "en_core_web_trf"],
                            "description": "SpaCy model to use for extraction",
                            "default": "en_core_web_lg"
                        },
                        "entity_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Entity types to extract (uses SpaCy's standard types)",
                            "default": ["PERSON", "ORG", "GPE", "DATE", "MONEY"]
                        },
                        "merge_entities": {
                            "type": "boolean",
                            "description": "Merge adjacent entities of the same type",
                            "default": False
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.ENTITY_EXTRACTION
            )
        ]
    
    def _generate_relationship_analysis_tools(self) -> List[MCPToolSpec]:
        """Generate relationship analysis tools"""
        
        return [
            MCPToolSpec(
                name="extract_relationships_llm",
                title="LLM Relationship Extractor",
                description="Extract semantic relationships between entities using large language models with configurable relationship types",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text content containing entities and relationships"
                        },
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "type": {"type": "string"},
                                    "start": {"type": "integer"},
                                    "end": {"type": "integer"}
                                },
                                "required": ["text", "type"]
                            },
                            "description": "Previously extracted entities to find relationships between"
                        },
                        "relationship_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": self.relationship_types
                            },
                            "description": "Types of relationships to extract",
                            "default": ["PART_OF", "LOCATED_IN", "WORKS_FOR", "USES"]
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Minimum confidence for relationship extraction",
                            "default": 0.6
                        },
                        "max_distance": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "description": "Maximum character distance between related entities",
                            "default": 200
                        }
                    },
                    "required": ["text", "entities"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.RELATIONSHIP_ANALYSIS
            ),
            
            MCPToolSpec(
                name="extract_relationships_dependency",
                title="Dependency-Based Relationship Extractor",
                description="Extract relationships using syntactic dependency parsing for high-precision grammatical relationships",
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to analyze for syntactic relationships"
                        },
                        "dependency_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["nsubj", "dobj", "prep", "amod", "compound", "appos"]
                            },
                            "description": "Dependency relation types to extract",
                            "default": ["nsubj", "dobj", "prep"]
                        },
                        "include_modifiers": {
                            "type": "boolean",
                            "description": "Include adjectival and adverbial modifiers",
                            "default": True
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.RELATIONSHIP_ANALYSIS
            )
        ]
    
    def _generate_graph_operations_tools(self) -> List[MCPToolSpec]:
        """Generate graph operations tools"""
        
        return [
            MCPToolSpec(
                name="build_knowledge_graph",
                title="Knowledge Graph Builder",
                description="Construct a comprehensive knowledge graph from extracted entities and relationships with validation and optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "text": {"type": "string"},
                                    "type": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "metadata": {"type": "object"}
                                },
                                "required": ["text", "type"]
                            },
                            "description": "Entities to include in the knowledge graph"
                        },
                        "relationships": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source": {"type": "string"},
                                    "target": {"type": "string"},
                                    "relation": {"type": "string"},
                                    "confidence": {"type": "number"},
                                    "metadata": {"type": "object"}
                                },
                                "required": ["source", "target", "relation"]
                            },
                            "description": "Relationships between entities"
                        },
                        "merge_similar": {
                            "type": "boolean",
                            "description": "Merge semantically similar entities",
                            "default": True
                        },
                        "similarity_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Similarity threshold for entity merging",
                            "default": 0.9
                        },
                        "validate_relationships": {
                            "type": "boolean",
                            "description": "Validate relationship consistency and remove invalid edges",
                            "default": True
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "description": "Include entity and relationship metadata in graph",
                            "default": True
                        }
                    },
                    "required": ["entities"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": False},
                domain=ToolDomain.GRAPH_OPERATIONS
            ),
            
            MCPToolSpec(
                name="merge_knowledge_graphs",
                title="Knowledge Graph Merger",
                description="Merge multiple knowledge graphs with entity alignment and relationship consolidation",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graphs": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "nodes": {"type": "array"},
                                    "edges": {"type": "array"},
                                    "metadata": {"type": "object"}
                                }
                            },
                            "description": "Knowledge graphs to merge",
                            "minItems": 2
                        },
                        "alignment_strategy": {
                            "type": "string",
                            "enum": ["exact_match", "similarity_based", "hybrid"],
                            "description": "Strategy for aligning entities across graphs",
                            "default": "hybrid"
                        },
                        "conflict_resolution": {
                            "type": "string", 
                            "enum": ["keep_first", "keep_highest_confidence", "merge_all"],
                            "description": "How to resolve conflicting information",
                            "default": "keep_highest_confidence"
                        }
                    },
                    "required": ["graphs"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": False},
                domain=ToolDomain.GRAPH_OPERATIONS
            )
        ]
    
    def _generate_query_systems_tools(self) -> List[MCPToolSpec]:
        """Generate query systems tools"""
        
        return [
            MCPToolSpec(
                name="query_graph_multihop",
                title="Multi-hop Graph Query Engine",
                description="Execute complex multi-hop traversal queries across knowledge graphs with path optimization",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph": {
                            "type": "object",
                            "description": "Knowledge graph to query"
                        },
                        "start_entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Starting entities for traversal"
                        },
                        "target_entities": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Target entities to reach (optional)"
                        },
                        "max_hops": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Maximum number of hops in traversal",
                            "default": 3
                        },
                        "relationship_filter": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Only traverse these relationship types"
                        },
                        "return_paths": {
                            "type": "boolean",
                            "description": "Return full paths in addition to results",
                            "default": False
                        }
                    },
                    "required": ["graph", "start_entities"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.QUERY_SYSTEMS
            )
        ]
    
    def _generate_analytics_tools(self) -> List[MCPToolSpec]:
        """Generate analytics tools"""
        
        return [
            MCPToolSpec(
                name="calculate_graph_metrics",
                title="Graph Metrics Calculator",
                description="Calculate comprehensive graph analytics including centrality measures, clustering coefficients, and network statistics",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph": {
                            "type": "object",
                            "description": "Knowledge graph to analyze"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["pagerank", "betweenness", "closeness", "degree", "clustering", "modularity"]
                            },
                            "description": "Metrics to calculate",
                            "default": ["pagerank", "degree", "clustering"]
                        },
                        "normalize": {
                            "type": "boolean",
                            "description": "Normalize metric values to 0-1 range",
                            "default": True
                        },
                        "top_k": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 1000,
                            "description": "Return top K entities for each metric",
                            "default": 10
                        }
                    },
                    "required": ["graph"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True},
                domain=ToolDomain.ANALYTICS
            )
        ]
    
    def _generate_export_visualization_tools(self) -> List[MCPToolSpec]:
        """Generate export and visualization tools"""
        
        return [
            MCPToolSpec(
                name="export_graph_json",
                title="JSON Graph Exporter",
                description="Export knowledge graphs and analysis results as structured JSON with flexible formatting options",
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "Graph data or analysis results to export"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["cytoscape", "d3", "networkx", "custom"],
                            "description": "JSON format for specific visualization libraries",
                            "default": "custom"
                        },
                        "include_metadata": {
                            "type": "boolean",
                            "description": "Include entity and relationship metadata",
                            "default": True
                        },
                        "pretty_print": {
                            "type": "boolean",
                            "description": "Format JSON with indentation for readability",
                            "default": True
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Optional file path to save JSON output"
                        }
                    },
                    "required": ["data"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": False},
                domain=ToolDomain.EXPORT_VISUALIZATION
            ),
            
            MCPToolSpec(
                name="create_interactive_visualization",
                title="Interactive Graph Visualizer",
                description="Create interactive web-based visualizations of knowledge graphs with customizable layouts and styling",
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph": {
                            "type": "object",
                            "description": "Knowledge graph to visualize"
                        },
                        "layout": {
                            "type": "string",
                            "enum": ["force_directed", "hierarchical", "circular", "grid"],
                            "description": "Visualization layout algorithm",
                            "default": "force_directed"
                        },
                        "node_size_metric": {
                            "type": "string",
                            "enum": ["degree", "pagerank", "betweenness", "fixed"],
                            "description": "Metric to determine node sizes",
                            "default": "degree"
                        },
                        "color_by_type": {
                            "type": "boolean",
                            "description": "Color nodes by entity type",
                            "default": True
                        },
                        "interactive_features": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["zoom", "pan", "hover_info", "click_details", "search"]
                            },
                            "description": "Interactive features to enable",
                            "default": ["zoom", "pan", "hover_info"]
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["html", "svg", "png"],
                            "description": "Output format for visualization",
                            "default": "html"
                        }
                    },
                    "required": ["graph"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": False},
                domain=ToolDomain.EXPORT_VISUALIZATION
            )
        ]
    
    def format_for_mcp_client(self, tools: List[MCPToolSpec]) -> List[Dict[str, Any]]:
        """Format tools for MCP client consumption"""
        
        formatted_tools = []
        for tool in tools:
            formatted_tools.append({
                "name": tool.name,
                "title": tool.title,
                "description": tool.description,
                "inputSchema": tool.input_schema,
                "annotations": tool.annotations
            })
        
        return formatted_tools

def main():
    """Generate and display MCP-compliant tools"""
    
    generator = MCPCompliantToolGenerator()
    tools = generator.generate_all_tools()
    formatted_tools = generator.format_for_mcp_client(tools)
    
    print(f"Generated {len(tools)} MCP-compliant tools")
    print("\nSample tool (extract_entities_llm_gemini):")
    
    # Find and display the Gemini entity extraction tool
    gemini_tool = next((t for t in formatted_tools if t["name"] == "extract_entities_llm_gemini"), None)
    if gemini_tool:
        print(json.dumps(gemini_tool, indent=2))
    
    # Show domain distribution
    domain_counts = {}
    for tool in tools:
        domain = tool.domain.value
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print(f"\nTools by domain:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")

if __name__ == "__main__":
    main()