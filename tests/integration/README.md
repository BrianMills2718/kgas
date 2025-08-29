# Integration Tests

These are active integration tests for the main /src/ system.
Moved from root directory on 2025-08-29.

## Test Files:
- test_analytics_access.py - Tests analytics system pipeline
- test_cross_modal_registration.py - Tests tool registry for cross-modal tools  
- test_cross_modal_simple.py - Individual tool import tests
- test_neo4j_auth.py - Neo4j connection verification
- test_pandas_tools.py - Pandas-dependent tools validation
- test_registry_discovery.py - Tool registry discovery validation

## Usage:
These validate that the primary /src/ codebase integration works.
They test different components than the /tool_compatability/poc/vertical_slice/ work.

