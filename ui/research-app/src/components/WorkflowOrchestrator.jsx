import React, { useState, useEffect } from 'react';
import { PlayIcon, StopIcon, RefreshIcon, DocumentTextIcon, BeakerIcon } from '@heroicons/react/outline';
import mcpClient from '../services/mcpClient';

const WorkflowOrchestrator = () => {
  const [query, setQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState('claude-3-5-sonnet');
  const [isExecuting, setIsExecuting] = useState(false);
  const [workflowPlan, setWorkflowPlan] = useState(null);
  const [executionResults, setExecutionResults] = useState(null);
  const [progress, setProgress] = useState({ step: 0, total: 0, message: '' });
  const [availableTools, setAvailableTools] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);

  // Model configuration options
  const availableModels = [
    {
      id: 'claude-3-5-sonnet',
      name: 'Claude 3.5 Sonnet',
      description: 'Best for complex reasoning and research analysis',
      capabilities: ['reasoning', 'analysis', 'writing'],
      cost: 'High'
    },
    {
      id: 'gpt-4',
      name: 'GPT-4',
      description: 'Strong general capabilities with broad knowledge',
      capabilities: ['reasoning', 'coding', 'analysis'],
      cost: 'High'
    },
    {
      id: 'gemini-pro',
      name: 'Gemini Pro',
      description: 'Fast and efficient for structured tasks',
      capabilities: ['analysis', 'structured_output', 'multimodal'],
      cost: 'Medium'
    }
  ];

  // Example workflow templates
  const workflowTemplates = [
    {
      name: 'Document Analysis',
      query: 'Analyze the uploaded document for key themes, extract entities, and identify relationships',
      tools: ['load_pdf_document', 'extract_entities_from_text', 'extract_relationships', 'build_graph_entities']
    },
    {
      name: 'Entity Extraction',
      query: 'Extract all named entities from the text and classify them by type',
      tools: ['extract_entities_from_text', 'assess_confidence']
    },
    {
      name: 'Graph Construction',
      query: 'Build a knowledge graph from the document with PageRank analysis',
      tools: ['process_document_complete_pipeline', 'calculate_pagerank']
    },
    {
      name: 'Multi-hop Query',
      query: 'Find connections between entities in the knowledge graph',
      tools: ['query_graph', 'get_lineage']
    }
  ];

  useEffect(() => {
    initializeOrchestrator();
  }, []);

  const initializeOrchestrator = async () => {
    try {
      // Load available tools from MCP server
      const tools = await mcpClient.listTools();
      setAvailableTools(tools);

      // Get system status
      const status = await mcpClient.getSystemStatus();
      setSystemStatus(status);

      // Set up event listeners for real-time updates
      mcpClient.on('toolComplete', handleToolComplete);
      mcpClient.on('workflowProgress', handleWorkflowProgress);
      mcpClient.on('workflowComplete', handleWorkflowComplete);
    } catch (error) {
      console.error('Failed to initialize workflow orchestrator:', error);
    }
  };

  const handleToolComplete = (event) => {
    const { toolName, result } = event;
    setProgress(prev => ({
      ...prev,
      step: prev.step + 1,
      message: `Completed: ${toolName}`
    }));
  };

  const handleWorkflowProgress = (event) => {
    setProgress(event);
  };

  const handleWorkflowComplete = (result) => {
    setExecutionResults(result);
    setIsExecuting(false);
    setProgress({ step: 0, total: 0, message: 'Workflow completed' });
  };

  const generateWorkflowPlan = async () => {
    if (!query.trim()) return;

    try {
      setIsExecuting(true);
      setWorkflowPlan(null);

      // Simulate LLM-driven workflow planning
      // In production, this would call the backend orchestration service
      const planningResult = await planWorkflow(query, selectedModel);
      setWorkflowPlan(planningResult);
    } catch (error) {
      console.error('Failed to generate workflow plan:', error);
    } finally {
      setIsExecuting(false);
    }
  };

  const planWorkflow = async (userQuery, model) => {
    // Simulate workflow planning based on natural language input
    // In production, this would use the selected LLM to generate a tool sequence
    
    const toolsByCategory = mcpClient.getToolsByCategory();
    
    // Simple heuristic-based planning (would be replaced by LLM)
    let selectedTools = [];
    
    if (userQuery.toLowerCase().includes('document') || userQuery.toLowerCase().includes('pdf')) {
      selectedTools.push('load_pdf_document');
    }
    
    if (userQuery.toLowerCase().includes('entities') || userQuery.toLowerCase().includes('extract')) {
      selectedTools.push('extract_entities_from_text');
    }
    
    if (userQuery.toLowerCase().includes('relationships') || userQuery.toLowerCase().includes('connections')) {
      selectedTools.push('extract_relationships');
    }
    
    if (userQuery.toLowerCase().includes('graph') || userQuery.toLowerCase().includes('knowledge')) {
      selectedTools.push('build_graph_entities', 'build_graph_edges');
    }
    
    if (userQuery.toLowerCase().includes('pagerank') || userQuery.toLowerCase().includes('importance')) {
      selectedTools.push('calculate_pagerank');
    }
    
    if (userQuery.toLowerCase().includes('query') || userQuery.toLowerCase().includes('search')) {
      selectedTools.push('query_graph');
    }

    // If no specific tools identified, use complete pipeline
    if (selectedTools.length === 0) {
      selectedTools = ['process_document_complete_pipeline'];
    }

    return {
      query: userQuery,
      model: model,
      tools: selectedTools,
      estimated_duration: selectedTools.length * 30, // 30 seconds per tool estimate
      confidence: 0.85,
      generated_at: new Date().toISOString()
    };
  };

  const executeWorkflow = async () => {
    if (!workflowPlan) return;

    try {
      setIsExecuting(true);
      setExecutionResults(null);
      setProgress({ step: 0, total: workflowPlan.tools.length, message: 'Starting workflow...' });

      // Execute workflow using MCP client
      if (workflowPlan.tools.includes('process_document_complete_pipeline')) {
        // Use complete pipeline if available
        const result = await mcpClient.callTool('process_document_complete_pipeline', {
          file_path: '/path/to/document.pdf', // Would come from file upload
          include_pagerank: workflowPlan.tools.includes('calculate_pagerank'),
          include_query: workflowPlan.tools.includes('query_graph'),
          query_text: workflowPlan.query
        });
        setExecutionResults(result);
      } else {
        // Execute tools sequentially
        const results = [];
        for (let i = 0; i < workflowPlan.tools.length; i++) {
          const toolName = workflowPlan.tools[i];
          setProgress({ 
            step: i, 
            total: workflowPlan.tools.length, 
            message: `Executing: ${toolName}` 
          });

          const result = await mcpClient.callTool(toolName, {
            // Tool-specific parameters would be determined by the workflow planner
          });
          results.push({ tool: toolName, result });
        }
        setExecutionResults({ tools_executed: results });
      }
    } catch (error) {
      console.error('Workflow execution failed:', error);
      setExecutionResults({ error: error.message });
    } finally {
      setIsExecuting(false);
    }
  };

  const stopWorkflow = () => {
    setIsExecuting(false);
    setProgress({ step: 0, total: 0, message: 'Workflow stopped' });
  };

  const loadTemplate = (template) => {
    setQuery(template.query);
    setWorkflowPlan(null);
    setExecutionResults(null);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Natural Language Workflow Orchestrator
        </h1>
        <p className="text-gray-600">
          Describe your analysis goals in plain English and let AI orchestrate the appropriate KGAS tools
        </p>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">System Status</h3>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {systemStatus.tools_available?.total_mcp_tools || 0} tools available
              </span>
              <div className={`w-3 h-3 rounded-full ${
                systemStatus.status === 'success' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Templates */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Quick Start Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {workflowTemplates.map((template, index) => (
            <button
              key={index}
              onClick={() => loadTemplate(template)}
              className="p-3 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="font-medium text-gray-900">{template.name}</div>
              <div className="text-sm text-gray-600 mt-1">{template.query}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Natural Language Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Describe your analysis goal:
        </label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Example: Analyze the uploaded document for key themes, extract entities, and identify relationships between them"
          className="w-full h-24 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Model Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Choose your AI model:
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {availableModels.map((model) => (
            <div
              key={model.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedModel === model.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedModel(model.id)}
            >
              <div className="font-medium text-gray-900">{model.name}</div>
              <div className="text-sm text-gray-600 mt-1">{model.description}</div>
              <div className="flex items-center justify-between mt-2">
                <div className="flex space-x-1">
                  {model.capabilities.map((cap, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
                <span className="text-xs text-gray-500">Cost: {model.cost}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="mb-6 flex space-x-3">
        <button
          onClick={generateWorkflowPlan}
          disabled={!query.trim() || isExecuting}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <BeakerIcon className="w-4 h-4 mr-2" />
          Plan Workflow
        </button>

        {workflowPlan && (
          <button
            onClick={executeWorkflow}
            disabled={isExecuting}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlayIcon className="w-4 h-4 mr-2" />
            Execute
          </button>
        )}

        {isExecuting && (
          <button
            onClick={stopWorkflow}
            className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            <StopIcon className="w-4 h-4 mr-2" />
            Stop
          </button>
        )}
      </div>

      {/* Progress Indicator */}
      {isExecuting && progress.total > 0 && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Step {progress.step + 1} of {progress.total}
            </span>
            <span className="text-sm text-blue-700">
              {Math.round(((progress.step) / progress.total) * 100)}%
            </span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2 mb-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((progress.step) / progress.total) * 100}%` }}
            ></div>
          </div>
          <div className="text-sm text-blue-800">{progress.message}</div>
        </div>
      )}

      {/* Workflow Plan Display */}
      {workflowPlan && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Generated Workflow Plan</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Query Analysis</h4>
              <p className="text-sm text-gray-600 mb-3">{workflowPlan.query}</p>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <span>Model: {workflowPlan.model}</span>
                <span>Est. Duration: {Math.floor(workflowPlan.estimated_duration / 60)}m {workflowPlan.estimated_duration % 60}s</span>
                <span>Confidence: {Math.round(workflowPlan.confidence * 100)}%</span>
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Tool Sequence</h4>
              <div className="space-y-2">
                {workflowPlan.tools.map((tool, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                      {index + 1}
                    </span>
                    <span className="text-sm text-gray-700">{tool}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Execution Results */}
      {executionResults && (
        <div className="p-4 bg-white border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Execution Results</h3>
          {executionResults.error ? (
            <div className="p-3 bg-red-50 border border-red-200 rounded text-red-800">
              Error: {executionResults.error}
            </div>
          ) : (
            <div className="space-y-4">
              {executionResults.tools_executed && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Tools Executed</h4>
                  <div className="space-y-2">
                    {executionResults.tools_executed.map((item, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded">
                        <div className="font-medium text-gray-900">{item.tool || item}</div>
                        {item.result && (
                          <div className="text-sm text-gray-600 mt-1">
                            Status: {item.result.status || 'Completed'}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {executionResults.pipeline_result && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Pipeline Results</h4>
                  <pre className="text-sm text-gray-600 bg-gray-50 p-3 rounded overflow-x-auto">
                    {JSON.stringify(executionResults.pipeline_result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowOrchestrator;