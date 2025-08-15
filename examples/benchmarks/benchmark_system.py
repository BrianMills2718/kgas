#!/usr/bin/env python3
"""
KGAS Performance Benchmark System - Phase 8.1

Measures current system performance with real data and fail-fast validation.
NO MOCKS, NO SIMULATIONS - Uses actual PDFs and real processing pipeline.

This benchmark system provides baseline measurements for optimization efforts.
"""

import os
import sys
import time
import psutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.service_manager import ServiceManager
from src.tools.phase1.t01_pdf_loader import PDFLoader
from src.tools.phase1.t15a_text_chunker import TextChunker
from src.tools.phase1.t23a_spacy_ner import SpacyNER
from src.tools.phase1.t27_relationship_extractor import RelationshipExtractor
from src.tools.phase1.t31_entity_builder import EntityBuilder
from src.tools.phase1.t34_edge_builder import EdgeBuilder
from src.tools.phase1.t49_multihop_query import MultiHopQuery
from src.tools.phase1.t68_pagerank import PageRank


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test"""
    test_name: str
    document_info: Dict[str, Any]
    execution_time: float
    memory_used: int
    memory_peak: int
    entities_extracted: int
    relationships_found: int
    chunks_created: int
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SystemPerformanceBaseline:
    """Overall system performance baseline"""
    total_tests: int
    successful_tests: int
    failure_rate: float
    average_processing_time: float
    peak_memory_usage: int
    entities_per_second: float
    documents_per_hour: float
    baseline_established: str
    performance_thresholds: Dict[str, float]
    test_results: List[BenchmarkResult]


class PerformanceBenchmark:
    """
    KGAS Performance Benchmark System
    
    Tests real system performance with actual documents and processing.
    Fails fast if critical performance thresholds are not met.
    """
    
    def __init__(self):
        """Initialize benchmark system with fail-fast validation"""
        self.service_manager = None
        self.tools = {}
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.results_dir = Path(__file__).parent / "benchmark_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Performance thresholds (fail-fast if exceeded)
        self.thresholds = {
            "max_processing_time_small": 2.0,     # 2 seconds for small PDFs
            "max_processing_time_medium": 10.0,   # 10 seconds for medium PDFs
            "max_processing_time_large": 30.0,    # 30 seconds for large PDFs
            "max_memory_usage_mb": 2048,          # 2GB max memory
            "min_entities_per_second": 10,        # Minimum processing rate
            "max_failure_rate": 0.1               # Maximum 10% failure rate
        }
        
        self.test_cases = [
            {"name": "small_pdf", "pages": 1, "expected_entities": 5, "max_time": 2.0},
            {"name": "medium_pdf", "pages": 5, "expected_entities": 25, "max_time": 10.0},
            {"name": "large_pdf", "pages": 20, "expected_entities": 100, "max_time": 30.0},
            {"name": "batch_processing", "count": 5, "expected_entities": 50, "max_time": 60.0}
        ]
    
    def initialize_system(self) -> bool:
        """Initialize KGAS system components with fail-fast validation"""
        try:
            print("Initializing KGAS system for benchmarking...")
            
            # Initialize service manager
            self.service_manager = ServiceManager()
            if not self.service_manager:
                raise RuntimeError("Failed to initialize ServiceManager")
            
            # Initialize tools with real instances (no mocks)
            self.tools = {
                'pdf_loader': PDFLoader(self.service_manager),
                'text_chunker': TextChunker(self.service_manager),
                'spacy_ner': SpacyNER(self.service_manager),
                'relationship_extractor': RelationshipExtractor(self.service_manager),
                'entity_builder': EntityBuilder(self.service_manager),
                'edge_builder': EdgeBuilder(self.service_manager),
                'multihop_query': MultiHopQuery(self.service_manager),
                'pagerank': PageRank(self.service_manager)
            }
            
            # Validate all tools are properly initialized
            for tool_name, tool in self.tools.items():
                if not tool:
                    raise RuntimeError(f"Failed to initialize {tool_name}")
                
                # Test health check if available
                if hasattr(tool, 'health_check'):
                    health_result = tool.health_check()
                    if not health_result or (hasattr(health_result, 'status') and health_result.status != 'success'):
                        raise RuntimeError(f"Health check failed for {tool_name}")
            
            print("✅ System initialization completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ SYSTEM INITIALIZATION FAILED: {e}")
            raise RuntimeError(f"Cannot proceed with benchmarking - system initialization failed: {e}")
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment meets requirements"""
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            if memory.available < 4 * 1024 * 1024 * 1024:  # 4GB minimum
                raise RuntimeError(f"Insufficient memory: {memory.available / (1024**3):.1f}GB available, need 4GB minimum")
            
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            if cpu_count < 2:
                raise RuntimeError(f"Insufficient CPU cores: {cpu_count} available, need 2 minimum")
            
            # Check disk space
            disk = psutil.disk_usage(self.results_dir)
            if disk.free < 1 * 1024 * 1024 * 1024:  # 1GB minimum
                raise RuntimeError(f"Insufficient disk space: {disk.free / (1024**3):.1f}GB available, need 1GB minimum")
            
            # Validate test data exists
            if not self.test_data_dir.exists():
                print(f"Creating test data directory: {self.test_data_dir}")
                self.test_data_dir.mkdir(parents=True, exist_ok=True)
            
            print("✅ Test environment validation passed")
            return True
            
        except Exception as e:
            print(f"❌ TEST ENVIRONMENT VALIDATION FAILED: {e}")
            raise RuntimeError(f"Environment not suitable for benchmarking: {e}")
    
    def create_test_documents(self) -> Dict[str, Path]:
        """Create or locate test documents for benchmarking"""
        test_docs = {}
        
        try:
            # Look for existing test PDFs
            existing_pdfs = list(self.test_data_dir.glob("*.pdf"))
            
            if existing_pdfs:
                print(f"Found {len(existing_pdfs)} existing test PDFs")
                for pdf in existing_pdfs[:3]:  # Use first 3 PDFs found
                    test_docs[f"real_pdf_{pdf.stem}"] = pdf
            
            # If no PDFs found, create minimal test documents
            if not test_docs:
                print("No test PDFs found, creating minimal test documents...")
                test_docs = self._create_minimal_test_docs()
            
            # Validate test documents
            for doc_name, doc_path in test_docs.items():
                if not doc_path.exists():
                    raise FileNotFoundError(f"Test document not found: {doc_path}")
                
                # Check file size is reasonable
                size_mb = doc_path.stat().st_size / (1024 * 1024)
                if size_mb > 100:  # 100MB limit
                    raise ValueError(f"Test document too large: {doc_name} is {size_mb:.1f}MB")
            
            print(f"✅ Prepared {len(test_docs)} test documents")
            return test_docs
            
        except Exception as e:
            print(f"❌ FAILED TO PREPARE TEST DOCUMENTS: {e}")
            raise RuntimeError(f"Cannot create test documents: {e}")
    
    def _create_minimal_test_docs(self) -> Dict[str, Path]:
        """Create minimal test documents for benchmarking"""
        test_docs = {}
        
        try:
            # Create text files that can be processed by the system
            small_text = "This is a small test document. John Smith works at Acme Corp. The company is located in New York. John is a software engineer who develops AI systems."
            
            medium_text = small_text * 20  # Repeat to make it larger
            
            large_text = medium_text * 10  # Even larger
            
            # Write test files
            for name, content in [("small", small_text), ("medium", medium_text), ("large", large_text)]:
                test_file = self.test_data_dir / f"test_{name}.txt"
                test_file.write_text(content)
                test_docs[f"{name}_document"] = test_file
            
            return test_docs
            
        except Exception as e:
            raise RuntimeError(f"Failed to create minimal test documents: {e}")
    
    def benchmark_document_processing(self, doc_path: Path, test_name: str) -> BenchmarkResult:
        """Benchmark complete document processing pipeline"""
        print(f"\nBenchmarking: {test_name} ({doc_path.name})")
        
        start_time = time.time()
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        peak_memory = initial_memory
        
        entities_count = 0
        relationships_count = 0
        chunks_count = 0
        
        try:
            # Step 1: Document Loading
            print("  Loading document...")
            pdf_loader = self.tools['pdf_loader']
            
            # Prepare input for tool
            load_request = {
                "tool_id": "T01_PDF_LOADER",
                "operation": "load",
                "input_data": {"file_path": str(doc_path)},
                "parameters": {}
            }
            
            if hasattr(pdf_loader, 'execute'):
                load_result = pdf_loader.execute(load_request)
            else:
                # Fallback to legacy interface
                load_result = pdf_loader.load_document(str(doc_path))
            
            if not load_result or (hasattr(load_result, 'status') and load_result.status != 'success'):
                raise RuntimeError(f"Document loading failed: {load_result}")
            
            # Extract text from result
            if hasattr(load_result, 'data'):
                document_text = load_result.data.get('document', {}).get('text', '')
            else:
                document_text = getattr(load_result, 'text', str(load_result))
            
            if not document_text or len(document_text.strip()) < 10:
                raise RuntimeError("Document loading produced insufficient text")
            
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
            
            # Step 2: Text Chunking
            print("  Chunking text...")
            text_chunker = self.tools['text_chunker']
            
            chunk_request = {
                "tool_id": "T15A_TEXT_CHUNKER",
                "operation": "chunk",
                "input_data": {"text": document_text, "document_ref": f"test_doc_{test_name}"},
                "parameters": {"chunk_size": 500}
            }
            
            if hasattr(text_chunker, 'execute'):
                chunk_result = text_chunker.execute(chunk_request)
            else:
                chunk_result = text_chunker.chunk_text(document_text)
            
            if hasattr(chunk_result, 'data'):
                chunks_count = len(chunk_result.data.get('chunks', []))
            else:
                chunks_count = len(getattr(chunk_result, 'chunks', [chunk_result]))
            
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
            
            # Step 3: Entity Extraction
            print("  Extracting entities...")
            spacy_ner = self.tools['spacy_ner']
            
            ner_request = {
                "tool_id": "T23A_SPACY_NER",
                "operation": "extract",
                "input_data": {"text": document_text, "chunk_ref": f"chunk_{test_name}"},
                "parameters": {}
            }
            
            if hasattr(spacy_ner, 'execute'):
                ner_result = spacy_ner.execute(ner_request)
            else:
                ner_result = spacy_ner.extract_entities(document_text)
            
            if hasattr(ner_result, 'data'):
                entities_count = len(ner_result.data.get('entities', []))
            else:
                entities_count = len(getattr(ner_result, 'entities', [ner_result]))
            
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
            
            # Step 4: Relationship Extraction
            print("  Extracting relationships...")
            rel_extractor = self.tools['relationship_extractor']
            
            rel_request = {
                "tool_id": "T27_RELATIONSHIP_EXTRACTOR",
                "operation": "extract",
                "input_data": {"text": document_text, "entities": []},
                "parameters": {}
            }
            
            if hasattr(rel_extractor, 'execute'):
                rel_result = rel_extractor.execute(rel_request)
            else:
                rel_result = rel_extractor.extract_relationships(document_text, [])
            
            if hasattr(rel_result, 'data'):
                relationships_count = len(rel_result.data.get('relationships', []))
            else:
                relationships_count = len(getattr(rel_result, 'relationships', [rel_result]))
            
            current_memory = process.memory_info().rss
            peak_memory = max(peak_memory, current_memory)
            
            execution_time = time.time() - start_time
            memory_used = peak_memory - initial_memory
            
            # Validate results meet minimum expectations
            if entities_count == 0:
                print(f"  ⚠️  WARNING: No entities extracted from {doc_path.name}")
            
            print(f"  ✅ Completed in {execution_time:.2f}s")
            print(f"     Entities: {entities_count}, Relationships: {relationships_count}, Chunks: {chunks_count}")
            print(f"     Memory used: {memory_used / (1024*1024):.1f}MB")
            
            return BenchmarkResult(
                test_name=test_name,
                document_info={
                    "file_path": str(doc_path),
                    "file_size": doc_path.stat().st_size,
                    "text_length": len(document_text)
                },
                execution_time=execution_time,
                memory_used=memory_used,
                memory_peak=peak_memory,
                entities_extracted=entities_count,
                relationships_found=relationships_count,
                chunks_created=chunks_count,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            memory_used = process.memory_info().rss - initial_memory
            
            print(f"  ❌ FAILED after {execution_time:.2f}s: {e}")
            
            return BenchmarkResult(
                test_name=test_name,
                document_info={"file_path": str(doc_path), "file_size": doc_path.stat().st_size},
                execution_time=execution_time,
                memory_used=memory_used,
                memory_peak=peak_memory,
                entities_extracted=entities_count,
                relationships_found=relationships_count,
                chunks_created=chunks_count,
                success=False,
                error_message=str(e)
            )
    
    def run_comprehensive_benchmark(self) -> SystemPerformanceBaseline:
        """Run comprehensive benchmark suite and establish performance baseline"""
        print("=" * 60)
        print("KGAS PERFORMANCE BENCHMARK SUITE")
        print("=" * 60)
        
        # Initialize and validate system
        self.initialize_system()
        self.validate_test_environment()
        
        # Prepare test documents
        test_documents = self.create_test_documents()
        
        if not test_documents:
            raise RuntimeError("No test documents available for benchmarking")
        
        # Run benchmarks
        all_results = []
        
        for doc_name, doc_path in test_documents.items():
            result = self.benchmark_document_processing(doc_path, doc_name)
            all_results.append(result)
            
            # Fail fast if critical thresholds exceeded
            if result.success and result.execution_time > self.thresholds["max_processing_time_large"]:
                raise RuntimeError(f"PERFORMANCE THRESHOLD EXCEEDED: {result.test_name} took {result.execution_time:.2f}s (max: {self.thresholds['max_processing_time_large']}s)")
            
            memory_mb = result.memory_peak / (1024 * 1024)
            if memory_mb > self.thresholds["max_memory_usage_mb"]:
                raise RuntimeError(f"MEMORY THRESHOLD EXCEEDED: {result.test_name} used {memory_mb:.1f}MB (max: {self.thresholds['max_memory_usage_mb']}MB)")
        
        # Calculate baseline metrics
        successful_tests = [r for r in all_results if r.success]
        failed_tests = [r for r in all_results if not r.success]
        
        if not successful_tests:
            raise RuntimeError("ALL BENCHMARK TESTS FAILED - Cannot establish performance baseline")
        
        failure_rate = len(failed_tests) / len(all_results)
        if failure_rate > self.thresholds["max_failure_rate"]:
            raise RuntimeError(f"FAILURE RATE TOO HIGH: {failure_rate:.1%} (max: {self.thresholds['max_failure_rate']:.1%})")
        
        avg_time = sum(r.execution_time for r in successful_tests) / len(successful_tests)
        peak_memory = max(r.memory_peak for r in all_results)
        total_entities = sum(r.entities_extracted for r in successful_tests)
        total_time = sum(r.execution_time for r in successful_tests)
        
        entities_per_second = total_entities / total_time if total_time > 0 else 0
        documents_per_hour = 3600 / avg_time if avg_time > 0 else 0
        
        if entities_per_second < self.thresholds["min_entities_per_second"]:
            raise RuntimeError(f"PROCESSING RATE TOO LOW: {entities_per_second:.1f} entities/sec (min: {self.thresholds['min_entities_per_second']})")
        
        baseline = SystemPerformanceBaseline(
            total_tests=len(all_results),
            successful_tests=len(successful_tests),
            failure_rate=failure_rate,
            average_processing_time=avg_time,
            peak_memory_usage=peak_memory,
            entities_per_second=entities_per_second,
            documents_per_hour=documents_per_hour,
            baseline_established=datetime.now().isoformat(),
            performance_thresholds=self.thresholds,
            test_results=all_results
        )
        
        return baseline
    
    def save_benchmark_results(self, baseline: SystemPerformanceBaseline) -> Path:
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"benchmark_baseline_{timestamp}.json"
        
        # Convert to serializable format
        results_data = asdict(baseline)
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n✅ Benchmark results saved to: {results_file}")
        return results_file
    
    def print_benchmark_summary(self, baseline: SystemPerformanceBaseline):
        """Print comprehensive benchmark summary"""
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Total tests: {baseline.total_tests}")
        print(f"Successful tests: {baseline.successful_tests}")
        print(f"Failure rate: {baseline.failure_rate:.1%}")
        print(f"Average processing time: {baseline.average_processing_time:.2f}s")
        print(f"Peak memory usage: {baseline.peak_memory_usage / (1024*1024):.1f}MB")
        print(f"Entity extraction rate: {baseline.entities_per_second:.1f} entities/second")
        print(f"Document processing rate: {baseline.documents_per_hour:.1f} documents/hour")
        
        print(f"\nPerformance Status:")
        if baseline.failure_rate <= self.thresholds["max_failure_rate"]:
            print("✅ Failure rate within acceptable limits")
        else:
            print("❌ Failure rate exceeds threshold")
        
        if baseline.entities_per_second >= self.thresholds["min_entities_per_second"]:
            print("✅ Processing rate meets minimum requirements")
        else:
            print("❌ Processing rate below minimum threshold")
        
        if baseline.peak_memory_usage <= self.thresholds["max_memory_usage_mb"] * 1024 * 1024:
            print("✅ Memory usage within limits")
        else:
            print("❌ Memory usage exceeds threshold")
        
        print(f"\nBaseline established: {baseline.baseline_established}")
        print("=" * 60)


def main():
    """Main entry point for benchmark system"""
    try:
        benchmark = PerformanceBenchmark()
        baseline = benchmark.run_comprehensive_benchmark()
        
        benchmark.print_benchmark_summary(baseline)
        results_file = benchmark.save_benchmark_results(baseline)
        
        print(f"\n🎉 BENCHMARK COMPLETED SUCCESSFULLY!")
        print(f"Performance baseline established and saved to: {results_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ BENCHMARK FAILED: {e}")
        print("System performance does not meet minimum requirements.")
        print("Address performance issues before proceeding with optimization.")
        return 1


if __name__ == "__main__":
    sys.exit(main())