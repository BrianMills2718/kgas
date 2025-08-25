"""
Streaming Text Loader - Handle large files without loading into memory
PhD Research: Memory-efficient text processing
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from poc.base_tool import BaseTool, ToolResult
from poc.data_types import DataType, DataSchema
from poc.data_references import (
    DataReference, 
    TextDataWithReference, 
    StorageType,
    ProcessingStrategy
)
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field


class StreamingConfig(BaseModel):
    """Configuration for streaming text loader"""
    small_file_threshold: int = Field(default=1024*1024, description="Files smaller than this are loaded to memory")
    large_file_threshold: int = Field(default=10*1024*1024, description="Files larger than this use memory mapping")
    max_file_size: int = Field(default=10*1024*1024*1024, description="Maximum file size allowed")


class StreamingTextLoader(BaseTool[DataSchema.FileData, TextDataWithReference, StreamingConfig]):
    """
    Load text files using references for memory efficiency.
    
    Key features:
    - Creates references for large files (>1MB)
    - Loads small files directly into memory
    - Supports memory-mapped access
    - Provides streaming interface
    """
    
    def __init__(self, config: Optional[StreamingConfig] = None):
        super().__init__(config)
        
        # Thresholds for different strategies
        cfg = self.config
        self.small_file_threshold = cfg.small_file_threshold
        self.large_file_threshold = cfg.large_file_threshold
        self.max_file_size = cfg.max_file_size
    
    @property
    def tool_id(self) -> str:
        return "StreamingTextLoader"
    
    @property
    def name(self) -> str:
        return "Streaming Text Loader"
    
    @property
    def description(self) -> str:
        return "Load text files efficiently using references for large files"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    @property
    def input_schema(self) -> Type[DataSchema.FileData]:
        return DataSchema.FileData
    
    @property
    def output_schema(self) -> Type[TextDataWithReference]:
        return TextDataWithReference
    
    @property
    def config_schema(self) -> Type[StreamingConfig]:
        return StreamingConfig
    
    def default_config(self) -> StreamingConfig:
        return StreamingConfig()
    
    @property
    def input_type(self) -> DataType:
        return DataType.FILE
    
    @property 
    def output_type(self) -> DataType:
        return DataType.TEXT
    
    def _validate_input(self, input_data: DataSchema.FileData) -> DataSchema.FileData:
        """Validate the input file"""
        
        # Check file exists
        if not os.path.exists(input_data.path):
            raise FileNotFoundError(f"File not found: {input_data.path}")
        
        # Check file size
        actual_size = os.path.getsize(input_data.path)
        if actual_size > self.max_file_size:
            raise ValueError(f"File too large: {actual_size / (1024*1024*1024):.1f}GB (max: 10GB)")
        
        # Update size if needed
        input_data.size_bytes = actual_size
        
        return input_data
    
    def _determine_strategy(self, size_bytes: int) -> ProcessingStrategy:
        """Determine the best processing strategy based on file size"""
        
        if size_bytes <= self.small_file_threshold:
            return ProcessingStrategy.FULL_LOAD
        elif size_bytes <= self.large_file_threshold:
            return ProcessingStrategy.STREAMING
        else:
            return ProcessingStrategy.MEMORY_MAP
    
    def _execute(self, input_data: DataSchema.FileData, **kwargs) -> TextDataWithReference:
        """
        Load text file using appropriate strategy.
        
        For small files: Load content directly
        For large files: Create reference for streaming
        """
        
        file_path = input_data.path
        size_bytes = input_data.size_bytes
        
        # Determine strategy
        strategy = self._determine_strategy(size_bytes)
        
        # Get encoding
        encoding = self._detect_encoding(file_path)
        
        if strategy == ProcessingStrategy.FULL_LOAD:
            # Small file - load directly
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return TextDataWithReference(
                content=content,
                source=file_path,
                encoding=encoding,
                metadata={
                    "strategy": strategy.value,
                    "size_bytes": size_bytes,
                    "mime_type": input_data.mime_type
                }
            )
        
        else:
            # Large file - create reference
            storage_type = (
                StorageType.MEMORY_MAPPED 
                if strategy == ProcessingStrategy.MEMORY_MAP 
                else StorageType.FILE
            )
            
            reference = DataReference(
                storage_type=storage_type,
                location=file_path,
                size_bytes=size_bytes,
                mime_type=input_data.mime_type,
                encoding=encoding,
                metadata={
                    "strategy": strategy.value,
                    "line_count": self._estimate_line_count(file_path, size_bytes)
                }
            )
            
            return TextDataWithReference(
                reference=reference,
                source=file_path,
                encoding=encoding,
                metadata={
                    "strategy": strategy.value,
                    "size_bytes": size_bytes,
                    "mime_type": input_data.mime_type
                }
            )
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding by reading first few bytes.
        
        Simple detection - could be enhanced with chardet library.
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return 'utf-8'
        except UnicodeDecodeError:
            # Fall back to latin-1
            return 'latin-1'
    
    def _estimate_line_count(self, file_path: str, size_bytes: int) -> int:
        """
        Estimate line count without reading entire file.
        
        Samples first 10KB and extrapolates.
        """
        sample_size = min(10240, size_bytes)  # 10KB sample
        
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
        
        # Count newlines in sample
        newlines_in_sample = sample.count(b'\n')
        
        if sample_size < size_bytes:
            # Extrapolate
            estimated = int(newlines_in_sample * (size_bytes / sample_size))
        else:
            estimated = newlines_in_sample
        
        return estimated
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return tool capabilities"""
        return {
            **super().get_capabilities(),
            "max_file_size": self.max_file_size,
            "streaming_threshold": self.small_file_threshold,
            "memory_map_threshold": self.large_file_threshold,
            "supported_strategies": [s.value for s in ProcessingStrategy]
        }


