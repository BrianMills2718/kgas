"""
Field-based matching approach (current method) for comparison.
"""

from typing import Dict, Any, List, Set
from mock_tools import (
    MockT03TextLoader,
    MockT15ATextChunker,
    MockT23CEntityExtractor,
    MockT68PageRank
)


class FieldMatcher:
    """Traditional field name matching approach."""
    
    def __init__(self):
        # Manually define what each tool expects and produces
        self.tool_interfaces = {
            "T03": {
                "inputs": {"file_path"},
                "outputs": {"content", "metadata"}
            },
            "T15A": {
                "inputs": {"text"},  # Note: expects "text" not "content"
                "outputs": {"chunks", "num_chunks"}
            },
            "T23C": {
                "inputs": {"text", "chunks"},  # Can accept either
                "outputs": {"entities", "relationships", "num_entities"}
            },
            "T68": {
                "inputs": {"graph"},
                "outputs": {"scores", "num_nodes"}
            }
        }
    
    def can_connect(self, tool1_id: str, tool2_id: str) -> bool:
        """
        Check if tool1 can connect to tool2 using field name matching.
        
        This is the naive approach: just check if any output field
        matches any input field.
        """
        if tool1_id not in self.tool_interfaces:
            return False
        if tool2_id not in self.tool_interfaces:
            return False
        
        tool1_outputs = self.tool_interfaces[tool1_id]["outputs"]
        tool2_inputs = self.tool_interfaces[tool2_id]["inputs"]
        
        # Check if any output field matches any input field
        common_fields = tool1_outputs & tool2_inputs
        return len(common_fields) > 0
    
    def get_field_mapping(self, tool1_id: str, tool2_id: str) -> Dict[str, str]:
        """Get field mapping between tools."""
        if not self.can_connect(tool1_id, tool2_id):
            return {}
        
        tool1_outputs = self.tool_interfaces[tool1_id]["outputs"]
        tool2_inputs = self.tool_interfaces[tool2_id]["inputs"]
        
        # Find matching fields
        mapping = {}
        for output_field in tool1_outputs:
            if output_field in tool2_inputs:
                mapping[output_field] = output_field
        
        return mapping
    
    def execute_pipeline(self, tools: List[str], input_data: Dict[str, Any]) -> Any:
        """
        Try to execute a pipeline using field matching.
        
        This will fail for T03 → T15A because:
        - T03 outputs "content"
        - T15A expects "text"
        """
        current_data = input_data
        
        tool_instances = {
            "T03": MockT03TextLoader(),
            "T15A": MockT15ATextChunker(),
            "T23C": MockT23CEntityExtractor(),
            "T68": MockT68PageRank()
        }
        
        for i, tool_id in enumerate(tools):
            if tool_id not in tool_instances:
                raise ValueError(f"Unknown tool: {tool_id}")
            
            tool = tool_instances[tool_id]
            
            # Try to execute
            try:
                result = tool.execute(current_data)
                current_data = result
            except Exception as e:
                # This will happen for T03 → T15A
                return {
                    "error": f"Pipeline failed at {tool_id}",
                    "reason": str(e),
                    "step": i
                }
        
        return current_data


class ImprovedFieldMatcher(FieldMatcher):
    """
    Improved field matcher with manual mappings.
    
    This represents the "adapter" approach where we manually
    define field mappings.
    """
    
    def __init__(self):
        super().__init__()
        
        # Manual field mappings (band-aid solution)
        self.manual_mappings = {
            ("T03", "T15A"): {"content": "text"},  # Map content to text
            ("T15A", "T23C"): {"chunks": "chunks"},  # Direct match
            ("T03", "T23C"): {"content": "text"},  # Map content to text
        }
    
    def execute_pipeline_with_adapters(self, tools: List[str], input_data: Dict[str, Any]) -> Any:
        """Execute pipeline with manual field adapters."""
        current_data = input_data
        
        tool_instances = {
            "T03": MockT03TextLoader(),
            "T15A": MockT15ATextChunker(),
            "T23C": MockT23CEntityExtractor(),
            "T68": MockT68PageRank()
        }
        
        for i, tool_id in enumerate(tools):
            if tool_id not in tool_instances:
                raise ValueError(f"Unknown tool: {tool_id}")
            
            tool = tool_instances[tool_id]
            
            # Apply field mapping if we're not at the first tool
            if i > 0:
                prev_tool = tools[i-1]
                mapping_key = (prev_tool, tool_id)
                
                if mapping_key in self.manual_mappings:
                    # Apply manual mapping
                    mapped_data = {}
                    for out_field, in_field in self.manual_mappings[mapping_key].items():
                        if out_field in current_data:
                            mapped_data[in_field] = current_data[out_field]
                    # Keep other fields
                    for key, value in current_data.items():
                        if key not in mapped_data:
                            mapped_data[key] = value
                    current_data = mapped_data
            
            # Execute tool
            try:
                result = tool.execute(current_data)
                current_data = result
            except Exception as e:
                return {
                    "error": f"Pipeline failed at {tool_id}",
                    "reason": str(e),
                    "step": i
                }
        
        return current_data