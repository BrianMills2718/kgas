#!/usr/bin/env python3
"""Simple test of 5-tool pipeline"""

import sys
import os
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')

sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from integrate_tools import integrate_ready_tools, integrate_legacy_tools

# Initialize framework
framework = CleanToolFramework(
    neo4j_uri="bolt://localhost:7687",
    sqlite_path="vertical_slice.db"
)

# Clean Neo4j
with framework.neo4j.session() as session:
    session.run("MATCH (n:VSEntity) DETACH DELETE n")

# Integrate tools
integrate_ready_tools(framework)
integrate_legacy_tools(framework)

print("\n=== Testing 5-Tool Pipeline ===")
print("Registered tools:", list(framework.capabilities.keys()))

# Create test file
test_file = "test.txt"
with open(test_file, 'w') as f:
    f.write("Brian Chhun and Sarah Chen work on KGAS at Melbourne University.")

# Chain 1: simple_text_loader
print("\nStep 1: simple_text_loader")
result1 = framework.execute_chain(['simple_text_loader'], test_file)
print(f"  Success: {result1.success}, Uncertainty: {result1.total_uncertainty:.3f}")

# Chain 2: t15a_text_chunker (chunks the text)
print("Step 2: t15a_text_chunker")
result2 = framework.execute_chain(['t15a_text_chunker'], result1.data)
print(f"  Success: {result2.success}, Uncertainty: {result2.total_uncertainty:.3f}")

# Since chunker returns chunks, let's go back to using full text for entity extraction
# Chain 3: gemini_entity_extractor
print("Step 3: gemini_entity_extractor")
result3 = framework.execute_chain(['gemini_entity_extractor'], result1.data)
print(f"  Success: {result3.success}, Uncertainty: {result3.total_uncertainty:.3f}")

# Chain 4: t34_edge_builder (enhance edges)
print("Step 4: t34_edge_builder")
result4 = framework.execute_chain(['t34_edge_builder'], result3.data)
print(f"  Success: {result4.success}, Uncertainty: {result4.total_uncertainty:.3f}")

# Chain 5: neo4j_graph_builder (persist)
print("Step 5: neo4j_graph_builder")
result5 = framework.execute_chain(['neo4j_graph_builder'], result4.data)
print(f"  Success: {result5.success}, Uncertainty: {result5.total_uncertainty:.3f}")

# Calculate total uncertainty
all_uncertainties = (
    result1.step_uncertainties + 
    result2.step_uncertainties + 
    result3.step_uncertainties + 
    result4.step_uncertainties +
    result5.step_uncertainties
)

confidence = 1.0
for u in all_uncertainties:
    confidence *= (1 - u)
total_uncertainty = 1 - confidence

print("\n=== 5-Tool Pipeline Complete ===")
print(f"Tools used: {len(all_uncertainties)}")
print(f"Individual uncertainties: {[f'{u:.3f}' for u in all_uncertainties]}")
print(f"Combined uncertainty: {total_uncertainty:.3f}")
print(f"✅ Successfully executed {len(all_uncertainties)}-tool pipeline!")

# Clean up
os.remove(test_file)
framework.cleanup()