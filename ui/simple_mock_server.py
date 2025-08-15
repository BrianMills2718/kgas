#!/usr/bin/env python3
"""
Simple Mock KGAS Server for Testing File Upload and Export Generation
"""

import os
import uuid
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Pydantic models
class AnalysisRequest(BaseModel):
    files: List[str]
    parameters: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    query: str
    parameters: Dict[str, Any] = {}

class ExportRequest(BaseModel):
    format: str
    citation_style: str = "apa"
    data: Dict[str, Any] = {}

# FastAPI app
app = FastAPI(title="KGAS Research UI Backend - Mock Mode", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
uploads_dir = Path("uploads")
exports_dir = Path("exports") 
uploads_dir.mkdir(exist_ok=True)
exports_dir.mkdir(exist_ok=True)

# Global state
analysis_sessions = {}

@app.get("/")
async def serve_ui():
    """Serve the main UI"""
    return FileResponse("functional_ui_backend.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "mock", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload"""
    # Save the file
    file_id = str(uuid.uuid4())
    file_path = uploads_dir / f"{file_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    print(f"✅ File uploaded: {file.filename} -> {file_path}")
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "size": len(content),
        "status": "uploaded"
    }

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest):
    """Start analysis pipeline"""
    session_id = str(uuid.uuid4())
    
    # Initialize session
    analysis_sessions[session_id] = {
        "status": "running",
        "progress": 0,
        "current_tool": "PDF Loading",
        "files": request.files,
        "start_time": time.time(),
        "results": {}
    }
    
    # Start background analysis simulation
    asyncio.create_task(simulate_analysis(session_id))
    
    print(f"✅ Analysis started: session {session_id}")
    
    return {
        "session_id": session_id,
        "status": "started",
        "files": request.files
    }

async def simulate_analysis(session_id: str):
    """Simulate analysis pipeline execution"""
    session = analysis_sessions[session_id]
    
    steps = [
        ("PDF Loading", 16),
        ("Text Chunking", 32), 
        ("Entity Extraction", 48),
        ("Relationship Extraction", 64),
        ("Graph Building", 80),
        ("PageRank Calculation", 100)
    ]
    
    try:
        for step_name, progress in steps:
            await asyncio.sleep(2)  # Simulate processing time
            session.update({
                "current_tool": step_name,
                "progress": progress
            })
            print(f"📊 Analysis progress: {step_name} - {progress}%")
        
        # Complete analysis
        session.update({
            "status": "completed",
            "progress": 100,
            "current_tool": "Complete",
            "results": {
                "entities": [
                    {"name": "John Smith", "type": "PERSON", "confidence": 0.95},
                    {"name": "Stanford University", "type": "ORG", "confidence": 0.92},
                    {"name": "Artificial Intelligence", "type": "CONCEPT", "confidence": 0.88}
                ],
                "relationships": [
                    {"source": "John Smith", "target": "Stanford University", "type": "AFFILIATED_WITH"},
                    {"source": "John Smith", "target": "Artificial Intelligence", "type": "RESEARCHES"}
                ],
                "graph": {
                    "node_count": 15,
                    "edge_count": 23
                }
            }
        })
        
        print(f"✅ Analysis completed: session {session_id}")
        
    except Exception as e:
        session.update({
            "status": "error",
            "errors": [str(e)]
        })
        print(f"❌ Analysis failed: {e}")

