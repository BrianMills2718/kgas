#!/usr/bin/env python3
"""
Day 1: Build Real Facade - Get ONE real tool working
Based on successful kill-switch test, build a working facade with real tools
"""

import sys
sys.path.insert(0, '/home/brian/projects/Digimons')

from src.core.service_manager import ServiceManager
from src.tools.phase1.t31_entity_builder_unified import T31EntityBuilderUnified
from src.tools.phase1.t34_edge_builder_unified import T34EdgeBuilderUnified
from src.tools.phase1.t68_pagerank import PageRankCalculator
from src.core.tool_contract import ToolRequest
from src.tools.utils.database_manager import DatabaseSessionManager

class SimpleFacade:
    """Simple facade to demonstrate real tool connectivity"""
    
    def __init__(self, cleanup_on_init=True):
        print("🔧 Initializing SimpleFacade...")
        
        # Initialize service manager
        self.service_manager = ServiceManager()
        
        # Initialize real tools
        self.t31 = T31EntityBuilderUnified(self.service_manager)
        self.t34 = T34EdgeBuilderUnified(self.service_manager)
        self.t68 = PageRankCalculator(self.service_manager)
        
        # Clean database if requested (using T31's driver)
        if cleanup_on_init and hasattr(self.t31, 'driver') and self.t31.driver:
            self.db_manager = DatabaseSessionManager(self.t31.driver)
            self.db_manager.cleanup_all()
            print("   Database cleaned")
        
        print("   ✓ T31 Entity Builder initialized")
        print("   ✓ T34 Edge Builder initialized") 
        print("   ✓ T68 PageRank Calculator initialized")
        print("   SimpleFacade ready!")
    
    def process_entities_only(self, text: str) -> dict:
        """Process text through entity extraction and building only"""
        
        print(f"\n📄 Processing text: {text[:50]}...")
        
        # Step 1: Create synthetic entities (simulating T23C output)
        synthetic_entities = self._extract_synthetic_entities(text)
        print(f"   Step 1: Extracted {len(synthetic_entities)} entities")
        
        # Step 2: Build entities with T31 (REAL)
        entities_result = self._build_entities(synthetic_entities)
        if not entities_result["success"]:
            return {"success": False, "error": f"T31 failed: {entities_result['error']}"}
        print(f"   Step 2: T31 built {len(entities_result['entities'])} entity nodes")
        
        return {
            "success": True,
            "entities": entities_result["entities"],
            "entity_count": len(entities_result["entities"]),
            "processing_method": "simple_facade_entities_only"
        }
    
    def process_full_pipeline(self, text: str) -> dict:
        """Process text through full pipeline: entities → edges → pagerank"""
        
        print(f"\n📄 Processing full pipeline: {text[:50]}...")
        
        # Step 1: Process entities
        entities_result = self.process_entities_only(text)
        if not entities_result["success"]:
            return entities_result
        
        # Step 2: Create synthetic relationships
        synthetic_relationships = self._extract_synthetic_relationships(text, entities_result["entities"])
        print(f"   Step 3: Created {len(synthetic_relationships)} synthetic relationships")
        
        # Step 3: Build edges with T34 (REAL)
        edges_result = self._build_edges(synthetic_relationships)
        if not edges_result["success"]:
            return {"success": False, "error": f"T34 failed: {edges_result['error']}"}
        print(f"   Step 4: T34 built {len(edges_result['edges'])} edges")
        
        # Step 4: Calculate PageRank with T68 (REAL)
        pagerank_result = self._calculate_pagerank()
        if not pagerank_result["success"]:
            return {"success": False, "error": f"T68 failed: {pagerank_result['error']}"}
        print(f"   Step 5: T68 calculated PageRank for {len(pagerank_result['pagerank'])} nodes")
        
        return {
            "success": True,
            "entities": entities_result["entities"],
            "edges": edges_result["edges"],
            "pagerank": pagerank_result["pagerank"],
            "entity_count": len(entities_result["entities"]),
            "edge_count": len(edges_result["edges"]),
            "pagerank_count": len(pagerank_result["pagerank"]),
            "processing_method": "simple_facade_full_pipeline"
        }
    
    def _extract_synthetic_entities(self, text: str) -> list:
        """Create synthetic entities (simulates T23C output)"""
        # Simple entity extraction for testing
        entities = []
        
        # Extract simple patterns
        import re
        
        # Company patterns
        company_matches = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+Inc\.|\s+Corporation|\s+Corp\.)?)\b', text)
        for i, match in enumerate(company_matches[:3]):  # Limit to 3
            if len(match) > 3 and match not in [e["text"] for e in entities]:
                entities.append({
                    "text": match,
                    "entity_type": "ORGANIZATION",
                    "start_pos": text.find(match),
                    "end_pos": text.find(match) + len(match),
                    "confidence": 0.85,
                    "entity_id": f"org_{i:03d}",
                    "canonical_name": match,
                    "source_chunk": "synthetic_chunk_001"
                })
        
        # Person patterns  
        person_matches = re.findall(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b', text)
        for i, match in enumerate(person_matches[:3]):  # Limit to 3
            if match not in [e["text"] for e in entities]:
                entities.append({
                    "text": match,
                    "entity_type": "PERSON",
                    "start_pos": text.find(match),
                    "end_pos": text.find(match) + len(match),
                    "confidence": 0.90,
                    "entity_id": f"person_{i:03d}",
                    "canonical_name": match,
                    "source_chunk": "synthetic_chunk_001"
                })
        
        # Location patterns
        location_matches = re.findall(r'\b([A-Z][a-z]+(?:,\s+[A-Z][a-z]+)?)\b', text)
        for i, match in enumerate(location_matches[:2]):  # Limit to 2
            if len(match) > 3 and "Inc" not in match and match not in [e["text"] for e in entities]:
                entities.append({
                    "text": match,
                    "entity_type": "GPE", 
                    "start_pos": text.find(match),
                    "end_pos": text.find(match) + len(match),
                    "confidence": 0.80,
                    "entity_id": f"location_{i:03d}",
                    "canonical_name": match,
                    "source_chunk": "synthetic_chunk_001"
                })
        
        return entities
    
    def _extract_synthetic_relationships(self, text: str, entities: list) -> list:
        """Create synthetic relationships between entities"""
        relationships = []
        
        # Check entity format and create lookup
        if entities and isinstance(entities[0], dict):
            # T31 output format uses "canonical_name" instead of "text"
            entity_lookup = {}
            for e in entities:
                # Try different possible key names
                entity_name = e.get("canonical_name") or e.get("text") or e.get("surface_form", "")
                if entity_name:
                    entity_lookup[entity_name] = e
        else:
            entity_lookup = {}
        
        # Simple pattern-based relationships
        patterns = [
            (r'([^,]+),\s+led by(?:\s+CEO)?\s+([^,]+)', "LED_BY"),
            (r'([^,]+)\s+is headquartered in\s+([^,\.]+)', "HEADQUARTERED_IN"),
            (r'([^,]+)\s+was founded by\s+([^,\.]+)', "FOUNDED_BY"),
            (r'([^,]+)\s+acquired\s+([^,\.]+)', "ACQUIRED"),
            (r'([^,]+)\s+competes with\s+([^,\.]+)', "COMPETES_WITH")
        ]
        
        for pattern, rel_type in patterns:
            import re
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                subject_text = match[0].strip()
                object_text = match[1].strip()
                
                # Find matching entities
                subject_entity = self._find_best_entity_match(subject_text, entity_lookup)
                object_entity = self._find_best_entity_match(object_text, entity_lookup)
                
                if subject_entity and object_entity and subject_entity != object_entity:
                    # Create T34-compatible relationship format
                    relationship = {
                        "subject": {
                            "text": subject_entity.get("canonical_name") or subject_entity.get("text", subject_text),
                            "entity_id": subject_entity.get("entity_id"),
                            "entity_type": subject_entity.get("entity_type")
                        },
                        "object": {
                            "text": object_entity.get("canonical_name") or object_entity.get("text", object_text),
                            "entity_id": object_entity.get("entity_id"),
                            "entity_type": object_entity.get("entity_type")
                        },
                        "relationship_type": rel_type,
                        "confidence": 0.85,
                        "extraction_method": "pattern_based",
                        "evidence_text": f"{subject_text} {rel_type.lower().replace('_', ' ')} {object_text}",
                        "relationship_id": f"rel_{len(relationships):03d}"
                    }
                    relationships.append(relationship)
        
        return relationships
    
    def _find_best_entity_match(self, text: str, entity_lookup: dict) -> dict:
        """Find best matching entity for text fragment"""
        # Exact match
        if text in entity_lookup:
            return entity_lookup[text]
        
        # Partial match
        for entity_text, entity in entity_lookup.items():
            if entity_text.lower() in text.lower() or text.lower() in entity_text.lower():
                return entity
        
        return None
    
    def _build_entities(self, synthetic_entities: list) -> dict:
        """Build entities using real T31 tool"""
        try:
            request = ToolRequest(input_data={"mentions": synthetic_entities})
            result = self.t31.execute(request)
            
            if result.status == "success":
                return {
                    "success": True,
                    "entities": result.data.get("entities", []),
                    "confidence": result.data.get("confidence", 0.0)
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message or "T31 execution failed"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _build_edges(self, synthetic_relationships: list) -> dict:
        """Build edges using real T34 tool"""
        try:
            # Create request with proper format for T34
            request = ToolRequest(
                input_data={
                    "relationships": synthetic_relationships,
                    "source_refs": ["synthetic_facade_processing"]
                },
                options={"verify_entities": True}
            )
            
            # WORKAROUND: T34 expects request.parameters, add it manually
            # This is a compatibility fix - T34 hasn't been updated to new interface
            class ParameterRequest:
                def __init__(self, base_request):
                    self.input_data = base_request.input_data
                    self.options = base_request.options
                    self.parameters = base_request.options  # Map options to parameters
                    self.workflow_id = base_request.workflow_id
                    self.request_id = base_request.request_id
                    self.timestamp = base_request.timestamp
            
            request = ParameterRequest(request)
            result = self.t34.execute(request)
            
            if result.status == "success":
                return {
                    "success": True,
                    "edges": result.data.get("edges", []),
                    "confidence": result.data.get("confidence", 0.0)
                }
            else:
                return {
                    "success": False,
                    "error": result.error_message or "T34 execution failed"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_pagerank(self) -> dict:
        """Calculate PageRank using real T68 tool"""
        try:
            # Use ToolRequest interface for T68
            request = ToolRequest(
                input_data={"graph_ref": "neo4j://main_graph"}
            )
            
            # Add parameters for compatibility
            class ParameterRequest:
                def __init__(self, base_request):
                    self.input_data = base_request.input_data
                    self.options = base_request.options
                    self.parameters = base_request.options
                    self.workflow_id = base_request.workflow_id
                    self.request_id = base_request.request_id
                    self.timestamp = base_request.timestamp
            
            request = ParameterRequest(request)
            result = self.t68.execute(request)
            
            # Debug: print actual result structure
            print(f"   DEBUG: T68 result type: {type(result)}")
            print(f"   DEBUG: T68 result status: {getattr(result, 'status', 'no status attr')}")
            print(f"   DEBUG: T68 result data keys: {list(result.data.keys()) if hasattr(result, 'data') and result.data else 'no data'}")
            
            # Handle ToolResult format
            if hasattr(result, 'status') and result.status == "success":
                pagerank_data = result.data if hasattr(result, 'data') else {}
                
                return {
                    "success": True,
                    "pagerank": pagerank_data,
                    "confidence": 0.8  # Default confidence
                }
            else:
                error_msg = getattr(result, 'error_message', 'T68 execution failed')
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            print(f"   DEBUG: T68 exception: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


def test_real_facade():
    """Test the real facade with actual tools"""
    
    print("=" * 70)
    print("DAY 1: REAL FACADE TEST")
    print("=" * 70)
    
    try:
        # Initialize facade
        facade = SimpleFacade(cleanup_on_init=True)
        
        # Test document
        test_text = """
        Apple Inc., led by CEO Tim Cook, is headquartered in Cupertino, California.
        The company was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
        Apple competes with Microsoft Corporation in various technology markets.
        """
        
        print("\n🧪 TEST 1: Entities Only Processing")
        entities_result = facade.process_entities_only(test_text)
        
        if entities_result["success"]:
            print(f"✅ Entities test passed: {entities_result['entity_count']} entities created")
        else:
            print(f"❌ Entities test failed: {entities_result['error']}")
            return False
        
        print("\n🧪 TEST 2: Full Pipeline Processing")
        full_result = facade.process_full_pipeline(test_text)
        
        if full_result["success"]:
            print(f"✅ Full pipeline passed:")
            print(f"   - Entities: {full_result['entity_count']}")
            print(f"   - Edges: {full_result['edge_count']}")
            print(f"   - PageRank nodes: {full_result['pagerank_count']}")
        else:
            print(f"❌ Full pipeline failed: {full_result['error']}")
            return False
        
        # Validation checks
        success_checks = {
            "Entities created": full_result['entity_count'] > 0,
            "Edges created": full_result['edge_count'] > 0, 
            "PageRank calculated": full_result['pagerank_count'] > 0,
            "Pipeline completes": full_result['success'],
            "Tools integrate": True  # If we got here, tools integrated
        }
        
        print("\n" + "=" * 70)
        print("SUCCESS VALIDATION:")
        print("=" * 70)
        
        all_passed = True
        for check, passed in success_checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check}")
            if not passed:
                all_passed = False
        
        print("\n" + "=" * 70)
        if all_passed:
            print("🎉 DAY 1 SUCCESS: Real facade working!")
            print("   → T31, T34, T68 integrate successfully")
            print("   → Ready for Day 2: Connect T23C → T31")
        else:
            print("⚠️  Day 1 incomplete - fix issues before Day 2")
        print("=" * 70)
        
        return all_passed
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_facade()
    sys.exit(0 if success else 1)