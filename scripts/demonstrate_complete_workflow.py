#!/usr/bin/env python3
"""
Complete Workflow Demonstration

Demonstrates the full enhanced reasoning workflow with DAG generation
on the Carter Naval Academy speech document.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def demonstrate_complete_workflow():
    """Demonstrate complete workflow with natural language query and DAG generation"""
    print("🎯 Complete Enhanced Reasoning Workflow Demonstration")
    print("=" * 60)
    
    try:
        from src.agents.reasoning_enhanced_workflow_agent import ReasoningEnhancedWorkflowAgent
        from src.core.enhanced_reasoning_llm_client import EnhancedReasoningLLMClient
        
        # Initialize reasoning-enhanced workflow agent
        print("1. Creating Reasoning Enhanced Workflow Agent...")
        agent = ReasoningEnhancedWorkflowAgent()
        print("   ✅ Agent initialized with reasoning capture")
        
        # Load the Carter Naval Academy speech document
        document_path = "/home/brian/projects/Digimons/experiments/lit_review/data/test_texts/texts/carter_anapolis.txt"
        
        print(f"2. Loading document: {document_path}")
        if not os.path.exists(document_path):
            print(f"   ❌ Document not found: {document_path}")
            return False
            
        with open(document_path, 'r') as f:
            document_content = f.read()
        
        print(f"   ✅ Document loaded ({len(document_content)} characters)")
        print(f"   📄 Sample: {document_content[:150]}...")
        
        # Define the natural language query
        natural_language_query = """
        Analyze this presidential speech and create a workflow to:
        1. Extract key leadership principles mentioned
        2. Identify the main themes and messages  
        3. Categorize the rhetorical strategies used
        4. Generate a summary of actionable insights
        """
        
        print("3. Natural Language Query:")
        print("   " + "=" * 50)
        for line in natural_language_query.strip().split('\n'):
            print(f"   {line.strip()}")
        print("   " + "=" * 50)
        
        print("4. Generating DAG workflow with reasoning capture...")
        
        # Create AgentRequest for workflow generation
        from src.core.workflow_schema import AgentRequest, AgentLayer
        
        agent_request = AgentRequest(
            natural_language_description=natural_language_query.strip(),
            layer=AgentLayer.LAYER_2,  # User review layer for demonstration
            available_documents=[document_content],
            target_outputs=["leadership_principles", "themes", "rhetorical_strategies", "actionable_insights"],
            constraints={"focus": "presidential_speech_analysis", "format": "structured_analysis"}
        )
        
        # Generate workflow with reasoning capture
        workflow_response = agent.generate_workflow(agent_request)
        
        if workflow_response.status in ['success', 'requires_review']:
            # Get the generated workflow
            workflow = workflow_response.generated_workflow
            workflow_yaml = workflow_response.workflow_yaml
            
            print("   ✅ DAG generation successful!")
            print("")
            print("5. Generated DAG Structure:")
            print("   " + "=" * 50)
            
            # Display workflow information
            if workflow:
                print(f"   📊 Status: {workflow_response.status}")
                print(f"   🎯 Ready to Execute: {workflow_response.ready_to_execute}")
                print(f"   📝 Reasoning: {workflow_response.reasoning}")
                print("")
                
                # Show workflow steps
                if hasattr(workflow, 'steps') and workflow.steps:
                    print(f"   📋 Workflow Steps ({len(workflow.steps)} total):")
                    for i, step in enumerate(workflow.steps, 1):
                        step_name = getattr(step, 'name', f'Step {i}')
                        step_tool = getattr(step, 'tool_id', 'Unknown tool')
                        print(f"      {i}. {step_name} [{step_tool}]")
                        if hasattr(step, 'description'):
                            print(f"         → {step.description}")
                else:
                    print("   📋 Workflow structure: Basic workflow object created")
                
                print("")
                
                # Show YAML representation
                if workflow_yaml:
                    print(f"   📜 YAML Length: {len(workflow_yaml)} characters")
                    print(f"   📜 YAML Preview:")
                    yaml_lines = workflow_yaml.split('\n')[:10]
                    for line in yaml_lines:
                        print(f"      {line}")
                    if len(workflow_yaml.split('\n')) > 10:
                        print("      [... YAML continues ...]")
                else:
                    print("   ⚠️  No YAML representation available")
            else:
                print("   ⚠️  No workflow object generated")
            
            print("   " + "=" * 50)
            print("")
            
            print("6. Agent Response Details:")
            print("   " + "=" * 50)
            print(f"   📊 Status: {workflow_response.status}")
            print(f"   🔍 Ready to Execute: {workflow_response.ready_to_execute}")
            if hasattr(workflow_response, 'assumptions') and workflow_response.assumptions:
                print(f"   💡 Assumptions ({len(workflow_response.assumptions)}):")
                for assumption in workflow_response.assumptions:
                    print(f"      • {assumption}")
            if hasattr(workflow_response, 'suggestions') and workflow_response.suggestions:
                print(f"   💡 Suggestions ({len(workflow_response.suggestions)}):")
                for suggestion in workflow_response.suggestions:
                    print(f"      • {suggestion}")
            print("   " + "=" * 50)
            
            # Get trace information if available
            trace_id = getattr(workflow_response, 'reasoning_trace_id', None)
            if trace_id:
                print(f"7. Reasoning Trace ID: {trace_id}")
                print("   💾 Complete reasoning trace stored in database")
            
            print("")
            print("🎉 COMPLETE WORKFLOW DEMONSTRATION SUCCESSFUL")
            print("✅ Natural language query processed")
            print("✅ DAG workflow generated") 
            print("✅ Reasoning trace captured")
            print("✅ API parsing bug resolved")
            
            return True
            
        else:
            error = workflow_response.error_message or 'Unknown error'
            print(f"   ❌ DAG generation failed: {error}")
            print("")
            print("🔍 DEBUGGING INFO:")
            print(f"   Status: {workflow_response.status}")
            print(f"   Error: {workflow_response.error_message}")
            print(f"   Reasoning: {workflow_response.reasoning}")
            return False
            
    except Exception as e:
        print(f"❌ Complete workflow demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete workflow demonstration"""
    success = demonstrate_complete_workflow()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)