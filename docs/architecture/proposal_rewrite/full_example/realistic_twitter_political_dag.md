# Twitter Political Attitude Analysis DAG - Using Real KGAS Tools Only

This example demonstrates political attitude analysis using only existing KGAS tools (no dynamic generation). Communities are DETECTED from the follow graph network structure, NOT given as input labels.

## Research Question
"Is there a statistical difference in attitudes toward Biden vs Trump between users in different Twitter network communities?"

## Input Data
Single JSON file containing ONLY:
- Tweets with text, user_id, timestamp  
- Follow relationships (who follows whom)
- NO community labels (these must be detected from network structure)

## Processing DAG

```
                T06_JSON_LOAD
                Load Twitter data JSON
                 (Tweets + Follows only)
                       |
        +--------------+--------------+
        |                             |
        v                             v
   T31_ENTITY_BUILDER           T34_EDGE_BUILDER
   Create User nodes            Build follow graph
   from tweet authors           from relationships
        |                             |
        +--------------+--------------+
                       |
                       v
              T50_COMMUNITY_DETECTION
              Detect communities from
              follow graph using Louvain
                       |
                       v
         T23C_ONTOLOGY_AWARE_EXTRACTOR
         Extract politician mentions and
         sentiment from tweet texts
                       |
                       v
              T56_GRAPH_METRICS
              Calculate metrics per community:
              - Mean sentiment scores
              - Sentiment variance
              - Coverage statistics
                       |
                       v
             T58_GRAPH_COMPARISON
             Statistical comparison between
             communities' sentiment patterns
                       |
                       v
              T60_GRAPH_EXPORT
              Export results as structured
              data for further analysis
```

## Tool Implementations with Self-Assessment

### T06_JSON_LOAD (Real KGAS Tool)
```python
class T06_JSON_LOAD(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        file_path = request.input_data["file_path"]
        
        with open(file_path) as f:
            data = json.load(f)
        
        tweets = data.get("tweets", [])
        follows = data.get("follows", [])  # {follower: id, followed: id}
        
        # Assess data completeness
        tweets_with_text = sum(1 for t in tweets if t.get("text"))
        tweets_with_user = sum(1 for t in tweets if t.get("user_id"))
        
        # Check follow graph coverage
        tweet_users = set(t["user_id"] for t in tweets if t.get("user_id"))
        graph_users = set()
        for edge in follows:
            graph_users.add(edge["follower"])
            graph_users.add(edge["followed"])
        
        coverage = len(tweet_users & graph_users) / len(tweet_users) if tweet_users else 0
        
        # Self-assess uncertainty
        if len(tweets) > 10000 and len(follows) > 50000 and coverage > 0.7:
            uncertainty = 0.15
            reasoning = f"Rich data: {len(tweets)} tweets, {len(follows)} edges, {coverage:.0%} coverage"
        elif len(tweets) > 5000 and coverage > 0.5:
            uncertainty = 0.3
            reasoning = f"Moderate data: {len(tweets)} tweets, {coverage:.0%} coverage"
        else:
            uncertainty = 0.5
            reasoning = f"Limited data: {len(tweets)} tweets, {coverage:.0%} coverage"
        
        return ToolResult(
            data={"tweets": tweets, "follow_edges": follows},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                evidence_count=len(tweets)
            )
        )
```

### T31_ENTITY_BUILDER + T34_EDGE_BUILDER (Real KGAS Tools)
```python
class T31_ENTITY_BUILDER(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        tweets = request.input_data["tweets"]
        
        # Build user entities from tweet authors
        users = {}
        for tweet in tweets:
            user_id = tweet.get("user_id")
            if user_id and user_id not in users:
                users[user_id] = {
                    "id": user_id,
                    "type": "User",
                    "tweet_count": 0
                }
            if user_id:
                users[user_id]["tweet_count"] += 1
        
        uncertainty = 0.1 if len(users) > 1000 else 0.2
        reasoning = f"Created {len(users)} user entities"
        
        return ToolResult(
            data={"entities": users},
            uncertainty=UniversalUncertainty(uncertainty=uncertainty, reasoning=reasoning)
        )

class T34_EDGE_BUILDER(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        follow_edges = request.input_data["follow_edges"]
        
        # Build graph edges
        edges = []
        for edge in follow_edges:
            edges.append({
                "source": edge["follower"],
                "target": edge["followed"],
                "type": "FOLLOWS"
            })
        
        uncertainty = 0.1 if len(edges) > 10000 else 0.25
        reasoning = f"Built {len(edges)} follow relationships"
        
        return ToolResult(
            data={"edges": edges},
            uncertainty=UniversalUncertainty(uncertainty=uncertainty, reasoning=reasoning)
        )
```

