# Twitter Political Analysis: Practical Uncertainty Schemas

## Core Uncertainty Schema (Used Everywhere)

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class UniversalUncertainty(BaseModel):
    """Single uncertainty format for ALL operations"""
    uncertainty: float = Field(ge=0, le=1, description="0=certain, 1=uncertain")
    reasoning: str = Field(description="Expert reasoning for assessment")
    evidence_count: Optional[int] = Field(default=None, description="Number of evidences considered")
    data_coverage: Optional[float] = Field(default=None, description="Fraction of needed data available")
```

## Tool Result Schemas

### T06_JSON_LOAD Output Schema
```python
class TwitterDataLoad(BaseModel):
    """Output from loading Twitter JSON"""
    tweets: List[Dict[str, Any]]
    follow_edges: List[Dict[str, str]]  # {follower: id, followed: id}
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class T06Result(BaseModel):
    data: TwitterDataLoad
    uncertainty: UniversalUncertainty
    execution_time: float
    memory_used: int
```

### T31_ENTITY_BUILDER Output Schema
```python
class UserEntity(BaseModel):
    """User entity from tweets"""
    id: str
    type: str = "User"
    tweet_count: int
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

class T31Result(BaseModel):
    data: Dict[str, UserEntity]  # user_id -> entity
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T34_EDGE_BUILDER Output Schema
```python
class FollowEdge(BaseModel):
    """Follow relationship"""
    source: str
    target: str
    type: str = "FOLLOWS"
    weight: float = 1.0

class T34Result(BaseModel):
    data: List[FollowEdge]
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T50_COMMUNITY_DETECTION Output Schema
```python
class CommunityDetectionResult(BaseModel):
    """Community detection output"""
    user_communities: Dict[str, str]  # user_id -> community_id
    community_members: Dict[str, List[str]]  # community_id -> [user_ids]
    n_communities: int
    modularity: float
    community_sizes: List[int]

class T50Result(BaseModel):
    data: CommunityDetectionResult
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T23C_ONTOLOGY_AWARE_EXTRACTOR Output Schema
```python
class UserSentiment(BaseModel):
    """Sentiment data for a user"""
    user_id: str
    community: str
    biden_sentiments: List[float]  # -1 to 1
    trump_sentiments: List[float]  # -1 to 1
    tweet_count: int
    
class ExtractionResult(BaseModel):
    """Extraction output"""
    user_sentiments: Dict[str, UserSentiment]  # user_id -> sentiment
    total_extractions: int
    extraction_rate: float
    politicians_found: List[str]

class T23CResult(BaseModel):
    data: ExtractionResult
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T56_GRAPH_METRICS Output Schema
```python
class SentimentStats(BaseModel):
    """Statistics for sentiment"""
    mean: Optional[float]
    std: Optional[float]
    count: int
    positive_count: int
    negative_count: int
    neutral_count: int

class CommunityMetrics(BaseModel):
    """Metrics for a community"""
    community_id: str
    size: int
    users_with_sentiment: int
    biden_sentiment: SentimentStats
    trump_sentiment: SentimentStats
    coverage: float  # % of community with sentiment data

class T56Result(BaseModel):
    data: Dict[str, CommunityMetrics]  # community_id -> metrics
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T58_GRAPH_COMPARISON Output Schema
```python
class StatisticalComparison(BaseModel):
    """Statistical test results"""
    community1: str
    community2: str
    politician: str
    mean_diff: float
    effect_size: float
    t_statistic: float
    p_value: float
    significant: bool
    sample_sizes: Dict[str, int]

class ComparisonResult(BaseModel):
    """All comparison results"""
    comparisons: List[StatisticalComparison]
    summary: Dict[str, Any]

class T58Result(BaseModel):
    data: ComparisonResult
    uncertainty: UniversalUncertainty
    execution_time: float
```

### T60_GRAPH_EXPORT Output Schema
```python
class ExportResult(BaseModel):
    """Export confirmation"""
    export_path: str
    format: str
    records_exported: int
    file_size_bytes: int

class T60Result(BaseModel):
    data: ExportResult
    uncertainty: UniversalUncertainty
    execution_time: float
```

## Uncertainty Assessment Context Schemas

These schemas structure the context passed to the LLM for uncertainty assessment:

```python
class AssessmentContext(BaseModel):
    """Base context for uncertainty assessment"""
    operation_type: str
    tool_id: str
    timestamp: str

class DataLoadContext(AssessmentContext):
    """Context for data loading assessment"""
    operation_type: str = "data_load"
    tweet_count: int
    edge_count: int
    user_coverage: float  # % users in both tweets and graph
    missing_fields: List[str]
    file_size_mb: float

class CommunityDetectionContext(AssessmentContext):
    """Context for community detection assessment"""
    operation_type: str = "community_detection"
    modularity: float
    n_communities: int
    min_community_size: int
    max_community_size: int
    algorithm: str = "louvain"
    graph_density: float

class ExtractionContext(AssessmentContext):
    """Context for extraction assessment"""
    operation_type: str = "entity_extraction"
    extraction_rate: float
    tweets_processed: int
    ambiguous_cases: int
    politicians_found: List[str]
    sentiment_clarity: float  # 0-1 how clear sentiments are

class AggregationContext(AssessmentContext):
    """Context for aggregation assessment"""
    operation_type: str = "aggregation"
    aggregation_level: str  # "tweet_to_user" or "user_to_community"
    evidence_count: int
    uncertainties: List[float]  # Individual uncertainties being aggregated
    agreement_score: float  # 0-1 how much evidences agree
    conflict_cases: int

class StatisticalContext(AssessmentContext):
    """Context for statistical comparison assessment"""
    operation_type: str = "statistical_test"
    test_type: str = "t_test"
    sample_sizes: Dict[str, int]
    effect_sizes: List[float]
    p_values: List[float]
    power_analysis: Optional[float]
```

