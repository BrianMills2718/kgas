# Tool Integration Phase - Scale Available Tools

## ⚠️ PERMANENT - DO NOT REMOVE ⚠️

### IMPORTANT CLARIFICATIONS
- **Spacy is DEPRECATED** - Do NOT use or integrate any tools requiring spacy
- **Actual Tool Count**: 15 tools found (not 37 as initially stated)
  - 8 T-series tools in `/archive/archived/legacy_tools_2025_07_23/`
  - 7 tools in `/src/tools/`
- **Deprecated Tools**: 
  - `t23a_spacy_ner` - uses deprecated spacy
  - `t27_relationship_extractor` - uses deprecated spacy
- **Successfully Integrated**: 6 tools working with UniversalAdapter
- **Pending**: `t01_pdf_loader` awaiting pypdf installation

## ⚠️ PERMANENT - DO NOT REMOVE ⚠️

### API Configuration
- **API Keys Location**: `/home/brian/projects/Digimons/.env`
- **Default LLM Model**: `gemini/gemini-1.5-flash` via litellm
- **Always load .env first** before claiming API keys are missing
```python
from dotenv import load_dotenv
import os

# ALWAYS load from the project .env file
load_dotenv('/home/brian/projects/Digimons/.env')
api_key = os.getenv('GEMINI_API_KEY')
```

---

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
│   └── Evidence_ToolIntegration_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md                        # Archived completed work
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Test with REAL tools and services
- Archive completed phases to avoid chronological confusion

---

## 2. Codebase Structure

### Clean Vertical Slice (COMPLETE)
```
tool_compatability/poc/vertical_slice/
├── framework/
│   └── clean_framework.py          # Extensible framework with BFS chain discovery
├── services/                       # All working with fixes applied
├── tools/                          # 3 tools with uncertainty
└── tests/                          # End-to-end test passing
```

### Existing Tool Library (TO INTEGRATE)
```
src/tools/
├── T01_PDFLoader.py through T14_*  # Document loaders
├── T15_TextChunker.py through T30_* # Entity processing
├── T31_EntityBuilder.py through T68_* # Graph analytics
└── T69_* through T85_*              # Cross-modal tools
```

### Key Integration Points
- **ServiceManager**: `/src/services/service_manager.py` - Central service orchestration
- **UniversalAdapter**: `/src/core/adapter_factory.py` - Wraps tools with services
- **ProvenanceService**: Track all operations with uncertainty
- **IdentityService**: Entity resolution across tools

### Important Documentation
- **Tool Capabilities**: `/docs/architecture/VERTICAL_SLICE_20250826.md`
- **Uncertainty Model**: `/docs/architecture/UNCERTAINTY_20250825.md`
- **Tool Registry**: `/src/tool_management/tool_registry.py`

---

## 3. Current Status

### ✅ Completed (Vertical Slice)
- Clean framework with dynamic chain discovery
- Real Gemini API integration working
- Physics-style uncertainty propagation
- 3 demonstration tools integrated

### 🎯 Current Goal: Scale to 37 Tools
Integrate existing tool library into clean framework with uncertainty assessment for each tool.

---

## 4. PHASE 1: Tool Inventory & Classification

### Task 1.1: Create Tool Catalog

**File**: Create `/tool_compatability/poc/tool_catalog.py`

