#!/usr/bin/env python3
"""
StreamingFileLoader - Native tool for the extensible framework
Handles large files (50MB+) with streaming to avoid memory issues
"""

import os
import mmap
import hashlib
from pathlib import Path
from typing import Iterator, Optional, Generator
import mimetypes
# Optional imports - fail gracefully if not available
try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import chardet
    HAS_CHARDET = True  
except ImportError:
    HAS_CHARDET = False

# Framework imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataSchema, DataType
from data_references import ProcessingStrategy, DataReference

class StreamingFileLoader(ExtensibleTool):
    """
    Load files of any size using streaming/memory-mapped approaches.
    NO SERVICE DEPENDENCIES - fail fast on any error.
    """
    
    def __init__(self, chunk_size: int = 1024 * 1024):  # 1MB chunks
        """Initialize with configurable chunk size"""
        self.chunk_size = chunk_size
        self.supported_formats = {
            '.txt': self._stream_text,
            '.md': self._stream_text,
            '.pdf': self._stream_pdf,
            '.json': self._stream_text,
            '.csv': self._stream_text,
            '.log': self._stream_text,
            '.xml': self._stream_text,
            '.html': self._stream_text
        }
    
    def get_capabilities(self) -> ToolCapabilities:
        """Return tool capabilities"""
        return ToolCapabilities(
            tool_id="StreamingFileLoader",
            name="Streaming File Loader",
            description="Load large files using streaming to avoid memory issues",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            processing_strategy=ProcessingStrategy.STREAMING,
            max_input_size=500 * 1024 * 1024,  # 500MB max
            supports_streaming=True,
            memory_efficient=True
        )
    
    def process(self, input_data: DataSchema.FileData, context=None):
        """
        Process file with streaming - FAIL FAST on any error.
        
        For large files, returns a DataReference that can be streamed.
        For small files (<10MB), returns full TextData.
        """
        # Validate file exists - FAIL FAST
        if not os.path.exists(input_data.path):
            raise FileNotFoundError(f"File not found: {input_data.path}")
        
        # Security check - FAIL FAST on suspicious paths
        if "../" in input_data.path or input_data.path.startswith("/etc"):
            raise ValueError(f"Suspicious file path: {input_data.path}")
        
        # Get file extension
        ext = Path(input_data.path).suffix.lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Unsupported format: {ext}")
        
        # Get file size
        file_size = os.path.getsize(input_data.path)
        
        # Decide on strategy based on size
        if file_size < 10 * 1024 * 1024:  # <10MB - load fully
            return self._load_small_file(input_data)
        else:  # Large file - return reference for streaming
            return self._create_streaming_reference(input_data)
    
    def _load_small_file(self, input_data: DataSchema.FileData) -> ToolResult:
        """Load small file completely into memory"""
        ext = Path(input_data.path).suffix.lower()
        
        try:
            # Use appropriate loader
            content = self.supported_formats[ext](input_data.path, full_load=True)
            
            # Calculate checksum
            with open(input_data.path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            
            text_data = DataSchema.TextData(
                content=content,
                source=input_data.path,
                char_count=len(content),
                line_count=content.count('\n') + 1,
                checksum=checksum
            )
            
            return ToolResult(success=True, data=text_data)
            
        except Exception as e:
            # FAIL FAST - no recovery
            raise RuntimeError(f"Failed to load file: {str(e)}")
    
    def _create_streaming_reference(self, input_data: DataSchema.FileData) -> ToolResult:
        """Create a reference for streaming large files"""
        
        # Create data reference with streaming iterator
        reference = DataReference(
            reference_id=f"stream_{hashlib.md5(input_data.path.encode()).hexdigest()[:8]}",
            source_path=input_data.path,
            data_type=DataType.TEXT,
            size_bytes=input_data.size_bytes,
            strategy=ProcessingStrategy.STREAMING,
            stream_generator=self._create_stream_generator(input_data.path)
        )
        
        return ToolResult(
            success=True,
            data=reference,
            metadata={
                "streaming": True,
                "chunk_size": self.chunk_size,
                "total_size": input_data.size_bytes
            }
        )
    
    def _create_stream_generator(self, file_path: str) -> Generator[str, None, None]:
        """Create a generator that streams file content"""
        ext = Path(file_path).suffix.lower()
        
        # Use appropriate streaming method
        yield from self.supported_formats[ext](file_path, full_load=False)
    
    def _stream_text(self, file_path: str, full_load: bool = False) -> str | Generator[str, None, None]:
        """Stream or load text file"""
        
        if full_load:
            # Load entire file
            encoding = self._detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        else:
            # Stream file in chunks
            def generator():
                encoding = self._detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding) as f:
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        yield chunk
            return generator()
    
    def _stream_pdf(self, file_path: str, full_load: bool = False) -> str | Generator[str, None, None]:
        """Stream or load PDF file"""
        
        if not HAS_PDF:
            raise RuntimeError("PyPDF2 not installed - cannot process PDF files")
        
        if full_load:
            # Load entire PDF
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            return '\n'.join(text)
        else:
            # Stream PDF page by page
            def generator():
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        yield page.extract_text() + '\n'
            return generator()
    
    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        if HAS_CHARDET:
            with open(file_path, 'rb') as f:
                raw = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw)
                return result['encoding'] or 'utf-8'
        else:
            # Fallback to utf-8 if chardet not available
            return 'utf-8'
    
    def stream_chunks(self, reference: DataReference, chunk_size: int = None) -> Iterator[str]:
        """
        Stream file content in chunks from a DataReference.
        This is used by downstream tools to process the stream.
        """
        if reference.strategy != ProcessingStrategy.STREAMING:
            raise ValueError("Reference is not configured for streaming")
        
        chunk_size = chunk_size or self.chunk_size
        buffer = ""
        
        for content in reference.stream_generator:
            buffer += content
            
            # Yield complete chunks
            while len(buffer) >= chunk_size:
                yield buffer[:chunk_size]
                buffer = buffer[chunk_size:]
        
        # Yield remaining buffer
        if buffer:
            yield buffer


# Example usage
if __name__ == "__main__":
    loader = StreamingFileLoader()
    
    # Test with a small file
    small_file = DataSchema.FileData(
        path="/tmp/test.txt",
        size_bytes=1000,
        mime_type="text/plain"
    )
    
    # Create test file
    with open("/tmp/test.txt", "w") as f:
        f.write("This is a test file.\n" * 50)
    
    result = loader.process(small_file)
    if result.success:
        print(f"✅ Loaded small file: {result.data.char_count} chars")
    
    # For large files, it would return a DataReference:
    # large_file = DataSchema.FileData(path="/tmp/large.txt", size_bytes=50*1024*1024)
    # result = loader.process(large_file)
    # if result.success and isinstance(result.data, DataReference):
    #     for chunk in loader.stream_chunks(result.data):
    #         process_chunk(chunk)  # Process each chunk without loading entire file