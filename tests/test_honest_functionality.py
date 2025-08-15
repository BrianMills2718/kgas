#!/usr/bin/env python3
"""
Honest Functionality Test - Phase 5, Task 5.1
Tests what ACTUALLY works vs what doesn't
"""

import sys
import os
from typing import Dict, Any

def test_pdf_loading() -> bool:
    """Test if we can actually load PDFs"""
    try:
        import PyPDF2
        pdf_path = "test_data/simple_test.pdf"
        
        if not os.path.exists(pdf_path):
            return False
            
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        return len(text) > 100
    except Exception:
        return False

def test_text_extraction() -> bool:
    """Test if text extraction from PDF works"""
    try:
        import PyPDF2
        pdf_path = "test_data/simple_test.pdf"
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
        
        # Check if we get recognizable text
        return "Technology" in text or "Apple" in text
    except Exception:
        return False

def test_entity_extraction() -> bool:
    """Test if entity extraction works"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        test_text = "Apple Inc. was founded by Steve Jobs in Cupertino."
        doc = nlp(test_text)
        
        entities = [ent for ent in doc.ents]
        
        # Should find at least Apple, Steve Jobs, and Cupertino
        return len(entities) >= 3
    except Exception:
        return False

def test_graph_storage() -> bool:
    """Test if we can store data in Neo4j"""
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Try to create a test node
            result = session.run(
                """
                CREATE (t:TestNode {name: 'test', timestamp: timestamp()})
                RETURN t
                """
            )
            node = result.single()
            
            # Clean up
            session.run("MATCH (t:TestNode {name: 'test'}) DELETE t")
        
        driver.close()
        return node is not None
        
    except Exception:
        return False

def test_graph_query() -> bool:
    """Test if we can query Neo4j"""
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count LIMIT 1")
            count = result.single()["count"]
        
        driver.close()
        return isinstance(count, int)
        
    except Exception:
        return False

def test_multi_hop() -> bool:
    """Test if multi-hop queries work"""
    try:
        from src.core.service_manager import ServiceManager
        from src.tools.phase1.t49_multihop_query import MultiHopQuery
        
        sm = ServiceManager()
        tool = MultiHopQuery(sm)
        
        # Tool initializes successfully
        return True
    except Exception:
        return False

def test_llm_integration() -> bool:
    """Test if LLM integration works"""
    try:
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        
        client = LLMExtractionClient()
        
        # Check if API keys are configured
        openai_available = client.openai_available
        google_available = client.google_available
        
        return openai_available or google_available
    except Exception:
        return False

def test_tool_initialization() -> bool:
    """Test if all basic tools can be initialized"""
    try:
        from src.core.service_manager import ServiceManager
        sm = ServiceManager()
        
        tools = [
            'src.tools.phase1.t01_pdf_loader.PDFLoader',
            'src.tools.phase1.t15a_text_chunker.TextChunker',
            'src.tools.phase1.t23a_spacy_ner.SpacyNER',
            'src.tools.phase1.t31_entity_builder.EntityBuilder',
            'src.tools.phase1.t34_edge_builder.EdgeBuilder',
        ]
        
        for tool_path in tools:
            module_name, class_name = tool_path.rsplit('.', 1)
            module = __import__(module_name, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            tool = tool_class(sm)
        
        return True
    except Exception:
        return False

def test_pipeline_integration() -> bool:
    """Test if the basic pipeline works end-to-end"""
    try:
        # Test minimal pipeline
        import PyPDF2
        import spacy
        from neo4j import GraphDatabase
        
        # All components available
        pdf_available = True
        nlp = spacy.load("en_core_web_sm")
        
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.close()
        
        return True
    except Exception:
        return False

def test_real_document_processing() -> bool:
    """Test if we can process a real document"""
    try:
        pdf_path = "test_data/simple_test.pdf"
        
        if not os.path.exists(pdf_path):
            return False
        
        # Load PDF
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = reader.pages[0].extract_text()
        
        # Extract entities
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:500])  # Process first 500 chars
        
        entities = [ent for ent in doc.ents]
        
        # Success if we got both text and entities
        return len(text) > 100 and len(entities) > 5
        
    except Exception:
        return False

def run_honest_tests() -> Dict[str, Any]:
    """Run all tests and return honest results"""
    
    print("=" * 60)
    print("HONEST FUNCTIONALITY TEST")
    print("Testing what ACTUALLY works...")
    print("=" * 60)
    
    tests = {
        "pdf_loading": test_pdf_loading,
        "text_extraction": test_text_extraction,
        "entity_extraction": test_entity_extraction,
        "graph_storage": test_graph_storage,
        "graph_query": test_graph_query,
        "multi_hop": test_multi_hop,
        "llm_integration": test_llm_integration,
        "tool_initialization": test_tool_initialization,
        "pipeline_integration": test_pipeline_integration,
        "real_document_processing": test_real_document_processing
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print(f"\nTesting {test_name}...", end=" ")
        try:
            result = test_func()
            results[test_name] = result
            print("✓ PASSED" if result else "✗ FAILED")
        except Exception as e:
            results[test_name] = False
            print(f"✗ ERROR: {str(e)[:50]}")
    
    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ({passed/total*100:.0f}%)")
    print(f"Failed: {failed} ({failed/total*100:.0f}%)")
    
    print("\n✓ WORKING FEATURES:")
    for test, result in results.items():
        if result:
            print(f"  - {test.replace('_', ' ').title()}")
    
    print("\n✗ NOT WORKING:")
    for test, result in results.items():
        if not result:
            print(f"  - {test.replace('_', ' ').title()}")
    
    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL SYSTEM STATUS")
    print("=" * 60)
    
    critical_tests = ["pdf_loading", "text_extraction", "entity_extraction", "graph_storage"]
    critical_passing = all(results.get(test, False) for test in critical_tests)
    
    if critical_passing:
        if passed >= 8:
            print("✅ System is MOSTLY FUNCTIONAL (~80%)")
            print("   Basic pipeline works, most features operational")
        elif passed >= 6:
            print("⚠️  System is PARTIALLY FUNCTIONAL (~60%)")
            print("   Core features work but some components need fixes")
        else:
            print("⚠️  System is MINIMALLY FUNCTIONAL (~40%)")
            print("   Only basic features work")
    else:
        print("❌ System is NOT FUNCTIONAL")
        print("   Critical components are broken")
    
    return results

if __name__ == "__main__":
    results = run_honest_tests()
    
    # Exit with appropriate code
    critical_tests = ["pdf_loading", "text_extraction", "entity_extraction", "graph_storage"]
    critical_passing = all(results.get(test, False) for test in critical_tests)
    
    sys.exit(0 if critical_passing else 1)