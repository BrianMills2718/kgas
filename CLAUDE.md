# Extensible Tool Composition Framework - Integration & Validation Phase

## 1. Coding Philosophy (MANDATORY)

### Core Principles
- **NO LAZY IMPLEMENTATIONS**: No mocking/stubs/fallbacks/pseudo-code/simplified implementations
- **FAIL-FAST PRINCIPLES**: Surface errors immediately, don't hide them
- **EVIDENCE-BASED DEVELOPMENT**: All claims require raw evidence in structured evidence files  
- **TEST DRIVEN DESIGN**: Write tests first where possible

### Evidence Requirements
```
evidence/
├── current/
│   └── Evidence_Integration_[Task].md   # Current integration work only
├── completed/
│   ├── Evidence_Week1_*.md             # Framework features implemented
│   └── Evidence_POC_*.md               # Previous POC attempts
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Mark all untested components as "NOT TESTED"
- Must test with REAL services (Gemini API, Neo4j)

---

## 2. KGAS Uncertainty System - Core Principles (PERMANENT)

### Fundamental Design Decisions

#### 2.1 Subjective Expert Assessment is Intentional
- **Uncertainty scores ARE meaningful** - they represent the LLM's subjective expert assessment
- **0.30 means what the prompt defines** - typically "moderate confidence" 
- **Subjectivity mirrors human experts** - Social scientists routinely make subjective confidence assessments
- **NOT a calibrated measurement** - Not claiming 0.30 means 70% accurate in objective terms
- **Transparency over precision** - Reasoning explains the score, making subjectivity reviewable

#### 2.2 Dynamic Tool Generation from Theory Schemas
- **Tools generated at runtime** from theory papers, not pre-built
- **Theory schemas → LLM generates Python code** → Runtime compilation
- **Maintains fidelity** to theoretical specifications
- **Implementation choices documented** - When LLM chooses (e.g., cosine vs Euclidean distance), it's recorded with reasoning

#### 2.3 Localized Uncertainty, Not Global
- **Missing data affects only relevant tools** - 30% missing psychology scores → high uncertainty for psychology-dependent tools
- **Independent analyses unaffected** - Community detection works fine without psychology scores
- **Each tool assesses based on ITS needs** - Not global data coverage
- **Prevents cascade** of unnecessary uncertainty propagation

#### 2.4 Universal Uncertainty Schema
```python
class UniversalUncertainty(BaseModel):
    """Single uncertainty format for ALL operations"""
    uncertainty: float  # 0=certain, 1=uncertain
    reasoning: str  # Expert reasoning for assessment (CRITICAL)
    evidence_count: Optional[int]  # For aggregations
    data_coverage: Optional[float]  # Fraction of needed data
```

#### 2.5 Dempster-Shafer for Aggregation Only
- **USE D-S for**: Multiple tweets → user belief, Users → community, Cross-modal synthesis (3+ evidences)
- **DON'T USE D-S for**: Individual tool uncertainty, Sequential chains, Single evidence
- **Computationally trivial** - Just multiplication and addition, O(n) complexity
- **Convergent evidence reduces uncertainty** - Agreement across sources increases confidence

#### 2.6 The Reasoning Field is Critical
Every uncertainty assessment MUST include comprehensive reasoning that:
- Explains what factors were considered
- Justifies the uncertainty score  
- Documents assumptions made
- Notes what evidence would reduce uncertainty
- Provides enough detail for review and reproducibility

#### 2.7 System Identity: Expert Reasoning Trace System
**What this IS**:
- An expert reasoning trace system
- Makes computational social science transparent
- Documents all analytical decisions
- Embeds expert judgment reproducibly

**What this is NOT**:
- A calibrated measurement instrument
- A predictive model
- A causal inference system
- A claim to objective truth

---

## 3. Active Work Tracking

**CRITICAL**: See `/CLAUDE_CURRENT.md` for all active work streams and current status.

### Current Focus (2025-08-26)
1. **KGAS Integration** - Phase 1 of SIMPLIFIED_INTEGRATION_PLAN (1/6 tools working)
2. **Uncertainty System** - Design complete, POC successful
3. **Vertical Slice** - POC complete in `/experiments/vertical_slice_poc/`
4. **Framework Integration** - Needs connection to real tools

## 4. Codebase Structure

### Active Work Locations
- **Integration Plan**: `/docs/architecture/architecture_review_20250808/SIMPLIFIED_INTEGRATION_PLAN.md`
- **Current Status**: `/CLAUDE_CURRENT.md` (tracks all work streams)
- **Vertical Slice POC**: `/experiments/vertical_slice_poc/` (COMPLETE)
- **Evidence**: `/evidence/current/` (active work)

### Framework Entry Points
- `/tool_compatability/poc/framework.py` - Main extensible framework
- `/tool_compatability/poc/test_framework_extensibility.py` - Framework demo
- `/tool_compatability/poc/proof_of_concept.py` - **TO CREATE**: Real integration test

### Core Framework Components
```
tool_compatability/poc/
├── framework.py           # 🎯 MAIN: Extensible Tool Composition Framework
├── base_tool.py          # Base class with metrics
├── base_tool_v2.py       # Enhanced with ToolContext support
├── data_types.py         # 10 semantic types
├── tool_context.py       # ✅ Multi-input support
├── schema_versions.py    # ✅ Schema versioning & migration
├── semantic_types.py     # ✅ Semantic compatibility checking
├── data_references.py    # ✅ Memory management (streaming/references)
├── registry.py           # Original registry (being replaced by framework)
└── tools/
    ├── text_loader.py            # Basic file loader
    ├── entity_extractor.py       # Uses Gemini API
    ├── graph_builder.py          # Uses Neo4j
    ├── entity_extractor_v2.py    # Multi-input version
    └── streaming_text_loader.py  # Memory-efficient version
