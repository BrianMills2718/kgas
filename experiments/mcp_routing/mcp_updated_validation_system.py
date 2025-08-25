#!/usr/bin/env python3
"""
Updated MCP-Compliant DAG Validation System

Tests Gemini's tool selection using realistic MCP tool specifications
following the official MCP protocol format.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

import litellm
from run_with_env import load_env

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_env()

@dataclass
class MCPTool:
    """MCP-compliant tool specification"""
    name: str
    title: str
    description: str
    input_schema: Dict[str, Any]
    annotations: Dict[str, Any]

class MCPToolCatalog:
    """Generate realistic MCP tool catalog"""
    
    def generate_complete_catalog(self) -> List[MCPTool]:
        """Generate ~100 MCP-compliant tools"""
        
        tools = []
        
        # Document Loading (15 tools)
        doc_tools = [
            ("load_document_pdf", "PDF Document Loader", "Extract text and metadata from PDF documents with structure preservation"),
            ("load_document_docx", "Word Document Loader", "Load Microsoft Word documents with formatting and metadata"),
            ("load_document_html", "HTML Document Loader", "Extract clean text from HTML with optional element filtering"),
            ("load_document_csv", "CSV Document Loader", "Parse CSV files with configurable delimiters and type inference"),
            ("load_document_json", "JSON Document Loader", "Load and validate JSON documents with schema validation"),
            ("load_document_xml", "XML Document Loader", "Parse XML documents with namespace and schema support"),
            ("load_document_txt", "Text Document Loader", "Load plain text with encoding detection and normalization"),
            ("load_document_xlsx", "Excel Spreadsheet Loader", "Load Excel files with multiple sheet support"),
            ("load_document_pptx", "PowerPoint Loader", "Extract content from PowerPoint presentations"),
            ("load_document_epub", "EPUB eBook Loader", "Load eBook content with chapter structure preservation"),
            ("load_document_rtf", "RTF Document Loader", "Parse Rich Text Format with formatting preservation"),
            ("load_document_odt", "OpenDocument Loader", "Load OpenDocument text files with style preservation"),
            ("load_document_markdown", "Markdown Loader", "Parse Markdown with metadata and structure extraction"),
            ("load_web_content", "Web Content Loader", "Fetch and clean content from web URLs"),
            ("load_email_content", "Email Content Loader", "Extract text and metadata from email messages")
        ]
        
        for name, title, desc in doc_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to document"},
                        "extract_metadata": {"type": "boolean", "default": True, "description": "Extract metadata"},
                        "preserve_structure": {"type": "boolean", "default": False, "description": "Maintain structure"}
                    },
                    "required": ["file_path"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True}
            ))
        
        # Text Processing (20 tools)
        text_tools = [
            ("chunk_text_semantic", "Semantic Text Chunker", "Split text using semantic boundaries for optimal processing"),
            ("chunk_text_fixed", "Fixed-Size Text Chunker", "Split text into fixed-size chunks with overlap"),
            ("chunk_text_sliding", "Sliding Window Chunker", "Create overlapping text windows for analysis"),
            ("clean_text_basic", "Basic Text Cleaner", "Remove noise and normalize text formatting"),
            ("clean_text_aggressive", "Advanced Text Cleaner", "Comprehensive cleaning with language detection"),
            ("clean_text_business", "Business Text Cleaner", "Specialized cleaning for business documents"),
            ("tokenize_words", "Word Tokenizer", "Split text into word tokens with language support"),
            ("tokenize_sentences", "Sentence Tokenizer", "Split text into sentence boundaries"),
            ("extract_keywords_tfidf", "TF-IDF Keyword Extractor", "Extract keywords using TF-IDF scoring"),
            ("extract_keywords_rake", "RAKE Keyword Extractor", "Extract keywords using RAKE algorithm"),
            ("extract_keywords_yake", "YAKE Keyword Extractor", "Language-independent keyword extraction"),
            ("normalize_text", "Text Normalizer", "Standardize text format and encoding"),
            ("remove_stopwords", "Stopword Remover", "Filter common stopwords by language"),
            ("stem_words", "Word Stemmer", "Reduce words to root forms"),
            ("lemmatize_text", "Text Lemmatizer", "Convert words to dictionary forms"),
            ("detect_language", "Language Detector", "Identify document language"),
            ("translate_text", "Text Translator", "Translate between languages using AI"),
            ("extract_ngrams", "N-gram Extractor", "Extract n-gram patterns from text"),
            ("summarize_extractive", "Extractive Summarizer", "Create summaries using sentence extraction"),
            ("summarize_abstractive", "Abstractive Summarizer", "Generate AI-powered abstractive summaries")
        ]
        
        for name, title, desc in text_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text content to process"},
                        "language": {"type": "string", "enum": ["en", "es", "fr", "de", "auto"], "default": "auto"},
                        "max_length": {"type": "integer", "minimum": 100, "maximum": 10000, "default": 1000}
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True}
            ))
        
        # Entity Extraction (25 tools)
        entity_tools = [
            ("extract_entities_llm_gemini", "Gemini Entity Extractor", "Advanced entity extraction using Gemini"),
            ("extract_entities_llm_claude", "Claude Entity Extractor", "High-quality entity extraction using Claude"),
            ("extract_entities_llm_gemini", "Gemini Entity Extractor", "Google Gemini-powered entity extraction"),
            ("extract_entities_llm_local", "Local LLM Entity Extractor", "Privacy-focused local LLM extraction"),
            ("extract_entities_spacy_sm", "SpaCy Small Model", "Fast entity extraction with SpaCy small model"),
            ("extract_entities_spacy_md", "SpaCy Medium Model", "Balanced accuracy/speed with SpaCy medium"),
            ("extract_entities_spacy_lg", "SpaCy Large Model", "High-accuracy SpaCy large model extraction"),
            ("extract_entities_spacy_trf", "SpaCy Transformer", "State-of-art SpaCy transformer model"),
            ("extract_entities_scientific", "Scientific Entity Extractor", "Domain-specific scientific text analysis"),
            ("extract_entities_business", "Business Entity Extractor", "Specialized for business document analysis"),
            ("extract_entities_medical", "Medical Entity Extractor", "Healthcare and medical text processing"),
            ("extract_entities_legal", "Legal Entity Extractor", "Legal document and contract analysis"),
            ("extract_entities_financial", "Financial Entity Extractor", "Financial document and data extraction"),
            ("extract_entities_academic", "Academic Entity Extractor", "Research paper and academic text analysis"),
            ("extract_entities_news", "News Entity Extractor", "Journalism and news article processing"),
            ("extract_entities_social", "Social Media Extractor", "Social media post and comment analysis"),
            ("extract_entities_regex", "Regex Entity Extractor", "Pattern-based extraction using regex"),
            ("extract_entities_basic", "Basic Entity Extractor", "Simple rule-based entity extraction"),
            ("extract_entities_ensemble", "Ensemble Entity Extractor", "Combine multiple extraction methods"),
            ("extract_entities_custom", "Custom Entity Extractor", "User-defined entity extraction models"),
            ("extract_entities_multilingual", "Multilingual Extractor", "Cross-language entity extraction"),
            ("extract_entities_temporal", "Temporal Entity Extractor", "Time and date expression extraction"),
            ("extract_entities_geographic", "Geographic Extractor", "Location and geographic entity extraction"),
            ("extract_entities_active", "Active Learning Extractor", "Adaptive extraction with user feedback"),
            ("extract_performance_metrics", "Performance Metrics Extractor", "Extract quantitative performance data")
        ]
        
        for name, title, desc in entity_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"},
                        "entity_types": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Entity types to extract",
                            "default": ["PERSON", "ORG", "LOC", "DATE"]
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "default": 0.7,
                            "description": "Minimum confidence score"
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True}
            ))
        
        # Relationship Analysis (15 tools)
        rel_tools = [
            ("extract_relationships_llm", "LLM Relationship Extractor", "AI-powered semantic relationship extraction"),
            ("extract_relationships_dependency", "Dependency Parser", "Grammar-based relationship extraction"),
            ("extract_relationships_pattern", "Pattern-Based Extractor", "Rule-based relationship identification"),
            ("extract_relationships_semantic", "Semantic Relationship Analyzer", "Meaning-based relationship extraction"),
            ("extract_relationships_coreference", "Coreference Resolver", "Entity reference resolution"),
            ("extract_relationships_temporal", "Temporal Relationship Extractor", "Time-based relationships"),
            ("extract_relationships_spatial", "Spatial Relationship Analyzer", "Location-based relationships"),
            ("extract_relationships_causal", "Causal Relationship Detector", "Cause-effect relationship identification"),
            ("extract_relationships_hierarchical", "Hierarchy Extractor", "Parent-child relationship detection"),
            ("extract_relationships_network", "Network Relationship Analyzer", "Social network relationship analysis"),
            ("extract_relationships_knowledge", "Knowledge-Based Extractor", "Domain knowledge relationship extraction"),
            ("extract_relationships_statistical", "Statistical Relationship Analyzer", "Data-driven relationship discovery"),
            ("extract_relationships_graph", "Graph-Based Extractor", "Graph algorithm relationship identification"),
            ("extract_relationships_hybrid", "Hybrid Relationship Extractor", "Multi-method relationship extraction"),
            ("extract_financial_ratios", "Financial Ratio Calculator", "Calculate financial performance ratios")
        ]
        
        for name, title, desc in rel_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text containing relationships"},
                        "entities": {"type": "array", "description": "Previously extracted entities"},
                        "relationship_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Relationship types to extract"
                        }
                    },
                    "required": ["text"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True}
            ))
        
        # Graph Operations (12 tools)  
        graph_tools = [
            ("build_knowledge_graph", "Knowledge Graph Builder", "Construct comprehensive knowledge graphs"),
            ("build_graph_entities", "Entity Graph Builder", "Build graphs from entity data"),
            ("build_graph_relationships", "Relationship Graph Builder", "Construct graphs from relationships"),
            ("merge_graphs", "Graph Merger", "Combine multiple graphs with alignment"),
            ("filter_graph", "Graph Filter", "Filter graphs by criteria"),
            ("prune_graph", "Graph Pruner", "Remove low-importance nodes and edges"),
            ("cluster_graph", "Graph Clusterer", "Identify communities in graphs"),
            ("validate_graph", "Graph Validator", "Validate graph structure and consistency"),
            ("optimize_graph", "Graph Optimizer", "Optimize graph for performance"),
            ("transform_graph", "Graph Transformer", "Transform graph structure and format"),
            ("sample_graph", "Graph Sampler", "Extract representative subgraphs"),
            ("project_graph", "Graph Projector", "Project graphs to different representations")
        ]
        
        for name, title, desc in graph_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "entities": {"type": "array", "description": "Graph entities"},
                        "relationships": {"type": "array", "description": "Graph relationships"},
                        "merge_similar": {"type": "boolean", "default": True, "description": "Merge similar entities"}
                    },
                    "required": ["entities"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": False}
            ))
        
        # Analytics & Query Tools (13 tools)
        analytics_tools = [
            ("calculate_pagerank", "PageRank Calculator", "Calculate node importance using PageRank"),
            ("calculate_centrality", "Centrality Metrics", "Compute various centrality measures"),
            ("detect_communities", "Community Detector", "Identify graph communities"),
            ("analyze_financial_trends", "Financial Trend Analyzer", "Analyze financial data trends"),
            ("forecast_financial_metrics", "Financial Forecaster", "Predict future financial performance"),
            ("calculate_similarity", "Similarity Calculator", "Compute entity similarity scores"),
            ("detect_anomalies", "Anomaly Detector", "Identify unusual patterns in data"),
            ("perform_clustering", "Data Clusterer", "Group similar data points"),
            ("query_graph_multihop", "Multi-hop Query Engine", "Execute complex graph traversals"),
            ("query_graph_semantic", "Semantic Query Engine", "Meaning-based graph queries"),
            ("query_graph_path", "Path Finding Engine", "Find optimal paths in graphs"),
            ("find_shortest_paths", "Shortest Path Finder", "Compute shortest paths between nodes"),
            ("measure_influence", "Influence Measurer", "Quantify entity influence in networks")
        ]
        
        for name, title, desc in analytics_tools:
            tools.append(MCPTool(
                name=name,
                title=title,
                description=desc,
                input_schema={
                    "type": "object",
                    "properties": {
                        "graph": {"type": "object", "description": "Graph to analyze"},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to calculate"
                        },
                        "normalize": {"type": "boolean", "default": True, "description": "Normalize results"}
                    },
                    "required": ["graph"]
                },
                annotations={"destructiveHint": False, "readOnlyHint": True}
            ))
        
        return tools
    
    def format_for_gemini(self, tools: List[MCPTool]) -> List[Dict[str, Any]]:
        """Format tools for Gemini consumption (MCP protocol format)"""
        
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

class UpdatedDAGValidator:
    """Updated DAG validator using real MCP format"""
    
    def __init__(self):
        self.catalog = MCPToolCatalog()
        self.all_tools = self.catalog.generate_complete_catalog()
        self.formatted_tools = self.catalog.format_for_gemini(self.all_tools)
        
        logger.info(f"Initialized with {len(self.all_tools)} MCP-compliant tools")
    
    def generate_dag_for_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate DAG using real MCP tool format"""
        
        # Show first 50 tools to Gemini (to manage context window)
        tool_sample = self.formatted_tools[:50]
        
        system_prompt = f"""
You are an expert workflow designer. Generate a tool call workflow (DAG) for this task.

Available tools (MCP format):
{json.dumps(tool_sample, indent=1)}

Return a JSON workflow with this structure:
{{
    "steps": [
        {{
            "id": "step_name",
            "tool": "exact_tool_name_from_list", 
            "params": {{"param_name": "param_value"}},
            "inputs": ["reference_from_previous_step"],
            "outputs": ["reference_for_next_step"]
        }}
    ],
    "flow": ["step1 -> step2", "step2 -> step3"],
    "rationale": "detailed explanation of workflow design choices"
}}

Design an efficient workflow using the MCP tools provided.
Use proper JSON Schema parameter types and validation.
        """
        
        try:
            response = litellm.completion(
                model="gemini/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Task: {prompt}"}
                ],
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            dag = json.loads(response_text)
            
            return dag
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON parsing failed: {e}", "raw_response": response_text}
        except Exception as e:
            return {"error": f"DAG generation failed: {e}"}
    
    def test_single_prompt(self, prompt: str, expected_tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """Test single prompt with MCP-compliant tools"""
        
        logger.info(f"Testing prompt: '{prompt[:60]}...'")
        
        start_time = time.time()
        gemini_dag = self.generate_dag_for_prompt(prompt)
        generation_time = time.time() - start_time
        
        if "error" in gemini_dag:
            return {
                "prompt": prompt,
                "success": False,
                "error": gemini_dag["error"],
                "generation_time": generation_time
            }
        
        # Extract Gemini's tool choices
        gemini_tools = [step.get("tool", "") for step in gemini_dag.get("steps", [])]
        
        # Analysis
        analysis = {
            "prompt": prompt,
            "success": True,
            "generation_time": generation_time,
            "gemini_dag": gemini_dag,
            "gemini_tools": gemini_tools,
            "tool_count": len(gemini_tools),
            "uses_mcp_format": self._validates_mcp_usage(gemini_dag),
            "parameter_complexity": self._assess_parameter_complexity(gemini_dag),
            "workflow_logic": self._assess_workflow_logic(gemini_dag)
        }
        
        if expected_tools:
            analysis["comparison"] = {
                "expected_tools": expected_tools,
                "tool_overlap": len(set(gemini_tools) & set(expected_tools)),
                "exact_match": set(gemini_tools) == set(expected_tools)
            }
        
        return analysis
    
    def _validates_mcp_usage(self, dag: Dict[str, Any]) -> bool:
        """Check if DAG demonstrates understanding of MCP format"""
        
        steps = dag.get("steps", [])
        if not steps:
            return False
        
        # Check if tools exist in our catalog
        available_tool_names = {tool.name for tool in self.all_tools}
        used_tools = {step.get("tool", "") for step in steps}
        
        valid_tools = used_tools & available_tool_names
        return len(valid_tools) / len(used_tools) > 0.7 if used_tools else False
    
    def _assess_parameter_complexity(self, dag: Dict[str, Any]) -> str:
        """Assess how well Gemini handles MCP parameter schemas"""
        
        steps = dag.get("steps", [])
        if not steps:
            return "none"
        
        param_usage = 0
        for step in steps:
            params = step.get("params", {})
            if params and isinstance(params, dict) and len(params) > 0:
                param_usage += 1
        
        param_rate = param_usage / len(steps)
        
        if param_rate > 0.7:
            return "high"
        elif param_rate > 0.3:
            return "medium"
        else:
            return "low"
    
    def _assess_workflow_logic(self, dag: Dict[str, Any]) -> str:
        """Assess logical consistency of workflow"""
        
        steps = dag.get("steps", [])
        if len(steps) < 2:
            return "simple"
        
        # Check input/output dependencies
        all_outputs = set()
        dependency_errors = 0
        
        for step in steps:
            inputs = step.get("inputs", [])
            for inp in inputs:
                if inp not in all_outputs and inp != "":
                    dependency_errors += 1
            
            outputs = step.get("outputs", [])
            all_outputs.update(outputs)
        
        total_inputs = sum(len(step.get("inputs", [])) for step in steps)
        
        if total_inputs == 0:
            return "linear"
        
        error_rate = dependency_errors / total_inputs if total_inputs > 0 else 0
        
        if error_rate < 0.2:
            return "logical"
        elif error_rate < 0.5:
            return "mostly_logical"
        else:
            return "inconsistent"
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test with various prompts"""
        
        test_prompts = [
            "Extract entities and relationships from this research paper and build a knowledge graph",
            "Process this business document to find key people, organizations, and financial information",
            "Analyze this academic paper for methodologies, datasets, and performance metrics",
            "Load this PDF document, extract important entities, and create a summary report",
            "Build a comprehensive knowledge graph from scientific literature with entity extraction",
            "Process financial reports to identify trends, ratios, and forecasting insights"
        ]
        
        results = []
        
        for prompt in test_prompts:
            result = self.test_single_prompt(prompt)
            results.append(result)
            
            # Brief delay between tests
            time.sleep(2)
        
        # Aggregate analysis
        successful_tests = [r for r in results if r["success"]]
        
        aggregate_stats = {
            "total_tests": len(test_prompts),
            "successful_tests": len(successful_tests),
            "success_rate": len(successful_tests) / len(test_prompts),
            "avg_generation_time": sum(r["generation_time"] for r in successful_tests) / len(successful_tests) if successful_tests else 0,
            "avg_tool_count": sum(r["tool_count"] for r in successful_tests) / len(successful_tests) if successful_tests else 0,
            "mcp_format_usage": sum(1 for r in successful_tests if r["uses_mcp_format"]) / len(successful_tests) if successful_tests else 0,
            "parameter_complexity_distribution": self._analyze_parameter_complexity(successful_tests),
            "workflow_logic_distribution": self._analyze_workflow_logic(successful_tests)
        }
        
        return {
            "test_results": results,
            "aggregate_analysis": aggregate_stats,
            "tool_catalog_size": len(self.all_tools),
            "mcp_compliant": True,
            "timestamp": time.time()
        }
    
    def _analyze_parameter_complexity(self, results: List[Dict]) -> Dict[str, int]:
        """Analyze parameter complexity distribution"""
        
        distribution = {"high": 0, "medium": 0, "low": 0, "none": 0}
        for result in results:
            complexity = result.get("parameter_complexity", "none")
            distribution[complexity] = distribution.get(complexity, 0) + 1
        
        return distribution
    
    def _analyze_workflow_logic(self, results: List[Dict]) -> Dict[str, int]:
        """Analyze workflow logic distribution"""
        
        distribution = {"logical": 0, "mostly_logical": 0, "inconsistent": 0, "linear": 0, "simple": 0}
        for result in results:
            logic = result.get("workflow_logic", "simple")
            distribution[logic] = distribution.get(logic, 0) + 1
        
        return distribution
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save test results"""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"mcp_updated_validation_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {filepath}")
        return str(filepath)

