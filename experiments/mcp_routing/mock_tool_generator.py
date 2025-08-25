#!/usr/bin/env python3
"""
Mock Tool Generator for MCP Routing Experiments

Generates 100+ mock MCP tools across different categories to test
tool organization and routing strategies.
"""

import json
import random
from typing import Dict, List, Any, Literal, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import time


class ToolCategory(Enum):
    DOCUMENT_LOADERS = "document_loaders"
    TEXT_PROCESSING = "text_processing" 
    ENTITY_EXTRACTION = "entity_extraction"
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    GRAPH_OPERATIONS = "graph_operations"
    QUERY_SYSTEMS = "query_systems"
    ANALYTICS = "analytics"
    EXPORT_VISUALIZATION = "export_visualization"


@dataclass
class MockToolSpec:
    """Specification for a mock MCP tool"""
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    input_types: List[str]
    output_types: List[str]
    parameters: Dict[str, Any]
    complexity_score: float  # 0.1-1.0, affects execution time
    dependencies: List[str]  # Other tools this typically follows
    parallel_compatible: List[str]  # Tools this can run in parallel with
    
    def to_mcp_tool_description(self) -> Dict[str, Any]:
        """Convert to MCP tool description format"""
        return {
            "name": self.tool_id,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self._generate_input_schema(),
                "required": self._get_required_inputs()
            }
        }
    
    def _generate_input_schema(self) -> Dict[str, Any]:
        """Generate JSON schema for tool inputs"""
        schema = {}
        
        # Add input_ref for reference-based tools
        if self.input_types:
            schema["input_ref"] = {
                "type": "string",
                "description": f"Reference to input data of type: {', '.join(self.input_types)}"
            }
        
        # Add tool-specific parameters
        for param_name, param_spec in self.parameters.items():
            schema[param_name] = param_spec
            
        return schema
    
    def _get_required_inputs(self) -> List[str]:
        """Get required input parameters"""
        required = []
        if self.input_types:
            required.append("input_ref")
        return required


