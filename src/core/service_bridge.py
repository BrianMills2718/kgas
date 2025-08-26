#!/usr/bin/env python3
"""
Bridge to connect critical services to framework
"""

import time
from typing import Dict, Any, Optional
from src.core.provenance_service import ProvenanceService
from src.core.service_manager import ServiceManager

class ServiceBridge:
    """Connects framework to critical services"""
    
    def __init__(self, service_manager: ServiceManager = None):
        self.service_manager = service_manager or ServiceManager()
        self._services = {}
        
    def get_provenance_service(self) -> ProvenanceService:
        """Get or create provenance service"""
        if 'provenance' not in self._services:
            self._services['provenance'] = ProvenanceService()
        return self._services['provenance']
    
    def track_execution(self, tool_id: str, input_data: Any, output_data: Any) -> Dict:
        """Track tool execution in provenance"""
        provenance = self.get_provenance_service()
        
        # Use ProvenanceService's actual interface
        if output_data is None:
            # Starting an operation
            op_id = provenance.start_operation(
                operation_type='tool_execution',
                agent_details={'tool_id': tool_id, 'framework': 'composition_service'},
                used={
                    'input_type': type(input_data).__name__,
                    'input_hash': str(hash(str(input_data)))[:8]
                },
                parameters={'tool': tool_id}
            )
            return {'operation_id': op_id, 'status': 'started'}
        else:
            # Completing an operation (simplified - normally would use the op_id from start)
            input_hash = str(hash(str(input_data)))[:8]
            output_hash = str(hash(str(output_data)))[:8]
            
            # For simplicity, create a new completed operation
            op_id = provenance.start_operation(
                operation_type='tool_execution',
                agent_details={'tool_id': tool_id},
                used={'input': input_hash},
                parameters={'tool': tool_id}
            )
            
            # Complete it immediately
            provenance.complete_operation(
                op_id,
                outputs=[output_hash],
                success=True
            )
            
            # Return trace
            trace = {
                'operation_id': op_id,
                'tool_id': tool_id,
                'timestamp': time.time(),
                'input_hash': input_hash,
                'output_hash': output_hash
            }
            
            return trace
    
    def get_lineage(self, entity_id: str) -> Dict:
        """Get lineage for an entity"""
        provenance = self.get_provenance_service()
        lineage = provenance.get_lineage(entity_id)
        return lineage
    
    def get_impact_analysis(self, entity_id: str) -> Dict:
        """Get impact analysis for changes to an entity"""
        provenance = self.get_provenance_service()
        impact = provenance.analyze_impact(entity_id)
        return impact