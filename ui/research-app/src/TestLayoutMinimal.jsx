import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { BrowserRouter as Router } from 'react-router-dom'

const MinimalLayout = ({ children }) => {
  const location = useLocation()
  
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      {/* Header */}
      <header style={{ backgroundColor: 'white', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '4rem' }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#111827' }}>
                KGAS Research Platform
              </h1>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                MCP Connected
              </span>
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <Link
              to="/"
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '1rem 0.75rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#6b7280',
                textDecoration: 'none'
              }}
            >
              Workflow
            </Link>
            <Link
              to="/status"
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '1rem 0.75rem',
                fontSize: '0.875rem',
                fontWeight: '500',
                color: '#6b7280',
                textDecoration: 'none'
              }}
            >
              Status
            </Link>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
        {children}
      </main>
    </div>
  )
}

const TestLayoutMinimal = () => {
  return (
    <Router>
      <MinimalLayout>
        <div>
          <h1>Layout Fixed!</h1>
          <p>If you see this, the layout component works without breaking imports</p>
        </div>
      </MinimalLayout>
    </Router>
  )
}

export default TestLayoutMinimal