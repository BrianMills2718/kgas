"""
Extensible Tool Composition Framework
PhD Research: Unified framework for modular tool chaining
"""

from typing import Dict, List, Optional, Any, Type, Tuple, Set, Generic, TypeVar
from dataclasses import dataclass
from abc import ABC, abstractmethod
import networkx as nx
from pydantic import BaseModel

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data_types import DataType
from semantic_types import SemanticType, SemanticTypeRegistry, Domain
from schema_versions import SchemaMigrator
from data_references import ProcessingStrategy, DataReference
from tool_context import ToolContext

# Import BaseTool differently to avoid relative import issue
import base_tool
BaseTool = base_tool.BaseTool

# Define simpler ToolResult for framework
T = TypeVar('T')

class ToolResult(BaseModel, Generic[T]):
    """Simple tool result for the framework with uncertainty"""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    uncertainty: float = 0.0  # 0=certain, 1=uncertain
    reasoning: str = ""       # Why this uncertainty level
    provenance: Optional[Dict[str, Any]] = None  # Execution trace


@dataclass
class ToolCapabilities:
    """Complete capabilities of a tool"""
    # Basic info
    tool_id: str
    name: str
    description: str
    
    # Type information
    input_type: DataType
    output_type: DataType
    semantic_input: Optional[SemanticType] = None
    semantic_output: Optional[SemanticType] = None
    
    # Schema information
    schema_version: str = "1.0.0"
    supported_versions: List[str] = None
    
    # Memory management
    processing_strategy: ProcessingStrategy = ProcessingStrategy.FULL_LOAD
    max_input_size: int = 10 * 1024 * 1024  # 10MB default
    supports_streaming: bool = False
    
    # Multi-input support
    required_params: List[str] = None
    optional_params: List[str] = None
    accepts_context: bool = True
    
    def __post_init__(self):
        if self.supported_versions is None:
            self.supported_versions = [self.schema_version]
        if self.required_params is None:
            self.required_params = []
        if self.optional_params is None:
            self.optional_params = []


class ExtensibleTool(ABC):
    """Base class for tools in the extensible framework"""
    
    @abstractmethod
    def get_capabilities(self) -> ToolCapabilities:
        """Return tool capabilities"""
        pass
    
    @abstractmethod
    def process(self, input_data: Any, context: Optional[ToolContext] = None) -> ToolResult:
        """Process input with optional context"""
        pass
    
    def validate_input(self, input_data: Any, context: Optional[ToolContext] = None) -> bool:
        """Validate input before processing"""
        return True
    
    def estimate_memory(self, input_size: int) -> int:
        """Estimate memory usage for given input size"""
        caps = self.get_capabilities()
        if caps.processing_strategy == ProcessingStrategy.STREAMING:
            return 1024 * 1024  # 1MB buffer
        return input_size


