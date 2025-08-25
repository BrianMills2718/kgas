"""
Transformation Matrix for Tool Compatibility

This implements the type-based compatibility matrix where tools
are defined by the data type transformations they perform.
Any valid path through the matrix is a valid tool chain.
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

from data_types import DataType, DataSchema, get_schema, describe_transformation


@dataclass
class ToolTransformation:
    """
    Defines what transformation a tool performs.
    A tool takes one data type and produces another.
    """
    tool_id: str
    tool_name: str
    input_type: DataType
    output_type: DataType
    description: Optional[str] = None
    confidence: float = 1.0  # How reliable is this transformation
    
    def __str__(self):
        return f"{self.tool_id}: {self.input_type.value} → {self.output_type.value}"


class TransformationMatrix:
    """
    Manages the matrix of possible transformations.
    This is essentially a directed graph where:
    - Nodes are DataTypes
    - Edges are Tools that perform transformations
    """
    
    def __init__(self):
        self.transformations: Dict[str, ToolTransformation] = {}
        self.type_graph: Dict[DataType, List[Tuple[DataType, str]]] = {}
        self._build_type_graph()
    
    def register_tool(self, transformation: ToolTransformation):
        """Register a tool and its transformation"""
        self.transformations[transformation.tool_id] = transformation
        self._add_to_graph(transformation)
    
    def _add_to_graph(self, transformation: ToolTransformation):
        """Add transformation to the type graph"""
        if transformation.input_type not in self.type_graph:
            self.type_graph[transformation.input_type] = []
        
        self.type_graph[transformation.input_type].append(
            (transformation.output_type, transformation.tool_id)
        )
    
    def _build_type_graph(self):
        """Rebuild the type graph from registered transformations"""
        self.type_graph.clear()
        for transform in self.transformations.values():
            self._add_to_graph(transform)
    
    def get_compatible_tools(self, tool_id: str) -> List[str]:
        """
        Find all tools that can accept the output of the given tool.
        This is the key to compatibility!
        """
        tool = self.transformations.get(tool_id)
        if not tool:
            return []
        
        output_type = tool.output_type
        
        # Find all tools that accept this output type
        compatible = []
        for other_id, other_tool in self.transformations.items():
            if other_tool.input_type == output_type and other_id != tool_id:
                compatible.append(other_id)
        
        return compatible
    
    def find_all_paths(self, start_type: DataType, end_type: DataType, 
                      max_length: int = 10) -> List[List[str]]:
        """
        Find all possible tool chains from start_type to end_type.
        Returns list of tool ID sequences.
        """
        def find_paths_recursive(current_type: DataType, target_type: DataType, 
                               path: List[str], visited_types: Set[DataType]) -> List[List[str]]:
            
            if current_type == target_type:
                return [path] if path else [[]]  # Empty path if start == end
            
            if len(path) >= max_length:
                return []  # Path too long
            
            all_paths = []
            
            # Get all transformations from current type
            for next_type, tool_id in self.type_graph.get(current_type, []):
                if next_type not in visited_types:  # Avoid cycles
                    new_visited = visited_types.copy()
                    new_visited.add(next_type)
                    
                    sub_paths = find_paths_recursive(
                        next_type, target_type, 
                        path + [tool_id], 
                        new_visited
                    )
                    all_paths.extend(sub_paths)
            
            return all_paths
        
        visited = {start_type}
        return find_paths_recursive(start_type, end_type, [], visited)
    
    def find_shortest_path(self, start_type: DataType, end_type: DataType) -> Optional[List[str]]:
        """Find the shortest tool chain from start to end"""
        all_paths = self.find_all_paths(start_type, end_type)
        if not all_paths:
            return None
        
        return min(all_paths, key=len)
    
    def validate_chain(self, tool_chain: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate that a sequence of tools forms a valid chain.
        Returns (is_valid, error_message)
        """
        if not tool_chain:
            return True, None
        
        for i in range(len(tool_chain) - 1):
            current_tool = self.transformations.get(tool_chain[i])
            next_tool = self.transformations.get(tool_chain[i + 1])
            
            if not current_tool:
                return False, f"Tool '{tool_chain[i]}' not found"
            if not next_tool:
                return False, f"Tool '{tool_chain[i + 1]}' not found"
            
            if current_tool.output_type != next_tool.input_type:
                return False, (f"Type mismatch: {current_tool.tool_id} outputs "
                             f"{current_tool.output_type.value} but {next_tool.tool_id} "
                             f"expects {next_tool.input_type.value}")
        
        return True, None
    
    def get_matrix_visualization(self) -> str:
        """
        Generate a text visualization of the transformation matrix.
        Shows which types can transform to which other types.
        """
        # Get all unique data types
        all_types = set()
        for transform in self.transformations.values():
            all_types.add(transform.input_type)
            all_types.add(transform.output_type)
        
        type_list = sorted(all_types, key=lambda t: t.value)
        
        # Build adjacency matrix
        matrix = []
        header = "FROM \\ TO  | " + " | ".join(t.value[:4] for t in type_list)
        matrix.append(header)
        matrix.append("-" * len(header))
        
        for from_type in type_list:
            row = f"{from_type.value[:12]:12} |"
            for to_type in type_list:
                # Find tools that do this transformation
                tools = [tid for tid, t in self.transformations.items()
                        if t.input_type == from_type and t.output_type == to_type]
                
                if tools:
                    # Show count or first tool ID
                    cell = f"{len(tools):^4}" if len(tools) > 1 else tools[0][:4]
                else:
                    cell = "  - "
                
                row += f" {cell} |"
            
            matrix.append(row)
        
        return "\n".join(matrix)
    
    def suggest_next_tools(self, current_type: DataType) -> List[Tuple[str, DataType]]:
        """
        Given the current data type, suggest tools that could be used next.
        Returns list of (tool_id, output_type) tuples.
        """
        suggestions = []
        
        for tool_id, transform in self.transformations.items():
            if transform.input_type == current_type:
                suggestions.append((tool_id, transform.output_type))
        
        return suggestions
    
    def get_statistics(self) -> Dict:
        """Get statistics about the transformation matrix"""
        stats = {
            "total_tools": len(self.transformations),
            "total_types": len(set(t.input_type for t in self.transformations.values()) | 
                              set(t.output_type for t in self.transformations.values())),
            "transformations_by_type": {},
            "tools_by_input_type": {},
            "tools_by_output_type": {},
            "reachability": {}
        }
        
        # Count transformations by type
        for transform in self.transformations.values():
            key = f"{transform.input_type.value} → {transform.output_type.value}"
            stats["transformations_by_type"][key] = stats["transformations_by_type"].get(key, 0) + 1
            
            # Count by input type
            input_key = transform.input_type.value
            stats["tools_by_input_type"][input_key] = stats["tools_by_input_type"].get(input_key, 0) + 1
            
            # Count by output type
            output_key = transform.output_type.value
            stats["tools_by_output_type"][output_key] = stats["tools_by_output_type"].get(output_key, 0) + 1
        
        # Check reachability between common types
        common_paths = [
            (DataType.RAW_TEXT, DataType.TABLE_FORMAT),
            (DataType.RAW_TEXT, DataType.GRAPH_STRUCTURE),
            (DataType.RAW_TEXT, DataType.ANALYZED_RESULTS),
            (DataType.GRAPH_STRUCTURE, DataType.TABLE_FORMAT)
        ]
        
        for start, end in common_paths:
            paths = self.find_all_paths(start, end)
            stats["reachability"][f"{start.value} → {end.value}"] = len(paths)
        
        return stats


