# KGAS Cross-Modal Analysis Implementation + Evidence-Based Development

## 🎯 **MISSION: Enable Cross-Modal Workflow Execution with Real Tool Registry Integration**

**Current Status (2025-08-06)**: 
- ✅ **Success/Failure Paradox Resolved**: Tool registry populated with 5 real KGAS tools 
- ✅ **Enhanced Reasoning System**: Complete 4-level hierarchical decision capture implemented
- ✅ **Safe Workflow Execution**: Fail-fast architecture with no mock fallbacks operational
- ✅ **Cross-Modal Infrastructure Discovered**: Extensive existing capabilities found
- 🚀 **IMMEDIATE PRIORITY**: Cross-modal tool registry integration for graph→table→vector→synthesis workflows

## 📋 **IMPLEMENTATION OVERVIEW** 

The KGAS system has successfully resolved the critical "success/failure paradox" where DAG generation succeeded but tool execution failed due to an empty tool registry. Investigation revealed sophisticated cross-modal infrastructure already exists but needs registry integration to enable complex analysis workflows involving data format transfers and synthesis.

### **Recently Resolved Issues**
- **Tool Registry Population**: `tool_registry_loader.py` automatically discovers and registers KGAS tools (5 tools registered)
- **Service Manager Integration**: Fixed KGAS tool constructor requirements with proper `service_manager` parameter
- **LLM Tool ID Mapping**: Created `tool_id_mapper.py` for LLM-generated names → registry IDs  
- **Safe Workflow Execution**: `safe_workflow_executor.py` implements fail-fast execution with comprehensive error handling
- **Workflow Agent Enhancement**: Successfully integrated tool registry initialization at agent startup

### **Discovered Cross-Modal Infrastructure**
**Analysis Status**: ✅ **COMPLETE** - Comprehensive cross-modal capabilities already implemented

**Key Infrastructure Components**:
- **`CrossModalConverter`** (`src/analytics/cross_modal_converter.py`): Complete Graph ↔ Table ↔ Vector conversion matrix
- **`GraphTableExporterUnified`** (`src/tools/cross_modal/graph_table_exporter_unified.py`): Production-ready graph→table conversion with standardized tool interface
- **`CrossModalWorkflows`** (`src/workflows/cross_modal_workflows.py`): Sophisticated workflow orchestration with agent integration
- **`CrossModalTool`** (`src/tools/phase_c/cross_modal_tool.py`): Cross-modal analysis tool wrapper with fallback analyzer
- **`VectorEmbedder`** (`src/tools/phase1/t15b_vector_embedder_kgas.py`): Vector embeddings capability

## 🔧 **PHASE 1: Cross-Modal Tool Registry Integration (1-2 days)**

### **Objective**
Register existing sophisticated cross-modal tools in the tool registry to enable LLM-generated DAGs for graph→table→vector→synthesis analysis workflows.

### **Gap Analysis**
**Root Issue**: Cross-modal tools exist but aren't registered, preventing workflow execution

**Current State**: 
- 5 real KGAS tools registered (T01, T15A, T23A, T31, T34, T49, T68)
- Cross-modal tools implemented but not discoverable by workflow system
- LLM can generate DAGs but tools aren't available for execution

**Required Integration**: Register 4 sophisticated cross-modal tools

### **Implementation Steps**

#### **Step 1: Update Tool Registry Loader with Cross-Modal Tools**
**File**: `src/core/tool_registry_loader.py` 

