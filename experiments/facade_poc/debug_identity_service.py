#!/usr/bin/env python3
"""Debug what identity service actually returns"""

import sys
import os
sys.path.insert(0, '/home/brian/projects/Digimons')

# Set Neo4j credentials
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'

from src.core.service_manager import ServiceManager

try:
    sm = ServiceManager()
    identity = sm.get_identity_service()
    
    # Test what create_mention returns
    result = identity.create_mention(
        surface_form='Test Entity',
        start_pos=0,
        end_pos=11,
        source_ref='test',
        entity_type='PERSON',
        confidence=0.9
    )
    
    print('Result type:', type(result))
    print('Result:', result)
    if isinstance(result, dict):
        print('Keys:', list(result.keys()))
        print('Has mention_id?', 'mention_id' in result)
        print('Has status?', 'status' in result)
        print('Has data?', 'data' in result)
        if 'data' in result:
            print('Data:', result['data'])
            if isinstance(result['data'], dict):
                print('Data keys:', list(result['data'].keys()))
except Exception as e:
    print(f"Error: {e}")