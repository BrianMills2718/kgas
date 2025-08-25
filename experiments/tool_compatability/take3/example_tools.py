"""
Example tools showing how pipeline accumulation works in practice.

Each tool:
1. Declares its requirements
2. Reads what it needs from the pipeline
3. Adds its output as a new stage
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from pipeline_data import PipelineData, ExtractionResult, GraphNodes, PageRankResult


class PipelineTool(ABC):
    """Base class for pipeline-aware tools"""
    
    def __init__(self, tool_id: str):
        self.tool_id = tool_id
        self.required_stages: List[str] = []  # Stages this tool needs
        self.output_stage: str = ""  # Stage name this tool creates
    
    @abstractmethod
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        """Execute tool and add results to pipeline"""
        pass
    
    def validate_inputs(self, pipeline: PipelineData) -> bool:
        """Validate that required stages exist"""
        return pipeline.validate_dependencies(self.required_stages)


# ============= Document Loaders =============

class T01_PDFLoader(PipelineTool):
    """Loads PDF and adds raw text to pipeline"""
    
    def __init__(self):
        super().__init__("T01_PDF_LOADER")
        self.required_stages = []  # No requirements - it's a source
        self.output_stage = "raw_text"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        file_path = parameters.get("file_path")
        
        # Simulate PDF loading
        text = f"Simulated text from {file_path}: John Smith is the CEO of TechCorp. TechCorp was founded in 2020."
        
        pipeline.add_stage(
            stage_name="raw_text",
            data=text,
            tool_id=self.tool_id
        )
        
        # Also add metadata about the source
        pipeline.add_stage(
            stage_name="source_metadata",
            data={
                "file_path": file_path,
                "page_count": 5,
                "extraction_method": "pdfplumber"
            },
            tool_id=self.tool_id
        )
        
        return pipeline


class T05_CSVLoader(PipelineTool):
    """Loads CSV and adds table data to pipeline"""
    
    def __init__(self):
        super().__init__("T05_CSV_LOADER")
        self.required_stages = []
        self.output_stage = "table_data"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        file_path = parameters.get("file_path")
        
        # Simulate CSV loading
        table_data = {
            "columns": ["Name", "Role", "Company"],
            "rows": [
                {"Name": "John Smith", "Role": "CEO", "Company": "TechCorp"},
                {"Name": "Jane Doe", "Role": "CTO", "Company": "TechCorp"}
            ]
        }
        
        pipeline.add_stage(
            stage_name="table_data",
            data=table_data,
            tool_id=self.tool_id
        )
        
        return pipeline


# ============= Extraction Tools =============

class T23C_OntologyAwareExtractor(PipelineTool):
    """
    Extracts entities and relationships using LLM.
    Can work with either raw_text or table_data.
    """
    
    def __init__(self):
        super().__init__("T23C_ONTOLOGY_AWARE")
        # Note: We don't set required_stages because we can work with different inputs
        self.output_stage = "extraction"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        mode = parameters.get("mode", "full_extraction")
        
        # Flexible input - can work with text OR table
        input_data = None
        input_type = None
        
        if pipeline.has_stage("raw_text"):
            input_data = pipeline.get_stage("raw_text")
            input_type = "text"
        elif pipeline.has_stage("table_data"):
            input_data = pipeline.get_stage("table_data")
            input_type = "table"
        else:
            raise ValueError("T23C requires either 'raw_text' or 'table_data' stage")
        
        # Simulate extraction based on input type
        if input_type == "text":
            extraction = self._extract_from_text(input_data, mode)
        else:
            extraction = self._extract_from_table(input_data, mode)
        
        # Add extraction results
        pipeline.add_stage(
            stage_name="extraction",
            data=extraction,
            tool_id=self.tool_id,
            dependencies=["raw_text"] if input_type == "text" else ["table_data"]
        )
        
        return pipeline
    
    def _extract_from_text(self, text: str, mode: str) -> Dict[str, Any]:
        """Simulate extraction from text"""
        
        if mode == "entity_only":
            return {
                "entities": [
                    {"id": "e1", "text": "John Smith", "type": "PERSON"},
                    {"id": "e2", "text": "TechCorp", "type": "ORGANIZATION"}
                ],
                "relationships": []
            }
        
        elif mode == "full_extraction":
            return {
                "entities": [
                    {"id": "e1", "text": "John Smith", "type": "PERSON", 
                     "properties": {"role": "CEO"}},
                    {"id": "e2", "text": "TechCorp", "type": "ORGANIZATION",
                     "properties": {"founded": "2020"}}
                ],
                "relationships": [
                    {"id": "r1", "source_id": "e1", "target_id": "e2", 
                     "type": "CEO_OF", "confidence": 0.95}
                ]
            }
        
        else:  # theory_guided
            return {
                "entities": [
                    {"id": "e1", "text": "John Smith", "type": "PERSON",
                     "theory_role": "in_group_member"},
                    {"id": "e2", "text": "TechCorp", "type": "ORGANIZATION",
                     "theory_role": "in_group"}
                ],
                "relationships": [
                    {"id": "r1", "source_id": "e1", "target_id": "e2",
                     "type": "MEMBER_OF", "theory_type": "group_membership"}
                ],
                "theory_annotations": {
                    "theory": "social_categorization",
                    "concepts_identified": ["in_group", "membership"]
                }
            }
    
    def _extract_from_table(self, table_data: Dict, mode: str) -> Dict[str, Any]:
        """Simulate extraction from table"""
        entities = []
        relationships = []
        
        for row in table_data["rows"]:
            # Create entities from each cell
            person_id = f"e_{row['Name'].replace(' ', '_')}"
            company_id = f"e_{row['Company'].replace(' ', '_')}"
            
            entities.append({
                "id": person_id,
                "text": row["Name"],
                "type": "PERSON"
            })
            
            entities.append({
                "id": company_id,
                "text": row["Company"],
                "type": "ORGANIZATION"
            })
            
            # Create relationship
            relationships.append({
                "id": f"r_{person_id}_{company_id}",
                "source_id": person_id,
                "target_id": company_id,
                "type": row["Role"] + "_OF"
            })
        
        # Deduplicate entities
        seen = set()
        unique_entities = []
        for e in entities:
            if e["id"] not in seen:
                seen.add(e["id"])
                unique_entities.append(e)
        
        return {
            "entities": unique_entities,
            "relationships": relationships
        }


# ============= Graph Building Tools =============

class T31_EntityBuilder(PipelineTool):
    """Builds graph nodes from extracted entities"""
    
    def __init__(self):
        super().__init__("T31_ENTITY_BUILDER")
        self.required_stages = ["extraction"]
        self.output_stage = "graph_nodes"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        self.validate_inputs(pipeline)
        
        extraction = pipeline.get_stage("extraction")
        entities = extraction.get("entities", [])
        
        # Build graph nodes
        nodes = []
        for entity in entities:
            node = {
                "id": entity["id"],
                "label": entity["text"],
                "type": entity["type"],
                "properties": entity.get("properties", {})
            }
            nodes.append(node)
        
        pipeline.add_stage(
            stage_name="graph_nodes",
            data=GraphNodes(nodes=nodes, node_count=len(nodes)),
            tool_id=self.tool_id,
            dependencies=["extraction"]
        )
        
        return pipeline


class T34_EdgeBuilder(PipelineTool):
    """Builds graph edges from relationships and nodes"""
    
    def __init__(self):
        super().__init__("T34_EDGE_BUILDER")
        self.required_stages = ["extraction", "graph_nodes"]
        self.output_stage = "graph_structure"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        self.validate_inputs(pipeline)
        
        extraction = pipeline.get_stage("extraction")
        graph_nodes = pipeline.get_stage("graph_nodes")
        
        relationships = extraction.get("relationships", [])
        nodes = graph_nodes.nodes if hasattr(graph_nodes, 'nodes') else graph_nodes.get("nodes", [])
        
        # Build edges
        edges = []
        for rel in relationships:
            edge = {
                "id": rel["id"],
                "source": rel["source_id"],
                "target": rel["target_id"],
                "type": rel["type"],
                "properties": rel.get("properties", {})
            }
            edges.append(edge)
        
        # Create full graph structure
        graph = {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges)
        }
        
        pipeline.add_stage(
            stage_name="graph_structure",
            data=graph,
            tool_id=self.tool_id,
            dependencies=["extraction", "graph_nodes"]
        )
        
        return pipeline


# ============= Analysis Tools =============

class T68_PageRank(PipelineTool):
    """Calculates PageRank scores for graph"""
    
    def __init__(self):
        super().__init__("T68_PAGERANK")
        self.required_stages = ["graph_structure"]
        self.output_stage = "pagerank_scores"
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        self.validate_inputs(pipeline)
        
        graph = pipeline.get_stage("graph_structure")
        damping = parameters.get("damping_factor", 0.85)
        
        # Simulate PageRank calculation
        scores = {}
        nodes = graph.get("nodes", [])
        
        # Simple simulation - normally would use networkx or similar
        base_score = 1.0 / len(nodes) if nodes else 0
        for node in nodes:
            # Simulate higher scores for nodes with more connections
            node_id = node["id"]
            edge_count = sum(1 for e in graph.get("edges", []) 
                           if e["source"] == node_id or e["target"] == node_id)
            scores[node_id] = base_score * (1 + edge_count * 0.1)
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        result = PageRankResult(
            scores=scores,
            iterations=100,
            convergence_delta=0.0001
        )
        
        pipeline.add_stage(
            stage_name="pagerank_scores",
            data=result,
            tool_id=self.tool_id,
            dependencies=["graph_structure"]
        )
        
        return pipeline


class T91_TableFormatter(PipelineTool):
    """
    Formats analysis results as a table.
    Can work with different types of analysis results.
    """
    
    def __init__(self):
        super().__init__("T91_TABLE_FORMATTER")
        # Flexible - can format different types of results
        self.output_stage = "formatted_table"
        self._call_count = 0  # Track calls to create unique stage names
    
    def execute(self, pipeline: PipelineData, parameters: Dict[str, Any]) -> PipelineData:
        # Find what we can format
        if pipeline.has_stage("pagerank_scores"):
            data = self._format_pagerank(pipeline)
            deps = ["pagerank_scores"]
            stage_suffix = "_pagerank"
        elif pipeline.has_stage("extraction"):
            data = self._format_extraction(pipeline)
            deps = ["extraction"]
            stage_suffix = "_extraction"
        else:
            raise ValueError("T91 needs analysis results to format")
        
        # Create unique stage name if needed
        stage_name = "formatted_table"
        if pipeline.has_stage(stage_name):
            self._call_count += 1
            stage_name = f"formatted_table{stage_suffix}_{self._call_count}"
        
        pipeline.add_stage(
            stage_name=stage_name,
            data=data,
            tool_id=self.tool_id,
            dependencies=deps
        )
        
        return pipeline
    
    def _format_pagerank(self, pipeline: PipelineData) -> Dict[str, Any]:
        """Format PageRank scores as table"""
        pagerank = pipeline.get_stage("pagerank_scores")
        
        # Also get node labels if available
        labels = {}
        if pipeline.has_stage("graph_nodes"):
            nodes = pipeline.get_stage("graph_nodes")
            if hasattr(nodes, 'nodes'):
                nodes_list = nodes.nodes
            else:
                nodes_list = nodes.get("nodes", [])
            
            for node in nodes_list:
                labels[node["id"]] = node["label"]
        
        # Build table
        rows = []
        scores = pagerank.scores if hasattr(pagerank, 'scores') else pagerank.get("scores", {})
        
        for node_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            rows.append({
                "Node ID": node_id,
                "Label": labels.get(node_id, node_id),
                "PageRank Score": f"{score:.4f}"
            })
        
        return {
            "columns": ["Node ID", "Label", "PageRank Score"],
            "rows": rows,
            "row_count": len(rows)
        }
    
    def _format_extraction(self, pipeline: PipelineData) -> Dict[str, Any]:
        """Format extraction results as table"""
        extraction = pipeline.get_stage("extraction")
        
        rows = []
        for entity in extraction.get("entities", []):
            rows.append({
                "ID": entity["id"],
                "Text": entity["text"],
                "Type": entity["type"]
            })
        
        return {
            "columns": ["ID", "Text", "Type"],
            "rows": rows,
            "row_count": len(rows)
        }