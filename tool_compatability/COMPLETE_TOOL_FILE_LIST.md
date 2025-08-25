# Complete KGAS Tool File List

## Summary Statistics
- **188 total Python files** in `/src/tools/` directory
- **82 unique tool implementations** (files with T## identifiers)
- **30+ test files** for tools
- **20+ adapter files** for tool compatibility
- **Multiple registry and discovery services**

## Tool Implementation Files by Phase

### Phase 1 Core Tools (76 files)
**Loaders (T01-T14):**
- `/src/tools/phase1/t01_pdf_loader.py` (alias)
- `/src/tools/phase1/t01_pdf_loader_standalone.py`
- `/src/tools/phase1/t01_pdf_loader_unified.py` (main)
- `/src/tools/phase1/t01_pdf_processor.py`
- `/src/tools/phase1/t02_word_loader_unified.py`
- `/src/tools/phase1/t03_text_loader_unified.py`
- `/src/tools/phase1/t04_markdown_loader_unified.py`
- `/src/tools/phase1/t05_csv_loader_unified.py`
- `/src/tools/phase1/t06_json_loader_unified.py`
- `/src/tools/phase1/t07_html_loader_unified.py`
- `/src/tools/phase1/t08_xml_loader_unified.py`
- `/src/tools/phase1/t09_yaml_loader_unified.py`
- `/src/tools/phase1/t10_excel_loader_unified.py`
- `/src/tools/phase1/t11_powerpoint_loader_unified.py`
- `/src/tools/phase1/t12_zip_loader_unified.py`
- `/src/tools/phase1/t13_web_scraper_unified.py`
- `/src/tools/phase1/t14_email_parser_unified.py`

**Processing Tools:**
- `/src/tools/phase1/t15a_text_chunker.py` (alias)
- `/src/tools/phase1/t15a_text_chunker_standalone.py`
- `/src/tools/phase1/t15a_text_chunker_unified.py` (main)
- `/src/tools/phase1/t15b_vector_embedder.py`
- `/src/tools/phase1/t23a_llm_enhanced.py`
- `/src/tools/phase1/t23a_spacy_ner.py` (deprecated)
- `/src/tools/phase1/t23a_spacy_ner_standalone.py`
- `/src/tools/phase1/t23a_spacy_ner_unified.py`
- `/src/tools/phase1/t23c_llm_entity_extractor.py` (alias to phase2)
- `/src/tools/phase1/t27_relationship_extractor.py` (alias)
- `/src/tools/phase1/t27_relationship_extractor_fixed.py`
- `/src/tools/phase1/t27_relationship_extractor_standalone.py`
- `/src/tools/phase1/t27_relationship_extractor_unified.py` (main)
- `/src/tools/phase1/t41_async_text_embedder.py`

**Graph Construction:**
- `/src/tools/phase1/t31_entity_builder.py` (alias)
- `/src/tools/phase1/t31_entity_builder_improved.py`
- `/src/tools/phase1/t31_entity_builder_neo4j.py`
- `/src/tools/phase1/t31_entity_builder_standalone.py`
- `/src/tools/phase1/t31_entity_builder_unified.py` (main)
- `/src/tools/phase1/t34_edge_builder.py` (alias)
- `/src/tools/phase1/t34_edge_builder_neo4j.py`
- `/src/tools/phase1/t34_edge_builder_standalone.py`
- `/src/tools/phase1/t34_edge_builder_unified.py` (main)

**Graph Operations:**
- `/src/tools/phase1/t49_multihop_query.py` (alias)
- `/src/tools/phase1/t49_multihop_query_neo4j.py`
- `/src/tools/phase1/t49_multihop_query_standalone.py`
- `/src/tools/phase1/t49_multihop_query_unified.py` (main)
- `/src/tools/phase1/t49_multihop_query_unified_backup.py`
- `/src/tools/phase1/t68_pagerank.py` (alias)
- `/src/tools/phase1/t68_pagerank_neo4j.py`
- `/src/tools/phase1/t68_pagerank_optimized.py`
- `/src/tools/phase1/t68_pagerank_standalone.py`
- `/src/tools/phase1/t68_pagerank_unified.py` (main)
- `/src/tools/phase1/t85_twitter_explorer.py`

**Support Files:**
- `/src/tools/phase1/base_neo4j_tool.py`
- `/src/tools/phase1/neo4j_error_handler.py`
- `/src/tools/phase1/phase1_mcp_tools.py`
- `/src/tools/phase1/vertical_slice_workflow.py`
- `/src/tools/phase1/multihop_query/` (5 component files)

### Phase 2 Advanced Tools (70 files)
**Main Tools:**
- `/src/tools/phase2/t23c_ontology_aware_extractor.py` (wrapper)
- `/src/tools/phase2/t23c_ontology_aware_extractor_unified.py` (main)
- `/src/tools/phase2/t50_community_detection.py`
- `/src/tools/phase2/t50_community_detection_unified.py`
- `/src/tools/phase2/t50_graph_builder.py`
- `/src/tools/phase2/t51_centrality_analysis.py`
- `/src/tools/phase2/t51_centrality_analysis_unified.py`
- `/src/tools/phase2/t52_graph_clustering.py`
- `/src/tools/phase2/t52_graph_clustering_unified.py`
- `/src/tools/phase2/t53_network_motifs.py`
- `/src/tools/phase2/t53_network_motifs_unified.py`
- `/src/tools/phase2/t54_graph_visualization.py`
- `/src/tools/phase2/t54_graph_visualization_unified.py`
- `/src/tools/phase2/t55_temporal_analysis.py`
- `/src/tools/phase2/t55_temporal_analysis_unified.py`
- `/src/tools/phase2/t56_graph_metrics.py`
- `/src/tools/phase2/t56_graph_metrics_unified.py`
- `/src/tools/phase2/t57_path_analysis.py`
- `/src/tools/phase2/t57_path_analysis_unified.py`
- `/src/tools/phase2/t58_graph_comparison_unified.py`
- `/src/tools/phase2/t59_scale_free_analysis_unified.py`
- `/src/tools/phase2/t60_graph_export_unified.py`

**Component Modules:**
- `/src/tools/phase2/extraction_components/` (4 files)
- `/src/tools/phase2/centrality_analysis/` (5 files)
- `/src/tools/phase2/clustering/` (5 files)
- `/src/tools/phase2/community_detection/` (5 files)
- `/src/tools/phase2/graph_visualization/` (5 files)
- `/src/tools/phase2/metrics/` (7 files)
- `/src/tools/phase2/network_motifs/` (5 files)
- `/src/tools/phase2/path_analysis/` (6 files)
- `/src/tools/phase2/temporal/` (5 files)
- `/src/tools/phase2/visualization/` (5 files)

**Support Files:**
- `/src/tools/phase2/async_multi_document_processor.py`
- `/src/tools/phase2/enhanced_vertical_slice_workflow.py`
- `/src/tools/phase2/interactive_graph_visualizer.py`

### Phase 3 Fusion Tools (20 files)
**Main Tools:**
- `/src/tools/phase3/t301_multi_document_fusion.py`
- `/src/tools/phase3/t301_multi_document_fusion_unified.py`

**Component Modules:**
- `/src/tools/phase3/fusion/` (4 files)
- `/src/tools/phase3/fusion_algorithms/` (5 files)
- `/src/tools/phase3/document_ingestion/` (1 file)

**Support Files:**
- `/src/tools/phase3/basic_multi_document_workflow.py`
- `/src/tools/phase3/fusion_coordinator.py`
- `/src/tools/phase3/data_models.py`

### Phase C Tools (5 files)
- `/src/tools/phase_c/clustering_tool.py`
- `/src/tools/phase_c/collaborative_tool.py`
- `/src/tools/phase_c/cross_modal_tool.py`
- `/src/tools/phase_c/multi_document_tool.py`
- `/src/tools/phase_c/temporal_tool.py`

### Cross-Modal Tools (2 files)
- `/src/tools/cross_modal/graph_table_exporter.py`
- `/src/tools/cross_modal/multi_format_exporter.py`

### Base Classes (6 files)
- `/src/tools/base_tool.py`
- `/src/tools/base_tool_fixed.py`
- `/src/tools/base_classes/tool_performance_monitor.py`
- `/src/tools/base_classes/tool_protocol.py`
- `/src/tools/base_classes/tool_validator.py`
- `/src/tools/base_classes/unified_tool_wrapper.py`

## Core Tool Infrastructure Files

### Tool Contracts & Protocols
- `/src/core/tool_contract.py`
- `/src/core/tool_protocol.py`
- `/src/core/base_tool.py`

### Tool Registry & Discovery
- `/src/tools/tool_registry.py`
- `/src/core/tool_registry.py`
- `/src/core/tool_registry_auto.py`
- `/src/core/tool_registry_service.py`
- `/src/core/tool_discovery_service.py`
- `/src/mcp/tool_registry.py`
- `/data/tool_registry.json`

### Tool Factories
- `/src/core/tool_factory.py`
- `/src/core/tool_factory_refactored.py`
- `/src/core/tool_adapters/tool_adapter_factory.py`

### Tool Adapters
- `/src/core/tool_adapter.py`
- `/src/core/tool_adapter_bridge.py`
- `/src/core/tool_adapter_layer2.py`
- `/src/core/tool_adapters.py`
- `/src/core/field_adapters.py`
- `/src/core/adapters/` (8 adapter files)
- `/src/core/phase_adapters/` (6 phase adapter files)

### Tool Management
- `/src/core/tool_management/tool_discovery.py`
- `/src/core/tool_management/tool_instantiator.py`
- `/src/core/tool_management/tool_auditor.py`
- `/src/core/tool_management/async_tool_auditor.py`
- `/src/core/tool_management/workflow_config.py`
- `/src/core/tool_management/consistency_validator.py`
- `/src/core/tool_management/environment_monitor.py`

### Tool Monitoring & Validation
- `/src/core/tool_performance_monitor.py`
- `/src/core/tool_audit_service.py`
- `/src/core/pipeline_validator.py`

### MCP Integration
- `/src/mcp/tool_wrapper.py`
- `/src/orchestration/mcp_adapter.py`
- `/src/tools/phase1/phase1_mcp_tools.py`
- `/src/tools/enhanced_mcp_tools.py`

## Test Files

### Unit Tests
- `/tests/unit/test_tool_contracts.py`
- `/tests/unit/test_tool_adapters.py`
- `/tests/unit/test_tool_success_rate.py`
- `/tests/test_tool_basics.py`

### Integration Tests
- `/tests/integration/test_unified_tools_integration.py`
- `/tests/integration/test_tool_adapters_decomposition.py`

### Functional Tests
- `/tests/functional/test_mcp_tools_complete.py`
- `/tests/functional/test_all_tools_updated.py`
- `/tests/functional/test_mcp_tool_chains.py`
- `/tests/functional/test_mcp_tools_live.py`
- `/tests/functional/test_tools_functional_real.py`

### Phase Tests
- `/tests/test_phase_c_tool_wrappers.py`

## Documentation Files

### Architecture Documentation
- `/docs/architecture/systems/tool-registry-architecture.md`
- `/docs/architecture/systems/tool-contract-validation-specification.md`
- `/docs/architecture/concepts/services-vs-tools.md`
- `/docs/architecture/architecture_review_20250808/tool_compatibility_investigation.md`

### Analysis & Reports
- `/docs/analysis/tool-interface-compliance-report.md`
- `/docs/operations/reports/tool-audit-report.md`
- `/docs/operations/reports/tool-status-report.md`

### Roadmap & Planning
- `/docs/roadmap/initiatives/tooling/tool-implementation-status.md`
- `/docs/roadmap/initiatives/tooling/tool-count-methodology.md`
- `/docs/roadmap/initiatives/tooling/tool-count-clarification.md`
- `/docs/roadmap/initiatives/tooling/tool-rollout-timeline.md`
- `/docs/roadmap/initiatives/tooling/tool-rollout-gantt.md`

## Experimental Tool Files

### Tool Compatibility Experiments
- `/experiments/tool_compatability/take1/` (11 files)
- `/experiments/tool_compatability/take3/` (8 files)  
- `/experiments/tool_compatability/take4/` (7 files)
- `/experiments/tool_compatability/taje2/` (5 files)
- `/experiments/tool_compatability/GraphRAG/` (100+ files)

## Scripts & Utilities

### Tool Scripts
- `/scripts/fix_tool_categories.py`
- `/scripts/fix_tool_ids.py`
- `/scripts/migrate_tool_interfaces.py`
- `/scripts/audit_tool_interfaces.py`
- `/scripts/verify_tool_success_rate.py`
- `/scripts/generate_tool_registry_report.py`

## Key Findings

1. **Many Duplicate Versions**: Most tools have 3-5 versions (standalone, unified, neo4j, fixed, etc.)
2. **Alias Files Everywhere**: Many files are just imports from other files for backwards compatibility
3. **Phase Organization**: Tools organized by phase but many cross-references
4. **Component Decomposition**: Phase 2 tools heavily decomposed into component modules
5. **Incomplete Adapters**: Adapter directories exist but many are empty
6. **Registry Fragmentation**: Multiple registry implementations across different directories
7. **Test Coverage**: Extensive test files but unclear if all are current
8. **Documentation Scattered**: Tool documentation across multiple directories

## The Real Tool Count

Based on unique T## identifiers and removing aliases/duplicates:
- **~38-40 actual distinct tools implemented**
- **14 loaders** (T01-T14)
- **8 processing tools** (T15A/B, T23A/C, T27, T31, T34, T41)
- **2 query tools** (T49, T68)
- **11 phase 2 analysis tools** (T50-T60)
- **1 phase 3 fusion tool** (T301)
- **1 mystery tool** (T85 Twitter Explorer)

The rest of the 188 files are:
- Duplicate versions
- Component modules
- Support files
- Base classes
- Infrastructure