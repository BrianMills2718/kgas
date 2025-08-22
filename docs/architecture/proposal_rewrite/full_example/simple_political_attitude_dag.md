# Simple DAG: Political Attitude Analysis by Community

## Research Question
"Is there a statistical difference in attitudes toward Biden vs Trump based on online community membership?"

## Data
- Reddit posts from r/politics and r/conservative 
- 10,000 posts mentioning Biden or Trump
- User community membership based on posting history

## DAG Structure

```
                    DATA LOADING
                         |
        +----------------+----------------+
        |                                 |
  T06_JSON_LOAD                    T05_CSV_LOAD
  Reddit posts                     User metadata
  (post_id, text,                  (user_id, 
   author, subreddit)              community_label)
        |                                 |
        +----------------+----------------+
                         |
                  T302_MULTI_DOC_FUSION
                  Join posts with users
                  Output: unified dataset
                         |
                         |
                  ENTITY EXTRACTION
                         |
                T23C_ONTOLOGY_AWARE_EXTRACTOR
                Extract politician mentions
                Tag sentiment toward each
                         |
                         |
                   DATA PREPARATION
                         |
                  DYNAMIC_DATA_PREP_TOOL (Generated)
                  Structure for analysis:
                  - Group by community
                  - Aggregate sentiments
                  - Create comparison matrix
                         |
                         |
                 STATISTICAL ANALYSIS
                         |
                  DYNAMIC_T_TEST_TOOL (Generated)
                  Compare attitudes:
                  - r/politics → Biden vs Trump
                  - r/conservative → Biden vs Trump
                  - Between communities
                         |
                         |
                  FINAL RESULTS
                  Statistical significance
                  Effect sizes
                  Confidence intervals
```

## Tool Execution with Uncertainty

### T06_JSON_LOAD
```python
class T06_JSON_LOAD(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        # Load Reddit posts
        posts = load_json(request.input_data["file_path"])
        
        # Check data quality
        valid_posts = [p for p in posts if p.get("text") and p.get("author")]
        coverage = len(valid_posts) / len(posts)
        
        # Self-assess uncertainty
        uncertainty = UniversalUncertainty(
            uncertainty=0.12 if coverage > 0.95 else 0.25,
            reasoning=f"Loaded {len(valid_posts)} valid posts out of {len(posts)}. Coverage: {coverage:.1%}"
        )
        
        return ToolResult(
            data={"posts": valid_posts},
            uncertainty=uncertainty,
            metadata={"total": len(posts), "valid": len(valid_posts)}
        )
```

### T05_CSV_LOAD  
```python
class T05_CSV_LOAD(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        # Load user metadata
        users_df = pd.read_csv(request.input_data["file_path"])
        
        # Check completeness
        complete_users = users_df.dropna(subset=["user_id", "community_label"])
        coverage = len(complete_users) / len(users_df)
        
        # Self-assess uncertainty
        uncertainty = UniversalUncertainty(
            uncertainty=0.10 if coverage > 0.90 else 0.30,
            reasoning=f"User metadata {coverage:.0%} complete. Missing community labels for {len(users_df) - len(complete_users)} users."
        )
        
        return ToolResult(
            data={"users": complete_users.to_dict()},
            uncertainty=uncertainty,
            metadata={"coverage": coverage}
        )
```

### T302_MULTI_DOC_FUSION
```python
class T302_MULTI_DOC_FUSION(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        posts = request.input_data["posts"]
        users = request.input_data["users"]
        
        # Join posts with user metadata
        joined = []
        unmatched = 0
        
        for post in posts:
            author = post["author"]
            if author in users:
                post["community"] = users[author]["community_label"]
                joined.append(post)
            else:
                unmatched += 1
        
        join_rate = len(joined) / len(posts)
        
        # Self-assess uncertainty
        uncertainty = UniversalUncertainty(
            uncertainty=0.20 if join_rate > 0.80 else 0.35,
            reasoning=f"Successfully joined {len(joined)} posts ({join_rate:.0%}). {unmatched} posts from users without community labels.",
            data_coverage=join_rate
        )
        
        return ToolResult(
            data={"unified_dataset": joined},
            uncertainty=uncertainty,
            metadata={"joined": len(joined), "unmatched": unmatched}
        )
```

