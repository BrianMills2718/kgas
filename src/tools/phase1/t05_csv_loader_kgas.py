"""T05 CSV Loader - Contract-First Implementation"""

from pathlib import Path
from typing import List, Dict, Any
import logging
import pandas as pd
import numpy as np

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class T05CSVLoaderKGAS(KGASTool):
    """CSV file loader implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T05", tool_name="CSV Data Loader")
        self.service_manager = service_manager
        self.description = "Loads and processes structured data from CSV files"
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
            if path.suffix.lower() not in ['.csv', '.tsv']:
                return self.create_error_result(
                    request, f"Invalid file type: {path.suffix}", 
                    f"Only .csv and .tsv files are supported"
                )
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="file_load",
                inputs=[str(file_path)],
                parameters={"workflow_id": request.workflow_id}
            )
            
            # Determine delimiter
            delimiter = '\t' if path.suffix.lower() == '.tsv' else ','
            
            # Load CSV data with pandas
            try:
                # Try multiple encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                df = None
                used_encoding = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(path, delimiter=delimiter, encoding=encoding)
                        used_encoding = encoding
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    return self.create_error_result(
                        request, "Unable to decode CSV file", 
                        f"Tried encodings: {encodings}"
                    )
                    
            except pd.errors.ParserError as e:
                return self.create_error_result(
                    request, f"CSV parsing error: {str(e)}", 
                    f"Failed to parse CSV: {str(e)}"
                )
            except Exception as e:
                return self.create_error_result(
                    request, f"Failed to load CSV: {str(e)}", 
                    f"Error loading CSV file: {str(e)}"
                )
            
            # Extract data and metadata
            rows, columns = df.shape
            column_names = df.columns.tolist()
            
            # Determine column types
            column_types = {}
            for col in column_names:
                dtype = str(df[col].dtype)
                if 'int' in dtype:
                    column_types[col] = 'integer'
                elif 'float' in dtype:
                    column_types[col] = 'float'
                elif 'object' in dtype:
                    column_types[col] = 'string'
                elif 'datetime' in dtype:
                    column_types[col] = 'datetime'
                elif 'bool' in dtype:
                    column_types[col] = 'boolean'
                else:
                    column_types[col] = 'unknown'
            
            # Calculate missing values
            missing_values = {}
            for col in column_names:
                missing_count = df[col].isna().sum()
                missing_values[col] = {
                    "count": int(missing_count),
                    "percentage": float(missing_count / rows * 100) if rows > 0 else 0.0
                }
            
            # Convert data to list of dicts (first 1000 rows for preview)
            preview_rows = min(1000, rows)
            data_preview = df.head(preview_rows).replace({np.nan: None}).to_dict('records')
            
            # Calculate data quality metrics
            data_quality = self._calculate_data_quality(df, missing_values)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                rows=rows,
                columns=columns,
                data_quality=data_quality
            )
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"Loaded CSV with {rows} rows and {columns} columns"],
                success=True
            )
            
            # Return standardized result
            return ToolResult(
                status="success",
                data={
                    "file_path": str(file_path),
                    "size_bytes": path.stat().st_size,
                    "encoding": used_encoding,
                    "rows": rows,
                    "columns": columns,
                    "column_names": column_names,
                    "column_types": column_types,
                    "missing_values": missing_values,
                    "data_quality": data_quality,
                    "data_preview": data_preview,
                    "preview_rows": preview_rows,
                    "statistics": {
                        "total_cells": rows * columns,
                        "missing_cells": sum(mv["count"] for mv in missing_values.values()),
                        "completeness": data_quality["completeness"]
                    }
                },
                confidence=ConfidenceScore(value=confidence, evidence_weight=10),
                metadata={
                    "tool_version": self.version,
                    "file_name": path.name,
                    "file_extension": path.suffix,
                    "delimiter": delimiter
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
                if path.suffix.lower() not in ['.csv', '.tsv']:
                    result.add_error(f"Invalid file type: {path.suffix}. Supported: .csv, .tsv")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string", 
                    "description": "Path to CSV or TSV file"
                }
            },
            "required": ["file_path"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "size_bytes": {"type": "integer"},
                "encoding": {"type": "string"},
                "rows": {"type": "integer"},
                "columns": {"type": "integer"},
                "column_names": {"type": "array", "items": {"type": "string"}},
                "column_types": {"type": "object"},
                "missing_values": {"type": "object"},
                "data_quality": {"type": "object"},
                "data_preview": {"type": "array"},
                "preview_rows": {"type": "integer"},
                "statistics": {
                    "type": "object",
                    "properties": {
                        "total_cells": {"type": "integer"},
                        "missing_cells": {"type": "integer"},
                        "completeness": {"type": "number"}
                    }
                }
            },
            "required": ["file_path", "size_bytes", "rows", "columns", "column_names", "statistics"]
        }
    
    def get_theory_compatibility(self) -> List[str]:
        """No theory compatibility for basic loader."""
        return []
    
    def _calculate_data_quality(self, df: pd.DataFrame, missing_values: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        rows, columns = df.shape
        total_cells = rows * columns
        missing_cells = sum(mv["count"] for mv in missing_values.values())
        
        # Completeness score
        completeness = (total_cells - missing_cells) / total_cells if total_cells > 0 else 0.0
        
        # Uniqueness scores for each column
        uniqueness = {}
        for col in df.columns:
            unique_count = df[col].nunique()
            uniqueness[col] = unique_count / rows if rows > 0 else 0.0
        
        # Consistency checks
        consistency_issues = []
        
        # Check for mixed types in string columns
        for col in df.columns:
            if df[col].dtype == 'object':  # String column
                # Check if it contains mixed numeric/string values
                numeric_count = 0
                string_count = 0
                for val in df[col].dropna().head(100):  # Sample first 100 non-null values
                    try:
                        float(val)
                        numeric_count += 1
                    except (ValueError, TypeError):
                        string_count += 1
                
                if numeric_count > 0 and string_count > 0:
                    consistency_issues.append({
                        "column": col,
                        "issue": "mixed_types",
                        "details": f"Contains both numeric ({numeric_count}) and string ({string_count}) values"
                    })
        
        return {
            "completeness": completeness,
            "missing_percentage": (missing_cells / total_cells * 100) if total_cells > 0 else 0.0,
            "uniqueness_scores": uniqueness,
            "consistency_issues": consistency_issues,
            "has_duplicates": df.duplicated().any(),
            "duplicate_rows": int(df.duplicated().sum())
        }
    
    def _calculate_confidence(self, rows: int, columns: int, data_quality: Dict[str, Any]) -> float:
        """Calculate confidence score for CSV data."""
        base_confidence = 0.95  # High confidence for structured data
        
        # Factors that affect confidence
        factors = []
        
        # Data size factor
        if rows > 100:
            factors.append(0.95)
        elif rows > 10:
            factors.append(0.85)
        else:
            factors.append(0.7)
        
        # Completeness factor
        completeness = data_quality["completeness"]
        if completeness > 0.95:
            factors.append(0.95)
        elif completeness > 0.8:
            factors.append(0.85)
        else:
            factors.append(0.7)
        
        # Consistency factor
        if len(data_quality["consistency_issues"]) == 0:
            factors.append(0.95)
        elif len(data_quality["consistency_issues"]) < 3:
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