#!/usr/bin/env python3
"""
Complete Multi-Modal Demonstration with Real Vector Embeddings
Using OpenAI text-embedding-3-small or local all-MiniLM-L6-v2
"""

import asyncio
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.tool_registry import ToolRegistry
from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorEmbedder:
    """Handle vector embeddings with OpenAI or local models"""
    
    def __init__(self, model_type: str = "openai"):
        self.model_type = model_type
        self.embeddings = None
        
        if model_type == "openai":
            self._setup_openai()
        elif model_type == "local":
            self._setup_local()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _setup_openai(self):
        """Setup OpenAI embeddings"""
        try:
            import openai
            from openai import OpenAI
            
            # Get API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            self.client = OpenAI(api_key=api_key)
            self.model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
            self.embedding_dim = 1536  # text-embedding-3-small dimension
            logger.info(f"✅ OpenAI embeddings initialized with {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup OpenAI: {e}")
            raise
    
    def _setup_local(self):
        """Setup local sentence-transformers embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            
            # Use all-MiniLM-L6-v2 as requested
            self.model_name = "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
            logger.info(f"✅ Local embeddings initialized with {self.model_name}")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        if self.model_type == "openai":
            return self._embed_openai(texts)
        else:
            return self._embed_local(texts)
    
    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            # OpenAI API handles batching internally
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings with OpenAI {self.model_name}")
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
    
    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        try:
            # Encode texts to get embeddings
            embeddings = self.model.encode(texts, convert_to_numpy=False)
            
            # Convert to list format
            embeddings_list = [emb.tolist() for emb in embeddings]
            
            logger.info(f"Generated {len(embeddings_list)} embeddings with local {self.model_name}")
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            raise

async def create_sample_document():
    """Create a sample document for demonstration"""
    doc_path = Path("multimodal_demo_document_real.txt")
    
    content = """Apple Inc. Financial Report Q4 2024

Executive Summary:
Tim Cook, CEO of Apple Inc., announced record-breaking revenue of $123.9 billion for Q4 2024. The company, headquartered in Cupertino, California, continues to lead innovation in consumer technology.

Key Partnerships:
Apple Inc. has strengthened its partnership with TSMC for chip manufacturing. The collaboration with Foxconn remains crucial for iPhone production. Samsung supplies display components despite market competition.

Competition Analysis:  
Apple competes directly with Samsung, Google, and Microsoft in various market segments. The smartphone market shows Apple leading with 28% market share, followed by Samsung at 22%.

Innovation Initiatives:
The Apple Vision Pro, led by Mike Rockwell, represents the company's entry into spatial computing. John Giannandrea directs AI research, focusing on improving Siri and machine learning capabilities.

