#!/usr/bin/env python3
"""
Quality Service Integration for KGAS Framework
Connects QualityService to track quality alongside uncertainty
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import json

@dataclass
class QualityAssessment:
    """Quality assessment for a pipeline step"""
    confidence_score: float
    quality_tier: str  # HIGH, MEDIUM, LOW, UNCERTAIN
    factors: Dict[str, float]
    reasoning: str

class QualityIntegratedFramework:
    """
    Enhanced framework that integrates QualityService
    Tracks both uncertainty and quality for each pipeline step
    """
    
    def __init__(self, framework, quality_service):
        """
        Initialize with existing framework and quality service
        
        Args:
            framework: CleanToolFramework instance
            quality_service: QualityService instance
        """
        self.framework = framework
        self.quality = quality_service
        
        # Wrap the execute_chain method to add quality tracking
        self._original_execute = framework.execute_chain
        framework.execute_chain = self._quality_enhanced_execute
    
    def _quality_enhanced_execute(self, chain: List[str], input_data: Any):
        """
        Enhanced execution that tracks quality alongside uncertainty
        """
        # Track quality assessments for each step
        quality_assessments = []
        
        # Store original method temporarily
        original_method = self.framework.execute_chain
        self.framework.execute_chain = self._original_execute
        
        try:
            # Execute the original chain
            result = self._original_execute(chain, input_data)
            
            if result.success:
                # Assess quality for each step
                for i, (tool_id, uncertainty, reasoning) in enumerate(zip(
                    chain, 
                    result.step_uncertainties, 
                    result.step_reasonings
                )):
                    # Convert uncertainty to confidence (inverse relationship)
                    base_confidence = 1.0 - uncertainty
                    
                    # Factors that affect quality
                    factors = self._determine_quality_factors(
                        tool_id, 
                        uncertainty,
                        i, 
                        len(chain)
                    )
                    
                    # Assess confidence using QualityService
                    confidence = self.quality.assess_confidence(
                        object_ref=f"pipeline_step_{i}_{tool_id}",
                        base_confidence=base_confidence,
                        factors=factors
                    )
                    
                    # Store assessment
                    assessment = QualityAssessment(
                        confidence_score=confidence['confidence'],
                        quality_tier=confidence['quality_tier'],
                        factors=factors,
                        reasoning=f"{reasoning} | Quality: {confidence['quality_tier']}"
                    )
                    quality_assessments.append(assessment)
                
                # Calculate combined quality-adjusted uncertainty
                combined_quality = self._combine_quality_uncertainty(
                    result.step_uncertainties,
                    quality_assessments
                )
                
                # Add quality data to result
                result.quality_assessments = quality_assessments
                result.quality_adjusted_uncertainty = combined_quality['adjusted_uncertainty']
                result.overall_quality_tier = combined_quality['overall_tier']
                
                # Log quality summary
                print(f"\n📊 Quality Assessment Summary:")
                print(f"   Original uncertainty: {result.total_uncertainty:.3f}")
                print(f"   Quality-adjusted uncertainty: {combined_quality['adjusted_uncertainty']:.3f}")
                print(f"   Overall quality tier: {combined_quality['overall_tier']}")
                
                for i, (tool, assessment) in enumerate(zip(chain, quality_assessments)):
                    print(f"   Step {i+1} ({tool}): {assessment.quality_tier} "
                          f"(confidence: {assessment.confidence_score:.3f})")
            
            return result
            
        finally:
            # Restore wrapped method
            self.framework.execute_chain = original_method
    
    def _determine_quality_factors(self, tool_id: str, uncertainty: float, 
                                   step_index: int, total_steps: int) -> Dict[str, float]:
        """
        Determine factors that affect quality for a tool
        """
        factors = {}
        
        # Tool-specific quality factors
        if 'load' in tool_id.lower():
            factors['data_completeness'] = 0.95  # Loaders usually preserve data well
            factors['format_preservation'] = 0.90
        elif 'extract' in tool_id.lower():
            factors['extraction_accuracy'] = 0.8 if uncertainty < 0.3 else 0.6
            factors['semantic_preservation'] = 0.75
        elif 'persist' in tool_id.lower() or 'graph' in tool_id.lower():
            factors['storage_reliability'] = 0.99  # Storage is highly reliable
            factors['data_integrity'] = 0.95
        else:
            factors['processing_quality'] = 0.8
        
        # Position in pipeline affects quality
        if step_index == 0:
            factors['source_quality'] = 0.9  # First step has good source
        elif step_index == total_steps - 1:
            factors['final_validation'] = 0.85  # Last step gets validation
        else:
            factors['intermediate_quality'] = 0.75  # Middle steps have more variance
        
        # Uncertainty affects quality
        if uncertainty < 0.1:
            factors['low_uncertainty_bonus'] = 0.1
        elif uncertainty > 0.5:
            factors['high_uncertainty_penalty'] = -0.2
        
        return factors
    
    def _combine_quality_uncertainty(self, uncertainties: List[float], 
                                    assessments: List[QualityAssessment]) -> Dict:
        """
        Combine uncertainty with quality assessments for final score
        """
        # Use quality service to aggregate confidence scores
        confidence_scores = [a.confidence_score for a in assessments]
        
        avg_confidence = self.quality.aggregate_confidence(
            confidence_scores=confidence_scores,
            aggregation_method='weighted_mean'
        )
        avg_quality_factor = avg_confidence  # 0 to 1
        
        # Original uncertainty (physics model)
        confidence = 1.0
        for u in uncertainties:
            confidence *= (1 - u)
        original_uncertainty = 1 - confidence
        
        # Quality adjustment: high quality reduces effective uncertainty
        # Low quality increases effective uncertainty
        quality_adjustment = 1.0 - (0.5 * avg_quality_factor)  # 0.5 to 1.0
        adjusted_uncertainty = original_uncertainty * quality_adjustment
        
        # Determine overall tier
        if avg_confidence >= 0.9:
            overall_tier = "HIGH"
        elif avg_confidence >= 0.7:
            overall_tier = "MEDIUM"
        elif avg_confidence >= 0.5:
            overall_tier = "LOW"
        else:
            overall_tier = "UNCERTAIN"
        
        return {
            'adjusted_uncertainty': adjusted_uncertainty,
            'overall_tier': overall_tier,
            'average_confidence': avg_confidence,
            'quality_factor': avg_quality_factor
        }
    
    def get_quality_statistics(self) -> Dict[str, Any]:
        """Get quality statistics from the service"""
        return self.quality.get_statistics()


# Test the integration
if __name__ == "__main__":
    import sys
    from pathlib import Path
    from dotenv import load_dotenv
    
    load_dotenv('/home/brian/projects/Digimons/.env')
    sys.path.append('/home/brian/projects/Digimons')
    sys.path.append('/home/brian/projects/Digimons/tool_compatability/poc/vertical_slice')
    
    from neo4j import GraphDatabase
    from framework.clean_framework import CleanToolFramework, ToolCapabilities, DataType
    from tools.text_loader_v3 import TextLoaderV3
    from tools.knowledge_graph_extractor import KnowledgeGraphExtractor
    from tools.graph_persister import GraphPersister
    from src.services.quality_service import QualityService
    
    print("=== Testing Quality Service Integration ===\n")
    
    # Initialize components
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "devpassword"))
    framework = CleanToolFramework("bolt://localhost:7687", "vertical_slice.db")
    quality_service = QualityService(driver)
    
    # Create quality-integrated framework
    qi_framework = QualityIntegratedFramework(framework, quality_service)
    
    # Register tools
    framework.register_tool(TextLoaderV3(), ToolCapabilities(
        tool_id="TextLoaderV3",
        input_type=DataType.FILE,
        output_type=DataType.TEXT,
        input_construct="file_path",
        output_construct="character_sequence",
        transformation_type="text_extraction"
    ))
    
    framework.register_tool(KnowledgeGraphExtractor(), ToolCapabilities(
        tool_id="KnowledgeGraphExtractor",
        input_type=DataType.TEXT,
        output_type=DataType.KNOWLEDGE_GRAPH,
        input_construct="character_sequence",
        output_construct="knowledge_graph",
        transformation_type="knowledge_graph_extraction"
    ))
    
    framework.register_tool(
        GraphPersister(framework.neo4j, framework.identity, framework.crossmodal),
        ToolCapabilities(
            tool_id="GraphPersister",
            input_type=DataType.KNOWLEDGE_GRAPH,
            output_type=DataType.NEO4J_GRAPH,
            input_construct="knowledge_graph",
            output_construct="persisted_graph",
            transformation_type="graph_persistence"
        )
    )
    
    # Create test file
    test_file = "test_quality.txt"
    with open(test_file, 'w') as f:
        f.write("Brian Chhun developed KGAS at the University of Melbourne.")
    
    # Execute with quality tracking
    chain = framework.find_chain(DataType.FILE, DataType.NEO4J_GRAPH)
    result = framework.execute_chain(chain, test_file)
    
    if result.success:
        print("\n✅ Pipeline executed with quality tracking")
        print(f"Quality-adjusted uncertainty: {result.quality_adjusted_uncertainty:.3f}")
        print(f"Overall quality tier: {result.overall_quality_tier}")
    
    # Clean up
    import os
    os.remove(test_file)
    framework.cleanup()
    driver.close()
    
    print("\n✅ Quality integration test complete")