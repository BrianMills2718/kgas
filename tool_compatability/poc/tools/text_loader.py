"""
TextLoader Tool - Loads text from files

This tool reads text files from disk and converts them to the standard
TextData format for processing by other tools.
"""

from pathlib import Path
from typing import Type, Optional
from pydantic import BaseModel, Field
import chardet
import logging

from ..base_tool import BaseTool
from ..data_types import DataType, DataSchema


class TextLoaderConfig(BaseModel):
    """Configuration for TextLoader"""
    max_size_mb: float = Field(default=10.0, description="Maximum file size in MB")
    encoding: Optional[str] = Field(default=None, description="Text encoding (auto-detect if None)")
    fallback_encoding: str = Field(default="utf-8", description="Fallback encoding if detection fails")
    
    class Config:
        schema_extra = {
            "example": {
                "max_size_mb": 10.0,
                "encoding": None,
                "fallback_encoding": "utf-8"
            }
        }


class TextLoader(BaseTool[DataSchema.FileData, DataSchema.TextData, TextLoaderConfig]):
    """
    Loads text content from files.
    
    This tool:
    - Reads files from disk
    - Auto-detects encoding if not specified
    - Validates file size limits
    - Converts to standard TextData format
    """
    
    __version__ = "1.0.0"
    
    # ========== Type Definitions ==========
    
    @property
    def input_type(self) -> DataType:
        return DataType.FILE
    
    @property
    def output_type(self) -> DataType:
        return DataType.TEXT
    
    @property
    def input_schema(self) -> Type[DataSchema.FileData]:
        return DataSchema.FileData
    
    @property
    def output_schema(self) -> Type[DataSchema.TextData]:
        return DataSchema.TextData
    
    @property
    def config_schema(self) -> Type[TextLoaderConfig]:
        return TextLoaderConfig
    
    def default_config(self) -> TextLoaderConfig:
        return TextLoaderConfig()
    
    # ========== Core Implementation ==========
    
    def _detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding name
        """
        try:
            with open(file_path, 'rb') as f:
                # Read first 10KB for detection
                raw_data = f.read(10240)
                if not raw_data:
                    return self.config.fallback_encoding
                
                result = chardet.detect(raw_data)
                encoding = result.get('encoding')
                confidence = result.get('confidence', 0)
                
                if encoding and confidence > 0.7:
                    self.logger.info(f"Detected encoding: {encoding} "
                                   f"(confidence: {confidence:.2f})")
                    return encoding
                else:
                    self.logger.warning(f"Low confidence encoding detection: "
                                      f"{encoding} ({confidence:.2f}), "
                                      f"using fallback: {self.config.fallback_encoding}")
                    return self.config.fallback_encoding
                    
        except Exception as e:
            self.logger.error(f"Encoding detection failed: {e}")
            return self.config.fallback_encoding
    
    def _execute(self, input_data: DataSchema.FileData) -> DataSchema.TextData:
        """
        Load text from file.
        
        Args:
            input_data: File reference with metadata
            
        Returns:
            TextData with file contents
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too large or can't be read
        """
        path = Path(input_data.path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        # Check file size
        size_mb = input_data.size_bytes / (1024 * 1024)
        if size_mb > self.config.max_size_mb:
            raise ValueError(
                f"File too large: {size_mb:.1f}MB "
                f"(max: {self.config.max_size_mb}MB)"
            )
        
        # Determine encoding
        if self.config.encoding:
            encoding = self.config.encoding
            self.logger.info(f"Using configured encoding: {encoding}")
        elif input_data.encoding:
            encoding = input_data.encoding
            self.logger.info(f"Using file-specified encoding: {encoding}")
        else:
            encoding = self._detect_encoding(path)
        
        # Read file
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError as e:
            # Try fallback encoding
            self.logger.warning(f"Failed to read with {encoding}, "
                              f"trying fallback: {self.config.fallback_encoding}")
            try:
                with open(path, 'r', encoding=self.config.fallback_encoding) as f:
                    content = f.read()
            except Exception as e2:
                raise ValueError(f"Failed to read file with any encoding: {e2}")
        except Exception as e:
            raise ValueError(f"Failed to read file: {e}")
        
        # Create metadata
        metadata = {
            "source_file": str(path),
            "encoding_used": encoding,
            "file_size_bytes": input_data.size_bytes,
            "mime_type": input_data.mime_type
        }
        
        # Create and return TextData
        return DataSchema.TextData.from_string(content, metadata)
    
    # ========== Utility Methods ==========
    
    @classmethod
    def load_file(cls, file_path: str, **config_kwargs) -> DataSchema.TextData:
        """
        Convenience method to load a file directly.
        
        Args:
            file_path: Path to file
            **config_kwargs: Configuration overrides
            
        Returns:
            TextData with file contents
        """
        # Get file info
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        size_bytes = path.stat().st_size
        
        # Guess MIME type
        suffix = path.suffix.lower()
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.csv': 'text/csv'
        }
        mime_type = mime_types.get(suffix, 'text/plain')
        
        # Create file data
        file_data = DataSchema.FileData(
            path=str(path.absolute()),
            size_bytes=size_bytes,
            mime_type=mime_type
        )
        
        # Create loader with config
        config = TextLoaderConfig(**config_kwargs)
        loader = cls(config)
        
        # Process and return
        result = loader.process(file_data)
        if result.success:
            return result.data
        else:
            raise RuntimeError(f"Failed to load file: {result.error}")