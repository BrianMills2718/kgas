#!/usr/bin/env python3
"""
Corrected DAG Validation System

Tests Gemini's ability to reverse-engineer optimal workflows from prompts.
Each reference DAG has one carefully crafted prompt optimized for that workflow.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Import our components
from mock_tool_generator import MockToolGenerator
import litellm
from run_with_env import load_env

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_env()

@dataclass
class TaskDAGPair:
    """A task with optimized DAG and carefully crafted prompt"""
    task_id: str
    description: str
    optimized_dag: Dict[str, Any]
    crafted_prompt: str
    design_rationale: str
    
@dataclass
class ComparisonResult:
    """Results of comparing reference DAG vs Gemini's reverse-engineered DAG"""
    task_id: str
    crafted_prompt: str
    reference_dag: Dict[str, Any]
    gemini_dag: Dict[str, Any]
    comparison_successful: bool
    metrics: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    manual_annotations: Dict[str, Any]
    timestamp: float
    comparison_id: str

class OptimizedDAGLibrary:
    """Library of hand-crafted optimal DAGs with tailored prompts"""
    
    def __init__(self):
        self.task_dag_pairs = self._create_optimized_pairs()
    
    def _create_optimized_pairs(self) -> Dict[str, TaskDAGPair]:
        """Create 3 optimized DAG + prompt pairs"""
        
        return {
            "research_paper_extraction": TaskDAGPair(
                task_id="research_paper_extraction",
                description="Comprehensive academic paper analysis with methodology extraction",
                optimized_dag={
                    "steps": [
                        {
                            "id": "load_pdf",
                            "tool": "load_document_pdf",
                            "params": {"extract_metadata": True, "preserve_structure": True},
                            "inputs": [],
                            "outputs": ["document_ref"]
                        },
                        {
                            "id": "segment_document",
                            "tool": "chunk_text_semantic",
                            "params": {"chunk_size": 1500, "overlap": 200, "respect_sections": True},
                            "inputs": ["document_ref"],
                            "outputs": ["chunks_ref"]
                        },
                        {
                            "id": "extract_methodologies",
                            "tool": "extract_entities_scientific",
                            "params": {"entity_types": ["METHOD", "ALGORITHM", "TECHNIQUE"], "confidence_threshold": 0.8},
                            "inputs": ["chunks_ref"],
                            "outputs": ["methods_ref"]
                        },
                        {
                            "id": "extract_datasets",
                            "tool": "extract_entities_scientific", 
                            "params": {"entity_types": ["DATASET", "CORPUS", "BENCHMARK"], "confidence_threshold": 0.8},
                            "inputs": ["chunks_ref"],
                            "outputs": ["datasets_ref"]
                        },
                        {
                            "id": "extract_metrics",
                            "tool": "extract_performance_metrics",
                            "params": {"metric_types": ["ACCURACY", "F1", "PRECISION", "RECALL", "AUC"], "normalize_values": True},
                            "inputs": ["chunks_ref"],
                            "outputs": ["metrics_ref"]
                        },
                        {
                            "id": "extract_experimental_results",
                            "tool": "extract_entities_scientific",
                            "params": {"entity_types": ["RESULT", "FINDING", "CONCLUSION"], "confidence_threshold": 0.7},
                            "inputs": ["chunks_ref"],
                            "outputs": ["results_ref"]
                        },
                        {
                            "id": "link_method_performance",
                            "tool": "extract_relationships_llm",
                            "params": {"relationship_types": ["ACHIEVES", "OUTPERFORMS", "USES", "EVALUATES"], "cross_reference": True},
                            "inputs": ["methods_ref", "metrics_ref", "datasets_ref"],
                            "outputs": ["relationships_ref"]
                        },
                        {
                            "id": "build_research_graph",
                            "tool": "build_knowledge_graph",
                            "params": {"include_metadata": True, "merge_similar_entities": True, "validate_relationships": True},
                            "inputs": ["methods_ref", "datasets_ref", "metrics_ref", "results_ref", "relationships_ref"],
                            "outputs": ["research_graph_ref"]
                        },
                        {
                            "id": "export_structured_analysis",
                            "tool": "export_academic_summary",
                            "params": {"include_citations": True, "format": "structured_json", "validate_completeness": True},
                            "inputs": ["research_graph_ref"],
                            "outputs": ["final_analysis_ref"]
                        }
                    ],
                    "flow": [
                        "load_pdf -> segment_document",
                        "segment_document -> extract_methodologies",
                        "segment_document -> extract_datasets", 
                        "segment_document -> extract_metrics",
                        "segment_document -> extract_experimental_results",
                        "extract_methodologies + extract_metrics + extract_datasets -> link_method_performance",
                        "extract_methodologies + extract_datasets + extract_metrics + extract_experimental_results + link_method_performance -> build_research_graph",
                        "build_research_graph -> export_structured_analysis"
                    ]
                },
                crafted_prompt="Extract and systematically catalog all methodologies, algorithms, techniques, datasets, benchmarks, performance metrics (accuracy, F1, precision, recall, AUC), and experimental results from this research paper. Identify the relationships between methods and their performance on specific datasets, then construct a comprehensive knowledge graph that maps the complete experimental landscape. Export a structured analysis that preserves all methodological details, dataset associations, performance comparisons, and experimental findings with full citation context.",
                design_rationale="This workflow is designed for comprehensive academic analysis requiring high precision entity extraction, relationship mapping, and structured knowledge representation. Each step uses specialized tools with careful parameter tuning for academic content. The multi-step approach ensures no information is lost and relationships are properly captured."
            ),
            
            "business_intelligence_report": TaskDAGPair(
                task_id="business_intelligence_report", 
                description="Rapid business document processing for executive insights",
                optimized_dag={
                    "steps": [
                        {
                            "id": "ingest_document",
                            "tool": "load_document_pdf",
                            "params": {"fast_mode": True, "extract_tables": True},
                            "inputs": [],
                            "outputs": ["doc_ref"]
                        },
                        {
                            "id": "clean_business_text",
                            "tool": "clean_text_business",
                            "params": {"remove_headers_footers": True, "normalize_currency": True, "standardize_dates": True},
                            "inputs": ["doc_ref"],
                            "outputs": ["clean_doc_ref"]
                        },
                        {
                            "id": "extract_key_entities",
                            "tool": "extract_entities_business",
                            "params": {"entity_types": ["PERSON", "ORGANIZATION", "MONEY", "DATE", "PRODUCT", "METRIC"], "prioritize_financial": True},
                            "inputs": ["clean_doc_ref"],
                            "outputs": ["entities_ref"]
                        },
                        {
                            "id": "generate_executive_summary", 
                            "tool": "summarize_executive",
                            "params": {"max_length": 300, "focus_areas": ["key_insights", "financial_highlights", "action_items"], "tone": "professional"},
                            "inputs": ["clean_doc_ref", "entities_ref"],
                            "outputs": ["summary_ref"]
                        },
                        {
                            "id": "create_insight_dashboard",
                            "tool": "create_business_dashboard",
                            "params": {"chart_types": ["summary_cards", "key_metrics", "trend_indicators"], "executive_format": True},
                            "inputs": ["entities_ref", "summary_ref"],
                            "outputs": ["dashboard_ref"]
                        },
                        {
                            "id": "package_deliverable",
                            "tool": "export_business_report",
                            "params": {"format": "executive_pdf", "include_dashboard": True, "add_branding": True},
                            "inputs": ["summary_ref", "dashboard_ref"],
                            "outputs": ["business_report_ref"]
                        }
                    ],
                    "flow": [
                        "ingest_document -> clean_business_text",
                        "clean_business_text -> extract_key_entities",
                        "clean_business_text + extract_key_entities -> generate_executive_summary",
                        "extract_key_entities + generate_executive_summary -> create_insight_dashboard",
                        "generate_executive_summary + create_insight_dashboard -> package_deliverable"
                    ]
                },
                crafted_prompt="Process this business document to rapidly extract key business entities (people, organizations, financial figures, dates, products, metrics), generate a concise executive summary highlighting key insights and financial highlights with actionable items, create a visual insight dashboard with summary cards and trend indicators, and package everything into a professional executive report with branding suitable for C-level presentation.",
                design_rationale="This workflow prioritizes speed and executive-level presentation. It uses business-specific tools for entity extraction and cleaning, focuses on rapid insight generation, and emphasizes visual presentation suitable for business stakeholders. Each step is optimized for business content and executive consumption."
            ),
            
            "financial_trend_analysis": TaskDAGPair(
                task_id="financial_trend_analysis",
                description="Deep financial analysis with temporal trends and forecasting",
                optimized_dag={
                    "steps": [
                        {
                            "id": "load_financial_doc",
                            "tool": "load_document_pdf",
                            "params": {"preserve_tables": True, "extract_numbers": True, "maintain_formatting": True},
                            "inputs": [],
                            "outputs": ["financial_doc_ref"]
                        },
                        {
                            "id": "extract_financial_entities",
                            "tool": "extract_entities_financial",
                            "params": {"entity_types": ["REVENUE", "PROFIT", "EXPENSE", "ASSET", "LIABILITY", "CASHFLOW"], "normalize_currencies": True, "extract_percentages": True},
                            "inputs": ["financial_doc_ref"],
                            "outputs": ["financial_entities_ref"]
                        },
                        {
                            "id": "extract_temporal_data",
                            "tool": "extract_entities_temporal",
                            "params": {"date_formats": ["Q1", "Q2", "Q3", "Q4", "YYYY", "MM/YYYY"], "fiscal_year_aware": True, "quarter_normalization": True},
                            "inputs": ["financial_doc_ref"],
                            "outputs": ["temporal_ref"]
                        },
                        {
                            "id": "extract_financial_ratios",
                            "tool": "extract_financial_ratios",
                            "params": {"ratio_types": ["PROFITABILITY", "LIQUIDITY", "EFFICIENCY", "LEVERAGE"], "calculate_derived": True},
                            "inputs": ["financial_doc_ref"],
                            "outputs": ["ratios_ref"]
                        },
                        {
                            "id": "analyze_trends",
                            "tool": "analyze_financial_trends",
                            "params": {"trend_types": ["GROWTH", "DECLINE", "SEASONAL", "CYCLICAL"], "time_windows": ["quarterly", "yearly"], "statistical_significance": True},
                            "inputs": ["financial_entities_ref", "temporal_ref"],
                            "outputs": ["trends_ref"]
                        },
                        {
                            "id": "forecast_metrics",
                            "tool": "forecast_financial_metrics",
                            "params": {"forecast_periods": 4, "confidence_intervals": True, "scenario_analysis": ["optimistic", "realistic", "pessimistic"]},
                            "inputs": ["financial_entities_ref", "temporal_ref", "trends_ref"],
                            "outputs": ["forecasts_ref"]
                        },
                        {
                            "id": "create_financial_dashboard",
                            "tool": "create_financial_dashboard",
                            "params": {"chart_types": ["line", "bar", "waterfall", "heat_map"], "include_forecasts": True, "interactive": True},
                            "inputs": ["financial_entities_ref", "trends_ref", "forecasts_ref", "ratios_ref"],
                            "outputs": ["dashboard_ref"]
                        },
                        {
                            "id": "generate_analyst_report",
                            "tool": "generate_financial_report",
                            "params": {"sections": ["executive_summary", "trend_analysis", "forecast", "recommendations"], "analyst_tone": True},
                            "inputs": ["trends_ref", "forecasts_ref", "ratios_ref"],
                            "outputs": ["analyst_report_ref"]
                        }
                    ],
                    "flow": [
                        "load_financial_doc -> extract_financial_entities",
                        "load_financial_doc -> extract_temporal_data",
                        "load_financial_doc -> extract_financial_ratios",
                        "extract_financial_entities + extract_temporal_data -> analyze_trends",
                        "extract_financial_entities + extract_temporal_data + analyze_trends -> forecast_metrics",
                        "extract_financial_entities + analyze_trends + forecast_metrics + extract_financial_ratios -> create_financial_dashboard",
                        "analyze_trends + forecast_metrics + extract_financial_ratios -> generate_analyst_report"
                    ]
                },
                crafted_prompt="Conduct comprehensive financial analysis of this report by extracting all financial entities (revenue, profit, expenses, assets, liabilities, cash flow), temporal data (quarters, fiscal years), and financial ratios (profitability, liquidity, efficiency, leverage). Analyze trends across quarterly and yearly time windows with statistical significance testing. Generate forecasts for the next 4 periods with confidence intervals and scenario analysis (optimistic, realistic, pessimistic). Create an interactive financial dashboard with line charts, bar charts, waterfall charts, and heat maps that includes forecast visualizations. Produce a comprehensive analyst report with executive summary, detailed trend analysis, forecast methodology, and investment recommendations.",
                design_rationale="This workflow is designed for deep financial analysis requiring specialized financial entity extraction, temporal analysis, trend identification, and forecasting. It uses domain-specific tools for financial ratios, trend analysis, and forecasting. The multi-step approach ensures comprehensive coverage of all financial aspects with proper temporal relationships and forward-looking analysis."
            )
        }
    
    def get_task_pair(self, task_id: str) -> Optional[TaskDAGPair]:
        """Get task DAG pair by task ID"""
        return self.task_dag_pairs.get(task_id)
    
    def get_all_tasks(self) -> List[str]:
        """Get all available task IDs"""
        return list(self.task_dag_pairs.keys())

class GeminiDAGGenerator:
    """Generate tool call DAGs using Gemini"""
    
    def __init__(self, available_tools: List[Dict]):
        self.available_tools = available_tools
    
    def generate_dag_for_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate tool call DAG for crafted prompt"""
        
        system_prompt = f"""
You are an expert workflow designer. Generate a tool call workflow (DAG) for this task.

Available tools:
{json.dumps(self.available_tools[:75], indent=1)}  # Show first 75 tools

Return a JSON workflow with this exact structure:
{{
    "steps": [
        {{
            "id": "unique_step_name",
            "tool": "exact_tool_name_from_list_above", 
            "params": {{"param_name": "param_value"}},
            "inputs": ["reference_from_previous_step_output"],
            "outputs": ["reference_for_next_step_input"]
        }}
    ],
    "flow": ["step1 -> step2", "step1 -> step3", "step2 + step3 -> step4"],
    "rationale": "detailed explanation of workflow design choices and tool selection reasoning"
}}

Design an efficient, logical workflow that accomplishes the task completely.
Use only tools from the provided list.
Ensure inputs/outputs form a valid dependency chain.
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
            
            # Validate basic structure
            if not isinstance(dag.get("steps"), list):
                return {"error": "Invalid DAG structure: steps must be a list", "raw_response": response_text}
            
            return dag
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse Gemini DAG response: {e}", "raw_response": response_text}
        except Exception as e:
            return {"error": f"Failed to generate DAG: {e}"}