class ToolFramework:
    """
    Unified framework for tool composition.
    
    Integrates:
    - Semantic type checking
    - Schema versioning
    - Memory management
    - Multi-input support
    - Automatic chain discovery
    """
    
    def __init__(self):
        self.tools: Dict[str, ExtensibleTool] = {}
        self.capabilities: Dict[str, ToolCapabilities] = {}
        self.semantic_registry = SemanticTypeRegistry()
        self.schema_migrator = SchemaMigrator()
        self.graph = nx.DiGraph()
        
    def register_tool(self, tool: ExtensibleTool) -> None:
        """
        Register a tool with the framework.
        
        Automatically:
        - Extracts capabilities
        - Registers semantic types
        - Updates compatibility graph
        """
        caps = tool.get_capabilities()
        self.tools[caps.tool_id] = tool
        self.capabilities[caps.tool_id] = caps
        
        # Register semantic types if provided
        if caps.semantic_input:
            self.semantic_registry.register_type(caps.semantic_input)
        if caps.semantic_output:
            self.semantic_registry.register_type(caps.semantic_output)
        
        # Update graph
        self._update_compatibility_graph()
        
        print(f"✅ Registered tool: {caps.tool_id}")
        print(f"   Input: {caps.input_type} ({caps.semantic_input.semantic_tag if caps.semantic_input else 'generic'})")
        print(f"   Output: {caps.output_type} ({caps.semantic_output.semantic_tag if caps.semantic_output else 'generic'})")
    
    def _update_compatibility_graph(self):
        """Update tool compatibility graph"""
        self.graph.clear()
        
        # Add all tools as nodes
        for tool_id in self.tools:
            self.graph.add_node(tool_id)
        
        # Add edges where tools can connect
        for t1_id, t1_caps in self.capabilities.items():
            for t2_id, t2_caps in self.capabilities.items():
                if t1_id != t2_id:
                    if self._can_connect(t1_caps, t2_caps):
                        self.graph.add_edge(t1_id, t2_id)
    
    def _can_connect(self, tool1: ToolCapabilities, tool2: ToolCapabilities) -> bool:
        """Check if two tools can connect"""
        
        # Basic type compatibility
        if tool1.output_type != tool2.input_type:
            return False
        
        # Semantic compatibility
        if tool1.semantic_output and tool2.semantic_input:
            compat, _ = tool1.semantic_output.is_compatible_with(tool2.semantic_input)
            if not compat:
                return False
        
        # Schema compatibility (can we migrate?)
        if tool1.schema_version != tool2.schema_version:
            if not self.schema_migrator.can_migrate(tool1.schema_version, tool2.schema_version):
                return False
        
        return True
    
    def find_chains(self, 
                   start_type: DataType,
                   end_type: DataType,
                   domain: Optional[Domain] = None,
                   max_memory: Optional[int] = None) -> List[List[str]]:
        """
        Find all valid tool chains.
        
        Args:
            start_type: Input data type
            end_type: Desired output type
            domain: Optional domain constraint
            max_memory: Optional memory constraint
            
        Returns:
            List of tool chains (each chain is a list of tool IDs)
        """
        chains = []
        
        # Find tools that accept start_type
        start_tools = [
            tid for tid, caps in self.capabilities.items()
            if caps.input_type == start_type
            and (not domain or not caps.semantic_input or caps.semantic_input.context.domain == domain)
        ]
        
        # Find tools that produce end_type
        end_tools = [
            tid for tid, caps in self.capabilities.items()
            if caps.output_type == end_type
            and (not domain or not caps.semantic_output or caps.semantic_output.context.domain == domain)
        ]
        
        # Find paths
        for start_tool in start_tools:
            for end_tool in end_tools:
                if start_tool == end_tool:
                    chains.append([start_tool])
                else:
                    try:
                        paths = list(nx.all_simple_paths(self.graph, start_tool, end_tool))
                        chains.extend(paths)
                    except nx.NetworkXNoPath:
                        continue
        
        # Filter by memory if specified
        if max_memory:
            chains = [c for c in chains if self._estimate_chain_memory(c) <= max_memory]
        
        return chains
    
    def _estimate_chain_memory(self, chain: List[str]) -> int:
        """Estimate maximum memory usage for a chain"""
        max_memory = 0
        for tool_id in chain:
            tool = self.tools[tool_id]
            caps = self.capabilities[tool_id]
            if caps.processing_strategy == ProcessingStrategy.FULL_LOAD:
                max_memory = max(max_memory, caps.max_input_size)
            else:
                max_memory = max(max_memory, 1024 * 1024)  # 1MB for streaming
        return max_memory
    
    def execute_chain(self,
                     chain: List[str],
                     input_data: Any,
                     context: Optional[ToolContext] = None) -> ToolResult:
        """
        Execute a tool chain.
        
        Handles:
        - Schema migration between tools
        - Memory management (streaming/references)
        - Context passing
        - Error handling
        """
        if not context:
            context = ToolContext()
        
        current_data = input_data
        current_version = "1.0.0"
        
        for i, tool_id in enumerate(chain):
            tool = self.tools[tool_id]
            caps = self.capabilities[tool_id]
            
            print(f"\n🔧 Executing {tool_id} ({i+1}/{len(chain)})")
            
            # Handle schema migration if needed
            if current_version != caps.schema_version:
                if hasattr(current_data, '_version'):
                    print(f"   📄 Migrating schema {current_version} → {caps.schema_version}")
                    current_data = self.schema_migrator.migrate(current_data, caps.schema_version)
                    current_version = caps.schema_version
            
            # Handle memory management
            if caps.processing_strategy == ProcessingStrategy.STREAMING:
                print(f"   💾 Using streaming strategy")
                # Tool will handle streaming internally
            
            # Execute tool
            try:
                result = tool.process(current_data, context)
                
                if not result.success:
                    print(f"   ❌ Failed: {result.error}")
                    return result
                
                current_data = result.data
                
                # Update version if output has one
                if hasattr(current_data, '_version'):
                    current_version = current_data._version
                
                print(f"   ✅ Success")
                
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                return ToolResult(success=False, error=str(e))
        
        return ToolResult(success=True, data=current_data)
    
    def add_tool_simple(self, 
                       tool_class: Type[BaseTool],
                       semantic_input: Optional[SemanticType] = None,
                       semantic_output: Optional[SemanticType] = None,
                       **kwargs) -> None:
        """
        Simple method to add a tool to the framework.
        
        Example:
            framework.add_tool_simple(
                TextLoader,
                semantic_output=MEDICAL_RECORDS
            )
        """
        # Create wrapper that adapts BaseTool to ExtensibleTool
        class ToolAdapter(ExtensibleTool):
            def __init__(self):
                self.base_tool = tool_class(**kwargs)
            
            def get_capabilities(self) -> ToolCapabilities:
                return ToolCapabilities(
                    tool_id=self.base_tool.tool_id,
                    name=getattr(self.base_tool, 'name', self.base_tool.tool_id),
                    description=getattr(self.base_tool, 'description', ''),
                    input_type=self.base_tool.input_type,
                    output_type=self.base_tool.output_type,
                    semantic_input=semantic_input,
                    semantic_output=semantic_output,
                    schema_version=getattr(self.base_tool, 'version', '1.0.0')
                )
            
            def process(self, input_data: Any, context: Optional[ToolContext] = None) -> ToolResult:
                # Use context if tool supports it
                if context and hasattr(self.base_tool, 'process_with_context'):
                    return self.base_tool.process_with_context(input_data, context)
                return self.base_tool.process(input_data)
        
        adapter = ToolAdapter()
        self.register_tool(adapter)
    
    def describe_chain(self, chain: List[str]) -> str:
        """Get human-readable description of a chain"""
        descriptions = []
        for i, tool_id in enumerate(chain):
            caps = self.capabilities[tool_id]
            
            desc = f"{i+1}. {caps.name}"
            if caps.semantic_input:
                desc += f" (expects {caps.semantic_input.semantic_tag})"
            if caps.semantic_output:
                desc += f" → {caps.semantic_output.semantic_tag}"
            
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def validate_chain(self, chain: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate that a chain can execute"""
        
        if not chain:
            return False, "Empty chain"
        
        for i in range(len(chain) - 1):
            t1_caps = self.capabilities[chain[i]]
            t2_caps = self.capabilities[chain[i+1]]
            
            if not self._can_connect(t1_caps, t2_caps):
                return False, f"Cannot connect {chain[i]} to {chain[i+1]}"
        
        return True, None


# Example: Creating a medical pipeline tool
class MedicalTextAnalyzer(ExtensibleTool):
    """Example of how to create a framework-compatible tool"""
    
    def get_capabilities(self) -> ToolCapabilities:
        from semantic_types import MEDICAL_RECORDS, MEDICAL_ENTITIES
        
        return ToolCapabilities(
            tool_id="MedicalTextAnalyzer",
            name="Medical Text Analyzer",
            description="Extract medical entities from clinical text",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            semantic_input=MEDICAL_RECORDS,
            semantic_output=MEDICAL_ENTITIES,
            schema_version="2.0.0",
            processing_strategy=ProcessingStrategy.STREAMING,
            max_input_size=100 * 1024 * 1024,  # 100MB
            supports_streaming=True,
            required_params=["medical_ontology"],
            accepts_context=True
        )
    
    def process(self, input_data: Any, context: Optional[ToolContext] = None) -> ToolResult:
        # Implementation would go here
        # This is where you'd use Gemini API with medical prompts
        pass


def create_framework_demo():
    """Demo showing how the framework works"""
    
    print("="*60)
    print("EXTENSIBLE TOOL COMPOSITION FRAMEWORK DEMO")
    print("="*60)
    
    # Create framework
    framework = ToolFramework()
    
    # Register some tools
    from semantic_types import (
        MEDICAL_RECORDS, MEDICAL_ENTITIES, MEDICAL_KNOWLEDGE_GRAPH,
        SOCIAL_POSTS, SOCIAL_NETWORK
    )
    
    # Medical tools
    framework.add_tool_simple(
        BaseTool,  # Would be actual tool class
        semantic_output=MEDICAL_RECORDS
    )
    
    # Find chains
    print("\n🔍 Finding medical processing chains:")
    chains = framework.find_chains(
        DataType.TEXT,
        DataType.GRAPH,
        domain=Domain.MEDICAL
    )
    
    for chain in chains:
        print(f"\nChain: {' → '.join(chain)}")
        print(framework.describe_chain(chain))
        
        valid, error = framework.validate_chain(chain)
        if valid:
            print("✅ Valid chain")
        else:
            print(f"❌ Invalid: {error}")
    
    return framework


if __name__ == "__main__":
    framework = create_framework_demo()