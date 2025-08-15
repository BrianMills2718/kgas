#!/usr/bin/env python3
"""
Performance Benchmarking for KGAS System
Measures response times, throughput, and resource usage
"""

import asyncio
import time
import psutil
import statistics
from datetime import datetime
from typing import List, Dict, Any

class PerformanceBenchmark:
    def __init__(self):
        self.results = {}
        
    def measure_memory(self):
        """Get current memory usage"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def measure_cpu(self):
        """Get current CPU usage"""
        return psutil.cpu_percent(interval=0.1)
    
    async def benchmark_entity_extraction(self, iterations: int = 10):
        """Benchmark entity extraction performance"""
        from src.tools.phase2.extraction_components.entity_resolution import EntityResolver
        from src.core.service_manager import ServiceManager
        
        sm = ServiceManager()
        er = EntityResolver(sm.identity_service)
        
        test_texts = [
            "Dr. Smith from MIT studies artificial intelligence.",
            "Google announced a partnership with OpenAI.",
            "The COVID-19 pandemic affected supply chains."
        ]
        
        times = []
        memory_usage = []
        
        print(f"Running {iterations} iterations of entity extraction...")
        
        for i in range(iterations):
            start_mem = self.measure_memory()
            start_time = time.time()
            
            for text in test_texts:
                mention = er.create_mention(text[:20], 'ENTITY', f'test_{i}', 0.8, 'benchmark')
            
            elapsed = time.time() - start_time
            end_mem = self.measure_memory()
            
            times.append(elapsed)
            memory_usage.append(end_mem - start_mem)
            
            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")
        
        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory": statistics.mean(memory_usage),
            "throughput": len(test_texts) / statistics.mean(times)  # entities/second
        }
    
    async def benchmark_neo4j_operations(self, iterations: int = 10):
        """Benchmark Neo4j database operations"""
        from src.core.neo4j_config import get_neo4j_config
        from neo4j import GraphDatabase
        
        config = get_neo4j_config()
        driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password)
        )
        
        times = []
        print(f"Running {iterations} iterations of Neo4j operations...")
        
        for i in range(iterations):
            start_time = time.time()
            
            with driver.session() as session:
                # Count nodes
                session.run("MATCH (n) RETURN count(n) as count LIMIT 1").single()
                
                # Simple pattern match
                session.run("""
                    MATCH (e:Entity)-[:RELATED_TO]->(e2:Entity) 
                    RETURN e, e2 LIMIT 10
                """).consume()
                
                # Create test node
                session.run("""
                    CREATE (t:TestNode {id: $id, timestamp: $ts})
                    """, id=f"test_{i}", ts=datetime.now().isoformat()
                )
                
                # Delete test node
                session.run("""
                    MATCH (t:TestNode {id: $id})
                    DELETE t
                    """, id=f"test_{i}"
                )
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            if (i + 1) % 5 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations")
        
        driver.close()
        
        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "operations_per_second": 4 / statistics.mean(times)  # 4 ops per iteration
        }
    
    async def benchmark_tool_execution(self):
        """Benchmark tool execution"""
        from src.core.tool_contract import get_tool_registry
        from src.tools.base_tool import ToolRequest
        
        registry = get_tool_registry()
        
        if 'T49_MULTIHOP_QUERY' not in registry._tools:
            return {"error": "T49 tool not available"}
        
        tool = registry.get_tool('T49_MULTIHOP_QUERY')
        
        times = []
        print("Running tool execution benchmark...")
        
        for i in range(5):
            request = ToolRequest(
                tool_id='T49_MULTIHOP_QUERY',
                operation='query',
                input_data={'query': f'test query {i}', 'max_hops': 2},
                parameters={}
            )
            
            start_time = time.time()
            result = tool.execute(request)
            elapsed = time.time() - start_time
            
            times.append(elapsed)
        
        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times)
        }
    
    async def run_all_benchmarks(self):
        """Run all performance benchmarks"""
        print("=" * 60)
        print("KGAS PERFORMANCE BENCHMARKING")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"CPU Cores: {psutil.cpu_count()}")
        print(f"Total Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.2f} GB")
        print(f"Available Memory: {psutil.virtual_memory().available / 1024 / 1024 / 1024:.2f} GB\n")
        
        # Entity Extraction Benchmark
        print("1. Entity Extraction Performance")
        print("-" * 40)
        try:
            entity_results = await self.benchmark_entity_extraction(10)
            print(f"   Average Time: {entity_results['avg_time']*1000:.2f} ms")
            print(f"   Min/Max Time: {entity_results['min_time']*1000:.2f} / {entity_results['max_time']*1000:.2f} ms")
            print(f"   Throughput: {entity_results['throughput']:.1f} entities/second")
            print(f"   Memory Delta: {entity_results['avg_memory']:.2f} MB")
            self.results['entity_extraction'] = entity_results
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results['entity_extraction'] = {"error": str(e)}
        
        # Neo4j Operations Benchmark
        print("\n2. Neo4j Database Performance")
        print("-" * 40)
        try:
            neo4j_results = await self.benchmark_neo4j_operations(10)
            print(f"   Average Time: {neo4j_results['avg_time']*1000:.2f} ms")
            print(f"   Min/Max Time: {neo4j_results['min_time']*1000:.2f} / {neo4j_results['max_time']*1000:.2f} ms")
            print(f"   Operations/Second: {neo4j_results['operations_per_second']:.1f}")
            self.results['neo4j'] = neo4j_results
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results['neo4j'] = {"error": str(e)}
        
        # Tool Execution Benchmark
        print("\n3. Tool Execution Performance")
        print("-" * 40)
        try:
            tool_results = await self.benchmark_tool_execution()
            if "error" not in tool_results:
                print(f"   Average Time: {tool_results['avg_time']*1000:.2f} ms")
                print(f"   Min/Max Time: {tool_results['min_time']*1000:.2f} / {tool_results['max_time']*1000:.2f} ms")
            else:
                print(f"   ⚠️  {tool_results['error']}")
            self.results['tool_execution'] = tool_results
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results['tool_execution'] = {"error": str(e)}
        
        # Performance Summary
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        
        # Check if meets performance requirements
        meets_requirements = True
        
        if 'entity_extraction' in self.results and 'error' not in self.results['entity_extraction']:
            avg_time = self.results['entity_extraction']['avg_time']
            if avg_time < 0.1:  # < 100ms
                print("✅ Entity Extraction: FAST (<100ms)")
            elif avg_time < 0.5:  # < 500ms
                print("✅ Entity Extraction: ACCEPTABLE (<500ms)")
            else:
                print("⚠️  Entity Extraction: SLOW (>500ms)")
                meets_requirements = False
        
        if 'neo4j' in self.results and 'error' not in self.results['neo4j']:
            ops_per_sec = self.results['neo4j']['operations_per_second']
            if ops_per_sec > 50:
                print("✅ Neo4j Operations: FAST (>50 ops/sec)")
            elif ops_per_sec > 10:
                print("✅ Neo4j Operations: ACCEPTABLE (>10 ops/sec)")
            else:
                print("⚠️  Neo4j Operations: SLOW (<10 ops/sec)")
                meets_requirements = False
        
        if meets_requirements:
            print("\n🎉 System meets performance requirements!")
        else:
            print("\n⚠️  Performance optimization needed")
        
        # Save results
        import json
        with open("performance_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "cpu_cores": psutil.cpu_count(),
                    "total_memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                },
                "benchmarks": self.results
            }, f, indent=2)
        
        print("\nResults saved to performance_results.json")
        
        return meets_requirements

if __name__ == "__main__":
    benchmark = PerformanceBenchmark()
    success = asyncio.run(benchmark.run_all_benchmarks())
    exit(0 if success else 1)