class ExtractorConfig(BaseModel):
    """Configuration for streaming entity extractor"""
    chunk_size: int = Field(default=1024*1024, description="Size of chunks for streaming")
    overlap_size: int = Field(default=1024, description="Overlap between chunks")


class StreamingEntityExtractor(BaseTool[TextDataWithReference, DataSchema.EntitiesData, ExtractorConfig]):
    """
    Extract entities from text data, supporting both content and references.
    
    Can process:
    - Small files from memory (content)
    - Large files via streaming (reference)
    """
    
    def __init__(self, config: Optional[ExtractorConfig] = None):
        super().__init__(config)
        
        # Processing settings
        cfg = self.config
        self.chunk_size = cfg.chunk_size
        self.overlap_size = cfg.overlap_size
    
    @property
    def tool_id(self) -> str:
        return "StreamingEntityExtractor"
    
    @property
    def name(self) -> str:
        return "Streaming Entity Extractor"
    
    @property
    def description(self) -> str:
        return "Extract entities from text, supporting large files via streaming"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    @property
    def input_schema(self) -> Type[TextDataWithReference]:
        return TextDataWithReference
    
    @property
    def output_schema(self) -> Type[DataSchema.EntitiesData]:
        return DataSchema.EntitiesData
    
    @property
    def config_schema(self) -> Type[ExtractorConfig]:
        return ExtractorConfig
    
    def default_config(self) -> ExtractorConfig:
        return ExtractorConfig()
    
    @property
    def input_type(self) -> DataType:
        return DataType.TEXT
    
    @property
    def output_type(self) -> DataType:
        return DataType.ENTITIES
    
    def _execute(self, input_data: TextDataWithReference, **kwargs) -> DataSchema.EntitiesData:
        """
        Extract entities from text data.
        
        Uses streaming for large files to avoid memory issues.
        """
        
        entities = []
        
        if input_data.is_referenced:
            # Process via streaming
            entities = self._extract_streaming(input_data)
        else:
            # Process from memory
            entities = self._extract_from_content(input_data.content)
        
        return DataSchema.EntitiesData(
            entities=entities,
            metadata={
                "source": input_data.source,
                "processing": "streaming" if input_data.is_referenced else "in-memory",
                "total_found": len(entities)
            }
        )
    
    def _extract_streaming(self, input_data: TextDataWithReference) -> list:
        """
        Extract entities by processing file in chunks.
        
        Maintains overlap between chunks to avoid missing entities at boundaries.
        """
        entities = []
        seen_entities = set()  # Deduplication
        
        overlap_buffer = ""
        
        for chunk in input_data.stream_content(self.chunk_size):
            # Process chunk with overlap from previous
            text_to_process = overlap_buffer + chunk
            
            # Extract from this chunk
            chunk_entities = self._extract_from_content(text_to_process)
            
            # Deduplicate
            for entity in chunk_entities:
                entity_key = (entity.text, entity.type)
                if entity_key not in seen_entities:
                    entities.append(entity)
                    seen_entities.add(entity_key)
            
            # Save end of chunk as overlap for next iteration
            if len(chunk) >= self.overlap_size:
                overlap_buffer = chunk[-self.overlap_size:]
            else:
                overlap_buffer = chunk
        
        return entities
    
    def _extract_from_content(self, content: str) -> list:
        """
        Extract entities from text content.
        
        Simple regex-based extraction for demonstration.
        In production, would use NER model.
        """
        import re
        from poc.data_types import DataSchema
        
        entities = []
        
        # Simple patterns for demonstration
        patterns = {
            "PERSON": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
            "COMPANY": r"\b[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)* (?:Inc|Corp|LLC|Ltd|Company)\b",
            "LOCATION": r"\b(?:New |San |Los )?[A-Z][a-z]+(?:[ -][A-Z][a-z]+)*\b"
        }
        
        for entity_type, pattern in patterns.items():
            for match in re.finditer(pattern, content):
                entity = DataSchema.Entity(
                    id=f"e_{len(entities)}",
                    text=match.group(),
                    type=entity_type,
                    score=0.75  # Fixed score for demo
                )
                entities.append(entity)
        
        return entities