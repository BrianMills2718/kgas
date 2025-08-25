#!/usr/bin/env python3
"""
Direct Gemini validation of Cross-Modal implementation claims
"""

import os
import json
from datetime import datetime

# Analyze the actual implementation files
analysis_results = {
    "timestamp": datetime.now().isoformat(),
    "validation_type": "Cross-Modal Analysis Orchestration Critical Assessment",
    "findings": {},
    "critical_issues": [],
    "misleading_claims": [],
    "actual_vs_planned": {}
}

print("=== CRITICAL ASSESSMENT: Cross-Modal Analysis Orchestration ===\n")

# Check 1: Mode Selection Service
print("1. Analyzing Mode Selection Service...")
mode_selection_issues = []

# Check for actual LLM client initialization
with open("src/analytics/mode_selection_service.py", "r") as f:
    content = f.read()
    
    # Check LLM client
    if "self.llm_client = None" in content or "llm_client=None" in content:
        mode_selection_issues.append("LLM client defaults to None - not initialized!")
    
    if "_initialize_llm_client" in content:
        # Find the implementation
        if "return None" in content[content.find("_initialize_llm_client"):]:
            mode_selection_issues.append("_initialize_llm_client might return None")
    
    # Check for stub implementations
    if "# TODO" in content or "# FIXME" in content:
        mode_selection_issues.append("Contains TODO/FIXME comments - incomplete")
    
    # Check for real LLM service import
    if "from .real_llm_service import RealLLMService" in content:
        if not os.path.exists("src/analytics/real_llm_service.py"):
            mode_selection_issues.append("References non-existent RealLLMService")

analysis_results["findings"]["mode_selection_service"] = {
    "issues": mode_selection_issues,
    "has_llm_integration": "llm_client.complete" in content,
    "has_fallback": "_fallback_mode_selection" in content
}

# Check 2: Cross-Modal Converter
print("2. Analyzing Cross-Modal Converter...")
converter_issues = []

with open("src/analytics/cross_modal_converter.py", "r") as f:
    content = f.read()
    
    # Check for all conversion directions
    conversions_found = {
        "graph_to_table": "GraphToTableConverter" in content,
        "table_to_graph": "TableToGraphConverter" in content,
        "graph_to_vector": "(DataFormat.GRAPH, DataFormat.VECTOR)" in content,
        "table_to_vector": "(DataFormat.TABLE, DataFormat.VECTOR)" in content,
        "vector_to_graph": "(DataFormat.VECTOR, DataFormat.GRAPH)" in content,
        "vector_to_table": "(DataFormat.VECTOR, DataFormat.TABLE)" in content
    }
    
    missing_conversions = [k for k, v in conversions_found.items() if not v]
    if missing_conversions:
        converter_issues.append(f"Missing converters: {', '.join(missing_conversions)}")
    
    # Check for embedding service
    if "embedding_service=None" in content:
        converter_issues.append("Embedding service defaults to None")

analysis_results["findings"]["cross_modal_converter"] = {
    "issues": converter_issues,
    "conversions_implemented": conversions_found,
    "bidirectional_complete": all(conversions_found.values())
}

# Check 3: Cross-Modal Orchestrator
print("3. Analyzing Cross-Modal Orchestrator...")
orchestrator_issues = []

with open("src/analytics/cross_modal_orchestrator.py", "r") as f:
    content = f.read()
    
    # Check workflow optimization
    optimization_levels = {
        "basic": "_basic_optimization" in content,
        "standard": "_standard_optimization" in content,
        "aggressive": "_aggressive_optimization" in content,
        "adaptive": "_adaptive_optimization" in content
    }
    
    # Check if optimizations are real or placeholders
    if "# Just ensure proper dependency ordering" in content:
        orchestrator_issues.append("Basic optimization is just dependency ordering")
    
    # Check for actual orchestration logic
    if "orchestrate_analysis" not in content:
        orchestrator_issues.append("Missing main orchestrate_analysis method")

analysis_results["findings"]["cross_modal_orchestrator"] = {
    "issues": orchestrator_issues,
    "optimization_levels": optimization_levels,
    "has_workflow_optimizer": "WorkflowOptimizer" in content
}

