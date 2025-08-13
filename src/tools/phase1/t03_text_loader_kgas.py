"""T03 Text Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any
import logging

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult, ConfidenceScore
)
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T03TextLoaderKGAS(KGASTool):
    """Text file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T03", tool_name="Text File Loader")
        self.service_manager = service_manager
        self.description = "Loads text files with encoding detection"
        self.category = "document_loader"
        self.version = "1.0.0"
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute text loading with contract interface."""
        try:
            # Extract file path from request
            file_path = request.input_data.get("file_path")
            if not file_path:
                return self.create_error_result(
                    request, "Missing required field: file_path", "Missing required field: file_path"
                )
            
            # Optional encoding parameter
            encoding = request.input_data.get("encoding", "utf-8")
            
            # Load file
            path = Path(file_path)
            if not path.exists():
                return self.create_error_result(
                    request, f"File not found: {file_path}", f"File not found: {file_path}"
                )
            
            if not path.is_file():
                return self.create_error_result(
                    request, f"Path is not a file: {file_path}", f"Path is not a file: {file_path}"
                )
            
            # Read file content
            try:
                content = path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                # Try with different encodings
                for alt_encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                    try:
                        content = path.read_text(encoding=alt_encoding)
                        encoding = alt_encoding
                        logger.info(f"Successfully read file with {alt_encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    return self.create_error_result(
                        request, "Unable to decode file with any supported encoding", "Unable to decode file with any supported encoding"
                    )
            
            # Track with provenance (using real methods)
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={
                    "encoding": encoding,
                    "workflow_id": request.workflow_id
                }
            )
            
            # Calculate statistics
            lines = content.splitlines()
            words = content.split()
            
            # Create result data
            result_data = {
                "content": content,
                "file_path": str(file_path),
                "size_bytes": len(content.encode(encoding)),
                "encoding": encoding,
                "statistics": {
                    "lines": len(lines),
                    "words": len(words),
                    "characters": len(content)
                }
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded {len(content)} characters from {path.name}"],
                success=True
            )
            
            # Return success result
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=1.0, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "file_name": path.name,
                    "file_extension": path.suffix
                },
                provenance=op_id,
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in T03 text loader: {e}", exc_info=True)
            return self.create_error_result(request, str(e), str(e))
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input has required file_path."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
            
        if "file_path" not in input_data:
            result.add_error("Missing required field: file_path")
        else:
            file_path = input_data.get("file_path")
            if not isinstance(file_path, str):
                result.add_error("file_path must be a string")
            elif not file_path.strip():
                result.add_error("file_path cannot be empty")
        
        # Optional encoding validation
        if "encoding" in input_data:
            encoding = input_data.get("encoding")
            if not isinstance(encoding, str):
                result.add_error("encoding must be a string")
            
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to text file"
                },
                "encoding": {
                    "type": "string",
                    "description": "Text encoding (default: utf-8)",
                    "default": "utf-8"
                }
            },
            "required": ["file_path"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "file_path": {"type": "string"},
                "size_bytes": {"type": "integer"},
                "encoding": {"type": "string"},
                "statistics": {
                    "type": "object",
                    "properties": {
                        "lines": {"type": "integer"},
                        "words": {"type": "integer"},
                        "characters": {"type": "integer"}
                    },
                    "required": ["lines", "words", "characters"]
                }
            },
            "required": ["content", "file_path", "size_bytes", "encoding", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []