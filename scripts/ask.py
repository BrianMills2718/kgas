#!/usr/bin/env python3
"""Simple CLI for natural language document analysis"""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from src.agents.workflow_agent import WorkflowAgent
from src.core.enhanced_api_client import EnhancedAPIClient

def inject_document_paths(dag, document_files):
    """Inject actual document paths into the generated DAG"""
    if not document_files:
        return dag
    
    # Find the first step that loads documents (usually T01_PDF_LOADER)
    for step in dag.get("steps", []):
        tool_id = step.get("tool_id", "")
        
        # If this is a document loader, inject the file path
        if tool_id in ["T01_PDF_LOADER", "T01", "T02", "T03", "T04", "T05"]:
            # Use the first document for now (could be enhanced to handle multiple)
            document_path = str(document_files[0])
            
            # Add file_path to input_data
            if "input_data" not in step:
                step["input_data"] = {}
            step["input_data"]["file_path"] = document_path
            
            # Also add to parameters
            if "parameters" not in step:
                step["parameters"] = {}
            step["parameters"]["file_path"] = document_path
            
            print(f"   📄 Injected document path: {document_path}")
            break
    
    return dag

def main():
    parser = argparse.ArgumentParser(
        description="Ask questions about documents using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/ask.py --question "What are the main topics?" --docs ./data/
  python scripts/ask.py -q "Who are the key people mentioned?" -d document.pdf
  python scripts/ask.py -q "Extract relationships between organizations" -d ./research_papers/
        """
    )
    
    parser.add_argument(
        "-q", "--question", 
        required=True,
        help="Your question or analysis request in natural language"
    )
    
    parser.add_argument(
        "-d", "--docs", 
        required=True,
        help="Path to document(s) - can be a file or directory"
    )
    
    parser.add_argument(
        "--format", 
        choices=["json", "text", "table"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed workflow steps"
    )
    
    args = parser.parse_args()
    
    # Validate documents path
    docs_path = Path(args.docs)
    if not docs_path.exists():
        print(f"❌ Error: Path '{args.docs}' does not exist")
        return 1
    
    # Find documents
    if docs_path.is_file():
        document_files = [docs_path]
    else:
        # Find all text/PDF files in directory
        extensions = ['.txt', '.pdf', '.md', '.docx']
        document_files = []
        for ext in extensions:
            document_files.extend(docs_path.glob(f'*{ext}'))
            document_files.extend(docs_path.glob(f'**/*{ext}'))
    
    if not document_files:
        print(f"❌ Error: No supported documents found in '{args.docs}'")
        print("   Supported formats: .txt, .pdf, .md, .docx")
        return 1
    
    print(f"🔍 Found {len(document_files)} document(s)")
    if args.verbose:
        for doc in document_files[:5]:  # Show first 5
            print(f"   - {doc.name}")
        if len(document_files) > 5:
            print(f"   ... and {len(document_files)-5} more")
    
    # Initialize the workflow agent
    try:
        print("🤖 Initializing AI analysis system...")
        client = EnhancedAPIClient()
        agent = WorkflowAgent(api_client=client)
        
        # Enhance the question with document context
        enhanced_question = f"""
        {args.question}
        
        Process these specific documents: {[str(doc) for doc in document_files]}
        Start by loading the first document: {str(document_files[0])}
        """
        
        if args.verbose:
            print(f"📝 Question: {args.question}")
            print("🔄 Generating analysis workflow...")
        
        # Generate workflow DAG
        dag_result = agent.generate_workflow_dag(enhanced_question)
        
        if dag_result["status"] != "success":
            print(f"❌ Failed to generate analysis plan: {dag_result.get('error')}")
            return 1
        
        dag = dag_result["dag"]
        
        if args.verbose:
            print(f"✅ Generated workflow with {len(dag.get('steps', []))} steps:")
            for i, step in enumerate(dag.get('steps', []), 1):
                print(f"   {i}. {step.get('operation', step['step_id'])}")
        
        # Inject actual document paths into the DAG
        print("🔧 Configuring workflow with document paths...")
        dag = inject_document_paths(dag, document_files)
        
        # Execute the workflow
        print("⚡ Running analysis...")
        execution_result = agent.execute_workflow_from_dag(dag)
        
        if execution_result["status"] == "success":
            print("✅ Analysis completed!")
            
            # Format and display results
            if args.format == "json":
                print("\n📊 Results (JSON):")
                print(json.dumps(execution_result.get("data", {}), indent=2))
            
            elif args.format == "table":
                print("\n📊 Results (Table):")
                data = execution_result.get("data", {})
                # Simple table formatting
                for key, value in data.items():
                    print(f"{key:20} | {value}")
            
            else:  # text format
                print("\n📊 Results:")
                data = execution_result.get("data", {})
                if data:
                    for key, value in data.items():
                        print(f"\n{key.replace('_', ' ').title()}:")
                        if isinstance(value, dict):
                            for k, v in value.items():
                                print(f"  • {k}: {v}")
                        elif isinstance(value, list):
                            for item in value[:10]:  # Show first 10 items
                                print(f"  • {item}")
                            if len(value) > 10:
                                print(f"  ... and {len(value)-10} more")
                        else:
                            print(f"  {value}")
                else:
                    print("  No specific results returned - analysis may have completed successfully")
                    print("  but results need to be retrieved from the database or files.")
        
        else:
            print(f"⚠️ Analysis had issues: {execution_result.get('error_message')}")
            if args.verbose:
                print(f"   Details: {execution_result}")
            
            # Still might have partial results
            if execution_result.get("data"):
                print("\n📊 Partial Results:")
                print(json.dumps(execution_result["data"], indent=2))
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())