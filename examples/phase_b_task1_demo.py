#!/usr/bin/env python3
"""
Phase B Task 1 Demo: Advanced Question Analysis & Intent Classification
Demonstrates the new advanced question analysis capabilities
"""
from src.nlp.advanced_intent_classifier import AdvancedIntentClassifier, QuestionIntent
from src.nlp.question_complexity_analyzer import QuestionComplexityAnalyzer, ComplexityLevel
from src.nlp.context_extractor import ContextExtractor
from src.nlp.tool_chain_generator import ToolChainGenerator

def demo_advanced_question_analysis():
    """Demonstrate advanced question analysis capabilities"""
    print("=== Phase B Task 1: Advanced Question Analysis Demo ===\n")
    
    # Initialize components
    classifier = AdvancedIntentClassifier()
    complexity_analyzer = QuestionComplexityAnalyzer()
    context_extractor = ContextExtractor()
    chain_generator = ToolChainGenerator()
    
    # Test questions of varying complexity
    test_questions = [
        # Simple questions
        "What companies are mentioned in this document?",
        
        # Moderate complexity
        "Compare Microsoft and Google's AI strategies",
        
        # Complex multi-intent questions
        "Analyze the evolution of cloud computing from 2010 to 2024, identify key players and their market share, predict future trends, and compare AWS vs Azure vs GCP performance metrics",
        
        # Advanced pattern analysis
        "What patterns emerge in customer sentiment across different product categories and how do they correlate with sales data?",
        
        # Temporal + Causal analysis
        "What caused the shift in consumer behavior during 2020-2021 and how did companies adapt their strategies?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"Question {i}: {question}")
        print(f"{'='*80}")
        
        # 1. Intent Classification
        intent_result = classifier.classify(question)
        print(f"\n1. INTENT CLASSIFICATION:")
        print(f"   Primary Intent: {intent_result.primary_intent.value}")
        print(f"   Confidence: {intent_result.confidence:.2f}")
        if intent_result.secondary_intents:
            print(f"   Secondary Intents: {[i.value for i in intent_result.secondary_intents]}")
        print(f"   Multi-step Required: {intent_result.requires_multi_step}")
        print(f"   Recommended Tools: {intent_result.recommended_tools}")
        
        # 2. Complexity Analysis
        complexity_result = complexity_analyzer.analyze(question, intent_result)
        print(f"\n2. COMPLEXITY ANALYSIS:")
        print(f"   Level: {complexity_result.level.value}")
        print(f"   Estimated Tools: {complexity_result.estimated_tools}")
        print(f"   Parallelizable Components: {complexity_result.parallelizable_components}")
        print(f"   Estimated Time: {complexity_result.estimated_time_seconds}s")
        print(f"   Estimated Memory: {complexity_result.estimated_memory_mb}MB")
        print(f"   Execution Strategy: {complexity_result.execution_strategy}")
        
        # 3. Context Extraction
        context_result = context_extractor.extract(question)
        print(f"\n3. CONTEXT EXTRACTION:")
        if context_result.mentioned_entities:
            print(f"   Entities: {context_result.mentioned_entities}")
        if context_result.has_temporal_context:
            print(f"   Temporal: {context_result.temporal_constraints}")
        if context_result.requires_comparison:
            print(f"   Comparison Type: {context_result.comparison_type}")
        if context_result.requires_aggregation:
            print(f"   Aggregation: {context_result.aggregation_type} ({context_result.aggregation_scope})")
        if context_result.ambiguity_level > 0:
            print(f"   Ambiguity Level: {context_result.ambiguity_level:.2f}")
            print(f"   Missing Context: {context_result.missing_context}")
        
        # 4. Tool Chain Generation
        tool_chain = chain_generator.generate_chain(
            intent_result, complexity_result, context_result, question
        )
        print(f"\n4. OPTIMAL TOOL CHAIN:")
        print(f"   Total Steps: {len(tool_chain.steps)}")
        print(f"   Can Parallelize: {tool_chain.can_parallelize}")
        print(f"   Execution DAG:")
        for step in tool_chain.steps:
            deps = f" (depends on: {step.depends_on})" if step.depends_on else ""
            print(f"      - {step.tool_id}{deps}")
        if tool_chain.optimization_notes:
            print(f"   Optimization Notes:")
            for note in tool_chain.optimization_notes:
                print(f"      * {note}")
    
    print("\n" + "="*80)
    print("PHASE B TASK 1 CAPABILITIES SUMMARY:")
    print("="*80)
    print("✓ 15 Intent Categories (vs 5 in Phase A)")
    print("✓ Multi-dimensional question analysis")
    print("✓ Complexity-based execution planning")
    print("✓ Context-aware tool selection")
    print("✓ Dynamic tool chain generation")
    print("✓ Parallelization opportunity detection")
    print("✓ Resource estimation and optimization")
    print("\nReady for Phase B Task 2: Dynamic DAG Builder & Execution Planner")

if __name__ == "__main__":
    demo_advanced_question_analysis()