```python
#!/usr/bin/env python3
"""Catalog all existing tools and their characteristics"""

import os
import importlib.util
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ToolInfo:
    tool_id: str
    file_path: str
    input_type: str
    output_type: str
    requires_llm: bool
    is_deterministic: bool
    dependencies: List[str]

def scan_tools_directory() -> List[ToolInfo]:
    """Scan src/tools/ and catalog all tools"""
    tools = []
    tools_dir = "/home/brian/projects/Digimons/src/tools"
    
    for filename in os.listdir(tools_dir):
        if filename.startswith('T') and filename.endswith('.py'):
            tool_path = os.path.join(tools_dir, filename)
            tool_info = analyze_tool(tool_path)
            tools.append(tool_info)
    
    return tools

def analyze_tool(tool_path: str) -> ToolInfo:
    """Analyze a tool file to extract its characteristics"""
    # Load the module
    spec = importlib.util.spec_from_file_location("tool", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Extract tool characteristics
    # Look for execute(), process(), or run() methods
    # Check for LLM imports (litellm, openai)
    # Check for service dependencies
    
    return ToolInfo(...)

if __name__ == "__main__":
    tools = scan_tools_directory()
    print(f"Found {len(tools)} tools")
    
    # Group by category
    document_loaders = [t for t in tools if 'loader' in t.tool_id.lower()]
    entity_tools = [t for t in tools if 'entity' in t.tool_id.lower()]
    graph_tools = [t for t in tools if 'graph' in t.tool_id.lower()]
    
    print(f"Document loaders: {len(document_loaders)}")
    print(f"Entity tools: {len(entity_tools)}")
    print(f"Graph tools: {len(graph_tools)}")
```

**Evidence Required**: `evidence/current/Evidence_ToolIntegration_Catalog.md`
- List all 37 tools found
- Group by input/output types
- Identify which use LLMs vs deterministic

### Task 1.2: Define Extended DataTypes

**File**: Create `/tool_compatability/poc/vertical_slice/framework/data_types.py`

```python
from enum import Enum

class DataType(Enum):
    """Extended data types for all tools"""
    # File types
    FILE = "file"
    PDF = "pdf"
    DOCX = "docx"
    CSV = "csv"
    JSON = "json"
    
    # Text types
    TEXT = "text"
    CHUNKS = "chunks"
    SENTENCES = "sentences"
    
    # Entity types
    ENTITIES = "entities"
    RELATIONSHIPS = "relationships"
    MENTIONS = "mentions"
    
    # Graph types
    KNOWLEDGE_GRAPH = "knowledge_graph"
    NEO4J_GRAPH = "neo4j_graph"
    NETWORK = "network"
    
    # Table types
    TABLE = "table"
    DATAFRAME = "dataframe"
    METRICS = "metrics"
    
    # Vector types
    VECTOR = "vector"
    EMBEDDINGS = "embeddings"
    CLUSTERS = "clusters"
    
    # Visualization
    VISUALIZATION = "visualization"
    PLOT = "plot"
```

---

## 5. PHASE 2: Tool Wrapper Implementation

### Task 2.1: Create Universal Tool Wrapper

**File**: Create `/tool_compatability/poc/vertical_slice/framework/tool_wrapper.py`

```python
#!/usr/bin/env python3
"""Universal wrapper for integrating legacy tools with uncertainty"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from framework.data_types import DataType
import hashlib
import json

@dataclass
class UncertaintyConfig:
    """Configuration for tool uncertainty assessment"""
    tool_id: str
    input_type: DataType
    output_type: DataType
    input_construct: str
    output_construct: str
    base_uncertainty: float  # For deterministic tools
    uncertainty_factors: Dict[str, float]  # Conditional adjustments

class ToolWrapper:
    """Wraps legacy tools with uncertainty assessment"""
    
    def __init__(self, legacy_tool: Any, config: UncertaintyConfig):
        self.tool = legacy_tool
        self.config = config
        self._setup_tool()
    
    def _setup_tool(self):
        """Initialize the legacy tool"""
        # Handle different initialization patterns
        if hasattr(self.tool, 'initialize'):
            self.tool.initialize()
        elif hasattr(self.tool, 'setup'):
            self.tool.setup()
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Execute tool with uncertainty assessment"""
        try:
            # Execute the legacy tool
            result = self._execute_legacy_tool(input_data)
            
            # Assess uncertainty
            uncertainty = self._assess_uncertainty(input_data, result)
            
            # Format response
            return {
                'success': True,
                'data': result,
                'uncertainty': uncertainty['score'],
                'reasoning': uncertainty['reasoning'],
                'construct_mapping': f"{self.config.input_construct} → {self.config.output_construct}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0,
                'reasoning': f"Tool execution failed: {e}"
            }
    
    def _execute_legacy_tool(self, input_data: Any) -> Any:
        """Execute the legacy tool with proper method detection"""
        # Try different execution methods
        if hasattr(self.tool, 'execute'):
            return self.tool.execute(input_data)
        elif hasattr(self.tool, 'process'):
            return self.tool.process(input_data)
        elif hasattr(self.tool, 'run'):
            return self.tool.run(input_data)
        else:
            raise AttributeError(f"Tool {self.config.tool_id} has no execution method")
    
    def _assess_uncertainty(self, input_data: Any, result: Any) -> Dict[str, Any]:
        """Assess uncertainty based on tool type and results"""
        
        # For LLM tools, check if they provide confidence
        if hasattr(result, 'confidence'):
            return {
                'score': 1.0 - result.confidence,
                'reasoning': f"LLM confidence: {result.confidence}"
            }
        
        # For deterministic tools, use base uncertainty
        uncertainty = self.config.base_uncertainty
        reasoning = f"Base uncertainty for {self.config.tool_id}"
        
        # Apply conditional factors
        if self._is_sparse_data(input_data):
            uncertainty *= 1.5
            reasoning += " (sparse input data)"
        
        if self._is_large_output(result):
            uncertainty *= 1.2
            reasoning += " (large output, potential information overload)"
        
        return {
            'score': min(uncertainty, 1.0),
            'reasoning': reasoning
        }
```

