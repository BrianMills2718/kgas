# Concrete DAG Execution with Uncertainty Tracking

## Scenario Setup

Analyzing COVID vaccine discourse with Self-Categorization Theory:
- **Input**: 10,000 tweets from 500 users over 7 days
- **Reality**: 30% users missing psychology scores, 15% tweets missing timestamps
- **Goal**: Understand group polarization dynamics

## Phase 1: Theory Extraction

### Execution
```python
theory_extraction_request = ToolRequest(
    input_data={"pdf_path": "Turner_1986.pdf"},
    theory_schema=None,  # Extracting the schema
    options={"focus": "self_categorization"}
)

# T302 executes
theory_extraction_result = ToolResult(
    status="success",
    data={
        "theory_schema": {
            "constructs": ["prototype", "meta_contrast_ratio", "depersonalization"],
            "algorithms": {
                "mathematical": [{
                    "name": "meta_contrast_ratio",
                    "formula": "MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
                    "parameters": {"x_i": "position", "x_outgroup": "outgroup_positions"}
                }],
                "logical": [{
                    "name": "prototype_identification",
                    "rules": ["IF max_similarity_to_ingroup THEN is_prototype"]
                }]
            }
        }
    },
    uncertainty=ToolUncertainty(
        score=0.15,
        belief_masses=BeliefMass(support=0.85, reject=0.05, uncertain=0.10),
        justification="Turner 1986 is foundational text with explicit formulas. Minor uncertainty from interpreting 'depersonalization' operationalization.",
        contributing_factors=["Clear mathematical formula", "Some procedural elements require interpretation"],
        primary_dimension=UncertaintyDimension.THEORY_CONSTRUCT_ALIGNMENT,
        data_coverage=None,  # Not applicable for theory extraction
        propagates_to=["DYNAMIC_TOOL_GENERATOR"]  # Only affects tool generation
    )
)
```

## Phase 1.5: Dynamic Tool Generation (Critical Innovation!)

### Generate MCR Calculator from Theory
```python
generation_request = DynamicToolGenerationRequest(
    algorithm_spec=AlgorithmSpecification(
        name="meta_contrast_ratio",
        type=AlgorithmType.MATHEMATICAL,
        formula_or_rules="MCR_i = Σ|x_i - x_outgroup_j| / Σ|x_i - x_ingroup_k|",
        parameters={
            "x_i": "individual position vector",
            "x_outgroup": "outgroup member positions",
            "x_ingroup": "ingroup member positions"
        },
        required_inputs={
            "user_positions": "Dict[str, List[float]]",
            "group_assignments": "Dict[str, str]"
        },
        output_format={"mcr_scores": "Dict[str, float]"}
    ),
    theory_name="Self-Categorization Theory",
    context="Analyzing vaccine discourse groups"
)

# LLM generates tool code
generated_tool = GeneratedToolCode(
    tool_id="DYNAMIC_MCR_CALCULATOR",
    python_code="""
class GeneratedMCRCalculator(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        positions = request.input_data['user_positions']
        groups = request.input_data['group_assignments']
        
        mcr_scores = {}
        users_processed = 0
        users_skipped = 0
        
        for user_id, position in positions.items():
            if position is None:
                users_skipped += 1
                continue
                
            user_group = groups.get(user_id)
            if not user_group:
                users_skipped += 1
                continue
            
            # Calculate distances
            in_distances = []
            out_distances = []
            
            for other_id, other_pos in positions.items():
                if other_id == user_id or other_pos is None:
                    continue
                    
                distance = np.linalg.norm(np.array(position) - np.array(other_pos))
                
                if groups.get(other_id) == user_group:
                    in_distances.append(distance)
                else:
                    out_distances.append(distance)
            
            if in_distances and out_distances:
                mcr = sum(out_distances) / sum(in_distances)
                mcr_scores[user_id] = mcr
                users_processed += 1
        
        # Assess uncertainty based on ACTUAL coverage for MCR
        coverage = users_processed / (users_processed + users_skipped)
        
        # Contextual assessment
        if coverage > 0.8:
            uncertainty_score = 0.15
            justification = f"Strong MCR calculation with {coverage:.1%} coverage"
            masses = BeliefMass(support=0.82, reject=0.03, uncertain=0.15)
        elif coverage > 0.6:
            uncertainty_score = 0.25
            justification = f"Moderate MCR coverage at {coverage:.1%}"
            masses = BeliefMass(support=0.70, reject=0.15, uncertain=0.15)
        else:
            uncertainty_score = 0.40
            justification = f"Limited MCR coverage at {coverage:.1%}"
            masses = BeliefMass(support=0.55, reject=0.30, uncertain=0.15)
        
        return ToolResult(
            status="success",
            data={"mcr_scores": mcr_scores, "n_calculated": users_processed},
            uncertainty=ToolUncertainty(
                score=uncertainty_score,
                belief_masses=masses,
                justification=justification,
                contributing_factors=[
                    f"{users_processed} users with complete data",
                    f"{users_skipped} users skipped (missing data)",
                    "Position vectors derived from embeddings"
                ],
                primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
                data_coverage=coverage,
                propagates_to=["prototype_identification", "polarization_analysis"]
            )
        )
    """,
    algorithm_spec=generation_request.algorithm_spec,
    uncertainty_factors=[
        "Coverage of users with position data",
        "Quality of position vector derivation",
        "Group assignment clarity"
    ],
    imports_required=["numpy", "typing"],
    input_schema={"user_positions": "Dict", "group_assignments": "Dict"},
    output_schema={"mcr_scores": "Dict", "n_calculated": "int"}
)
```

