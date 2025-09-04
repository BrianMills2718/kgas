# Complete KGAS System Workflow Diagram
*Extracted from proposal materials - 2025-08-29*  
*Status: Complete System Architecture - Visual Reference*

## Overview

This document presents the complete 13-phase KGAS workflow for Social Identity Theory analysis of COVID discourse, showing tool dependencies, data flows, and cross-modal transfers. This comprehensive diagram demonstrates the full system capability from theory extraction through policy recommendations.

**Research Question**: "Why do vaccine hesitant groups reject mainstream health information?"  
**Theory**: Social Identity Theory (Tajfel & Turner, 1979)  
**Dataset**: 7.7M tweets from 2,506 users with psychological profiles

## Complete System DAG

```
================================================================================
    KGAS FULL SYSTEM DAG: SOCIAL IDENTITY THEORY ANALYSIS OF COVID DISCOURSE
================================================================================

                         PHASE 1: THEORY EXTRACTION                          
                                                                             
                                     ↓                 
                       T302_THEORY_EXTRACTION          
                       Extract SIT from papers         
                       Output: theory_schema           
                                     ↓                 
                             SIT Requirements:    
                           • Group boundaries    
                           • Identity strength   
                           • Intergroup bias     
                           • Hypothesis: ID→Bias 
                                     ↓                                         

                      PHASE 2: MULTI-DOCUMENT INGESTION                        
                                                                                
                         ↓           ↓           ↓           ↓
 T01_PDF_LOAD    T05_CSV_LOAD        T06_JSON_LOAD   T13_WEB_SCRAPE
 COVID tweets    User psychol.       Network data    Health sources
                                     ↓
                          T301_MULTI_DOC_FUSION     
                          Fuse all data sources     
                          Output: unified_dataset   
                                     ↓                                         

                    PHASE 3: THEORY-GUIDED EXTRACTION                          
                                                                                
                                     ↓                 
                      T23C_ONTOLOGY_AWARE_EXTRACTOR   
                      Input: text + theory_schema     
                      Extracts:                       
                      • Vaccine hesitant groups       
                      • Mainstream groups             
                      • Identity markers              
                      • Bias indicators               
                      • Relationships + properties    
                                     ↓                                         

                     PHASE 4: GRAPH CONSTRUCTION                               
                                                                                
                                     ↓                 
                        T31_ENTITY_BUILDER            
                        Create 2,506 user nodes       
                        + group identity nodes        
                                     ↓                 
                        T34_EDGE_BUILDER              
                        Build identification edges    
                        + interaction edges           
                                     ↓                   
                   ↓                                  ↓            
         T50_COMMUNITY_DETECT                 T68_PAGERANK         
         Find group clusters                  Calculate influence  
         Output: 3 communities                Output: centrality   
                                     ↓             
                             GRAPH METRICS:        
                          • Community A: 512 users 
                          • Community B: 887 users 
                          • Community C: 1107 users
                                     ↓                                         

                 PHASE 5: CROSS-MODAL TRANSFER (GRAPH → TABLE)                 
                                                                                
                                     ↓                 
                       GRAPH_TABLE_EXPORTER           
                       Convert communities to table   
                       Schema: user_id, community_id  
                                     ↓                                         

                  PHASE 6: TABLE ANALYSIS (PSYCHOLOGY)                         
                                                                                
                                     ↓                 
                       STATISTICAL_ANALYSIS_TOOL      
                       Analyze psychology by community
                       Community A: M=5.8 conspiracy  
                       Community B: M=2.1 conspiracy  
                                     ↓                 
                          SEM_MODELING_TOOL           
                       Test: Identity→Bias→Rejection  
                       Model fit: CFI=0.94            
                                     ↓             
                          HIGH IDENTITY USERS:     
                          IDs with score > 5.0     
                          {ID047, ID091, ID238...} 
                                     ↓                                         

                 PHASE 7: CROSS-MODAL TRANSFER (TABLE → VECTOR)                
                                                                                
                                     ↓                 
                        USER_SELECTION_FILTER         
                        Select high-identity users    
                                     ↓                                         

                    PHASE 8: VECTOR ANALYSIS (LANGUAGE)                        
                                                                                
                                     ↓                 
                        T15B_VECTOR_EMBEDDER          
                        Embed tweets from users       
                                     ↓                   
                   ↓                                  ↓            
         SEMANTIC_DISTANCE_CALC              CLUSTERING_TOOL       
         Between groups: 0.84                Language patterns:    
         Within A: 0.23                      • Rejection language  
         Within B: 0.31                      • Solidarity language 
                                     ↓                                         

                    PHASE 9: CROSS-MODAL SYNTHESIS                             
                                                                                
                                     ↓                 
                        CROSS_MODAL_ANALYZER          
                        Integrate all modalities:     
                        • Graph: Communities          
                        • Table: Psychology           
                        • Vector: Language            
                                                      
                        Correlations:                
                        • Network→Semantic: r=0.67    
                        • Identity→Rejection: r=0.72  
                                     ↓                                         

                    PHASE 10: AGENT-BASED SIMULATION                           
                                                                                
                                     ↓                 
                      AGENT_PARAMETERIZATION_TOOL     
                      Create 2,506 agents with:       
                      • Psychology profiles           
                      • Network positions             
                      • Language patterns             
                                     ↓                 
                       SIMULATION_EXECUTION_TOOL      
                       Test intervention scenarios:   
                       • Trusted messenger: -24%      
                       • Identity affirmation: -31%   
                       • Direct confrontation: +12%   
                                     ↓                                         

                    PHASE 11: UNCERTAINTY ANALYSIS                             
                                                                                
                                     ↓                 
                       IC_UNCERTAINTY_ANALYZER        
                       12 Dimensions assessed:        
                       • Source: Very Likely (80-95%) 
                       • Extraction: Likely (55-80%)  
                       • Construct: Likely (55-80%)   
                       • Theory Fit: Very Likely      
                                                      
                       OVERALL: LIKELY (55-80%)       
                                     ↓                                         

                    PHASE 12: INSIGHTS & VALIDATION                            
                                                                                
                                     ↓                 
                       THEORY_VALIDATION_TOOL         
                       SIT Hypothesis: SUPPORTED      
                       Effect size: d=1.2 (large)     
                       Key finding: High identity +   
                       network distance = 3.2x        
                       information rejection          
                                     ↓                 
                       INTERVENTION_RECOMMENDER       
                       Policy recommendations:        
                       1. Use in-group messengers     
                       2. Affirm group identity       
                       3. Avoid confrontation         
                       4. Target central nodes        
                                     ↓                                         

                    PHASE 13: VISUALIZATION & REPORTING                        
                                                                                
                         ↓           ↓           ↓           ↓
 T54_GRAPH_VIZ   DASHBOARD_GEN       REPORT_GEN      EXPORT_TOOLS  
 Interactive     Web interface       PDF report      CSV/JSON/LaTeX
 network view    Real-time           With charts     For papers    
                                     ↓
                              FINAL OUTPUT:          
                          • Executive summary        
                          • Theory validation        
                          • Cross-modal findings     
                          • Uncertainty assessment   
                          • Policy recommendations   
                          • Interactive visuals      
                          • Full provenance trail   
```

## Execution Metrics

**Total Tools Used**: 28  
**Parallel Operations**: 6 (marked with parallel branches)  
**Cross-Modal Transfers**: 3 (Graph→Table, Table→Vector, All→Synthesis)  
**Data Processed**: 7.7M tweets, 2,506 users with psychological profiles  
**Theoretical Constructs**: 5 (identity, bias, rejection, threat, solidarity)  
**Confidence Level**: LIKELY (55-80% per IC standards)  

## Key Innovation

**Theory-Guided Data Flow**: Social Categorization Theory (SCT) determines the entire data flow pattern:
- Graph (identify communities) → Table (measure psychology) → Vector (analyze language)
- This is NOT three parallel analyses but theory-guided sequential refinement

## Theory-Schema Alignment Analysis

### Category 1: Theory-Specified Tools
**Directly from SCT schema**:

- **T23C_ONTOLOGY_AWARE_EXTRACTOR** ✓
  - Extracts: Self-Categories, Prototypes, Meta-Contrast Ratios
  - Direct mapping from theory entities to data patterns
  - Uses theory schema as extraction template

- **T68_PAGERANK** ✓ (Partial alignment)
  - Maps to: "Referent Informational Influence" mechanism
  - Theory: "Influence flows from prototypical members"
  - PageRank identifies high-influence potential prototypes

