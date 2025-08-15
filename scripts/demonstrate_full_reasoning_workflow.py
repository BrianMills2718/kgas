#!/usr/bin/env python3
"""
Demonstrate Full Reasoning-Enhanced Workflow

Complete example applying the enhanced reasoning system to Carter's Naval Academy speech,
showing comprehensive decision trace capture throughout the analysis pipeline.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def demonstrate_full_workflow():
    """Demonstrate complete reasoning-enhanced workflow"""
    print("🚀 Full Reasoning-Enhanced Workflow Demonstration")
    print("Document: Carter Naval Academy Speech (1978)")
    print("=" * 70)
    
    document_path = "/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/texts/carter_anapolis.txt"
    
    if not os.path.exists(document_path):
        print(f"❌ Document not found: {document_path}")
        return False
    
    try:
        from src.agents.reasoning_enhanced_workflow_agent import ReasoningEnhancedWorkflowAgent
        from src.core.workflow_schema import AgentRequest, AgentLayer
        from src.core.reasoning_query_interface import ReasoningQueryInterface
        
        print("1. Initializing Reasoning-Enhanced Workflow Agent...")
        
        # Create workflow agent with full reasoning capture
        agent = ReasoningEnhancedWorkflowAgent(
            api_client=None,  # Will create enhanced API client
            reasoning_store=None,  # Will create reasoning store
            capture_reasoning=True  # Enable comprehensive reasoning capture
        )
        
        print(f"   ✅ Agent initialized with reasoning database: reasoning_traces.db")
        
        print("\n2. Creating Workflow Generation Request...")
        
        # Create comprehensive analysis request
        request = AgentRequest(
            natural_language_description=(
                "Analyze the Carter Naval Academy speech document to extract key entities, relationships, "
                "and themes. Focus on political entities (countries, leaders), military concepts, "
                "policy positions, and international relations. Generate a comprehensive analysis "
                "workflow that processes the full document text and produces structured insights."
            ),
            layer=AgentLayer.LAYER_2,  # User review layer for transparency
            available_documents=[document_path],
            target_outputs=[
                "entities_extracted",
                "relationships_identified", 
                "key_themes",
                "policy_positions",
                "international_relations_analysis"
            ],
            constraints={
                "text_processing": "Process complete document text without truncation",
                "context_preservation": "Maintain context throughout analysis", 
                "evidence_requirement": "Provide evidence for all extracted entities and relationships"
            }
        )
        
        print(f"   ✅ Request created for document analysis")
        print(f"   Document: {document_path}")
        print(f"   Target outputs: {len(request.target_outputs)} analysis types")
        
        print("\n3. Executing Reasoning-Enhanced Workflow Generation...")
        
        start_time = time.time()
        
        # This will create a comprehensive reasoning trace
        response = agent.generate_workflow(request)
        
        execution_time = time.time() - start_time
        
        print(f"   ⏱️  Workflow generation completed in {execution_time:.1f} seconds")
        print(f"   📊 Response status: {response.status}")
        
        if hasattr(response, 'reasoning_trace_id') and response.reasoning_trace_id:
            trace_id = response.reasoning_trace_id
            print(f"   🧠 Reasoning trace captured: {trace_id}")
            
            print("\n4. Analyzing Captured Reasoning Trace...")
            
            # Get the reasoning trace
            reasoning_trace = agent.get_reasoning_trace(trace_id)
            
            if reasoning_trace:
                print(f"   ✅ Reasoning trace retrieved successfully")
                print(f"   📈 Total reasoning steps: {len(reasoning_trace.all_steps)}")
                print(f"   🎯 Overall confidence: {reasoning_trace.overall_confidence:.2f}")
                print(f"   ✅ Workflow success: {reasoning_trace.success}")
                
                print("\n5. Decision-Level Breakdown...")
                
                # Analyze decision levels
                from src.core.reasoning_trace import DecisionLevel, ReasoningType
                
                level_counts = {}
                type_counts = {}
                
                for step_id, step in reasoning_trace.all_steps.items():
                    level = step.decision_level.value
                    rtype = step.reasoning_type.value
                    
                    level_counts[level] = level_counts.get(level, 0) + 1
                    type_counts[rtype] = type_counts.get(rtype, 0) + 1
                
                print("   Decision Levels:")
                for level, count in level_counts.items():
                    print(f"   • {level}: {count} decisions")
                
                print("   Reasoning Types:")
                for rtype, count in type_counts.items():
                    print(f"   • {rtype}: {count} steps")
                
                print("\n6. Key Decision Points...")
                
                # Show key decision points with confidence
                key_decisions = []
                for step_id, step in reasoning_trace.all_steps.items():
                    if step.confidence_score >= 0.7:  # High confidence decisions
                        key_decisions.append((
                            step.decision_point,
                            step.confidence_score,
                            step.reasoning_text[:100] + "..." if len(step.reasoning_text) > 100 else step.reasoning_text
                        ))
                
                key_decisions.sort(key=lambda x: x[1], reverse=True)  # Sort by confidence
                
                for i, (decision, confidence, reasoning) in enumerate(key_decisions[:5]):
                    print(f"   {i+1}. {decision}")
                    print(f"      Confidence: {confidence:.2f}")
                    print(f"      Reasoning: {reasoning}")
                    print()
                
                print("7. Advanced Reasoning Analysis...")
                
                # Use query interface for advanced analysis
                query_interface = ReasoningQueryInterface(agent.reasoning_store)
                
                # Analyze the trace
                analysis = query_interface.analyze_trace(trace_id)
                
                if analysis:
                    print(f"   📊 Reasoning Quality Score: {analysis.reasoning_quality_score:.2f}")
                    print(f"   🎯 Decision Consistency Score: {analysis.decision_consistency_score:.2f}")
                    print(f"   📈 Confidence Calibration Score: {analysis.confidence_calibration_score:.2f}")
                    
                    if analysis.identified_issues:
                        print("   ⚠️  Identified Issues:")
                        for issue in analysis.identified_issues:
                            print(f"      • {issue}")
                    
                    if analysis.improvement_suggestions:
                        print("   💡 Improvement Suggestions:")
                        for suggestion in analysis.improvement_suggestions:
                            print(f"      • {suggestion}")
                
                print("\n8. Workflow Generation Results...")
                
                if response.status == "requires_review":
                    print("   ✅ Workflow generated successfully (requires user review)")
                    
                    if hasattr(response, 'generated_workflow') and response.generated_workflow:
                        workflow = response.generated_workflow
                        print(f"   📋 Workflow steps: {len(workflow.steps) if hasattr(workflow, 'steps') else 'N/A'}")
                        
                        if hasattr(workflow, 'metadata'):
                            print(f"   🏷️  Workflow name: {workflow.metadata.name}")
                        
                    if hasattr(response, 'assumptions') and response.assumptions:
                        print("   🤔 Key Assumptions:")
                        for assumption in response.assumptions:
                            print(f"      • {assumption}")
                    
                    if hasattr(response, 'suggestions') and response.suggestions:
                        print("   💡 Next Steps:")
                        for suggestion in response.suggestions:
                            print(f"      • {suggestion}")
                
                elif response.status == "success":
                    print("   🎉 Workflow generated and ready for execution")
                
                else:
                    print(f"   ⚠️  Workflow generation status: {response.status}")
                    if hasattr(response, 'error_message'):
                        print(f"   ❌ Error: {response.error_message}")
                
                print("\n🎉 REASONING-ENHANCED WORKFLOW DEMONSTRATION COMPLETE")
                print("=" * 70)
                print("✅ Full reasoning trace captured and analyzed")
                print("✅ Hierarchical decision structure validated")
                print("✅ Advanced reasoning analysis completed") 
                print("✅ Workflow generation with transparent decision-making")
                
                return True
                
            else:
                print("   ❌ Failed to retrieve reasoning trace")
                return False
                
        else:
            print("   ⚠️  No reasoning trace ID in response")
            print("   This may indicate reasoning capture was disabled")
            return False
            
    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the full reasoning workflow demonstration"""
    success = demonstrate_full_workflow()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)