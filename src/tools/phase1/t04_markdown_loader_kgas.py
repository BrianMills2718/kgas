"""T04 Markdown Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import re
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.meta import MetaExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.codehilite import CodeHiliteExtension

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T04MarkdownLoaderKGAS(KGASTool):
    """Markdown file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T04", tool_name="Markdown Document Loader")
        self.service_manager = service_manager
        self.description = "Loads and parses Markdown documents with structure preservation"
        self.category = "document_loader"
        self.version = "1.0.0"
        
        # Initialize markdown parser with extensions
        self.md = markdown.Markdown(extensions=[
            'meta',
            'toc',
            'tables',
            'codehilite',
            'fenced_code',
            'nl2br',
            'sane_lists',
            'smarty',
            'admonition'
        ])
        
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
            
            # Validate file extension
            if path.suffix.lower() not in ['.md', '.markdown', '.mkd', '.mdown']:
                return self.create_error_result(
                    request, f"Invalid file type: {path.suffix}", 
                    f"Only .md, .markdown, .mkd, .mdown files are supported"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={"workflow_id": request.workflow_id}
            )
            
            # Read markdown content
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Parse markdown
            html = self.md.convert(content)
            
            # Extract metadata
            metadata = getattr(self.md, 'Meta', {})
            
            # Extract structure
            structure = self._extract_structure(content, html)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                content=content,
                structure=structure,
                metadata=metadata
            )
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded {len(content)} characters from {path.name}"],
                success=True
            )
            
            # Return standardized result
            return ToolResult(
                status="success",
                data={
                    "content": content,
                    "file_path": str(file_path),
                    "size_bytes": path.stat().st_size,
                    "html": html,
                    "metadata": metadata,
                    "structure": structure,
                    "statistics": {
                        "lines": len(content.splitlines()),
                        "words": len(content.split()),
                        "characters": len(content)
                    }
                },
                confidence=ConfidenceScore(value=confidence, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "file_name": path.name,
                    "file_extension": path.suffix
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
                if path.suffix.lower() not in ['.md', '.markdown', '.mkd', '.mdown']:
                    result.add_error(f"Invalid file type: {path.suffix}. Supported: .md, .markdown, .mkd, .mdown")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to Markdown file"
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
                "html": {"type": "string"},
                "metadata": {"type": "object"},
                "structure": {
                    "type": "object",
                    "properties": {
                        "headings": {"type": "array"},
                        "links": {"type": "array"},
                        "images": {"type": "array"},
                        "tables": {"type": "array"},
                        "code_blocks": {"type": "array"},
                        "max_heading_level": {"type": "integer"},
                        "has_lists": {"type": "boolean"},
                        "has_blockquotes": {"type": "boolean"},
                        "total_sections": {"type": "integer"}
                    }
                },
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
            "required": ["content", "file_path", "size_bytes", "html", "metadata", "structure", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []
    
    def _extract_structure(self, content: str, html: str) -> Dict[str, Any]:
        """Extract structural elements from markdown."""
        structure = {
            "headings": [],
            "links": [],
            "images": [],
            "tables": [],
            "code_blocks": [],
            "max_heading_level": 0,
            "has_lists": False,
            "has_blockquotes": False,
            "total_sections": 0
        }
        
        # Extract headings
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            structure["headings"].append({
                "level": level,
                "text": text
            })
            structure["max_heading_level"] = max(structure["max_heading_level"], level)
        
        structure["total_sections"] = len(structure["headings"])
        
        # Extract links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            structure["links"].append({
                "text": match.group(1),
                "url": match.group(2)
            })
        
        # Extract images
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        for match in re.finditer(image_pattern, content):
            structure["images"].append({
                "alt": match.group(1),
                "url": match.group(2)
            })
        
        # Detect tables (simple check)
        if '|' in content and re.search(r'\|[^|]+\|', content):
            # Count table rows
            table_rows = len(re.findall(r'^\|.*\|$', content, re.MULTILINE))
            if table_rows > 0:
                structure["tables"].append({
                    "rows": table_rows
                })
        
        # Extract code blocks
        code_block_pattern = r'```([^\n]*)\n(.*?)```'
        for match in re.finditer(code_block_pattern, content, re.DOTALL):
            language = match.group(1).strip() or "plain"
            code = match.group(2).strip()
            structure["code_blocks"].append({
                "language": language,
                "lines": len(code.splitlines())
            })
        
        # Detect lists
        if re.search(r'^[\*\-\+]\s+', content, re.MULTILINE) or re.search(r'^\d+\.\s+', content, re.MULTILINE):
            structure["has_lists"] = True
        
        # Detect blockquotes
        if re.search(r'^>\s+', content, re.MULTILINE):
            structure["has_blockquotes"] = True
        
        return structure
    
    def _calculate_confidence(self, content: str, structure: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate confidence score for markdown document."""
        base_confidence = 0.95  # High confidence for markdown parsing
        
        # Factors that affect confidence
        factors = []
        
        # Content length factor
        if len(content) > 1000:
            factors.append(0.95)
        elif len(content) > 100:
            factors.append(0.85)
        else:
            factors.append(0.6)
        
        # Structure richness factor
        structure_elements = (
            len(structure["headings"]) +
            len(structure["links"]) +
            len(structure["images"]) +
            len(structure["tables"]) +
            len(structure["code_blocks"])
        )
        if structure_elements > 10:
            factors.append(0.95)
        elif structure_elements > 3:
            factors.append(0.9)
        else:
            factors.append(0.8)
        
        # Metadata factor
        if metadata:
            factors.append(0.95)
        else:
            factors.append(0.9)
        
        # Calculate average factor
        if factors:
            avg_factor = sum(factors) / len(factors)
            confidence = base_confidence * avg_factor
        else:
            confidence = base_confidence
        
        return min(1.0, max(0.0, confidence))