def main():
    """Run updated MCP-compliant validation"""
    
    # Verify API access
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("Missing GOOGLE_API_KEY in environment")
        return
    
    validator = UpdatedDAGValidator()
    
    try:
        results = validator.run_comprehensive_test()
        
        # Save results
        results_file = validator.save_results(results)
        
        # Print summary
        print("\n" + "="*80)
        print("🔬 MCP-COMPLIANT DAG VALIDATION COMPLETE")
        print("="*80)
        
        stats = results["aggregate_analysis"]
        
        print(f"Total tests: {stats['total_tests']}")
        print(f"Successful tests: {stats['successful_tests']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Tool catalog size: {results['tool_catalog_size']}")
        print(f"Average generation time: {stats['avg_generation_time']:.2f}s")
        print(f"Average tools per workflow: {stats['avg_tool_count']:.1f}")
        print(f"MCP format usage: {stats['mcp_format_usage']:.1%}")
        
        print(f"\n📊 PARAMETER COMPLEXITY:")
        for level, count in stats['parameter_complexity_distribution'].items():
            print(f"  {level}: {count}")
        
        print(f"\n🔗 WORKFLOW LOGIC:")
        for logic, count in stats['workflow_logic_distribution'].items():
            print(f"  {logic}: {count}")
        
        print(f"\n📄 Detailed results: {results_file}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise

if __name__ == "__main__":
    main()