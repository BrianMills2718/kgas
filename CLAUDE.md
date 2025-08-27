# KGAS Uncertainty System - Real Quality Detection Implementation

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
│   └── Evidence_UncertaintyFix_[Task].md   # Current work only
├── completed/
│   └── Evidence_*.md                       # Archived completed work
```

**CRITICAL**: 
- Raw execution logs required (copy-paste terminal output)
- No success claims without showing actual execution
- Test with REAL documents showing quality detection
- Mark all untested components as "NOT TESTED"

---

## 2. Current Problem Statement

### The Core Issue
The uncertainty model returns **hardcoded constants** instead of assessing actual quality:

```python
# CURRENT BROKEN BEHAVIOR:
TextLoaderV3: Always returns 0.02 for .txt files
KnowledgeGraphExtractor: Fixed 0.25 or 0.35 based only on entity COUNT
GraphPersister: Always 0.0 (this is OK - storage is deterministic)
```

### Evidence of Problem
Document `doc_008_noisy.txt` contains obvious OCR errors:
```
Br1an Chhun developcd the KGA5 svstem at the Un1versity of Me1bourne.
```
But gets same 0.02 uncertainty as clean documents!

### Result
**Correlation: -0.143** (NEGATIVE!) - uncertainty doesn't predict errors because values are meaningless.

---

## 3. Codebase Structure

### Key Files to Modify
```
tool_compatability/poc/vertical_slice/
├── tools/
│   ├── text_loader_v3.py           # NEEDS: Real quality detection
│   └── knowledge_graph_extractor.py # NEEDS: Confidence assessment
├── thesis_evidence/
│   ├── evidence_collector.py       # Works but needs updated tools
│   └── run_thesis_collection.py    # Re-run after fixes
└── framework/
    └── clean_framework.py           # Should work as-is
```

### Test Documents Location
```
thesis_evidence/ground_truth_data/documents/
├── doc_001_simple.txt    # Clean text, expect ~0.15 uncertainty
├── doc_008_noisy.txt     # OCR errors, expect ~0.45 uncertainty  
├── doc_006_ambiguous.txt # Ambiguous refs, expect ~0.35 uncertainty
```

### Integration Points
- **LLM**: `gemini/gemini-1.5-flash` via `litellm`
- **Neo4j**: `bolt://localhost:7687` with auth `('neo4j', 'devpassword')`
- **SQLite**: `vertical_slice.db` and `thesis_results/thesis_results.db`
- **Python**: Use `/home/brian/projects/Digimons/.venv/bin/python` for execution

---

## 4. TASK 1: Fix TextLoaderV3 Quality Detection

### Objective
Make TextLoaderV3 detect actual text quality issues and adjust uncertainty accordingly.

### Implementation Requirements

**File**: `/tool_compatability/poc/vertical_slice/tools/text_loader_v3.py`

**Step 1: Import regex at top of file**
```python
import re  # Add this to imports
```

**Step 2: Add quality assessment method to TextLoaderV3 class**:

```python
def _assess_text_quality(self, text: str, file_type: str) -> Tuple[float, List[str]]:
    """
    Detect ACTUAL quality problems in text
    Returns: (quality_uncertainty, list_of_issues)
    """
    quality_uncertainty = 0.0
    issues = []
    
    # 1. OCR Error Detection - CRITICAL for thesis
    ocr_patterns = [
        (r'\b\w*[0-9]+\w*[a-zA-Z]+\w*\b', "digit-letter mixing"),  # Br1an, Un1versity
        (r'[!@#$%^&*](?=[a-zA-Z])|[a-zA-Z](?=[!@#$%^&*])', "symbol adjacency"),  # gr@ph, J@ne
        (r'\b[A-Z][a-z]*[0-9]\w*\b', "corrupted proper nouns"),  # Me1bourne, 2O24
        (r'(?<![A-Z])[0-9](?=[a-zA-Z])|(?<=[a-zA-Z])[0-9](?![0-9])', "embedded digits")  # 5ystem, pr0ject
    ]
    
    total_words = len(text.split())
    total_ocr_errors = 0
    
    for pattern, description in ocr_patterns:
        matches = re.findall(pattern, text)
        if matches:
            total_ocr_errors += len(matches)
            issues.append(f"{description}: {matches[:3]}")  # Show first 3 examples
    
    # Calculate OCR error rate
    if total_words > 0:
        ocr_error_rate = total_ocr_errors / total_words
        if ocr_error_rate > 0.01:  # >1% corrupted words
            quality_uncertainty += min(ocr_error_rate * 5, 0.4)  # Cap at 0.4
            issues.append(f"OCR error rate: {ocr_error_rate:.1%}")
    
    # 2. Truncation Detection
    truncation_markers = ['[TRUNCATED]', '[ERROR', 'Page missing', '...']
    for marker in truncation_markers:
        if marker in text:
            quality_uncertainty += 0.2
            issues.append(f"truncation: {marker}")
            break
    
    # 3. Formatting Issues
    # Excessive line breaks
    if text.count('\n\n\n') > 0:
        quality_uncertainty += 0.05
        issues.append("excessive line breaks")
    
    # Broken words across lines (simple check)
    if re.search(r'\w+\n\w+', text):
        quality_uncertainty += 0.05
        issues.append("broken word continuation")
    
    # Multiple spaces
    if '    ' in text or '\t\t' in text:
        quality_uncertainty += 0.03
        issues.append("irregular spacing")
    
    return min(quality_uncertainty, 0.5), issues  # Cap at 0.5 for text quality
```

