"""
Compatibility Matrix and LLM Planning for Simple Contracts

Shows how tools can chain together and how LLM can plan workflows.
"""

from typing import Dict, List, Set, Optional, Tuple
from simple_contracts import (
    ToolContract, SimpleTool,
    T01_PDFLoader, T05_CSVLoader, T23C_OntologyAware,
    T31_EntityBuilder, T34_EdgeBuilder, T68_PageRank,
    T91_TableFormatter
)
import json


class CompatibilityMatrix:
    """Determine which tools can follow which tools"""
    
    def __init__(self):
        self.tools: Dict[str, SimpleTool] = {}
        self.contracts: Dict[str, ToolContract] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        tools = [
            T01_PDFLoader(),
            T05_CSVLoader(),
            T23C_OntologyAware(),
            T31_EntityBuilder(),
            T34_EdgeBuilder(),
            T68_PageRank(),
            T91_TableFormatter()
        ]
        
        for tool in tools:
            contract = tool.get_contract()
            self.tools[contract.tool_id] = tool
            self.contracts[contract.tool_id] = contract
    
    def can_follow(self, tool_a_id: str, tool_b_id: str) -> bool:
        """Can tool_b run after tool_a?"""
        
        if tool_a_id not in self.contracts or tool_b_id not in self.contracts:
            return False
        
        produces = self.contracts[tool_a_id].produces
        consumes = self.contracts[tool_b_id].consumes
        
        # Special handling for flexible tools
        if tool_b_id == "T23C_ONTOLOGY_AWARE":
            # T23C can work with text OR table_data
            return "text" in produces or "table_data" in produces
        
        if tool_b_id == "T91_TABLE_FORMATTER":
            # T91 can format various things
            return any(field in produces for field in ["pagerank_scores", "entities", "nodes"])
        
        # Normal tools: check if all required fields are produced
        for field in consumes:
            if field not in produces:
                return False
        
        return True
    
    def get_compatible_next_tools(self, current_fields: Set[str]) -> List[str]:
        """Given current data fields, which tools can run?"""
        
        compatible = []
        
        for tool_id, contract in self.contracts.items():
            # Check if tool can run with current fields
            can_run = True
            
            # Special handling for flexible tools
            if tool_id == "T23C_ONTOLOGY_AWARE":
                can_run = "text" in current_fields or "table_data" in current_fields
            elif tool_id == "T91_TABLE_FORMATTER":
                can_run = any(field in current_fields for field in ["pagerank_scores", "entities", "nodes"])
            else:
                # Normal tools: check all requirements
                for field in contract.consumes:
                    if field not in current_fields:
                        can_run = False
                        break
            
            if can_run:
                compatible.append(tool_id)
        
        return compatible
    
    def build_full_matrix(self) -> Dict[str, List[str]]:
        """Build complete compatibility matrix"""
        
        matrix = {}
        
        for tool_a_id in self.contracts:
            matrix[tool_a_id] = []
            for tool_b_id in self.contracts:
                if tool_a_id != tool_b_id and self.can_follow(tool_a_id, tool_b_id):
                    matrix[tool_a_id].append(tool_b_id)
        
        return matrix
    
    def find_path(self, start_fields: Set[str], goal_fields: Set[str]) -> Optional[List[str]]:
        """Find a tool sequence that achieves the goal"""
        
        # BFS to find shortest path
        from collections import deque
        
        queue = deque([(start_fields, [])])
        visited = set()
        
        while queue:
            current_fields, path = queue.popleft()
            
            # Check if we've achieved the goal
            if goal_fields.issubset(current_fields):
                return path
            
            # Skip if we've seen this field combination
            fields_tuple = tuple(sorted(current_fields))
            if fields_tuple in visited:
                continue
            visited.add(fields_tuple)
            
            # Try each compatible tool
            compatible_tools = self.get_compatible_next_tools(current_fields)
            
            for tool_id in compatible_tools:
                # Skip if already in path (avoid loops)
                if tool_id in path:
                    continue
                
                # Calculate new fields after running this tool
                new_fields = current_fields.copy()
                new_fields.update(self.contracts[tool_id].produces.keys())
                
                # Add to queue
                new_path = path + [tool_id]
                queue.append((new_fields, new_path))
        
        return None  # No path found


class LLMPlanner:
    """Generate prompts for LLM to plan workflows"""
    
    def __init__(self, matrix: CompatibilityMatrix):
        self.matrix = matrix
    
    def generate_planning_prompt(self, user_request: str) -> str:
        """Generate prompt for LLM to plan workflow"""
        
        prompt = f"""You are planning a tool workflow for this request:
"{user_request}"

Available tools and their contracts:

"""
        
        for tool_id, contract in self.matrix.contracts.items():
            prompt += f"{tool_id}:\n"
            prompt += f"  Description: {contract.description}\n"
            
            if contract.consumes:
                prompt += f"  Requires: {list(contract.consumes.keys())}\n"
            elif tool_id == "T23C_ONTOLOGY_AWARE":
                prompt += f"  Requires: text OR table_data\n"
            elif tool_id == "T91_TABLE_FORMATTER":
                prompt += f"  Requires: pagerank_scores OR entities OR nodes\n"
            
            prompt += f"  Produces: {list(contract.produces.keys())}\n\n"
        
        prompt += """Plan a sequence of tools to accomplish the user's request.
Return the tool sequence as a JSON list of tool IDs.

Example response:
["T01_PDF_LOADER", "T23C_ONTOLOGY_AWARE", "T31_ENTITY_BUILDER"]
"""
        
        return prompt
    
    def validate_plan(self, tool_sequence: List[str], start_fields: Set[str]) -> Tuple[bool, str]:
        """Validate that a tool sequence is valid"""
        
        current_fields = start_fields.copy()
        
        for i, tool_id in enumerate(tool_sequence):
            if tool_id not in self.matrix.contracts:
                return False, f"Unknown tool: {tool_id}"
            
            contract = self.matrix.contracts[tool_id]
            
            # Check if tool can run with current fields
            if tool_id == "T23C_ONTOLOGY_AWARE":
                if "text" not in current_fields and "table_data" not in current_fields:
                    return False, f"Step {i+1}: T23C needs text or table_data"
            elif tool_id == "T91_TABLE_FORMATTER":
                if not any(field in current_fields for field in ["pagerank_scores", "entities", "nodes"]):
                    return False, f"Step {i+1}: T91 needs something to format"
            else:
                for field in contract.consumes:
                    if field not in current_fields:
                        return False, f"Step {i+1}: {tool_id} needs '{field}' but it's not available"
            
            # Update current fields
            current_fields.update(contract.produces.keys())
        
        return True, "Plan is valid"


