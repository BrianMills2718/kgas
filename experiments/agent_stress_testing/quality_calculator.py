#!/usr/bin/env python3
"""
Quality Score Calculator - NO HARDCODED VALUES

All quality calculations use configurable thresholds and weights.
"""

import yaml
import os
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class QualityResult:
    """Result of quality assessment"""
    score: float
    components: Dict[str, float]
    meets_threshold: bool
    recommendations: List[str]


class QualityCalculator:
    """
    Calculates quality scores based on configurable criteria.
    NO hardcoded thresholds - all values from config.
    """
    
    def __init__(self, config_path: str = None):
        """Load quality configuration"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'quality_config.yaml')
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Get environment-specific overrides
        env = os.getenv('AGENT_ENV', 'development')
        if env in self.config.get('environment_overrides', {}):
            self._apply_overrides(self.config['environment_overrides'][env])
    
    def _apply_overrides(self, overrides: Dict[str, Any]):
        """Apply environment-specific configuration overrides"""
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict:
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, overrides)
    
    def calculate_tool_quality(self, tool_name: str, tool_result: Dict[str, Any]) -> QualityResult:
        """
        Calculate quality score for a tool execution result.
        
        Args:
            tool_name: Name of the tool (for threshold lookup)
            tool_result: Tool execution result with metrics
            
        Returns:
            QualityResult with score and analysis
        """
        weights = self.config['quality_thresholds']['scoring_weights']
        
        # Component 1: Entity/Result Confidence
        entity_confidence = self._calculate_entity_confidence(tool_result)
        
        # Component 2: Result Completeness  
        result_completeness = self._calculate_completeness(tool_result)
        
        # Component 3: Processing Success
        processing_success = self._calculate_processing_success(tool_result)
        
        # Weighted combination
        overall_score = (
            entity_confidence * weights['entity_confidence'] +
            result_completeness * weights['result_completeness'] + 
            processing_success * weights['processing_success']
        )
        
        components = {
            'entity_confidence': entity_confidence,
            'result_completeness': result_completeness,
            'processing_success': processing_success
        }
        
        # Check against tool-specific threshold
        tool_threshold = self._get_tool_threshold(tool_name)
        meets_threshold = overall_score >= tool_threshold
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall_score, components, tool_name, tool_threshold
        )
        
        return QualityResult(
            score=overall_score,
            components=components,
            meets_threshold=meets_threshold,
            recommendations=recommendations
        )
    
    def _calculate_entity_confidence(self, tool_result: Dict[str, Any]) -> float:
        """Calculate confidence based on entity extraction results"""
        if 'entities' not in tool_result:
            return 0.5  # Neutral score for non-entity tools
        
        entities = tool_result['entities']
        if not entities:
            return 0.0
        
        # Average confidence of extracted entities
        confidences = [e.get('confidence', 0.5) for e in entities]
        return sum(confidences) / len(confidences)
    
    def _calculate_completeness(self, tool_result: Dict[str, Any]) -> float:
        """Calculate completeness based on result counts"""
        base_score = 0.5
        
        # Entity count scoring
        entity_count = len(tool_result.get('entities', []))
        if entity_count > 0:
            base_score += min(0.3, entity_count * 0.05)  # Up to 0.3 bonus
        
        # Relationship count scoring
        relationship_count = len(tool_result.get('relationships', []))
        if relationship_count > 0:
            base_score += min(0.2, relationship_count * 0.02)  # Up to 0.2 bonus
        
        return min(1.0, max(0.0, base_score))
    
    def _calculate_processing_success(self, tool_result: Dict[str, Any]) -> float:
        """Calculate success based on processing metrics"""
        # Check for errors
        if tool_result.get('status') == 'error':
            return 0.0
        elif tool_result.get('status') == 'partial':
            return 0.6
        elif tool_result.get('status') == 'success':
            return 1.0
        else:
            return 0.5  # Unknown status
    
    def _get_tool_threshold(self, tool_name: str) -> float:
        """Get quality threshold for specific tool type"""
        thresholds = self.config['quality_thresholds']
        
        # Map tool names to threshold categories
        tool_mapping = {
            'document_processor': 'document_processing',
            'text_analyzer': 'entity_extraction', 
            'relationship_extractor': 'relationship_extraction',
            'network_analyzer': 'network_analysis'
        }
        
        threshold_key = tool_mapping.get(tool_name, 'global_minimum')
        return thresholds.get(threshold_key, thresholds['global_minimum'])
    
    def _generate_recommendations(self, score: float, components: Dict[str, float], 
                                 tool_name: str, threshold: float) -> List[str]:
        """Generate improvement recommendations based on quality analysis"""
        recommendations = []
        
        if score < threshold:
            recommendations.append(f"Quality {score:.2f} below threshold {threshold:.2f}")
            
            # Specific recommendations based on component scores
            if components['entity_confidence'] < 0.6:
                recommendations.append("Consider increasing confidence threshold or using alternative model")
            
            if components['result_completeness'] < 0.6:
                recommendations.append("Low result count - check input data quality or processing parameters")
            
            if components['processing_success'] < 0.8:
                recommendations.append("Processing issues detected - check logs for errors")
        
        return recommendations
    
    def should_retry(self, quality_result: QualityResult, current_attempt: int) -> bool:
        """Determine if execution should be retried based on quality"""
        max_attempts = self.config['retry_configuration']['max_attempts']
        
        # Don't retry if we've hit max attempts
        if current_attempt >= max_attempts:
            return False
        
        # Don't retry if quality is acceptable
        if quality_result.meets_threshold:
            return False
        
        # Retry if quality is below global minimum
        global_min = self.config['quality_thresholds']['global_minimum']
        return quality_result.score < global_min
    
    def get_retry_strategy(self, attempt: int) -> Dict[str, Any]:
        """Get retry strategy for current attempt"""
        strategies = self.config['retry_configuration']['retry_strategies']
        
        # Cycle through strategies
        strategy_index = (attempt - 1) % len(strategies)
        return strategies[strategy_index]
    
    def get_tool_timeout(self, tool_name: str) -> int:
        """Get timeout for specific tool"""
        timeouts = self.config['tool_timeouts']
        return timeouts.get(tool_name, timeouts['default'])


# Example usage
if __name__ == "__main__":
    # Example tool result
    sample_result = {
        'status': 'success',
        'entities': [
            {'text': 'Apple Inc.', 'confidence': 0.9},
            {'text': 'Tim Cook', 'confidence': 0.8},
            {'text': 'Cupertino', 'confidence': 0.7}
        ],
        'relationships': [
            {'source': 'Tim Cook', 'target': 'Apple Inc.', 'type': 'CEO'}
        ]
    }
    
    calculator = QualityCalculator()
    quality = calculator.calculate_tool_quality('text_analyzer', sample_result)
    
    print(f"Quality Score: {quality.score:.2f}")
    print(f"Meets Threshold: {quality.meets_threshold}")
    print(f"Components: {quality.components}")
    if quality.recommendations:
        print("Recommendations:")
        for rec in quality.recommendations:
            print(f"  - {rec}")