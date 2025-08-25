#!/usr/bin/env python3
"""
Real Tool Call DAG Validation System

Tests Gemini's tool selection quality by comparing generated DAGs
against reference DAGs, with automated metrics and human-reviewable outputs.
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
class ReferenceDAG:
    """Reference tool call workflow for comparison"""
    task_id: str
    description: str
    dag: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {
                "complexity": self._calculate_complexity(),
                "tool_count": len(self.dag.get("steps", [])),
                "categories": self._extract_categories(),
                "dependencies": self._extract_dependencies()
            }
    
    def _calculate_complexity(self) -> str:
        steps = len(self.dag.get("steps", []))
        if steps <= 3:
            return "simple"
        elif steps <= 6:
            return "medium"
        else:
            return "complex"
    
    def _extract_categories(self) -> List[str]:
        categories = set()
        for step in self.dag.get("steps", []):
            tool_name = step.get("tool", "")
            if "load" in tool_name:
                categories.add("document_loading")
            elif "extract" in tool_name:
                categories.add("entity_extraction")
            elif "chunk" in tool_name:
                categories.add("text_processing")
            elif "build" in tool_name or "graph" in tool_name:
                categories.add("graph_operations")
            elif "export" in tool_name:
                categories.add("output_formatting")
        return list(categories)
    
    def _extract_dependencies(self) -> List[Tuple[str, str]]:
        dependencies = []
        for step in self.dag.get("steps", []):
            step_id = step.get("id", "")
            inputs = step.get("inputs", [])
            for input_ref in inputs:
                dependencies.append((input_ref, step_id))
        return dependencies

@dataclass
class DAGComparisonResult:
    """Results of comparing two DAGs"""
    query: str
    reference_dag_id: str
    gemini_dag: Dict[str, Any]
    comparison_successful: bool
    metrics: Dict[str, float]
    detailed_analysis: Dict[str, Any]
    timestamp: float
    comparison_id: str

class ReferenceDAGLibrary:
    """Library of reference DAGs for different tasks"""
    
    def __init__(self):
        self.reference_dags = self._create_reference_dags()
        self.test_queries = self._create_test_queries()
    
    def _create_reference_dags(self) -> Dict[str, ReferenceDAG]:
        """Create expert-designed reference DAGs"""
        
        return {
            "academic_paper_analysis": ReferenceDAG(
                task_id="academic_paper_analysis",
                description="Extract methodologies, datasets, and performance metrics from academic ML paper",
                dag={
                    "steps": [
                        {
                            "id": "load_doc",
                            "tool": "load_document_pdf",
                            "params": {"extract_metadata": True},
                            "inputs": [],
                            "outputs": ["document_ref"]
                        },
                        {
                            "id": "chunk_text", 
                            "tool": "chunk_text_semantic",
                            "params": {"chunk_size": 1000, "overlap": 100},
                            "inputs": ["document_ref"],
                            "outputs": ["chunks_ref"]
                        },
                        {
                            "id": "extract_methods",
                            "tool": "extract_entities_scientific",
                            "params": {"entity_types": ["METHOD", "ALGORITHM"]},
                            "inputs": ["chunks_ref"],
                            "outputs": ["methods_ref"]
                        },
                        {
                            "id": "extract_datasets",
                            "tool": "extract_entities_scientific", 
                            "params": {"entity_types": ["DATASET", "CORPUS"]},
                            "inputs": ["chunks_ref"],
                            "outputs": ["datasets_ref"]
                        },
                        {
                            "id": "extract_metrics",
                            "tool": "extract_performance_metrics",
                            "params": {"metric_types": ["ACCURACY", "F1", "PRECISION"]},
                            "inputs": ["chunks_ref"],
                            "outputs": ["metrics_ref"]
                        },
                        {
                            "id": "link_method_performance",
                            "tool": "extract_relationships_llm",
                            "params": {"relationship_types": ["ACHIEVES", "PERFORMS"]},
                            "inputs": ["methods_ref", "metrics_ref"],
                            "outputs": ["relationships_ref"]
                        },
                        {
                            "id": "build_graph",
                            "tool": "build_knowledge_graph",
                            "params": {"include_metadata": True},
                            "inputs": ["methods_ref", "datasets_ref", "metrics_ref", "relationships_ref"],
                            "outputs": ["graph_ref"]
                        }
                    ],
                    "flow": [
                        "load_doc -> chunk_text",
                        "chunk_text -> extract_methods",
                        "chunk_text -> extract_datasets", 
                        "chunk_text -> extract_metrics",
                        "extract_methods + extract_metrics -> link_method_performance",
                        "extract_methods + extract_datasets + extract_metrics + link_method_performance -> build_graph"
                    ]
                },
                metadata={}
            ),
            
            "simple_document_processing": ReferenceDAG(
                task_id="simple_document_processing",
                description="Extract key entities and create basic summary from business document",
                dag={
                    "steps": [
                        {
                            "id": "load_doc",
                            "tool": "load_document_pdf", 
                            "params": {},
                            "inputs": [],
                            "outputs": ["document_ref"]
                        },
                        {
                            "id": "extract_entities",
                            "tool": "extract_entities_basic",
                            "params": {"entity_types": ["PERSON", "ORG", "DATE", "MONEY"]},
                            "inputs": ["document_ref"],
                            "outputs": ["entities_ref"]
                        },
                        {
                            "id": "create_summary",
                            "tool": "summarize_extractive",
                            "params": {"max_sentences": 5},
                            "inputs": ["document_ref"],
                            "outputs": ["summary_ref"]
                        },
                        {
                            "id": "export_results",
                            "tool": "export_json",
                            "params": {"include_metadata": True},
                            "inputs": ["entities_ref", "summary_ref"],
                            "outputs": ["results_ref"]
                        }
                    ],
                    "flow": [
                        "load_doc -> extract_entities",
                        "load_doc -> create_summary",
                        "extract_entities + create_summary -> export_results"
                    ]
                },
                metadata={}
            ),
            
            "business_report_analysis": ReferenceDAG(
                task_id="business_report_analysis",
                description="Analyze financial report for key metrics, trends, and insights",
                dag={
                    "steps": [
                        {
                            "id": "load_doc",
                            "tool": "load_document_pdf",
                            "params": {"preserve_tables": True},
                            "inputs": [],
                            "outputs": ["document_ref"]
                        },
                        {
                            "id": "extract_financials",
                            "tool": "extract_entities_financial",
                            "params": {"entity_types": ["REVENUE", "PROFIT", "EXPENSE"]},
                            "inputs": ["document_ref"],
                            "outputs": ["financials_ref"]
                        },
                        {
                            "id": "extract_dates",
                            "tool": "extract_entities_temporal",
                            "params": {"date_formats": ["Q1", "Q2", "Q3", "Q4", "YYYY"]},
                            "inputs": ["document_ref"],
                            "outputs": ["dates_ref"]
                        },
                        {
                            "id": "analyze_trends",
                            "tool": "analyze_financial_trends",
                            "params": {"trend_types": ["GROWTH", "DECLINE", "SEASONAL"]},
                            "inputs": ["financials_ref", "dates_ref"],
                            "outputs": ["trends_ref"]
                        },
                        {
                            "id": "create_dashboard",
                            "tool": "create_financial_dashboard",
                            "params": {"chart_types": ["line", "bar", "pie"]},
                            "inputs": ["financials_ref", "trends_ref"],
                            "outputs": ["dashboard_ref"]
                        }
                    ],
                    "flow": [
                        "load_doc -> extract_financials",
                        "load_doc -> extract_dates",
                        "extract_financials + extract_dates -> analyze_trends",
                        "extract_financials + analyze_trends -> create_dashboard"
                    ]
                },
                metadata={}
            )
        }
    
    def _create_test_queries(self) -> Dict[str, List[str]]:
        """Create natural language queries for each reference DAG"""
        
        return {
            "academic_paper_analysis": [
                "Analyze this machine learning research paper to extract the methodologies used, datasets tested, and performance results achieved",
                "Extract all the ML methods, datasets, and accuracy scores from this academic paper and show their relationships",
                "Process this research paper to identify algorithms, training data, and experimental results, then create a knowledge graph"
            ],
            "simple_document_processing": [
                "Extract the key information and create a summary from this business document", 
                "Process this document to find important entities and generate a brief summary",
                "Get the main entities and summarize this document in JSON format"
            ],
            "business_report_analysis": [
                "Analyze this financial report to extract revenue, profit, and expense data and identify trends",
                "Process this quarterly report to find key financial metrics and create a dashboard showing trends",
                "Extract financial data from this business report and analyze growth patterns over time"
            ]
        }
    
    def get_reference_dag(self, task_id: str) -> Optional[ReferenceDAG]:
        """Get reference DAG by task ID"""
        return self.reference_dags.get(task_id)
    
    def get_test_queries(self, task_id: str) -> List[str]:
        """Get test queries for a task"""
        return self.test_queries.get(task_id, [])
    
    def get_all_tasks(self) -> List[str]:
        """Get all available task IDs"""
        return list(self.reference_dags.keys())

class GeminiDAGGenerator:
    """Generate tool call DAGs using Gemini"""
    
    def __init__(self, available_tools: List[Dict]):
        self.available_tools = available_tools
    
    def generate_dag_for_query(self, query: str) -> Dict[str, Any]:
        """Generate tool call DAG for natural language query"""
        
        prompt = f"""
