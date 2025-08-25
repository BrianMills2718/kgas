#!/usr/bin/env python3
"""
System Stress Test Framework - Find Breaking Points and Boundaries

This framework systematically tests the limits of our KGAS system across multiple dimensions
to identify where and how it breaks under various stress conditions.
"""
import sys
import os
import time
import psutil
import threading
import tempfile
import random
import string
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

sys.path.append('/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest
from src.tools.phase1.t01_pdf_loader_unified import T01PDFLoaderUnified
from src.tools.phase1.t15a_text_chunker_unified import T15ATextChunkerUnified
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StressTestType(Enum):
    VOLUME = "volume"           # Large amounts of data
    COMPLEXITY = "complexity"   # Complex/difficult data
    CONCURRENCY = "concurrency" # Multiple simultaneous operations
    MEMORY = "memory"           # Memory pressure
    MALFORMED = "malformed"     # Invalid/corrupted data
    EDGE_CASES = "edge_cases"   # Boundary conditions
    PERFORMANCE = "performance" # Speed/throughput limits

@dataclass
class StressTestResult:
    test_name: str
    test_type: StressTestType
    success: bool
    breaking_point: Optional[str]
    max_successful: Any
    failure_mode: Optional[str]
    performance_metrics: Dict[str, Any]
    resource_usage: Dict[str, Any]
    error_details: Optional[str]

class SystemStressTester:
    """Comprehensive system stress testing framework"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.tools = self._initialize_tools()
        self.test_results = []
        
    def _initialize_tools(self):
        """Initialize all tools for testing"""
        return {
            'T01': T01PDFLoaderUnified(self.service_manager),
            'T15A': T15ATextChunkerUnified(self.service_manager),
            'T23A': T23ASpacyNERUnified(self.service_manager),
            'T27': T27RelationshipExtractorUnified(self.service_manager)
        }
    
    # ==================== VOLUME STRESS TESTS ====================
    
    def test_document_size_limits(self) -> List[StressTestResult]:
        """Test limits of document processing by size"""
        logger.info("🔬 Testing document size limits...")
        
        results = []
        sizes_to_test = [
            (1024, "1KB"),           # Tiny
            (10 * 1024, "10KB"),     # Small  
            (100 * 1024, "100KB"),   # Medium
            (1024 * 1024, "1MB"),    # Large
            (10 * 1024 * 1024, "10MB"),   # Very Large
            (50 * 1024 * 1024, "50MB"),   # Huge
            (100 * 1024 * 1024, "100MB"), # Massive
        ]
        
        max_successful_size = 0
        breaking_point = None
        
        for size_bytes, size_label in sizes_to_test:
            logger.info(f"  Testing document size: {size_label}")
            
            # Generate test document
            test_text = self._generate_test_document(size_bytes)
            
            try:
                start_time = time.time()
                memory_before = psutil.Process().memory_info().rss
                
                # Test full pipeline
                success = self._test_document_pipeline(test_text, f"volume_test_{size_label}")
                
                end_time = time.time()
                memory_after = psutil.Process().memory_info().rss
                
                if success:
                    max_successful_size = size_bytes
                    logger.info(f"    ✅ {size_label} - SUCCESS")
                else:
                    breaking_point = size_label
                    logger.info(f"    ❌ {size_label} - FAILED")
                    break
                    
                results.append(StressTestResult(
                    test_name=f"document_size_{size_label}",
                    test_type=StressTestType.VOLUME,
                    success=success,
                    breaking_point=breaking_point,
                    max_successful=max_successful_size,
                    failure_mode=None,
                    performance_metrics={
                        "processing_time": end_time - start_time,
                        "throughput_chars_per_sec": len(test_text) / (end_time - start_time)
                    },
                    resource_usage={
                        "memory_used_mb": (memory_after - memory_before) / 1024 / 1024,
                        "peak_memory_mb": memory_after / 1024 / 1024
                    },
                    error_details=None
                ))
                
            except Exception as e:
                breaking_point = size_label
                logger.error(f"    💥 {size_label} - CRASHED: {e}")
                
                results.append(StressTestResult(
                    test_name=f"document_size_{size_label}",
                    test_type=StressTestType.VOLUME,
                    success=False,
                    breaking_point=breaking_point,
                    max_successful=max_successful_size,
                    failure_mode="CRASH",
                    performance_metrics={},
                    resource_usage={},
                    error_details=str(e)
                ))
                break
        
        logger.info(f"📊 Document Size Limits: Max successful = {max_successful_size} bytes, Breaking point = {breaking_point}")
        return results
    
    def test_entity_density_limits(self) -> List[StressTestResult]:
        """Test limits based on entity density (entities per text length)"""
        logger.info("🔬 Testing entity density limits...")
        
        results = []
        entity_densities = [
            (0.01, "Low - 1%"),      # 1 entity per 100 chars
            (0.05, "Medium - 5%"),   # 5 entities per 100 chars  
            (0.1, "High - 10%"),     # 10 entities per 100 chars
            (0.2, "Very High - 20%"), # 20 entities per 100 chars
            (0.5, "Extreme - 50%"),  # 50 entities per 100 chars
        ]
        
        base_text_size = 10000  # 10KB base document
        
        for density, density_label in entity_densities:
            logger.info(f"  Testing entity density: {density_label}")
            
            try:
                # Generate text with specific entity density
                test_text = self._generate_entity_dense_text(base_text_size, density)
                
                start_time = time.time()
                success = self._test_entity_extraction_pipeline(test_text, f"density_test_{density}")
                end_time = time.time()
                
                results.append(StressTestResult(
                    test_name=f"entity_density_{density}",
                    test_type=StressTestType.COMPLEXITY,
                    success=success,
                    breaking_point=None if success else density_label,
                    max_successful=density if success else None,
                    failure_mode=None if success else "PROCESSING_FAILURE",
                    performance_metrics={
                        "processing_time": end_time - start_time,
                        "entity_density": density
                    },
                    resource_usage={
                        "peak_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
                    },
                    error_details=None
                ))
                
                if success:
                    logger.info(f"    ✅ {density_label} - SUCCESS")
                else:
                    logger.info(f"    ❌ {density_label} - FAILED")
                    
            except Exception as e:
                logger.error(f"    💥 {density_label} - CRASHED: {e}")
                results.append(StressTestResult(
                    test_name=f"entity_density_{density}",
                    test_type=StressTestType.COMPLEXITY,
                    success=False,
                    breaking_point=density_label,
                    max_successful=None,
                    failure_mode="CRASH",
                    performance_metrics={},
                    resource_usage={},
                    error_details=str(e)
                ))
                break
        
        return results
    
    # ==================== CONCURRENCY STRESS TESTS ====================
    
    def test_concurrent_processing_limits(self) -> List[StressTestResult]:
        """Test limits of concurrent document processing"""
        logger.info("🔬 Testing concurrent processing limits...")
        
        results = []
        concurrency_levels = [1, 2, 5, 10, 20, 50, 100]
        
        for num_concurrent in concurrency_levels:
            logger.info(f"  Testing {num_concurrent} concurrent operations...")
            
            try:
                success, metrics = self._test_concurrent_operations(num_concurrent)
                
                results.append(StressTestResult(
                    test_name=f"concurrent_ops_{num_concurrent}",
                    test_type=StressTestType.CONCURRENCY,
                    success=success,
                    breaking_point=None if success else f"{num_concurrent}_operations",
                    max_successful=num_concurrent if success else None,
                    failure_mode=None if success else "CONCURRENCY_FAILURE",
                    performance_metrics=metrics,
                    resource_usage={
                        "peak_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
                    },
                    error_details=None
                ))
                
                if success:
                    logger.info(f"    ✅ {num_concurrent} concurrent - SUCCESS")
                else:
                    logger.info(f"    ❌ {num_concurrent} concurrent - FAILED")
                    break
                    
            except Exception as e:
                logger.error(f"    💥 {num_concurrent} concurrent - CRASHED: {e}")
                results.append(StressTestResult(
                    test_name=f"concurrent_ops_{num_concurrent}",
                    test_type=StressTestType.CONCURRENCY,
                    success=False,
                    breaking_point=f"{num_concurrent}_operations",
                    max_successful=None,
                    failure_mode="CRASH",
                    performance_metrics={},
                    resource_usage={},
                    error_details=str(e)
                ))
                break
        
        return results
    
    # ==================== MALFORMED DATA STRESS TESTS ====================
    
    def test_malformed_data_handling(self) -> List[StressTestResult]:
        """Test system resilience to malformed/corrupted data"""
        logger.info("🔬 Testing malformed data handling...")
        
        results = []
        malformed_tests = [
            ("empty_text", ""),
            ("only_whitespace", "   \n\t\r   "),
            ("only_punctuation", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("mixed_encodings", "Hello 世界 🌍 café naïve résumé"),
            ("very_long_words", "a" * 1000 + " " + "b" * 2000),
            ("unicode_control", "\x00\x01\x02\x03\x1f\x7f"),
            ("html_tags", "<html><body><script>alert('test')</script></body></html>"),
            ("json_injection", '{"key": "value", "injection": true}'),
            ("sql_injection", "'; DROP TABLE entities; --"),
            ("regex_bombs", "a" * 100 + "(" * 50 + "a" * 100 + ")" * 50),
        ]
        
        for test_name, malformed_text in malformed_tests:
            logger.info(f"  Testing malformed data: {test_name}")
            
            try:
                start_time = time.time()
                success = self._test_document_pipeline(malformed_text, f"malformed_{test_name}")
                end_time = time.time()
                
                results.append(StressTestResult(
                    test_name=f"malformed_{test_name}",
                    test_type=StressTestType.MALFORMED,
                    success=success,
                    breaking_point=None,
                    max_successful=test_name if success else None,
                    failure_mode=None if success else "MALFORMED_DATA_FAILURE",
                    performance_metrics={
                        "processing_time": end_time - start_time
                    },
                    resource_usage={
                        "peak_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
                    },
                    error_details=None
                ))
                
                if success:
                    logger.info(f"    ✅ {test_name} - HANDLED GRACEFULLY")
                else:
                    logger.info(f"    ⚠️  {test_name} - FAILED TO PROCESS")
                    
            except Exception as e:
                logger.error(f"    💥 {test_name} - CRASHED: {e}")
                results.append(StressTestResult(
                    test_name=f"malformed_{test_name}",
                    test_type=StressTestType.MALFORMED,
                    success=False,
                    breaking_point=test_name,
                    max_successful=None,
                    failure_mode="CRASH",
                    performance_metrics={},
                    resource_usage={},
                    error_details=str(e)
                ))
        
        return results
    
    # ==================== EDGE CASE STRESS TESTS ====================
    
    def test_edge_cases(self) -> List[StressTestResult]:
        """Test boundary conditions and edge cases"""
        logger.info("🔬 Testing edge cases...")
        
        results = []
        edge_cases = [
            ("single_char", "a"),
            ("single_word", "hello"),
            ("single_sentence", "This is a test sentence."),
            ("no_entities", "The quick brown fox jumps over the lazy dog."),
            ("only_numbers", "123 456 789 0.123 -456 3.14159"),
            ("only_dates", "2024-01-01 January 1st 2024 01/01/2024"),
            ("repeated_text", "test " * 1000),
            ("nested_entities", "John Smith from Smith Corp in Smith County worked at Smith Industries"),
            ("ambiguous_entities", "Apple makes computers. I ate an apple. Apple stock rose."),
            ("overlapping_entities", "New York City in New York State in the United States of America"),
        ]
        
        for test_name, test_text in edge_cases:
            logger.info(f"  Testing edge case: {test_name}")
            
            try:
                start_time = time.time()
                success = self._test_document_pipeline(test_text, f"edge_{test_name}")
                end_time = time.time()
                
                results.append(StressTestResult(
                    test_name=f"edge_{test_name}",
                    test_type=StressTestType.EDGE_CASES,
                    success=success,
                    breaking_point=None,
                    max_successful=test_name if success else None,
                    failure_mode=None if success else "EDGE_CASE_FAILURE",
                    performance_metrics={
                        "processing_time": end_time - start_time
                    },
                    resource_usage={
                        "peak_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024
                    },
                    error_details=None
                ))
                
                if success:
                    logger.info(f"    ✅ {test_name} - SUCCESS")
                else:
                    logger.info(f"    ❌ {test_name} - FAILED")
                    
            except Exception as e:
                logger.error(f"    💥 {test_name} - CRASHED: {e}")
                results.append(StressTestResult(
                    test_name=f"edge_{test_name}",
                    test_type=StressTestType.EDGE_CASES,
                    success=False,
                    breaking_point=test_name,
                    max_successful=None,
                    failure_mode="CRASH",
                    performance_metrics={},
                    resource_usage={},
                    error_details=str(e)
                ))
        
        return results
    
    # ==================== HELPER METHODS ====================
    
    def _generate_test_document(self, size_bytes: int) -> str:
        """Generate a test document of specified size with realistic content"""
        # Base content that will be repeated/modified to reach target size
        base_content = """
        The research conducted by Dr. Sarah Johnson at Stanford University shows promising results.
        Microsoft Corporation has partnered with Google Research to develop new AI technologies.
        The study was funded by the National Science Foundation and published in Nature.
        Results indicate a 95% improvement in processing efficiency compared to previous methods.
        The team includes researchers from MIT, Stanford, and Carnegie Mellon University.
        """
        
        # Calculate how many repetitions we need
        base_size = len(base_content)
        repetitions = max(1, size_bytes // base_size)
        
        # Generate content
        content = base_content * repetitions
        
        # Add random variations to make it more realistic
        if size_bytes > base_size * repetitions:
            remaining = size_bytes - len(content)
            content += " Additional research data: " + "x" * max(0, remaining - 25)
        
        return content[:size_bytes]  # Trim to exact size
    
    def _generate_entity_dense_text(self, text_size: int, entity_density: float) -> str:
        """Generate text with specific entity density"""
        # Entity templates
        person_names = ["John Smith", "Sarah Johnson", "Michael Chen", "Emily Rodriguez", "David Wilson"]
        org_names = ["TechCorp", "DataSystems", "AI Solutions", "Research Labs", "Innovation Inc"]
        location_names = ["New York", "San Francisco", "Boston", "Seattle", "Austin"]
        
        num_entities = int(text_size * entity_density / 10)  # Rough estimate
        
        content = []
        for i in range(num_entities):
            person = random.choice(person_names)
            org = random.choice(org_names)
            location = random.choice(location_names)
            
            sentence = f"{person} works at {org} located in {location}. "
            content.append(sentence)
        
        # Fill remaining space with filler text
        full_content = "".join(content)
        if len(full_content) < text_size:
            filler = "Additional research data and analysis results. " * ((text_size - len(full_content)) // 50)
            full_content += filler
        
        return full_content[:text_size]
    
    def _test_document_pipeline(self, text: str, test_id: str) -> bool:
        """Test full document processing pipeline"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_file = f.name
            
            try:
                # T01: Load document
                t01_request = ToolRequest(
                    tool_id='T01',
                    operation='load_document',
                    input_data={'file_path': temp_file, 'workflow_id': test_id},
                    parameters={}
                )
                t01_result = self.tools['T01'].execute(t01_request)
                if t01_result.status != "success":
                    return False
                
                # T15A: Chunk text
                t15a_request = ToolRequest(
                    tool_id='T15A',
                    operation='chunk_text',
                    input_data={
                        'document_ref': t01_result.data['document_ref'],
                        'text': text,
                        'confidence': 0.8
                    },
                    parameters={}
                )
                t15a_result = self.tools['T15A'].execute(t15a_request)
                if t15a_result.status != "success":
                    return False
                
                # T23A: Extract entities
                chunks = t15a_result.data.get('chunks', [])
                if not chunks:
                    return True  # Empty chunks is valid for some edge cases
                
                chunk = chunks[0]
                t23a_request = ToolRequest(
                    tool_id='T23A',
                    operation='extract_entities',
                    input_data={
                        'text': chunk.get('text', ''),
                        'chunk_ref': chunk.get('chunk_ref', ''),
                        'confidence_threshold': 0.0
                    },
                    parameters={}
                )
                t23a_result = self.tools['T23A'].execute(t23a_request)
                if t23a_result.status != "success":
                    return False
                
                return True
                
            finally:
                # Clean up temp file
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            return False
    
    def _test_entity_extraction_pipeline(self, text: str, test_id: str) -> bool:
        """Test just entity extraction pipeline"""
        try:
            t23a_request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': text,
                    'chunk_ref': f'test_{test_id}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            t23a_result = self.tools['T23A'].execute(t23a_request)
            return t23a_result.status == "success"
        except Exception:
            return False
    
    def _test_concurrent_operations(self, num_concurrent: int) -> tuple[bool, Dict[str, Any]]:
        """Test concurrent operations"""
        test_text = "John Smith works at TechCorp in San Francisco. The company was founded by Sarah Johnson."
        
        def worker():
            return self._test_entity_extraction_pipeline(test_text, f"concurrent_{threading.current_thread().ident}")
        
        start_time = time.time()
        
        threads = []
        results = []
        
        for i in range(num_concurrent):
            thread = threading.Thread(target=lambda: results.append(worker()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        end_time = time.time()
        
        success_count = sum(1 for r in results if r)
        success_rate = success_count / len(results) if results else 0
        
        metrics = {
            "total_operations": num_concurrent,
            "successful_operations": success_count,
            "success_rate": success_rate,
            "total_time": end_time - start_time,
            "avg_time_per_op": (end_time - start_time) / num_concurrent
        }
        
        # Consider success if >80% operations succeeded
        return success_rate > 0.8, metrics
    
    # ==================== MAIN TEST RUNNER ====================
    
    def run_all_stress_tests(self) -> Dict[str, List[StressTestResult]]:
        """Run all stress tests and return comprehensive results"""
        logger.info("🚀 Starting comprehensive system stress testing...")
        
        all_results = {}
        
        # Run each category of stress tests
        test_categories = [
            ("Volume Tests", self.test_document_size_limits),
            ("Entity Density Tests", self.test_entity_density_limits),
            ("Concurrency Tests", self.test_concurrent_processing_limits),
            ("Malformed Data Tests", self.test_malformed_data_handling),
            ("Edge Case Tests", self.test_edge_cases),
        ]
        
        for category_name, test_method in test_categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"🧪 {category_name}")
            logger.info(f"{'='*60}")
            
            try:
                results = test_method()
                all_results[category_name] = results
                self.test_results.extend(results)
            except Exception as e:
                logger.error(f"❌ {category_name} failed completely: {e}")
                all_results[category_name] = []
        
        self._generate_stress_test_report(all_results)
        return all_results
    
    def _generate_stress_test_report(self, all_results: Dict[str, List[StressTestResult]]):
        """Generate comprehensive stress test report"""
        logger.info(f"\n{'='*80}")
        logger.info("📋 COMPREHENSIVE STRESS TEST REPORT")
        logger.info(f"{'='*80}")
        
        total_tests = sum(len(results) for results in all_results.values())
        total_passed = sum(len([r for r in results if r.success]) for results in all_results.values())
        overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n🎯 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {total_passed}")
        logger.info(f"   Failed: {total_tests - total_passed}")
        logger.info(f"   Success Rate: {overall_pass_rate:.1f}%")
        
        for category_name, results in all_results.items():
            if not results:
                continue
                
            logger.info(f"\n📊 {category_name}:")
            passed = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            logger.info(f"   Passed: {len(passed)}/{len(results)} ({len(passed)/len(results)*100:.1f}%)")
            
            if failed:
                logger.info(f"   Breaking Points:")
                for failure in failed:
                    logger.info(f"     - {failure.test_name}: {failure.breaking_point or 'Unknown'}")
                    if failure.error_details:
                        logger.info(f"       Error: {failure.error_details}")
            
            if passed:
                # Find performance boundaries
                max_performance = max(passed, key=lambda x: x.performance_metrics.get('processing_time', 0))
                logger.info(f"   Performance Boundary: {max_performance.test_name}")
        
        logger.info(f"\n🎯 SYSTEM BOUNDARIES IDENTIFIED:")
        
        # Volume boundaries
        volume_results = all_results.get("Volume Tests", [])
        if volume_results:
            max_size = max([r.max_successful for r in volume_results if r.max_successful], default=0)
            logger.info(f"   📄 Max Document Size: {max_size / 1024 / 1024:.1f}MB")
        
        # Concurrency boundaries  
        concurrency_results = all_results.get("Concurrency Tests", [])
        if concurrency_results:
            max_concurrent = max([r.max_successful for r in concurrency_results if r.max_successful], default=0)
            logger.info(f"   🔀 Max Concurrent Operations: {max_concurrent}")
        
        # Memory usage
        peak_memory = max([r.resource_usage.get('peak_memory_mb', 0) for r in self.test_results])
        logger.info(f"   💾 Peak Memory Usage: {peak_memory:.1f}MB")
        
        logger.info(f"\n{'='*80}")


if __name__ == "__main__":
    print("🔬 SYSTEM STRESS TESTING FRAMEWORK")
    print("=" * 60)
    print("Finding the breaking points and boundaries of the KGAS system...")
    print()
    
    tester = SystemStressTester()
    results = tester.run_all_stress_tests()
    
    print(f"\n✅ Stress testing complete!")
    print(f"📁 Results saved in framework for analysis")