# ADR-031: MCP Tool Exposure Strategy

## Status
**Tentative** - Based on experimental evidence, pending real-world validation

## Context

The KGAS system currently contains 36 registered tools with plans to scale to 121 tools. We need to expose these tools via the Model Context Protocol (MCP) for external AI agent consumption. Our investigation revealed critical limitations in MCP that fundamentally affect our architecture decisions:

### Key Findings from Research

1. **The 40-Tool Barrier**: While MCP has no theoretical limit on tool count, practical implementations like Cursor limit agents to ~40 tools due to LLM reasoning degradation. This is not a protocol limitation but a cognitive constraint of current LLMs.

2. **Token Tax**: Every tool description consumes tokens in the LLM context window. A set of 37 tools can consume 6,000+ tokens before processing the user's actual query, directly impacting cost and latency.

3. **Choice Paradox**: LLM accuracy degrades as the number of available tools increases. The probability of selecting the wrong tool increases with larger choice spaces.

4. **Security Considerations**: While MCP's security model has significant gaps (command injection, token theft, tool poisoning), we are explicitly choosing not to implement advanced security features at this stage as this is a research/academic system.

### Current System Architecture

- **Tool Registry**: 36 tools auto-registered via `ToolAutoRegistry`
- **Contract System**: YAML-based contracts for validation
- **MCP Implementation**: FastMCP framework with decomposed service architecture
- **Tool Diversity**: Tools range from simple (PDF loading) to complex (ontology-aware extraction)
- **Primary Model**: Gemini-2.5-flash (configurable)

## Decision

Based on comprehensive experimental testing with 100 mock MCP tools, we will implement a **Reference-Based Semantic Workflow Tool** strategy for MCP exposure with the following approach:

### Experimental Evidence Summary

Our controlled experiments compared 6 organization strategies across multiple scenarios:

| Strategy | Tools Exposed | Context Usage | Message Size | Performance |
|----------|---------------|---------------|--------------|-------------|
| **Direct Exposure** | 100 | 100.0% | 25,622 bytes | ❌ Hits limits |
| **Semantic Workflow** | 5-15 | 9.7% | 1,500 bytes | ✅ **Winner** |
| **Dynamic Filtering** | 10 | 32.4% | 3,158 bytes | ✅ Runner-up |
| **Reference-Based** | Variable | Low | ~600 bytes | ✅ Excellent |

**Key Findings:**
- Context window saturates at 40+ tools (confirmed "40-tool barrier")
- Semantic workflow approach shows 17x message size reduction
- Reference-based data flow leverages existing provenance system optimally
- Tool selection accuracy remains high with 10-15 semantic tools

### 1. High-Level Semantic Tools Only

Rather than exposing all 121 internal tools, we will create 10-15 high-level semantic workflow tools that encapsulate common user intents:

```python
# User-facing MCP tools (what agents see)
extract_knowledge_graph()      # Combines T23A, T23B, T23C, T27
build_graph_from_documents()   # Combines T01, T15A, T31, T34
analyze_graph_insights()        # Combines T49, T68, T50
export_analysis_results()      # Combines multiple export tools

# Internal tools remain hidden from MCP but available to workflows
```

### 2. Reference-Based Data Flow (Critical Innovation)

**All MCP tools work with data references instead of raw data**, leveraging our existing provenance system:

```python
@mcp.tool()
def extract_knowledge_graph(
    input_ref: str,  # Reference to input data (tracked by provenance)
    method: Literal["spacy", "llm", "hybrid"] = "hybrid",
    ontology_mode: Literal["open", "closed", "mixed"] = "mixed",
    extract_relations: bool = True,
    extract_properties: bool = True
) -> str:  # Returns reference to knowledge graph (tracked by provenance)
    """
    Extract comprehensive knowledge graph from referenced input.
    Routes internally to T23A_SPACY_NER, T23B_LLM_NER, or T23C_ONTOLOGY_AWARE
    based on parameters.
    
    Returns data reference for chaining with other tools.
    """
```

**Benefits of Reference-Based Approach:**
- Massive message size reduction (90%+ vs. raw data passing)
- Natural state management through existing provenance chains
- Enables complex multi-step workflows via reference chaining
- Scales to any data size without MCP message limits

### 3. Internal Router Pattern

Implement an internal routing layer that maps semantic tools to internal tool combinations:

```python
class MCPToolRouter:
    def route_to_internal_tools(self, mcp_tool: str, params: Dict) -> List[str]:
        """Map high-level MCP tool to internal tool pipeline"""
        if mcp_tool == "extract_knowledge_graph":
            if params["method"] == "spacy":
                return ["T23A_SPACY_NER", "T27_RELATIONSHIP_EXTRACTOR"]
            elif params["method"] == "llm":
                return ["T23B_LLM_NER"]  # Handles entities, relations, properties
            elif params["method"] == "hybrid":
                return ["T23C_ONTOLOGY_AWARE_EXTRACTOR"]
```

