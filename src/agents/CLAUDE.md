# Agents Module - CLAUDE.md

## Overview
The `src/agents/` directory contains intelligent agents that handle workflow generation and tool orchestration through natural language processing and DAG construction.

## Architecture Clarification (2025-08-05)

### Tool Selection vs Mode Selection (CORRECTED)
**Core Principle**: Mode selection is implicit in tool DAG creation, not a separate process.

**How It Actually Works**:
1. **User Input**: Natural language analytic question (e.g., "What companies does John Smith work for?")
2. **Agent Analysis**: LLM agent examines available tools and constructs DAG of tool calls
3. **Implicit Mode Definition**: Tool sequence defines data modes at each step
   - T01 (PDF Loader) → produces Text
   - T23a (Entity Extractor) → produces Graph entities  
   - T27 (Relationship Extractor) → produces Graph relationships
   - T31/T34 (Graph Builders) → produces Neo4j Graph
   - T91 (Graph→Table) → produces Table format
   - T95 (Table→Vector) → produces Vector embeddings
4. **Output**: Result of final tool call in DAG

**No Separate Mode Selection Required**: 
- Cross-modal conversions happen through tool transitions
- Each tool knows its input/output formats
- DAG implicitly defines the data flow: Graph → Table → Vector → etc.

## Current Implementation Status

### WorkflowAgent (`workflow_agent.py`)
**Purpose**: Convert natural language descriptions into executable tool DAGs

**Key Features**:
- **Multi-Layer Interface**: 3 layers of automation (full auto, user review, manual YAML)
- **LLM Integration**: Uses Gemini 2.5 Flash for intelligent workflow generation
- **Tool Registry Integration**: Knows all available tools and their capabilities
- **DAG Construction**: Creates directed acyclic graphs of tool execution
- **Workflow Validation**: Validates generated workflows before execution

**Architecture Pattern**:
```python
class WorkflowAgent:
    """Intelligent agent for workflow generation from natural language"""
    
    def generate_workflow(self, request: AgentRequest) -> AgentResponse:
        """Convert natural language to executable DAG of tool calls"""
        # 1. Analyze user request
        # 2. Examine available tools
        # 3. Construct tool DAG
        # 4. Validate workflow
        # 5. Return executable workflow
```

### Agent Layers

#### Layer 1: Full Automation
- Agent generates workflow DAG and executes immediately
- No user intervention required
- Suitable for standard analysis patterns

#### Layer 2: User Review  
- Agent generates workflow DAG for user review
- User can modify YAML before execution
- Balances automation with control

#### Layer 3: Manual YAML
- User writes workflow YAML directly
- Agent provides templates and guidance
- Maximum user control over tool orchestration

### Tool DAG Construction Process

The agent follows this process to create tool DAGs:

1. **Parse Natural Language**: Extract intent, entities, and desired outputs
2. **Tool Analysis**: Examine available tools and their input/output formats
3. **DAG Generation**: Create sequence of tool calls that achieves the goal
4. **Format Validation**: Ensure tool outputs match next tool inputs
5. **Mode Inference**: Data modes are implicit from tool sequence

**Example DAG Generation**:
```yaml
# User: "Analyze this PDF and find relationships between people"
# Generated DAG:
steps:
  - step_id: "load_pdf"
    tool_id: "T01_PDF_LOADER"
    output_format: "text"
    
  - step_id: "extract_entities" 
    tool_id: "T23A_SPACY_NER"
    depends_on: ["load_pdf"]
    input_format: "text"
    output_format: "graph_entities"
    
  - step_id: "extract_relationships"
    tool_id: "T27_RELATIONSHIP_EXTRACTOR" 
    depends_on: ["extract_entities"]
    input_format: "text_with_entities"
    output_format: "graph_relationships"
    
  - step_id: "build_graph"
    tool_id: "T31_ENTITY_BUILDER"
    depends_on: ["extract_relationships"]
    input_format: "entities_and_relationships"
    output_format: "neo4j_graph"
```

### Cross-Modal Tool Integration

**Cross-Modal Conversions**: Handled automatically through tool transitions in DAG

**Format Chain Examples**:
- **Text → Graph**: T01 (PDF) → T23a (NER) → T31 (Graph Builder)
- **Graph → Table**: T68 (PageRank) → T91 (Graph to Table Export)
- **Table → Vector**: T95 (Table to Vector) → T96 (Vector Embeddings)
- **Vector → Graph**: T97 (Vector Clustering) → T98 (Cluster to Graph)

**Lossless Conversion Principle**: Each tool preserves semantic information in format transitions.

## Usage Patterns

### Basic Workflow Generation
```python
from src.agents.workflow_agent import WorkflowAgent

agent = WorkflowAgent()
request = AgentRequest(
    natural_language_description="Analyze PDF for entity relationships",
    layer=AgentLayer.LAYER_2,
    available_documents=["document.pdf"]
)

response = agent.generate_workflow(request)
# Returns executable YAML workflow DAG
```