# Create the global transformation matrix
TRANSFORMATION_MATRIX = TransformationMatrix()


def register_kgas_tools():
    """Register the known KGAS tools with their transformations"""
    
    tools = [
        # Extraction tools
        ToolTransformation(
            tool_id="T23C",
            tool_name="LLM Ontology-Aware Extractor",
            input_type=DataType.RAW_TEXT,
            output_type=DataType.EXTRACTED_DATA,
            description="Extract entities, relationships, and properties using LLM with ontology"
        ),
        
        # Graph building tools
        ToolTransformation(
            tool_id="T31",
            tool_name="Entity Builder",
            input_type=DataType.EXTRACTED_DATA,
            output_type=DataType.GRAPH_STRUCTURE,
            description="Build graph nodes from extracted entities"
        ),
        
        ToolTransformation(
            tool_id="T34",
            tool_name="Edge Builder",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.GRAPH_STRUCTURE,
            description="Add edges to existing graph structure"
        ),
        
        # Analysis tools
        ToolTransformation(
            tool_id="T68",
            tool_name="PageRank Calculator",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.ENRICHED_GRAPH,
            description="Calculate PageRank scores for graph nodes"
        ),
        
        ToolTransformation(
            tool_id="T49",
            tool_name="Multihop Query",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.ANALYZED_RESULTS,
            description="Perform multi-hop graph queries"
        ),
        
        # Conversion tools
        ToolTransformation(
            tool_id="T91",
            tool_name="Graph to Table Converter",
            input_type=DataType.ENRICHED_GRAPH,
            output_type=DataType.TABLE_FORMAT,
            description="Convert graph data to tabular format"
        ),
        
        ToolTransformation(
            tool_id="T91B",
            tool_name="Simple Graph to Table",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.TABLE_FORMAT,
            description="Convert basic graph to table without metrics"
        ),
        
        # Vector tools
        ToolTransformation(
            tool_id="T15B",
            tool_name="Vector Embedder",
            input_type=DataType.RAW_TEXT,
            output_type=DataType.VECTOR_EMBEDDINGS,
            description="Generate vector embeddings from text"
        ),
        
        # Storage tools
        ToolTransformation(
            tool_id="T70",
            tool_name="Neo4j Writer",
            input_type=DataType.GRAPH_STRUCTURE,
            output_type=DataType.NEO4J_TRANSACTION,
            description="Prepare graph for Neo4j insertion"
        ),
        
        ToolTransformation(
            tool_id="T71",
            tool_name="SQLite Writer",
            input_type=DataType.TABLE_FORMAT,
            output_type=DataType.SQLITE_RECORDS,
            description="Prepare table for SQLite storage"
        )
    ]
    
    for tool in tools:
        TRANSFORMATION_MATRIX.register_tool(tool)
    
    return TRANSFORMATION_MATRIX


