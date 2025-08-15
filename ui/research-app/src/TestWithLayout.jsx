import React from 'react'
import { BrowserRouter as Router } from 'react-router-dom'
import Layout from './components/Layout'

const TestWithLayout = () => {
  console.log('TestWithLayout rendering...')
  
  return (
    <Router>
      <Layout mcpConnected={false} systemStatus={null}>
        <div style={{ padding: '20px' }}>
          <h1>Layout Test</h1>
          <p>If you see navigation and layout, Layout component works</p>
        </div>
      </Layout>
    </Router>
  )
}

export default TestWithLayout