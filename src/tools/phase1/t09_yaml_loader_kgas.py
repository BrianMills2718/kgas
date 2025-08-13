"""T09 YAML Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any, Union
import logging
import yaml

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T09YAMLLoaderKGAS(KGASTool):
    """YAML file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T09", tool_name="YAML Document Loader")
        self.service_manager = service_manager
        self.description = "Loads and parses YAML documents with structure analysis"
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
            
            # Validate file extension
            if path.suffix.lower() not in ['.yaml', '.yml']:
                return self.create_error_result(
                    request, f"Invalid file type: {path.suffix}", 
                    f"Only .yaml and .yml files are supported"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={"workflow_id": request.workflow_id}
            )
            
            # Load YAML data
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse YAML - could be single or multi-document
                documents = list(yaml.safe_load_all(content))
                
                if len(documents) == 1:
                    # Single document YAML
                    data = documents[0]
                    is_multi_doc = False
                else:
                    # Multi-document YAML
                    data = documents
                    is_multi_doc = True
                    
            except yaml.YAMLError as e:
                return self.create_error_result(
                    request, f"YAML parsing error: {str(e)}", 
                    f"Invalid YAML format: {str(e)}"
                )
            except UnicodeDecodeError as e:
                return self.create_error_result(
                    request, f"Encoding error: {str(e)}", 
                    f"File encoding error: {str(e)}"
                )
            except Exception as e:
                return self.create_error_result(
                    request, f"Failed to load YAML: {str(e)}", 
                    f"Error loading YAML file: {str(e)}"
                )
            
            # Determine structure and statistics
            if is_multi_doc:
                yaml_type = "multi_document"
                structure = self._analyze_multi_doc_structure(data)
                statistics = self._calculate_multi_doc_statistics(data)
                # Handle case where all documents are None
                non_none_docs = [doc for doc in data if doc is not None]
                if non_none_docs:
                    depth = max(self._calculate_depth(doc) for doc in non_none_docs)
                else:
                    depth = 1
            else:
                yaml_type = self._determine_yaml_type(data)
                structure = self._extract_structure(data)
                statistics = self._calculate_statistics(data)
                depth = self._calculate_depth(data)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                data=data,
                yaml_type=yaml_type,
                depth=depth,
                statistics=statistics,
                is_multi_doc=is_multi_doc
            )
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded YAML {yaml_type} with depth {depth}"],
                success=True
            )
            
            # Return standardized result
            return ToolResult(
                status="success",
                data={
                    "data": data,
                    "file_path": str(file_path),
                    "size_bytes": path.stat().st_size,
                    "yaml_type": yaml_type,
                    "is_multi_document": is_multi_doc,
                    "document_count": len(documents) if is_multi_doc else 1,
                    "structure": structure,
                    "depth": depth,
                    "statistics": statistics,
                    "text_content": content  # Original YAML text
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
                if path.suffix.lower() not in ['.yaml', '.yml']:
                    result.add_error(f"Invalid file type: {path.suffix}. Supported: .yaml, .yml")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to YAML file"
                }
            },
            "required": ["file_path"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "data": {"type": ["object", "array", "string", "number", "boolean", "null"]},
                "file_path": {"type": "string"},
                "size_bytes": {"type": "integer"},
                "yaml_type": {"type": "string"},
                "is_multi_document": {"type": "boolean"},
                "document_count": {"type": "integer"},
                "structure": {"type": "object"},
                "depth": {"type": "integer"},
                "statistics": {"type": "object"},
                "text_content": {"type": "string"}
            },
            "required": ["data", "file_path", "size_bytes", "yaml_type", "structure", "depth", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []
    
    def _determine_yaml_type(self, data: Any) -> str:
        """Determine the type of YAML data."""
        if isinstance(data, dict):
            return "object"
        elif isinstance(data, list):
            return "array"
        elif isinstance(data, str):
            return "string"
        elif isinstance(data, (int, float)):
            return "number"
        elif isinstance(data, bool):
            return "boolean"
        elif data is None:
            return "null"
        else:
            return "unknown"
    
    def _extract_structure(self, data: Any) -> Dict[str, Any]:
        """Extract structure information from YAML data."""
        if isinstance(data, dict):
            return {
                "type": "object",
                "key_count": len(data.keys()),
                "keys": list(data.keys())[:20],  # First 20 keys
                "has_nested_objects": any(isinstance(v, dict) for v in data.values()),
                "has_lists": any(isinstance(v, list) for v in data.values())
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "element_types": list(set(type(item).__name__ for item in data[:10]))
            }
        else:
            return {
                "type": self._determine_yaml_type(data),
                "value_type": type(data).__name__
            }
    
    def _analyze_multi_doc_structure(self, documents: List[Any]) -> Dict[str, Any]:
        """Analyze structure of multi-document YAML."""
        doc_structures = []
        for i, doc in enumerate(documents):
            if doc is not None:
                doc_structures.append({
                    f"document_{i}": self._extract_structure(doc)
                })
        
        return {
            "type": "multi_document",
            "document_count": len(documents),
            "documents": doc_structures[:5]  # First 5 documents
        }
    
    def _calculate_depth(self, data: Any) -> int:
        """Calculate the maximum depth of nested structures."""
        def get_depth(obj: Any, current_depth: int = 1) -> int:
            if isinstance(obj, dict):
                if not obj:
                    return current_depth
                return max(get_depth(v, current_depth + 1) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return current_depth
                return max(get_depth(item, current_depth + 1) for item in obj)
            else:
                return current_depth
        
        return get_depth(data)
    
    def _calculate_statistics(self, data: Any) -> Dict[str, Any]:
        """Calculate statistics about the YAML data."""
        stats = {
            "total_keys": 0,
            "total_values": 0,
            "value_types": {"string": 0, "number": 0, "boolean": 0, "null": 0, "object": 0, "array": 0},
            "max_array_length": 0,
            "total_arrays": 0,
            "total_objects": 0
        }
        
        def analyze(obj: Any):
            if isinstance(obj, dict):
                stats["total_objects"] += 1
                stats["total_keys"] += len(obj)
                for value in obj.values():
                    analyze(value)
            elif isinstance(obj, list):
                stats["total_arrays"] += 1
                stats["max_array_length"] = max(stats["max_array_length"], len(obj))
                for item in obj:
                    analyze(item)
            else:
                stats["total_values"] += 1
                if isinstance(obj, str):
                    stats["value_types"]["string"] += 1
                elif isinstance(obj, (int, float)):
                    stats["value_types"]["number"] += 1
                elif isinstance(obj, bool):
                    stats["value_types"]["boolean"] += 1
                elif obj is None:
                    stats["value_types"]["null"] += 1
        
        analyze(data)
        return stats
    
    def _calculate_multi_doc_statistics(self, documents: List[Any]) -> Dict[str, Any]:
        """Calculate statistics for multi-document YAML."""
        combined_stats = {
            "total_documents": len(documents),
            "non_null_documents": sum(1 for doc in documents if doc is not None),
            "document_types": {},
            "total_keys": 0,
            "total_values": 0,
            "total_objects": 0,
            "total_arrays": 0
        }
        
        for doc in documents:
            if doc is not None:
                doc_type = self._determine_yaml_type(doc)
                combined_stats["document_types"][doc_type] = combined_stats["document_types"].get(doc_type, 0) + 1
                
                # Aggregate statistics
                doc_stats = self._calculate_statistics(doc)
                combined_stats["total_keys"] += doc_stats["total_keys"]
                combined_stats["total_values"] += doc_stats["total_values"]
                combined_stats["total_objects"] += doc_stats["total_objects"]
                combined_stats["total_arrays"] += doc_stats["total_arrays"]
        
        return combined_stats
    
    def _calculate_confidence(self, data: Any, yaml_type: str, depth: int, 
                            statistics: Dict[str, Any], is_multi_doc: bool) -> float:
        """Calculate confidence score for YAML data."""
        base_confidence = 0.95  # High confidence for valid YAML
        
        # Factors that affect confidence
        factors = []
        
        # Data complexity factor
        if is_multi_doc:
            total_elements = statistics.get("total_keys", 0) + statistics.get("total_values", 0)
        else:
            total_elements = statistics["total_keys"] + statistics["total_values"]
            
        if total_elements > 50:
            factors.append(0.95)
        elif total_elements > 10:
            factors.append(0.90)
        else:
            factors.append(0.80)
        
        # Depth factor
        if depth <= 3:
            factors.append(0.95)
        elif depth <= 5:
            factors.append(0.90)
        else:
            factors.append(0.85)
        
        # Structure regularity factor
        if yaml_type in ["object", "array", "multi_document"]:
            factors.append(0.95)
        else:
            factors.append(0.85)
        
        # Multi-document penalty (slightly more complex)
        if is_multi_doc:
            factors.append(0.90)
        
        # Calculate average factor
        if factors:
            avg_factor = sum(factors) / len(factors)
            confidence = base_confidence * avg_factor
        else:
            confidence = base_confidence
        
        return min(1.0, max(0.0, confidence))