### T50_COMMUNITY_DETECTION (Real KGAS Tool)
```python
class T50_COMMUNITY_DETECTION(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        entities = request.input_data["entities"]
        edges = request.input_data["edges"]
        
        # Build NetworkX graph
        G = nx.DiGraph()
        for user_id in entities:
            G.add_node(user_id)
        for edge in edges:
            G.add_edge(edge["source"], edge["target"])
        
        # Convert to undirected for community detection
        G_undirected = G.to_undirected()
        
        # Detect communities using Louvain
        communities = nx.community.louvain_communities(G_undirected)
        
        # Create user->community mapping
        user_communities = {}
        community_members = {}
        for i, community in enumerate(communities):
            community_id = f"community_{i}"
            community_members[community_id] = list(community)
            for user in community:
                user_communities[user] = community_id
        
        # Calculate modularity
        modularity = nx.community.modularity(G_undirected, communities)
        
        # Self-assess based on modularity and sizes
        sizes = [len(c) for c in communities]
        
        if modularity > 0.4 and min(sizes) > 100:
            uncertainty = 0.18
            reasoning = f"Clear communities: modularity={modularity:.2f}, {len(communities)} communities"
        elif modularity > 0.3:
            uncertainty = 0.3
            reasoning = f"Moderate communities: modularity={modularity:.2f}"
        else:
            uncertainty = 0.45
            reasoning = f"Weak community structure: modularity={modularity:.2f}"
        
        return ToolResult(
            data={
                "user_communities": user_communities,
                "community_members": community_members,
                "n_communities": len(communities)
            },
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                evidence_count=len(communities)
            )
        )
```

### T23C_ONTOLOGY_AWARE_EXTRACTOR (Real KGAS Tool)
```python
class T23C_ONTOLOGY_AWARE_EXTRACTOR(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        tweets = request.input_data["tweets"]
        user_communities = request.input_data["user_communities"]
        
        # Extract politician mentions and sentiment
        user_sentiments = {}
        
        for tweet in tweets:
            text = tweet.get("text", "").lower()
            user_id = tweet.get("user_id")
            
            if not user_id or user_id not in user_communities:
                continue
            
            # Check for politicians
            biden_mentioned = "biden" in text
            trump_mentioned = "trump" in text
            
            if not (biden_mentioned or trump_mentioned):
                continue
            
            # Extract sentiment (would use LLM in real implementation)
            if user_id not in user_sentiments:
                user_sentiments[user_id] = {
                    "Biden": [],
                    "Trump": [],
                    "community": user_communities[user_id]
                }
            
            if biden_mentioned:
                # Simplified sentiment scoring
                sentiment = self._analyze_sentiment(text, "biden")
                user_sentiments[user_id]["Biden"].append(sentiment)
            
            if trump_mentioned:
                sentiment = self._analyze_sentiment(text, "trump")
                user_sentiments[user_id]["Trump"].append(sentiment)
        
        # Self-assess
        extraction_rate = len(user_sentiments) / len(user_communities)
        
        if extraction_rate > 0.3:
            uncertainty = 0.25
            reasoning = f"Good extraction: {len(user_sentiments)} users with sentiments ({extraction_rate:.0%})"
        elif extraction_rate > 0.15:
            uncertainty = 0.4
            reasoning = f"Moderate extraction: {extraction_rate:.0%} of users"
        else:
            uncertainty = 0.6
            reasoning = f"Limited extraction: only {extraction_rate:.0%} of users"
        
        return ToolResult(
            data={"user_sentiments": user_sentiments},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                evidence_count=len(user_sentiments)
            )
        )
    
    def _analyze_sentiment(self, text: str, politician: str) -> float:
        """Simplified sentiment analysis - would use LLM in real implementation"""
        # Returns score from -1 (negative) to 1 (positive)
        positive_words = ["good", "great", "support", "love", "best"]
        negative_words = ["bad", "terrible", "hate", "worst", "corrupt"]
        
        score = 0.0
        for word in positive_words:
            if word in text:
                score += 0.2
        for word in negative_words:
            if word in text:
                score -= 0.2
        
        return max(-1, min(1, score))
```

