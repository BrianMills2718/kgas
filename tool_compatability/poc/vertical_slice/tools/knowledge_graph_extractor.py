#!/usr/bin/env python3
"""Knowledge Graph extraction using LLM with uncertainty assessment"""

import json
import os
import time
import random
from typing import Dict, List, Any, Tuple
import litellm
from dotenv import load_dotenv

class KnowledgeGraphExtractor:
    """Extract knowledge graph from text using LLM"""
    
    def __init__(self, chunk_size=4000, overlap=200, schema_mode="open"):
        # CRITICAL: Load .env FIRST
        load_dotenv('/home/brian/projects/Digimons/.env')
        
        self.tool_id = "KnowledgeGraphExtractor"
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.schema_mode = schema_mode
        
        # Now this will work - get API key after loading .env
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in /home/brian/projects/Digimons/.env")
        
        # Always use gemini-1.5-flash
        self.model = "gemini/gemini-1.5-flash"
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Extract knowledge graph from text
        
        Returns:
            Dict with entities, relationships, uncertainty, and reasoning
        """
        if not text or len(text.strip()) == 0:
            return {
                'success': False,
                'error': 'Empty text provided',
                'uncertainty': 1.0,
                'reasoning': 'No text to extract from'
            }
        
        # Handle chunking if text is too long
        chunks = []
        if len(text) > self.chunk_size:
            chunks = self._create_chunks(text)
            print(f"Text chunked into {len(chunks)} chunks")
        else:
            chunks = [text]
        
        # Extract from each chunk
        all_entities = []
        all_relationships = []
        chunk_uncertainties = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            kg_data = self._extract_knowledge_graph(chunk)
            
            if kg_data and 'entities' in kg_data:
                all_entities.extend(kg_data['entities'])
                all_relationships.extend(kg_data.get('relationships', []))
                # Assess uncertainty for this chunk
                chunk_uncertainties.append(self._assess_chunk_uncertainty(
                    chunk_length=len(chunk),
                    entity_count=len(kg_data['entities']),
                    relationship_count=len(kg_data.get('relationships', []))
                ))
        
        # Deduplicate entities by name
        unique_entities = {}
        for entity in all_entities:
            key = entity.get('name', '').lower()
            if key and key not in unique_entities:
                unique_entities[key] = entity
        
        # Final unified assessment
        uncertainty, reasoning = self._assess_extraction_uncertainty(
            text_length=len(text),
            entity_count=len(unique_entities),
            relationship_count=len(all_relationships),
            chunk_count=len(chunks),
            chunk_uncertainties=chunk_uncertainties
        )
        
        return {
            'success': True,
            'entities': list(unique_entities.values()),
            'relationships': all_relationships,
            'uncertainty': uncertainty,
            'reasoning': reasoning,
            'construct_mapping': 'character_sequence → knowledge_graph'
        }
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks of text"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end
                for sep in ['. ', '.\n', '! ', '? ']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep != -1:
                        end = last_sep + len(sep)
                        break
            
            chunks.append(text[start:end])
            start = end - self.overlap  # Overlap for context
        
        return chunks
    
    def _extract_knowledge_graph(self, text: str) -> Dict:
        """Extract entities and relationships using LLM"""
        
        prompt = f"""Extract a knowledge graph from the following text.

Return a JSON object with entities and relationships. Be comprehensive but accurate.

IMPORTANT Entity Types (use these exact types):
- PERSON: For people (e.g., Brian Chhun, Jane Smith)
- ORGANIZATION: For institutions, companies, departments (e.g., University of Melbourne)  
- SYSTEM: For software systems or frameworks (e.g., KGAS)
- TECHNOLOGY: For programming languages, databases, tools (e.g., Python, Neo4j)
- LOCATION: For places
- CONCEPT: For abstract ideas or processes

Common Relationship Types:
- STUDIES_AT, WORKS_AT, MEMBER_OF (person → organization)
- DEVELOPED, CREATED, BUILT (person → system/technology)
- USES, IMPLEMENTS (system → technology)
- SUPERVISES, MANAGES (person → person)
- LOCATED_IN (anything → location)

Format:
{{
  "entities": [
    {{
      "id": "unique_id",
      "name": "entity name", 
      "type": "PERSON|ORGANIZATION|SYSTEM|TECHNOLOGY|LOCATION|CONCEPT",
      "attributes": {{}}
    }}
  ],
  "relationships": [
    {{
      "source": "source_entity_name",
      "target": "target_entity_name", 
      "type": "RELATIONSHIP_TYPE",
      "attributes": {{}}
    }}
  ]
}}

Text:
{text[:3500]}  # Limit for API call

