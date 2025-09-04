# Schema Discovery and Theory-Data Mapping for KGAS
*Extracted from proposal materials - 2025-08-29*  
*Status: Advanced Feature - Future Implementation*

## Overview

This document addresses a critical challenge in computational social science: how to bridge the gap between theoretical requirements and heterogeneous real-world data schemas. The solution involves automated schema discovery and intelligent theory-data mapping using LLM reasoning.

**Core Problem**: Theory schemas specify requirements like "user identities, timestamps, group membership" while actual data files have unknown schemas with columns like ["uid", "tweet_text", "created_at", "CB_score"].

## The Schema Discovery Challenge

### Traditional Assumptions (Current Approach)
```python
# Fixed schema assumptions
T01_PDF_LOAD: 
  Assumes: PDFs have extractable text
T05_CSV_LOAD:
  Assumes: CSV has "user_id" and "conspiracy_score" columns  
T06_JSON_LOAD:
  Assumes: JSON has "follows" array
```

**Problems**:
- Hardcoded column names fail with different data sources
- Cannot handle format variations
- No adaptation to missing or renamed fields
- Brittle with real-world data heterogeneity

### Schema Discovery Solution

**Intelligent Discovery Process**:
```python
# Discover actual schemas first
T300_SCHEMA_DISCOVERER:
  Input: Raw data files
  Output: Discovered schemas
  
  Process:
  1. Inspect CSV headers → ["uid", "CB_score", "trust_idx"]
  2. Sample JSON structure → {"author": str, "posted_at": int}
  3. Probe graph format → Node/edge lists with properties
```

## Implementation Architecture

### 1. Schema Discovery Engine

```python
class SchemaDiscoverer:
    """Automatically discover data schemas from heterogeneous sources"""
    
    def discover_csv_schema(self, file_path: str) -> Dict:
        """Analyze CSV structure and content"""
        df = pd.read_csv(file_path, nrows=100)  # Sample for analysis
        
        schema = {
            "format": "csv",
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "sample_values": df.head(5).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "estimated_semantics": self._infer_column_semantics(df)
        }
        return schema
    
    def discover_json_schema(self, file_path: str) -> Dict:
        """Analyze JSON structure and nested properties"""
        with open(file_path) as f:
            sample_data = [json.loads(line) for line in f.readlines()[:100]]
        
        # Build schema from sample
        schema = {
            "format": "json",
            "structure": self._analyze_json_structure(sample_data),
            "nested_objects": self._find_nested_objects(sample_data),
            "array_fields": self._identify_arrays(sample_data),
            "estimated_semantics": self._infer_json_semantics(sample_data)
        }
        return schema
    
    def _infer_column_semantics(self, df: pd.DataFrame) -> Dict:
        """Use heuristics and LLM to infer column meanings"""
        semantic_hints = {}
        
        for col in df.columns:
            # Pattern matching heuristics
            if any(pattern in col.lower() for pattern in ['id', 'uid', 'user']):
                semantic_hints[col] = "user_identifier"
            elif any(pattern in col.lower() for pattern in ['time', 'date', 'created']):
                semantic_hints[col] = "temporal"
            elif any(pattern in col.lower() for pattern in ['score', 'rating', 'measure']):
                semantic_hints[col] = "numeric_measure"
            else:
                # Use LLM for ambiguous cases
                sample_values = df[col].dropna().head(10).tolist()
                semantic_hints[col] = self._llm_infer_semantics(col, sample_values)
        
        return semantic_hints
```

### 2. Theory-Data Mapper

