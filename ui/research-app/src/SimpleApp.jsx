import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'

// Simple test components
const WorkflowPage = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Natural Language Workflow Orchestrator</h1>
    <p className="text-gray-600 mb-4">Describe your analysis goals in plain English</p>
    
    <textarea 
      className="w-full h-24 p-3 border border-gray-300 rounded-md"
      placeholder="Example: Analyze the uploaded document for key themes, extract entities, and identify relationships"
    />
    
    <div className="mt-4">
      <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
        Plan Workflow
      </button>
    </div>
  </div>
)

const StatusPage = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">System Status</h1>
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-center">
        <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
        <span className="text-green-800 font-medium">System Operational</span>
      </div>
      <div className="mt-2 text-sm text-green-600">
        MCP Server: Connected • 44 tools available
      </div>
    </div>
  </div>
)

const SimpleApp = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">KGAS Research Platform</h1>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600">MCP Connected</span>
              </div>
            </div>
          </div>
        </header>
        
        {/* Navigation */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              <Link
                to="/"
                className="flex items-center px-3 py-4 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              >
                Workflow
              </Link>
              <Link
                to="/status"
                className="flex items-center px-3 py-4 text-sm font-medium border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              >
                Status
              </Link>
            </div>
          </div>
        </nav>
        
        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<WorkflowPage />} />
            <Route path="/status" element={<StatusPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default SimpleApp