def demonstrate_matrix():
    """Demonstrate the transformation matrix capabilities"""
    
    # Register tools
    matrix = register_kgas_tools()
    
    print("TRANSFORMATION MATRIX")
    print("=" * 60)
    print(matrix.get_matrix_visualization())
    
    print("\n\nFINDING PATHS")
    print("=" * 60)
    
    # Find paths from raw text to table format
    paths = matrix.find_all_paths(DataType.RAW_TEXT, DataType.TABLE_FORMAT)
    print(f"\nPaths from RAW_TEXT to TABLE_FORMAT: {len(paths)} found")
    for i, path in enumerate(paths, 1):
        print(f"  {i}. {' → '.join(path)}")
    
    # Find shortest path
    shortest = matrix.find_shortest_path(DataType.RAW_TEXT, DataType.TABLE_FORMAT)
    print(f"\nShortest path: {' → '.join(shortest) if shortest else 'None'}")
    
    # Test compatibility
    print("\n\nCOMPATIBILITY TESTING")
    print("=" * 60)
    
    test_tool = "T23C"
    compatible = matrix.get_compatible_tools(test_tool)
    print(f"\nTools compatible after {test_tool}: {compatible}")
    
    # Validate a chain
    test_chain = ["T23C", "T31", "T68", "T91"]
    valid, error = matrix.validate_chain(test_chain)
    print(f"\nChain {' → '.join(test_chain)}: {'✓ Valid' if valid else f'✗ Invalid: {error}'}")
    
    # Get statistics
    print("\n\nSTATISTICS")
    print("=" * 60)
    stats = matrix.get_statistics()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    demonstrate_matrix()