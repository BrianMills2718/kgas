# KGAS Validation Matrix

## Core Framework: 14 Uncertainty Dimensions × Validation Methods

### Master Validation Matrix

| **Uncertainty Dimension** | **What System Should Assess** | **Validation Methods** | **Data/Ground Truth** | **Current Plan** | **Feasibility** |
|--------------------------|------------------------------|----------------------|---------------------|-----------------|----------------|
| **1. Source Credibility** | Quality/authority of sources | " Expert comparison<br>" Inter-LLM agreement<br>" Test set: high vs low quality papers | Nature/Science vs predatory journals | Not yet planned | High - 1 week |
| **2. Cross-Source Coherence** | Agreement/contradiction between sources | " Inter-LLM agreement<br>" Expert validation<br>" Contradiction detection test | Known contradictory source pairs | Partially via inter-LLM | High - 3 days |
| **3. Temporal Relevance** | How evidence ages/decays | " Time series holdout<br>" Expert judgment on decay<br>" Old vs recent evidence test | Temporal datasets | Optional time series test | Medium |
| **4. Extraction Completeness** | Coverage of available information | " Hand-coding comparison<br>" Inter-LLM comparison<br>" Expert assessment | 5-10 hand-coded theories |  **Planned** | High |
| **5. Entity Recognition** | Accurate entity identification | " Mechanical Turk<br>" NER benchmarks<br>" Inter-LLM agreement | 500 coded tweets, CoNLL-2003 |  **Planned** | High |
| **6. Construct Validity** | Whether constructs measure what claimed | " COVID correlations<br>" Sentiment baselines<br>" Inter-LLM agreement | 2,506 users with psych scales |  **Planned** | High |
| **7. Theory-Data Fit** | Theory alignment with data patterns | " Replication studies<br>" Expert assessment<br>" Inter-LLM agreement | 3-5 papers with data |  **Planned** | High |
| **8. Study Limitations** | Identifying methodological limits | " Retracted papers test<br>" Review/rebuttal comparison<br>" Expert validation | Papers with known flaws | Not yet planned | Medium |
| **9. Sampling Bias** | Detecting non-representative samples | " WEIRD vs diverse test<br>" Expert validation<br>" Inter-LLM agreement | Biased/unbiased pairs | Not yet planned | Medium |
| **10. Diagnosticity** | Evidence relevance to claims | " HotPotQA benchmark<br>" Expert assessment<br>" Inter-LLM agreement | HotPotQA dataset |  **Planned** | High |
| **11. Sufficiency** | Adequate evidence for confidence | " Varied evidence amounts<br>" Expert comparison<br>" Systematic review data | Evidence gradients | Not yet planned | Medium |
| **12. Confidence Calibration** | Confidence matches accuracy | • Aggregate performance<br>• Calibration curves<br>• Post-hoc analysis | All test results | Emerges from tests | High |
| **13. Entity Identity Resolution** | Same entity across mentions | • Hand-code resolutions<br>• Name variation tests<br>• Inter-LLM agreement | Papers with known entities | Partially via hand-coding | High |
| **14. Reasoning Chain Validity** | Multi-step reasoning accuracy | • HotPotQA benchmark<br>• Hand-traced chains<br>• Inter-LLM agreement | HotPotQA + expert traces | ✓ **Planned** (HotPotQA) | High |

---

## Validation Method Capabilities

### How Each Method Maps to Dimensions