```

### Integration Points
- **Gemini API**: via `litellm` in EntityExtractor
  - API key in `/home/brian/projects/Digimons/.env` (auto-loads via python-dotenv)
- **Neo4j**: via `neo4j-driver` in GraphBuilder
  - Docker container: `bolt://localhost:7687` (neo4j/devpassword)

### Related Documentation
- `/tool_compatability/poc/README.md` - Original POC design
- `/tool_compatability/poc/CRITICAL_ISSUES_POC_PLAN.md` - 5 critical issues identified
- `/tool_compatability/poc/PHD_IMPLEMENTATION_PLAN.md` - 4-week PhD plan
- `/tool_compatability/the_real_problem.md` - Root cause analysis
- `/tool_compatability/tool_disposition_plan.md` - Migration strategy for 38 tools

---

## 3. Current Status: EXPERIMENTAL PHASE - PROVING CONCEPTS

### ✅ Completed (Week 1)
1. **Multi-input support**: ToolContext passes ontologies/parameters
2. **Schema versioning**: Auto-migration between versions
3. **Memory management**: Streaming for 50MB+ files  
4. **Semantic types**: Domain-aware compatibility checking
5. **Framework design**: Extensible framework created

### ✅ Experimental POC Success (2025-01-26)
**Location**: `/experiments/vertical_slice_poc/`
1. **KG Extraction Works**: Successfully extracted 27 entities, 22 relationships with 0.25 uncertainty using Gemini API
2. **Neo4j Persistence Works**: 100% success rate persisting to Neo4j with actual Entity nodes (fixed bug)
3. **No Mocks**: Used real Gemini API and real Neo4j database
4. **Evidence**: Full logs in `evidence/current/Evidence_Integration_POC_Success.md`

### 🚧 In Progress
- **Experiment 03**: Testing uncertainty propagation through pipeline
- **Experiment 04**: Framework integration (after Exp 03 succeeds)

### What Actually Works
- Direct KG extraction with uncertainty from LLM (proven)
- Neo4j persistence with Entity nodes (proven)
- Framework can register tools and discover chains (not yet integrated with proven approach)

---

## 4. Task: Integration Proof of Concept

### Objective
Prove the framework works with real tools and real services, not just in theory.

### Success Criteria
1. Execute ONE complete chain: File → Entities → Graph
2. Use REAL Gemini API (no mocks)
3. Write to REAL Neo4j (verifiable)
4. At least 2 framework features working (e.g., semantic types + streaming)

### Implementation Steps

#### Step 1: Create Real Test Data (15 minutes)

**File**: Create `/tool_compatability/poc/test_data/medical_article.txt`

```bash
# Download real medical content
curl -s "https://en.wikipedia.org/wiki/Myocardial_infarction" | \
  python3 -c "import sys, html2text; print(html2text.html2text(sys.stdin.read()))" | \
  head -500 > test_data/medical_article.txt

# Verify it has medical content
grep -i "cardiac\|heart\|myocardial" test_data/medical_article.txt
```

**Evidence Required**: `evidence/current/Evidence_Integration_TestData.md`
- Show file created with actual medical content
- Confirm size and content sample

#### Step 2: Verify Services (30 minutes)

**File**: Create `/tool_compatability/poc/verify_services.py`

