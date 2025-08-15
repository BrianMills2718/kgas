#!/usr/bin/env python3
"""
Example: Using the KGAS Cross-Modal REST API

This example demonstrates how to use the REST API for:
1. Analyzing documents
2. Converting between formats
3. Getting mode recommendations
4. Batch processing

Make sure the API server is running first:
    python run_api_server.py
"""

import requests
import json
from pathlib import Path
import time

# API base URL (local only)
API_BASE = "http://localhost:8000"


def check_health():
    """Check if the API is healthy"""
    print("🏥 Checking API health...")
    response = requests.get(f"{API_BASE}/api/health")
    
    if response.status_code == 200:
        health = response.json()
        print(f"✅ API Status: {health['status']}")
        print(f"   Services: {json.dumps(health['services'], indent=2)}")
        return True
    else:
        print(f"❌ API is not healthy: {response.status_code}")
        return False


def analyze_document(file_path: str, target_format: str = "graph"):
    """Analyze a document"""
    print(f"\n📄 Analyzing document: {file_path}")
    print(f"   Target format: {target_format}")
    
    with open(file_path, "rb") as f:
        files = {"file": (Path(file_path).name, f)}
        data = {
            "target_format": target_format,
            "task": "extract entities and relationships",
            "optimization_level": "balanced",
            "validation_level": "standard"
        }
        
        response = requests.post(
            f"{API_BASE}/api/analyze",
            files=files,
            params=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis complete!")
        print(f"   Workflow ID: {result['workflow_id']}")
        print(f"   Selected mode: {result['selected_mode']}")
        print(f"   Results: {json.dumps(result['results'], indent=2)[:200]}...")
        return result
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def convert_data(data, source_format: str, target_format: str):
    """Convert data between formats"""
    print(f"\n🔄 Converting data from {source_format} to {target_format}")
    
    request_data = {
        "data": data,
        "source_format": source_format,
        "target_format": target_format
    }
    
    response = requests.post(
        f"{API_BASE}/api/convert",
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Conversion complete!")
        print(f"   Conversion time: {result['performance']['conversion_time']:.3f}s")
        print(f"   Data preview: {json.dumps(result['data'], indent=2)[:200]}...")
        return result
    else:
        print(f"❌ Conversion failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def get_mode_recommendation(task: str, data_type: str, size: int):
    """Get AI recommendation for analysis mode"""
    print(f"\n🤖 Getting mode recommendation")
    print(f"   Task: {task}")
    print(f"   Data type: {data_type}")
    print(f"   Size: {size}")
    
    request_data = {
        "task": task,
        "data_type": data_type,
        "size": size,
        "performance_priority": "quality"
    }
    
    response = requests.post(
        f"{API_BASE}/api/recommend",
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Recommendation received!")
        print(f"   Primary mode: {result['primary_mode']}")
        print(f"   Confidence: {result['confidence']:.2f} ({result['confidence_level']})")
        print(f"   Reasoning: {result['reasoning'][:200]}...")
        return result
    else:
        print(f"❌ Recommendation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def batch_analyze(file_paths: list, target_format: str = "graph"):
    """Submit batch analysis job"""
    print(f"\n📦 Submitting batch analysis for {len(file_paths)} files")
    
    files = []
    for path in file_paths:
        with open(path, "rb") as f:
            files.append(("files", (Path(path).name, f.read())))
    
    response = requests.post(
        f"{API_BASE}/api/batch/analyze",
        files=files,
        params={
            "target_format": target_format,
            "task": "extract entities"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Batch job created!")
        print(f"   Job ID: {result['job_id']}")
        return result['job_id']
    else:
        print(f"❌ Batch submission failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None


def check_job_status(job_id: str):
    """Check status of batch job"""
    response = requests.get(f"{API_BASE}/api/jobs/{job_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Job Status: {result['status']}")
        print(f"   Progress: {result['progress']['processed']}/{result['progress']['total']} ({result['progress']['percentage']:.1f}%)")
        
        if result['status'] == 'completed':
            print(f"   Results available: {len(result['results'])} files processed")
        
        return result
    else:
        print(f"❌ Failed to get job status: {response.status_code}")
        return None


def main():
    """Run example API usage"""
    print("="*60)
    print("KGAS Cross-Modal REST API Example")
    print("="*60)
    
    # 1. Check health
    if not check_health():
        print("\n⚠️  API is not running. Start it with: python run_api_server.py")
        return
    
    # 2. Get mode recommendation
    recommendation = get_mode_recommendation(
        task="analyze social network relationships",
        data_type="entities_and_relationships",
        size=1000
    )
    
    # 3. Example graph data
    graph_data = {
        "nodes": [
            {"id": "1", "label": "Alice", "type": "PERSON"},
            {"id": "2", "label": "Bob", "type": "PERSON"},
            {"id": "3", "label": "TechCorp", "type": "ORGANIZATION"}
        ],
        "edges": [
            {"source": "1", "target": "3", "relationship": "WORKS_FOR"},
            {"source": "2", "target": "3", "relationship": "WORKS_FOR"},
            {"source": "1", "target": "2", "relationship": "KNOWS"}
        ]
    }
    
    # 4. Convert graph to table
    table_result = convert_data(
        data=graph_data,
        source_format="graph",
        target_format="table"
    )
    
    # 5. Convert graph to vector
    vector_result = convert_data(
        data=graph_data,
        source_format="graph",
        target_format="vector"
    )
    
    # 6. If you have a test file, analyze it
    test_file = Path("test_document.txt")
    if test_file.exists():
        analysis_result = analyze_document(
            str(test_file),
            target_format="graph"
        )
    else:
        print(f"\n📝 Create '{test_file}' to test document analysis")
    
    # 7. Example batch processing
    test_files = [f"test{i}.txt" for i in range(3)]
    existing_files = [f for f in test_files if Path(f).exists()]
    
    if existing_files:
        job_id = batch_analyze(existing_files)
        if job_id:
            # Wait and check status
            time.sleep(2)
            check_job_status(job_id)
    else:
        print(f"\n📝 Create test files ({', '.join(test_files)}) to test batch processing")
    
    # 8. Get statistics
    print("\n📈 API Statistics:")
    response = requests.get(f"{API_BASE}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"   {json.dumps(stats['api'], indent=2)}")
    
    print("\n✨ Example complete! The API is ready for your custom applications.")
    print("   - Build a web UI with React/Vue/Angular")
    print("   - Automate with Python/JavaScript/Shell scripts")
    print("   - Integrate with Jupyter notebooks")
    print("   - Create custom research tools")


if __name__ == "__main__":
    main()