```python
class TheoryDataMapper:
    """Map theory requirements to discovered data schemas using LLM reasoning"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def map_theory_to_data(self, theory_schema: Dict, discovered_schemas: List[Dict]) -> Dict:
        """Generate mapping between theory needs and actual data"""
        
        mapping_prompt = f"""
        Theory Requirements:
        {json.dumps(theory_schema['data_requirements'], indent=2)}
        
        Available Data Schemas:
        {json.dumps(discovered_schemas, indent=2)}
        
        Generate mapping rules to connect theory requirements to actual data fields.
        Consider semantic similarity, data types, and content patterns.
        
        For each theory requirement, specify:
        1. Which data source provides it
        2. Which field/column contains the data  
        3. Any transformations needed
        4. Confidence level (high/medium/low)
        5. Alternative sources if primary unavailable
        """
        
        mapping = self.llm.generate(mapping_prompt, temperature=0.1)
        
        # Parse and validate mapping
        validated_mapping = self._validate_mapping(mapping, theory_schema, discovered_schemas)
        
        return validated_mapping
    
    def _validate_mapping(self, mapping: Dict, theory_schema: Dict, schemas: List[Dict]) -> Dict:
        """Validate that mappings are feasible and complete"""
        validated = {}
        
        for requirement, mapping_spec in mapping.items():
            # Check if data source exists
            source = mapping_spec.get('data_source')
            field = mapping_spec.get('field')
            
            if self._field_exists_in_schemas(source, field, schemas):
                validated[requirement] = {
                    **mapping_spec,
                    'validation_status': 'valid',
                    'accessor_function': self._generate_accessor(mapping_spec)
                }
            else:
                validated[requirement] = {
                    **mapping_spec,
                    'validation_status': 'missing',
                    'fallback_strategy': self._suggest_fallback(requirement, schemas)
                }
        
        return validated
```

### 3. Unified Data Access Layer

```python
class UnifiedDataAccessor:
    """Provide consistent interface to heterogeneous data sources"""
    
    def __init__(self, mapping: Dict):
        self.mapping = mapping
        self.data_sources = {}
    
    def load_data_source(self, source_name: str, file_path: str):
        """Load and cache data source"""
        if source_name.endswith('.csv'):
            self.data_sources[source_name] = pd.read_csv(file_path)
        elif source_name.endswith('.json'):
            self.data_sources[source_name] = self._load_json_data(file_path)
        # ... other formats
    
    def get_user_identity(self, record_context: Dict) -> str:
        """Get user identifier regardless of source schema"""
        mapping_spec = self.mapping['user_identifier']
        source = mapping_spec['data_source']
        field = mapping_spec['field']
        transform = mapping_spec.get('transformation')
        
        if source in self.data_sources:
            raw_value = self._extract_field(source, field, record_context)
            return self._apply_transformation(raw_value, transform) if transform else raw_value
        
        # Try fallback strategy
        return self._attempt_fallback('user_identifier', record_context)
    
    def get_timestamp(self, record_context: Dict) -> datetime:
        """Get timestamp with automatic format conversion"""
        mapping_spec = self.mapping['temporal_data']
        source = mapping_spec['data_source']
        field = mapping_spec['field']
        format_hint = mapping_spec.get('format')
        
        raw_value = self._extract_field(source, field, record_context)
        
        # Smart timestamp parsing
        if format_hint == 'iso':
            return pd.to_datetime(raw_value)
        elif format_hint == 'unix':
            return pd.to_datetime(raw_value, unit='s')
        else:
            # Auto-detect format
            return pd.to_datetime(raw_value, infer_datetime_format=True)
    
    def get_psychology_scores(self, user_id: str) -> Dict:
        """Get psychological profile data"""
        mapping_spec = self.mapping['psychology_data']
        # ... implementation for accessing psychology data
```

## Example Workflow

### Step 1: Multi-Source Discovery

**Input Data Sources**:
```
tweets.csv: ["uid", "tweet", "created_at", "likes", "retweets"]
psychology.csv: ["participant_id", "CB_score", "trust_gov", "anxiety_level"]  
network.json: {"nodes": [{"id": ..., "label": ...}], "edges": [...]}
```

### Step 2: Schema Discovery Results

```python
discovered_schemas = [
    {
        "source": "tweets.csv",
        "format": "csv", 
        "columns": ["uid", "tweet", "created_at", "likes", "retweets"],
        "semantics": {
            "uid": "user_identifier",
            "tweet": "text_content", 
            "created_at": "temporal",
            "likes": "engagement_metric",
            "retweets": "engagement_metric"
        }
    },
    {
        "source": "psychology.csv",
        "format": "csv",
        "columns": ["participant_id", "CB_score", "trust_gov", "anxiety_level"],
        "semantics": {
            "participant_id": "user_identifier",
            "CB_score": "conspiracy_belief_measure",
            "trust_gov": "trust_measure", 
            "anxiety_level": "psychological_measure"
        }
    },
    {
        "source": "network.json",
        "format": "json",
        "structure": "graph_format",
        "semantics": {
            "nodes.id": "user_identifier",
            "edges": "social_connections"
        }
    }
]
```

