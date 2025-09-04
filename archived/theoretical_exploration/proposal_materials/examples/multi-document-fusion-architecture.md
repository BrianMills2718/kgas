# Multi-Document Fusion Architecture for KGAS
*Extracted from proposal materials - 2025-08-29*  
*Status: Implementation Example - Core Architecture*

## Overview

This document explains KGAS's approach to multi-document fusion, which builds unified property graphs in Neo4j through entity resolution and linking rather than traditional relational database joins. This architecture enables cross-modal analysis and theory-aware processing.

**Key Innovation**: Create unified property graphs that preserve relationships between heterogeneous data sources while enabling graph algorithms, statistical analysis, and vector operations on the same underlying data.

## Core Problem

Modern computational social science research involves heterogeneous data sources that must be integrated for comprehensive analysis:

- **Textual Data**: Tweets, posts, documents with unstructured content
- **Behavioral Data**: User interactions, network connections, temporal patterns  
- **Psychological Data**: Survey responses, personality measures, demographic info
- **Contextual Data**: External sources, credibility ratings, metadata

**Traditional Challenge**: These sources have different schemas, formats, and granularities, making integration complex.

## Property Graph Solution

### Why Graph Instead of Relational Tables?

1. **Natural Representation**: Social networks and interactions are inherently graph-structured
2. **Flexible Schema**: Heterogeneous data sources with different properties
3. **Graph Algorithms**: PageRank, community detection work directly on structure
4. **Cross-Modal Capability**: Can export to tables (Phase 5) or vectors (Phase 7) as needed
5. **Entity Resolution**: Graph structure helps identify same entities across sources

### Graph Structure Design

#### Node Types
```cypher
// User nodes with psychological properties
(:User {
    user_id: "ID001",
    conspiracy_score: 5.8,
    anxiety_score: 3.2,
    trust_score: 1.9,
    registration_date: date,
    verified: boolean
})

// Tweet/Content nodes  
(:Tweet {
    tweet_id: "TW2938472",
    text: "Don't trust the vaccine...",
    timestamp: 1614556800,
    user_id: "ID001",
    retweet_count: 45,
    like_count: 127
})

// Information Source nodes
(:Source {
    url: "cdc.gov/vaccines",
    credibility: 0.95,
    type: "official_health",
    domain: "cdc.gov"
})

// Group/Community nodes (derived)
(:Community {
    community_id: "vaccine_hesitant",
    size: 512,
    avg_conspiracy_score: 6.2,
    formation_date: date
})
```

#### Relationship Types
```cypher
// User authored content
(user:User)-[:AUTHORED {timestamp: datetime}]->(tweet:Tweet)

// Social network structure
(user1:User)-[:FOLLOWS {since: date}]->(user2:User)
(user1:User)-[:MENTIONS {in_tweet: "TW123"}]->(user2:User)
(user1:User)-[:RETWEETS {timestamp: datetime}]->(tweet:Tweet)

// Content-source relationships
(tweet:Tweet)-[:CITES {context: "supporting"}]->(source:Source)
(tweet:Tweet)-[:CONTRADICTS {context: "opposing"}]->(source:Source)

// Community membership (derived)
(user:User)-[:BELONGS_TO {confidence: float, since: date}]->(community:Community)

// Influence relationships (computed)
(user1:User)-[:INFLUENCES {strength: float, mechanism: "retweet"}]->(user2:User)
```

## Multi-Document Fusion Process

### Input Data Sources Example

**1. Tweet Data (T01_PDF_LOAD)**
```json
{
  "tweet_id": "TW001",
  "user_id": "u_042",
  "text": "Climate change is the biggest threat we face",
  "timestamp": "2024-01-15T10:30:00",
  "retweet_of": null,
  "reply_to": null,
  "hashtags": ["#ClimateChange", "#Science"],
  "mentions": ["@EPA"],
  "like_count": 23,
  "retweet_count": 8
}
```

**2. User Psychology Profiles (T05_CSV_LOAD)**
```csv
user_id,conspiracy_score,anxiety_score,trust_score,education,age_range
u_042,2.1,3.8,7.2,college,25-34
u_101,6.8,5.2,2.1,high_school,45-54
u_238,4.3,4.1,5.5,graduate,35-44
```

**3. Network Interaction Data (T06_JSON_LOAD)**
```json
{
  "user_id": "u_042",
  "follows": ["u_101", "u_238", "u_405"],
  "followers": ["u_067", "u_129", "u_331"],
  "mentioned_by": ["u_101", "u_405"],
  "retweets_from": ["u_238"]
}
```

**4. Information Sources (T13_WEB_SCRAPE)**
```json
{
  "url": "cdc.gov/climate-health",
  "content": "Climate change affects public health...",
  "cited_by_users": ["u_042", "u_238"],
  "credibility_rating": 0.95,
  "domain_authority": 0.98,
  "publication_date": "2023-11-15"
}
```

### Fusion Algorithm