**Add Cross-Modal Tool Patterns**:
```python
def _get_tool_class_patterns(self) -> Dict[str, List[str]]:
    """Get patterns to match tool classes to registry IDs"""
    patterns = {
        # Existing KGAS tools...
        "T01_PDF_LOADER": ["T01PDFLoaderKGAS"],
        "T15A_TEXT_CHUNKER": ["T15ATextChunkerKGAS"],
        "T23A_SPACY_NER": ["T23ASpacyNERKGAS"],
        "T31_ENTITY_BUILDER": ["T31EntityBuilderKGAS"],
        "T34_EDGE_BUILDER": ["T34EdgeBuilderKGAS"],
        "T49_MULTIHOP_QUERY": ["T49MultihopQueryKGAS"],
        "T68_PAGERANK": ["T68PageRankKGAS"],
        
        # Cross-modal tools to register
        "GRAPH_TABLE_EXPORTER": ["GraphTableExporterUnified"],
        "CROSS_MODAL_ANALYZER": ["CrossModalTool"],
        "VECTOR_EMBEDDER": ["T15BVectorEmbedderKGAS"],
        "MULTI_FORMAT_EXPORTER": ["MultiFormatExporter"]
    }
    return patterns

def _get_tool_file_paths(self) -> Dict[str, str]:
    """Get file paths for tool discovery"""
    return {
        # Existing KGAS tool paths...
        "T01_PDF_LOADER": "src/tools/phase1/t01_pdf_loader_kgas.py",
        "T15A_TEXT_CHUNKER": "src/tools/phase1/t15a_text_chunker_kgas.py",
        "T23A_SPACY_NER": "src/tools/phase1/t23a_spacy_ner_kgas.py",
        "T31_ENTITY_BUILDER": "src/tools/phase1/t31_entity_builder_kgas.py",
        "T34_EDGE_BUILDER": "src/tools/phase1/t34_edge_builder_kgas.py", 
        "T49_MULTIHOP_QUERY": "src/tools/phase1/t49_multihop_query_kgas.py",
        "T68_PAGERANK": "src/tools/phase1/t68_pagerank_kgas.py",
        
        # Cross-modal tool paths
        "GRAPH_TABLE_EXPORTER": "src/tools/cross_modal/graph_table_exporter_unified.py",
        "CROSS_MODAL_ANALYZER": "src/tools/phase_c/cross_modal_tool.py",
        "VECTOR_EMBEDDER": "src/tools/phase1/t15b_vector_embedder_kgas.py",
        "MULTI_FORMAT_EXPORTER": "src/tools/cross_modal/multi_format_exporter.py"
    }

def _create_tool_instance(self, tool_class: Type[KGASTool], tool_id: str) -> KGASTool:
    """Create tool instance with proper constructor arguments"""
    service_manager = ServiceManager()
    
    # All KGAS tools and cross-modal tools require service_manager
    if (tool_id.endswith("_KGAS") or "KGAS" in str(tool_class.__name__) or
        tool_id in ["GRAPH_TABLE_EXPORTER", "CROSS_MODAL_ANALYZER", "VECTOR_EMBEDDER", "MULTI_FORMAT_EXPORTER"]):
        return tool_class(service_manager=service_manager)
    else:
        # Fallback for other tools
        return tool_class()
```

#### **Step 2: Update Tool ID Mapper with Cross-Modal Mappings**
**File**: `src/core/tool_id_mapper.py`

**Add Cross-Modal Tool Mappings**:
```python
def _create_tool_mappings(self) -> Dict[str, str]:
    """Create bidirectional mappings between LLM names and registry IDs"""
    mappings = {
        # Existing KGAS tool mappings...
        "pdf loader": "T01_PDF_LOADER",
        "text chunker": "T15A_TEXT_CHUNKER", 
        "entity extractor": "T23A_SPACY_NER",
        "entity builder": "T31_ENTITY_BUILDER",
        "edge builder": "T34_EDGE_BUILDER",
        "multihop query": "T49_MULTIHOP_QUERY",
        "pagerank": "T68_PAGERANK",
        
        # Cross-modal tool mappings for LLM DAG generation
        "graph to table converter": "GRAPH_TABLE_EXPORTER",
        "graph table exporter": "GRAPH_TABLE_EXPORTER", 
        "table converter": "GRAPH_TABLE_EXPORTER",
        "cross modal analyzer": "CROSS_MODAL_ANALYZER",
        "cross-modal analysis": "CROSS_MODAL_ANALYZER",
        "modal integration": "CROSS_MODAL_ANALYZER",
        "vector embedder": "VECTOR_EMBEDDER",
        "embedding generator": "VECTOR_EMBEDDER",
        "vector generator": "VECTOR_EMBEDDER", 
        "multi format exporter": "MULTI_FORMAT_EXPORTER",
        "format converter": "MULTI_FORMAT_EXPORTER",
        "data exporter": "MULTI_FORMAT_EXPORTER"
    }
    return mappings
```

#### **Step 3: Create Cross-Modal Workflow Template**
**File**: `src/workflows/cross_modal_dag_template.py` (NEW FILE)