**Step 3: Modify the process method** (find and update):

```python
def process(self, file_path: str) -> Dict[str, Any]:
    """Process file with REAL quality detection"""
    try:
        # Existing file reading code...
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Get file type uncertainty (existing)
        file_type = file_path.split('.')[-1].lower()
        base_uncertainty = self.uncertainty_constants.get(file_type, 0.1)
        
        # NEW: Assess actual text quality
        quality_uncertainty, quality_issues = self._assess_text_quality(text, file_type)
        
        # Combine uncertainties
        total_uncertainty = min(base_uncertainty + quality_uncertainty, 0.95)
        
        # Build detailed reasoning
        base_reasoning = self.reasoning_templates.get(file_type, 'File extraction')
        if quality_issues:
            reasoning = f"{base_reasoning} | Quality issues: {'; '.join(quality_issues)}"
        else:
            reasoning = base_reasoning
        
        return {
            'success': True,
            'text': text,
            'uncertainty': total_uncertainty,
            'reasoning': reasoning,
            'construct_mapping': 'file_path → character_sequence'
        }
    except Exception as e:
        # Fail-fast principle
        raise RuntimeError(f"TextLoaderV3 failed: {str(e)}") from e
```

### Testing Task 1

```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Test on noisy document (should detect OCR errors)
python3 -c "
from tools.text_loader_v3 import TextLoaderV3
loader = TextLoaderV3()
result = loader.process('thesis_evidence/ground_truth_data/documents/doc_008_noisy.txt')
print(f'Uncertainty: {result[\"uncertainty\"]:.3f}')
print(f'Reasoning: {result[\"reasoning\"]}')
"
```

**Expected**: Uncertainty ~0.35-0.50 with OCR errors listed in reasoning

---

## 5. TASK 2: Fix KnowledgeGraphExtractor Confidence

### Objective
Make KnowledgeGraphExtractor assess extraction difficulty and confidence.

### Implementation Requirements

**File**: `/tool_compatability/poc/vertical_slice/tools/knowledge_graph_extractor.py`

**Replace the entire `_assess_extraction_uncertainty` method**:

```python
def _assess_extraction_uncertainty(self, text_length: int, entity_count: int, 
                                  relationship_count: int, chunk_count: int,
                                  chunk_uncertainties: List[float]) -> Tuple[float, str]:
    """
    Assess extraction uncertainty based on ACTUAL extraction challenges
    """
    # Start with base LLM uncertainty
    base_uncertainty = 0.25
    adjustments = []
    
    # 1. Entity Extraction Quality
    if entity_count == 0:
        base_uncertainty = 0.95
        adjustments.append("no entities extracted")
    elif entity_count < 3:
        base_uncertainty += 0.15
        adjustments.append(f"sparse extraction ({entity_count} entities)")
    elif text_length > 0:
        # Check for suspiciously high entity density
        entity_density = entity_count / (text_length / 1000)  # entities per 1000 chars
        if entity_density > 20:
            base_uncertainty += 0.10
            adjustments.append(f"possible over-extraction (density: {entity_density:.1f}/1k chars)")
    
    # 2. Relationship Quality
    if entity_count > 0:
        relationship_ratio = relationship_count / entity_count
        if relationship_ratio < 0.5:  # Very few relationships
            base_uncertainty += 0.10
            adjustments.append(f"sparse relationships ({relationship_ratio:.1f} per entity)")
        elif relationship_ratio > 3:  # Too many relationships
            base_uncertainty += 0.05
            adjustments.append(f"dense relationships ({relationship_ratio:.1f} per entity)")
    
    # 3. Chunking Impact
    if chunk_count > 1:
        base_uncertainty += 0.05 * (chunk_count - 1)  # Each chunk adds uncertainty
        adjustments.append(f"{chunk_count} chunks processed")
    
    # Build reasoning
    reasoning = f"Extracted {entity_count} entities and {relationship_count} relationships"
    if adjustments:
        reasoning += f" | Adjustments: {'; '.join(adjustments)}"
    
    # Ensure valid range
    final_uncertainty = min(max(base_uncertainty, 0.0), 0.95)
    
    return final_uncertainty, reasoning
```