### 4. No Hierarchical Categories in MCP

MCP doesn't support hierarchical organization. Tools will use clear, descriptive names that indicate their workflow purpose:

- `extract_*` - Knowledge extraction workflows
- `build_*` - Graph construction workflows  
- `analyze_*` - Analysis and insights workflows
- `export_*` - Data export workflows
- `query_*` - Information retrieval workflows

### 5. Tool Discovery Documentation

Since MCP relies on docstrings for discovery, each tool will have comprehensive documentation:

```python
@mcp.tool()
def extract_knowledge_graph(...):
    """
    Extract entities, relationships, and properties to build a knowledge graph.
    
    Use Cases:
    - Research paper analysis: extract key concepts and relationships
    - Document intelligence: build semantic understanding of documents
    - Ontology population: extract instances for existing ontologies
    
    Methods:
    - "spacy": Fast, rule-based extraction using spaCy NLP
    - "llm": Comprehensive extraction using Gemini-2.5-flash
    - "hybrid": Combines NLP with ontology validation
    
    Returns structured knowledge graph with confidence scores.
    """
```

## Consequences

### Positive

1. **Cognitive Load Management**: Agents see only 10-15 tools, well within the 40-tool practical limit
2. **Token Efficiency**: Dramatically reduces context window consumption
3. **Higher Success Rates**: Simpler choice space improves tool selection accuracy
4. **Workflow Alignment**: Tools match user intent rather than technical implementation
5. **Maintainability**: Changes to internal tools don't break external MCP interface
6. **Scalability**: Can add internal tools without expanding MCP surface area

### Negative

1. **Loss of Granularity**: External agents cannot access specific low-level tools directly
2. **Parameter Complexity**: Each semantic tool has more parameters to learn
3. **Abstraction Overhead**: Additional routing layer adds complexity
4. **Discovery Challenge**: Users must understand which semantic tool encompasses their need

### Neutral

1. **Security Posture**: We acknowledge but do not address MCP security vulnerabilities
2. **Contract System**: Existing YAML contracts remain for internal validation only
3. **Tool Registry**: Internal auto-registration continues unchanged

## Implementation Notes

### Phase 1: Tool Mapping (Week 1)
- Analyze 121 planned tools to identify semantic workflows
- Group tools by user intent rather than technical function
- Design parameter schemas for flexibility

### Phase 2: Router Implementation (Week 2)
- Build `MCPSemanticRouter` class
- Map semantic tools to internal pipelines
- Implement parameter translation layer

### Phase 3: MCP Integration (Week 3)
- Update FastMCP server with semantic tools
- Write comprehensive docstrings
- Test with various MCP clients

### Not Implementing

Based on our analysis and current priorities:

1. **Security hardening** - No OAuth 2.0 Resource Indicators (RFC 8707)
2. **Tool versioning** - No formal version management system
3. **Agent Gateway** - No centralized security/governance layer
4. **RAG-for-tools** - No vector search pre-filtering (unnecessary with 15 tools)

### Note on Tentative Status

This ADR is marked **TENTATIVE** because it is based on controlled experiments with 100 mock MCP tools, not real-world validation with actual KGAS tools and external AI agents. The experimental evidence strongly supports this approach, but implementation requires:

1. **Real Tool Validation**: Testing with actual KGAS tools to confirm routing works correctly
2. **Agent Behavior Analysis**: Measuring how real AI agents (not our mock agents) perform tool selection
3. **Performance Validation**: Confirming simulated performance matches actual execution
4. **User Experience Testing**: Ensuring external developers can effectively use the semantic tools

The ADR will be updated to **ACCEPTED** after successful real-world validation demonstrates the approach works as expected.

## References

- [MCP Limitations Research](/home/brian/projects/Digimons/research/mcp_limitations.txt)
- [MCP Routing Experiments](/home/brian/projects/Digimons/experiments/mcp_routing/)
- [Experimental Results Summary](/home/brian/projects/Digimons/experiments/mcp_routing/EXPERIMENT_SUMMARY.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- Cursor's 40-tool limit discussions (community forums)
- Berkeley Function Calling Leaderboard (37 function maximum)

## Decision Makers

- Project Lead: Brian
- Date: 2025-08-04
- Review: Pending

## Related ADRs

- ADR-013: MCP Protocol Integration (defines basic MCP adoption)
- ADR-008: Core Service Architecture (defines internal tool structure)
- ADR-001: Phase Interface Design (defines tool contracts)