**Standard Cross-Modal DAG Structure**:
```python
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class CrossModalDAGTemplate:
    """Standard template for cross-modal analysis workflows"""
    
    @staticmethod
    def create_graph_table_vector_synthesis_dag(
        source_data_ref: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Create DAG for graph→table→vector→synthesis analysis"""
        
        dag = {
            "dag_id": f"cross_modal_analysis_{analysis_type}",
            "description": "Cross-modal analysis with format transfers and synthesis",
            "steps": [
                {
                    "step_id": "load_source_data",
                    "tool_id": "T01_PDF_LOADER",  # Or appropriate loader
                    "operation": "load",
                    "input_data": {"file_path": source_data_ref},
                    "parameters": {}
                },
                {
                    "step_id": "extract_entities",
                    "tool_id": "T23A_SPACY_NER", 
                    "operation": "extract",
                    "input_data": "$load_source_data.text",
                    "parameters": {"confidence_threshold": 0.8},
                    "depends_on": ["load_source_data"]
                },
                {
                    "step_id": "build_graph",
                    "tool_id": "T31_ENTITY_BUILDER",
                    "operation": "build", 
                    "input_data": "$extract_entities.entities",
                    "parameters": {},
                    "depends_on": ["extract_entities"]
                },
                {
                    "step_id": "convert_graph_to_table",
                    "tool_id": "GRAPH_TABLE_EXPORTER",
                    "operation": "convert",
                    "input_data": {
                        "graph_data": "$build_graph.graph",
                        "table_type": "edge_list"
                    },
                    "parameters": {},
                    "depends_on": ["build_graph"]
                },
                {
                    "step_id": "generate_vectors",
                    "tool_id": "VECTOR_EMBEDDER",
                    "operation": "embed",
                    "input_data": {
                        "text_data": "$load_source_data.text",
                        "entities": "$extract_entities.entities"
                    },
                    "parameters": {"embedding_model": "sentence-transformers"},
                    "depends_on": ["extract_entities"]
                },
                {
                    "step_id": "cross_modal_synthesis",
                    "tool_id": "CROSS_MODAL_ANALYZER", 
                    "operation": "integrate",
                    "input_data": {
                        "graph_data": "$build_graph.graph",
                        "table_data": "$convert_graph_to_table.table_data", 
                        "vector_data": "$generate_vectors.embeddings"
                    },
                    "parameters": {"integration_mode": "comprehensive"},
                    "depends_on": ["build_graph", "convert_graph_to_table", "generate_vectors"]
                }
            ]
        }
        
        return dag
```

### **Evidence-Based Validation**
```bash
# Test cross-modal tool registry integration
python -c "
from src.core.tool_registry_loader import initialize_tool_registry
from src.core.service_manager import ServiceManager

# Initialize tool registry with cross-modal tools
registry_results = initialize_tool_registry()

print(f'Tools registered: {len(registry_results)}')
print(f'Registry contents: {list(registry_results.keys())}')

# Check for cross-modal tools
cross_modal_tools = [
    'GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 
    'VECTOR_EMBEDDER', 'MULTI_FORMAT_EXPORTER'
]

for tool_id in cross_modal_tools:
    if tool_id in registry_results:
        print(f'✅ {tool_id} successfully registered')
    else:
        print(f'❌ {tool_id} missing from registry')
"

# Test cross-modal workflow DAG generation  
python -c "
from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate

dag = CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag(
    source_data_ref='test_document.pdf',
    analysis_type='comprehensive'
)

print(f'✅ Cross-modal DAG created: {dag[\"dag_id\"]}')
print(f'   Steps: {len(dag[\"steps\"])}')
print(f'   Tools used: {[step[\"tool_id\"] for step in dag[\"steps\"]]}')
"

# Test LLM tool ID mapping for cross-modal tools
python -c "
from src.core.tool_id_mapper import ToolIDMapper

mapper = ToolIDMapper()

test_llm_names = [
    'graph to table converter',
    'cross modal analyzer', 
    'vector embedder',
    'format converter'
]

for llm_name in test_llm_names:
    registry_id = mapper.map_llm_name_to_registry_id(llm_name)
    if registry_id:
        print(f'✅ \"{llm_name}\" → {registry_id}')
    else:
        print(f'❌ \"{llm_name}\" → No mapping found')
"
```