### T56_GRAPH_METRICS (Real KGAS Tool)
```python
class T56_GRAPH_METRICS(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        user_sentiments = request.input_data["user_sentiments"]
        community_members = request.input_data["community_members"]
        
        # Calculate metrics per community
        community_metrics = {}
        
        for community_id, members in community_members.items():
            # Aggregate sentiments for this community
            biden_scores = []
            trump_scores = []
            
            for user_id in members:
                if user_id in user_sentiments:
                    user_data = user_sentiments[user_id]
                    if user_data["Biden"]:
                        biden_scores.extend(user_data["Biden"])
                    if user_data["Trump"]:
                        trump_scores.extend(user_data["Trump"])
            
            if biden_scores or trump_scores:
                community_metrics[community_id] = {
                    "size": len(members),
                    "users_with_sentiment": sum(1 for u in members if u in user_sentiments),
                    "biden_sentiment": {
                        "mean": np.mean(biden_scores) if biden_scores else None,
                        "std": np.std(biden_scores) if biden_scores else None,
                        "count": len(biden_scores)
                    },
                    "trump_sentiment": {
                        "mean": np.mean(trump_scores) if trump_scores else None,
                        "std": np.std(trump_scores) if trump_scores else None,
                        "count": len(trump_scores)
                    },
                    "coverage": sum(1 for u in members if u in user_sentiments) / len(members)
                }
        
        # Self-assess
        avg_coverage = np.mean([m["coverage"] for m in community_metrics.values()])
        
        if avg_coverage > 0.25 and len(community_metrics) >= 3:
            uncertainty = 0.2
            reasoning = f"Good metrics: {avg_coverage:.0%} coverage, {len(community_metrics)} communities"
        elif avg_coverage > 0.15:
            uncertainty = 0.35
            reasoning = f"Moderate metrics: {avg_coverage:.0%} coverage"
        else:
            uncertainty = 0.55
            reasoning = f"Limited metrics: {avg_coverage:.0%} coverage"
        
        return ToolResult(
            data={"community_metrics": community_metrics},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                evidence_count=len(community_metrics)
            )
        )
```

