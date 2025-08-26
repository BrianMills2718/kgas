# Vertical Slice POC - Experimental Development

**Purpose**: Prove core concepts work before attempting framework integration
**Location**: `/experiments/vertical_slice_poc/`
**Status**: Starting experimental phase
**Date**: 2025-01-26

## Why Experiments First?

Before integrating into the main codebase with its 10 IdentityService implementations and complex service dependencies, we need to **prove the basic approach works** with simple, standalone scripts.

## Core Questions We're Answering

1. **Can we extract a knowledge graph with uncertainty from an LLM in one call?**
2. **Can we actually persist this to Neo4j without issues?**
3. **Can we export graph metrics to SQLite for cross-modal analysis?**
4. **Does uncertainty propagation work as expected?**
5. **Only then: Can we wrap this in the extensible framework?**

## Experiment Structure

```
/experiments/vertical_slice_poc/
├── CLAUDE.md                    # This file - the plan
├── requirements.txt             # Minimal dependencies
├── config.py                    # Shared configuration
├── 
├── 01_basic_extraction/         # Can we extract KG with uncertainty?
│   ├── extract_kg.py           
│   ├── test_chunking.py        
│   ├── test_document.txt       
│   └── outputs/                
│
├── 02_neo4j_persistence/       # Can we write to Neo4j properly?
│   ├── persist_to_neo4j.py     
│   ├── verify_neo4j.py         
│   ├── clean_neo4j.py          
│   └── issues.md               
│
├── 03_uncertainty_test/        # Does uncertainty work as expected?
│   ├── extract_with_uncertainty.py
│   ├── propagate_uncertainty.py
│   ├── test_deterministic.py  
│   └── results.md
│
└── 04_framework_integration/   # Only after 1-3 work
    ├── with_framework.py
    ├── without_framework.py
    └── comparison.md
```

## Experiment 01: Basic Knowledge Graph Extraction

### Goal
Extract a knowledge graph from real text using an LLM, including uncertainty assessment in a single call.

### Key Questions
- Which LLM gives best results? (GPT-4, Claude, Gemini?)
- What prompt format works best?
- Does the LLM reliably return uncertainty?
- How consistent are extractions across runs?
- How do we handle text longer than context window?

### Implementation Plan
```python
# Simplest possible extraction - no framework, no services
def extract_knowledge_graph(text: str) -> dict:
    """Direct LLM call to extract KG with uncertainty"""
    prompt = f"""
    Extract a knowledge graph from this text.
    
    Return JSON with:
    {{
      "entities": [
        {{"id": "unique_id", "name": "Entity Name", "type": "person|org|location|event|concept", "properties": {{}}}}
      ],
      "relationships": [
        {{"source": "entity_id", "target": "entity_id", "type": "RELATIONSHIP_TYPE", "properties": {{}}}}
      ],
      "uncertainty": 0.0-1.0,
      "reasoning": "explanation of uncertainty"
    }}
    
    Text: {text}
    """
    # Direct API call - no abstraction layers
```

### Success Criteria
- [ ] Extracts entities AND relationships in one call
- [ ] Returns valid JSON consistently
- [ ] Includes uncertainty and reasoning
- [ ] Handles 5-page document via chunking
- [ ] Runs 5 times with consistent results

### Test Document
Start with a simple news article about a company acquisition - clear entities and relationships.

## Experiment 02: Neo4j Persistence

### Goal
Write the extracted knowledge graph to Neo4j, creating actual Entity nodes (fixing the current bug).

### Key Questions
- How do we handle connection management?
- What's the right Cypher for MERGE vs CREATE?
- How do we handle duplicate entities across chunks?
- What about relationship properties?
- Transaction management?

### Implementation Plan
```python
def persist_to_neo4j(kg_data: dict) -> dict:
    """Direct Neo4j writes - no IdentityService"""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    
    with driver.session() as session:
        # Create entities (FIXING THE BUG - actually create Entity nodes!)
        for entity in kg_data['entities']:
            session.run("""
                MERGE (e:Entity {canonical_name: $name})
                ON CREATE SET e.id = $id, e.type = $type
                SET e += $properties
            """, name=entity['name'], id=entity['id'], 
                type=entity['type'], properties=entity.get('properties', {}))
```

### Success Criteria
- [ ] Successfully connects to Neo4j
- [ ] Creates Entity nodes (not just Mentions)
- [ ] Handles properties correctly
- [ ] Creates relationships with properties
- [ ] Can query back what was written
- [ ] Handles updates without duplicates

## Experiment 03: Uncertainty Testing

### Goal
Implement and validate uncertainty propagation through the pipeline.

### Key Questions
- How do we get consistent uncertainty from LLMs?
- What uncertainty values for TextLoader operations?
- How to verify GraphPersister has 0.0 uncertainty on success?
- Does the physics model combination work?