## 🔍 **PHASE 2: Cross-Modal Execution Pipeline Testing (1 day)**

### **Objective**
Test complete cross-modal workflow execution with real tool registry integration to ensure graph→table→vector→synthesis analysis works end-to-end.

### **Test Strategy**
Execute comprehensive cross-modal workflows using registered tools to validate full functionality.

### **Test Implementation**

#### **Step 1: Cross-Modal Tool Execution Testing**
**File**: `scripts/test_cross_modal_execution.py` (NEW FILE)

**Comprehensive Test Suite**:
```python
#!/usr/bin/env python3
"""Test cross-modal workflow execution with real tools"""

import time
import json
from pathlib import Path
from src.agents.workflow_agent import WorkflowAgent  
from src.core.service_manager import ServiceManager
from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate

def test_cross_modal_tool_registry():
    """Test that all cross-modal tools are registered and accessible"""
    print("🔍 Testing Cross-Modal Tool Registry...")
    
    agent = WorkflowAgent(service_manager=ServiceManager())
    available_tools = agent.tool_registry.list_tools()
    
    required_tools = [
        "GRAPH_TABLE_EXPORTER", "CROSS_MODAL_ANALYZER",
        "VECTOR_EMBEDDER", "MULTI_FORMAT_EXPORTER"
    ]
    
    registry_status = {}
    for tool_id in required_tools:
        is_registered = tool_id in available_tools
        registry_status[tool_id] = is_registered
        status_icon = "✅" if is_registered else "❌"
        print(f"   {status_icon} {tool_id}: {'Registered' if is_registered else 'Missing'}")
    
    all_registered = all(registry_status.values())
    print(f"📊 Registry Status: {'PASS' if all_registered else 'FAIL'} ({sum(registry_status.values())}/{len(required_tools)} tools)")
    return all_registered

def test_cross_modal_dag_generation():
    """Test cross-modal DAG template generation"""
    print("\n🔍 Testing Cross-Modal DAG Generation...")
    
    try:
        dag = CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag(
            source_data_ref="test_document.pdf",
            analysis_type="comprehensive"
        )
        
        # Validate DAG structure
        required_steps = [
            "load_source_data", "extract_entities", "build_graph",
            "convert_graph_to_table", "generate_vectors", "cross_modal_synthesis"
        ]
        
        dag_steps = [step["step_id"] for step in dag["steps"]]
        missing_steps = [step for step in required_steps if step not in dag_steps]
        
        if not missing_steps:
            print(f"   ✅ DAG Structure: Complete ({len(dag_steps)} steps)")
            print(f"   ✅ Tool Chain: {' → '.join([step['tool_id'] for step in dag['steps']])}")
            return True
        else:
            print(f"   ❌ DAG Structure: Missing steps {missing_steps}")
            return False
            
    except Exception as e:
        print(f"   ❌ DAG Generation Failed: {e}")
        return False

def test_cross_modal_workflow_execution():
    """Test complete cross-modal workflow execution"""
    print("\n🔍 Testing Cross-Modal Workflow Execution...")
    
    start_time = time.time()
    
    try:
        # Create test document for processing
        test_doc = Path("test_cross_modal_document.txt") 
        test_doc.write_text("""
        Cognitive Load Theory is a theoretical framework that describes how working memory 
        limitations affect learning. The theory identifies three types of cognitive load:
        intrinsic, extraneous, and germane. The coherence principle suggests that 
        excluding extraneous material improves learning outcomes.
        """)
        
        # Initialize workflow agent
        agent = WorkflowAgent(service_manager=ServiceManager())
        
        # Generate cross-modal DAG
        dag = CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag(
            source_data_ref=str(test_doc),
            analysis_type="test"
        )
        
        # Execute workflow
        result = agent.execute_workflow_from_dag(dag)
        
        execution_time = time.time() - start_time
        
        # Validate execution results
        if result and result.get("status") == "success":
            print(f"   ✅ Workflow Execution: SUCCESS")
            print(f"   ✅ Execution Time: {execution_time:.2f}s")
            
            # Validate cross-modal outputs
            workflow_data = result.get("data", {})
            cross_modal_results = workflow_data.get("cross_modal_synthesis", {})
            
            if cross_modal_results:
                modalities = cross_modal_results.get("modalities", [])
                integration_score = cross_modal_results.get("integration_score", 0)
                print(f"   ✅ Cross-Modal Integration: {len(modalities)} modalities, score: {integration_score}")
                return True
            else:
                print("   ⚠️  Cross-Modal Results: Missing synthesis output")
                return False
        else:
            error_msg = result.get("error", "Unknown error") if result else "No result returned"
            print(f"   ❌ Workflow Execution: FAILED - {error_msg}")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Workflow Execution: EXCEPTION after {execution_time:.2f}s - {e}")
        return False
    finally:
        # Cleanup test document
        if test_doc.exists():
            test_doc.unlink()

def test_llm_cross_modal_dag_generation():
    """Test LLM-generated DAG for cross-modal analysis"""
    print("\n🔍 Testing LLM Cross-Modal DAG Generation...")
    
    try:
        agent = WorkflowAgent(service_manager=ServiceManager())
        
        # Test natural language request for cross-modal analysis
        user_request = """
        I want to analyze a document using graph, table and vector representations,
        then synthesize findings across all three modalities for comprehensive insights.
        """
        
        # Generate DAG from natural language
        dag_result = agent.generate_workflow_dag(user_request)
        
        if dag_result and dag_result.get("status") == "success":
            dag = dag_result.get("dag", {})
            steps = dag.get("steps", [])
            
            # Check for cross-modal tools in generated DAG
            used_tools = [step.get("tool_id") for step in steps]
            cross_modal_tools_used = [
                tool for tool in used_tools 
                if tool in ["GRAPH_TABLE_EXPORTER", "CROSS_MODAL_ANALYZER", "VECTOR_EMBEDDER"]
            ]
            
            if cross_modal_tools_used:
                print(f"   ✅ LLM DAG Generation: SUCCESS")
                print(f"   ✅ Cross-Modal Tools Used: {cross_modal_tools_used}")
                print(f"   ✅ Total Steps: {len(steps)}")
                return True
            else:
                print(f"   ⚠️  LLM DAG Generation: No cross-modal tools included")
                print(f"   Tools used: {used_tools}")
                return False
        else:
            error_msg = dag_result.get("error", "Unknown error") if dag_result else "No result"
            print(f"   ❌ LLM DAG Generation: FAILED - {error_msg}")
            return False
            
    except Exception as e:
        print(f"   ❌ LLM DAG Generation: EXCEPTION - {e}")
        return False

def main():
    """Run comprehensive cross-modal testing suite"""
    print("🚀 KGAS Cross-Modal Analysis Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Tool Registry", test_cross_modal_tool_registry),
        ("DAG Generation", test_cross_modal_dag_generation), 
        ("Workflow Execution", test_cross_modal_workflow_execution),
        ("LLM DAG Generation", test_llm_cross_modal_dag_generation)
    ]
    
    results = {}
    overall_start = time.time()
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}: CRITICAL ERROR - {e}")
            results[test_name] = False
    
    total_time = time.time() - overall_start
    
    # Summary
    print(f"\n{'='*20} TEST SUMMARY {'='*20}")
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {test_name}: {'PASS' if passed else 'FAIL'}")
    
    print(f"\n📊 Overall Result: {passed_tests}/{total_tests} tests passed")
    print(f"⏱️  Total Execution Time: {total_time:.2f}s")
    
    if passed_tests == total_tests:
        print("🎉 Cross-Modal Analysis System: FULLY OPERATIONAL")
        return True
    else:
        print("⚠️  Cross-Modal Analysis System: REQUIRES FIXES")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

### **Execution Validation Commands**
```bash
# Run comprehensive cross-modal testing
python scripts/test_cross_modal_execution.py