```python
#!/usr/bin/env python3
"""Verify Gemini and Neo4j are accessible with real operations"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/brian/projects/Digimons/.env')

def test_gemini():
    """Test Gemini API with real extraction"""
    import litellm
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "No GEMINI_API_KEY"
    
    try:
        response = litellm.completion(
            model="gemini/gemini-2.0-flash-exp",
            messages=[{
                "role": "user", 
                "content": "Extract medical entities from: 'Patient diagnosed with acute myocardial infarction, prescribed aspirin and metoprolol'"
            }],
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        
        # Check if real entities found
        has_disease = "myocardial" in content.lower() or "infarction" in content.lower()
        has_medication = "aspirin" in content.lower() or "metoprolol" in content.lower()
        
        if has_disease and has_medication:
            return True, f"Extracted entities: {content[:100]}..."
        else:
            return False, f"No medical entities found in: {content}"
            
    except Exception as e:
        return False, f"API call failed: {str(e)}"

def test_neo4j():
    """Test Neo4j with real write and read"""
    from neo4j import GraphDatabase
    
    try:
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "devpassword")
        )
        
        # Clear test data
        with driver.session() as session:
            session.run("MATCH (n:TestEntity) DELETE n")
        
        # Write test nodes
        with driver.session() as session:
            result = session.run("""
                CREATE (d:TestEntity:Disease {name: 'Myocardial Infarction'})
                CREATE (m1:TestEntity:Medication {name: 'Aspirin'})  
                CREATE (m2:TestEntity:Medication {name: 'Metoprolol'})
                CREATE (m1)-[:TREATS]->(d)
                CREATE (m2)-[:TREATS]->(d)
                RETURN count(*) as nodes_created
            """)
            count = result.single()["nodes_created"]
        
        # Verify write
        with driver.session() as session:
            result = session.run("MATCH (n:TestEntity) RETURN count(n) as count")
            actual_count = result.single()["count"]
        
        driver.close()
        
        if actual_count == 3:
            return True, f"Created and verified {actual_count} nodes in Neo4j"
        else:
            return False, f"Expected 3 nodes, found {actual_count}"
            
    except Exception as e:
        return False, f"Neo4j error: {str(e)}"

if __name__ == "__main__":
    print("="*60)
    print("SERVICE VERIFICATION")
    print("="*60)
    
    # Test Gemini
    gemini_ok, gemini_msg = test_gemini()
    print(f"\nGemini API: {'✅' if gemini_ok else '❌'}")
    print(f"  {gemini_msg}")
    
    # Test Neo4j
    neo4j_ok, neo4j_msg = test_neo4j()
    print(f"\nNeo4j: {'✅' if neo4j_ok else '❌'}")
    print(f"  {neo4j_msg}")
    
    # Summary
    print("\n" + "="*60)
    if gemini_ok and neo4j_ok:
        print("✅ READY: Both services working")
        sys.exit(0)
    else:
        print("❌ BLOCKED: Fix services before proceeding")
        sys.exit(1)
```

**Evidence Required**: `evidence/current/Evidence_Integration_Services.md`
- Full output of verify_services.py
- Must show actual Gemini response with entities
- Must show Neo4j node creation confirmed

#### Step 3: Integrate Real Tools (1 hour)

**File**: Create `/tool_compatability/poc/framework_integration.py`

```python
#!/usr/bin/env python3
"""Integrate existing tools with the framework"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from framework import ExtensibleTool, ToolCapabilities, ToolResult
from data_types import DataType, DataSchema
from semantic_types import MEDICAL_RECORDS, MEDICAL_ENTITIES, MEDICAL_KNOWLEDGE_GRAPH
from data_references import ProcessingStrategy

# Import existing tools
from tools.text_loader import TextLoader
from tools.entity_extractor import EntityExtractor  
from tools.graph_builder import GraphBuilder

class TextLoaderAdapter(ExtensibleTool):
    """Adapter to make TextLoader work with framework"""
    
    def __init__(self):
        self.tool = TextLoader()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="TextLoader",
            name="Text File Loader",
            description="Load text files into memory",
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            semantic_output=MEDICAL_RECORDS,  # For medical pipeline
            max_input_size=10 * 1024 * 1024,  # 10MB
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        try:
            # Use existing TextLoader
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=result.error)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class EntityExtractorAdapter(ExtensibleTool):
    """Adapter for EntityExtractor with Gemini"""
    
    def __init__(self):
        self.tool = EntityExtractor()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="EntityExtractor",
            name="Medical Entity Extractor",
            description="Extract medical entities using Gemini",
            input_type=DataType.TEXT,
            output_type=DataType.ENTITIES,
            semantic_input=MEDICAL_RECORDS,
            semantic_output=MEDICAL_ENTITIES,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        # MUST USE REAL GEMINI API - NO MOCKS
        # EntityExtractor should already load API key from .env
        try:
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=result.error)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class GraphBuilderAdapter(ExtensibleTool):
    """Adapter for GraphBuilder with Neo4j"""
    
    def __init__(self):
        self.tool = GraphBuilder()
    
    def get_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            tool_id="GraphBuilder",
            name="Medical Knowledge Graph Builder",
            description="Build knowledge graph in Neo4j",
            input_type=DataType.ENTITIES,
            output_type=DataType.GRAPH,
            semantic_input=MEDICAL_ENTITIES,
            semantic_output=MEDICAL_KNOWLEDGE_GRAPH,
            processing_strategy=ProcessingStrategy.FULL_LOAD
        )
    
    def process(self, input_data, context=None):
        # MUST WRITE TO REAL NEO4J - NO MOCKS
        try:
            result = self.tool.process(input_data)
            
            if result.success:
                return ToolResult(success=True, data=result.data)
            else:
                return ToolResult(success=False, error=result.error)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

def register_real_tools(framework):
    """Register all real tools with framework"""
    
    print("\n📦 Registering Real Tools:")
    print("-" * 40)
    
    framework.register_tool(TextLoaderAdapter())
    framework.register_tool(EntityExtractorAdapter())
    framework.register_tool(GraphBuilderAdapter())
    
    return framework
```

