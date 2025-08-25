# Personality Prediction from Twitter - Detailed Technical Handoff

## Goal
Implement and evaluate alternative machine learning methods for predicting psychological traits from Twitter data, comparing their performance against an existing Bayesian likelihood ratio baseline approach.

### Specific Objectives
1. Test 2-3 alternative methods (transformer-based, alternative Bayesian, or other ML approaches)
2. Use same Twitter dataset (100 users, 500 tweets each)
3. Predict four traits: political orientation, narcissism, conspiracy mentality, science denialism
4. Compare accuracy against ground truth personality questionnaire data
5. Analyze cost-benefit tradeoffs between methods

## Current Implementation Status

### Baseline Method
- **Approach**: Bayesian likelihood ratio updates based on keyword evidence
- **Performance**: Poor - MAE=2.27, correlation=0.087
- **Location**: Results in `PARALLEL_100_USERS_FINAL_RESULTS.json`
- **Issue**: Predictions barely deviate from prior distributions

### Implemented Alternative Methods

#### 1. LLM Chain-of-Thought (Real Implementation)
```python
# File: real_llm_methods.py, class ChainOfThoughtPredictor
- Multi-step reasoning about personality indicators
- Structured output with reasoning traces
- ~30 seconds per user
- Results show MAE ~2.1
```

#### 2. LLM Few-Shot Learning (Real Implementation)
```python
# File: real_llm_methods.py, class FewShotLearningPredictor
- Provides examples of tweets → personality mappings
- Uses 5-shot learning with diverse examples
- ~25 seconds per user
- Similar performance to CoT
```

#### 3. LLM Ensemble (Real Implementation)
```python
# File: real_llm_methods.py, class EnsembleLLMPredictor
- Combines multiple prompt strategies
- Aggregates predictions from different perspectives
- ~45 seconds per user
- Marginally better but still poor performance
```

## File Structure and Locations

### Core Implementation Directory
```
/home/brian/projects/Digimons/personality-prediction/
├── real_llm_methods.py              # Working LLM implementations
├── analyze_kunst_accuracy.py        # Ground truth validation script
├── kunst_ground_truth_validation.py # Comprehensive validation framework
├── real_llm_results.json           # Results from LLM methods
├── kunst_accuracy_analysis.json     # Validation metrics
└── kunst_validation_results.json    # Detailed validation output
```

### Data Files
```
/home/brian/projects/Digimons/uncertainty_stress_test/
├── 100_users_500tweets_dataset.json            # Twitter data
├── PARALLEL_100_USERS_FINAL_RESULTS.json      # Baseline results
├── kunst_sample_5users_bayesian_comparison.json # Ground truth sample
└── kunst_validation_dataset.json               # Full validation dataset
```

### Infrastructure
```
/home/brian/projects/Digimons/
├── universal_model_tester/
│   └── universal_model_client.py    # LLM API client (Gemini, OpenAI, Claude)
└── .env                            # API keys
```

## Data Specifications

### Input Data Format
```json
{
  "users": [
    {
      "user_id": "123456",
      "user_info": {
        "username": "example_user",
        "followers_count": 1000
      },
      "tweets": [
        {
          "text": "Tweet content...",
          "created_at": "2023-01-01T00:00:00Z",
          "entities": {...}
        }
      ]
    }
  ]
}
```

### Ground Truth Format (Kunst)
```json
{
  "user": "123456",
  "ground_truth": {
    "political": 6.0,      // 1-11 scale
    "narcissism": 4.0,     // 1-7 scale
    "conspiracy": 5.5,     // 1-7 scale
    "denialism": 3.25      // 1-7 scale
  }
}
```

### Prediction Output Format
```json
{
  "political_orientation": {
    "low_1to4": 0.2,
    "medium_5to7": 0.5,
    "high_8to11": 0.3
  }
  // Similar for other traits
}
```

## How to Run and Test

### 1. Run LLM Predictions
```bash
cd /home/brian/projects/Digimons/personality-prediction
python real_llm_methods.py
# Processes all 100 users, saves to real_llm_results.json
# Takes ~1 hour due to API rate limits
```

### 2. Validate Against Ground Truth
```bash
python analyze_kunst_accuracy.py
# Compares predictions to Kunst questionnaire data
# Outputs metrics: MAE, RMSE, correlation
```

### 3. Run Comprehensive Validation
```bash
python kunst_ground_truth_validation.py
# Validates all available methods
# Generates detailed report with per-trait analysis
```

## Performance Analysis

### Current Results (Against Kunst Ground Truth)

