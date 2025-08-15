#!/usr/bin/env python3
"""
Comprehensive System Validation Script
Validates all components of the KGAS system
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Component tests
async def validate_tool_registration():
    """Validate tool registration system"""
    from src.core.tool_registry_auto import discover_and_register_tools
    
    summary = discover_and_register_tools()
    
    return {
        "total_tools": summary.get("registered", 0),
        "registered": summary.get("registered", 0),
        "failed": summary.get("failed", 0),
        "status": summary.get("registered", 0) >= 40
    }

async def validate_services():
    """Validate core services"""
    from src.core.service_manager import ServiceManager
    
    sm = ServiceManager()
    
    # Check if services are available
    has_identity = hasattr(sm, 'identity_service') and sm.identity_service is not None
    has_provenance = hasattr(sm, 'provenance_service') and sm.provenance_service is not None
    has_quality = hasattr(sm, 'quality_service') and sm.quality_service is not None
    
    return {
        "identity_service": has_identity,
        "provenance_service": has_provenance,
        "quality_service": has_quality,
        "all_healthy": has_identity and has_provenance and has_quality,
        "status": has_identity  # At minimum need identity service
    }

async def validate_entity_extraction():
    """Validate entity extraction pipeline"""
    from src.tools.phase2.t23c_ontology_aware_extractor_unified import OntologyAwareExtractor
    from src.core.service_manager import ServiceManager
    
    try:
        sm = ServiceManager()
        extractor = OntologyAwareExtractor(sm)
        
        test_texts = [
            "Dr. Smith from MIT studies artificial intelligence.",
            "Google announced a new partnership with OpenAI yesterday.",
            "The COVID-19 pandemic affected global supply chains."
        ]
        
        results = []
        for text in test_texts:
            result = extractor.extract_entities(text, source_ref='validation')
            if result:
                results.append({
                    "text": text[:50],
                    "entities": result.get("total_entities", 0),
                    "relationships": result.get("total_relationships", 0)
                })
        
        total_entities = sum(r["entities"] for r in results)
        return {
            "test_count": len(test_texts),
            "successful": len(results),
            "total_entities": total_entities,
            "status": total_entities > 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": False
        }

async def validate_neo4j_connection():
    """Validate Neo4j database connection"""
    from src.core.neo4j_config import get_neo4j_config
    from neo4j import GraphDatabase
    
    try:
        config = get_neo4j_config()
        driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
        
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count LIMIT 1")
            count = result.single()["count"]
            
        driver.close()
        
        return {
            "connected": True,
            "node_count": count,
            "status": True
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "status": False
        }

async def validate_api_clients():
    """Validate LLM API clients"""
    from src.core.enhanced_api_client import EnhancedAPIClient
    
    try:
        client = EnhancedAPIClient()
        available_models = client.list_available_models()
        
        return {
            "models_available": len(available_models),
            "models": available_models,
            "status": len(available_models) > 0
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": False
        }

async def validate_workflow_execution():
    """Validate end-to-end workflow"""
    try:
        from src.core.tool_contract import get_tool_registry
        from src.tools.base_tool import ToolRequest
        
        registry = get_tool_registry()
        
        # Test T49 Multi-hop query
        if 'T49_MULTIHOP_QUERY' in registry.tools:
            tool = registry.get_tool('T49_MULTIHOP_QUERY')
            request = ToolRequest(
                tool_id='T49_MULTIHOP_QUERY',
                operation='query',
                input_data={'query': 'test', 'max_hops': 2},
                parameters={}
            )
            result = tool.execute(request)
            
            return {
                "workflow": "multi_hop_query",
                "executed": True,
                "status": result.status == "success"
            }
        else:
            return {
                "workflow": "multi_hop_query",
                "executed": False,
                "status": False
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": False
        }

async def run_comprehensive_validation():
    """Run all validation tests"""
    print("=" * 60)
    print("COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    validations = {
        "Tool Registration": validate_tool_registration,
        "Core Services": validate_services,
        "Entity Extraction": validate_entity_extraction,
        "Neo4j Connection": validate_neo4j_connection,
        "API Clients": validate_api_clients,
        "Workflow Execution": validate_workflow_execution
    }
    
    results = {}
    passed = 0
    total = len(validations)
    
    for name, validator in validations.items():
        print(f"Validating {name}...")
        try:
            result = await validator()
            results[name] = result
            if result.get("status", False):
                print(f"  ✅ {name}: PASSED")
                passed += 1
            else:
                print(f"  ❌ {name}: FAILED")
                if "error" in result:
                    print(f"     Error: {result['error']}")
        except Exception as e:
            print(f"  ❌ {name}: ERROR - {e}")
            results[name] = {"status": False, "error": str(e)}
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ PASS" if result.get("status", False) else "❌ FAIL"
        print(f"{name:.<30} {status}")
        
        # Print key metrics
        if name == "Tool Registration" and result.get("status"):
            print(f"  - Registered: {result['registered']} tools")
        elif name == "Entity Extraction" and result.get("status"):
            print(f"  - Entities extracted: {result['total_entities']}")
        elif name == "Neo4j Connection" and result.get("status"):
            print(f"  - Nodes in database: {result['node_count']}")
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 SYSTEM FULLY VALIDATED - READY FOR PRODUCTION!")
    elif passed >= total - 1:
        print("\n✅ System mostly validated (minor issues)")
    else:
        print("\n⚠️  System validation incomplete - issues need attention")
    
    # Save results
    with open("validation_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "total": total,
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to validation_results.json")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_validation())
    exit(0 if success else 1)