**Evidence Required**: `evidence/current/Evidence_Integration_Adapters.md`
- Show each adapter created
- Confirm they wrap real tools not mocks
- Show successful registration in framework

#### Step 4: Execute Real Chain (1 hour)

**File**: Create `/tool_compatability/poc/proof_of_concept.py`

```python
#!/usr/bin/env python3
"""
PROOF OF CONCEPT: Framework with Real Tools and Services
This must work with NO MOCKS - only real services
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from framework import ToolFramework
from framework_integration import register_real_tools
from data_types import DataSchema, Domain
from semantic_types import Domain
import time
import psutil

def verify_neo4j_results():
    """Check if data actually in Neo4j"""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "devpassword")
    )
    
    with driver.session() as session:
        # Count nodes created in this session
        result = session.run("""
            MATCH (n) 
            WHERE n.created_by = 'framework_poc'
            RETURN count(n) as node_count
        """)
        count = result.single()["node_count"]
    
    driver.close()
    return count

def main():
    print("="*60)
    print("PROOF OF CONCEPT: Real Tools, Real Services")
    print("="*60)
    
    # 1. Create framework and register real tools
    framework = ToolFramework()
    register_real_tools(framework)
    
    # 2. Load real medical text
    test_file = Path("test_data/medical_article.txt")
    if not test_file.exists():
        print("❌ No test data found. Run Step 1 first.")
        return False
    
    file_data = DataSchema.FileData(
        path=str(test_file),
        size_bytes=test_file.stat().st_size,
        mime_type="text/plain"
    )
    
    print(f"\n📄 Test file: {test_file.name}")
    print(f"   Size: {file_data.size_bytes / 1024:.1f}KB")
    
    # 3. Find medical processing chain
    print("\n🔍 Finding chain for medical text processing:")
    chains = framework.find_chains(
        DataType.FILE,
        DataType.GRAPH,
        domain=Domain.MEDICAL
    )
    
    if not chains:
        print("❌ No chains found!")
        
        # Debug: Show what tools are registered
        print("\nRegistered tools:")
        for tid, caps in framework.capabilities.items():
            print(f"  - {tid}: {caps.input_type} → {caps.output_type}")
        return False
    
    chain = chains[0]
    print(f"   Chain found: {' → '.join(chain)}")
    
    # 4. Execute chain with monitoring
    print("\n⚡ Executing chain:")
    print("-" * 40)
    
    # Monitor memory
    process = psutil.Process()
    mem_before = process.memory_info().rss / (1024 * 1024)  # MB
    
    start_time = time.time()
    result = framework.execute_chain(chain, file_data)
    duration = time.time() - start_time
    
    mem_after = process.memory_info().rss / (1024 * 1024)  # MB
    mem_used = mem_after - mem_before
    
    print(f"\n📊 Execution Metrics:")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Memory used: {mem_used:.1f}MB")
    
    # 5. Verify results
    print("\n🔍 Verification:")
    print("-" * 40)
    
    if not result.success:
        print(f"❌ Chain failed: {result.error}")
        return False
    
    print("✅ Chain executed successfully")
    
    # Check if entities were extracted
    if hasattr(result.data, 'entities'):
        entity_count = len(result.data.entities)
        print(f"✅ Entities extracted: {entity_count}")
        
        # Show first 3 entities as proof
        for entity in result.data.entities[:3]:
            print(f"   - {entity.text} ({entity.type})")
    
    # Check Neo4j
    neo4j_count = verify_neo4j_results()
    if neo4j_count > 0:
        print(f"✅ Neo4j nodes created: {neo4j_count}")
    else:
        print("❌ No nodes found in Neo4j")
    
    # 6. Test semantic blocking
    print("\n🚫 Testing Semantic Type Enforcement:")
    print("-" * 40)
    
    # Try to find social network chain with medical data
    social_chains = framework.find_chains(
        DataType.FILE,
        DataType.GRAPH,
        domain=Domain.SOCIAL
    )
    
    if not social_chains:
        print("✅ Correctly blocked: No social chains for medical tools")
    else:
        print("❌ ERROR: Found social chains with medical tools!")
    
    # 7. Summary
    print("\n" + "="*60)
    print("PROOF OF CONCEPT RESULTS:")
    print("="*60)
    
    success_criteria = [
        ("Real file processed", file_data.size_bytes > 0),
        ("Chain discovered", len(chains) > 0),
        ("Chain executed", result.success),
        ("Entities extracted", entity_count > 0 if 'entity_count' in locals() else False),
        ("Neo4j populated", neo4j_count > 0),
        ("Semantic types enforced", len(social_chains) == 0 if 'social_chains' in locals() else False),
        ("Memory efficient", mem_used < 100)  # Should be <100MB for small file
    ]
    
    for criterion, passed in success_criteria:
        status = "✅" if passed else "❌"
        print(f"{status} {criterion}")
    
    all_passed = all(passed for _, passed in success_criteria)
    
    if all_passed:
        print("\n🎉 PROOF OF CONCEPT SUCCESSFUL!")
        print("The framework works with real tools and services.")
    else:
        print("\n⚠️ PROOF OF CONCEPT INCOMPLETE")
        print("Some criteria not met. Debug required.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

**Evidence Required**: `evidence/current/Evidence_Integration_POC.md`
```
Must include:
1. Full execution log (no truncation)
2. Proof of Gemini API call (show extracted entities)
3. Proof of Neo4j writes (query results)
4. Memory usage stats
5. Semantic type blocking confirmation
```

---

## 5. Troubleshooting Guide

### If Gemini API Fails
```bash
# Check API key
echo $GEMINI_API_KEY

