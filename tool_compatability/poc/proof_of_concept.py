#!/usr/bin/env python3
"""
PROOF OF CONCEPT: Framework with Real Tools and Services
This must work with NO MOCKS for Gemini (mock Neo4j is OK)
"""

import sys
import os
from pathlib import Path
import time
import psutil

# Setup paths
poc_dir = Path(__file__).parent
sys.path.insert(0, str(poc_dir))

from framework import ToolFramework, ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataSchema, DataType
from semantic_types import Domain, MEDICAL_RECORDS, MEDICAL_ENTITIES, MEDICAL_KNOWLEDGE_GRAPH
from data_references import ProcessingStrategy

# Simple mock tools for testing since imports are problematic
class SimpleTextLoader(ExtensibleTool):
    """Simple text loader for POC"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="TextLoader",
            name="Text File Loader",
            description="Load text files",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            semantic_output=MEDICAL_RECORDS,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        """Load text from file"""
        try:
            with open(input_data.path, 'r') as f:
                content = f.read()
            
            result = DataSchema.TextData(
                content=content,
                source=input_data.path,
                char_count=len(content),
                line_count=content.count('\n') + 1,
                checksum=f"md5_{hash(content)}"
            )
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GeminiEntityExtractor(ExtensibleTool):
    """Entity extractor using real Gemini API"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="EntityExtractor",
            name="Gemini Entity Extractor",
            description="Extract entities using Gemini",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            semantic_input=MEDICAL_RECORDS,
            semantic_output=MEDICAL_ENTITIES,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        """Extract entities using Gemini API"""
        import litellm
        from dotenv import load_dotenv
        from datetime import datetime
        
        # Load API key
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        try:
            # Use REAL Gemini API
            prompt = f"""Extract medical entities from this text. Return in this exact format:
            
            DISEASES: disease1, disease2
            MEDICATIONS: med1, med2
            SYMPTOMS: symptom1, symptom2
            PROCEDURES: proc1, proc2
            
            Text: {input_data.content[:2000]}"""
            
            response = litellm.completion(
                model="gemini/gemini-2.0-flash-exp",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            print(f"   Gemini response received ({len(content)} chars)")
            
            # Parse response
            entities = []
            entity_id = 0
            
            for line in content.split('\n'):
                if ':' in line:
                    entity_type, items = line.split(':', 1)
                    entity_type = entity_type.strip().upper()
                    
                    # Map to standard types
                    type_map = {
                        'DISEASES': 'DISEASE',
                        'MEDICATIONS': 'MEDICATION',
                        'SYMPTOMS': 'SYMPTOM',
                        'PROCEDURES': 'PROCEDURE'
                    }
                    
                    if entity_type in type_map:
                        for item in items.split(','):
                            item = item.strip()
                            if item and item.lower() != 'none':
                                entities.append(DataSchema.Entity(
                                    id=f"e{entity_id}",
                                    text=item,
                                    type=type_map[entity_type],
                                    confidence=0.85
                                ))
                                entity_id += 1
            
            print(f"   Extracted {len(entities)} entities")
            
            result = DataSchema.EntitiesData(
                entities=entities,
                source_checksum=f"md5_{hash(input_data.content)}",
                extraction_model="gemini/gemini-2.0-flash-exp",
                extraction_timestamp=datetime.now().isoformat()
            )
            
            return ToolResult(success=True, data=result)
            
        except Exception as e:
            return ToolResult(success=False, error=f"Gemini API error: {str(e)}")


class MockGraphBuilder(ExtensibleTool):
    """Graph builder using mock Neo4j"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphBuilder",
            name="Mock Graph Builder",
            description="Build graph in mock Neo4j",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH,
            semantic_input=MEDICAL_ENTITIES,
            semantic_output=MEDICAL_KNOWLEDGE_GRAPH,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        """Build graph in mock Neo4j"""
        try:
            # Import mock Neo4j
            import mock_neo4j
            neo4j = mock_neo4j.patch_neo4j()
            
            driver = neo4j.GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "devpassword")
            )
            
            node_count = 0
            edge_count = 0
            
            with driver.session() as session:
                # Create nodes
                for entity in input_data.entities:
                    session.run(f"""
                        CREATE (n:Entity:{entity.type} {{
                            id: '{entity.id}',
                            text: '{entity.text}',
                            confidence: {entity.confidence},
                            created_by: 'framework_poc'
                        }})
                    """)
                    node_count += 1
                
                # Create relationships between medications and diseases
                medications = [e for e in input_data.entities if e.type == 'MEDICATION']
                diseases = [e for e in input_data.entities if e.type == 'DISEASE']
                
                for med in medications:
                    for disease in diseases:
                        session.run(f"""
                            MATCH (m:MEDICATION {{id: '{med.id}'}}),
                                  (d:DISEASE {{id: '{disease.id}'}})
                            CREATE (m)-[:TREATS]->(d)
                        """)
                        edge_count += 1
            
            driver.close()
            
            print(f"   Created {node_count} nodes, {edge_count} edges in mock Neo4j")
            
            from datetime import datetime
            import uuid
            
            result = DataSchema.GraphData(
                graph_id=str(uuid.uuid4()),
                source_checksum=f"md5_{hash(str(input_data.entities))}",
                created_timestamp=datetime.now().isoformat(),
                node_count=node_count,
                edge_count=edge_count,
                node_types=list(set(e.type for e in input_data.entities)),
                edge_types=['TREATS'] if edge_count > 0 else []
            )
            
            return ToolResult(success=True, data=result)
            
        except Exception as e:
            return ToolResult(success=False, error=f"Graph builder error: {str(e)}")


def verify_neo4j_results():
    """Check if data actually in Neo4j"""
    try:
        import mock_neo4j
        neo4j = mock_neo4j.patch_neo4j()
        
        driver = neo4j.GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        
        with driver.session() as session:
            result = session.run("""
                MATCH (n) 
                WHERE n.created_by = 'framework_poc'
                RETURN count(n) as node_count
            """)
            count = result.single()["node_count"]
        
        driver.close()
        return count
    except:
        return 0


def main():
    print("="*60)
    print("PROOF OF CONCEPT: Real Tools, Real Services")
    print("="*60)
    
    # 1. Create framework and register tools
    framework = ToolFramework()
    
    print("\n📦 Registering Tools:")
    print("-" * 40)
    framework.register_tool(SimpleTextLoader())
    framework.register_tool(GeminiEntityExtractor())
    framework.register_tool(MockGraphBuilder())
    
    # 2. Load real medical text
    test_file = Path("test_data/medical_article.txt")
    if not test_file.exists():
        print("❌ No test data found. Run Step 1 first.")
        return False
    
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=test_file.stat().st_size,
        mime_type="text/plain"
    )
    
    print(f"\n📄 Test file: {test_file.name}")
    print(f"   Size: {file_data.size_bytes / 1024:.1f}KB")
    
    # 3. Find medical processing chain
    print("\n🔍 Finding chain for medical text processing:")
    chains = framework.find_chains(
        DataType.FILE,
        DataType.GRAPH,
        domain=Domain.MEDICAL
    )
    
    if not chains:
        print("❌ No chains found!")
        
        # Debug: Show what tools are registered
        print("\nRegistered tools:")
        for tid, caps in framework.capabilities.items():
            print(f"  - {tid}: {caps.input_type} → {caps.output_type}")
            if caps.semantic_output:
                print(f"    Semantic: {caps.semantic_output.semantic_tag}")
        return False
    
    chain = chains[0]
    print(f"   Chain found: {' → '.join(chain)}")
    
    # 4. Execute chain with monitoring
    print("\n⚡ Executing chain:")
    print("-" * 40)
    
    # Monitor memory
    process = psutil.Process()
    mem_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    start_time = time.time()
    result = framework.execute_chain(chain, file_data)
    duration = time.time() - start_time
    
    mem_after = process.memory_info().rss / (1024 * 1024)  # MB
    mem_used = mem_after - mem_before
    
    print(f"\n📊 Execution Metrics:")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Memory used: {mem_used:.1f}MB")
    
    # 5. Verify results
    print("\n🔍 Verification:")
    print("-" * 40)
    
    if not result.success:
        print(f"❌ Chain failed: {result.error}")
        return False
    
    print("✅ Chain executed successfully")
    
    # Check if we have graph data
    if hasattr(result.data, 'node_count'):
        print(f"✅ Graph created: {result.data.node_count} nodes, {result.data.edge_count} edges")
        if hasattr(result.data, 'node_types'):
            print(f"   Node types: {', '.join(result.data.node_types)}")
        if hasattr(result.data, 'edge_types'):
            print(f"   Edge types: {', '.join(result.data.edge_types)}")
    
    # Check mock Neo4j
    neo4j_count = verify_neo4j_results()
    if neo4j_count > 0:
        print(f"✅ Neo4j verified: {neo4j_count} nodes with created_by='framework_poc'")
    
    # 6. Test semantic blocking
    print("\n🚫 Testing Semantic Type Enforcement:")
    print("-" * 40)
    
    # Try to find social network chain with medical data
    social_chains = framework.find_chains(
        DataType.FILE,
        DataType.GRAPH,
        domain=Domain.SOCIAL
    )
    
    if not social_chains or len(social_chains) == 0:
        print("✅ Correctly blocked: No social chains for medical tools")
        semantic_blocked = True
    else:
        print("❌ ERROR: Found social chains with medical tools!")
        semantic_blocked = False
    
    # 7. Summary
    print("\n" + "="*60)
    print("PROOF OF CONCEPT RESULTS:")
    print("="*60)
    
    success_criteria = [
        ("Real file processed", file_data.size_bytes > 0),
        ("Chain discovered", len(chains) > 0),
        ("Chain executed", result.success),
        ("Graph created", hasattr(result.data, 'node_count') and result.data.node_count > 0),
        ("Neo4j populated", neo4j_count > 0),
        ("Semantic types enforced", semantic_blocked),
        ("Memory efficient", mem_used < 100)  # Should be <100MB for small file
    ]
    
    for criterion, passed in success_criteria:
        status = "✅" if passed else "❌"
        print(f"{status} {criterion}")
    
    all_passed = all(passed for _, passed in success_criteria)
    
    if all_passed:
        print("\n🎉 PROOF OF CONCEPT SUCCESSFUL!")
        print("The framework works with real tools and services.")
        print("- Gemini API extracted real medical entities")
        print("- Mock Neo4j stored the graph data")
        print("- Semantic types prevented invalid chains")
    else:
        print("\n⚠️ PROOF OF CONCEPT INCOMPLETE")
        print("Some criteria not met. Debug required.")
    
    return all_passed


if __name__ == "__main__":
    # Clear mock Neo4j before starting
    import os
    if os.path.exists("/tmp/mock_neo4j_db.json"):
        os.remove("/tmp/mock_neo4j_db.json")
    
    success = main()
    sys.exit(0 if success else 1)