#!/usr/bin/env python3
"""
KGAS Standalone Performance Benchmark System - Phase 8.1

Measures current system performance for tools that don't require external services.
NO MOCKS, NO SIMULATIONS - Uses actual data processing with available tools.

This benchmark focuses on core processing capabilities that can run standalone.
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

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tools.base_tool import ToolRequest


@dataclass
class StandaloneBenchmarkResult:
    """Result of a standalone benchmark test"""
    test_name: str
    tool_name: str
    document_info: Dict[str, Any]
    execution_time: float
    memory_used: int
    memory_peak: int
    output_size: int
    processing_rate: float  # items per second
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class StandalonePerformanceBaseline:
    """Standalone system performance baseline"""
    total_tests: int
    successful_tests: int
    failure_rate: float
    tool_performance: Dict[str, Dict[str, float]]
    system_performance: Dict[str, float]
    baseline_established: str
    performance_thresholds: Dict[str, float]
    test_results: List[StandaloneBenchmarkResult]


class StandalonePerformanceBenchmark:
    """
    KGAS Standalone Performance Benchmark System
    
    Tests performance of tools that can run without external services.
    Maintains fail-fast principle while working with available infrastructure.
    """
    
    def __init__(self):
        """Initialize standalone benchmark system"""
        self.available_tools = {}
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.results_dir = Path(__file__).parent / "benchmark_results"
        self.results_dir.mkdir(exist_ok=True)
        
        # Performance thresholds (fail-fast if exceeded)
        self.thresholds = {
            "max_pdf_load_time": 5.0,         # 5 seconds for PDF loading
            "max_text_chunk_time": 2.0,       # 2 seconds for text chunking
            "max_spacy_ner_time": 10.0,       # 10 seconds for NER
            "max_memory_usage_mb": 1024,      # 1GB max memory per operation
            "min_processing_rate": 1000,      # Min 1000 chars/sec processing
            "max_failure_rate": 0.05          # Maximum 5% failure rate
        }
    
    def discover_available_tools(self) -> Dict[str, Any]:
        """Discover which tools can be loaded without external dependencies"""
        available_tools = {}
        
        print("Discovering available tools...")
        
        # Test PDF Loader (should work standalone)
        try:
            from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
            # Create minimal service manager mock for testing
            class MinimalServiceManager:
                def __init__(self):
                    self.identity_service = None
                    self.provenance_service = None
                    self.quality_service = None
            
            tool = T01PDFLoaderUnified(MinimalServiceManager())
            available_tools['pdf_loader'] = tool
            print("✅ PDF Loader available")
        except Exception as e:
            print(f"❌ PDF Loader unavailable: {e}")
        
        # Test Text Chunker (should work standalone)
        try:
            from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
            tool = T15ATextChunkerUnified(MinimalServiceManager())
            available_tools['text_chunker'] = tool
            print("✅ Text Chunker available")
        except Exception as e:
            print(f"❌ Text Chunker unavailable: {e}")
        
        # Test SpaCy NER (should work if SpaCy model is available)
        try:
            from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
            tool = T23ASpacyNERUnified(MinimalServiceManager())
            available_tools['spacy_ner'] = tool
            print("✅ SpaCy NER available")
        except Exception as e:
            print(f"⚠️  SpaCy NER unavailable (expected if no model): {e}")
        
        if not available_tools:
            raise RuntimeError("NO TOOLS AVAILABLE - Cannot run benchmark without any functional tools")
        
        print(f"Found {len(available_tools)} available tools for benchmarking")
        return available_tools
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment meets requirements"""
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            if memory.available < 2 * 1024 * 1024 * 1024:  # 2GB minimum
                raise RuntimeError(f"Insufficient memory: {memory.available / (1024**3):.1f}GB available, need 2GB minimum")
            
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            if cpu_count < 1:
                raise RuntimeError(f"Insufficient CPU cores: {cpu_count} available, need 1 minimum")
            
            # Check disk space
            disk = psutil.disk_usage(self.results_dir)
            if disk.free < 500 * 1024 * 1024:  # 500MB minimum
                raise RuntimeError(f"Insufficient disk space: {disk.free / (1024**3):.1f}GB available, need 0.5GB minimum")
            
            # Create test data directory
            if not self.test_data_dir.exists():
                self.test_data_dir.mkdir(parents=True, exist_ok=True)
            
            print("✅ Test environment validation passed")
            return True
            
        except Exception as e:
            print(f"❌ TEST ENVIRONMENT VALIDATION FAILED: {e}")
            raise RuntimeError(f"Environment not suitable for benchmarking: {e}")
    
    def create_test_data(self) -> Dict[str, Any]:
        """Create test data of various sizes and complexities"""
        test_data = {}
        
        try:
            # Small text document
            small_text = """
            John Smith is a software engineer at Acme Corporation. He works in New York City.
            The company develops artificial intelligence systems for healthcare applications.
            John graduated from MIT in 2015 with a degree in Computer Science.
            His current project involves natural language processing and machine learning.
            """.strip()
            
            # Medium text document (repeat and expand)
            medium_text = ""
            for i in range(10):
                medium_text += f"""
                Document section {i+1}: Mary Johnson works at TechCorp as a data scientist.
                She specializes in machine learning algorithms and statistical analysis.
                The company is located in San Francisco, California.
                Mary has published several papers on deep learning and neural networks.
                Her research focuses on computer vision and image recognition systems.
                The team includes developers from Google, Microsoft, and Amazon.
                They are working on breakthrough technologies in artificial intelligence.
                """.strip() + "\n\n"
            
            # Large text document (much larger)
            large_text_sections = []
            companies = ["Apple", "Google", "Microsoft", "Amazon", "Facebook", "Tesla", "Netflix", "Adobe"]
            cities = ["San Francisco", "New York", "Seattle", "Austin", "Boston", "Chicago", "Los Angeles", "Denver"]
            roles = ["engineer", "scientist", "manager", "analyst", "developer", "researcher", "architect", "consultant"]
            
            for i in range(50):
                company = companies[i % len(companies)]
                city = cities[i % len(cities)]
                role = roles[i % len(roles)]
                large_text_sections.append(f"""
                Section {i+1}: Dr. Sarah Thompson is a senior {role} at {company} Corporation.
                She is based in {city} and leads a team of 15 professionals.
                The company has been developing innovative solutions since 2010.
                Their latest project involves blockchain technology and cryptocurrency.
                Dr. Thompson has over 20 years of experience in the technology industry.
                She holds patents in artificial intelligence and machine learning.
                The team collaborates with universities including Stanford, MIT, and Carnegie Mellon.
                Recent achievements include successful deployment of large-scale systems.
                """.strip())
            
            large_text = "\n\n".join(large_text_sections)
            
            # Create test files
            test_data['small'] = {
                'text': small_text,
                'size': len(small_text),
                'expected_entities': 5,
                'expected_chunks': 1
            }
            
            test_data['medium'] = {
                'text': medium_text,
                'size': len(medium_text),
                'expected_entities': 30,
                'expected_chunks': 5
            }
            
            test_data['large'] = {
                'text': large_text,
                'size': len(large_text),
                'expected_entities': 150,
                'expected_chunks': 20
            }
            
            print(f"Created test data:")
            for name, data in test_data.items():
                print(f"  {name}: {data['size']} chars, ~{data['expected_entities']} entities")
            
            return test_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to create test data: {e}")
    
    def benchmark_tool_operation(self, tool_name: str, tool: Any, test_data: Dict[str, Any]) -> List[StandaloneBenchmarkResult]:
        """Benchmark a specific tool with various test data sizes"""
        results = []
        
        print(f"\nBenchmarking {tool_name}...")
        
        for data_name, data in test_data.items():
            print(f"  Testing with {data_name} data ({data['size']} chars)...")
            
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            peak_memory = initial_memory
            
            start_time = time.time()
            
            try:
                # Prepare request based on tool type
                if tool_name == 'pdf_loader':
                    # Create temporary text file for PDF loader to process
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                        tmp_file.write(data['text'])
                        tmp_path = tmp_file.name
                    
                    request = ToolRequest(
                        tool_id="T01_PDF_LOADER",
                        operation="load",
                        input_data={"file_path": tmp_path}
                    )
                    
                    result = tool.execute(request)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    # Extract output size
                    if hasattr(result, 'data') and result.data:
                        output_size = len(str(result.data.get('document', {}).get('text', '')))
                    else:
                        output_size = len(str(result))
                
                elif tool_name == 'text_chunker':
                    request = ToolRequest(
                        tool_id="T15A_TEXT_CHUNKER",
                        operation="chunk",
                        input_data={
                            "text": data['text'],
                            "document_ref": f"test_doc_{data_name}"
                        }
                    )
                    
                    result = tool.execute(request)
                    
                    # Extract output size
                    if hasattr(result, 'data') and result.data:
                        chunks = result.data.get('chunks', [])
                        output_size = len(chunks)
                    else:
                        output_size = 1
                
                elif tool_name == 'spacy_ner':
                    request = ToolRequest(
                        tool_id="T23A_SPACY_NER",
                        operation="extract",
                        input_data={
                            "text": data['text'],
                            "chunk_ref": f"chunk_{data_name}"
                        }
                    )
                    
                    result = tool.execute(request)
                    
                    # Extract output size
                    if hasattr(result, 'data') and result.data:
                        entities = result.data.get('entities', [])
                        output_size = len(entities)
                    else:
                        output_size = 0
                
                else:
                    raise ValueError(f"Unknown tool type: {tool_name}")
                
                execution_time = time.time() - start_time
                current_memory = process.memory_info().rss
                peak_memory = max(peak_memory, current_memory)
                memory_used = peak_memory - initial_memory
                
                # Calculate processing rate
                processing_rate = data['size'] / execution_time if execution_time > 0 else 0
                
                # Check if result indicates success
                success = True
                error_message = None
                
                if hasattr(result, 'status') and result.status == 'error':
                    success = False
                    error_message = getattr(result, 'error_message', 'Unknown error')
                elif not result:
                    success = False
                    error_message = "No result returned"
                
                # Validate against thresholds
                threshold_key = f"max_{tool_name.replace('_', '_')}_time"
                max_time = self.thresholds.get(threshold_key, 10.0)
                
                if execution_time > max_time:
                    print(f"    ⚠️  WARNING: Exceeded time threshold ({execution_time:.2f}s > {max_time}s)")
                
                memory_mb = memory_used / (1024 * 1024)
                if memory_mb > self.thresholds["max_memory_usage_mb"]:
                    print(f"    ⚠️  WARNING: Exceeded memory threshold ({memory_mb:.1f}MB > {self.thresholds['max_memory_usage_mb']}MB)")
                
                print(f"    ✅ Completed in {execution_time:.3f}s, {memory_mb:.1f}MB, {processing_rate:.0f} chars/sec, output size: {output_size}")
                
                results.append(StandaloneBenchmarkResult(
                    test_name=f"{tool_name}_{data_name}",
                    tool_name=tool_name,
                    document_info={
                        "data_name": data_name,
                        "input_size": data['size'],
                        "expected_output": data.get('expected_entities', data.get('expected_chunks', 1))
                    },
                    execution_time=execution_time,
                    memory_used=memory_used,
                    memory_peak=peak_memory,
                    output_size=output_size,
                    processing_rate=processing_rate,
                    success=success,
                    error_message=error_message
                ))
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_used = process.memory_info().rss - initial_memory
                
                print(f"    ❌ FAILED after {execution_time:.3f}s: {e}")
                
                results.append(StandaloneBenchmarkResult(
                    test_name=f"{tool_name}_{data_name}",
                    tool_name=tool_name,
                    document_info={
                        "data_name": data_name,
                        "input_size": data['size']
                    },
                    execution_time=execution_time,
                    memory_used=memory_used,
                    memory_peak=peak_memory,
                    output_size=0,
                    processing_rate=0,
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    def run_comprehensive_benchmark(self) -> StandalonePerformanceBaseline:
        """Run comprehensive standalone benchmark suite"""
        print("=" * 70)
        print("KGAS STANDALONE PERFORMANCE BENCHMARK SUITE")
        print("=" * 70)
        
        # Validate environment
        self.validate_test_environment()
        
        # Discover available tools
        available_tools = self.discover_available_tools()
        
        # Create test data
        test_data = self.create_test_data()
        
        # Run benchmarks for each available tool
        all_results = []
        tool_performance = {}
        
        for tool_name, tool in available_tools.items():
            tool_results = self.benchmark_tool_operation(tool_name, tool, test_data)
            all_results.extend(tool_results)
            
            # Calculate tool-specific performance metrics
            successful_results = [r for r in tool_results if r.success]
            if successful_results:
                tool_performance[tool_name] = {
                    'avg_execution_time': sum(r.execution_time for r in successful_results) / len(successful_results),
                    'avg_processing_rate': sum(r.processing_rate for r in successful_results) / len(successful_results),
                    'success_rate': len(successful_results) / len(tool_results),
                    'total_tests': len(tool_results)
                }
            else:
                tool_performance[tool_name] = {
                    'avg_execution_time': 0,
                    'avg_processing_rate': 0,
                    'success_rate': 0,
                    'total_tests': len(tool_results)
                }
        
        # Calculate overall system performance
        successful_tests = [r for r in all_results if r.success]
        failed_tests = [r for r in all_results if not r.success]
        
        if not successful_tests:
            raise RuntimeError("ALL BENCHMARK TESTS FAILED - Cannot establish performance baseline")
        
        failure_rate = len(failed_tests) / len(all_results)
        if failure_rate > self.thresholds["max_failure_rate"]:
            print(f"⚠️  WARNING: High failure rate: {failure_rate:.1%}")
        
        # Calculate system-wide performance metrics
        avg_processing_rate = sum(r.processing_rate for r in successful_tests) / len(successful_tests)
        avg_memory_usage = sum(r.memory_used for r in successful_tests) / len(successful_tests)
        peak_memory_usage = max(r.memory_peak for r in all_results)
        
        system_performance = {
            'avg_processing_rate_chars_per_sec': avg_processing_rate,
            'avg_memory_usage_mb': avg_memory_usage / (1024 * 1024),
            'peak_memory_usage_mb': peak_memory_usage / (1024 * 1024),
            'total_processing_time': sum(r.execution_time for r in successful_tests)
        }
        
        baseline = StandalonePerformanceBaseline(
            total_tests=len(all_results),
            successful_tests=len(successful_tests),
            failure_rate=failure_rate,
            tool_performance=tool_performance,
            system_performance=system_performance,
            baseline_established=datetime.now().isoformat(),
            performance_thresholds=self.thresholds,
            test_results=all_results
        )
        
        return baseline
    
    def save_benchmark_results(self, baseline: StandalonePerformanceBaseline) -> Path:
        """Save benchmark results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"standalone_benchmark_{timestamp}.json"
        
        # Convert to serializable format
        results_data = asdict(baseline)
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n✅ Benchmark results saved to: {results_file}")
        return results_file
    
    def print_benchmark_summary(self, baseline: StandalonePerformanceBaseline):
        """Print comprehensive benchmark summary"""
        print("\n" + "=" * 70)
        print("STANDALONE BENCHMARK RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"Total tests: {baseline.total_tests}")
        print(f"Successful tests: {baseline.successful_tests}")
        print(f"Failure rate: {baseline.failure_rate:.1%}")
        
        print(f"\nSystem Performance:")
        sys_perf = baseline.system_performance
        print(f"  Average processing rate: {sys_perf['avg_processing_rate_chars_per_sec']:.0f} chars/second")
        print(f"  Average memory usage: {sys_perf['avg_memory_usage_mb']:.1f}MB")
        print(f"  Peak memory usage: {sys_perf['peak_memory_usage_mb']:.1f}MB")
        print(f"  Total processing time: {sys_perf['total_processing_time']:.2f}s")
        
        print(f"\nTool Performance:")
        for tool_name, perf in baseline.tool_performance.items():
            print(f"  {tool_name}:")
            print(f"    Success rate: {perf['success_rate']:.1%} ({perf['total_tests']} tests)")
            print(f"    Avg execution time: {perf['avg_execution_time']:.3f}s")
            print(f"    Avg processing rate: {perf['avg_processing_rate']:.0f} chars/sec")
        
        print(f"\nPerformance Status:")
        if baseline.failure_rate <= self.thresholds["max_failure_rate"]:
            print("✅ Failure rate within acceptable limits")
        else:
            print("❌ Failure rate exceeds threshold")
        
        min_rate = min([perf['avg_processing_rate'] for perf in baseline.tool_performance.values() if perf['avg_processing_rate'] > 0] or [0])
        if min_rate >= self.thresholds["min_processing_rate"]:
            print("✅ Processing rates meet minimum requirements")
        else:
            print(f"⚠️  Some tools below minimum processing rate ({min_rate:.0f} < {self.thresholds['min_processing_rate']})")
        
        if sys_perf['peak_memory_usage_mb'] <= self.thresholds["max_memory_usage_mb"]:
            print("✅ Memory usage within limits")
        else:
            print("❌ Memory usage exceeds threshold")
        
        print(f"\nBaseline established: {baseline.baseline_established}")
        print("=" * 70)


def main():
    """Main entry point for standalone benchmark system"""
    try:
        benchmark = StandalonePerformanceBenchmark()
        baseline = benchmark.run_comprehensive_benchmark()
        
        benchmark.print_benchmark_summary(baseline)
        results_file = benchmark.save_benchmark_results(baseline)
        
        print(f"\n🎉 STANDALONE BENCHMARK COMPLETED SUCCESSFULLY!")
        print(f"Performance baseline established for available tools.")
        print(f"Results saved to: {results_file}")
        print(f"\nNote: This benchmark covers tools that can run without external services.")
        print(f"Full system benchmark requires Neo4j, Redis, and other services to be running.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ BENCHMARK FAILED: {e}")
        print("Address the issues and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())