"""
Tool Compatibility Patches
Fixes interface mismatches between tools
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class PatchedToolRequest:
    """ToolRequest with parameters property for backward compatibility"""
    input_data: Any
    theory_schema: Optional[Any] = None
    concept_library: Optional[Any] = None
    options: Dict[str, Any] = field(default_factory=dict)
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def parameters(self):
        """Alias for options to fix tool compatibility"""
        return self.options