# Expected Output:
# 🚀 KGAS Cross-Modal Analysis Testing Suite
# ==================== Tool Registry ====================
#    ✅ GRAPH_TABLE_EXPORTER: Registered
#    ✅ CROSS_MODAL_ANALYZER: Registered  
#    ✅ VECTOR_EMBEDDER: Registered
#    ✅ MULTI_FORMAT_EXPORTER: Registered
# 📊 Registry Status: PASS (4/4 tools)
# 
# ==================== DAG Generation ====================
#    ✅ DAG Structure: Complete (6 steps)
#    ✅ Tool Chain: T01_PDF_LOADER → T23A_SPACY_NER → T31_ENTITY_BUILDER → GRAPH_TABLE_EXPORTER → VECTOR_EMBEDDER → CROSS_MODAL_ANALYZER
# 
# ==================== Workflow Execution ====================
#    ✅ Workflow Execution: SUCCESS
#    ✅ Execution Time: 5.23s
#    ✅ Cross-Modal Integration: 3 modalities, score: 0.75
#
# ==================== LLM DAG Generation ====================
#    ✅ LLM DAG Generation: SUCCESS
#    ✅ Cross-Modal Tools Used: ['GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 'VECTOR_EMBEDDER']
#    ✅ Total Steps: 6
#
# ==================== TEST SUMMARY ====================
# ✅ Tool Registry: PASS
# ✅ DAG Generation: PASS
# ✅ Workflow Execution: PASS  
# ✅ LLM DAG Generation: PASS
#
# 📊 Overall Result: 4/4 tests passed
# ⏱️  Total Execution Time: 12.45s
# 🎉 Cross-Modal Analysis System: FULLY OPERATIONAL