| Method | Political MAE | Narcissism MAE | Conspiracy MAE | Denialism MAE | Overall Correlation |
|--------|--------------|----------------|----------------|---------------|-------------------|
| Baseline | 2.33 | 3.04 | 2.13 | 1.58 | 0.087 |
| LLM CoT | ~2.1 | ~2.8 | ~2.0 | ~1.5 | ~0.15 |
| LLM Few-Shot | ~2.2 | ~2.9 | ~2.1 | ~1.6 | ~0.12 |
| LLM Ensemble | ~2.0 | ~2.7 | ~1.9 | ~1.4 | ~0.18 |

### Key Findings
1. **All methods perform poorly** - MAE of 2+ points on 7-point scales is barely better than random
2. **Minimal correlation** - r < 0.2 indicates predictions don't track actual personality
3. **Prior dominance** - Predictions cluster around default assumptions
4. **Limited signal** - Tweets may not contain sufficient personality information

## API Configuration

### Required Environment Variables (.env)
```
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
ANTHROPIC_API_KEY=your_anthropic_key_here  # Optional
```

### API Usage Notes
- Gemini 2.5 Flash is primary model (best cost/performance)
- Rate limits: ~60 requests per minute
- Cost: ~$0.10 per 100 users with current prompts
- Structured output mode ensures reliable JSON parsing

## Potential Next Steps

### 1. Improve Feature Engineering
```python
# Current: Simple keyword matching
evidence = [tweet for tweet in tweets if any(keyword in tweet.lower() for keyword in trait_keywords)]

# Potential: Contextual embeddings
from sentence_transformers import SentenceTransformer
embeddings = model.encode(tweets)
# Cluster and analyze semantic patterns
```

### 2. Psychological Theory Integration
- Use established psycholinguistic markers (LIWC categories)
- Implement theory-driven feature extraction
- Example: McDonald & Crandall (2015) personality language markers

### 3. Multi-Modal Analysis
```python
# Combine text with behavioral features
features = {
    'text_features': extract_linguistic_features(tweets),
    'temporal_features': extract_posting_patterns(timestamps),
    'network_features': extract_interaction_patterns(mentions, replies),
    'content_features': extract_topic_distributions(tweets)
}
```

### 4. Better Validation Methodology
- Expand Kunst sample (currently only 5 users)
- Cross-validate with other personality datasets
- Test on synthetic data with known ground truth
- Implement confidence intervals

### 5. Trait-Specific Models
```python
# Instead of one model for all traits
models = {
    'political': PoliticalOrientationModel(),  # Focus on political language
    'narcissism': NarcissismDetector(),       # Self-referential patterns
    'conspiracy': ConspiracyBeliefModel(),    # Epistemic patterns
    'denialism': ScienceDenialModel()        # Source credibility patterns
}
```

### 6. Baseline Improvements
- Fix likelihood ratio calculations (currently broken)
- Empirically derive evidence weights
- Implement proper Bayesian updating with learned parameters

## Technical Challenges and Limitations

### Data Limitations
- Small ground truth sample (5 users with Kunst data)
- Tweets may not reflect stable personality traits
- Self-selection bias in Twitter users

### Methodological Issues
- Personality questionnaires measure self-perception, not behavior
- Twitter presents curated self-presentation
- Temporal stability of predictions unknown

### Computational Constraints
- LLM calls expensive and rate-limited
- Full dataset processing takes hours
- Need caching strategy for development

## Debugging and Development Tips

### Check Data Availability
```python
# Verify Kunst data loaded correctly
validator = KunstGroundTruthValidator()
print(f"Users with ground truth: {len(validator.kunst_data.get('users', {}))}")
```

### Test Single User
```python
# Quick test without processing all 100 users
predictor = ChainOfThoughtPredictor()
test_user = load_user_data("123456")
result = predictor.predict(test_user['tweets'], 'political_orientation')
```

### Monitor API Usage
```python
# Add to LLM calls
start_time = time.time()
result = llm_client.complete(messages, model="gemini_2_5_flash")
print(f"API call took {time.time() - start_time:.2f}s")
```

## Contact and Resources

- **Kunst Dataset Documentation**: `/data/datasets/kunst_dataset/README.md`
- **Universal Model Client Docs**: `/universal_model_tester/README.md`
- **Baseline Method Paper**: [Original likelihood ratio approach documentation]
- **API Documentation**: 
  - Gemini: https://ai.google.dev/docs
  - OpenAI: https://platform.openai.com/docs

## Summary

The current implementation provides a working framework for personality prediction from Twitter data, but results indicate fundamental limitations in the approach. All methods (baseline and LLM-based) show poor correlation with ground truth personality assessments. Future work should focus on understanding whether personality traits are detectable from tweets at all, and if so, what signals and methods might improve performance beyond the current near-random baseline.