```python
class MultiDocumentFusion:
    """Build unified property graph from heterogeneous sources"""
    
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        self.entity_resolver = EntityResolver()
        
    def fuse_documents(self, data_sources: Dict) -> str:
        """Create unified graph from all data sources"""
        
        # Step 1: Create base nodes
        user_nodes = self._create_user_nodes(data_sources)
        content_nodes = self._create_content_nodes(data_sources) 
        source_nodes = self._create_source_nodes(data_sources)
        
        # Step 2: Entity resolution across sources
        resolved_entities = self._resolve_entities(user_nodes)
        
        # Step 3: Create relationships
        self._create_authorship_edges(resolved_entities, content_nodes)
        self._create_social_edges(resolved_entities, data_sources['network'])
        self._create_citation_edges(content_nodes, source_nodes)
        
        # Step 4: Derive community structure
        communities = self._detect_communities()
        self._create_community_nodes(communities)
        
        # Step 5: Compute influence metrics
        self._compute_influence_relationships()
        
        return "fusion_complete"
    
    def _create_user_nodes(self, data_sources: Dict) -> List[Dict]:
        """Create user nodes with integrated properties"""
        users = []
        
        # Base users from tweets
        tweet_users = set()
        for tweet in data_sources['tweets']:
            tweet_users.add(tweet['user_id'])
        
        # Enrich with psychology data
        psych_data = {row['user_id']: row for row in data_sources['psychology']}
        
        for user_id in tweet_users:
            user_props = {'user_id': user_id}
            
            # Add psychological properties if available
            if user_id in psych_data:
                psych = psych_data[user_id]
                user_props.update({
                    'conspiracy_score': psych['conspiracy_score'],
                    'anxiety_score': psych['anxiety_score'], 
                    'trust_score': psych['trust_score'],
                    'education': psych['education'],
                    'age_range': psych['age_range']
                })
            
            # Create neo4j node
            with self.driver.session() as session:
                session.run("""
                    CREATE (u:User $props)
                """, props=user_props)
            
            users.append(user_props)
        
        return users
    
    def _create_social_edges(self, users: List[Dict], network_data: List[Dict]) -> None:
        """Create social network relationships"""
        
        for network_record in network_data:
            user_id = network_record['user_id']
            
            # Create FOLLOWS relationships
            for followed_id in network_record.get('follows', []):
                with self.driver.session() as session:
                    session.run("""
                        MATCH (u1:User {user_id: $user1})
                        MATCH (u2:User {user_id: $user2})
                        CREATE (u1)-[:FOLLOWS {created: datetime()}]->(u2)
                    """, user1=user_id, user2=followed_id)
            
            # Create MENTIONS relationships
            for mentioned_id in network_record.get('mentioned_by', []):
                with self.driver.session() as session:
                    session.run("""
                        MATCH (u1:User {user_id: $user1})
                        MATCH (u2:User {user_id: $user2})
                        CREATE (u1)-[:MENTIONS {created: datetime()}]->(u2)
                    """, user1=mentioned_id, user2=user_id)
    
    def _detect_communities(self) -> List[Dict]:
        """Use graph algorithms to detect communities"""
        
        with self.driver.session() as session:
            # Use Louvain algorithm for community detection
            result = session.run("""
                CALL gds.louvain.stream('user-network')
                YIELD nodeId, communityId
                RETURN gds.util.asNode(nodeId).user_id as user_id, 
                       communityId,
                       count(*) as community_size
                ORDER BY communityId
            """)
            
            communities = {}
            for record in result:
                comm_id = record['communityId']
                if comm_id not in communities:
                    communities[comm_id] = {
                        'community_id': f"community_{comm_id}",
                        'members': [],
                        'size': 0
                    }
                
                communities[comm_id]['members'].append(record['user_id'])
                communities[comm_id]['size'] += 1
        
        return list(communities.values())
    
    def _resolve_entities(self, entities: List[Dict]) -> List[Dict]:
        """Resolve entity references across data sources"""
        
        # Handle user ID variations (u_042, user_042, 042, etc.)
        resolved = []
        id_mapping = {}
        
        for entity in entities:
            canonical_id = self.entity_resolver.canonicalize_user_id(entity['user_id'])
            
            if canonical_id not in id_mapping:
                id_mapping[canonical_id] = entity
                entity['canonical_id'] = canonical_id
                resolved.append(entity)
            else:
                # Merge properties from duplicate entities
                existing = id_mapping[canonical_id]
                existing.update({k: v for k, v in entity.items() if v is not None})
        
        return resolved
```

## Theory-Aware Extraction Integration

### Ontology-Aware Processing

The property graph enables theory-guided entity extraction:

