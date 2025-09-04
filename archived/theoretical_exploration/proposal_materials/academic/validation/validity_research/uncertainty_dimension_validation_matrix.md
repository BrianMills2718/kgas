# Uncertainty Dimensions × Validation Methods Matrix

## Mapping What We Can Actually Validate

| **Uncertainty Dimension** | **What System Should Assess** | **How We Can Validate This** | **Method** | **Actual Test/Data** | **What We Learn** |
|--------------------------|------------------------------|----------------------------|-----------|-------------------|-------------------|
| **1. Source Credibility** | Quality/authority of sources | ❌ No direct validation planned | - | - | Can't validate without expert-rated source corpus |
| **2. Cross-Source Coherence** | Agreement/contradiction between sources | ⚠️ Partially validatable | Inter-LLM comparison | Different LLMs on same papers | If models consistently identify same patterns (weak proxy) |
| **3. Temporal Relevance** | How evidence ages | ⚠️ Potentially testable | Time series analysis | Hide temporal data, test decay | If system weights recent > old appropriately |
| **4. Extraction Completeness** | Coverage of available information | ✅ Directly validatable | Human comparison | Hand-coded theories (5-10 papers) | % concepts captured vs human extraction |
| **5. Entity Recognition** | Accurate entity identification | ✅ Directly validatable | Crowd validation | Mechanical Turk (500 tweets) | F1 score for entity extraction |
| **6. Construct Validity** | Whether constructs measure what claimed | ✅ Directly validatable | Ground truth correlation | COVID psych scales (2,506 users) | If extracted constructs correlate with validated measures |
| **7. Theory-Data Fit** | Theory alignment with data | ✅ Directly validatable | Replication test | Papers with data (3-5) | If theory produces similar results on same data |
| **8. Study Limitations** | Identifying methodological limits | ❌ No validation planned | - | - | Would need papers with known hidden limitations |
| **9. Sampling Bias** | Detecting non-representative samples | ❌ No validation planned | - | - | Would need biased/unbiased sample pairs |
| **10. Diagnosticity** | Evidence relevance to claims | ⚠️ Partially via HotPotQA | Retrieval test | HotPotQA benchmark | If system retrieves relevant evidence for queries |
| **11. Sufficiency** | Adequate evidence for confidence | ❌ No validation planned | - | - | Would need varying evidence amounts with expert ratings |
| **12. Confidence Calibration** | Confidence matches accuracy | ⚠️ Partially testable | Performance correlation | Aggregate across all tests | If stated confidence correlates with actual performance |

---

## Validation Methods × What They Actually Test

| **Method** | **What It Actually Validates** | **Which Dimensions It Touches** | **Strength of Evidence** |
|-----------|--------------------------------|--------------------------------|------------------------|
| **Hand-coding comparison** | Extraction accuracy, theory structure | #4 Completeness (directly) | Strong - direct comparison |
| **COVID correlations** | Construct meaningfulness | #6 Construct validity (directly) | Strong - ground truth |
| **Mechanical Turk** | Basic extraction accuracy | #5 Entity recognition (directly) | Moderate - simple tasks only |
| **Inter-LLM agreement** | Consistency (NOT accuracy) | #2 Coherence (weakly) | Weak - no ground truth |
| **Theory replication** | Application capability | #7 Theory-data fit (directly) | Strong - empirical test |
| **HotPotQA** | Multi-hop reasoning, retrieval | #10 Diagnosticity (partially) | Moderate - retrieval proxy |
| **Time series holdout** | Predictive capability | #3 Temporal (indirectly) | Weak - different purpose |
| **Multi-resolution** | Cross-level consistency | None directly | N/A - different framework |
| **Cross-modal** | Modality capabilities | None directly | N/A - different framework |

---

## Reality Check: Coverage Assessment

### What We Can Validate Well (✅)
- **Extraction Completeness** (#4) - Hand-coding gives direct ground truth
- **Entity Recognition** (#5) - Mechanical Turk provides baseline
- **Construct Validity** (#6) - COVID correlations are perfect test
- **Theory-Data Fit** (#7) - Replication tests directly validate

### What We Partially Validate (⚠️)
- **Cross-Source Coherence** (#2) - Inter-LLM gives weak signal
- **Temporal Relevance** (#3) - Time series might show something
- **Diagnosticity** (#10) - HotPotQA tests retrieval relevance
- **Confidence Calibration** (#12) - Can check post-hoc across tests

### What We Cannot Validate (❌)
- **Source Credibility** (#1) - No expert-rated source corpus
- **Study Limitations** (#8) - No hidden limitation dataset
- **Sampling Bias** (#9) - No bias test pairs
- **Sufficiency** (#11) - No sufficiency ground truth

---

## Key Insights

1. **Only 4 of 12 dimensions have strong validation** - The ones with clear ground truth
2. **Methods don't map cleanly to dimensions** - Each method tests something slightly different
3. **The mismatch reveals the real structure**:
   - We have **extraction validation** (hand-coding, Turk)
   - We have **meaning validation** (COVID correlations, replication)
   - We have **consistency validation** (inter-LLM)
   - We have **capability validation** (HotPotQA, multi-modal)

4. **The 12 dimensions assume a different task** - They're for assessing evidence quality in research, not validating a system

---

## Honest Assessment for Proposal

"We validate KGAS across multiple aspects of system performance:

**Direct Validation** (4 dimensions with ground truth):
- Extraction completeness via expert hand-coding
- Entity recognition via crowd validation
- Construct validity via psychological correlations
- Theory-data fit via replication studies

**Indirect Assessment** (4 dimensions with proxy measures):
- Cross-source coherence via inter-model agreement
- Temporal patterns via time series analysis
- Diagnosticity via retrieval benchmarks
- Confidence calibration via aggregate performance

**Not Validated** (4 dimensions requiring future work):
- Source credibility assessment
- Limitation detection
- Sampling bias identification
- Evidence sufficiency judgment

This validation strategy focuses on dimensions where ground truth is available or constructible within the scope of a dissertation project."