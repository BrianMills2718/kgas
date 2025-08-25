"""
Stress tests to find where pipeline accumulation breaks down.

These tests explore edge cases and potential failure modes.
"""

import json
import sys
from typing import List, Dict, Any
from dataclasses import dataclass
from pipeline_data import PipelineData
from example_tools import (
    T01_PDFLoader, T23C_OntologyAwareExtractor, 
    T31_EntityBuilder, T34_EdgeBuilder,
    T68_PageRank, T91_TableFormatter
)


def stress_test_1_memory_accumulation():
    """
    PROBLEM: Pipeline keeps accumulating data - what about memory?
    
    Each stage adds data but nothing gets removed.
    What happens with 1000 large documents?
    """
    print("\n" + "="*60)
    print("STRESS TEST 1: Memory Accumulation")
    print("="*60)
    
    pipeline = PipelineData()
    
    # Simulate processing many documents
    for i in range(100):
        # Each stage adds ~1MB of data
        large_text = "x" * 1_000_000  # 1MB string
        pipeline.add_stage(f"document_{i}", large_text, tool_id=f"loader_{i}")
        
        # Check memory usage
        if i % 10 == 0:
            total_size = sum(
                pipeline.get_stage_metadata(stage).size_bytes 
                for stage in pipeline.list_stages()
            )
            print(f"After {i} documents: {total_size / 1_000_000:.1f} MB")
    
    print(f"Final stages count: {len(pipeline.list_stages())}")
    print("\n🚨 PROBLEM: Memory grows linearly with documents!")
    print("📝 NEED: Pagination, streaming, or cleanup strategies")
    
    return pipeline


def stress_test_2_stage_name_collisions():
    """
    PROBLEM: What if we want to run the same tool multiple times?
    
    Example: Extract → Review → Extract again → Refine
    Both extractions want to create "extraction" stage.
    """
    print("\n" + "="*60)
    print("STRESS TEST 2: Stage Name Collisions")
    print("="*60)
    
    pipeline = PipelineData()
    
    # First extraction
    pipeline = T01_PDFLoader().execute(pipeline, {"file_path": "doc.pdf"})
    pipeline = T23C_OntologyAwareExtractor().execute(pipeline, {"mode": "entity_only"})
    
    print(f"After first extraction: {pipeline.list_stages()}")
    
    # Try to extract again with different params
    try:
        # This will fail - "extraction" already exists!
        pipeline = T23C_OntologyAwareExtractor().execute(pipeline, {"mode": "full_extraction"})
    except ValueError as e:
        print(f"\n🚨 ERROR: {e}")
    
    print("\n🚨 PROBLEM: Can't run same tool twice!")
    print("📝 NEED: Dynamic stage naming or versioning")
    
    # Potential solution: Tool instances with IDs
    class ExtractorWithID(T23C_OntologyAwareExtractor):
        def __init__(self, instance_id: str):
            super().__init__()
            self.instance_id = instance_id
            self.output_stage = f"extraction_{instance_id}"
    
    # Now we can run multiple times
    pipeline2 = PipelineData()
    pipeline2 = T01_PDFLoader().execute(pipeline2, {"file_path": "doc.pdf"})
    
    extractor1 = ExtractorWithID("initial")
    pipeline2.add_stage("extraction_initial", {"entities": ["A", "B"]}, tool_id="T23C_1")
    
    extractor2 = ExtractorWithID("refined")  
    pipeline2.add_stage("extraction_refined", {"entities": ["A", "B", "C"]}, tool_id="T23C_2")
    
    print(f"\nWith IDs: {pipeline2.list_stages()}")
    print("✅ WORKAROUND: Tool instances with unique IDs")