class MockToolGenerator:
    """Generates comprehensive set of mock MCP tools"""
    
    def __init__(self):
        self.tools: List[MockToolSpec] = []
        self.tool_counter = 0
        
    def generate_all_tools(self) -> List[MockToolSpec]:
        """Generate all 100+ mock tools across categories"""
        
        # Document Loaders (12 tools)
        self.tools.extend(self._generate_document_loaders())
        
        # Text Processing (15 tools)  
        self.tools.extend(self._generate_text_processing_tools())
        
        # Entity Extraction (18 tools)
        self.tools.extend(self._generate_entity_extraction_tools())
        
        # Relationship Analysis (16 tools)
        self.tools.extend(self._generate_relationship_analysis_tools())
        
        # Graph Operations (14 tools)
        self.tools.extend(self._generate_graph_operation_tools())
        
        # Query Systems (10 tools)
        self.tools.extend(self._generate_query_system_tools())
        
        # Analytics (8 tools)
        self.tools.extend(self._generate_analytics_tools())
        
        # Export/Visualization (7 tools)
        self.tools.extend(self._generate_export_visualization_tools())
        
        return self.tools
    
    def generate_tools(self, count: int, seed: int = None) -> List[MockToolSpec]:
        """Generate specified number of tools with optional seed for reproducibility"""
        if seed is not None:
            import random
            random.seed(seed)
        
        # Generate all tools first if not already generated
        if not self.tools:
            self.generate_all_tools()
        
        all_tools = self.tools.copy()
        
        if count >= len(all_tools):
            # If requesting more tools than available, duplicate with variations
            extended_tools = all_tools.copy()
            
            # Create variations by modifying complexity and names
            for i in range(count - len(all_tools)):
                base_tool = all_tools[i % len(all_tools)]
                variation = MockToolSpec(
                    tool_id=f"{base_tool.tool_id}_v{i//len(all_tools) + 2}",
                    name=f"{base_tool.name} V{i//len(all_tools) + 2}",
                    description=f"{base_tool.description} (Enhanced variant)",
                    category=base_tool.category,
                    input_types=base_tool.input_types,
                    output_types=base_tool.output_types,
                    parameters=base_tool.parameters,
                    complexity_score=min(1.0, base_tool.complexity_score + 0.1),
                    dependencies=base_tool.dependencies,
                    parallel_compatible=base_tool.parallel_compatible
                )
                extended_tools.append(variation)
            
            return extended_tools[:count]
        else:
            # Return subset of tools
            if seed is not None:
                import random
                return random.sample(all_tools, count)
            else:
                return all_tools[:count]
    
    def _generate_document_loaders(self) -> List[MockToolSpec]:
        """Generate document loader tools"""
        loaders = []
        
        formats = [
            ("pdf", "Extract text and metadata from PDF documents"),
            ("docx", "Load and parse Microsoft Word documents"),
            ("txt", "Load plain text files with encoding detection"),  
            ("csv", "Parse CSV files with configurable delimiters"),
            ("json", "Load and validate JSON documents"),
            ("xml", "Parse XML documents with schema validation"),
            ("html", "Extract content from HTML documents"),
            ("xlsx", "Load Excel spreadsheets with multiple sheets"),
            ("pptx", "Extract text from PowerPoint presentations"),
            ("epub", "Load eBook content from EPUB files"),
            ("rtf", "Parse Rich Text Format documents"),
            ("odt", "Load OpenDocument text files")
        ]
        
        for format_type, description in formats:
            tool = MockToolSpec(
                tool_id=f"load_document_{format_type}",
                name=f"Load {format_type.upper()} Document",
                description=description,
                category=ToolCategory.DOCUMENT_LOADERS,
                input_types=[],  # Takes file path, not reference
                output_types=["document_ref"],
                parameters={
                    "file_path": {"type": "string", "description": f"Path to {format_type} file"},
                    "encoding": {"type": "string", "default": "auto", "description": "Text encoding"},
                    "extract_metadata": {"type": "boolean", "default": True}
                },
                complexity_score=0.3,
                dependencies=[],
                parallel_compatible=[]
            )
            loaders.append(tool)
            
        return loaders
    
    def _generate_text_processing_tools(self) -> List[MockToolSpec]:
        """Generate text processing tools"""
        processors = []
        
        processing_types = [
            ("chunk_text_fixed", "Split text into fixed-size chunks", 0.2),
            ("chunk_text_semantic", "Split text using semantic boundaries", 0.4),
            ("chunk_text_sliding", "Create overlapping text chunks", 0.3),
            ("clean_text_basic", "Remove noise and normalize text", 0.2),
            ("clean_text_aggressive", "Intensive text cleaning and normalization", 0.4),
            ("tokenize_words", "Split text into word tokens", 0.1),
            ("tokenize_sentences", "Split text into sentence tokens", 0.2),
            ("extract_keywords", "Extract important keywords and phrases", 0.5),
            ("summarize_extractive", "Create extractive text summaries", 0.6),
            ("summarize_abstractive", "Generate abstractive summaries", 0.8),
            ("translate_text", "Translate text between languages", 0.7),
            ("detect_language", "Identify text language", 0.3),
            ("normalize_unicode", "Normalize Unicode text encoding", 0.2),
            ("remove_stopwords", "Filter out common stop words", 0.1),
            ("stem_words", "Apply word stemming algorithms", 0.2)
        ]
        
        for tool_type, description, complexity in processing_types:
            tool = MockToolSpec(
                tool_id=tool_type,
                name=tool_type.replace("_", " ").title(),
                description=description,
                category=ToolCategory.TEXT_PROCESSING,
                input_types=["document_ref", "text_ref"],
                output_types=["text_ref", "chunks_ref"],
                parameters={
                    "chunk_size": {"type": "integer", "default": 1000, "description": "Size of text chunks"},
                    "overlap": {"type": "integer", "default": 100, "description": "Overlap between chunks"},
                    "preserve_formatting": {"type": "boolean", "default": False}
                },
                complexity_score=complexity,
                dependencies=["load_document_*"],
                parallel_compatible=[]
            )
            processors.append(tool)
            
        return processors
    
    def _generate_entity_extraction_tools(self) -> List[MockToolSpec]:
        """Generate entity extraction tools"""
        extractors = []
        
        extraction_methods = [
            # SpaCy variants
            ("extract_entities_spacy_sm", "SpaCy small model entity extraction", 0.3),
            ("extract_entities_spacy_md", "SpaCy medium model entity extraction", 0.4),
            ("extract_entities_spacy_lg", "SpaCy large model entity extraction", 0.5),
            ("extract_entities_spacy_trf", "SpaCy transformer model extraction", 0.7),
            
            # LLM variants  
            ("extract_entities_llm_gpt4", "GPT-4 based entity extraction", 0.8),
            ("extract_entities_llm_claude", "Claude based entity extraction", 0.8),
            ("extract_entities_llm_gemini", "Gemini based entity extraction", 0.8),
            ("extract_entities_llm_local", "Local LLM entity extraction", 0.6),
            
            # Domain-specific
            ("extract_entities_biomedical", "Biomedical entity extraction", 0.6),
            ("extract_entities_financial", "Financial entity extraction", 0.6),
            ("extract_entities_legal", "Legal entity extraction", 0.6),
            ("extract_entities_scientific", "Scientific entity extraction", 0.6),
            ("extract_entities_news", "News/media entity extraction", 0.5),
            ("extract_entities_social", "Social media entity extraction", 0.5),
            
            # Hybrid approaches
            ("extract_entities_hybrid", "Combined rule+ML entity extraction", 0.7),
            ("extract_entities_ensemble", "Ensemble of multiple extractors", 0.9),
            ("extract_entities_active", "Active learning entity extraction", 0.8),
            ("extract_entities_few_shot", "Few-shot learning extraction", 0.6)
        ]
        
        for method, description, complexity in extraction_methods:
            tool = MockToolSpec(
                tool_id=method,
                name=method.replace("_", " ").title(),
                description=description,
                category=ToolCategory.ENTITY_EXTRACTION,
                input_types=["text_ref", "chunks_ref"],
                output_types=["entities_ref"],
                parameters={
                    "confidence_threshold": {"type": "number", "default": 0.8, "minimum": 0.0, "maximum": 1.0},
                    "entity_types": {"type": "array", "items": {"type": "string"}, "description": "Entity types to extract"},
                    "max_entities": {"type": "integer", "default": 100, "description": "Maximum entities to extract"}
                },
                complexity_score=complexity,
                dependencies=["chunk_text_*", "clean_text_*"],
                parallel_compatible=["extract_relationships_*"]
            )
            extractors.append(tool)
            
        return extractors
        
    def _generate_relationship_analysis_tools(self) -> List[MockToolSpec]:
        """Generate relationship analysis tools"""
        analyzers = []
        
        relationship_methods = [
            ("extract_relationships_pattern", "Pattern-based relationship extraction", 0.4),
            ("extract_relationships_dependency", "Dependency parsing relationships", 0.5),
            ("extract_relationships_coreference", "Coreference-based relationships", 0.6),
            ("extract_relationships_llm", "LLM-based relationship extraction", 0.8),
            ("extract_relationships_knowledge", "Knowledge graph relationships", 0.7),
            ("extract_relationships_temporal", "Temporal relationship analysis", 0.6),
            ("extract_relationships_causal", "Causal relationship detection", 0.7),
            ("extract_relationships_spatial", "Spatial relationship analysis", 0.5),
            ("analyze_relationship_strength", "Quantify relationship strength", 0.4),
            ("classify_relationship_types", "Classify relationship categories", 0.5),
            ("validate_relationships", "Validate extracted relationships", 0.6),
            ("merge_relationships", "Merge duplicate relationships", 0.4),
            ("filter_relationships", "Filter relationships by criteria", 0.3),
            ("rank_relationships", "Rank relationships by importance", 0.5),
            ("cluster_relationships", "Group similar relationships", 0.6),
            ("extract_relationship_chains", "Find relationship chains", 0.7)
        ]
        
        for method, description, complexity in relationship_methods:
            tool = MockToolSpec(
                tool_id=method,
                name=method.replace("_", " ").title(),
                description=description,
                category=ToolCategory.RELATIONSHIP_ANALYSIS,
                input_types=["entities_ref", "text_ref"],
                output_types=["relationships_ref"],
                parameters={
                    "relationship_types": {"type": "array", "items": {"type": "string"}},
                    "min_confidence": {"type": "number", "default": 0.7},
                    "max_distance": {"type": "integer", "default": 5, "description": "Max word distance"}
                },
                complexity_score=complexity,
                dependencies=["extract_entities_*"],
                parallel_compatible=["extract_entities_*"]
            )
            analyzers.append(tool)
            
        return analyzers
    
    def _generate_graph_operation_tools(self) -> List[MockToolSpec]:
        """Generate graph operation tools"""
        operations = []
        
        graph_ops = [
            ("build_graph_entities", "Build graph from entity data", 0.4),
            ("build_graph_relationships", "Build graph from relationship data", 0.5),
            ("merge_graphs", "Merge multiple graphs", 0.6),
            ("validate_graph_structure", "Validate graph consistency", 0.4),
            ("optimize_graph_layout", "Optimize graph for visualization", 0.5),
            ("calculate_graph_metrics", "Calculate graph statistics", 0.4),
            ("detect_graph_communities", "Find communities in graph", 0.7),
            ("find_graph_clusters", "Cluster graph nodes", 0.6),
            ("analyze_graph_centrality", "Calculate centrality measures", 0.5),
            ("find_shortest_paths", "Find shortest paths in graph", 0.4),
            ("detect_graph_anomalies", "Identify unusual graph patterns", 0.6),
            ("simplify_graph", "Reduce graph complexity", 0.4),
            ("enrich_graph_metadata", "Add metadata to graph elements", 0.3),
            ("export_graph_format", "Convert graph to different formats", 0.3)
        ]
        
        for op, description, complexity in graph_ops:
            tool = MockToolSpec(
                tool_id=op,
                name=op.replace("_", " ").title(),
                description=description,
                category=ToolCategory.GRAPH_OPERATIONS,
                input_types=["entities_ref", "relationships_ref", "graph_ref"],
                output_types=["graph_ref"],
                parameters={
                    "layout_algorithm": {"type": "string", "enum": ["force", "circular", "hierarchical"]},
                    "include_metadata": {"type": "boolean", "default": True},
                    "max_nodes": {"type": "integer", "default": 1000}
                },
                complexity_score=complexity,
                dependencies=["build_graph_*", "extract_*"],
                parallel_compatible=[]
            )
            operations.append(tool)
            
        return operations
    
    def _generate_query_system_tools(self) -> List[MockToolSpec]:
        """Generate query system tools"""
        queries = []
        
        query_types = [
            ("query_graph_multihop", "Multi-hop graph traversal queries", 0.6),
            ("query_graph_semantic", "Semantic similarity queries", 0.7),
            ("query_graph_temporal", "Time-based graph queries", 0.5),
            ("query_graph_pattern", "Pattern matching queries", 0.6),
            ("query_graph_aggregation", "Aggregation and statistics queries", 0.4),
            ("query_graph_subgraph", "Subgraph extraction queries", 0.5),
            ("query_graph_path", "Path finding queries", 0.4),
            ("query_graph_neighborhood", "Neighborhood exploration", 0.3),
            ("query_graph_similarity", "Find similar entities/patterns", 0.6),
            ("query_graph_ranking", "Ranking and top-k queries", 0.4)
        ]
        
        for query_type, description, complexity in query_types:
            tool = MockToolSpec(
                tool_id=query_type,
                name=query_type.replace("_", " ").title(),
                description=description,
                category=ToolCategory.QUERY_SYSTEMS,
                input_types=["graph_ref"],
                output_types=["query_results_ref"],
                parameters={
                    "query": {"type": "string", "description": "Natural language query"},
                    "max_results": {"type": "integer", "default": 10},
                    "include_paths": {"type": "boolean", "default": False}
                },
                complexity_score=complexity,
                dependencies=["build_graph_*"],
                parallel_compatible=[]
            )
            queries.append(tool)
            
        return queries
    
    def _generate_analytics_tools(self) -> List[MockToolSpec]:
        """Generate analytics tools"""
        analytics = []
        
        analytic_types = [
            ("calculate_pagerank", "Calculate PageRank importance scores", 0.5),
            ("detect_anomalies", "Identify anomalous patterns", 0.7),
            ("perform_clustering", "Cluster similar entities", 0.6),
            ("analyze_trends", "Analyze temporal trends", 0.6),
            ("calculate_similarity", "Calculate entity similarities", 0.4),
            ("predict_links", "Predict missing relationships", 0.8),
            ("analyze_influence", "Analyze influence propagation", 0.7),
            ("detect_outliers", "Statistical outlier detection", 0.5)
        ]
        
        for analytic, description, complexity in analytic_types:
            tool = MockToolSpec(
                tool_id=analytic,
                name=analytic.replace("_", " ").title(),
                description=description,
                category=ToolCategory.ANALYTICS,
                input_types=["graph_ref", "entities_ref"],
                output_types=["analysis_ref"],
                parameters={
                    "algorithm": {"type": "string", "description": "Algorithm to use"},
                    "sensitivity": {"type": "number", "default": 0.5},
                    "iterations": {"type": "integer", "default": 100}
                },
                complexity_score=complexity,
                dependencies=["build_graph_*"],
                parallel_compatible=[]
            )
            analytics.append(tool)
            
        return analytics
    
    def _generate_export_visualization_tools(self) -> List[MockToolSpec]:
        """Generate export and visualization tools"""
        exporters = []
        
        export_types = [
            ("export_json", "Export data as JSON", 0.2),
            ("export_csv", "Export tabular data as CSV", 0.2),
            ("export_graphml", "Export graph as GraphML", 0.3),
            ("export_gephi", "Export for Gephi visualization", 0.3),
            ("visualize_network", "Create network visualization", 0.5),
            ("generate_report", "Generate analysis report", 0.6),
            ("create_dashboard", "Create interactive dashboard", 0.7)
        ]
        
        for export_type, description, complexity in export_types:
            tool = MockToolSpec(
                tool_id=export_type,
                name=export_type.replace("_", " ").title(),
                description=description,
                category=ToolCategory.EXPORT_VISUALIZATION,
                input_types=["graph_ref", "analysis_ref", "query_results_ref"],
                output_types=["export_ref"],
                parameters={
                    "format": {"type": "string", "enum": ["json", "csv", "html", "pdf"]},
                    "include_metadata": {"type": "boolean", "default": True},
                    "compression": {"type": "string", "enum": ["none", "gzip", "zip"]}
                },
                complexity_score=complexity,
                dependencies=["*"],
                parallel_compatible=[]
            )
            exporters.append(tool)
            
        return exporters
    
    def save_tool_specs(self, filepath: str):
        """Save all tool specifications to JSON file"""
        tool_data = {
            "total_tools": len(self.tools),
            "categories": {cat.value: len([t for t in self.tools if t.category == cat]) 
                         for cat in ToolCategory},
            "tools": [asdict(tool) for tool in self.tools]
        }
        
        with open(filepath, 'w') as f:
            json.dump(tool_data, f, indent=2, default=str)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about generated tools"""
        return {
            "total_tools": len(self.tools),
            "by_category": {cat.value: len([t for t in self.tools if t.category == cat]) 
                           for cat in ToolCategory},
            "complexity_distribution": {
                "simple (0.1-0.3)": len([t for t in self.tools if t.complexity_score <= 0.3]),
                "medium (0.4-0.6)": len([t for t in self.tools if 0.3 < t.complexity_score <= 0.6]),
                "complex (0.7-1.0)": len([t for t in self.tools if t.complexity_score > 0.6])
            },
            "parallel_opportunities": len([t for t in self.tools if t.parallel_compatible])
        }


if __name__ == "__main__":
    generator = MockToolGenerator()
    tools = generator.generate_all_tools()
    
    print(f"Generated {len(tools)} mock MCP tools")
    print("\nCategory breakdown:")
    stats = generator.get_stats()
    for category, count in stats["by_category"].items():
        print(f"  {category}: {count} tools")
    
    print(f"\nComplexity distribution:")
    for level, count in stats["complexity_distribution"].items():
        print(f"  {level}: {count} tools")
    
    # Save specifications
    generator.save_tool_specs("mock_tools_spec.json")
    print(f"\nTool specifications saved to mock_tools_spec.json")