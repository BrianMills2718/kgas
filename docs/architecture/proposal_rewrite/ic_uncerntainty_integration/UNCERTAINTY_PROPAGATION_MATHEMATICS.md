# Mathematical Framework for Uncertainty Propagation in KGAS

## 📋 **Executive Summary**

This document establishes the mathematical foundation for uncertainty propagation in KGAS's multi-modal, multi-level architecture. It addresses the critical challenge of maintaining calibrated confidence scores as information flows through theory extraction, cross-modal transformations, and autonomous agent decision-making.

**Document Date**: 2025-08-06  
**Author**: Claude (Opus 4.1)  
**Purpose**: Define rigorous mathematical framework for uncertainty quantification  

## 🔬 **Fundamental Uncertainty Types**

### **Aleatoric Uncertainty (Irreducible)**
- **Definition**: Inherent randomness in the system
- **Sources**: Natural language ambiguity, theory vagueness, measurement noise
- **Mathematical Representation**: σ²_aleatoric
- **Cannot be reduced** by gathering more data

### **Epistemic Uncertainty (Reducible)**
- **Definition**: Uncertainty from lack of knowledge
- **Sources**: Limited training data, model limitations, incomplete theory extraction
- **Mathematical Representation**: σ²_epistemic  
- **Can be reduced** by improving models or gathering more information

### **Total Uncertainty**
```
σ²_total = σ²_aleatoric + σ²_epistemic
```

## 📐 **Core Mathematical Framework**

### **1. Probability Distribution Representation**

Instead of single confidence values, maintain probability distributions:

```python
class UncertaintyDistribution:
    """
    Represent uncertainty as probability distribution
    
    Benefits:
    - Captures full uncertainty information
    - Enables proper propagation
    - Supports decision theory
    """
    
    mean: float          # Expected value
    variance: float      # Uncertainty spread
    distribution_type: str  # 'normal', 'beta', 'dirichlet'
    parameters: Dict     # Distribution-specific parameters
```

### **2. Beta Distribution for Bounded Confidence**

For confidence scores bounded [0,1], use Beta distribution:

```
Beta(α, β)

mean = α / (α + β)
variance = αβ / ((α + β)² (α + β + 1))

α = success_count + 1  # Pseudo-counts
β = failure_count + 1
```

**Advantages**:
- Natural for probabilities
- Conjugate prior for Bernoulli
- Intuitive parameter interpretation

### **3. Uncertainty Propagation Rules**

#### **Linear Propagation (Addition)**
When combining independent uncertainties:

```
If X ~ N(μ_x, σ²_x) and Y ~ N(μ_y, σ²_y)
Then Z = X + Y ~ N(μ_x + μ_y, σ²_x + σ²_y)
```

#### **Non-Linear Propagation (General)**
Using Taylor expansion (Delta method):

```
If Y = g(X) and X ~ N(μ, σ²)
Then Y ≈ N(g(μ), |g'(μ)|² σ²)
```

#### **Product Propagation (Multiplication)**
For confidence multiplication:

```
If C₁ ~ Beta(α₁, β₁) and C₂ ~ Beta(α₂, β₂)
Then C₁ × C₂ ≈ Beta(α_prod, β_prod)

Where:
α_prod = α₁α₂ / (α₁ + β₁)
β_prod = α₁β₂ + α₂β₁ + β₁β₂ / (α₁ + β₁)
```

## 🔄 **Multi-Level Propagation Architecture**

### **Level 1: Tool-Level Uncertainty**

```python
def propagate_tool_uncertainty(
    input_uncertainty: UncertaintyDistribution,
    tool_accuracy: float,
    tool_variance: float
) -> UncertaintyDistribution:
    """
    Propagate uncertainty through a single tool
    
    U_out² = U_in² + U_tool² + 2ρ·U_in·U_tool
    
    Where ρ is correlation coefficient
    """
    
    # Assume independence for simplicity (ρ = 0)
    output_variance = input_uncertainty.variance + tool_variance
    
    # Adjust mean based on tool accuracy
    output_mean = input_uncertainty.mean * tool_accuracy
    
    return UncertaintyDistribution(
        mean=output_mean,
        variance=output_variance,
        distribution_type='normal'
    )
```

### **Level 2: Cross-Modal Transformation**

```python
def propagate_cross_modal(
    source_dist: UncertaintyDistribution,
    transformation_type: Tuple[str, str]
) -> UncertaintyDistribution:
    """
    Propagate uncertainty across modal boundaries
    
    Special handling for information loss
    """
    
    # Transformation-specific uncertainty
    TRANSFORMATION_UNCERTAINTY = {
        ('graph', 'table'): {
            'mean_degradation': 0.95,    # 5% average confidence loss
            'variance_inflation': 1.15    # 15% uncertainty increase
        },
        ('table', 'vector'): {
            'mean_degradation': 0.90,    # 10% average confidence loss
            'variance_inflation': 1.25    # 25% uncertainty increase
        },
        ('graph', 'vector'): {
            'mean_degradation': 0.85,    # 15% average confidence loss
            'variance_inflation': 1.30    # 30% uncertainty increase
        }
    }
    
    transform = TRANSFORMATION_UNCERTAINTY[transformation_type]
    
    # Apply transformation effects
    output_mean = source_dist.mean * transform['mean_degradation']
    output_variance = source_dist.variance * transform['variance_inflation']
    
    # Add transformation-specific noise
    transformation_noise = 0.01  # Base transformation uncertainty
    output_variance += transformation_noise
    
    return UncertaintyDistribution(
        mean=output_mean,
        variance=output_variance,
        distribution_type=source_dist.distribution_type
    )
```

### **Level 3: Theory-Driven Aggregation**

```python
def aggregate_theory_uncertainty(
    extraction_uncertainty: UncertaintyDistribution,
    application_uncertainty: UncertaintyDistribution,
    context_match: float  # How well theory matches context [0,1]
) -> UncertaintyDistribution:
    """
    Combine theory extraction and application uncertainties
    
    Uses Bayesian approach with context as prior weight
    """
    
    # Weight extraction by how well theory matches
    weighted_extraction_var = extraction_uncertainty.variance / context_match
    
    # Combine using precision weighting (inverse variance)
    precision_extraction = 1 / weighted_extraction_var
    precision_application = 1 / application_uncertainty.variance
    
    # Combined precision and mean
    combined_precision = precision_extraction + precision_application
    combined_mean = (
        extraction_uncertainty.mean * precision_extraction +
        application_uncertainty.mean * precision_application
    ) / combined_precision
    
    combined_variance = 1 / combined_precision
    
    return UncertaintyDistribution(
        mean=combined_mean,
        variance=combined_variance,
        distribution_type='normal'
    )
```

## 🎯 **Cascade and Threshold Handling**

### **Uncertainty Explosion Detection**

```python
def detect_uncertainty_explosion(
    uncertainty_trajectory: List[float],
    window_size: int = 5
) -> bool:
    """
    Detect if uncertainty is growing uncontrollably
    
    Uses exponential growth detection
    """
    
    if len(uncertainty_trajectory) < window_size:
        return False
        
    recent = uncertainty_trajectory[-window_size:]
    
    # Fit exponential: U(t) = U₀ * e^(rt)
    log_uncertainties = np.log(recent)
    times = np.arange(window_size)
    
    # Linear regression on log scale
    slope, intercept = np.polyfit(times, log_uncertainties, 1)
    
    # Growth rate r = slope
    growth_rate = slope
    
    # Explosion if doubling time < threshold
    if growth_rate > 0:
        doubling_time = np.log(2) / growth_rate
        return doubling_time < 3  # Explodes if doubles in <3 steps
    
    return False
```

### **Threshold-Based Decision Making**

```python
class UncertaintyThresholds:
    """
    Decision thresholds based on uncertainty levels
    """
    
    # IC-aligned thresholds
    HIGH_CONFIDENCE = 0.93      # "Almost certain"
    MODERATE_CONFIDENCE = 0.70  # "Likely"  
    LOW_CONFIDENCE = 0.40       # "Roughly even chance"
    UNRELIABLE = 0.20          # "Unlikely" - need more evidence
    
    @staticmethod
    def make_decision(
        confidence: float,
        decision_criticality: str = 'medium'
    ) -> DecisionAction:
        """
        Map confidence to action based on criticality
        """
        
        CRITICALITY_ADJUSTMENTS = {
            'low': 0.0,      # No adjustment
            'medium': 0.1,   # Require 10% more confidence
            'high': 0.2,     # Require 20% more confidence
            'critical': 0.3  # Require 30% more confidence
        }
        
        adjusted_threshold = (
            UncertaintyThresholds.MODERATE_CONFIDENCE + 
            CRITICALITY_ADJUSTMENTS[decision_criticality]
        )
        
        if confidence >= adjusted_threshold:
            return DecisionAction.PROCEED
        elif confidence >= UncertaintyThresholds.LOW_CONFIDENCE:
            return DecisionAction.GATHER_MORE_EVIDENCE
        else:
            return DecisionAction.ABORT_OR_FALLBACK
```

## 📊 **Information-Theoretic Uncertainty**

### **Entropy-Based Uncertainty**

For categorical distributions (e.g., theory type selection):

