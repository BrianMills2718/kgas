#!/usr/bin/env python3
"""Fixed CLI for natural language document analysis - creates simple, working workflows"""

import argparse
import sys
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.workflow_agent import WorkflowAgent
from src.core.enhanced_api_client import EnhancedAPIClient

def create_simple_dag_for_centrality(file_path: str) -> dict:
    """Create a simple DAG focused on finding central entities"""
    return {
        "metadata": {
            "name": "Entity Centrality Analysis",
            "description": "Find central entities and relations in documents",
            "version": "1.0.0"
        },
        "steps": [
            {
                "step_id": "load_document",
                "tool_id": "T01",
                "name": "Load Document", 
                "input_data": {"file_path": file_path},
                "parameters": {"file_path": file_path},
                "depends_on": []
            },
            {
                "step_id": "extract_entities",
                "tool_id": "T23C",
                "name": "Extract Entities",
                "input_data": {"text": "$load_document.content"},
                "parameters": {},
                "depends_on": ["load_document"]
            },
            {
                "step_id": "build_graph",
                "tool_id": "T31",
                "name": "Build Entity Graph",
                "input_data": {"entities": "$extract_entities.entities"},
                "parameters": {},
                "depends_on": ["extract_entities"]
            },
            {
                "step_id": "analyze_centrality",
                "tool_id": "T68",
                "name": "Calculate PageRank Centrality",
                "input_data": {"graph": "$build_graph.graph"},
                "parameters": {},
                "depends_on": ["build_graph"]
            }
        ],
        "entry_point": "load_document"
    }

def main():
    parser = argparse.ArgumentParser(description="Ask questions about documents using AI analysis")
    parser.add_argument("-q", "--question", required=True, 
                       help="Your question about the documents")
    parser.add_argument("-d", "--documents", required=True,
                       help="Path to document file or directory")
    
    args = parser.parse_args()
    
    # Find documents
    doc_path = Path(args.documents)
    if not doc_path.exists():
        print(f"❌ Path not found: {doc_path}")
        sys.exit(1)
    
    # Get first document file
    document_files = []
    if doc_path.is_file():
        document_files = [doc_path]
    elif doc_path.is_dir():
        # Find text files
        for ext in ['*.txt', '*.pdf']:
            document_files.extend(doc_path.glob(ext))
        
        if not document_files:
            # Look recursively
            for ext in ['*.txt', '*.pdf']:
                document_files.extend(doc_path.rglob(ext))
    
    if not document_files:
        print(f"❌ No .txt or .pdf files found in: {doc_path}")
        sys.exit(1)
    
    print(f"🔍 Found {len(document_files)} document(s)")
    
    # Use the first document for analysis
    target_file = document_files[0]
    print(f"📄 Analyzing: {target_file}")
    
    try:
        print("🤖 Initializing AI analysis system...")
        client = EnhancedAPIClient()
        agent = WorkflowAgent(api_client=client)
        
        print("🔧 Creating analysis workflow...")
        
        # For centrality questions, use our optimized DAG
        if any(word in args.question.lower() for word in ['central', 'important', 'key', 'main', 'primary']):
            dag = create_simple_dag_for_centrality(str(target_file))
            print("✅ Using centrality analysis workflow")
        else:
            # For other questions, generate a simple workflow
            dag_result = agent.generate_workflow_dag(args.question, [str(target_file)])
            
            if dag_result["status"] != "success":
                print(f"❌ Failed to create analysis plan: {dag_result.get('error', 'Unknown error')}")
                sys.exit(1)
                
            dag = dag_result["dag"]
            print("✅ Generated custom analysis workflow")
        
        print(f"📋 Workflow has {len(dag['steps'])} steps")
        
        print("🚀 Executing analysis...")
        result = agent.execute_workflow_from_dag(dag)
        
        if result["status"] == "success":
            print("✅ Analysis completed successfully!")
            print("\n📊 Results:")
            print("=" * 50)
            
            # Extract meaningful results
            data = result.get("data", {})
            
            # Show centrality results if available
            if "analyze_centrality" in data:
                centrality_data = data["analyze_centrality"]
                print("🎯 Most Central Entities:")
                if isinstance(centrality_data, dict):
                    # Sort by score if available
                    items = list(centrality_data.items())[:10]  # Top 10
                    for entity, score in items:
                        print(f"   • {entity}: {score}")
                else:
                    print(f"   {centrality_data}")
                    
            # Show extracted entities if available  
            elif "extract_entities" in data:
                entities_data = data["extract_entities"]
                print("🏷️  Extracted Entities:")
                if isinstance(entities_data, dict) and "entities" in entities_data:
                    entities = entities_data["entities"][:15]  # First 15
                    for entity in entities:
                        if isinstance(entity, dict):
                            name = entity.get('name', entity.get('text', str(entity)))
                            entity_type = entity.get('type', entity.get('label', 'Unknown'))
                            print(f"   • {name} ({entity_type})")
                        else:
                            print(f"   • {entity}")
                else:
                    print(f"   {entities_data}")
                    
            # Show document content summary if available
            elif "load_document" in data:
                doc_data = data["load_document"]  
                print("📄 Document Summary:")
                if isinstance(doc_data, dict):
                    content = doc_data.get("content", "")
                    if content:
                        # Show first 500 characters
                        print(f"   Content preview: {content[:500]}...")
                        if "statistics" in doc_data:
                            stats = doc_data["statistics"]
                            print(f"   📊 Stats: {stats.get('words', 0)} words, {stats.get('characters', 0)} characters")
                    
            print("=" * 50)
            
        else:
            error = result.get("error_message", result.get("error", "Unknown error"))
            print(f"❌ Analysis failed: {error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()