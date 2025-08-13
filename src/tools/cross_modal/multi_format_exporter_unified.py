"""
Multi Format Exporter Unified Tool - Exports data to multiple formats
"""

import logging
from typing import Dict, Any
from .multi_format_exporter import MultiFormatExporter as MultiFormatExporterImpl
from src.tools.base_tool import BaseTool
from src.core.service_manager import ServiceManager

logger = logging.getLogger(__name__)


class MultiFormatExporterUnified(BaseTool):
    """
    Unified interface for Multi Format Exporter.
    Exports data to various formats like JSON, CSV, XML, etc.
    """
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize Multi Format Exporter with unified interface"""
        if service_manager is None:
            service_manager = ServiceManager()
        super().__init__(service_manager)
        
        # Set standardized tool ID
        self.tool_id = "MULTI_FORMAT_EXPORTER"
        self.tool_name = "Multi Format Exporter"
        
        # Initialize the implementation
        self.exporter = MultiFormatExporterImpl()
        
        logger.info("Multi Format Exporter initialized with unified interface")
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data export to specified format"""
        try:
            # Extract parameters
            data = request.get("data", {})
            format_type = request.get("format", "json")
            options = request.get("options", {})
            
            # Export based on format type
            if format_type == "json":
                result = self.exporter.export_json(data, **options)
            elif format_type == "csv":
                result = self.exporter.export_csv(data, **options)
            elif format_type == "xml":
                result = self.exporter.export_xml(data, **options)
            elif format_type == "yaml":
                result = self.exporter.export_yaml(data, **options)
            elif format_type == "markdown":
                result = self.exporter.export_markdown(data, **options)
            else:
                result = self.exporter.export_default(data, format_type, **options)
            
            return {
                "status": "success",
                "data": result,
                "metadata": {
                    "tool_id": self.tool_id,
                    "format": format_type,
                    "options": options
                }
            }
        except Exception as e:
            logger.error(f"Multi format export failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "metadata": {"tool_id": self.tool_id}
            }
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data"""
        if not isinstance(input_data, dict):
            return False
        if "data" not in input_data:
            return False
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Check tool health"""
        return {
            "status": "success",
            "healthy": True,
            "tool_id": self.tool_id,
            "metadata": {
                "exporter_available": self.exporter is not None,
                "supported_formats": ["json", "csv", "xml", "yaml", "markdown"]
            }
        }
    
    def get_status(self) -> str:
        """Get tool status"""
        return "ready"
    
    def get_contract(self) -> Dict[str, Any]:
        """Get tool contract"""
        return {
            "tool_id": self.tool_id,
            "name": self.tool_name,
            "description": "Export data to multiple formats",
            "category": "cross_modal",  # Required parameter for ToolContract
            "input_schema": {
                "type": "object",
                "properties": {
                    "data": {"type": "object"},
                    "format": {"type": "string", "enum": ["json", "csv", "xml", "yaml", "markdown"]},
                    "options": {"type": "object"}
                },
                "required": ["data"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "exported_data": {"type": "string"},
                    "metadata": {"type": "object"}
                }
            },
            "dependencies": [],
            "performance_requirements": {
                "max_execution_time": 15.0,
                "max_memory_mb": 300
            }
        }