**Evidence Required**: `evidence/current/Evidence_ToolIntegration_Wrapper.md`
- Test wrapper with a legacy tool
- Show uncertainty assessment working
- Verify construct mapping

---

## 6. PHASE 3: Tool Migration - Batch 1 (Document Loaders)

### Task 3.1: Migrate Document Loaders

**File**: Create `/tool_compatability/poc/integrated_tools/document_loaders.py`

```python
#!/usr/bin/env python3
"""Integrate document loader tools (T01-T14)"""

import sys
sys.path.append('/home/brian/projects/Digimons')

from src.tools.T01_PDFLoader import PDFLoader
from src.tools.T02_WordDocumentLoader import WordLoader
from src.tools.T03_CSVTableExtractor import CSVLoader
# ... import other loaders

from framework.tool_wrapper import ToolWrapper, UncertaintyConfig
from framework.data_types import DataType

def integrate_pdf_loader():
    """Integrate T01_PDFLoader with uncertainty"""
    config = UncertaintyConfig(
        tool_id="T01_PDFLoader",
        input_type=DataType.PDF,
        output_type=DataType.TEXT,
        input_construct="pdf_file",
        output_construct="document_text",
        base_uncertainty=0.15,
        uncertainty_factors={
            'ocr_required': 1.5,
            'encrypted': 2.0,
            'corrupted': 3.0
        }
    )
    
    legacy_tool = PDFLoader()
    return ToolWrapper(legacy_tool, config)

def integrate_all_document_loaders():
    """Integrate all document loader tools"""
    loaders = {
        'T01_PDFLoader': (PDFLoader, 0.15),
        'T02_WordLoader': (WordLoader, 0.08),
        'T03_CSVLoader': (CSVLoader, 0.02),
        'T04_JSONLoader': (JSONLoader, 0.01),
        # Add all 14 loaders
    }
    
    integrated_tools = {}
    for tool_id, (tool_class, uncertainty) in loaders.items():
        config = UncertaintyConfig(
            tool_id=tool_id,
            input_type=DataType.FILE,
            output_type=DataType.TEXT,
            input_construct="file_path",
            output_construct="extracted_text",
            base_uncertainty=uncertainty,
            uncertainty_factors={}
        )
        integrated_tools[tool_id] = ToolWrapper(tool_class(), config)
    
    return integrated_tools

if __name__ == "__main__":
    # Test integration
    pdf_loader = integrate_pdf_loader()
    result = pdf_loader.process("test.pdf")
    print(f"Success: {result['success']}")
    print(f"Uncertainty: {result['uncertainty']}")
```

**Evidence Required**: `evidence/current/Evidence_ToolIntegration_DocumentLoaders.md`
- Show each loader working
- Document uncertainty values
- Test with real files

