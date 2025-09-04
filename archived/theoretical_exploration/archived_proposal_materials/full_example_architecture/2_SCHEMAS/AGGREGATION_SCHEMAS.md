# Aggregation Schemas for KGAS

## Overview
Aggregation tools are **persistent infrastructure** that reduce uncertainty by combining multiple pieces of evidence. They are NOT dynamically generated but are generic tools that work across theories.

## Core Aggregation Levels

### 1. Tweet → User Aggregation
Combines multiple tweet-level assessments into user-level beliefs

### 2. User → Community Aggregation  
Combines individual user assessments into community-level characteristics

### 3. Temporal Window Aggregation
Combines time-sliced data into temporal patterns

### 4. Cross-Modal Aggregation
Combines evidence from different modalities (graph, table, vector)

## Aggregation Schemas

### Tweet to User Aggregation

```python
from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum

class AggregationLevel(str, Enum):
    TWEET_TO_USER = "tweet_to_user"
    USER_TO_COMMUNITY = "user_to_community"
    TEMPORAL_WINDOW = "temporal_window"
    CROSS_MODAL = "cross_modal"

class BeliefMass(BaseModel):
    """Dempster-Shafer belief mass assignment"""
    support: float = Field(ge=0, le=1)
    reject: float = Field(ge=0, le=1)
    uncertain: float = Field(ge=0, le=1)
    
    def validate_sum(self):
        total = self.support + self.reject + self.uncertain
        assert abs(total - 1.0) < 0.001, f"Masses must sum to 1.0, got {total}"

class EvidenceItem(BaseModel):
    """Single piece of evidence to aggregate"""
    id: str = Field(description="Identifier (tweet_id, user_id, etc)")
    belief_masses: BeliefMass
    source_tool: str = Field(description="Tool that generated this evidence")
    confidence: float = Field(ge=0, le=1, description="Confidence in this evidence")
    metadata: Optional[Dict] = None

class TweetUserAggregationRequest(BaseModel):
    """Request to aggregate tweets to user level"""
    user_id: str
    tweet_evidences: List[EvidenceItem]
    aggregation_method: str = Field(default="dempster_shafer")

class TweetUserAggregationResult(BaseModel):
    """Result of tweet to user aggregation"""
    user_id: str
    aggregated_belief: BeliefMass
    n_tweets: int
    
    # Aggregation metrics
    consistency_score: float = Field(
        ge=0, le=1,
        description="How consistent the tweets were"
    )
    conflict_level: float = Field(
        ge=0, le=1, 
        description="Amount of conflict between tweets"
    )
    
    # Uncertainty reduction
    input_avg_uncertainty: float
    output_uncertainty: float
    uncertainty_reduction: float = Field(
        description="How much aggregation reduced uncertainty"
    )
    
    # Details
    high_conflict_pairs: List[tuple] = Field(
        default_factory=list,
        description="Tweet pairs with high disagreement"
    )
```

### User to Community Aggregation

```python
class UserCommunityAggregationRequest(BaseModel):
    """Request to aggregate users to community level"""
    community_id: str
    user_evidences: List[EvidenceItem]
    aggregation_method: str = Field(default="weighted_dempster_shafer")
    
    # Weighting factors
    weight_by_influence: bool = Field(
        default=True,
        description="Weight users by their network influence"
    )
    influence_scores: Optional[Dict[str, float]] = None

class UserCommunityAggregationResult(BaseModel):
    """Result of user to community aggregation"""
    community_id: str
    aggregated_belief: BeliefMass
    n_users: int
    
    # Community characteristics
    homogeneity: float = Field(
        ge=0, le=1,
        description="How similar users are within community"
    )
    polarization: float = Field(
        ge=0, le=1,
        description="How extreme the community beliefs are"
    )
    
    # Prototype identification
    prototype_users: List[str] = Field(
        default_factory=list,
        description="Most representative users"
    )
    
    # Uncertainty
    aggregated_uncertainty: float
    confidence_justification: str
```

### Cross-Modal Aggregation

```python
class ModalityEvidence(BaseModel):
    """Evidence from one analysis modality"""
    modality: str = Field(description="graph, table, or vector")
    belief_masses: BeliefMass
    confidence: float = Field(ge=0, le=1)
    key_findings: List[str]
    supporting_metrics: Dict[str, float]

class CrossModalAggregationRequest(BaseModel):
    """Request to aggregate across modalities"""
    hypothesis: str = Field(description="What we're testing")
    modality_evidences: List[ModalityEvidence]
    
class CrossModalAggregationResult(BaseModel):
    """Result of cross-modal aggregation"""
    integrated_belief: BeliefMass
    
    # Convergence metrics
    convergence_score: float = Field(
        ge=0, le=1,
        description="How well modalities agree"
    )
    primary_modality: str = Field(
        description="Most informative modality"
    )
    
    # Conflict analysis
    conflicts: List[Dict] = Field(
        default_factory=list,
        description="Where modalities disagree"
    )
    
    # Uncertainty reduction from convergence
    uncertainty_before_convergence: float
    uncertainty_after_convergence: float
    convergence_benefit: float
```

