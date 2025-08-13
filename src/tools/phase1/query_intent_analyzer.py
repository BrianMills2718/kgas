#!/usr/bin/env python3
"""
Query Intent Analyzer - Determines expected answer types from queries.
This component is CRITICAL for fixing the 60% accuracy problem.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)

class ExpectedAnswerType(Enum):
    """Expected answer types for queries"""
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    NUMBER = "NUMBER"
    EVENT = "EVENT"
    UNKNOWN = "UNKNOWN"
    MULTIPLE = "MULTIPLE"  # Query could have multiple valid types

class QueryIntentAnalyzer:
    """Analyze query intent to determine expected answer type"""
    
    def __init__(self):
        # Question word patterns mapped to expected types
        self.question_patterns = {
            ExpectedAnswerType.PERSON: [
                (r'\bwho\b', 0.9),
                (r'\bwhom\b', 0.9),
                (r'\bwhose\b', 0.8),
                (r'\bperson\b', 0.95),
                (r'\bpeople\b', 0.95),
                (r'\bindividual\b', 0.9),
                (r'\bCEO\b', 0.95),
                (r'\bCTO\b', 0.95),
                (r'\bfounder\b', 0.9),
                (r'\bleader\b', 0.85),
                (r'\bmanager\b', 0.85),
                (r'\bdirector\b', 0.85),
                (r'\bemployee\b', 0.9),
                (r'\bworks?\s+(?:at|for)\b', 0.85),
            ],
            ExpectedAnswerType.ORGANIZATION: [
                (r'\bwhat\s+(?:company|companies|organization|org)\b', 0.95),
                (r'\bwhich\s+(?:company|companies|organization|org)\b', 0.95),
                (r'\bcompan(?:y|ies)\b', 0.9),
                (r'\borganization\b', 0.9),
                (r'\bcorporation\b', 0.9),
                (r'\bfirm\b', 0.85),
                (r'\bagency\b', 0.85),
                (r'\binstitution\b', 0.85),
                (r'\buniversity\b', 0.95),
                (r'\bcollege\b', 0.9),
                (r'\bpartners?\b', 0.8),
                (r'\bacquired?\b', 0.85),
                (r'\bmerged?\b', 0.85),
                (r'\bowned\s+by\b', 0.85),
            ],
            ExpectedAnswerType.LOCATION: [
                (r'\bwhere\b', 0.9),
                (r'\blocation\b', 0.95),
                (r'\bplace\b', 0.9),
                (r'\bcity\b', 0.95),
                (r'\bcountry\b', 0.95),
                (r'\bstate\b', 0.9),
                (r'\bregion\b', 0.85),
                (r'\baddress\b', 0.9),
                (r'\bheadquarter(?:s|ed)\b', 0.9),
                (r'\blocated\b', 0.9),
                (r'\bbased\s+in\b', 0.9),
                (r'\boffice\b', 0.85),
            ],
            ExpectedAnswerType.DATE: [
                (r'\bwhen\b', 0.9),
                (r'\bdate\b', 0.95),
                (r'\btime\b', 0.85),
                (r'\byear\b', 0.9),
                (r'\bmonth\b', 0.85),
                (r'\bday\b', 0.85),
                (r'\bfounded\b', 0.8),
                (r'\bestablished\b', 0.8),
                (r'\bcreated\b', 0.75),
            ],
            ExpectedAnswerType.NUMBER: [
                (r'\bhow\s+(?:many|much)\b', 0.95),
                (r'\bnumber\b', 0.9),
                (r'\bcount\b', 0.9),
                (r'\bamount\b', 0.9),
                (r'\bprice\b', 0.9),
                (r'\bcost\b', 0.9),
                (r'\bvalue\b', 0.85),
                (r'\bpercentage\b', 0.9),
                (r'\bratio\b', 0.85),
            ],
            ExpectedAnswerType.EVENT: [
                (r'\bevent\b', 0.95),
                (r'\bhappened\b', 0.8),
                (r'\boccurred\b', 0.8),
                (r'\btook\s+place\b', 0.85),
                (r'\bincident\b', 0.85),
                (r'\bmeeting\b', 0.85),
                (r'\bconference\b', 0.85),
            ]
        }
        
        # Context patterns that can override question words
        self.context_patterns = {
            "asking_for_person": [
                r'\b(?:name|identify|person|individual|people)\b',
                r'\b(?:CEO|CTO|CFO|founder|employee|staff|worker)\b',
                r'\b(?:lead|manage|direct|head|run)\b'
            ],
            "asking_for_organization": [
                r'\b(?:company|corporation|firm|organization|institution)\b',
                r'\b(?:partner|acquire|merge|compete|collaborate)\b',
                r'\b(?:work\s+for|employed\s+by|hired\s+by)\b'
            ],
            "asking_for_location": [
                r'\b(?:location|place|city|country|state|region)\b',
                r'\b(?:headquarter|office|branch|facility)\b',
                r'\b(?:located|based|situated|found)\b'
            ]
        }
    
    def analyze_query(self, query_text: str) -> Tuple[ExpectedAnswerType, float, Dict[str, any]]:
        """
        Analyze query to determine expected answer type.
        
        Returns:
            (expected_type, confidence, metadata)
        """
        query_lower = query_text.lower()
        
        # Track scores for each type
        type_scores = {answer_type: 0.0 for answer_type in ExpectedAnswerType}
        pattern_matches = {answer_type: [] for answer_type in ExpectedAnswerType}
        
        # Check question word patterns
        for answer_type, patterns in self.question_patterns.items():
            for pattern, weight in patterns:
                if re.search(pattern, query_lower):
                    type_scores[answer_type] += weight
                    pattern_matches[answer_type].append(pattern)
        
        # Check context patterns for additional signals
        context_boost = 0.3
        
        if any(re.search(p, query_lower) for p in self.context_patterns["asking_for_person"]):
            type_scores[ExpectedAnswerType.PERSON] += context_boost
            
        if any(re.search(p, query_lower) for p in self.context_patterns["asking_for_organization"]):
            type_scores[ExpectedAnswerType.ORGANIZATION] += context_boost
            
        if any(re.search(p, query_lower) for p in self.context_patterns["asking_for_location"]):
            type_scores[ExpectedAnswerType.LOCATION] += context_boost
        
        # Determine the most likely type
        max_score = max(type_scores.values())
        
        if max_score == 0:
            return ExpectedAnswerType.UNKNOWN, 0.0, {"reason": "No patterns matched"}
        
        # Check if multiple types have high scores (ambiguous query)
        high_scoring_types = [
            answer_type for answer_type, score in type_scores.items()
            if score > max_score * 0.8 and score > 0.5
        ]
        
        if len(high_scoring_types) > 1:
            # Query is ambiguous, could have multiple valid answer types
            primary_type = max(type_scores.items(), key=lambda x: x[1])[0]
            return ExpectedAnswerType.MULTIPLE, max_score / 2, {
                "primary_type": primary_type,
                "possible_types": high_scoring_types,
                "scores": {k.value: v for k, v in type_scores.items() if v > 0},
                "pattern_matches": {k.value: v for k, v in pattern_matches.items() if v}
            }
        
        # Single clear answer type
        best_type = max(type_scores.items(), key=lambda x: x[1])[0]
        confidence = min(1.0, max_score / 2)  # Normalize confidence
        
        return best_type, confidence, {
            "scores": {k.value: v for k, v in type_scores.items() if v > 0},
            "pattern_matches": {k.value: v for k, v in pattern_matches.items() if v},
            "reason": f"Matched patterns for {best_type.value}"
        }
    
    def get_compatible_entity_types(self, expected_answer_type: ExpectedAnswerType) -> List[str]:
        """
        Get Neo4j entity types compatible with the expected answer type.
        
        Maps high-level answer types to actual entity types in the graph.
        """
        type_mapping = {
            ExpectedAnswerType.PERSON: ["PERSON", "PER"],
            ExpectedAnswerType.ORGANIZATION: ["ORGANIZATION", "ORG", "COMPANY", "GPE"],  # GPE can be organizations
            ExpectedAnswerType.LOCATION: ["LOCATION", "LOC", "GPE", "FACILITY", "PLACE"],
            ExpectedAnswerType.DATE: ["DATE", "TIME"],
            ExpectedAnswerType.NUMBER: ["NUMBER", "QUANTITY", "PERCENT", "MONEY", "CARDINAL"],
            ExpectedAnswerType.EVENT: ["EVENT"],
            ExpectedAnswerType.UNKNOWN: [],  # Accept any type
            ExpectedAnswerType.MULTIPLE: []  # Accept any type
        }
        
        return type_mapping.get(expected_answer_type, [])
    
    def score_answer_relevance(
        self, 
        answer_entity: Dict[str, any],
        expected_type: ExpectedAnswerType,
        query_text: str
    ) -> float:
        """
        Score how relevant an answer entity is to the query.
        
        Args:
            answer_entity: Entity dict with 'entity_type', 'canonical_name', etc.
            expected_type: Expected answer type from query analysis
            query_text: Original query text
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Type match scoring (most important)
        entity_type = answer_entity.get("entity_type", "UNKNOWN")
        compatible_types = self.get_compatible_entity_types(expected_type)
        
        if compatible_types and entity_type in compatible_types:
            score += 0.7  # Strong type match
        elif expected_type in [ExpectedAnswerType.UNKNOWN, ExpectedAnswerType.MULTIPLE]:
            score += 0.3  # No type preference, partial credit
        else:
            score += 0.0  # Wrong type
        
        # Name relevance scoring (secondary factor)
        entity_name = answer_entity.get("canonical_name", "").lower()
        query_lower = query_text.lower()
        
        # Check if entity name appears in query (might be asking about it)
        if entity_name in query_lower:
            score *= 0.5  # Penalize if answer is just repeating the query
        
        # PageRank influence (tertiary factor)
        pagerank = answer_entity.get("pagerank_score", 0.0)
        if pagerank > 0:
            score += min(0.3, pagerank * 10)  # Cap PageRank influence at 0.3
        
        return min(1.0, score)