### Implementation Plan
```python
# Test uncertainty at each step
def test_uncertainty_propagation():
    # Step 1: TextLoader uncertainty (configurable constants)
    text_uncertainty = {"pdf": 0.15, "txt": 0.02}["pdf"]
    
    # Step 2: KG extraction uncertainty (from LLM)
    kg_uncertainty = kg_data['uncertainty']  # e.g., 0.25
    
    # Step 3: GraphPersister uncertainty (0.0 on success)
    persist_uncertainty = 0.0 if all_writes_succeeded else calculate_failure_rate()
    
    # Combine using physics model
    confidence = (1 - text_uncertainty) * (1 - kg_uncertainty) * (1 - persist_uncertainty)
    total_uncertainty = 1 - confidence
    
    assert total_uncertainty == expected  # What IS expected?
```

### Success Criteria
- [ ] TextLoader uses configurable constants
- [ ] KG extractor returns uncertainty from LLM
- [ ] GraphPersister has 0.0 uncertainty on success
- [ ] Combined uncertainty follows physics model
- [ ] Reasoning is preserved through pipeline

## Experiment 04: Framework Integration

### Goal
Only after experiments 1-3 work, wrap in the extensible framework.

### Key Questions
- How does type-based discovery work with our tools?
- Can framework find the chain automatically?
- Does semantic type checking prevent invalid chains?
- Performance overhead of framework?

### Implementation Plan
```python
# Compare with and without framework
from framework import ExtensibleTool, ToolFramework

class KnowledgeGraphExtractor(ExtensibleTool):
    def get_capabilities(self):
        return ToolCapabilities(
            input_type=DataType.TEXT,
            output_type=DataType.KNOWLEDGE_GRAPH,
            input_construct="document_text",
            output_construct="knowledge_graph"
        )
    
    def process(self, text, context):
        # Wrap our proven extraction logic
        return extract_knowledge_graph(text)
```

### Success Criteria
- [ ] Framework discovers chain automatically
- [ ] Same results as standalone scripts
- [ ] Uncertainty propagates correctly
- [ ] Semantic types work as expected
- [ ] No significant performance overhead

## Dependencies

```txt
# requirements.txt
neo4j==5.14.0          # Neo4j driver
openai==1.6.0          # For GPT-4
anthropic==0.8.0       # For Claude
google-generativeai==0.3.0  # For Gemini
python-dotenv==1.0.0   # For API keys
pandas==2.1.0          # For data manipulation
```

## Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = "openai"  # or "anthropic" or "google"
LLM_MODEL = "gpt-4-turbo-preview"
API_KEY = os.getenv(f"{LLM_PROVIDER.upper()}_API_KEY")

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# SQLite Configuration
SQLITE_PATH = "experiments.db"

# Uncertainty Constants
TEXT_UNCERTAINTY = {
    "pdf": 0.15,
    "txt": 0.02,
    "html": 0.12,
    "default": 0.10
}
```

## Validation Approach

### For Each Experiment:
1. **Start simple** - Hardcode everything
2. **Make it work** - Don't worry about clean code
3. **Document issues** - What broke? What was surprising?
4. **Iterate** - Fix issues, try again
5. **Only then** - Think about abstraction

### What We're NOT Doing Yet:
- Building services
- Creating frameworks
- Type checking
- Error handling
- Performance optimization
- Making it "clean"

## Success Metrics

### Experiment Success:
- Can extract KG from a 5-page document
- Can persist to Neo4j with Entity nodes
- Can export metrics to SQLite
- Uncertainty propagation works
- All without framework complexity

### Ready for Integration When:
- All 4 experiments pass success criteria
- We understand the failure modes
- We have solutions for chunking, merging, deduplication
- Uncertainty values are reasonable and consistent

## Common Pitfalls to Avoid

1. **Don't abstract too early** - Prove it works first
2. **Don't ignore failures** - Document what breaks
3. **Don't assume LLM consistency** - Test multiple runs
4. **Don't skip verification** - Actually check Neo4j/SQLite
5. **Don't overcomplicate** - Simple scripts first

## Next Steps

1. Create `requirements.txt` with minimal dependencies
2. Create `config.py` with connection details
3. Start with `01_basic_extraction/extract_kg.py`
4. Use a real but simple test document
5. See what actually happens

## Questions to Answer Before Production

- **LLM Choice**: Which provider gives best KG extraction?
- **Prompt Engineering**: What prompt format is most reliable?
- **Chunking Strategy**: How to merge partial graphs?
- **Entity Resolution**: When to merge vs create new?
- **Property Handling**: How to handle nested/complex properties?
- **Error Recovery**: What to do when one chunk fails?
- **Performance**: How long for a 100-page document?
- **Cost**: How much per document?

## Current Status

- [ ] Experiment 01: Basic extraction
- [ ] Experiment 02: Neo4j persistence  
- [ ] Experiment 03: Uncertainty testing
- [ ] Experiment 04: Framework integration

**Next Action**: Create extract_kg.py and test with real document

---

*Remember: We're proving concepts, not building production code. Keep it simple.*