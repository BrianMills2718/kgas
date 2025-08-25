"""
Concrete examples showing how pipeline accumulation works for different workflows.

This demonstrates:
1. How tools chain together naturally
2. How data accumulates through the pipeline
3. How tools can flexibly read from different stages
4. How the same tool can work in different contexts
"""

from pipeline_data import PipelineData
from example_tools import (
    T01_PDFLoader,
    T05_CSVLoader,
    T23C_OntologyAwareExtractor,
    T31_EntityBuilder,
    T34_EdgeBuilder,
    T68_PageRank,
    T91_TableFormatter
)


def example_1_basic_pdf_to_graph():
    """
    Classic pipeline: PDF → Text → Extraction → Graph → Analysis
    
    Shows how data accumulates through each stage.
    """
    print("=" * 60)
    print("EXAMPLE 1: Basic PDF to Graph Analysis")
    print("=" * 60)
    
    # Initialize empty pipeline
    pipeline = PipelineData()
    print(f"Initial pipeline: {pipeline.list_stages()}")
    
    # Step 1: Load PDF
    loader = T01_PDFLoader()
    pipeline = loader.execute(pipeline, {"file_path": "document.pdf"})
    print(f"\nAfter T01: {pipeline.list_stages()}")
    print(f"  raw_text: '{pipeline.get_stage('raw_text')[:50]}...'")
    
    # Step 2: Extract entities and relationships
    extractor = T23C_OntologyAwareExtractor()
    pipeline = extractor.execute(pipeline, {"mode": "full_extraction"})
    print(f"\nAfter T23C: {pipeline.list_stages()}")
    extraction = pipeline.get_stage("extraction")
    print(f"  Entities: {len(extraction['entities'])}")
    print(f"  Relationships: {len(extraction['relationships'])}")
    
    # Step 3: Build graph nodes
    node_builder = T31_EntityBuilder()
    pipeline = node_builder.execute(pipeline, {})
    print(f"\nAfter T31: {pipeline.list_stages()}")
    nodes = pipeline.get_stage("graph_nodes")
    print(f"  Nodes created: {nodes.node_count}")
    
    # Step 4: Build full graph structure
    edge_builder = T34_EdgeBuilder()
    pipeline = edge_builder.execute(pipeline, {})
    print(f"\nAfter T34: {pipeline.list_stages()}")
    graph = pipeline.get_stage("graph_structure")
    print(f"  Graph: {graph['node_count']} nodes, {graph['edge_count']} edges")
    
    # Step 5: Calculate PageRank
    pagerank = T68_PageRank()
    pipeline = pagerank.execute(pipeline, {"damping_factor": 0.85})
    print(f"\nAfter T68: {pipeline.list_stages()}")
    scores = pipeline.get_stage("pagerank_scores")
    print(f"  PageRank calculated for {len(scores.scores)} nodes")
    
    # Step 6: Format results as table
    formatter = T91_TableFormatter()
    pipeline = formatter.execute(pipeline, {})
    print(f"\nAfter T91: {pipeline.list_stages()}")
    table = pipeline.get_stage("formatted_table")
    print(f"  Table: {table['row_count']} rows")
    
    # Show final pipeline state
    print("\n" + "=" * 40)
    print("FINAL PIPELINE STATE:")
    print("=" * 40)
    for stage in pipeline.list_stages():
        meta = pipeline.get_stage_metadata(stage)
        print(f"  {stage}:")
        print(f"    Tool: {meta.tool_id}")
        print(f"    Type: {meta.data_type}")
        print(f"    Size: {meta.size_bytes} bytes")
        if meta.dependencies:
            print(f"    Depends on: {meta.dependencies}")
    
    return pipeline