```python
def calculate_entropy_uncertainty(
    probabilities: np.ndarray
) -> float:
    """
    Shannon entropy as uncertainty measure
    
    H(X) = -Σ p(x) log p(x)
    
    Maximum uncertainty when uniform distribution
    """
    
    # Avoid log(0)
    probabilities = np.clip(probabilities, 1e-10, 1.0)
    
    entropy = -np.sum(probabilities * np.log2(probabilities))
    
    # Normalize by maximum entropy
    max_entropy = np.log2(len(probabilities))
    normalized_uncertainty = entropy / max_entropy if max_entropy > 0 else 0
    
    return normalized_uncertainty
```

### **Mutual Information for Dependency**

When uncertainties are correlated:

```python
def calculate_mutual_information(
    X: np.ndarray,
    Y: np.ndarray
) -> float:
    """
    Mutual information I(X;Y) measures dependency
    
    I(X;Y) = H(X) + H(Y) - H(X,Y)
    
    Used to detect correlated uncertainties
    """
    
    # Estimate joint and marginal distributions
    hist_2d, x_edges, y_edges = np.histogram2d(X, Y, bins=20)
    
    # Convert to probabilities
    joint_prob = hist_2d / hist_2d.sum()
    marginal_x = joint_prob.sum(axis=1)
    marginal_y = joint_prob.sum(axis=0)
    
    # Calculate entropies
    H_X = calculate_entropy_uncertainty(marginal_x)
    H_Y = calculate_entropy_uncertainty(marginal_y)
    H_XY = calculate_entropy_uncertainty(joint_prob.flatten())
    
    mutual_info = H_X + H_Y - H_XY
    
    # Normalize by minimum entropy
    normalized_mi = mutual_info / min(H_X, H_Y) if min(H_X, H_Y) > 0 else 0
    
    return normalized_mi
```

## 🔧 **Practical Implementation Patterns**

### **Efficient Approximations**

```python
class EfficientUncertaintyPropagation:
    """
    Practical approximations for production use
    """
    
    @staticmethod
    def gaussian_approximation(
        dist: UncertaintyDistribution
    ) -> Tuple[float, float]:
        """
        Approximate any distribution as Gaussian
        Fast but less accurate
        """
        return dist.mean, dist.variance
    
    @staticmethod
    def monte_carlo_propagation(
        input_dist: UncertaintyDistribution,
        transformation: Callable,
        n_samples: int = 1000
    ) -> UncertaintyDistribution:
        """
        Monte Carlo propagation for complex transformations
        Accurate but computationally expensive
        """
        
        # Sample from input distribution
        samples = input_dist.sample(n_samples)
        
        # Apply transformation
        transformed = [transformation(s) for s in samples]
        
        # Estimate output distribution
        output_mean = np.mean(transformed)
        output_var = np.var(transformed)
        
        return UncertaintyDistribution(
            mean=output_mean,
            variance=output_var,
            distribution_type='empirical'
        )
    
    @staticmethod
    def cached_propagation(
        transformation_key: str,
        input_uncertainty: float
    ) -> float:
        """
        Use pre-computed propagation tables
        Very fast, limited flexibility
        """
        
        PROPAGATION_CACHE = {
            # Pre-computed for common transformations
            'graph_to_table': {
                0.9: 0.85,  # 90% confidence → 85% after transformation
                0.8: 0.74,
                0.7: 0.63,
                0.6: 0.52,
                0.5: 0.41
            }
        }
        
        # Interpolate if exact value not in cache
        cache = PROPAGATION_CACHE[transformation_key]
        return np.interp(input_uncertainty, 
                        list(cache.keys()), 
                        list(cache.values()))
```

### **Calibration and Validation**

```python
class UncertaintyCalibration:
    """
    Ensure predicted uncertainties match observed frequencies
    """
    
    @staticmethod
    def calculate_calibration_error(
        predicted_confidences: np.ndarray,
        actual_outcomes: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Expected Calibration Error (ECE)
        
        ECE = Σ |confidence - accuracy| * bin_weight
        """
        
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        
        for i in range(n_bins):
            # Get predictions in this confidence bin
            in_bin = (predicted_confidences >= bin_boundaries[i]) & \
                    (predicted_confidences < bin_boundaries[i + 1])
            
            if in_bin.sum() == 0:
                continue
                
            # Calculate accuracy in bin
            bin_accuracy = actual_outcomes[in_bin].mean()
            
            # Average confidence in bin
            bin_confidence = predicted_confidences[in_bin].mean()
            
            # Weight by number of samples
            bin_weight = in_bin.sum() / len(predicted_confidences)
            
            # Add to ECE
            ece += np.abs(bin_confidence - bin_accuracy) * bin_weight
            
        return ece
    
    @staticmethod
    def calibrate_uncertainty(
        raw_confidence: float,
        calibration_model: Callable
    ) -> float:
        """
        Apply learned calibration function
        
        Common approaches:
        - Platt scaling (logistic)
        - Isotonic regression
        - Beta calibration
        """
        
        return calibration_model(raw_confidence)
```