Geographic Presence:
Major operations in Cupertino, Austin, Shanghai, London, and Singapore support global distribution."""
    
    doc_path.write_text(content)
    logger.info(f"✅ Created sample document: {doc_path} ({len(content)} chars)")
    return doc_path, content

async def demonstrate_real_vectors():
    """Demonstrate multi-modal analysis with real vector embeddings"""
    
    print("\n" + "="*60)
    print("🚀 MULTI-MODAL ANALYSIS WITH REAL VECTOR EMBEDDINGS")
    print("="*60)
    
    # Initialize components
    service_manager = ServiceManager()
    registry = ToolRegistry()
    
    # Create sample document
    doc_path, doc_content = await create_sample_document()
    
    # Phase 1: Linear Pipeline (Document → Entities → Graph)
    print("\n📊 Phase 1: Linear Pipeline")
    print("-" * 40)
    
    # Step 1: Text Chunking
    T15A = registry.get_tool("T15A")
    chunk_request = ToolRequest(
        input_data={
            "text": doc_content,
            "document_ref": str(doc_path),
            "chunk_size": 512,
            "overlap": 50
        },
        options={"workflow_id": "demo_workflow"}
    )
    
    chunk_result = T15A.execute(chunk_request)
    chunks = chunk_result.data.get("chunks", [])
    print(f"✅ Text chunked: {len(chunks)} chunks created")
    
    # Step 2: Entity Extraction
    T23A = registry.get_tool("T23A")
    entities = []
    
    for chunk in chunks:
        extract_request = ToolRequest(
            input_data={
                "text": chunk["text"],
                "chunk_ref": chunk["chunk_ref"]
            },
            options={"confidence_threshold": 0.8}
        )
        
        extract_result = T23A.execute(extract_request)
        if extract_result.status == "success":
            entities.extend(extract_result.data.get("entities", []))
    
    # Deduplicate entities
    unique_entities = {}
    for entity in entities:
        key = entity["name"]
        if key not in unique_entities or entity["confidence"] > unique_entities[key]["confidence"]:
            unique_entities[key] = entity
    
    entities = list(unique_entities.values())
    print(f"✅ Entities extracted: {len(entities)} unique entities")
    
    # Step 3: Build Graph
    T31 = registry.get_tool("T31")
    graph_request = ToolRequest(
        input_data={
            "entities": entities,
            "source_refs": [str(doc_path)]
        },
        options={}
    )
    
    graph_result = T31.execute(graph_request)
    print(f"✅ Graph built: {graph_result.data.get('entities_created', 0)} nodes created")
    
    # Phase 2: REAL Vector Embeddings
    print("\n🔮 Phase 2: Real Vector Embeddings")
    print("-" * 40)
    
    # Choose embedding model based on availability
    model_type = "openai" if os.getenv("OPENAI_API_KEY") else "local"
    
    if model_type == "openai":
        print(f"Using OpenAI {os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')}")
    else:
        print("Using local all-MiniLM-L6-v2 (install sentence-transformers if needed)")
    
    try:
        # Initialize vector embedder
        embedder = VectorEmbedder(model_type=model_type)
        
        # Prepare texts for embedding
        entity_texts = [f"{e['name']} ({e['entity_type']})" for e in entities]
        
        # Generate real embeddings
        start_time = time.time()
        embeddings = embedder.embed_texts(entity_texts)
        embed_time = time.time() - start_time
        
        print(f"✅ Generated {len(embeddings)} real embeddings")
        print(f"   Model: {embedder.model_name}")
        print(f"   Dimensions: {embedder.embedding_dim}")
        print(f"   Time: {embed_time:.3f}s")
        
        # Create embedding records
        vector_data = {}
        for entity, embedding in zip(entities, embeddings):
            vector_data[entity["name"]] = {
                "entity_type": entity["entity_type"],
                "embedding": embedding[:10],  # Store first 10 dims for display
                "full_dimension": len(embedding),
                "model": embedder.model_name
            }
        
        # Calculate cosine similarities
        print("\n📐 Vector Similarity Analysis:")
        
        # Import numpy for cosine similarity
        import numpy as np
        
        def cosine_similarity(v1, v2):
            """Calculate cosine similarity between two vectors"""
            v1 = np.array(v1)
            v2 = np.array(v2)
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        
        # Find most similar entities to "Apple Inc."
        if "Apple Inc." in [e["name"] for e in entities]:
            apple_idx = next(i for i, e in enumerate(entities) if e["name"] == "Apple Inc.")
            apple_embedding = embeddings[apple_idx]
            
            similarities = []
            for i, (entity, embedding) in enumerate(zip(entities, embeddings)):
                if i != apple_idx:
                    sim = cosine_similarity(apple_embedding, embedding)
                    similarities.append((entity["name"], sim))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            print("Most similar to 'Apple Inc.':")
            for name, sim in similarities[:3]:
                print(f"  - {name}: {sim:.4f}")
        
    except Exception as e:
        logger.error(f"Vector embedding failed: {e}")
        print(f"❌ Vector embedding failed: {e}")
        print("\nTo use local embeddings, install: pip install sentence-transformers")
        print("To use OpenAI, ensure OPENAI_API_KEY is set in .env")
        return
    
    # Phase 3: Parallel Analysis (PageRank + Table Export)
    print("\n⚡ Phase 3: Parallel Analysis")
    print("-" * 40)
    
    async def run_pagerank():
        T68 = registry.get_tool("T68")
        pr_request = ToolRequest(
            input_data={"graph_ref": "neo4j://graph/main"},
            options={}
        )
        start = time.time()
        result = T68.execute(pr_request)
        return result, time.time() - start
    
    async def run_table_export():
        table_exporter = registry.get_tool("graph_table_exporter")
        if not table_exporter:
            logger.warning("Table exporter not found")
            return None, 0
        
        export_request = ToolRequest(
            input_data={
                "graph_data": {"entities": entities},
                "table_type": "edge_list"
            },
            options={}
        )
        start = time.time()
        result = table_exporter.execute(export_request)
        return result, time.time() - start
    
    # Execute in parallel
    (pagerank_result, pr_time), (table_result, te_time) = await asyncio.gather(
        run_pagerank(),
        run_table_export()
    )
    
    if pagerank_result and pagerank_result.status == "success":
        print(f"✅ PageRank completed in {pr_time:.3f}s")
        scores = pagerank_result.data.get("pagerank_scores", [])
        if scores:
            print("   Top entities by PageRank:")
            for entity, score in scores[:3]:
                print(f"   - {entity}: {score:.4f}")
    
    if table_result and table_result.status == "success":
        print(f"✅ Table export completed in {te_time:.3f}s")
    
    # Save results
    output_file = Path("multimodal_demo_real_vectors.json")
    results = {
        "graph_entities": len(entities),
        "vector_embeddings": {
            "model": embedder.model_name,
            "dimension": embedder.embedding_dim,
            "count": len(embeddings),
            "sample_vectors": vector_data
        },
        "pagerank_top": scores[:3] if pagerank_result else [],
        "execution_time": pr_time + te_time + embed_time
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE WITH REAL VECTORS")
    print("="*60)
    
    # Cleanup
    doc_path.unlink()

if __name__ == "__main__":
    asyncio.run(demonstrate_real_vectors())