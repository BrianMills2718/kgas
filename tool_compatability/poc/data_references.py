"""
Data References for Memory Management
PhD Research: Handle large data without loading into memory
"""

from typing import Iterator, Optional, Dict, Any, Union
from pathlib import Path
from pydantic import BaseModel, Field
from enum import Enum
import mmap
import io


class StorageType(str, Enum):
    """Types of storage for data references"""
    FILE = "file"
    URL = "url"
    DATABASE = "database"
    MEMORY_MAPPED = "memory_mapped"
    STREAM = "stream"


class DataReference(BaseModel):
    """
    Reference to data without loading it into memory.
    
    Key features:
    - Lazy loading via streaming
    - Memory-mapped file access
    - Chunk-based processing
    - Metadata without content
    """
    
    storage_type: StorageType
    location: str  # Path, URL, or identifier
    size_bytes: int
    mime_type: Optional[str] = None
    encoding: Optional[str] = "utf-8"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Cache for memory-mapped file
    _mmap_cache: Optional[mmap.mmap] = None
    
    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = False
    
    def stream(self, chunk_size: int = 8192) -> Iterator[bytes]:
        """
        Stream data in chunks without loading entire file.
        
        Args:
            chunk_size: Size of each chunk in bytes
            
        Yields:
            Chunks of data
        """
        if self.storage_type == StorageType.FILE:
            with open(self.location, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        elif self.storage_type == StorageType.MEMORY_MAPPED:
            # Use memory-mapped file for efficient access
            if not self._mmap_cache:
                f = open(self.location, 'rb')
                self._mmap_cache = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            
            offset = 0
            while offset < self.size_bytes:
                end = min(offset + chunk_size, self.size_bytes)
                yield self._mmap_cache[offset:end]
                offset = end
        
        else:
            raise NotImplementedError(f"Streaming not implemented for {self.storage_type}")
    
    def stream_text(self, chunk_size: int = 8192) -> Iterator[str]:
        """
        Stream text data in chunks.
        
        Args:
            chunk_size: Size of each chunk in bytes
            
        Yields:
            Text chunks
        """
        for byte_chunk in self.stream(chunk_size):
            yield byte_chunk.decode(self.encoding or 'utf-8', errors='replace')
    
    def get_lines(self, start_line: int = 0, num_lines: Optional[int] = None) -> Iterator[str]:
        """
        Get specific lines from the file without loading all.
        
        Args:
            start_line: Starting line number (0-indexed)
            num_lines: Number of lines to return (None = all remaining)
            
        Yields:
            Lines of text
        """
        if self.storage_type != StorageType.FILE:
            raise NotImplementedError("Line access only for files")
        
        with open(self.location, 'r', encoding=self.encoding) as f:
            # Skip to start line
            for _ in range(start_line):
                line = f.readline()
                if not line:
                    return
            
            # Yield requested lines
            lines_yielded = 0
            for line in f:
                yield line.rstrip('\n')
                lines_yielded += 1
                if num_lines and lines_yielded >= num_lines:
                    break
    
    def get_sample(self, max_bytes: int = 1024) -> str:
        """
        Get a small sample of the data for preview.
        
        Args:
            max_bytes: Maximum bytes to read
            
        Returns:
            Sample text
        """
        if self.storage_type == StorageType.FILE:
            with open(self.location, 'r', encoding=self.encoding) as f:
                return f.read(max_bytes)
        else:
            # Use streaming for other types
            sample = b""
            for chunk in self.stream(max_bytes):
                sample += chunk
                if len(sample) >= max_bytes:
                    break
            return sample[:max_bytes].decode(self.encoding or 'utf-8', errors='replace')
    
    def search(self, pattern: str, max_results: int = 10) -> Iterator[tuple[int, str]]:
        """
        Search for pattern in file without loading all.
        
        Args:
            pattern: Pattern to search for
            max_results: Maximum results to return
            
        Yields:
            (line_number, line_content) tuples
        """
        if self.storage_type != StorageType.FILE:
            raise NotImplementedError("Search only for files")
        
        results_found = 0
        with open(self.location, 'r', encoding=self.encoding) as f:
            for line_num, line in enumerate(f):
                if pattern in line:
                    yield (line_num, line.rstrip('\n'))
                    results_found += 1
                    if results_found >= max_results:
                        break
    
    def cleanup(self):
        """Clean up any resources (like memory maps)"""
        if self._mmap_cache:
            self._mmap_cache.close()
            self._mmap_cache = None
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        self.cleanup()


class TextDataWithReference(BaseModel):
    """
    TextData that can use either content or reference.
    
    Allows tools to work with both small (in-memory) and large (referenced) data.
    """
    
    # Either content OR reference must be provided
    content: Optional[str] = None
    reference: Optional[DataReference] = None
    
    # Common metadata
    source: Optional[str] = None
    encoding: str = "utf-8"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.content and not self.reference:
            raise ValueError("Either content or reference must be provided")
        if self.content and self.reference:
            raise ValueError("Cannot have both content and reference")
    
    @property
    def is_referenced(self) -> bool:
        """Check if data is referenced (not in memory)"""
        return self.reference is not None
    
    @property
    def size_bytes(self) -> int:
        """Get size of data"""
        if self.content:
            return len(self.content.encode(self.encoding))
        elif self.reference:
            return self.reference.size_bytes
        return 0
    
    def get_content(self, max_size: Optional[int] = None) -> str:
        """
        Get content, either from memory or by loading reference.
        
        Args:
            max_size: Maximum size to load (prevents OOM)
            
        Returns:
            Content string
        """
        if self.content:
            return self.content
        
        elif self.reference:
            if max_size and self.reference.size_bytes > max_size:
                raise ValueError(f"Content too large: {self.reference.size_bytes} > {max_size}")
            
            # Load from reference
            if self.reference.storage_type == StorageType.FILE:
                with open(self.reference.location, 'r', encoding=self.encoding) as f:
                    return f.read()
            else:
                # Use streaming
                chunks = []
                for chunk in self.reference.stream_text():
                    chunks.append(chunk)
                return ''.join(chunks)
        
        return ""
    
    def stream_content(self, chunk_size: int = 8192) -> Iterator[str]:
        """
        Stream content in chunks.
        
        Args:
            chunk_size: Size of chunks
            
        Yields:
            Text chunks
        """
        if self.content:
            # Stream from memory
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i:i + chunk_size]
        
        elif self.reference:
            # Stream from reference
            yield from self.reference.stream_text(chunk_size)


class ProcessingStrategy(str, Enum):
    """Strategies for processing large data"""
    FULL_LOAD = "full_load"      # Load entire data (small files)
    STREAMING = "streaming"       # Process in chunks
    MEMORY_MAP = "memory_map"     # Use memory-mapped files
    SAMPLING = "sampling"         # Process representative sample
    REFERENCE = "reference"       # Pass reference only