### Testing Task 2

```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

# Test extraction with simple text
python3 -c "
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
extractor = KnowledgeGraphExtractor()
test_text = 'Brian Chhun developed KGAS at the University of Melbourne.'
result = extractor.process(test_text)
print(f'Uncertainty: {result[\"uncertainty\"]:.3f}')
print(f'Reasoning: {result[\"reasoning\"]}')
"
```

**Expected**: Uncertainty ~0.25-0.35 with entity/relationship counts in reasoning

---

## 6. TASK 3: Re-run Thesis Collection

### Objective
Re-run the complete thesis evidence collection with proper uncertainty assessment.

### Steps

**Step 1: Verify fixes are working**:
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice

python3 -c "
from tools.text_loader_v3 import TextLoaderV3
from tools.knowledge_graph_extractor import KnowledgeGraphExtractor

# Test on noisy document
loader = TextLoaderV3()
result1 = loader.process('thesis_evidence/ground_truth_data/documents/doc_008_noisy.txt')
print(f'TextLoader uncertainty: {result1[\"uncertainty\"]:.3f}')
print(f'Reasoning: {result1[\"reasoning\"][:100]}...')

# Test on simple document
result2 = loader.process('thesis_evidence/ground_truth_data/documents/doc_001_simple.txt')
print(f'\\nSimple doc uncertainty: {result2[\"uncertainty\"]:.3f}')
print(f'Reasoning: {result2[\"reasoning\"][:100]}...')
"
```

**Expected**: 
- Noisy doc: ~0.35-0.50 uncertainty
- Simple doc: ~0.02-0.05 uncertainty

**Step 2: Clean previous results**:
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
rm -rf thesis_evidence/thesis_results/*
rm -rf thesis_evidence/thesis_analysis/*
```

**Step 3: Run full collection**:
```bash
cd thesis_evidence
/home/brian/projects/Digimons/.venv/bin/python run_thesis_collection.py
```

**Step 4: Check correlation**:
```bash
python3 -c "
import json
with open('thesis_analysis/thesis_summary.json') as f:
    summary = json.load(f)
print(f'Correlation: {summary[\"hypothesis_validation\"][\"correlation_coefficient\"]:.3f}')
print(f'Validated: {summary[\"hypothesis_validation\"][\"validated\"]}')
"
```

### Evidence Required

Create `evidence/current/Evidence_UncertaintyFix_Results.md`:

```markdown
# Evidence: Fixed Uncertainty Model Results

## Task 1: TextLoaderV3 Quality Detection
[Copy actual terminal output showing OCR detection]

## Task 2: KnowledgeGraphExtractor Confidence
[Copy actual terminal output showing varied uncertainty]

## Task 3: Full Collection Results
### Correlation
[Show correlation value - should be positive]

### Uncertainty Distribution
- Simple documents: [values]
- Noisy documents: [values]
- Difference: [X times higher]

### Success Criteria
✅/❌ Positive correlation achieved
✅/❌ Noisy docs have higher uncertainty than simple
✅/❌ Each uncertainty has explainable reasoning
```

---

## 7. Success Criteria

### Minimum Success ✅
- [ ] TextLoaderV3 detects OCR errors in doc_008_noisy.txt
- [ ] Uncertainty varies between document types
- [ ] Positive correlation (>0.0) between uncertainty and error
- [ ] Each uncertainty has detailed reasoning

### Target Success 🎯
- [ ] Correlation > 0.3 (moderate positive)
- [ ] Noisy documents have 2x+ uncertainty vs simple
- [ ] Ambiguous documents fall in middle range
- [ ] All reasoning chains are explainable

---

## 8. Troubleshooting

### If imports fail
```bash
cd /home/brian/projects/Digimons/tool_compatability/poc/vertical_slice
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### If correlation is still negative
Check that:
1. TextLoaderV3 is actually detecting quality issues
2. The quality_uncertainty is being added to base_uncertainty
3. The reasoning shows detected issues

### If Gemini API fails
The retry logic should handle it, but if persistent:
```bash
# Wait 30 seconds and retry
sleep 30
```

---

## 9. Important Notes

1. **Fail-Fast**: If quality detection fails, raise errors immediately
2. **Evidence**: Every claim needs terminal output proof
3. **Real Detection**: Actually detect OCR patterns, not fake scores
4. **Correlation Focus**: Goal is positive correlation, not perfect accuracy

---

*Last Updated: 2025-08-27*
*Phase: Uncertainty Model Fix*
*Priority: Get defensible thesis results with real quality detection*