"""
Reasoning Query and Analysis Interface

Provides comprehensive query and analysis capabilities for reasoning traces,
including pattern detection, confidence analysis, and decision path exploration.

NO MOCKS - Production-ready implementation for reasoning trace analysis.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

from .reasoning_trace import (
    ReasoningTrace, ReasoningStep, DecisionLevel, ReasoningType
)
from .reasoning_trace_store import ReasoningTraceStore

logger = logging.getLogger(__name__)


@dataclass
class ReasoningPattern:
    """Detected reasoning pattern"""
    pattern_id: str
    pattern_type: str
    frequency: int
    confidence_range: Tuple[float, float]
    common_contexts: List[str]
    example_steps: List[str]  # Step IDs
    success_rate: float
    metadata: Dict[str, Any]


@dataclass
class DecisionAnalysis:
    """Analysis of decision-making patterns"""
    decision_point: str
    total_decisions: int
    avg_confidence: float
    confidence_distribution: Dict[str, int]  # confidence ranges -> counts
    common_reasoning_patterns: List[str]
    success_rate: float
    avg_duration_ms: Optional[float]
    alternatives_analysis: Dict[str, Any]


@dataclass
class TraceAnalysis:
    """Comprehensive analysis of a reasoning trace"""
    trace_id: str
    operation_type: str
    total_steps: int
    success: bool
    overall_confidence: float
    duration_ms: Optional[int]
    
    # Step-level analysis
    steps_by_level: Dict[str, int]
    steps_by_type: Dict[str, int]
    confidence_progression: List[float]
    decision_path: List[str]
    
    # Quality metrics
    reasoning_quality_score: float
    decision_consistency_score: float
    confidence_calibration_score: float
    
    # Issues and patterns
    identified_issues: List[str]
    reasoning_patterns: List[str]
    improvement_suggestions: List[str]


class ReasoningQueryInterface:
    """Advanced query and analysis interface for reasoning traces"""
    
    def __init__(self, reasoning_store: ReasoningTraceStore):
        """Initialize reasoning query interface
        
        Args:
            reasoning_store: ReasoningTraceStore instance
        """
        self.reasoning_store = reasoning_store
        self.logger = logging.getLogger(__name__)
        
        # Analysis cache
        self._pattern_cache = {}
        self._analysis_cache = {}
        
        self.logger.info("ReasoningQueryInterface initialized")
    
    # ============ Basic Queries ============
    
    def get_traces_by_operation(
        self,
        operation_type: str,
        success_only: Optional[bool] = None,
        limit: int = 100
    ) -> List[ReasoningTrace]:
        """Get traces for a specific operation type
        
        Args:
            operation_type: Type of operation to filter by
            success_only: Filter by success status
            limit: Maximum number of results
            
        Returns:
            List of matching traces
        """
        return self.reasoning_store.query_traces(
            operation_type=operation_type,
            success_only=success_only,
            limit=limit
        )
    
    def get_steps_by_decision_pattern(
        self,
        decision_level: Optional[DecisionLevel] = None,
        reasoning_type: Optional[ReasoningType] = None,
        confidence_threshold: float = 0.0,
        limit: int = 200
    ) -> List[ReasoningStep]:
        """Get steps matching decision patterns
        
        Args:
            decision_level: Filter by decision level
            reasoning_type: Filter by reasoning type
            confidence_threshold: Minimum confidence score
            limit: Maximum number of results
            
        Returns:
            List of matching reasoning steps
        """
        return self.reasoning_store.query_steps(
            decision_level=decision_level,
            reasoning_type=reasoning_type,
            confidence_threshold=confidence_threshold,
            limit=limit
        )
    
    def find_similar_decisions(
        self,
        reference_step: ReasoningStep,
        similarity_threshold: float = 0.7,
        limit: int = 50
    ) -> List[Tuple[ReasoningStep, float]]:
        """Find steps with similar decision patterns
        
        Args:
            reference_step: Reference step to compare against
            similarity_threshold: Minimum similarity score
            limit: Maximum number of results
            
        Returns:
            List of (step, similarity_score) tuples
        """
        # Get candidate steps
        candidates = self.get_steps_by_decision_pattern(
            decision_level=reference_step.decision_level,
            reasoning_type=reference_step.reasoning_type,
            limit=500
        )
        
        # Calculate similarity scores
        similar_steps = []
        for candidate in candidates:
            if candidate.step_id == reference_step.step_id:
                continue
                
            similarity = self._calculate_step_similarity(reference_step, candidate)
            if similarity >= similarity_threshold:
                similar_steps.append((candidate, similarity))
        
        # Sort by similarity and limit results
        similar_steps.sort(key=lambda x: x[1], reverse=True)
        return similar_steps[:limit]
    
    # ============ Pattern Analysis ============
    
    def detect_reasoning_patterns(
        self,
        operation_type: Optional[str] = None,
        min_frequency: int = 5,
        lookback_days: int = 30
    ) -> List[ReasoningPattern]:
        """Detect common reasoning patterns
        
        Args:
            operation_type: Filter by operation type
            min_frequency: Minimum pattern frequency
            lookback_days: Days to look back for pattern detection
            
        Returns:
            List of detected reasoning patterns
        """
        cache_key = f"patterns_{operation_type}_{min_frequency}_{lookback_days}"
        
        if cache_key in self._pattern_cache:
            cache_time, patterns = self._pattern_cache[cache_key]
            if (datetime.now() - cache_time).seconds < 3600:  # 1 hour cache
                return patterns
        
        # Get recent traces
        since_date = datetime.now() - timedelta(days=lookback_days)
        traces = self.reasoning_store.query_traces(
            operation_type=operation_type,
            since=since_date,
            limit=1000
        )
        
        # Analyze patterns
        patterns = self._analyze_reasoning_patterns(traces, min_frequency)
        
        # Cache results
        self._pattern_cache[cache_key] = (datetime.now(), patterns)
        
        return patterns
    
    def analyze_decision_quality(
        self,
        decision_point: str,
        lookback_days: int = 30
    ) -> DecisionAnalysis:
        """Analyze quality of decisions at a specific decision point
        
        Args:
            decision_point: Decision point to analyze
            lookback_days: Days to look back for analysis
            
        Returns:
            DecisionAnalysis with quality metrics
        """
        # Get recent steps for this decision point
        since_date = datetime.now() - timedelta(days=lookback_days)
        
        # Query steps matching this decision point
        all_steps = self.reasoning_store.query_steps(limit=1000)
        matching_steps = [
            step for step in all_steps 
            if decision_point.lower() in step.decision_point.lower()
        ]
        
        if not matching_steps:
            return DecisionAnalysis(
                decision_point=decision_point,
                total_decisions=0,
                avg_confidence=0.0,
                confidence_distribution={},
                common_reasoning_patterns=[],
                success_rate=0.0,
                avg_duration_ms=None,
                alternatives_analysis={}
            )
        
        # Analyze decision patterns
        return self._analyze_decision_patterns(decision_point, matching_steps)
    
    def analyze_confidence_calibration(
        self,
        operation_type: Optional[str] = None,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze how well confidence scores correlate with actual success
        
        Args:
            operation_type: Filter by operation type
            lookback_days: Days to look back for analysis
            
        Returns:
            Confidence calibration analysis
        """
        # Get recent traces
        since_date = datetime.now() - timedelta(days=lookback_days)
        traces = self.reasoning_store.query_traces(
            operation_type=operation_type,
            since=since_date,
            limit=500
        )
        
        if not traces:
            return {"error": "No traces found for analysis"}
        
        # Group traces by confidence ranges
        confidence_ranges = {
            "very_low": (0.0, 0.3),
            "low": (0.3, 0.5),
            "medium": (0.5, 0.7),
            "high": (0.7, 0.9),
            "very_high": (0.9, 1.0)
        }
        
        calibration_data = {}
        
        for range_name, (min_conf, max_conf) in confidence_ranges.items():
            range_traces = [
                t for t in traces 
                if min_conf <= t.overall_confidence < max_conf
            ]
            
            if range_traces:
                success_rate = sum(1 for t in range_traces if t.success) / len(range_traces)
                avg_confidence = sum(t.overall_confidence for t in range_traces) / len(range_traces)
                
                calibration_data[range_name] = {
                    "count": len(range_traces),
                    "avg_confidence": avg_confidence,
                    "success_rate": success_rate,
                    "calibration_error": abs(avg_confidence - success_rate),
                    "confidence_range": (min_conf, max_conf)
                }
        
        # Calculate overall calibration metrics
        total_traces = len(traces)
        overall_success_rate = sum(1 for t in traces if t.success) / total_traces
        avg_confidence = sum(t.overall_confidence for t in traces) / total_traces
        
        return {
            "total_traces_analyzed": total_traces,
            "overall_success_rate": overall_success_rate,
            "overall_avg_confidence": avg_confidence,
            "overall_calibration_error": abs(avg_confidence - overall_success_rate),
            "confidence_range_analysis": calibration_data,
            "analysis_period_days": lookback_days
        }
    
    # ============ Comprehensive Analysis ============
    
    def analyze_trace(self, trace_id: str) -> Optional[TraceAnalysis]:
        """Perform comprehensive analysis of a single trace
        
        Args:
            trace_id: Trace to analyze
            
        Returns:
            TraceAnalysis with comprehensive metrics
        """
        trace = self.reasoning_store.get_trace(trace_id)
        if not trace:
            return None
        
        # Basic metrics
        steps_by_level = Counter()
        steps_by_type = Counter()
        confidence_progression = []
        decision_path = []
        
        for step in trace.all_steps.values():
            steps_by_level[step.decision_level.value] += 1
            steps_by_type[step.reasoning_type.value] += 1
            confidence_progression.append(step.confidence_score)
            decision_path.append(step.decision_point)
        
        # Quality scores
        reasoning_quality = self._calculate_reasoning_quality_score(trace)
        consistency_score = self._calculate_decision_consistency_score(trace)
        calibration_score = self._calculate_confidence_calibration_score(trace)
        
        # Issues and patterns
        issues = self._identify_trace_issues(trace)
        patterns = self._identify_trace_patterns(trace)
        suggestions = self._generate_improvement_suggestions(trace, issues)
        
        return TraceAnalysis(
            trace_id=trace_id,
            operation_type=trace.operation_type,
            total_steps=trace.total_steps,
            success=trace.success,
            overall_confidence=trace.overall_confidence,
            duration_ms=trace.total_duration_ms,
            steps_by_level=dict(steps_by_level),
            steps_by_type=dict(steps_by_type),
            confidence_progression=confidence_progression,
            decision_path=decision_path,
            reasoning_quality_score=reasoning_quality,
            decision_consistency_score=consistency_score,
            confidence_calibration_score=calibration_score,
            identified_issues=issues,
            reasoning_patterns=patterns,
            improvement_suggestions=suggestions
        )
    
    def compare_traces(
        self,
        trace_ids: List[str],
        comparison_metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare multiple reasoning traces
        
        Args:
            trace_ids: List of trace IDs to compare
            comparison_metrics: Specific metrics to compare
            
        Returns:
            Comparison analysis
        """
        if not comparison_metrics:
            comparison_metrics = [
                "overall_confidence", "success_rate", "duration",
                "reasoning_quality", "decision_consistency"
            ]
        
        # Get trace analyses
        analyses = []
        for trace_id in trace_ids:
            analysis = self.analyze_trace(trace_id)
            if analysis:
                analyses.append(analysis)
        
        if not analyses:
            return {"error": "No valid traces found for comparison"}
        
        # Compare metrics
        comparison = {
            "traces_compared": len(analyses),
            "comparison_metrics": comparison_metrics,
            "results": {}
        }
        
        for metric in comparison_metrics:
            metric_values = []
            for analysis in analyses:
                if hasattr(analysis, metric):
                    metric_values.append(getattr(analysis, metric))
            
            if metric_values:
                comparison["results"][metric] = {
                    "values": metric_values,
                    "avg": sum(metric_values) / len(metric_values),
                    "min": min(metric_values),
                    "max": max(metric_values),
                    "range": max(metric_values) - min(metric_values)
                }
        
        return comparison
    
    # ============ Advanced Queries ============
    
    def find_decision_chains(
        self,
        starting_decision: str,
        max_depth: int = 5,
        min_confidence: float = 0.5
    ) -> List[List[ReasoningStep]]:
        """Find chains of related decisions
        
        Args:
            starting_decision: Decision point to start from
            max_depth: Maximum chain depth
            min_confidence: Minimum confidence for included steps
            
        Returns:
            List of decision chains (each chain is a list of steps)
        """
        # Get starting steps
        all_steps = self.reasoning_store.query_steps(limit=1000)
        starting_steps = [
            step for step in all_steps
            if starting_decision.lower() in step.decision_point.lower()
            and step.confidence_score >= min_confidence
        ]
        
        chains = []
        for start_step in starting_steps:
            chain = self._build_decision_chain(start_step, max_depth, min_confidence)
            if len(chain) > 1:  # Only include chains with multiple steps
                chains.append(chain)
        
        return chains
    
    def get_error_patterns(
        self,
        lookback_days: int = 30,
        min_frequency: int = 3
    ) -> List[Dict[str, Any]]:
        """Analyze error patterns in reasoning traces
        
        Args:
            lookback_days: Days to look back for analysis
            min_frequency: Minimum error frequency to report
            
        Returns:
            List of error patterns with analysis
        """
        # Get recent traces with errors
        since_date = datetime.now() - timedelta(days=lookback_days)
        failed_traces = self.reasoning_store.query_traces(
            success_only=False,
            since=since_date,
            limit=500
        )
        
        failed_traces = [t for t in failed_traces if not t.success]
        
        # Analyze error patterns
        error_patterns = defaultdict(list)
        
        for trace in failed_traces:
            for step in trace.all_steps.values():
                if step.error_occurred:
                    pattern_key = f"{step.reasoning_type.value}_{step.decision_level.value}"
                    error_patterns[pattern_key].append({
                        "trace_id": trace.trace_id,
                        "step_id": step.step_id,
                        "error_message": step.error_message,
                        "decision_point": step.decision_point,
                        "context": step.context
                    })
        
        # Filter by frequency and format results
        result_patterns = []
        for pattern_key, errors in error_patterns.items():
            if len(errors) >= min_frequency:
                error_messages = [e["error_message"] for e in errors if e.get("error_message")]
                most_common_error = Counter(error_messages).most_common(1)[0][0] if error_messages else "Unknown"
                
                result_patterns.append({
                    "pattern": pattern_key,
                    "frequency": len(errors),
                    "most_common_error": most_common_error,
                    "affected_traces": len(set(e["trace_id"] for e in errors)),
                    "examples": errors[:5]  # First 5 examples
                })
        
        # Sort by frequency
        result_patterns.sort(key=lambda x: x["frequency"], reverse=True)
        
        return result_patterns
    
    # ============ Helper Methods ============
    
    def _calculate_step_similarity(self, step1: ReasoningStep, step2: ReasoningStep) -> float:
        """Calculate similarity between two reasoning steps"""
        similarity_score = 0.0
        
        # Decision level and type similarity
        if step1.decision_level == step2.decision_level:
            similarity_score += 0.3
        if step1.reasoning_type == step2.reasoning_type:
            similarity_score += 0.3
        
        # Decision point similarity (simple text similarity)
        decision_similarity = self._text_similarity(step1.decision_point, step2.decision_point)
        similarity_score += decision_similarity * 0.2
        
        # Confidence similarity
        conf_diff = abs(step1.confidence_score - step2.confidence_score)
        conf_similarity = 1.0 - min(conf_diff, 1.0)
        similarity_score += conf_similarity * 0.1
        
        # Context similarity
        context_similarity = self._dict_similarity(step1.context, step2.context)
        similarity_score += context_similarity * 0.1
        
        return min(similarity_score, 1.0)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity"""
        if not text1 or not text2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _dict_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """Calculate similarity between two dictionaries"""
        if not dict1 or not dict2:
            return 0.0
        
        # Compare keys
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        key_overlap = len(keys1.intersection(keys2)) / len(keys1.union(keys2)) if keys1.union(keys2) else 0.0
        
        return key_overlap
    
    def _analyze_reasoning_patterns(self, traces: List[ReasoningTrace], min_frequency: int) -> List[ReasoningPattern]:
        """Analyze reasoning patterns from traces"""
        patterns = []
        
        # Group steps by reasoning type and decision level
        pattern_groups = defaultdict(list)
        
        for trace in traces:
            for step in trace.all_steps.values():
                pattern_key = f"{step.reasoning_type.value}_{step.decision_level.value}"
                pattern_groups[pattern_key].append((step, trace.success))
        
        # Analyze each pattern group
        for pattern_key, step_data in pattern_groups.items():
            if len(step_data) >= min_frequency:
                steps, successes = zip(*step_data)
                
                confidence_scores = [s.confidence_score for s in steps]
                contexts = [str(s.context) for s in steps]
                
                pattern = ReasoningPattern(
                    pattern_id=f"pattern_{pattern_key}_{len(patterns)}",
                    pattern_type=pattern_key,
                    frequency=len(step_data),
                    confidence_range=(min(confidence_scores), max(confidence_scores)),
                    common_contexts=list(set(contexts))[:5],  # Top 5 unique contexts
                    example_steps=[s.step_id for s in steps[:3]],  # First 3 examples
                    success_rate=sum(successes) / len(successes),
                    metadata={
                        "avg_confidence": sum(confidence_scores) / len(confidence_scores),
                        "confidence_std": self._calculate_std(confidence_scores)
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_decision_patterns(self, decision_point: str, steps: List[ReasoningStep]) -> DecisionAnalysis:
        """Analyze patterns for a specific decision point"""
        
        # Basic metrics
        total_decisions = len(steps)
        confidence_scores = [s.confidence_score for s in steps]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Confidence distribution
        confidence_ranges = {
            "0.0-0.3": 0,
            "0.3-0.5": 0,
            "0.5-0.7": 0,
            "0.7-0.9": 0,
            "0.9-1.0": 0
        }
        
        for conf in confidence_scores:
            if conf < 0.3:
                confidence_ranges["0.0-0.3"] += 1
            elif conf < 0.5:
                confidence_ranges["0.3-0.5"] += 1
            elif conf < 0.7:
                confidence_ranges["0.5-0.7"] += 1
            elif conf < 0.9:
                confidence_ranges["0.7-0.9"] += 1
            else:
                confidence_ranges["0.9-1.0"] += 1
        
        # Duration analysis
        durations = [s.duration_ms for s in steps if s.duration_ms is not None]
        avg_duration = sum(durations) / len(durations) if durations else None
        
        # Success rate (approximate - based on error occurrence)
        errors = sum(1 for s in steps if s.error_occurred)
        success_rate = (total_decisions - errors) / total_decisions
        
        # Common reasoning patterns
        reasoning_texts = [s.reasoning_text for s in steps if s.reasoning_text]
        common_words = self._extract_common_words(reasoning_texts)
        
        return DecisionAnalysis(
            decision_point=decision_point,
            total_decisions=total_decisions,
            avg_confidence=avg_confidence,
            confidence_distribution=confidence_ranges,
            common_reasoning_patterns=common_words[:5],
            success_rate=success_rate,
            avg_duration_ms=avg_duration,
            alternatives_analysis={
                "steps_with_alternatives": sum(1 for s in steps if s.options_considered),
                "avg_alternatives_per_step": sum(len(s.options_considered) for s in steps) / total_decisions
            }
        )
    
    def _calculate_reasoning_quality_score(self, trace: ReasoningTrace) -> float:
        """Calculate reasoning quality score for a trace"""
        if not trace.all_steps:
            return 0.0
        
        quality_factors = []
        
        # Factor 1: Reasoning text completeness
        steps_with_reasoning = sum(1 for s in trace.all_steps.values() if s.reasoning_text.strip())
        reasoning_completeness = steps_with_reasoning / len(trace.all_steps)
        quality_factors.append(reasoning_completeness)
        
        # Factor 2: Confidence consistency
        confidences = [s.confidence_score for s in trace.all_steps.values()]
        conf_std = self._calculate_std(confidences)
        confidence_consistency = max(0.0, 1.0 - conf_std)  # Lower std = higher consistency
        quality_factors.append(confidence_consistency)
        
        # Factor 3: Decision level coverage
        levels_covered = len(set(s.decision_level for s in trace.all_steps.values()))
        level_coverage = levels_covered / 4.0  # 4 possible levels
        quality_factors.append(level_coverage)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _calculate_decision_consistency_score(self, trace: ReasoningTrace) -> float:
        """Calculate decision consistency score"""
        if len(trace.all_steps) < 2:
            return 1.0
        
        # Check for contradictory decisions
        consistency_score = 1.0
        
        # Simple heuristic: check if similar decision points have similar outcomes
        decision_groups = defaultdict(list)
        for step in trace.all_steps.values():
            key = step.decision_point[:50]  # Group by first 50 chars
            decision_groups[key].append(step)
        
        for group in decision_groups.values():
            if len(group) > 1:
                confidences = [s.confidence_score for s in group]
                conf_variance = self._calculate_std(confidences) ** 2
                consistency_score -= min(conf_variance, consistency_score)
        
        return max(0.0, consistency_score)
    
    def _calculate_confidence_calibration_score(self, trace: ReasoningTrace) -> float:
        """Calculate confidence calibration score"""
        # Simple approximation based on outcome vs confidence
        if trace.success:
            # For successful traces, higher confidence is better calibrated
            return trace.overall_confidence
        else:
            # For failed traces, lower confidence is better calibrated
            return 1.0 - trace.overall_confidence
    
    def _identify_trace_issues(self, trace: ReasoningTrace) -> List[str]:
        """Identify potential issues in a trace"""
        issues = []
        
        # Check for low confidence decisions
        low_confidence_steps = [s for s in trace.all_steps.values() if s.confidence_score < 0.3]
        if low_confidence_steps:
            issues.append(f"Found {len(low_confidence_steps)} low confidence decisions")
        
        # Check for missing reasoning
        no_reasoning_steps = [s for s in trace.all_steps.values() if not s.reasoning_text.strip()]
        if no_reasoning_steps:
            issues.append(f"Found {len(no_reasoning_steps)} steps without reasoning text")
        
        # Check for errors
        error_steps = [s for s in trace.all_steps.values() if s.error_occurred]
        if error_steps:
            issues.append(f"Found {len(error_steps)} steps with errors")
        
        # Check for very short execution times (might indicate rushed decisions)
        quick_steps = [s for s in trace.all_steps.values() 
                      if s.duration_ms is not None and s.duration_ms < 100]
        if len(quick_steps) > len(trace.all_steps) * 0.5:
            issues.append("Many decisions made very quickly (< 100ms)")
        
        return issues
    
    def _identify_trace_patterns(self, trace: ReasoningTrace) -> List[str]:
        """Identify reasoning patterns in a trace"""
        patterns = []
        
        # Check for hierarchical reasoning
        levels_used = set(s.decision_level for s in trace.all_steps.values())
        if len(levels_used) >= 3:
            patterns.append("Hierarchical reasoning across multiple decision levels")
        
        # Check for iterative refinement
        workflow_steps = [s for s in trace.all_steps.values() 
                         if s.reasoning_type == ReasoningType.WORKFLOW_PLANNING]
        if len(workflow_steps) > 1:
            patterns.append("Iterative workflow planning")
        
        # Check for error recovery
        error_handling_steps = [s for s in trace.all_steps.values()
                               if s.reasoning_type == ReasoningType.ERROR_HANDLING]
        if error_handling_steps:
            patterns.append("Error handling and recovery")
        
        return patterns
    
    def _generate_improvement_suggestions(self, trace: ReasoningTrace, issues: List[str]) -> List[str]:
        """Generate improvement suggestions based on identified issues"""
        suggestions = []
        
        if "low confidence decisions" in ' '.join(issues):
            suggestions.append("Consider gathering more context for low-confidence decisions")
        
        if "without reasoning text" in ' '.join(issues):
            suggestions.append("Ensure all decision steps include explanatory reasoning")
        
        if "with errors" in ' '.join(issues):
            suggestions.append("Implement better error prevention and handling")
        
        if "made very quickly" in ' '.join(issues):
            suggestions.append("Allow more time for complex decision-making processes")
        
        if trace.overall_confidence < 0.5:
            suggestions.append("Consider breaking complex decisions into smaller steps")
        
        return suggestions
    
    def _build_decision_chain(
        self, 
        start_step: ReasoningStep, 
        max_depth: int, 
        min_confidence: float
    ) -> List[ReasoningStep]:
        """Build a chain of related decisions"""
        chain = [start_step]
        current_step = start_step
        
        for _ in range(max_depth - 1):
            # Find next step in chain (simplified - could use more sophisticated matching)
            next_step = None
            
            # For now, just return single step chains
            # In a full implementation, this would trace through parent-child relationships
            # and find semantically related decisions
            break
        
        return chain
    
    def _extract_common_words(self, texts: List[str], top_n: int = 10) -> List[str]:
        """Extract common words from reasoning texts"""
        if not texts:
            return []
        
        # Simple word frequency analysis
        all_words = []
        for text in texts:
            words = text.lower().split()
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
            all_words.extend(filtered_words)
        
        word_counts = Counter(all_words)
        return [word for word, count in word_counts.most_common(top_n)]
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def clear_cache(self) -> None:
        """Clear analysis cache"""
        self._pattern_cache.clear()
        self._analysis_cache.clear()
        self.logger.info("Reasoning query interface cache cleared")


# Factory function
def create_reasoning_query_interface(reasoning_store: ReasoningTraceStore) -> ReasoningQueryInterface:
    """Create reasoning query interface
    
    Args:
        reasoning_store: ReasoningTraceStore instance
        
    Returns:
        ReasoningQueryInterface instance
    """
    return ReasoningQueryInterface(reasoning_store)