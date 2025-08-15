#!/usr/bin/env python3
"""
KGAS Integration with Claude Code as Agent Brain

This implementation leverages Claude Code's native capabilities:
1. Subagents for parallel analysis and focused tasks
2. MCP servers for KGAS tool integration
3. SDK for programmatic control
4. Natural language to workflow generation

Key insights from claude-code guides:
- Subagents get their own context window (better for complex tasks)
- Can run up to 10 subagents in parallel
- MCP servers provide tool integration
- SDK allows programmatic control with streaming
"""

import os
import sys
import json
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncIterator
from dataclasses import dataclass, field

# For Claude Code SDK integration
try:
    from claude_code_sdk import query, ClaudeCodeOptions, Message
except ImportError:
    print("Installing claude-code-sdk...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "claude-code-sdk"])
    from claude_code_sdk import query, ClaudeCodeOptions, Message


@dataclass
class KGASRequest:
    """Research request from user"""
    query: str
    documents: List[str]
    analysis_type: str = "exploratory"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class KGASWorkflow:
    """Generated workflow specification"""
    name: str
    phases: List[Dict[str, Any]]
    outputs: List[str]
    subagent_tasks: List[Dict[str, Any]]  # Tasks for parallel subagents
    

class KGASClaudeCodeIntegration:
    """
    Integrates KGAS with Claude Code as the agent brain.
    Uses Claude Code's native capabilities for orchestration.
    """
    
    def __init__(self, mcp_config_path: Optional[str] = None):
        self.mcp_config_path = mcp_config_path or self._create_kgas_mcp_config()
        self.results_dir = Path("kgas_analysis_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def _create_kgas_mcp_config(self) -> str:
        """Create MCP configuration for KGAS tools"""
        config = {
            "mcpServers": {
                "kgas": {
                    "command": "python",
                    "args": ["/home/brian/projects/Digimons/kgas_mcp_server.py"],
                    "env": {}
                }
            }
        }
        
        config_path = Path("kgas_mcp_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        return str(config_path)
    
    async def process_research_request(self, request: KGASRequest) -> Dict[str, Any]:
        """
        Process research request using Claude Code as the brain.
        
        This demonstrates:
        1. Natural language understanding
        2. Workflow generation 
        3. Subagent delegation for parallel tasks
        4. MCP tool integration
        """
        
        print(f"\n{'='*80}")
        print("🧠 KGAS + Claude Code Integration")
        print(f"{'='*80}")
        print(f"📝 Request: {request.query}")
        print(f"📄 Documents: {len(request.documents)}")
        
        # Step 1: Generate workflow using Claude Code
        workflow = await self._generate_workflow(request)
        
        # Step 2: Execute workflow with subagents
        results = await self._execute_workflow_with_subagents(workflow, request)
        
        # Step 3: Synthesize results
        synthesis = await self._synthesize_results(results, request)
        
        return {
            "request": request.query,
            "workflow": workflow,
            "results": results,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_workflow(self, request: KGASRequest) -> KGASWorkflow:
        """Use Claude Code to generate workflow from natural language"""
        
        prompt = f"""
You are a KGAS workflow generator. Generate a workflow for this research request:

Request: {request.query}
Documents: {', '.join(request.documents)}
Analysis Type: {request.analysis_type}

Create a workflow that:
1. Identifies which KGAS MCP tools to use
2. Breaks down into phases that can run in parallel where possible
3. Defines clear outputs

Available KGAS MCP tools:
- mcp__kgas__load_pdf_document - Load PDF documents
- mcp__kgas__chunk_text - Chunk text for processing  
- mcp__kgas__extract_entities_from_text - Extract entities using NER
- mcp__kgas__query_graph - Query the knowledge graph
- mcp__kgas__calculate_pagerank - Calculate PageRank scores

Format as JSON with:
- name: workflow name
- phases: list of phases with tools and inputs
- outputs: expected outputs
- subagent_tasks: tasks that can be delegated to subagents for parallel execution
"""
        
        # Use Claude Code SDK to generate workflow
        messages = []
        async for message in query(
            prompt=prompt,
            options=ClaudeCodeOptions(
                max_turns=1,
                output_format="json"
            )
        ):
            messages.append(message)
        
        # Parse generated workflow
        if messages and messages[-1].get("type") == "assistant":
            workflow_json = json.loads(messages[-1]["message"]["content"][0]["text"])
            return KGASWorkflow(**workflow_json)
        else:
            # Fallback workflow
            return self._create_default_workflow(request)
    
    def _create_default_workflow(self, request: KGASRequest) -> KGASWorkflow:
        """Create default workflow if generation fails"""
        
        subagent_tasks = []
        
        # Create subagent tasks for each document
        for i, doc in enumerate(request.documents):
            subagent_tasks.append({
                "name": f"analyze_document_{i}",
                "description": f"Analyze document: {Path(doc).name}",
                "prompt": f"""
Use the KGAS MCP tools to analyze this document:
1. Load the PDF using mcp__kgas__load_pdf_document with file_path: {doc}
2. Chunk the text using mcp__kgas__chunk_text
3. Extract entities using mcp__kgas__extract_entities_from_text for each chunk
4. Build a summary of key findings

Return a structured analysis with:
- Main topics
- Key entities
- Important relationships
- Summary insights
"""
            })
        
        # Add synthesis task
        subagent_tasks.append({
            "name": "synthesize_findings",
            "description": "Synthesize findings across all documents",
            "prompt": """
Review the analyses from all document subagents and:
1. Identify common themes across documents
2. Find contradictions or disagreements
3. Create a unified knowledge graph using mcp__kgas__query_graph
4. Generate overall insights and recommendations
"""
        })
        
        return KGASWorkflow(
            name="Multi-Document Analysis",
            phases=[
                {
                    "name": "document_analysis",
                    "parallel": True,
                    "tasks": [f"analyze_document_{i}" for i in range(len(request.documents))]
                },
                {
                    "name": "synthesis",
                    "tasks": ["synthesize_findings"]
                }
            ],
            outputs=["document_summaries", "unified_analysis", "knowledge_graph"],
            subagent_tasks=subagent_tasks
        )
    
    async def _execute_workflow_with_subagents(self, 
                                               workflow: KGASWorkflow, 
                                               request: KGASRequest) -> Dict[str, Any]:
        """
        Execute workflow using Claude Code subagents.
        
        Key advantages:
        - Each subagent gets its own context window
        - Can run up to 10 in parallel
        - Better for complex, focused tasks
        """
        
        print("\n🚀 Executing workflow with subagents...")
        
        # Create master prompt that delegates to subagents
        subagent_prompts = []
        for task in workflow.subagent_tasks:
            subagent_prompts.append(f"""
Task: {task['name']}
Description: {task['description']}

{task['prompt']}
""")
        
        master_prompt = f"""
Execute this KGAS analysis workflow using subagents for parallel processing.

Original Request: {request.query}

Use subagents to run these tasks in parallel:

{chr(10).join([f"{i+1}. {task['name']}" for i, task in enumerate(workflow.subagent_tasks)])}

For each subagent task, provide this prompt:
{chr(10).join(subagent_prompts)}

Important:
- Use the Task tool to create subagents
- Run document analysis tasks in parallel (up to 10)
- Wait for all document analyses before synthesis
- Each subagent should use the KGAS MCP tools (mcp__kgas__*)
- Collect and return all subagent results

After all subagents complete, compile the results into a final analysis.
"""
        
        # Execute with Claude Code SDK
        results = {}
        
        async for message in query(
            prompt=master_prompt,
            options=ClaudeCodeOptions(
                max_turns=10,  # Allow multiple turns for complex workflow
                mcp_config=self.mcp_config_path,
                allowed_tools=[
                    "Task",  # For subagents
                    "mcp__kgas__load_pdf_document",
                    "mcp__kgas__chunk_text", 
                    "mcp__kgas__extract_entities_from_text",
                    "mcp__kgas__query_graph",
                    "mcp__kgas__calculate_pagerank"
                ]
            )
        ):
            # Process streaming results
            if message.get("type") == "assistant":
                # Extract results from assistant messages
                content = message.get("message", {}).get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        # Parse any structured results
                        try:
                            if "{" in item["text"] and "}" in item["text"]:
                                json_str = item["text"][item["text"].find("{"):item["text"].rfind("}")+1]
                                results.update(json.loads(json_str))
                        except:
                            pass
        
        return results
    
    async def _synthesize_results(self, results: Dict[str, Any], request: KGASRequest) -> str:
        """Synthesize results into final research output"""
        
        synthesis_prompt = f"""
Synthesize the KGAS analysis results into a comprehensive research report.

Original Request: {request.query}

Analysis Results:
{json.dumps(results, indent=2)}

Create a research synthesis that includes:
1. Executive Summary
2. Key Findings by Document
3. Cross-Document Patterns
4. Knowledge Graph Insights
5. Recommendations
6. Areas for Further Research

Format as a clear, academic-style report.
"""
        
        synthesis = ""
        async for message in query(
            prompt=synthesis_prompt,
            options=ClaudeCodeOptions(max_turns=1)
        ):
            if message.get("type") == "assistant":
                content = message.get("message", {}).get("content", [])
                for item in content:
                    if item.get("type") == "text":
                        synthesis += item["text"]
        
        return synthesis
    
    async def demonstrate_capabilities(self):
        """Demonstrate various KGAS + Claude Code integration patterns"""
        
        print("\n📋 KGAS + Claude Code Integration Capabilities\n")
        
        # Example 1: Theory Extraction with Subagents
        print("1️⃣ Theory Extraction Using Parallel Subagents")
        print("   - Each subagent extracts theory components")
        print("   - Parallel processing of vocabulary, constructs, relationships")
        print("   - Synthesis subagent creates unified theory schema")
        
        # Example 2: Multi-Document Fusion
        print("\n2️⃣ Multi-Document Analysis") 
        print("   - Subagent per document (up to 10 parallel)")
        print("   - Each has full context for deep analysis")
        print("   - Master agent synthesizes findings")
        
        # Example 3: Real-time Analysis Pipeline
        print("\n3️⃣ Streaming Analysis Pipeline")
        print("   - Stream results as subagents complete")
        print("   - Progressive refinement of findings")
        print("   - Early insights while processing continues")
        
        # Example request
        example = KGASRequest(
            query="Extract and apply psychological theories from academic papers to analyze political speeches",
            documents=[
                "/home/brian/projects/Digimons/kunst_paper.txt",
                "/home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt"
            ],
            analysis_type="theory_application"
        )
        
        print(f"\n🔬 Example Analysis:")
        print(f"   Query: {example.query}")
        print(f"   Using {len(example.documents)} documents")
        print(f"   Type: {example.analysis_type}")
        
        # Show how it would work
        print("\n🎯 Execution Flow:")
        print("1. Claude Code generates KGAS workflow")
        print("2. Creates subagents for parallel document processing") 
        print("3. Each subagent uses KGAS MCP tools independently")
        print("4. Master agent coordinates and synthesizes")
        print("5. Final research report with full provenance")


async def main():
    """Demonstrate KGAS + Claude Code integration"""
    
    integration = KGASClaudeCodeIntegration()
    
    # Show capabilities
    await integration.demonstrate_capabilities()
    
    # Example: Run actual analysis
    request = KGASRequest(
        query="Analyze the psychological factors in political rhetoric using the Kunst framework",
        documents=[
            "/home/brian/projects/Digimons/kunst_paper.txt",
            "/home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt"
        ],
        analysis_type="theory_application"
    )
    
    print("\n\n🚀 Running Actual Analysis...")
    print("(This would use Claude Code SDK with KGAS MCP tools)")
    
    # Uncomment to run actual analysis:
    # results = await integration.process_research_request(request)
    # print(f"\n✅ Analysis Complete!")
    # print(f"Results saved to: {integration.results_dir}")


if __name__ == "__main__":
    asyncio.run(main())