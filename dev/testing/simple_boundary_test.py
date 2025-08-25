#!/usr/bin/env python3
"""
Simple System Boundary Test - Quick and clear boundary identification
"""
import sys
import time
import psutil
import logging

sys.path.append('/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.base_tool import ToolRequest
from src.tools.phase1.t23a_spacy_ner_unified import T23ASpacyNERUnified

# Suppress debug logging
logging.getLogger().setLevel(logging.ERROR)

def test_boundaries():
    print("🎯 SYSTEM BOUNDARY IDENTIFICATION")
    print("=" * 50)
    
    service_manager = ServiceManager()
    t23a = T23ASpacyNERUnified(service_manager)
    
    # Test text sizes
    base_text = "John Smith works at TechCorp in San Francisco. Sarah Johnson founded the company. "
    
    print("\n📏 TEXT SIZE BOUNDARIES:")
    sizes_kb = [1, 10, 50, 100, 500, 1000]
    
    for size_kb in sizes_kb:
        text_size = size_kb * 1024
        repetitions = text_size // len(base_text)
        test_text = base_text * repetitions
        test_text = test_text[:text_size]
        
        try:
            start_time = time.time()
            memory_before = psutil.Process().memory_info().rss / 1024 / 1024
            
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'test_{size_kb}kb',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            result = t23a.execute(request)
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            if result.status == "success":
                entities = result.data.get('entities', [])
                time_taken = end_time - start_time
                memory_used = memory_after - memory_before
                
                print(f"{size_kb:4}KB: ✅ {len(entities):3} entities, {time_taken:5.2f}s, +{memory_used:4.1f}MB (Peak: {memory_after:5.1f}MB)")
                
                # Identify performance boundaries
                if time_taken > 10:
                    print(f"      ⚠️  SLOW: Processing time > 10s")
                if memory_after > 1500:
                    print(f"      ⚠️  HIGH MEMORY: > 1.5GB")
                    
            else:
                print(f"{size_kb:4}KB: ❌ FAILED - {result.error_message}")
                break
                
        except Exception as e:
            print(f"{size_kb:4}KB: 💥 CRASHED - {str(e)[:50]}...")
            break
    
    print("\n🏢 ENTITY COUNT BOUNDARIES:")
    entity_counts = [10, 50, 100, 500, 1000]
    
    for target_count in entity_counts:
        # Generate text with many unique entities
        entities_text = []
        for i in range(target_count):
            entities_text.append(f"Person{i} works at Company{i} in City{i}. ")
        
        test_text = "".join(entities_text)
        
        try:
            start_time = time.time()
            
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities', 
                input_data={
                    'text': test_text,
                    'chunk_ref': f'entities_{target_count}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            result = t23a.execute(request)
            end_time = time.time()
            
            if result.status == "success":
                actual_entities = len(result.data.get('entities', []))
                time_taken = end_time - start_time
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                
                print(f"{target_count:4} target: ✅ {actual_entities:3} found, {time_taken:5.2f}s, {memory_mb:5.1f}MB")
                
                if time_taken > 30:
                    print(f"         ⚠️  VERY SLOW: > 30s processing")
                if memory_mb > 2000:
                    print(f"         ⚠️  HIGH MEMORY: > 2GB")
                    
            else:
                print(f"{target_count:4} target: ❌ FAILED")
                break
                
        except Exception as e:
            print(f"{target_count:4} target: 💥 CRASHED - {str(e)[:50]}...")
            break
    
    print("\n🛡️  RESILIENCE BOUNDARIES:")
    malformed_tests = [
        ("Empty", ""),
        ("Whitespace", "   \n\t   "),
        ("Punctuation", "!@#$%^&*()"),
        ("Long word", "a" * 5000),
        ("Unicode", "Hello 世界 🌍"),
        ("HTML", "<html><body>Test</body></html>"),
        ("Control chars", "\x00\x01\x02\x03"),
    ]
    
    for test_name, test_text in malformed_tests:
        try:
            request = ToolRequest(
                tool_id='T23A',
                operation='extract_entities',
                input_data={
                    'text': test_text,
                    'chunk_ref': f'malformed_{test_name.lower()}',
                    'confidence_threshold': 0.0
                },
                parameters={}
            )
            
            result = t23a.execute(request)
            
            if result.status == "success":
                entities = len(result.data.get('entities', []))
                print(f"{test_name:12}: ✅ HANDLED ({entities} entities)")
            else:
                print(f"{test_name:12}: ⚠️  REJECTED - {result.error_message[:30]}...")
                
        except Exception as e:
            print(f"{test_name:12}: 💥 CRASHED - {str(e)[:30]}...")
    
    print("\n" + "=" * 50)
    print("🏁 BOUNDARY IDENTIFICATION COMPLETE")
    memory_final = psutil.Process().memory_info().rss / 1024 / 1024
    print(f"Final memory usage: {memory_final:.1f}MB")

if __name__ == "__main__":
    test_boundaries()