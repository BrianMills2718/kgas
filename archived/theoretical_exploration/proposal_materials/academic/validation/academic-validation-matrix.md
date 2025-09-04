# KGAS Validation Matrix - Actual Planned Tests

## Single Matrix Approach: All Planned Validation Activities

| **Validation Test** | **What It Validates** | **Method** | **Actual Dataset/Source** | **Metric** | **Why This Matters** | **Timeline** |
|-------------------|---------------------|-----------|-------------------------|------------|---------------------|-------------|
| **HotPotQA Multi-hop Retrieval** | System can trace complex theoretical connections | Test knowledge graph against HotPotQA queries | HotPotQA benchmark dataset | F1 score (report actual, no target) | Validates retrieval & reasoning core capability | Week 1-2 |
| **COVID Construct Correlations** | Extracted constructs are meaningful | Extract psychological constructs from tweets → correlate with self-reported measures | Kunst et al. COVID dataset: 2,506 Twitter users with validated psychology scales | Pearson r (any positive correlation is success) | Proves system extracts real psychological signal | Week 3-5 |
| **Hand-Coded Theory Comparison** | System extracts theory structure correctly | You hand-code 5-10 theories with V13 meta-schema → compare to system extraction | Academic papers you select (Young 1996, etc.) | Concept overlap %, relationship accuracy | Ground truth for theory extraction capability | Week 2-3 |
| **Inter-LLM Reliability** | Extraction is reproducible | Extract same theories with GPT-4, Claude, Gemini | Same 5-10 papers as hand-coding | Agreement score (note: consistency ≠ correctness) | Shows method stability across models | Week 1 |
| **Theory Replication Test** | System can apply extracted theories | Extract theory → apply to paper's original data → compare conclusions | 3-5 papers with available datasets (ANES, OSF papers, Pew data) | % key findings replicated | Ultimate test: can system do science? | Week 6-8 |
| **Mechanical Turk Simple Tasks** | Basic extraction accuracy | 500 tweets coded for: sentiment, entities mentioned, causal claims | Twitter data sample | Precision/Recall/F1 vs crowd truth | Baseline extraction validation | Week 2 |
| **Time Series Prediction** | Theory-based prediction (optional) | Hide last 20% of temporal data, predict using extracted theories | Any temporal dataset (COVID timeline, etc.) | Correlation between predicted & actual | Tests if theories have predictive power | Week 12 |
| **Multi-Resolution Consistency** | Patterns coherent across levels | Analyze same COVID data at: individual (user traits), network (clusters), population (trends) | COVID dataset | Qualitative: Do patterns align? | Tests Davis's multi-resolution principle | Week 9 |
| **Cross-Modal Capabilities** | Each modality adds unique value | Apply graph/table/vector analysis to same data | COVID or other dataset | Document what each enables (not convergence) | Shows value of multi-modal approach | Week 9 |
| **Sentiment Baseline Check** | Meets established NLP standards | Compare to published sentiment analysis benchmarks | Reference: "BERT achieves 94% on Twitter" | Match published baselines | Sanity check on basic NLP | Week 1 |
| **Paper + Dataset Replication** | Full pipeline validation | Extract methodology → apply to data → compare to published results | Papers with replication packages | Statistical findings match % | End-to-end system validation | Week 10-11 |

---

## Two Matrix Approach

### Matrix 1: Core System Capabilities - What Can KGAS Do?

| **Capability** | **Validation Test** | **Real Data We'll Use** | **What Success Looks Like** | **Week** |
|---------------|---------------------|------------------------|----------------------------|----------|
| **Theory Extraction** | Hand-coded comparison | 5-10 papers (Young 1996, etc.) + your V13 coding | Captures majority of concepts/relationships | 2-3 |
| **Multi-hop Reasoning** | HotPotQA benchmark | HotPotQA dataset | Any positive F1 score | 1-2 |
| **Construct Detection** | COVID correlations | 2,506 users with psych profiles | Any significant correlation (p<0.05) | 3-5 |
| **Theory Application** | Replication studies | 3-5 papers with data (ANES, OSF) | Reproduces some key findings | 6-8 |
| **Basic NLP** | Crowd validation | 500 Mechanical Turk coded tweets | Reasonable F1 (>0.5) | 2 |
| **Reproducibility** | Inter-LLM agreement | Same papers, 3+ LLMs | High consistency (>70%) | 1 |

### Matrix 2: Advanced Validation - How Well Does KGAS Perform?

| **Advanced Test** | **Method** | **Baseline/Comparison** | **What We Learn** | **Priority** |
|------------------|-----------|------------------------|------------------|--------------|
| **Multi-Resolution** | 3-level COVID analysis | Individual→Network→Population coherence | If patterns are consistent across scales | MEDIUM |
| **Cross-Modal Value** | Graph vs Table vs Vector on same data | Document unique insights per mode | What each modality uniquely provides | HIGH |
| **Prediction** | Time series holdout | Correlation with actual (expect low) | Whether theories have predictive power | LOW |
| **Full Pipeline** | Complete paper→data→results | Published paper results | End-to-end system performance | HIGH |
| **Sentiment Sanity Check** | Compare to BERT baseline | Published benchmarks | Basic NLP competence | LOW |

---

## Simplified Decision Version

### What We're Actually Doing: Validation Priority List

| **Must Do** (Proof of Concept) | **Data Ready** | **Effort** |
|--------------------------------|---------------|------------|
| ✓ Hand-code 5-10 theories for comparison | You + papers | 1 week |
| ✓ COVID construct correlations | Kunst dataset available | 1 week |
| ✓ HotPotQA multi-hop test | Benchmark available | 2 days |
| ✓ Inter-LLM reliability test | Just need API access | 1 day |
| ✓ Basic crowd coding validation | $200-300 Mechanical Turk | 3 days |

| **Should Do** (Strengthens Case) | **Data Needs** | **Effort** |
|----------------------------------|---------------|------------|
| ⟳ Theory replication (3 papers) | Find papers with data | 2 weeks |
| ⟳ Multi-resolution COVID analysis | Already have data | 3 days |
| ⟳ Cross-modal comparison | Any dataset | 2 days |

| **Could Do** (If Time) | **Data Needs** | **Effort** |
|----------------------|---------------|------------|
| ○ Time series prediction | Temporal data | 1 week |
| ○ Full pipeline test | Complete paper+data | 1 week |
| ○ Extended crowd coding | More funds | 1 week |

---

## Key Principles for All Tests:
1. **No targets** - We report what we get
2. **Real data** - COVID dataset, HotPotQA, actual papers
3. **Mixed methods** - Quantitative (correlations) + Qualitative (multi-resolution)
4. **System validation** - Testing KGAS capabilities, not theory truth
5. **Feasible scope** - Can complete in ~12 weeks