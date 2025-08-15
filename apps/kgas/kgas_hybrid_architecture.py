#!/usr/bin/env python3
"""
KGAS Hybrid Architecture: Reproducible Workflows with Intelligent Orchestration

This approach combines:
1. Deterministic YAML workflows for reproducibility
2. Claude Code for natural language understanding and adaptive execution
3. Fine-grained control over tool usage and parameters
4. Audit trails for academic reproducibility
"""

import os
import sys
import json
import yaml
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ExecutionMode(Enum):
    """Control how much autonomy Claude Code has"""
    STRICT = "strict"              # Follow workflow exactly
    GUIDED = "guided"              # Allow minor adaptations
    AUTONOMOUS = "autonomous"      # Full Claude Code control
    INTERACTIVE = "interactive"    # Ask user at decision points


@dataclass
class WorkflowSpec:
    """Reproducible workflow specification"""
    id: str
    name: str
    version: str
    description: str
    inputs: Dict[str, Any]
    phases: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_yaml(self) -> str:
        """Convert to YAML for storage/sharing"""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "inputs": self.inputs,
            "phases": self.phases,
            "outputs": self.outputs,
            "constraints": self.constraints,
            "metadata": self.metadata
        }
    
    def calculate_hash(self) -> str:
        """Calculate deterministic hash for reproducibility"""
        # Sort keys to ensure consistent hashing
        workflow_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(workflow_str.encode()).hexdigest()


@dataclass
class ExecutionContext:
    """Tracks execution state for reproducibility"""
    workflow_spec: WorkflowSpec
    execution_mode: ExecutionMode
    start_time: datetime
    random_seed: Optional[int] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    
    def log_decision(self, decision_point: str, choice: str, rationale: str):
        """Log all decisions for reproducibility"""
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "decision_point": decision_point,
            "choice": choice,
            "rationale": rationale,
            "context_hash": self._get_context_hash()
        })
    
    def _get_context_hash(self) -> str:
        """Hash current context state"""
        context_data = {
            "workflow_id": self.workflow_spec.id,
            "phase_results": list(self.results.keys()),
            "parameters": self.parameters
        }
        return hashlib.sha256(
            json.dumps(context_data, sort_keys=True).encode()
        ).hexdigest()[:8]