## Aggregation Algorithms

### Dempster-Shafer Combination

```python
class DempsterShaferAggregator:
    """Core aggregation algorithm using Dempster-Shafer theory"""
    
    def aggregate(self, evidences: List[BeliefMass]) -> BeliefMass:
        """Combine multiple belief masses"""
        if not evidences:
            return BeliefMass(support=0, reject=0, uncertain=1)
        
        combined = evidences[0]
        conflicts = []
        
        for evidence in evidences[1:]:
            # Calculate conflict
            K = (combined.support * evidence.reject + 
                 combined.reject * evidence.support)
            
            if K >= 0.99:  # Near complete conflict
                conflicts.append((combined, evidence))
                continue  # Skip this evidence
            
            # Normalization factor
            factor = 1 / (1 - K)
            
            # Combine beliefs
            new_combined = BeliefMass(
                support=factor * (
                    combined.support * evidence.support +
                    combined.support * evidence.uncertain +
                    combined.uncertain * evidence.support
                ),
                reject=factor * (
                    combined.reject * evidence.reject +
                    combined.reject * evidence.uncertain +
                    combined.uncertain * evidence.reject
                ),
                uncertain=factor * combined.uncertain * evidence.uncertain
            )
            
            combined = new_combined
        
        return combined, conflicts

class WeightedAggregator:
    """Weighted aggregation for user to community"""
    
    def aggregate(
        self, 
        evidences: List[EvidenceItem],
        weights: Dict[str, float]
    ) -> BeliefMass:
        """Weight evidences by influence or other factors"""
        
        weighted_support = 0
        weighted_reject = 0
        weighted_uncertain = 0
        total_weight = 0
        
        for evidence in evidences:
            weight = weights.get(evidence.id, 1.0)
            weighted_support += evidence.belief_masses.support * weight
            weighted_reject += evidence.belief_masses.reject * weight
            weighted_uncertain += evidence.belief_masses.uncertain * weight
            total_weight += weight
        
        if total_weight > 0:
            return BeliefMass(
                support=weighted_support / total_weight,
                reject=weighted_reject / total_weight,
                uncertain=weighted_uncertain / total_weight
            )
        
        return BeliefMass(support=0, reject=0, uncertain=1)
```

## Uncertainty Reduction Through Aggregation

### Key Principle
Multiple consistent evidences reduce uncertainty:

```python
def calculate_uncertainty_reduction(
    input_uncertainties: List[float],
    consistency_score: float
) -> float:
    """Calculate how much aggregation reduces uncertainty"""
    
    avg_input_uncertainty = np.mean(input_uncertainties)
    n_evidences = len(input_uncertainties)
    
    # More evidence → more reduction
    evidence_factor = 1 - np.exp(-n_evidences / 10)
    
    # Higher consistency → more reduction
    consistency_factor = consistency_score
    
    # Reduction formula
    reduction = evidence_factor * consistency_factor * 0.5
    
    # Output uncertainty
    output_uncertainty = avg_input_uncertainty * (1 - reduction)
    
    return {
        "input_avg": avg_input_uncertainty,
        "output": output_uncertainty,
        "reduction": reduction,
        "reduction_percent": reduction * 100
    }
```

### Example: 23 Tweets to 1 User

```python
# Input: 23 tweets with varying uncertainties
tweet_uncertainties = [0.22, 0.25, 0.20, 0.23, ...]  # 23 values
avg_tweet_uncertainty = 0.22

# High consistency (tweets agree)
consistency = 0.85

# Calculate reduction
reduction = calculate_uncertainty_reduction(
    tweet_uncertainties,
    consistency
)

# Result:
# Input average: 0.22
# Output: 0.12
# Reduction: 45%
```

## Implementation Notes

1. **Aggregation tools are infrastructure** - Not generated dynamically
2. **Multiple aggregation methods** - Dempster-Shafer, weighted average, voting
3. **Conflict detection** - Identify and handle conflicting evidence
4. **Uncertainty always reduces** - With consistent evidence
5. **Weights matter** - Influential users count more in community aggregation
6. **Cross-modal is special** - Convergence provides extra validation

## Usage in DAG

Aggregation tools appear at key transition points:
- After extracting multiple tweets → aggregate to user
- After analyzing multiple users → aggregate to community
- After multiple time windows → aggregate to trends
- After multiple modalities → aggregate to synthesis

These are critical for reducing uncertainty and providing population-level insights from instance-level analyses.