#!/usr/bin/env python3
"""Test Neo4j connection and CrossModalTool with correct auth."""

import os
import sys
sys.path.append('/home/brian/projects/Digimons')

# Set environment variables
os.environ['NEO4J_PASSWORD'] = 'devpassword'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'

from neo4j import GraphDatabase

# Test direct connection
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "devpassword")
)

try:
    driver.verify_connectivity()
    print("✅ Neo4j connection successful with devpassword")
    
    # Test CrossModalTool
    from src.tools.phase_c.cross_modal_tool import CrossModalTool
    tool = CrossModalTool()
    print("✅ CrossModalTool initialized successfully")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
finally:
    driver.close()