### Custom Tool DAG Creation
```python
# For advanced users who want specific tool sequences
workflow_yaml = """
metadata:
  name: "Custom Analysis Pipeline"
  
steps:
  - step_id: "pdf_load"
    tool_id: "T01_PDF_LOADER"
    # ... tool parameters
    
  - step_id: "entity_extract"
    tool_id: "T23C_ONTOLOGY_AWARE"  # Use advanced extractor
    depends_on: ["pdf_load"]
    # ... parameters
"""

execution = agent.execute_workflow_from_yaml(workflow_yaml, inputs)
```

## Integration Points

### Tool Registry Integration
- **Tool Discovery**: Agent knows all available tools and their capabilities
- **Contract Validation**: Ensures tool inputs/outputs are compatible
- **Format Matching**: Validates data format compatibility in DAG

### Workflow Engine Integration  
- **Execution**: Executes generated DAGs through workflow engine
- **Monitoring**: Tracks execution progress and errors
- **Result Aggregation**: Combines results from multiple tool executions

### Service Manager Integration
- **Service Access**: Access to core services through service manager
- **Resource Management**: Manages tool initialization and cleanup
- **Error Handling**: Centralized error handling for workflow execution

## Configuration

### Agent Configuration
```python
# Agent can be configured with different LLM backends
agent = WorkflowAgent(api_client=enhanced_api_client)

# Or use service manager integration
from src.core.service_manager import get_service_manager
service_manager = get_service_manager()
agent = WorkflowAgent(api_client=service_manager.enhanced_api_client)
```

### Workflow Templates
The agent uses predefined templates for common patterns:
- **PDF Analysis**: Standard document processing pipeline
- **Multi-Document Fusion**: Cross-document analysis workflows
- **Graph Analysis**: Pure graph analysis workflows
- **Custom**: User-defined workflow patterns

## Testing and Validation

### Agent Testing
```python
# Test workflow generation
def test_workflow_generation():
    agent = WorkflowAgent()
    request = AgentRequest(
        natural_language_description="Find relationships in PDF",
        layer=AgentLayer.LAYER_2
    )
    
    response = agent.generate_workflow(request)
    assert response.status == "requires_review"
    assert response.generated_workflow is not None
    assert len(response.generated_workflow.steps) > 0
```

### DAG Validation
```python  
# Test DAG structure
def test_dag_structure():
    # Verify tool sequence makes sense
    # Check input/output format compatibility  
    # Validate dependencies are correct
    # Ensure no circular dependencies
```

## Common Commands

### Agent Testing Commands
```bash
# Test workflow agent
python -c "from src.agents.workflow_agent import WorkflowAgent; agent = WorkflowAgent(); print('WorkflowAgent initialized')"

# Test workflow generation
python -c "
from src.agents.workflow_agent import WorkflowAgent, AgentRequest, AgentLayer
agent = WorkflowAgent()
request = AgentRequest(
    natural_language_description='Analyze PDF for entities',
    layer=AgentLayer.LAYER_2
)
response = agent.generate_workflow(request)
print(f'Workflow generation: {response.status}')
"

# List available workflow templates
python -c "from src.agents.workflow_agent import WorkflowAgent; agent = WorkflowAgent(); print(agent.get_workflow_templates())"
```

### Workflow Execution Commands
```bash
# Execute workflow from YAML
python -c "
from src.agents.workflow_agent import WorkflowAgent
agent = WorkflowAgent()
yaml_content = '''
metadata:
  name: Test Workflow
steps:
  - step_id: test
    tool_id: T01_PDF_LOADER
'''
result = agent.execute_workflow_from_yaml(yaml_content, {})
print(f'Execution: {result[\"status\"]}')
"
```

## Troubleshooting

### Common Issues
1. **LLM API Unavailable**: Agent falls back to mock client with clear error messages
2. **Tool Registry Empty**: Check that tools are properly registered  
3. **Invalid DAG**: Workflow validation will catch dependency issues
4. **Format Mismatches**: Tool contract validation prevents incompatible tool sequences

### Debug Commands
```bash
# Check available tools
python -c "from src.core.tool_contract import get_tool_registry; registry = get_tool_registry(); print(f'Tools: {len(registry.list_tools())}')"

# Validate workflow schema
python -c "from src.core.workflow_schema import validate_workflow; print('Workflow schema validation available')"

# Test LLM integration
python -c "from src.core.enhanced_api_client import EnhancedAPIClient; client = EnhancedAPIClient(); print('API client available')"
```

## Implementation Notes

### Key Design Decisions
1. **Mode Selection Eliminated**: Tool DAG implicitly defines data modes
2. **Three Layer Architecture**: Balances automation with user control
3. **LLM-Driven Generation**: Uses advanced language models for intelligent workflow creation
4. **Contract-Based Validation**: Ensures tool compatibility through formal contracts
5. **Template System**: Provides starting points for common analysis patterns

### Future Enhancements
- **Learning from Execution**: Improve DAG generation based on execution results
- **Performance Optimization**: Cache generated workflows for similar requests  
- **Multi-Modal Input**: Support image/video analysis workflow generation
- **Collaborative Editing**: Multi-user workflow development capabilities