"""
Enhanced LLM Client with Reasoning Capture

Extends the standard LLM client to capture structured reasoning from LLM responses,
including chain-of-thought processes, decision justifications, and confidence assessments.

NO MOCKS - Production-ready implementation for comprehensive LLM reasoning capture.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import re

from .enhanced_api_client import EnhancedAPIClient
from .reasoning_trace import (
    ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType,
    create_llm_reasoning_step
)
from .reasoning_trace_store import ReasoningTraceStore

logger = logging.getLogger(__name__)


class EnhancedReasoningLLMClient:
    """LLM client with structured reasoning capture capabilities"""
    
    def __init__(
        self, 
        base_client: Optional[EnhancedAPIClient] = None,
        reasoning_store: Optional[ReasoningTraceStore] = None,
        capture_reasoning: bool = True
    ):
        """Initialize enhanced reasoning LLM client
        
        Args:
            base_client: Base LLM client (creates one if not provided)
            reasoning_store: Store for reasoning traces (creates one if not provided)
            capture_reasoning: Whether to capture reasoning traces
        """
        # Initialize base LLM client
        if base_client:
            self.base_client = base_client
        else:
            try:
                from .service_manager import get_service_manager
                service_manager = get_service_manager()
                self.base_client = getattr(service_manager, 'enhanced_api_client', None)
                if not self.base_client:
                    self.base_client = EnhancedAPIClient()
            except Exception as e:
                logger.error(f"Failed to initialize base LLM client: {e}")
                self.base_client = EnhancedAPIClient()
        
        # Initialize reasoning store
        if reasoning_store:
            self.reasoning_store = reasoning_store
        else:
            from .reasoning_trace_store import create_reasoning_trace_store
            self.reasoning_store = create_reasoning_trace_store()
        
        self.capture_reasoning = capture_reasoning
        
        # Current trace context
        self.current_trace: Optional[ReasoningTrace] = None
        self.current_step: Optional[ReasoningStep] = None
        
        logger.info(f"Enhanced reasoning LLM client initialized (capture_reasoning={capture_reasoning})")
    
    def start_reasoning_trace(
        self, 
        operation_type: str,
        operation_id: Optional[str] = None,
        session_id: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new reasoning trace
        
        Args:
            operation_type: Type of operation being traced
            operation_id: Associated operation ID
            session_id: Session identifier
            initial_context: Initial context information
            
        Returns:
            Trace ID
        """
        if not self.capture_reasoning:
            return ""
        
        self.current_trace = ReasoningTrace(
            operation_type=operation_type,
            operation_id=operation_id,
            session_id=session_id,
            initial_context=initial_context or {}
        )
        
        logger.debug(f"Started reasoning trace {self.current_trace.trace_id}")
        return self.current_trace.trace_id
    
    def complete_reasoning_trace(
        self, 
        success: bool = True, 
        final_outputs: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[str]:
        """Complete and store the current reasoning trace
        
        Args:
            success: Whether the operation succeeded
            final_outputs: Final outputs from the operation
            error_message: Error message if failed
            
        Returns:
            Trace ID if stored successfully, None otherwise
        """
        if not self.capture_reasoning or not self.current_trace:
            return None
        
        # Complete trace
        self.current_trace.final_outputs = final_outputs or {}
        self.current_trace.complete_trace(success, error_message)
        
        # Store trace
        if self.reasoning_store.store_trace(self.current_trace):
            trace_id = self.current_trace.trace_id
            logger.debug(f"Completed and stored reasoning trace {trace_id}")
            
            # Clear current trace
            self.current_trace = None
            self.current_step = None
            
            return trace_id
        else:
            logger.error(f"Failed to store reasoning trace {self.current_trace.trace_id}")
            return None
    
    def generate_text_with_reasoning(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        decision_point: str = "",
        reasoning_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text with structured reasoning capture
        
        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            decision_point: Description of the decision being made
            reasoning_context: Additional context for reasoning
            **kwargs: Additional arguments for base client
            
        Returns:
            Response with reasoning information
        """
        start_time = datetime.now()
        
        # Enhance prompt with reasoning instructions
        enhanced_prompt = self._create_reasoning_prompt(
            prompt, decision_point, reasoning_context or {}
        )
        
        # Call base LLM client
        try:
            # Use make_request method from EnhancedAPIClient
            api_response = self.base_client.make_request(
                request_type="chat_completion",
                prompt=enhanced_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Convert APIResponse to expected format
            response = {
                "success": api_response.success,
                "content": api_response.response_data if api_response.success else "",
                "error": api_response.error if not api_response.success else None,
                "model": api_response.service_used,
                "tokens_used": getattr(api_response, 'tokens_used', 0)
            }
            
            if not response.get("success"):
                # Handle LLM failure
                error_msg = response.get("error", "Unknown LLM error")
                self._capture_llm_error_step(prompt, error_msg, decision_point)
                return response
            
            # Extract reasoning from response
            reasoning_info = self._extract_reasoning_from_response(
                response["content"], enhanced_prompt
            )
            
            # Capture reasoning step
            if self.capture_reasoning:
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._capture_llm_reasoning_step(
                    decision_point=decision_point or "LLM text generation",
                    prompt=prompt,
                    enhanced_prompt=enhanced_prompt,
                    response_content=response["content"],
                    reasoning_info=reasoning_info,
                    context=reasoning_context or {},
                    execution_time=execution_time
                )
            
            # Enhance response with reasoning
            response["reasoning_info"] = reasoning_info
            response["decision_point"] = decision_point
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            self._capture_llm_error_step(prompt, str(e), decision_point)
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "reasoning_info": {},
                "decision_point": decision_point
            }
    
    def generate_structured_response(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        decision_point: str = "",
        reasoning_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured response with reasoning capture
        
        Args:
            prompt: Input prompt
            response_schema: Expected response structure
            decision_point: Description of the decision being made
            reasoning_context: Additional context for reasoning
            **kwargs: Additional arguments for LLM client
            
        Returns:
            Structured response with reasoning
        """
        # Create structured prompt
        structured_prompt = self._create_structured_reasoning_prompt(
            prompt, response_schema, decision_point, reasoning_context or {}
        )
        
        # Generate response
        response = self.generate_text_with_reasoning(
            prompt=structured_prompt,
            decision_point=decision_point or "Structured response generation",
            reasoning_context=reasoning_context,
            **kwargs
        )
        
        if response.get("success"):
            # Parse structured response
            try:
                parsed_response = self._parse_structured_response(
                    response["content"], response_schema
                )
                response["structured_data"] = parsed_response
                response["parsing_success"] = True
            except Exception as e:
                logger.error(f"Failed to parse structured response: {e}")
                response["structured_data"] = {}
                response["parsing_success"] = False
                response["parsing_error"] = str(e)
        
        return response
    
    def _create_reasoning_prompt(
        self, 
        original_prompt: str, 
        decision_point: str,
        context: Dict[str, Any]
    ) -> str:
        """Create enhanced prompt with reasoning instructions"""
        
        reasoning_instructions = f"""
You are an expert reasoning system. For every response, you must:

1. **Think Step-by-Step**: Break down your reasoning process
2. **Show Your Work**: Explain how you arrived at your conclusion
3. **Assess Confidence**: Rate your confidence (0.0-1.0) and explain why
4. **Consider Alternatives**: Mention other options you considered
5. **Identify Assumptions**: List any assumptions you're making

**Decision Context**: {decision_point}
**Additional Context**: {json.dumps(context, indent=2) if context else "None"}

**REASONING FORMAT**:
```reasoning
**Step-by-Step Thinking:**
[Your detailed reasoning process]

**Confidence Assessment:** [0.0-1.0]
**Confidence Justification:** [Why this confidence level]

**Alternatives Considered:**
[Other options you evaluated]

**Key Assumptions:**
[Assumptions you're making]
```

**ACTUAL RESPONSE:**
[Your actual response to the prompt]

---

**Original Request:**
{original_prompt}
"""
        
        return reasoning_instructions
    
    def _create_structured_reasoning_prompt(
        self,
        original_prompt: str,
        response_schema: Dict[str, Any],
        decision_point: str,
        context: Dict[str, Any]
    ) -> str:
        """Create structured prompt with reasoning for schema-based responses"""
        
        schema_description = json.dumps(response_schema, indent=2)
        
        structured_prompt = f"""
You are an expert reasoning system that provides structured responses. You must:

1. **Follow the Exact Schema**: Your response must match the provided JSON schema
2. **Include Reasoning**: Provide detailed reasoning for each decision
3. **Assess Confidence**: Include confidence scores where appropriate
4. **Show Alternatives**: Mention other options considered

**Decision Context**: {decision_point}
**Additional Context**: {json.dumps(context, indent=2) if context else "None"}

**REQUIRED RESPONSE SCHEMA**:
```json
{schema_description}
```

**REASONING SECTION** (before your structured response):
```reasoning
**Schema Field Decisions:**
[Explain how you determined each field value]

**Confidence Assessment:** [0.0-1.0]
**Reasoning:** [Why this confidence level]

**Validation Notes:**
[How you ensured schema compliance]
```

**STRUCTURED JSON RESPONSE**:
```json
[Your response following the exact schema]
```

---

**Original Request:**
{original_prompt}
"""
        
        return structured_prompt
    
    def _extract_reasoning_from_response(
        self, 
        response_content: str,
        original_prompt: str
    ) -> Dict[str, Any]:
        """Extract structured reasoning information from LLM response"""
        
        reasoning_info = {
            "step_by_step_thinking": "",
            "confidence_score": 0.0,
            "confidence_justification": "",
            "alternatives_considered": [],
            "key_assumptions": [],
            "reasoning_extracted": False
        }
        
        try:
            # Look for reasoning block
            reasoning_pattern = r"```reasoning\s*(.*?)\s*```"
            reasoning_match = re.search(reasoning_pattern, response_content, re.DOTALL | re.IGNORECASE)
            
            if reasoning_match:
                reasoning_text = reasoning_match.group(1)
                reasoning_info["reasoning_extracted"] = True
                
                # Extract step-by-step thinking
                thinking_pattern = r"\*\*Step-by-Step Thinking:\*\*\s*(.*?)(?=\*\*|$)"
                thinking_match = re.search(thinking_pattern, reasoning_text, re.DOTALL | re.IGNORECASE)
                if thinking_match:
                    reasoning_info["step_by_step_thinking"] = thinking_match.group(1).strip()
                
                # Extract confidence
                confidence_pattern = r"\*\*Confidence Assessment:\*\*\s*([0-9]*\.?[0-9]+)"
                confidence_match = re.search(confidence_pattern, reasoning_text, re.IGNORECASE)
                if confidence_match:
                    try:
                        reasoning_info["confidence_score"] = float(confidence_match.group(1))
                    except ValueError:
                        pass
                
                # Extract confidence justification
                conf_just_pattern = r"\*\*Confidence Justification:\*\*\s*(.*?)(?=\*\*|$)"
                conf_just_match = re.search(conf_just_pattern, reasoning_text, re.DOTALL | re.IGNORECASE)
                if conf_just_match:
                    reasoning_info["confidence_justification"] = conf_just_match.group(1).strip()
                
                # Extract alternatives
                alt_pattern = r"\*\*Alternatives Considered:\*\*\s*(.*?)(?=\*\*|$)"
                alt_match = re.search(alt_pattern, reasoning_text, re.DOTALL | re.IGNORECASE)
                if alt_match:
                    alternatives_text = alt_match.group(1).strip()
                    # Split by lines and clean up
                    alternatives = [alt.strip("- ").strip() for alt in alternatives_text.split('\n') 
                                  if alt.strip() and not alt.startswith('**')]
                    reasoning_info["alternatives_considered"] = alternatives
                
                # Extract assumptions
                assumptions_pattern = r"\*\*Key Assumptions:\*\*\s*(.*?)(?=\*\*|$)"
                assumptions_match = re.search(assumptions_pattern, reasoning_text, re.DOTALL | re.IGNORECASE)
                if assumptions_match:
                    assumptions_text = assumptions_match.group(1).strip()
                    # Split by lines and clean up
                    assumptions = [assump.strip("- ").strip() for assump in assumptions_text.split('\n') 
                                 if assump.strip() and not assump.startswith('**')]
                    reasoning_info["key_assumptions"] = assumptions
                
            else:
                # Try to extract reasoning from unstructured response
                reasoning_info.update(self._extract_fallback_reasoning(response_content))
                
        except Exception as e:
            logger.warning(f"Failed to extract reasoning from LLM response: {e}")
            reasoning_info["extraction_error"] = str(e)
        
        return reasoning_info
    
    def _extract_fallback_reasoning(self, response_content: str) -> Dict[str, Any]:
        """Extract reasoning from unstructured response as fallback"""
        
        fallback_info = {
            "step_by_step_thinking": "",
            "confidence_score": 0.5,  # Default moderate confidence
            "confidence_justification": "Confidence not explicitly stated",
            "alternatives_considered": [],
            "key_assumptions": [],
            "reasoning_extracted": False,
            "fallback_extraction": True
        }
        
        # Look for confidence indicators in text
        confidence_phrases = [
            (r"(very confident|highly confident|certain)", 0.9),
            (r"(confident|sure|believe)", 0.8),
            (r"(likely|probably|tend to think)", 0.7),
            (r"(might|could|possible)", 0.6),
            (r"(uncertain|unsure|not sure)", 0.4),
            (r"(doubt|unlikely|probably not)", 0.3)
        ]
        
        for pattern, score in confidence_phrases:
            if re.search(pattern, response_content, re.IGNORECASE):
                fallback_info["confidence_score"] = score
                fallback_info["confidence_justification"] = f"Inferred from language: {pattern}"
                break
        
        # Look for reasoning indicators
        reasoning_indicators = [
            "because", "since", "given that", "considering", "due to",
            "therefore", "thus", "hence", "consequently", "as a result"
        ]
        
        has_reasoning = any(indicator in response_content.lower() 
                          for indicator in reasoning_indicators)
        
        if has_reasoning:
            fallback_info["step_by_step_thinking"] = "Reasoning present but not structured"
            fallback_info["reasoning_extracted"] = True
        
        return fallback_info
    
    def _parse_structured_response(
        self, 
        response_content: str, 
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse structured JSON response from LLM"""
        
        # Look for JSON block
        json_pattern = r"```json\s*(.*?)\s*```"
        json_match = re.search(json_pattern, response_content, re.DOTALL | re.IGNORECASE)
        
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON-like structure
            json_text = response_content
        
        # Parse JSON
        try:
            parsed_data = json.loads(json_text)
            return parsed_data
        except json.JSONDecodeError as e:
            # Try to clean up and parse again
            cleaned_json = self._clean_json_text(json_text)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse JSON response: {e}")
    
    def _clean_json_text(self, json_text: str) -> str:
        """Clean up JSON text for parsing"""
        # Remove comments
        json_text = re.sub(r'//.*?$', '', json_text, flags=re.MULTILINE)
        
        # Remove trailing commas
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix common issues
        json_text = json_text.strip()
        
        return json_text
    
    def _capture_llm_reasoning_step(
        self,
        decision_point: str,
        prompt: str,
        enhanced_prompt: str,
        response_content: str,
        reasoning_info: Dict[str, Any],
        context: Dict[str, Any],
        execution_time: int
    ) -> None:
        """Capture LLM reasoning as a reasoning step"""
        
        if not self.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.LLM,
            reasoning_type=ReasoningType.REASONING_CHAIN,
            decision_point=decision_point,
            context={
                "original_prompt": prompt,
                "enhanced_prompt_length": len(enhanced_prompt),
                "response_length": len(response_content),
                **context
            },
            decision_made={
                "response": response_content,
                "reasoning_extracted": reasoning_info.get("reasoning_extracted", False)
            },
            reasoning_text=reasoning_info.get("step_by_step_thinking", ""),
            confidence_score=reasoning_info.get("confidence_score", 0.0),
            duration_ms=execution_time,
            metadata={
                "reasoning_info": reasoning_info,
                "alternatives_considered": reasoning_info.get("alternatives_considered", []),
                "key_assumptions": reasoning_info.get("key_assumptions", []),
                "confidence_justification": reasoning_info.get("confidence_justification", "")
            }
        )
        
        # Add to current trace
        parent_step_id = self.current_step.step_id if self.current_step else None
        self.current_trace.add_step(step, parent_step_id)
        
        logger.debug(f"Captured LLM reasoning step: {step.step_id}")
    
    def _capture_llm_error_step(
        self, 
        prompt: str, 
        error_message: str, 
        decision_point: str
    ) -> None:
        """Capture LLM error as reasoning step"""
        
        if not self.current_trace:
            return
        
        step = ReasoningStep(
            decision_level=DecisionLevel.LLM,
            reasoning_type=ReasoningType.ERROR_HANDLING,
            decision_point=decision_point or "LLM call failed",
            context={"prompt": prompt},
            decision_made={"error": error_message},
            reasoning_text=f"LLM call failed: {error_message}",
            confidence_score=0.0,
            error_occurred=True,
            error_message=error_message
        )
        
        # Add to current trace
        parent_step_id = self.current_step.step_id if self.current_step else None
        self.current_trace.add_step(step, parent_step_id)
        
        logger.debug(f"Captured LLM error step: {step.step_id}")
    
    def set_current_step(self, step: ReasoningStep) -> None:
        """Set the current reasoning step for context"""
        self.current_step = step
    
    def get_current_trace_id(self) -> Optional[str]:
        """Get the current trace ID"""
        return self.current_trace.trace_id if self.current_trace else None
    
    def get_reasoning_statistics(self) -> Dict[str, Any]:
        """Get reasoning capture statistics"""
        if self.reasoning_store:
            return self.reasoning_store.get_statistics()
        return {}


# Factory function
def create_enhanced_reasoning_llm_client(
    base_client: Optional[EnhancedAPIClient] = None,
    reasoning_store: Optional[ReasoningTraceStore] = None,
    capture_reasoning: bool = True
) -> EnhancedReasoningLLMClient:
    """Create enhanced reasoning LLM client
    
    Args:
        base_client: Base LLM client
        reasoning_store: Reasoning trace store
        capture_reasoning: Whether to capture reasoning
        
    Returns:
        Enhanced reasoning LLM client
    """
    return EnhancedReasoningLLMClient(
        base_client=base_client,
        reasoning_store=reasoning_store,
        capture_reasoning=capture_reasoning
    )