def example_2_csv_to_graph():
    """
    Alternative pipeline: CSV → Table → Extraction → Graph
    
    Shows how T23C can work with table data instead of text.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: CSV to Graph (Alternative Input)")
    print("=" * 60)
    
    pipeline = PipelineData()
    
    # Step 1: Load CSV (different starting point)
    csv_loader = T05_CSVLoader()
    pipeline = csv_loader.execute(pipeline, {"file_path": "data.csv"})
    print(f"After T05: {pipeline.list_stages()}")
    table = pipeline.get_stage("table_data")
    print(f"  Table: {len(table['rows'])} rows, {len(table['columns'])} columns")
    
    # Step 2: T23C can extract from table data too!
    extractor = T23C_OntologyAwareExtractor()
    pipeline = extractor.execute(pipeline, {"mode": "full_extraction"})
    print(f"\nAfter T23C: {pipeline.list_stages()}")
    extraction = pipeline.get_stage("extraction")
    print(f"  Extracted {len(extraction['entities'])} entities from table")
    
    # Rest of pipeline is the same
    pipeline = T31_EntityBuilder().execute(pipeline, {})
    pipeline = T34_EdgeBuilder().execute(pipeline, {})
    pipeline = T68_PageRank().execute(pipeline, {})
    
    print(f"\nFinal stages: {pipeline.list_stages()}")
    
    return pipeline


def example_3_branching_pipeline():
    """
    Pipeline with multiple analysis branches.
    
    Shows how multiple tools can read from the same stage.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Branching Analysis")
    print("=" * 60)
    
    # Build up to graph structure
    pipeline = PipelineData()
    pipeline = T01_PDFLoader().execute(pipeline, {"file_path": "doc.pdf"})
    pipeline = T23C_OntologyAwareExtractor().execute(pipeline, {"mode": "full_extraction"})
    pipeline = T31_EntityBuilder().execute(pipeline, {})
    pipeline = T34_EdgeBuilder().execute(pipeline, {})
    
    print(f"Base pipeline: {pipeline.list_stages()}")
    
    # Branch 1: PageRank analysis
    pipeline = T68_PageRank().execute(pipeline, {"damping_factor": 0.85})
    print(f"\nBranch 1 - PageRank added: {pipeline.list_stages()[-1]}")
    
    # Branch 2: Direct formatting of extraction (skips PageRank)
    # T91 can format extraction results directly
    formatter = T91_TableFormatter()
    
    # Save current pipeline state
    current_stages = pipeline.list_stages()
    
    # T91 will see pagerank_scores exists and format that
    pipeline_with_pagerank_table = formatter.execute(pipeline, {})
    print(f"Branch 2a - Format PageRank: {pipeline_with_pagerank_table.list_stages()[-1]}")
    
    # Create alternate pipeline without PageRank to show flexibility
    pipeline_alt = PipelineData()
    pipeline_alt = T01_PDFLoader().execute(pipeline_alt, {"file_path": "doc.pdf"})
    pipeline_alt = T23C_OntologyAwareExtractor().execute(pipeline_alt, {"mode": "full_extraction"})
    
    # T91 will format extraction directly since no PageRank exists
    pipeline_alt = formatter.execute(pipeline_alt, {})
    print(f"Branch 2b - Format Extraction directly: {pipeline_alt.list_stages()[-1]}")
    
    return pipeline


