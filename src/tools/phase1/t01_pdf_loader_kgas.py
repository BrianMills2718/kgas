"""T01 PDF Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import pypdf

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T01PDFLoaderKGAS(KGASTool):
    """PDF file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T01", tool_name="PDF Document Loader")
        self.service_manager = service_manager
        self.description = "Loads and extracts text from PDF documents"
        self.category = "document_loader"
        self.version = "1.0.0"
        
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute file loading with contract interface."""
        try:
            # Extract and validate file path
            file_path = request.input_data.get("file_path")
            path = Path(file_path)
            
            if not path.exists():
                return self.create_error_result(
                    request, f"File not found: {file_path}", 
                    f"File not found: {file_path}"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={"workflow_id": request.workflow_id}
            )
            
            # Extract text based on file type
            if path.suffix.lower() == '.pdf':
                extraction_result = self._extract_text_from_pdf(path)
            elif path.suffix.lower() == '.txt':
                extraction_result = self._extract_text_from_txt(path)
            else:
                return self.create_error_result(
                    request, f"Unsupported file type: {path.suffix}", 
                    f"Only .pdf and .txt files are supported"
                )
            
            if extraction_result["status"] != "success":
                return self.create_error_result(
                    request, extraction_result["error"], 
                    extraction_result.get("error_details", extraction_result["error"])
                )
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded {len(extraction_result['text'])} characters from {path.name}"],
                success=True
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                text=extraction_result["text"],
                page_count=extraction_result["page_count"],
                file_size=path.stat().st_size
            )
            
            # Return standardized result
            return ToolResult(
                status="success",
                data={
                    "content": extraction_result["text"],
                    "file_path": str(file_path),
                    "size_bytes": path.stat().st_size,
                    "page_count": extraction_result["page_count"],
                    "statistics": {
                        "lines": len(extraction_result["text"].splitlines()),
                        "words": len(extraction_result["text"].split()),
                        "characters": len(extraction_result["text"])
                    }
                },
                confidence=ConfidenceScore(value=confidence, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "file_name": path.name,
                    "file_extension": path.suffix,
                    "extraction_method": "pypdf" if path.suffix.lower() == '.pdf' else "text"
                },
                provenance=op_id,
                request_id=request.request_id
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
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
            else:
                # Check file extension
                path = Path(file_path)
                if path.suffix.lower() not in ['.pdf', '.txt']:
                    result.add_error(f"Invalid file type: {path.suffix}. Supported: .pdf, .txt")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to PDF or text file"
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
                "page_count": {"type": "integer"},
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
            "required": ["content", "file_path", "size_bytes", "page_count", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []
    
    def _extract_text_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from PDF using pypdf."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Check if encrypted
                if pdf_reader.is_encrypted:
                    return {
                        "status": "error",
                        "error": "PDF is encrypted and cannot be read",
                        "error_details": "The PDF file is password-protected"
                    }
                
                total_pages = len(pdf_reader.pages)
                
                # Extract text from all pages
                text_pages = []
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        text_pages.append(page_text)
                    except Exception as e:
                        # Continue with other pages if one fails
                        logger.warning(f"Failed to extract page {page_num + 1}: {e}")
                        text_pages.append(f"[Error extracting page {page_num + 1}]")
                
                # Combine all pages
                full_text = "\n\n".join(text_pages)
                
                # Basic text cleaning
                cleaned_text = self._clean_extracted_text(full_text)
                
                return {
                    "status": "success",
                    "text": cleaned_text,
                    "page_count": total_pages
                }
                
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return {
                "status": "error",
                "error": f"Failed to extract text from PDF: {str(e)}",
                "error_details": str(e)
            }
    
    def _extract_text_from_txt(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from text file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            text = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if text is None:
                return {
                    "status": "error",
                    "error": "Unable to decode text file with any supported encoding",
                    "error_details": f"Tried encodings: {encodings}"
                }
            
            # Basic text cleaning
            cleaned_text = self._clean_extracted_text(text)
            
            return {
                "status": "success",
                "text": cleaned_text,
                "page_count": 1  # Text files are single "page"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to read text file: {str(e)}",
                "error_details": str(e)
            }
    
    def _clean_extracted_text(self, text: str) -> str:
        """Basic text cleaning for extracted text."""
        if not text:
            return ""
        
        import re
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newlines
        text = re.sub(r'\n\n+', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove empty lines at start and end
        text = text.strip()
        
        return text
    
    def _calculate_confidence(self, text: str, page_count: int, file_size: int) -> float:
        """Calculate confidence score for extracted text."""
        base_confidence = 0.9  # High confidence for direct extraction
        
        # Factors that affect confidence
        factors = []
        
        # Text length factor
        if len(text) > 1000:
            factors.append(0.95)
        elif len(text) > 100:
            factors.append(0.85)
        else:
            factors.append(0.6)
        
        # Page count factor (for PDFs)
        if page_count > 1:
            factors.append(0.95)
        else:
            factors.append(0.9)
        
        # File size factor
        if file_size > 10000:  # > 10KB
            factors.append(0.95)
        elif file_size > 1000:  # > 1KB
            factors.append(0.85)
        else:
            factors.append(0.7)
        
        # Calculate average factor
        if factors:
            avg_factor = sum(factors) / len(factors)
            confidence = base_confidence * avg_factor
        else:
            confidence = base_confidence
        
        return min(1.0, max(0.0, confidence))