Generate a tool call workflow (DAG) for this task: "{query}"

Available tools:
{json.dumps(self.available_tools[:50], indent=2)}  # Limit to first 50 tools for readability

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
    "rationale": "detailed explanation of workflow design choices"
}}

Design an efficient, logical workflow that accomplishes the task completely.
Use only tools from the provided list.
Ensure inputs/outputs form a valid dependency chain.
        """
        
        try:
            response = litellm.completion(
                model="gemini/gemini-2.5-flash",
                messages=[{"role": "user", "content": prompt}],
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

class DAGComparator:
    """Compare DAGs using automated metrics"""
    
    def compare_dags(self, reference_dag: ReferenceDAG, gemini_dag: Dict[str, Any]) -> DAGComparisonResult:
        """Compare reference DAG against Gemini-generated DAG"""
        
        if "error" in gemini_dag:
            return DAGComparisonResult(
                query="",
                reference_dag_id=reference_dag.task_id,
                gemini_dag=gemini_dag,
                comparison_successful=False,
                metrics={"overall_score": 0.0},
                detailed_analysis={"error": gemini_dag["error"]},
                timestamp=time.time(),
                comparison_id=self._generate_comparison_id()
            )
        
        metrics = {
            "structural_similarity": self._structural_similarity(reference_dag.dag, gemini_dag),
            "tool_overlap": self._tool_overlap(reference_dag.dag, gemini_dag),
            "workflow_efficiency": self._workflow_efficiency(reference_dag.dag, gemini_dag),
            "dependency_correctness": self._dependency_correctness(reference_dag.dag, gemini_dag),
            "parameter_appropriateness": self._parameter_appropriateness(reference_dag.dag, gemini_dag),
            "output_completeness": self._output_completeness(reference_dag.dag, gemini_dag)
        }
        
        metrics["overall_score"] = sum(metrics.values()) / len(metrics)
        
        detailed_analysis = self._detailed_analysis(reference_dag.dag, gemini_dag)
        
        return DAGComparisonResult(
            query="",
            reference_dag_id=reference_dag.task_id,
            gemini_dag=gemini_dag,
            comparison_successful=True,
            metrics=metrics,
            detailed_analysis=detailed_analysis,
            timestamp=time.time(),
            comparison_id=self._generate_comparison_id()
        )
    
    def _generate_comparison_id(self) -> str:
        """Generate unique comparison ID"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    
    def _structural_similarity(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Compare DAG structure (steps, dependencies)"""
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        if ref_steps == 0 and gem_steps == 0:
            return 1.0
        
        # Penalize major differences in step count
        step_ratio = min(ref_steps, gem_steps) / max(ref_steps, gem_steps)
        
        # Compare flow structure
        ref_flow = set(ref_dag.get("flow", []))
        gem_flow = set(gem_dag.get("flow", []))
        
        if not ref_flow and not gem_flow:
            flow_similarity = 1.0
        elif not ref_flow or not gem_flow:
            flow_similarity = 0.0
        else:
            flow_overlap = len(ref_flow & gem_flow)
            flow_union = len(ref_flow | gem_flow)
            flow_similarity = flow_overlap / flow_union if flow_union > 0 else 0.0
        
        return (step_ratio * 0.6) + (flow_similarity * 0.4)
    
    def _tool_overlap(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Compare tools used in each DAG"""
        ref_tools = set(step["tool"] for step in ref_dag.get("steps", []))
        gem_tools = set(step["tool"] for step in gem_dag.get("steps", []))
        
        if not ref_tools and not gem_tools:
            return 1.0
        
        if not ref_tools or not gem_tools:
            return 0.0
        
        overlap = len(ref_tools & gem_tools)
        union = len(ref_tools | gem_tools)
        
        return overlap / union if union > 0 else 0.0
    
    def _workflow_efficiency(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Compare workflow efficiency (fewer steps = better if same outcome)"""
        ref_steps = len(ref_dag.get("steps", []))
        gem_steps = len(gem_dag.get("steps", []))
        
        if ref_steps == 0 and gem_steps == 0:
            return 1.0
        
        if gem_steps <= ref_steps:
            return 1.0  # Gemini is more efficient or equal
        else:
            return ref_steps / gem_steps  # Penalize extra steps
    
    def _dependency_correctness(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Check if dependencies make logical sense"""
        gem_steps = gem_dag.get("steps", [])
        
        all_outputs = set()
        dependency_errors = 0
        total_dependencies = 0
        
        for step in gem_steps:
            # Check inputs exist
            inputs = step.get("inputs", [])
            total_dependencies += len(inputs)
            
            for input_ref in inputs:
                if input_ref not in all_outputs:
                    dependency_errors += 1
            
            # Add outputs
            outputs = step.get("outputs", [])
            all_outputs.update(outputs)
        
        if total_dependencies == 0:
            return 1.0
        
        return max(0.0, 1.0 - (dependency_errors / total_dependencies))
    
    def _parameter_appropriateness(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Compare parameter usage"""
        gem_steps = gem_dag.get("steps", [])
        
        param_score = 0
        total_steps = len(gem_steps)
        
        if total_steps == 0:
            return 1.0
        
        for step in gem_steps:
            params = step.get("params", {})
            tool_name = step.get("tool", "")
            
            # Basic check: does step have reasonable parameters?
            if params:  # Has parameters
                param_score += 1
            elif "extract" in tool_name.lower() or "analyze" in tool_name.lower():
                # Tools that typically need parameters but don't have them
                param_score += 0.5
            else:  # Tools that might not need parameters
                param_score += 1
        
        return param_score / total_steps
    
    def _output_completeness(self, ref_dag: Dict, gem_dag: Dict) -> float:
        """Check if final outputs cover required information"""
        ref_final_outputs = set()
        gem_final_outputs = set()
        
        ref_steps = ref_dag.get("steps", [])
        gem_steps = gem_dag.get("steps", [])
        
        # Get all outputs
        for step in ref_steps:
            ref_final_outputs.update(step.get("outputs", []))
        
        for step in gem_steps:
            gem_final_outputs.update(step.get("outputs", []))
        
        if not ref_final_outputs and not gem_final_outputs:
            return 1.0
        
        if not ref_final_outputs or not gem_final_outputs:
            return 0.0
        
        # Simple semantic matching
        semantic_matches = 0
        for ref_output in ref_final_outputs:
            for gem_output in gem_final_outputs:
                if self._semantic_match(ref_output, gem_output):
                    semantic_matches += 1
                    break
        
        return semantic_matches / len(ref_final_outputs) if ref_final_outputs else 0.0
    
    def _semantic_match(self, ref_output: str, gem_output: str) -> bool:
        """Simple semantic matching of output references"""
        ref_words = set(ref_output.lower().split('_'))
        gem_words = set(gem_output.lower().split('_'))
        
        overlap = len(ref_words & gem_words)
        return overlap > 0
    
    def _detailed_analysis(self, ref_dag: Dict, gem_dag: Dict) -> Dict[str, Any]:
        """Provide detailed analysis for human review"""
        return {
            "tool_comparison": {
                "reference_tools": [step["tool"] for step in ref_dag.get("steps", [])],
                "gemini_tools": [step["tool"] for step in gem_dag.get("steps", [])],
                "tools_only_in_reference": list(set(step["tool"] for step in ref_dag.get("steps", [])) - 
                                               set(step["tool"] for step in gem_dag.get("steps", []))),
                "tools_only_in_gemini": list(set(step["tool"] for step in gem_dag.get("steps", [])) - 
                                           set(step["tool"] for step in ref_dag.get("steps", [])))
            },
            "workflow_comparison": {
                "reference_step_count": len(ref_dag.get("steps", [])),
                "gemini_step_count": len(gem_dag.get("steps", [])),
                "reference_flow": ref_dag.get("flow", []),
                "gemini_flow": gem_dag.get("flow", [])
            },
            "gemini_rationale": gem_dag.get("rationale", "No rationale provided")
        }

class ReviewableReportGenerator:
    """Generate human-reviewable comparison reports"""
    
    def generate_comparison_report(self, query: str, reference_dag: ReferenceDAG, 
                                 comparison_result: DAGComparisonResult) -> Dict[str, Any]:
        """Generate human-reviewable comparison report"""
        
        return {
            "test_case": {
                "query": query,
                "task_id": reference_dag.task_id,
                "timestamp": comparison_result.timestamp,
                "comparison_id": comparison_result.comparison_id
            },
            "automated_metrics": {
                "overall_score": comparison_result.metrics.get("overall_score", 0.0),
                "individual_scores": comparison_result.metrics,
                "interpretation": self._interpret_scores(comparison_result.metrics)
            },
            "side_by_side_comparison": {
                "reference_workflow": {
                    "description": reference_dag.description,
                    "steps": reference_dag.dag["steps"],
                    "flow": reference_dag.dag["flow"],
                    "tool_count": len(reference_dag.dag["steps"]),
                    "complexity": reference_dag.metadata["complexity"]
                },
                "gemini_workflow": {
                    "steps": comparison_result.gemini_dag.get("steps", []),
                    "flow": comparison_result.gemini_dag.get("flow", []),
                    "tool_count": len(comparison_result.gemini_dag.get("steps", [])),
                    "rationale": comparison_result.gemini_dag.get("rationale", "No rationale provided")
                }
            },
            "key_differences": comparison_result.detailed_analysis,
            "human_review_questions": [
                "Is Gemini's workflow logically sound?",
                "Does Gemini's approach achieve the same goal more efficiently?",
                "Are there critical steps missing in Gemini's workflow?",
                "Are Gemini's tool choices appropriate for the task?",
                "Overall, which workflow would you prefer and why?"
            ],
            "review_template": {
                "overall_preference": "[reference/gemini/neither] - Fill in your preference",
                "reasoning": "[Explain your reasoning here]",
                "score_agreement": "[agree/disagree with automated scores] - Do you agree with the automated assessment?",
                "gemini_strengths": "[What did Gemini do well?]",
                "gemini_weaknesses": "[What could Gemini improve?]",
                "notes": "[Additional observations]"
            }
        }
    
    def _interpret_scores(self, metrics: Dict[str, float]) -> Dict[str, str]:
        """Interpret automated scores for human consumption"""
        
        interpretations = {}
        
        for metric_name, score in metrics.items():
            if score >= 0.8:
                interpretations[metric_name] = "Excellent"
            elif score >= 0.6:
                interpretations[metric_name] = "Good"
            elif score >= 0.4:
                interpretations[metric_name] = "Fair"
            elif score >= 0.2:
                interpretations[metric_name] = "Poor"
            else:
                interpretations[metric_name] = "Very Poor"
        
        return interpretations

class DAGValidationSystem:
    """Main system for validating tool call DAGs"""
    
    def __init__(self):
        self.tool_generator = MockToolGenerator()
        self.available_tools = self._format_tools_for_gemini()
        self.dag_library = ReferenceDAGLibrary()
        self.dag_generator = GeminiDAGGenerator(self.available_tools)
        self.comparator = DAGComparator()
        self.report_generator = ReviewableReportGenerator()
        
        logger.info(f"Initialized with {len(self.available_tools)} available tools")
        logger.info(f"Reference DAGs: {self.dag_library.get_all_tasks()}")
    
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
    
    def validate_single_query(self, query: str, task_id: str) -> Optional[Dict[str, Any]]:
        """Validate Gemini's DAG generation for a single query"""
        
        reference_dag = self.dag_library.get_reference_dag(task_id)
        if not reference_dag:
            logger.error(f"No reference DAG found for task: {task_id}")
            return None
        
        logger.info(f"Generating DAG for query: '{query[:50]}...'")
        
        # Generate Gemini DAG
        gemini_dag = self.dag_generator.generate_dag_for_query(query)
        
        # Compare DAGs
        comparison_result = self.comparator.compare_dags(reference_dag, gemini_dag)
        comparison_result.query = query
        
        # Generate human-reviewable report
        report = self.report_generator.generate_comparison_report(
            query, reference_dag, comparison_result
        )
        
        return report
    
    def validate_all_tasks(self) -> Dict[str, Any]:
        """Validate Gemini across all reference tasks and queries"""
        
        logger.info("🔬 Starting Comprehensive DAG Validation")
        
        all_results = {}
        aggregate_metrics = {
            "total_tests": 0,
            "successful_generations": 0,
            "overall_scores": [],
            "metric_averages": {},
            "task_performance": {}
        }
        
        for task_id in self.dag_library.get_all_tasks():
            logger.info(f"Testing task: {task_id}")
            
            task_queries = self.dag_library.get_test_queries(task_id)
            task_results = []
            
            for i, query in enumerate(task_queries):
                logger.info(f"  Query {i+1}/{len(task_queries)}: {query[:50]}...")
                
                result = self.validate_single_query(query, task_id)
                if result:
                    task_results.append(result)
                    
                    # Update aggregate metrics
                    aggregate_metrics["total_tests"] += 1
                    
                    if result["automated_metrics"]["overall_score"] > 0:
                        aggregate_metrics["successful_generations"] += 1
                        aggregate_metrics["overall_scores"].append(
                            result["automated_metrics"]["overall_score"]
                        )
                
                # Small delay to avoid rate limits
                time.sleep(2)
            
            all_results[task_id] = {
                "task_description": self.dag_library.get_reference_dag(task_id).description,
                "query_results": task_results,
                "task_summary": self._summarize_task_results(task_results)
            }
        
        # Calculate aggregate statistics
        if aggregate_metrics["overall_scores"]:
            aggregate_metrics["average_overall_score"] = sum(aggregate_metrics["overall_scores"]) / len(aggregate_metrics["overall_scores"])
            aggregate_metrics["success_rate"] = aggregate_metrics["successful_generations"] / aggregate_metrics["total_tests"]
            
            # Calculate metric averages
            all_individual_metrics = {}
            for task_results in all_results.values():
                for query_result in task_results["query_results"]:
                    individual_scores = query_result["automated_metrics"]["individual_scores"]
                    for metric_name, score in individual_scores.items():
                        if metric_name not in all_individual_metrics:
                            all_individual_metrics[metric_name] = []
                        all_individual_metrics[metric_name].append(score)
            
            for metric_name, scores in all_individual_metrics.items():
                aggregate_metrics["metric_averages"][metric_name] = sum(scores) / len(scores)
        
        final_results = {
            "validation_summary": {
                "timestamp": time.time(),
                "total_tasks": len(self.dag_library.get_all_tasks()),
                "total_queries": aggregate_metrics["total_tests"],
                "framework_version": "1.0_dag_validation"
            },
            "aggregate_metrics": aggregate_metrics,
            "task_results": all_results,
            "overall_assessment": self._generate_overall_assessment(aggregate_metrics),
            "human_review_summary": self._generate_human_review_summary(all_results)
        }
        
        return final_results
    
    def _summarize_task_results(self, task_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize results for a single task"""
        
        if not task_results:
            return {"summary": "No successful results"}
        
        overall_scores = [r["automated_metrics"]["overall_score"] for r in task_results]
        
        return {
            "queries_tested": len(task_results),
            "average_score": sum(overall_scores) / len(overall_scores),
            "best_score": max(overall_scores),
            "worst_score": min(overall_scores),
            "consistency": max(overall_scores) - min(overall_scores)  # Lower is more consistent
        }
    
    def _generate_overall_assessment(self, aggregate_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment of Gemini's performance"""
        
        if not aggregate_metrics.get("overall_scores"):
            return {"assessment": "No valid results to assess"}
        
        avg_score = aggregate_metrics.get("average_overall_score", 0)
        success_rate = aggregate_metrics.get("success_rate", 0)
        
        if avg_score >= 0.8 and success_rate >= 0.9:
            assessment = "Excellent - Gemini consistently generates high-quality DAGs"
        elif avg_score >= 0.6 and success_rate >= 0.8:
            assessment = "Good - Gemini generates generally appropriate DAGs with some room for improvement"
        elif avg_score >= 0.4 and success_rate >= 0.6:
            assessment = "Fair - Gemini shows mixed performance, significant improvements needed"
        else:
            assessment = "Poor - Gemini struggles with DAG generation, manual review recommended"
        
        return {
            "assessment": assessment,
            "confidence": "high" if success_rate >= 0.8 else "medium" if success_rate >= 0.6 else "low",
            "recommendations": self._generate_recommendations(avg_score, success_rate)
        }
    
    def _generate_recommendations(self, avg_score: float, success_rate: float) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if avg_score >= 0.7:
            recommendations.append("Gemini DAG generation suitable for production with monitoring")
        elif avg_score >= 0.5:
            recommendations.append("Gemini DAG generation viable for development/testing with human review")
        else:
            recommendations.append("Alternative DAG generation methods recommended")
        
        if success_rate < 0.8:
            recommendations.append("Improve error handling for DAG generation failures")
        
        recommendations.append("Use human review template for validation of critical workflows")
        recommendations.append("Consider fine-tuning prompts based on identified weaknesses")
        
        return recommendations
    
    def _generate_human_review_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary for human reviewers"""
        
        return {
            "review_instructions": [
                "Each test case includes side-by-side DAG comparison",
                "Focus on workflow logic and tool appropriateness",
                "Use provided review template for consistent evaluation",
                "Pay attention to Gemini's rationale for its choices"
            ],
            "key_areas_to_evaluate": [
                "Logical flow of operations",
                "Completeness of task coverage", 
                "Efficiency of tool selection",
                "Appropriateness of parameters",
                "Quality of dependency management"
            ],
            "total_cases_for_review": sum(
                len(task_data["query_results"]) 
                for task_data in all_results.values()
            )
        }
    
    def save_validation_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save validation results to file"""
        
        if not filename:
            timestamp = int(time.time())
            filename = f"dag_validation_results_{timestamp}.json"
        
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Validation results saved to: {filepath}")
        return str(filepath)

def main():
    """Run DAG validation system"""
    
    # Verify API access
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("Missing GOOGLE_API_KEY in environment")
        return
    
    # Initialize validation system
    validator = DAGValidationSystem()
    
    try:
        # Run comprehensive validation
        results = validator.validate_all_tasks()
        
        # Save results
        results_file = validator.save_validation_results(results)
        
        # Print summary
        print("\n" + "="*70)
        print("🔬 DAG VALIDATION SYSTEM COMPLETE")
        print("="*70)
        
        summary = results["validation_summary"]
        aggregate = results["aggregate_metrics"]
        assessment = results["overall_assessment"]
        
        print(f"Tasks tested: {summary['total_tasks']}")
        print(f"Queries tested: {summary['total_queries']}")
        
        if aggregate.get("average_overall_score") is not None:
            print(f"\n📊 PERFORMANCE METRICS:")
            print(f"Average overall score: {aggregate['average_overall_score']:.2f}")
            print(f"Success rate: {aggregate['success_rate']:.1%}")
            print(f"Successful generations: {aggregate['successful_generations']}/{aggregate['total_tests']}")
            
            print(f"\n🎯 ASSESSMENT:")
            print(f"{assessment['assessment']}")
            print(f"Confidence: {assessment['confidence']}")
            
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in assessment["recommendations"]:
                print(f"• {rec}")
        else:
            print("\n❌ No valid results generated")
        
        print(f"\n📄 Detailed results: {results_file}")
        print(f"👥 Cases for human review: {results['human_review_summary']['total_cases_for_review']}")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise

if __name__ == "__main__":
    main()