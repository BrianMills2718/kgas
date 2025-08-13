"""
Unified tool interface for all KGAS tools.
This MUST be implemented by all tools for agent orchestration.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

class ToolStatus(Enum):
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ToolContract:
    """Tool capability specification"""
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required_services: List[str]
    performance_limits: Dict[str, Any]

class UnifiedToolInterface(ABC):
    """Base interface all tools MUST implement"""
    
    @abstractmethod
    def get_contract(self) -> ToolContract:
        """Return tool's contract specification"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input against contract"""
        pass
    
    @abstractmethod
    def execute(self, request: 'ToolRequest') -> 'ToolResult':
        """Execute tool operation"""
        pass
    
    @abstractmethod
    def get_status(self) -> ToolStatus:
        """Get current tool status"""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check tool health"""
        pass