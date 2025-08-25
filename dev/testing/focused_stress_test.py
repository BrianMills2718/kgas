#!/usr/bin/env python3
"""
Focused Stress Test - Quick identification of system breaking points

This script focuses on the most critical boundaries to identify where the system breaks.
"""
import sys
import time
import psutil
import tempfile
import os
import logging

sys.path.append('/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified
from src.tools.phase1.t27_relationship_extractor_unified import T27RelationshipExtractorUnified

logging.basicConfig(level=logging.WARNING)  # Reduce noise

def test_text_size_boundaries():
    """Find the text size breaking point"""
    print("🔍 TESTING TEXT SIZE BOUNDARIES")
    print("=" * 50)
    
    service_manager = ServiceManager()
    t23a = T23ASpacyNERUnified(service_manager)
    
    # Test sizes in KB
    sizes_kb = [1, 10, 50, 100, 500, 1000, 5000, 10000]
    
    for size_kb in sizes_kb:
        # Generate test text
        base_text = "John Smith works at TechCorp in San Francisco. Sarah Johnson founded the company. "
        text_size = size_kb * 1024
        repetitions = text_size // len(base_text)
        test_text = base_text * repetitions
        test_text = test_text[:text_size]  # Trim to exact size
        
        print(f"Testing {size_kb}KB ({len(test_text)} chars)... ", end="")
        
        try:
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'size_test_{size_kb}kb',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            result = t23a.execute(request)
            
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            if result.status == "success":
                entities = result.data.get('entities', [])
                processing_time = end_time - start_time
                memory_used = memory_after - memory_before
                
                print(f"✅ SUCCESS")
                print(f"   Entities: {len(entities)}")
                print(f"   Time: {processing_time:.2f}s")
                print(f"   Memory: +{memory_used:.1f}MB (Peak: {memory_after:.1f}MB)")
                
                # Check if processing is getting slow
                if processing_time > 30:  # 30 second threshold
                    print(f"   ⚠️  SLOW - Processing time exceeding threshold")
                    
                if memory_after > 2000:  # 2GB threshold
                    print(f"   ⚠️  HIGH MEMORY - Memory usage exceeding threshold")
                    
            else:
                print(f"❌ FAILED - {result.error_message}")
                break
                
        except Exception as e:
            print(f"💥 CRASHED - {e}")
            break
        
        print()

def test_entity_count_boundaries():
    """Find the entity count breaking point"""
    print("\n🔍 TESTING ENTITY COUNT BOUNDARIES")
    print("=" * 50)
    
    service_manager = ServiceManager()
    t23a = T23ASpacyNERUnified(service_manager)
    t27 = T27RelationshipExtractorUnified(service_manager)
    
    # Test different entity counts
    entity_counts = [10, 50, 100, 200, 500, 1000, 2000]
    
    for target_entities in entity_counts:
        print(f"Testing ~{target_entities} entities... ", end="")
        
        # Generate text with many entities
        persons = ["John Smith", "Sarah Johnson", "Michael Chen", "Emily Rodriguez", "David Wilson"]
        orgs = ["TechCorp", "DataSystems", "AI Solutions", "Research Labs", "Innovation Inc"]
        places = ["New York", "San Francisco", "Boston", "Seattle", "Austin"]
        
        sentences = []
        for i in range(target_entities // 3):  # Roughly 3 entities per sentence
            person = persons[i % len(persons)]
            org = orgs[i % len(orgs)]  
            place = places[i % len(places)]
            sentences.append(f"{person} works at {org} located in {place}. ")
        
        test_text = "".join(sentences)
        
        try:
            start_time = time.time()
            
            # Test T23A
            t23a_request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'entity_test_{target_entities}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            t23a_result = t23a.execute(t23a_request)
            
            if t23a_result.status != "success":
                print(f"❌ T23A FAILED - {t23a_result.error_message}")
                break
            
            entities = t23a_result.data.get('entities', [])
            actual_entities = len(entities)
            
            # Test T27 if we have enough entities
            if actual_entities >= 2:
                formatted_entities = []
                for entity in entities:
                    formatted_entities.append({
                        "text": entity.get("surface_form", ""),
                        "entity_type": entity.get("entity_type", "UNKNOWN"),
                        "start": entity.get("start_pos", 0),
                        "end": entity.get("end_pos", 0),
                        "confidence": entity.get("confidence", 0.8)
                    })
                
                t27_request = ToolRequest(
                    tool_id='T27',
                    operation='extract_relationships',
                    input_data={
                        'text': test_text,
                        'entities': formatted_entities,
                        'chunk_ref': f'rel_test_{target_entities}'
                    },
                    parameters={'confidence_threshold': 0.3}
                )
                
                t27_result = t27.execute(t27_request)
                relationships = t27_result.data.get('relationships', []) if t27_result.status == "success" else []
            else:
                relationships = []
            
            end_time = time.time()
            processing_time = end_time - start_time
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            
            print(f"✅ SUCCESS")
            print(f"   Text: {len(test_text)} chars")
            print(f"   Entities: {actual_entities}")
            print(f"   Relationships: {len(relationships)}")
            print(f"   Time: {processing_time:.2f}s")
            print(f"   Memory: {memory_mb:.1f}MB")
            
            # Performance warnings
            if processing_time > 60:
                print(f"   ⚠️  VERY SLOW - {processing_time:.1f}s processing time")
            if memory_mb > 3000:
                print(f"   ⚠️  HIGH MEMORY - {memory_mb:.1f}MB usage")
                
        except Exception as e:
            print(f"💥 CRASHED - {e}")
            break
        
        print()

def test_malformed_data_resilience():
    """Test resilience to various malformed inputs"""
    print("\n🔍 TESTING MALFORMED DATA RESILIENCE")
    print("=" * 50)
    
    service_manager = ServiceManager()
    t23a = T23ASpacyNERUnified(service_manager)
    
    malformed_tests = [
        ("Empty text", ""),
        ("Only whitespace", "   \n\t\r   "),
        ("Only punctuation", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
        ("Very long word", "a" * 10000),
        ("Unicode mixed", "Hello 世界 🌍 café naïve résumé Москва"),
        ("HTML tags", "<html><body><h1>Test</h1><script>alert('xss')</script></body></html>"),
        ("JSON-like", '{"name": "John", "company": "TechCorp", "location": "NYC"}'),
        ("SQL-like", "SELECT * FROM users WHERE name='John'; DROP TABLE users;"),
        ("Control chars", "\x00\x01\x02\x03\x1f\x7f"),
        ("Repeated pattern", "John works at TechCorp. " * 1000),
    ]
    
    for test_name, test_text in malformed_tests:
        print(f"Testing {test_name}... ", end="")
        
        try:
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'malformed_{test_name.replace(" ", "_")}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            result = t23a.execute(request)
            
            if result.status == "success":
                entities = result.data.get('entities', [])
                print(f"✅ HANDLED GRACEFULLY ({len(entities)} entities)")
            else:
                print(f"⚠️  FAILED GRACEFULLY - {result.error_message}")
                
        except Exception as e:
            print(f"💥 CRASHED - {e}")
        
        print()

def test_concurrent_stress():
    """Test concurrent processing limits"""
    print("\n🔍 TESTING CONCURRENT PROCESSING")
    print("=" * 50)
    
    import threading
    import queue
    
    service_manager = ServiceManager()
    t23a = T23ASpacyNERUnified(service_manager)
    
    test_text = "John Smith works at TechCorp in San Francisco. Sarah Johnson founded the company in 2020."
    
    def worker(worker_id, results_queue):
        try:
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'concurrent_worker_{worker_id}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            start_time = time.time()
            result = t23a.execute(request)
            end_time = time.time()
            
            results_queue.put({
                'worker_id': worker_id,
                'success': result.status == "success",
                'time': end_time - start_time,
                'entities': len(result.data.get('entities', [])) if result.status == "success" else 0
            })
            
        except Exception as e:
            results_queue.put({
                'worker_id': worker_id,
                'success': False,
                'error': str(e),
                'time': 0,
                'entities': 0
            })
    
    concurrency_levels = [1, 2, 5, 10, 20, 50]
    
    for num_threads in concurrency_levels:
        print(f"Testing {num_threads} concurrent operations... ", end="")
        
        results_queue = queue.Queue()
        threads = []
        
        start_time = time.time()
        
        # Start threads
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i, results_queue))
            threads.append(thread)
            thread.start()
        
        # Wait for completion with timeout
        for thread in threads:
            thread.join(timeout=30)
        
        end_time = time.time()
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        success_rate = len(successful) / num_threads * 100 if num_threads > 0 else 0
        avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0
        total_time = end_time - start_time
        
        print(f"✅ {success_rate:.1f}% success rate")
        print(f"   Completed: {len(successful)}/{num_threads}")
        print(f"   Avg time per op: {avg_time:.2f}s")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f}MB")
        
        if failed:
            print(f"   Failures: {len(failed)}")
            for failure in failed[:3]:  # Show first 3 failures
                print(f"     - Worker {failure['worker_id']}: {failure.get('error', 'Unknown error')}")
        
        print()
        
        # Stop if success rate drops too low
        if success_rate < 80:
            print(f"   ⚠️  Success rate dropped below 80%, stopping concurrency test")
            break

if __name__ == "__main__":
    print("🎯 FOCUSED SYSTEM STRESS TEST")
    print("=" * 60)
    print("Identifying critical breaking points and boundaries...")
    print()
    
    start_time = time.time()
    
    try:
        test_text_size_boundaries()
        test_entity_count_boundaries()  
        test_malformed_data_resilience()
        test_concurrent_stress()
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test framework crashed: {e}")
    
    end_time = time.time()
    
    print(f"\n{'='*60}")
    print(f"🏁 STRESS TEST COMPLETE")
    print(f"   Total time: {end_time - start_time:.1f}s")
    print(f"   Peak memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f}MB")
    print(f"{'='*60}")