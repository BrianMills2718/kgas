# Personality Prediction Method Comparison

This framework compares three different approaches to psychological trait prediction on Twitter data:

## 🎯 Objective

Test and compare alternative personality prediction methods against your existing likelihood ratio approach to identify strengths, weaknesses, and potential improvements.

## 🧠 Methods Compared

### 1. **Likelihood Ratio Method (Your Baseline)**
- **Approach**: Bayesian likelihood ratio updates with LLM probability distributions
- **Input**: Twitter text chunks per user
- **Output**: Probability distributions over trait scales
- **Strengths**: Uncertainty quantification, interpretable probabilities
- **Data**: Uses your existing PARALLEL_100_USERS_FINAL_RESULTS.json

### 2. **BERT Deep Learning Method**
- **Repository**: Adapted from [rcantini/BERT_personality_detection](https://github.com/rcantini/BERT_personality_detection)
- **Approach**: Fine-tuned BERT transformer for personality classification
- **Input**: Raw Twitter text
- **Output**: Learned feature representations → trait predictions
- **Strengths**: Captures complex linguistic patterns, state-of-the-art NLP

### 3. **Beta-Bayesian Updating Method**
- **Repository**: Adapted from [ajosanchez/applied-bayesian-updating](https://github.com/ajosanchez/applied-bayesian-updating)
- **Approach**: Sequential Beta-Binomial conjugate updating
- **Input**: Binary evidence extracted from tweets
- **Output**: Beta distribution parameters for each trait
- **Strengths**: Fast computation, principled uncertainty, interpretable

## 📊 Traits Analyzed

All methods predict the same 4 psychological traits:
- **Political Orientation** (1-11 scale)
- **Conspiracy Mentality** (1-11 scale)  
- **Science Denialism** (1-11 scale)
- **Narcissism** (1-11 scale)

## 🚀 Quick Start

```bash
# Ensure you have the baseline results file
ls uncertainty_stress_test/PARALLEL_100_USERS_FINAL_RESULTS.json

# Run the comparison
cd personality-prediction
python run_comparison.py
```

## 📁 File Structure

```
personality-prediction/
├── README.md                           # This file
├── run_comparison.py                   # Main execution script
├── method_comparison_framework.py      # Core comparison framework
├── bert_personality_predictor.py       # BERT-based method
├── beta_bayesian_predictor.py         # Beta-Bayesian method
└── comparison_results.json            # Output results
```

## 📈 Output Format

The comparison generates:

### Performance Metrics
- Processing time per method
- Confidence score distributions
- Memory usage (if available)

### Prediction Consistency
- Agreement between methods per trait
- Correlation analysis
- Variance in predictions

### Methodology Analysis
- Approach differences
- Computational complexity
- Strengths/weaknesses assessment

## 🔧 Implementation Details

### Data Processing
- **Baseline**: Uses existing chunk-based LLM predictions
- **BERT**: Aggregates user tweets into single text input
- **Beta-Bayesian**: Converts tweets to binary evidence (keyword-based)

### Evaluation Approach
- Same 100 users tested across all methods
- Synthetic tweet generation based on baseline predictions
- Fair comparison on identical data

### Output Harmonization
All methods output predictions in your standard format:
```json
{
  "trait_name": {
    "low_1to4": 0.2,
    "medium_5to7": 0.7, 
    "high_8to11": 0.1
  }
}
```

## 📊 Expected Insights

### Methodological Differences
- **Likelihood Ratio**: Complex probability reasoning, expensive computation
- **BERT**: Pattern recognition, requires training data, black box
- **Beta-Bayesian**: Simple statistics, fast, interpretable but limited

### Performance Trade-offs
- **Accuracy vs Speed**: Compare prediction quality vs processing time
- **Interpretability vs Sophistication**: Simple vs complex approaches
- **Data Requirements**: Training needs vs zero-shot capabilities

## 🎯 Validation Approach

Since this is method comparison (not accuracy validation):
1. **Consistency Check**: Do methods agree on same users?
2. **Face Validity**: Do predictions make intuitive sense?
3. **Computational Efficiency**: Time and resource usage
4. **Robustness**: Performance across different user types

## 🔄 Next Steps

Based on comparison results:
1. **High Agreement** → Methods capture similar signals, choose fastest
2. **Moderate Agreement** → Methods complement each other, consider ensemble  
3. **Low Agreement** → Investigate differences, identify best approach

## 🛠️ Extensions

### Add New Methods
To add another prediction method:
1. Create new predictor class with `predict_user_personality()` method
2. Add to `MethodComparisonFramework.run_comparison_on_users()`
3. Update output format conversion

### Scale to Full Dataset
- Modify `max_users` parameter in `run_comparison.py`
- Consider parallel processing for large-scale comparison
- Add memory management for big datasets

## 📋 Requirements

- Python 3.8+
- transformers (for BERT)
- tensorflow (for BERT)
- scipy (for Beta distributions)
- numpy, pandas, matplotlib
- Your existing uncertainty_stress_test environment

## 🤝 Contributing

This framework is designed for your specific use case but can be adapted for:
- Different personality models (Big Five, MBTI, etc.)
- Other social media platforms
- Additional prediction methods
- Different evaluation metrics

## 📄 License

Follows the licenses of the original repositories:
- BERT method: Based on MIT licensed repository
- Beta-Bayesian: Based on original research implementation