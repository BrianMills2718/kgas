# Phase D.12: Tool Data Flow Robustness & Integration

**Status**: Investigation Phase  
**Started**: 2025-08-06  
**Duration**: 4 weeks  
**Priority**: CRITICAL for reliable pipeline execution

## 🎯 Objectives

Ensure reliable end-to-end execution of natural language → DAG → tool execution → results pipeline through:
1. Validated data flow between all tool pairs
2. Proper resource management and cleanup
3. Fail-fast architecture with comprehensive logging
4. Integration tests for each tool connection

## 🔍 Current State Analysis

### Identified Issues
1. **Field Name Mismatches**: T01 outputs `content`, T23C expects `text`
2. **Resource Leaks**: Neo4j connections may not be properly closed on failure
3. **Transaction Management**: No rollback on partial failures
4. **Temp File Cleanup**: PDF processing may leave temporary files
5. **Error Propagation**: Failures don't always propagate cleanly through pipeline

### Working Components
- Individual tools execute successfully in isolation
- Tool registry and discovery functioning
- Basic DAG generation works for simple cases
- Workflow engine can start execution

## 📋 Implementation Tasks

### Week 1: Schema Audit & Mapping Layer

#### Task D.12.1: Tool Schema Audit
**Duration**: 2 days  
**Deliverable**: Complete mapping of all tool input/output schemas

```python
# Document for each tool:
- Tool ID
- Input schema fields and types
- Output schema fields and types  
- Required vs optional fields
- Field semantics (what each field represents)
```

#### Task D.12.2: Field Mapping Implementation
**Duration**: 3 days  
**Deliverable**: Explicit mapping layer between tool pairs

```python
class ToolFieldMapper:
    """Maps output fields from one tool to input fields of another"""
    
    FIELD_MAPPINGS = {
        ("T01", "T23C"): {
            "content": "text",  # T01.content → T23C.text
            "file_path": "document_ref"
        },
        ("T23C", "T31"): {
            "entities": "entity_list",
            "relationships": "relationship_list"
        },
        ("T31", "T68"): {
            # Direct compatibility - same field names
        }
    }
    
    def map_fields(self, source_tool: str, target_tool: str, data: dict) -> dict:
        """Transform data fields from source tool format to target tool format"""
```

### Week 2: Transaction Management & Resource Cleanup

#### Task D.12.3: Transaction Management
**Duration**: 3 days  
**Deliverable**: Atomic operations with proper rollback

```python
class TransactionalToolExecution:
    """Ensures atomic tool execution with rollback on failure"""
    
    def execute_with_transaction(self, tool, request):
        neo4j_tx = None
        sqlite_tx = None
        
        try:
            # Begin transactions
            if tool.uses_neo4j:
                neo4j_tx = self.neo4j.begin_transaction()
            if tool.uses_sqlite:
                sqlite_tx = self.sqlite.begin_transaction()
            
            # Execute tool
            result = tool.execute(request)
            
            # Commit on success
            if neo4j_tx:
                neo4j_tx.commit()
            if sqlite_tx:
                sqlite_tx.commit()
                
            return result
            
        except Exception as e:
            # Rollback on failure
            if neo4j_tx:
                neo4j_tx.rollback()
            if sqlite_tx:
                sqlite_tx.rollback()
            raise
```

#### Task D.12.4: Resource Cleanup Handlers
**Duration**: 2 days  
**Deliverable**: Guaranteed cleanup of resources

```python
class ResourceManager:
    """Manages resource lifecycle for tools"""
    
    def __init__(self):
        self.temp_files = []
        self.connections = []
        
    def register_temp_file(self, path):
        self.temp_files.append(path)
        
    def cleanup(self):
        """Clean up all registered resources"""
        for file in self.temp_files:
            if Path(file).exists():
                Path(file).unlink()
                
        for conn in self.connections:
            conn.close()
```

### Week 3: Integration Testing

#### Task D.12.5: Tool Pair Integration Tests
**Duration**: 3 days  
**Deliverable**: Tests for each tool connection

```python
# test_tool_integration.py

def test_t01_to_t23c_integration():
    """Test data flows correctly from T01 to T23C"""
    # Load document with T01
    t01_result = t01.execute({"file_path": "test.txt"})
    
    # Map fields
    t23c_input = mapper.map_fields("T01", "T23C", t01_result.data)
    
    # Execute T23C with mapped data
    t23c_result = t23c.execute(t23c_input)
    
    # Verify success
    assert t23c_result.status == "success"
    assert "entities" in t23c_result.data

def test_full_pipeline_integration():
    """Test complete pipeline T01 → T23C → T31 → T68"""
    # Test document
    test_doc = create_test_document()
    
    # Execute full pipeline
    result = execute_pipeline(test_doc)
    
    # Verify end-to-end success
    assert result["status"] == "success"
    assert "centrality_scores" in result["data"]
```

