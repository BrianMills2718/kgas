# IC-Informed Uncertainty Framework - Mermaid Diagrams

## Overall System Flow

```mermaid
graph TB
    subgraph Input
        RQ[Research Question]
        EV[Evidence Sources]
        CTX[Context]
    end
    
    subgraph "IC Standards"
        ICD203[ICD-203 Probability Bands]
        ICD206[ICD-206 Source Quality]
        HEUER[Heuer's Principles]
    end
    
    subgraph "Single LLM Analysis"
        ASSUMPTIONS[Key Assumptions Check]
        ACH[Alternative Hypotheses]
        DIAG[Diagnostic Evidence]
        GAPS[Information Gaps]
        DECEPTION[Deception Detection]
        ICPROB[IC Probability Assignment]
        CONF[Confidence Assessment]
    end
    
    subgraph "Mathematical Propagation"
        RSS[Root-Sum-Squares]
        COV[Covariance Matrix]
        PROP[Uncertainty Propagation]
    end
    
    subgraph Output
        BAND[IC Probability Band]
        LEVEL[Confidence Level]
        REPORT[Uncertainty Report]
    end
    
    RQ --> ASSUMPTIONS
    EV --> ASSUMPTIONS
    CTX --> ASSUMPTIONS
    
    ICD203 -.-> ICPROB
    ICD206 -.-> DIAG
    HEUER -.-> CONF
    
    ASSUMPTIONS --> ACH
    ACH --> DIAG
    DIAG --> GAPS
    GAPS --> DECEPTION
    DECEPTION --> ICPROB
    ICPROB --> CONF
    
    CONF --> RSS
    RSS --> PROP
    COV --> PROP
    
    PROP --> BAND
    PROP --> LEVEL
    BAND --> REPORT
    LEVEL --> REPORT
    
    classDef input fill:#e1f5fe
    classDef ic fill:#f3e5f5
    classDef llm fill:#fff9c4
    classDef math fill:#c8e6c9
    classDef output fill:#ffccbc
    
    class RQ,EV,CTX input
    class ICD203,ICD206,HEUER ic
    class ASSUMPTIONS,ACH,DIAG,GAPS,DECEPTION,ICPROB,CONF llm
    class RSS,COV,PROP math
    class BAND,LEVEL,REPORT output
```

## Entity Resolution Flow

```mermaid
graph LR
    subgraph "Evidence Sources"
        GE[Graph Evidence]
        TE[Table Evidence]
        TXE[Text Evidence]
    end
    
    subgraph "Reference Types"
        EXP[Explicit Named<br/>0.90-0.99]
        CON[Contextual Pronoun<br/>0.70-0.90]
        AMB[Ambiguous Group<br/>0.50-0.75]
        STR[Strategic Ambiguity<br/>0.25-0.50]
        NOC[No Context<br/>0.10-0.30]
    end
    
    subgraph "Quality Assessment"
        Q206[ICD-206 Quality]
        WEIGHT[Quality Weighting]
        DIST[Probability Distribution]
    end
    
    subgraph "Resolution"
        RES[Entity Resolution]
        UNC[Uncertainty Assignment]
        OUT[Resolution Output]
    end
    
    GE --> Q206
    TE --> Q206
    TXE --> Q206
    
    Q206 --> WEIGHT
    WEIGHT --> DIST
    
    DIST --> RES
    
    EXP --> UNC
    CON --> UNC
    AMB --> UNC
    STR --> UNC
    NOC --> UNC
    
    RES --> OUT
    UNC --> OUT
    
    classDef evidence fill:#e3f2fd
    classDef reftype fill:#f3e5f5
    classDef quality fill:#fff9c4
    classDef resolution fill:#c8e6c9
    
    class GE,TE,TXE evidence
    class EXP,CON,AMB,STR,NOC reftype
    class Q206,WEIGHT,DIST quality
    class RES,UNC,OUT resolution
```

## Uncertainty Propagation

```mermaid
graph TD
    subgraph "Stage Uncertainties"
        S1[σ_source = 0.10]
        S2[σ_entity = 0.05]
        S3[σ_process = 0.05]
    end
    
    subgraph "Propagation Method"
        IND{Independent?}
        RSS_CALC[["σ_total = √(σ₁² + σ₂² + σ₃²)"]]
        COV_CALC[["σ_total² = σᵀ Σ σ"]]
    end
    
    subgraph "IC Mapping"
        TOTAL[σ_total = 0.122]
        MAP{Map to IC Band}
        
        AC[Almost Certain<br/>σ < 0.05]
        VL[Very Likely<br/>0.05-0.10]
        L[Likely<br/>0.10-0.20]
        REC[Roughly Even<br/>0.20-0.30]
        U[Unlikely<br/>0.30-0.40]
        VU[Very Unlikely<br/>0.40-0.50]
        ANC[Almost No Chance<br/>σ > 0.50]
    end
    
    S1 --> IND
    S2 --> IND
    S3 --> IND
    
    IND -->|Yes| RSS_CALC
    IND -->|No| COV_CALC
    
    RSS_CALC --> TOTAL
    COV_CALC --> TOTAL
    
    TOTAL --> MAP
    
    MAP --> AC
    MAP --> VL
    MAP --> L
    MAP --> REC
    MAP --> U
    MAP --> VU
    MAP --> ANC
    
    L -.->|Selected| OUTPUT[IC Band: "Likely"]
    
    classDef stage fill:#e1f5fe
    classDef calc fill:#fff9c4
    classDef band fill:#c8e6c9
    classDef selected fill:#ffccbc,stroke:#f44336,stroke-width:3px
    
    class S1,S2,S3 stage
    class IND,RSS_CALC,COV_CALC,TOTAL,MAP calc
    class AC,VL,L,REC,U,VU,ANC band
    class L selected
```

## IC Analysis Components

```mermaid
graph LR
    subgraph "IC Methodologies"
        direction TB
        A[1. Assumptions Check]
        B[2. Alternative Hypotheses]
        C[3. Evidence Evaluation]
        D[4. Information Gaps]
        E[5. Deception Detection]
        F[6. Confidence Calibration]
        
        A --> B
        B --> C
        C --> D
        D --> E
        E --> F
    end
    
    subgraph "Output Structure"
        direction TB
        O1[Assumptions List]
        O2[Ranked Hypotheses]
        O3[Evidence Quality]
        O4[Critical Gaps]
        O5[Deception Risk]
        O6[IC Probability Band]
        O7[Confidence Level]
    end
    
    A -.-> O1
    B -.-> O2
    C -.-> O3
    D -.-> O4
    E -.-> O5
    F -.-> O6
    F -.-> O7
    
    classDef method fill:#f3e5f5
    classDef output fill:#c8e6c9
    
    class A,B,C,D,E,F method
    class O1,O2,O3,O4,O5,O6,O7 output
```