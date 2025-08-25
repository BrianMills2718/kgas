# MCP Tool Routing & Organization Experiments

## Purpose

This experiment suite tests different approaches to organizing and exposing tools via the Model Context Protocol (MCP) to determine the optimal strategy for handling large tool sets (100+ tools) while managing LLM cognitive constraints.

## Background

Research shows that LLMs experience reasoning degradation when presented with large tool choice spaces (the "40-tool barrier"). Our system has 36 current tools scaling to 121 planned tools. We need to determine the best organization strategy for MCP exposure.

## Experimental Variables

### Tool Organization Strategies

1. **Direct Exposure** (Baseline)
   - All 100+ tools exposed directly to MCP
   - Minimal abstraction
   - Tests raw LLM performance limits

2. **Reference-Based Tools**
   - Tools accept/return data references instead of raw data
   - Leverages existing provenance system for state
   - Small message sizes, complex workflows via chaining

3. **Semantic Workflow Tools**
   - 10-15 high-level workflow tools
   - Each tool encapsulates multiple internal tools
   - Parameters control internal routing

4. **Hierarchical Categories**
   - Tools grouped by function (extract/, build/, analyze/, query/)
   - MCP clients see organized structure
   - Tests if categorization helps tool selection

5. **Dynamic Tool Filtering**
   - RAG-for-tools approach
   - Vector search pre-filters relevant tools per query
   - Agent sees only 5-10 contextually relevant tools

6. **Agent Gateway Pattern**
   - Single MCP server acts as intelligent proxy
   - Routes to appropriate internal tool collections
   - Centralized optimization and caching

## Test Scenarios

### Scenario A: Simple Linear Workflows
- Document processing pipeline (load -> chunk -> extract -> build -> analyze)
- Measures baseline performance with different organization strategies
- Tests: completion rate, execution time, tool selection accuracy

### Scenario B: Complex Multi-Branch Workflows  
- Document comparison across multiple analysis dimensions
- Requires parallel execution and result merging
- Tests: workflow complexity handling, parallel optimization

### Scenario C: Adaptive Workflows
- Agent must adapt based on intermediate results
- Tests quality-based tool selection and strategy changes
- Example: Low-confidence entity extraction triggers LLM enhancement

### Scenario D: Scale Stress Testing
- Incrementally increase available tools (20, 40, 60, 80, 100, 121)
- Measure performance degradation curves
- Identify actual breaking points vs. theoretical limits  

### Scenario E: Real-World Query Patterns
- Process actual research questions from academic papers
- Tests practical applicability and tool discovery
- Measures answer quality and completeness

## Performance Metrics

### Primary Metrics
- **Task Completion Rate**: % of workflows completed successfully
- **Tool Selection Accuracy**: % of optimal tools chosen vs. suboptimal
- **Execution Time**: Total time from query to results
- **Message Size**: Average MCP message payload size

### Secondary Metrics  
- **Reasoning Degradation**: Quality decrease as tool count increases
- **Parallelization Efficiency**: Actual vs. theoretical speedup
- **Error Recovery**: Success rate when intermediate steps fail
- **Tool Discovery**: Can agents find appropriate tools for novel tasks?

### Cognitive Load Metrics
- **Decision Time**: Time LLM spends on tool selection
- **Context Window Usage**: % of context consumed by tool descriptions
- **Tool Confusion**: Frequency of similar tool misselection
- **Abandonment Rate**: % of workflows abandoned due to complexity

## Mock Tool Design

### Tool Categories (100 total)
- **Document Loaders** (12 tools): PDF, Word, CSV, JSON, HTML, XML, etc.
- **Text Processing** (15 tools): Chunking, cleaning, tokenization, etc.
- **Entity Extraction** (18 tools): SpaCy, LLM, hybrid, domain-specific variants
- **Relationship Analysis** (16 tools): Pattern-based, ML-based, ontology-aware
- **Graph Operations** (14 tools): Building, merging, analysis, visualization
- **Query Systems** (10 tools): Multi-hop, semantic, temporal, causal
- **Analytics** (8 tools): PageRank, clustering, anomaly detection
- **Export/Visualization** (7 tools): Multiple formats and visualizations

### Reference-Based Tool Pattern
```python
@mcp.tool()
def extract_entities_spacy(input_ref: str, confidence: float = 0.8) -> str:
    """Extract entities using SpaCy NLP from referenced text."""
    # Returns: entity_ref (tracked by provenance)
    
@mcp.tool()  
def enhance_entities_llm(entity_ref: str, method: str = "gemini") -> str:
    """Enhance entity extraction using LLM analysis."""
    # Returns: enhanced_entity_ref
```

### Workflow Tool Pattern
```python
@mcp.tool()
def analyze_document_comprehensive(
    document_path: str,
    analysis_depth: Literal["quick", "standard", "deep"] = "standard",
    focus_areas: List[str] = ["entities", "relationships", "patterns"]
) -> AnalysisResult:
    """Complete document analysis workflow."""
    # Internally routes to 8-12 tools based on parameters
```

## Expected Outcomes

### Hypothesis 1: Reference-Based Efficiency
Reference-based tools will show 90%+ reduction in message size while maintaining workflow flexibility, enabling complex multi-step processes without hitting context limits.

### Hypothesis 2: Semantic Tool Sweet Spot  
10-15 semantic workflow tools will optimize the trade-off between choice complexity and capability granularity, achieving highest completion rates.

### Hypothesis 3: Dynamic Filtering Scalability
RAG-for-tools approach will scale linearly with tool count, maintaining consistent performance even at 121 tools.

### Hypothesis 4: Agent Gateway Optimization
Centralized gateway will show best performance for complex workflows through intelligent caching and routing optimization.

### Hypothesis 5: Breaking Point Identification
We'll identify the actual tool count where each strategy breaks down, providing data-driven limits for deployment.

## Implementation Plan

### Phase 1: Mock Infrastructure (Week 1)
- Build 100 mock MCP tools across all categories
- Implement reference registry and provenance simulation
- Create test harness for automated scenario execution

### Phase 2: Organization Strategy Implementation (Week 2)  
- Implement all 6 organization strategies
- Build performance measurement framework
- Create standardized test scenarios

### Phase 3: Systematic Testing (Week 3)
- Execute all scenarios across all strategies
- Collect comprehensive performance data
- Analyze cognitive load and degradation patterns

### Phase 4: Analysis & Recommendations (Week 4)
- Statistical analysis of results
- Identify optimal strategies for different use cases
- Update ADR-031 with data-driven recommendations
- Plan production implementation

## Success Criteria

1. **Clear Winner Identification**: One strategy shows >20% better performance
2. **Scalability Validation**: At least one strategy handles 121 tools effectively  
3. **Breaking Point Data**: Precise identification of tool count limits per strategy
4. **Production Readiness**: Winning strategy can be implemented in current architecture
5. **Evidence-Based ADR**: ADR-031 updated with experimental data, not theory

This experiment will provide the empirical foundation for designing KGAS's MCP tool exposure strategy, ensuring we optimize for actual LLM behavior rather than theoretical constraints.