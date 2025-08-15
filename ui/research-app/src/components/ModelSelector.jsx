import React, { useState, useEffect } from 'react';
import { ChipIcon, CpuChipIcon, LightningBoltIcon, CurrencyDollarIcon, CheckCircleIcon } from '@heroicons/react/outline';

const ModelSelector = ({ selectedModel, onModelChange, disabled = false }) => {
  const [modelStats, setModelStats] = useState({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const models = [
    {
      id: 'claude-3-5-sonnet',
      name: 'Claude 3.5 Sonnet',
      provider: 'Anthropic',
      description: 'Best-in-class reasoning and analysis capabilities',
      strengths: [
        'Complex reasoning and analysis',
        'Research methodology expertise',
        'Nuanced understanding of academic content',
        'Excellent entity relationship detection'
      ],
      capabilities: {
        context_window: '200K tokens',
        reasoning: 'Excellent',
        speed: 'Medium',
        cost_per_1k: '$3.00',
        multimodal: true,
        structured_output: true
      },
      use_cases: [
        'Academic research analysis',
        'Complex document understanding',
        'Multi-step reasoning workflows',
        'Entity relationship mapping'
      ],
      limitations: [
        'Higher cost per token',
        'Moderate processing speed'
      ],
      recommended_for: ['academic_research', 'complex_analysis', 'document_processing']
    },
    {
      id: 'gpt-4-turbo',
      name: 'GPT-4 Turbo',
      provider: 'OpenAI',
      description: 'Powerful general-purpose model with broad knowledge',
      strengths: [
        'Broad knowledge across domains',
        'Strong coding and technical analysis',
        'Good performance on structured tasks',
        'Reliable consistency'
      ],
      capabilities: {
        context_window: '128K tokens',
        reasoning: 'Very Good',
        speed: 'Medium',
        cost_per_1k: '$2.50',
        multimodal: true,
        structured_output: true
      },
      use_cases: [
        'General document analysis',
        'Technical content processing',
        'Workflow automation',
        'Mixed content types'
      ],
      limitations: [
        'Less specialized for academic content',
        'Moderate cost'
      ],
      recommended_for: ['general_analysis', 'technical_documents', 'automation']
    },
    {
      id: 'gemini-pro',
      name: 'Gemini Pro',
      provider: 'Google',
      description: 'Fast and efficient with strong multimodal capabilities',
      strengths: [
        'Fast processing speed',
        'Cost-effective for large volumes',
        'Strong multimodal integration',
        'Good structured output'
      ],
      capabilities: {
        context_window: '1M tokens',
        reasoning: 'Good',
        speed: 'Fast',
        cost_per_1k: '$1.25',
        multimodal: true,
        structured_output: true
      },
      use_cases: [
        'High-volume processing',
        'Real-time analysis',
        'Batch document processing',
        'Multimodal content analysis'
      ],
      limitations: [
        'Less sophisticated reasoning',
        'May miss nuanced relationships'
      ],
      recommended_for: ['batch_processing', 'real_time', 'cost_optimization']
    },
    {
      id: 'claude-3-haiku',
      name: 'Claude 3 Haiku',
      provider: 'Anthropic',
      description: 'Fast and economical for simple tasks',
      strengths: [
        'Very fast processing',
        'Most cost-effective',
        'Good for simple extractions',
        'Reliable for structured tasks'
      ],
      capabilities: {
        context_window: '200K tokens',
        reasoning: 'Basic',
        speed: 'Very Fast',
        cost_per_1k: '$0.50',
        multimodal: false,
        structured_output: true
      },
      use_cases: [
        'Simple entity extraction',
        'Basic classification tasks',
        'High-volume simple processing',
        'Real-time applications'
      ],
      limitations: [
        'Limited reasoning capabilities',
        'Not suitable for complex analysis'
      ],
      recommended_for: ['simple_tasks', 'high_volume', 'real_time']
    }
  ];

  useEffect(() => {
    // Simulate loading model performance statistics
    loadModelStats();
  }, []);

  const loadModelStats = async () => {
    // In production, this would fetch real usage statistics
    const mockStats = {
      'claude-3-5-sonnet': {
        avg_response_time: 4.2,
        success_rate: 0.96,
        user_satisfaction: 0.94,
        recent_usage: 2847
      },
      'gpt-4-turbo': {
        avg_response_time: 3.8,
        success_rate: 0.94,
        user_satisfaction: 0.91,
        recent_usage: 1923
      },
      'gemini-pro': {
        avg_response_time: 1.9,
        success_rate: 0.92,
        user_satisfaction: 0.87,
        recent_usage: 4156
      },
      'claude-3-haiku': {
        avg_response_time: 0.8,
        success_rate: 0.89,
        user_satisfaction: 0.82,
        recent_usage: 7834
      }
    };
    setModelStats(mockStats);
  };

  const getModelRecommendation = (taskType, userPreferences = {}) => {
    // Simple recommendation logic based on task type
    const recommendations = {
      'academic_research': 'claude-3-5-sonnet',
      'technical_analysis': 'gpt-4-turbo',
      'batch_processing': 'gemini-pro',
      'real_time': 'claude-3-haiku'
    };
    
    return recommendations[taskType] || 'claude-3-5-sonnet';
  };

  const estimateCost = (model, estimatedTokens = 10000) => {
    const costPerK = parseFloat(model.capabilities.cost_per_1k.replace('$', ''));
    return ((estimatedTokens / 1000) * costPerK).toFixed(2);
  };

  const getSpeedIcon = (speed) => {
    switch (speed) {
      case 'Very Fast':
        return <LightningBoltIcon className="w-4 h-4 text-green-500" />;
      case 'Fast':
        return <LightningBoltIcon className="w-4 h-4 text-blue-500" />;
      case 'Medium':
        return <CpuChipIcon className="w-4 h-4 text-yellow-500" />;
      default:
        return <ChipIcon className="w-4 h-4 text-gray-500" />;
    }
  };

  const getReasoningBadge = (reasoning) => {
    const badges = {
      'Excellent': 'bg-green-100 text-green-800',
      'Very Good': 'bg-blue-100 text-blue-800',
      'Good': 'bg-yellow-100 text-yellow-800',
      'Basic': 'bg-gray-100 text-gray-800'
    };
    
    return badges[reasoning] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Choose AI Model</h3>
          <p className="text-sm text-gray-600">
            Select the model that best fits your analysis requirements
          </p>
        </div>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          {showAdvanced ? 'Simple View' : 'Advanced Options'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {models.map((model) => {
          const isSelected = selectedModel === model.id;
          const stats = modelStats[model.id] || {};
          
          return (
            <div
              key={model.id}
              className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => !disabled && onModelChange(model.id)}
            >
              {isSelected && (
                <CheckCircleIcon className="absolute top-3 right-3 w-5 h-5 text-blue-500" />
              )}

              {/* Model Header */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-gray-900">{model.name}</h4>
                  <span className="text-xs text-gray-500">{model.provider}</span>
                </div>
                <p className="text-sm text-gray-600">{model.description}</p>
              </div>

              {/* Key Capabilities */}
              <div className="mb-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Reasoning:</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${getReasoningBadge(model.capabilities.reasoning)}`}>
                    {model.capabilities.reasoning}
                  </span>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Speed:</span>
                  <div className="flex items-center space-x-1">
                    {getSpeedIcon(model.capabilities.speed)}
                    <span>{model.capabilities.speed}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Cost (1K tokens):</span>
                  <div className="flex items-center space-x-1">
                    <CurrencyDollarIcon className="w-3 h-3 text-green-600" />
                    <span>{model.capabilities.cost_per_1k}</span>
                  </div>
                </div>
              </div>

              {/* Performance Stats */}
              {stats.avg_response_time && (
                <div className="mb-3 p-2 bg-white rounded border">
                  <div className="text-xs text-gray-500 mb-1">Performance</div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-gray-600">Avg. Response:</span>
                      <span className="ml-1 font-medium">{stats.avg_response_time}s</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Success Rate:</span>
                      <span className="ml-1 font-medium">{Math.round(stats.success_rate * 100)}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Advanced Information */}
              {showAdvanced && (
                <div className="space-y-3 pt-3 border-t border-gray-200">
                  {/* Strengths */}
                  <div>
                    <div className="text-xs font-medium text-gray-700 mb-1">Strengths</div>
                    <div className="space-y-1">
                      {model.strengths.slice(0, 2).map((strength, index) => (
                        <div key={index} className="text-xs text-gray-600">
                          • {strength}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Use Cases */}
                  <div>
                    <div className="text-xs font-medium text-gray-700 mb-1">Best For</div>
                    <div className="flex flex-wrap gap-1">
                      {model.use_cases.slice(0, 3).map((useCase, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                        >
                          {useCase}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Technical Details */}
                  <div>
                    <div className="text-xs font-medium text-gray-700 mb-1">Technical</div>
                    <div className="text-xs text-gray-600 space-y-1">
                      <div>Context: {model.capabilities.context_window}</div>
                      <div className="flex items-center space-x-2">
                        <span>Multimodal: {model.capabilities.multimodal ? '✓' : '✗'}</span>
                        <span>Structured: {model.capabilities.structured_output ? '✓' : '✗'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Cost Estimation */}
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  Est. cost for 10K tokens: ${estimateCost(model)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Model Comparison */}
      {showAdvanced && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-800 mb-3">Quick Comparison</h4>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2">Model</th>
                  <th className="text-center py-2">Speed</th>
                  <th className="text-center py-2">Reasoning</th>
                  <th className="text-center py-2">Cost</th>
                  <th className="text-center py-2">Context</th>
                </tr>
              </thead>
              <tbody>
                {models.map((model) => (
                  <tr key={model.id} className="border-b border-gray-100">
                    <td className="py-2 font-medium">{model.name}</td>
                    <td className="text-center py-2">{model.capabilities.speed}</td>
                    <td className="text-center py-2">{model.capabilities.reasoning}</td>
                    <td className="text-center py-2">{model.capabilities.cost_per_1k}</td>
                    <td className="text-center py-2">{model.capabilities.context_window}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Model Recommendations */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">💡 Recommendations</h4>
        <div className="space-y-2 text-sm text-blue-800">
          <div><strong>For academic research:</strong> Claude 3.5 Sonnet offers the best reasoning capabilities</div>
          <div><strong>For high-volume processing:</strong> Gemini Pro provides the best speed/cost balance</div>
          <div><strong>For real-time applications:</strong> Claude 3 Haiku offers the fastest response times</div>
          <div><strong>For technical analysis:</strong> GPT-4 Turbo excels at structured technical content</div>
        </div>
      </div>
    </div>
  );
};

export default ModelSelector;