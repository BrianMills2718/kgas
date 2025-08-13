"""
Enhanced Reasoning Trace System - Data Models

Implements hierarchical reasoning capture for KGAS decision tracking with 4-level 
decision hierarchy: System, Agent, Tool, and LLM levels.

NO MOCKS - Production-ready implementation for comprehensive decision reasoning traces.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DecisionLevel(Enum):
    """Decision hierarchy levels for reasoning capture"""
    SYSTEM = "system"          # High-level system decisions
    AGENT = "agent"            # Agent workflow and tool selection decisions  
    TOOL = "tool"              # Individual tool execution decisions
    LLM = "llm"                # LLM reasoning and response generation


class ReasoningType(Enum):
    """Types of reasoning captured"""
    WORKFLOW_PLANNING = "workflow_planning"        # How workflow was planned
    TOOL_SELECTION = "tool_selection"             # Why specific tools were chosen
    PARAMETER_SELECTION = "parameter_selection"    # How tool parameters were set
    MODE_SELECTION = "mode_selection"             # Cross-modal analysis decisions
    ERROR_HANDLING = "error_handling"             # How errors were handled
    OPTIMIZATION = "optimization"                 # Performance optimization decisions
    VALIDATION = "validation"                     # Validation and quality decisions
    REASONING_CHAIN = "reasoning_chain"           # Chain-of-thought reasoning
    FALLBACK_DECISION = "fallback_decision"       # Fallback strategy decisions


@dataclass
class ReasoningStep:
    """Individual reasoning step within a trace"""
    
    step_id: str = field(default_factory=lambda: f"step_{uuid.uuid4().hex[:12]}")
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    decision_level: DecisionLevel = DecisionLevel.SYSTEM
    reasoning_type: ReasoningType = ReasoningType.WORKFLOW_PLANNING
    
    # Core reasoning data
    decision_point: str = ""                    # What decision was being made
    context: Dict[str, Any] = field(default_factory=dict)         # Context available for decision
    options_considered: List[Dict[str, Any]] = field(default_factory=list)  # What options were evaluated
    decision_made: Dict[str, Any] = field(default_factory=dict)   # Final decision
    reasoning_text: str = ""                    # Natural language reasoning
    confidence_score: float = 0.0              # Confidence in decision (0.0-1.0)
    
    # Relationships
    parent_step_id: Optional[str] = None        # Parent reasoning step
    child_step_ids: List[str] = field(default_factory=list)       # Child reasoning steps
    
    # Metadata
    duration_ms: Optional[int] = None           # Time taken for decision
    metadata: Dict[str, Any] = field(default_factory=dict)        # Additional metadata
    error_occurred: bool = False                # Whether error occurred
    error_message: Optional[str] = None         # Error details if any

    def add_child_step(self, child_step: 'ReasoningStep') -> None:
        """Add a child reasoning step"""
        child_step.parent_step_id = self.step_id
        if child_step.step_id not in self.child_step_ids:
            self.child_step_ids.append(child_step.step_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        # Convert enums to strings
        result['decision_level'] = self.decision_level.value
        result['reasoning_type'] = self.reasoning_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningStep':
        """Create from dictionary"""
        # Convert string enums back to enum objects
        if 'decision_level' in data:
            data['decision_level'] = DecisionLevel(data['decision_level'])
        if 'reasoning_type' in data:
            data['reasoning_type'] = ReasoningType(data['reasoning_type'])
        
        return cls(**data)


@dataclass
class ReasoningTrace:
    """Complete reasoning trace for a workflow or operation"""
    
    trace_id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:16]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Trace identification
    operation_type: str = ""                    # Type of operation (workflow, tool_execution, etc.)
    operation_id: Optional[str] = None          # Associated operation ID
    session_id: Optional[str] = None            # User/system session ID
    
    # Trace content
    root_step_ids: List[str] = field(default_factory=list)        # Top-level reasoning steps
    all_steps: Dict[str, ReasoningStep] = field(default_factory=dict)  # All steps by ID
    
    # Summary information
    total_steps: int = 0
    total_duration_ms: Optional[int] = None
    overall_confidence: float = 0.0
    success: bool = True
    
    # Context and metadata
    initial_context: Dict[str, Any] = field(default_factory=dict)
    final_outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Completion status
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

    def add_step(self, step: ReasoningStep, parent_step_id: Optional[str] = None) -> str:
        """Add a reasoning step to the trace"""
        
        # Store step
        self.all_steps[step.step_id] = step
        
        # Handle parent-child relationships
        if parent_step_id and parent_step_id in self.all_steps:
            parent_step = self.all_steps[parent_step_id]
            parent_step.add_child_step(step)
        else:
            # This is a root step
            if step.step_id not in self.root_step_ids:
                self.root_step_ids.append(step.step_id)
        
        # Update trace statistics
        self.total_steps = len(self.all_steps)
        self._update_statistics()
        
        logger.debug(f"Added reasoning step {step.step_id} to trace {self.trace_id}")
        return step.step_id
    
    def get_step(self, step_id: str) -> Optional[ReasoningStep]:
        """Get a specific reasoning step"""
        return self.all_steps.get(step_id)
    
    def get_steps_by_level(self, level: DecisionLevel) -> List[ReasoningStep]:
        """Get all steps at a specific decision level"""
        return [step for step in self.all_steps.values() if step.decision_level == level]
    
    def get_steps_by_type(self, reasoning_type: ReasoningType) -> List[ReasoningStep]:
        """Get all steps of a specific reasoning type"""
        return [step for step in self.all_steps.values() if step.reasoning_type == reasoning_type]
    
    def get_reasoning_chain(self, step_id: str) -> List[ReasoningStep]:
        """Get the complete reasoning chain leading to a step"""
        chain = []
        current_step = self.get_step(step_id)
        
        while current_step:
            chain.insert(0, current_step)  # Insert at beginning for correct order
            parent_id = current_step.parent_step_id
            current_step = self.get_step(parent_id) if parent_id else None
        
        return chain
    
    def get_step_children(self, step_id: str) -> List[ReasoningStep]:
        """Get all child steps of a specific step"""
        step = self.get_step(step_id)
        if not step:
            return []
        
        return [self.all_steps[child_id] for child_id in step.child_step_ids 
                if child_id in self.all_steps]
    
    def complete_trace(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark trace as completed"""
        self.completed_at = datetime.now().isoformat()
        self.success = success
        self.error_message = error_message
        self._update_statistics()
        
        logger.info(f"Completed reasoning trace {self.trace_id} (success={success}, steps={self.total_steps})")
    
    def _update_statistics(self) -> None:
        """Update trace statistics"""
        if not self.all_steps:
            return
        
        # Calculate total duration
        durations = [step.duration_ms for step in self.all_steps.values() 
                    if step.duration_ms is not None]
        self.total_duration_ms = sum(durations) if durations else None
        
        # Calculate overall confidence (average of all steps)
        confidences = [step.confidence_score for step in self.all_steps.values()]
        self.overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = {
            'trace_id': self.trace_id,
            'created_at': self.created_at,
            'operation_type': self.operation_type,
            'operation_id': self.operation_id,
            'session_id': self.session_id,
            'root_step_ids': self.root_step_ids,
            'all_steps': {step_id: step.to_dict() for step_id, step in self.all_steps.items()},
            'total_steps': self.total_steps,
            'total_duration_ms': self.total_duration_ms,
            'overall_confidence': self.overall_confidence,
            'success': self.success,
            'initial_context': self.initial_context,
            'final_outputs': self.final_outputs,
            'metadata': self.metadata,
            'completed_at': self.completed_at,
            'error_message': self.error_message
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningTrace':
        """Create from dictionary"""
        # Convert step dictionaries back to ReasoningStep objects
        all_steps = {}
        if 'all_steps' in data:
            for step_id, step_data in data['all_steps'].items():
                all_steps[step_id] = ReasoningStep.from_dict(step_data)
        
        # Create trace without all_steps first
        trace_data = data.copy()
        trace_data.pop('all_steps', None)
        
        trace = cls(**trace_data)
        trace.all_steps = all_steps
        
        return trace


# Factory functions for common reasoning step types

def create_workflow_planning_step(
    decision_point: str,
    context: Dict[str, Any],
    workflow_generated: Dict[str, Any],
    reasoning_text: str,
    confidence: float = 0.8
) -> ReasoningStep:
    """Create a workflow planning reasoning step"""
    return ReasoningStep(
        decision_level=DecisionLevel.AGENT,
        reasoning_type=ReasoningType.WORKFLOW_PLANNING,
        decision_point=decision_point,
        context=context,
        decision_made=workflow_generated,
        reasoning_text=reasoning_text,
        confidence_score=confidence
    )


def create_tool_selection_step(
    decision_point: str,
    available_tools: List[str],
    selected_tool: str,
    reasoning_text: str,
    confidence: float = 0.8
) -> ReasoningStep:
    """Create a tool selection reasoning step"""
    return ReasoningStep(
        decision_level=DecisionLevel.AGENT,
        reasoning_type=ReasoningType.TOOL_SELECTION,
        decision_point=decision_point,
        context={"available_tools": available_tools},
        options_considered=[{"tool": tool} for tool in available_tools],
        decision_made={"selected_tool": selected_tool},
        reasoning_text=reasoning_text,
        confidence_score=confidence
    )


def create_llm_reasoning_step(
    decision_point: str,
    prompt: str,
    llm_response: str,
    reasoning_text: str,
    confidence: float = 0.9
) -> ReasoningStep:
    """Create an LLM reasoning step"""
    return ReasoningStep(
        decision_level=DecisionLevel.LLM,
        reasoning_type=ReasoningType.REASONING_CHAIN,
        decision_point=decision_point,
        context={"prompt": prompt},
        decision_made={"response": llm_response},
        reasoning_text=reasoning_text,
        confidence_score=confidence
    )


def create_error_handling_step(
    decision_point: str,
    error_context: Dict[str, Any],
    fallback_decision: Dict[str, Any],
    reasoning_text: str,
    confidence: float = 0.6
) -> ReasoningStep:
    """Create an error handling reasoning step"""
    return ReasoningStep(
        decision_level=DecisionLevel.SYSTEM,
        reasoning_type=ReasoningType.ERROR_HANDLING,
        decision_point=decision_point,
        context=error_context,
        decision_made=fallback_decision,
        reasoning_text=reasoning_text,
        confidence_score=confidence,
        error_occurred=True
    )