JSON Output:"""
        
        # Robust retry logic with exponential backoff
        max_retries = 10  # More attempts
        base_delay = 5  # Start with 5 seconds
        max_delay = 60  # Cap at 60 seconds
        
        for attempt in range(max_retries):
            try:
                # Use Gemini for extraction
                response = litellm.completion(
                    model="gemini/gemini-1.5-flash",
                    messages=[{"role": "user", "content": prompt}],
                    api_key=self.api_key,
                    temperature=0.1,  # Low temperature for consistency
                    max_tokens=2000
                )
                
                # Parse response
                content = response.choices[0].message.content
                
                # Extract JSON from response
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0]
                else:
                    json_str = content
                
                kg_data = json.loads(json_str.strip())
                
                # Add unique IDs if missing
                for i, entity in enumerate(kg_data.get('entities', [])):
                    if 'id' not in entity:
                        entity['id'] = f"entity_{i+1}"
                
                return kg_data
                
            except (litellm.exceptions.InternalServerError, 
                    litellm.exceptions.ServiceUnavailable,
                    litellm.exceptions.RateLimitError) as e:
                # Handle multiple error types
                if attempt < max_retries - 1:
                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** attempt) + random.uniform(0, 3), max_delay)
                    print(f"API error ({type(e).__name__}), retrying in {delay:.1f}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"API failed after {max_retries} attempts - giving up")
                    return {'entities': [], 'relationships': []}
            except Exception as e:
                print(f"LLM extraction error: {e}")
                return {'entities': [], 'relationships': []}
    
    def _assess_chunk_uncertainty(self, chunk_length: int, entity_count: int, relationship_count: int) -> float:
        """Assess uncertainty for a single chunk extraction"""
        base_uncertainty = 0.25  # Base LLM extraction uncertainty
        
        # Adjust based on extraction density
        if entity_count == 0:
            return 0.9  # Very high uncertainty if nothing extracted
        
        density = (entity_count + relationship_count) / (chunk_length / 100)
        
        if density < 0.5:
            # Very sparse extraction
            return base_uncertainty + 0.2
        elif density > 5:
            # Very dense - might be over-extraction
            return base_uncertainty + 0.1
        else:
            # Normal density
            return base_uncertainty
    
    def _assess_extraction_uncertainty(self, text_length: int, entity_count: int, 
                                      relationship_count: int, chunk_count: int,
                                      chunk_uncertainties: List[float]) -> Tuple[float, str]:
        """
        Assess extraction uncertainty based on ACTUAL extraction challenges
        """
        # Start with base LLM uncertainty
        base_uncertainty = 0.25
        adjustments = []
        
        # 1. Entity Extraction Quality
        if entity_count == 0:
            base_uncertainty = 0.95
            adjustments.append("no entities extracted")
        elif entity_count < 3:
            base_uncertainty += 0.15
            adjustments.append(f"sparse extraction ({entity_count} entities)")
        elif text_length > 0:
            # Check for suspiciously high entity density
            entity_density = entity_count / (text_length / 1000)  # entities per 1000 chars
            if entity_density > 20:
                base_uncertainty += 0.10
                adjustments.append(f"possible over-extraction (density: {entity_density:.1f}/1k chars)")
        
        # 2. Relationship Quality
        if entity_count > 0:
            relationship_ratio = relationship_count / entity_count
            if relationship_ratio < 0.5:  # Very few relationships
                base_uncertainty += 0.10
                adjustments.append(f"sparse relationships ({relationship_ratio:.1f} per entity)")
            elif relationship_ratio > 3:  # Too many relationships
                base_uncertainty += 0.05
                adjustments.append(f"dense relationships ({relationship_ratio:.1f} per entity)")
        
        # 3. Chunking Impact
        if chunk_count > 1:
            base_uncertainty += 0.05 * (chunk_count - 1)  # Each chunk adds uncertainty
            adjustments.append(f"{chunk_count} chunks processed")
        
        # Build reasoning
        reasoning = f"Extracted {entity_count} entities and {relationship_count} relationships"
        if adjustments:
            reasoning += f" | Adjustments: {'; '.join(adjustments)}"
        
        # Ensure valid range
        final_uncertainty = min(max(base_uncertainty, 0.0), 0.95)
        
        return final_uncertainty, reasoning

# Test the extractor
if __name__ == "__main__":
    extractor = KnowledgeGraphExtractor()
    
    test_text = """
    John Smith is the CEO of TechCorp, a leading technology company based in San Francisco.
    He previously worked at DataSystems Inc. where he led the AI research team.
    TechCorp recently acquired SmallStartup for $50 million.
    """
    
    result = extractor.process(test_text)
    if result['success']:
        print(f"✅ Extracted {len(result['entities'])} entities")
        print(f"✅ Extracted {len(result['relationships'])} relationships")
        print(f"Uncertainty: {result['uncertainty']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
    else:
        print(f"❌ Extraction failed: {result.get('error')}")