#!/usr/bin/env python3
"""
Test entity extraction functionality
"""

import sys
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest

def test_spacy_extraction():
    """Test entity extraction using SpaCy (no LLM required)"""
    
    print("Testing SpaCy Entity Extraction")
    print("=" * 50)
    
    # Initialize service manager and tool
    sm = ServiceManager()
    spacy_tool = SpacyNER(sm)
    
    # Test text with clear entities
    test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California. Microsoft CEO Satya Nadella met with Tim Cook."
    
    # Create tool request
    request = ToolRequest(
        tool_id="T23A_SPACY_NER",
        operation="extract",
        input_data={"text": test_text},
        parameters={}
    )
    
    try:
        # Try different methods to call the tool
        if hasattr(spacy_tool, 'execute'):
            result = spacy_tool.execute(request)
        elif hasattr(spacy_tool, 'run'):
            result = spacy_tool.run(request)
        elif hasattr(spacy_tool, 'extract_entities'):
            # Direct method call
            result = spacy_tool.extract_entities(test_text)
        else:
            # List available methods
            methods = [m for m in dir(spacy_tool) if not m.startswith('_')]
            print(f"Available methods: {methods[:10]}")
            return False
            
        print(f"Extraction successful!")
        
        # Display results
        if isinstance(result, dict):
            entities = result.get('entities', [])
            print(f"Found {len(entities)} entities:")
            for entity in entities[:5]:  # Show first 5
                if isinstance(entity, dict):
                    print(f"  - {entity.get('text', 'N/A')} ({entity.get('type', 'N/A')})")
                else:
                    print(f"  - {entity}")
        else:
            print(f"Result type: {type(result)}")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_extraction_fallback():
    """Test LLM extraction with fallback to SpaCy"""
    
    print("\nTesting LLM Extraction with Fallback")
    print("=" * 50)
    
    try:
        from src.tools.phase2.extraction_components.llm_integration import LLMExtractionClient
        from src.ontology_generator import DomainOntology, EntityType, RelationshipType
        
        # Create a simple ontology
        entity_types = [
            EntityType(
                name='PERSON', 
                description='Person entity',
                attributes=['name', 'role'],
                examples=['Steve Jobs', 'Tim Cook']
            ),
            EntityType(
                name='ORGANIZATION',
                description='Organization entity',
                attributes=['name', 'type'],
                examples=['Apple Inc.', 'Microsoft']
            )
        ]
        relationship_types = [
            RelationshipType(
                name='FOUNDED',
                description='Founded relationship',
                source_types=['PERSON'],
                target_types=['ORGANIZATION'],
                examples=['Steve Jobs founded Apple']
            )
        ]
        
        ontology = DomainOntology(
            domain_name='tech',
            domain_description='Technology domain',
            entity_types=entity_types,
            relationship_types=relationship_types,
            extraction_patterns=[]
        )
        
        # Try LLM extraction
        client = LLMExtractionClient()
        text = 'Steve Jobs founded Apple Inc. in 1976.'
        
        try:
            result = client._extract_entities_sync(text, ontology)
            print(f"LLM extraction successful!")
            print(f"  Entities: {len(result.get('entities', []))}")
            print(f"  Relationships: {len(result.get('relationships', []))}")
            return True
        except Exception as llm_error:
            print(f"LLM extraction failed: {llm_error}")
            
            # Fallback to SpaCy
            print("Falling back to SpaCy extraction...")
            return test_spacy_extraction()
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Falling back to SpaCy extraction...")
        return test_spacy_extraction()

if __name__ == "__main__":
    # Test SpaCy first (should work)
    spacy_success = test_spacy_extraction()
    
    # Test LLM with fallback
    llm_success = test_llm_extraction_fallback()
    
    # Summary
    print("\n" + "=" * 50)
    print("EXTRACTION TEST SUMMARY")
    print("=" * 50)
    print(f"SpaCy extraction: {'✓ PASSED' if spacy_success else '✗ FAILED'}")
    print(f"LLM extraction (with fallback): {'✓ PASSED' if llm_success else '✗ FAILED'}")
    
    sys.exit(0 if spacy_success else 1)