def stress_test_3_parameter_flow():
    """
    PROBLEM: How do parameters affect pipeline execution?
    
    If T23C runs with mode="entity_only", T34 can't build edges.
    How do we handle parameter-dependent compatibility?
    """
    print("\n" + "="*60)
    print("STRESS TEST 3: Parameter-Dependent Compatibility")
    print("="*60)
    
    pipeline = PipelineData()
    pipeline = T01_PDFLoader().execute(pipeline, {"file_path": "doc.pdf"})
    
    # Extract with entity_only mode
    pipeline = T23C_OntologyAwareExtractor().execute(pipeline, {"mode": "entity_only"})
    extraction = pipeline.get_stage("extraction")
    print(f"Entity-only extraction: {len(extraction['relationships'])} relationships")
    
    # T31 works fine with just entities
    pipeline = T31_EntityBuilder().execute(pipeline, {})
    
    # But T34 needs relationships!
    try:
        pipeline = T34_EdgeBuilder().execute(pipeline, {})
        graph = pipeline.get_stage("graph_structure")
        print(f"Graph edges: {graph['edge_count']}")  # Will be 0!
    except Exception as e:
        print(f"🚨 ERROR: {e}")
    
    print("\n🚨 PROBLEM: Parameter choices affect downstream compatibility")
    print("📝 NEED: Parameter validation in planning phase")


def stress_test_4_pipeline_composition():
    """
    PROBLEM: What if we want to combine multiple pipelines?
    
    Pipeline1: PDF → Extract → Graph1
    Pipeline2: CSV → Extract → Graph2
    Pipeline3: Merge(Graph1, Graph2) → Analysis
    """
    print("\n" + "="*60)
    print("STRESS TEST 4: Cross-Pipeline References")
    print("="*60)
    
    # Pipeline 1: PDF processing
    pipeline1 = PipelineData()
    pipeline1 = T01_PDFLoader().execute(pipeline1, {"file_path": "doc1.pdf"})
    pipeline1 = T23C_OntologyAwareExtractor().execute(pipeline1, {"mode": "full_extraction"})
    
    # Pipeline 2: CSV processing
    from example_tools import T05_CSVLoader
    pipeline2 = PipelineData()
    pipeline2 = T05_CSVLoader().execute(pipeline2, {"file_path": "data.csv"})
    pipeline2 = T23C_OntologyAwareExtractor().execute(pipeline2, {"mode": "full_extraction"})
    
    # How do we merge?
    print("Pipeline 1 stages:", pipeline1.list_stages())
    print("Pipeline 2 stages:", pipeline2.list_stages())
    
    # Option 1: Manual merge
    merged = PipelineData()
    merged.add_stage("source1_extraction", 
                    pipeline1.get_stage("extraction"), 
                    tool_id="MERGE")
    merged.add_stage("source2_extraction", 
                    pipeline2.get_stage("extraction"),
                    tool_id="MERGE")
    
    # But now tools expecting "extraction" won't find it!
    print("\n🚨 PROBLEM: No standard way to merge pipelines")
    print("📝 NEED: Pipeline composition operators")


def stress_test_5_error_recovery():
    """
    PROBLEM: What happens when a tool fails mid-pipeline?
    
    Can we retry? Skip? Use defaults?
    """
    print("\n" + "="*60)
    print("STRESS TEST 5: Error Recovery")
    print("="*60)
    
    # Create a failing tool
    class FailingTool:
        def __init__(self, fail_probability=0.5):
            self.fail_probability = fail_probability
            self.tool_id = "FAILING_TOOL"
            
        def execute(self, pipeline, params):
            import random
            if random.random() < self.fail_probability:
                raise RuntimeError("Tool randomly failed!")
            
            pipeline.add_stage("risky_analysis", {"result": "success"}, tool_id=self.tool_id)
            return pipeline
    
    pipeline = PipelineData()
    pipeline = T01_PDFLoader().execute(pipeline, {"file_path": "doc.pdf"})
    
    failing_tool = FailingTool(fail_probability=0.9)
    
    # Try up to 3 times
    max_retries = 3
    for attempt in range(max_retries):
        try:
            pipeline = failing_tool.execute(pipeline, {})
            print(f"✅ Succeeded on attempt {attempt + 1}")
            break
        except RuntimeError as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("\n🚨 PROBLEM: No built-in retry mechanism")
                print("📝 NEED: Retry policies, fallback strategies")