- **CROSS_MODAL_ANALYZER** ✓
  - Implements: computational_representation.modality_flow
  - Theory specifies: Graph→weighted edges→meta-contrast→depersonalization
  - Tool orchestrates exact flow specified in schema

### Category 2: Theory-Enabling Tools
**Computational necessities not in SCT schema but required to operationalize it**:

- **T301_MULTI_DOC_FUSION**
  - Why needed: Build graph structure that theory assumes exists
  - Creates entity relationships theory analyzes

- **T50_COMMUNITY_DETECT**
  - Why needed: Identify in-groups/out-groups for meta-contrast
  - SCT assumes groups exist, doesn't explain finding them

- **Statistical Analysis Tools**
  - Why needed: Quantify psychological differences between groups
  - SCT describes mechanisms but not measurement procedures

### Category 3: Extensions Beyond Theory
**Tools that extend beyond SCT into policy applications**:

- **AGENT_PARAMETERIZATION_TOOL**
- **SIMULATION_EXECUTION_TOOL** 
- **INTERVENTION_RECOMMENDER**

## Critical Implementation Gaps

### Missing Tools (as of original analysis)
1. **Aggregation Tools**:
   - TWEET_USER_AGGREGATOR (aggregate tweets to user level)
   - USER_COMMUNITY_AGGREGATOR (aggregate users to community)

2. **Schema Tools**:
   - T300_SCHEMA_DISCOVERER (inspect data sources)
   - T301_SCHEMA_MAPPER (map discovered to theory needs)
   - T302_MULTI_DOC_FUSION (entity resolution across docs)

3. **Analysis Tools**:
   - T51_META_CONTRAST_CALCULATOR (SCT-specific MCR)
   - STATISTICAL_ANALYSIS_TOOL
   - SEM_MODELING_TOOL
   - SEMANTIC_DISTANCE_CALC

4. **Cross-Modal Tools**:
   - GRAPH_TABLE_EXPORTER
   - USER_SELECTION_FILTER
   - CROSS_MODAL_ANALYZER (synthesis)

5. **Simulation Tools**:
   - AGENT_PARAMETERIZATION_TOOL
   - SIMULATION_EXECUTION_TOOL

6. **Validation Tools**:
   - THEORY_VALIDATION_TOOL
   - INTERVENTION_RECOMMENDER

## Architectural Insights

### Cross-Modal Flow Pattern
The workflow demonstrates three distinct analytical modalities:
1. **Graph Analysis** (Phases 4-5): Community structure, influence patterns
2. **Table Analysis** (Phases 6-7): Statistical analysis, psychological measures
3. **Vector Analysis** (Phase 8): Language patterns, semantic relationships

### Theory Integration Points
- **Phase 1**: Theory extraction creates analysis template
- **Phase 3**: Theory-guided entity extraction
- **Phase 9**: Cross-modal synthesis validates theory predictions
- **Phase 12**: Formal theory validation and hypothesis testing

### Uncertainty Propagation
- **Tool-Level**: Each tool assesses its own uncertainty
- **Phase-Level**: Uncertainty propagates through dependencies
- **Overall**: IC uncertainty framework provides systematic assessment

## Research Workflow Insights

### Sequential vs Parallel Processing
- **Sequential**: Theory-guided refinement through modalities
- **Parallel**: Within-phase operations (e.g., community detection + PageRank)
- **Iterative**: Cross-modal synthesis informs further analysis

### Quality Assurance Points
- **Phase 3**: Theory alignment validation
- **Phase 9**: Cross-modal consistency checking
- **Phase 11**: Comprehensive uncertainty assessment
- **Phase 12**: Theory validation against predictions

### Scalability Considerations
- **Data Volume**: 7.7M tweets processed through multiple phases
- **Computational**: 28 tools coordinated in dependency graph
- **Temporal**: Full pipeline execution estimated 45-60 minutes
- **Memory**: Multiple data representations maintained simultaneously

---

**Status**: Complete system architecture diagram demonstrating full KGAS capabilities for theory-driven computational social science research.

**Usage**: Reference for understanding complete system flow, tool dependencies, and cross-modal analysis patterns. Essential for implementation planning and academic presentations.

**Key Value**: Shows how theory-driven analysis differs from traditional data science pipelines through systematic theory integration and cross-modal validation.