@app.get("/api/analysis/status/{session_id}")
async def get_analysis_status(session_id: str):
    """Get analysis progress status"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return analysis_sessions[session_id]

@app.post("/api/query")
async def execute_query(request: QueryRequest):
    """Execute natural language query"""
    # Simulate query processing
    await asyncio.sleep(1)
    
    results = [
        {
            "answer": f"Based on the analysis, here are the key findings for: {request.query}",
            "confidence": 0.87,
            "path": ["Document", "Entity", "Relationship", "Answer"],
            "evidence": "This information was extracted from the uploaded documents using NLP analysis."
        }
    ]
    
    print(f"🔍 Query executed: {request.query}")
    
    return {
        "query": request.query,
        "results": results,
        "path_count": len(results),
        "execution_time": 1.2
    }

def generate_latex_export(data: Dict[str, Any]) -> str:
    """Generate LaTeX export"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    files_list = '\n'.join(f"\\item {f.get('name', 'Unknown')}" for f in data.get('uploadedFiles', []))
    
    latex_content = """\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{geometry}
\\geometry{margin=1in}

\\title{KGAS Analysis Report}
\\author{Generated by KGAS Research UI}
\\date{\\today}

\\begin{document}
\\maketitle

\\section{Analysis Summary}
This report was generated from the KGAS (Knowledge Graph Analysis System) processing of uploaded documents.

\\section{Files Analyzed}
\\begin{itemize}
""" + files_list + """
\\end{itemize}

\\section{Key Findings}
\\subsection{Entities Discovered}
The analysis identified several key entities in the documents:
\\begin{itemize}
\\item John Smith (Person, 95\\% confidence)
\\item Stanford University (Organization, 92\\% confidence) 
\\item Artificial Intelligence (Concept, 88\\% confidence)
\\end{itemize}

\\subsection{Relationships}
Key relationships discovered:
\\begin{itemize}
\\item John Smith is affiliated with Stanford University
\\item John Smith researches Artificial Intelligence
\\end{itemize}

\\section{Graph Statistics}
\\begin{itemize}
\\item Total nodes: 15
\\item Total edges: 23
\\item Analysis completed: """ + timestamp + """
\\end{itemize}

\\section{Methodology}
This analysis was performed using the KGAS pipeline, which includes:
\\begin{enumerate}
\\item PDF text extraction
\\item Text chunking and preprocessing
\\item Named Entity Recognition (NER)
\\item Relationship extraction
\\item Knowledge graph construction
\\item PageRank importance scoring
\\end{enumerate}

\\end{document}"""
    
    return latex_content

def generate_markdown_export(data: Dict[str, Any]) -> str:
    """Generate Markdown export"""
    return f"""# KGAS Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Files Analyzed
{chr(10).join(f"- {f['name']}" for f in data.get('uploadedFiles', []))}

## Key Findings

### Entities Discovered
- **John Smith** (Person, 95% confidence)
- **Stanford University** (Organization, 92% confidence)
- **Artificial Intelligence** (Concept, 88% confidence)

### Relationships
- John Smith → affiliated with → Stanford University
- John Smith → researches → Artificial Intelligence

## Graph Statistics
- **Total nodes:** 15
- **Total edges:** 23
- **Analysis completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Methodology
This analysis used the KGAS pipeline:
1. PDF text extraction
2. Text chunking and preprocessing  
3. Named Entity Recognition (NER)
4. Relationship extraction
5. Knowledge graph construction
6. PageRank importance scoring
"""

@app.post("/api/export")
async def generate_export(request: ExportRequest):
    """Generate export file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if request.format == "latex":
        content = generate_latex_export(request.data)
        filename = f"kgas_report_{timestamp}.tex"
    elif request.format == "markdown":
        content = generate_markdown_export(request.data)
        filename = f"kgas_report_{timestamp}.md"
    elif request.format == "html":
        md_content = generate_markdown_export(request.data)
        content = f"<html><body><pre>{md_content}</pre></body></html>"
        filename = f"kgas_report_{timestamp}.html"
    elif request.format == "json":
        content = json.dumps(request.data, indent=2)
        filename = f"kgas_data_{timestamp}.json"
    else:
        content = generate_markdown_export(request.data)
        filename = f"kgas_report_{timestamp}.txt"
    
    # Save export file
    export_path = exports_dir / filename
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"📄 Export generated: {filename} ({len(content)} characters)")
    
    return {
        "filename": filename,
        "format": request.format,
        "size": len(content),
        "download_url": f"/api/download/{filename}",
        "timestamp": timestamp
    }

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated export file"""
    file_path = exports_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    print(f"📥 File downloaded: {filename}")
    return FileResponse(file_path, filename=filename)

# Mount static files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    print("🚀 Starting KGAS Mock Server...")
    print("📡 Server will be available at: http://localhost:8899")
    print("🎯 Features: File upload, analysis, query, export - all working with mock data")
    uvicorn.run(app, host="0.0.0.0", port=8899)