## Phase 2: Data Loading (Parallel, Independent)

### Load Tweets (T06_JSON_LOAD)
```python
tweet_load_result = ToolResult(
    status="success",
    data={
        "tweets": [
            {"id": "t1", "user_id": "u1", "text": "Vaccines are safe", "timestamp": "2021-01-01T10:00:00"},
            {"id": "t2", "user_id": "u1", "text": "Trust the science", "timestamp": "2021-01-01T11:00:00"},
            # ... 9,998 more
        ]
    },
    uncertainty=ToolUncertainty(
        score=0.10,
        belief_masses=BeliefMass(support=0.88, reject=0.02, uncertain=0.10),
        justification="JSON loaded completely. 15% tweets missing timestamps won't affect user assignment or text analysis.",
        contributing_factors=["Complete JSON parse", "15% missing timestamps"],
        primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
        data_coverage=0.85,  # For temporal analysis specifically
        propagates_to=["temporal_analysis"]  # ONLY affects time-based analyses
    )
)
```

### Load Psychology Scores (T05_CSV_LOAD)
```python
psych_load_result = ToolResult(
    status="success",
    data={
        "psychology": {
            "u1": {"conspiracy_belief": 2.3, "trust_institutions": 7.8},
            "u2": {"conspiracy_belief": 6.7, "trust_institutions": 3.2},
            # ... 350 users with complete data (70%)
            "u351": None,  # Missing
            # ... 150 users missing (30%)
        }
    },
    uncertainty=ToolUncertainty(
        score=0.08,  # Low uncertainty for LOADING
        belief_masses=BeliefMass(support=0.90, reject=0.02, uncertain=0.08),
        justification="CSV parsed successfully. Missing values are explicit, not parsing errors.",
        contributing_factors=["Clean CSV format", "Missing values clearly marked"],
        primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
        data_coverage=1.0,  # Successfully loaded what was there
        propagates_to=[]  # Loading uncertainty doesn't propagate; missing data will affect specific analyses
    )
)
```

## Phase 3: Entity Extraction (Uses Tweets, Not Psychology)

### T23C_ONTOLOGY_AWARE_EXTRACTOR
```python
extraction_result = ToolResult(
    status="success",
    data={
        "entities": [
            {"user_id": "u1", "stance": "pro_vaccine", "certainty": 0.85},
            {"user_id": "u2", "stance": "vaccine_hesitant", "certainty": 0.72},
            # All 500 users extracted from tweets
        ]
    },
    uncertainty=ToolUncertainty(
        score=0.22,
        belief_masses=BeliefMass(support=0.75, reject=0.10, uncertain=0.15),
        justification="Stance detection from text has inherent ambiguity. All 500 users analyzed. Missing psychology data irrelevant for text extraction.",
        contributing_factors=[
            "Ambiguity in stance detection from text",
            "Some users have mixed signals",
            "Sarcasm detection challenges"
        ],
        primary_dimension=UncertaintyDimension.MEASUREMENT_VALIDITY,
        data_coverage=1.0,  # Extracted from all users' tweets
        propagates_to=["group_assignment", "stance_analysis"]
    )
)
```