## 🎨 **Visualization and Debugging**

### **Uncertainty Flow Diagram**

```python
def visualize_uncertainty_flow(
    propagation_chain: List[UncertaintyNode]
) -> None:
    """
    Visualize how uncertainty propagates through system
    """
    
    import matplotlib.pyplot as plt
    
    positions = []
    uncertainties = []
    labels = []
    
    for i, node in enumerate(propagation_chain):
        positions.append(i)
        uncertainties.append(node.uncertainty.mean)
        labels.append(node.name)
    
    # Plot with confidence bands
    means = [u.mean for u in uncertainties]
    stds = [np.sqrt(u.variance) for u in uncertainties]
    
    plt.figure(figsize=(12, 6))
    plt.plot(positions, means, 'b-', label='Mean confidence')
    plt.fill_between(positions,
                     [m - s for m, s in zip(means, stds)],
                     [m + s for m, s in zip(means, stds)],
                     alpha=0.3, label='±1 std')
    
    # Mark thresholds
    plt.axhline(y=0.93, color='g', linestyle='--', label='High confidence')
    plt.axhline(y=0.40, color='r', linestyle='--', label='Low confidence')
    
    plt.xticks(positions, labels, rotation=45)
    plt.ylabel('Confidence')
    plt.xlabel('Processing Stage')
    plt.title('Uncertainty Propagation Through Pipeline')
    plt.legend()
    plt.tight_layout()
    plt.show()
```

## 🔍 **Common Pitfalls and Solutions**

### **Pitfall 1: Independence Assumption**
**Problem**: Assuming uncertainties are independent when they're correlated  
**Solution**: Use copulas or empirical correlation estimates

### **Pitfall 2: Gaussian Assumption**
**Problem**: Assuming normal distributions for bounded quantities  
**Solution**: Use Beta distributions for probabilities, truncated normals for bounded values

### **Pitfall 3: Ignoring Model Uncertainty**
**Problem**: Only tracking data uncertainty, not model uncertainty  
**Solution**: Use ensemble methods or Bayesian approaches

### **Pitfall 4: Cascade Failures**
**Problem**: Small uncertainties compound to create failures  
**Solution**: Monitor cumulative uncertainty and set circuit breakers

### **Pitfall 5: Over-confidence**
**Problem**: Systematic under-estimation of uncertainty  
**Solution**: Regular calibration against ground truth

## 📈 **Performance Considerations**

### **Computational Complexity**

| Method | Complexity | Accuracy | Use Case |
|--------|-----------|----------|----------|
| Point estimate | O(1) | Low | Quick estimates |
| Gaussian propagation | O(n) | Medium | Most propagation |
| Monte Carlo | O(n×m) | High | Complex transformations |
| Full Bayesian | O(n³) | Highest | Critical decisions |

### **Optimization Strategies**

1. **Lazy Evaluation**: Only compute uncertainty when needed
2. **Caching**: Pre-compute common propagation patterns
3. **Approximation**: Use simpler distributions when accuracy permits
4. **Pruning**: Skip negligible uncertainty contributions
5. **Batching**: Process multiple uncertainties together

## 🎯 **Integration with IC Standards**

### **Mapping to ICD-203**

```python
def map_to_icd203(
    uncertainty: UncertaintyDistribution
) -> Tuple[str, str]:
    """
    Map uncertainty to IC probability and confidence levels
    """
    
    # Probability words
    probability = map_to_ic_probability(uncertainty.mean)
    
    # Confidence in assessment
    if uncertainty.variance < 0.01:
        confidence = "High confidence"
    elif uncertainty.variance < 0.04:
        confidence = "Moderate confidence"
    else:
        confidence = "Low confidence"
        
    return probability, confidence
```

## 📚 **Mathematical Foundations Summary**

This framework provides:

1. **Rigorous propagation rules** for multi-level uncertainty
2. **Practical approximations** for production use
3. **Calibration methods** to ensure accuracy
4. **Threshold handling** for decision support
5. **IC standards compliance** for reporting

The mathematics balance theoretical correctness with computational efficiency, enabling KGAS to maintain calibrated uncertainty estimates throughout its autonomous research workflows.

---

**Document Status**: Mathematical Framework Complete  
**Next Step**: Implementation patterns and code templates  
**Validation**: Requires empirical testing with real data