# Test directly
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('/home/brian/projects/Digimons/.env')
print('Key loaded:', bool(os.getenv('GEMINI_API_KEY')))
"

# If key missing, check .env file
cat /home/brian/projects/Digimons/.env | grep GEMINI
```

### If Neo4j Connection Fails
```bash
# Check if running
docker ps | grep neo4j

# If not running, start it
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/devpassword \
  neo4j:latest

# Test connection
python3 -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'devpassword'))
driver.verify_connectivity()
print('✅ Neo4j connected')
"
```

### If Chain Discovery Fails
```python
# Debug what tools are registered
for tool_id, caps in framework.capabilities.items():
    print(f"{tool_id}:")
    print(f"  Input: {caps.input_type}")
    print(f"  Output: {caps.output_type}")
    print(f"  Semantic: {caps.semantic_input} → {caps.semantic_output}")
```

---

## 6. Success Criteria

### Minimum Success
- ✅ One complete chain executes (File → Entities → Graph)
- ✅ Real Gemini API returns entities (no mocks)
- ✅ Real Neo4j has nodes written (verifiable)

### Target Success  
- ✅ All above plus...
- ✅ Semantic types prevent invalid chains
- ✅ Memory usage stays reasonable (<100MB)
- ✅ At least 5 entities extracted

### Full Success
- ✅ All above plus...
- ✅ Process 10MB file with streaming
- ✅ Schema migration works if needed
- ✅ Context parameters used

---

## 7. Next Phase (After POC Success)

Once the proof of concept works:

1. **Add Remaining Tools** (Week 2)
   - StreamingTextLoader for large files
   - EntityExtractorV2 with ontologies
   - 20+ domain-specific tools

2. **Build Composition Agent** (Week 3)
   - Agent that uses framework.find_chains()
   - Learns from successful chains
   - Suggests optimal pipelines

3. **Run Benchmarks** (Week 4)
   - Compare to hardcoded pipelines
   - Measure overhead
   - Document for PhD thesis

---

*Last Updated: 2025-01-26*
*Phase: Experimental POC*
*Status: Experiments 1-2 successful, testing uncertainty propagation next*
*Next: Experiment 03 - uncertainty propagation, then framework integration*