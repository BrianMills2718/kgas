import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  XCircleIcon,
  RefreshIcon,
  InformationCircleIcon,
  ClockIcon,
  DatabaseIcon,
  ServerIcon
} from '@heroicons/react/outline';
import mcpClient from '../services/mcpClient';

const ServiceStatus = ({ compact = false, showDetails = true }) => {
  const [serviceStatus, setServiceStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkServiceStatus();
    
    // Set up periodic status checks
    const interval = setInterval(checkServiceStatus, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  const checkServiceStatus = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const status = await mcpClient.getSystemStatus();
      setServiceStatus(status);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to check service status:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'available':
      case 'active':
      case 'operational':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'degraded':
      case 'unavailable':
        return <ExclamationCircleIcon className="w-5 h-5 text-yellow-500" />;
      case 'disconnected':
      case 'error':
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <InformationCircleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
      case 'available':
      case 'active':
      case 'operational':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'degraded':
      case 'unavailable':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
      case 'disconnected':
      case 'error':
      case 'failed':
        return 'text-red-700 bg-red-50 border-red-200';
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const formatUptime = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now - then;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes}m`;
    }
    return `${diffMinutes}m`;
  };

  // Core services configuration
  const coreServices = [
    {
      id: 'identity_service',
      name: 'Identity Service (T107)',
      description: 'Entity mention management and resolution',
      icon: <DatabaseIcon className="w-4 h-4" />,
      critical: true
    },
    {
      id: 'provenance_service',
      name: 'Provenance Service (T110)',
      description: 'Operation tracking and lineage',
      icon: <ClockIcon className="w-4 h-4" />,
      critical: true
    },
    {
      id: 'quality_service',
      name: 'Quality Service (T111)',
      description: 'Confidence assessment and propagation',
      icon: <CheckCircleIcon className="w-4 h-4" />,
      critical: true
    },
    {
      id: 'workflow_service',
      name: 'Workflow Service (T121)',
      description: 'Checkpoint and recovery management',
      icon: <ServerIcon className="w-4 h-4" />,
      critical: false
    }
  ];

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        {isLoading ? (
          <RefreshIcon className="w-4 h-4 text-gray-400 animate-spin" />
        ) : error ? (
          <XCircleIcon className="w-4 h-4 text-red-500" />
        ) : (
          <>
            {getStatusIcon(serviceStatus?.status)}
            <span className="text-sm text-gray-600">
              {serviceStatus?.tools_available?.total_mcp_tools || 0} tools
            </span>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
          <div className="flex items-center space-x-2">
            {lastUpdate && (
              <span className="text-xs text-gray-500">
                Updated {formatUptime(lastUpdate)} ago
              </span>
            )}
            <button
              onClick={checkServiceStatus}
              disabled={isLoading}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <RefreshIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">
        {error ? (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <XCircleIcon className="w-5 h-5 text-red-500 mr-2" />
              <span className="text-red-800">Failed to load system status</span>
            </div>
            <div className="text-sm text-red-600 mt-1">{error}</div>
          </div>
        ) : !serviceStatus ? (
          <div className="flex items-center justify-center py-8">
            <RefreshIcon className="w-6 h-6 text-gray-400 animate-spin mr-2" />
            <span className="text-gray-600">Loading system status...</span>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Overall System Status */}
            <div className={`p-3 rounded-md border ${getStatusColor(serviceStatus.status)}`}>
              <div className="flex items-center">
                {getStatusIcon(serviceStatus.status)}
                <span className="ml-2 font-medium">
                  Overall System: {serviceStatus.status || 'Unknown'}
                </span>
              </div>
            </div>

            {/* MCP Tools Overview */}
            {serviceStatus.tools_available && (
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-blue-50 rounded-md">
                  <div className="text-sm text-blue-600 font-medium">Total MCP Tools</div>
                  <div className="text-2xl font-bold text-blue-800">
                    {serviceStatus.tools_available.total_mcp_tools}
                  </div>
                </div>
                <div className="p-3 bg-green-50 rounded-md">
                  <div className="text-sm text-green-600 font-medium">Core Services</div>
                  <div className="text-2xl font-bold text-green-800">
                    {serviceStatus.tools_available.core_services}
                  </div>
                </div>
              </div>
            )}

            {/* Core Services Status */}
            {showDetails && (
              <div>
                <h4 className="font-medium text-gray-800 mb-3">Core Services</h4>
                <div className="space-y-2">
                  {coreServices.map((service) => {
                    const serviceHealth = serviceStatus.system_health?.services?.[service.id];
                    const status = serviceHealth || 'unknown';
                    
                    return (
                      <div
                        key={service.id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                      >
                        <div className="flex items-center">
                          <div className="flex items-center justify-center w-8 h-8 bg-white rounded mr-3">
                            {service.icon}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{service.name}</div>
                            <div className="text-sm text-gray-600">{service.description}</div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {service.critical && (
                            <span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                              Critical
                            </span>
                          )}
                          {getStatusIcon(status)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Infrastructure Status */}
            {showDetails && serviceStatus.system_health && (
              <div>
                <h4 className="font-medium text-gray-800 mb-3">Infrastructure</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {/* Neo4j Database */}
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex items-center">
                      <DatabaseIcon className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="text-sm font-medium text-gray-900">Neo4j Database</span>
                    </div>
                    {getStatusIcon(serviceStatus.system_health.neo4j)}
                  </div>

                  {/* spaCy NLP */}
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex items-center">
                      <ServerIcon className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="text-sm font-medium text-gray-900">spaCy NLP</span>
                    </div>
                    {getStatusIcon(serviceStatus.system_health.spacy)}
                  </div>
                </div>
              </div>
            )}

            {/* Configuration Status */}
            {showDetails && serviceStatus.configuration && (
              <div>
                <h4 className="font-medium text-gray-800 mb-3">Configuration</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Neo4j Configured:</span>
                    <span className={serviceStatus.configuration.neo4j_configured ? 'text-green-600' : 'text-red-600'}>
                      {serviceStatus.configuration.neo4j_configured ? 'Yes' : 'No'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">spaCy Configured:</span>
                    <span className={serviceStatus.configuration.spacy_configured ? 'text-green-600' : 'text-red-600'}>
                      {serviceStatus.configuration.spacy_configured ? 'Yes' : 'No'}
                    </span>
                  </div>
                  {serviceStatus.configuration.workflow_storage && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Workflow Storage:</span>
                      <span className="text-gray-900 font-mono text-xs">
                        {serviceStatus.configuration.workflow_storage}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tool Breakdown */}
            {showDetails && serviceStatus.tools_available && (
              <div>
                <h4 className="font-medium text-gray-800 mb-3">Tool Categories</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Phase 1 Tools:</span>
                    <span className="font-medium">{serviceStatus.tools_available.phase1_tools}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pipeline Tools:</span>
                    <span className="font-medium">{serviceStatus.tools_available.pipeline_tools}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Timestamp */}
            <div className="pt-3 border-t border-gray-200">
              <div className="text-xs text-gray-500">
                Status checked: {serviceStatus.timestamp ? new Date(serviceStatus.timestamp).toLocaleString() : 'Unknown'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ServiceStatus;