## Workflow Orchestration Schema

```python
class WorkflowStep(BaseModel):
    """Single step in analysis workflow"""
    step_id: str
    tool_id: str
    input_refs: List[str]  # References to previous step outputs
    parameters: Dict[str, Any]
    
class WorkflowDAG(BaseModel):
    """Complete workflow specification"""
    workflow_id: str
    description: str
    steps: List[WorkflowStep]
    dependencies: Dict[str, List[str]]  # step_id -> [depends_on]

class WorkflowResult(BaseModel):
    """Final workflow output"""
    workflow_id: str
    final_uncertainty: UniversalUncertainty
    step_results: Dict[str, Any]  # step_id -> result
    convergence_analysis: Optional[str]  # Cross-modal convergence
    key_findings: List[str]
```

## Example Usage: Uncertainty Assessment

```python
def assess_community_detection_uncertainty(
    result: CommunityDetectionResult,
    graph_stats: Dict[str, Any]
) -> UniversalUncertainty:
    """Assess uncertainty for community detection"""
    
    # Build context for LLM
    context = CommunityDetectionContext(
        tool_id="T50_COMMUNITY_DETECTION",
        timestamp=datetime.now().isoformat(),
        modularity=result.modularity,
        n_communities=result.n_communities,
        min_community_size=min(result.community_sizes),
        max_community_size=max(result.community_sizes),
        graph_density=graph_stats["density"]
    )
    
    # LLM assessment
    prompt = f"""
    Assess uncertainty for community detection with these characteristics:
    {context.json(indent=2)}
    
    Consider:
    - Modularity score (higher = clearer communities)
    - Community sizes (very small = less reliable)
    - Graph density (affects algorithm performance)
    
    Return UniversalUncertainty with your assessment.
    """
    
    return llm.structured_output(prompt, UniversalUncertainty)
```

## Example: Tweet-to-User Aggregation

```python
def aggregate_tweet_sentiments(
    tweet_sentiments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Aggregate multiple tweet sentiments to user level"""
    
    # Calculate agreement between tweets
    sentiments = [t["sentiment"] for t in tweet_sentiments]
    agreement_score = 1 - np.std(sentiments) if len(sentiments) > 1 else 0.5
    
    # Build aggregation context
    context = AggregationContext(
        tool_id="TWEET_USER_AGGREGATOR",
        timestamp=datetime.now().isoformat(),
        aggregation_level="tweet_to_user",
        evidence_count=len(tweet_sentiments),
        uncertainties=[t["uncertainty"] for t in tweet_sentiments],
        agreement_score=agreement_score,
        conflict_cases=sum(1 for s in sentiments if abs(s) < 0.1)  # neutral
    )
    
    # Get aggregated uncertainty
    prompt = f"""
    Assess aggregated uncertainty for combining {len(tweet_sentiments)} tweets:
    {context.json(indent=2)}
    
    Individual tweet uncertainties: {context.uncertainties}
    Agreement score: {context.agreement_score:.2f}
    
    Should multiple agreeing tweets reduce uncertainty?
    Should conflicting tweets maintain/increase it?
    
    Return UniversalUncertainty with aggregated assessment.
    """
    
    aggregated_uncertainty = llm.structured_output(prompt, UniversalUncertainty)
    
    return {
        "user_sentiment": np.mean(sentiments),
        "uncertainty": aggregated_uncertainty,
        "evidence_count": len(tweet_sentiments)
    }
```

## Key Design Principles

1. **Single Uncertainty Schema**: `UniversalUncertainty` used everywhere
2. **Structured Contexts**: Typed contexts for different assessment scenarios
3. **Clear Data Flow**: Each tool's output schema feeds into next tool's input
4. **No Magic Numbers**: All uncertainty comes from LLM assessment with reasoning
5. **Aggregation Aware**: Schemas support evidence aggregation patterns

## Benefits of This Schema Design

- **Type Safety**: Pydantic validation ensures data integrity
- **Clear Interfaces**: Each tool knows exactly what it receives and produces
- **Traceable Uncertainty**: Every uncertainty has reasoning and evidence count
- **Flexible Assessment**: Context schemas can include any relevant factors
- **Natural Aggregation**: The LLM understands when evidences should reduce uncertainty

This schema design provides the structure needed for implementation while maintaining the flexibility of pure LLM intelligence for uncertainty assessment.