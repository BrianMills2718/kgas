#!/usr/bin/env python3
"""
KGAS UI Integration: Frontend-Driven Exploration-to-Strict Workflows

This shows how the exploration-to-strict system integrates perfectly with a web UI.
The UI becomes the interface for:
1. Starting explorations with natural language
2. Monitoring real-time execution
3. Managing workflow library
4. Running strict reproductions
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Web framework imports
from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ExecutionStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UIExecutionState:
    """Real-time execution state for the UI"""
    execution_id: str
    status: ExecutionStatus
    progress: float  # 0.0 to 1.0
    current_phase: str
    current_tool: str
    start_time: str
    estimated_remaining: Optional[int]  # seconds
    tool_calls_completed: int
    total_estimated_tools: int
    live_outputs: Dict[str, Any]
    errors: List[str]
    

class KGASUIBackend:
    """Backend API for KGAS UI integration"""
    
    def __init__(self):
        self.app = FastAPI(title="KGAS Research Assistant")
        self.active_executions = {}  # execution_id -> UIExecutionState
        self.websocket_connections = {}  # execution_id -> [websockets]
        self.workflow_library = self._load_workflow_library()
        self.execution_history = self._load_execution_history()
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/")
        async def dashboard():
            """Main dashboard"""
            return HTMLResponse(self._generate_dashboard_html())
        
        @self.app.post("/api/explore")
        async def start_exploration(request: Dict[str, Any], background_tasks: BackgroundTasks):
            """Start a new exploration"""
            
            execution_id = f"explore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize execution state
            state = UIExecutionState(
                execution_id=execution_id,
                status=ExecutionStatus.QUEUED,
                progress=0.0,
                current_phase="initializing",
                current_tool="",
                start_time=datetime.now().isoformat(),
                estimated_remaining=None,
                tool_calls_completed=0,
                total_estimated_tools=0,
                live_outputs={},
                errors=[]
            )
            
            self.active_executions[execution_id] = state
            
            # Start execution in background
            background_tasks.add_task(self._run_exploration, execution_id, request)
            
            return {
                "execution_id": execution_id,
                "status": "queued",
                "message": "Exploration queued for execution"
            }
        
        @self.app.post("/api/execute-strict")
        async def execute_strict_workflow(request: Dict[str, Any], background_tasks: BackgroundTasks):
            """Execute a workflow in strict mode"""
            
            workflow_id = request["workflow_id"]
            execution_id = f"strict_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize execution state
            state = UIExecutionState(
                execution_id=execution_id,
                status=ExecutionStatus.QUEUED,
                progress=0.0,
                current_phase="loading_workflow",
                current_tool="",
                start_time=datetime.now().isoformat(),
                estimated_remaining=None,
                tool_calls_completed=0,
                total_estimated_tools=0,
                live_outputs={},
                errors=[]
            )
            
            self.active_executions[execution_id] = state
            
            # Start execution in background
            background_tasks.add_task(self._run_strict_workflow, execution_id, workflow_id, request.get("inputs", {}))
            
            return {
                "execution_id": execution_id,
                "status": "queued",
                "workflow_id": workflow_id
            }
        
        @self.app.get("/api/executions/{execution_id}")
        async def get_execution_status(execution_id: str):
            """Get current execution status"""
            
            if execution_id in self.active_executions:
                return asdict(self.active_executions[execution_id])
            else:
                # Check history
                return {"error": "Execution not found"}
        
        @self.app.get("/api/workflows")
        async def list_workflows():
            """List available workflows"""
            return {
                "workflows": [
                    {
                        "id": wf["id"],
                        "name": wf["name"],
                        "description": wf["description"],
                        "version": wf["version"],
                        "created": wf.get("created", "unknown"),
                        "source": wf.get("source", {}).get("type", "manual"),
                        "executions": len([h for h in self.execution_history if h.get("workflow_id") == wf["id"]])
                    }
                    for wf in self.workflow_library
                ]
            }
        
        @self.app.post("/api/workflows/{workflow_id}/crystallize")
        async def crystallize_execution(workflow_id: str, request: Dict[str, Any]):
            """Crystallize an exploration into a reusable workflow"""
            
            execution_id = request["execution_id"]
            workflow_name = request["name"]
            description = request.get("description", "")
            
            # Load execution data
            execution_path = self._load_execution_path(execution_id)
            
            # Crystallize to workflow
            crystallized = execution_path.to_workflow_spec(workflow_name, description)
            
            # Add to library
            self.workflow_library.append(crystallized)
            self._save_workflow_library()
            
            return {
                "workflow_id": crystallized["id"],
                "message": "Workflow crystallized successfully"
            }
        
        @self.app.websocket("/ws/{execution_id}")
        async def websocket_endpoint(websocket: WebSocket, execution_id: str):
            """WebSocket for real-time execution updates"""
            
            await websocket.accept()
            
            # Add to connections
            if execution_id not in self.websocket_connections:
                self.websocket_connections[execution_id] = []
            self.websocket_connections[execution_id].append(websocket)
            
            try:
                # Send current state if execution exists
                if execution_id in self.active_executions:
                    await websocket.send_json(asdict(self.active_executions[execution_id]))
                
                # Keep connection alive
                while True:
                    await websocket.receive_text()
                    
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                # Remove from connections
                if execution_id in self.websocket_connections:
                    self.websocket_connections[execution_id].remove(websocket)
    
    async def _run_exploration(self, execution_id: str, request: Dict[str, Any]):
        """Run exploration in background with real-time updates"""
        
        state = self.active_executions[execution_id]
        
        try:
            # Update status
            state.status = ExecutionStatus.RUNNING
            state.current_phase = "analysis"
            await self._broadcast_update(execution_id)
            
            # Simulate Claude Code exploration with captured path
            # In real implementation, this would use ClaudeCodeWithCapture
            
            tools_to_execute = [
                ("mcp__kgas__load_pdf_document", {"file": request.get("documents", [""])[0]}),
                ("mcp__kgas__chunk_text", {"size": 1000}),
                ("mcp__kgas__extract_entities_from_text", {}),
                ("mcp__kgas__build_knowledge_graph", {}),
                ("mcp__kgas__calculate_pagerank", {}),
                ("mcp__kgas__query_graph", {"query": "main themes"})
            ]
            
            state.total_estimated_tools = len(tools_to_execute)
            
            # Execute tools with updates
            for i, (tool_name, inputs) in enumerate(tools_to_execute):
                state.current_tool = tool_name
                state.progress = i / len(tools_to_execute)
                state.estimated_remaining = (len(tools_to_execute) - i) * 2  # 2 seconds per tool
                
                await self._broadcast_update(execution_id)
                
                # Simulate tool execution
                await asyncio.sleep(2)  # Simulate processing time
                
                # Update outputs
                state.live_outputs[tool_name] = {
                    "status": "completed",
                    "timestamp": datetime.now().isoformat(),
                    "sample_output": f"Result from {tool_name}"
                }
                
                state.tool_calls_completed += 1
            
            # Complete execution
            state.status = ExecutionStatus.COMPLETED
            state.progress = 1.0
            state.current_phase = "completed"
            state.current_tool = ""
            state.estimated_remaining = 0
            
            # Save execution path (in real implementation)
            execution_result = {
                "execution_id": execution_id,
                "prompt": request.get("prompt", ""),
                "results": state.live_outputs,
                "can_crystallize": True,  # This exploration can become a workflow
                "completed_at": datetime.now().isoformat()
            }
            
            self.execution_history.append(execution_result)
            
            await self._broadcast_update(execution_id)
            
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            state.errors.append(str(e))
            await self._broadcast_update(execution_id)
    
    async def _run_strict_workflow(self, execution_id: str, workflow_id: str, inputs: Dict[str, Any]):
        """Run strict workflow execution"""
        
        state = self.active_executions[execution_id]
        
        try:
            # Load workflow
            workflow = next((wf for wf in self.workflow_library if wf["id"] == workflow_id), None)
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            state.status = ExecutionStatus.RUNNING
            state.current_phase = "strict_execution"
            
            # Count total tools
            total_tools = sum(len(phase.get("tools", [])) for phase in workflow.get("phases", []))
            state.total_estimated_tools = total_tools
            
            completed_tools = 0
            
            # Execute phases
            for phase in workflow.get("phases", []):
                state.current_phase = phase["name"]
                await self._broadcast_update(execution_id)
                
                for tool_spec in phase.get("tools", []):
                    state.current_tool = tool_spec["tool"]
                    state.progress = completed_tools / total_tools
                    
                    await self._broadcast_update(execution_id)
                    
                    # Execute tool (simulated)
                    await asyncio.sleep(1)
                    
                    state.live_outputs[tool_spec["tool"]] = {
                        "status": "completed",
                        "timestamp": datetime.now().isoformat(),
                        "reproducible": True  # This was run in strict mode
                    }
                    
                    completed_tools += 1
                    state.tool_calls_completed = completed_tools
            
            # Complete
            state.status = ExecutionStatus.COMPLETED
            state.progress = 1.0
            state.current_phase = "completed"
            
            await self._broadcast_update(execution_id)
            
        except Exception as e:
            state.status = ExecutionStatus.FAILED
            state.errors.append(str(e))
            await self._broadcast_update(execution_id)
    
    async def _broadcast_update(self, execution_id: str):
        """Broadcast execution update to all connected WebSockets"""
        
        if execution_id not in self.websocket_connections:
            return
            
        state = self.active_executions[execution_id]
        message = asdict(state)
        
        # Send to all connected clients
        disconnected = []
        for websocket in self.websocket_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for ws in disconnected:
            self.websocket_connections[execution_id].remove(ws)
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>KGAS Research Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
        .execution { padding: 10px; margin: 10px 0; background: #f5f5f5; }
        .progress { width: 100%; height: 20px; background: #ddd; }
        .progress-bar { height: 100%; background: #4CAF50; transition: width 0.3s; }
        .status-running { border-left: 4px solid #2196F3; }
        .status-completed { border-left: 4px solid #4CAF50; }
        .status-failed { border-left: 4px solid #f44336; }
        button { padding: 10px 20px; margin: 5px; background: #2196F3; color: white; border: none; cursor: pointer; }
        input, textarea { width: 300px; padding: 5px; margin: 5px; }
    </style>
</head>
<body>
    <h1>🔬 KGAS Research Assistant</h1>
    
    <div class="section">
        <h2>Start New Analysis</h2>
        <form id="explorationForm">
            <div>
                <label>Research Question:</label><br>
                <textarea id="prompt" placeholder="Analyze the psychological factors in political rhetoric..."></textarea>
            </div>
            <div>
                <label>Documents:</label><br>
                <input type="text" id="documents" placeholder="path/to/document1.pdf,path/to/document2.pdf">
            </div>
            <div>
                <button type="submit">🚀 Start Exploration</button>
                <button type="button" onclick="showStrictMode()">🔒 Run Strict Workflow</button>
            </div>
        </form>
    </div>
    
    <div class="section">
        <h2>Active Executions</h2>
        <div id="activeExecutions">No active executions</div>
    </div>
    
    <div class="section">
        <h2>Workflow Library</h2>
        <div id="workflowLibrary">Loading...</div>
    </div>
    
    <div class="section">
        <h2>Execution History</h2>
        <div id="executionHistory">Loading...</div>
    </div>

    <script>
        // WebSocket connections for real-time updates
        const activeConnections = new Map();
        
        // Start exploration
        document.getElementById('explorationForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value;
            const documents = document.getElementById('documents').value.split(',').map(d => d.trim());
            
            const response = await fetch('/api/explore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt, documents })
            });
            
            const result = await response.json();
            
            if (result.execution_id) {
                // Connect WebSocket for real-time updates
                connectWebSocket(result.execution_id);
                updateActiveExecutions();
            }
        });
        
        // Connect WebSocket for execution updates
        function connectWebSocket(executionId) {
            const ws = new WebSocket(`ws://localhost:8000/ws/${executionId}`);
            
            ws.onmessage = (event) => {
                const state = JSON.parse(event.data);
                updateExecutionDisplay(executionId, state);
            };
            
            ws.onclose = () => {
                activeConnections.delete(executionId);
            };
            
            activeConnections.set(executionId, ws);
        }
        
        // Update execution display
        function updateExecutionDisplay(executionId, state) {
            const container = document.getElementById('activeExecutions');
            
            let execDiv = document.getElementById(`exec-${executionId}`);
            if (!execDiv) {
                execDiv = document.createElement('div');
                execDiv.id = `exec-${executionId}`;
                execDiv.className = `execution status-${state.status}`;
                container.appendChild(execDiv);
            }
            
            execDiv.innerHTML = `
                <h4>${executionId}</h4>
                <div><strong>Status:</strong> ${state.status}</div>
                <div><strong>Phase:</strong> ${state.current_phase}</div>
                <div><strong>Tool:</strong> ${state.current_tool}</div>
                <div><strong>Progress:</strong> ${state.tool_calls_completed}/${state.total_estimated_tools}</div>
                <div class="progress">
                    <div class="progress-bar" style="width: ${state.progress * 100}%"></div>
                </div>
                ${state.status === 'completed' ? `
                    <button onclick="crystallizeWorkflow('${executionId}')">💎 Crystallize to Workflow</button>
                ` : ''}
                ${state.errors.length > 0 ? `
                    <div style="color: red;"><strong>Errors:</strong> ${state.errors.join(', ')}</div>
                ` : ''}
            `;
        }
        
        // Crystallize exploration to workflow
        async function crystallizeWorkflow(executionId) {
            const name = prompt('Workflow name:');
            if (!name) return;
            
            const description = prompt('Description (optional):') || '';
            
            const response = await fetch(`/api/workflows/${executionId}/crystallize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ execution_id: executionId, name, description })
            });
            
            const result = await response.json();
            alert(`Workflow crystallized: ${result.workflow_id}`);
            
            loadWorkflowLibrary();
        }
        
        // Load workflow library
        async function loadWorkflowLibrary() {
            const response = await fetch('/api/workflows');
            const data = await response.json();
            
            const container = document.getElementById('workflowLibrary');
            container.innerHTML = data.workflows.map(wf => `
                <div class="execution">
                    <h4>${wf.name} (${wf.version})</h4>
                    <div><strong>ID:</strong> ${wf.id}</div>
                    <div><strong>Description:</strong> ${wf.description}</div>
                    <div><strong>Source:</strong> ${wf.source}</div>
                    <div><strong>Executions:</strong> ${wf.executions}</div>
                    <button onclick="runStrictWorkflow('${wf.id}')">🔒 Run Strict</button>
                </div>
            `).join('');
        }
        
        // Run workflow in strict mode
        async function runStrictWorkflow(workflowId) {
            const response = await fetch('/api/execute-strict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workflow_id: workflowId, inputs: {} })
            });
            
            const result = await response.json();
            
            if (result.execution_id) {
                connectWebSocket(result.execution_id);
                updateActiveExecutions();
            }
        }
        
        // Initialize
        loadWorkflowLibrary();
        
        // Auto-refresh active executions
        setInterval(updateActiveExecutions, 5000);
        
        function updateActiveExecutions() {
            // This would fetch current active executions
        }
    </script>
</body>
</html>
        """
    
    def _load_workflow_library(self) -> List[Dict[str, Any]]:
        """Load workflow library"""
        # In real implementation, load from database/files
        return [
            {
                "id": "theory_application_v1",
                "name": "Theory Application Analysis",
                "description": "Apply theoretical framework to documents",
                "version": "1.0.0",
                "created": "2025-01-25T10:00:00Z",
                "source": {"type": "manual"}
            }
        ]
    
    def _load_execution_history(self) -> List[Dict[str, Any]]:
        """Load execution history"""
        return []
    
    def _load_execution_path(self, execution_id: str):
        """Load execution path for crystallization"""
        # In real implementation, load from storage
        pass
    
    def _save_workflow_library(self):
        """Save workflow library"""
        # In real implementation, persist to database/files
        pass


def run_ui_server():
    """Run the KGAS UI server"""
    
    print("🌐 Starting KGAS UI Server...")
    print("   Dashboard: http://localhost:8000/")
    print("   API Docs: http://localhost:8000/docs")
    
    backend = KGASUIBackend()
    
    uvicorn.run(
        backend.app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    run_ui_server()