### T58_GRAPH_COMPARISON (Real KGAS Tool)
```python
class T58_GRAPH_COMPARISON(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        community_metrics = request.input_data["community_metrics"]
        
        # Find communities with sufficient data
        viable_communities = [
            (cid, metrics) for cid, metrics in community_metrics.items()
            if metrics["biden_sentiment"]["count"] >= 30 and 
               metrics["trump_sentiment"]["count"] >= 30
        ]
        
        if len(viable_communities) < 2:
            return ToolResult(
                data={"error": "Insufficient data for comparison"},
                uncertainty=UniversalUncertainty(
                    uncertainty=0.9,
                    reasoning="Need at least 2 communities with 30+ sentiments each"
                )
            )
        
        # Compare top 2 communities
        viable_communities.sort(key=lambda x: x[1]["size"], reverse=True)
        comm1_id, comm1_data = viable_communities[0]
        comm2_id, comm2_data = viable_communities[1]
        
        # Statistical comparison
        from scipy import stats
        
        comparisons = {}
        
        # Compare Biden sentiment
        if comm1_data["biden_sentiment"]["mean"] is not None and comm2_data["biden_sentiment"]["mean"] is not None:
            diff = abs(comm1_data["biden_sentiment"]["mean"] - comm2_data["biden_sentiment"]["mean"])
            pooled_std = np.sqrt((comm1_data["biden_sentiment"]["std"]**2 + comm2_data["biden_sentiment"]["std"]**2) / 2)
            effect_size = diff / pooled_std if pooled_std > 0 else 0
            
            # Approximate t-test (would need raw data for exact)
            se = pooled_std * np.sqrt(1/comm1_data["biden_sentiment"]["count"] + 1/comm2_data["biden_sentiment"]["count"])
            t_stat = diff / se if se > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=comm1_data["biden_sentiment"]["count"] + comm2_data["biden_sentiment"]["count"] - 2))
            
            comparisons["biden"] = {
                "community1": comm1_id,
                "community2": comm2_id,
                "mean_diff": diff,
                "effect_size": effect_size,
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant": p_value < 0.05
            }
        
        # Compare Trump sentiment (similar logic)
        if comm1_data["trump_sentiment"]["mean"] is not None and comm2_data["trump_sentiment"]["mean"] is not None:
            diff = abs(comm1_data["trump_sentiment"]["mean"] - comm2_data["trump_sentiment"]["mean"])
            pooled_std = np.sqrt((comm1_data["trump_sentiment"]["std"]**2 + comm2_data["trump_sentiment"]["std"]**2) / 2)
            effect_size = diff / pooled_std if pooled_std > 0 else 0
            
            se = pooled_std * np.sqrt(1/comm1_data["trump_sentiment"]["count"] + 1/comm2_data["trump_sentiment"]["count"])
            t_stat = diff / se if se > 0 else 0
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=comm1_data["trump_sentiment"]["count"] + comm2_data["trump_sentiment"]["count"] - 2))
            
            comparisons["trump"] = {
                "community1": comm1_id,
                "community2": comm2_id,
                "mean_diff": diff,
                "effect_size": effect_size,
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant": p_value < 0.05
            }
        
        # Self-assess
        min_n = min(
            comm1_data["biden_sentiment"]["count"],
            comm1_data["trump_sentiment"]["count"],
            comm2_data["biden_sentiment"]["count"],
            comm2_data["trump_sentiment"]["count"]
        )
        
        if min_n > 100 and any(c.get("p_value", 1) < 0.001 for c in comparisons.values()):
            uncertainty = 0.15
            reasoning = f"Strong evidence: n>{min_n}, significant differences found"
        elif min_n > 50:
            uncertainty = 0.3
            reasoning = f"Moderate evidence: n={min_n}"
        else:
            uncertainty = 0.5
            reasoning = f"Limited evidence: n={min_n}"
        
        return ToolResult(
            data={
                "comparisons": comparisons,
                "summary": {
                    "communities_compared": [comm1_id, comm2_id],
                    "significant_differences": sum(1 for c in comparisons.values() if c.get("significant", False))
                }
            },
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning,
                evidence_count=min_n * 2  # samples from both communities
            )
        )
```

### T60_GRAPH_EXPORT (Real KGAS Tool)
```python
class T60_GRAPH_EXPORT(KGASTool):
    def execute(self, request: ToolRequest) -> ToolResult:
        comparisons = request.input_data["comparisons"]
        community_metrics = request.input_data["community_metrics"]
        
        # Format results for export
        export_data = {
            "analysis_type": "Twitter Political Attitude Comparison",
            "communities": community_metrics,
            "statistical_comparisons": comparisons,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        output_path = request.parameters.get("output_path", "twitter_analysis_results.json")
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        uncertainty = 0.05  # Export is deterministic
        reasoning = f"Exported {len(community_metrics)} communities, {len(comparisons)} comparisons"
        
        return ToolResult(
            data={"export_path": output_path},
            uncertainty=UniversalUncertainty(
                uncertainty=uncertainty,
                reasoning=reasoning
            )
        )
```

## Key Points

1. **ALL REAL KGAS TOOLS**: No dynamically generated tools - using T06, T31, T34, T50, T23C, T56, T58, T60
2. **Communities DETECTED**: Communities come from network structure via T50, not from input data
3. **Single input file**: One JSON with tweets and follows only
4. **Self-assessment built in**: Each tool assesses its own uncertainty during execution
5. **Statistical comparison**: T58 provides real statistical testing capabilities
6. **Complete workflow**: From raw data to statistical results using only existing tools

## Uncertainty Sources
- **Data completeness**: How many users appear in both tweets and follow graph
- **Community quality**: Modularity score from community detection
- **Extraction coverage**: Percentage of users with extractable sentiments
- **Sample sizes**: Number of data points for statistical tests
- **Statistical power**: Effect sizes and p-values from comparisons