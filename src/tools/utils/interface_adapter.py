"""
Tool Interface Adapter

Provides adapters to handle data format mismatches between tools.
This is a systematic solution to interface compatibility issues.
"""

from typing import Dict, List, Any, Union
from src.tools.base_tool import ToolResult


class InterfaceAdapter:
    """Adapts data formats between tools for compatibility"""
    
    @staticmethod
    def entities_to_mentions(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert T23c Entity format to T31 Mention format.
        
        Args:
            entities: List of Entity objects from T23c
            
        Returns:
            List of Mention-like objects for T31
        """
        mentions = []
        for entity in entities:
            mention = {
                "text": entity.get("canonical_name", entity.get("text", "")),
                "entity_type": entity.get("entity_type", "UNKNOWN"),
                "confidence": entity.get("confidence", 0.8),
                "entity_id": entity.get("entity_id"),
                # Add position info if available
                "start": entity.get("start_pos", 0),
                "end": entity.get("end_pos", len(entity.get("canonical_name", "")))
            }
            mentions.append(mention)
        return mentions
    
    @staticmethod
    def dict_to_tool_result(result_dict: Dict[str, Any], tool_id: str) -> ToolResult:
        """
        Convert dictionary output to proper ToolResult.
        
        Args:
            result_dict: Dictionary output from tool
            tool_id: ID of the tool
            
        Returns:
            Properly formatted ToolResult
        """
        # Extract common fields if present
        status = result_dict.get("status", "success")
        error_message = result_dict.get("error", result_dict.get("error_message"))
        
        # Remove status/error from data to avoid duplication
        data = {k: v for k, v in result_dict.items() 
                if k not in ["status", "error", "error_message"]}
        
        return ToolResult(
            tool_id=tool_id,
            status=status,
            data=data,
            error_message=error_message,
            execution_time=0.0,  # Would need to track this
            memory_used=0
        )
    
    @staticmethod
    def texts_to_chunks(texts: List[str], source_ref: str = "unknown") -> List[Dict[str, Any]]:
        """
        Convert simple text list to chunk format for VectorEmbedder.
        
        Args:
            texts: List of text strings
            source_ref: Source reference
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        for i, text in enumerate(texts):
            chunk = {
                "chunk_id": f"chunk_{source_ref}_{i}",
                "text": text,
                "metadata": {
                    "source": source_ref,
                    "index": i
                }
            }
            chunks.append(chunk)
        return chunks
    
    @staticmethod
    def adapt_vector_input(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt various input formats for VectorEmbedder.
        
        Args:
            input_data: Input in various formats
            
        Returns:
            Standardized chunk format
        """
        # If already in chunk format, return as-is
        if "chunks" in input_data:
            return input_data
        
        # Convert from texts format
        if "texts" in input_data:
            chunks = InterfaceAdapter.texts_to_chunks(
                input_data["texts"],
                input_data.get("source_ref", "unknown")
            )
            return {
                "chunks": chunks,
                "collection_name": input_data.get("collection_name", "default")
            }
        
        # Convert from single text
        if "text" in input_data:
            chunks = InterfaceAdapter.texts_to_chunks(
                [input_data["text"]],
                input_data.get("source_ref", "unknown")
            )
            return {
                "chunks": chunks,
                "collection_name": input_data.get("collection_name", "default")
            }
        
        # Unknown format
        raise ValueError(f"Unknown vector input format: {list(input_data.keys())}")
    
    @staticmethod
    def validate_tool_chain(tool_outputs: List[Any], tool_inputs: List[Dict[str, Any]]) -> List[str]:
        """
        Validate that tool outputs can feed into next tool inputs.
        
        Args:
            tool_outputs: List of outputs from tools
            tool_inputs: List of expected inputs for next tools
            
        Returns:
            List of compatibility issues found
        """
        issues = []
        
        for i in range(len(tool_outputs) - 1):
            output = tool_outputs[i]
            expected_input = tool_inputs[i + 1]
            
            # Check if output format matches expected input
            if isinstance(output, ToolResult):
                output_data = output.data
            else:
                output_data = output
            
            # Check for required fields
            for field in expected_input.get("required", []):
                if field not in output_data:
                    issues.append(
                        f"Tool {i} output missing required field '{field}' "
                        f"for tool {i+1} input"
                    )
        
        return issues


# Convenience functions for common adaptations

def adapt_t23c_to_t31(t23c_output: Union[Dict, ToolResult]) -> Dict[str, Any]:
    """Adapt T23c output for T31 input."""
    if isinstance(t23c_output, ToolResult):
        data = t23c_output.data
    else:
        data = t23c_output
    
    entities = data.get("entities", [])
    mentions = InterfaceAdapter.entities_to_mentions(entities)
    
    return {
        "mentions": mentions,
        "source_refs": data.get("source_refs", ["adapted_from_t23c"])
    }


def fix_tool_result(tool_output: Any, tool_id: str) -> ToolResult:
    """Ensure tool output is a proper ToolResult."""
    if isinstance(tool_output, ToolResult):
        return tool_output
    
    if isinstance(tool_output, dict):
        return InterfaceAdapter.dict_to_tool_result(tool_output, tool_id)
    
    # Wrap other types in ToolResult
    return ToolResult(
        tool_id=tool_id,
        status="success",
        data={"result": tool_output},
        execution_time=0.0,
        memory_used=0
    )