# Simple Twitter Political Attitude Analysis DAG

## Research Question
"Is there a statistical difference in attitudes toward Biden vs Trump between users from different political communities on Twitter?"

## Data
- Single JSON file: `twitter_political_data.json`
- Contains: tweets, user info, community labels (derived from follow patterns)
- ~50,000 tweets mentioning Biden or Trump

## Simple DAG Structure

```
        T06_JSON_LOAD
        Load all Twitter data
        (tweets, users, communities)
                |
                |
        T23C_ONTOLOGY_AWARE_EXTRACTOR
        Extract politicians & sentiment
        (Biden/Trump mentions + attitudes)
                |
                |
        DYNAMIC_DATA_AGGREGATOR_TOOL (Generated)
        Group by user and community
        Aggregate sentiment scores
                |
                |
        DYNAMIC_T_TEST_TOOL (Generated)
        Statistical comparison:
        - Left community: Biden vs Trump
        - Right community: Biden vs Trump
        - Between communities
                |
                |
        RESULTS
        p-values, effect sizes
```

## Tool Implementations with Self-Assessment

### T06_JSON_LOAD
```python
class T06_JSON_LOAD(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        file_path = request.input_data["file_path"]
        
        # Load the single JSON file
        with open(file_path) as f:
            data = json.load(f)
        
        # Check data completeness
        tweets_with_text = len([t for t in data["tweets"] if t.get("text")])
        tweets_with_user = len([t for t in data["tweets"] if t.get("user_id")])
        users_with_community = len([u for u in data["users"] if u.get("community")])
        
        total_tweets = len(data["tweets"])
        total_users = len(data["users"])
        
        text_coverage = tweets_with_text / total_tweets
        user_coverage = tweets_with_user / total_tweets  
        community_coverage = users_with_community / total_users
        
        # Self-assess based on actual data quality
        if text_coverage > 0.95 and user_coverage > 0.90 and community_coverage > 0.80:
            uncertainty = 0.12
            reasoning = f"High quality data: {text_coverage:.0%} tweets have text, {community_coverage:.0%} users have community labels"
        elif text_coverage > 0.80 and community_coverage > 0.60:
            uncertainty = 0.25
            reasoning = f"Moderate data quality: {text_coverage:.0%} text coverage, {community_coverage:.0%} community coverage"
        else:
            uncertainty = 0.40
            reasoning = f"Data quality concerns: only {text_coverage:.0%} text, {community_coverage:.0%} communities"
        
        return ToolResult(
            data=data,
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                data_coverage=min(text_coverage, community_coverage)
            ),
            metadata={
                "tweets": total_tweets,
                "users": total_users,
                "text_coverage": text_coverage,
                "community_coverage": community_coverage
            }
        )
```

### T23C_ONTOLOGY_AWARE_EXTRACTOR
```python
class T23C_ONTOLOGY_AWARE_EXTRACTOR(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        data = request.input_data["data"]
        tweets = data["tweets"]
        users = data["users"]
        
        # Create user lookup
        user_lookup = {u["user_id"]: u for u in users}
        
        # Extract politician mentions and sentiment
        extracted = []
        no_politician = 0
        ambiguous_sentiment = 0
        missing_user = 0
        
        for tweet in tweets:
            text = tweet.get("text", "")
            user_id = tweet.get("user_id")
            
            # Check for politicians
            biden_mentioned = "biden" in text.lower()
            trump_mentioned = "trump" in text.lower()
            
            if not (biden_mentioned or trump_mentioned):
                no_politician += 1
                continue
                
            if user_id not in user_lookup:
                missing_user += 1
                continue
            
            # Extract sentiment toward each politician
            if biden_mentioned:
                biden_sentiment = self.extract_sentiment(text, "biden")
                if biden_sentiment["confidence"] < 0.6:
                    ambiguous_sentiment += 1
                
                extracted.append({
                    "tweet_id": tweet["tweet_id"],
                    "user_id": user_id,
                    "community": user_lookup[user_id].get("community"),
                    "politician": "Biden",
                    "sentiment": biden_sentiment["score"],
                    "confidence": biden_sentiment["confidence"]
                })
            
            if trump_mentioned:
                trump_sentiment = self.extract_sentiment(text, "trump")
                if trump_sentiment["confidence"] < 0.6:
                    ambiguous_sentiment += 1
                    
                extracted.append({
                    "tweet_id": tweet["tweet_id"],
                    "user_id": user_id,
                    "community": user_lookup[user_id].get("community"),
                    "politician": "Trump",
                    "sentiment": trump_sentiment["score"],
                    "confidence": trump_sentiment["confidence"]
                })
        
        # Calculate extraction statistics
        extraction_rate = len(extracted) / (len(tweets) * 1.5)  # Adjust for dual mentions
        ambiguity_rate = ambiguous_sentiment / max(len(extracted), 1)
        
        # Self-assess
        if extraction_rate > 0.60 and ambiguity_rate < 0.20:
            uncertainty = 0.22
            reasoning = f"Extracted {len(extracted)} politician-sentiment pairs. Low ambiguity ({ambiguity_rate:.0%})"
        elif extraction_rate > 0.40:
            uncertainty = 0.35
            reasoning = f"Moderate extraction rate ({extraction_rate:.0%}), {ambiguity_rate:.0%} ambiguous"
        else:
            uncertainty = 0.50
            reasoning = f"Low extraction rate ({extraction_rate:.0%}), high ambiguity or missing data"
        
        return ToolResult(
            data={"extractions": extracted},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning
            ),
            metadata={
                "total_extractions": len(extracted),
                "no_politician": no_politician,
                "ambiguous": ambiguous_sentiment,
                "missing_user": missing_user
            }
        )
    
    def extract_sentiment(self, text: str, politician: str) -> Dict:
        """LLM-based sentiment extraction"""
        # This would call LLM to assess sentiment
        # Returns: {"score": -1 to 1, "confidence": 0 to 1}
        pass
```