### Step 3: Theory-Data Mapping

**Self-Categorization Theory Requirements**:
```json
{
  "data_requirements": {
    "user_identifier": "Unique user identification",
    "group_membership": "Social group assignments", 
    "position_vectors": "Quantified user positions",
    "temporal_data": "Time-ordered data for process tracking",
    "social_connections": "Network relationship data"
  }
}
```

**Generated Mapping**:
```python
theory_data_mapping = {
    "user_identifier": {
        "primary_source": "tweets.csv",
        "primary_field": "uid",
        "alternatives": [
            {"source": "psychology.csv", "field": "participant_id"},
            {"source": "network.json", "field": "nodes.id"}
        ],
        "confidence": "high"
    },
    "temporal_data": {
        "primary_source": "tweets.csv", 
        "primary_field": "created_at",
        "transformation": "iso_to_datetime",
        "confidence": "high"
    },
    "position_vectors": {
        "primary_source": "psychology.csv",
        "primary_field": ["CB_score", "trust_gov", "anxiety_level"],
        "transformation": "normalize_and_vectorize",
        "confidence": "medium"
    },
    "social_connections": {
        "primary_source": "network.json",
        "primary_field": "edges",
        "transformation": "edge_list_to_adjacency",
        "confidence": "high"
    },
    "group_membership": {
        "primary_source": "DERIVED",
        "derivation_method": "community_detection_from_network",
        "confidence": "low",
        "note": "Must be computed from network structure"
    }
}
```

### Step 4: Unified Access Implementation

```python
# Usage example with unified interface
accessor = UnifiedDataAccessor(theory_data_mapping)
accessor.load_data_source("tweets.csv", "path/to/tweets.csv")
accessor.load_data_source("psychology.csv", "path/to/psychology.csv")
accessor.load_data_source("network.json", "path/to/network.json")

# Now use consistent interface regardless of underlying schemas
user_id = accessor.get_user_identity({"source": "tweets", "row": 42})
timestamp = accessor.get_timestamp({"source": "tweets", "row": 42}) 
psych_profile = accessor.get_psychology_scores(user_id)
connections = accessor.get_social_connections(user_id)
```

## Benefits and Applications

### Flexibility and Robustness
- **Schema Agnostic**: Works with any data format/structure
- **Handles Missing Data**: Graceful degradation with fallback strategies
- **Format Variations**: Automatic conversion between data types
- **Real-World Ready**: Handles messy, heterogeneous data sources

### Research Workflow Integration
- **Theory-First**: Starts with theoretical requirements
- **Data-Adaptive**: Adapts to available data sources
- **LLM-Enhanced**: Uses AI reasoning for semantic mapping
- **Validation Built-In**: Ensures mapping feasibility

### Implementation Efficiency
- **Reduces Hardcoding**: No more manual schema assumptions
- **Reusable Mappings**: Save successful mappings for similar datasets
- **Error Prevention**: Validates mappings before analysis
- **Developer Friendly**: Clear separation between theory and data concerns

## Integration with KGAS Architecture

### Phase 2 Enhancement
```python
# Enhanced Phase 2 with schema discovery
PHASE_2_ENHANCED = [
    "T300_SCHEMA_DISCOVERER",     # Discover all data schemas
    "T301_THEORY_DATA_MAPPER",    # Map theory needs to data
    "T302_UNIFIED_ACCESSOR",      # Create consistent interfaces
    "T303_MULTI_DOC_FUSION"       # Fuse with unified access
]
```

### Tool Integration
- **All Downstream Tools**: Use unified accessor instead of direct file access
- **Error Handling**: Graceful handling when expected data unavailable
- **Performance**: Efficient data access with caching and optimization
- **Monitoring**: Track mapping success rates and data coverage

### Future Extensions
- **Dynamic Schema Learning**: Improve mappings from usage patterns
- **Multi-Theory Support**: Handle competing theoretical requirements
- **Real-Time Adaptation**: Update mappings as new data sources added
- **Collaborative Mapping**: Share successful mappings across research teams

---

**Status**: Advanced feature for handling real-world data heterogeneity in computational social science research. Ready for implementation when KGAS Phase 1 proves basic architectural feasibility.

**Research Impact**: Enables KGAS to work with diverse, real-world datasets without requiring manual schema engineering, making computational social science more accessible and robust.