---

## 7. PHASE 4: Pipeline Testing

### Task 4.1: Test Integrated Pipelines

**File**: Create `/tool_compatability/poc/test_integrated_pipelines.py`

```python
#!/usr/bin/env python3
"""Test pipelines with integrated tools"""

from framework.clean_framework import CleanToolFramework
from integrated_tools.document_loaders import integrate_all_document_loaders

def test_document_processing_pipeline():
    """Test PDF → Text → Entities → Graph"""
    framework = CleanToolFramework(
        neo4j_uri="bolt://localhost:7687",
        sqlite_path="integrated_test.db"
    )
    
    # Register integrated tools
    loaders = integrate_all_document_loaders()
    for tool_id, tool in loaders.items():
        framework.register_tool(tool, tool.config)
    
    # Find and execute chain
    chain = framework.find_chain(DataType.PDF, DataType.NEO4J_GRAPH)
    if chain:
        print(f"Found chain: {' → '.join(chain)}")
        result = framework.execute_chain(chain, "test.pdf")
        print(f"Total uncertainty: {result.total_uncertainty:.3f}")
        
        # Verify uncertainty propagation
        assert result.total_uncertainty > 0
        assert result.total_uncertainty < 1.0
    else:
        print("No chain found")

def test_cross_modal_pipeline():
    """Test Graph → Table → Statistical Analysis"""
    # Similar structure for cross-modal tools
    pass

if __name__ == "__main__":
    test_document_processing_pipeline()
    test_cross_modal_pipeline()
```

**Evidence Required**: `evidence/current/Evidence_ToolIntegration_Pipelines.md`
- Show multiple pipelines working
- Document uncertainty propagation
- Compare to vertical slice baseline

---

## 8. Success Criteria

### Phase Completion Checkpoints

#### Phase 1: Tool Inventory ✓
- [ ] All 37 tools cataloged
- [ ] DataTypes extended for all tool types
- [ ] Dependencies documented

#### Phase 2: Wrapper Implementation ✓
- [ ] Universal wrapper created
- [ ] Uncertainty assessment working
- [ ] Legacy tool compatibility verified

#### Phase 3: Tool Migration ✓
- [ ] Document loaders (T01-T14) integrated
- [ ] Entity tools (T15-T30) integrated
- [ ] Graph tools (T31-T68) integrated
- [ ] Cross-modal tools (T69-T85) integrated

#### Phase 4: Testing ✓
- [ ] 5+ different pipelines tested
- [ ] Uncertainty propagation verified
- [ ] Performance acceptable (<100ms overhead)

### Evidence Requirements
Each phase MUST produce evidence showing:
1. Tools successfully wrapped
2. Uncertainty values reasonable (0.01-0.9 range)
3. Pipeline execution with real data
4. No mocking - actual tool execution

---

## 9. Testing Commands

```bash
# Phase 1: Catalog tools
python3 tool_compatability/poc/tool_catalog.py

# Phase 2: Test wrapper
python3 -c "from framework.tool_wrapper import ToolWrapper; print('Wrapper ready')"

# Phase 3: Test integrated tools
python3 tool_compatability/poc/integrated_tools/document_loaders.py

# Phase 4: Test pipelines
python3 tool_compatability/poc/test_integrated_pipelines.py
```

---

## 10. Troubleshooting

### If legacy tool import fails
```python
# Add to path
import sys
sys.path.append('/home/brian/projects/Digimons')
```

### If tool has no standard interface
```python
# Create adapter
class ToolAdapter:
    def __init__(self, legacy_tool):
        self.tool = legacy_tool
    
    def execute(self, input_data):
        # Map to tool's actual method
        return self.tool.custom_method(input_data)
```

### If uncertainty seems wrong
- Check if tool is deterministic vs probabilistic
- Verify input data quality
- Review uncertainty factors in config

---

*Last Updated: 2025-08-27*
*Phase: Tool Integration - Scale to 37 Tools*
*Priority: Demonstrate framework scales to full tool suite*