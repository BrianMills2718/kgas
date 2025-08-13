#!/usr/bin/env python3
"""
IC Integration Performance Impact Assessment

Comprehensive analysis of current KGAS performance baselines and 
projected impact of IC (Implementation Correctness) integration.
"""

import os
import sys
import time
import json
import psutil
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append(str(Path(__file__).parent / "src"))

def get_system_baseline() -> Dict[str, Any]:
    """Establish current system performance baseline."""
    
    baseline = {
        "timestamp": datetime.now().isoformat(),
        "system_resources": {
            "cpu_cores": psutil.cpu_count(),
            "total_memory_gb": psutil.virtual_memory().total / (1024**3),
            "available_memory_gb": psutil.virtual_memory().available / (1024**3),
            "memory_usage_percent": psutil.virtual_memory().percent,
            "cpu_usage_percent": psutil.cpu_percent(interval=1.0),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "disk_free_gb": psutil.disk_usage('/').free / (1024**3)
        },
        "service_availability": {},
        "performance_limits": {}
    }
    
    # Check service availability
    services = {
        "neo4j_config": bool(os.getenv("NEO4J_PASSWORD")),
        "gemini_api": bool(os.getenv("GEMINI_API_KEY")),
        "openai_api": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic_api": bool(os.getenv("ANTHROPIC_API_KEY"))
    }
    baseline["service_availability"] = services
    
    # Check if monitoring is available
    try:
        from src.monitoring.system_monitor import get_system_monitor
        monitor = get_system_monitor()
        baseline["monitoring_available"] = True
    except Exception as e:
        baseline["monitoring_available"] = False
        baseline["monitoring_error"] = str(e)
    
    # Check if structured LLM service is available
    try:
        from src.core.structured_llm_service import get_structured_llm_service
        llm_service = get_structured_llm_service()
        baseline["llm_service_available"] = llm_service.available
        if llm_service.available:
            baseline["llm_service_stats"] = llm_service.get_stats()
    except Exception as e:
        baseline["llm_service_available"] = False
        baseline["llm_service_error"] = str(e)
    
    return baseline

