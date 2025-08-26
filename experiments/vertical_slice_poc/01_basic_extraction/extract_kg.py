#!/usr/bin/env python3
"""
Experiment 01: Basic Knowledge Graph Extraction
Goal: Extract a knowledge graph with uncertainty from an LLM in one call

This is a simple, standalone script - no framework, no services, no abstraction.
We're proving the concept works before building complexity.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for config
sys.path.append(str(Path(__file__).parent.parent))
import config

def extract_knowledge_graph_gemini(text: str) -> Dict[str, Any]:
    """
    Extract knowledge graph using Google Gemini.
    Returns entities, relationships, uncertainty, and reasoning in one call.
    """
    import google.generativeai as genai
    
    # Configure Gemini
    genai.configure(api_key=config.API_KEY)
    model = genai.GenerativeModel(config.LLM_MODEL)
    
    # Build the prompt - being very explicit about what we want
    prompt = f"""
    Extract a knowledge graph from the following text.
    
    You must return valid JSON with this exact structure:
    {{
      "entities": [
        {{
          "id": "unique_identifier_no_spaces",
          "name": "Human Readable Name",
          "type": "person|organization|location|event|concept",
          "properties": {{
            "key": "value"
          }}
        }}
      ],
      "relationships": [
        {{
          "source": "source_entity_id",
          "target": "target_entity_id", 
          "type": "RELATIONSHIP_TYPE",
          "properties": {{
            "key": "value"
          }}
        }}
      ],
      "uncertainty": 0.25,
      "reasoning": "I assessed uncertainty of 0.25 because..."
    }}
    
    Important instructions:
    - Entity IDs should be lowercase with underscores (e.g., "barack_obama", "united_states")
    - Relationship types should be UPPERCASE with underscores (e.g., "WORKS_FOR", "LOCATED_IN")
    - Uncertainty should be between 0.0 (certain) and 1.0 (completely uncertain)
    - Reasoning should explain what factors influenced the uncertainty score
    - Include all relevant entities and relationships you can identify
    
    Text to analyze:
    {text[:config.CHUNK_SIZE]}
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # Sometimes Gemini adds markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        # Parse JSON
        kg_data = json.loads(response_text.strip())
        
        # Validate structure
        required_keys = ["entities", "relationships", "uncertainty", "reasoning"]
        for key in required_keys:
            if key not in kg_data:
                print(f"Warning: Missing key '{key}' in response")
                kg_data[key] = [] if key in ["entities", "relationships"] else None
        
        return kg_data
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response text: {response_text[:500]}...")
        return {
            "entities": [],
            "relationships": [],
            "uncertainty": 1.0,
            "reasoning": f"Failed to parse LLM response: {str(e)}"
        }
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {
            "entities": [],
            "relationships": [],
            "uncertainty": 1.0,
            "reasoning": f"API call failed: {str(e)}"
        }

def extract_knowledge_graph_openai(text: str) -> Dict[str, Any]:
    """
    Extract knowledge graph using OpenAI GPT-4.
    Alternative implementation for comparison.
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=config.API_KEYS["openai"])
    
    prompt = f"""
    Extract a knowledge graph from this text.
    
    Return JSON with entities (id, name, type, properties) and 
    relationships (source, target, type, properties), 
    plus uncertainty (0-1) and reasoning.
    
    Text: {text[:config.CHUNK_SIZE]}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "entities": [],
            "relationships": [],
            "uncertainty": 1.0,
            "reasoning": f"API call failed: {str(e)}"
        }