### T23C_ONTOLOGY_AWARE_EXTRACTOR
```python
class T23C_ONTOLOGY_AWARE_EXTRACTOR(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        posts = request.input_data["unified_dataset"]
        
        # Extract entities and sentiment
        extracted = []
        ambiguous = 0
        
        for post in posts:
            entities = extract_politicians(post["text"])
            sentiment = analyze_sentiment(post["text"], entities)
            
            if sentiment["confidence"] < 0.7:
                ambiguous += 1
            
            extracted.append({
                "post_id": post["post_id"],
                "community": post["community"],
                "politician": entities,
                "sentiment": sentiment["score"],
                "confidence": sentiment["confidence"]
            })
        
        ambiguity_rate = ambiguous / len(posts)
        
        # Self-assess uncertainty
        uncertainty = UniversalUncertainty(
            uncertainty=0.25 if ambiguity_rate < 0.20 else 0.40,
            reasoning=f"Extracted sentiment for {len(posts)} posts. {ambiguous} ({ambiguity_rate:.0%}) had ambiguous sentiment."
        )
        
        return ToolResult(
            data={"sentiment_data": extracted},
            uncertainty=uncertainty,
            metadata={"ambiguous_count": ambiguous}
        )
```

### DYNAMIC_DATA_PREP_TOOL (Generated)
```python
class DynamicDataPrepTool(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        sentiment_data = request.input_data["sentiment_data"]
        
        # Structure for statistical analysis
        grouped = {
            "r_politics": {"Biden": [], "Trump": []},
            "r_conservative": {"Biden": [], "Trump": []}
        }
        
        missing_data = 0
        for item in sentiment_data:
            community = item["community"]
            politician = item["politician"]
            sentiment = item["sentiment"]
            
            if community and politician:
                grouped[community][politician].append(sentiment)
            else:
                missing_data += 1
        
        # Check sample sizes
        min_sample = min(
            len(grouped["r_politics"]["Biden"]),
            len(grouped["r_politics"]["Trump"]),
            len(grouped["r_conservative"]["Biden"]),
            len(grouped["r_conservative"]["Trump"])
        )
        
        # Self-assess uncertainty
        if min_sample > 100:
            uncertainty = UniversalUncertainty(
                uncertainty=0.15,
                reasoning=f"All groups have n>{min_sample}, adequate for t-tests"
            )
        else:
            uncertainty = UniversalUncertainty(
                uncertainty=0.35,
                reasoning=f"Smallest group has n={min_sample}, may affect statistical power"
            )
        
        return ToolResult(
            data={"grouped_data": grouped},
            uncertainty=uncertainty,
            metadata={"min_sample_size": min_sample}
        )
```

### DYNAMIC_T_TEST_TOOL (Generated)
```python
class DynamicTTestTool(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        grouped = request.input_data["grouped_data"]
        
        results = {}
        
        # Within community comparisons
        for community in ["r_politics", "r_conservative"]:
            biden_scores = grouped[community]["Biden"]
            trump_scores = grouped[community]["Trump"]
            
            if len(biden_scores) > 30 and len(trump_scores) > 30:
                t_stat, p_value = stats.ttest_ind(biden_scores, trump_scores)
                effect_size = (np.mean(biden_scores) - np.mean(trump_scores)) / np.std(biden_scores + trump_scores)
                
                results[f"{community}_comparison"] = {
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "effect_size": effect_size,
                    "n_biden": len(biden_scores),
                    "n_trump": len(trump_scores)
                }
        
        # Assess based on sample sizes and effect sizes
        min_n = min(results[k]["n_biden"] for k in results)
        avg_effect = np.mean([abs(r["effect_size"]) for r in results.values()])
        
        if min_n > 100 and avg_effect > 0.5:
            uncertainty = UniversalUncertainty(
                uncertainty=0.20,
                reasoning=f"Large samples (n>{min_n}) and clear effects (d={avg_effect:.2f})"
            )
        elif min_n > 50:
            uncertainty = UniversalUncertainty(
                uncertainty=0.30,
                reasoning=f"Moderate samples (n={min_n}) provide reasonable confidence"
            )
        else:
            uncertainty = UniversalUncertainty(
                uncertainty=0.45,
                reasoning=f"Small samples (n={min_n}) limit statistical confidence"
            )
        
        return ToolResult(
            data={"statistical_results": results},
            uncertainty=uncertainty,
            metadata={"tests_performed": len(results)}
        )
```

## Key Points About This Example

1. **No theory extraction** - Starts with raw data
2. **Uncertainty is about THIS execution**:
   - Data completeness
   - Join success rates  
   - Sentiment extraction confidence
   - Sample sizes for statistics
   
3. **NOT about**:
   - Whether results replicate
   - Whether other LLMs agree
   - Validation metrics
   
4. **Each tool self-assesses** based on its actual execution:
   - Coverage rates
   - Ambiguity levels
   - Sample sizes
   - Effect sizes

5. **Natural uncertainty flow**:
   - Low for clean data loads (0.10-0.12)
   - Higher for ambiguous sentiment (0.25-0.40)
   - Depends on sample sizes for statistics (0.20-0.45)

This is much simpler and focused on the actual data quality and analysis, not meta-validation.