```python
def theory_guided_extraction(graph, theory_schema):
    """Extract theory-relevant entities from property graph"""
    
    extracted_entities = []
    
    # Extract based on theory requirements
    for entity_spec in theory_schema['entities']:
        if entity_spec['indigenous_name'] == "Self-Category":
            # Query graph for group identity markers
            with graph.session() as session:
                groups = session.run("""
                    MATCH (u:User)-[:AUTHORED]->(t:Tweet)
                    WHERE t.text =~ '.*\\b(we|us|our)\\b.*vaccine.*'
                    RETURN u.user_id, t.text, 'in_group' as level
                """)
                extracted_entities.extend(groups)
        
        elif entity_spec['indigenous_name'] == "Prototype":
            # Find most prototypical members using graph metrics
            prototypes = session.run("""
                MATCH (u:User)-[:AUTHORED]->(t:Tweet)
                WITH u, COUNT(t) as tweet_count, 
                     AVG(u.conspiracy_score) as avg_conspiracy
                WHERE tweet_count > 100
                RETURN u.user_id, 
                       calculate_meta_contrast(u) as prototypicality_score
                ORDER BY prototypicality_score DESC
                LIMIT 10
            """)
            extracted_entities.extend(prototypes)
    
    return extracted_entities
```

### Cross-Modal Export Capabilities

The unified graph enables export to different analytical modalities:

```python
class CrossModalExporter:
    """Export graph data to different analytical formats"""
    
    def export_to_table(self, community_focus: str = None) -> pd.DataFrame:
        """Export graph metrics to statistical analysis table"""
        
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:BELONGS_TO]->(c:Community)
        OPTIONAL MATCH (u)-[:AUTHORED]->(t:Tweet)
        WITH u, c, COUNT(t) as tweet_count
        RETURN 
            u.user_id as user_id,
            u.conspiracy_score as conspiracy_score,
            u.anxiety_score as anxiety_score,
            u.trust_score as trust_score,
            c.community_id as community_id,
            tweet_count,
            gds.alpha.centrality.betweenness.stream(u) as betweenness_centrality
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            return pd.DataFrame([record.data() for record in result])
    
    def export_to_vectors(self, embedding_dimension: int = 384) -> Dict:
        """Export user features as vectors for similarity analysis"""
        
        # Get user feature vectors
        query = """
        MATCH (u:User)-[:AUTHORED]->(t:Tweet)
        WITH u, COLLECT(t.text) as user_texts
        RETURN 
            u.user_id as user_id,
            user_texts,
            [u.conspiracy_score, u.anxiety_score, u.trust_score] as psych_vector
        """
        
        vectors = {}
        with self.driver.session() as session:
            result = session.run(query)
            for record in result:
                # Combine text embeddings with psychological features
                text_embedding = self._embed_texts(record['user_texts'])
                psych_features = record['psych_vector']
                
                vectors[record['user_id']] = {
                    'text_embedding': text_embedding,
                    'psych_features': psych_features,
                    'combined_vector': self._combine_features(text_embedding, psych_features)
                }
        
        return vectors
```

## Benefits and Applications

### Research Workflow Integration

1. **Unified Data Model**: Single graph contains all data relationships
2. **Theory Integration**: Graph structure supports theory-specific queries
3. **Cross-Modal Analysis**: Export to optimal format for each analysis type
4. **Provenance Tracking**: All relationships maintain source information

### Computational Advantages

1. **Graph Algorithms**: Direct application of network analysis methods
2. **Efficient Queries**: Graph databases optimized for relationship traversal
3. **Scalable**: Property graphs handle large, complex datasets efficiently
4. **Flexible Schema**: Easy to add new data sources and relationships

### Research Quality

1. **Entity Resolution**: Systematic handling of identity across sources
2. **Data Integration**: Comprehensive view of research subjects
3. **Relationship Preservation**: Social and content relationships maintained
4. **Temporal Tracking**: Time-ordered data enables process analysis

## Example Output Structure

### Unified Property Graph
```cypher
// Example query results showing integrated data
MATCH (u:User {user_id: "u_042"})-[r]->(target)
RETURN u, type(r), target

// Results:
// u_042 AUTHORED TW001 ("Climate change is the biggest threat...")
// u_042 FOLLOWS u_101 (psychology profile: high trust, low conspiracy)
// u_042 BELONGS_TO community_pro_science (512 members)
// u_042 CITES cdc.gov/climate-health (credibility: 0.95)
```

### Cross-Modal Export Examples

**Table Export** (for statistical analysis):
```
user_id | conspiracy_score | community_id | centrality | tweet_count
u_042   | 2.1             | pro_science  | 0.034      | 127
u_101   | 6.8             | vaccine_hesitant | 0.091  | 203
```

**Vector Export** (for similarity analysis):
```python
{
  "u_042": {
    "combined_vector": [0.23, -0.15, 0.67, ..., 2.1, 3.8, 7.2],
    "text_embedding": [0.23, -0.15, 0.67, ...],  # 384 dim
    "psych_features": [2.1, 3.8, 7.2]             # 3 dim
  }
}
```

---

**Status**: Core architectural component for KGAS multi-document integration. Demonstrates how property graphs enable theory-aware analysis while supporting cross-modal export capabilities.

**Implementation Priority**: Essential for Phase 2 implementation - provides foundation for all downstream analysis capabilities.