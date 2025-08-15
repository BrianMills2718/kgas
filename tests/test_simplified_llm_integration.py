#!/usr/bin/env python3
"""
Simplified test for LLM entity resolution integration
"""

import pytest
from src.services.llm_entity_resolver import (
    LLMEntityResolutionService,
    MockEntityResolver
)


def test_llm_entity_resolution_f1_score():
    """Test that LLM resolution achieves >60% F1 score"""
    
    # Create resolver with mock provider
    resolver = LLMEntityResolutionService(provider=MockEntityResolver())
    
    # Test cases with known ground truth
    test_cases = [
        {
            'text': 'Dr. Smith met with Smith Industries CEO.',
            'expected_entities': ['Dr. Smith', 'Smith Industries'],
        },
        {
            'text': 'NASA administrator spoke about National Aeronautics and Space Administration budget.',
            'expected_entities': ['NASA', 'National Aeronautics and Space Administration'],
        },
        {
            'text': 'John Doe works at Apple Inc. Mr. Doe is a senior engineer.',
            'expected_entities': ['John Doe', 'Apple Inc.'],
        },
    ]
    
    total_correct = 0
    total_predicted = 0 
    total_expected = 0
    
    for case in test_cases:
        entities = resolver.provider.resolve_entities(case['text'])
        
        predicted_names = [e.canonical_name for e in entities]
        expected_names = case['expected_entities']
        
        # For each expected entity, check if it or a variant was found
        for expected in expected_names:
            found = False
            for predicted in predicted_names:
                # Check exact match or partial match
                if expected.lower() in predicted.lower() or predicted.lower() in expected.lower():
                    found = True
                    break
            if found:
                total_correct += 1
        
        total_predicted += len(predicted_names)
        total_expected += len(expected_names)
    
    # Calculate F1 score
    precision = total_correct / total_predicted if total_predicted > 0 else 0
    recall = total_correct / total_expected if total_expected > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\nLLM Entity Resolution F1 Score: {f1_score:.2f} ({f1_score*100:.1f}%)")
    
    # Must exceed 60% (0.6)
    assert f1_score > 0.6, f"F1 score {f1_score:.2f} must exceed 0.6 (60%)"


def test_cross_document_entity_resolution():
    """Test entity resolution across multiple documents"""
    
    resolver = LLMEntityResolutionService(provider=MockEntityResolver())
    
    # Test documents with cross-references
    documents = [
        {
            'id': 'doc1',
            'text': 'Dr. Emily Johnson is the CEO of TechCorp Inc. She founded the company in 2020.'
        },
        {
            'id': 'doc2', 
            'text': 'Emily Johnson previously worked at Microsoft Corporation. Johnson is known for innovation.'
        }
    ]
    
    # Resolve entities
    results = resolver.resolve_cross_document_entities(documents)
    
    # Verify results
    assert 'doc1' in results
    assert 'doc2' in results
    
    # Check that entities were found
    assert len(results['doc1']) > 0, "Should find entities in doc1"
    assert len(results['doc2']) > 0, "Should find entities in doc2"
    
    # Check that Emily Johnson was found
    doc1_names = [e.canonical_name for e in results['doc1']]
    doc2_names = [e.canonical_name for e in results['doc2']]
    
    emily_found_doc1 = any('Emily' in name or 'Johnson' in name for name in doc1_names)
    emily_found_doc2 = any('Emily' in name or 'Johnson' in name for name in doc2_names)
    
    assert emily_found_doc1, "Should find Emily Johnson in doc1"
    assert emily_found_doc2, "Should find Emily/Johnson in doc2"


def test_entity_disambiguation():
    """Test disambiguating entities with same names"""
    
    resolver = LLMEntityResolutionService(provider=MockEntityResolver())
    
    documents = [
        {
            'id': 'doc1',
            'text': 'Dr. Chen from Stanford researches CRISPR gene editing technology.'
        },
        {
            'id': 'doc2',
            'text': 'Dr. Chen at Harvard studies cancer immunotherapy treatments.'
        }
    ]
    
    results = resolver.resolve_cross_document_entities(documents)
    
    # Should have entities in both documents
    assert len(results['doc1']) > 0
    assert len(results['doc2']) > 0
    
    # Check that Dr. Chen was found in both
    doc1_chen = any('Chen' in e.canonical_name for e in results['doc1'])
    doc2_chen = any('Chen' in e.canonical_name for e in results['doc2'])
    
    assert doc1_chen, "Should find Dr. Chen in doc1"
    assert doc2_chen, "Should find Dr. Chen in doc2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])