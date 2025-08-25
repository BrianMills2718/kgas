#!/usr/bin/env python3
"""
Real Facade Implementation for KGAS Tool Compatibility
Based on successful kill-switch test - T31 accepts synthetic mentions
"""

import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Set environment variables for testing
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'devpassword'

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import uuid
import time
import logging
from pathlib import Path

# Import core services
from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest, ToolResult

# Import real tools
from src.tools.phase1.t03_text_loader_unified import T03TextLoaderUnified
from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FacadeRequest:
    """Simplified request format for facade"""
    text: str
    document_id: Optional[str] = None
    extract_entities: bool = True
    build_graph: bool = True
    include_edges: bool = True


@dataclass
class FacadeResult:
    """Simplified result format for facade"""
    success: bool
    entities: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class EntityToMentionTranslator:
    """Translate T23C entities to T31 mentions"""
    
    def translate(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert entities from T23C format to T31 mention format"""
        mentions = []
        
        for entity in entities:
            # T23C provides resolved entities, T31 needs raw mentions
            # Create synthetic mention data that T31 can process
            mention = {
                "text": entity.get("name", entity.get("surface_form", "")),
                "entity_type": entity.get("type", entity.get("entity_type", "UNKNOWN")),
                "start_pos": entity.get("start_pos", 0),  # Use real if available, else synthetic
                "end_pos": entity.get("end_pos", len(entity.get("name", ""))),  # Synthetic if needed
                "confidence": entity.get("confidence", 0.85)
            }
            
            # Add any additional properties
            if "properties" in entity:
                mention["properties"] = entity["properties"]
            
            mentions.append(mention)
        
        logger.info(f"Translated {len(entities)} entities to {len(mentions)} mentions")
        return mentions


class RelationshipToEdgeTranslator:
    """Translate T23C relationships to T34 edge format"""
    
    def translate(self, relationships: List[Dict[str, Any]], entity_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Convert relationships from T23C format to T34 edge format"""
        edges = []
        
        for rel in relationships:
            # Map entity names to IDs if needed
            source = rel.get("source", rel.get("subject"))
            target = rel.get("target", rel.get("object"))
            
            # Create edge in T34 expected format
            edge = {
                "source_entity": source,
                "target_entity": target,
                "relationship_type": rel.get("type", rel.get("predicate", "RELATED_TO")),
                "confidence": rel.get("confidence", 0.7),
                "evidence": rel.get("evidence_text", ""),
                "properties": rel.get("properties", {})
            }
            
            edges.append(edge)
        
        logger.info(f"Translated {len(relationships)} relationships to {len(edges)} edges")
        return edges


class KGASToolFacade:
    """
    Unified facade for KGAS tools - hides complexity behind simple interface
    """
    
    def __init__(self):
        """Initialize facade with real tools and services"""
        logger.info("Initializing KGAS Tool Facade...")
        
        # Initialize service manager
        self.service_manager = ServiceManager()
        
        # Initialize tools with service manager
        self.t03_loader = T03TextLoaderUnified(self.service_manager)
        self.t23c_extractor = OntologyAwareExtractor(self.service_manager)
        self.t31_entity_builder = T31EntityBuilderUnified(self.service_manager)
        self.t34_edge_builder = T34EdgeBuilderUnified(self.service_manager)
        
        # Initialize translators
        self.entity_translator = EntityToMentionTranslator()
        self.edge_translator = RelationshipToEdgeTranslator()
        
        logger.info("Facade initialization complete")
    
    def process_text(self, request: FacadeRequest) -> FacadeResult:
        """
        Process text through the full pipeline with simplified interface
        
        This single method replaces the complex orchestration of:
        - T03 text loading
        - T23C entity/relationship extraction
        - T31 entity building
        - T34 edge building
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing text (length: {len(request.text)} chars)")
            
            # Step 1: Load text (T03)
            if request.document_id is None:
                request.document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Create a temporary file for T03 (it expects a file path)
            temp_file = f"/tmp/{request.document_id}.txt"
            with open(temp_file, 'w') as f:
                f.write(request.text)
            
            t03_request = ToolRequest(input_data={"file_path": temp_file})
            t03_result = self.t03_loader.execute(t03_request)
            
            if t03_result.status != "success":
                return FacadeResult(
                    success=False,
                    entities=[],
                    edges=[],
                    metadata={},
                    error=f"Text loading failed: {t03_result.error_details}"
                )
            
            loaded_text = t03_result.data.get("document", {}).get("text", request.text)
            
            # Step 2: Extract entities and relationships (T23C)
            entities = []
            relationships = []
            
            if request.extract_entities:
                t23c_request = ToolRequest(input_data={
                    "text": loaded_text,
                    "chunk_ref": request.document_id
                })
                t23c_result = self.t23c_extractor.execute(t23c_request)
                
                if t23c_result.status == "success":
                    entities = t23c_result.data.get("entities", [])
                    relationships = t23c_result.data.get("relationships", [])
                    logger.info(f"Extracted {len(entities)} entities and {len(relationships)} relationships")
                else:
                    logger.warning(f"Entity extraction failed: {t23c_result.error_details}")
            
            # Step 3: Build graph entities (T31)
            graph_entities = []
            
            if request.build_graph and entities:
                # Translate entities to mentions for T31
                mentions = self.entity_translator.translate(entities)
                
                t31_request = ToolRequest(input_data={"mentions": mentions})
                t31_result = self.t31_entity_builder.execute(t31_request)
                
                if t31_result.status == "success":
                    graph_entities = t31_result.data.get("entities", [])
                    logger.info(f"Built {len(graph_entities)} graph entities")
                else:
                    logger.warning(f"Entity building failed: {t31_result.error_details}")
            
            # Step 4: Build graph edges (T34)
            graph_edges = []
            
            if request.include_edges and relationships and graph_entities:
                # Create entity map for edge translation
                entity_map = {e.get("name", ""): e.get("id", "") for e in graph_entities}
                
                # Translate relationships to edges
                edges = self.edge_translator.translate(relationships, entity_map)
                
                t34_request = ToolRequest(input_data={"relationships": edges})
                t34_result = self.t34_edge_builder.execute(t34_request)
                
                if t34_result.status == "success":
                    graph_edges = t34_result.data.get("edges", [])
                    logger.info(f"Built {len(graph_edges)} graph edges")
                else:
                    logger.warning(f"Edge building failed: {t34_result.error_details}")
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Return simplified result
            return FacadeResult(
                success=True,
                entities=graph_entities,
                edges=graph_edges,
                metadata={
                    "document_id": request.document_id,
                    "text_length": len(request.text),
                    "entities_extracted": len(entities),
                    "entities_built": len(graph_entities),
                    "relationships_extracted": len(relationships),
                    "edges_built": len(graph_edges),
                    "execution_time": execution_time,
                    "tools_used": ["T03", "T23C", "T31", "T34"]
                }
            )
            
        except Exception as e:
            logger.error(f"Facade processing failed: {str(e)}", exc_info=True)
            return FacadeResult(
                success=False,
                entities=[],
                edges=[],
                metadata={"execution_time": time.time() - start_time},
                error=str(e)
            )
    
    def process_document(self, file_path: str) -> FacadeResult:
        """Process a document file through the pipeline"""
        try:
            # Read the document
            with open(file_path, 'r') as f:
                text = f.read()
            
            # Create request
            request = FacadeRequest(
                text=text,
                document_id=Path(file_path).stem,
                extract_entities=True,
                build_graph=True,
                include_edges=True
            )
            
            # Process through facade
            return self.process_text(request)
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return FacadeResult(
                success=False,
                entities=[],
                edges=[],
                metadata={},
                error=str(e)
            )


def demonstrate_facade():
    """Demonstrate the facade with sample text"""
    
    print("=" * 60)
    print("KGAS TOOL FACADE DEMONSTRATION")
    print("=" * 60)
    
    # Initialize facade
    facade = KGASToolFacade()
    
    # Sample text for testing
    sample_text = """
    Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino, California.
    The company was co-founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    Apple's products include the iPhone, iPad, and MacBook, which are sold worldwide.
    Tim Cook took over as CEO after Steve Jobs resigned in 2011.
    The company has retail stores in major cities like New York, London, and Tokyo.
    """
    
    print("\n📄 Input Text:")
    print("-" * 40)
    print(sample_text[:200] + "..." if len(sample_text) > 200 else sample_text)
    
    # Create simple request
    request = FacadeRequest(
        text=sample_text,
        extract_entities=True,
        build_graph=True,
        include_edges=True
    )
    
    print("\n🔄 Processing through facade...")
    print("-" * 40)
    
    # Process with facade - ONE simple call instead of complex orchestration
    result = facade.process_text(request)
    
    print("\n✅ Results:")
    print("-" * 40)
    
    if result.success:
        print(f"Success: {result.success}")
        print(f"Entities built: {len(result.entities)}")
        print(f"Edges built: {len(result.edges)}")
        print(f"Execution time: {result.metadata.get('execution_time', 0):.2f} seconds")
        
        print("\n📊 Metadata:")
        for key, value in result.metadata.items():
            print(f"  {key}: {value}")
        
        if result.entities:
            print("\n🏢 Sample Entities (first 3):")
            for entity in result.entities[:3]:
                print(f"  - {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
        
        if result.edges:
            print("\n🔗 Sample Edges (first 3):")
            for edge in result.edges[:3]:
                print(f"  - {edge.get('source_entity', 'N/A')} -> {edge.get('target_entity', 'N/A')} ({edge.get('relationship_type', 'N/A')})")
    else:
        print(f"❌ Processing failed: {result.error}")
    
    print("\n" + "=" * 60)
    
    # Compare complexity
    print("\n📈 COMPLEXITY COMPARISON:")
    print("-" * 40)
    print("Without Facade (original approach):")
    print("  - Initialize 4+ tools separately")
    print("  - Manage complex data transformations")
    print("  - Handle incompatible interfaces")
    print("  - Orchestrate workflow manually")
    print("  - ~200+ lines of code")
    
    print("\nWith Facade (new approach):")
    print("  - Single facade initialization")
    print("  - Simple request/result format")
    print("  - Automatic data translation")
    print("  - Built-in orchestration")
    print("  - ~10 lines of code")
    
    print("\n🎯 Complexity Reduction: ~20x simpler!")
    
    return result


if __name__ == "__main__":
    result = demonstrate_facade()
    sys.exit(0 if result.success else 1)