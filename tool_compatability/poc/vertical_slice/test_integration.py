#!/usr/bin/env python3
# Run after register_with_framework.py

import sys
sys.path.append('/home/brian/projects/Digimons')
sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')

from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
from services.vector_service import VectorService
from services.table_service import TableService
from tools.vector_tool import VectorTool
from tools.table_tool import TableTool

# Initialize framework
framework = CleanToolFramework(
    neo4j_uri='bolt://localhost:7687',
    sqlite_path='vertical_slice.db'
)

# Create services
vector_service = VectorService()
table_service = TableService()

# Register adapted tools
framework.register_tool(
    VectorTool(vector_service),
    ToolCapabilities(
        tool_id="VectorTool",
        input_type=DataType.TEXT,
        output_type=DataType.VECTOR,
        input_construct="text",
        output_construct="embedding",
        transformation_type="embedding"
    )
)

framework.register_tool(
    TableTool(table_service),
    ToolCapabilities(
        tool_id="TableTool",
        input_type=DataType.VECTOR,
        output_type=DataType.TABLE,
        input_construct="embedding",
        output_construct="stored",
        transformation_type="persistence"
    )
)

# Test actual chain execution
test_data = {'text': 'Integration test text'}
chain = framework.find_chain(DataType.TEXT, DataType.TABLE)
print(f"Chain found: {chain}")
result = framework.execute_chain(chain, test_data)

if result.success:
    print(f"✅ Integration successful: {result.data}")
else:
    print(f"❌ Integration failed: {result.error}")