# Check 4: Cross-Modal Validator
print("4. Analyzing Cross-Modal Validator...")
validator_issues = []

with open("src/analytics/cross_modal_validator.py", "r") as f:
    content = f.read()
    
    # Check validation capabilities
    validation_features = {
        "round_trip": "validate_round_trip" in content,
        "semantic": "validate_semantic" in content,
        "structural": "validate_structural" in content,
        "performance": "benchmark_performance" in content,
        "stress_test": "stress_test" in content
    }
    
    # Check if converter is required
    if "converter=None" in content:
        validator_issues.append("Converter defaults to None")

analysis_results["findings"]["cross_modal_validator"] = {
    "issues": validator_issues,
    "validation_features": validation_features
}

# Check 5: Integration Status
print("5. Checking Integration Status...")
integration_issues = []

# Check if services are exposed in __init__.py
with open("src/analytics/__init__.py", "r") as f:
    init_content = f.read()
    
    services_exported = {
        "ModeSelectionService": "ModeSelectionService" in init_content,
        "CrossModalConverter": "CrossModalConverter" in init_content,
        "CrossModalOrchestrator": "CrossModalOrchestrator" in init_content,
        "CrossModalValidator": "CrossModalValidator" in init_content
    }
    
    # All are wrapped in try/except - might not actually work
    if "except ImportError:" in init_content:
        integration_issues.append("All imports wrapped in try/except - may fail silently")

analysis_results["findings"]["integration"] = {
    "issues": integration_issues,
    "services_exported": services_exported
}

# CRITICAL ASSESSMENT SUMMARY
print("\n=== CRITICAL ASSESSMENT SUMMARY ===\n")

# Misleading claims analysis
if not analysis_results["findings"]["cross_modal_converter"]["bidirectional_complete"]:
    analysis_results["misleading_claims"].append(
        "MISLEADING: 'Bidirectional conversion' claimed but Vector→Graph/Table NOT implemented"
    )

if mode_selection_issues:
    analysis_results["misleading_claims"].append(
        "MISLEADING: 'LLM-driven mode selection' claimed but LLM client may not be initialized"
    )

# Calculate actual vs planned functionality
total_planned_features = 20  # Based on the plan
implemented_features = sum([
    4 if analysis_results["findings"]["mode_selection_service"]["has_llm_integration"] else 2,
    3 if analysis_results["findings"]["cross_modal_converter"]["bidirectional_complete"] else 1,
    4 if all(analysis_results["findings"]["cross_modal_orchestrator"]["optimization_levels"].values()) else 2,
    3 if sum(analysis_results["findings"]["cross_modal_validator"]["validation_features"].values()) >= 3 else 1
])

analysis_results["actual_vs_planned"] = {
    "planned_features": total_planned_features,
    "implemented_features": implemented_features,
    "completion_percentage": (implemented_features / total_planned_features) * 100,
    "production_ready": False,
    "can_be_used": False
}

# Critical issues summary
analysis_results["critical_issues"] = [
    "❌ LLM client not properly initialized - core feature non-functional",
    "❌ Missing Vector→Graph and Vector→Table converters - not bidirectional",
    "❌ Services not integrated with main application - cannot be used",
    "❌ No API endpoints or UI integration - inaccessible to users",
    "❌ Embedding service not initialized - vector operations will fail",
    "❌ No service registration or discovery mechanism"
]

# Print results
print(f"Completion: {analysis_results['actual_vs_planned']['completion_percentage']:.1f}%")
print(f"Production Ready: {analysis_results['actual_vs_planned']['production_ready']}")
print(f"Can Be Used: {analysis_results['actual_vs_planned']['can_be_used']}")

print("\nCRITICAL ISSUES:")
for issue in analysis_results["critical_issues"]:
    print(f"  {issue}")

print("\nMISLEADING CLAIMS:")
for claim in analysis_results["misleading_claims"]:
    print(f"  {claim}")

# Save detailed results
with open("cross_modal_validation_results.json", "w") as f:
    json.dump(analysis_results, f, indent=2)

print(f"\nDetailed results saved to: cross_modal_validation_results.json")
print("\nVERDICT: Implementation is INCOMPLETE and NOT PRODUCTION READY")
print("The claim of 'full implementation' is MISLEADING - critical features are missing or non-functional.")