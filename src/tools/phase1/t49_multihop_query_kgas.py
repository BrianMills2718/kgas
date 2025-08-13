"""T49 Multi-hop Query - Contract-First Implementation

This tool implements the KGASTool interface for performing multi-hop queries
on the Neo4j graph to answer natural language questions.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass
import re
import string

from src.core.tool_contract import (
    KGASTool, ToolRequest, ToolResult, 
    ToolValidationResult
)
from src.core.confidence_scoring.data_models import ConfidenceScore
from src.core.service_manager import ServiceManager
from src.tools.phase1.query_intent_analyzer import QueryIntentAnalyzer, ExpectedAnswerType
from src.core.standard_config import get_database_uri
import os

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Driver = None

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of multi-hop query."""
    results: List[Dict[str, Any]]
    query_entities: List[Dict[str, Any]]
    paths_found: int
    total_paths_explored: int
    execution_time: float


class T49MultiHopQueryKGAS(KGASTool):
    """Multi-hop query implementing contract-first interface."""
    
    def __init__(self, service_manager: ServiceManager):
        super().__init__(tool_id="T49", tool_name="Multi-hop Query")
        self.service_manager = service_manager
        self.description = "Performs multi-hop queries on graph to answer questions"
        self.category = "graph_analysis"
        self.version = "1.0.0"
        
        # Query configuration
        self.max_hops_limit = 3
        self.default_result_limit = 10
        self.min_path_weight = 0.01
        self.pagerank_boost_factor = 2.0
        
        # Initialize Neo4j connection
        self.driver = None
        self._initialize_neo4j_connection()
        
        # Initialize query intent analyzer
        self.intent_analyzer = QueryIntentAnalyzer()
        
    def _initialize_neo4j_connection(self):
        """Initialize Neo4j connection."""
        if not NEO4J_AVAILABLE:
            logger.warning("Neo4j driver not available. Install with: pip install neo4j")
            return
        
        try:
            # Load environment variables 
            from dotenv import load_dotenv
            from pathlib import Path
            env_path = Path(__file__).parent.parent.parent.parent / '.env'
            load_dotenv(env_path)
            
            # Get Neo4j settings from environment
            neo4j_uri = get_database_uri()
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', '')
            
            self.driver = GraphDatabase.driver(
                neo4j_uri, 
                auth=(neo4j_user, neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            logger.info("Neo4j connection established for T49")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def execute(self, request: ToolRequest) -> ToolResult:
        """Execute multi-hop query."""
        start_time = datetime.now()
        
        try:
            # Validate requirements
            if not self.driver:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "Neo4j not available",
                        "error_details": "Neo4j connection required for multi-hop queries"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="Neo4j not available"
                )
            
            # Extract parameters
            query_text = request.input_data.get("query_text", "")
            max_hops = request.input_data.get("max_hops", 2)
            result_limit = request.input_data.get("result_limit", self.default_result_limit)
            
            if not query_text:
                return ToolResult(
                    status="error",
                    data=None,
                    confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                    metadata={
                        "tool_id": self.tool_id,
                        "error_message": "No query provided",
                        "error_details": "query_text is required"
                    },
                    provenance=None,
                    request_id=request.request_id,
                    execution_time=0.0,
                    error_details="No query provided"
                )
            
            # Validate parameters
            max_hops = min(max(max_hops, 1), self.max_hops_limit)
            result_limit = min(max(result_limit, 1), 100)
            
            # Start provenance tracking
            op_id = self.service_manager.provenance_service.start_operation(
                tool_id=self.tool_id,
                operation_type="multihop_query",
                inputs=[],
                parameters={
                    "workflow_id": request.workflow_id,
                    "query_text": query_text,
                    "max_hops": max_hops,
                    "result_limit": result_limit
                }
            )
            
            # Execute query
            result = self._execute_query(query_text, max_hops, result_limit)
            
            # Generate natural language answer
            answer = self._generate_natural_language_answer(query_text, result.results, result.query_entities)
            
            # Create result data with enhanced answer
            result_data = {
                "answer": answer,  # NEW: Natural language answer
                "results": result.results,
                "query_entities": result.query_entities,
                "paths_found": result.paths_found,
                "total_paths_explored": result.total_paths_explored,
                "execution_time": result.execution_time,
                "query_metadata": {
                    "query_text": query_text,
                    "max_hops": max_hops,
                    "result_limit": result_limit,
                    "actual_results": len(result.results)
                },
                "answer_confidence": min(0.9, 0.3 + (len(result.results) * 0.1))  # Answer confidence
            }
            
            # Complete provenance
            self.service_manager.provenance_service.complete_operation(
                operation_id=op_id,
                outputs=[f"result_{i}" for i in range(len(result.results))],
                success=True,
                metadata={
                    "paths_found": result.paths_found,
                    "query_entities": len(result.query_entities),
                    "results_returned": len(result.results)
                }
            )
            
            # Calculate confidence based on results
            confidence_value = min(0.9, 0.5 + (len(result.results) * 0.1))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ToolResult(
                status="success",
                data=result_data,
                confidence=ConfidenceScore(value=confidence_value, evidence_weight=max(1, result.paths_found)),
                metadata={
                    "tool_version": self.version,
                    "query_complete": True
                },
                provenance=op_id,
                request_id=request.request_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in {self.tool_id}: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            return ToolResult(
                status="error",
                data=None,
                confidence=ConfidenceScore(value=0.0, evidence_weight=1),
                metadata={
                    "tool_id": self.tool_id,
                    "error_message": str(e),
                    "error_details": str(e)
                },
                provenance=None,
                request_id=request.request_id,
                execution_time=execution_time,
                error_details=str(e)
            )
    
    def _execute_query(self, query_text: str, max_hops: int, result_limit: int) -> QueryResult:
        """Execute the multi-hop query."""
        exec_start = datetime.now()
        
        # Extract entities from query
        query_entities = self._extract_query_entities(query_text)
        
        if not query_entities:
            return QueryResult(
                results=[],
                query_entities=[],
                paths_found=0,
                total_paths_explored=0,
                execution_time=0.0
            )
        
        # Find paths for each hop level
        all_paths = []
        total_explored = 0
        
        with self.driver.session() as session:
            for hop in range(1, max_hops + 1):
                paths = self._find_paths(session, query_entities, hop)
                all_paths.extend(paths)
                total_explored += len(paths)
                
                # Early exit if we have enough results
                if len(all_paths) >= result_limit * 2:
                    break
        
        # Rank and format results
        ranked_results = self._rank_results(all_paths, query_entities, result_limit, query_text)
        
        exec_time = (datetime.now() - exec_start).total_seconds()
        
        return QueryResult(
            results=ranked_results,
            query_entities=[{"text": e["text"], "type": e["type"]} for e in query_entities],
            paths_found=len(all_paths),
            total_paths_explored=total_explored,
            execution_time=exec_time
        )
    
    def _extract_query_entities(self, query_text: str) -> List[Dict[str, Any]]:
        """Extract entities from query text with improved matching."""
        entities = []
        
        # Analyze query intent
        query_lower = query_text.lower()
        looking_for_person = any(word in query_lower for word in ['who', 'person', 'people'])
        looking_for_org = any(word in query_lower for word in ['what', 'organization', 'company', 'university'])
        looking_for_place = any(word in query_lower for word in ['where', 'location', 'place', 'city'])
        
        logger.debug(f"[T49] Extracting entities from query: {query_text}")
        logger.debug(f"[T49] Looking for - Person: {looking_for_person}, Org: {looking_for_org}, Place: {looking_for_place}")
        
        # First try: Enhanced fuzzy matching for theory-related queries
        entities = self._fuzzy_match_entities(query_text)
        if entities:
            logger.debug(f"[T49] Found entities via fuzzy matching: {entities}")
            return entities
        
        with self.driver.session() as session:
            # Extract meaningful phrases from query
            # Remove only the most common question words, but keep prepositions that might be part of entity names
            stop_words = {'who', 'what', 'where', 'when', 'why', 'how', 'does', 'is', 'are', 
                         'the', 'a', 'an', 'about', 'tell', 'me', 'with'}
            
            # Keep all words for entity extraction
            # Strip punctuation from words
            all_words = query_text.split()
            # Clean words by removing trailing punctuation
            cleaned_words = []
            for word in all_words:
                # Remove trailing punctuation but keep internal punctuation
                cleaned_word = word.rstrip(string.punctuation)
                if cleaned_word:  # Only add non-empty words
                    cleaned_words.append(cleaned_word)
            all_words = cleaned_words
            
            logger.debug(f"[T49] Cleaned words: {all_words}")
            
            # Create a filtered list for combinations but use all_words for single word extraction
            filtered_words = [w for w in all_words if w.lower() not in stop_words]
            potential_names = []
            
            # Single words (capitalized or specific words like 'Stanford')
            for i, word in enumerate(all_words):
                if len(word) > 2 and (word[0].isupper() or word.lower() in ['stanford', 'university']):
                    if word not in potential_names:  # Avoid duplicates
                        potential_names.append(word)
            
            # Two-word combinations (using all words, not filtered)
            for i in range(len(all_words) - 1):
                word1, word2 = all_words[i], all_words[i+1]
                # Skip if both are stop words
                if word1.lower() in stop_words and word2.lower() in stop_words:
                    continue
                # Include if either word is capitalized or is a key word
                if (word1[0].isupper() or word2[0].isupper() or 
                    word1.lower() in ['stanford', 'university'] or 
                    word2.lower() in ['stanford', 'university']):
                    combo = f"{word1} {word2}"
                    if combo not in potential_names:
                        potential_names.append(combo)
            
            # Three-word combinations
            for i in range(len(all_words) - 2):
                word1, word2, word3 = all_words[i], all_words[i+1], all_words[i+2]
                # Skip if all are stop words
                if all(w.lower() in stop_words for w in [word1, word2, word3]):
                    continue
                # Include if any word is capitalized or is a key word
                if any(w[0].isupper() or w.lower() in ['stanford', 'university'] 
                       for w in [word1, word2, word3]):
                    combo = f"{word1} {word2} {word3}"
                    if combo not in potential_names:
                        potential_names.append(combo)
            
            # Special handling for common patterns
            # "at [Organization]" pattern
            for i in range(len(all_words) - 1):
                if all_words[i].lower() == 'at' and i+1 < len(all_words):
                    org_name = all_words[i+1]
                    # Also check for multi-word organizations after 'at'
                    if i+2 < len(all_words) and all_words[i+2][0].isupper():
                        org_name = f"{all_words[i+1]} {all_words[i+2]}"
                    if org_name not in potential_names:
                        potential_names.append(org_name)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_names = []
            for name in potential_names:
                if name not in seen:
                    seen.add(name)
                    unique_names.append(name)
            potential_names = unique_names
            
            logger.debug(f"[T49] Potential entity names: {potential_names}")
            
            # Search for entities with better matching
            seen_ids = set()
            for name in potential_names:
                if len(name) < 2:  # Skip very short strings
                    continue
                
                # Build type filter based on the entity name itself, not just query intent
                # This allows finding both people AND organizations in the same query
                name_lower = name.lower()
                type_filter = ""
                
                # Check if the name looks like an organization
                org_keywords = [
                    'university', 'company', 'corporation', 'institute', 'college', 
                    'organization', 'corp', 'inc', 'ltd', 'limited', 'llc', 'plc', 
                    'gmbh', 'associates', 'partners', 'group', 'foundation', 'bank',
                    'solutions', 'technologies', 'systems', 'services', 'consulting'
                ]
                if any(org_word in name_lower for org_word in org_keywords):
                    # This name is likely an organization
                    type_filter = "AND e.entity_type IN ['ORGANIZATION', 'ORG', 'GPE']"
                # Check if it looks like a person name (capitalized multi-word without org indicators)
                elif name[0].isupper() and len(name.split()) >= 2 and not any(org_word in name_lower for org_word in org_keywords):
                    # Likely a person name
                    type_filter = "AND e.entity_type IN ['PERSON', 'PER']"
                else:
                    # Not sure - use query intent but don't filter if looking for multiple types
                    if looking_for_person and not looking_for_org:
                        type_filter = "AND e.entity_type IN ['PERSON', 'PER']"
                    elif looking_for_org and not looking_for_person:
                        type_filter = "AND e.entity_type IN ['ORGANIZATION', 'ORG', 'GPE']"
                    elif looking_for_place:
                        type_filter = "AND e.entity_type IN ['LOCATION', 'LOC', 'GPE']"
                    # else: no filter when looking for multiple types
                
                # More precise matching - look for exact matches first
                logger.debug(f"[T49] Searching for exact match: '{name}' with filter: {type_filter}")
                result = session.run(f"""
                    MATCH (e:Entity)
                    WHERE toLower(e.canonical_name) = toLower($name)
                    {type_filter}
                    RETURN e.entity_id AS id, e.canonical_name AS name, 
                           e.entity_type AS type, e.confidence AS confidence
                    LIMIT 3
                """, name=name)
                
                found_exact = False
                records = list(result)
                logger.debug(f"[T49] Found {len(records)} exact matches for '{name}'")
                for record in records:
                    if record["id"] not in seen_ids:
                        entity = {
                            "id": record["id"],
                            "text": record["name"],
                            "type": record["type"] or "UNKNOWN",
                            "confidence": record["confidence"] or 0.5,
                            "matched_text": name,
                            "match_quality": 1.0  # Exact match
                        }
                        entities.append(entity)
                        seen_ids.add(record["id"])
                        found_exact = True
                
                # If no exact match, try contains (but be more selective)
                if not found_exact and len(name) > 3:  # Only for longer names
                    result = session.run(f"""
                        MATCH (e:Entity)
                        WHERE toLower(e.canonical_name) CONTAINS toLower($name)
                        {type_filter}
                        RETURN e.entity_id AS id, e.canonical_name AS name, 
                               e.entity_type AS type, e.confidence AS confidence
                        ORDER BY SIZE(e.canonical_name)
                        LIMIT 3
                    """, name=name)
                    
                    for record in result:
                        if record["id"] not in seen_ids:
                            # Only add if the match is reasonable (not too long compared to search term)
                            if len(record["name"]) <= len(name) * 2:
                                entity = {
                                    "id": record["id"],
                                    "text": record["name"],
                                    "type": record["type"] or "UNKNOWN",
                                    "confidence": record["confidence"] or 0.5,
                                    "matched_text": name,
                                    "match_quality": 0.8  # Partial match
                                }
                                entities.append(entity)
                                seen_ids.add(record["id"])
        
        # Sort by match quality and length of matched text (prefer exact matches and longer phrases)
        entities.sort(key=lambda e: (e["match_quality"], len(e["matched_text"])), reverse=True)
        
        logger.debug(f"[T49] Found {len(entities)} entities before limiting")
        return entities[:10]  # Limit to top 10 entities
    
    def _find_paths(self, session, query_entities: List[Dict], hop_count: int) -> List[Dict[str, Any]]:
        """Find paths of specified hop count from query entities."""
        paths = []
        
        for entity in query_entities:
            if hop_count == 1:
                # Direct relationships
                query = """
                    MATCH (e:Entity {entity_id: $entity_id})-[r]-(t:Entity)
                    WHERE e.entity_id <> t.entity_id
                    RETURN e, r, t, 
                           e.pagerank_score AS start_score,
                           t.pagerank_score AS end_score,
                           r.weight AS edge_weight
                    LIMIT 50
                """
            elif hop_count == 2:
                # Two-hop paths
                query = """
                    MATCH (e:Entity {entity_id: $entity_id})-[r1]-(m:Entity)-[r2]-(t:Entity)
                    WHERE e.entity_id <> m.entity_id AND m.entity_id <> t.entity_id AND e.entity_id <> t.entity_id
                    RETURN e, r1, m, r2, t,
                           e.pagerank_score AS start_score,
                           m.pagerank_score AS mid_score,
                           t.pagerank_score AS end_score,
                           r1.weight AS edge1_weight,
                           r2.weight AS edge2_weight
                    LIMIT 50
                """
            else:  # hop_count == 3
                # Three-hop paths
                query = """
                    MATCH (e:Entity {entity_id: $entity_id})-[r1]-(m1:Entity)-[r2]-(m2:Entity)-[r3]-(t:Entity)
                    WHERE ALL(x IN [e.entity_id, m1.entity_id, m2.entity_id, t.entity_id] WHERE 
                          COUNT(y IN [e.entity_id, m1.entity_id, m2.entity_id, t.entity_id] WHERE x = y) = 1)
                    RETURN e, r1, m1, r2, m2, r3, t,
                           e.pagerank_score AS start_score,
                           m1.pagerank_score AS mid1_score,
                           m2.pagerank_score AS mid2_score,
                           t.pagerank_score AS end_score,
                           r1.weight AS edge1_weight,
                           r2.weight AS edge2_weight,
                           r3.weight AS edge3_weight
                    LIMIT 30
                """
            
            result = session.run(query, entity_id=entity["id"])
            
            for record in result:
                path = self._format_path(record, hop_count)
                if path:
                    paths.append(path)
        
        return paths
    
    def _format_path(self, record, hop_count: int) -> Dict[str, Any]:
        """Format a path record into result format."""
        try:
            if hop_count == 1:
                return {
                    "type": "1-hop",
                    "start": record["e"]["canonical_name"],
                    "end": record["t"]["canonical_name"],
                    "relationship": "RELATED",  # Neo4j doesn't expose relationship type easily in results
                    "path": f"{record['e']['canonical_name']} -> {record['t']['canonical_name']}",
                    "score": (record["start_score"] or 0.01) * (record["end_score"] or 0.01) * (record["edge_weight"] or 0.5),
                    "evidence": f"Direct relationship found"
                }
            elif hop_count == 2:
                return {
                    "type": "2-hop",
                    "start": record["e"]["canonical_name"],
                    "middle": record["m"]["canonical_name"],
                    "end": record["t"]["canonical_name"],
                    "path": f"{record['e']['canonical_name']} -> {record['m']['canonical_name']} -> {record['t']['canonical_name']}",
                    "score": (record["start_score"] or 0.01) * (record["mid_score"] or 0.01) * 
                            (record["end_score"] or 0.01) * (record["edge1_weight"] or 0.5) * 
                            (record["edge2_weight"] or 0.5),
                    "evidence": f"Connected through {record['m']['canonical_name']}"
                }
            else:  # hop_count == 3
                return {
                    "type": "3-hop",
                    "start": record["e"]["canonical_name"],
                    "middle1": record["m1"]["canonical_name"],
                    "middle2": record["m2"]["canonical_name"],
                    "end": record["t"]["canonical_name"],
                    "path": f"{record['e']['canonical_name']} -> {record['m1']['canonical_name']} -> {record['m2']['canonical_name']} -> {record['t']['canonical_name']}",
                    "score": (record["start_score"] or 0.01) * (record["mid1_score"] or 0.01) * 
                            (record["mid2_score"] or 0.01) * (record["end_score"] or 0.01) * 
                            (record["edge1_weight"] or 0.5) * (record["edge2_weight"] or 0.5) * 
                            (record["edge3_weight"] or 0.5),
                    "evidence": f"Connected through {record['m1']['canonical_name']} and {record['m2']['canonical_name']}"
                }
        except Exception as e:
            logger.error(f"Error formatting path: {e}")
            return None
    
    def _rank_results(self, paths: List[Dict], query_entities: List[Dict], limit: int, query_text: str = None) -> List[Dict[str, Any]]:
        """Rank results by type-aware scoring and format for output."""
        
        # Analyze query intent if query text provided
        expected_type = ExpectedAnswerType.UNKNOWN
        type_confidence = 0.0
        intent_metadata = {}
        
        if query_text:
            expected_type, type_confidence, intent_metadata = self.intent_analyzer.analyze_query(query_text)
            logger.info(f"[T49] Query intent: {expected_type.value} (confidence: {type_confidence:.2f})")
            logger.debug(f"[T49] Intent metadata: {intent_metadata}")
        
        # Get compatible entity types for filtering
        compatible_types = self.intent_analyzer.get_compatible_entity_types(expected_type)
        
        # Fetch entity types for all answer entities if we have a type preference
        answer_entities = {}
        if compatible_types and self.driver:
            with self.driver.session() as session:
                # Get unique answer entity names
                answer_entity_names = list(set(path.get("end", "") for path in paths))
                
                for entity_name in answer_entity_names:
                    if not entity_name:
                        continue
                        
                    # Fetch entity details from Neo4j
                    result = session.run("""
                        MATCH (e:Entity)
                        WHERE e.canonical_name = $name
                        RETURN e.entity_id AS id, e.canonical_name AS name, 
                               e.entity_type AS type, e.pagerank_score AS pagerank
                        LIMIT 1
                    """, name=entity_name)
                    
                    record = result.single()
                    if record:
                        answer_entities[entity_name] = {
                            "entity_id": record["id"],
                            "canonical_name": record["name"],
                            "entity_type": record["type"] or "UNKNOWN",
                            "pagerank_score": record["pagerank"] or 0.0
                        }
        
        # Score and rank paths
        scored_paths = []
        for path in paths:
            answer_name = path.get("end", "Unknown")
            answer_entity = answer_entities.get(answer_name, {
                "canonical_name": answer_name,
                "entity_type": "UNKNOWN",
                "pagerank_score": 0.0
            })
            
            # Calculate type-aware relevance score
            if query_text and expected_type != ExpectedAnswerType.UNKNOWN:
                relevance_score = self.intent_analyzer.score_answer_relevance(
                    answer_entity, expected_type, query_text
                )
            else:
                # Fallback to PageRank-based scoring
                relevance_score = path["score"] * self.pagerank_boost_factor
            
            # Combine path score with relevance score
            final_score = path["score"] * 0.3 + relevance_score * 0.7
            
            scored_paths.append({
                "path": path,
                "answer_entity": answer_entity,
                "relevance_score": relevance_score,
                "final_score": final_score,
                "type_match": answer_entity["entity_type"] in compatible_types if compatible_types else True
            })
        
        # Sort by final score (type-aware)
        scored_paths.sort(key=lambda x: x["final_score"], reverse=True)
        
        # Log type filtering results for debugging
        if compatible_types:
            matching_count = sum(1 for sp in scored_paths if sp["type_match"])
            logger.info(f"[T49] Type filtering: {matching_count}/{len(scored_paths)} paths have compatible answer types")
            logger.debug(f"[T49] Compatible types: {compatible_types}")
        
        # Format top results
        results = []
        for i, scored_path in enumerate(scored_paths[:limit]):
            path = scored_path["path"]
            answer_entity = scored_path["answer_entity"]
            
            result = {
                "rank": i + 1,
                "text": answer_entity["canonical_name"],  # Compatibility field
                "name": answer_entity["canonical_name"],  # Compatibility field
                "answer": answer_entity["canonical_name"],
                "path": path["path"],
                "type": path["type"],
                "score": scored_path["final_score"],
                "confidence": min(0.95, scored_path["final_score"]),
                "evidence": path["evidence"],
                "entity_type": answer_entity["entity_type"],
                "type_match": scored_path["type_match"],
                "relevance_score": scored_path["relevance_score"],
                "query_intent": expected_type.value if query_text else "UNKNOWN"
            }
            results.append(result)
        
        # Add intent analysis to results metadata
        if results and query_text:
            results[0]["intent_analysis"] = {
                "expected_type": expected_type.value,
                "confidence": type_confidence,
                "metadata": intent_metadata
            }
        
        return results
    
    def validate_input(self, input_data: Any) -> ToolValidationResult:
        """Validate input parameters."""
        result = ToolValidationResult(is_valid=True)
        
        if not isinstance(input_data, dict):
            result.add_error("Input must be a dictionary")
            return result
        
        # Required field
        if "query_text" not in input_data:
            result.add_error("Missing required field: query_text")
        elif not isinstance(input_data["query_text"], str):
            result.add_error("query_text must be a string")
        elif not input_data["query_text"].strip():
            result.add_error("query_text cannot be empty")
        
        # Optional parameters
        if "max_hops" in input_data:
            max_hops = input_data["max_hops"]
            if not isinstance(max_hops, int) or max_hops < 1 or max_hops > self.max_hops_limit:
                result.add_warning(f"max_hops should be between 1 and {self.max_hops_limit}")
        
        if "result_limit" in input_data:
            limit = input_data["result_limit"]
            if not isinstance(limit, int) or limit < 1:
                result.add_warning("result_limit should be a positive integer")
        
        return result
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Define input schema."""
        return {
            "type": "object",
            "properties": {
                "query_text": {
                    "type": "string",
                    "description": "Natural language query"
                },
                "max_hops": {
                    "type": "integer",
                    "description": "Maximum number of hops",
                    "minimum": 1,
                    "maximum": self.max_hops_limit,
                    "default": 2
                },
                "result_limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "minimum": 1,
                    "maximum": 100,
                    "default": self.default_result_limit
                }
            },
            "required": ["query_text"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Define output schema."""
        return {
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rank": {"type": "integer"},
                            "answer": {"type": "string"},
                            "path": {"type": "string"},
                            "type": {"type": "string"},
                            "score": {"type": "number"},
                            "confidence": {"type": "number"},
                            "evidence": {"type": "string"}
                        }
                    }
                },
                "query_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "type": {"type": "string"}
                        }
                    }
                },
                "paths_found": {"type": "integer"},
                "total_paths_explored": {"type": "integer"},
                "execution_time": {"type": "number"},
                "query_metadata": {"type": "object"}
            },
            "required": ["results", "query_entities", "paths_found"]
        }
    
    def _generate_natural_language_answer(self, query_text: str, results: List[Dict], query_entities: List[Dict]) -> str:
        """Generate natural language answers from graph traversal results."""
        try:
            if not results or not query_text:
                return "I couldn't find relevant information in the knowledge graph."
            
            # Detect query type and generate appropriate answer
            query_lower = query_text.lower()
            
            # Extract relevant entities and relationships from results
            entities = []
            relationships = []
            
            for result in results[:5]:  # Use top 5 results
                if result.get("answer"):
                    entities.append(result["answer"])
                if result.get("path"):
                    for path_item in result["path"]:
                        if path_item.get("relationship"):
                            relationships.append(path_item["relationship"])
            
            # Generate answer based on query pattern
            if any(word in query_lower for word in ["what is", "define", "definition"]):
                return self._generate_definition_answer(query_entities, entities, relationships)
            elif any(word in query_lower for word in ["how", "process", "procedure"]):
                return self._generate_process_answer(query_entities, entities, relationships)
            elif any(word in query_lower for word in ["why", "reason", "because"]):
                return self._generate_causal_answer(query_entities, entities, relationships)
            elif any(word in query_lower for word in ["who", "which", "what"]):
                return self._generate_identification_answer(query_entities, entities, relationships)
            else:
                return self._generate_relationship_answer(query_entities, entities, relationships)
                
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return f"I found {len(results)} related items in the knowledge graph, but couldn't generate a clear answer."
    
    def _generate_definition_answer(self, query_entities: List[Dict], entities: List[str], relationships: List[str]) -> str:
        """Generate definition-style answer."""
        if not entities:
            return "I couldn't find a definition for that concept in the knowledge graph."
        
        main_entity = entities[0] if entities else "the concept"
        if len(entities) == 1:
            return f"{main_entity} is a key concept in the knowledge graph with various relationships to other entities."
        else:
            related_entities = ", ".join(entities[1:3])  # Show up to 2 related entities
            return f"{main_entity} is connected to {related_entities} and other concepts in the knowledge graph."
    
    def _generate_process_answer(self, query_entities: List[Dict], entities: List[str], relationships: List[str]) -> str:
        """Generate process/procedure answer."""
        if not entities:
            return "I couldn't find information about that process in the knowledge graph."
        
        if relationships:
            return f"The process involves {entities[0]} and is connected through relationships like {relationships[0]} in the knowledge graph."
        else:
            return f"The process involves {entities[0]} and related concepts in the knowledge graph."
    
    def _generate_causal_answer(self, query_entities: List[Dict], entities: List[str], relationships: List[str]) -> str:
        """Generate causal/explanatory answer."""
        if not entities:
            return "I couldn't find causal relationships for that concept in the knowledge graph."
        
        return f"Based on the knowledge graph, {entities[0]} is causally related to other concepts through various relationships."
    
    def _generate_identification_answer(self, query_entities: List[Dict], entities: List[str], relationships: List[str]) -> str:
        """Generate identification answer."""
        if not entities:
            return "I couldn't identify specific entities matching your query in the knowledge graph."
        
        if len(entities) == 1:
            return f"The relevant entity is {entities[0]}."
        else:
            entity_list = ", ".join(entities[:3])
            return f"The relevant entities include: {entity_list}."
    
    def _generate_relationship_answer(self, query_entities: List[Dict], entities: List[str], relationships: List[str]) -> str:
        """Generate relationship answer."""
        if not entities:
            return "I couldn't find relationships for those concepts in the knowledge graph."
        
        if len(entities) >= 2:
            return f"{entities[0]} is related to {entities[1]} and other concepts in the knowledge graph."
        else:
            return f"{entities[0]} has various relationships with other concepts in the knowledge graph."

    def _fuzzy_match_entities(self, query_text: str) -> List[Dict[str, Any]]:
        """Enhanced fuzzy matching for theory-related entities."""
        entities = []
        query_lower = query_text.lower()
        
        try:
            with self.driver.session() as session:
                # Get all entities from the graph for fuzzy matching
                result = session.run("""
                    MATCH (e:Entity) 
                    WHERE e.canonical_name IS NOT NULL AND e.canonical_name <> 'None'
                    RETURN e.canonical_name AS name, e.entity_type AS type, e.entity_id AS id
                    LIMIT 100
                """)
                
                graph_entities = [(record["name"], record["type"], record["id"]) for record in result]
                
                # Fuzzy matching strategies
                for entity_name, entity_type, entity_id in graph_entities:
                    if not entity_name or entity_name == "None":
                        continue
                        
                    entity_name_lower = entity_name.lower()
                    
                    # Strategy 1: Direct substring match
                    if entity_name_lower in query_lower or any(word in entity_name_lower for word in query_lower.split()):
                        entities.append({
                            "text": entity_name,
                            "canonical_name": entity_name,
                            "entity_id": entity_id,
                            "id": entity_id,  # Compatibility field
                            "type": entity_type,
                            "match_type": "substring"
                        })
                        continue
                    
                    # Strategy 2: Key term matching
                    query_words = set(query_lower.split())
                    entity_words = set(entity_name_lower.split())
                    
                    # Remove common stop words
                    stop_words = {"the", "a", "an", "is", "are", "what", "how", "theory", "principle"}
                    query_words -= stop_words
                    entity_words -= stop_words
                    
                    # Check for word overlap
                    if query_words & entity_words:  # Intersection
                        entities.append({
                            "text": entity_name,
                            "canonical_name": entity_name,
                            "entity_id": entity_id,
                            "id": entity_id,  # Compatibility field
                            "type": entity_type,
                            "match_type": "word_overlap"
                        })
                        continue
                    
                    # Strategy 3: Acronym matching (e.g., "CLT" for "Cognitive Load Theory")
                    if "(" in entity_name and ")" in entity_name:
                        acronym_match = re.search(r'\(([^)]+)\)', entity_name)
                        if acronym_match:
                            acronym = acronym_match.group(1).lower()
                            if acronym in query_lower:
                                entities.append({
                                    "text": entity_name,
                                    "canonical_name": entity_name,
                                    "entity_id": entity_id,
                                    "id": entity_id,  # Compatibility field
                                    "type": entity_type,
                                    "match_type": "acronym"
                                })
                
                # Remove duplicates and limit results
                unique_entities = []
                seen_names = set()
                for entity in entities:
                    if entity["canonical_name"] not in seen_names:
                        unique_entities.append(entity)
                        seen_names.add(entity["canonical_name"])
                
                return unique_entities[:5]  # Limit to top 5 matches
                
        except Exception as e:
            logger.error(f"Fuzzy matching failed: {e}")
            return []

    def get_theory_compatibility(self) -> List[str]:
        """T49 supports query theories."""
        return ["query_theory", "graph_theory", "information_retrieval_theory"]
    
    def cleanup(self):
        """Clean up Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None