def demonstrate_matrix():
    """Show the compatibility matrix in action"""
    print("\n" + "="*60)
    print("COMPATIBILITY MATRIX DEMONSTRATION")
    print("="*60)
    
    matrix = CompatibilityMatrix()
    
    # Show full matrix
    full_matrix = matrix.build_full_matrix()
    
    print("\nTool Compatibility (what can follow what):")
    for tool_a, compatible in full_matrix.items():
        if compatible:
            print(f"{tool_a} →")
            for tool_b in compatible:
                print(f"  → {tool_b}")
    
    # Show pathfinding
    print("\n" + "-"*40)
    print("PATHFINDING EXAMPLES")
    print("-"*40)
    
    # Path 1: file_path to formatted_table
    start = {"file_path"}
    goal = {"formatted_table"}
    path = matrix.find_path(start, goal)
    print(f"\nPath from {start} to {goal}:")
    if path:
        print(" → ".join(path))
    else:
        print("No path found")
    
    # Path 2: file_path to pagerank_scores
    goal = {"pagerank_scores"}
    path = matrix.find_path(start, goal)
    print(f"\nPath from {start} to {goal}:")
    if path:
        print(" → ".join(path))
    else:
        print("No path found")
    
    # Path 3: table_data to graph
    start = {"table_data"}
    goal = {"graph"}
    path = matrix.find_path(start, goal)
    print(f"\nPath from {start} to {goal}:")
    if path:
        print(" → ".join(path))
    else:
        print("No path found")


def demonstrate_llm_planning():
    """Show how LLM planning would work"""
    print("\n" + "="*60)
    print("LLM PLANNING DEMONSTRATION")
    print("="*60)
    
    matrix = CompatibilityMatrix()
    planner = LLMPlanner(matrix)
    
    # Example user requests
    requests = [
        "Load a PDF and extract entities",
        "Load a CSV file and build a graph",
        "Analyze a document with PageRank and format as table"
    ]
    
    for request in requests:
        print(f"\nUser request: '{request}'")
        print("-"*40)
        
        # Generate prompt (would go to LLM)
        prompt = planner.generate_planning_prompt(request)
        print("Generated prompt for LLM (truncated):")
        print(prompt[:500] + "...")
        
        # Simulate LLM response
        if "PDF" in request and "entities" in request:
            simulated_plan = ["T01_PDF_LOADER", "T23C_ONTOLOGY_AWARE"]
        elif "CSV" in request and "graph" in request:
            simulated_plan = ["T05_CSV_LOADER", "T23C_ONTOLOGY_AWARE", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER"]
        else:
            simulated_plan = ["T01_PDF_LOADER", "T23C_ONTOLOGY_AWARE", "T31_ENTITY_BUILDER", 
                            "T34_EDGE_BUILDER", "T68_PAGERANK", "T91_TABLE_FORMATTER"]
        
        print(f"\nSimulated LLM response: {simulated_plan}")
        
        # Validate plan
        start_fields = {"file_path"} if "PDF" in request else {"file_path"}
        valid, message = planner.validate_plan(simulated_plan, start_fields)
        print(f"Validation: {'✅' if valid else '❌'} {message}")


def show_statistics():
    """Show statistics about the tool system"""
    print("\n" + "="*60)
    print("SYSTEM STATISTICS")
    print("="*60)
    
    matrix = CompatibilityMatrix()
    
    print(f"Total tools: {len(matrix.contracts)}")
    
    # Count connections
    full_matrix = matrix.build_full_matrix()
    total_connections = sum(len(compatible) for compatible in full_matrix.values())
    print(f"Total possible connections: {total_connections}")
    
    # Average connections per tool
    avg_connections = total_connections / len(matrix.contracts) if matrix.contracts else 0
    print(f"Average connections per tool: {avg_connections:.1f}")
    
    # Tools that can start workflows (no requirements)
    starters = []
    for tool_id, contract in matrix.contracts.items():
        if not contract.consumes or tool_id in ["T23C_ONTOLOGY_AWARE"]:
            starters.append(tool_id)
    print(f"\nWorkflow starters: {starters}")
    
    # Tools that typically end workflows
    enders = []
    for tool_id, compatible in full_matrix.items():
        if not compatible:
            enders.append(tool_id)
    print(f"Workflow enders: {enders}")
    
    # Most connected tools
    connections = [(tool_id, len(compatible)) for tool_id, compatible in full_matrix.items()]
    connections.sort(key=lambda x: x[1], reverse=True)
    print(f"\nMost connected tools:")
    for tool_id, count in connections[:3]:
        print(f"  {tool_id}: {count} connections")


if __name__ == "__main__":
    demonstrate_matrix()
    demonstrate_llm_planning()
    show_statistics()