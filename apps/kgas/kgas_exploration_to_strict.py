#!/usr/bin/env python3
"""
KGAS Exploration-to-Strict Workflow System

Key insight: Every exploration with Claude Code should capture the execution path
and crystallize it into a reproducible workflow.

This enables:
1. Free exploration with Claude Code's adaptability
2. Automatic workflow generation from successful runs
3. Perfect reproducibility of any previous execution
4. Progressive formalization of research methods
"""

import os
import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ToolCall:
    """Record of a single tool invocation"""
    timestamp: str
    tool_name: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    duration_ms: int
    context_hash: str
    success: bool
    error: Optional[str] = None
    
    def to_workflow_step(self) -> Dict[str, Any]:
        """Convert to workflow step specification"""
        return {
            "tool": self.tool_name,
            "inputs": self.inputs,
            "expected_output_keys": list(self.outputs.keys()) if self.success else [],
            "timeout_ms": self.duration_ms * 2,  # Give some buffer
            "critical": True  # In strict mode, all steps are critical
        }


@dataclass
class ExecutionPath:
    """Complete path through an exploration"""
    execution_id: str
    start_time: str
    end_time: str
    original_prompt: str
    tool_calls: List[ToolCall]
    decisions: List[Dict[str, Any]]
    parallel_groups: List[List[int]]  # Indices of tools that ran in parallel
    final_outputs: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_hash(self) -> str:
        """Calculate deterministic hash of execution path"""
        path_data = {
            "tools": [(tc.tool_name, tc.inputs) for tc in self.tool_calls],
            "outputs": sorted(self.final_outputs.keys())
        }
        return hashlib.sha256(
            json.dumps(path_data, sort_keys=True).encode()
        ).hexdigest()
    
    def to_workflow_spec(self, 
                        name: Optional[str] = None,
                        description: Optional[str] = None) -> Dict[str, Any]:
        """Convert execution path to reproducible workflow specification"""
        
        # Generate workflow from execution
        workflow = {
            "id": f"crystallized_{self.execution_id[:8]}",
            "name": name or f"Workflow from {self.start_time}",
            "description": description or f"Crystallized from: {self.original_prompt[:100]}...",
            "version": "1.0.0",
            "source": {
                "type": "exploration",
                "execution_id": self.execution_id,
                "prompt": self.original_prompt,
                "timestamp": self.start_time
            },
            "phases": self._generate_phases(),
            "outputs": self._generate_output_spec(),
            "execution_hash": self.calculate_hash(),
            "metadata": {
                "original_duration_ms": self._calculate_duration(),
                "tool_count": len(self.tool_calls),
                "parallelism_used": len(self.parallel_groups) > 0
            }
        }
        
        return workflow
    
    def _generate_phases(self) -> List[Dict[str, Any]]:
        """Generate workflow phases from execution path"""
        phases = []
        
        if not self.parallel_groups:
            # Sequential execution - one phase
            phases.append({
                "id": "main",
                "name": "Sequential Execution",
                "tools": [tc.to_workflow_step() for tc in self.tool_calls]
            })
        else:
            # Parallel execution - group into phases
            processed_indices = set()
            
            for i, group in enumerate(self.parallel_groups):
                phase_tools = []
                for idx in group:
                    if idx < len(self.tool_calls):
                        phase_tools.append(self.tool_calls[idx].to_workflow_step())
                        processed_indices.add(idx)
                
                phases.append({
                    "id": f"parallel_group_{i}",
                    "name": f"Parallel Group {i+1}",
                    "parallel": True,
                    "tools": phase_tools
                })
            
            # Add any sequential tools not in parallel groups
            sequential_tools = []
            for idx, tc in enumerate(self.tool_calls):
                if idx not in processed_indices:
                    sequential_tools.append(tc.to_workflow_step())
            
            if sequential_tools:
                phases.append({
                    "id": "sequential_completion",
                    "name": "Sequential Completion",
                    "tools": sequential_tools
                })
        
        return phases
    
    def _generate_output_spec(self) -> List[Dict[str, Any]]:
        """Generate output specification from final outputs"""
        outputs = []
        
        for key, value in self.final_outputs.items():
            output_type = "json"
            if isinstance(value, str):
                output_type = "text"
            elif isinstance(value, list):
                output_type = "array"
                
            outputs.append({
                "name": key,
                "type": output_type,
                "description": f"Output from exploration: {key}"
            })
            
        return outputs
    
    def _calculate_duration(self) -> int:
        """Calculate total execution duration"""
        return sum(tc.duration_ms for tc in self.tool_calls)


