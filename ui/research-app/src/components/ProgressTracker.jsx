import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  ClockIcon, 
  ExclamationCircleIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  ArrowRightIcon,
  DocumentTextIcon,
  ChartBarIcon
} from '@heroicons/react/outline';

const ProgressTracker = ({ 
  workflowId, 
  steps = [], 
  onCancel,
  onPause,
  onResume,
  compact = false 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepStatuses, setStepStatuses] = useState({});
  const [workflowStatus, setWorkflowStatus] = useState('idle'); // idle, running, paused, completed, failed
  const [startTime, setStartTime] = useState(null);
  const [endTime, setEndTime] = useState(null);
  const [logs, setLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    // Initialize step statuses
    const initialStatuses = {};
    steps.forEach((step, index) => {
      initialStatuses[index] = {
        status: 'pending', // pending, running, completed, failed, skipped
        startTime: null,
        endTime: null,
        result: null,
        error: null,
        duration: 0
      };
    });
    setStepStatuses(initialStatuses);
  }, [steps]);

  useEffect(() => {
    // Simulate workflow execution for demo purposes
    // In production, this would listen to real MCP events
    if (workflowStatus === 'running' && currentStep < steps.length) {
      const stepTimeout = setTimeout(() => {
        executeNextStep();
      }, 2000 + Math.random() * 3000); // 2-5 seconds per step

      return () => clearTimeout(stepTimeout);
    }
  }, [workflowStatus, currentStep, steps]);

  const executeNextStep = () => {
    const stepIndex = currentStep;
    const step = steps[stepIndex];
    
    if (!step) return;

    // Mark step as running
    updateStepStatus(stepIndex, {
      status: 'running',
      startTime: new Date()
    });

    addLog(`Starting step ${stepIndex + 1}: ${step.toolName}`, 'info');

    // Simulate step execution
    setTimeout(() => {
      // Simulate success/failure (90% success rate)
      const success = Math.random() > 0.1;
      
      if (success) {
        updateStepStatus(stepIndex, {
          status: 'completed',
          endTime: new Date(),
          result: {
            status: 'success',
            data: `Mock result for ${step.toolName}`,
            executionTime: (Math.random() * 5 + 1).toFixed(2)
          }
        });
        
        addLog(`Completed step ${stepIndex + 1}: ${step.toolName}`, 'success');
        
        // Move to next step
        if (stepIndex + 1 < steps.length) {
          setCurrentStep(stepIndex + 1);
        } else {
          // Workflow completed
          setWorkflowStatus('completed');
          setEndTime(new Date());
          addLog('Workflow completed successfully', 'success');
        }
      } else {
        // Simulate failure
        updateStepStatus(stepIndex, {
          status: 'failed',
          endTime: new Date(),
          error: `Mock error in ${step.toolName}: Connection timeout`
        });
        
        addLog(`Failed step ${stepIndex + 1}: ${step.toolName}`, 'error');
        setWorkflowStatus('failed');
        setEndTime(new Date());
      }
    }, 1500 + Math.random() * 2000);
  };

  const updateStepStatus = (stepIndex, updates) => {
    setStepStatuses(prev => ({
      ...prev,
      [stepIndex]: {
        ...prev[stepIndex],
        ...updates,
        duration: updates.endTime && prev[stepIndex].startTime
          ? updates.endTime - prev[stepIndex].startTime
          : prev[stepIndex].duration
      }
    }));
  };

  const addLog = (message, level = 'info') => {
    const newLog = {
      id: Date.now() + Math.random(),
      timestamp: new Date(),
      message,
      level
    };
    setLogs(prev => [...prev, newLog].slice(-100)); // Keep last 100 logs
  };

  const startWorkflow = () => {
    setWorkflowStatus('running');
    setStartTime(new Date());
    setCurrentStep(0);
    addLog('Workflow started', 'info');
  };

  const pauseWorkflow = () => {
    setWorkflowStatus('paused');
    addLog('Workflow paused', 'warning');
    if (onPause) onPause();
  };

  const resumeWorkflow = () => {
    setWorkflowStatus('running');
    addLog('Workflow resumed', 'info');
    if (onResume) onResume();
  };

  const cancelWorkflow = () => {
    setWorkflowStatus('cancelled');
    setEndTime(new Date());
    addLog('Workflow cancelled', 'warning');
    if (onCancel) onCancel();
  };

  const getStepIcon = (stepIndex) => {
    const status = stepStatuses[stepIndex]?.status || 'pending';
    
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'running':
        return <PlayIcon className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'failed':
        return <ExclamationCircleIcon className="w-5 h-5 text-red-500" />;
      case 'skipped':
        return <ArrowRightIcon className="w-5 h-5 text-gray-400" />;
      default:
        return <ClockIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getProgressPercentage = () => {
    const completedSteps = Object.values(stepStatuses).filter(
      status => status.status === 'completed'
    ).length;
    return steps.length > 0 ? (completedSteps / steps.length) * 100 : 0;
  };

  const getTotalDuration = () => {
    if (!startTime) return 0;
    const end = endTime || new Date();
    return end - startTime;
  };

  const formatDuration = (ms) => {
    if (!ms) return '0s';
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${remainingSeconds}s`;
  };

  const getLogIcon = (level) => {
    switch (level) {
      case 'success':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'error':
        return <ExclamationCircleIcon className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <ExclamationCircleIcon className="w-4 h-4 text-yellow-500" />;
      default:
        return <DocumentTextIcon className="w-4 h-4 text-blue-500" />;
    }
  };

  if (compact) {
    return (
      <div className="flex items-center space-x-3">
        <div className="flex-1">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="font-medium text-gray-900">
              {workflowStatus === 'running' ? 'Running' : 
               workflowStatus === 'completed' ? 'Completed' :
               workflowStatus === 'failed' ? 'Failed' : 'Ready'}
            </span>
            <span className="text-gray-600">
              {Math.round(getProgressPercentage())}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                workflowStatus === 'failed' ? 'bg-red-500' :
                workflowStatus === 'completed' ? 'bg-green-500' : 'bg-blue-500'
              }`}
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
        </div>
        
        {workflowStatus === 'idle' && (
          <button
            onClick={startWorkflow}
            className="p-2 text-blue-600 hover:text-blue-800"
          >
            <PlayIcon className="w-4 h-4" />
          </button>
        )}
        
        {workflowStatus === 'running' && (
          <button
            onClick={pauseWorkflow}
            className="p-2 text-yellow-600 hover:text-yellow-800"
          >
            <PauseIcon className="w-4 h-4" />
          </button>
        )}
        
        {workflowStatus === 'paused' && (
          <button
            onClick={resumeWorkflow}
            className="p-2 text-green-600 hover:text-green-800"
          >
            <PlayIcon className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Workflow Progress</h3>
            {workflowId && (
              <p className="text-sm text-gray-600">ID: {workflowId}</p>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            {startTime && (
              <span className="text-sm text-gray-600">
                Duration: {formatDuration(getTotalDuration())}
              </span>
            )}
            
            {workflowStatus === 'idle' && (
              <button
                onClick={startWorkflow}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                <PlayIcon className="w-4 h-4 mr-1" />
                Start
              </button>
            )}
            
            {workflowStatus === 'running' && (
              <>
                <button
                  onClick={pauseWorkflow}
                  className="flex items-center px-3 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  <PauseIcon className="w-4 h-4 mr-1" />
                  Pause
                </button>
                <button
                  onClick={cancelWorkflow}
                  className="flex items-center px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  <StopIcon className="w-4 h-4 mr-1" />
                  Cancel
                </button>
              </>
            )}
            
            {workflowStatus === 'paused' && (
              <button
                onClick={resumeWorkflow}
                className="flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <PlayIcon className="w-4 h-4 mr-1" />
                Resume
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Step {Math.min(currentStep + 1, steps.length)} of {steps.length}
          </span>
          <span className="text-sm text-gray-600">
            {Math.round(getProgressPercentage())}% Complete
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${
              workflowStatus === 'failed' ? 'bg-red-500' :
              workflowStatus === 'completed' ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${getProgressPercentage()}%` }}
          />
        </div>

        {/* Step List */}
        <div className="space-y-3">
          {steps.map((step, index) => {
            const status = stepStatuses[index] || {};
            const isActive = index === currentStep;
            
            return (
              <div
                key={index}
                className={`flex items-center p-3 rounded-lg border ${
                  isActive && workflowStatus === 'running'
                    ? 'border-blue-300 bg-blue-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex-shrink-0 mr-3">
                  {getStepIcon(index)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{step.toolName}</h4>
                    {status.duration > 0 && (
                      <span className="text-sm text-gray-600">
                        {formatDuration(status.duration)}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600">{step.displayName || step.description}</p>
                  
                  {status.error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-800">
                      Error: {status.error}
                    </div>
                  )}
                  
                  {status.result && (
                    <div className="mt-2 text-sm text-gray-600">
                      ✓ {status.result.data}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Logs Section */}
        {logs.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-medium text-gray-800">Execution Log</h4>
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                {showLogs ? 'Hide' : 'Show'} Details
              </button>
            </div>
            
            {showLogs && (
              <div className="max-h-48 overflow-y-auto bg-gray-50 border border-gray-200 rounded-md p-3">
                <div className="space-y-2">
                  {logs.slice(-10).map((log) => (
                    <div key={log.id} className="flex items-start space-x-2 text-sm">
                      <div className="flex-shrink-0 mt-0.5">
                        {getLogIcon(log.level)}
                      </div>
                      <div className="flex-1">
                        <span className="text-gray-600">
                          {log.timestamp.toLocaleTimeString()}
                        </span>
                        <span className="ml-2 text-gray-900">{log.message}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Summary Stats */}
        {(workflowStatus === 'completed' || workflowStatus === 'failed') && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {Object.values(stepStatuses).filter(s => s.status === 'completed').length}
                </div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {Object.values(stepStatuses).filter(s => s.status === 'failed').length}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">
                  {formatDuration(getTotalDuration())}
                </div>
                <div className="text-sm text-gray-600">Total Time</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTracker;