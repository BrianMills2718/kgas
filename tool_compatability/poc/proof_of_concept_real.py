#!/usr/bin/env python3
"""
PROOF OF CONCEPT: Real Tools, Real Services, NO MOCKS
FAIL-FAST: If any service is unavailable, crash immediately
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
    """Entity extractor using REAL Gemini API - NO MOCKS"""
    
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
        """Extract entities using Gemini API - FAIL FAST if unavailable"""
        import litellm
        from dotenv import load_dotenv
        from datetime import datetime
        
        # Load API key
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError("GEMINI_API_KEY not set - FAILING FAST")
        
        try:
            # Use REAL Gemini API - NO FALLBACK
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
            # FAIL FAST - no recovery
            raise RuntimeError(f"Gemini API FAILED: {str(e)}")


class RealGraphBuilder(ExtensibleTool):
    """Graph builder using REAL Neo4j - NO MOCKS"""
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphBuilder",
            name="Real Neo4j Graph Builder",
            description="Build graph in REAL Neo4j",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH,
            semantic_input=MEDICAL_ENTITIES,
            semantic_output=MEDICAL_KNOWLEDGE_GRAPH,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        """Build graph in REAL Neo4j - FAIL FAST if unavailable"""
        try:
            from neo4j import GraphDatabase
            
            # Connect to REAL Neo4j - NO FALLBACK
            driver = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "devpassword")
            )
            
            # Test connection - FAIL FAST if not available
            driver.verify_connectivity()
            
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
            
            print(f"   Created {node_count} nodes, {edge_count} edges in REAL Neo4j")
            
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
            
        except ImportError:
            raise RuntimeError("Neo4j driver not installed - FAILING FAST")
        except Exception as e:
            raise RuntimeError(f"Neo4j connection FAILED: {str(e)} - FAILING FAST")


def verify_neo4j_results():
    """Check if data actually in REAL Neo4j"""
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        
        driver.verify_connectivity()  # FAIL FAST if not available
        
        with driver.session() as session:
            result = session.run("""
                MATCH (n) 
                WHERE n.created_by = 'framework_poc'
                RETURN count(n) as node_count
            """)
            count = result.single()["node_count"]
        
        driver.close()
        return count
    except Exception as e:
        raise RuntimeError(f"Neo4j verification FAILED: {str(e)}")


def main():
    print("="*60)
    print("PROOF OF CONCEPT: Real Tools, Real Services, NO MOCKS")
    print("FAIL-FAST: Any missing service will crash")
    print("="*60)
    
    # 1. Create framework and register tools
    framework = ToolFramework()
    
    print("\n📦 Registering Tools:")
    print("-" * 40)
    framework.register_tool(SimpleTextLoader())
    framework.register_tool(GeminiEntityExtractor())
    framework.register_tool(RealGraphBuilder())
    
    # 2. Load real medical text
    test_file = Path("test_data/medical_article.txt")
    if not test_file.exists():
        raise RuntimeError("Test data not found - FAILING FAST")
    
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
        raise RuntimeError("No chains found - FAILING FAST")
    
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
        raise RuntimeError(f"Chain FAILED: {result.error}")
    
    print("✅ Chain executed successfully")
    
    # Check if we have graph data
    if hasattr(result.data, 'node_count'):
        print(f"✅ Graph created: {result.data.node_count} nodes, {result.data.edge_count} edges")
    
    # Check REAL Neo4j
    neo4j_count = verify_neo4j_results()
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
    
    if social_chains:
        raise RuntimeError("ERROR: Found social chains with medical tools!")
    
    print("✅ Correctly blocked: No social chains for medical tools")
    
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
        ("Semantic types enforced", not social_chains),
        ("Memory efficient", mem_used < 200)  # Library overhead is ~170MB
    ]
    
    for criterion, passed in success_criteria:
        if not passed:
            raise RuntimeError(f"FAILED: {criterion}")
        print(f"✅ {criterion}")
    
    print("\n🎉 PROOF OF CONCEPT SUCCESSFUL!")
    print("All real services working, no mocks used.")
    return True


if __name__ == "__main__":
    # NO CLEANUP - we want to see the data in Neo4j
    
    try:
        success = main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        print("POC FAILED - Fix the issue and try again")
        sys.exit(1)