class ExecutionCapture:
    """Captures execution paths from Claude Code runs"""
    
    def __init__(self, storage_dir: str = "kgas_execution_paths"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.current_execution = None
        
    def start_capture(self, prompt: str, metadata: Dict[str, Any] = None) -> str:
        """Start capturing a new execution"""
        execution_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        self.current_execution = {
            "execution_id": execution_id,
            "start_time": datetime.now().isoformat(),
            "prompt": prompt,
            "tool_calls": [],
            "decisions": [],
            "metadata": metadata or {}
        }
        
        return execution_id
    
    def capture_tool_call(self, 
                         tool_name: str,
                         inputs: Dict[str, Any],
                         outputs: Dict[str, Any],
                         duration_ms: int,
                         success: bool = True,
                         error: Optional[str] = None):
        """Capture a tool call in the current execution"""
        
        if not self.current_execution:
            raise ValueError("No active execution capture")
            
        tool_call = ToolCall(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            inputs=self._sanitize_inputs(inputs),
            outputs=self._sanitize_outputs(outputs),
            duration_ms=duration_ms,
            context_hash=self._calculate_context_hash(),
            success=success,
            error=error
        )
        
        self.current_execution["tool_calls"].append(tool_call)
    
    def capture_decision(self,
                        decision_point: str,
                        choice: str,
                        alternatives: List[str],
                        rationale: str):
        """Capture a decision made during execution"""
        
        if not self.current_execution:
            raise ValueError("No active execution capture")
            
        self.current_execution["decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "decision_point": decision_point,
            "choice": choice,
            "alternatives": alternatives,
            "rationale": rationale
        })
    
    def capture_parallel_execution(self, tool_indices: List[int]):
        """Capture that certain tools ran in parallel"""
        
        if not self.current_execution:
            raise ValueError("No active execution capture")
            
        if "parallel_groups" not in self.current_execution:
            self.current_execution["parallel_groups"] = []
            
        self.current_execution["parallel_groups"].append(tool_indices)
    
    def complete_capture(self, final_outputs: Dict[str, Any]) -> ExecutionPath:
        """Complete the current execution capture"""
        
        if not self.current_execution:
            raise ValueError("No active execution capture")
            
        self.current_execution["end_time"] = datetime.now().isoformat()
        self.current_execution["final_outputs"] = final_outputs
        
        # Create ExecutionPath object
        execution_path = ExecutionPath(
            execution_id=self.current_execution["execution_id"],
            start_time=self.current_execution["start_time"],
            end_time=self.current_execution["end_time"],
            original_prompt=self.current_execution["prompt"],
            tool_calls=self.current_execution["tool_calls"],
            decisions=self.current_execution["decisions"],
            parallel_groups=self.current_execution.get("parallel_groups", []),
            final_outputs=final_outputs,
            metadata=self.current_execution["metadata"]
        )
        
        # Save to disk
        self._save_execution_path(execution_path)
        
        # Reset current execution
        self.current_execution = None
        
        return execution_path
    
    def _sanitize_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize inputs for storage (remove large data, keep references)"""
        sanitized = {}
        
        for key, value in inputs.items():
            if isinstance(value, str) and len(value) > 1000:
                # Store hash for large strings
                sanitized[key] = {
                    "_type": "large_string",
                    "length": len(value),
                    "hash": hashlib.sha256(value.encode()).hexdigest()[:16],
                    "preview": value[:100] + "..."
                }
            elif isinstance(value, bytes):
                # Store hash for binary data
                sanitized[key] = {
                    "_type": "binary",
                    "length": len(value),
                    "hash": hashlib.sha256(value).hexdigest()[:16]
                }
            else:
                sanitized[key] = value
                
        return sanitized
    
    def _sanitize_outputs(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize outputs, keeping more detail than inputs"""
        # Similar to inputs but might keep more data
        return self._sanitize_inputs(outputs)
    
    def _calculate_context_hash(self) -> str:
        """Calculate hash of current execution context"""
        if not self.current_execution:
            return "no_context"
            
        # Hash based on tools called so far
        tool_sequence = [
            (tc.tool_name, tc.success) 
            for tc in self.current_execution["tool_calls"]
        ]
        
        return hashlib.sha256(
            json.dumps(tool_sequence).encode()
        ).hexdigest()[:8]
    
    def _save_execution_path(self, execution_path: ExecutionPath):
        """Save execution path to disk"""
        
        filename = f"execution_{execution_path.execution_id}.json"
        filepath = self.storage_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                "execution_path": execution_path.__dict__,
                "workflow_spec": execution_path.to_workflow_spec()
            }, f, indent=2, default=str)
            
        print(f"💾 Execution path saved: {filepath}")


