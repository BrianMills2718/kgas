#!/usr/bin/env python3
"""
Simple test of MCP-based relationship extraction to validate fixes work via MCP protocol.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

async def test_mcp_relationship_extraction():
    """Test relationship extraction via MCP using FastMCP client"""
    
    print("🔌 Testing MCP-Based Relationship Extraction")
    print("   Goal: Validate fixes work via MCP protocol")
    print("   Method: FastMCP Client → KGAS MCP Server")
    print("=" * 60)
    
    try:
        from fastmcp import Client
        
        # Create client pointing to our MCP server
        client = Client("kgas_mcp_server.py")
        
        async with client:
            print("✅ Connected to KGAS MCP server")
            
            # Test content with clear relationships
            test_content = "Dr. Sarah Chen works at MIT Computer Science Department. She collaborates with Prof. Michael Rodriguez from Stanford University."
            
            print(f"📝 Test content: {test_content}")
            
            # Step 1: Text chunking via MCP
            print("\n🔧 Step 1: MCP chunk_text")
            chunk_result = await client.call_tool("chunk_text", {
                "document_ref": "storage://mcp_test/test.txt",
                "text": test_content,
                "document_confidence": 0.9,
                "chunk_size": 500,
                "overlap": 50
            })
            
            print(f"   Chunk result type: {type(chunk_result)}")
            
            # FastMCP returns TextContent objects, need to parse JSON
            if isinstance(chunk_result, list) and len(chunk_result) > 0:
                # Extract JSON from TextContent
                chunk_json_str = chunk_result[0].text
                chunk_data = json.loads(chunk_json_str)
                print(f"   Parsed chunk data: {chunk_data}")
            else:
                print(f"❌ Unexpected chunk result format: {chunk_result}")
                return False
            
            if "error" in chunk_data:
                print(f"❌ Chunking failed: {chunk_data['error']}")
                return False
            
            chunks = chunk_data.get("chunks", [])
            if not chunks:
                print("❌ No chunks returned")
                return False
            
            print(f"   ✅ Created {len(chunks)} chunks")
            chunk = chunks[0]  # Use first chunk
            
            # Step 2: Entity extraction via MCP
            print("\n🔧 Step 2: MCP extract_entities")
            entity_result = await client.call_tool("extract_entities", {
                "chunk_ref": chunk["chunk_ref"],
                "text": chunk["text"],
                "chunk_confidence": chunk.get("confidence", 0.8),
                "confidence_threshold": 0.3
            })
            
            print(f"   Entity result type: {type(entity_result)}")
            
            # Parse entity result from FastMCP
            if isinstance(entity_result, list) and len(entity_result) > 0:
                entity_json_str = entity_result[0].text
                entity_data = json.loads(entity_json_str)
                print(f"   Parsed entity data keys: {list(entity_data.keys())}")
            else:
                print(f"❌ Unexpected entity result format: {entity_result}")
                return False
            
            if "error" in entity_data:
                print(f"❌ Entity extraction failed: {entity_data['error']}")
                return False
                
            entities = entity_data.get("entities", [])
            if not entities:
                print("❌ No entities returned")
                return False
                
            print(f"   ✅ Extracted {len(entities)} entities")
            for i, entity in enumerate(entities):
                print(f"     {i+1}. {entity.get('surface_form')} ({entity.get('entity_type')})")
            
            # Step 3: Format conversion for T27
            print("\n🔧 Step 3: Format conversion (T23A → T27)")
            t27_entities = []
            for entity in entities:
                t27_entity = {
                    'text': entity.get('surface_form', ''),
                    'label': entity.get('entity_type', ''),
                    'start': entity.get('start_pos', 0),
                    'end': entity.get('end_pos', 0)
                }
                t27_entities.append(t27_entity)
            
            print(f"   ✅ Converted {len(t27_entities)} entities to T27 format")
            
            # Step 4: Relationship extraction via MCP
            print("\n🔧 Step 4: MCP extract_relationships")
            relationship_result = await client.call_tool("extract_relationships", {
                "chunk_ref": chunk["chunk_ref"],
                "text": chunk["text"],
                "entities": t27_entities,
                "confidence": 0.1
            })
            
            print(f"   Relationship result type: {type(relationship_result)}")
            
            # Parse relationship result from FastMCP
            if isinstance(relationship_result, list) and len(relationship_result) > 0:
                rel_json_str = relationship_result[0].text
                rel_data = json.loads(rel_json_str)
                print(f"   Parsed relationship data keys: {list(rel_data.keys())}")
            else:
                print(f"❌ Unexpected relationship result format: {relationship_result}")
                return False
            
            if "error" in rel_data:
                print(f"❌ Relationship extraction failed: {rel_data['error']}")
                return False
            
            relationships = rel_data.get("relationships", [])
            
            print(f"\n📊 FINAL MCP RESULTS:")
            print(f"   Entities: {len(entities)}")
            print(f"   Relationships: {len(relationships)}")
            
            if len(relationships) > 0:
                print(f"\n🎉 SUCCESS: MCP relationship extraction working!")
                print(f"   ✅ MCP protocol: Working")
                print(f"   ✅ Tool chain: Chunk → Entity → Relationship")
                print(f"   ✅ Format conversion: T23A → T27 via MCP")
                
                print(f"\n📋 Extracted Relationships:")
                for i, rel in enumerate(relationships):
                    source = rel.get("source_entity", "Unknown")
                    rel_type = rel.get("relationship_type", "Unknown")
                    target = rel.get("target_entity", "Unknown")
                    conf = rel.get("confidence", 0.0)
                    print(f"   {i+1}. {source} → {rel_type} → {target} (conf: {conf:.2f})")
                
                return True
            else:
                print(f"\n❌ FAILURE: No relationships extracted via MCP")
                print(f"   Issue may be in MCP tool interface or T27 integration")
                return False
            
    except Exception as e:
        print(f"💥 MCP TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_relationship_extraction())
    if success:
        print(f"\n🚀 MCP ARCHITECTURE VALIDATION: SUCCESS")
        print(f"   Recommendation: Continue with MCP-based stress tests")
    else:
        print(f"\n⚠️ MCP ARCHITECTURE NEEDS DEBUGGING")
        print(f"   Recommendation: Fix MCP integration issues first")
    
    sys.exit(0 if success else 1)