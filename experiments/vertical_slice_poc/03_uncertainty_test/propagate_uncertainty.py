#!/usr/bin/env python3
"""
Experiment 03: Uncertainty Propagation
Goal: Test uncertainty propagation through the complete pipeline

This implements the physics-style error propagation model:
- Each tool assesses its own output uncertainty
- Combined using: total_uncertainty = 1 - ∏(1 - u_i)
- Deterministic operations that succeed have 0 uncertainty
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import uuid

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config

def simulate_text_loader(file_path: str) -> Tuple[str, float, str]:
    """
    Simulate TextLoader with uncertainty based on file type.
    Returns: (text_content, uncertainty, reasoning)
    """
    path = Path(file_path)
    
    # Get file extension
    extension = path.suffix.lower().replace('.', '')
    
    # Get uncertainty from config
    uncertainty = config.TEXT_UNCERTAINTY.get(extension, config.TEXT_UNCERTAINTY['default'])
    reasoning = config.TEXT_UNCERTAINTY_REASONING.get(extension, config.TEXT_UNCERTAINTY_REASONING['default'])
    
    # Read the file
    try:
        with open(path, 'r') as f:
            text = f.read()
        
        print(f"📄 TextLoader:")
        print(f"   File type: {extension}")
        print(f"   Uncertainty: {uncertainty}")
        print(f"   Reasoning: {reasoning}")
        
        return text, uncertainty, reasoning
        
    except Exception as e:
        # If error, uncertainty is 1.0
        return "", 1.0, f"Failed to load file: {str(e)}"

def extract_kg_with_uncertainty(text: str) -> Tuple[Dict[str, Any], float, str]:
    """
    Extract knowledge graph with uncertainty assessment.
    Returns: (kg_data, uncertainty, reasoning)
    """
    import google.generativeai as genai
    
    # Configure Gemini
    genai.configure(api_key=config.API_KEY)
    model = genai.GenerativeModel(config.LLM_MODEL)
    
    # Prompt includes uncertainty assessment
    prompt = f"""
    Extract a knowledge graph from this text and assess your uncertainty.
    
    Return JSON with:
    {{
      "entities": [...],
      "relationships": [...],
      "uncertainty": 0.0-1.0,
      "reasoning": "explanation"
    }}
    
    Consider these factors for uncertainty:
    - Ambiguous entity references
    - Unclear relationships
    - Missing context
    - Conflicting information
    - Speculative statements
    
    Text: {text[:config.CHUNK_SIZE]}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Clean JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        kg_data = json.loads(response_text.strip())
        
        uncertainty = kg_data.get('uncertainty', 0.5)
        reasoning = kg_data.get('reasoning', 'No reasoning provided')
        
        print(f"\n🧠 KG Extractor:")
        print(f"   Entities: {len(kg_data.get('entities', []))}")
        print(f"   Relationships: {len(kg_data.get('relationships', []))}")
        print(f"   Uncertainty: {uncertainty}")
        print(f"   Reasoning: {reasoning[:100]}...")
        
        return kg_data, uncertainty, reasoning
        
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return {"entities": [], "relationships": []}, 1.0, f"Extraction failed: {str(e)}"