## Phase 4: Graph Analysis (Independent of Psychology)

### Community Detection (T50_COMMUNITY_DETECT)
```python
community_result = ToolResult(
    status="success",
    data={
        "communities": {
            "community_A": ["u1", "u50", "u99", ...],  # 150 users
            "community_B": ["u2", "u67", "u204", ...],  # 200 users  
            "community_C": ["u3", "u88", "u350", ...],  # 150 users
        },
        "modularity": 0.72
    },
    uncertainty=ToolUncertainty(
        score=0.15,
        belief_masses=BeliefMass(support=0.82, reject=0.03, uncertain=0.15),
        justification="High modularity (0.72) indicates clear communities. Based on network structure only - psychology data not needed.",
        contributing_factors=[
            "Clear community structure (modularity=0.72)",
            "Stable across multiple runs",
            "Based on retweet/mention network"
        ],
        primary_dimension=UncertaintyDimension.MEASUREMENT_VALIDITY,
        data_coverage=1.0,  # All network data used
        propagates_to=["community_level_analyses", "group_comparisons"]
    )
)
```

### MCR Calculation (Dynamic Tool, Affected by Missing Positions)
```python
# Prepare data for MCR
# Note: Position vectors derived from tweet embeddings, not psychology scores
user_positions = {}
for user_id in all_users:
    # Get position from tweet embeddings
    tweets = get_user_tweets(user_id)
    if tweets:
        embeddings = embed_tweets(tweets)
        user_positions[user_id] = np.mean(embeddings, axis=0)  # Average embedding
    else:
        user_positions[user_id] = None

# Execute dynamically generated MCR tool
mcr_request = ToolRequest(
    input_data={
        "user_positions": user_positions,  # 450/500 have positions (90%)
        "group_assignments": community_result.data["communities"]
    }
)

mcr_result = ToolResult(
    status="success",
    data={
        "mcr_scores": {
            "u1": 3.2,  # High MCR - very different from outgroup
            "u2": 2.8,
            # ... 450 users with MCR scores
        },
        "n_calculated": 450
    },
    uncertainty=ToolUncertainty(
        score=0.18,  # Good coverage
        belief_masses=BeliefMass(support=0.78, reject=0.07, uncertain=0.15),
        justification="MCR calculated for 90% of users (450/500). Missing 10% due to no tweets, not psychology data.",
        contributing_factors=[
            "450 users with tweet-based positions",
            "50 users with no tweets to embed",
            "Embedding quality affects position accuracy"
        ],
        primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
        data_coverage=0.90,
        propagates_to=["prototype_identification"]
    )
)
```

## Phase 5: Psychology Analysis (Affected by Missing Data)

### SEM Modeling (T56_SEM_MODEL)
```python
sem_request = ToolRequest(
    input_data={
        "psychology_data": psych_load_result.data["psychology"],
        "behavioral_data": extraction_result.data["entities"]
    }
)

sem_result = ToolResult(
    status="success",
    data={
        "model_fit": {"CFI": 0.94, "RMSEA": 0.05},
        "path_coefficients": {
            "conspiracy_belief->vaccine_hesitancy": 0.67,
            "trust_institutions->vaccine_acceptance": 0.72
        },
        "n_complete_cases": 350  # Only 70% had psychology data
    },
    uncertainty=ToolUncertainty(
        score=0.28,
        belief_masses=BeliefMass(support=0.68, reject=0.17, uncertain=0.15),
        justification="Good model fit (CFI=0.94) but only 350/500 users (70%) had psychology data. Missing data may bias if not random.",
        contributing_factors=[
            "30% missing psychology scores",
            "Good fit for available data",
            "Potential selection bias"
        ],
        primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
        data_coverage=0.70,
        propagates_to=["psychological_predictions", "intervention_design"]
    )
)
```