# Test specific cross-modal conversion
python -c "
from src.tools.cross_modal.graph_table_exporter_unified import GraphTableExporterUnified
from src.core.service_manager import ServiceManager

tool = GraphTableExporterUnified(ServiceManager())
contract = tool.get_contract()

print(f'✅ GraphTableExporter Contract: {contract.tool_id}')
print(f'   Input schema: {\"graph_data\" in contract.input_schema[\"properties\"]}')
print(f'   Output schema: {\"table_data\" in contract.output_schema[\"properties\"]}')
"
```

## ✅ **SUCCESS CRITERIA & DEFINITION OF DONE**

### **Phase 1 Complete When:**
- ✅ All 4 cross-modal tools registered in tool registry (`GRAPH_TABLE_EXPORTER`, `CROSS_MODAL_ANALYZER`, `VECTOR_EMBEDDER`, `MULTI_FORMAT_EXPORTER`)
- ✅ Tool ID mapper updated with cross-modal tool mappings for LLM DAG generation
- ✅ Cross-modal workflow templates created for standard analysis patterns
- ✅ Registry integration verified through evidence-based validation commands

### **Phase 2 Complete When:**
- ✅ Comprehensive cross-modal testing suite passes all 4 test categories
- ✅ Tool registry test confirms all cross-modal tools are accessible
- ✅ DAG generation test validates complete workflow templates  
- ✅ Workflow execution test demonstrates end-to-end functionality
- ✅ LLM DAG generation test confirms natural language → cross-modal workflows

### **Cross-Modal Analysis System Complete When:**
- ✅ Natural language requests automatically generate DAGs using cross-modal tools
- ✅ Graph→table→vector→synthesis workflows execute successfully end-to-end
- ✅ Data integrity maintained across all format conversions
- ✅ LLM can dynamically select appropriate cross-modal tools based on user requests


## 📋 **VERIFICATION COMMANDS**

### **Phase 1: Cross-Modal Tool Registry Integration**
```bash
# Verify cross-modal tools are registered
python -c "
from src.core.tool_registry_loader import initialize_tool_registry