def benchmark_llm_performance() -> Dict[str, Any]:
    """Benchmark current LLM service performance."""
    
    benchmark_results = {
        "test_timestamp": datetime.now().isoformat(),
        "llm_performance": {},
        "errors": []
    }
    
    try:
        from src.core.structured_llm_service import get_structured_llm_service
        from pydantic import BaseModel, Field
        
        class TestSchema(BaseModel):
            message: str = Field(description="A test message")
            confidence: float = Field(description="Confidence score", ge=0.0, le=1.0)
            
        llm_service = get_structured_llm_service()
        
        if not llm_service.available:
            benchmark_results["errors"].append("LLM service not available - cannot benchmark")
            return benchmark_results
        
        # Run multiple test requests to get average performance
        test_prompt = "Generate a test response with message 'Performance test' and confidence 0.85"
        response_times = []
        successes = 0
        failures = 0
        
        for i in range(5):  # 5 test requests
            try:
                start_time = time.time()
                result = llm_service.structured_completion(
                    prompt=test_prompt,
                    schema=TestSchema,
                    temperature=0.1
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                successes += 1
                
            except Exception as e:
                failures += 1
                benchmark_results["errors"].append(f"Test {i+1} failed: {str(e)}")
        
        if response_times:
            benchmark_results["llm_performance"] = {
                "total_tests": successes + failures,
                "successful_tests": successes,
                "failed_tests": failures,
                "success_rate": successes / (successes + failures),
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "median_response_time_ms": statistics.median(response_times),
                "response_times": response_times
            }
        
        # Get service stats
        benchmark_results["service_stats"] = llm_service.get_stats()
        
    except Exception as e:
        benchmark_results["errors"].append(f"LLM benchmark failed: {str(e)}")
    
    return benchmark_results

def estimate_ic_overhead() -> Dict[str, Any]:
    """Estimate overhead that IC integration would add."""
    
    ic_estimates = {
        "analysis_timestamp": datetime.now().isoformat(),
        "ic_overhead_estimates": {},
        "assumptions": [],
        "risk_factors": []
    }
    
    # IC integration overhead estimates based on proposed architecture
    ic_estimates["ic_overhead_estimates"] = {
        "additional_llm_calls_per_operation": {
            "contract_analysis": 1,  # One LLM call to analyze tool contracts
            "implementation_verification": 1,  # One LLM call to verify implementation
            "total_per_tool_execution": 2
        },
        "estimated_response_time_overhead_ms": {
            "contract_analysis": 1500,  # ~1.5s for contract analysis
            "implementation_verification": 2000,  # ~2s for implementation verification
            "total_per_tool_execution": 3500  # ~3.5s total overhead
        },
        "memory_overhead_mb": {
            "ic_cache": 50,  # Estimated cache for IC analysis results
            "additional_context": 20,  # Additional context storage
            "llm_service_overhead": 30,  # Additional LLM service memory
            "total": 100  # ~100MB additional memory usage
        },
        "caching_benefits": {
            "contract_analysis_cache_hit_rate": 0.8,  # 80% cache hit rate expected
            "implementation_verification_cache_hit_rate": 0.6,  # 60% cache hit rate
            "effective_overhead_reduction": 0.7  # 70% reduction due to caching
        }
    }
    
    # Assumptions made
    ic_estimates["assumptions"] = [
        "IC analysis requires 2 additional LLM calls per tool execution",
        "Contract analysis takes ~1.5s, implementation verification ~2s",
        "Caching reduces overhead by 70% for repeated operations",
        "Memory overhead is approximately 100MB for IC infrastructure",
        "Network latency for API calls remains constant",
        "Current system has capacity for additional LLM API calls"
    ]
    
    # Risk factors
    ic_estimates["risk_factors"] = [
        "LLM API rate limits may be exceeded with additional calls",
        "Memory usage could increase beyond available capacity",
        "Cache effectiveness depends on operation patterns",
        "Complex tool chains could amplify overhead multiplicatively",
        "Error handling and retry logic adds additional latency",
        "Structured output validation adds processing overhead"
    ]
    
    return ic_estimates

def analyze_pipeline_impact() -> Dict[str, Any]:
    """Analyze impact on typical KGAS pipeline execution."""
    
    pipeline_analysis = {
        "analysis_timestamp": datetime.now().isoformat(),
        "pipeline_scenarios": {},
        "performance_projections": {}
    }
    
    # Define typical pipeline scenarios
    scenarios = {
        "simple_document_processing": {
            "tools": ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23A_NER", "T31_ENTITY_BUILDER"],
            "estimated_current_time_seconds": 15,
            "tool_count": 4
        },
        "complex_multi_document_analysis": {
            "tools": ["T01_PDF_LOADER", "T15A_TEXT_CHUNKER", "T23C_ONTOLOGY_EXTRACTOR", 
                     "T301_MULTI_DOC_FUSION", "T31_ENTITY_BUILDER", "T34_EDGE_BUILDER", 
                     "T68_PAGERANK", "T49_MULTIHOP_QUERY"],
            "estimated_current_time_seconds": 45,
            "tool_count": 8
        },
        "real_time_query_processing": {
            "tools": ["T49_MULTIHOP_QUERY", "T68_PAGERANK"],
            "estimated_current_time_seconds": 3,
            "tool_count": 2
        }
    }
    
    pipeline_analysis["pipeline_scenarios"] = scenarios
    
    # Calculate IC impact for each scenario
    ic_overhead_per_tool = 3.5  # seconds (from estimates above)
    ic_overhead_with_caching = ic_overhead_per_tool * 0.3  # 70% reduction due to caching
    
    for scenario_name, scenario in scenarios.items():
        tool_count = scenario["tool_count"]
        current_time = scenario["estimated_current_time_seconds"]
        
        # Without caching
        ic_overhead_total = tool_count * ic_overhead_per_tool
        new_total_time_no_cache = current_time + ic_overhead_total
        slowdown_factor_no_cache = new_total_time_no_cache / current_time
        
        # With caching
        ic_overhead_total_cached = tool_count * ic_overhead_with_caching
        new_total_time_cached = current_time + ic_overhead_total_cached
        slowdown_factor_cached = new_total_time_cached / current_time
        
        pipeline_analysis["performance_projections"][scenario_name] = {
            "current_time_seconds": current_time,
            "tool_count": tool_count,
            "ic_overhead_no_cache_seconds": ic_overhead_total,
            "ic_overhead_with_cache_seconds": ic_overhead_total_cached,
            "projected_time_no_cache_seconds": new_total_time_no_cache,
            "projected_time_with_cache_seconds": new_total_time_cached,
            "slowdown_factor_no_cache": slowdown_factor_no_cache,
            "slowdown_factor_with_cache": slowdown_factor_cached,
            "acceptable_performance": slowdown_factor_cached < 3.0  # Acceptable if < 3x slowdown
        }
    
    return pipeline_analysis

def assess_resource_constraints() -> Dict[str, Any]:
    """Assess resource constraints and capacity for IC integration."""
    
    resource_assessment = {
        "assessment_timestamp": datetime.now().isoformat(),
        "current_usage": {},
        "capacity_analysis": {},
        "bottleneck_analysis": {}
    }
    
    # Current resource usage
    vm = psutil.virtual_memory()
    resource_assessment["current_usage"] = {
        "memory_used_gb": vm.used / (1024**3),
        "memory_available_gb": vm.available / (1024**3),
        "memory_usage_percent": vm.percent,
        "cpu_usage_percent": psutil.cpu_percent(interval=1.0),
        "active_processes": len(psutil.pids())
    }
    
    # Capacity analysis for IC integration
    ic_memory_overhead = 0.1  # 100MB estimated overhead
    projected_memory_usage = vm.used / (1024**3) + ic_memory_overhead
    memory_headroom = vm.total / (1024**3) - projected_memory_usage
    
    resource_assessment["capacity_analysis"] = {
        "projected_memory_usage_gb": projected_memory_usage,
        "memory_headroom_gb": memory_headroom,
        "memory_capacity_sufficient": memory_headroom > 1.0,  # Need >1GB headroom
        "estimated_additional_cpu_load_percent": 15,  # Additional LLM processing
        "cpu_capacity_assessment": "sufficient" if psutil.cpu_percent() < 70 else "constrained"
    }
    
    # Potential bottlenecks
    bottlenecks = []
    
    if vm.percent > 80:
        bottlenecks.append("High memory usage may limit IC integration")
    
    if psutil.cpu_percent(interval=1.0) > 70:
        bottlenecks.append("High CPU usage may affect IC performance")
    
    # Check API key availability for additional LLM calls
    api_keys_available = sum([
        bool(os.getenv("GEMINI_API_KEY")),
        bool(os.getenv("OPENAI_API_KEY")),
        bool(os.getenv("ANTHROPIC_API_KEY"))
    ])
    
    if api_keys_available == 0:
        bottlenecks.append("No LLM API keys available - IC integration impossible")
    elif api_keys_available == 1:
        bottlenecks.append("Only one LLM API available - rate limiting risk")
    
    resource_assessment["bottleneck_analysis"] = {
        "identified_bottlenecks": bottlenecks,
        "api_keys_available": api_keys_available,
        "rate_limiting_risk": "high" if api_keys_available <= 1 else "medium",
        "overall_risk_level": "high" if len(bottlenecks) > 2 else "medium" if len(bottlenecks) > 0 else "low"
    }
    
    return resource_assessment

def generate_recommendations() -> Dict[str, Any]:
    """Generate recommendations for IC integration based on performance analysis."""
    
    recommendations = {
        "timestamp": datetime.now().isoformat(),
        "performance_recommendations": [],
        "implementation_strategies": [],
        "risk_mitigation": [],
        "monitoring_requirements": []
    }
    
    # Performance recommendations
    recommendations["performance_recommendations"] = [
        "Implement aggressive caching for IC analysis results to achieve 70%+ cache hit rates",
        "Use asynchronous processing for IC analysis to avoid blocking main pipeline execution",
        "Implement tiered IC analysis - quick checks for simple cases, detailed analysis for complex cases",
        "Consider batching IC analysis requests to reduce per-request overhead",
        "Implement circuit breaker pattern to disable IC when performance degrades",
        "Set strict timeouts for IC analysis (max 5s per tool) to prevent pipeline blocking"
    ]
    
    # Implementation strategies
    recommendations["implementation_strategies"] = [
        "Phase 1: Implement basic IC analysis with caching infrastructure",
        "Phase 2: Add performance monitoring and optimization",
        "Phase 3: Implement advanced features like batch analysis and smart caching",
        "Use feature flags to enable/disable IC analysis per tool or pipeline",
        "Implement degraded mode where IC analysis can be skipped under load",
        "Create IC analysis service as separate microservice to isolate performance impact"
    ]
    
    # Risk mitigation
    recommendations["risk_mitigation"] = [
        "Implement comprehensive performance monitoring for IC operations",
        "Set up alerts for IC analysis timeouts and failure rates",
        "Create automated fallback mechanism to disable IC under high load",
        "Implement API rate limiting and quota management for LLM services",
        "Add memory usage monitoring specifically for IC infrastructure",
        "Create performance regression tests for IC integration"
    ]
    
    # Monitoring requirements
    recommendations["monitoring_requirements"] = [
        "Track IC analysis response times (target: <2s average)",
        "Monitor IC cache hit rates (target: >70%)",
        "Track IC analysis success rates (target: >95%)",
        "Monitor additional memory usage from IC infrastructure",
        "Track pipeline slowdown factors (target: <2x with caching)",
        "Monitor LLM API usage and rate limiting",
        "Track IC analysis impact on overall system throughput"
    ]
    
    return recommendations

def main():
    """Generate comprehensive IC integration performance impact assessment."""
    
    print("🔍 IC Integration Performance Impact Assessment")
    print("=" * 60)
    print()
    
    # Collect all assessment data
    assessment_data = {
        "assessment_metadata": {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "assessment_scope": "IC integration performance impact analysis",
            "uncertainty_level": "MEDIUM_RISK"
        }
    }
    
    print("📊 Establishing system baseline...")
    assessment_data["system_baseline"] = get_system_baseline()
    
    print("⚡ Benchmarking LLM performance...")
    assessment_data["llm_benchmark"] = benchmark_llm_performance()
    
    print("📈 Estimating IC overhead...")
    assessment_data["ic_overhead_estimates"] = estimate_ic_overhead()
    
    print("🔄 Analyzing pipeline impact...")
    assessment_data["pipeline_impact"] = analyze_pipeline_impact()
    
    print("💾 Assessing resource constraints...")
    assessment_data["resource_constraints"] = assess_resource_constraints()
    
    print("💡 Generating recommendations...")
    assessment_data["recommendations"] = generate_recommendations()
    
    # Save complete assessment
    output_file = Path("IC_Performance_Impact_Assessment.json")
    with open(output_file, 'w') as f:
        json.dump(assessment_data, f, indent=2, default=str)
    
    print()
    print("=" * 60)
    print("📋 ASSESSMENT SUMMARY")
    print("=" * 60)
    
    # Extract key findings for summary
    baseline = assessment_data["system_baseline"]
    llm_benchmark = assessment_data["llm_benchmark"]
    pipeline_impact = assessment_data["pipeline_impact"]
    resource_constraints = assessment_data["resource_constraints"]
    
    print(f"🖥️  System Resources:")
    print(f"   CPU Cores: {baseline['system_resources']['cpu_cores']}")
    print(f"   Total Memory: {baseline['system_resources']['total_memory_gb']:.1f} GB")
    print(f"   Available Memory: {baseline['system_resources']['available_memory_gb']:.1f} GB")
    print(f"   Current Memory Usage: {baseline['system_resources']['memory_usage_percent']:.1f}%")
    print()
    
    print(f"🤖 LLM Service Performance:")
    if llm_benchmark.get("llm_performance"):
        perf = llm_benchmark["llm_performance"]
        print(f"   Service Available: {baseline.get('llm_service_available', False)}")
        print(f"   Success Rate: {perf.get('success_rate', 0):.1%}")
        print(f"   Average Response Time: {perf.get('avg_response_time_ms', 0):.0f}ms")
    else:
        print(f"   Service Available: {baseline.get('llm_service_available', False)}")
        print(f"   Benchmark Status: Could not complete performance tests")
    print()
    
    print(f"📈 IC Integration Impact Projections:")
    for scenario_name, projection in pipeline_impact["performance_projections"].items():
        print(f"   {scenario_name}:")
        print(f"     Current time: {projection['current_time_seconds']:.1f}s")
        print(f"     With IC (cached): {projection['projected_time_with_cache_seconds']:.1f}s")
        print(f"     Slowdown factor: {projection['slowdown_factor_with_cache']:.1f}x")
        print(f"     Acceptable: {'✅' if projection['acceptable_performance'] else '❌'}")
    print()
    
    print(f"💾 Resource Capacity Assessment:")
    capacity = resource_constraints["capacity_analysis"]
    print(f"   Memory capacity sufficient: {'✅' if capacity['memory_capacity_sufficient'] else '❌'}")
    print(f"   Memory headroom: {capacity['memory_headroom_gb']:.1f} GB")
    print(f"   CPU capacity: {capacity['cpu_capacity_assessment']}")
    print()
    
    bottlenecks = resource_constraints["bottleneck_analysis"]
    print(f"🚨 Risk Assessment:")
    print(f"   Overall risk level: {bottlenecks['overall_risk_level'].upper()}")
    print(f"   API keys available: {bottlenecks['api_keys_available']}")
    print(f"   Rate limiting risk: {bottlenecks['rate_limiting_risk']}")
    if bottlenecks["identified_bottlenecks"]:
        print(f"   Bottlenecks identified:")
        for bottleneck in bottlenecks["identified_bottlenecks"]:
            print(f"     - {bottleneck}")
    print()
    
    print(f"💡 Key Recommendations:")
    recs = assessment_data["recommendations"]["performance_recommendations"][:3]
    for i, rec in enumerate(recs, 1):
        print(f"   {i}. {rec}")
    
    print()
    print(f"📄 Complete assessment saved to: {output_file}")
    print()
    print("🎯 CONCLUSION:")
    
    # Determine overall feasibility
    memory_ok = capacity['memory_capacity_sufficient']
    performance_ok = all(p['acceptable_performance'] for p in pipeline_impact["performance_projections"].values())
    llm_available = baseline.get('llm_service_available', False)
    risk_acceptable = bottlenecks['overall_risk_level'] in ['low', 'medium']
    
    if memory_ok and performance_ok and llm_available and risk_acceptable:
        print("✅ IC integration appears FEASIBLE with proper implementation")
        print("   Key success factors: Aggressive caching, performance monitoring, fallback mechanisms")
    elif not llm_available:
        print("❌ IC integration NOT FEASIBLE - LLM service unavailable")
        print("   Required: Set up API keys and verify LLM service functionality")
    elif not memory_ok:
        print("⚠️  IC integration RISKY - Insufficient memory capacity")
        print("   Required: Increase available memory or optimize memory usage")
    elif not performance_ok:
        print("⚠️  IC integration RISKY - Projected performance degradation too high")
        print("   Required: Implement aggressive caching and performance optimizations")
    else:
        print("⚠️  IC integration RISKY - Multiple constraints identified")
        print("   Required: Address bottlenecks before proceeding with integration")

if __name__ == "__main__":
    main()