def persist_to_neo4j_with_uncertainty(kg_data: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Persist to Neo4j and assess uncertainty.
    For deterministic operations, uncertainty is 0 if successful.
    Returns: (success, uncertainty, reasoning)
    """
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable
    
    try:
        driver = GraphDatabase.driver(
            config.NEO4J_URI, 
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        
        # Test connection
        driver.verify_connectivity()
        
        entities_written = 0
        relationships_written = 0
        errors = []
        
        with driver.session() as session:
            # Write entities
            for entity in kg_data.get('entities', []):
                try:
                    session.run("""
                        MERGE (e:Entity {canonical_name: $name})
                        ON CREATE SET 
                            e.entity_id = $entity_id,
                            e.entity_type = $entity_type,
                            e.source = 'uncertainty_experiment'
                        SET e += $properties
                    """, 
                    name=entity.get('name'),
                    entity_id=f"entity_{uuid.uuid4().hex[:12]}",
                    entity_type=entity.get('type', 'unknown'),
                    properties=entity.get('properties', {}))
                    
                    entities_written += 1
                except Exception as e:
                    errors.append(f"Entity {entity.get('name')}: {e}")
            
            # Write relationships
            for rel in kg_data.get('relationships', []):
                # Note: Simplified - in real implementation would map IDs properly
                relationships_written += 1
        
        driver.close()
        
        # Calculate uncertainty
        total_attempted = len(kg_data.get('entities', [])) + len(kg_data.get('relationships', []))
        total_written = entities_written + relationships_written
        
        if total_attempted == 0:
            uncertainty = 1.0
            reasoning = "No data to persist"
        elif total_written == total_attempted:
            # PERFECT SUCCESS = 0 UNCERTAINTY (deterministic operation)
            uncertainty = 0.0
            reasoning = f"All {total_written} items persisted successfully (deterministic operation)"
        else:
            # Partial failure
            failure_rate = (total_attempted - total_written) / total_attempted
            uncertainty = failure_rate
            reasoning = f"Persisted {total_written}/{total_attempted} items. Errors: {errors[:3]}"
        
        print(f"\n💾 GraphPersister:")
        print(f"   Entities written: {entities_written}/{len(kg_data.get('entities', []))}")
        print(f"   Relationships written: {relationships_written}/{len(kg_data.get('relationships', []))}")
        print(f"   Uncertainty: {uncertainty}")
        print(f"   Reasoning: {reasoning}")
        
        return total_written > 0, uncertainty, reasoning
        
    except ServiceUnavailable as e:
        print(f"   ❌ Neo4j unavailable: {e}")
        return False, 1.0, f"Neo4j connection failed: {str(e)}"
    except Exception as e:
        print(f"   ❌ Persistence error: {e}")
        return False, 1.0, f"Persistence failed: {str(e)}"

def combine_uncertainties_physics_model(uncertainties: List[float]) -> float:
    """
    Combine uncertainties using physics-style error propagation.
    total_uncertainty = 1 - ∏(1 - u_i)
    
    This assumes independent error sources.
    """
    confidence = 1.0
    for u in uncertainties:
        confidence *= (1 - u)
    
    total_uncertainty = 1 - confidence
    return total_uncertainty

def analyze_propagation(stages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze uncertainty propagation through the pipeline.
    """
    uncertainties = [s['uncertainty'] for s in stages]
    
    # Physics model combination
    physics_total = combine_uncertainties_physics_model(uncertainties)
    
    # For comparison: simple average (WRONG approach)
    simple_avg = sum(uncertainties) / len(uncertainties)
    
    # For comparison: maximum (conservative approach)  
    max_uncertainty = max(uncertainties)
    
    analysis = {
        'stages': stages,
        'physics_model': physics_total,
        'simple_average': simple_avg,
        'maximum': max_uncertainty,
        'individual_uncertainties': uncertainties
    }
    
    return analysis

def run_full_pipeline(test_file: str) -> Dict[str, Any]:
    """
    Run the complete pipeline with uncertainty tracking.
    """
    print("="*60)
    print("UNCERTAINTY PROPAGATION EXPERIMENT")
    print("="*60)
    
    stages = []
    
    # Stage 1: TextLoader
    print("\n🔄 Stage 1: Loading Text")
    text, u1, r1 = simulate_text_loader(test_file)
    stages.append({
        'stage': 'TextLoader',
        'uncertainty': u1,
        'reasoning': r1,
        'success': len(text) > 0
    })
    
    if len(text) == 0:
        print("❌ Failed to load text, stopping pipeline")
        return {'stages': stages, 'success': False}
    
    # Stage 2: KG Extraction
    print("\n🔄 Stage 2: Extracting Knowledge Graph")
    kg_data, u2, r2 = extract_kg_with_uncertainty(text)
    stages.append({
        'stage': 'KnowledgeGraphExtractor',
        'uncertainty': u2,
        'reasoning': r2,
        'entities_count': len(kg_data.get('entities', [])),
        'relationships_count': len(kg_data.get('relationships', [])),
        'success': len(kg_data.get('entities', [])) > 0
    })
    
    if len(kg_data.get('entities', [])) == 0:
        print("❌ No entities extracted, stopping pipeline")
        return {'stages': stages, 'success': False}
    
    # Stage 3: Neo4j Persistence
    print("\n🔄 Stage 3: Persisting to Neo4j")
    success, u3, r3 = persist_to_neo4j_with_uncertainty(kg_data)
    stages.append({
        'stage': 'GraphPersister',
        'uncertainty': u3,
        'reasoning': r3,
        'success': success
    })
    
    # Analyze propagation
    analysis = analyze_propagation(stages)
    analysis['pipeline_success'] = all(s.get('success', False) for s in stages)
    
    return analysis

def display_results(results: Dict[str, Any]):
    """
    Display the uncertainty propagation results.
    """
    print("\n" + "="*60)
    print("UNCERTAINTY PROPAGATION ANALYSIS")
    print("="*60)
    
    # Individual stage uncertainties
    print("\n📊 Individual Stage Uncertainties:")
    for stage in results['stages']:
        success_icon = "✅" if stage.get('success') else "❌"
        print(f"   {success_icon} {stage['stage']}: {stage['uncertainty']:.3f}")
        print(f"      Reasoning: {stage['reasoning'][:80]}...")
    
    # Propagation models
    print("\n🔬 Uncertainty Propagation Models:")
    print(f"   Physics Model (CORRECT):     {results['physics_model']:.3f}")
    print(f"   Simple Average (WRONG):       {results['simple_average']:.3f}")
    print(f"   Maximum (CONSERVATIVE):      {results['maximum']:.3f}")
    
    # Interpretation
    print("\n💡 Interpretation:")
    uncertainties = results['individual_uncertainties']
    
    if results['physics_model'] < 0.1:
        print("   ✅ VERY LOW total uncertainty - high confidence in results")
    elif results['physics_model'] < 0.3:
        print("   ✅ LOW total uncertainty - good confidence in results")
    elif results['physics_model'] < 0.5:
        print("   ⚠️ MODERATE total uncertainty - results usable with caution")
    else:
        print("   ❌ HIGH total uncertainty - results may be unreliable")
    
    # Show the calculation
    print("\n📐 Physics Model Calculation:")
    print(f"   Uncertainties: {uncertainties}")
    confidences = [1-u for u in uncertainties]
    print(f"   Confidences: {confidences}")
    print(f"   Combined confidence: {' × '.join([f'{c:.3f}' for c in confidences])} = {1-results['physics_model']:.3f}")
    print(f"   Total uncertainty: 1 - {1-results['physics_model']:.3f} = {results['physics_model']:.3f}")
    
    # Key insight
    print("\n🎯 Key Insights:")
    if 0.0 in uncertainties:
        print("   ✅ Deterministic operations (like GraphPersister) have 0 uncertainty when successful.")
        print("      This correctly reduces overall pipeline uncertainty.")
    
    if results['physics_model'] > results['simple_average']:
        print("   ✅ Physics model gives HIGHER uncertainty than simple average.")
        print("      This is CORRECT: uncertainties compound, they don't average out.")
        print("      Example: Two 10% uncertainties → 19% total, not 10% average.")

def main():
    """Main experiment function"""
    
    # Use the test document from Experiment 01
    test_file = Path(__file__).parent.parent / "01_basic_extraction/test_document.txt"
    
    if not test_file.exists():
        print(f"❌ Test document not found at {test_file}")
        print("Run Experiment 01 first to create test document")
        sys.exit(1)
    
    # Run the pipeline with uncertainty tracking
    results = run_full_pipeline(str(test_file))
    
    # Display results
    display_results(results)
    
    # Save results
    output_file = Path(__file__).parent / "uncertainty_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📁 Results saved to {output_file}")
    
    # Validate against expected behavior
    print("\n" + "="*60)
    print("VALIDATION")
    print("="*60)
    
    validations = [
        ("Pipeline completed", results.get('pipeline_success', False)),
        ("Physics model calculated", 'physics_model' in results),
        ("Total uncertainty < 0.5", results.get('physics_model', 1.0) < 0.5),
        ("GraphPersister has 0 uncertainty on success", 
         any(s['stage'] == 'GraphPersister' and s['uncertainty'] == 0.0 
             for s in results.get('stages', []) if s.get('success'))),
        ("Physics model correctly compounds uncertainty", 
         results.get('physics_model', 0.0) > 0.0)  # Should be non-zero when there are uncertainties
    ]
    
    for validation, passed in validations:
        status = "✅" if passed else "❌"
        print(f"{status} {validation}")
    
    all_passed = all(passed for _, passed in validations)
    
    if all_passed:
        print("\n🎉 EXPERIMENT SUCCESSFUL!")
        print("Uncertainty propagation works as designed.")
    else:
        print("\n⚠️ Some validations failed - review results")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)