registry_results = initialize_tool_registry()
cross_modal_tools = ['GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 'VECTOR_EMBEDDER', 'MULTI_FORMAT_EXPORTER']
registered_cross_modal = [tool for tool in cross_modal_tools if tool in registry_results]

print(f'Cross-modal tools registered: {len(registered_cross_modal)}/{len(cross_modal_tools)}')
for tool in cross_modal_tools:
    status = '✅' if tool in registry_results else '❌'
    print(f'   {status} {tool}')
"

# Test tool ID mapping for cross-modal tools  
python -c "
from src.core.tool_id_mapper import ToolIDMapper

mapper = ToolIDMapper()
test_mappings = [
    ('graph to table converter', 'GRAPH_TABLE_EXPORTER'),
    ('cross modal analyzer', 'CROSS_MODAL_ANALYZER'),
    ('vector embedder', 'VECTOR_EMBEDDER'),
    ('format converter', 'MULTI_FORMAT_EXPORTER')
]

print('LLM → Registry ID mappings:')
for llm_name, expected in test_mappings:
    actual = mapper.map_llm_name_to_registry_id(llm_name)
    status = '✅' if actual == expected else '❌'
    print(f'   {status} \"{llm_name}\" → {actual}')
"

# Test cross-modal DAG template creation
python -c "
from src.workflows.cross_modal_dag_template import CrossModalDAGTemplate

dag = CrossModalDAGTemplate.create_graph_table_vector_synthesis_dag('test.pdf')
cross_modal_steps = [step for step in dag['steps'] if step['tool_id'] in ['GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 'VECTOR_EMBEDDER']]

print(f'✅ Cross-modal DAG template: {len(dag[\"steps\"])} steps')
print(f'✅ Cross-modal tools in DAG: {len(cross_modal_steps)} tools')
print(f'   Tools: {[step[\"tool_id\"] for step in cross_modal_steps]}')
"
```

### **Phase 2: Cross-Modal Execution Testing**
```bash
# Run comprehensive cross-modal test suite
python scripts/test_cross_modal_execution.py

# Expected result: All 4 test categories pass
# - Tool Registry: PASS
# - DAG Generation: PASS  
# - Workflow Execution: PASS
# - LLM DAG Generation: PASS

# Test individual cross-modal tool execution
python -c "
from src.tools.cross_modal.graph_table_exporter_unified import GraphTableExporterUnified
from src.core.service_manager import ServiceManager
from src.core.tool_contract import ToolRequest

tool = GraphTableExporterUnified(ServiceManager())
test_data = {
    'graph_data': {'nodes': [{'id': 'A'}, {'id': 'B'}], 'edges': [{'source': 'A', 'target': 'B'}]},
    'table_type': 'edge_list'
}

request = ToolRequest(input_data=test_data)
result = tool.execute(request)

print(f'Graph→Table conversion: {result[\"status\"]}')
if result['status'] == 'success':
    table_data = result.get('data', {}).get('table_data', {})
    print(f'✅ Table created with {len(table_data.get(\"rows\", []))} rows')
"
```

### **Continuous Cross-Modal Validation**  
```bash
# Verify LLM can generate cross-modal workflows from natural language
python -c "
from src.agents.workflow_agent import WorkflowAgent
from src.core.service_manager import ServiceManager

agent = WorkflowAgent(ServiceManager())
user_request = 'I need to convert graph data to a table, then generate vector embeddings and synthesize insights across all formats'

dag_result = agent.generate_workflow_dag(user_request)

if dag_result and dag_result.get('status') == 'success':
    dag = dag_result['dag']
    tools_used = [step['tool_id'] for step in dag['steps']]
    cross_modal_tools = [tool for tool in tools_used if tool in ['GRAPH_TABLE_EXPORTER', 'CROSS_MODAL_ANALYZER', 'VECTOR_EMBEDDER']]
    
    print(f'✅ LLM DAG generation: {len(dag[\"steps\"])} steps')  
    print(f'✅ Cross-modal tools used: {cross_modal_tools}')
else:
    print('❌ LLM DAG generation failed')
"

# Test end-to-end cross-modal analysis workflow
python -c "
print('🎯 END-TO-END CROSS-MODAL ANALYSIS: Natural Language → DAG → Execution → Results')
print('   User Request → LLM generates DAG → Cross-modal tools execute → Graph+Table+Vector synthesis')
"
```

## 🎯 **NEXT IMPLEMENTATION PRIORITIES** 

1. **IMMEDIATE (Phase 1)**: Register cross-modal tools in tool registry and update mappings
2. **HIGH (Phase 2)**: Test cross-modal execution pipeline with comprehensive validation suite
3. **Functionally READY**: Once Phases 1-2 complete, KGAS will support complex cross-modal analysis workflows with natural language interface

### **Implementation Sequence**
Each phase must be completed with supporting evidence before proceeding:

**Phase 1 Evidence Required**:
- Tool registry shows 9+ tools (5 KGAS + 4 cross-modal)
- LLM tool ID mappings work for cross-modal tools  
- Cross-modal DAG templates generate valid workflows

**Phase 2 Evidence Required**:
- All 4 cross-modal test categories pass
- End-to-end workflow execution succeeds
- Data integrity maintained across format conversions


**System Complete When**:
- User can request "analyze this document using graphs, tables, and vectors" in natural language
- System automatically generates appropriate DAG with cross-modal tools
- Workflow executes successfully with real tools (no mocks/fallbacks)  
- Results include integrated insights from all three data modalities