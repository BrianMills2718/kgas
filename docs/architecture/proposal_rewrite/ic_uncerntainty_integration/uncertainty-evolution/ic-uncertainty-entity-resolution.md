# IC-Informed Entity Resolution Uncertainty

## Entity Resolution Confidence Framework

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Entity Resolution with IC Principles                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Core Principle: Evidence-Based Resolution (Not Format-Based)                   │
│  ─────────────────────────────────────────────────────────────                 │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                         Evidence Collection                              │  │
│  ├─────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                          │  │
│  │  Graph Evidence          Table Evidence         Text Evidence           │  │
│  │  ┌─────────────┐        ┌─────────────┐       ┌─────────────┐        │  │
│  │  │ Node Labels  │        │ Column Data │       │ Mentions    │        │  │
│  │  │ Relationships│        │ Row Context │       │ Pronouns    │        │  │
│  │  │ Properties   │        │ Aggregations│       │ Context     │        │  │
│  │  └──────┬──────┘        └──────┬──────┘       └──────┬──────┘        │  │
│  │         │                       │                      │               │  │
│  │         └───────────────────────┴──────────────────────┘               │  │
│  │                                 │                                       │  │
│  │                                 ▼                                       │  │
│  │                    All Evidence Treated Equally                         │  │
│  │                    (Quality-weighted, not format-biased)                │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Reference Type Classification                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ EXPLICIT NAMED ENTITY                          Confidence: 0.90 - 0.99   │  │
│  │ ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │ │ Examples:                                                        │    │  │
│  │ │ • "President Biden announced..."                                │    │  │
│  │ │ • "Microsoft Corporation filed..."                              │    │  │
│  │ │ • "Dr. Jane Smith's research shows..."                          │    │  │
│  │ │                                                                  │    │  │
│  │ │ Characteristics:                                                 │    │  │
│  │ │ • Clear proper noun or title                                    │    │  │
│  │ │ • Unambiguous in context                                        │    │  │
│  │ │ • Direct named reference                                        │    │  │
│  │ └─────────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ CONTEXTUAL PRONOUN                             Confidence: 0.70 - 0.90   │  │
│  │ ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │ │ Examples:                                                        │    │  │
│  │ │ • "Biden spoke. He said..." (clear antecedent)                  │    │  │
│  │ │ • "The company announced. It will..." (recent reference)        │    │  │
│  │ │ • "After the meeting, they decided..." (participant list known) │    │  │
│  │ │                                                                  │    │  │
│  │ │ Factors affecting confidence:                                    │    │  │
│  │ │ • Distance to antecedent                                        │    │  │
│  │ │ • Number of intervening entities                                │    │  │
│  │ │ • Clarity of context                                            │    │  │
│  │ └─────────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ AMBIGUOUS GROUP REFERENCE                       Confidence: 0.50 - 0.75   │  │
│  │ ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │ │ Examples:                                                        │    │  │
│  │ │ • "They opposed the legislation" (multiple groups possible)     │    │  │
│  │ │ • "The organizations met" (which organizations?)                │    │  │
│  │ │ • "Several senators argued" (subset unclear)                    │    │  │
│  │ │                                                                  │    │  │
│  │ │ Challenges:                                                      │    │  │
│  │ │ • Multiple valid candidates                                      │    │  │
│  │ │ • Vague collective terms                                         │    │  │
│  │ │ • Cultural/contextual ambiguity                                 │    │  │
│  │ └─────────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ STRATEGIC AMBIGUITY                             Confidence: 0.25 - 0.50   │  │
│  │ ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │ │ Examples:                                                        │    │  │
│  │ │ • "Sources close to the matter" (deliberately vague)            │    │  │
│  │ │ • "Some members of Congress" (intentionally non-specific)       │    │  │
│  │ │ • "It has been suggested that" (passive voice obscuration)      │    │  │
│  │ │                                                                  │    │  │
│  │ │ Indicators:                                                      │    │  │
│  │ │ • Intentional vagueness                                          │    │  │
│  │ │ • Political hedging                                              │    │  │
│  │ │ • Source protection                                              │    │  │
│  │ └─────────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ NO CONTEXT                                       Confidence: 0.10 - 0.30   │  │
│  │ ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │ │ Examples:                                                        │    │  │
│  │ │ • Pronoun at document start                                     │    │  │
│  │ │ • Reference with no prior context                               │    │  │
│  │ │ • Isolated quote without attribution                            │    │  │
│  │ │                                                                  │    │  │
│  │ │ Resolution approach:                                             │    │  │
│  │ │ • Assign high uncertainty                                        │    │  │
│  │ │ • Flag for human review                                          │    │  │
│  │ │ • Seek additional context                                        │    │  │
│  │ └─────────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    Resolution Algorithm                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  1. Collect all evidence (graph, table, text)                                  │
│  2. Apply ICD-206 quality assessment to each piece                             │
│  3. Weight evidence by quality, not source format                              │
│  4. Calculate probability distribution over candidates                          │
│  5. Apply Heuer's principle: More agreement ≠ higher accuracy                  │
│  6. Assign confidence based on reference type and evidence quality             │
│  7. Output IC-standard uncertainty assessment                                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Entity Resolution Principles

1. **Evidence Quality Over Quantity**: ICD-206 assessment trumps simple vote counting
2. **Format Agnostic**: Graph/Table/Text evidence evaluated equally by quality
3. **Realistic Confidence**: LLMs excel at context but have limits
4. **Strategic Ambiguity Recognition**: Some vagueness is intentional
5. **Transparent Uncertainty**: Clear confidence ranges for each reference type