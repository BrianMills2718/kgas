"""
Simple Explicit Tool Contracts System

Each tool declares what it consumes and produces.
Workflow passes a simple dict between tools.
"""

from typing import Dict, Any, List, Optional, Type, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json


@dataclass
class ToolContract:
    """Contract defining what a tool needs and produces"""
    tool_id: str
    consumes: Dict[str, Type]  # field_name -> type
    produces: Dict[str, Type]  # field_name -> type
    optional_consumes: Dict[str, Type] = None  # Optional inputs
    description: str = ""
    
    def __post_init__(self):
        if self.optional_consumes is None:
            self.optional_consumes = {}
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Check if data satisfies input requirements"""
        # Check required fields
        for field, expected_type in self.consumes.items():
            if field not in data:
                raise ValueError(f"{self.tool_id} requires '{field}' but it's missing")
            
            # Basic type checking
            if not isinstance(data[field], expected_type):
                raise TypeError(
                    f"{self.tool_id} requires '{field}' to be {expected_type.__name__} "
                    f"but got {type(data[field]).__name__}"
                )
        
        return True
    
    def can_execute(self, data: Dict[str, Any]) -> bool:
        """Check if tool can run with current data (non-throwing)"""
        try:
            return self.validate_input(data)
        except (ValueError, TypeError):
            return False


class SimpleTool(ABC):
    """Base class for tools with contracts"""
    
    @abstractmethod
    def get_contract(self) -> ToolContract:
        """Return this tool's contract"""
        pass
    
    @abstractmethod
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute tool with input data.
        Returns dict with produced fields.
        """
        pass


class SimpleWorkflow:
    """Execute tools in sequence with contract validation"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}  # Current working data
        self.history: List[Dict] = []  # Execution history for debugging
        self.errors: List[Dict] = []  # Error log
    
    def execute(self, tool: SimpleTool, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a tool and update data"""
        
        contract = tool.get_contract()
        
        # Validate inputs
        try:
            contract.validate_input(self.data)
        except (ValueError, TypeError) as e:
            error = {
                "tool": contract.tool_id,
                "error": str(e),
                "available_data": list(self.data.keys())
            }
            self.errors.append(error)
            raise
        
        # Execute tool
        try:
            result = tool.execute(self.data, params)
        except Exception as e:
            error = {
                "tool": contract.tool_id,
                "error": f"Execution failed: {e}",
                "input_data": dict(self.data)
            }
            self.errors.append(error)
            raise
        
        # Update data with results
        for field, value in result.items():
            self.data[field] = value
        
        # Log history
        self.history.append({
            "tool": contract.tool_id,
            "params": params,
            "produced": list(result.keys()),
            "data_size": len(str(self.data))  # Track data growth
        })
        
        return self.data
    
    def reset(self):
        """Clear workflow for new execution"""
        self.data = {}
        self.history = []
        self.errors = []
    
    def get_summary(self) -> Dict:
        """Get execution summary"""
        return {
            "steps_executed": len(self.history),
            "current_fields": list(self.data.keys()),
            "errors": len(self.errors),
            "data_size": len(str(self.data))
        }


# ============== Example Tools ==============

class T01_PDFLoader(SimpleTool):
    """Load PDF and extract text"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T01_PDF_LOADER",
            consumes={"file_path": str},
            produces={"text": str, "page_count": int},
            description="Load PDF and extract text"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        file_path = data["file_path"]
        
        # Simulate PDF loading
        text = f"Simulated text from {file_path}: John Smith is the CEO of TechCorp. Founded in 2020."
        
        return {
            "text": text,
            "page_count": 5
        }


class T05_CSVLoader(SimpleTool):
    """Load CSV into table format"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T05_CSV_LOADER",
            consumes={"file_path": str},
            produces={"table_data": dict},
            description="Load CSV as table"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        file_path = data["file_path"]
        
        # Simulate CSV loading
        table = {
            "columns": ["Name", "Role", "Company"],
            "rows": [
                {"Name": "John Smith", "Role": "CEO", "Company": "TechCorp"},
                {"Name": "Jane Doe", "Role": "CTO", "Company": "TechCorp"}
            ]
        }
        
        return {"table_data": table}


class T23C_OntologyAware(SimpleTool):
    """Extract entities and relationships - can work with text OR table"""
    
    def get_contract(self) -> ToolContract:
        # This tool can work with EITHER text OR table_data
        # We'll handle this specially
        return ToolContract(
            tool_id="T23C_ONTOLOGY_AWARE",
            consumes={},  # We'll check manually
            produces={"entities": list, "relationships": list},
            optional_consumes={"text": str, "table_data": dict},
            description="Extract entities and relationships from text or table"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        mode = params.get("mode", "full") if params else "full"
        
        # Check what input is available
        if "text" in data:
            return self._extract_from_text(data["text"], mode)
        elif "table_data" in data:
            return self._extract_from_table(data["table_data"], mode)
        else:
            raise ValueError("T23C requires either 'text' or 'table_data'")
    
    def _extract_from_text(self, text: str, mode: str) -> Dict[str, Any]:
        """Extract from text"""
        entities = [
            {"id": "e1", "text": "John Smith", "type": "PERSON"},
            {"id": "e2", "text": "TechCorp", "type": "ORGANIZATION"}
        ]
        
        relationships = []
        if mode == "full":
            relationships = [
                {"id": "r1", "source": "e1", "target": "e2", "type": "CEO_OF"}
            ]
        
        return {"entities": entities, "relationships": relationships}
    
    def _extract_from_table(self, table: dict, mode: str) -> Dict[str, Any]:
        """Extract from table"""
        entities = []
        relationships = []
        
        for row in table["rows"]:
            person_id = f"e_{row['Name'].replace(' ', '_')}"
            company_id = f"e_{row['Company'].replace(' ', '_')}"
            
            entities.append({"id": person_id, "text": row["Name"], "type": "PERSON"})
            entities.append({"id": company_id, "text": row["Company"], "type": "ORGANIZATION"})
            
            if mode == "full":
                relationships.append({
                    "id": f"r_{person_id}",
                    "source": person_id,
                    "target": company_id,
                    "type": row["Role"].upper() + "_OF"
                })
        
        # Deduplicate entities
        seen = set()
        unique_entities = []
        for e in entities:
            if e["id"] not in seen:
                seen.add(e["id"])
                unique_entities.append(e)
        
        return {"entities": unique_entities, "relationships": relationships}


class T31_EntityBuilder(SimpleTool):
    """Build graph nodes from entities"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T31_ENTITY_BUILDER",
            consumes={"entities": list},
            produces={"nodes": list},
            description="Build graph nodes from entities"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        entities = data["entities"]
        
        nodes = []
        for entity in entities:
            node = {
                "id": entity["id"],
                "label": entity["text"],
                "type": entity["type"]
            }
            nodes.append(node)
        
        return {"nodes": nodes}


class T34_EdgeBuilder(SimpleTool):
    """Build graph edges from relationships"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T34_EDGE_BUILDER",
            consumes={"relationships": list, "nodes": list},
            produces={"edges": list, "graph": dict},
            description="Build graph structure from nodes and relationships"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        relationships = data["relationships"]
        nodes = data["nodes"]
        
        edges = []
        for rel in relationships:
            edge = {
                "id": rel["id"],
                "source": rel["source"],
                "target": rel["target"],
                "type": rel["type"]
            }
            edges.append(edge)
        
        graph = {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
        
        return {"edges": edges, "graph": graph}


class T68_PageRank(SimpleTool):
    """Calculate PageRank scores"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T68_PAGERANK",
            consumes={"graph": dict},
            produces={"pagerank_scores": dict},
            description="Calculate PageRank for graph"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        graph = data["graph"]
        
        # Simulate PageRank
        scores = {}
        for node in graph["nodes"]:
            scores[node["id"]] = 0.15 + 0.85 * (1.0 / graph["node_count"])
        
        return {"pagerank_scores": scores}


class T91_TableFormatter(SimpleTool):
    """Format results as table - flexible input"""
    
    def get_contract(self) -> ToolContract:
        return ToolContract(
            tool_id="T91_TABLE_FORMATTER",
            consumes={},  # Flexible - will check what's available
            produces={"formatted_table": dict},
            optional_consumes={
                "pagerank_scores": dict,
                "entities": list,
                "nodes": list
            },
            description="Format available data as table"
        )
    
    def execute(self, data: Dict[str, Any], params: Optional[Dict] = None) -> Dict[str, Any]:
        # Format whatever is available
        if "pagerank_scores" in data:
            return self._format_pagerank(data)
        elif "entities" in data:
            return self._format_entities(data)
        elif "nodes" in data:
            return self._format_nodes(data)
        else:
            raise ValueError("T91 needs something to format (pagerank_scores, entities, or nodes)")
    
    def _format_pagerank(self, data: Dict) -> Dict[str, Any]:
        scores = data["pagerank_scores"]
        nodes = data.get("nodes", [])
        
        # Create label map
        labels = {n["id"]: n["label"] for n in nodes}
        
        rows = []
        for node_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            rows.append({
                "Node": node_id,
                "Label": labels.get(node_id, node_id),
                "Score": f"{score:.4f}"
            })
        
        return {
            "formatted_table": {
                "columns": ["Node", "Label", "Score"],
                "rows": rows
            }
        }
    
    def _format_entities(self, data: Dict) -> Dict[str, Any]:
        entities = data["entities"]
        
        rows = []
        for e in entities:
            rows.append({
                "ID": e["id"],
                "Text": e["text"],
                "Type": e["type"]
            })
        
        return {
            "formatted_table": {
                "columns": ["ID", "Text", "Type"],
                "rows": rows
            }
        }
    
    def _format_nodes(self, data: Dict) -> Dict[str, Any]:
        nodes = data["nodes"]
        
        rows = []
        for n in nodes:
            rows.append({
                "ID": n["id"],
                "Label": n["label"],
                "Type": n["type"]
            })
        
        return {
            "formatted_table": {
                "columns": ["ID", "Label", "Type"],
                "rows": rows
            }
        }