class KGASHybridOrchestrator:
    """
    Hybrid orchestrator that combines:
    - Reproducible YAML workflows
    - Claude Code for intelligent execution
    - Fine-grained control options
    """
    
    def __init__(self, mcp_config_path: Optional[str] = None):
        self.mcp_config_path = mcp_config_path
        self.workflow_library = self._load_workflow_library()
        self.execution_history = []
        
    def _load_workflow_library(self) -> Dict[str, WorkflowSpec]:
        """Load pre-defined reproducible workflows"""
        library = {}
        
        # Example: Theory Application Workflow
        library["theory_application_v1"] = WorkflowSpec(
            id="theory_application_v1",
            name="Theory Application Analysis",
            version="1.0.0",
            description="Apply theoretical framework to analyze documents",
            inputs={
                "theory_document": {"type": "path", "required": True},
                "target_documents": {"type": "array", "items": "path"},
                "analysis_parameters": {
                    "confidence_threshold": 0.7,
                    "min_evidence_count": 3
                }
            },
            phases=[
                {
                    "id": "theory_extraction",
                    "name": "Extract Theoretical Framework",
                    "tools": [
                        {
                            "tool": "mcp__kgas__load_pdf_document",
                            "inputs": {"file_path": "${inputs.theory_document}"}
                        },
                        {
                            "tool": "mcp__kgas__extract_theory_schema",
                            "inputs": {"document": "${phases.theory_extraction.outputs[0]}"}
                        }
                    ],
                    "validation": {
                        "require_output": ["theory_schema"],
                        "schema_validation": True
                    }
                },
                {
                    "id": "document_analysis", 
                    "name": "Analyze Target Documents",
                    "parallel": True,
                    "foreach": "${inputs.target_documents}",
                    "tools": [
                        {
                            "tool": "mcp__kgas__load_pdf_document",
                            "inputs": {"file_path": "${item}"}
                        },
                        {
                            "tool": "mcp__kgas__chunk_text",
                            "inputs": {
                                "text": "${phases.document_analysis.outputs[0].text}",
                                "chunk_size": 1000
                            }
                        },
                        {
                            "tool": "mcp__kgas__apply_theory",
                            "inputs": {
                                "theory": "${phases.theory_extraction.outputs.theory_schema}",
                                "chunks": "${phases.document_analysis.outputs[1].chunks}"
                            }
                        }
                    ]
                },
                {
                    "id": "synthesis",
                    "name": "Synthesize Findings",
                    "tools": [
                        {
                            "tool": "mcp__kgas__build_unified_graph",
                            "inputs": {
                                "analyses": "${phases.document_analysis.outputs}"
                            }
                        },
                        {
                            "tool": "mcp__kgas__calculate_pagerank",
                            "inputs": {"graph": "${phases.synthesis.outputs[0]}"}
                        }
                    ]
                }
            ],
            outputs=[
                {"name": "theory_schema", "source": "${phases.theory_extraction.outputs.theory_schema}"},
                {"name": "document_analyses", "source": "${phases.document_analysis.outputs}"},
                {"name": "knowledge_graph", "source": "${phases.synthesis.outputs[0]}"},
                {"name": "central_concepts", "source": "${phases.synthesis.outputs[1]}"}
            ],
            constraints={
                "max_execution_time": 3600,  # 1 hour
                "max_parallel_tasks": 10,
                "required_tool_versions": {
                    "kgas": ">=0.8.0"
                }
            }
        )
        
        return library
    
    async def execute_workflow(self,
                              workflow_id: str,
                              inputs: Dict[str, Any],
                              execution_mode: ExecutionMode = ExecutionMode.GUIDED,
                              **kwargs) -> Dict[str, Any]:
        """
        Execute a workflow with specified level of control.
        
        Modes:
        - STRICT: Follow workflow exactly, fail on any deviation
        - GUIDED: Allow Claude Code to adapt within constraints
        - AUTONOMOUS: Let Claude Code optimize execution
        - INTERACTIVE: Ask user for decisions at key points
        """
        
        # Load workflow specification
        if workflow_id not in self.workflow_library:
            raise ValueError(f"Unknown workflow: {workflow_id}")
            
        workflow_spec = self.workflow_library[workflow_id]
        
        # Create execution context
        context = ExecutionContext(
            workflow_spec=workflow_spec,
            execution_mode=execution_mode,
            start_time=datetime.now(),
            random_seed=kwargs.get("random_seed"),
            parameters=inputs
        )
        
        print(f"\n{'='*80}")
        print(f"🔬 KGAS Workflow Execution")
        print(f"{'='*80}")
        print(f"Workflow: {workflow_spec.name} (v{workflow_spec.version})")
        print(f"Mode: {execution_mode.value}")
        print(f"Hash: {workflow_spec.calculate_hash()[:8]}")
        
        # Execute based on mode
        if execution_mode == ExecutionMode.STRICT:
            result = await self._execute_strict(context)
        elif execution_mode == ExecutionMode.GUIDED:
            result = await self._execute_guided(context)
        elif execution_mode == ExecutionMode.AUTONOMOUS:
            result = await self._execute_autonomous(context)
        else:  # INTERACTIVE
            result = await self._execute_interactive(context)
        
        # Save execution record for reproducibility
        execution_record = {
            "workflow_id": workflow_id,
            "workflow_hash": workflow_spec.calculate_hash(),
            "execution_mode": execution_mode.value,
            "inputs": inputs,
            "start_time": context.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "audit_trail": context.audit_trail,
            "results": result
        }
        
        self._save_execution_record(execution_record)
        
        return result
    
    async def _execute_strict(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute workflow exactly as specified"""
        print("\n📋 Executing in STRICT mode - no deviations allowed")
        
        # Generate exact tool sequence
        tool_sequence = self._generate_tool_sequence(context.workflow_spec)
        
        # Execute via Claude Code with strict instructions
        prompt = f"""
Execute this KGAS workflow EXACTLY as specified. Do not deviate.

Workflow: {context.workflow_spec.name}
Hash: {context.workflow_spec.calculate_hash()[:8]}

Tool sequence to execute:
{json.dumps(tool_sequence, indent=2)}

Parameters:
{json.dumps(context.parameters, indent=2)}

IMPORTANT:
- Execute tools in exact order given
- Use exact parameters specified
- Do not add or skip any tools
- Report any errors immediately
- Return structured results matching output specification
"""
        
        # Would execute via Claude Code SDK here
        # For now, return mock result
        return {
            "status": "success",
            "mode": "strict",
            "workflow_hash": context.workflow_spec.calculate_hash(),
            "outputs": {}
        }
    
    async def _execute_guided(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute with Claude Code guidance within constraints"""
        print("\n🎯 Executing in GUIDED mode - adaptive within constraints")
        
        constraints_prompt = f"""
Execute this KGAS workflow with the following constraints:

Workflow: {context.workflow_spec.name}
Version: {context.workflow_spec.version}

Constraints:
- Must complete all phases in order
- Can adapt tool parameters within ranges
- Can add error handling and retries
- Must produce all specified outputs

Workflow specification:
{yaml.dump(context.workflow_spec.phases)}

You may:
- Optimize parallel execution
- Add validation steps
- Retry failed operations
- Choose best parameters within constraints

You may NOT:
- Skip required phases
- Change output format
- Exceed time/resource limits
"""
        
        context.log_decision(
            "execution_mode",
            "guided",
            "Allowing controlled adaptation for robustness"
        )
        
        return {
            "status": "success",
            "mode": "guided",
            "adaptations_made": []
        }
    
    async def _execute_autonomous(self, context: ExecutionContext) -> Dict[str, Any]:
        """Let Claude Code optimize execution"""
        print("\n🚀 Executing in AUTONOMOUS mode - full optimization allowed")
        
        optimization_prompt = f"""
Achieve the research goal using KGAS tools optimally.

Goal: {context.workflow_spec.description}
Inputs: {json.dumps(context.parameters)}

You have full autonomy to:
- Choose tools and parameters
- Parallelize operations
- Add analysis steps
- Optimize for quality/speed

The only requirement is producing these outputs:
{json.dumps(context.workflow_spec.outputs)}
"""
        
        return {
            "status": "success", 
            "mode": "autonomous"
        }
    
    async def _execute_interactive(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute with user input at decision points"""
        print("\n👤 Executing in INTERACTIVE mode - user decisions required")
        
        # Would implement interactive decision points
        return {
            "status": "success",
            "mode": "interactive",
            "user_decisions": []
        }
    
    def _generate_tool_sequence(self, workflow_spec: WorkflowSpec) -> List[Dict[str, Any]]:
        """Generate exact tool sequence from workflow spec"""
        sequence = []
        
        for phase in workflow_spec.phases:
            for tool_spec in phase.get("tools", []):
                sequence.append({
                    "phase": phase["id"],
                    "tool": tool_spec["tool"],
                    "inputs": tool_spec["inputs"]
                })
                
        return sequence
    
    def _save_execution_record(self, record: Dict[str, Any]):
        """Save execution record for reproducibility"""
        
        # Create reproducibility directory
        repro_dir = Path("kgas_reproducibility")
        repro_dir.mkdir(exist_ok=True)
        
        # Save with timestamp and hash
        filename = f"{record['workflow_id']}_{record['start_time'].replace(':', '-')}.json"
        filepath = repro_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
            
        print(f"\n💾 Execution record saved: {filepath}")
        print(f"   Workflow hash: {record['workflow_hash'][:8]}")
    
    def reproduce_execution(self, execution_record_path: str) -> Dict[str, Any]:
        """Reproduce a previous execution exactly"""
        
        with open(execution_record_path, 'r') as f:
            record = json.load(f)
            
        print(f"\n🔄 Reproducing execution from: {execution_record_path}")
        print(f"   Original workflow hash: {record['workflow_hash'][:8]}")
        
        # Verify workflow hasn't changed
        current_workflow = self.workflow_library.get(record['workflow_id'])
        if current_workflow:
            current_hash = current_workflow.calculate_hash()
            if current_hash != record['workflow_hash']:
                print(f"   ⚠️  WARNING: Workflow has changed!")
                print(f"   Original: {record['workflow_hash'][:8]}")
                print(f"   Current:  {current_hash[:8]}")
        
        # Re-execute with same parameters
        return asyncio.run(self.execute_workflow(
            workflow_id=record['workflow_id'],
            inputs=record['inputs'],
            execution_mode=ExecutionMode[record['execution_mode'].upper()],
            random_seed=record.get('random_seed')
        ))


class WorkflowBuilder:
    """Build reproducible workflows from research requirements"""
    
    @staticmethod
    def build_from_requirements(requirements: Dict[str, Any]) -> WorkflowSpec:
        """Build workflow from research requirements"""
        
        # This would implement workflow generation logic
        # For now, return a simple example
        
        return WorkflowSpec(
            id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=requirements.get("name", "Custom Analysis"),
            version="1.0.0",
            description=requirements.get("description", ""),
            inputs=requirements.get("inputs", {}),
            phases=requirements.get("phases", []),
            outputs=requirements.get("outputs", []),
            constraints=requirements.get("constraints", {})
        )


# Example usage
async def demonstrate_hybrid_approach():
    """Demonstrate the hybrid approach with different execution modes"""
    
    orchestrator = KGASHybridOrchestrator()
    
    # Example inputs
    inputs = {
        "theory_document": "/home/brian/projects/Digimons/kunst_paper.txt",
        "target_documents": [
            "/home/brian/projects/Digimons/lit_review/data/test_texts/texts/carter_speech.txt"
        ],
        "analysis_parameters": {
            "confidence_threshold": 0.8
        }
    }
    
    print("\n🔬 KGAS Hybrid Architecture Demonstration")
    print("="*50)
    
    # 1. Strict mode - fully reproducible
    print("\n1️⃣ STRICT Mode - Fully Reproducible")
    print("   Use when: Publishing results, regulatory compliance")
    print("   Behavior: Exact tool sequence, deterministic")
    
    # 2. Guided mode - balanced
    print("\n2️⃣ GUIDED Mode - Adaptive within Constraints")  
    print("   Use when: Production analysis, quality important")
    print("   Behavior: Optimizations allowed, outputs guaranteed")
    
    # 3. Autonomous mode - maximum flexibility
    print("\n3️⃣ AUTONOMOUS Mode - Full Claude Code Control")
    print("   Use when: Exploratory analysis, finding insights")
    print("   Behavior: Claude Code chooses optimal approach")
    
    # 4. Interactive mode - human in the loop
    print("\n4️⃣ INTERACTIVE Mode - Human Decisions")
    print("   Use when: High-stakes analysis, learning")
    print("   Behavior: User approves key decisions")
    
    # Show how to execute
    print("\n📊 Example Execution:")
    print("="*50)
    
    # Would actually execute here
    # result = await orchestrator.execute_workflow(
    #     workflow_id="theory_application_v1",
    #     inputs=inputs,
    #     execution_mode=ExecutionMode.GUIDED
    # )
    
    print("\n✅ Benefits of Hybrid Approach:")
    print("- Reproducibility when needed (STRICT mode)")
    print("- Flexibility when helpful (GUIDED/AUTONOMOUS)")
    print("- Human control when required (INTERACTIVE)")
    print("- All executions tracked and auditable")
    print("- Can replay any previous analysis exactly")


if __name__ == "__main__":
    asyncio.run(demonstrate_hybrid_approach())