## Phase 6: Aggregation - Tweet to User Level

### TWEET_USER_AGGREGATOR for user "u1"
```python
# User u1 has 23 tweets
tweet_evidences = []
for tweet in user_u1_tweets:
    # Each tweet was analyzed for stance
    tweet_evidence = EvidenceItem(
        id=tweet["id"],
        belief_masses=BeliefMass(
            support=0.70 + random.uniform(-0.1, 0.1),  # Varying confidence
            reject=0.15 + random.uniform(-0.05, 0.05),
            uncertain=0.15
        ),
        source_tool="T23C_ONTOLOGY_EXTRACTOR"
    )
    tweet_evidences.append(tweet_evidence)

aggregation_request = AggregationRequest(
    instances=tweet_evidences,
    aggregation_level=AggregationLevel.TWEET_TO_USER,
    aggregation_key="u1",
    method="dempster_shafer"
)

# Dempster-Shafer combination
combined = tweet_evidences[0].belief_masses
for evidence in tweet_evidences[1:]:
    K = combined.support * evidence.belief_masses.reject + combined.reject * evidence.belief_masses.support
    if K < 0.99:
        factor = 1 / (1 - K)
        combined = BeliefMass(
            support=factor * (combined.support * evidence.belief_masses.support + 
                             combined.support * evidence.belief_masses.uncertain +
                             combined.uncertain * evidence.belief_masses.support),
            reject=factor * (combined.reject * evidence.belief_masses.reject +
                           combined.reject * evidence.belief_masses.uncertain +
                           combined.uncertain * evidence.belief_masses.reject),
            uncertain=factor * combined.uncertain * evidence.belief_masses.uncertain
        )

user_aggregation_result = AggregationResult(
    status="success",
    data={"u1": {"aggregated_stance": "pro_vaccine", "strength": 0.82}},
    uncertainty=ToolUncertainty(
        score=0.12,  # Reduced from ~0.22 per tweet
        belief_masses=BeliefMass(support=0.84, reject=0.06, uncertain=0.10),
        justification="23 consistent tweets provide strong evidence. Aggregation reduced uncertainty by 45%.",
        contributing_factors=[
            "High consistency across tweets (low conflict)",
            "Sufficient sample size (23 tweets)",
            "Clear stance signals"
        ],
        primary_dimension=UncertaintyDimension.EVIDENCE_INTEGRATION,
        data_coverage=1.0,
        propagates_to=["user_level_analyses"]
    ),
    aggregated_beliefs={"u1": combined},
    conflict_metrics=ConflictMetrics(
        average_conflict=0.08,
        max_conflict=0.18,
        conflict_pairs=[("t1", "t15")],
        consensus_level="high"
    ),
    n_instances_per_key={"u1": 23},
    uncertainty_reduction=0.10
)
```

## Phase 7: Cross-Modal Synthesis