### DYNAMIC_DATA_AGGREGATOR_TOOL (Generated)
```python
class DynamicDataAggregatorTool(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        extractions = request.input_data["extractions"]
        
        # Aggregate by user first (multiple tweets per user)
        user_sentiments = {}
        for item in extractions:
            key = (item["user_id"], item["community"], item["politician"])
            if key not in user_sentiments:
                user_sentiments[key] = []
            user_sentiments[key].append(item["sentiment"])
        
        # Average per user, then group by community
        grouped = {
            "left": {"Biden": [], "Trump": []},
            "right": {"Biden": [], "Trump": []}
        }
        
        for (user_id, community, politician), sentiments in user_sentiments.items():
            if community in grouped:
                avg_sentiment = np.mean(sentiments)
                grouped[community][politician].append(avg_sentiment)
        
        # Check sample sizes
        sample_sizes = {
            f"{comm}_{pol}": len(grouped[comm][pol])
            for comm in grouped
            for pol in ["Biden", "Trump"]
        }
        min_sample = min(sample_sizes.values())
        
        # Self-assess based on sample sizes
        if min_sample > 200:
            uncertainty = 0.15
            reasoning = f"Large samples (min n={min_sample}) provide strong statistical power"
        elif min_sample > 100:
            uncertainty = 0.25
            reasoning = f"Adequate samples (min n={min_sample}) for reliable t-tests"
        elif min_sample > 50:
            uncertainty = 0.35
            reasoning = f"Moderate samples (min n={min_sample}), results should be interpreted cautiously"
        else:
            uncertainty = 0.50
            reasoning = f"Small samples (min n={min_sample}) limit statistical reliability"
        
        return ToolResult(
            data={
                "grouped_sentiments": grouped,
                "sample_sizes": sample_sizes
            },
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning
            ),
            metadata={"min_sample_size": min_sample}
        )
```

### DYNAMIC_T_TEST_TOOL (Generated)
```python
class DynamicTTestTool(KGASTool):
    """Generated from simple statistical test specification"""
    
    def execute(self, request: ToolRequest) -> ToolResult:
        grouped = request.input_data["grouped_sentiments"]
        sample_sizes = request.input_data["sample_sizes"]
        
        results = {}
        
        # Within-community comparisons
        for community in ["left", "right"]:
            biden = grouped[community]["Biden"]
            trump = grouped[community]["Trump"]
            
            if len(biden) >= 30 and len(trump) >= 30:
                t_stat, p_value = stats.ttest_ind(biden, trump)
                effect_size = (np.mean(biden) - np.mean(trump)) / np.std(biden + trump)
                
                results[f"{community}_biden_vs_trump"] = {
                    "t": t_stat,
                    "p": p_value,
                    "d": effect_size,
                    "n_biden": len(biden),
                    "n_trump": len(trump),
                    "mean_diff": np.mean(biden) - np.mean(trump)
                }
        
        # Between-community comparisons
        for politician in ["Biden", "Trump"]:
            left = grouped["left"][politician]
            right = grouped["right"][politician]
            
            if len(left) >= 30 and len(right) >= 30:
                t_stat, p_value = stats.ttest_ind(left, right)
                effect_size = (np.mean(left) - np.mean(right)) / np.std(left + right)
                
                results[f"{politician}_left_vs_right"] = {
                    "t": t_stat,
                    "p": p_value,
                    "d": effect_size,
                    "n_left": len(left),
                    "n_right": len(right),
                    "mean_diff": np.mean(left) - np.mean(right)
                }
        
        # Self-assess based on effect sizes and sample sizes
        min_n = min(r.get("n_biden", r.get("n_left", 0)) for r in results.values())
        avg_effect = np.mean([abs(r["d"]) for r in results.values()])
        significant_results = sum(1 for r in results.values() if r["p"] < 0.05)
        
        if min_n > 150 and avg_effect > 0.5:
            uncertainty = 0.18
            reasoning = f"Strong results: large samples (n>{min_n}), clear effects (avg d={avg_effect:.2f})"
        elif min_n > 75:
            uncertainty = 0.28
            reasoning = f"Reliable results: adequate samples (n>{min_n}), {significant_results}/{len(results)} significant"
        else:
            uncertainty = 0.40
            reasoning = f"Limited confidence: smaller samples (n={min_n}), interpret with caution"
        
        return ToolResult(
            data={"statistical_tests": results},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning
            ),
            metadata={
                "tests_performed": len(results),
                "significant_results": significant_results
            }
        )
```

## Key Points

1. **Single input file** - Everything in one JSON
2. **T23C for extraction** - No T23A/SPACY references
3. **Tools self-assess** - Uncertainty is part of execution, not separate
4. **Uncertainty is about THIS execution**:
   - Data completeness in the file
   - Extraction success rate
   - Sentiment ambiguity
   - Sample sizes for statistics

5. **NOT about**:
   - Consistency across runs
   - Inter-LLM agreement
   - Any validation metrics

The pattern is consistent: each tool assesses its own uncertainty based on what it actually did in this execution.