class WorkflowCrystallizer:
    """
    Converts captured execution paths into refined workflows.
    Can also merge multiple executions into a generalized workflow.
    """
    
    def __init__(self, capture_dir: str = "kgas_execution_paths"):
        self.capture_dir = Path(capture_dir)
        self.workflow_dir = Path("kgas_crystallized_workflows")
        self.workflow_dir.mkdir(exist_ok=True)
        
    def crystallize_execution(self, 
                            execution_id: str,
                            workflow_name: str,
                            description: str = None,
                            refinements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Convert a single execution into a refined workflow"""
        
        # Load execution path
        execution_file = self.capture_dir / f"execution_{execution_id}.json"
        with open(execution_file, 'r') as f:
            data = json.load(f)
            
        execution_path = ExecutionPath(**data["execution_path"])
        
        # Generate base workflow
        workflow = execution_path.to_workflow_spec(workflow_name, description)
        
        # Apply refinements
        if refinements:
            workflow = self._apply_refinements(workflow, refinements)
            
        # Add crystallization metadata
        workflow["crystallization"] = {
            "source_execution": execution_id,
            "crystallized_at": datetime.now().isoformat(),
            "refinements_applied": refinements is not None
        }
        
        # Save crystallized workflow
        self._save_workflow(workflow)
        
        return workflow
    
    def merge_executions(self,
                        execution_ids: List[str],
                        workflow_name: str,
                        strategy: str = "common_path") -> Dict[str, Any]:
        """Merge multiple executions into a generalized workflow"""
        
        executions = []
        for exec_id in execution_ids:
            execution_file = self.capture_dir / f"execution_{exec_id}.json"
            with open(execution_file, 'r') as f:
                data = json.load(f)
                executions.append(ExecutionPath(**data["execution_path"]))
        
        if strategy == "common_path":
            workflow = self._merge_common_path(executions)
        elif strategy == "union":
            workflow = self._merge_union(executions)
        elif strategy == "intersection":
            workflow = self._merge_intersection(executions)
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
            
        workflow["name"] = workflow_name
        workflow["crystallization"] = {
            "source_executions": execution_ids,
            "merge_strategy": strategy,
            "crystallized_at": datetime.now().isoformat()
        }
        
        self._save_workflow(workflow)
        return workflow
    
    def _apply_refinements(self, 
                          workflow: Dict[str, Any], 
                          refinements: Dict[str, Any]) -> Dict[str, Any]:
        """Apply manual refinements to a workflow"""
        
        # Example refinements:
        # - Add parameter ranges instead of fixed values
        # - Add error handling steps
        # - Specify parallelization hints
        # - Add validation steps
        
        if "parameter_ranges" in refinements:
            # Replace fixed values with ranges
            for phase in workflow["phases"]:
                for tool in phase.get("tools", []):
                    tool_name = tool["tool"]
                    if tool_name in refinements["parameter_ranges"]:
                        ranges = refinements["parameter_ranges"][tool_name]
                        for param, range_spec in ranges.items():
                            if param in tool["inputs"]:
                                tool["inputs"][param] = {
                                    "type": "range",
                                    "min": range_spec["min"],
                                    "max": range_spec["max"],
                                    "default": tool["inputs"][param]
                                }
        
        if "add_validation" in refinements:
            # Add validation steps after specified tools
            pass
            
        return workflow
    
    def _merge_common_path(self, executions: List[ExecutionPath]) -> Dict[str, Any]:
        """Find common execution path across multiple runs"""
        
        # Find tools that appear in all executions
        all_tools = []
        for exec_path in executions:
            exec_tools = [(tc.tool_name, tc.inputs) for tc in exec_path.tool_calls]
            all_tools.append(exec_tools)
            
        # Find common subsequence
        common_tools = self._find_common_subsequence(all_tools)
        
        # Build workflow from common path
        workflow = {
            "id": f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "version": "1.0.0",
            "phases": [{
                "id": "common_path",
                "name": "Common Execution Path",
                "tools": [
                    {"tool": tool_name, "inputs": inputs}
                    for tool_name, inputs in common_tools
                ]
            }]
        }
        
        return workflow
    
    def _find_common_subsequence(self, sequences: List[List[Tuple]]) -> List[Tuple]:
        """Find longest common subsequence of tools"""
        # Simplified - in practice would use dynamic programming
        if not sequences:
            return []
            
        # For now, return intersection in order
        common = []
        for item in sequences[0]:
            if all(item in seq for seq in sequences[1:]):
                common.append(item)
                
        return common
    
    def _merge_union(self, executions: List[ExecutionPath]) -> Dict[str, Any]:
        """Create workflow that includes all tools from all executions"""
        # Implementation would merge all unique tools
        pass
    
    def _merge_intersection(self, executions: List[ExecutionPath]) -> Dict[str, Any]:
        """Create workflow with only tools common to all executions"""
        # Implementation would find strict intersection
        pass
    
    def _save_workflow(self, workflow: Dict[str, Any]):
        """Save crystallized workflow"""
        
        filename = f"{workflow['id']}.yaml"
        filepath = self.workflow_dir / filename
        
        with open(filepath, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False)
            
        print(f"💎 Crystallized workflow saved: {filepath}")


# Integration with Claude Code execution
class ClaudeCodeWithCapture:
    """
    Wrapper that captures execution paths from Claude Code runs.
    This would integrate with the actual Claude Code SDK.
    """
    
    def __init__(self):
        self.capture = ExecutionCapture()
        
    async def execute_with_capture(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Execute Claude Code request while capturing the path"""
        
        # Start capture
        execution_id = self.capture.start_capture(prompt, kwargs)
        
        print(f"🎯 Starting exploration with capture: {execution_id}")
        
        # In real implementation, would hook into Claude Code SDK
        # to capture actual tool calls
        
        # Mock execution for demonstration
        self.capture.capture_tool_call(
            tool_name="mcp__kgas__load_pdf_document",
            inputs={"file_path": "kunst_paper.pdf"},
            outputs={"text": "paper content", "pages": 30},
            duration_ms=1250,
            success=True
        )
        
        self.capture.capture_decision(
            decision_point="chunk_size_selection",
            choice="1000",
            alternatives=["500", "1000", "2000"],
            rationale="Document has medium-length paragraphs"
        )
        
        self.capture.capture_tool_call(
            tool_name="mcp__kgas__chunk_text",
            inputs={"text": "paper content", "size": 1000},
            outputs={"chunks": ["chunk1", "chunk2", "chunk3"]},
            duration_ms=800,
            success=True
        )
        
        # Capture parallel execution
        self.capture.capture_parallel_execution([2, 3, 4])  # Next 3 tools in parallel
        
        # Complete capture
        final_outputs = {
            "theory_schema": {"type": "psychological", "factors": 5},
            "analysis_complete": True
        }
        
        execution_path = self.capture.complete_capture(final_outputs)
        
        print(f"✅ Exploration complete, path captured: {execution_path.calculate_hash()[:8]}")
        
        return {
            "execution_id": execution_id,
            "execution_path": execution_path,
            "results": final_outputs
        }


# Example usage
async def demonstrate_exploration_to_strict():
    """Demonstrate the exploration to strict workflow process"""
    
    print("🔬 KGAS Exploration-to-Strict Demonstration")
    print("="*60)
    
    # 1. Run exploration with Claude Code
    print("\n1️⃣ Running exploration with full Claude Code autonomy...")
    
    executor = ClaudeCodeWithCapture()
    result = await executor.execute_with_capture(
        prompt="Analyze Kunst paper and apply theory to Carter speech",
        mode="exploration",
        capture_execution=True
    )
    
    execution_id = result["execution_id"]
    print(f"   Execution ID: {execution_id}")
    print(f"   Path hash: {result['execution_path'].calculate_hash()[:8]}")
    
    # 2. Crystallize into workflow
    print("\n2️⃣ Crystallizing execution into reproducible workflow...")
    
    crystallizer = WorkflowCrystallizer()
    workflow = crystallizer.crystallize_execution(
        execution_id=execution_id,
        workflow_name="Kunst Theory Application",
        description="Apply psychological theory framework to political speech",
        refinements={
            "parameter_ranges": {
                "mcp__kgas__chunk_text": {
                    "size": {"min": 500, "max": 2000}
                }
            }
        }
    )
    
    print(f"   Workflow ID: {workflow['id']}")
    print(f"   Phases: {len(workflow['phases'])}")
    print(f"   Total tools: {sum(len(p.get('tools', [])) for p in workflow['phases'])}")
    
    # 3. Re-run in strict mode
    print("\n3️⃣ Re-running crystallized workflow in STRICT mode...")
    print(f"   Using workflow: {workflow['id']}")
    print(f"   Hash: {workflow['execution_hash'][:8]}")
    print("   🔒 This execution will be 100% reproducible")
    
    # 4. Show workflow reuse
    print("\n4️⃣ Workflow can now be:")
    print("   ✅ Version controlled (Git)")
    print("   ✅ Shared with collaborators")
    print("   ✅ Modified with parameter ranges")
    print("   ✅ Used in papers with DOI")
    print("   ✅ Re-run exactly by reviewers")
    
    print("\n📊 Benefits:")
    print("   • Exploration preserves all paths")
    print("   • Successful paths become workflows")
    print("   • Full reproducibility when needed")
    print("   • Progressive formalization of methods")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demonstrate_exploration_to_strict())