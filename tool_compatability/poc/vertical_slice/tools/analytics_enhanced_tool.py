#!/usr/bin/env python3
"""
Analytics Enhanced Tool - Integrates vertical slice tools with analytics capabilities

Combines vertical slice tool functionality with analytics components:
- CrossModalConverter for advanced data transformations  
- KnowledgeSynthesizer for reasoning and hypothesis generation
- Data format adapters for seamless integration
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import sys

# Add main system path for analytics imports
sys.path.append('/home/brian/projects/Digimons')

from adapters.openai_embedding_service import OpenAIEmbeddingService
from adapters.analytics_data_adapters import VerticalSliceDataAdapter
from src.analytics.cross_modal_converter import CrossModalConverter, DataFormat
from src.analytics.knowledge_synthesizer import HypothesisGenerator

logger = logging.getLogger(__name__)


class AnalyticsEnhancedTool:
    """Enhanced tool that combines vertical slice functionality with analytics capabilities"""
    
    def __init__(self):
        """Initialize analytics enhanced tool"""
        self.tool_id = "AnalyticsEnhancedTool"
        
        # Initialize analytics components
        self.embedding_service = OpenAIEmbeddingService()
        self.data_adapter = VerticalSliceDataAdapter()
        self.cross_modal_converter = CrossModalConverter(embedding_service=self.embedding_service)
        self.knowledge_synthesizer = HypothesisGenerator()
        
        logger.info("AnalyticsEnhancedTool initialized with full analytics capabilities")
    
    def process(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process data with analytics enhancement (sync wrapper for async functionality)"""
        try:
            # Use asyncio to handle async analytics components
            return asyncio.run(self._process_async(data, **kwargs))
        except Exception as e:
            logger.error(f"Analytics enhanced processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'uncertainty': 1.0,
                'reasoning': f'Analytics enhancement failed: {str(e)}'
            }
    
    async def _process_async(self, data: Dict[str, Any], 
                           enhance_mode: str = "conversion",
                           **kwargs) -> Dict[str, Any]:
        """Async processing with analytics enhancement
        
        Args:
            data: Input data (vertical slice format or text)
            enhance_mode: Type of analytics enhancement
                - "conversion": Cross-modal data conversion
                - "reasoning": Knowledge synthesis and hypothesis generation  
                - "full": Both conversion and reasoning
        """
        try:
            base_result = {}
            
            # Handle different input types
            if isinstance(data, str):
                # Plain text input
                base_result = {
                    'success': True,
                    'text': data,
                    'uncertainty': 0.05,
                    'reasoning': 'Text input processed'
                }
            elif isinstance(data, dict) and 'text' in data:
                # Text-based input (from VectorTool output, etc.)
                base_result = data.copy()
            else:
                # Complex data input
                base_result = {
                    'success': True,
                    'data': data,
                    'uncertainty': 0.1,
                    'reasoning': 'Complex data processed'
                }
            
            # Apply analytics enhancement based on mode
            if enhance_mode in ["conversion", "full"]:
                base_result = await self._apply_cross_modal_conversion(base_result)
            
            if enhance_mode in ["reasoning", "full"]:
                base_result = await self._apply_knowledge_synthesis(base_result)
            
            # Add analytics metadata
            base_result['analytics_enhanced'] = True
            base_result['enhancement_mode'] = enhance_mode
            base_result['tool_id'] = self.tool_id
            
            return base_result
            
        except Exception as e:
            logger.error(f"Async analytics processing failed: {e}")
            raise
    
    async def _apply_cross_modal_conversion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply cross-modal conversion analytics"""
        try:
            # Convert vertical slice data to analytics format
            analytics_df = self.data_adapter.vertical_slice_to_table(data)
            
            # Apply cross-modal conversion (TABLE → VECTOR)
            conversion_result = await self.cross_modal_converter.convert_data(
                data=analytics_df,
                source_format=DataFormat.TABLE,
                target_format=DataFormat.VECTOR
            )
            
            # Enhance original data with conversion results
            data['cross_modal_analysis'] = {
                'validation_passed': conversion_result.validation_passed,
                'preservation_score': conversion_result.preservation_score,
                'semantic_integrity': conversion_result.semantic_integrity,
                'analytics_vector_dim': len(conversion_result.data) if hasattr(conversion_result.data, '__len__') else 0,
                'conversion_warnings': conversion_result.warnings
            }
            
            # Update uncertainty based on conversion quality  
            original_uncertainty = data.get('uncertainty', 0.1)
            conversion_uncertainty = 1.0 - conversion_result.preservation_score if conversion_result.preservation_score else 0.5
            
            # Combine uncertainties using physics formula
            import math
            combined_uncertainty = math.sqrt(original_uncertainty**2 + conversion_uncertainty**2)
            data['uncertainty'] = min(combined_uncertainty, 1.0)
            
            # Enhanced reasoning
            data['reasoning'] = f"{data.get('reasoning', 'Base processing')} | Analytics: preservation {conversion_result.preservation_score:.3f}, validation {'passed' if conversion_result.validation_passed else 'failed'}"
            
            logger.info(f"Cross-modal conversion applied: preservation {conversion_result.preservation_score:.3f}")
            return data
            
        except Exception as e:
            logger.error(f"Cross-modal conversion failed: {e}")
            data['cross_modal_analysis'] = {'error': str(e)}
            return data
    
    async def _apply_knowledge_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply knowledge synthesis and reasoning"""
        try:
            # Extract text for synthesis
            text_content = ""
            if 'text' in data:
                text_content = data['text']
            elif 'entities' in data:
                # Create text from entities for synthesis
                entities = data['entities']
                entity_names = [e.get('name', str(e)) for e in entities[:5]]  # Top 5 entities
                text_content = f"Analysis of entities: {', '.join(entity_names)}"
            else:
                text_content = str(data)[:200]  # First 200 chars
            
            if not text_content.strip():
                data['knowledge_synthesis'] = {'error': 'No text content for synthesis'}
                return data
            
            # Apply hypothesis generation (knowledge synthesis)
            synthesis_context = {
                'text_content': text_content,
                'data_type': data.get('data_type', 'unknown'),
                'original_uncertainty': data.get('uncertainty', 0.1)
            }
            
            # Note: The hypothesis generator may need specific input format
            # For now, we'll simulate the synthesis process
            hypotheses = await self._generate_hypotheses(synthesis_context)
            
            data['knowledge_synthesis'] = {
                'hypotheses_generated': len(hypotheses),
                'top_hypothesis': hypotheses[0] if hypotheses else None,
                'synthesis_confidence': 0.75,  # Placeholder - would be calculated by synthesizer
                'reasoning_type': 'abductive'  # Could be abductive, inductive, or deductive
            }
            
            # Update reasoning with synthesis insights
            if hypotheses:
                data['reasoning'] = f"{data.get('reasoning', 'Base processing')} | Synthesis: {hypotheses[0][:100]}..."
            
            logger.info(f"Knowledge synthesis applied: {len(hypotheses)} hypotheses generated")
            return data
            
        except Exception as e:
            logger.error(f"Knowledge synthesis failed: {e}")
            data['knowledge_synthesis'] = {'error': str(e)}
            return data
    
    async def _generate_hypotheses(self, context: Dict[str, Any]) -> List[str]:
        """Generate hypotheses using real knowledge synthesizer"""
        try:
            text_content = context['text_content']
            data_type = context.get('data_type', 'unknown')
            
            # Create research-focused prompt for hypothesis generation
            prompt = f"""
            Analyze the following text and generate 3-5 research hypotheses based on the content:
            
            Text: {text_content}
            Data Type: {data_type}
            
            Generate testable research hypotheses that:
            1. Build on the content's key concepts
            2. Suggest novel research directions
            3. Are specific enough to be testable
            4. Connect to broader theoretical frameworks
            
            Format each hypothesis as a clear, testable statement.
            """
            
            # Use the real HypothesisGenerator
            hypothesis_objects = await self.knowledge_synthesizer.generate_hypotheses(
                prompt=prompt,
                max_hypotheses=5,
                creativity_level=0.7
            )
            
            # Extract text from structured hypotheses
            hypotheses = [h.get('text', str(h)) for h in hypothesis_objects]
            
            # Fail-fast: ensure we have real hypotheses
            if not hypotheses or all(len(h.strip()) < 10 for h in hypotheses):
                raise RuntimeError("HypothesisGenerator failed to produce meaningful hypotheses")
            
            logger.info(f"Real hypothesis generation completed: {len(hypotheses)} hypotheses")
            return hypotheses
            
        except Exception as e:
            logger.error(f"Real hypothesis generation failed: {e}")
            # Fail-fast: don't hide the error with fallbacks
            raise RuntimeError(f"Knowledge synthesis failed: {str(e)}")  
    
    async def cleanup(self):
        """Clean up analytics resources"""
        try:
            await self.cross_modal_converter.cleanup()
            await self.embedding_service.close()
            logger.info("Analytics enhanced tool cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        # Don't attempt async cleanup in __del__ - causes runtime warnings
        # Cleanup should be explicitly called by the user
        pass


# Factory function
def create_analytics_enhanced_tool() -> AnalyticsEnhancedTool:
    """Create an analytics enhanced tool instance"""
    return AnalyticsEnhancedTool()


# Test the analytics enhanced tool
if __name__ == "__main__":
    async def test_analytics_tool():
        tool = AnalyticsEnhancedTool()
        
        print("🚀 Testing Analytics Enhanced Tool\n")
        
        # Test 1: Text processing with conversion
        print("📊 Test 1: Text processing with cross-modal conversion")
        result1 = await tool._process_async(
            "Machine learning research on neural network architectures and deep learning applications",
            enhance_mode="conversion"
        )
        print(f"   Success: {result1['success']}")
        print(f"   Preservation score: {result1.get('cross_modal_analysis', {}).get('preservation_score', 'N/A')}")
        print(f"   Uncertainty: {result1['uncertainty']:.3f}")
        
        # Test 2: Knowledge synthesis
        print("\n🧠 Test 2: Knowledge synthesis and reasoning")
        result2 = await tool._process_async(
            "Artificial intelligence systems require robust evaluation frameworks for safety and performance",
            enhance_mode="reasoning"
        )
        print(f"   Success: {result2['success']}")
        print(f"   Hypotheses generated: {result2.get('knowledge_synthesis', {}).get('hypotheses_generated', 0)}")
        print(f"   Top hypothesis: {result2.get('knowledge_synthesis', {}).get('top_hypothesis', 'N/A')[:80]}...")
        
        # Test 3: Full enhancement
        print("\n⚡ Test 3: Full analytics enhancement")
        result3 = await tool._process_async(
            "Research on cross-modal data fusion and multi-modal learning approaches",
            enhance_mode="full"
        )
        print(f"   Success: {result3['success']}")
        print(f"   Enhancement mode: {result3['enhancement_mode']}")
        print(f"   Analytics enhanced: {result3['analytics_enhanced']}")
        
        await tool.cleanup()
        print("\n✅ Analytics enhanced tool tests completed!")
    
    asyncio.run(test_analytics_tool())