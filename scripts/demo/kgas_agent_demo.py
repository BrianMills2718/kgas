#!/usr/bin/env python3
"""
KGAS Agent Architecture Demonstration

This demonstrates how KGAS should work as an autonomous analysis system:
1. User provides natural language request
2. Research agent analyzes request and generates workflow
3. Execution agent runs workflow using KGAS MCP tools
4. Results are interpreted and presented

This shows the intended Layer 1 (Agent-Controlled) interface.
"""

import os
import sys
import json
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configuration
DEMO_OUTPUT_DIR = Path("kgas_agent_demo_results")
DEMO_OUTPUT_DIR.mkdir(exist_ok=True)

@dataclass
class ResearchRequest:
    """User's natural language research request"""
    query: str
    documents: List[str]
    context: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class WorkflowSpecification:
    """Generated workflow specification"""
    name: str
    description: str
    phases: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    yaml_content: str
    explanation: str

@dataclass
class ExecutionResult:
    """Results from workflow execution"""
    execution_id: str
    status: str
    results: Dict[str, Any]
    outputs: Dict[str, Any]
    execution_time: float
    provenance: List[Dict[str, Any]]

@dataclass
class ResearchResponse:
    """Complete response to user's research request"""
    original_request: str
    refined_query: str
    methodology_explanation: str
    results: ExecutionResult
    interpretation: str
    visualizations: List[str]
    follow_up_suggestions: List[str]


