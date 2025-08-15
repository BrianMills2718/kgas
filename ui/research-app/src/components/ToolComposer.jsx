import React, { useState, useEffect, useRef } from 'react';
import { 
  PlusIcon, 
  TrashIcon, 
  ArrowRightIcon, 
  CogIcon, 
  PlayIcon,
  DocumentIcon,
  ShareIcon,
  SaveIcon
} from '@heroicons/react/outline';
import mcpClient from '../services/mcpClient';

const ToolComposer = ({ onWorkflowChange, initialWorkflow = null }) => {
  const [availableTools, setAvailableTools] = useState([]);
  const [toolsByCategory, setToolsByCategory] = useState({});
  const [workflowSteps, setWorkflowSteps] = useState([]);
  const [selectedStep, setSelectedStep] = useState(null);
  const [draggedTool, setDraggedTool] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showParameters, setShowParameters] = useState(false);
  const dropZoneRef = useRef(null);

  useEffect(() => {
    loadAvailableTools();
    if (initialWorkflow) {
      setWorkflowSteps(initialWorkflow.steps || []);
    }
  }, [initialWorkflow]);

  useEffect(() => {
    // Notify parent of workflow changes
    if (onWorkflowChange) {
      onWorkflowChange({
        steps: workflowSteps,
        isValid: validateWorkflow(),
        estimatedDuration: calculateEstimatedDuration()
      });
    }
  }, [workflowSteps]);

  const loadAvailableTools = async () => {
    try {
      const tools = await mcpClient.listTools();
      setAvailableTools(tools);
      
      const categorized = mcpClient.getToolsByCategory();
      setToolsByCategory(categorized);
    } catch (error) {
      console.error('Failed to load tools:', error);
    }
  };

  const validateWorkflow = () => {
    if (workflowSteps.length === 0) return false;
    
    // Check if all steps have required parameters
    return workflowSteps.every(step => {
      const tool = availableTools.find(t => t.name === step.toolName);
      if (!tool) return false;
      
      // Basic validation - could be enhanced with actual parameter schemas
      return step.parameters && typeof step.parameters === 'object';
    });
  };

  const calculateEstimatedDuration = () => {
    // Estimate duration based on tool types
    const baseDurations = {
      'load_pdf_document': 30,
      'extract_entities_from_text': 45,
      'extract_relationships': 60,
      'build_graph_entities': 40,
      'build_graph_edges': 35,
      'calculate_pagerank': 120,
      'query_graph': 25,
      'process_document_complete_pipeline': 300
    };

    return workflowSteps.reduce((total, step) => {
      return total + (baseDurations[step.toolName] || 30);
    }, 0);
  };

  const handleDragStart = (e, tool) => {
    setDraggedTool(tool);
    e.dataTransfer.effectAllowed = 'copy';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (draggedTool) {
      addToolToWorkflow(draggedTool);
      setDraggedTool(null);
    }
  };

  const addToolToWorkflow = (tool, insertIndex = -1) => {
    const newStep = {
      id: `step_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      toolName: tool.name,
      displayName: tool.description || tool.name,
      parameters: getDefaultParameters(tool),
      outputMapping: {},
      conditions: [],
      enabled: true
    };

    if (insertIndex >= 0) {
      const newSteps = [...workflowSteps];
      newSteps.splice(insertIndex, 0, newStep);
      setWorkflowSteps(newSteps);
    } else {
      setWorkflowSteps([...workflowSteps, newStep]);
    }
  };

  const getDefaultParameters = (tool) => {
    // Return default parameters based on tool type
    const defaults = {
      'load_pdf_document': {
        file_path: '${uploaded_file_path}',
        workflow_id: '${workflow_id}',
        extract_metadata: true
      },
      'extract_entities_from_text': {
        chunk_ref: '${previous_output.chunk_ref}',
        text_content: '${previous_output.text_content}',
        base_confidence: 0.8
      },
      'extract_relationships': {
        chunk_ref: '${previous_output.chunk_ref}',
        text_content: '${previous_output.text_content}',
        entities: '${previous_output.entities}',
        base_confidence: 0.8
      },
      'query_graph': {
        query_text: '${user_query}',
        max_hops: 3,
        result_limit: 20
      }
    };

    return defaults[tool.name] || {};
  };

  const removeStep = (stepId) => {
    setWorkflowSteps(workflowSteps.filter(step => step.id !== stepId));
    if (selectedStep?.id === stepId) {
      setSelectedStep(null);
    }
  };

  const moveStep = (fromIndex, toIndex) => {
    const newSteps = [...workflowSteps];
    const [movedStep] = newSteps.splice(fromIndex, 1);
    newSteps.splice(toIndex, 0, movedStep);
    setWorkflowSteps(newSteps);
  };

  const updateStepParameters = (stepId, parameters) => {
    setWorkflowSteps(workflowSteps.map(step => 
      step.id === stepId ? { ...step, parameters } : step
    ));
  };

  const updateStepConditions = (stepId, conditions) => {
    setWorkflowSteps(workflowSteps.map(step => 
      step.id === stepId ? { ...step, conditions } : step
    ));
  };

  const filteredTools = availableTools.filter(tool =>
    tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (tool.description && tool.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const saveWorkflow = () => {
    const workflow = {
      name: prompt('Enter workflow name:') || 'Untitled Workflow',
      steps: workflowSteps,
      created_at: new Date().toISOString(),
      version: '1.0'
    };
    
    // In production, this would save to backend
    localStorage.setItem(`workflow_${workflow.name}`, JSON.stringify(workflow));
    alert('Workflow saved locally!');
  };

  const exportWorkflow = () => {
    const workflow = {
      name: 'Custom Workflow',
      steps: workflowSteps,
      metadata: {
        created_at: new Date().toISOString(),
        estimated_duration: calculateEstimatedDuration(),
        tool_count: workflowSteps.length
      }
    };

    const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'kgas_workflow.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex bg-gray-50">
      {/* Tool Library Panel */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Tool Library</h3>
          <input
            type="text"
            placeholder="Search tools..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {Object.entries(toolsByCategory).map(([category, tools]) => (
            <div key={category} className="mb-6">
              <h4 className="font-medium text-gray-700 mb-3">{category}</h4>
              <div className="space-y-2">
                {tools.filter(tool => 
                  !searchTerm || 
                  tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  (tool.description && tool.description.toLowerCase().includes(searchTerm.toLowerCase()))
                ).map((tool) => (
                  <div
                    key={tool.name}
                    draggable
                    onDragStart={(e) => handleDragStart(e, tool)}
                    className="p-3 bg-gray-50 border border-gray-200 rounded-lg cursor-grab hover:border-blue-300 hover:bg-blue-50 transition-colors"
                  >
                    <div className="font-medium text-gray-900 text-sm">{tool.name}</div>
                    <div className="text-xs text-gray-600 mt-1">
                      {tool.description || 'No description available'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workflow Canvas */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Workflow Designer</h3>
            <div className="flex space-x-2">
              <button
                onClick={saveWorkflow}
                className="flex items-center px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                <SaveIcon className="w-4 h-4 mr-1" />
                Save
              </button>
              <button
                onClick={exportWorkflow}
                className="flex items-center px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <ShareIcon className="w-4 h-4 mr-1" />
                Export
              </button>
              <button
                onClick={() => setShowParameters(!showParameters)}
                className="flex items-center px-3 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
              >
                <CogIcon className="w-4 h-4 mr-1" />
                Parameters
              </button>
            </div>
          </div>
          
          {workflowSteps.length > 0 && (
            <div className="mt-2 text-sm text-gray-600">
              {workflowSteps.length} steps • Est. duration: {Math.floor(calculateEstimatedDuration() / 60)}m {calculateEstimatedDuration() % 60}s
            </div>
          )}
        </div>

        {/* Canvas Area */}
        <div className="flex-1 p-6 overflow-auto">
          <div
            ref={dropZoneRef}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="min-h-full"
          >
            {workflowSteps.length === 0 ? (
              <div className="flex items-center justify-center h-64 border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-center">
                  <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No workflow steps</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Drag tools from the library to build your workflow
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {workflowSteps.map((step, index) => (
                  <div key={step.id} className="flex items-center space-x-4">
                    {/* Step Number */}
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>

                    {/* Step Card */}
                    <div
                      className={`flex-1 p-4 bg-white border-2 rounded-lg cursor-pointer transition-colors ${
                        selectedStep?.id === step.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedStep(step)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{step.toolName}</h4>
                          <p className="text-sm text-gray-600">{step.displayName}</p>
                          {Object.keys(step.parameters).length > 0 && (
                            <div className="mt-2 text-xs text-gray-500">
                              {Object.keys(step.parameters).length} parameters configured
                            </div>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              removeStep(step.id);
                            }}
                            className="p-1 text-gray-400 hover:text-red-600"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Arrow to next step */}
                    {index < workflowSteps.length - 1 && (
                      <ArrowRightIcon className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Parameter Panel */}
      {showParameters && selectedStep && (
        <div className="w-1/3 bg-white border-l border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Step Configuration</h3>
            <p className="text-sm text-gray-600">{selectedStep.toolName}</p>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {/* Basic Info */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Name
                </label>
                <input
                  type="text"
                  value={selectedStep.displayName}
                  onChange={(e) => {
                    const updatedSteps = workflowSteps.map(step =>
                      step.id === selectedStep.id
                        ? { ...step, displayName: e.target.value }
                        : step
                    );
                    setWorkflowSteps(updatedSteps);
                    setSelectedStep({ ...selectedStep, displayName: e.target.value });
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Parameters */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Parameters
                </label>
                <div className="space-y-3">
                  {Object.entries(selectedStep.parameters).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-xs font-medium text-gray-600 mb-1">
                        {key}
                      </label>
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => {
                          const newParameters = {
                            ...selectedStep.parameters,
                            [key]: e.target.value
                          };
                          updateStepParameters(selectedStep.id, newParameters);
                          setSelectedStep({
                            ...selectedStep,
                            parameters: newParameters
                          });
                        }}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                        placeholder={`Enter ${key}`}
                      />
                    </div>
                  ))}
                </div>

                {/* Add Parameter */}
                <button
                  onClick={() => {
                    const newKey = prompt('Parameter name:');
                    if (newKey) {
                      const newParameters = {
                        ...selectedStep.parameters,
                        [newKey]: ''
                      };
                      updateStepParameters(selectedStep.id, newParameters);
                      setSelectedStep({
                        ...selectedStep,
                        parameters: newParameters
                      });
                    }
                  }}
                  className="mt-2 flex items-center text-sm text-blue-600 hover:text-blue-800"
                >
                  <PlusIcon className="w-4 h-4 mr-1" />
                  Add Parameter
                </button>
              </div>

              {/* Execution Conditions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Execution Conditions
                </label>
                <div className="text-sm text-gray-600">
                  <div className="flex items-center mb-2">
                    <input
                      type="checkbox"
                      checked={selectedStep.enabled}
                      onChange={(e) => {
                        const updatedSteps = workflowSteps.map(step =>
                          step.id === selectedStep.id
                            ? { ...step, enabled: e.target.checked }
                            : step
                        );
                        setWorkflowSteps(updatedSteps);
                        setSelectedStep({ ...selectedStep, enabled: e.target.checked });
                      }}
                      className="mr-2"
                    />
                    <span>Enabled</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ToolComposer;