### Three Independent Analyses Converge
```python
synthesis_request = CrossModalSynthesisRequest(
    modality_results={
        "graph": ModalityEvidence(
            modality="graph",
            key_findings=[
                "Three distinct communities (modularity=0.72)",
                "High MCR for community leaders (avg 3.5)",
                "Dense within-group connections"
            ],
            belief_masses=BeliefMass(support=0.80, reject=0.05, uncertain=0.15),
            supporting_metrics={"modularity": 0.72, "avg_mcr": 3.5}
        ),
        "table": ModalityEvidence(
            modality="table",
            key_findings=[
                "Conspiracy belief predicts hesitancy (β=0.67)",
                "Trust inversely related (β=-0.72)",
                "70% data coverage affects generalization"
            ],
            belief_masses=BeliefMass(support=0.68, reject=0.17, uncertain=0.15),
            supporting_metrics={"cfi": 0.94, "rmsea": 0.05, "n": 350}
        ),
        "vector": ModalityEvidence(
            modality="vector",
            key_findings=[
                "Language divergence between groups (d=0.84)",
                "Within-group convergence over time",
                "Emotional language increases in hesitant group"
            ],
            belief_masses=BeliefMass(support=0.75, reject=0.10, uncertain=0.15),
            supporting_metrics={"between_distance": 0.84, "within_distance": 0.23}
        )
    },
    synthesis_goal="Understand vaccine hesitancy group dynamics"
)

# Assess convergence
convergence = ConvergenceAssessment(
    agreement_score=0.78,
    convergent_findings=[
        "Clear group boundaries exist",
        "Groups becoming more polarized over time",
        "Identity drives information processing"
    ],
    divergent_findings=[
        "Psychology data limited to 70% (table only)",
        "Some users change groups (graph shows, vectors don't)"
    ],
    explanation="Strong convergence on main findings despite different data coverage"
)

# Combine evidences with convergence bonus
synthesis_result = CrossModalSynthesisResult(
    status="success",
    data={
        "synthesis": {
            "main_finding": "Self-categorization drives vaccine hesitancy through group polarization",
            "confidence": "High (convergent evidence)",
            "effect_size": "Large (d=0.84 language, β=0.67 psychology)"
        }
    },
    uncertainty=ToolUncertainty(
        score=0.18,  # Reduced due to convergence
        belief_masses=BeliefMass(support=0.78, reject=0.07, uncertain=0.15),
        justification="Three independent modalities converge on same pattern. Psychology limitations don't undermine graph/vector findings.",
        contributing_factors=[
            "High convergence (0.78 agreement)",
            "Independent evidence sources",
            "Consistent effect sizes"
        ],
        primary_dimension=UncertaintyDimension.INFERENCE_CHAIN_VALIDITY,
        data_coverage=None,  # Synthesis, not data processing
        propagates_to=["final_conclusions", "interventions"]
    ),
    convergence=convergence,
    integrated_uncertainty=ToolUncertainty(
        score=0.18,
        belief_masses=BeliefMass(support=0.78, reject=0.07, uncertain=0.15),
        justification="Convergent evidence reduces uncertainty despite individual limitations",
        contributing_factors=["Cross-validation across modalities"],
        primary_dimension=UncertaintyDimension.EVIDENCE_INTEGRATION,
        data_coverage=None,
        propagates_to=["final_report"]
    ),
    primary_evidence_source="graph",  # Most complete data
    evidence_weights={"graph": 0.40, "vector": 0.35, "table": 0.25}
)
```

## Final Uncertainty Trace