class ResearchInteractionAgent:
    """
    Primary agent that handles user interaction and research guidance.
    This is the conversational layer that understands research intent.
    """
    
    def __init__(self):
        self.agent_id = "research_interaction_agent"
        self.conversation_history = []
        
    async def handle_research_request(self, request: ResearchRequest) -> ResearchResponse:
        """Handle complete research request from natural language to results"""
        
        print(f"\n{'='*80}")
        print("🧑‍🎓 RESEARCH INTERACTION AGENT")
        print(f"{'='*80}")
        print(f"📝 Request: {request.query}")
        print(f"📄 Documents: {len(request.documents)} files")
        
        # Step 1: Analyze research intent
        print("\n🔍 Analyzing research intent...")
        intent = await self._analyze_research_intent(request)
        
        # Step 2: Refine research question if needed
        print("🎯 Refining research question...")
        refined_query = await self._refine_research_question(request, intent)
        
        # Step 3: Generate workflow specification
        print("🏗️  Generating workflow specification...")
        workflow_spec = await self._generate_workflow_specification(refined_query, request.documents, intent)
        
        # Step 4: Delegate to execution agent
        print("\n🤖 Delegating to Workflow Execution Agent...")
        execution_agent = WorkflowExecutionAgent()
        execution_results = await execution_agent.execute_workflow(workflow_spec)
        
        # Step 5: Interpret results
        print("\n📊 Interpreting results...")
        interpretation = await self._interpret_results(execution_results, intent, request)
        
        # Step 6: Generate visualizations
        print("📈 Generating visualizations...")
        visualizations = await self._generate_visualizations(execution_results)
        
        # Step 7: Suggest follow-ups
        follow_ups = await self._suggest_follow_ups(interpretation, execution_results)
        
        response = ResearchResponse(
            original_request=request.query,
            refined_query=refined_query,
            methodology_explanation=workflow_spec.explanation,
            results=execution_results,
            interpretation=interpretation,
            visualizations=visualizations,
            follow_up_suggestions=follow_ups
        )
        
        # Save response
        self._save_research_response(response)
        
        return response
    
    async def _analyze_research_intent(self, request: ResearchRequest) -> Dict[str, Any]:
        """Analyze the user's research intent"""
        
        # In real implementation, this would use LLM to analyze intent
        # For demo, we'll simulate the analysis
        
        if "conspiracy" in request.query.lower() or "psychological factors" in request.query.lower():
            intent_type = "theory_application"
            domain = "psychology"
            methodology = "theory-guided content analysis"
        elif "extract" in request.query.lower() and "theory" in request.query.lower():
            intent_type = "theory_extraction"
            domain = "academic"
            methodology = "meta-schema extraction"
        else:
            intent_type = "exploratory_analysis"
            domain = "general"
            methodology = "open-ended exploration"
        
        return {
            "intent_type": intent_type,
            "domain": domain,
            "methodology": methodology,
            "complexity": "moderate",
            "required_tools": self._determine_required_tools(intent_type)
        }
    
    def _determine_required_tools(self, intent_type: str) -> List[str]:
        """Determine which KGAS tools are needed"""
        
        tool_sets = {
            "theory_extraction": [
                "T01_pdf_loader",
                "T15A_text_chunker",
                "meta_schema_extractor",
                "theory_schema_generator"
            ],
            "theory_application": [
                "T01_pdf_loader",
                "T15A_text_chunker",
                "T23A_entity_extractor",
                "theory_applicator",
                "T31_entity_builder",
                "T34_edge_builder",
                "T49_query_engine"
            ],
            "exploratory_analysis": [
                "T01_pdf_loader",
                "T15A_text_chunker",
                "T23A_entity_extractor",
                "T27_relationship_extractor",
                "T31_entity_builder",
                "T34_edge_builder",
                "T68_pagerank",
                "T49_query_engine"
            ]
        }
        
        return tool_sets.get(intent_type, tool_sets["exploratory_analysis"])
    
    async def _refine_research_question(self, request: ResearchRequest, intent: Dict[str, Any]) -> str:
        """Refine the research question for clarity and specificity"""
        
        # In real implementation, this would use LLM to refine
        # For demo, we'll add specificity
        
        if intent["intent_type"] == "theory_application":
            return f"Apply psychological conspiracy theory model from {request.documents[0]} to analyze {request.documents[1]} for conspiracy-related factors and risk assessment"
        elif intent["intent_type"] == "theory_extraction":
            return f"Extract theoretical framework from {request.documents[0]} using meta-schema v10 approach, focusing on key constructs and relationships"
        else:
            return request.query
    
    async def _generate_workflow_specification(self, refined_query: str, documents: List[str], intent: Dict[str, Any]) -> WorkflowSpecification:
        """Generate YAML workflow specification"""
        
        # Create workflow based on intent
        if intent["intent_type"] == "theory_application":
            workflow = self._create_theory_application_workflow(documents, intent)
        elif intent["intent_type"] == "theory_extraction":
            workflow = self._create_theory_extraction_workflow(documents, intent)
        else:
            workflow = self._create_exploratory_workflow(documents, intent)
        
        # Convert to YAML
        yaml_content = yaml.dump(workflow, default_flow_style=False)
        
        # Generate explanation
        explanation = f"""
This workflow will:
1. Load and process {len(documents)} documents using KGAS MCP tools
2. Apply {intent['methodology']} methodology
3. Use tools: {', '.join(intent['required_tools'][:3])}...
4. Generate structured outputs with full provenance
5. Provide results suitable for {intent['domain']} research
"""
        
        return WorkflowSpecification(
            name=workflow["name"],
            description=workflow["description"],
            phases=workflow["phases"],
            outputs=workflow["outputs"],
            yaml_content=yaml_content,
            explanation=explanation.strip()
        )
    
    def _create_theory_application_workflow(self, documents: List[str], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow for applying theory to text"""
        
        return {
            "name": "Theory Application Analysis",
            "description": "Apply extracted theory to analyze text for psychological factors",
            "version": "1.0",
            "phases": [
                {
                    "name": "document_loading",
                    "description": "Load source documents",
                    "tools": [
                        {
                            "tool": "T01_pdf_loader",
                            "inputs": {
                                "file_path": documents[0],
                                "output_format": "text"
                            }
                        },
                        {
                            "tool": "T01_pdf_loader",
                            "inputs": {
                                "file_path": documents[1],
                                "output_format": "text"
                            }
                        }
                    ]
                },
                {
                    "name": "theory_extraction",
                    "description": "Extract theory from academic paper",
                    "tools": [
                        {
                            "tool": "T15A_text_chunker",
                            "inputs": {
                                "text": "{{phase1.document_loading.outputs[0].text}}",
                                "chunk_size": 2000,
                                "overlap": 200
                            }
                        },
                        {
                            "tool": "meta_schema_extractor",
                            "inputs": {
                                "chunks": "{{phase2.theory_extraction.outputs[0].chunks}}",
                                "extraction_mode": "psychological_theory"
                            }
                        }
                    ]
                },
                {
                    "name": "text_analysis",
                    "description": "Analyze target text using theory",
                    "tools": [
                        {
                            "tool": "T15A_text_chunker",
                            "inputs": {
                                "text": "{{phase1.document_loading.outputs[1].text}}",
                                "chunk_size": 1000,
                                "overlap": 100
                            }
                        },
                        {
                            "tool": "theory_applicator",
                            "inputs": {
                                "theory_schema": "{{phase2.theory_extraction.outputs[1].schema}}",
                                "text_chunks": "{{phase3.text_analysis.outputs[0].chunks}}"
                            }
                        }
                    ]
                },
                {
                    "name": "graph_construction",
                    "description": "Build knowledge graph from analysis",
                    "tools": [
                        {
                            "tool": "T31_entity_builder",
                            "inputs": {
                                "entities": "{{phase3.text_analysis.outputs[1].detected_factors}}"
                            }
                        },
                        {
                            "tool": "T34_edge_builder",
                            "inputs": {
                                "relationships": "{{phase3.text_analysis.outputs[1].relationships}}"
                            }
                        }
                    ]
                },
                {
                    "name": "analysis",
                    "description": "Analyze graph and generate insights",
                    "tools": [
                        {
                            "tool": "T68_pagerank",
                            "inputs": {
                                "damping_factor": 0.85,
                                "iterations": 100
                            }
                        },
                        {
                            "tool": "T49_query_engine",
                            "inputs": {
                                "queries": [
                                    "What are the main psychological factors?",
                                    "What is the overall risk assessment?",
                                    "What are the protective factors?"
                                ]
                            }
                        }
                    ]
                }
            ],
            "outputs": [
                {
                    "name": "theory_schema",
                    "format": "json",
                    "include_provenance": True
                },
                {
                    "name": "analysis_results",
                    "format": "json",
                    "include_provenance": True
                },
                {
                    "name": "risk_assessment",
                    "format": "json",
                    "include_provenance": True
                },
                {
                    "name": "knowledge_graph",
                    "format": "graphml",
                    "include_provenance": True
                }
            ]
        }
    
    def _create_theory_extraction_workflow(self, documents: List[str], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow for extracting theory from academic paper"""
        
        return {
            "name": "Theory Extraction Workflow",
            "description": "Extract theoretical framework using meta-schema v10",
            "version": "1.0",
            "phases": [
                {
                    "name": "document_processing",
                    "tools": [
                        {
                            "tool": "T01_pdf_loader",
                            "inputs": {"file_path": documents[0]}
                        },
                        {
                            "tool": "T15A_text_chunker",
                            "inputs": {"chunk_size": 2000, "overlap": 200}
                        }
                    ]
                },
                {
                    "name": "vocabulary_extraction",
                    "tools": [
                        {
                            "tool": "meta_schema_phase1",
                            "inputs": {"mode": "comprehensive_vocabulary"}
                        }
                    ]
                },
                {
                    "name": "classification",
                    "tools": [
                        {
                            "tool": "meta_schema_phase2",
                            "inputs": {"vocabulary": "{{phase2.outputs.vocabulary}}"}
                        }
                    ]
                },
                {
                    "name": "schema_generation",
                    "tools": [
                        {
                            "tool": "meta_schema_phase3",
                            "inputs": {"classification": "{{phase3.outputs}}"}
                        }
                    ]
                }
            ],
            "outputs": [
                {
                    "name": "theory_schema",
                    "format": "yaml",
                    "include_provenance": True
                }
            ]
        }
    
    def _create_exploratory_workflow(self, documents: List[str], intent: Dict[str, Any]) -> Dict[str, Any]:
        """Create general exploratory analysis workflow"""
        
        return {
            "name": "Exploratory Analysis Workflow",
            "description": "Open-ended exploration of documents",
            "version": "1.0",
            "phases": [
                {
                    "name": "ingestion",
                    "tools": [
                        {"tool": "T01_pdf_loader", "inputs": {"file_paths": documents}},
                        {"tool": "T15A_text_chunker", "inputs": {"chunk_size": 1000}}
                    ]
                },
                {
                    "name": "extraction",
                    "tools": [
                        {"tool": "T23A_entity_extractor"},
                        {"tool": "T27_relationship_extractor"}
                    ]
                },
                {
                    "name": "construction",
                    "tools": [
                        {"tool": "T31_entity_builder"},
                        {"tool": "T34_edge_builder"}
                    ]
                },
                {
                    "name": "analysis",
                    "tools": [
                        {"tool": "T68_pagerank"},
                        {"tool": "T49_query_engine"}
                    ]
                }
            ],
            "outputs": [
                {"name": "entities", "format": "json"},
                {"name": "relationships", "format": "json"},
                {"name": "graph_metrics", "format": "json"}
            ]
        }
    
    async def _interpret_results(self, execution_results: ExecutionResult, intent: Dict[str, Any], request: ResearchRequest) -> str:
        """Interpret execution results in research context"""
        
        if execution_results.status != "success":
            return f"Analysis encountered an error: {execution_results.results.get('error', 'Unknown error')}"
        
        # Create interpretation based on intent
        if intent["intent_type"] == "theory_application":
            interpretation = self._interpret_theory_application_results(execution_results)
        elif intent["intent_type"] == "theory_extraction":
            interpretation = self._interpret_theory_extraction_results(execution_results)
        else:
            interpretation = self._interpret_exploratory_results(execution_results)
        
        return interpretation
    
    def _interpret_theory_application_results(self, results: ExecutionResult) -> str:
        """Interpret results from theory application"""
        
        # Extract key findings from results
        risk_score = results.results.get("risk_assessment", {}).get("overall_risk", 0.5)
        risk_level = "low" if risk_score < 0.3 else "moderate" if risk_score < 0.7 else "high"
        factors = results.results.get("detected_factors", [])
        
        interpretation = f"""
## Analysis Results: Psychological Factors Assessment

### Overall Risk Assessment
The analysis indicates a **{risk_level} risk level** ({risk_score:.1%}) based on the psychological factors detected in the text.

### Key Findings
1. **Detected Factors**: {len(factors)} psychological factors were identified
2. **Dominant Patterns**: The most prominent factors include {', '.join(factors[:3]) if factors else 'none identified'}
3. **Protective Elements**: Analysis shows presence of protective factors that may mitigate risks

### Research Implications
This analysis demonstrates how psychological theories can be systematically applied to text analysis, providing quantitative risk assessments based on established theoretical frameworks. The knowledge graph construction enables deeper exploration of factor relationships.

### Methodological Notes
The analysis used KGAS MCP tools to process documents, extract theory-relevant features, and build a queryable knowledge graph. All results include full provenance tracking for reproducibility.
"""
        
        return interpretation.strip()
    
    def _interpret_theory_extraction_results(self, results: ExecutionResult) -> str:
        """Interpret results from theory extraction"""
        
        schema = results.results.get("theory_schema", {})
        
        return f"""
## Theory Extraction Results

### Extracted Framework
Successfully extracted theoretical framework with:
- **Model Type**: {schema.get('model_type', 'Not specified')}
- **Nodes**: {len(schema.get('nodes', []))} theoretical constructs
- **Connections**: {len(schema.get('connections', []))} relationships
- **Properties**: Comprehensive metadata and modifiers

### Key Components
The theory includes constructs such as {', '.join([n.get('label', '') for n in schema.get('nodes', [])[:3]])}...

### Application Potential
This extracted schema can now be applied to analyze other texts using the same theoretical lens.
"""
    
    def _interpret_exploratory_results(self, results: ExecutionResult) -> str:
        """Interpret exploratory analysis results"""
        
        entities = results.results.get("entities", [])
        relationships = results.results.get("relationships", [])
        
        return f"""
## Exploratory Analysis Results

### Document Overview
- **Entities Extracted**: {len(entities)}
- **Relationships Identified**: {len(relationships)}
- **Graph Complexity**: Network analysis reveals interconnected knowledge structure

### Key Entities
The most central entities based on PageRank analysis include...

### Relationship Patterns
Analysis identified several relationship types connecting key concepts...
"""
    
    async def _generate_visualizations(self, results: ExecutionResult) -> List[str]:
        """Generate visualization specifications"""
        
        visualizations = [
            "knowledge_graph_network.html",
            "factor_distribution_chart.png",
            "risk_assessment_gauge.html",
            "entity_centrality_plot.png"
        ]
        
        # In real implementation, would generate actual visualizations
        # For demo, we'll just return the planned visualizations
        
        return visualizations
    
    async def _suggest_follow_ups(self, interpretation: str, results: ExecutionResult) -> List[str]:
        """Suggest follow-up analyses"""
        
        suggestions = [
            "Apply the same theoretical framework to additional texts for comparison",
            "Explore specific factor relationships in more detail using graph queries",
            "Conduct temporal analysis if documents span different time periods",
            "Compare results with baseline texts to validate findings",
            "Export knowledge graph for visualization in specialized tools"
        ]
        
        return suggestions
    
    def _save_research_response(self, response: ResearchResponse):
        """Save the complete research response"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main response
        response_file = DEMO_OUTPUT_DIR / f"research_response_{timestamp}.json"
        with open(response_file, 'w') as f:
            json.dump({
                "original_request": response.original_request,
                "refined_query": response.refined_query,
                "methodology_explanation": response.methodology_explanation,
                "interpretation": response.interpretation,
                "visualizations": response.visualizations,
                "follow_up_suggestions": response.follow_up_suggestions,
                "execution_time": response.results.execution_time,
                "status": response.results.status
            }, f, indent=2, default=str)
        
        # Save workflow
        workflow_file = DEMO_OUTPUT_DIR / f"workflow_{timestamp}.yaml"
        with open(workflow_file, 'w') as f:
            f.write(response.results.results.get("workflow_yaml", ""))
        
        print(f"\n💾 Results saved to: {DEMO_OUTPUT_DIR}")


class WorkflowExecutionAgent:
    """
    Subagent focused on efficient workflow execution.
    This agent has minimal context and focuses on running tools.
    """
    
    def __init__(self):
        self.agent_id = "workflow_execution_agent"
        self.execution_history = []
    
    async def execute_workflow(self, workflow_spec: WorkflowSpecification) -> ExecutionResult:
        """Execute workflow using KGAS MCP tools"""
        
        print(f"\n{'='*80}")
        print("⚙️  WORKFLOW EXECUTION AGENT")
        print(f"{'='*80}")
        print(f"📋 Workflow: {workflow_spec.name}")
        print(f"🔧 Phases: {len(workflow_spec.phases)}")
        
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # Initialize results storage
            phase_results = {}
            provenance = []
            
            # Execute each phase
            for i, phase in enumerate(workflow_spec.phases):
                print(f"\n▶️  Phase {i+1}/{len(workflow_spec.phases)}: {phase['name']}")
                
                phase_result = await self._execute_phase(phase, phase_results)
                phase_results[phase['name']] = phase_result
                
                # Track provenance
                provenance.append({
                    "phase": phase['name'],
                    "tools": [tool['tool'] for tool in phase['tools']],
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
                
                print(f"   ✅ Phase completed")
            
            # Generate outputs
            print("\n📊 Generating outputs...")
            outputs = await self._generate_outputs(workflow_spec.outputs, phase_results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create mock results for demo
            if "theory_application" in workflow_spec.name.lower():
                results = self._create_theory_application_results()
            elif "theory_extraction" in workflow_spec.name.lower():
                results = self._create_theory_extraction_results()
            else:
                results = self._create_exploratory_results()
            
            results["workflow_yaml"] = workflow_spec.yaml_content
            
            return ExecutionResult(
                execution_id=execution_id,
                status="success",
                results=results,
                outputs=outputs,
                execution_time=execution_time,
                provenance=provenance
            )
            
        except Exception as e:
            return ExecutionResult(
                execution_id=execution_id,
                status="error",
                results={"error": str(e)},
                outputs={},
                execution_time=(datetime.now() - start_time).total_seconds(),
                provenance=[]
            )
    
    async def _execute_phase(self, phase: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow phase"""
        
        phase_results = {}
        
        for tool_spec in phase.get('tools', []):
            tool_name = tool_spec['tool']
            inputs = tool_spec.get('inputs', {})
            
            print(f"   🔧 Running {tool_name}...")
            
            # In real implementation, would call actual MCP tools
            # For demo, we'll simulate tool execution
            
            if tool_name == "T01_pdf_loader":
                result = {"text": f"[Loaded content from {inputs.get('file_path', 'document')}]", "pages": 100}
            elif tool_name == "T15A_text_chunker":
                result = {"chunks": [f"Chunk {i}" for i in range(10)], "total_chunks": 10}
            elif tool_name == "T23A_entity_extractor":
                result = {"entities": ["Entity1", "Entity2", "Entity3"], "total": 3}
            elif tool_name == "meta_schema_extractor":
                result = {"schema": self._create_sample_theory_schema()}
            elif tool_name == "theory_applicator":
                result = self._create_theory_application_result()
            else:
                result = {"status": "completed", "data": {}}
            
            phase_results[tool_name] = result
        
        return phase_results
    
    async def _generate_outputs(self, output_specs: List[Dict[str, Any]], results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow outputs"""
        
        outputs = {}
        
        for output_spec in output_specs:
            output_name = output_spec['name']
            output_format = output_spec['format']
            
            # Generate output based on format
            if output_format == "json":
                outputs[output_name] = {"data": results, "format": "json"}
            elif output_format == "yaml":
                outputs[output_name] = {"data": yaml.dump(results), "format": "yaml"}
            elif output_format == "graphml":
                outputs[output_name] = {"data": "<graphml>...</graphml>", "format": "graphml"}
            else:
                outputs[output_name] = {"data": str(results), "format": output_format}
        
        return outputs
    
    def _create_theory_application_results(self) -> Dict[str, Any]:
        """Create mock theory application results"""
        
        return {
            "risk_assessment": {
                "overall_risk": 0.426,
                "risk_level": "moderate",
                "confidence": 0.85
            },
            "detected_factors": [
                "transparency_orientation",
                "unity_language",
                "institutional_trust",
                "historical_grounding",
                "balanced_rhetoric"
            ],
            "protective_factors": {
                "transparency": 0.8,
                "unity": 0.916,
                "trust": 0.7
            },
            "risk_factors": {
                "narcissism": 0.3,
                "denialism": 0.2,
                "extremity": 0.1
            },
            "graph_metrics": {
                "nodes": 48,
                "edges": 127,
                "density": 0.112,
                "components": 1
            }
        }
    
    def _create_theory_extraction_results(self) -> Dict[str, Any]:
        """Create mock theory extraction results"""
        
        return {
            "theory_schema": self._create_sample_theory_schema()
        }
    
    def _create_sample_theory_schema(self) -> Dict[str, Any]:
        """Create sample theory schema"""
        
        return {
            "model_type": "network",
            "theory_name": "Psychological Conspiracy Theory Model",
            "nodes": [
                {"id": "narcissism", "label": "Narcissism", "type": "psychological_trait"},
                {"id": "denialism", "label": "Denialism", "type": "psychological_trait"},
                {"id": "conspiracy_support", "label": "Conspiracy Theory Support", "type": "behavioral_outcome"}
            ],
            "connections": [
                {"source": "narcissism", "target": "conspiracy_support", "type": "predicts", "strength": "strong"},
                {"source": "denialism", "target": "conspiracy_support", "type": "predicts", "strength": "moderate"}
            ],
            "properties": {
                "measurement": "Combined survey and behavioral data",
                "sample_size": 2506,
                "validation": "Cross-validated"
            }
        }
    
    def _create_theory_application_result(self) -> Dict[str, Any]:
        """Create theory application result"""
        
        return {
            "detected_factors": {
                "narcissism": {"presence": 0.3, "examples": ["I", "my", "our responsibility"]},
                "denialism": {"presence": 0.2, "examples": ["open discussion", "transparency"]},
                "conspiracy_mentality": {"presence": 0.1, "examples": []}
            },
            "relationships": [
                {"from": "transparency", "to": "trust", "strength": 0.8},
                {"from": "unity", "to": "cooperation", "strength": 0.9}
            ]
        }
    
    def _create_exploratory_results(self) -> Dict[str, Any]:
        """Create exploratory analysis results"""
        
        return {
            "entities": ["United States", "Soviet Union", "Congress", "Peace", "Cooperation"],
            "relationships": [
                {"from": "United States", "to": "Soviet Union", "type": "negotiates_with"},
                {"from": "Congress", "to": "cooperation", "type": "supports"}
            ],
            "graph_metrics": {
                "nodes": 25,
                "edges": 47,
                "avg_degree": 3.76,
                "clustering_coefficient": 0.23
            }
        }


class KGASAgentDemo:
    """
    Main demo class showing the complete KGAS agent architecture
    """
    
    def __init__(self):
        self.research_agent = ResearchInteractionAgent()
        
    async def run_demo(self):
        """Run complete demonstration of KGAS agent architecture"""
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KGAS AGENT ARCHITECTURE DEMONSTRATION                      ║
║                                                                               ║
║  This demonstrates how KGAS works as an autonomous analysis system:           ║
║  1. User provides natural language research request                           ║
║  2. Research agent understands intent and generates workflow                  ║
║  3. Execution agent runs workflow using KGAS MCP tools                        ║
║  4. Results are interpreted and presented to user                             ║
║                                                                               ║
║  This implements the Layer 1 (Agent-Controlled) interface from the            ║
║  multi-layer agent architecture.                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # Demo 1: Theory Application (Kunst paper to Carter speech)
        print("\n" + "━"*80)
        print("📚 DEMO 1: Apply Psychological Theory to Text Analysis")
        print("━"*80)
        
        request1 = ResearchRequest(
            query="Apply the psychological conspiracy theory model from the Kunst paper to analyze President Carter's speech for conspiracy-related factors",
            documents=[
                "/home/brian/projects/Digimons/kunst_paper.txt",
                "/home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt"
            ],
            context={"research_domain": "political_psychology"}
        )
        
        response1 = await self.research_agent.handle_research_request(request1)
        self._display_response(response1)
        
        # Demo 2: Theory Extraction
        print("\n" + "━"*80)
        print("📚 DEMO 2: Extract Theoretical Framework from Academic Paper")
        print("━"*80)
        
        request2 = ResearchRequest(
            query="Extract the theoretical framework from this academic paper using meta-schema v10 approach",
            documents=["/home/brian/projects/Digimons/kunst_paper.txt"],
            context={"extraction_focus": "psychological_constructs"}
        )
        
        response2 = await self.research_agent.handle_research_request(request2)
        self._display_response(response2)
        
        print("\n" + "━"*80)
        print("✅ KGAS Agent Architecture Demonstration Complete")
        print("━"*80)
        print(f"\nResults saved to: {DEMO_OUTPUT_DIR}")
        print("\nThis demonstration shows how KGAS integrates:")
        print("  • Natural language understanding")
        print("  • Automated workflow generation")
        print("  • MCP tool orchestration")
        print("  • Theory-aware analysis")
        print("  • Research-oriented interpretation")
    
    def _display_response(self, response: ResearchResponse):
        """Display research response in readable format"""
        
        print(f"\n🎯 Refined Query: {response.refined_query}")
        print(f"\n📋 Methodology: {response.methodology_explanation}")
        print(f"\n⏱️  Execution Time: {response.results.execution_time:.2f} seconds")
        print(f"\n📊 Results Status: {response.results.status}")
        
        if response.results.status == "success":
            print(f"\n💡 Interpretation:")
            print(response.interpretation)
            
            print(f"\n📈 Visualizations Generated:")
            for viz in response.visualizations[:3]:
                print(f"   • {viz}")
            
            print(f"\n🔮 Follow-up Suggestions:")
            for suggestion in response.follow_up_suggestions[:3]:
                print(f"   • {suggestion}")


async def main():
    """Run the KGAS agent demonstration"""
    
    demo = KGASAgentDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())