| **Method** | **Strong For** | **Moderate For** | **Notes** |
|-----------|---------------|------------------|-----------|
| **Hand-Coding (You)** | • Theory structure (#4)<br>• Quality assessment<br>• Complex extraction tasks | • All dimensions requiring expert judgment | **Gold standard** for complex tasks |
| **Paper Replication** | • **Theory-data fit (#7)**<br>• Complete validation pipeline<br>• Extraction + application | • Construct validity (#6)<br>• Extraction completeness (#4) | **Ultimate validation**: Extract theory → Apply to their data → Compare results |
| **Inter-LLM Agreement** | • **Universal application**<br>• Consistency checking | • **Can apply to ALL 14 dimensions** | Shows reliability, not accuracy |
| **Expert Comparison** | • Source credibility (#1)<br>• Limitations (#8)<br>• Sufficiency (#11) | • Theory-data fit (#7)<br>• Sampling bias (#9) | When you can't hand-code everything |
| **Crowd Coding** | • Entity recognition (#5)<br>• Simple extraction (#4) | • Basic construct validity (#6) | Limited to simple, objective tasks |
| **Ground Truth Datasets** | • Diagnosticity (#10)<br>• Entity recognition (#5) | • Extraction completeness (#4) | Best when available |
| **Correlation Analysis** | • Construct validity (#6)<br>• Confidence calibration (#12) | • Theory-data fit (#7) | Quantitative validation |

---

## Implementation Plan

### Currently Planned Validations

| **Dimension** | **Primary Method** | **Secondary Methods** | **Timeline** |
|--------------|-------------------|----------------------|-------------|
| Extraction Completeness (#4) | **Your hand-coding** (5-10 theories V13) | Inter-LLM agreement + LLM quality assessment | Week 2-3 |
| Entity Recognition (#5) | Mechanical Turk | NER benchmarks + Inter-LLM agreement | Week 2 |
| Construct Validity (#6) | COVID correlations | Sentiment baselines + Inter-LLM agreement | Week 3-5 |
| Theory-Data Fit (#7) | **Paper replication** (extract methodology → apply to their dataset → compare results) | **Your qualitative assessment** + Inter-LLM agreement | Week 6-8 |
| Diagnosticity (#10) | HotPotQA | Inter-LLM agreement | Week 1-2 |

**Note**: Inter-LLM agreement applied to all validations as standard consistency check

### Recommended Additions (Easy Wins)

| **Dimension** | **Method** | **Effort** | **Impact** |
|--------------|-----------|-----------|-----------|
| Source Credibility (#1) | High/low quality test set | 1 week | High - fundamental capability |
| Cross-Source Coherence (#2) | Contradiction detection | 3 days | High - critical for synthesis |
| Sampling Bias (#9) | WEIRD vs diverse papers | 1 week | Medium - shows sophistication |
| Confidence Calibration (#12) | Automatic from all tests | 0 days | High - emerges naturally |

### Future Work

| **Dimension** | **Why Deferred** | **What It Would Take** |
|--------------|-----------------|----------------------|
| Study Limitations (#8) | Need curated test set | Collect retracted papers |
| Temporal Relevance (#3) | Need temporal data | Time series datasets |
| Sufficiency (#11) | Need expert ratings | Systematic review analysis |

---

## Key Insights

### Coverage Analysis
- **Currently validating**: 7 of 14 dimensions (50%)
  - Dimensions 4, 5, 6, 7, 10, 13 (partial), 14
- **Easy to add**: 4 more dimensions (79% total)
  - Dimensions 1, 2, 9, 12
- **Requires significant effort**: 3 dimensions (21%)
  - Dimensions 3, 8, 11

### Method Distribution
- **All dimensions** can use inter-LLM agreement as consistency check
- **Expert comparison** needed for subjective dimensions
- **Ground truth** available for only ~half of dimensions
- **Multiple methods** strengthen validation for each dimension

### Validation Principles
1. **Methods are flexible**: Any method can potentially apply to any dimension
2. **Multiple methods are better**: Triangulation strengthens claims
3. **Inter-LLM agreement** shows consistency, not correctness
4. **Ground truth** is gold standard where available
5. **Expert judgment** fills gaps where ground truth doesn't exist

---

## Simplified Decision Framework

```
For each dimension:
1. Is ground truth available?
   YES � Use it as primary validation
   NO  � Use expert comparison

2. Can crowds do this task?
   YES � Add Mechanical Turk validation
   NO  � Skip crowd validation

3. Would multiple LLMs help?
   YES � Add inter-LLM agreement as secondary
   ALWAYS � Yes for consistency check

4. Is this currently planned?
   YES � Execute as planned
   NO  � Assess effort vs impact for prioritization
```

---

## Bottom Line

- **System validation focus**: Testing KGAS capabilities, not theory truth
- **14 dimensions**: Comprehensive uncertainty assessment framework
- **Multiple methods**: Each dimension can be validated multiple ways
- **Current coverage**: 7 dimensions planned/partial, 4 more easily added (79% total achievable)
- **No predetermined targets**: Report what we measure, not what we hope