import React from 'react'
import { BrowserRouter as Router } from 'react-router-dom'

const SimpleLayout = ({ children }) => {
  return (
    <div>
      <div style={{ background: '#f0f0f0', padding: '10px', marginBottom: '10px' }}>
        <h1>KGAS Header</h1>
        <nav>
          <span style={{ marginRight: '20px' }}>Home</span>
          <span>Status</span>
        </nav>
      </div>
      <div style={{ padding: '20px' }}>
        {children}
      </div>
    </div>
  )
}

const TestLayoutSimple = () => {
  return (
    <Router>
      <SimpleLayout>
        <h1>Simple Layout Test</h1>
        <p>This tests if layout works with inline styles and no Heroicons</p>
      </SimpleLayout>
    </Router>
  )
}

export default TestLayoutSimple