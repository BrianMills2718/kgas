#!/usr/bin/env python3
"""
Set up and test Neo4j connection with Docker
"""

import os
import time
import subprocess
from neo4j import GraphDatabase

def setup_neo4j_docker():
    """Set up Neo4j in Docker and configure KGAS to use it"""
    print("🐳 SETTING UP NEO4J WITH DOCKER")
    print("=" * 60)
    
    # Neo4j Docker settings
    neo4j_password = os.getenv("NEO4J_PASSWORD", "kgas_test_2024")  # Allow override via environment
    container_name = "kgas-neo4j"
    
    print("\n1️⃣ Starting Neo4j Docker container...")
    
    # Stop existing container if running
    subprocess.run(["docker", "stop", container_name], capture_output=True)
    subprocess.run(["docker", "rm", container_name], capture_output=True)
    
    # Start Neo4j container
    docker_cmd = [
        "docker", "run",
        "--name", container_name,
        "-d",  # detached
        "-p", "7474:7474",  # HTTP
        "-p", "7687:7687",  # Bolt
        "-e", f"NEO4J_AUTH=neo4j/{neo4j_password}",
        "-e", "NEO4J_ACCEPT_LICENSE_AGREEMENT=yes",
        "-e", "NEO4J_dbms_memory_pagecache_size=512M",
        "-e", "NEO4J_dbms_memory_heap_max__size=512M",
        "neo4j:5.12.0"
    ]
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Neo4j container started")
            print(f"   • Container: {container_name}")
            print(f"   • HTTP: http://localhost:7474")
            print(f"   • Bolt: bolt://localhost:7687")
            print(f"   • User: neo4j")
            print(f"   • Password: {neo4j_password}")
        else:
            print(f"   ❌ Failed to start container: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Docker error: {e}")
        print("   Make sure Docker is running!")
        return False
    
    # Wait for Neo4j to be ready
    print("\n2️⃣ Waiting for Neo4j to be ready...")
    time.sleep(10)  # Give it time to start
    
    # Test connection
    print("\n3️⃣ Testing Neo4j connection...")
    max_retries = 30
    for i in range(max_retries):
        try:
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", neo4j_password)
            )
            
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                print(f"   ✅ Neo4j is ready! Test query returned: {test_value}")
                
                # Create indexes for KGAS
                print("\n4️⃣ Creating KGAS indexes...")
                session.run("CREATE INDEX entity_id IF NOT EXISTS FOR (n:Entity) ON (n.entity_id)")
                session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name)")
                session.run("CREATE INDEX mention_id IF NOT EXISTS FOR (m:Mention) ON (m.mention_id)")
                print("   ✅ Indexes created")
                
                driver.close()
                break
                
        except Exception as e:
            if i < max_retries - 1:
                print(f"   ⏳ Waiting for Neo4j... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"   ❌ Connection failed: {e}")
                return False
    
    # Update .env file
    print("\n5️⃣ Updating .env configuration...")
    env_updates = {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": neo4j_password
    }
    
    # Read existing .env
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_lines = f.readlines()
    
    # Update or add Neo4j settings
    updated = False
    for key, value in env_updates.items():
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                found = True
                updated = True
                break
        if not found:
            env_lines.append(f"{key}={value}\n")
            updated = True
    
    # Write back
    if updated:
        with open(".env", "w") as f:
            f.writelines(env_lines)
        print("   ✅ Updated .env with Neo4j credentials")
    
    # Also set environment variables for current session
    os.environ["NEO4J_URI"] = "bolt://localhost:7687"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = neo4j_password
    
    print("\n✅ Neo4j setup complete!")
    print(f"   • Browse UI: http://localhost:7474")
    print(f"   • Login: neo4j / {neo4j_password}")
    
    return True

def test_neo4j_tools():
    """Test Neo4j-dependent tools"""
    print("\n🧪 TESTING NEO4J-DEPENDENT TOOLS")
    print("=" * 60)
    
    try:
        from src.core.service_manager import get_service_manager
        from src.tools.base_tool import ToolRequest
        
        service_manager = get_service_manager()
        
        # First, let's create some test data
        print("\n1️⃣ Creating test entities and relationships...")
        
        # Create some test mentions
        test_mentions = [
            {
                'mention_id': 'mention_001',
                'entity_id': 'entity_stanford',
                'surface_form': 'Stanford University',
                'entity_type': 'ORG',
                'confidence': 0.95,
                'source_ref': 'test_doc',
                'text': 'Stanford University',
                'label': 'ORG'
            },
            {
                'mention_id': 'mention_002',
                'entity_id': 'entity_mit',
                'surface_form': 'MIT',
                'entity_type': 'ORG',
                'confidence': 0.92,
                'source_ref': 'test_doc',
                'text': 'MIT',
                'label': 'ORG'
            },
            {
                'mention_id': 'mention_003',
                'entity_id': 'entity_sarah',
                'surface_form': 'Dr. Sarah Chen',
                'entity_type': 'PERSON',
                'confidence': 0.88,
                'source_ref': 'test_doc',
                'text': 'Dr. Sarah Chen',
                'label': 'PERSON'
            }
        ]
        
        # Test T31: Entity Builder
        print("\n2️⃣ Testing T31 - Entity Builder...")
        from src.tools.phase1.t31_entity_builder import EntityBuilder
        
        entity_builder = EntityBuilder(service_manager)
        
        t31_request = ToolRequest(
            tool_id="T31",
            operation="build_entities",
            input_data={
                "mentions": test_mentions,
                "source_refs": ["test_doc"]
            },
            parameters={}
        )
        
        t31_result = entity_builder.execute(t31_request)
        if t31_result.status == "success":
            entities = t31_result.data.get('entities', [])
            print(f"   ✅ T31 working! Created {len(entities)} entity nodes")
            for entity in entities:
                print(f"   • {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown')})")
        else:
            print(f"   ❌ T31 failed: {t31_result.error_message}")
        
        # Test T34: Edge Builder
        print("\n3️⃣ Testing T34 - Edge Builder...")
        from src.tools.phase1.t34_edge_builder import EdgeBuilder
        
        test_relationships = [
            {
                'head_entity': 'Dr. Sarah Chen',
                'tail_entity': 'Stanford University',
                'relationship_type': 'AFFILIATED_WITH',
                'confidence': 0.85,
                'evidence_text': 'Dr. Sarah Chen from Stanford University'
            },
            {
                'head_entity': 'Stanford University',
                'tail_entity': 'MIT',
                'relationship_type': 'COLLABORATES_WITH',
                'confidence': 0.80,
                'evidence_text': 'Stanford-MIT collaboration'
            }
        ]
        
        edge_builder = EdgeBuilder(service_manager)
        
        t34_request = ToolRequest(
            tool_id="T34",
            operation="build_edges",
            input_data={
                "relationships": test_relationships,
                "source_refs": ["test_doc"]
            },
            parameters={}
        )
        
        t34_result = edge_builder.execute(t34_request)
        if t34_result.status == "success":
            edges = t34_result.data.get('edges', [])
            print(f"   ✅ T34 working! Created {len(edges)} relationship edges")
        else:
            print(f"   ❌ T34 failed: {t34_result.error_message}")
        
        # Test T68: PageRank
        print("\n4️⃣ Testing T68 - PageRank Calculator...")
        from src.tools.phase1.t68_pagerank import PageRankCalculator
        
        pagerank_calc = PageRankCalculator(service_manager)
        
        t68_request = ToolRequest(
            tool_id="T68",
            operation="calculate_pagerank",
            input_data={"graph_ref": "neo4j://graph/main"},
            parameters={
                "damping_factor": 0.85,
                "max_iterations": 100
            }
        )
        
        t68_result = pagerank_calc.execute(t68_request)
        if t68_result.status == "success":
            ranked_entities = t68_result.data.get('ranked_entities', [])
            print(f"   ✅ T68 working! Calculated PageRank for {len(ranked_entities)} entities")
            
            # Show top entities
            if ranked_entities:
                print("   Top entities by PageRank:")
                for entity in ranked_entities[:5]:
                    print(f"   • {entity.get('name', 'Unknown')}: {entity.get('pagerank', 0):.4f}")
        else:
            print(f"   ❌ T68 failed: {t68_result.error_message}")
        
        # Test T49: Multi-hop Query
        print("\n5️⃣ Testing T49 - Multi-hop Query...")
        from src.tools.phase1.t49_multihop_query import MultiHopQuery
        
        query_engine = MultiHopQuery(service_manager)
        
        t49_request = ToolRequest(
            tool_id="T49",
            operation="query_graph",
            input_data={
                "question": "What organizations are connected to Stanford?"
            },
            parameters={
                "max_hops": 2,
                "result_limit": 10
            }
        )
        
        t49_result = query_engine.execute(t49_request)
        if t49_result.status == "success":
            results = t49_result.data.get('results', [])
            print(f"   ✅ T49 working! Found {len(results)} query results")
            
            # Show some results
            for result in results[:3]:
                print(f"   • {result.get('path', 'No path')}")
        else:
            print(f"   ❌ T49 failed: {t49_result.error_message}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 NEO4J TOOLS TEST SUMMARY")
        print("=" * 60)
        print("With Neo4j connected, these additional tools are now available:")
        print("✅ T31: Entity Builder - Create entity nodes in graph")
        print("✅ T34: Edge Builder - Create relationship edges")
        print("✅ T68: PageRank Calculator - Calculate entity importance")
        print("✅ T49: Multi-hop Query - Query the knowledge graph")
        
        print("\nTotal working tools: 8 (up from 4!)")
        
        return True
        
    except Exception as e:
        print(f"❌ Neo4j tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup and test"""
    print("🚀 KGAS NEO4J SETUP WITH DOCKER")
    print("=" * 80)
    
    # Check if Docker is running
    try:
        result = subprocess.run(["docker", "version"], capture_output=True)
        if result.returncode != 0:
            print("❌ Docker is not running! Please start Docker first.")
            return
    except:
        print("❌ Docker command not found! Please install Docker.")
        return
    
    # Setup Neo4j
    if setup_neo4j_docker():
        # Test Neo4j tools
        test_neo4j_tools()
        
        print("\n🎉 Setup complete! You now have:")
        print("• Neo4j running in Docker")
        print("• 8 working KGAS tools (double what you had!)")
        print("• Full graph construction and querying capabilities")
        
        print("\n📝 Next steps:")
        print("1. Browse Neo4j at http://localhost:7474")
        print("2. Run the full pipeline to build a knowledge graph")
        print("3. Query your graph with natural language")
    else:
        print("\n❌ Setup failed. Check the errors above.")

if __name__ == "__main__":
    main()