def example_4_data_lineage():
    """
    Demonstrate data lineage tracking.
    
    Shows how we can trace dependencies through the pipeline.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Data Lineage Tracking")
    print("=" * 60)
    
    # Build a pipeline
    pipeline = PipelineData()
    pipeline = T01_PDFLoader().execute(pipeline, {"file_path": "doc.pdf"})
    pipeline = T23C_OntologyAwareExtractor().execute(pipeline, {"mode": "full_extraction"})
    pipeline = T31_EntityBuilder().execute(pipeline, {})
    pipeline = T34_EdgeBuilder().execute(pipeline, {})
    pipeline = T68_PageRank().execute(pipeline, {})
    pipeline = T91_TableFormatter().execute(pipeline, {})
    
    # Show lineage for final table
    print("\nLineage for 'formatted_table':")
    lineage = pipeline.get_lineage("formatted_table")
    for i, stage in enumerate(lineage):
        meta = pipeline.get_stage_metadata(stage)
        indent = "  " * i
        print(f"{indent}→ {stage} (tool: {meta.tool_id})")
    
    # Show what each stage depends on
    print("\nDependency graph:")
    for stage in pipeline.list_stages():
        meta = pipeline.get_stage_metadata(stage)
        if meta.dependencies:
            print(f"  {stage} ← {meta.dependencies}")
        else:
            print(f"  {stage} ← [source]")
    
    return pipeline


def example_5_flexible_tool_behavior():
    """
    Show how the same tool behaves differently based on pipeline state.
    
    T23C and T91 adapt to what's available in the pipeline.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Flexible Tool Behavior")
    print("=" * 60)
    
    # Scenario A: T23C with text input
    pipeline_a = PipelineData()
    pipeline_a = T01_PDFLoader().execute(pipeline_a, {"file_path": "doc.pdf"})
    pipeline_a = T23C_OntologyAwareExtractor().execute(pipeline_a, {"mode": "entity_only"})
    
    print("Scenario A - T23C with text:")
    extraction_a = pipeline_a.get_stage("extraction")
    print(f"  Input: raw_text")
    print(f"  Output: {len(extraction_a['entities'])} entities, {len(extraction_a['relationships'])} relationships")
    
    # Scenario B: T23C with table input
    pipeline_b = PipelineData()
    pipeline_b = T05_CSVLoader().execute(pipeline_b, {"file_path": "data.csv"})
    pipeline_b = T23C_OntologyAwareExtractor().execute(pipeline_b, {"mode": "full_extraction"})
    
    print("\nScenario B - T23C with table:")
    extraction_b = pipeline_b.get_stage("extraction")
    print(f"  Input: table_data")
    print(f"  Output: {len(extraction_b['entities'])} entities, {len(extraction_b['relationships'])} relationships")
    
    # Scenario C: T91 formats whatever analysis is available
    pipeline_c = PipelineData()
    pipeline_c = T01_PDFLoader().execute(pipeline_c, {"file_path": "doc.pdf"})
    pipeline_c = T23C_OntologyAwareExtractor().execute(pipeline_c, {"mode": "full_extraction"})
    
    # Without PageRank
    formatter = T91_TableFormatter()
    pipeline_c1 = formatter.execute(pipeline_c, {})
    table1 = pipeline_c1.get_stage("formatted_table")
    
    print("\nScenario C1 - T91 formats extraction:")
    print(f"  Input: extraction")
    print(f"  Output: Table with {table1['row_count']} entity rows")
    
    # With PageRank
    pipeline_c = T31_EntityBuilder().execute(pipeline_c, {})
    pipeline_c = T34_EdgeBuilder().execute(pipeline_c, {})
    pipeline_c = T68_PageRank().execute(pipeline_c, {})
    pipeline_c2 = formatter.execute(pipeline_c, {})
    table2 = pipeline_c2.get_stage("formatted_table")
    
    print("\nScenario C2 - T91 formats PageRank:")
    print(f"  Input: pagerank_scores")
    print(f"  Output: Table with {table2['row_count']} score rows")
    
    return pipeline_c2


def run_all_examples():
    """Run all examples to demonstrate pipeline accumulation"""
    
    print("\n" + "#" * 60)
    print("# PIPELINE ACCUMULATION EXAMPLES")
    print("#" * 60)
    
    # Run examples
    pipelines = []
    pipelines.append(example_1_basic_pdf_to_graph())
    pipelines.append(example_2_csv_to_graph())
    pipelines.append(example_3_branching_pipeline())
    pipelines.append(example_4_data_lineage())
    pipelines.append(example_5_flexible_tool_behavior())
    
    # Summary
    print("\n" + "#" * 60)
    print("# SUMMARY")
    print("#" * 60)
    
    print("\nKey observations:")
    print("1. Data accumulates - all stages remain accessible")
    print("2. Tools can adapt to different inputs (T23C works with text OR table)")
    print("3. Tools can read from ANY previous stage, not just the last one")
    print("4. The same tool behaves differently based on pipeline context")
    print("5. Full data lineage is preserved automatically")
    print("6. No schema adapters needed - tools work with their natural formats")
    
    return pipelines


if __name__ == "__main__":
    run_all_examples()