class ManualAnnotator:
    """Manual analysis and annotation of DAG differences"""
    
    def annotate_comparison(self, task_pair: TaskDAGPair, gemini_dag: Dict[str, Any]) -> Dict[str, Any]:
        """Manually annotate the differences between reference and Gemini DAGs"""
        
        if "error" in gemini_dag:
            return {
                "comparison_possible": False,
                "error": gemini_dag["error"],
                "annotations": {}
            }
        
        reference_dag = task_pair.optimized_dag
        
        # Extract tool lists
        ref_tools = [step["tool"] for step in reference_dag.get("steps", [])]
        gem_tools = [step["tool"] for step in gemini_dag.get("steps", [])]
        
        # Manual annotations based on tool choices and workflow structure
        annotations = {
            "tool_choice_analysis": self._analyze_tool_choices(ref_tools, gem_tools, task_pair),
            "workflow_structure_analysis": self._analyze_workflow_structure(reference_dag, gemini_dag, task_pair),
            "efficiency_analysis": self._analyze_efficiency(reference_dag, gemini_dag),
            "completeness_analysis": self._analyze_completeness(reference_dag, gemini_dag, task_pair),
            "domain_awareness_analysis": self._analyze_domain_awareness(ref_tools, gem_tools, task_pair.task_id),
            "prompt_interpretation_analysis": self._analyze_prompt_interpretation(task_pair.crafted_prompt, gemini_dag),
            "overall_assessment": self._overall_assessment(task_pair, gemini_dag)
        }
        
        return {
            "comparison_possible": True,
            "annotations": annotations,
            "gemini_rationale": gemini_dag.get("rationale", "No rationale provided")
        }
    
    def _analyze_tool_choices(self, ref_tools: List[str], gem_tools: List[str], task_pair: TaskDAGPair) -> Dict[str, Any]:
        """Analyze differences in tool selection"""
        
        ref_set = set(ref_tools)
        gem_set = set(gem_tools)
        
        overlap = ref_set & gem_set
        ref_only = ref_set - gem_set
        gem_only = gem_set - ref_set
        
        # Manual assessment of tool quality differences
        tool_quality_analysis = {}
        
        # Check for tool substitutions
        substitutions = []
        for ref_tool in ref_only:
            for gem_tool in gem_only:
                if self._tools_functionally_similar(ref_tool, gem_tool):
                    substitutions.append({
                        "reference_tool": ref_tool,
                        "gemini_tool": gem_tool,
                        "assessment": self._assess_tool_substitution(ref_tool, gem_tool)
                    })
        
        return {
            "tool_overlap_count": len(overlap),
            "tools_in_common": list(overlap),
            "reference_only_tools": list(ref_only),
            "gemini_only_tools": list(gem_only), 
            "tool_substitutions": substitutions,
            "manual_assessment": self._manual_tool_assessment(ref_tools, gem_tools, task_pair.task_id)
        }
    
    def _analyze_workflow_structure(self, ref_dag: Dict, gem_dag: Dict, task_pair: TaskDAGPair) -> Dict[str, Any]:
        """Analyze workflow structure differences"""
        
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        return {
            "step_count_comparison": {
                "reference_steps": ref_steps,
                "gemini_steps": gem_steps,
                "difference": gem_steps - ref_steps,
                "efficiency_assessment": "More efficient" if gem_steps < ref_steps else "More comprehensive" if gem_steps > ref_steps else "Same complexity"
            },
            "flow_comparison": {
                "reference_flow": ref_dag.get("flow", []),
                "gemini_flow": gem_dag.get("flow", []),
                "structure_assessment": self._assess_flow_structure(ref_dag.get("flow", []), gem_dag.get("flow", []))
            },
            "dependency_analysis": self._analyze_dependencies(ref_dag, gem_dag)
        }
    
    def _analyze_efficiency(self, ref_dag: Dict, gem_dag: Dict) -> Dict[str, Any]:
        """Analyze efficiency differences"""
        
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        efficiency_ratio = ref_steps / gem_steps if gem_steps > 0 else 0
        
        return {
            "efficiency_ratio": efficiency_ratio,
            "assessment": "Gemini more efficient" if efficiency_ratio > 1.2 else "Reference more efficient" if efficiency_ratio < 0.8 else "Similar efficiency",
            "step_reduction": ref_steps - gem_steps,
            "potential_trade_offs": self._assess_efficiency_tradeoffs(ref_steps, gem_steps)
        }
    
    def _analyze_completeness(self, ref_dag: Dict, gem_dag: Dict, task_pair: TaskDAGPair) -> Dict[str, Any]:
        """Analyze task completeness"""
        
        # Check if Gemini's workflow addresses all aspects of the crafted prompt
        prompt_requirements = self._extract_prompt_requirements(task_pair.crafted_prompt)
        gemini_capabilities = self._extract_workflow_capabilities(gem_dag)
        
        coverage = []
        for requirement in prompt_requirements:
            covered = any(requirement.lower() in cap.lower() for cap in gemini_capabilities)
            coverage.append({
                "requirement": requirement,
                "covered": covered,
                "covering_capability": next((cap for cap in gemini_capabilities if requirement.lower() in cap.lower()), None)
            })
        
        return {
            "prompt_requirements": prompt_requirements,
            "gemini_capabilities": gemini_capabilities,
            "requirement_coverage": coverage,
            "coverage_percentage": sum(1 for c in coverage if c["covered"]) / len(coverage) if coverage else 0,
            "missing_requirements": [c["requirement"] for c in coverage if not c["covered"]]
        }
    
    def _analyze_domain_awareness(self, ref_tools: List[str], gem_tools: List[str], task_id: str) -> Dict[str, Any]:
        """Analyze domain-specific awareness"""
        
        domain_tools = {
            "research_paper_extraction": ["scientific", "academic", "research", "citation"],
            "business_intelligence_report": ["business", "executive", "dashboard", "insight"],
            "financial_trend_analysis": ["financial", "trend", "forecast", "ratio"]
        }
        
        expected_domain_keywords = domain_tools.get(task_id, [])
        
        ref_domain_tools = [tool for tool in ref_tools if any(keyword in tool.lower() for keyword in expected_domain_keywords)]
        gem_domain_tools = [tool for tool in gem_tools if any(keyword in tool.lower() for keyword in expected_domain_keywords)]
        
        return {
            "expected_domain_keywords": expected_domain_keywords,
            "reference_domain_tools": ref_domain_tools,
            "gemini_domain_tools": gem_domain_tools,
            "domain_awareness_assessment": "Strong" if len(gem_domain_tools) >= len(ref_domain_tools) * 0.7 else "Moderate" if len(gem_domain_tools) > 0 else "Weak"
        }
    
    def _analyze_prompt_interpretation(self, prompt: str, gem_dag: Dict) -> Dict[str, Any]:
        """Analyze how well Gemini interpreted the prompt"""
        
        key_verbs = ["extract", "analyze", "generate", "create", "identify", "process", "construct"]
        key_nouns = ["methodology", "dataset", "metric", "trend", "forecast", "dashboard", "report", "summary"]
        
        prompt_lower = prompt.lower()
        found_verbs = [verb for verb in key_verbs if verb in prompt_lower]
        found_nouns = [noun for noun in key_nouns if noun in prompt_lower]
        
        gem_tools = [step["tool"] for step in gem_dag.get("steps", [])]
        gem_tools_str = " ".join(gem_tools).lower()
        
        verb_coverage = [verb for verb in found_verbs if verb in gem_tools_str]
        noun_coverage = [noun for noun in found_nouns if noun in gem_tools_str]
        
        return {
            "prompt_key_verbs": found_verbs,
            "prompt_key_nouns": found_nouns,
            "verb_coverage": verb_coverage,
            "noun_coverage": noun_coverage,
            "interpretation_quality": "Good" if len(verb_coverage) > len(found_verbs) * 0.5 and len(noun_coverage) > len(found_nouns) * 0.3 else "Fair" if len(verb_coverage) > 0 or len(noun_coverage) > 0 else "Poor"
        }
    
    def _overall_assessment(self, task_pair: TaskDAGPair, gem_dag: Dict) -> Dict[str, Any]:
        """Overall manual assessment"""
        
        return {
            "reverse_engineering_difficulty": "High" if len(task_pair.optimized_dag["steps"]) > 6 else "Medium" if len(task_pair.optimized_dag["steps"]) > 3 else "Low",
            "gemini_approach_viability": self._assess_viability(gem_dag),
            "comparative_strengths": self._identify_comparative_strengths(task_pair.optimized_dag, gem_dag),
            "comparative_weaknesses": self._identify_comparative_weaknesses(task_pair.optimized_dag, gem_dag),
            "recommended_winner": self._recommend_winner(task_pair, gem_dag)
        }
    
    # Helper methods
    def _tools_functionally_similar(self, tool1: str, tool2: str) -> bool:
        """Check if two tools are functionally similar"""
        similar_groups = [
            ["extract_entities_basic", "extract_entities_llm_gpt4", "extract_entities_spacy"],
            ["summarize_extractive", "summarize_abstractive"],
            ["chunk_text_semantic", "chunk_text_fixed"],
            ["clean_text_basic", "clean_text_business"]
        ]
        
        for group in similar_groups:
            if tool1 in group and tool2 in group:
                return True
        return False
    
    def _assess_tool_substitution(self, ref_tool: str, gem_tool: str) -> str:
        """Assess the quality of tool substitution"""
        quality_rankings = {
            "extract_entities_llm_gpt4": 5,
            "extract_entities_scientific": 4,
            "extract_entities_business": 4,
            "extract_entities_spacy": 3,
            "extract_entities_basic": 2,
            "summarize_abstractive": 4,
            "summarize_extractive": 3,
            "summarize_executive": 4
        }
        
        ref_quality = quality_rankings.get(ref_tool, 3)
        gem_quality = quality_rankings.get(gem_tool, 3)
        
        if gem_quality > ref_quality:
            return "Upgrade - Gemini chose better tool"
        elif gem_quality < ref_quality:
            return "Downgrade - Reference tool is better"
        else:
            return "Equivalent - Similar quality tools"
    
    def _manual_tool_assessment(self, ref_tools: List[str], gem_tools: List[str], task_id: str) -> str:
        """Manual assessment of overall tool choices"""
        
        # Task-specific assessments
        if task_id == "research_paper_extraction":
            if "extract_entities_llm_gpt4" in gem_tools and "extract_entities_scientific" in ref_tools:
                return "Gemini uses more powerful general tool vs specialized tools - potentially better"
            if "build_knowledge_graph" in ref_tools and not any("graph" in tool for tool in gem_tools):
                return "Reference includes knowledge graph construction which Gemini misses"
        
        elif task_id == "business_intelligence_report":
            if any("business" in tool for tool in gem_tools):
                return "Gemini shows domain awareness with business-specific tools"
            if any("dashboard" in tool for tool in ref_tools) and not any("dashboard" in tool for tool in gem_tools):
                return "Reference includes dashboard creation which Gemini might be missing"
        
        elif task_id == "financial_trend_analysis":
            if any("trend" in tool for tool in ref_tools) and not any("trend" in tool for tool in gem_tools):
                return "Reference includes explicit trend analysis which Gemini misses"
            if any("forecast" in tool for tool in ref_tools) and not any("forecast" in tool for tool in gem_tools):
                return "Reference includes forecasting capability which Gemini lacks"
        
        return "Mixed - both approaches have merits"
    
    def _assess_flow_structure(self, ref_flow: List[str], gem_flow: List[str]) -> str:
        """Assess flow structure differences"""
        if len(gem_flow) < len(ref_flow):
            return "Gemini uses simpler flow structure"
        elif len(gem_flow) > len(ref_flow):
            return "Gemini uses more complex flow structure"
        else:
            return "Similar complexity flow structures"
    
    def _analyze_dependencies(self, ref_dag: Dict, gem_dag: Dict) -> Dict[str, Any]:
        """Analyze dependency structure"""
        return {
            "reference_dependencies": len(ref_dag.get("flow", [])),
            "gemini_dependencies": len(gem_dag.get("flow", [])),
            "complexity_assessment": "Gemini simpler" if len(gem_dag.get("flow", [])) < len(ref_dag.get("flow", [])) else "Gemini more complex" if len(gem_dag.get("flow", [])) > len(ref_dag.get("flow", [])) else "Similar complexity"
        }
    
    def _assess_efficiency_tradeoffs(self, ref_steps: int, gem_steps: int) -> str:
        """Assess potential efficiency trade-offs"""
        if gem_steps < ref_steps:
            return "Fewer steps may mean less granular control but higher efficiency"
        elif gem_steps > ref_steps:
            return "More steps may provide better control but lower efficiency"
        else:
            return "Similar step count suggests comparable efficiency"
    
    def _extract_prompt_requirements(self, prompt: str) -> List[str]:
        """Extract key requirements from the crafted prompt"""
        # Simple keyword extraction - could be enhanced with NLP
        keywords = []
        prompt_lower = prompt.lower()
        
        requirement_patterns = [
            "extract", "analyze", "identify", "generate", "create", "construct", "process",
            "methodology", "dataset", "metric", "trend", "forecast", "dashboard", "summary", "report"
        ]
        
        for pattern in requirement_patterns:
            if pattern in prompt_lower:
                keywords.append(pattern)
        
        return keywords
    
    def _extract_workflow_capabilities(self, gem_dag: Dict) -> List[str]:
        """Extract capabilities from Gemini's workflow"""
        capabilities = []
        
        for step in gem_dag.get("steps", []):
            tool_name = step.get("tool", "")
            capabilities.append(tool_name)
        
        return capabilities
    
    def _assess_viability(self, gem_dag: Dict) -> str:
        """Assess the viability of Gemini's approach"""
        steps = gem_dag.get("steps", [])
        
        if len(steps) == 0:
            return "Non-viable - no steps"
        elif len(steps) < 3:
            return "Potentially viable but very simple"
        elif len(steps) > 10:
            return "Potentially viable but very complex"
        else:
            return "Viable - reasonable complexity"
    
    def _identify_comparative_strengths(self, ref_dag: Dict, gem_dag: Dict) -> List[str]:
        """Identify Gemini's comparative strengths"""
        strengths = []
        
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        if gem_steps < ref_steps:
            strengths.append("More efficient workflow")
        
        gem_tools = [step["tool"] for step in gem_dag.get("steps", [])]
        if any("llm" in tool.lower() for tool in gem_tools):
            strengths.append("Uses advanced LLM capabilities")
        
        return strengths
    
    def _identify_comparative_weaknesses(self, ref_dag: Dict, gem_dag: Dict) -> List[str]:
        """Identify Gemini's comparative weaknesses"""
        weaknesses = []
        
        ref_tools = [step["tool"] for step in ref_dag.get("steps", [])]
        gem_tools = [step["tool"] for step in gem_dag.get("steps", [])]
        
        # Check for missing specialized tools
        if any("scientific" in tool for tool in ref_tools) and not any("scientific" in tool for tool in gem_tools):
            weaknesses.append("Missing specialized scientific tools")
        
        if any("financial" in tool for tool in ref_tools) and not any("financial" in tool for tool in gem_tools):
            weaknesses.append("Missing specialized financial tools")
        
        return weaknesses
    
    def _recommend_winner(self, task_pair: TaskDAGPair, gem_dag: Dict) -> str:
        """Recommend which approach is better"""
        # This would require more sophisticated analysis
        # For now, return a simple assessment
        
        ref_steps = len(task_pair.optimized_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        if gem_steps < ref_steps * 0.7 and gem_steps > 2:
            return "Gemini - more efficient"
        elif gem_steps > ref_steps * 1.3:
            return "Reference - appropriate complexity"
        else:
            return "Unclear - need real-world testing"

class CorrectedDAGValidator:
    """Main validator for corrected DAG comparison"""
    
    def __init__(self):
        self.tool_generator = MockToolGenerator()
        self.available_tools = self._format_tools_for_gemini()
        self.dag_library = OptimizedDAGLibrary()
        self.dag_generator = GeminiDAGGenerator(self.available_tools)
        self.annotator = ManualAnnotator()
        
        logger.info(f"Initialized with {len(self.available_tools)} available tools")
        logger.info(f"Optimized DAGs: {self.dag_library.get_all_tasks()}")
    
    def _format_tools_for_gemini(self) -> List[Dict[str, Any]]:
        """Format tools for Gemini consumption"""
        all_tools = self.tool_generator.generate_all_tools()
        formatted_tools = []
        
        for tool in all_tools:
            formatted_tools.append({
                "name": tool.tool_id,
                "description": tool.description,
                "category": tool.category.value,
                "inputs": tool.input_types,
                "outputs": tool.output_types,
                "complexity": tool.complexity_score
            })
        
        return formatted_tools
    
    def validate_single_task(self, task_id: str) -> Optional[ComparisonResult]:
        """Validate Gemini's reverse-engineering for a single task"""
        
        task_pair = self.dag_library.get_task_pair(task_id)
        if not task_pair:
            logger.error(f"No task pair found for task: {task_id}")
            return None
        
        logger.info(f"Testing reverse-engineering for task: {task_id}")
        logger.info(f"Crafted prompt: '{task_pair.crafted_prompt[:100]}...'")
        
        # Generate Gemini DAG from crafted prompt
        gemini_dag = self.dag_generator.generate_dag_for_prompt(task_pair.crafted_prompt)
        
        # Manual annotation
        manual_analysis = self.annotator.annotate_comparison(task_pair, gemini_dag)
        
        # Calculate basic metrics
        metrics = self._calculate_basic_metrics(task_pair.optimized_dag, gemini_dag)
        
        comparison_id = hashlib.md5(f"{task_id}_{time.time()}".encode()).hexdigest()[:8]
        
        return ComparisonResult(
            task_id=task_id,
            crafted_prompt=task_pair.crafted_prompt,
            reference_dag=task_pair.optimized_dag,
            gemini_dag=gemini_dag,
            comparison_successful=manual_analysis["comparison_possible"],
            metrics=metrics,
            detailed_analysis=manual_analysis,
            manual_annotations=manual_analysis.get("annotations", {}),
            timestamp=time.time(),
            comparison_id=comparison_id
        )
    
    def _calculate_basic_metrics(self, ref_dag: Dict, gem_dag: Dict) -> Dict[str, float]:
        """Calculate basic comparison metrics"""
        
        if "error" in gem_dag:
            return {"success": 0.0}
        
        ref_tools = set(step["tool"] for step in ref_dag.get("steps", []))
        gem_tools = set(step["tool"] for step in gem_dag.get("steps", []))
        
        tool_overlap = len(ref_tools & gem_tools) / len(ref_tools | gem_tools) if ref_tools | gem_tools else 0
        
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        efficiency = min(ref_steps, gem_steps) / max(ref_steps, gem_steps) if max(ref_steps, gem_steps) > 0 else 0
        
        return {
            "success": 1.0,
            "tool_overlap": tool_overlap,
            "efficiency_similarity": efficiency,
            "step_count_ratio": gem_steps / ref_steps if ref_steps > 0 else 0
        }
    
    def validate_all_tasks(self) -> Dict[str, Any]:
        """Validate all task pairs"""
        
        logger.info("🔬 Starting Corrected DAG Validation")
        
        all_results = {}
        
        for task_id in self.dag_library.get_all_tasks():
            result = self.validate_single_task(task_id)
            if result:
                all_results[task_id] = result
                
                # Brief delay between tests
                time.sleep(3)
        
        return {
            "validation_summary": {
                "timestamp": time.time(),
                "total_tasks": len(self.dag_library.get_all_tasks()),
                "successful_comparisons": len(all_results),
                "framework_version": "corrected_dag_validation_1.0"
            },
            "task_results": all_results,
            "overall_analysis": self._analyze_overall_results(all_results)
        }
    
    def _analyze_overall_results(self, results: Dict[str, ComparisonResult]) -> Dict[str, Any]:
        """Analyze overall results"""
        
        if not results:
            return {"status": "No results to analyze"}
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r.comparison_successful)
        
        # Aggregate manual assessments
        winner_counts = {"gemini": 0, "reference": 0, "unclear": 0}
        
        for result in results.values():
            if result.comparison_successful:
                winner = result.manual_annotations.get("overall_assessment", {}).get("recommended_winner", "unclear")
                if "gemini" in winner.lower():
                    winner_counts["gemini"] += 1
                elif "reference" in winner.lower():
                    winner_counts["reference"] += 1
                else:
                    winner_counts["unclear"] += 1
        
        return {
            "total_comparisons": total_tests,
            "successful_comparisons": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "winner_distribution": winner_counts,
            "gemini_success_rate": winner_counts["gemini"] / successful_tests if successful_tests > 0 else 0,
            "key_insights": self._extract_key_insights(results)
        }
    
    def _extract_key_insights(self, results: Dict[str, ComparisonResult]) -> List[str]:
        """Extract key insights from manual annotations"""
        
        insights = []
        
        # Tool substitution patterns
        tool_upgrades = 0
        tool_downgrades = 0
        
        for result in results.values():
            if result.comparison_successful:
                substitutions = result.manual_annotations.get("tool_choice_analysis", {}).get("tool_substitutions", [])
                for sub in substitutions:
                    if "upgrade" in sub.get("assessment", "").lower():
                        tool_upgrades += 1
                    elif "downgrade" in sub.get("assessment", "").lower():
                        tool_downgrades += 1
        
        if tool_upgrades > tool_downgrades:
            insights.append(f"Gemini frequently chooses higher-quality tools ({tool_upgrades} upgrades vs {tool_downgrades} downgrades)")
        
        # Efficiency patterns
        more_efficient = sum(1 for r in results.values() if r.comparison_successful and 
                            r.manual_annotations.get("efficiency_analysis", {}).get("assessment", "") == "Gemini more efficient")
        
        if more_efficient > len(results) / 2:
            insights.append("Gemini consistently creates more efficient workflows")
        
        return insights
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save validation results"""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"corrected_dag_validation_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        # Convert ComparisonResult objects to dicts for JSON serialization
        serializable_results = {}
        for task_id, result in results.get("task_results", {}).items():
            if isinstance(result, ComparisonResult):
                serializable_results[task_id] = asdict(result)
            else:
                serializable_results[task_id] = result
        
        results["task_results"] = serializable_results
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {filepath}")
        return str(filepath)

def main():
    """Run corrected DAG validation"""
    
    # Verify API access
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("Missing GOOGLE_API_KEY in environment")
        return
    
    validator = CorrectedDAGValidator()
    
    try:
        results = validator.validate_all_tasks()
        
        # Save results
        results_file = validator.save_results(results)
        
        # Print summary
        print("\n" + "="*80)
        print("🔬 CORRECTED DAG VALIDATION COMPLETE")
        print("="*80)
        
        summary = results["validation_summary"]
        analysis = results["overall_analysis"]
        
        print(f"Total tasks tested: {summary['total_tasks']}")
        print(f"Successful comparisons: {summary['successful_comparisons']}")
        
        print(f"\n🏆 REVERSE-ENGINEERING ASSESSMENT:")
        if "winner_distribution" in analysis:
            winners = analysis["winner_distribution"]
            print(f"Gemini wins: {winners['gemini']}")
            print(f"Reference wins: {winners['reference']}")
            print(f"Unclear: {winners['unclear']}")
            print(f"Gemini success rate: {analysis['gemini_success_rate']:.1%}")
        
        print(f"\n🔍 KEY INSIGHTS:")
        for insight in analysis.get("key_insights", []):
            print(f"• {insight}")
        
        print(f"\n📄 Detailed results: {results_file}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise

if __name__ == "__main__":
    main()