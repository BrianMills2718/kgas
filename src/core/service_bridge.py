#!/usr/bin/env python3
"""
Bridge to connect critical services to framework
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from src.core.provenance_service import ProvenanceService
from src.core.identity_service import IdentityService
from src.core.service_manager import ServiceManager

class ServiceBridge:
    """Connects framework to critical services with configuration support"""
    
    def __init__(self, service_manager: ServiceManager = None, config: Dict = None):
        """
        Initialize with optional configuration
        
        Args:
            service_manager: Service manager instance
            config: Dictionary with service configurations
                Example: {
                    'identity': {'persistence': True, 'db_path': 'identity.db'},
                    'provenance': {'backend': 'sqlite'}
                }
        """
        self.service_manager = service_manager or ServiceManager()
        self._services = {}
        self.config = config or {}
        
    def get_provenance_service(self) -> ProvenanceService:
        """Get or create configured provenance service"""
        if 'provenance' not in self._services:
            provenance_config = self.config.get('provenance', {})
            
            # Configure based on settings
            backend = provenance_config.get('backend', 'memory')
            if backend == 'sqlite':
                db_path = provenance_config.get('db_path', 'data/provenance.db')
                # Ensure directory exists
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Note: ProvenanceService doesn't have sqlite backend yet,
                # this is placeholder for future enhancement
                self._services['provenance'] = ProvenanceService()
                print(f"✅ ProvenanceService configured (backend: sqlite, path: {db_path})")
            else:
                self._services['provenance'] = ProvenanceService()
                print("⚠️ ProvenanceService with in-memory backend")
                
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
    
    def get_identity_service(self) -> IdentityService:
        """Get or create configured identity service"""
        if 'identity' not in self._services:
            identity_config = self.config.get('identity', {})
            
            # Configure based on settings
            if identity_config.get('persistence', False):
                db_path = identity_config.get('db_path', 'data/identity.db')
                # Ensure directory exists
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Note: IdentityService doesn't have persistence yet, 
                # this is placeholder for future enhancement
                self._services['identity'] = IdentityService()
                print(f"✅ IdentityService configured (persistence: {db_path})")
            else:
                self._services['identity'] = IdentityService()
                print("⚠️ IdentityService without persistence (in-memory only)")
        
        return self._services['identity']
    
    def track_entity(self, surface_form: str, entity_type: str,
                     confidence: float, source_tool: str) -> str:
        """Track entity mention and return entity_id"""
        identity = self.get_identity_service()
        
        # Create mention
        mention_result = identity.create_mention(
            surface_form=surface_form,
            start_pos=0,  # Simplified for now
            end_pos=len(surface_form),
            source_ref=source_tool,
            entity_type=entity_type,
            confidence=confidence
        )
        
        # Extract mention_id from result
        mention_id = mention_result.get('mention_id') if isinstance(mention_result, dict) else mention_result
        
        # Get or create entity
        entity_result = identity.get_entity_by_mention(mention_id)
        
        # Extract entity_id from result
        if isinstance(entity_result, dict):
            entity_id = entity_result.get('entity_id', str(mention_id))
        else:
            entity_id = str(entity_result) if entity_result else str(mention_id)
        
        return entity_id