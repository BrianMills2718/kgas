#!/usr/bin/env python3
"""
ChunkedEntityExtractor - Extract entities from text with batching and memory efficiency
"""

import os
import json
import hashlib
import time
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.base_tool import ExtensibleTool, ToolResult, ToolCapabilities, ProcessingStrategy
from poc.data_types import DataType, SemanticType, DataSchema

# Try to import litellm for Gemini
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not available - entity extraction will be limited")


class ChunkedEntityExtractor(ExtensibleTool):
    """
    Extract entities from text using chunked processing for memory efficiency.
    
    Features:
    - Processes text in configurable chunks (default 4000 chars)
    - Overlapping windows to avoid boundary issues
    - Batched LLM calls for efficiency
    - Entity deduplication across chunks
    - Progress tracking for large texts
    - Fail-fast on service errors
    """
    
    def __init__(self, 
                 chunk_size: int = 4000,
                 overlap: int = 200,
                 batch_size: int = 5,
                 model: str = "gemini/gemini-2.0-flash-exp"):
        """
        Initialize chunked entity extractor.
        
        Args:
            chunk_size: Size of each text chunk in characters
            overlap: Overlap between chunks to avoid boundary issues
            batch_size: Number of chunks to process in parallel
            model: LLM model to use for extraction
        """
        super().__init__()
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.batch_size = batch_size
        self.model = model
        
        # Load API key from environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key and LITELLM_AVAILABLE:
            # Try loading from .env file
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.getenv("GEMINI_API_KEY")
            except ImportError:
                pass
    
    def get_capabilities(self) -> ToolCapabilities:
        """Declare tool capabilities."""
        return ToolCapabilities(
            tool_id="ChunkedEntityExtractor",
            name="Chunked Entity Extractor",
            description="Extract entities from text with efficient chunking and batching",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            semantic_input=SemanticType.DOCUMENT,
            semantic_output=SemanticType.ENTITIES,
            processing_strategy=ProcessingStrategy.STREAMING,
            max_input_size=100 * 1024 * 1024,  # 100MB
            supports_streaming=True,
            memory_efficient=True
        )
    
    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Create overlapping chunks from text.
        
        Returns list of chunks with metadata.
        """
        chunks = []
        text_length = len(text)
        
        start = 0
        chunk_num = 0
        
        while start < text_length:
            # Calculate end position
            end = min(start + self.chunk_size, text_length)
            
            # Extract chunk
            chunk_text = text[start:end]
            
            # Create chunk metadata
            chunk = {
                'number': chunk_num,
                'text': chunk_text,
                'start_char': start,
                'end_char': end,
                'size': len(chunk_text),
                'is_last': end >= text_length
            }
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.overlap if end < text_length else text_length
            chunk_num += 1
        
        return chunks
    
    def _extract_from_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract entities from a single chunk using LLM.
        
        Returns list of extracted entities.
        """
        if not LITELLM_AVAILABLE:
            # Fallback: Simple regex-based extraction
            return self._fallback_extraction(chunk['text'])
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set - cannot perform LLM extraction")
        
        prompt = f"""Extract all named entities from the following text chunk.
        
Return entities as a JSON array with the following structure:
[
  {{
    "text": "entity text",
    "type": "PERSON|ORGANIZATION|LOCATION|DATE|CONCEPT|OTHER",
    "context": "brief context where entity appears"
  }}
]

Text chunk (chunk {chunk['number'] + 1}, chars {chunk['start_char']}-{chunk['end_char']}):
{chunk['text']}

Entities JSON:"""
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistency
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            entities_data = json.loads(response_text.strip())
            
            # Add chunk metadata to each entity
            for entity in entities_data:
                entity['chunk_number'] = chunk['number']
                entity['char_offset'] = chunk['start_char']
            
            return entities_data
            
        except Exception as e:
            # FAIL FAST - no fallback for LLM errors
            raise RuntimeError(f"LLM extraction failed for chunk {chunk['number']}: {e}")
    
    def _fallback_extraction(self, text: str) -> List[Dict[str, Any]]:
        """
        Simple fallback extraction without LLM.
        
        Uses basic patterns to find potential entities.
        """
        import re
        
        entities = []
        
        # Simple patterns for common entity types
        patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'URL': r'https?://[^\s]+',
            'CAPITALIZED': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            'ALL_CAPS': r'\b[A-Z]{2,}\b',
            'NUMBER': r'\b\d+(?:\.\d+)?\b'
        }
        
        for entity_type, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append({
                    'text': match.group(),
                    'type': 'OTHER' if entity_type in ['CAPITALIZED', 'ALL_CAPS'] else entity_type,
                    'context': text[max(0, match.start()-20):min(len(text), match.end()+20)],
                    'confidence': 0.3  # Low confidence for pattern matching
                })
        
        return entities
    
    def _deduplicate_entities(self, all_entities: List[Dict[str, Any]]) -> List[DataSchema.Entity]:
        """
        Deduplicate entities across chunks.
        
        Merges entities that appear in multiple chunks.
        """
        # Group by normalized text and type
        entity_map = {}
        
        for entity in all_entities:
            # Create normalized key
            key = (entity['text'].lower().strip(), entity.get('type', 'OTHER'))
            
            if key not in entity_map:
                entity_map[key] = {
                    'text': entity['text'],
                    'type': entity.get('type', 'OTHER'),
                    'contexts': [],
                    'chunks': set(),
                    'confidence': entity.get('confidence', 0.8)
                }
            
            # Add context and chunk info
            if 'context' in entity:
                entity_map[key]['contexts'].append(entity['context'])
            if 'chunk_number' in entity:
                entity_map[key]['chunks'].add(entity['chunk_number'])
        
        # Convert to Entity objects
        entities = []
        for (text, entity_type), data in entity_map.items():
            # Generate ID based on text and type
            entity_id = hashlib.md5(f"{text}:{entity_type}".encode()).hexdigest()[:12]
            
            entity = DataSchema.Entity(
                id=entity_id,
                text=data['text'],
                type=data['type'],
                confidence=data['confidence'],
                metadata={
                    'contexts': data['contexts'][:3],  # Keep top 3 contexts
                    'chunk_count': len(data['chunks']),
                    'chunks': sorted(list(data['chunks']))[:10]  # Keep first 10 chunks
                }
            )
            entities.append(entity)
        
        return entities
    
    def _process_in_batches(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process chunks in batches for efficiency.
        
        Returns all extracted entities.
        """
        all_entities = []
        total_chunks = len(chunks)
        
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:min(i + self.batch_size, total_chunks)]
            
            # Process batch
            for chunk in batch:
                print(f"  Processing chunk {chunk['number'] + 1}/{total_chunks} "
                      f"({chunk['size']} chars)...")
                
                try:
                    entities = self._extract_from_chunk(chunk)
                    all_entities.extend(entities)
                    print(f"    Found {len(entities)} entities")
                except Exception as e:
                    # FAIL FAST - propagate errors
                    raise RuntimeError(f"Batch processing failed at chunk {chunk['number']}: {e}")
            
            # Small delay between batches to avoid rate limiting
            if i + self.batch_size < total_chunks:
                time.sleep(0.5)
        
        return all_entities
    
    def process(self, input_data: DataSchema.TextData, context: Optional[Any] = None) -> ToolResult:
        """
        Process text to extract entities using chunked approach.
        
        Args:
            input_data: Text data to process
            context: Optional context
            
        Returns:
            ToolResult with extracted entities
        """
        try:
            print(f"\n{'='*60}")
            print(f"ChunkedEntityExtractor: Processing {input_data.char_count} characters")
            print(f"{'='*60}")
            
            # Track metrics
            start_time = time.perf_counter()
            
            # Create chunks
            print(f"\nCreating chunks (size={self.chunk_size}, overlap={self.overlap})...")
            chunks = self._create_chunks(input_data.content)
            print(f"Created {len(chunks)} chunks")
            
            # Process chunks in batches
            print(f"\nExtracting entities (batch_size={self.batch_size})...")
            all_entities = self._process_in_batches(chunks)
            print(f"Extracted {len(all_entities)} raw entities")
            
            # Deduplicate entities
            print(f"\nDeduplicating entities...")
            unique_entities = self._deduplicate_entities(all_entities)
            print(f"Deduplicated to {len(unique_entities)} unique entities")
            
            # Calculate metrics
            duration = time.perf_counter() - start_time
            
            # Print entity summary
            print(f"\n{'='*60}")
            print(f"Entity Summary:")
            type_counts = {}
            for entity in unique_entities:
                type_counts[entity.type] = type_counts.get(entity.type, 0) + 1
            for entity_type, count in sorted(type_counts.items()):
                print(f"  {entity_type}: {count}")
            
            # Create result
            result_data = DataSchema.EntitiesData(
                entities=unique_entities,
                source_checksum=input_data.checksum,
                extraction_model=self.model if LITELLM_AVAILABLE else "pattern_matching",
                extraction_timestamp=datetime.now().isoformat(),
                metadata={
                    'chunk_count': len(chunks),
                    'chunk_size': self.chunk_size,
                    'overlap': self.overlap,
                    'total_entities': len(all_entities),
                    'unique_entities': len(unique_entities),
                    'processing_time': duration
                }
            )
            
            # Update metrics
            self.metrics['entities_extracted'] = len(unique_entities)
            self.metrics['chunks_processed'] = len(chunks)
            self.metrics['processing_time'] = duration
            
            print(f"\n✅ Extraction complete in {duration:.2f}s")
            print(f"{'='*60}\n")
            
            return ToolResult(
                success=True,
                data=result_data,
                metadata={
                    'chunks': len(chunks),
                    'entities': len(unique_entities),
                    'duration': duration
                }
            )
            
        except Exception as e:
            # FAIL FAST - no graceful degradation
            error_msg = f"ChunkedEntityExtractor failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            print(f"{'='*60}\n")
            
            self.metrics['errors'] += 1
            
            return ToolResult(
                success=False,
                error=error_msg,
                metadata={'error_type': type(e).__name__}
            )


def main():
    """Test the chunked entity extractor."""
    print("Testing ChunkedEntityExtractor...")
    
    # Create test data
    test_text = """
    Apple Inc. is headquartered in Cupertino, California. The company was founded by 
    Steve Jobs, Steve Wozniak, and Ronald Wayne in April 1976. Tim Cook became CEO 
    in August 2011, succeeding Jobs.
    
    Microsoft Corporation, based in Redmond, Washington, was founded by Bill Gates 
    and Paul Allen in 1975. Satya Nadella has been CEO since 2014.
    
    Google LLC, a subsidiary of Alphabet Inc., is located in Mountain View, California.
    Larry Page and Sergey Brin founded Google in 1998 while they were PhD students at
    Stanford University. Sundar Pichai is the current CEO.
    
    Amazon.com Inc. was founded by Jeff Bezos in 1994 in Seattle, Washington. The
    company started as an online bookstore but has since diversified into cloud computing,
    digital streaming, and artificial intelligence. Andy Jassy became CEO in 2021.
    """ * 10  # Repeat to create larger text
    
    text_data = DataSchema.TextData(
        content=test_text,
        source="test_document",
        char_count=len(test_text),
        checksum=hashlib.md5(test_text.encode()).hexdigest()
    )
    
    # Create extractor with small chunks for testing
    extractor = ChunkedEntityExtractor(
        chunk_size=500,  # Small chunks for testing
        overlap=50,
        batch_size=2
    )
    
    # Process
    result = extractor.process(text_data)
    
    if result.success:
        print(f"\n✅ Test successful!")
        print(f"Extracted {len(result.data.entities)} unique entities")
        
        # Show sample entities
        print("\nSample entities:")
        for entity in result.data.entities[:10]:
            print(f"  - {entity.text} ({entity.type})")
    else:
        print(f"\n❌ Test failed: {result.error}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())