### Building the Complete Trace
```python
dag_trace = DAGUncertaintyTrace(
    dag_id="sct_covid_analysis",
    execution_timestamp="2024-01-15T10:00:00Z",
    tool_traces=[
        UncertaintyFlow(
            tool_id="T302_THEORY_EXTRACTION",
            tool_type="extraction",
            inherited_uncertainties={},
            local_uncertainty=theory_extraction_result.uncertainty,
            output_uncertainty=theory_extraction_result.uncertainty,
            propagation_type=PropagationType.SEQUENTIAL,
            combination_method="initial"
        ),
        UncertaintyFlow(
            tool_id="T50_COMMUNITY_DETECT",
            tool_type="graph_analysis",
            inherited_uncertainties={},  # Independent of theory extraction
            local_uncertainty=community_result.uncertainty,
            output_uncertainty=community_result.uncertainty,
            propagation_type=PropagationType.PARALLEL,
            combination_method="independent"
        ),
        UncertaintyFlow(
            tool_id="DYNAMIC_MCR_CALCULATOR",
            tool_type="theory_specific",
            inherited_uncertainties={"theory": theory_extraction_result.uncertainty},
            local_uncertainty=mcr_result.uncertainty,
            output_uncertainty=ToolUncertainty(
                score=0.20,  # Slightly higher due to theory uncertainty
                belief_masses=BeliefMass(support=0.76, reject=0.09, uncertain=0.15),
                justification="MCR calculation affected by theory interpretation and 10% missing positions",
                contributing_factors=["Theory extraction uncertainty", "90% position coverage"],
                primary_dimension=UncertaintyDimension.DATA_COMPLETENESS,
                data_coverage=0.90,
                propagates_to=["prototype_identification"]
            ),
            propagation_type=PropagationType.SEQUENTIAL,
            combination_method="multiplicative"
        ),
        UncertaintyFlow(
            tool_id="T56_SEM_MODEL",
            tool_type="statistical",
            inherited_uncertainties={},  # Independent - uses raw psychology data
            local_uncertainty=sem_result.uncertainty,
            output_uncertainty=sem_result.uncertainty,
            propagation_type=PropagationType.PARALLEL,
            combination_method="independent"
        ),
        UncertaintyFlow(
            tool_id="TWEET_USER_AGGREGATOR",
            tool_type="aggregation",
            inherited_uncertainties={"extraction": extraction_result.uncertainty},
            local_uncertainty=user_aggregation_result.uncertainty,
            output_uncertainty=user_aggregation_result.uncertainty,  # Reduced through aggregation
            propagation_type=PropagationType.AGGREGATION,
            combination_method="dempster_shafer"
        ),
        UncertaintyFlow(
            tool_id="CROSS_MODAL_SYNTHESIZER",
            tool_type="synthesis",
            inherited_uncertainties={
                "graph": community_result.uncertainty,
                "table": sem_result.uncertainty,
                "vector": ToolUncertainty(score=0.15, belief_masses=BeliefMass(support=0.80, reject=0.05, uncertain=0.15))
            },
            local_uncertainty=synthesis_result.uncertainty,
            output_uncertainty=synthesis_result.integrated_uncertainty,  # Reduced through convergence
            propagation_type=PropagationType.VALIDATION,
            combination_method="convergence_reduction"
        )
    ],
    critical_uncertainties=[
        {
            "tool": "T56_SEM_MODEL",
            "score": 0.28,
            "reason": "30% missing psychology data limits psychological conclusions"
        },
        {
            "tool": "T23C_ONTOLOGY_EXTRACTOR", 
            "score": 0.22,
            "reason": "Stance detection from text has inherent ambiguity"
        }
    ],
    final_uncertainty=synthesis_result.integrated_uncertainty,
    improvement_suggestions=[
        "Collect psychology scores for remaining 30% of users",
        "Use multiple coders to validate stance extraction",
        "Gather more tweets per user for stronger aggregation",
        "Include external validation data"
    ]
)
```

## Key Insights from Execution

### 1. Localized Uncertainty
- Missing psychology data (30%) only affected SEM modeling (0.28 uncertainty)
- Did NOT affect: community detection (0.15), MCR calculation (0.18), text analysis (0.22)
- Each tool assessed based on its specific needs

### 2. Aggregation Power
- Individual tweets: ~0.22 uncertainty
- After aggregating 23 tweets: 0.12 uncertainty (45% reduction)
- Consistency across tweets increased confidence

### 3. Convergence Validation  
- Graph analysis: 0.15 uncertainty (complete network data)
- Table analysis: 0.28 uncertainty (missing psychology)
- Vector analysis: 0.15 uncertainty (complete text data)
- **Synthesis: 0.18 uncertainty** (convergence reduced it)

### 4. Dynamic Tool Context
- MCR calculator assessed its own data coverage (90%)
- Didn't blindly inherit all upstream uncertainty
- Context-aware assessment based on what it needed

### 5. Critical Path
- Most uncertainty from SEM (psychology) path
- But this didn't contaminate other analyses
- System can identify which conclusions are most/least certain

## Final Assessment

**Overall System Uncertainty: 0.18** (High confidence)

**Why this is good:**
- Despite 30% missing psychology, overall conclusions are strong
- Multiple independent analyses converged
- Aggregation and validation reduced uncertainty
- System correctly identified what is and isn't affected

**Specific Confidence Levels:**
- **Group structure**: High (0.15) - complete network data
- **Polarization dynamics**: High (0.18) - convergent evidence  
- **Psychological drivers**: Moderate (0.28) - missing data
- **Identity processes**: High (0.12) - strong text evidence

**This demonstrates:**
1. Uncertainty doesn't contaminate everything
2. Missing data has localized effects
3. Aggregation and convergence improve confidence
4. The system can work well even with imperfect data