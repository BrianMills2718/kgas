#!/usr/bin/env python3
"""
Theory-Enhanced Workflow Engine
Extends standard pipeline with theory extraction capabilities
"""

from typing import List, Dict, Any, TYPE_CHECKING
from ...logging_config import get_logger
from ...tool_contract import ToolRequest, ToolResult

if TYPE_CHECKING:
    from ..pipeline_orchestrator import PipelineOrchestrator

logger = get_logger("core.orchestration.workflow_engines.theory_enhanced_engine")


class TheoryEnhancedWorkflow:
    """Workflow that includes theory extraction in the pipeline"""
    
    @staticmethod
    def get_theory_enhanced_pipeline() -> List[str]:
        """Define theory-enhanced processing pipeline"""
        return [
            "T01_PDF_LOADER",           # Extract text from PDF
            "T302_THEORY_EXTRACTION",   # ← NEW: Extract academic theory
            "T15A_TEXT_CHUNKER",        # Chunk text for processing 
            "T31_ENTITY_BUILDER",       # Build entities (now theory-enhanced)
            "T34_EDGE_BUILDER",         # Build relationships
            "T68_PAGERANK",             # Calculate importance scores
            "T49_MULTIHOP_QUERY"        # Answer questions
        ]
    
    @staticmethod
    def execute_theory_pipeline(orchestrator: 'PipelineOrchestrator', pdf_path: str) -> Dict[str, Any]:
        """Execute complete theory-enhanced pipeline"""
        
        results = {}
        workflow_data = {}
        
        logger.info(f"Starting theory-enhanced workflow for: {pdf_path}")
        
        try:
            # Step 1: Load PDF
            logger.info("Step 1: Loading PDF...")
            pdf_result = orchestrator.execute_tool(
                "T01_PDF_LOADER",
                ToolRequest(input_data={"file_path": pdf_path})
            )
            
            if pdf_result.status != "success":
                return {"status": "error", "error": "PDF loading failed", "details": pdf_result.error_details}
            
            extracted_text = pdf_result.data.get("text", "")
            if not extracted_text:
                return {"status": "error", "error": "No text extracted from PDF"}
                
            workflow_data["source_text"] = extracted_text
            results["pdf_loading"] = pdf_result
            logger.info(f"✅ PDF loaded: {len(extracted_text)} characters")
            
            # Step 2: Theory Extraction (NEW)
            logger.info("Step 2: Extracting theory...")
            theory_result = orchestrator.execute_tool(
                "T302_THEORY_EXTRACTION", 
                ToolRequest(input_data={"text": extracted_text})
            )
            
            if theory_result.status != "success":
                return {"status": "error", "error": "Theory extraction failed", "details": theory_result.error_details}
                
            # Store theory-enhanced entities for downstream processing
            workflow_data["theory_entities"] = theory_result.data["kgas_entities"]
            workflow_data["theory_relationships"] = theory_result.data["kgas_relationships"]
            workflow_data["theory_schema"] = theory_result.data["theory_schema"]
            results["theory_extraction"] = theory_result
            logger.info(f"✅ Theory extracted: {len(theory_result.data['kgas_entities'])} entities, {len(theory_result.data['kgas_relationships'])} relationships")
            
            # Step 3: Text Chunking
            logger.info("Step 3: Chunking text...")
            chunk_result = orchestrator.execute_tool(
                "T15A_TEXT_CHUNKER",
                ToolRequest(input_data={
                    "text": extracted_text,
                    "chunk_size": 512,
                    "theory_context": workflow_data["theory_schema"]  # Add theory context
                })
            )
            
            results["text_chunking"] = chunk_result
            if chunk_result.status == "success":
                logger.info(f"✅ Text chunked: {len(chunk_result.data.get('chunks', []))} chunks")
            
            # Step 4: Entity Building (theory-enhanced)
            logger.info("Step 4: Building entities...")
            entity_result = orchestrator.execute_tool(
                "T31_ENTITY_BUILDER", 
                ToolRequest(input_data={
                    "entities": workflow_data["theory_entities"],
                    "source_ref": pdf_path
                })
            )
            
            results["entity_building"] = entity_result
            if entity_result.status == "success":
                logger.info(f"✅ Entities built in graph database")
            
            # Step 5: Relationship Building
            logger.info("Step 5: Building relationships...")
            relationship_result = orchestrator.execute_tool(
                "T34_EDGE_BUILDER",
                ToolRequest(input_data={
                    "relationships": workflow_data["theory_relationships"],
                    "source_ref": pdf_path
                })
            )
            
            results["relationship_building"] = relationship_result
            if relationship_result.status == "success":
                logger.info(f"✅ Relationships built in graph database")
            
            # Step 6: PageRank Calculation
            logger.info("Step 6: Calculating PageRank...")
            pagerank_result = orchestrator.execute_tool(
                "T68_PAGERANK",
                ToolRequest(input_data={"graph_ref": "neo4j://graph/main"})
            )
            
            results["pagerank"] = pagerank_result
            if pagerank_result.status == "success":
                logger.info(f"✅ PageRank calculated")
            
            logger.info("🎉 Theory-enhanced workflow completed successfully")
            
            return {
                "status": "success",
                "workflow_results": results,
                "theory_metadata": {
                    "entities_created": len(workflow_data["theory_entities"]),
                    "relationships_created": len(workflow_data["theory_relationships"]),
                    "theory_type": theory_result.data["extraction_metadata"]["theory_type"],
                    "theory_title": workflow_data["theory_schema"]["title"]
                }
            }
            
        except Exception as e:
            logger.error(f"Theory-enhanced workflow failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "workflow_results": results
            }