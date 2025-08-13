"""T06 JSON Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any, Union
import logging
import json
from collections import deque

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T06JSONLoaderKGAS(KGASTool):
    """JSON file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T06", tool_name="JSON Document Loader")
        self.service_manager = service_manager
        self.description = "Loads and processes JSON documents with structure analysis"
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
            if path.suffix.lower() not in ['.json', '.jsonl', '.ndjson']:
                return self.create_error_result(
                    request, f"Invalid file type: {path.suffix}", 
                    f"Only .json, .jsonl, .ndjson files are supported"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={"workflow_id": request.workflow_id}
            )
            
            # Load JSON data
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    if path.suffix.lower() in ['.jsonl', '.ndjson']:
                        # Handle JSON Lines format
                        data = []
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line:  # Skip empty lines
                                try:
                                    data.append(json.loads(line))
                                except json.JSONDecodeError as e:
                                    return self.create_error_result(
                                        request, f"JSON parsing error at line {line_num}: {str(e)}", 
                                        f"Invalid JSON at line {line_num}: {str(e)}"
                                    )
                        json_type = "json_lines"
                    else:
                        # Regular JSON file
                        data = json.load(f)
                        json_type = self._determine_json_type(data)
                        
            except json.JSONDecodeError as e:
                return self.create_error_result(
                    request, f"JSON parsing error: {str(e)}", 
                    f"Invalid JSON format: {str(e)}"
                )
            except UnicodeDecodeError as e:
                return self.create_error_result(
                    request, f"Encoding error: {str(e)}", 
                    f"File encoding error: {str(e)}"
                )
            except Exception as e:
                return self.create_error_result(
                    request, f"Failed to load JSON: {str(e)}", 
                    f"Error loading JSON file: {str(e)}"
                )
            
            # Extract schema and statistics
            schema = self._extract_schema(data)
            statistics = self._calculate_statistics(data)
            
            # Calculate depth
            depth = self._calculate_depth(data)
            
            # Extract key information based on type
            if json_type == "object":
                key_count = len(data.keys()) if isinstance(data, dict) else 0
                array_length = None
            elif json_type == "array":
                key_count = None
                array_length = len(data) if isinstance(data, list) else 0
            elif json_type == "json_lines":
                key_count = None
                array_length = len(data)
            else:
                key_count = None
                array_length = None
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                data=data,
                json_type=json_type,
                depth=depth,
                statistics=statistics
            )
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded JSON {json_type} with depth {depth}"],
                success=True
            )
            
            # Return standardized result
            return ToolResult(
                status="success",
                data={
                    "data": data,
                    "file_path": str(file_path),
                    "size_bytes": path.stat().st_size,
                    "json_type": json_type,
                    "schema": schema,
                    "key_count": key_count,
                    "array_length": array_length,
                    "depth": depth,
                    "statistics": statistics
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
                if path.suffix.lower() not in ['.json', '.jsonl', '.ndjson']:
                    result.add_error(f"Invalid file type: {path.suffix}. Supported: .json, .jsonl, .ndjson")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to JSON file"
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
                "json_type": {"type": "string"},
                "schema": {"type": "object"},
                "key_count": {"type": ["integer", "null"]},
                "array_length": {"type": ["integer", "null"]},
                "depth": {"type": "integer"},
                "statistics": {"type": "object"}
            },
            "required": ["data", "file_path", "size_bytes", "json_type", "schema", "depth", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []
    
    def _determine_json_type(self, data: Any) -> str:
        """Determine the type of JSON data."""
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
    
    def _extract_schema(self, data: Any, max_depth: int = 10) -> Dict[str, Any]:
        """Extract schema information from JSON data."""
        def extract_type(obj: Any, depth: int = 0) -> Dict[str, Any]:
            if depth > max_depth:
                return {"type": "object", "description": "max depth exceeded"}
            
            if isinstance(obj, dict):
                properties = {}
                for key, value in obj.items():
                    properties[key] = extract_type(value, depth + 1)
                return {
                    "type": "object",
                    "properties": properties
                }
            elif isinstance(obj, list):
                if obj:
                    # Sample first few items for array type
                    item_types = []
                    for item in obj[:5]:  # Sample first 5 items
                        item_type = extract_type(item, depth + 1)
                        if item_type not in item_types:
                            item_types.append(item_type)
                    
                    if len(item_types) == 1:
                        return {
                            "type": "array",
                            "items": item_types[0]
                        }
                    else:
                        return {
                            "type": "array",
                            "items": {"oneOf": item_types}
                        }
                else:
                    return {"type": "array", "items": {}}
            elif isinstance(obj, str):
                return {"type": "string"}
            elif isinstance(obj, bool):
                return {"type": "boolean"}
            elif isinstance(obj, int):
                return {"type": "integer"}
            elif isinstance(obj, float):
                return {"type": "number"}
            elif obj is None:
                return {"type": "null"}
            else:
                return {"type": "unknown"}
        
        return extract_type(data)
    
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
        """Calculate statistics about the JSON data."""
        stats = {
            "total_keys": 0,
            "total_values": 0,
            "unique_keys": set(),
            "value_types": {"string": 0, "number": 0, "boolean": 0, "null": 0, "object": 0, "array": 0},
            "max_array_length": 0,
            "total_arrays": 0,
            "total_objects": 0
        }
        
        def analyze(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                stats["total_objects"] += 1
                for key, value in obj.items():
                    stats["total_keys"] += 1
                    stats["unique_keys"].add(f"{path}.{key}" if path else key)
                    analyze(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                stats["total_arrays"] += 1
                stats["max_array_length"] = max(stats["max_array_length"], len(obj))
                for i, item in enumerate(obj):
                    analyze(item, f"{path}[{i}]")
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
        
        # Convert set to count for JSON serialization
        stats["unique_key_count"] = len(stats["unique_keys"])
        del stats["unique_keys"]  # Remove set as it's not JSON serializable
        
        return stats
    
    def _calculate_confidence(self, data: Any, json_type: str, depth: int, statistics: Dict[str, Any]) -> float:
        """Calculate confidence score for JSON data."""
        base_confidence = 0.95  # High confidence for valid JSON
        
        # Factors that affect confidence
        factors = []
        
        # Data complexity factor
        total_elements = statistics["total_keys"] + statistics["total_values"]
        if total_elements > 100:
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
        if json_type in ["object", "array"]:
            factors.append(0.95)
        else:
            factors.append(0.85)
        
        # Calculate average factor
        if factors:
            avg_factor = sum(factors) / len(factors)
            confidence = base_confidence * avg_factor
        else:
            confidence = base_confidence
        
        return min(1.0, max(0.0, confidence))