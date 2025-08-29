# KGAS Thesis Requirements & System Goals
*Captured: 2025-08-29*
*Source: Direct from thesis author*

## 🎯 Core System Requirements

### Primary Goal
Build an **extensible, modular tool suite** that combines capabilities of:
- **StructGPT** - Structure-aware question answering over heterogeneous data
- **GraphRAG** - Graph-enhanced retrieval and reasoning

### Key Capabilities Required

#### 1. Data Format Flexibility
- **Tables**: Any tabular format (CSV, SQL, Excel, etc.)
- **Graphs**: Any graph format (Neo4j, NetworkX, RDF, etc.)
- **Vectors**: Embeddings and vector operations
- **Text**: Natural language documents
- **Structured Text**: CSV files, tweets, logs, etc.

#### 2. Ingestion & Structuring
- Ingest unstructured/semi-structured data (text, CSV, tweets)
- Automatically structure according to content
- Adapt structure based on analytic needs

#### 3. Dynamic Tool Chain Creation
- **Agentic evaluation** of:
  - Analytic goals (what user wants to know)
  - Available tools (what system can do)
- **Automatic composition** of tool chains to meet goals
- **On-the-fly creation** - not pre-defined pipelines

#### 4. Tool Chain Requirements
Every tool chain MUST have:
- **Full Provenance**: Track every operation and data transformation
- **Uncertainty Quantification**: Each tool reports confidence/uncertainty
- **Uncertainty Propagation**: Compound uncertainty through chain
- **Reasoning Traces**: Explainable decisions at each step

## 🏗️ Architectural Implications

### Tool Framework Needs
1. **Common Interface**: All tools speak same protocol
2. **Composability**: Any tool can connect to any compatible tool
3. **Extensibility**: Easy to add new tools without breaking system
4. **Metadata Flow**: Preserve context through entire chain

### Data Model Requirements
1. **Multi-Modal**: Handle text, tables, graphs, vectors in single pipeline
2. **Format Agnostic**: Abstract away specific formats
3. **Semantic Preservation**: Don't lose meaning in transformations

### Intelligence Layer
1. **Goal Understanding**: Parse analytic objectives
2. **Tool Discovery**: Know what each tool can do
3. **Chain Planning**: Find optimal path from input to goal
4. **Dynamic Execution**: Adapt plan based on intermediate results

## ✅ What We've Proven So Far

### Working
- ✅ Basic tool chaining (VectorTool → TableTool)
- ✅ Tool registration with capabilities
- ✅ Simple chain discovery
- ✅ Adapter pattern for integration

### Not Working Yet
- ❌ Uncertainty propagation (hardcoded to 0.0)
- ❌ Reasoning traces (just template strings)
- ❌ Provenance tracking (code exists, not verified)
- ❌ Multi-modal handling (only text→vector→table)
- ❌ Dynamic goal evaluation
- ❌ Graph operations
- ❌ Complex structuring

## 📊 Success Metrics

### Functional Success
1. Can ingest tweet CSV and build knowledge graph
2. Can answer questions requiring multi-hop graph traversal
3. Can combine vector similarity with graph structure
4. Can explain reasoning path taken

### Technical Success
1. Uncertainty changes meaningfully through pipeline
2. Provenance allows full reproducibility
3. New tools integrate without changing framework
4. System selects appropriate tools for task

### Research Success
1. Demonstrates advantage over pure LLM approaches
2. Shows when structure helps vs. when it doesn't
3. Quantifies uncertainty in knowledge extraction
4. Provides interpretable reasoning

## 🚀 Minimum Viable System

### Phase 1: Foundation (Current)
- [x] Basic tool framework
- [x] Simple chaining
- [ ] Real uncertainty model
- [ ] Verified provenance

### Phase 2: Multi-Modal
- [ ] Text → Graph extraction
- [ ] Table → Graph conversion
- [ ] Vector similarity tools
- [ ] Graph analysis tools

### Phase 3: Intelligence
- [ ] Goal parser
- [ ] Tool capability registry
- [ ] Dynamic chain planner
- [ ] Execution engine

### Phase 4: Production Features
- [ ] Error recovery
- [ ] Partial results
- [ ] Performance optimization
- [ ] UI/API

## 🎓 Thesis Alignment

This system would demonstrate:

1. **Modularity Advantage**: Complex analysis via simple, composable tools
2. **Uncertainty Value**: Knowing confidence improves decision-making
3. **Structure Benefits**: When/how structure improves over pure text
4. **Explainability**: Full reasoning traces for trustworthy AI
5. **Flexibility**: Same system handles diverse data and queries

## 📝 Not Required for Thesis

Based on clarification, these are NOT required:
- Specific performance benchmarks
- Comparison with all existing systems
- Production-ready deployment
- Specific deadline/timeline
- Perfect entity resolution
- Complete error handling

## 🔬 Research Questions System Could Answer

1. When does structured representation improve QA accuracy?
2. How does uncertainty propagation affect result confidence?
3. Can modular tools match end-to-end trained systems?
4. What's the value of provenance in analytic workflows?
5. How do reasoning traces affect user trust?

---

## Next Steps

With these requirements clear, we should:

1. **Fix uncertainty propagation** - Make it real, not hardcoded
2. **Verify provenance tracking** - Ensure it actually works
3. **Add graph tools** - Critical for GraphRAG-like capabilities
4. **Build goal evaluator** - For dynamic chain creation
5. **Create real reasoning traces** - Not just templates

The vertical slice approach is RIGHT - we just need to:
- Add real uncertainty
- Add more tool types (graph, table)
- Build the intelligence layer
- Verify all claims with evidence