#!/usr/bin/env python3
"""
Composition Service - Bridge between framework and production tools
CRITICAL: This is the convergence point for all tool systems
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tool_compatability" / "poc"))

from framework import ToolFramework, ExtensibleTool
from src.core.tool_contract import get_tool_registry
from src.core.service_manager import ServiceManager
from src.analytics.cross_modal_orchestrator import CrossModalOrchestrator


class CompositionService:
    """Single source of truth for tool composition"""
    
    def __init__(self, service_manager: ServiceManager = None):
        """Initialize with both framework and production systems"""
        self.service_manager = service_manager or ServiceManager()
        self.framework = ToolFramework()
        self.production_registry = get_tool_registry()
        self.orchestrator = CrossModalOrchestrator(service_manager)
        self.adapter_factory = None  # Will create in Task 1.2
        
        # Metrics for thesis evidence
        self.composition_metrics = {
            'chains_discovered': 0,
            'tools_adapted': 0,
            'execution_time': [],
            'overhead_percentage': []
        }
        
    def register_any_tool(self, tool: Any) -> bool:
        """
        Register ANY tool regardless of interface
        Returns True if successful
        """
        try:
            # Will implement with adapter factory
            if not self.adapter_factory:
                raise NotImplementedError("Adapter factory not yet created")
                
            adapted = self.adapter_factory.wrap(tool)
            self.framework.register_tool(adapted)
            
            self.composition_metrics['tools_adapted'] += 1
            return True
            
        except Exception as e:
            print(f"❌ Failed to register {tool}: {e}")
            return False
            
    def discover_chains(self, input_type: str, output_type: str) -> List[List[str]]:
        """
        Discover all possible chains from both systems
        """
        # Get chains from framework
        framework_chains = self.framework.find_chains(input_type, output_type)
        
        # TODO: Also query production registry
        
        self.composition_metrics['chains_discovered'] += len(framework_chains)
        return framework_chains
        
    def execute_chain(self, chain: List[str], input_data: Any) -> Any:
        """
        Execute a discovered chain with performance tracking
        """
        start_time = time.time()
        
        # Will implement execution logic
        result = None  # Placeholder
        
        execution_time = time.time() - start_time
        self.composition_metrics['execution_time'].append(execution_time)
        
        return result
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get composition metrics for thesis evidence"""
        return self.composition_metrics