#### Task D.12.6: Error Propagation Tests
**Duration**: 2 days  
**Deliverable**: Verify fail-fast behavior

```python
def test_pipeline_fails_fast_on_error():
    """Ensure pipeline stops immediately on tool failure"""
    # Provide invalid input to trigger failure
    with pytest.raises(ToolExecutionError):
        execute_pipeline("nonexistent.txt")
    
    # Verify no partial data in database
    assert neo4j.query("MATCH (n) RETURN count(n)")[0] == 0
    
    # Verify temp files cleaned up
    assert not Path("/tmp/pipeline_*").exists()
```

### Week 4: CLI Hardening & User Experience

#### Task D.12.7: CLI Error Handling
**Duration**: 2 days  
**Deliverable**: Robust CLI with clear error messages

```python
# ask.py improvements

def main():
    try:
        result = execute_analysis(args.question, args.documents)
        display_results(result)
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"❌ Document not found: {e}")
        sys.exit(1)
        
    except ToolExecutionError as e:
        print(f"❌ Analysis failed: {e}")
        logger.error(f"Tool execution failed: {e}", exc_info=True)
        sys.exit(1)
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        print("Please check logs for details")
        logger.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(2)
```

#### Task D.12.8: End-to-End Validation
**Duration**: 3 days  
**Deliverable**: Proven CLI functionality

```bash
# Test suite for CLI validation

# Test 1: Simple success case
python ask.py -q "What entities are in this?" -d simple.txt
assert $? -eq 0

# Test 2: Missing file handling  
python ask.py -q "Analyze this" -d nonexistent.txt
assert $? -eq 1
assert "Document not found" in output

# Test 3: Complex analysis
python ask.py -q "Find central entities" -d corpus/
assert $? -eq 0
assert results displayed

# Test 4: Resource cleanup validation
check_no_temp_files()
check_connections_closed()
check_no_orphan_transactions()
```

## 🎯 Success Criteria

### Functional Requirements
- [ ] CLI completes end-to-end without hanging or crashing
- [ ] Meaningful results displayed to user
- [ ] Clear error messages on failures
- [ ] Proper exit codes (0 for success, 1 for user error, 2 for system error)

### Technical Requirements  
- [ ] All tool pairs have explicit field mappings
- [ ] Transactions rollback on failure
- [ ] Resources cleaned up even on error
- [ ] All integration tests passing
- [ ] <2 minute execution time for typical analysis

### Quality Requirements
- [ ] Comprehensive logging at INFO level
- [ ] Debug logging captures full request/response data
- [ ] No resource leaks after 100 consecutive runs
- [ ] No partial data in databases after failures

## 📊 Validation Plan

### Manual Testing Protocol
1. Run 10 different natural language queries
2. Test with various document types (txt, pdf, missing)
3. Verify results are meaningful and accurate
4. Check logs for any warnings/errors
5. Monitor resource usage during execution

### Automated Testing
```bash
# Run integration test suite
pytest tests/integration/test_tool_dataflow.py -v

# Run CLI validation suite  
./scripts/validate_cli.sh

# Run stress test
python scripts/stress_test_pipeline.py --iterations 100
```

### Performance Benchmarks
- Single document analysis: <30 seconds
- 10 document corpus: <2 minutes
- Memory usage: <500MB peak
- No connection leaks after 24 hour run

## 🚫 Out of Scope

This phase does NOT include:
- Adding new tools or features
- Optimizing for performance (just reliability)
- Changing tool algorithms or logic
- UI improvements beyond basic CLI

## 📚 References

- [Tool Contract Specifications](../../architecture/specifications/tool-contracts.md)
- [Workflow Engine Design](../../architecture/systems/workflow-engine.md)
- [Error Handling Standards](../../development/standards/ERROR_HANDLING_BEST_PRACTICES.md)
- [Testing Standards](../../development/testing/TESTING_STANDARDS.md)

## 📝 Notes

### Key Insights from Investigation
1. Field mapping is the critical gap - tools work individually but not together
2. Resource cleanup only happens on success path currently
3. No integration tests exist for tool chaining
4. Error messages are too technical for end users

### Risk Mitigation
- **Risk**: Breaking existing functionality
  - **Mitigation**: Comprehensive test coverage before changes
- **Risk**: Performance regression  
  - **Mitigation**: Benchmark before/after, focus on correctness first
- **Risk**: Complex field mappings
  - **Mitigation**: Start with simple 1:1 mappings, iterate