def stress_test_6_data_validation():
    """
    PROBLEM: How do we ensure data integrity between stages?
    
    What if a tool produces malformed data?
    """
    print("\n" + "="*60)
    print("STRESS TEST 6: Data Validation")
    print("="*60)
    
    # Create a tool that produces bad data
    class BadDataTool:
        def execute(self, pipeline, params):
            # Produces wrong structure - T31 expects 'entities' list
            bad_extraction = {
                "entities": "NOT A LIST!",  # Wrong type!
                "relationships": None  # Should be list!
            }
            pipeline.add_stage("extraction", bad_extraction, tool_id="BAD_TOOL")
            return pipeline
    
    pipeline = PipelineData()
    bad_tool = BadDataTool()
    pipeline = bad_tool.execute(pipeline, {})
    
    # T31 will crash with bad data
    try:
        pipeline = T31_EntityBuilder().execute(pipeline, {})
    except Exception as e:
        print(f"🚨 ERROR: {e}")
    
    print("\n🚨 PROBLEM: No data validation between stages")
    print("📝 NEED: Schema validation, type checking")


def stress_test_7_large_scale_processing():
    """
    PROBLEM: How do we handle 1000 documents?
    
    Create 1000 pipelines? One pipeline with 1000 stages?
    """
    print("\n" + "="*60)
    print("STRESS TEST 7: Large-Scale Processing")
    print("="*60)
    
    # Option 1: One pipeline, many documents
    pipeline_single = PipelineData()
    
    for i in range(10):  # Would be 1000 in reality
        stage_name = f"doc_{i}_text"
        pipeline_single.add_stage(stage_name, f"Text from doc {i}", tool_id="BATCH")
    
    print(f"Option 1 - Single pipeline: {len(pipeline_single.list_stages())} stages")
    
    # Option 2: Many pipelines
    pipelines = []
    for i in range(10):
        p = PipelineData()
        p.add_stage("text", f"Text from doc {i}", tool_id="INDIVIDUAL")
        pipelines.append(p)
    
    print(f"Option 2 - Many pipelines: {len(pipelines)} pipelines")
    
    # Option 3: Batched pipeline
    class BatchedPipeline:
        def __init__(self, batch_size=100):
            self.batch_size = batch_size
            self.batches = []
            
        def process_documents(self, docs: List[str]):
            for i in range(0, len(docs), self.batch_size):
                batch = docs[i:i+self.batch_size]
                pipeline = PipelineData()
                pipeline.add_stage("batch_text", batch, tool_id="BATCH")
                # Process batch...
                self.batches.append(pipeline)
    
    print("\n🚨 PROBLEM: No clear pattern for large-scale processing")
    print("📝 NEED: Batch processing strategy, memory management")


def stress_test_8_tool_versioning():
    """
    PROBLEM: What happens when tool output format changes?
    
    T23C v1: {"entities": [...]}
    T23C v2: {"extracted_entities": [...]}  # Field renamed!
    """
    print("\n" + "="*60)
    print("STRESS TEST 8: Tool Version Evolution")
    print("="*60)
    
    # Simulate old version
    class T23C_v1:
        def execute(self, pipeline, params):
            pipeline.add_stage("extraction", {
                "entities": [{"id": "e1", "text": "John"}]
            }, tool_id="T23C_v1")
            return pipeline
    
    # Simulate new version
    class T23C_v2:
        def execute(self, pipeline, params):
            pipeline.add_stage("extraction", {
                "extracted_entities": [{"id": "e1", "label": "John"}],  # Different field names!
                "version": "2.0"
            }, tool_id="T23C_v2")
            return pipeline
    
    # Old pipeline
    pipeline_old = PipelineData()
    pipeline_old = T23C_v1().execute(pipeline_old, {})
    
    # New pipeline  
    pipeline_new = PipelineData()
    pipeline_new = T23C_v2().execute(pipeline_new, {})
    
    # T31 expects "entities" field
    try:
        # Works with v1
        T31_EntityBuilder().execute(pipeline_old, {})
        print("✅ T31 works with v1")
    except:
        print("❌ T31 fails with v1")
    
    try:
        # Fails with v2!
        T31_EntityBuilder().execute(pipeline_new, {})
        print("✅ T31 works with v2")
    except KeyError:
        print("❌ T31 fails with v2 - field name changed!")
    
    print("\n🚨 PROBLEM: Tool evolution breaks downstream tools")
    print("📝 NEED: Version compatibility layer")