def save_results(kg_data: Dict[str, Any], output_file: str):
    """Save extraction results to file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(kg_data, f, indent=2)
    
    print(f"Results saved to {output_path}")

def analyze_extraction(kg_data: Dict[str, Any]):
    """Analyze and print extraction results"""
    print("\n" + "="*60)
    print("EXTRACTION RESULTS")
    print("="*60)
    
    # Entity analysis
    entities = kg_data.get("entities", [])
    print(f"\n📊 Entities: {len(entities)}")
    
    if entities:
        # Count by type
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        print("  Types:")
        for entity_type, count in sorted(type_counts.items()):
            print(f"    - {entity_type}: {count}")
        
        # Show first few entities
        print("\n  First 3 entities:")
        for entity in entities[:3]:
            print(f"    - {entity.get('name', 'unnamed')} ({entity.get('type', 'unknown')})")
    
    # Relationship analysis
    relationships = kg_data.get("relationships", [])
    print(f"\n🔗 Relationships: {len(relationships)}")
    
    if relationships:
        # Count by type
        rel_counts = {}
        for rel in relationships:
            rel_type = rel.get("type", "unknown")
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1
        
        print("  Types:")
        for rel_type, count in sorted(rel_counts.items()):
            print(f"    - {rel_type}: {count}")
        
        # Show first few relationships
        print("\n  First 3 relationships:")
        for rel in relationships[:3]:
            print(f"    - {rel.get('source', '?')} --[{rel.get('type', '?')}]--> {rel.get('target', '?')}")
    
    # Uncertainty analysis
    uncertainty = kg_data.get("uncertainty")
    reasoning = kg_data.get("reasoning", "No reasoning provided")
    
    print(f"\n🎯 Uncertainty: {uncertainty}")
    print(f"   Reasoning: {reasoning[:200]}..." if len(reasoning) > 200 else f"   Reasoning: {reasoning}")
    
    print("\n" + "="*60)

def main():
    """Main experiment function"""
    print("Knowledge Graph Extraction Experiment")
    print(f"Using: {config.LLM_PROVIDER} / {config.LLM_MODEL}")
    print("-" * 40)
    
    # Read test document
    test_file = Path(__file__).parent / "test_document.txt"
    
    if not test_file.exists():
        print(f"Error: Test document not found at {test_file}")
        print("Creating a sample test document...")
        
        # Create a simple test document
        sample_text = """
        TechCorp Announces Acquisition of DataFlow Systems
        
        San Francisco, CA - January 26, 2025
        
        TechCorp, a leading software company based in San Francisco, announced today 
        its acquisition of DataFlow Systems for $2.3 billion. The acquisition was 
        approved by TechCorp's CEO Sarah Johnson and DataFlow's founder Michael Chen.
        
        DataFlow Systems, founded in 2018 in Seattle, specializes in real-time data 
        processing and has over 500 employees. The company's main product, StreamEngine,
        processes over 1 billion events per day for Fortune 500 companies.
        
        "This acquisition strengthens our position in the enterprise data market," 
        said Sarah Johnson. "DataFlow's technology complements our existing CloudBase 
        platform perfectly."
        
        The deal is expected to close in Q2 2025, pending regulatory approval. 
        TechCorp plans to maintain DataFlow's Seattle office as an engineering hub.
        """
        
        with open(test_file, 'w') as f:
            f.write(sample_text)
        print(f"Created sample document at {test_file}")
    
    # Read the document
    with open(test_file, 'r') as f:
        text = f.read()
    
    print(f"Document length: {len(text)} characters")
    
    # Extract knowledge graph
    print("\nExtracting knowledge graph...")
    
    if config.LLM_PROVIDER == "gemini" or config.LLM_PROVIDER == "google":
        kg_data = extract_knowledge_graph_gemini(text)
    elif config.LLM_PROVIDER == "openai":
        kg_data = extract_knowledge_graph_openai(text)
    else:
        print(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
        return
    
    # Analyze results
    analyze_extraction(kg_data)
    
    # Save results
    timestamp = Path(__file__).parent / "outputs" / "extraction_result.json"
    save_results(kg_data, str(timestamp))
    
    # Return success/failure
    if kg_data.get("entities") and kg_data.get("uncertainty") is not None:
        print("\n✅ Extraction successful!")
        return True
    else:
        print("\n❌ Extraction failed - check the output")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)