def stress_test_9_conditional_execution():
    """
    PROBLEM: How do we handle conditional logic in linear pipelines?
    
    If confidence < 0.5, use different extraction.
    If entity_count > 100, use sampling.
    """
    print("\n" + "="*60)
    print("STRESS TEST 9: Conditional Execution")
    print("="*60)
    
    pipeline = PipelineData()
    pipeline.add_stage("extraction", {
        "entities": ["A", "B"],
        "confidence": 0.3  # Low confidence!
    }, tool_id="T23C")
    
    extraction = pipeline.get_stage("extraction")
    
    # Need conditional logic
    if extraction["confidence"] < 0.5:
        print("Low confidence - need aggressive re-extraction")
        # But how do we tell the pipeline to use different tools?
        # We can't modify the pipeline execution flow!
    
    print("\n🚨 PROBLEM: No way to express conditional logic")
    print("📝 NEED: Conditional execution support or wrapper pattern")


def stress_test_10_stage_dependencies():
    """
    PROBLEM: How do we know which stages a tool actually used?
    
    T91 can format extraction OR pagerank, but how do we know which?
    """
    print("\n" + "="*60)
    print("STRESS TEST 10: Ambiguous Dependencies")
    print("="*60)
    
    # Scenario 1: T91 formats extraction
    pipeline1 = PipelineData()
    pipeline1.add_stage("extraction", {"entities": ["A", "B"]}, tool_id="T23C")
    formatter = T91_TableFormatter()
    pipeline1 = formatter.execute(pipeline1, {})
    
    # What did T91 actually use?
    meta = pipeline1.get_stage_metadata("formatted_table")
    print(f"T91 used: {meta.dependencies}")
    
    # Scenario 2: T91 formats pagerank
    pipeline2 = PipelineData()
    pipeline2.add_stage("extraction", {"entities": ["A", "B"]}, tool_id="T23C")
    pipeline2.add_stage("pagerank_scores", {"scores": {"A": 0.5}}, tool_id="T68")
    formatter2 = T91_TableFormatter()
    pipeline2 = formatter2.execute(pipeline2, {})
    
    # Dependencies might not reflect actual usage!
    print("\n🚨 PROBLEM: Tools might not accurately report dependencies")
    print("📝 NEED: Runtime dependency tracking")


def run_all_stress_tests():
    """Run all stress tests to find breaking points"""
    
    print("\n" + "#"*60)
    print("# PIPELINE ACCUMULATION STRESS TESTS")
    print("#"*60)
    
    stress_test_1_memory_accumulation()
    stress_test_2_stage_name_collisions()
    stress_test_3_parameter_flow()
    stress_test_4_pipeline_composition()
    stress_test_5_error_recovery()
    stress_test_6_data_validation()
    stress_test_7_large_scale_processing()
    stress_test_8_tool_versioning()
    stress_test_9_conditional_execution()
    stress_test_10_stage_dependencies()
    
    print("\n" + "#"*60)
    print("# CRITICAL ISSUES FOUND")
    print("#"*60)
    
    print("""
    1. MEMORY: Unbounded accumulation (scales with documents)
    2. REUSE: Can't run same tool twice (name collisions)
    3. PARAMS: Parameter choices affect downstream compatibility
    4. MERGE: No way to combine pipelines
    5. ERRORS: No retry/recovery mechanism
    6. VALIDATION: No data integrity checks
    7. SCALE: Unclear how to handle 1000s of documents
    8. VERSIONING: Tool evolution breaks pipelines
    9. CONDITIONALS: No conditional execution
    10. DEPENDENCIES: Ambiguous dependency tracking
    """)
    
    print("📝 These issues need solutions before production use!")


if __name__ == "__main__":
    run_all_stress_tests()